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
    # Người duyệt là ai có quyền admin: danh sách này là phía GitHub trả về, không phải cấu hình.
    if isinstance(gh, gate_app.GiaLap):
        gh.du_lieu.update({"/collaborators/%s/permission" % x: {"permission": "admin"} for x in nguoi_tin})
    ra = io.StringIO()
    with contextlib.redirect_stdout(ra):
        ma = gate_app.chay(gh, sha)
    return ma, ra.getvalue()


def lan_chay(d):
    return d["/actions/workflows/cong-nhanh.yml/runs?head_sha=%s&event=pull_request" % SHA]["workflow_runs"]


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
        lan_chay(d).append(dict(lan_chay(d)[0], conclusion="failure"))
        gh = gate_app.GiaLap(d)
        chay(gh)
        self.assertEqual(gh.da_phat[0][2]["conclusion"], "failure")

    def test_duyet_hop_le_qua_duong_api(self):
        gh = gate_app.GiaLap(can_duyet(du_lieu()))
        chay(gh)
        self.assertEqual(gh.da_phat[0][2]["conclusion"], "success")

    def test_quyen_ghi_khong_duyet_duoc(self):
        for quyen in ("write", "maintain", "read", "none"):
            with self.subTest(quyen):
                d = can_duyet(du_lieu())
                d["/collaborators/khac/permission"] = {"permission": quyen}
                gh = gate_app.GiaLap(d)
                chay(gh, nguoi_tin=())
                self.assertEqual(gh.da_phat[0][2]["conclusion"], "failure")
                self.assertIn("không có quyền admin", gh.da_phat[0][2]["output"]["summary"])

    def test_nguoi_la_gop_y_khong_chan_duoc(self):
        d = can_duyet(du_lieu(), state="CHANGES_REQUESTED")
        d["/collaborators/khac/permission"] = {"permission": "read"}
        d["/pulls/7/files"][0]["filename"] = "app.py"
        gh = gate_app.GiaLap(d)
        chay(gh, nguoi_tin=())
        self.assertEqual(gh.da_phat[0][2]["conclusion"], "success")

    def test_admin_yeu_cau_sua_thi_chan(self):
        d = can_duyet(du_lieu(), state="CHANGES_REQUESTED")
        d["/pulls/7/files"][0]["filename"] = "app.py"
        gh = gate_app.GiaLap(d)
        chay(gh)
        self.assertEqual(gh.da_phat[0][2]["conclusion"], "failure")

    def test_khong_doc_duoc_quyen_thi_dong(self):
        for ma in (403, 404, 500):
            with self.subTest(ma):
                gh = GitHubHong(can_duyet(du_lieu()), "/collaborators/", gate_app.LoiApi("hỏng", ma))
                self.assertEqual(chay(gh, nguoi_tin=())[0], 1)
                self.assertEqual(gh.da_phat[0][2]["conclusion"], "failure")

    def test_nguoi_xet_khong_con_tai_khoan_khong_lam_sap(self):
        d = can_duyet(du_lieu())
        d["/pulls/7/reviews"][0]["user"] = None
        gh = gate_app.GiaLap(d)
        self.assertEqual(chay(gh, nguoi_tin=())[0], 0)
        self.assertEqual(gh.da_phat[0][2]["conclusion"], "failure")

    def test_bot_gop_y_khong_hoi_quyen_khong_lam_ket_cong(self):
        # GitHub trả 404 «is not a user» cho vài tài khoản bot: hỏi quyền của chúng sẽ làm mọi PR có bot góp ý kẹt.
        for login, loai in (("Copilot", "Bot"), ("github-actions[bot]", "Bot")):
            with self.subTest(login):
                d = can_duyet(du_lieu(), login=login)
                d["/pulls/7/reviews"][0]["user"]["type"] = loai
                d["/pulls/7/files"][0]["filename"] = "app.py"
                gh = gate_app.GiaLap(d)
                chay(gh, nguoi_tin=())
                self.assertEqual(gh.da_phat[0][2]["conclusion"], "success")

    def test_khong_doc_bien_nguoi_duyet_cu(self):
        d = can_duyet(du_lieu())
        d["/collaborators/khac/permission"] = {"permission": "write"}
        gh = gate_app.GiaLap(d)
        with mock.patch.dict(os.environ, {"XUONG_NGUOI_DUYET": "khac"}):
            chay(gh, nguoi_tin=())
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
        d["/pulls/7"]["head"]["label"] = "la:nhanh"
        d["/pulls?state=all&head=la:nhanh"] = d.pop("/pulls?state=all&head=chu:nhanh")
        lan_chay(d)[0].update(head_repository=la)
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
        lan_chay(d)[0].update(head_repository={"full_name": "la/repo"})
        gh = gate_app.GiaLap(d)
        chay(gh)
        self.assertTrue(gh.da_phat[0][2]["output"]["title"].startswith("cho "))
        self.assertEqual(gh.da_phat[0][2]["conclusion"], "failure")

    def _xet(self, *luot, doi_base=(), doi_tu_dong=(), pr_khac=()):
        d = du_lieu()
        lan_chay(d)[:] = [dict(lan_chay(d)[0], **x) for x in luot]
        d["/issues/7/events"] += [{"event": "base_ref_changed", "created_at": luc} for luc in doi_base]
        d["/issues/7/events"] += [{"event": "automatic_base_change_succeeded", "created_at": luc} for luc in doi_tu_dong]
        d["/pulls?state=all&head=chu:nhanh"] += [{"number": 9, "created_at": a, "closed_at": b} for a, b in pr_khac]
        gh = gate_app.GiaLap(d)
        chay(gh)
        return gh.da_phat[0][2]

    def _cho(self, q):
        self.assertEqual(q["conclusion"], "failure")
        self.assertTrue(q["output"]["title"].startswith("cho "), q["output"]["title"])

    def test_pr_tung_doi_base_thi_khong_luot_nao_tinh(self):
        # L8 trên GitHub thật: lượt tạo 2 giây sau khi đổi base vẫn chạy ref merge của base cũ, base đó có workflow in pass.
        for luot in ({}, {"created_at": "2026-11-01T00:00:20Z"}, {"created_at": "2026-12-01T00:00:00Z"}):
            self._cho(self._xet(luot, doi_base=("2026-11-01T00:00:10Z",)))
        self._cho(self._xet({"created_at": "2026-11-01T00:00:20Z"}, doi_base=("2026-11-01T00:00:03Z", "2026-11-01T00:00:10Z")))

    def test_su_kien_doi_base_o_trang_hai_van_tinh(self):
        # Sự kiện như `deployed` tích thêm mỗi lượt, nên đổi base có thể nằm ngoài trang đầu.
        d = du_lieu()
        d["/issues/7/events"] = [{"event": "deployed", "created_at": "2026-11-01T00:00:11Z"}] * 100

        class HaiTrang(gate_app.GiaLap):
            def goi(self, phuong_thuc, duong, body=None):
                if phuong_thuc == "GET" and duong.endswith("/issues/7/events?per_page=100&page=2"):
                    return [{"event": "base_ref_changed", "created_at": "2026-11-01T00:00:10Z"}]
                return super().goi(phuong_thuc, duong, body)

        gh = HaiTrang(d)
        chay(gh)
        self._cho(gh.da_phat[0][2])

    def test_su_kien_khac_sau_doi_base_khong_mo_lai(self):
        # Gắn nhãn sau khi đổi base không được xoá dấu đổi base.
        d = du_lieu()
        d["/issues/7/events"] += [{"event": "base_ref_changed", "created_at": "2026-11-01T00:00:10Z"}, {"event": "labeled", "created_at": "2026-11-01T00:00:11Z"}]
        gh = gate_app.GiaLap(d)
        chay(gh)
        self._cho(gh.da_phat[0][2])

    def test_trang_thieu_muc_van_doc_trang_sau(self):
        d = du_lieu()
        d["/issues/7/events"] = [{"event": "deployed", "created_at": "2026-11-01T00:00:11Z"}] * 99

        class ThieuMuc(gate_app.GiaLap):
            def goi(self, phuong_thuc, duong, body=None):
                if phuong_thuc == "GET" and duong.endswith("/issues/7/events?per_page=100&page=2"):
                    return [{"event": "base_ref_changed", "created_at": "2026-11-01T00:00:10Z"}]
                return super().goi(phuong_thuc, duong, body)

        gh = ThieuMuc(d)
        chay(gh)
        self._cho(gh.da_phat[0][2])

    def test_su_kien_khac_tren_pr_khong_chan(self):
        d = du_lieu()
        d["/issues/7/events"] += [{"event": "renamed", "created_at": "2026-11-01T00:00:10Z"}, {"event": "deployed", "created_at": "2026-11-01T00:00:11Z"}]
        gh = gate_app.GiaLap(d)
        chay(gh)
        self.assertEqual(gh.da_phat[0][2]["conclusion"], "success")

    def test_luot_truoc_khi_mo_pr_khong_tinh(self):
        self._cho(self._xet({"created_at": "2026-10-31T23:59:59Z"}))

    def test_github_tu_doi_base_cung_chan(self):
        # Nhánh cha merge và xoá: GitHub không ghi base_ref_changed. Ref merge cũng có thể còn của nhánh cha.
        self._cho(self._xet({}, doi_tu_dong=("2026-11-01T00:00:10Z",)))
        self._cho(self._xet({"created_at": "2026-11-01T00:00:20Z"}, doi_tu_dong=("2026-11-01T00:00:10Z",)))

    def test_nhanh_tung_co_pr_khac_thi_khong_luot_nao_tinh(self):
        # PR đóng rồi vẫn sinh lượt: sửa tiêu đề, hoặc lượt tạo trễ hơn lúc đóng. Thời điểm không phân biệt được, nên mọi PR khác đều chặn.
        for pr in (("2026-11-01T00:00:01Z", None), ("2026-11-01T00:00:01Z", "2026-11-01T00:00:09Z"),
                   ("2026-10-01T00:00:00Z", "2026-10-02T00:00:00Z"), ("2026-11-01T00:00:30Z", None), (None, None)):
            self._cho(self._xet({}, pr_khac=(pr,)))

    def test_luot_do_tren_main_khong_bi_luot_cua_pr_khac_giau(self):
        # Lượt đỏ trên main, lượt xanh sau của PR đã đóng vào base lạ: không ra success, cũng không phát chữ sai là lỗi test.
        self._cho(self._xet({"conclusion": "failure"}, {"created_at": "2026-11-02T00:00:00Z"},
                            pr_khac=(("2026-11-01T00:00:01Z", "2026-11-01T00:00:03Z"),)))

    def test_tim_nhanh_khong_ra_chinh_pr_thi_dong(self):
        d = du_lieu()
        d["/pulls?state=all&head=chu:nhanh"][:] = []
        gh = gate_app.GiaLap(d)
        chay(gh)
        self._cho(gh.da_phat[0][2])

    def test_luot_cung_sha_tu_nhanh_khac_khong_tinh(self):
        self._cho(self._xet({"head_branch": "nhanh-khac"}))
        self.assertEqual(self._xet({}, {"head_branch": "nhanh-khac", "conclusion": "failure"})["conclusion"], "success")

    def test_thieu_du_lieu_thoi_gian_thi_dong(self):
        # Thiếu mốc nào cũng ra 0 lượt: không có dữ liệu thì không được tính là xanh.
        self._cho(self._xet({"created_at": None}))
        self._cho(self._xet({"head_branch": None}))
        self._cho(self._xet({}, doi_base=(None,)))

    def test_truong_pull_requests_khong_con_tac_dung(self):
        la = [{"number": 9, "base": {"ref": "x"}}]
        self.assertEqual(self._xet({"pull_requests": la})["conclusion"], "success")
        self.assertEqual(self._xet({"pull_requests": []})["conclusion"], "success")

    def test_thieu_created_at_cua_pr_thi_dong(self):
        d = du_lieu()
        del d["/pulls/7"]["created_at"]
        gh = gate_app.GiaLap(d)
        chay(gh)
        self._cho(gh.da_phat[0][2])

    def test_nhanh_co_ky_tu_dac_biet_duoc_ma_hoa(self):
        d = du_lieu()
        d["/pulls/7"]["head"].update(label="chu:a&state=open", ref="a&state=open")
        lan_chay(d)[0]["head_branch"] = "a&state=open"
        d["/pulls?state=all&head=chu:a%26state%3Dopen"] = d.pop("/pulls?state=all&head=chu:nhanh")
        gh = gate_app.GiaLap(d)
        chay(gh)
        self.assertEqual(gh.da_phat[0][2]["conclusion"], "success")

    def test_khong_doc_duoc_su_kien_thi_bao_loi(self):
        d = du_lieu()
        del d["/issues/7/events"]
        gh = gate_app.GiaLap(d)
        ma, _ = chay(gh)
        self.assertEqual((ma, gh.da_phat[0][2]["conclusion"]), (1, "failure"))

    def test_pr_fork_thieu_head_repository_thi_dong(self):
        d = du_lieu()
        la = {"full_name": "la/repo"}
        d["/pulls?state=open&base=main"][0]["head"]["repo"] = la
        d["/pulls/7"]["head"]["repo"] = la
        d["/pulls/7"]["head"]["label"] = "la:nhanh"
        d["/pulls?state=all&head=la:nhanh"] = d.pop("/pulls?state=all&head=chu:nhanh")
        del lan_chay(d)[0]["head_repository"]
        gh = gate_app.GiaLap(d)
        chay(gh)
        self.assertEqual(gh.da_phat[0][2]["conclusion"], "failure")

    def test_trang_vuot_tran_ghi_total_count_0_van_bao_loi(self):
        # API thật: quá 1000 lượt thì trang 11 trả rỗng và total_count 0.
        class Tran(gate_app.GiaLap):
            def goi(self, phuong, duong, body=None):
                so = int(duong.rsplit("=", 1)[1])
                return {"total_count": 1001, "workflow_runs": [{}] * 100} if so <= 10 else {"total_count": 0, "workflow_runs": []}
        with self.assertRaises(gate_app.LoiApi):
            gate_app._trang(Tran({}), "/runs?x=1", "workflow_runs")

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

    def test_fork_da_xoa_thi_khong_co_luot_nao_tinh_duoc(self):
        # Không còn repo đầu để so: PR này chỉ qua được khi mở lại từ nhánh còn tồn tại.
        d = du_lieu()
        d["/pulls/7"]["head"]["repo"] = None
        lan_chay(d)[0]["head_repository"] = None  # GitHub cũng để trống ở lượt: None == None không được tính là khớp.
        gh = gate_app.GiaLap(d)
        chay(gh)
        self._cho(gh.da_phat[0][2])


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
        trang = {1: [{"n": i} for i in range(100)], 2: [{"n": 100}], 3: []}

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

    def test_doc_bien_moi_truong_theo_sha(self):
        ma, ra = self._main(["--kho", str(MAU)], {ten.BIEN_SHA: SHA})
        self.assertEqual(ma, 0)
        self.assertIn("%s: success" % ten.CHECK_CUOI, ra)

    def test_thieu_token_khong_chay(self):
        ma, _ = self._main(["--sha", SHA], {"GITHUB_REPOSITORY": "chu/repo"})
        self.assertEqual(ma, 2)


class TestVungNhayCam(unittest.TestCase):
    def _chay(self, noi_dung):
        import tempfile
        with tempfile.TemporaryDirectory() as thu_muc:
            duong = os.path.join(thu_muc, "vung.txt")
            Path(duong).write_bytes(noi_dung)
            gh = gate_app.GiaLap(du_lieu())
            gh.du_lieu.update({"/collaborators/%s/permission" % x: {"permission": "admin"} for x in ("khac", "tac-gia")})
            ra = io.StringIO()
            with contextlib.redirect_stdout(ra):
                ma = gate_app.chay(gh, SHA, duong)
            return ma, gh.da_phat[-1][2]

    def test_vung_khai_tren_nhanh_goc_lam_pr_can_duyet(self):
        ma, body = self._chay(b"# quyen\nhoa_don/\n")
        self.assertEqual((ma, body["conclusion"], body["output"]["title"]), (0, "failure", "chan (cao)"))
        self.assertIn("Vùng nhạy cảm đã khai:** 1 mẫu", body["output"]["summary"])

    def test_tep_vung_hong_thi_khong_qua(self):
        ma, body = self._chay(b"\xff\xfe")
        self.assertEqual((ma, body["conclusion"]), (1, "failure"))
        self.assertIn("UTF-8", body["output"]["summary"])  # người xem check phải thấy lý do, không chỉ «0 mẫu»

    def test_main_doc_tep_vung_cua_repo(self):
        with mock.patch.object(gate_app, "chay", return_value=0) as gia:
            gate_app.main(["--kho", str(MAU), "--sha", SHA])
        self.assertEqual(gia.call_args.args[2], ten.TEP_VUNG)
        self.assertTrue(ten.TEP_VUNG.startswith("cong/"))  # workflow chỉ lấy /cong/ của nhánh gốc
