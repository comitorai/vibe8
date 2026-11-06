"""Hook ghi token trước khi merge bằng `gh api … /pulls/N/merge` (13/27 PR merge thiếu số máy ghi, 06/11)."""
import importlib.util
import io
import json
import subprocess
import unittest
from pathlib import Path
from unittest import mock

GOC_REPO = Path(__file__).resolve().parents[2]
_dac_ta = importlib.util.spec_from_file_location("hook_ghi_token", GOC_REPO / "nghiem-thu/hook_ghi_token.py")
hook = importlib.util.module_from_spec(_dac_ta)
_dac_ta.loader.exec_module(hook)


def kq(ma=0, ra="", loi=""):
    return subprocess.CompletedProcess([], ma, ra, loi)


class CanGhiApi(unittest.TestCase):
    def test_merge_qua_gh_api_lay_so_pr(self):
        for lenh, so in (
            ("gh api -X PUT repos/comitorai/vibe8/pulls/45/merge -f sha=abc -f merge_method=merge", 45),
            ("GH_TOKEN=x gh api --method PUT /repos/comitorai/vibe8/pulls/7/merge", 7),
            ("gh api -X PUT 'repos/{owner}/{repo}/pulls/12/merge'", 12),
            ('cd x && gh api -X PUT "repos/a/b/pulls/3/merge" -f sha=1', 3),
        ):
            with self.subTest(lenh):
                self.assertEqual(hook.can_ghi("PreToolUse", "Bash", lenh), (True, so))

    def test_khong_phai_merge(self):
        for su_kien, lenh in (
            ("PreToolUse", "gh api repos/a/b/pulls/45"),
            ("PreToolUse", "gh api repos/a/b/pulls/45/merged"),
            ("PreToolUse", "gh api repos/a/b/pulls/45/reviews"),
            ("PreToolUse", "echo repos/a/b/pulls/45/merge"),
            ("PreToolUse", "gh api repos/a/b/issues/45 && echo repos/a/b/pulls/9/merge"),
            ("PostToolUse", "gh api -X PUT repos/a/b/pulls/45/merge"),
        ):
            with self.subTest(lenh):
                self.assertEqual(hook.can_ghi(su_kien, "Bash", lenh)[0], False)

    def test_repo_trong_lenh(self):
        self.assertEqual(hook.repo_merge_api("gh api -X PUT repos/comitorai/vibe8/pulls/45/merge"), "comitorai/vibe8")
        self.assertIsNone(hook.repo_merge_api("gh api -X PUT repos/{owner}/{repo}/pulls/45/merge"))
        self.assertIsNone(hook.repo_merge_api("gh pr merge 45"))
        self.assertIsNone(hook.repo_merge_api(None))


class GhiApi(unittest.TestCase):
    def test_repo_khac_origin_thi_bo_va_im(self):
        with mock.patch.object(hook, "_chay", side_effect=[kq(ra="https://github.com/comitorai/vibe8.git\n")]) as chay:
            ok, bao = hook.ghi("/r", 45, "khac/repo")
        self.assertFalse(ok)
        self.assertEqual(chay.call_count, 1)  # không xin token, không chạy máy ghi
        self.assertIsNone(hook.tra_loi("PreToolUse", ok, bao))

    def test_cung_repo_khong_phan_biet_hoa_thuong(self):
        with mock.patch.object(hook, "_chay", side_effect=[kq(ra="https://github.com/comitorai/vibe8\n"),
                                                           kq(ra="gho_bimat\n"), kq(ra="PR 45 · token mới 9\n")]) as chay:
            ok, _ = hook.ghi("/r", 45, "ComitorAI/vibe8")
        self.assertTrue(ok)
        self.assertEqual(chay.call_args_list[2][0][0][-4:], ["--repo", "comitorai/vibe8", "--pr", "45"])


class MainApi(unittest.TestCase):
    def _main(self, lenh):
        vao = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "cwd": "/r", "tool_input": {"command": lenh}}
        ra = io.StringIO()
        with mock.patch("sys.stdout", ra):
            return hook.main(io.StringIO(json.dumps(vao))), ra.getvalue()

    def test_truyen_repo_cua_lenh(self):
        with mock.patch.object(hook, "ghi", return_value=(True, "PR 45")) as ghi:
            self.assertEqual(self._main("gh api -X PUT repos/comitorai/vibe8/pulls/45/merge -f sha=a"), (0, ""))
        ghi.assert_called_once_with("/r", 45, "comitorai/vibe8")

    def test_placeholder_dung_repo_hien_tai(self):
        with mock.patch.object(hook, "ghi", return_value=(True, "PR 12")) as ghi:
            self._main("gh api -X PUT repos/{owner}/{repo}/pulls/12/merge")
        ghi.assert_called_once_with("/r", 12)


if __name__ == "__main__":
    unittest.main()
