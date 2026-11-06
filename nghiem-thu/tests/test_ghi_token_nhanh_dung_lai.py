"""Tên nhánh dùng lại: máy ghi token chỉ tính lượt gọi sau lúc PR trước cùng tên nhánh đóng."""
import contextlib
import importlib.util
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock


def _nap(ten):
    dac_ta = importlib.util.spec_from_file_location(ten, Path(__file__).resolve().parents[2] / ("nghiem-thu/%s.py" % ten))
    mo_dun = importlib.util.module_from_spec(dac_ta)
    dac_ta.loader.exec_module(mo_dun)
    return mo_dun


ghi_token = _nap("ghi_token")

GOC = "/nha/lab/repo"
DONG_CU = "2026-01-02T10:00:00Z"  # PR #3 cùng nhánh `a` đóng lúc này


def luot(id_, nhanh, luc, vao=10):
    return {"type": "assistant", "cwd": GOC, "gitBranch": nhanh, "sessionId": "p1", "timestamp": luc,
            "requestId": "r" + id_, "message": {"id": id_, "usage": {"input_tokens": vao}}}


def pr(so, dong=None, ref="a", tao=None):
    return {"number": so, "closed_at": dong, "created_at": tao, "head": {"ref": ref, "repo": {"full_name": "chu/repo"}},
            "base": {"ref": "main"}}


class GhGia:
    def __init__(self, cung_nhanh):
        self.cung_nhanh, self.ghi = cung_nhanh, []

    def che(self, s):
        return s

    def goi(self, phuong, duong, than=None):
        if phuong == "GET" and duong == "/pulls/9":
            return pr(9)
        if phuong == "GET" and duong.startswith("/pulls?"):
            self.hoi = duong
            return self.cung_nhanh
        if phuong == "GET":
            return []
        self.ghi.append((phuong, duong, than))
        return {}


class TestMoc(unittest.TestCase):
    def test_lay_pr_truoc_dong_muon_nhat(self):
        gh = GhGia([pr(9), pr(3, DONG_CU), pr(2, "2026-01-01T00:00:00Z"), pr(12, "2026-02-01T00:00:00Z")])
        self.assertEqual(ghi_token.moc_dung_lai(gh, "chu/repo", 9, "a"), (3, DONG_CU))
        self.assertIn("head=chu:a", gh.hoi)

    def test_nhanh_moi_khong_co_moc(self):
        self.assertIsNone(ghi_token.moc_dung_lai(GhGia([pr(9)]), "chu/repo", 9, "a"))
        self.assertIsNone(ghi_token.moc_dung_lai(GhGia([]), "chu/repo", 9, "a"))

    def test_bo_qua_muc_hong(self):
        gh = GhGia([None, {"number": "3", "closed_at": DONG_CU}, {"number": 4, "closed_at": 7}, pr(5, "")])
        self.assertIsNone(ghi_token.moc_dung_lai(gh, "chu/repo", 9, "a"))


    def test_pr_song_song_dong_sau_luc_pr_nay_tao_thi_khong_lam_moc(self):
        gh = GhGia([pr(9, tao="2026-01-02T11:00:00Z"), pr(8, "2026-01-02T12:00:00Z"), pr(3, DONG_CU)])
        self.assertEqual(ghi_token.moc_dung_lai(gh, "chu/repo", 9, "a"), (3, DONG_CU))
        gh = GhGia([pr(9, tao="2026-01-02T11:00:00Z"), pr(8, "2026-01-02T12:00:00Z")])
        self.assertIsNone(ghi_token.moc_dung_lai(gh, "chu/repo", 9, "a"))

    def test_pr_dong_dung_luc_pr_nay_tao_van_lam_moc(self):
        gh = GhGia([pr(9, tao=DONG_CU), pr(3, DONG_CU)])
        self.assertEqual(ghi_token.moc_dung_lai(gh, "chu/repo", 9, "a"), (3, DONG_CU))

    def test_ten_nhanh_ky_tu_dac_biet_duoc_ma_hoa(self):
        import urllib.parse
        for nhanh in ("fix#12", "a&state=open", "c++", "tinh/nang"):
            gh = GhGia([])
            ghi_token.moc_dung_lai(gh, "chu/repo", 9, nhanh)
            hoi = urllib.parse.parse_qs(urllib.parse.urlsplit("https://x" + gh.hoi).query)
            self.assertEqual(hoi["head"], ["chu:" + nhanh])
            self.assertEqual(hoi["state"], ["all"])
            self.assertEqual(hoi["per_page"], ["100"])


class TestSauLuc(unittest.TestCase):
    def cong(self, dong, sau_luc):
        with tempfile.TemporaryDirectory() as td:
            t = Path(td) / "p.jsonl"
            t.write_text("".join(json.dumps(d) + "\n" for d in dong))
            return ghi_token.cong_theo_nhanh([t], GOC, sau_luc=sau_luc)

    def test_bo_luot_cua_pr_cu_ca_viec_truoc_khi_tao_nhanh(self):
        dong = [luot("m1", "main", "2026-01-01T00:00:00Z", 1), luot("m2", "a", "2026-01-02T09:00:00Z", 2),
                luot("m3", "main", "2026-01-02T11:00:00Z", 40), luot("m4", "a", "2026-01-02T12:00:00Z", 300)]
        self.assertEqual(self.cong(dong, None)["a"]["moi"], 343)
        o = self.cong(dong, DONG_CU)["a"]
        self.assertEqual((o["moi"], o["moi_truoc"], o["luot"]), (340, 40, 2))

    def test_so_toi_giay_du_dinh_dang_khac_nhau(self):
        dong = [luot("m1", "a", "2026-01-02T10:00:00.900Z", 1), luot("m2", "a", "2026-01-02T10:00:01.000Z", 2)]
        self.assertEqual(self.cong(dong, DONG_CU)["a"]["moi"], 2)


class TestChay(unittest.TestCase):
    def chay(self, cung_nhanh):
        with tempfile.TemporaryDirectory() as td:
            cl, cx = Path(td) / "cl" / "-x", Path(td) / "cx"
            cl.mkdir(parents=True)
            cx.mkdir()
            dong = [luot("m1", "a", "2026-01-02T09:00:00Z", 7), luot("m2", "a", "2026-01-02T12:00:00Z", 300)]
            (cl / "p.jsonl").write_text("".join(json.dumps(d) + "\n" for d in dong))
            gh = GhGia(cung_nhanh)
            with mock.patch.dict(os.environ, {"GH_TOKEN": "ghs_abc"}), mock.patch.object(ghi_token, "GitHub", lambda *a: gh), \
                    contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                ma = ghi_token.main(["--repo", "chu/repo", "--pr", "9", "--goc", GOC, "--ban-ghi", str(cl.parent),
                                     "--ban-ghi-codex", str(cx)])
            return ma, gh.ghi[0][2]["body"] if gh.ghi else ""

    def test_nhanh_dung_lai_chi_tinh_sau_moc_va_ghi_moc(self):
        ma, than = self.chay([pr(9), pr(3, DONG_CU)])
        self.assertEqual(ma, 0)
        self.assertIn("token-moi: 300", than)
        self.assertIn("Chỉ tính lượt gọi sau 2026-01-02 10:00:00 UTC, lúc PR #3 cùng tên nhánh đóng.", than)

    def test_nhanh_moi_tinh_het_va_khong_ghi_moc(self):
        ma, than = self.chay([pr(9)])
        self.assertEqual(ma, 0)
        self.assertIn("token-moi: 307", than)
        self.assertNotIn("Chỉ tính lượt gọi sau", than)


if __name__ == "__main__":
    unittest.main()
