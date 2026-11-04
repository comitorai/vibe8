"""Lỗi tiêm đã áp lên chính app mẫu (PR nghiệm thu thật) không được làm bài cục bộ đỏ vì hạ tầng."""
import importlib.util
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

GOC = Path(__file__).resolve().parents[2]
_DAC_TA = importlib.util.spec_from_file_location("kiem_cuc_bo", GOC / "nghiem-thu/kiem_cuc_bo.py")
kiem_cuc_bo = importlib.util.module_from_spec(_DAC_TA)
_DAC_TA.loader.exec_module(kiem_cuc_bo)


class TestVeMauGoc(unittest.TestCase):
    def setUp(self):
        self._mau = kiem_cuc_bo.MAU
        self.addCleanup(setattr, kiem_cuc_bo, "MAU", self._mau)

    def _voi_ban_va(self, tam, ban_va):
        mau = Path(tam) / "mau"
        shutil.copytree(self._mau, mau, ignore=shutil.ignore_patterns("__pycache__"))
        subprocess.run(["git", "init", "-q"], cwd=mau, check=True)
        kiem_cuc_bo._ve_mau_goc(mau)  # Chính PR đang chạy có thể đã áp lỗi tiêm này lên app mẫu.
        subprocess.run(["git", "apply", str(kiem_cuc_bo.LOI / (ban_va + ".patch"))], cwd=mau, check=True)
        shutil.rmtree(mau / ".git")
        kiem_cuc_bo.MAU = mau

    def test_ban_va_da_ap_trong_mau_thi_van_thu_duoc_tren_ban_goc(self):
        for ban_va, nhanh in (("L1-logic", "đỏ"), ("L2-xoa-test", "xanh"), ("L5-day-thang", "xanh")):
            with tempfile.TemporaryDirectory() as tam:
                self._voi_ban_va(tam, ban_va)
                self.assertEqual(kiem_cuc_bo._xet(None)[1], "xanh", ban_va)
                du_lieu, ket = kiem_cuc_bo._xet(ban_va)
                self.assertEqual(ket, nhanh, ban_va)
                self.assertTrue(du_lieu["tep"], ban_va)

    def test_mau_hong_khac_voi_ban_va_van_do(self):
        with tempfile.TemporaryDirectory() as tam:
            self._voi_ban_va(tam, "L1-logic")
            tinh = kiem_cuc_bo.MAU / "hoa_don/tinh.py"
            tinh.write_text(tinh.read_text(encoding="utf-8") + "\nraise RuntimeError\n", encoding="utf-8")
            self.assertEqual(kiem_cuc_bo._xet(None)[1], "đỏ")


if __name__ == "__main__":
    unittest.main()
