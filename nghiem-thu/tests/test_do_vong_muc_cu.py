import importlib.util
import unittest
from pathlib import Path

_DAC_TA = importlib.util.spec_from_file_location(
    "do_vong", Path(__file__).resolve().parents[2] / "nghiem-thu/do_vong.py")
do_vong = importlib.util.module_from_spec(_DAC_TA)
_DAC_TA.loader.exec_module(do_vong)

NAY = "2026-03-01T00:00:00Z"


def pr(so, muc):
    return {"so": so, "mo": "2026-02-01T00:00:00Z", "merge": "2026-02-01T10:00:00Z", "muc": muc,
            "ly_do_chan": [], "nhan": [], "than": ""}


class TestMucCu(unittest.TestCase):
    """Cổng còn hai mức từ 06/11: bảng không in dòng mức cũ rỗng, còn PR mức cũ trong kỳ thì ghi rõ là mức cũ."""

    def test_ky_chi_co_muc_moi_khong_in_muc_cu(self):
        b = do_vong.bang(do_vong.tinh([pr(1, "thuong"), pr(2, "cao")], [], NAY, 30))
        self.assertIn("| Thời gian ra · thuong |", b)
        self.assertIn("| Thời gian ra · cao |", b)
        self.assertNotIn("thap", b)
        self.assertNotIn("trung_binh", b)

    def test_muc_moi_rong_van_in(self):
        b = do_vong.bang(do_vong.tinh([pr(1, "cao")], [], NAY, 30))
        self.assertIn("| Thời gian ra · thuong | không có PR |", b)

    def test_pr_muc_cu_con_trong_ky_ghi_ro_muc_cu(self):
        b = do_vong.bang(do_vong.tinh([pr(1, "thap"), pr(2, "cao")], [], NAY, 30))
        self.assertIn("| Thời gian ra · thap (mức cũ, trước 06/11) | trung vị 10.0 giờ", b)
        self.assertNotIn("trung_binh", b)


if __name__ == "__main__":
    unittest.main()
