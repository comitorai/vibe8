import importlib.util
import unittest
from pathlib import Path

from cong import ten

_DAC_TA = importlib.util.spec_from_file_location(
    "do_nhip", Path(__file__).resolve().parents[2] / "nghiem-thu/do_nhip.py")
do_nhip = importlib.util.module_from_spec(_DAC_TA)
_DAC_TA.loader.exec_module(do_nhip)

PR = {"number": 7, "state": "closed", "created_at": "2026-01-01T00:00:00Z", "merged_at": "2026-01-01T00:02:00Z",
      "head": {"sha": "a" * 40}}


def check(giay, tieu_de):
    return {"completed_at": "2026-01-01T00:00:%02dZ" % giay, "output": {"title": tieu_de}, "app": {"slug": "cong"}}


def luot(ket, bat_dau="2026-01-01T00:00:01Z", xong="2026-01-01T00:00:11Z", trang_thai="completed"):
    return {"status": trang_thai, "conclusion": ket, "created_at": bat_dau, "run_started_at": bat_dau, "updated_at": xong,
            "path": ".github/workflows/%s.yml" % ten.CHECK_NHANH}


class TestChiSo(unittest.TestCase):
    def test_pr_tu_qua(self):
        d = do_nhip.chi_so(PR, [check(30, "cho_qua (thap)"), check(15, "cho (thap)")], [luot("success")], [])
        self.assertEqual(d["trang_thai"], "merged")
        self.assertEqual(d["mo_toi_cong"], 15)  # kết luận đầu, không theo thứ tự API trả
        self.assertEqual(d["muc"], "thap")  # mức theo kết luận mới nhất
        self.assertEqual(d["ci_giay"], 10)
        self.assertEqual(d["ci_do"], 0)
        self.assertEqual(d["mo_toi_merge"], 120)
        self.assertTrue(d["tu_qua"])

    def test_co_nguoi_duyet_khong_phai_tu_qua(self):
        duyet = [{"state": "COMMENTED", "submitted_at": "2026-01-01T00:00:50Z"},
                 {"state": "APPROVED", "submitted_at": "2026-01-01T00:01:00Z"}]
        d = do_nhip.chi_so(PR, [check(15, "cho_qua (cao)")], [luot("success")], duyet)
        self.assertEqual(d["mo_toi_duyet"], 60)
        self.assertFalse(d["tu_qua"])

    def test_luot_do_va_luot_dang_chay(self):
        d = do_nhip.chi_so(PR, [], [luot("failure"), luot("cancelled"), luot(None, trang_thai="in_progress")], [])
        self.assertEqual(d["ci_do"], 2)
        self.assertIsNone(d["mo_toi_cong"])
        self.assertIsNone(d["muc"])

    def test_pr_chua_merge_khong_tinh_tu_qua(self):
        d = do_nhip.chi_so(dict(PR, merged_at=None, state="open"), [], [], [])
        self.assertEqual(d["trang_thai"], "open")
        self.assertIsNone(d["mo_toi_merge"])
        self.assertFalse(d["tu_qua"])


class TestTongHop(unittest.TestCase):
    def test_trung_vi_va_ti_le(self):
        a = do_nhip.chi_so(PR, [check(10, "cho_qua (thap)")], [luot("success")], [])
        b = do_nhip.chi_so(dict(PR, merged_at=None, state="open"), [check(20, "chan (cao)")], [], [])
        t = do_nhip.tong_hop([a, b])
        self.assertEqual((t["so_pr"], t["so_merged"], t["so_tu_qua"], t["ti_le_tu_qua"]), (2, 1, 1, 1.0))
        self.assertEqual(t["trung_vi_mo_toi_cong"], 15)

    def test_rong_khong_loi(self):
        self.assertIsNone(do_nhip.tong_hop([])["ti_le_tu_qua"])


class GhGia:
    def __init__(self):
        self.duong = []

    def goi(self, phuong_thuc, duong, body=None):
        self.duong.append((phuong_thuc, duong))
        if "/check-runs" in duong:
            return {"check_runs": [check(10, "cho (thap)"),
                                   dict(check(1, "gia"), app={"slug": "github-actions"})]}
        if "/actions/runs" in duong:
            return {"workflow_runs": [luot("success"), dict(luot("failure"), path=".github/workflows/khac.yml")]}
        return []


class TestDocPr(unittest.TestCase):
    def test_chi_doc_va_loc_dung(self):
        gh = GhGia()
        d = do_nhip.doc_pr(gh, PR)
        self.assertEqual({p for p, _ in gh.duong}, {"GET"})
        self.assertTrue(any("filter=all" in x for _, x in gh.duong))  # mặc định API mất kết luận đầu
        self.assertEqual(d["mo_toi_cong"], 10)  # check của Actions cùng tên không tính
        self.assertEqual(d["ci_do"], 0)  # lượt đỏ của tệp workflow khác không tính


if __name__ == "__main__":
    unittest.main()
