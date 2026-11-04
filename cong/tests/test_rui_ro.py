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

    def test_tep_che_thu_vien_chuan_la_cao(self):
        for ten in ("sitecustomize.py", "usercustomize.py"):
            with self.subTest(ten):
                self.assertEqual(phan_loai([tep(ten)])["muc"], CAO)

    def test_them_tep_trung_mo_dun_chuan_la_cao(self):
        # A3, A4: `pprint.py` hay `tests/unittest.py` thêm vào là đủ làm CI xanh giả.
        for ten in ("unittest.py", "unittest/__init__.py", "pprint.py", "app/json.py", "tests/unittest.py",
                    "traceback.pyc", "signal.so"):
            with self.subTest(ten):
                self.assertEqual(phan_loai([tep(ten, "added")])["muc"], CAO)

    def test_doi_ten_thanh_mo_dun_chuan_la_cao(self):
        t = tep("pprint.py", "renamed", 0, 0, None, previous_filename="a.py")
        self.assertEqual(phan_loai([t])["muc"], CAO)

    def test_sua_tep_trung_ten_mo_dun_co_san_khong_oan(self):
        self.assertEqual(phan_loai([tep("app/json.py")])["muc"], THAP)

    def test_ten_gan_mo_dun_chuan_khong_oan(self):
        for ten in ("unittest/main.py", "pprint.md", "json.txt", "app/my_json.py"):
            with self.subTest(ten):
                self.assertEqual(phan_loai([tep(ten, "added")])["muc"], THAP)

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

    def test_anh_va_phong_chu_la_trung_binh(self):
        for ten in ("a.png", "b.JPG", "c.woff2", "d.pdf"):
            with self.subTest(ten):
                self.assertEqual(phan_loai([tep(ten, "added", 0, 0, None)])["muc"], TRUNG_BINH)

    def test_tep_khong_co_diff_chu_la_cao(self):
        # Không đọc được thì người phải xem: gồm tệp nhị phân lạ và tệp rỗng che mô-đun.
        for ten, trang_thai in (("du_lieu.bin", "added"), ("hoa_don/tinh/__init__.py", "added"), ("du_lieu.bin", "modified")):
            with self.subTest(ten):
                self.assertEqual(phan_loai([tep(ten, trang_thai, 0, 0, None)])["muc"], CAO)

    def test_ma_may_la_cao_o_moi_trang_thai_tru_xoa(self):
        # `.pyc` hash-based đứng thay `.py` mà không so với mã nguồn. Đổi tên từ tệp ảnh cũng không có patch.
        for ten in ("hoa_don/__pycache__/tinh.cpython-314.pyc", "tests/__pycache__/__init__.cpython-314.pyc",
                    "hoa_don/tinh.abi3.so", "HOA_DON/TINH.PYD", "a.wasm"):
            for trang_thai, them_truong in (("added", {}), ("modified", {}), ("copied", {}),
                                            ("renamed", {"previous_filename": "a.png"})):
                with self.subTest(ten=ten, trang_thai=trang_thai):
                    self.assertEqual(phan_loai([tep(ten, trang_thai, 0, 0, None, **them_truong)])["muc"], CAO)
        self.assertEqual(phan_loai([tep("cu.pyc", "removed", 0, 0, None)])["muc"], THAP)

    def test_doi_ten_thuan_ma_thuong_la_thap(self):
        t = tep("b.py", "renamed", 0, 0, None, previous_filename="a.py")
        self.assertEqual(phan_loai([t])["muc"], THAP)

    def test_trang_thai_la_thuong_la_trung_binh(self):
        self.assertEqual(phan_loai([tep("a.py", "changed", 0, 0, None)])["muc"], TRUNG_BINH)


class TestPhuThuoc(unittest.TestCase):
    def test_moi_tep_khai_phu_thuoc_la_cao(self):
        for ten in ("package.json", "web/package.json", "pyproject.toml", "go.mod", "requirements.txt",
                    "requirements-dev.txt", "setup.py", "setup.cfg", "Cargo.toml", "Gemfile", "composer.json",
                    "Pipfile", ".npmrc", "pnpm-workspace.yaml", ".nvmrc", "pom.xml", "build.gradle", "app/build.gradle.kts",
                    "settings.gradle", "settings.gradle.kts", "pdm.lock"):
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


class TestManifest(unittest.TestCase):
    def test_doi_ten_lockfile_manifest_ra_ngoai_van_cao(self):
        for cu in ("yarn.lock", "web/package.json", "requirements.txt"):
            with self.subTest(cu):
                t = tep("docs/cu.txt", "renamed", 0, 0, None, previous_filename=cu)
                self.assertEqual(phan_loai([t])["muc"], CAO)

    def test_tep_doi_moi_truong_chay_la_cao(self):
        for ten in ("requirements.txt", "requirements-dev.txt", "requirements/ci.txt", "requirements/ci.in", "a/requirements.in",
                    "constraints.txt", "constraints-ci.txt", "Dockerfile", "docker/Dockerfile.ci", ".python-version",
                    ".tool-versions", ".pre-commit-config.yaml", "web/package.json", "PIPFILE"):
            with self.subTest(ten):
                self.assertEqual(phan_loai([tep(ten)])["muc"], CAO)

    def test_khong_nham_ten_gan_giong(self):
        for ten in ("docs/requirements.md", "requirements/ghi-chu.md", "my-dockerfile-notes/a.py", "constraints.md"):
            with self.subTest(ten):
                self.assertEqual(phan_loai([tep(ten)])["muc"], THAP)


class TestTestCoSan(unittest.TestCase):
    """Chỉ thêm tệp test mới là tự qua: mọi cách đụng test có sẵn đều phải có người xem."""

    def test_xoa_tep_test(self):
        for ten in ("tests/test_a.py", "a_test.go", "web/a.spec.ts", "src/__tests__/a.js", "app/tests.py",
                    "testing/x.py", "test.py", "a.test.js", "a-test.rs", "test_a.py", "testx.py",
                    "src/FooTest.java", "FooTests.cs", "UserSpec.rb", "a_test.swift", "a_tests.go"):
            with self.subTest(ten):
                r = phan_loai([tep(ten, "removed", 0, 5, "@@ -1,5 +0,0 @@\n-x")])
                self.assertEqual(r["muc"], CAO)
                self.assertIn("test có sẵn", r["ly_do"][0])

    def test_ten_gan_giong_khong_phai_test(self):
        for ten in ("latest.py", "contest.py", "docs/spec.md", "inspect.py", "testdata.csv", "Contest.java",
                    "ProductSpec.md", "docs/LoadTest.pdf"):
            with self.subTest(ten):
                self.assertEqual(phan_loai([tep(ten, "removed", 0, 5, "@@ -1,5 +0,0 @@\n-x")])["muc"], THAP)

    def test_doi_ten_test_deu_cao(self):
        # Đổi tên trong vùng test làm hỏng khớp mẫu của trình chạy test, test đó lặng lẽ không chạy nữa.
        for moi, cu in (("docs/a.txt", "tests/test_a.py"), ("tests/b_tests.py", "tests/test_a.py"),
                        ("tests/test_b.py", "tests/test_a.py"), ("tests/test_a.py", "docs/a.py")):
            with self.subTest(moi):
                t = tep(moi, "renamed", 0, 0, None, previous_filename=cu)
                self.assertEqual(phan_loai([t])["muc"], CAO)

    def test_moi_cach_sua_test_co_san_deu_cao(self):
        for p, them, xoa in (("@@ -1,3 +1 @@\n-a\n-b\n-c\n+d", 1, 3),
                             ("@@ -1 +1 @@\n-    assert g()\n+    x = 1", 1, 1),
                             ("@@ -1 +1 @@\n-    assertEqual(f(), 1)\n+    assertEqual(f(), 2)", 1, 1),
                             ("@@ -1 +1 @@\n-    # assert g()\n+    x = 1", 1, 1),
                             ("@@ -1 +1,2 @@\n+    @unittest.skip('x')", 1, 0),
                             ("@@ -1 +1,2 @@\n+    def test_moi(self):\n+        self.assertTrue(f())", 2, 0)):
            with self.subTest(p):
                self.assertEqual(phan_loai([tep("tests/test_a.py", them=them, xoa=xoa, patch=p)])["muc"], CAO)

    def test_sua_test_khong_co_diff_la_cao(self):
        for status in ("modified", "changed"):
            with self.subTest(status):
                self.assertEqual(phan_loai([tep("tests/test_a.py", status, 0, 0, None)])["muc"], CAO)

    def test_them_tep_test_moi_la_thap(self):
        p = "@@ -0,0 +1,2 @@\n+def test_moi():\n+    assert f()"
        for ten in ("tests/test_moi.py", "a_test.go", "src/FooTest.java"):
            with self.subTest(ten):
                self.assertEqual(phan_loai([tep(ten, "added", 2, 0, p)])["muc"], THAP)

    def test_tep_test_rong_moi_can_duyet(self):
        # Không có diff nên không biết bên trong là gì; muốn tự qua thì tệp phải có nội dung đọc được.
        self.assertEqual(phan_loai([tep("tests/test_moi.py", "added", 0, 0, None)])["muc"], CAO)

    def test_init_trong_vung_test_la_cao(self):
        # `load_tests` trong `__init__.py` quyết định test nào được nạp, thêm mới cũng đủ tắt cả gói test.
        self.assertEqual(phan_loai([tep("tests/__init__.py", "added", 3, 0, "@@ -0,0 +1 @@\n+x")])["muc"], CAO)

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


class TestVungTestRong(unittest.TestCase):
    def _sua(self, duong):
        return rui_ro.phan_loai([{"filename": duong, "status": "modified", "additions": 1, "deletions": 1, "patch": "@@"}])["muc"]

    def test_du_lieu_ky_vong_va_test_cac_ngon_ngu_can_duyet(self):
        for duong in ("src/__snapshots__/a.test.js.snap", "pkg/testdata/golden.json", "__fixtures__/a.json", "fixtures/a.json", "a/__snapshots__/b.txt",
                      "integration_tests/helpers.py", "foo_test.dart", "x.bats", "test_x.sh", "a_test.exs", "a_test.cpp",
                      "TestFoo.java", "src/TestBar.kt", "cypress/integration/x.cy.js", "spec/models/user_spec.rb", "specs/a.py"):
            with self.subTest(duong):
                self.assertEqual(self._sua(duong), rui_ro.CAO)

    def test_ten_gan_giong_khong_phai_test(self):
        for duong in ("src/latest.sh", "contest.c", "src/Testing.ts", "Testimonial.txt", "hoa_don/snapshot.py"):
            with self.subTest(duong):
                self.assertEqual(self._sua(duong), rui_ro.THAP)

    def test_goi_trung_ten_trinh_chay_test_can_duyet(self):
        for duong in ("pytest.py", "pytest/__init__.py", "_pytest/__init__.py"):
            with self.subTest(duong):
                tep = {"filename": duong, "status": "added", "additions": 1, "deletions": 0, "patch": "@@"}
                self.assertEqual(rui_ro.phan_loai([tep])["muc"], rui_ro.CAO)
