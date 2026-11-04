#!/usr/bin/env python3
"""Chủ repo chạy để bật cổng: bảo vệ nhánh gốc, check có expected source là App, environment chỉ cho nhánh gốc.

Tạo GitHub App trước (Checks: write, Pull requests: read, Actions: read) vì lệnh này cần --app-id.
Dùng token của CHỦ REPO qua biến GH_TOKEN (không in ra). --kho chỉ in các lệnh gọi, không cần token, không có mạng.
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cong import ten  # noqa: E402
from cong.gate_app import GitHub, LoiApi  # noqa: E402

_DA_CO = 303  # GitHub trả 303 khi deployment branch policy đã tồn tại.


def ke_hoach(app_id):
    moi_truong = "/environments/" + ten.MOI_TRUONG
    return [
        {"phuong_thuc": "PUT", "duong": moi_truong, "body": {
            "wait_timer": 0, "reviewers": None,
            "deployment_branch_policy": {"protected_branches": False, "custom_branch_policies": True}}},
        {"phuong_thuc": "POST", "duong": moi_truong + "/deployment-branch-policies",
         "body": {"name": ten.NHANH_GOC, "type": "branch"}},
        # GITHUB_TOKEN của workflow trong PR không được ghi, không được duyệt PR.
        {"phuong_thuc": "PUT", "duong": "/actions/permissions/workflow",
         "body": {"default_workflow_permissions": "read", "can_approve_pull_request_reviews": False}},
        {"phuong_thuc": "PUT", "duong": "/branches/%s/protection" % ten.NHANH_GOC, "body": {
            "required_status_checks": {"strict": False, "checks": [{"context": ten.CHECK_CUOI, "app_id": app_id}]},
            "enforce_admins": True,
            # 0 lượt duyệt của GitHub vẫn buộc đi qua PR; việc duyệt do cổng xét theo rủi ro.
            "required_pull_request_reviews": {
                "required_approving_review_count": 0, "dismiss_stale_reviews": False,
                "require_code_owner_reviews": False, "require_last_push_approval": False},
            "restrictions": None, "required_linear_history": False,
            "allow_force_pushes": False, "allow_deletions": False, "lock_branch": False}},
    ]


def kiem_lai(bao_ve, moi_truong, chinh_sach, quyen, app_id):
    """Hàm thuần: đọc lại rồi so, trả danh sách chỗ sai. Ghi được chưa có nghĩa là đã có hiệu lực."""
    sai = []
    checks = (bao_ve.get("required_status_checks") or {}).get("checks")
    if checks != [{"context": ten.CHECK_CUOI, "app_id": app_id}]:
        sai.append("required check không đúng `%s` với app_id %d" % (ten.CHECK_CUOI, app_id))
    if not (bao_ve.get("enforce_admins") or {}).get("enabled"):
        sai.append("admin vẫn được vượt")
    if bao_ve.get("required_pull_request_reviews") is None:
        sai.append("chưa buộc đi qua PR")
    for khoa in ("allow_force_pushes", "allow_deletions"):
        if (bao_ve.get(khoa) or {}).get("enabled") is not False:
            sai.append(khoa + " chưa tắt")
    nhanh = (moi_truong.get("deployment_branch_policy") or {})
    if nhanh.get("custom_branch_policies") is not True or nhanh.get("protected_branches") is not False:
        sai.append("environment chưa giới hạn theo danh sách nhánh")
    ds = [(x.get("name"), x.get("type")) for x in chinh_sach.get("branch_policies") or []]
    if ds != [(ten.NHANH_GOC, "branch")]:
        sai.append("environment phải chỉ cho đúng nhánh %s" % ten.NHANH_GOC)
    if quyen.get("default_workflow_permissions") != "read" or quyen.get("can_approve_pull_request_reviews") is not False:
        sai.append("GITHUB_TOKEN mặc định phải chỉ đọc và không được duyệt PR")
    return sai


def ap_dung(gh, app_id):
    for buoc in ke_hoach(app_id):
        try:
            gh.goi(buoc["phuong_thuc"], buoc["duong"], buoc["body"])
        except LoiApi as loi:
            if loi.ma != _DA_CO:
                raise
    moi_truong = "/environments/" + ten.MOI_TRUONG
    return kiem_lai(gh.goi("GET", "/branches/%s/protection" % ten.NHANH_GOC), gh.goi("GET", moi_truong),
                    gh.goi("GET", moi_truong + "/deployment-branch-policies"),
                    gh.goi("GET", "/actions/permissions/workflow"), app_id)


def in_buoc_tay(repo):
    print("""
Việc script không làm thay được (App đã tạo trước, cài vào %(repo)s):
1. gh secret set %(khoa)s --env %(mt)s --repo %(repo)s
2. gh variable set %(id)s --env %(mt)s --repo %(repo)s
3. gh variable set %(duyet)s --env %(mt)s --repo %(repo)s --body "<login người duyệt, cách nhau dấu phẩy>"
4. Chạy thử một PR rồi xem check `%(check)s` có nguồn là App.""" % {
        "repo": repo, "khoa": ten.BIEN_KHOA_APP, "id": ten.BIEN_APP_CLIENT_ID, "mt": ten.MOI_TRUONG,
        "duyet": ten.BIEN_NGUOI_DUYET, "check": ten.CHECK_CUOI})


def main(argv=None):
    p = argparse.ArgumentParser(description="Bật cổng cho một repo.")
    p.add_argument("--repo", required=True, help="chu/repo")
    p.add_argument("--app-id", required=True, type=int, help="ID số của GitHub App phát check")
    p.add_argument("--kho", action="store_true", help="chỉ in lệnh gọi, không gọi GitHub")
    a = p.parse_args(argv)
    if not re.fullmatch(r"[\w.-]+/[\w.-]+", a.repo):
        print("--repo phải có dạng chu/repo")
        return 2
    if a.app_id <= 0:  # -1 nghĩa là App nào cũng được: mất đúng thứ cổng cần.
        print("--app-id phải là ID thật của App, không nhận số <= 0")
        return 2
    if a.kho:
        print("CHẠY KHÔ, không gọi GitHub.")
        for buoc in ke_hoach(a.app_id):
            print("\n%s /repos/%s%s" % (buoc["phuong_thuc"], a.repo, buoc["duong"]))
            print(json.dumps(buoc["body"], ensure_ascii=False, indent=2))
        print("\nRồi đọc lại bằng GET và so từng thiết lập.")
        in_buoc_tay(a.repo)
        return 0
    token = os.environ.get("GH_TOKEN", "")
    if not token:
        print("thiếu GH_TOKEN của chủ repo")
        return 2
    try:
        sai = ap_dung(GitHub(a.repo, token), a.app_id)
    except LoiApi as loi:
        print("lỗi: %s" % loi)
        if loi.than:
            print(loi.than)
        if loi.ma in (403, 404):
            print("Có thể thiếu quyền chủ repo, `%s` chưa có mã, hoặc repo private gói Free "
                  "(gói đó KHÔNG có cổng chặn được)." % ten.NHANH_GOC)
        return 1
    if sai:
        print("CHƯA BẬT ĐỦ:\n- " + "\n- ".join(sai))
        return 1
    print("Đã đặt và đọc lại khớp. Việc này chưa chứng minh cổng chặn được: phải chạy bài L1-L6 trên repo thật.")
    in_buoc_tay(a.repo)
    return 0


if __name__ == "__main__":
    sys.exit(main())
