import contextlib
import importlib.util
import io
import json
import os
import unittest
from pathlib import Path
from unittest import mock

from cong import gate_app, ten

_DAC_TA = importlib.util.spec_from_file_location(
    "bat_cong", Path(__file__).resolve().parents[2] / "nghiem-thu/bat_cong.py")
bat_cong = importlib.util.module_from_spec(_DAC_TA)
_DAC_TA.loader.exec_module(bat_cong)

APP = 123
DUNG_BV = {
    "required_status_checks": {"checks": [{"context": ten.CHECK_CUOI, "app_id": APP}]},
    "enforce_admins": {"enabled": True}, "required_pull_request_reviews": {"url": "x"},
    "allow_force_pushes": {"enabled": False}, "allow_deletions": {"enabled": False},
}
DUNG_MT = {"can_admins_bypass": False,
           "deployment_branch_policy": {"custom_branch_policies": True, "protected_branches": False}}
DUNG_CS = {"branch_policies": [{"name": ten.NHANH_GOC, "type": "branch"}]}
DUNG_QUYEN = {"default_workflow_permissions": "read", "can_approve_pull_request_reviews": False}
DUNG_KHO = {"allow_rebase_merge": False}


def main(argv, env=None):
    ra = io.StringIO()
    with mock.patch.dict(os.environ, env or {}, clear=True), contextlib.redirect_stdout(ra):
        return bat_cong.main(argv), ra.getvalue()


class TestKeHoach(unittest.TestCase):
    def test_check_co_nguon_la_app(self):
        bv = bat_cong.ke_hoach(APP)[-1]["body"]
        self.assertEqual(bv["required_status_checks"]["checks"], [{"context": ten.CHECK_CUOI, "app_id": APP}])
        self.assertTrue(bv["enforce_admins"])
        self.assertFalse(bv["allow_force_pushes"])
        self.assertIsNotNone(bv["required_pull_request_reviews"])

    def test_environment_chi_nhanh_goc(self):
        ke = bat_cong.ke_hoach(APP)
        self.assertTrue(ke[0]["body"]["deployment_branch_policy"]["custom_branch_policies"])
        self.assertFalse(ke[0]["body"]["deployment_branch_policy"]["protected_branches"])
        self.assertIs(ke[0]["body"]["can_admins_bypass"], False)
        self.assertEqual(ke[1]["body"], {"name": ten.NHANH_GOC, "type": "branch"})

    def test_github_token_chi_doc_khong_duyet_pr(self):
        buoc = [b for b in bat_cong.ke_hoach(APP) if b["duong"] == "/actions/permissions/workflow"]
        self.assertEqual([b["body"] for b in buoc], [DUNG_QUYEN])

    def test_tat_merge_kieu_rebase(self):
        self.assertEqual([b["body"] for b in bat_cong.ke_hoach(APP) if b["duong"] == ""], [DUNG_KHO])


class TestKho(unittest.TestCase):
    def test_kho_khong_goi_mang_khong_can_token(self):
        with mock.patch.object(bat_cong, "GitHub", side_effect=AssertionError("không được tạo")):
            ma, ra = main(["--repo", "chu/repo", "--app-id", "123", "--kho"])
        self.assertEqual(ma, 0)
        self.assertIn("PUT /repos/chu/repo/branches/main/protection", ra)
        self.assertIn('"app_id": 123', ra)

    def test_tu_choi_app_id_bat_ky(self):
        for so in ("-1", "0"):
            with self.subTest(so):
                self.assertEqual(main(["--repo", "chu/repo", "--app-id=" + so, "--kho"])[0], 2)

    def test_tu_choi_repo_rac(self):
        self.assertEqual(main(["--repo", "x/../../y", "--app-id", "1", "--kho"])[0], 2)

    def test_thieu_token_khi_chay_that(self):
        self.assertEqual(main(["--repo", "chu/repo", "--app-id", "1"])[0], 2)


class TestLoi(unittest.TestCase):
    def test_in_than_loi_de_sua_duoc(self):
        loi = gate_app.LoiApi("PUT x: HTTP 422", 422, "Invalid request: contexts")
        with mock.patch.object(bat_cong, "ap_dung", side_effect=loi):
            ma, ra = main(["--repo", "chu/repo", "--app-id", "1"], {"GH_TOKEN": "ghp_bimat"})
        self.assertEqual(ma, 1)
        self.assertIn("Invalid request: contexts", ra)
        self.assertNotIn("ghp_bimat", ra)


class TestKiemLai(unittest.TestCase):
    def test_dung_het(self):
        self.assertEqual(bat_cong.kiem_lai(DUNG_BV, DUNG_MT, DUNG_CS, DUNG_QUYEN, DUNG_KHO, APP), [])

    def test_con_merge_kieu_rebase_la_sai(self):
        for kho in ({"allow_rebase_merge": True}, {}):
            with self.subTest(str(kho)):
                self.assertEqual(len(bat_cong.kiem_lai(DUNG_BV, DUNG_MT, DUNG_CS, DUNG_QUYEN, kho, APP)), 1)

    def test_bat_tung_cho_sai(self):
        cac_ca = [
            ({"required_status_checks": {"checks": [{"context": ten.CHECK_CUOI, "app_id": -1}]}}, {}, {}, {}),
            ({"enforce_admins": {"enabled": False}}, {}, {}, {}),
            ({"required_pull_request_reviews": None}, {}, {}, {}),
            ({"allow_force_pushes": {"enabled": True}}, {}, {}, {}),
            ({"allow_deletions": {"enabled": True}}, {}, {}, {}),
            ({}, {"deployment_branch_policy": None}, {}, {}),
            ({}, {"can_admins_bypass": True}, {}, {}),
            ({}, {}, {"branch_policies": [{"name": "*", "type": "branch"}]}, {}),
            ({}, {}, {"branch_policies": [{"name": ten.NHANH_GOC, "type": "tag"}]}, {}),
            ({}, {}, {"branch_policies": DUNG_CS["branch_policies"] + [{"name": "dev", "type": "branch"}]}, {}),
            ({}, {}, {}, {"default_workflow_permissions": "write"}),
            ({}, {}, {}, {"can_approve_pull_request_reviews": True}),
        ]
        for bv, mt, cs, quyen in cac_ca:
            with self.subTest(str((bv, mt, cs, quyen))):
                sai = bat_cong.kiem_lai(dict(DUNG_BV, **bv), dict(DUNG_MT, **mt), dict(DUNG_CS, **cs),
                                        dict(DUNG_QUYEN, **quyen), DUNG_KHO, APP)
                self.assertEqual(len(sai), 1)


class GhGia(gate_app.GiaLap):
    def goi(self, phuong_thuc, duong, body=None):
        if phuong_thuc == "POST":
            self.da_phat.append((phuong_thuc, duong, body))
            raise gate_app.LoiApi("đã có", 303)
        return super().goi(phuong_thuc, duong, body)


class TestApDung(unittest.TestCase):
    def _gh(self, bao_ve=DUNG_BV, kho=DUNG_KHO):
        mt = "/environments/" + ten.MOI_TRUONG
        return GhGia(json.loads(json.dumps({
            "/branches/%s/protection" % ten.NHANH_GOC: bao_ve, mt: DUNG_MT,
            mt + "/deployment-branch-policies": DUNG_CS, "/actions/permissions/workflow": DUNG_QUYEN, "": kho})))

    def test_chinh_sach_da_co_khong_tinh_la_loi(self):
        gh = self._gh()
        self.assertEqual(bat_cong.ap_dung(gh, APP), [])
        self.assertEqual([x[0] for x in gh.da_phat], ["PUT", "POST", "PUT", "PATCH", "PUT"])

    def test_doc_lai_sai_thi_bao(self):
        self.assertTrue(bat_cong.ap_dung(self._gh(dict(DUNG_BV, enforce_admins={"enabled": False})), APP))

    def test_doc_lai_rebase_con_bat_thi_bao(self):
        self.assertTrue(bat_cong.ap_dung(self._gh(kho={"allow_rebase_merge": True}), APP))
