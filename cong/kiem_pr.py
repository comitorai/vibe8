"""Quyết định của cổng cuối. Hàm thuần, không đọc thân PR, nhãn hay tiêu đề.

Các khoá của du_lieu: sha_dau, trang_thai_pr, nhanh_dich, so_pr_vao_goc, tac_gia, nguoi_commit,
so_commit_khai, so_commit_doc, so_tep_khai, tep, vung_nhay_cam [mẫu, đọc từ nhánh gốc; None là repo chưa khai], lan_chay_nhanh [{head_sha, status, conclusion}],
nguoi_tin [login], nguoi_ghi [login có quyền ghi], duyet [{user, user_type, state, commit_id, submitted_at, body}].
"""
import re

from . import rui_ro, ten, the_duyet

CHO_QUA, CHAN, CHO = "cho_qua", "chan", "cho"

SHA_HOP_LE = re.compile(r"[0-9a-f]{40}")
_TRANG_THAI_XET = {"APPROVED", "CHANGES_REQUESTED", "DISMISSED"}
_NGOAI_LE = re.compile(r"^ngoai-le-co:[ \t]*(\S.{8,}\S)[ \t\r]*$", re.M)
# Phiếu phản bác (luật L3): một lượt review, thân có hai dòng này. Tái hiện bắt buộc cả khi không bác: ghi đã thử gì.
_PHIEU = re.compile(r"^phieu-phan-bac:[ \t]*(bac|khong-bac)[ \t\r]*$", re.M)
_TAI_HIEN = re.compile(r"^tai-hien:[ \t]*(\S.{8,}\S)[ \t\r]*$", re.M)
_TRANG_THAI_PHIEU = {"COMMENTED", "APPROVED", "CHANGES_REQUESTED"}
TRAN_PHIEU_BAC = 2  # L4: quá hai vòng bác thì người quyết


def _doc_phieu(du_lieu):
    """Phiếu hợp lệ theo thứ tự thời gian: [(bac|khong-bac, review, dòng tái hiện)]. Chỉ người có quyền ghi được ghi phiếu:
    repo công khai thì ai cũng gửi được review. Máy không phân biệt được hai agent dùng chung tài khoản, nên tác giả cũng
    ghi phiếu được (giới hạn ghi ở luật)."""
    ghi = {str(x).casefold() for x in du_lieu.get("nguoi_ghi") or [] if x}
    ds = []
    for r in sorted(du_lieu.get("duyet") or [], key=lambda r: str(r.get("submitted_at") or "")):
        than = str(r.get("body") or "")
        m, tai_hien = _PHIEU.search(than), _TAI_HIEN.search(than)
        if not m or r.get("state") not in _TRANG_THAI_PHIEU:  # PENDING là nháp, DISMISSED đã bị gỡ
            continue
        login = str(r.get("user") or "").casefold()
        if login not in ghi or r.get("user_type") != "User" or login.endswith("[bot]") or not tai_hien:
            continue
        ds.append((m.group(1), r, tai_hien.group(1)))
    return ds


def _so_bac(du_lieu):
    """Số vòng bác: số SHA khác nhau có phiếu bác. Một người bác hai lần trên một SHA vẫn là một vòng (L4 đếm vòng)."""
    return len({str(r.get("commit_id") or "") for ket, r, _ in _doc_phieu(du_lieu) if ket == "bac"})


def _xet_phieu(du_lieu, sha):
    """Trả (lý do chặn hoặc None, chi tiết)."""
    ds = [(ket, r) for ket, r, _ in _doc_phieu(du_lieu)]
    so_bac = _so_bac(du_lieu)
    dung_sha = [(ket, r) for ket, r in ds if r.get("commit_id") == sha]
    if so_bac >= TRAN_PHIEU_BAC:
        return "đã bác trên %d SHA khác nhau (trần L4): cần người có quyền admin, khác tác giả, duyệt đúng SHA" % so_bac, []
    if not dung_sha:
        return ("cần phiếu phản bác trên đúng SHA (mọi mức), là một review có dòng `phieu-phan-bac: bac|khong-bac` "
                "và `tai-hien: <cách tái hiện hoặc đã thử gì>` (L3)"), []
    # Một phiếu bác trên SHA này thì phiếu không bác ghi sau không gỡ được: phải có commit mới (Alex 1a, 06/11).
    bac = [r for ket, r in dung_sha if ket == "bac"]
    if bac:
        nguoi = rui_ro.hien_thi(bac[-1].get("user"))
        return ("phiếu phản bác của %s trên SHA này bác, phiếu không bác ghi sau không gỡ được: "
                "sửa bằng commit mới rồi xin phiếu mới, lượt sau chỉ xét phần vừa sửa (L4)") % nguoi, []
    nguoi = rui_ro.hien_thi(dung_sha[-1][1].get("user"))
    return None, ["phiếu phản bác không bác của %s" % nguoi]


def _xet_nhanh(lan_chay, sha):
    """Trả (xanh | do | cho, lý do). Mọi lượt của đúng SHA phải xanh: lượt xanh không che được lượt đỏ."""
    dung_sha = [c for c in (lan_chay or []) if c.get("head_sha") == sha]
    if not dung_sha:
        return CHO, "chưa có lượt cong-nhanh tính được. CI chưa bắt đầu thì chờ; vài phút không thấy lượt thì đẩy commit mới. PR xung đột hoặc vừa mở lại: đẩy commit mới. PR từng đổi base, nhánh đầu từng có PR khác: đóng PR này, đẩy nhánh tên mới rồi mở PR mới"
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
    """Trả {ket_luan, ly_do, chi_tiet, sha, rui_ro, so_dong, so_mau_vung, nguoi_duyet, qua_co, theo_tep, the_duyet, tran_l4}."""
    sha = du_lieu.get("sha_dau")
    ds_tep = du_lieu.get("tep")
    vung = du_lieu.get("vung_nhay_cam")
    chua_khai = vung is None
    if chua_khai:
        vung = []
    elif not isinstance(vung, list):
        vung = ["*"]  # dữ liệu vùng hỏng: coi mọi tệp là nhạy cảm
    rr = rui_ro.phan_loai(ds_tep, vung)
    hop_le, bo, dang_chan = _xet_duyet(du_lieu, sha)
    chan = []
    if chua_khai:
        # Máy không đọc được mã nào chạm tiền hay bảo mật: repo phải khai, kể cả khai «không có» bằng tệp chỉ có chú thích.
        chan.append("repo chưa khai vùng nhạy cảm `%s` ở nhánh gốc: khai đường dẫn thanh toán, xác thực, khoá bí mật, "
                    "migration (không có thì để tệp chỉ có chú thích), PR khai cần admin duyệt" % ten.TEP_VUNG)
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
    # Mọi mức đều cần phiếu (Alex 1a, 06/11): thẻ duyệt Cao chỉ đưa diff tệp Cao, phần Thường do phiếu soát.
    # Admin duyệt không thay phiếu; chỉ khi chạm trần L4 (đủ phiếu bác) thì admin là người quyết.
    ly_do_phieu, chi_tiet_phieu = _xet_phieu(du_lieu, sha)
    if ly_do_phieu and hop_le and _so_bac(du_lieu) >= TRAN_PHIEU_BAC:
        bo.append("đã chạm trần L4, người admin duyệt đúng SHA quyết thay phiếu")
    elif ly_do_phieu:
        chan.append(ly_do_phieu)
    else:
        bo += chi_tiet_phieu
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
    q = {
        "ket_luan": ket_luan, "ly_do": ly_do, "chi_tiet": rr["ly_do"] + bo, "sha": sha,
        "rui_ro": rr["muc"], "so_dong": rr["so_dong"], "so_mau_vung": len(vung),
        "nguoi_duyet": [rui_ro.hien_thi(r.get("user")) for r in hop_le],
        "qua_co": rr["qua_co"], "theo_tep": rr["theo_tep"], "the_duyet": None,
        "tran_l4": bool(ly_do_phieu) and _so_bac(du_lieu) >= TRAN_PHIEU_BAC,
    }
    # Thẻ chỉ dựng khi PR cần người admin: mức Cao, quá cỡ, hoặc chạm trần L4 (admin quyết thay phiếu, kể cả PR Thường).
    if rr["muc"] == rui_ro.CAO or rr["qua_co"] or q["tran_l4"]:
        q["the_duyet"] = the_duyet.lap_the(du_lieu, q, _doc_phieu(du_lieu), (nhanh, ly_do_nhanh))
    return q
