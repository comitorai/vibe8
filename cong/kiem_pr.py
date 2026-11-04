"""Quyết định của cổng cuối. Hàm thuần, không đọc thân PR, nhãn hay tiêu đề.

Các khoá của du_lieu: sha_dau, trang_thai_pr, tac_gia, nguoi_commit, so_tep_khai, tep,
check_nhanh [{head_sha, status, conclusion, app_slug}],
duyet [{user, user_type, association, state, commit_id, submitted_at, body}], push_cuoi.
"""
import re
from datetime import datetime

from . import rui_ro

CHO_QUA, CHAN, CHO = "cho_qua", "chan", "cho"

SHA_HOP_LE = re.compile(r"[0-9a-f]{40}")
_VAI_TIN = {"OWNER", "MEMBER", "COLLABORATOR"}
_TRANG_THAI_XET = {"APPROVED", "CHANGES_REQUESTED", "DISMISSED"}
_NGOAI_LE = re.compile(r"^ngoai-le-co:[ \t]*(\S.{9,})$", re.M)
APP_CHECK_NHANH = "github-actions"


def _gio(chuoi):
    try:
        gio = datetime.fromisoformat(str(chuoi).replace("Z", "+00:00"))
    except ValueError:
        return None
    return gio if gio.tzinfo else None


def _xet_nhanh(checks, sha):
    """Trả (xanh | do | cho, lý do). Chỉ `success` là xanh: neutral, skipped không tính."""
    dung_sha = [c for c in (checks or []) if c.get("head_sha") == sha]
    if not dung_sha:
        return CHO, "chưa có cong-nhanh của đúng SHA"
    if any(c.get("app_slug") != APP_CHECK_NHANH for c in dung_sha):
        return "do", "cong-nhanh do nguồn lạ phát"
    if any(c.get("status") != "completed" for c in dung_sha):
        return CHO, "cong-nhanh chưa chạy xong"
    if all(c.get("conclusion") == "success" for c in dung_sha):
        return "xanh", ""
    return "do", "cong-nhanh không xanh"


def _vi_sao_bo(r, sha, tac_gia, push_cuoi):
    login = str(r.get("user") or "").casefold()
    if not tac_gia:
        return "không rõ tác giả"
    if login in tac_gia:
        return "tự duyệt"
    if r.get("user_type") != "User" or login.endswith("[bot]"):
        return "không phải người"
    if r.get("association") not in _VAI_TIN:
        return "không có quyền trong repo"
    if r.get("commit_id") != sha:
        return "duyệt SHA khác"
    gio_duyet, gio_push = _gio(r.get("submitted_at")), _gio(push_cuoi)
    if gio_duyet is None or gio_push is None or gio_duyet <= gio_push:
        return "không chứng minh được duyệt sau lần push cuối"
    return None


def _xet_duyet(du_lieu, sha):
    """Trả (lần duyệt hợp lệ, lý do đã bỏ, người đang yêu cầu sửa đúng SHA)."""
    goc = [du_lieu.get("tac_gia")] + list(du_lieu.get("nguoi_commit") or [])
    tac_gia = {str(x).casefold() for x in goc if x} if du_lieu.get("tac_gia") else set()
    moi_nhat = {}
    ds = sorted(du_lieu.get("duyet") or [], key=lambda r: str(r.get("submitted_at") or ""))
    for r in ds:
        if r.get("state") in _TRANG_THAI_XET:
            moi_nhat[str(r.get("user") or "").casefold()] = r
    hop_le, bo, yeu_cau_sua = [], [], []
    for r in moi_nhat.values():
        ten_nguoi = rui_ro.hien_thi(r.get("user"))
        if r["state"] == "CHANGES_REQUESTED":
            if r.get("commit_id") == sha and r.get("association") in _VAI_TIN:
                yeu_cau_sua.append(ten_nguoi)
        elif r["state"] == "APPROVED":
            vi_sao = _vi_sao_bo(r, sha, tac_gia, du_lieu.get("push_cuoi"))
            if vi_sao:
                bo.append("bỏ duyệt của %s: %s" % (ten_nguoi, vi_sao))
            else:
                hop_le.append(r)
    return hop_le, bo, yeu_cau_sua


def quyet_dinh(du_lieu):
    """Trả {ket_luan, ly_do, chi_tiet, sha, rui_ro, so_dong, nguoi_duyet}."""
    sha = du_lieu.get("sha_dau")
    ds_tep = du_lieu.get("tep")
    rr = rui_ro.phan_loai(ds_tep)
    hop_le, bo, yeu_cau_sua = _xet_duyet(du_lieu, sha)
    chan = []
    if not (isinstance(sha, str) and SHA_HOP_LE.fullmatch(sha)):
        chan.append("head SHA không hợp lệ")
    if du_lieu.get("trang_thai_pr") != "open":
        chan.append("PR không ở trạng thái mở")
    if not isinstance(ds_tep, list) or du_lieu.get("so_tep_khai") != len(ds_tep):
        chan.append("danh sách tệp không đủ so với PR")
    if yeu_cau_sua:
        chan.append("đang có yêu cầu sửa trên đúng SHA: " + ", ".join(yeu_cau_sua))
    if rr["muc"] == rui_ro.CAO and not hop_le:
        chan.append("rủi ro cao: cần người khác tác giả duyệt đúng SHA, sau lần push cuối")
    if rr["qua_co"]:
        ly_do_le = [m.group(1) for m in (_NGOAI_LE.search(str(r.get("body") or "")) for r in hop_le) if m]
        if not ly_do_le:
            chan.append("quá %d dòng (%d): cần người duyệt ghi `ngoai-le-co: <lý do>`"
                        % (rui_ro.NGUONG_CO_DONG, rr["so_dong"]))
    nhanh, ly_do_nhanh = _xet_nhanh(du_lieu.get("check_nhanh"), sha)
    if nhanh == "do":
        chan.append(ly_do_nhanh)
    if chan:
        ket_luan, ly_do = CHAN, chan
    elif nhanh == CHO:
        ket_luan, ly_do = CHO, [ly_do_nhanh]
    else:
        ket_luan, ly_do = CHO_QUA, ["cong-nhanh xanh trên đúng SHA, không vướng điều kiện nào"]
    return {
        "ket_luan": ket_luan, "ly_do": ly_do, "chi_tiet": rr["ly_do"] + bo, "sha": sha,
        "rui_ro": rr["muc"], "so_dong": rr["so_dong"],
        "nguoi_duyet": [rui_ro.hien_thi(r.get("user")) for r in hop_le],
    }
