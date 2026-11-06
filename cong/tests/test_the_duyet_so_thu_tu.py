import hashlib
import unittest

from cong import the_duyet
from cong.kiem_pr import quyet_dinh
from cong.tests.test_kiem_pr import pr, tep

PATCH_CONG = "@@ -1,2 +1,2 @@\n-CU = 1\n+MOI = 2"


class TestSoThuTuVaDauBam(unittest.TestCase):
    def test_dau_bam_la_8_hex_dau_cua_sha256_ten_goc(self):
        goc = "cong/%s%s.py" % ("p" * 120, "q" * 120)
        ten = the_duyet._ten(tep(goc), 3)
        self.assertTrue(ten.startswith("[3] "))
        self.assertTrue(ten.endswith(" #" + hashlib.sha256(goc.encode("utf-8")).hexdigest()[:8]))

    def test_ten_khong_bi_cat_khong_co_dau_bam(self):
        self.assertEqual(the_duyet._ten(tep("cong/kiem_pr.py"), 1), "[1] `cong/kiem_pr.py`")

    def test_cung_doi_tuong_hai_lan_mang_hai_so(self):
        # Tra số theo id() gán cả hai lần xuất hiện cùng một số; đếm theo vị trí thì không.
        t = tep("cong/kiem_pr.py", 1, 1, patch=PATCH_CONG)
        the = quyet_dinh(pr(ds_tep=[t, t]))["the_duyet"]
        self.assertIn("- [1] `cong/kiem_pr.py`", the)
        self.assertIn("- [2] `cong/kiem_pr.py`", the)
        self.assertIn("**[1] `cong/kiem_pr.py`**", the)
        self.assertIn("**[2] `cong/kiem_pr.py`**", the)


if __name__ == "__main__":
    unittest.main()
