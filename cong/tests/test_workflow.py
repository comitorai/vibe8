"""Rà workflow bằng chữ, chỉ stdlib. Không thay được actionlint và không chứng minh chạy đúng trên GitHub."""
import re
import unittest
from pathlib import Path

from cong import ten

GOC = Path(__file__).resolve().parents[2]
NHANH = (GOC / ".github/workflows/cong-nhanh.yml").read_text(encoding="utf-8")
CUOI = (GOC / ".github/workflows/cong-cuoi.yml").read_text(encoding="utf-8")
TIN_HIEU = (GOC / ".github/workflows/tin-hieu-duyet.yml").read_text(encoding="utf-8")
BIEU_THUC_SHA = "${{ github.event.workflow_run.head_sha || github.event.pull_request.head.sha }}"
KHONG_XET_PR_DA_MERGE = "if: github.event.pull_request.merged != true"


def khoi_run(yml):
    dong = yml.splitlines()
    ket, i = [], 0
    while i < len(dong):
        m = re.match(r"^(\s*)(- )?run:\s*(.*)$", dong[i])
        i += 1
        if not m:
            continue
        khoi = [m.group(3)]
        thut = len(m.group(1))
        while i < len(dong) and (not dong[i].strip() or len(dong[i]) - len(dong[i].lstrip()) > thut):
            khoi.append(dong[i])
            i += 1
        ket.append("\n".join(khoi))
    return ket


class TestChungCacWorkflow(unittest.TestCase):
    def test_khoi_run_doc_duoc_chu(self):
        self.assertEqual(len(khoi_run(CUOI)), 1)
        self.assertEqual(khoi_run("a:\n  - run: |\n      x\n      y\n  - b: c"), ["|\n      x\n      y"])

    def test_action_ghim_sha(self):
        for yml in (NHANH, CUOI):
            ds = re.findall(r"uses:\s*(\S+)", yml)
            self.assertTrue(ds)
            for x in ds:
                self.assertRegex(x, r"^[\w./-]+@[0-9a-f]{40}$")

    def test_khong_noi_suy_vao_run(self):
        for yml in (NHANH, CUOI, TIN_HIEU):
            for khoi in khoi_run(yml):
                self.assertNotIn("${{", khoi)

    def test_checkout_khong_giu_credential(self):
        for yml in (NHANH, CUOI):
            self.assertEqual(yml.count("actions/checkout@"), yml.count("persist-credentials: false"))


class TestCongNhanh(unittest.TestCase):
    def test_su_kien_va_quyen(self):
        self.assertIn("\n  pull_request:\n", NHANH)
        self.assertRegex(NHANH, r"types: \[[^\]]*\bedited\b")  # đổi base phải sinh lượt mới
        self.assertNotIn("pull_request_target", NHANH)
        self.assertIn("permissions:\n  contents: read\n", NHANH)

    def test_khong_secret_khong_macos_khong_self_hosted(self):
        self.assertNotIn("secrets.", NHANH)
        self.assertIn("runs-on: ubuntu-latest", NHANH)
        self.assertNotIn("self-hosted", NHANH)

    def test_ten_check(self):
        self.assertIn("name: %s\n" % ten.CHECK_NHANH, NHANH)

    def test_khong_huy_luot_dang_chay(self):
        # Lượt bị huỷ thành `cancelled`, mà cổng đòi mọi lượt của SHA đều xanh.
        self.assertNotIn("concurrency", NHANH)

    def test_app_mau_cung_ban(self):
        mau = (GOC / "nghiem-thu/app-mau/.github/workflows/cong-nhanh.yml").read_text(encoding="utf-8")
        self.assertEqual(mau, NHANH)


class TestCongCuoi(unittest.TestCase):
    def test_su_kien(self):
        self.assertRegex(CUOI, r"\n  pull_request_target:[^\n]*\n    branches: \[%s\]\n" % ten.NHANH_GOC)
        self.assertRegex(CUOI, r"\n  workflow_run:[^\n]*\n    workflows: \[%s, tin-hieu-duyet\]\n" % ten.CHECK_NHANH)
        self.assertNotRegex(CUOI, r"\n  pull_request(_review)?:")
        self.assertRegex(CUOI, r"types: \[[^\]]*\bclosed\b")  # đóng một PR trùng SHA thì PR còn lại phải hết kẹt

    def test_khong_cham_ma_pr(self):
        # Chỉ một chỗ được đụng dữ liệu PR: giá trị SHA, chuyển qua env và kiểm dạng trước khi dùng.
        job = re.sub(r"(?m)^\s*#.*$", "", CUOI.split("\njobs:")[1]).replace(BIEU_THUC_SHA, "").replace(KHONG_XET_PR_DA_MERGE, "")
        for cam in ("pull_request.head", "head_ref", "github.event.pull_request.merge", "refs/pull", "github.sha"):
            self.assertNotIn(cam, job)

    def test_pr_da_merge_khong_danh_do_commit(self):
        self.assertIn(KHONG_XET_PR_DA_MERGE, CUOI)

    def test_chi_lay_thu_muc_cong(self):
        # F1: symlink `json` ở gốc repo nạp thay thư viện chuẩn trong job cầm token, đã tái hiện trên runner thật.
        self.assertIn("sparse-checkout: /cong/\n", CUOI)
        self.assertIn("sparse-checkout-cone-mode: false\n", CUOI)

    def test_checkout_nhanh_goc(self):
        self.assertEqual(CUOI.count("actions/checkout@"), 1)
        self.assertIn("ref: ${{ github.event.repository.default_branch }}", CUOI)

    def test_quyen_toi_thieu(self):
        self.assertIn("\npermissions: {}\n", CUOI)
        self.assertIn("permissions:\n      contents: read\n", CUOI)
        self.assertNotRegex(CUOI, r"(?<!permission-)(contents|checks|pull-requests|actions|issues|statuses): write")
        self.assertIn("permission-checks: write", CUOI)
        self.assertIn("permission-pull-requests: read", CUOI)
        self.assertIn("permission-actions: read", CUOI)
        self.assertIn("permission-issues: read", CUOI)
        self.assertEqual(len(re.findall(r"permission-[\w-]+:", CUOI)), 4)
        # Hướng dẫn tạo App phải khớp quyền workflow xin: thiếu một quyền là mọi PR hỏng.
        huong_dan = (GOC / "nghiem-thu/bat_cong.py").read_text(encoding="utf-8")
        for quyen in ("Checks: write", "Pull requests: read", "Actions: read", "Issues: read"):
            self.assertIn(quyen, huong_dan)

    def test_khoa_chi_qua_environment(self):
        self.assertIn("environment: %s\n" % ten.MOI_TRUONG, CUOI)
        self.assertEqual(CUOI.count("secrets."), 1)
        self.assertIn("private-key: ${{ secrets.%s }}" % ten.BIEN_KHOA_APP, CUOI)
        self.assertIn("client-id: ${{ vars.%s }}" % ten.BIEN_APP_CLIENT_ID, CUOI)

    def test_ten_job_khong_trung_check_cuoi(self):
        ten_job = re.findall(r"^    name: (\S+)$", CUOI, re.M)
        self.assertEqual(len(ten_job), 1)
        self.assertNotEqual(ten_job[0], ten.CHECK_CUOI)

    def test_luot_xet_gom_theo_sha_khong_huy(self):
        # Cùng một biểu thức với SHA truyền vào cổng: nhóm, SHA xét và SHA phát phải là một.
        self.assertIn("group: cong-cuoi-" + BIEU_THUC_SHA, CUOI)
        self.assertIn("cancel-in-progress: false", CUOI)

    def test_goi_dung_bien(self):
        self.assertIn("%s: ${{ steps.token.outputs.token }}" % ten.BIEN_TOKEN_APP, CUOI)
        self.assertIn("%s: %s" % (ten.BIEN_SHA, BIEU_THUC_SHA), CUOI)
        self.assertNotIn("pull_request.number", CUOI)
        self.assertNotIn("NGUOI_DUYET", CUOI)  # L9: cộng tác viên quyền ghi sửa được biến environment.
        self.assertIn("python3 -m cong.gate_app", CUOI)


class TestTinHieuDuyet(unittest.TestCase):
    def test_chi_danh_thuc_khong_co_gi_de_lay(self):
        self.assertIn("\npermissions: {}\n", TIN_HIEU)
        for cam in ("secrets.", "uses:", "environment:", "vars.", "${{"):
            self.assertNotIn(cam, TIN_HIEU)

    def test_nghe_du_loai_lan_xet(self):
        self.assertIn("\n  pull_request_review:\n    types: [submitted, edited, dismissed]\n", TIN_HIEU)

    def test_ten_khop_cong_cuoi(self):
        self.assertIn("name: tin-hieu-duyet\n", TIN_HIEU)


class TestAppMau(unittest.TestCase):
    def test_khong_qua_15_tep(self):
        tep = [p for p in (GOC / "nghiem-thu/app-mau").rglob("*")
               if p.is_file() and "__pycache__" not in p.parts]
        self.assertLessEqual(len(tep), 15)
