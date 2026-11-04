import unittest

from hoa_don.tinh import tong_tien


class TestTongTien(unittest.TestCase):
    def test_cong_cac_dong(self):
        self.assertEqual(tong_tien([(10000, 2), (5000, 1)]), 25000)

    def test_giam_gia(self):
        self.assertEqual(tong_tien([(10000, 2)], 10), 18000)

    def test_giam_het(self):
        self.assertEqual(tong_tien([(10000, 2)], 100), 0)

    def test_lam_tron_xuong(self):
        self.assertEqual(tong_tien([(999, 1)], 50), 499)

    def test_gio_rong(self):
        self.assertEqual(tong_tien([]), 0)

    def test_tu_choi_giam_ngoai_khoang(self):
        for giam in (-1, 101):
            with self.assertRaises(ValueError):
                tong_tien([(1, 1)], giam)

    def test_tu_choi_so_am(self):
        with self.assertRaises(ValueError):
            tong_tien([(-1, 1)])
