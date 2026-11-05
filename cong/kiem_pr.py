"""Quyết định của cổng cuối. Hàm thuần, không đọc thân PR, nhãn hay tiêu đề.

Các khoá của du_lieu: sha_dau, trang_thai_pr, nhanh_dich, so_pr_vao_goc, tac_gia, nguoi_commit,
so_commit_khai, so_commit_doc, so_tep_khai, tep, lan_chay_nhanh [{head_sha, status, conclusion}],
nguoi_tin [login], duyet [{user, user_type, state, commit_id, submitted_at, body}].
"""
import re

from . import rui_ro, ten

CHO_QUA, CHAN, CHO = "cho_qua", "chan", "cho"

SHA_HOP_LE = re.compile(r"[0-9a-f]{40}")
_TRANG_THAI_XET = {"APPROVED", "CHANGES_REQUESTED", "DISMISSED"}
_NGOAI_LE = re.compile(r"^ngoai-le-co:[ \t]*(\S.{8,}\S)[ \t\r]*$", re.M)


def _xet_nhanh(lan_chay, sha):
    """Trả (xanh | do | cho, lý do). Mọi lượt của đúng SHA phải xanh: lượt xanh không che được lượt đỏ."""
    dung_sha = [c for c in (lan_chay or []) if c.get("head_sha") == sha]
    if not dung_sha:
        return CHO, "chưa có lượt cong-nhanh tính được. CI chưa bắt đầu thì chờ. PR xung đột hoặc vừa mở lại: đẩy commit mới. PR từng đổi base, nhánh đầu từng có PR khác: đóng PR này, đẩy nhánh tên mới rồi mở PR mới"
    if any(c.get("status") != "completed" for c in dung_sha):
        return CHO, "cong-nhanh chưa chạy xong"
    if all(c.get("conclusion") == "success" for c in dung_sha):
        return "xanh", ""
    return "do", "có lượt cong-nhanh không xanh trên SHA này"


def _vi_sao_bo(r, sha, tac_gia):
    login = str(r.get("user") or "").casefold()
    if not tac_gia:
        return "không rõ tác giả"
    if login in tac_gia:
        return "tự duyệt"
    if r.get("user_type") != "User" or login.endswith("[bot]"):
        return "không phải người"
    if r.get("commit_id") != sha:
        return "duyệt SHA khác"
    return None


def _xet_duyet(du_lieu, sha):
    """Trả (lần duyệt hợp lệ, lý do đã bỏ, người đang chặn). Chỉ người trong nguoi_tin (có quyền admin) mới có tiếng nói."""
    goc = [du_lieu.get("tac_gia")] + list(du_lieu.get("nguoi_commit") or [])
    tac_gia = {str(x).casefold() for x in goc if x} if du_lieu.get("tac_gia") else set()
    tin = {str(x).casefold() for x in du_lieu.get("nguoi_tin") or [] if x}
    moi_nhat = {}
    for r in sorted(du_lieu.get("duyet") or [], key=lambda r: str(r.get("submitted_at") or "")):
        if r.get("state") in _TRANG_THAI_XET:
            moi_nhat[str(r.get("user") or "").casefold()] = r
    hop_le, bo, dang_chan = [], [], []
    for login, r in moi_nhat.items():
        ten_nguoi = rui_ro.hien_thi(r.get("user"))
        if login not in tin:
            if r["state"] == "APPROVED":
                bo.append("bỏ duyệt của %s: không có quyền admin trên repo" % ten_nguoi)
        elif r["state"] != "APPROVED":
            # Lượt bị gỡ cũng chặn: người khác không được xoá yêu cầu sửa của người duyệt.
            dang_chan.append(ten_nguoi)
        else:
            vi_sao = _vi_sao_bo(r, sha, tac_gia)
            if vi_sao:
                bo.append("bỏ duyệt của %s: %s" % (ten_nguoi, vi_sao))
            else:
                hop_le.append(r)
    return hop_le, bo, dang_chan


def quyet_dinh(du_lieu):
    """Trả {ket_luan, ly_do, chi_tiet, sha, rui_ro, so_dong, nguoi_duyet}."""
    sha = du_lieu.get("sha_dau")
    ds_tep = du_lieu.get("tep")
    rr = rui_ro.phan_loai(ds_tep)
    hop_le, bo, dang_chan = _xet_duyet(du_lieu, sha)
    chan = []
    if not (isinstance(sha, str) and SHA_HOP_LE.fullmatch(sha)):
        chan.append("head SHA không hợp lệ")
    if du_lieu.get("trang_thai_pr") != "open":
        chan.append("PR không ở trạng thái mở")
    if du_lieu.get("nhanh_dich") != ten.NHANH_GOC:
        chan.append("PR không nhắm vào nhánh gốc")
    if du_lieu.get("so_pr_vao_goc") != 1:
        chan.append("phải có đúng một PR mở vào nhánh gốc ở SHA này")
    if not isinstance(ds_tep, list) or du_lieu.get("so_tep_khai") != len(ds_tep):
        chan.append("danh sách tệp không đủ so với PR")
    if du_lieu.get("so_commit_khai") != du_lieu.get("so_commit_doc"):
        chan.append("danh sách commit không đủ so với PR")
    if dang_chan:
        chan.append("người duyệt đang yêu cầu sửa hoặc lượt xét đã bị gỡ: " + ", ".join(dang_chan))
    if rr["muc"] == rui_ro.CAO and not hop_le:
        chan.append("rủi ro cao: cần người có quyền admin, khác tác giả, duyệt đúng SHA")
    if rr["qua_co"]:
        ly_do_le = [m.group(1) for m in (_NGOAI_LE.search(str(r.get("body") or "")) for r in hop_le) if m]
        if not ly_do_le:
            chan.append("quá %d dòng (%d): cần người duyệt ghi `ngoai-le-co: <lý do>`" % (rui_ro.NGUONG_CO_DONG, rr["so_dong"]))
        bo += ["ngoại lệ cỡ: " + rui_ro.hien_thi(x) for x in ly_do_le]
    nhanh, ly_do_nhanh = _xet_nhanh(du_lieu.get("lan_chay_nhanh"), sha)
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
