import datetime as dt, importlib.util, json, subprocess, tempfile, unittest
from pathlib import Path
from zoneinfo import ZoneInfo

spec = importlib.util.spec_from_file_location("tien_do", Path(__file__).parents[1] / "tien_do.py")
td = importlib.util.module_from_spec(spec); spec.loader.exec_module(td)
TZ = ZoneInfo("Asia/Ho_Chi_Minh")
HEAD = "# Phase X-1: Thử\n\n**Xong khi:** x · **Hạn:** 20/11/2026\n**Cập nhật:** issue #9, nhãn `phase`\n\n"
COT = "| Task | Yêu cầu | Trạng thái | Chờ task | PR | Ghi chú |\n|---|---|---|---|---|---|\n"


def so(*rows): return HEAD + COT + "".join(f"| {r} |\n" for r in rows)


class TestSo(unittest.TestCase):
    def test_doc_so_va_chuan_hoa(self):
        dau, rows = td.doc_so(so("T1 | a | xong | — | #5 | ", "T2 | b | Đang làm | T1 | — | ", "T3 | c | chờ | — | — | ",
                                 "T4 | d | Đã huỷ | — | — | gộp vào T3"))
        self.assertEqual(dau["han"], dt.date(2026, 11, 20)); self.assertEqual(dau["issue"], 9)
        self.assertEqual([r["tt"] for r in rows.values()], [td.XONG, td.DANG, td.CHUA, td.HUY])
        self.assertEqual(rows["T1"]["pr"], 5)

    def test_ty_le_huy_ra_khoi_mau_so(self):  # HT-05
        _, rows = td.doc_so(so("T1 | a | xong | — | — | ", "T2 | b | chờ | — | — | ", "T3 | c | Đã huỷ | — | — | tách → T2"))
        d = td.dem(rows); mau = d[td.XONG] + d[td.DANG] + d[td.CHUA]
        self.assertEqual((mau, td.pct(d, mau)), (2, 50))

    def test_pham_vi_chi_dem_doi_yc(self):
        cu = td.doc_so(so("T1 | a | xong | — | — | ", "T2 | b | chờ | — | — | "))[1]
        moi = td.doc_so(so("T1 | a | xong | — | — | ", "T2 | b | Đã huỷ | — | — | doi-yc p.md", "T3 | c | chờ | — | — | doi-yc p.md",
                           "T4 | d | chờ | — | — | tách → x"))[1]
        self.assertEqual(td.pham_vi(cu, moi), 0)  # +1 (T3) -1 (T2); T4 là tách, không vào ±n
        self.assertEqual(td.pham_vi(cu, td.doc_so(so("T1 | a | xong | — | — | ", "T2 | b | chờ | — | — | ", "T3 | c | chờ | — | — | doi-yc p.md"))[1]), 1)


class TestMocGio(unittest.TestCase):
    def test_dem_moc(self):  # HT-11
        t = dt.datetime(2026, 11, 9, 9, 0, tzinfo=TZ)
        self.assertEqual(td.tuoi_cap_nhat(t, dt.datetime(2026, 11, 9, 11, 0, tzinfo=TZ)), 0)
        self.assertEqual(td.tuoi_cap_nhat(t, dt.datetime(2026, 11, 9, 12, 0, tzinfo=TZ)), 1)
        self.assertEqual(td.tuoi_cap_nhat(t, dt.datetime(2026, 11, 10, 9, 0, tzinfo=TZ)), 3)

    def test_doc_comment_bo_nguoi_la(self):
        cm = [{"body": "cap-nhat: lạ\nsuc-khoe: cham", "created_at": "2026-11-09T02:00:00Z", "author_association": "NONE"},
              {"body": "cap-nhat: T3 merge\nsuc-khoe: co-rui-ro\nly-do: CI", "created_at": "2026-11-09T01:00:00Z",
               "author_association": "OWNER", "reactions": {"+1": 1}}]
        c = td.doc_cap_nhat(cm, TZ)
        self.assertEqual((c["cau"], c["sk"], c["xn"]), ("T3 merge", "Có rủi ro", True))


class TestTrang(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp())
        self.g = lambda *a: subprocess.run(["git", "-C", str(self.d), "-c", "user.name=t", "-c", "user.email=t@t", *a],
                                           check=True, capture_output=True, env={"GIT_COMMITTER_DATE": "2026-11-01T10:00:00+07:00",
                                           "GIT_AUTHOR_DATE": "2026-11-01T10:00:00+07:00", "PATH": "/usr/bin:/bin:/opt/homebrew/bin"})
        self.g("init", "-q"); (self.d / "docs/phase").mkdir(parents=True)

    def ghi(self, text, msg="s"):
        (self.d / "docs/phase/X-1-1.md").write_text(text); self.g("add", "."); self.g("commit", "-qm", msg)

    def test_dung_yen_tu_lich_su_git(self):  # HT-12
        self.ghi(so("T1 | a | chờ | — | — | ", "T2 | b | chờ | — | — | "))
        ls = td.lich_su(self.d, "docs/phase/X-1-1.md", TZ)
        self.assertEqual(td.phan_tich_su(ls, dt.date(2026, 11, 4)), (0, 3))
        self.ghi(so("T1 | a | xong | — | — | ", "T2 | b | chờ | — | — | "))
        self.assertEqual(td.phan_tich_su(td.lich_su(self.d, "docs/phase/X-1-1.md", TZ), dt.date(2026, 11, 4))[1], 3)

    def test_xuat_trang_voi_lan_va_github(self):
        self.ghi(so("T1 | a | xong | — | #5 | ", "T2 | b | Đang làm | — | #6 | ", "T3 | c | chờ | T2 | — | "))
        lan = {"lan": [{"phase": "X-1-1", "ten": "Làn T2", "may": "may-a", "nhip": "chạy", "cho": ["Chờ CI"],
                        "cau": "T2 mở PR", "cau_tuoi_phut": 12, "buoc": "2/4", "da_chay_phut": 95, "pr": 6}]}
        (self.d / "lan.json").write_text(json.dumps(lan))
        pr = {5: {"state": "OPEN", "cho_ci": False}, 6: {"state": "OPEN", "cho_ci": True}}
        p = td.tinh_phase("X-1-1", (self.d / "docs/phase/X-1-1.md").read_text(), [], dt.datetime(2026, 11, 9, 9, 0, tzinfo=TZ),
                          pr.get, lambda n: [])
        self.assertEqual(p["rows"]["T1"]["tt"], td.DANG)  # sổ lệch GitHub thì tin GitHub
        self.assertEqual(len(p["lech"]), 1); self.assertIn("Chờ CI", p["rows"]["T2"]["co"])
        self.assertIn("Chờ task khác", p["rows"]["T3"]["co"]); self.assertIn("Thiếu cập nhật", p["co"])
        out = self.d / "t.html"
        self.assertEqual(td.main(["--repo-dir", str(self.d), "--ra", str(out), "--lan", str(self.d / "lan.json")]), 0)
        h = out.read_text()
        for s in ("Module X-1", "Chưa có câu cập nhật", "Làn T2", "bước 2/4", "tự khai", "Chưa đánh giá", "1/3 · 33%"):
            self.assertIn(s, h)
        self.assertNotIn("may-a", h.split("Làn T2")[0])


class TestVa(unittest.TestCase):
    def test_xss_ma_task_va_lan_json(self):  # chặn 1, 2
        t = so("T1 | a | xong | — | — | ", "T2<img src=x onerror=1> | b | chờ | — | — | ")
        self.assertEqual(list(td.doc_so(t)[1]), ["T1"])
        h = td.hang_lan({"ten": "<b>x", "may": "<i>", "nhip": "<s>", "cho": ["<u>"], "co": ["<u>"], "cau": "<a>", "cau_tuoi_phut": "<1>",
                         "buoc": "<c>", "da_chay_phut": "<2>", "ngu_canh_nghin": "<script>", "pr": "<3>"})
        self.assertNotIn("<script", h); self.assertNotIn("<i>", h); self.assertNotIn("<u>", h)
        self.assertIn("&lt;script&gt;", td.hang_lan({"ten": "<script>"}))
        self.assertTrue(any("không đúng dạng" in x for x in td.doc_so(t)[0]["canh_bao"]))  # phiếu vòng 2, điểm 1
        moc = so("T1 | a | xong | — | — | ") + "\n| Mốc | Ngày |\n|---|---|\n| T0 ra mắt | 1/1 |\n"
        self.assertEqual(td.doc_so(moc)[0]["canh_bao"], [])  # phản bác PR #63: bảng khác sau bảng task không bị báo

    def test_so_tran_khong_lam_hong_trang(self):  # phiếu vòng 2, điểm 2
        self.assertIsNone(td.so_nguyen(float("inf")))
        self.assertIn("x", td.hang_lan({"ten": "x", "pr": 1e999, "ngu_canh_nghin": float("inf")}))

    def test_phan_tram_tinh_ca_giai_doan_da_xong(self):  # chặn 3, HT-05
        mk = lambda *tt: so(*(f"T{i} | a | {x} | — | — | " for i, x in enumerate(tt, 1)))
        now = dt.datetime(2026, 11, 9, tzinfo=TZ)
        ps = [td.tinh_phase("X-1-1", mk("xong", "xong"), [], now, None, None),
              td.tinh_phase("X-1-2", mk("xong", "chờ", "chờ", "chờ"), [], now, None, None)]
        self.assertIn("3/6 · 50%", td.xuat("t", ps, [], now))
        ps = [td.tinh_phase("X-1-1", mk("xong"), [], now, None, None)]
        self.assertIn("1/1 · 100%", td.xuat("t", ps, [], now))

    def test_dong_hong_va_thieu_thu_muc(self):  # 4, 5, 7
        _, rows = td.doc_so(so("**T5** | a | xong | — | — | ", "T6 | a | xong | — | — | x | thừa", "T7 | a \\| b | xong | — | — | "))
        self.assertEqual(list(rows), ["T5", "T7"]); self.assertEqual(rows["T7"]["Yêu cầu"], "a | b")
        self.assertTrue(td.doc_so(so("T6 | a | xong | — | — | x | thừa"))[0]["canh_bao"])
        d = Path(tempfile.mkdtemp()); out = d / "o.html"
        self.assertEqual(td.main(["--repo-dir", str(d), "--ra", str(out)]), 0)
        self.assertIn("Không có docs/phase/", out.read_text())


class TestNacPr(unittest.TestCase):  # HT-13: vòng làn tô theo nấc PR
    SHA = "a" * 40
    XANH = [{"workflowName": "cong-nhanh", "name": "cong-nhanh", "status": "COMPLETED", "conclusion": "SUCCESS"}]

    def pr(self, state="OPEN", ci=None, reviews=()):
        return {"state": state, "headRefOid": self.SHA, "statusCheckRollup": self.XANH if ci is None else ci, "reviews": list(reviews)}

    def phieu(self, ket, sha=None, ai="COLLABORATOR"):
        return {"authorAssociation": ai, "body": f"phieu-phan-bac: {ket}\ntai-hien: chạy lại test", "commit": {"oid": sha or self.SHA}}

    def test_cac_nac(self):
        n = td.nac_pr
        self.assertEqual(n(self.pr("MERGED")), 5)
        self.assertIsNone(n(self.pr("CLOSED")))
        self.assertEqual(n(self.pr(ci=[])), 2)  # chưa có cong-nhanh
        self.assertEqual(n(self.pr(ci=[dict(self.XANH[0], status="IN_PROGRESS", conclusion=None)])), 2)
        self.assertEqual(n(self.pr(ci=[dict(self.XANH[0], conclusion="FAILURE")])), 2)
        self.assertEqual(n(self.pr()), 3)
        self.assertEqual(n(self.pr(reviews=[self.phieu("khong-bac")])), 4)

    def test_phieu_khong_tinh(self):
        n = td.nac_pr
        self.assertEqual(n(self.pr(reviews=[self.phieu("khong-bac", sha="b" * 40)])), 3)  # SHA cũ
        self.assertEqual(n(self.pr(reviews=[self.phieu("khong-bac", ai="NONE")])), 3)  # người lạ
        self.assertEqual(n(self.pr(reviews=[self.phieu("khong-bac"), self.phieu("bac")])), 3)  # còn bác trên head

    def test_hang_lan_to_vong_va_co_cho_phieu(self):
        l = {"ten": "Làn A", "pr": 7}
        h3 = td.hang_lan(l, nac=3)
        self.assertIn("--p:60", h3); self.assertIn("nấc PR 3/5", h3); self.assertIn("Chờ phiếu", h3)
        h4 = td.hang_lan(l, nac=4)
        self.assertIn("--p:80", h4); self.assertNotIn("Chờ phiếu", h4)
        self.assertIn("✓", td.hang_lan(l, nac=5))
        h0 = td.hang_lan(l)  # không có GitHub: như cũ
        self.assertIn("--p:0", h0); self.assertNotIn("nấc PR", h0)
        self.assertEqual(td.hang_lan(dict(l, cho=["Chờ phiếu"]), nac=3).count("Chờ phiếu"), 1)

    def test_lam_nac_va_nhanh_la(self):
        self.assertEqual(td.lam_nac({"pr": 7}, {7: {"nac": 4}}.get, None), 4)
        self.assertEqual(td.lam_nac({"nhanh": "--output=x"}, None, Path(".")), 0)
        self.assertEqual(td.lam_nac({"nhanh": "a..b"}, None, Path(".")), 0)
        self.assertEqual(td.lam_nac({}, None, Path(".")), 0)


if __name__ == "__main__":
    unittest.main()
