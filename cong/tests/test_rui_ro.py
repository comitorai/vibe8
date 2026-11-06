import importlib
import pkgutil
import sys
import unittest
from unittest import mock

from cong import rui_ro
from cong.rui_ro import CAO, THUONG, phan_loai


def tep(ten, status="modified", them=1, xoa=0, patch="@@ -1 +1 @@\n+x", **them_khoa):
    d = {"filename": ten, "status": status, "additions": them, "deletions": xoa, "patch": patch}
    d.update(them_khoa)
    return d


class TestMuc(unittest.TestCase):
    def test_ma_thuong_la_vua(self):
        self.assertEqual(phan_loai([tep("hoa_don/tinh.py")])["muc"], THUONG)

    def test_pr_rong_la_thuong(self):
        self.assertEqual(phan_loai([])["muc"], THUONG)

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

    def test_symlink_trung_mo_dun_chuan_la_cao(self):
        # GitHub trả symlink mới đúng dạng này: một dòng thêm, patch là đích, không có mode.
        for ten in ("json", "unittest", "app/argparse", "JSON"):
            with self.subTest(ten):
                self.assertEqual(phan_loai([tep(ten, "added", 1, 0, "@@ -0,0 +1 @@\n+evilpkg")])["muc"], CAO)

    def test_doi_ten_thanh_symlink_mo_dun_chuan_la_cao(self):
        # Đổi tên thuần: 0 dòng thay đổi, vẫn có thể là symlink.
        self.assertEqual(phan_loai([tep("json", "renamed", 0, 0, None, previous_filename="evilpkg")])["muc"], CAO)

    def test_tep_nhieu_dong_khong_duoi_khong_oan(self):
        for ten in ("bin/code", "scripts/trace", "token", "secrets"):
            with self.subTest(ten):
                self.assertNotEqual(phan_loai([tep(ten, "added", 2, 0)])["muc"], CAO)

    def test_ten_co_chu_hoa_trong_danh_sach_chuan(self):
        self.assertEqual(phan_loai([tep("cProfile.py", "added")])["muc"], CAO)

    def test_tep_ten_test_tu_qua_tren_moi_ban_python(self):
        for ten in ("test.py", "tests/test.py", "bin/test"):
            with self.subTest(ten):
                self.assertNotEqual(phan_loai([tep(ten, "added")])["muc"], CAO)

    def _nap_nhu_python_39(self, **gia):
        self.addCleanup(importlib.reload, rui_ro)
        with mock.patch.object(sys, "stdlib_module_names", None, create=True), mock.patch.object(pkgutil, "iter_modules", **gia):
            importlib.reload(rui_ro)

    def test_python_cu_quet_thu_muc_va_bo_test(self):
        self.addCleanup(importlib.reload, rui_ro)
        with mock.patch.object(sys, "stdlib_module_names", None, create=True):
            importlib.reload(rui_ro)
        for ten in ("subprocess", "unicodedata", "cprofile"):
            self.assertIn(ten, rui_ro._MO_DUN_CHUAN)
        self.assertNotIn("test", rui_ro._MO_DUN_CHUAN)

    def test_python_cu_quet_rong_van_giu_ten_co_ban(self):
        self._nap_nhu_python_39(return_value=[])
        self.assertEqual(rui_ro.phan_loai([tep("json.py", "added")])["muc"], CAO)

    def test_ten_khong_duoi_khac_khong_oan(self):
        for ten in ("LICENSE", "docs/VERSION", "evilpkg"):
            with self.subTest(ten):
                self.assertNotEqual(phan_loai([tep(ten, "added")])["muc"], CAO)

    def test_python_cu_van_du_danh_sach_mo_dun_chuan(self):
        # Trên 3.9 danh sách phải lấy được từ thư mục thư viện chuẩn, gồm cả mô-đun biên dịch.
        for ten in ("unicodedata", "subprocess", "re", "os", "sys", "json", "pytest"):
            with self.subTest(ten):
                self.assertIn(ten, rui_ro._MO_DUN_CHUAN)
                self.assertEqual(phan_loai([tep(ten + ".py", "added")])["muc"], CAO)
        self.assertNotIn("site-packages", rui_ro._MO_DUN_CHUAN)

    def test_doi_ten_thanh_mo_dun_chuan_la_cao(self):
        t = tep("pprint.py", "renamed", 0, 0, None, previous_filename="a.py")
        self.assertEqual(phan_loai([t])["muc"], CAO)

    def test_sua_tep_trung_ten_mo_dun_co_san_khong_oan(self):
        self.assertNotEqual(phan_loai([tep("app/json.py")])["muc"], CAO)

    def test_ten_gan_mo_dun_chuan_khong_oan(self):
        for ten in ("unittest/main.py", "pprint.md", "json.txt", "app/my_json.py"):
            with self.subTest(ten):
                self.assertNotEqual(phan_loai([tep(ten, "added")])["muc"], CAO)

    def test_khong_nham_ten_gan_giong(self):
        for ten in ("docs/github.md", "src/cong/x.py", "checklist.md", "my.github.io/a.md", "xuong.yml.md"):
            with self.subTest(ten):
                self.assertNotEqual(phan_loai([tep(ten)])["muc"], CAO)

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

    def test_app_mau_van_co_ca_rui_ro_thuong(self):
        self.assertNotEqual(phan_loai([tep("nghiem-thu/app-mau/hoa_don/tinh.py")])["muc"], CAO)

    def test_lockfile_la_cao(self):
        self.assertEqual(phan_loai([tep("web/pnpm-lock.yaml")])["muc"], CAO)

    def test_lockfile_khong_ha_muc_cao(self):
        self.assertEqual(phan_loai([tep("yarn.lock"), tep("CODEOWNERS")])["muc"], CAO)

    def test_anh_va_phong_chu_la_thuong(self):
        for ten in ("a.png", "b.JPG", "c.woff2", "d.pdf"):
            with self.subTest(ten):
                self.assertEqual(phan_loai([tep(ten, "added", 0, 0, None)])["muc"], THUONG)

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
        self.assertNotEqual(phan_loai([tep("cu.pyc", "removed", 0, 0, None)])["muc"], CAO)

    def test_doi_ten_thuan_ma_thuong_khong_oan(self):
        t = tep("b.py", "renamed", 0, 0, None, previous_filename="a.py")
        self.assertNotEqual(phan_loai([t])["muc"], CAO)

    def test_trang_thai_la_thuong_la_muc_thuong(self):
        self.assertEqual(phan_loai([tep("a.py", "changed", 0, 0, None)])["muc"], THUONG)

    def test_tep_khai_moi_truong_chay_khac_la_cao(self):
        for ten in (".yarnrc", ".pnpmfile.cjs", ".ruby-version", "rust-toolchain", "rust-toolchain.toml", "bunfig.toml", ".bun-version"):
            with self.subTest(ten):
                self.assertEqual(phan_loai([tep(ten, "added", 5, 0)])["muc"], CAO)

    def test_tep_khai_moi_truong_chay_la_cao(self):
        for ten in (".node-version", ".yarnrc.yml", "web/.yarnrc.yml", ".nvmrc"):
            with self.subTest(ten):
                self.assertEqual(phan_loai([tep(ten)])["muc"], CAO)

    def test_tai_lieu_bao_mat_la_cao(self):
        self.assertEqual(phan_loai([tep("docs/bao-mat.md")])["muc"], CAO)
        self.assertEqual(phan_loai([tep("docs/khac.md")])["muc"], THUONG)


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
                self.assertNotEqual(phan_loai([tep(ten)])["muc"], CAO)


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
                self.assertNotEqual(phan_loai([tep(ten, "removed", 0, 5, "@@ -1,5 +0,0 @@\n-x")])["muc"], CAO)

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

    def test_them_tep_test_moi_la_thuong(self):
        p = "@@ -0,0 +1,2 @@\n+def test_moi():\n+    assert f()"
        for ten in ("tests/test_moi.py", "a_test.go", "src/FooTest.java"):
            with self.subTest(ten):
                self.assertEqual(phan_loai([tep(ten, "added", 2, 0, p)])["muc"], THUONG)

    def test_tep_test_rong_moi_can_duyet(self):
        # Không có diff nên không biết bên trong là gì; muốn tự qua thì tệp phải có nội dung đọc được.
        self.assertEqual(phan_loai([tep("tests/test_moi.py", "added", 0, 0, None)])["muc"], CAO)

    def test_init_trong_vung_test_la_cao(self):
        # `load_tests` trong `__init__.py` quyết định test nào được nạp, thêm mới cũng đủ tắt cả gói test.
        self.assertEqual(phan_loai([tep("tests/__init__.py", "added", 3, 0, "@@ -0,0 +1 @@\n+x")])["muc"], CAO)

    def test_xoa_ma_thuong_khong_tinh_la_xoa_test(self):
        t = tep("hoa_don/cu.py", "removed", 0, 5, "@@ -1,5 +0,0 @@\n-x")
        self.assertNotEqual(phan_loai([t])["muc"], CAO)


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
        self.assertEqual(phan_loai([tep("tài-liệu/ghi chú.md")])["muc"], THUONG)

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
                self.assertNotEqual(self._sua(duong), rui_ro.CAO)

    def test_goi_trung_ten_trinh_chay_test_can_duyet(self):
        for duong in ("pytest.py", "pytest/__init__.py", "_pytest/__init__.py"):
            with self.subTest(duong):
                tep = {"filename": duong, "status": "added", "additions": 1, "deletions": 0, "patch": "@@"}
                self.assertEqual(rui_ro.phan_loai([tep])["muc"], rui_ro.CAO)


class TestMucVua(unittest.TestCase):
    """luat/phuong-phap.md mục 2 (hai mức từ 06/11): tài liệu, tệp tĩnh, test mới, mã và cấu hình chạy được đều là Thường."""

    def test_ma_va_cau_hinh_chay_duoc_la_vua(self):
        for ten in ("hoa_don/tinh.py", "src/app.ts", "bin/chay", "config/app.json", "web/logo.svg", "CMakeLists.txt", "a.sql"):
            for trang_thai in ("added", "modified", "removed"):
                with self.subTest(ten=ten, trang_thai=trang_thai):
                    self.assertEqual(phan_loai([tep(ten, trang_thai)])["muc"], THUONG)

    def test_doi_ten_ma_la_vua(self):
        t = tep("b.py", "renamed", 0, 0, None, previous_filename="a.py")
        self.assertEqual(phan_loai([t])["muc"], THUONG)

    def test_doi_tai_lieu_thanh_ma_la_vua(self):
        t = tep("chay.sh", "renamed", 0, 0, None, previous_filename="ghi-chu.md")
        self.assertEqual(phan_loai([t])["muc"], THUONG)

    def test_tai_lieu_va_test_moi_van_thuong(self):
        for t in (tep("docs/a.md"), tep("LICENSE"), tep("README.rst", "removed"), tep("ghi chú.txt"),
                  tep("tests/test_moi.py", "added"), tep("a.png", "removed", 0, 0, None)):
            with self.subTest(t["filename"]):
                self.assertEqual(phan_loai([t])["muc"], THUONG)

    def test_ten_gan_tai_lieu_van_la_vua(self):
        for ten in ("readme.sh", "license.py", "docs/a.md.py", "LICENSE/x.js"):
            with self.subTest(ten):
                self.assertEqual(phan_loai([tep(ten)])["muc"], THUONG)

    def test_ly_do_vua_gop_mot_dong(self):
        rr = phan_loai([tep("a%d.py" % i) for i in range(30)])
        self.assertEqual(len([x for x in rr["ly_do"] if "chạy được" in x]), 1)
        self.assertIn("30 tệp", " ".join(rr["ly_do"]))


class TestVungNhayCam(unittest.TestCase):
    """Repo tự khai mẫu đường dẫn nhạy cảm (quyền, xoá dữ liệu, migration, thanh toán): chạm vào là mức Cao."""

    VUNG = ["src/quyen/", "db/migrations/*", "*thanh_toan*"]

    def test_cham_vung_la_cao(self):
        for ten in ("src/quyen/vai_tro.py", "SRC/Quyen/a.ts", "db/migrations/0001.sql", "db/migrations/a/b.sql",
                    "app/thanh_toan/the.py", "docs/thanh_toan.md"):
            with self.subTest(ten):
                rr = phan_loai([tep(ten)], self.VUNG)
                self.assertEqual(rr["muc"], CAO)
                self.assertTrue(any("vùng nhạy cảm" in x for x in rr["ly_do"]))

    def test_doi_ten_ra_khoi_vung_van_cao(self):
        t = tep("src/khac.py", "renamed", 0, 0, None, previous_filename="src/quyen/a.py")
        self.assertEqual(phan_loai([t], self.VUNG)["muc"], CAO)

    def test_ngoai_vung_khong_oan(self):
        for ten in ("src/quyen.py", "src/quyenx/a.py", "db/migrations.md"):
            with self.subTest(ten):
                self.assertNotEqual(phan_loai([tep(ten)], self.VUNG)["muc"], CAO)

    def test_khong_khai_vung_thi_nhu_cu(self):
        self.assertEqual(phan_loai([tep("src/quyen/a.py")])["muc"], THUONG)


class TestCuPhapVung(unittest.TestCase):
    """Phản bác 05/11: mẫu viết theo thói quen gitignore/CODEOWNERS từng chết lặng. Giờ hoặc khớp, hoặc doc_vung báo lỗi."""

    def _muc(self, ten, mau, **k):
        return phan_loai([tep(ten, **k)], [mau])["muc"]

    def test_mau_quen_tay_van_khop(self):
        for ten, mau in [("vendor/thanh-toan", "vendor/thanh-toan/"),  # con trỏ submodule không có / cuối
                         ("src/quyen/a.py", "src/quyen"), ("src/auth.py", "auth.py"), ("a/b/auth.py", "auth.py"),
                         ("db/x/migrations/1.sql", "*/migrations/"), ("db/x/migrations/1.sql", "**/migrations/"),
                         ("src/auth.py", "src/**/auth.py"), ("src/a/b/auth.py", "src/**/auth.py"),
                         ("app/[id]/page.tsx", "app/[id]/page.tsx"), ("app/[id]/x.tsx", "app/[id]/*"),
                         ("src/c#/a.cs", "src/c#/")]:
            with self.subTest(ten=ten, mau=mau):
                self.assertEqual(self._muc(ten, mau), CAO)

    def test_khong_khop_lan(self):
        for ten, mau in [("src/quyen2/a.py", "src/quyen"), ("src/oauth.py", "auth.py"), ("app/i/page.tsx", "app/[id]/page.tsx"),
                         ("srcx/auth.py", "src/**/auth.py")]:
            with self.subTest(ten=ten, mau=mau):
                self.assertNotEqual(self._muc(ten, mau), CAO)

    def test_ten_cu_hong_khong_nem_loi(self):
        for cu in (0, False, [], {}):
            with self.subTest(cu=cu):
                self.assertEqual(phan_loai([tep("a.py", status="renamed", previous_filename=cu)], ["x/"])["muc"], CAO)


class TestDocVung(unittest.TestCase):
    def _doc(self, noi_dung):
        import os, tempfile
        with tempfile.TemporaryDirectory() as thu_muc:
            duong = os.path.join(thu_muc, "vung.txt")
            with open(duong, "wb") as f:
                f.write(noi_dung if isinstance(noi_dung, bytes) else noi_dung.encode())
            return rui_ro.doc_vung(duong)

    def test_doc_bo_chu_thich_va_dong_trong(self):
        self.assertEqual(self._doc("# quyền\nsrc/quyen/\n\n  db/migrations/*  # cuối dòng\n"), ["src/quyen/", "db/migrations/*"])

    def test_mau_khong_bao_gio_khop_thi_bao_loi(self):
        for dong in ("!src/quyen/", "src/\xa0quyen/", "ｓｒｃ/", "src/***/a"):
            with self.subTest(dong=dong):
                with self.assertRaises(ValueError):
                    self._doc(dong + "\n")

    def test_thang_giua_dong_khong_phai_chu_thich(self):
        self.assertEqual(self._doc("src/c#/\n"), ["src/c#/"])

    def test_khong_co_tep_la_khong_khai(self):
        self.assertIsNone(rui_ro.doc_vung("/khong/co/tep/nay.txt"))  # chưa khai: cổng chặn
        self.assertIsNone(rui_ro.doc_vung(None))

    def test_tep_hong_thi_bao_loi_khong_lang_le_bo_qua(self):
        for xau in (b"\xff\xfe", "/tuyet-doi\n", "a\\b\n", "../ra-ngoai\n", "\n".join("m%d/" % i for i in range(201))):
            with self.subTest(repr(xau)[:30]):
                with self.assertRaises(ValueError):
                    self._doc(xau)

    def test_mau_rong_sau_chu_thich_bi_bo(self):
        self.assertEqual(self._doc("   # chỉ chú thích\n"), [])
