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


def chay(gh, sha=SHA, nguoi_tin=("khac", "tac-gia")):
    ra = io.StringIO()
    with contextlib.redirect_stdout(ra):
        ma = gate_app.chay(gh, list(nguoi_tin), sha)
    return ma, ra.getvalue()


def lan_chay(d):
    return d["/actions/workflows/cong-nhanh.yml/runs?head_sha=%s&event=pull_request" % SHA]["workflow_runs"]


def thuoc_pr(so=7, base="main"):
    return [{"number": so, "base": {"ref": base}, "head": {"sha": SHA}}]


def can_duyet(d, login="khac", **khac):
    d["/pulls/7/files"][0]["filename"] = "CODEOWNERS"
    d["/pulls/7/reviews"] = [dict({"user": {"login": login, "type": "User"}, "state": "APPROVED", "commit_id": SHA,
                                   "submitted_at": "2026-11-02T00:00:00Z", "body": ""}, **khac)]
    return d


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

    def test_ci_chua_xong_phat_failure_ghi_ro_dang_cho(self):
        d = du_lieu()
        lan_chay(d)[0].update(status="in_progress", conclusion=None)
        gh = gate_app.GiaLap(d)
        ma, _ = chay(gh)
        self.assertEqual(ma, 0)
        self.assertEqual(gh.da_phat[0][2]["conclusion"], "failure")
        self.assertTrue(gh.da_phat[0][2]["output"]["title"].startswith("cho "))

    def test_luot_do_khong_duoc_luot_xanh_che(self):
        d = du_lieu()
        lan_chay(d).append({"head_sha": SHA, "status": "completed", "conclusion": "failure",
                            "head_repository": {"full_name": "chu/repo"}, "pull_requests": thuoc_pr()})
        gh = gate_app.GiaLap(d)
        chay(gh)
        self.assertEqual(gh.da_phat[0][2]["conclusion"], "failure")

    def test_duyet_hop_le_qua_duong_api(self):
        gh = gate_app.GiaLap(can_duyet(du_lieu()))
        chay(gh)
        self.assertEqual(gh.da_phat[0][2]["conclusion"], "success")

    def test_nguoi_ngoai_danh_sach_khong_duyet_duoc(self):
        gh = gate_app.GiaLap(can_duyet(du_lieu()))
        chay(gh, nguoi_tin=("nguoi-khac",))
        self.assertEqual(gh.da_phat[0][2]["conclusion"], "failure")

    def test_author_commit_khong_duyet_duoc(self):
        d = can_duyet(du_lieu())
        d["/pulls/7/commits"][0]["author"] = {"login": "khac"}
        gh = gate_app.GiaLap(d)
        chay(gh)
        self.assertEqual(gh.da_phat[0][2]["conclusion"], "failure")

    def test_committer_khong_duyet_duoc(self):
        d = can_duyet(du_lieu())
        d["/pulls/7/commits"][0]["committer"] = {"login": "khac"}
        gh = gate_app.GiaLap(d)
        chay(gh)
        self.assertEqual(gh.da_phat[0][2]["conclusion"], "failure")

    def test_commit_merge_cua_chu_khong_thanh_tu_duyet(self):
        d = can_duyet(du_lieu())
        d["/pulls/7"]["commits"] = 2
        d["/pulls/7/commits"].append({"author": {"login": "khac"}, "committer": {"login": "khac"},
                                      "parents": [{"sha": "1" * 40}, {"sha": "2" * 40}]})
        gh = gate_app.GiaLap(d)
        chay(gh)
        self.assertEqual(gh.da_phat[0][2]["conclusion"], "success")

    def test_commit_khong_ro_cha_van_tinh_la_commit_thuong(self):
        d = can_duyet(du_lieu())
        del d["/pulls/7/commits"][0]["parents"]
        d["/pulls/7/commits"][0]["author"] = {"login": "khac"}
        gh = gate_app.GiaLap(d)
        chay(gh)
        self.assertEqual(gh.da_phat[0][2]["conclusion"], "failure")

    def test_doc_thieu_commit_phat_failure(self):
        d = du_lieu()
        d["/pulls/7"]["commits"] = 300
        gh = gate_app.GiaLap(d)
        chay(gh)
        self.assertEqual(gh.da_phat[0][2]["conclusion"], "failure")

    def test_base_khac_goc_phat_failure(self):
        d = du_lieu()
        d["/pulls/7"]["base"]["ref"] = "x"
        gh = gate_app.GiaLap(d)
        chay(gh)
        self.assertEqual(gh.da_phat[0][2]["conclusion"], "failure")


def them_pr_fork(d, so=8):
    d["/pulls?state=open&base=main"].append({
        "number": so, "head": {"sha": SHA, "repo": {"full_name": "la/repo"}},
        "base": {"ref": "main", "repo": {"full_name": "chu/repo"}}})


class TestTimPr(unittest.TestCase):
    def test_khong_co_pr_thi_thu_hoi_check_cu(self):
        # Đổi base đi rồi đổi lại: `success` cũ không được ở lại chờ sẵn.
        d = du_lieu()
        d["/pulls?state=open&base=main"][0]["head"]["sha"] = SHA_MOI
        gh = gate_app.GiaLap(d)
        ma, _ = chay(gh)
        self.assertEqual(ma, 0)
        self.assertEqual([(x[2]["head_sha"], x[2]["conclusion"]) for x in gh.da_phat], [(SHA, "failure")])
        self.assertIn("không còn là head", json.dumps(gh.da_phat, ensure_ascii=False))

    def test_hai_pr_trong_repo_cung_sha_phat_failure(self):
        d = du_lieu()
        d["/pulls?state=open&base=main"].append(dict(d["/pulls?state=open&base=main"][0], number=8))
        gh = gate_app.GiaLap(d)
        chay(gh)
        self.assertEqual(gh.da_phat[0][2]["conclusion"], "failure")

    def test_khong_doc_duoc_danh_sach_van_phat_failure_tren_sha(self):
        gh = GitHubHong(du_lieu(), "/pulls?state", gate_app.LoiApi("hỏng", 500))
        ma, _ = chay(gh)
        self.assertEqual(ma, 1)
        self.assertEqual([(x[2]["head_sha"], x[2]["conclusion"]) for x in gh.da_phat], [(SHA, "failure")])

    def test_fork_cung_sha_khong_lam_ket_pr_trong_repo(self):
        d = du_lieu()
        them_pr_fork(d)
        gh = gate_app.GiaLap(d)
        chay(gh)
        self.assertEqual(gh.da_phat[0][2]["conclusion"], "success")

    def test_fork_mo_truoc_van_xet_pr_trong_repo(self):
        d = du_lieu()
        d["/pulls?state=open&base=main"].insert(0, {
            "number": 8, "head": {"sha": SHA, "repo": {"full_name": "la/repo"}},
            "base": {"ref": "main", "repo": {"full_name": "chu/repo"}}})
        gh = gate_app.GiaLap(d)
        chay(gh)
        self.assertEqual(gh.da_phat[0][2]["conclusion"], "success")

    def test_chi_co_pr_tu_fork_thi_van_xet(self):
        d = du_lieu()
        la = {"full_name": "la/repo"}
        d["/pulls?state=open&base=main"][0]["head"]["repo"] = la
        d["/pulls/7"]["head"]["repo"] = la
        lan_chay(d)[0].update(head_repository=la, pull_requests=[])  # Lượt PR fork không ghi PR nào.
        gh = gate_app.GiaLap(d)
        chay(gh)
        self.assertEqual(gh.da_phat[0][2]["conclusion"], "success")


class TestLocLuotCi(unittest.TestCase):
    def test_luot_do_cua_fork_khong_lam_ket(self):
        d = du_lieu()
        lan_chay(d).append({"head_sha": SHA, "status": "completed", "conclusion": "action_required",
                            "head_repository": {"full_name": "la/repo"}})
        gh = gate_app.GiaLap(d)
        chay(gh)
        self.assertEqual(gh.da_phat[0][2]["conclusion"], "success")

    def test_luot_xanh_cua_fork_khong_thay_duoc_luot_trong_repo(self):
        d = du_lieu()
        lan_chay(d)[0].update(head_repository={"full_name": "la/repo"}, pull_requests=[])
        gh = gate_app.GiaLap(d)
        chay(gh)
        self.assertTrue(gh.da_phat[0][2]["output"]["title"].startswith("cho "))
        self.assertEqual(gh.da_phat[0][2]["conclusion"], "failure")

    def _xet_mot_luot_khac_pr(self, *luot):
        d = du_lieu()
        lan_chay(d)[:] = [dict(lan_chay(d)[0], **x) for x in luot]
        gh = gate_app.GiaLap(d)
        chay(gh)
        return gh.da_phat[0][2]

    def test_luot_xanh_cua_pr_vao_base_la_khong_tinh(self):
        # PR vào nhánh khác mang workflow in pass, cùng SHA: lượt xanh đó không phải của PR này.
        q = self._xet_mot_luot_khac_pr({"pull_requests": thuoc_pr(9, "x")})
        self.assertEqual(q["conclusion"], "failure")
        self.assertTrue(q["output"]["title"].startswith("cho "))

    def test_luot_cua_chinh_pr_luc_con_base_khac_khong_tinh(self):
        self.assertEqual(self._xet_mot_luot_khac_pr({"pull_requests": thuoc_pr(7, "x")})["conclusion"], "failure")

    def test_luot_do_cua_pr_khac_cung_sha_khong_lam_ket(self):
        q = self._xet_mot_luot_khac_pr({}, {"conclusion": "failure", "pull_requests": thuoc_pr(9, "x")})
        self.assertEqual(q["conclusion"], "success")

    def test_luot_xanh_cua_pr_khac_cung_vao_goc_khong_tinh(self):
        # PR đã đóng có cùng SHA: lượt của nó không thay được lượt của PR này.
        self.assertEqual(self._xet_mot_luot_khac_pr({"pull_requests": thuoc_pr(9)})["conclusion"], "failure")

    def test_luot_khong_ghi_pr_thi_dong(self):
        for la in ({"pull_requests": []}, {"pull_requests": None}, {"pull_requests": [{"number": 7}]}):
            with self.subTest(la):
                self.assertEqual(self._xet_mot_luot_khac_pr(la)["conclusion"], "failure")

    def test_pr_fork_thieu_head_repository_thi_dong(self):
        d = du_lieu()
        la = {"full_name": "la/repo"}
        d["/pulls?state=open&base=main"][0]["head"]["repo"] = la
        d["/pulls/7"]["head"]["repo"] = la
        del lan_chay(d)[0]["head_repository"]
        gh = gate_app.GiaLap(d)
        chay(gh)
        self.assertEqual(gh.da_phat[0][2]["conclusion"], "failure")

    def test_khong_doc_du_luot_thi_dong(self):
        d = du_lieu()
        d["/actions/workflows/cong-nhanh.yml/runs?head_sha=%s&event=pull_request" % SHA]["total_count"] = 1200
        gh = gate_app.GiaLap(d)
        ma, _ = chay(gh)
        self.assertEqual((ma, gh.da_phat[0][2]["conclusion"]), (1, "failure"))

    def test_het_tran_trang_thi_bao_loi(self):
        class Day(gate_app.GiaLap):
            def goi(self, phuong, duong, body=None):
                return [{}] * 100
        with self.assertRaises(gate_app.LoiApi):
            gate_app._trang(Day({}), "/pulls/7/files", toi_da=3)

    def test_fork_da_xoa_lan_xanh_van_tinh(self):
        d = du_lieu()
        d["/pulls/7"]["head"]["repo"] = None
        gh = gate_app.GiaLap(d)
        chay(gh)
        self.assertEqual(gh.da_phat[0][2]["conclusion"], "success")

    def test_fork_da_xoa_khong_loc_duoc_thi_tinh_het(self):
        d = du_lieu()
        d["/pulls/7"]["head"]["repo"] = None
        lan_chay(d).append({"head_sha": SHA, "status": "completed", "conclusion": "failure"})
        gh = gate_app.GiaLap(d)
        chay(gh)
        self.assertEqual(gh.da_phat[0][2]["conclusion"], "failure")
        self.assertFalse(gh.da_phat[0][2]["output"]["title"].startswith("cho "))


class TestGiaLap(unittest.TestCase):
    def test_sai_query_la_loi(self):
        gh = gate_app.GiaLap(du_lieu())
        with self.assertRaises(gate_app.LoiApi):
            gh.goi("GET", "/actions/workflows/cong-nhanh.yml/runs?head_sha=%s" % SHA)

    def test_chi_trang_dau_co_du_lieu(self):
        gh = gate_app.GiaLap(du_lieu())
        self.assertTrue(gh.goi("GET", "/pulls/7/files?per_page=100&page=1"))
        self.assertEqual(gh.goi("GET", "/pulls/7/files?per_page=100&page=2"), [])


class GitHubDoiSha(gate_app.GiaLap):
    """Mỗi lần đọc /pulls/7 trả head kế tiếp trong danh sách."""

    def __init__(self, d, cac_sha):
        super().__init__(d)
        self.cac_sha = iter(cac_sha)

    def goi(self, phuong, duong, body=None):
        if duong == "/pulls/7":
            return dict(self.du_lieu[duong], head=dict(self.du_lieu[duong]["head"], sha=next(self.cac_sha)))
        return super().goi(phuong, duong, body)


class TestShaDoi(unittest.TestCase):
    """Lượt của SHA cũ chỉ được thu hồi check trên chính SHA cũ, không phát gì lên SHA mới: đó là việc của lượt SHA mới."""

    def _xet(self, cac_sha):
        gh = GitHubDoiSha(du_lieu(), cac_sha)
        ma, ra = chay(gh)
        return ma, ra, gh.da_phat

    def test_khong_doi_thi_phat(self):
        self.assertEqual([x[2]["head_sha"] for x in self._xet([SHA, SHA])[2]], [SHA])

    def _chi_thu_hoi(self, phat):
        self.assertEqual([(x[2]["head_sha"], x[2]["conclusion"]) for x in phat], [(SHA, "failure")])

    def test_da_doi_truoc_khi_doc_thi_chi_thu_hoi(self):
        ma, _, phat = self._xet([SHA_MOI])
        self.assertEqual(ma, 0)
        self._chi_thu_hoi(phat)

    def test_doi_giua_luc_doc_thi_chi_thu_hoi(self):
        ma, _, phat = self._xet([SHA, SHA_MOI])
        self.assertEqual(ma, 0)
        self._chi_thu_hoi(phat)


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

    def test_khong_doc_duoc_pr_van_phat_failure_tren_sha_su_kien(self):
        # `success` cũ không được ở lại khi lần xét mới hỏng.
        gh = GitHubHong(du_lieu(), "/pulls/7", gate_app.LoiApi("hỏng", 500))
        ma, _ = chay(gh)
        self.assertEqual(ma, 1)
        self.assertEqual([(x[2]["head_sha"], x[2]["conclusion"]) for x in gh.da_phat], [(SHA, "failure")])

    def test_sha_rac_tu_api_khong_len_check(self):
        d = du_lieu()
        d["/pulls/7"]["head"]["sha"] = "main"
        gh = gate_app.GiaLap(d)
        ma, _ = chay(gh)
        self.assertEqual(ma, 0)
        self.assertEqual([(x[2]["head_sha"], x[2]["conclusion"]) for x in gh.da_phat], [(SHA, "failure")])


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

    def test_loi_http_khong_mang_than_phan_hoi(self):
        def mo(yeu_cau, timeout):
            raise urllib.error.HTTPError(yeu_cau.full_url, 403, "x", {}, io.BytesIO(b"bi mat phan chieu"))

        with self.assertRaises(gate_app.LoiApi) as ng:
            self._gh(mo).goi("GET", "/pulls/1")
        self.assertEqual(ng.exception.ma, 403)
        self.assertNotIn("bi mat", str(ng.exception))
        self.assertNotIn(TOKEN, str(ng.exception))
        self.assertIn("bi mat", ng.exception.than)

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
        ma, ra = self._main(["--kho", str(MAU), "--sha", SHA])
        self.assertEqual(ma, 0)
        self.assertIn("CHẠY KHÔ", ra)
        self.assertIn("/check-runs", ra)

    def test_sha_rac_bi_tu_choi(self):
        for sha in ("", "main", "a" * 39, "A" * 40, SHA + "\n"):
            with self.subTest(repr(sha)):
                self.assertEqual(self._main(["--kho", str(MAU), "--sha", sha])[0], 2)

    def test_phai_co_sha(self):
        self.assertEqual(self._main(["--kho", str(MAU)])[0], 2)

    def test_tach_danh_sach_nguoi_duyet(self):
        with mock.patch.object(gate_app, "chay", return_value=0) as gia:
            self._main(["--kho", str(MAU), "--sha", SHA], {ten.BIEN_NGUOI_DUYET: "a, b  c,d\ne"})
        self.assertEqual(gia.call_args[0][1], ["a", "b", "c", "d", "e"])

    def test_doc_bien_moi_truong_theo_sha(self):
        env = {ten.BIEN_SHA: SHA, ten.BIEN_NGUOI_DUYET: "a, b  c"}
        ma, ra = self._main(["--kho", str(MAU)], env)
        self.assertEqual(ma, 0)
        self.assertIn("%s: success" % ten.CHECK_CUOI, ra)

    def test_khong_khai_nguoi_duyet_thi_failure(self):
        ma, ra = self._main(["--kho", str(MAU), "--sha", SHA])
        self.assertEqual(ma, 0)
        self.assertIn("%s: failure" % ten.CHECK_CUOI, ra)

    def test_thieu_token_khong_chay(self):
        ma, _ = self._main(["--sha", SHA], {"GITHUB_REPOSITORY": "chu/repo"})
        self.assertEqual(ma, 2)
