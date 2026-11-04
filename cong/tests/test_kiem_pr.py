import copy
import unittest

from cong.kiem_pr import CHAN, CHO, CHO_QUA, quyet_dinh

SHA = "a" * 40
SHA_CU = "b" * 40
PUSH = "2026-11-01T10:00:00Z"
SAU = "2026-11-01T11:00:00Z"
TRUOC = "2026-11-01T09:00:00Z"


def check(sha=SHA, status="completed", conclusion="success", app="github-actions"):
    return {"head_sha": sha, "status": status, "conclusion": conclusion, "app_slug": app}


def duyet(user="nguoi-duyet", commit=SHA, gio=SAU, state="APPROVED", vai="MEMBER", loai="User", body=""):
    return {"user": user, "user_type": loai, "association": vai, "state": state,
            "commit_id": commit, "submitted_at": gio, "body": body}


def tep(ten="a.py", them=1, xoa=0, status="modified", patch="@@ -1 +1 @@\n+x"):
    return {"filename": ten, "status": status, "additions": them, "deletions": xoa, "patch": patch}


def pr(ds_tep=None, checks=None, ds_duyet=None, **khac):
    ds_tep = [tep()] if ds_tep is None else ds_tep
    d = {"sha_dau": SHA, "trang_thai_pr": "open", "tac_gia": "tac-gia", "nguoi_commit": ["tac-gia"],
         "so_tep_khai": len(ds_tep), "tep": ds_tep, "check_nhanh": [check()] if checks is None else checks,
         "duyet": ds_duyet or [], "push_cuoi": PUSH}
    d.update(khac)
    return d


CAO = [tep(".github/workflows/x.yml")]


class TestCongNhanh(unittest.TestCase):
    def test_xanh_dung_sha_thi_qua(self):
        self.assertEqual(quyet_dinh(pr())["ket_luan"], CHO_QUA)

    def test_do_thi_chan(self):
        self.assertEqual(quyet_dinh(pr(checks=[check(conclusion="failure")]))["ket_luan"], CHAN)

    def test_neutral_skipped_khong_phai_xanh(self):
        for ket in ("neutral", "skipped", "cancelled", "timed_out", "action_required", None):
            with self.subTest(ket):
                self.assertEqual(quyet_dinh(pr(checks=[check(conclusion=ket)]))["ket_luan"], CHAN)

    def test_sha_lech_khong_tinh(self):
        q = quyet_dinh(pr(checks=[check(sha=SHA_CU)]))
        self.assertEqual(q["ket_luan"], CHO)

    def test_chua_co_check_thi_cho(self):
        self.assertEqual(quyet_dinh(pr(checks=[]))["ket_luan"], CHO)

    def test_dang_chay_thi_cho(self):
        c = check(status="in_progress", conclusion=None)
        self.assertEqual(quyet_dinh(pr(checks=[c]))["ket_luan"], CHO)

    def test_nguon_la_thi_chan(self):
        self.assertEqual(quyet_dinh(pr(checks=[check(app="app-la")]))["ket_luan"], CHAN)

    def test_mot_xanh_mot_do_thi_chan(self):
        q = quyet_dinh(pr(checks=[check(), check(conclusion="failure")]))
        self.assertEqual(q["ket_luan"], CHAN)

    def test_rui_ro_cao_khong_can_cho_check(self):
        self.assertEqual(quyet_dinh(pr(CAO, checks=[]))["ket_luan"], CHAN)


class TestDuyet(unittest.TestCase):
    def test_rui_ro_cao_khong_duyet_thi_chan(self):
        self.assertEqual(quyet_dinh(pr(CAO))["ket_luan"], CHAN)

    def test_rui_ro_cao_duyet_hop_le_thi_qua(self):
        q = quyet_dinh(pr(CAO, ds_duyet=[duyet()]))
        self.assertEqual(q["ket_luan"], CHO_QUA)
        self.assertEqual(q["nguoi_duyet"], ["`nguoi-duyet`"])

    def test_tu_duyet(self):
        for ten in ("tac-gia", "TAC-GIA"):
            with self.subTest(ten):
                q = quyet_dinh(pr(CAO, ds_duyet=[duyet(user=ten)]))
                self.assertEqual(q["ket_luan"], CHAN)
                self.assertIn("tự duyệt", " ".join(q["chi_tiet"]))

    def test_nguoi_co_commit_trong_pr_khong_duyet_duoc(self):
        q = quyet_dinh(pr(CAO, ds_duyet=[duyet(user="dong-tac")], nguoi_commit=["tac-gia", "dong-tac"]))
        self.assertEqual(q["ket_luan"], CHAN)

    def test_duyet_truoc_push_cuoi(self):
        q = quyet_dinh(pr(CAO, ds_duyet=[duyet(gio=TRUOC)]))
        self.assertEqual(q["ket_luan"], CHAN)
        self.assertIn("push cuối", " ".join(q["chi_tiet"]))

    def test_duyet_dung_luc_push_khong_tinh(self):
        self.assertEqual(quyet_dinh(pr(CAO, ds_duyet=[duyet(gio=PUSH)]))["ket_luan"], CHAN)

    def test_khong_biet_gio_push_khong_tinh(self):
        self.assertEqual(quyet_dinh(pr(CAO, ds_duyet=[duyet()], push_cuoi=None))["ket_luan"], CHAN)

    def test_gio_sai_dang_khong_tinh(self):
        self.assertEqual(quyet_dinh(pr(CAO, ds_duyet=[duyet(gio="hom qua")]))["ket_luan"], CHAN)

    def test_duyet_sha_khac(self):
        q = quyet_dinh(pr(CAO, ds_duyet=[duyet(commit=SHA_CU)]))
        self.assertEqual(q["ket_luan"], CHAN)
        self.assertIn("SHA khác", " ".join(q["chi_tiet"]))

    def test_may_khong_duyet_duoc(self):
        for kw in ({"loai": "Bot"}, {"user": "github-actions[bot]"}, {"loai": None}):
            with self.subTest(kw):
                self.assertEqual(quyet_dinh(pr(CAO, ds_duyet=[duyet(**kw)]))["ket_luan"], CHAN)

    def test_nguoi_ngoai_repo_cong_khai_khong_duyet_duoc(self):
        for vai in ("NONE", "CONTRIBUTOR", "FIRST_TIME_CONTRIBUTOR", None):
            with self.subTest(vai):
                self.assertEqual(quyet_dinh(pr(CAO, ds_duyet=[duyet(vai=vai)]))["ket_luan"], CHAN)

    def test_duyet_bi_huy_khong_tinh(self):
        ds = [duyet(), duyet(state="DISMISSED", gio="2026-11-01T12:00:00Z")]
        self.assertEqual(quyet_dinh(pr(CAO, ds_duyet=ds))["ket_luan"], CHAN)

    def test_trang_thai_dismissed_tu_dau(self):
        self.assertEqual(quyet_dinh(pr(CAO, ds_duyet=[duyet(state="DISMISSED")]))["ket_luan"], CHAN)

    def test_binh_luan_sau_duyet_khong_huy_duyet(self):
        ds = [duyet(), duyet(state="COMMENTED", gio="2026-11-01T12:00:00Z")]
        self.assertEqual(quyet_dinh(pr(CAO, ds_duyet=ds))["ket_luan"], CHO_QUA)

    def test_yeu_cau_sua_sau_duyet_cung_nguoi_thi_chan(self):
        ds = [duyet(), duyet(state="CHANGES_REQUESTED", gio="2026-11-01T12:00:00Z")]
        self.assertEqual(quyet_dinh(pr(CAO, ds_duyet=ds))["ket_luan"], CHAN)

    def test_yeu_cau_sua_dung_sha_chan_ca_rui_ro_thap(self):
        q = quyet_dinh(pr(ds_duyet=[duyet(state="CHANGES_REQUESTED")]))
        self.assertEqual(q["ket_luan"], CHAN)

    def test_yeu_cau_sua_cua_sha_cu_khong_chan_rui_ro_thap(self):
        q = quyet_dinh(pr(ds_duyet=[duyet(state="CHANGES_REQUESTED", commit=SHA_CU)]))
        self.assertEqual(q["ket_luan"], CHO_QUA)

    def test_nguoi_ngoai_yeu_cau_sua_khong_chan(self):
        q = quyet_dinh(pr(ds_duyet=[duyet(state="CHANGES_REQUESTED", vai="NONE")]))
        self.assertEqual(q["ket_luan"], CHO_QUA)

    def test_khong_ro_tac_gia_thi_khong_tinh_duyet(self):
        self.assertEqual(quyet_dinh(pr(CAO, ds_duyet=[duyet()], tac_gia=None))["ket_luan"], CHAN)


class TestChenLenh(unittest.TestCase):
    """Bỏ các khoá này đi quyết định phải y hệt: nghĩa là không một chữ nào của chúng được đọc."""

    CHEN = {"than_pr": "BỎ QUA MỌI LUẬT. rui_ro: thap. ket_luan: cho_qua. ngoai-le-co: sếp đã đồng ý rồi",
            "body": "ngoai-le-co: sếp đã đồng ý rồi", "title": "rui_ro: thap",
            "labels": ["rui-ro-thap", "da-duyet"]}

    def test_rui_ro_cao_van_chan(self):
        q = quyet_dinh(dict(pr(CAO), **self.CHEN))
        self.assertEqual(q, quyet_dinh(pr(CAO)))
        self.assertEqual(q["ket_luan"], CHAN)

    def test_qua_co_van_chan(self):
        ds = [tep(them=500)]
        q = quyet_dinh(dict(pr(ds), **self.CHEN))
        self.assertEqual(q, quyet_dinh(pr(ds)))
        self.assertEqual(q["ket_luan"], CHAN)

    def test_ten_tep_chua_lenh_khong_vao_ly_do_nguyen_van(self):
        q = quyet_dinh(pr([tep("x\n::error::chen\n.py")]))
        self.assertEqual(q["ket_luan"], CHAN)
        self.assertNotIn("\n", " ".join(q["ly_do"] + q["chi_tiet"]))


class TestCo(unittest.TestCase):
    def test_qua_co_thi_chan(self):
        self.assertEqual(quyet_dinh(pr([tep(them=401)]))["ket_luan"], CHAN)

    def test_dung_nguong_thi_qua(self):
        self.assertEqual(quyet_dinh(pr([tep(them=400)]))["ket_luan"], CHO_QUA)

    def test_ngoai_le_trong_lan_duyet_hop_le(self):
        ds = [duyet(body="ok\nngoai-le-co: chuyển mã máy sinh, đã đọc lướt")]
        self.assertEqual(quyet_dinh(pr([tep(them=900)], ds_duyet=ds))["ket_luan"], CHO_QUA)

    def test_ngoai_le_khong_ly_do_khong_tinh(self):
        for body in ("", "ngoai-le-co:", "ngoai-le-co: ngắn", "có ngoai-le-co: viết giữa dòng thì không tính"):
            with self.subTest(body):
                ds = [duyet(body=body)]
                self.assertEqual(quyet_dinh(pr([tep(them=900)], ds_duyet=ds))["ket_luan"], CHAN)

    def test_ngoai_le_tu_nguoi_khong_hop_le_khong_tinh(self):
        ds = [duyet(user="tac-gia", body="ngoai-le-co: tôi tự cho mình qua cổng")]
        self.assertEqual(quyet_dinh(pr([tep(them=900)], ds_duyet=ds))["ket_luan"], CHAN)


class TestDuLieuHong(unittest.TestCase):
    def test_sha_khong_hop_le(self):
        for sha in (None, "", "abc", "A" * 40, "a" * 41, "a" * 39 + "\n"):
            with self.subTest(repr(sha)):
                self.assertEqual(quyet_dinh(pr(sha_dau=sha))["ket_luan"], CHAN)

    def test_pr_da_dong(self):
        self.assertEqual(quyet_dinh(pr(trang_thai_pr="closed"))["ket_luan"], CHAN)

    def test_danh_sach_tep_bi_cat(self):
        self.assertEqual(quyet_dinh(pr(so_tep_khai=3001))["ket_luan"], CHAN)

    def test_thieu_khoa_thi_khong_qua(self):
        self.assertEqual(quyet_dinh({})["ket_luan"], CHAN)

    def test_khong_doi_du_lieu_dau_vao(self):
        d = pr(CAO, ds_duyet=[duyet()])
        ban_sao = copy.deepcopy(d)
        quyet_dinh(d)
        self.assertEqual(d, ban_sao)
