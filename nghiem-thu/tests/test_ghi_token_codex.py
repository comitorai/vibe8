import contextlib
import importlib.util
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock


def _nap(ten):
    dac_ta = importlib.util.spec_from_file_location(ten, Path(__file__).resolve().parents[2] / ("nghiem-thu/%s.py" % ten))
    mo_dun = importlib.util.module_from_spec(dac_ta)
    dac_ta.loader.exec_module(mo_dun)
    return mo_dun


ghi_token = _nap("ghi_token")

GOC = "/nha/lab/repo"


def mo_phien(phien="c1", nhanh="a", cwd=GOC):
    return {"timestamp": "2026-01-01T00:00:00Z", "type": "session_meta",
            "payload": {"id": phien, "session_id": phien, "cwd": cwd, "git": {"branch": nhanh} if nhanh else {}}}


def luot_codex(turn, cwd=GOC):
    return {"timestamp": "2026-01-01T00:00:01Z", "type": "turn_context", "payload": {"turn_id": turn, "cwd": cwd}}


def dung(turn, resp, luc="2026-01-01T00:00:02Z", vao=1000, dem=600, ra=50, phien="c1"):
    return {"timestamp": luc, "type": "token_usage_record",
            "payload": {"session_id": phien, "turn_id": turn, "response_id": resp,
                        "usage": {"input_tokens": vao, "cached_input_tokens": dem, "cache_write_input_tokens": 0,
                                  "output_tokens": ra, "reasoning_output_tokens": 10, "total_tokens": vao + ra}}}


class ThuMuc:
    def __enter__(self):
        self._td = tempfile.TemporaryDirectory()
        self.goc = Path(self._td.name)
        return self

    def __exit__(self, *a):
        self._td.cleanup()

    def tep(self, ten, dong):
        t = self.goc / ten
        t.parent.mkdir(parents=True, exist_ok=True)
        t.write_text("\n".join(d if isinstance(d, str) else json.dumps(d) for d in dong) + "\n")
        return t


class TestLuotCodex(unittest.TestCase):
    def cong(self, dong, goc_nhanh=("main",)):
        with ThuMuc() as tm:
            return ghi_token.cong_theo_nhanh([tm.tep("r.jsonl", dong)], GOC, goc_nhanh, ghi_token._luot_goi_codex)

    def test_token_moi_tru_phan_doc_dem(self):
        kq = self.cong([mo_phien(), luot_codex("t1"), dung("t1", "r1")])
        self.assertEqual(kq["a"], {"phien": 1, "luot": 1, "moi": 450, "doc_dem": 600, "moi_truoc": 0})

    def test_response_id_trung_chi_tinh_mot_lan(self):
        kq = self.cong([mo_phien(), luot_codex("t1"), dung("t1", "r1"), dung("t1", "r1"), dung("t1", "r2")])
        self.assertEqual(kq["a"]["luot"], 2)

    def test_cwd_ngoai_repo_bo_qua(self):
        kq = self.cong([mo_phien(), luot_codex("t1", "/nha/lab/repo-khac"), dung("t1", "r1"),
                        luot_codex("t2", GOC + "/con"), dung("t2", "r2")])
        self.assertEqual(kq["a"]["luot"], 1)

    def test_luot_khong_co_turn_context_bo_qua(self):
        self.assertEqual(self.cong([mo_phien(), dung("t9", "r1")]), {})

    def test_khong_co_nhanh_bo_qua(self):
        self.assertEqual(self.cong([mo_phien(nhanh=None), luot_codex("t1"), dung("t1", "r1")]), {})

    def test_phien_tren_main_khong_tinh(self):
        self.assertEqual(self.cong([mo_phien(nhanh="main"), luot_codex("t1"), dung("t1", "r1")]), {})

    def test_dong_hong_va_so_am(self):
        kq = self.cong(["{hong", "[]", {"type": "token_usage_record", "payload": "x"}, mo_phien(), luot_codex("t1"),
                        dung("t1", "r1", vao=-5, dem=-1, ra=7), dung("t1", "r2", vao=100, dem=900, ra=0)])
        self.assertEqual((kq["a"]["moi"], kq["a"]["doc_dem"]), (7, 100))  # đệm không vượt input

    def test_hai_phien_hai_tep(self):
        with ThuMuc() as tm:
            a = tm.tep("a.jsonl", [mo_phien("c1"), luot_codex("t1"), dung("t1", "r1", phien="c1")])
            b = tm.tep("b.jsonl", [mo_phien("c2"), luot_codex("t1"), dung("t1", "r2", phien="c2")])
            kq = ghi_token.cong_theo_nhanh([a, b], GOC, doc_luot=ghi_token._luot_goi_codex)
        self.assertEqual((kq["a"]["phien"], kq["a"]["luot"]), (2, 2))

    def test_ban_ghi_claude_khong_bi_doc_nhu_codex(self):
        claude = {"type": "assistant", "cwd": GOC, "gitBranch": "a", "sessionId": "p", "timestamp": "2026-01-01T00:00:01Z",
                  "requestId": "q", "message": {"id": "m", "usage": {"input_tokens": 9}}}
        self.assertEqual(self.cong([claude]), {})


class GhGia:
    def __init__(self):
        self.ghi = []

    def goi(self, phuong, duong, than=None):
        if duong == "/pulls/9":
            return {"number": 9, "head": {"ref": "a", "repo": {"full_name": "chu/repo"}}, "base": {"ref": "main"}}
        if phuong == "GET":
            return []
        self.ghi.append((phuong, duong, than))
        return {}

    def che(self, s):
        return s


class TestChayCodex(unittest.TestCase):
    def chay(self, claude, codex):
        with ThuMuc() as tm:
            if claude:
                tm.tep("cl/-x/p.jsonl", claude)
            tm.tep("cx/2026/01/01/r.jsonl", codex)
            gh, ra = GhGia(), io.StringIO()
            with mock.patch.dict(os.environ, {"GH_TOKEN": "ghs_abc"}), mock.patch.object(ghi_token, "GitHub", lambda *a: gh), \
                    mock.patch.object(ghi_token.platform, "node", lambda: "mn"), \
                    contextlib.redirect_stdout(ra), contextlib.redirect_stderr(io.StringIO()):
                ma = ghi_token.main(["--repo", "chu/repo", "--pr", "9", "--goc", GOC, "--ban-ghi", str(tm.goc / "cl"),
                                     "--ban-ghi-codex", str(tm.goc / "cx")])
            return ma, gh

    def test_dong_codex_rieng_va_cong_vao_tong(self):
        claude = [{"type": "assistant", "cwd": GOC, "gitBranch": "a", "sessionId": "p", "timestamp": "2026-01-01T00:00:01Z",
                   "requestId": "q", "message": {"id": "m", "usage": {"input_tokens": 10, "output_tokens": 5}}}]
        ma, gh = self.chay(claude, [mo_phien(), luot_codex("t1"), dung("t1", "r1")])
        self.assertEqual(ma, 0)
        than = gh.ghi[0][2]["body"]
        self.assertIn("| mn codex | 1 | 1 | 450 |", than)
        self.assertIn("| mn | 1 | 1 | 15 |", than)
        self.assertIn("token-moi: 465", than)
        self.assertEqual(set(ghi_token.doc_comment(than)), {"mn", "mn codex"})

    def test_chi_co_codex_van_ghi(self):
        ma, gh = self.chay(None, [mo_phien(), luot_codex("t1"), dung("t1", "r1")])
        self.assertEqual(ma, 0)
        self.assertIn("token-moi: 450", gh.ghi[0][2]["body"])

    def test_codex_nhanh_khac_khong_ghi(self):
        ma, gh = self.chay(None, [mo_phien(nhanh="b"), luot_codex("t1"), dung("t1", "r1")])
        self.assertEqual((ma, gh.ghi), (1, []))


if __name__ == "__main__":
    unittest.main()
