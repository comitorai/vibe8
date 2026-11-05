import contextlib
import importlib.util
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from cong.gate_app import LoiApi


def _nap(ten):
    dac_ta = importlib.util.spec_from_file_location(ten, Path(__file__).resolve().parents[2] / ("nghiem-thu/%s.py" % ten))
    mo_dun = importlib.util.module_from_spec(dac_ta)
    dac_ta.loader.exec_module(mo_dun)
    return mo_dun


ghi_token = _nap("ghi_token")
do_vong = _nap("do_vong")

GOC = "/nha/lab/repo"


def luot(id_, nhanh, luc, cwd=GOC, phien="p1", vao=10, tao=100, ra=5, doc=1000, req=None):
    return {"type": "assistant", "cwd": cwd, "gitBranch": nhanh, "sessionId": phien, "timestamp": luc,
            "requestId": req or "r" + id_,
            "message": {"id": id_, "usage": {"input_tokens": vao, "cache_creation_input_tokens": tao,
                                             "output_tokens": ra, "cache_read_input_tokens": doc}}}


class ThuMuc:
    def __enter__(self):
        self._td = tempfile.TemporaryDirectory()
        self.goc = Path(self._td.name)
        return self

    def __exit__(self, *a):
        self._td.cleanup()

    def tep(self, ten, dong):
        t = self.goc / ten
        t.parent.mkdir(parents=True, exist_ok=True)
        t.write_text("\n".join(d if isinstance(d, str) else json.dumps(d) for d in dong) + "\n")
        return t


class TestCong(unittest.TestCase):
    def cong(self, *dong, goc_nhanh=("main",)):
        with ThuMuc() as tm:
            return ghi_token.cong_theo_nhanh([tm.tep("a.jsonl", dong)], GOC, goc_nhanh)

    def test_mot_luot_goi_nhieu_dong_chi_tinh_mot_lan(self):
        k = self.cong(luot("m1", "x", "2026-01-01T00:00:01Z"), luot("m1", "x", "2026-01-01T00:00:02Z"),
                      luot("m2", "x", "2026-01-01T00:00:03Z"))
        self.assertEqual(k["x"], {"phien": 1, "luot": 2, "moi": 230, "doc_dem": 2000, "moi_truoc": 0})

    def test_trung_qua_hai_tep_chi_tinh_mot_lan(self):
        with ThuMuc() as tm:
            a = tm.tep("a.jsonl", [luot("m1", "x", "2026-01-01T00:00:01Z")])
            b = tm.tep("b/c.jsonl", [luot("m1", "x", "2026-01-01T00:00:01Z")])
            self.assertEqual(ghi_token.cong_theo_nhanh([a, b], GOC)["x"]["luot"], 1)

    def test_chi_lay_cwd_trong_repo(self):
        k = self.cong(luot("m1", "x", "2026-01-01T00:00:01Z", cwd=GOC + "/.claude/worktrees/w"),
                      luot("m2", "x", "2026-01-01T00:00:02Z", cwd=GOC + "-khac"),
                      luot("m3", "x", "2026-01-01T00:00:03Z", cwd="/nha/lab"),
                      luot("m4", "x", "2026-01-01T00:00:04Z", cwd=None))
        self.assertEqual(k["x"]["luot"], 1)

    def test_viec_o_main_truoc_khi_tao_nhanh_tinh_cho_nhanh_ke_tiep(self):
        k = self.cong(luot("m0", "HEAD", "2026-01-01T00:00:00Z"),
                      luot("m1", "main", "2026-01-01T00:00:01Z"),
                      luot("m2", "a", "2026-01-01T00:00:02Z"),
                      luot("m3", "main", "2026-01-01T00:00:03Z"),
                      luot("m4", "b", "2026-01-01T00:00:04Z"),
                      luot("m5", "main", "2026-01-01T00:00:05Z"))  # sau nhánh cuối: không tính cho nhánh nào
        self.assertEqual((k["a"]["luot"], k["a"]["moi_truoc"]), (3, 230))
        self.assertEqual((k["b"]["luot"], k["b"]["moi_truoc"]), (2, 115))
        self.assertNotIn("main", k)
        self.assertNotIn("HEAD", k)

    def test_thu_tu_theo_gio_khong_theo_dong(self):
        k = self.cong(luot("m2", "a", "2026-01-01T00:00:02Z"), luot("m1", "main", "2026-01-01T00:00:01Z"))
        self.assertEqual(k["a"]["moi_truoc"], 115)

    def test_main_cua_phien_khac_khong_gan_cho_nhanh(self):
        k = self.cong(luot("m1", "main", "2026-01-01T00:00:01Z", phien="p2"), luot("m2", "a", "2026-01-01T00:00:02Z"))
        self.assertEqual(k["a"]["moi_truoc"], 0)

    def test_nhanh_goc_khac_main(self):
        k = self.cong(luot("m1", "dev", "2026-01-01T00:00:01Z"), luot("m2", "a", "2026-01-01T00:00:02Z"),
                      goc_nhanh=("dev",))
        self.assertEqual(k["a"]["moi_truoc"], 115)

    def test_dong_hong_va_so_la_khong_lam_hong(self):
        xau = luot("m3", "x", "2026-01-01T00:00:03Z")
        xau["message"]["usage"].update(input_tokens=-5, output_tokens="9", cache_creation_input_tokens=None)
        k = self.cong("{khong phai json", "[]", "null", {"type": "user"},
                      dict(luot("m1", "x", "2026-01-01T00:00:01Z"), timestamp=None),
                      dict(luot("m2", "x", "2026-01-01T00:00:02Z"), requestId=None),
                      xau)
        self.assertEqual((k["x"]["luot"], k["x"]["moi"]), (1, 0))

    def test_dem_phien(self):
        k = self.cong(luot("m1", "x", "2026-01-01T00:00:01Z"), luot("m2", "x", "2026-01-01T00:00:02Z", phien="p2"))
        self.assertEqual(k["x"]["phien"], 2)


class TestCacTep(unittest.TestCase):
    def test_moi_thu_muc_co_nhac_repo_va_du_moi(self):
        with ThuMuc() as tm:
            co = tm.tep("-nha-khac/a.jsonl", [luot("m1", "x", "t")])
            tm.tep("-nha-khac/b.jsonl", [luot("m1", "x", "t", cwd="/nha/khac")])
            cu = tm.tep("-nha-lab-repo/c.jsonl", [luot("m1", "x", "t")])
            os.utime(cu, (1000, 1000))
            self.assertEqual(ghi_token.cac_tep(GOC, tm.goc, 2000), [co])

    def test_khong_co_thu_muc(self):
        self.assertEqual(ghi_token.cac_tep(GOC, "/khong/co/that", 0), [])


def du_lieu(**may):
    return {k: dict({"phien": 1, "luot": 2, "moi": 3, "doc_dem": 4, "moi_truoc": 0}, **v) for k, v in may.items()}


class TestComment(unittest.TestCase):
    def test_ghi_roi_doc_lai_va_do_vong_doc_duoc(self):
        than = ghi_token.than_comment("a", du_lieu(mn={"moi": 100, "luc": "2026-01-01 10:00"}, mb={"moi": 23}))
        self.assertEqual(ghi_token.doc_comment(than)["mn"]["moi"], 100)
        self.assertEqual(ghi_token.doc_comment(than)["mn"]["luc"], "2026-01-01 10:00")
        self.assertIn("token-moi: 123", than)
        self.assertEqual(do_vong.doc_token([{"body": than, "author_association": "OWNER"}]), 123)

    def test_du_lieu_hong_hay_la_bi_bo(self):
        self.assertEqual(ghi_token.doc_comment("<!-- du-lieu {hong} -->"), {})
        self.assertEqual(ghi_token.doc_comment("<!-- du-lieu [1] -->"), {})
        d = ghi_token.doc_comment('<!-- du-lieu {"a": {"phien": 1, "luot": true, "moi": 1, "doc_dem": 1, "moi_truoc": 0},'
                                  ' "b": {"phien": 1}, "c": 5} -->')
        self.assertEqual(d, {})

    def test_ten_may_khong_pha_duoc_comment(self):
        d = ghi_token.doc_comment(ghi_token.than_comment("a", du_lieu(**{"x --> <b>y|": {}})))
        self.assertEqual(list(d), ["x -- by"])
        than = ghi_token.than_comment("a`|<b>", du_lieu(m={}))
        self.assertIn("`ab`", than)

    def test_comment_cu_chi_tin_nguoi_trong_repo(self):
        than = ghi_token.than_comment("a", du_lieu(m={}))
        ds = [{"id": 1, "body": than, "author_association": "NONE", "updated_at": "2026-01-03"},
              {"id": 2, "body": than, "author_association": "OWNER", "updated_at": "2026-01-01"},
              {"id": 3, "body": than, "author_association": "COLLABORATOR", "updated_at": "2026-01-02"},
              {"id": 4, "body": "khac", "author_association": "OWNER", "updated_at": "2026-01-04"}]
        self.assertEqual(ghi_token.comment_cu(ds)["id"], 3)
        self.assertIsNone(ghi_token.comment_cu(ds[:1]))
        self.assertIsNone(do_vong.doc_token(ds[:1]))  # người ngoài dán số giả: không tính


class GhGia:
    def __init__(self, comment=(), loi_sua=None, pr=None):
        self.comment, self.loi_sua, self.ghi = list(comment), loi_sua, []
        self.pr = pr or {"number": 9, "head": {"ref": "a", "repo": {"full_name": "chu/repo"}}, "base": {"ref": "main"}}

    def che(self, s):
        return s

    def goi(self, phuong_thuc, duong, body=None):
        if phuong_thuc == "GET" and duong.startswith("/pulls/"):
            return self.pr
        if phuong_thuc == "GET" and duong.startswith("/pulls?"):
            self.hoi_head = duong
            return [dict(self.pr, created_at="2026-01-01"), dict(self.pr, number=3, created_at="2025-01-01")]
        if phuong_thuc == "GET":
            return self.comment
        if phuong_thuc == "PATCH" and self.loi_sua:
            raise LoiApi("sửa", self.loi_sua)
        self.ghi.append((phuong_thuc, duong, body))
        return {}


class TestChay(unittest.TestCase):
    def chay(self, gh, *them):
        with ThuMuc() as tm:
            tm.tep("-x/p.jsonl", [luot("m1", "main", "2026-01-01T00:00:01Z"), luot("m2", "a", "2026-01-01T00:00:02Z")])
            ra, loi = io.StringIO(), io.StringIO()
            with mock.patch.dict(os.environ, {"GH_TOKEN": "ghs_abc"}), mock.patch.object(ghi_token, "GitHub", lambda *a: gh), \
                    contextlib.redirect_stdout(ra), contextlib.redirect_stderr(loi):
                ma = ghi_token.main(["--repo", "chu/repo", "--pr", "9", "--goc", GOC, "--ban-ghi", str(tm.goc), *them])
            return ma, ra.getvalue(), loi.getvalue()

    def test_ghi_moi_khi_chua_co(self):
        gh = GhGia()
        ma, ra, _ = self.chay(gh)
        self.assertEqual(ma, 0)
        self.assertEqual([(p, d) for p, d, _ in gh.ghi], [("POST", "/issues/9/comments")])
        self.assertIn("token-moi: 230", gh.ghi[0][2]["body"])
        self.assertIn("token mới 230", ra)

    def test_sua_comment_cu_giu_dong_may_khac(self):
        cu = {"id": 5, "author_association": "OWNER", "body": ghi_token.than_comment("a", du_lieu(**{"may-kia": {"moi": 1000}}))}
        gh = GhGia([cu])
        self.assertEqual(self.chay(gh)[0], 0)
        self.assertEqual(gh.ghi[0][:2], ("PATCH", "/issues/comments/5"))
        self.assertIn("token-moi: 1230", gh.ghi[0][2]["body"])

    def test_comment_cua_nguoi_khac_khong_sua_duoc_thi_ghi_moi(self):
        cu = {"id": 5, "author_association": "MEMBER", "body": ghi_token.than_comment("a", du_lieu(m={}))}
        gh = GhGia([cu], loi_sua=403)
        self.assertEqual(self.chay(gh)[0], 0)
        self.assertEqual(gh.ghi[0][0], "POST")

    def test_loi_khac_thi_dung(self):
        cu = {"id": 5, "author_association": "OWNER", "body": ghi_token.than_comment("a", du_lieu(m={}))}
        gh = GhGia([cu], loi_sua=500)
        self.assertEqual(self.chay(gh)[0], 1)
        self.assertEqual(gh.ghi, [])

    def test_chay_kho_khong_ghi(self):
        gh = GhGia()
        ma, ra, _ = self.chay(gh, "--kho")
        self.assertEqual((ma, gh.ghi), (0, []))
        self.assertIn("token-moi: 230", ra)

    def test_khong_co_luot_goi_thi_khong_ghi(self):
        gh = GhGia(pr={"number": 9, "head": {"ref": "khac", "repo": {"full_name": "chu/repo"}}, "base": {"ref": "main"}})
        ma, _, loi = self.chay(gh)
        self.assertEqual((ma, gh.ghi), (1, []))
        self.assertIn("không có lượt gọi", loi)

    def test_pr_tu_repo_khac_thi_dung(self):
        gh = GhGia(pr={"number": 9, "head": {"ref": "a", "repo": {"full_name": "la/repo"}}, "base": {"ref": "main"}})
        self.assertEqual(self.chay(gh)[0], 1)
        self.assertEqual(gh.ghi, [])

    def test_tim_pr_theo_nhanh_lay_pr_moi_nhat(self):
        gh = GhGia()
        self.assertEqual(ghi_token.tim_pr(gh, "chu/repo", None, "a"), (9, "a", "main"))
        self.assertIn("head=chu:a", gh.hoi_head)

    def test_token_co_ky_tu_la_khong_chay_khong_in(self):
        loi = io.StringIO()
        with mock.patch.dict(os.environ, {"GH_TOKEN": "ghs_bimat\ngia"}), contextlib.redirect_stderr(loi):
            self.assertEqual(ghi_token.main(["--repo", "chu/repo"]), 2)
        self.assertNotIn("bimat", loi.getvalue())


if __name__ == "__main__":
    unittest.main()
