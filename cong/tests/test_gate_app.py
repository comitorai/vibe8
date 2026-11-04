import contextlib
import http.server
import io
import json
import os
import threading
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

from cong import gate_app, ten

MAU = Path(__file__).with_name("pr_mau.json")
SHA = "a" * 40
SHA_MOI = "c" * 40
TOKEN = "ghs_bimatgiaodenkhonginra"


def du_lieu():
    return json.loads(MAU.read_text(encoding="utf-8"))


def chay(gh, **kw):
    ra = io.StringIO()
    with contextlib.redirect_stdout(ra):
        kw.setdefault("cho_giay", 0)
        kw.setdefault("ngu", lambda s: None)
        ma = gate_app.chay(gh, "7", **kw)
    return ma, ra.getvalue()


class TestChay(unittest.TestCase):
    def test_phat_dung_mot_check_dung_sha_dung_ten(self):
        gh = gate_app.GiaLap(du_lieu())
        ma, _ = chay(gh)
        self.assertEqual(ma, 0)
        self.assertEqual(len(gh.da_phat), 1)
        phuong, duong, body = gh.da_phat[0]
        self.assertEqual((phuong, duong), ("POST", "/check-runs"))
        self.assertEqual(body["name"], ten.CHECK_CUOI)
        self.assertEqual(body["head_sha"], SHA)
        self.assertEqual(body["conclusion"], "success")

    def test_than_pr_khong_lot_vao_check(self):
        gh = gate_app.GiaLap(du_lieu())
        chay(gh)
        self.assertNotIn("BỎ QUA", json.dumps(gh.da_phat[0][2], ensure_ascii=False))

    def test_rui_ro_cao_phat_failure(self):
        d = du_lieu()
        d["/pulls/7/files"][0]["filename"] = ".github/workflows/x.yml"
        gh = gate_app.GiaLap(d)
        ma, _ = chay(gh)
        self.assertEqual(ma, 0)
        self.assertEqual(gh.da_phat[0][2]["conclusion"], "failure")

    def test_het_gio_cho_phat_failure_khong_neutral(self):
        d = du_lieu()
        d["/commits/%s/check-runs" % SHA]["check_runs"][0].update(status="in_progress", conclusion=None)
        gh = gate_app.GiaLap(d)
        ma, _ = chay(gh)
        self.assertEqual(ma, 0)
        self.assertEqual(gh.da_phat[0][2]["conclusion"], "failure")
        self.assertIn("hết 0 giây", gh.da_phat[0][2]["output"]["summary"])

    def test_cho_toi_khi_cong_nhanh_xong(self):
        d = du_lieu()
        ds = d["/commits/%s/check-runs" % SHA]["check_runs"]
        ds[0].update(status="in_progress", conclusion=None)
        gh = gate_app.GiaLap(d)
        lan_ngu = []

        def ngu(giay):
            lan_ngu.append(giay)
            ds[0].update(status="completed", conclusion="success")

        ma, _ = chay(gh, cho_giay=600, nghi=15, ngu=ngu)
        self.assertEqual((ma, lan_ngu), (0, [15]))
        self.assertEqual(gh.da_phat[0][2]["conclusion"], "success")

    def test_check_ten_khac_khong_tinh(self):
        d = du_lieu()
        d["/commits/%s/check-runs" % SHA]["check_runs"][0]["name"] = "cong-nhanh-gia"
        gh = gate_app.GiaLap(d)
        chay(gh)
        self.assertEqual(gh.da_phat[0][2]["conclusion"], "failure")

    def test_khong_co_gio_suite_thi_duyet_khong_tinh(self):
        d = du_lieu()
        d["/pulls/7/files"][0]["filename"] = "CODEOWNERS"
        d["/commits/%s/check-suites" % SHA]["check_suites"] = []
        d["/pulls/7/reviews"] = [{
            "user": {"login": "khac", "type": "User"}, "author_association": "MEMBER", "state": "APPROVED",
            "commit_id": SHA, "submitted_at": "2026-11-02T00:00:00Z", "body": ""}]
        gh = gate_app.GiaLap(d)
        chay(gh)
        self.assertEqual(gh.da_phat[0][2]["conclusion"], "failure")

    def test_duyet_hop_le_qua_duong_api(self):
        d = du_lieu()
        d["/pulls/7/files"][0]["filename"] = "CODEOWNERS"
        d["/pulls/7/reviews"] = [{
            "user": {"login": "khac", "type": "User"}, "author_association": "MEMBER", "state": "APPROVED",
            "commit_id": SHA, "submitted_at": "2026-11-02T00:00:00Z", "body": ""}]
        gh = gate_app.GiaLap(d)
        chay(gh)
        self.assertEqual(gh.da_phat[0][2]["conclusion"], "success")

    def test_nguoi_commit_lay_tu_api_khong_duyet_duoc(self):
        d = du_lieu()
        d["/pulls/7/files"][0]["filename"] = "CODEOWNERS"
        d["/pulls/7/commits"][0]["author"] = {"login": "khac"}
        d["/pulls/7/reviews"] = [{
            "user": {"login": "khac", "type": "User"}, "author_association": "MEMBER", "state": "APPROVED",
            "commit_id": SHA, "submitted_at": "2026-11-02T00:00:00Z", "body": ""}]
        gh = gate_app.GiaLap(d)
        chay(gh)
        self.assertEqual(gh.da_phat[0][2]["conclusion"], "failure")


class GitHubDoiSha(gate_app.GiaLap):
    """Head đổi đúng lúc đang đọc: /files đã là của commit mới."""

    def __init__(self, d, so_lan_doi):
        super().__init__(d)
        self.lan = 0
        self.so_lan_doi = so_lan_doi

    def goi(self, phuong, duong, body=None):
        if duong == "/pulls/7":
            self.lan += 1
            sha = SHA if self.lan <= 1 else SHA_MOI
            if self.so_lan_doi > 1:
                sha = "%040x" % self.lan
            return dict(self.du_lieu[duong], head={"sha": sha})
        if "/commits/" in duong and "/commits/%s/" % SHA not in duong:
            khoa = "check_runs" if "check-runs" in duong else "check_suites"
            sha_doc = duong.split("/")[2]
            mau = json.loads(json.dumps(self.du_lieu["/commits/%s/%s" % (SHA, khoa.replace("_", "-"))]))
            for x in mau[khoa]:
                if "head_sha" in x:
                    x["head_sha"] = sha_doc
            return mau if "page=1" in duong else {khoa: []}
        return super().goi(phuong, duong, body)


class TestShaDoi(unittest.TestCase):
    def test_doi_giua_chung_doc_lai_va_phat_tren_sha_moi(self):
        gh = GitHubDoiSha(du_lieu(), 1)
        ma, _ = chay(gh)
        self.assertEqual(ma, 0)
        self.assertEqual(len(gh.da_phat), 1)
        self.assertEqual(gh.da_phat[0][2]["head_sha"], SHA_MOI)

    def test_doi_lien_tuc_khong_phat_success(self):
        gh = GitHubDoiSha(du_lieu(), 99)
        ma, ra = chay(gh)
        self.assertEqual(ma, 1)
        self.assertIn("đổi liên tục", ra)
        self.assertEqual([x[2]["conclusion"] for x in gh.da_phat], ["failure"])


class GitHubHong(gate_app.GiaLap):
    def __init__(self, d, hong_tai, loi):
        super().__init__(d)
        self.hong_tai, self.loi = hong_tai, loi
        self.token = TOKEN

    def che(self, chuoi):
        return chuoi.replace(TOKEN, "***")

    def goi(self, phuong, duong, body=None):
        if self.hong_tai in duong and phuong == "GET":
            raise self.loi
        return super().goi(phuong, duong, body)


class TestHong(unittest.TestCase):
    def test_loi_doc_phat_failure_va_che_token(self):
        gh = GitHubHong(du_lieu(), "/reviews", RuntimeError("Bearer " + TOKEN))
        ma, ra = chay(gh)
        self.assertEqual(ma, 1)
        self.assertNotIn(TOKEN, ra)
        self.assertEqual(gh.da_phat[0][2]["conclusion"], "failure")
        self.assertNotIn(TOKEN, json.dumps(gh.da_phat))

    def test_khong_doc_duoc_pr_thi_khong_phat_gi(self):
        gh = GitHubHong(du_lieu(), "/pulls/7", gate_app.LoiApi("hỏng", 500))
        ma, _ = chay(gh)
        self.assertEqual(ma, 1)
        self.assertEqual(gh.da_phat, [])

    def test_sha_rac_tu_api_khong_phat(self):
        d = du_lieu()
        d["/pulls/7"]["head"]["sha"] = "main"
        d["/commits/main/check-runs"] = {"check_runs": []}
        d["/commits/main/check-suites"] = {"check_suites": []}
        gh = gate_app.GiaLap(d)
        ma, _ = chay(gh)
        self.assertEqual(ma, 1)
        self.assertEqual(gh.da_phat, [])


class _PhanHoi(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class TestGitHub(unittest.TestCase):
    def _gh(self, mo):
        gh = gate_app.GitHub("chu/repo", TOKEN)
        gh._mo = mo
        return gh

    def test_gui_token_o_header_khong_o_url(self):
        ghi = {}

        def mo(yeu_cau, timeout):
            ghi["url"], ghi["auth"] = yeu_cau.full_url, yeu_cau.get_header("Authorization")
            return _PhanHoi(b"{}")

        self._gh(mo).goi("GET", "/pulls/1")
        self.assertEqual(ghi["url"], "https://api.github.com/repos/chu/repo/pulls/1")
        self.assertEqual(ghi["auth"], "Bearer " + TOKEN)

    def test_tu_choi_api_khong_https(self):
        with self.assertRaises(gate_app.LoiApi):
            gate_app.GitHub("chu/repo", TOKEN, "http://api.github.com")

    def test_khong_di_theo_chuyen_huong(self):
        self.assertIsNone(gate_app._KhongChuyenHuong().redirect_request())

    def test_loi_http_khong_mang_than_phan_hoi(self):
        def mo(yeu_cau, timeout):
            raise urllib.error.HTTPError(yeu_cau.full_url, 403, "x", {}, io.BytesIO(b"bi mat phan chieu"))

        with self.assertRaises(gate_app.LoiApi) as ng:
            self._gh(mo).goi("GET", "/pulls/1")
        self.assertEqual(ng.exception.ma, 403)
        self.assertNotIn("bi mat", str(ng.exception))
        self.assertNotIn(TOKEN, str(ng.exception))

    def test_doc_het_cac_trang(self):
        trang = {1: [{"n": i} for i in range(100)], 2: [{"n": 100}]}

        def mo(yeu_cau, timeout):
            so = int(yeu_cau.full_url.rsplit("page=", 1)[1])
            return _PhanHoi(json.dumps(trang[so]).encode())

        self.assertEqual(len(gate_app._trang(self._gh(mo), "/pulls/1/files")), 101)

    def test_loi_5xx_thu_lai_roi_bao_loi(self):
        lan = []

        def mo(yeu_cau, timeout):
            lan.append(1)
            raise urllib.error.HTTPError(yeu_cau.full_url, 502, "x", {}, io.BytesIO(b""))

        with mock.patch.object(gate_app.time, "sleep"), self.assertRaises(gate_app.LoiApi):
            self._gh(mo).goi("GET", "/pulls/1")
        self.assertEqual(len(lan), 3)


class _Chuyen(http.server.BaseHTTPRequestHandler):
    da_goi = []

    def do_GET(self):
        self.da_goi.append((self.path, self.headers.get("Authorization")))
        self.send_response(302)
        self.send_header("Location", "/cho-khac")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, *a):
        pass


class TestCheVaChuyenHuongThat(unittest.TestCase):
    def test_gitHub_that_khong_mang_token_sang_noi_chuyen_huong(self):
        may = http.server.HTTPServer(("127.0.0.1", 0), _Chuyen)
        luong = threading.Thread(target=may.serve_forever, daemon=True)
        luong.start()
        self.addCleanup(may.server_close)
        self.addCleanup(may.shutdown)
        _Chuyen.da_goi = []
        with mock.patch.dict(os.environ, {"no_proxy": "*"}):
            gh = gate_app.GitHub("chu/repo", TOKEN)
            gh.goc_repo = "http://127.0.0.1:%d/repos/chu/repo" % may.server_address[1]
            with self.assertRaises(gate_app.LoiApi) as ng:
                gh.goi("GET", "/pulls/1")
        self.assertEqual(ng.exception.ma, 302)
        self.assertEqual([x[0] for x in _Chuyen.da_goi], ["/repos/chu/repo/pulls/1"])

    def test_gitHub_that_che_token_trong_log(self):
        gh = gate_app.GitHub("chu/repo", TOKEN)
        gh._mo = mock.Mock(side_effect=RuntimeError("Bearer " + TOKEN))
        ma, ra = chay(gh)
        self.assertEqual(ma, 1)
        self.assertNotIn(TOKEN, ra)
        self.assertIn("***", ra)


class TestMain(unittest.TestCase):
    def _main(self, argv, env=None):
        ra = io.StringIO()
        with mock.patch.dict(os.environ, env or {}, clear=True), contextlib.redirect_stdout(ra):
            return gate_app.main(argv), ra.getvalue()

    def test_chay_kho_khong_can_token(self):
        ma, ra = self._main(["--kho", str(MAU), "--pr", "7"])
        self.assertEqual(ma, 0)
        self.assertIn("CHẠY KHÔ", ra)
        self.assertIn("/check-runs", ra)

    def test_so_pr_rac_bi_tu_choi(self):
        for pr in ("", "0", "-1", "7/../../x", "7\n"):
            with self.subTest(repr(pr)):
                self.assertEqual(self._main(["--pr", pr])[0], 2)

    def test_thieu_token_khong_chay(self):
        ma, _ = self._main(["--pr", "7"], {"GITHUB_REPOSITORY": "chu/repo"})
        self.assertEqual(ma, 2)
