"""Luật L12: máy ghi token tách theo model và quy ra USD; do_vong.py đọc lại để báo trung vị và tỉ trọng."""
import json
import unittest

from test_ghi_token import GOC, ThuMuc, do_vong, ghi_token, luot


def luot_m(id_, nhanh, luc, model, ghi_1h=None, **k):
    e = luot(id_, nhanh, luc, **k)
    e["message"]["model"] = model
    if ghi_1h is not None:
        e["message"]["usage"]["cache_creation"] = {"ephemeral_1h_input_tokens": ghi_1h, "ephemeral_5m_input_tokens": 0}
    return e


def cong(*dong):
    with ThuMuc() as tm:
        return ghi_token.cong_theo_nhanh([tm.tep("a.jsonl", dong)], GOC, theo_model=True)


class TestTheoModel(unittest.TestCase):
    def test_tach_theo_model_va_ghi_dem_mot_gio(self):
        k = cong(luot_m("m1", "x", "2026-01-01T00:00:01Z", "claude-opus-5-5", ghi_1h=100),
                 luot_m("m2", "x", "2026-01-01T00:00:02Z", "claude-haiku-5-5"),
                 luot_m("m3", "x", "2026-01-01T00:00:03Z", "claude-haiku-5-5[1m]"))
        self.assertEqual(k["x"]["model"]["claude-opus-5-5"],
                         {"luot": 1, "vao": 10, "ghi_5m": 0, "ghi_1h": 100, "ra": 5, "doc": 1000})
        self.assertEqual(k["x"]["model"]["claude-haiku-5-5"]["luot"], 2)  # hậu tố [1m] gộp về một tên
        self.assertEqual(k["x"]["moi"], 345)  # tổng token mới không đổi

    def test_mac_dinh_khong_them_khoa_model(self):
        with ThuMuc() as tm:
            k = ghi_token.cong_theo_nhanh([tm.tep("a.jsonl", [luot_m("m1", "x", "2026-01-01T00:00:01Z", "m")])], GOC)
        self.assertNotIn("model", k["x"])

    def test_ghi_dem_mot_gio_lon_hon_tong_bi_cat(self):
        k = cong(luot_m("m1", "x", "2026-01-01T00:00:01Z", "claude-opus-5-5", ghi_1h=10 ** 9))
        self.assertEqual(k["x"]["model"]["claude-opus-5-5"]["ghi_1h"], 100)

    def test_chi_phi_theo_bang_gia(self):
        so = {"luot": 1, "vao": 1_000_000, "ghi_5m": 1_000_000, "ghi_1h": 1_000_000, "ra": 1_000_000, "doc": 1_000_000}
        # Opus 5.5: 4 vào + 5 ghi 5 phút + 8 ghi 1 giờ + 20 ra + 0,20 đọc
        self.assertAlmostEqual(ghi_token.chi_phi("claude-opus-5-5", so), 37.2)
        self.assertIsNone(ghi_token.chi_phi("gpt-moi", so))

    def test_comment_ghi_roi_do_vong_doc_lai(self):
        theo = cong(luot_m("m1", "x", "2026-01-01T00:00:01Z", "claude-opus-5-5"),
                    luot_m("m2", "x", "2026-01-01T00:00:02Z", "model-la"))["x"]
        than = ghi_token.than_comment("x", {"mn": dict(theo, phien=1, luc="2026-01-01 10:00")})
        self.assertIn("| model-la | 1 | 115 | 1000 | chưa có giá |", than)
        usd, theo_usd = do_vong.doc_usd([{"body": than, "author_association": "OWNER"}])
        mong = ghi_token.chi_phi("claude-opus-5-5", theo["model"]["claude-opus-5-5"])
        self.assertAlmostEqual(usd, mong, places=4)
        self.assertEqual(set(theo_usd), {"claude-opus-5-5"})  # model chưa có giá không vào USD
        # Máy khác đọc lại comment vẫn giữ phần theo model.
        self.assertEqual(ghi_token.doc_comment(than)["mn"]["model"], theo["model"])

    def test_du_lieu_model_hong_bi_bo(self):
        hong = {"mn": {"phien": 1, "luot": 1, "moi": 1, "doc_dem": 0, "moi_truoc": 0,
                       "model": {"a": {"luot": -1}, "b<x>": dict.fromkeys(ghi_token._LOAI, 1)}}}
        than = "<!-- du-lieu %s -->" % json.dumps(hong)  # comment bị sửa tay
        self.assertEqual(set(ghi_token.doc_comment(than)["mn"]["model"]), {"bx"})

    def test_comment_cu_khong_co_usd(self):
        than = ghi_token.than_comment("x", {"mn": {"phien": 1, "luot": 1, "moi": 1, "doc_dem": 0, "moi_truoc": 0}})
        self.assertNotIn("usd-quy-doi", than)
        self.assertIsNone(do_vong.doc_usd([{"body": than, "author_association": "OWNER"}]))
        self.assertIsNone(do_vong.doc_usd([{"body": than + "\nusd-quy-doi: 9.0000", "author_association": "NONE"}]))


class TestDoVong(unittest.TestCase):
    def test_trung_vi_va_ti_trong(self):
        from test_do_vong import NAY, pr
        ds = [dict(pr(1), usd=(1.0, {"claude-opus-5-5": 0.75, "claude-haiku-5-5": 0.25})),
              dict(pr(2), usd=(3.0, {"claude-opus-5-5": 3.0})), pr(3)]
        tk = do_vong.tinh(ds, [], NAY, 30)["token"]
        self.assertEqual((tk["usd_trung_vi"], tk["usd_co_ghi"], tk["usd_du_mau"]), (2.0, 2, False))
        self.assertEqual(tk["usd_ti_trong"], {"claude-opus-5-5": 0.94, "claude-haiku-5-5": 0.06})


if __name__ == "__main__":
    unittest.main()
