import importlib.util
import io
import json
import subprocess
import unittest
from pathlib import Path
from unittest import mock

GOC_REPO = Path(__file__).resolve().parents[2]


def _nap(ten):
    dac_ta = importlib.util.spec_from_file_location(ten, GOC_REPO / ("nghiem-thu/%s.py" % ten))
    mo_dun = importlib.util.module_from_spec(dac_ta)
    dac_ta.loader.exec_module(mo_dun)
    return mo_dun


hook = _nap("hook_ghi_token")


def kq(ma=0, ra="", loi=""):
    return subprocess.CompletedProcess([], ma, ra, loi)


class CanGhi(unittest.TestCase):
    def test_sau_khi_day_va_tao_pr(self):
        for lenh in ("git push", "git push -u origin nhanh", "git add . && git commit -m x && git push",
                     "git -C ~/lab/repo push origin x", "gh pr create --title a --body b",
                     "cd x; git push", "(git push)"):
            with self.subTest(lenh):
                self.assertEqual(hook.can_ghi("PostToolUse", "Bash", lenh), (True, None))

    def test_khong_ghi(self):
        for su_kien, tool, lenh in (("PostToolUse", "Bash", "git status"), ("PostToolUse", "Bash", "git pushx"),
                                    ("PostToolUse", "Bash", "echo gitpush"), ("PostToolUse", "Read", "git push"),
                                    ("PreToolUse", "Bash", "git push"), ("PostToolUse", "Bash", "gh pr merge 3"),
                                    ("PostToolUse", "Bash", None), ("Stop", "Bash", "git push"),
                                    ("PostToolUse", "Bash", "gh pr view 3")):
            with self.subTest(lenh):
                self.assertEqual(hook.can_ghi(su_kien, tool, lenh)[0], False)

    def test_truoc_merge_lay_so_pr(self):
        self.assertEqual(hook.can_ghi("PreToolUse", "Bash", "gh pr merge 35 --squash"), (True, 35))
        self.assertEqual(hook.can_ghi("PreToolUse", "Bash", "gh pr merge --merge 36 --delete-branch"), (True, 36))
        self.assertEqual(hook.can_ghi("PreToolUse", "Bash", "gh pr merge #37"), (True, 37))
        self.assertEqual(hook.can_ghi("PreToolUse", "Bash", "gh pr merge --squash"), (True, None))
        # Số sau dấu nối lệnh không phải số PR.
        self.assertEqual(hook.can_ghi("PreToolUse", "Bash", "gh pr merge --squash && sleep 5"), (True, None))


class Remote(unittest.TestCase):
    def test_doc_repo(self):
        for url in ("https://github.com/comitorai/vibe8.git", "https://github.com/comitorai/vibe8",
                    "git@github.com:comitorai/vibe8.git\n", "ssh://git@github.com/comitorai/vibe8.git"):
            with self.subTest(url):
                self.assertEqual(hook.repo_tu_remote(url), "comitorai/vibe8")
        self.assertIsNone(hook.repo_tu_remote("https://gitlab.com/a/b.git"))
        self.assertIsNone(hook.repo_tu_remote(""))


class Ghi(unittest.TestCase):
    def _chay(self, *ket):
        return mock.patch.object(hook, "_chay", side_effect=list(ket))

    def test_ghi_dung_repo_va_so_pr_khong_lo_token(self):
        with self._chay(kq(ra="https://github.com/a/b.git\n"), kq(ra="gho_bimat\n"),
                        kq(ra="PR 35 · nhánh x · token mới 10\n")) as chay:
            ok, bao = hook.ghi("/r", 35)
        self.assertTrue(ok)
        self.assertEqual(bao, "PR 35 · nhánh x · token mới 10")
        lenh, cwd, env = chay.call_args_list[2][0]
        self.assertEqual(lenh[-4:], ["--repo", "a/b", "--pr", "35"])
        self.assertEqual(env["GH_TOKEN"], "gho_bimat")
        self.assertNotIn("gho_bimat", " ".join(lenh))

    def test_loi_khong_lo_token(self):
        with self._chay(kq(ra="https://github.com/a/b\n"), kq(ra="gho_bimat\n"), kq(1, loi="lỗi gho_bimat\n")):
            ok, bao = hook.ghi("/r", None)
        self.assertFalse(ok)
        self.assertNotIn("gho_bimat", bao)

    def test_thieu_gh_hoac_remote_la(self):
        with self._chay(kq(ra="https://gitlab.com/a/b\n")):
            self.assertFalse(hook.ghi("/r", None)[0])
        with self._chay(kq(ra="https://github.com/a/b\n"), kq(1)):
            self.assertIn("gh auth token", hook.ghi("/r", None)[1])
        with mock.patch.object(hook, "_chay", side_effect=FileNotFoundError):
            self.assertFalse(hook.ghi("/r", None)[0])
        with mock.patch.object(hook, "_chay", side_effect=subprocess.TimeoutExpired("x", 50)):
            self.assertFalse(hook.ghi("/r", None)[0])


class TraLoi(unittest.TestCase):
    def test_sau_push_bao_agent(self):
        ra = hook.tra_loi("PostToolUse", True, "PR 35 · token mới 10")
        self.assertEqual(ra["hookSpecificOutput"]["hookEventName"], "PostToolUse")
        self.assertIn("token mới 10", ra["hookSpecificOutput"]["additionalContext"])
        ra = hook.tra_loi("PostToolUse", False, "403")
        self.assertIn("Chạy tay", ra["hookSpecificOutput"]["additionalContext"])

    def test_chua_co_pr_thi_im(self):
        self.assertIsNone(hook.tra_loi("PostToolUse", False, "nhánh x chưa có PR"))

    def test_truoc_merge_chi_bao_khi_hong(self):
        self.assertIsNone(hook.tra_loi("PreToolUse", True, "PR 35"))
        self.assertIn("systemMessage", hook.tra_loi("PreToolUse", False, "403"))


class Main(unittest.TestCase):
    def _main(self, vao):
        ra = io.StringIO()
        with mock.patch("sys.stdout", ra):
            ma = hook.main(io.StringIO(vao if isinstance(vao, str) else json.dumps(vao)))
        return ma, ra.getvalue()

    def test_luon_thoat_0_va_khong_ghi_khi_khong_can(self):
        with mock.patch.object(hook, "ghi") as ghi:
            for vao in ("khong-phai-json", "[]", {"hook_event_name": "PostToolUse", "tool_name": "Bash",
                                                  "tool_input": {"command": "ls"}}):
                with self.subTest(vao):
                    self.assertEqual(self._main(vao), (0, ""))
        ghi.assert_not_called()

    def test_ghi_hong_van_khong_chan_merge(self):
        with mock.patch.object(hook, "ghi", return_value=(False, "403")) as ghi:
            ma, ra = self._main({"hook_event_name": "PreToolUse", "tool_name": "Bash", "cwd": "/r",
                                 "tool_input": {"command": "gh pr merge 40 --squash"}})
        self.assertEqual(ma, 0)
        ghi.assert_called_once_with("/r", 40)
        self.assertIn("systemMessage", json.loads(ra))


class CauHinh(unittest.TestCase):
    def test_settings_goi_hook_hai_luc(self):
        d = json.loads((GOC_REPO / ".claude/settings.json").read_text(encoding="utf-8"))
        for su_kien in ("PreToolUse", "PostToolUse"):
            with self.subTest(su_kien):
                (muc,) = d["hooks"][su_kien]
                self.assertEqual(muc["matcher"], "Bash")
                self.assertIn("nghiem-thu/hook_ghi_token.py", muc["hooks"][0]["command"])


if __name__ == "__main__":
    unittest.main()
