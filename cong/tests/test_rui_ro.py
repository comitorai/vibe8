import unittest

from cong import rui_ro
from cong.rui_ro import CAO, THAP, TRUNG_BINH, phan_loai


def tep(ten, status="modified", them=1, xoa=0, patch="@@ -1 +1 @@\n+x", **them_khoa):
    d = {"filename": ten, "status": status, "additions": them, "deletions": xoa, "patch": patch}
    d.update(them_khoa)
    return d


class TestMuc(unittest.TestCase):
    def test_ma_thuong_la_thap(self):
        self.assertEqual(phan_loai([tep("hoa_don/tinh.py")])["muc"], THAP)

    def test_pr_rong_la_thap(self):
        self.assertEqual(phan_loai([])["muc"], THAP)

    def test_khong_phai_danh_sach_la_cao(self):
        self.assertEqual(phan_loai(None)["muc"], CAO)

    def test_tep_cong_la_cao(self):
        for ten in (".github/workflows/a.yml", ".github/CODEOWNERS", "CODEOWNERS", "docs/CODEOWNERS",
                    "xuong.yml", "luat/luat.yml", "cong/kiem_pr.py", "kiem-tra.sh", "scripts/check.sh",
                    "Makefile", "conftest.py", "vitest.config.ts", "nghiem-thu/app-mau/.github/workflows/x.yml",
                    "nghiem-thu/kiem_cuc_bo.py", "nghiem-thu/bat_cong.py", "nghiem-thu/loi/L1-logic.patch"):
            with self.subTest(ten):
                self.assertEqual(phan_loai([tep(ten)])["muc"], CAO)

    def test_khong_nham_ten_gan_giong(self):
        for ten in ("docs/github.md", "src/cong/x.py", "checklist.md", "my.github.io/a.md", "xuong.yml.md"):
            with self.subTest(ten):
                self.assertEqual(phan_loai([tep(ten)])["muc"], THAP)

    def test_lach_chu_hoa_va_chu_rong(self):
        for ten in (".GitHub/workflows/a.yml", "CodeOwners", "ＸＵＯＮＧ.yml", ".ｇｉｔｈｕｂ/a.yml"):
            with self.subTest(ten):
                self.assertEqual(phan_loai([tep(ten)])["muc"], CAO)

    def test_doi_ten_ra_khoi_vung_cong_van_cao(self):
        t = tep("docs/cu.yml", "renamed", 0, 0, None, previous_filename=".github/workflows/cong-cuoi.yml")
        self.assertEqual(phan_loai([t])["muc"], CAO)

    def test_doi_ten_vao_vung_cong_la_cao(self):
        t = tep(".github/workflows/x.yml", "renamed", 0, 0, None, previous_filename="docs/x.yml")
        self.assertEqual(phan_loai([t])["muc"], CAO)

    def test_app_mau_van_co_ca_rui_ro_thap(self):
        self.assertEqual(phan_loai([tep("nghiem-thu/app-mau/hoa_don/tinh.py")])["muc"], THAP)

    def test_lockfile_la_cao(self):
        self.assertEqual(phan_loai([tep("web/pnpm-lock.yaml")])["muc"], CAO)

    def test_lockfile_khong_ha_muc_cao(self):
        self.assertEqual(phan_loai([tep("yarn.lock"), tep("CODEOWNERS")])["muc"], CAO)

    def test_tep_nhi_phan_la_trung_binh(self):
        self.assertEqual(phan_loai([tep("a.png", "added", 0, 0, None)])["muc"], TRUNG_BINH)

    def test_doi_ten_thuan_ma_thuong_la_thap(self):
        t = tep("b.py", "renamed", 0, 0, None, previous_filename="a.py")
        self.assertEqual(phan_loai([t])["muc"], THAP)

    def test_trang_thai_la_thuong_la_trung_binh(self):
        self.assertEqual(phan_loai([tep("a.py", "changed", 0, 0, None)])["muc"], TRUNG_BINH)


class TestPhuThuoc(unittest.TestCase):
    def test_moi_tep_khai_phu_thuoc_la_cao(self):
        for ten in ("package.json", "web/package.json", "pyproject.toml", "go.mod", "requirements.txt",
                    "requirements-dev.txt", "setup.py", "setup.cfg", "Cargo.toml", "Gemfile", "composer.json",
                    "Pipfile", ".npmrc", "pnpm-workspace.yaml"):
            with self.subTest(ten):
                self.assertEqual(phan_loai([tep(ten)])["muc"], CAO)

    def test_lockfile_khong_tinh_vao_co(self):
        r = phan_loai([tep("web/Yarn.lock", them=5000, xoa=5000), tep("a.py", them=3)])
        self.assertEqual(r["so_dong"], 3)
        self.assertFalse(r["qua_co"])

    def test_tep_thuong_trung_ten_gan_giong_lockfile_van_tinh_co(self):
        self.assertTrue(phan_loai([tep("yarn.lock.txt", them=500)])["qua_co"])

    def test_ten_khong_phai_chuoi_khong_lam_hong_cach_dem(self):
        self.assertEqual(phan_loai([tep(7, them=5)])["so_dong"], 5)


class TestGiamTest(unittest.TestCase):
    def test_xoa_tep_test(self):
        for ten in ("tests/test_a.py", "a_test.go", "web/a.spec.ts", "src/__tests__/a.js", "app/tests.py",
                    "testing/x.py", "test.py", "a.test.js", "a-test.rs"):
            with self.subTest(ten):
                t = tep(ten, "removed", 0, 5, "@@ -1,5 +0,0 @@\n-x")
                r = phan_loai([t])
                self.assertEqual(r["muc"], CAO)
                self.assertIn("xoá test", r["ly_do"][0])

    def test_ten_gan_giong_khong_phai_test(self):
        for ten in ("latest.py", "contest.py", "docs/spec.md", "inspect.py", "testdata.csv"):
            with self.subTest(ten):
                self.assertEqual(phan_loai([tep(ten, "removed", 0, 5, "@@ -1,5 +0,0 @@\n-x")])["muc"], THAP)

    def test_doi_ten_test_ra_ngoai(self):
        t = tep("docs/a.txt", "renamed", 0, 0, None, previous_filename="tests/test_a.py")
        self.assertEqual(phan_loai([t])["muc"], CAO)

    def test_doi_ten_trong_vung_test_khong_cao(self):
        t = tep("tests/test_b.py", "renamed", 0, 0, None, previous_filename="tests/test_a.py")
        self.assertEqual(phan_loai([t])["muc"], THAP)

    def test_giam_dong_rong(self):
        t = tep("tests/test_a.py", them=1, xoa=3, patch="@@ -1,3 +1 @@\n-a\n-b\n-c\n+d")
        self.assertEqual(phan_loai([t])["muc"], CAO)

    def test_giam_khang_dinh_du_so_dong_khong_doi(self):
        p = "@@ -1,2 +1,2 @@\n-    self.assertEqual(f(), 1)\n-    assert g()\n+    x = 1\n+    y = 2"
        t = tep("tests/test_a.py", them=2, xoa=2, patch=p)
        r = phan_loai([t])
        self.assertEqual(r["muc"], CAO)
        self.assertIn("khẳng định", r["ly_do"][0])

    def test_chu_thich_hoa_khang_dinh_la_giam(self):
        for moi in ("# assert g()", "    // expect(a)", "x = 1  # assert g()"):
            with self.subTest(moi):
                p = "@@ -1 +1 @@\n-    assert g()\n+" + moi
                self.assertEqual(phan_loai([tep("tests/test_a.py", them=1, xoa=1, patch=p)])["muc"], CAO)

    def test_bo_chu_thich_co_chu_assert_khong_phai_giam(self):
        p = "@@ -1 +1 @@\n-    # assert g()\n+    x = 1"
        self.assertEqual(phan_loai([tep("tests/test_a.py", them=1, xoa=1, patch=p)])["muc"], THAP)

    def test_them_bo_qua_test(self):
        for dong in ("@unittest.skip('x')", "self.skipTest('x')", "it.only('a', f)", "xit('a', f)",
                     "@pytest.mark.xfail"):
            with self.subTest(dong):
                t = tep("tests/test_a.py", patch="@@ -1 +1,2 @@\n+    " + dong)
                self.assertEqual(phan_loai([t])["muc"], CAO)

    def test_them_test_binh_thuong_la_thap(self):
        p = "@@ -1 +1,2 @@\n+    def test_moi(self):\n+        self.assertTrue(f())"
        self.assertEqual(phan_loai([tep("tests/test_a.py", them=2, patch=p)])["muc"], THAP)

    def test_test_khong_co_patch_la_cao(self):
        self.assertEqual(phan_loai([tep("tests/test_a.py", them=900, xoa=0, patch=None)])["muc"], CAO)

    def test_xoa_ma_thuong_khong_tinh_la_xoa_test(self):
        t = tep("hoa_don/cu.py", "removed", 0, 5, "@@ -1,5 +0,0 @@\n-x")
        self.assertEqual(phan_loai([t])["muc"], THAP)


class TestTenLa(unittest.TestCase):
    def test_ten_la_la_cao(self):
        for ten in ("a\nb.py", "a\tb", "::error::x\n.py", "../ngoai.py", "a/../b.py", "/tuyet-doi.py",
                    "a\\b.py", "", None, 7, "a//b.py", "a\u202eb.py", "a\u200bb.py", "x\x1b[31m.py"):
            with self.subTest(repr(ten)):
                self.assertEqual(phan_loai([tep(ten)])["muc"], CAO)

    def test_ten_cu_la_cung_bi_bat(self):
        t = tep("a.py", "renamed", 0, 0, None, previous_filename="b\n.py")
        self.assertEqual(phan_loai([t])["muc"], CAO)

    def test_tieng_viet_khong_phai_ten_la(self):
        self.assertEqual(phan_loai([tep("tài-liệu/ghi chú.md")])["muc"], THAP)

    def test_ly_do_khong_giu_ky_tu_dieu_khien(self):
        ly_do = "\n".join(phan_loai([tep("x\n::add-mask::`a\u202e")])["ly_do"])
        self.assertNotIn("\n::", ly_do)
        self.assertNotIn("\u202e", ly_do)
        self.assertEqual(ly_do.count("`"), 2)

    def test_hien_thi_cat_ten_dai(self):
        self.assertLess(len(rui_ro.hien_thi("a" * 5000)), 300)


class TestCo(unittest.TestCase):
    def test_dung_nguong_khong_qua_co(self):
        self.assertFalse(phan_loai([tep("a.py", them=200, xoa=200)])["qua_co"])

    def test_qua_nguong_cong_nhieu_tep(self):
        r = phan_loai([tep("a.py", them=300), tep("b.py", them=100, xoa=1)])
        self.assertEqual(r["so_dong"], 401)
        self.assertTrue(r["qua_co"])

    def test_so_dong_khong_hop_le_la_cao(self):
        for sai in (-1, None, "9", True, 1.5):
            with self.subTest(repr(sai)):
                self.assertEqual(phan_loai([tep("a.py", them=sai)])["muc"], CAO)

    def test_phan_tu_khong_phai_tu_dien_la_cao(self):
        self.assertEqual(phan_loai(["a.py"])["muc"], CAO)
