import unittest

from cong.rui_ro import CAO, phan_loai


class CauHinhAgent(unittest.TestCase):
    def test_cau_hinh_agent_la_cao(self):
        for ten in (".claude/settings.json", ".claude/settings.local.json", ".claude/commands/x.md",
                    "app/.claude/settings.json", ".mcp.json", "app/.mcp.json"):
            with self.subTest(ten):
                ket = phan_loai([{"filename": ten, "status": "added", "additions": 1, "deletions": 0, "patch": "+x"}])
                self.assertEqual(ket["muc"], CAO)
                self.assertTrue(any("cấu hình agent" in l for l in ket["ly_do"]))

    def test_ten_gan_giong_khong_bi_bat(self):
        for ten in ("docs/claude.md", "docs/.claude.md", "mcp.json.md"):
            with self.subTest(ten):
                ket = phan_loai([{"filename": ten, "status": "added", "additions": 1, "deletions": 0, "patch": "+x"}])
                self.assertFalse(any("cấu hình agent" in l for l in ket["ly_do"]))



if __name__ == "__main__":
    unittest.main()
