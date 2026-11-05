import importlib.util
import unittest
from pathlib import Path

_DAC_TA = importlib.util.spec_from_file_location(
    "do_vong", Path(__file__).resolve().parents[2] / "nghiem-thu/do_vong.py")
do_vong = importlib.util.module_from_spec(_DAC_TA)
_DAC_TA.loader.exec_module(do_vong)

NAY = "2026-03-01T00:00:00Z"


def pr(so, mo="2026-02-01T00:00:00Z", merge="2026-02-01T10:00:00Z", muc="thap", chan=(), nhan=(), than=""):
    return {"so": so, "mo": mo, "merge": merge, "muc": muc, "ly_do_chan": list(chan), "nhan": list(nhan), "than": than}


def issue(so, mo="2026-02-03T00:00:00Z", nhan=("loi-lot",), than="pr-gay-loi: chưa rõ", la_pr=False):
    return {"so": so, "mo": mo, "nhan": list(nhan), "than": than, "la_pr": la_pr}


class TestLoiLot(unittest.TestCase):
    def test_dem_theo_nang_va_khau(self):
        ds = [issue(1, nhan=("loi-lot", "N1", "khau:test")), issue(2, nhan=("loi-lot", "N1", "khau:test")),
              issue(3, nhan=("loi-lot", "N3", "khau:cong")), issue(4, nhan=("loi-lot", "N2"))]
        k = do_vong.tinh([pr(i) for i in range(1, 201)], ds, NAY, 30)["loi_lot"]
        self.assertEqual(k["so"], 4)
        self.assertEqual(k["tren_100_pr"], 2.0)  # 4 lỗi / 200 PR đã merge
        self.assertEqual(k["bang"], {"N1 · test": 2, "N3 · cong": 1})
        self.assertEqual(k["chua_phan_loai"], [4])  # thiếu khâu: không đoán, liệt kê để người điền
        self.assertFalse(k["du_mau"])

    def test_nhan_sai_hai_muc_nang_la_chua_phan_loai(self):
        k = do_vong.tinh([pr(1)], [issue(1, nhan=("loi-lot", "N1", "N2", "khau:test")),
                                   issue(2, nhan=("loi-lot", "N1", "khau:la"))], NAY, 30)["loi_lot"]
        self.assertEqual(k["chua_phan_loai"], [1, 2])

    def test_ngoai_ky_khong_tinh(self):
        k = do_vong.tinh([pr(1)], [issue(1, mo="2025-12-01T00:00:00Z", nhan=("loi-lot", "N1", "khau:test"))], NAY, 30)
        self.assertEqual(k["loi_lot"]["so"], 0)

    def test_bat_truoc_merge_dem_rieng(self):
        k = do_vong.tinh([pr(1)], [issue(1, nhan=("bat-truoc-merge",))], NAY, 30)
        self.assertEqual((k["loi_lot"]["so"], k["bat_truoc_merge"]), (0, 1))

    def test_pr_mang_nhan_loi_lot_khong_phai_loi_lot(self):
        k = do_vong.tinh([pr(1)], [issue(5, nhan=("loi-lot", "bat-truoc-merge"), la_pr=True)], NAY, 30)
        self.assertEqual((k["loi_lot"]["so"], k["bat_truoc_merge"]), (0, 1))

    def test_pr_mo_truoc_ky_merge_trong_ky_van_tinh(self):
        k = do_vong.tinh([pr(1, mo="2026-01-20T00:00:00Z", merge="2026-02-10T00:00:00Z", muc="cao")], [], NAY, 30)
        self.assertEqual((k["so_merged"], k["thoi_gian_ra"]["cao"]["so"]), (1, 1))


class TestTiLeHong(unittest.TestCase):
    def test_loi_lot_va_hoan_lai_trong_7_ngay(self):
        ds_pr = [pr(1), pr(2), pr(3), pr(4),
                 pr(5, merge="2026-02-26T00:00:00Z"),  # chưa đủ 7 ngày: không vào mẫu
                 pr(6, merge=None),
                 pr(7, merge="2026-02-03T00:00:00Z", than="This reverts commit x.\n\nReverts chu/repo#2")]
        ds_is = [issue(1, than="pr-gay-loi: #1\n"),
                 issue(2, mo="2026-02-20T00:00:00Z", than="pr-gay-loi: #3"),  # quá 7 ngày sau merge: không tính
                 issue(3, than="pr-gay-loi: chưa rõ"),
                 issue(4, mo="2026-01-31T00:00:00Z", than="pr-gay-loi: #4"),  # mở trước khi PR merge: không tính
                 issue(5, than="- pr-gay-loi: #3"),  # viết lệch: không đoán, liệt kê
                 issue(6, than="")]
        k = do_vong.tinh(ds_pr, [dict(i, nhan=["loi-lot", "N2", "khau:test"]) for i in ds_is], NAY, 30)["ti_le_hong"]
        self.assertEqual(k["so_pr"], 5)  # 1, 2, 3, 4, 7
        self.assertEqual(k["gay_hong"], [1, 2])
        self.assertEqual(k["ti_le"], 0.4)
        self.assertEqual(k["khong_doc_duoc"], [5, 6])

    def test_revert_repo_khac_khong_tinh(self):
        ds = [pr(1), pr(2, than="Reverts khac/repo#1")]
        k = do_vong.tinh(ds, [], NAY, 30, repo="chu/repo")["ti_le_hong"]
        self.assertEqual(k["gay_hong"], [])
        k = do_vong.tinh([pr(1), pr(2, than="Reverts Chu/Repo#1")], [], NAY, 30, repo="chu/repo")["ti_le_hong"]
        self.assertEqual(k["gay_hong"], [1])

    def test_loi_lot_theo_muc_cua_pr_gay_loi(self):
        ds_is = [issue(1, nhan=["loi-lot"], than="pr-gay-loi: #1"), issue(2, nhan=["loi-lot"])]
        k = do_vong.tinh([pr(1, muc="cao")], ds_is, NAY, 30)["loi_lot"]
        self.assertEqual(k["theo_muc_pr"], {"cao": 1, "chưa rõ": 1})
        self.assertFalse(k["du_mau"])


class TestThoiGianRa(unittest.TestCase):
    def test_trung_vi_va_p90_theo_muc(self):
        ds = [pr(i, merge="2026-02-01T%02d:00:00Z" % i, muc="trung_binh") for i in range(1, 11)] + [pr(99, muc="cao", merge=None)]
        k = do_vong.tinh(ds, [], NAY, 30)["thoi_gian_ra"]
        self.assertEqual(k["trung_binh"]["so"], 10)
        self.assertEqual(k["trung_binh"]["trung_vi_gio"], 5.5)
        self.assertEqual(k["trung_binh"]["p90_gio"], 9)  # hạng gần nhất: phần tử thứ 9 trong 10
        self.assertNotIn("cao", k)  # PR chưa merge không có thời gian ra


class TestDoDung(unittest.TestCase):
    def test_tac_gia_tu_gan_chan_oan_khong_tinh(self):
        k = do_vong.tinh([pr(1, chan=["x"], nhan=["chan-oan"]) | {"oan_tu_gan": True}], [], NAY, 30)
        self.assertEqual(k["do_dung"]["x"]["so_oan"], 0)
        self.assertEqual(k["oan_tu_gan"], [1])

    def test_chan_oan_do_nguoi_duyet_gan_nhan(self):
        ds = [pr(1, chan=["đổi tệp của cổng"]), pr(2, chan=["đổi tệp của cổng", "chạm vùng nhạy cảm"], nhan=["chan-oan"]),
              pr(3, chan=["đổi tệp của cổng"])]
        k = do_vong.tinh(ds, [], NAY, 30)["do_dung"]
        self.assertEqual(k["đổi tệp của cổng"], {"so_chan": 3, "so_oan": 1, "do_dung": 0.67, "du_mau": False})
        self.assertEqual(k["chạm vùng nhạy cảm"]["do_dung"], 0.0)


class TestDocCheck(unittest.TestCase):
    TOM = ("**Kết luận:** chan\n\n**Lý do:**\n- rủi ro cao: cần người có quyền admin, khác tác giả, duyệt đúng SHA\n"
           "- có lượt `cong-nhanh` không xanh\n- quá 400 dòng (523)\n\n**Chi tiết:**\n- đổi tệp của cổng `cong/a.py`\n"
           "- đổi test có sẵn (`modified`) `cong/tests/t.py`\n- chạm vùng nhạy cảm `x/`: `x/a.py`\n")

    def test_nhom_ly_do_va_muc(self):
        ds = [{"completed_at": "2026-02-01T00:01:00Z", "output": {"title": "chan (cao)", "summary": self.TOM}},
              {"completed_at": "2026-02-01T00:09:00Z", "output": {"title": "cho_qua (cao)", "summary": "**Kết luận:** cho_qua"}}]
        muc, ly_do = do_vong.doc_check(ds)
        self.assertEqual(muc, "cao")
        # Chỉ mục «Lý do»; «Chi tiết» là phân loại rủi ro, không phải luật đã chặn. Số thay bằng N để gom nhóm.
        self.assertEqual(ly_do, ["có lượt · không xanh", "quá N dòng (N)"])

    def test_muc_lay_tu_luot_moi_nhat_co_muc(self):
        ds = [{"completed_at": "2026-02-01T00:01:00Z", "output": {"title": "chan (trung_binh)", "summary": ""}},
              {"completed_at": "2026-02-01T00:09:00Z", "output": {"title": "khong_xet (chua_ro)", "summary": ""}}]
        self.assertEqual(do_vong.doc_check(ds)[0], "trung_binh")

    def test_khong_co_check(self):
        self.assertEqual(do_vong.doc_check([]), (None, []))


class GhBaoVe:
    def __init__(self, nhanh):
        self.nhanh = nhanh

    def goi(self, phuong_thuc, duong, body=None):
        assert (phuong_thuc, duong) == ("GET", "/branches/main"), duong
        return self.nhanh


def bao_ve(*checks):
    return {"protection": {"required_status_checks": {"checks": [{"context": c, "app_id": a} for c, a in checks]}}}


class TestAppGhim(unittest.TestCase):
    def test_doc_app_ghim_cua_cong_cuoi(self):
        self.assertEqual(do_vong.app_ghim(GhBaoVe(bao_ve(("cong-nhanh", 15368), ("cong-cuoi", 5621104)))), 5621104)

    def test_chua_ghim_hoac_nguon_nao_cung_duoc(self):
        for nhanh in ({}, {"protection": {"enabled": False}}, bao_ve(("cong-cuoi", None)), bao_ve(("cong-cuoi", -1))):
            with self.subTest(nhanh):
                self.assertIsNone(do_vong.app_ghim(GhBaoVe(nhanh)))

    def test_loc_dung_app(self):
        ds = [{"app": {"id": 1}}, {"app": {"id": 15368, "slug": "github-actions"}}, {"app": None}, {}]
        self.assertEqual(do_vong.loc_app(ds, 1), [{"app": {"id": 1}}])
        self.assertEqual(do_vong.loc_app(ds, None), [])  # chưa biết App: không tin check nào


class TestBang(unittest.TestCase):
    def test_canh_bao_khi_chua_ghim_app(self):
        k = do_vong.tinh([pr(1)], [], NAY, 30)
        self.assertNotIn("chưa ghim App", do_vong.bang(dict(k, app_cong=5621104)))
        self.assertIn("chưa ghim App", do_vong.bang(dict(k, app_cong=None)))

    def test_token_ghi_chua_do(self):
        k = do_vong.tinh([pr(1)], [], NAY, 30)
        self.assertEqual((k["token"]["co_ghi"], k["token"]["thieu"]), (0, [1]))
        self.assertIn("chưa đo: 0 / 1 PR merge", do_vong.bang(k))
        self.assertIn("chưa đủ mẫu", do_vong.bang(k))

    def test_token_trung_vi_va_tinh_ca_pr_bi_bo(self):
        ds = [dict(pr(1), token=100), dict(pr(2), token=300), dict(pr(3), token=200), pr(4),
              dict(pr(5, merge=None), dong=True, token=600),  # bị bỏ: không vào trung vị, vào bình quân
              dict(pr(6, merge=None), token=900)]  # còn mở: không tính
        tk = do_vong.tinh(ds, [], NAY, 30)["token"]
        self.assertEqual((tk["co_ghi"], tk["so_merge"], tk["thieu"]), (3, 4, [4]))
        self.assertEqual((tk["trung_vi"], tk["binh_quan_ca_bo"], tk["so_bo"]), (200, 400, 1))
        b = do_vong.bang(do_vong.tinh(ds, [], NAY, 30))
        self.assertIn("trung vị 200 token mới, bình quân 400 khi tính cả 1 PR bị bỏ, 3 / 4 PR merge", b)
        self.assertIn("**PR merge chưa có token máy ghi** (không vào trung vị): #4", b)


class TestDocToken(unittest.TestCase):
    def test_lay_comment_moi_nhat_cua_nguoi_trong_repo(self):
        def c(so, ai, ngay, dau=True):
            return {"body": ("<!-- token-may-ghi -->\n" if dau else "") + "token-moi: %d" % so,
                    "author_association": ai, "updated_at": "2026-01-0%d" % ngay}
        ds = [c(1, "OWNER", 1), c(2, "MEMBER", 2), c(9, "NONE", 3), c(8, "OWNER", 4, dau=False)]
        self.assertEqual(do_vong.doc_token(ds), 2)
        self.assertIsNone(do_vong.doc_token([]))
        self.assertIsNone(do_vong.doc_token([{"body": None, "author_association": "OWNER"}]))


if __name__ == "__main__":
    unittest.main()
