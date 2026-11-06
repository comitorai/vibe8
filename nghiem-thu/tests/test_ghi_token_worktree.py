"""Lượt trong worktree lấy nhánh của worktree, không lấy gitBranch cũ của thư mục mở phiên (PR 45 mất số, 06/11)."""
import subprocess
import tempfile
import unittest
from pathlib import Path

from test_ghi_token import GOC, ThuMuc, ghi_token, luot

WT = GOC + "/.claude/worktrees/l12"


def cong(*dong, nhanh_wt=None):
    with ThuMuc() as tm:
        return ghi_token.cong_theo_nhanh([tm.tep("a.jsonl", dong)], GOC, nhanh_wt=nhanh_wt)


class TheoWorktree(unittest.TestCase):
    def test_luot_trong_worktree_tinh_cho_nhanh_worktree(self):
        # Phiên mở ở bản chính đang ở nhánh chon-model, rồi cd vào worktree l12 (nhánh luat-l12):
        # Claude Code vẫn ghi gitBranch=chon-model.
        k = cong(luot("m1", "chon-model", "2026-01-01T00:00:01Z"),
                 luot("m2", "chon-model", "2026-01-01T00:00:02Z", cwd=WT),
                 luot("m3", "chon-model", "2026-01-01T00:00:03Z", cwd=WT + "/luat"),
                 nhanh_wt={WT: "luat-l12"})
        self.assertEqual(k["chon-model"]["luot"], 1)
        self.assertEqual(k["luat-l12"]["luot"], 2)

    def test_khong_co_ban_do_thi_giu_gitbranch(self):
        k = cong(luot("m1", "x", "2026-01-01T00:00:01Z", cwd=WT))
        self.assertEqual(set(k), {"x"})

    def test_worktree_sau_nhat_thang_va_ten_gan_giong_khong_khop(self):
        sau = WT + "/con"
        self.assertEqual(ghi_token._nhanh_theo_cwd(sau + "/a", "g", {WT: "ngoai", sau: "trong"}), "trong")
        self.assertEqual(ghi_token._nhanh_theo_cwd(WT + "-khac", "g", {WT: "ngoai"}), "g")

    def test_worktree_o_nhanh_goc_van_chuyen_cho_nhanh_ke_tiep(self):
        # Worktree đang ở main: lượt đó vẫn là «việc trước khi tạo nhánh».
        k = cong(luot("m1", "x", "2026-01-01T00:00:01Z", cwd=WT),
                 luot("m2", "x", "2026-01-01T00:00:02Z"),
                 nhanh_wt={WT: "main"})
        self.assertEqual(k["x"]["luot"], 2)
        self.assertEqual(k["x"]["moi_truoc"], 115)


class DocWorktree(unittest.TestCase):
    def test_doc_porcelain_bo_ban_chinh_va_head_roi(self):
        ra = ("worktree %s\nHEAD a\nbranch refs/heads/main\n\n"
              "worktree %s\nHEAD b\nbranch refs/heads/luat-l12\n\n"
              "worktree %s/.claude/worktrees/roi\nHEAD c\ndetached\n" % (GOC, WT, GOC))
        self.assertEqual(ghi_token._doc_worktree(ra, GOC), {WT: "luat-l12"})

    def test_git_that(self):
        with tempfile.TemporaryDirectory() as td:
            goc = Path(td).resolve() / "repo"
            chay = lambda *l, cwd=goc: subprocess.run(["git", *l], cwd=cwd, check=True, capture_output=True)  # noqa: E731
            goc.mkdir()
            chay("init", "-q", "-b", "main")
            chay("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "a")
            chay("worktree", "add", "-q", str(goc / ".claude/worktrees/w"), "-b", "nhanh-w")
            self.assertEqual(ghi_token.nhanh_cua_worktree(goc), {str(goc / ".claude/worktrees/w"): "nhanh-w"})
        self.assertEqual(ghi_token.nhanh_cua_worktree(Path("/khong/co/repo/nay")), {})


if __name__ == "__main__":
    unittest.main()
