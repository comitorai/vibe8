import contextlib
import io
import unittest

from hoa_don.__main__ import main


class TestDongLenh(unittest.TestCase):
    def test_in_tong(self):
        ra = io.StringIO()
        with contextlib.redirect_stdout(ra):
            self.assertEqual(main(["10000x2", "5000x1", "--giam", "10"]), 0)
        self.assertEqual(ra.getvalue().strip(), "22500")

    def test_loi_tra_ma_khac_khong(self):
        loi = io.StringIO()
        with contextlib.redirect_stderr(loi):
            self.assertEqual(main(["10000x2", "--giam", "200"]), 1)
        self.assertIn("giảm giá", loi.getvalue())
