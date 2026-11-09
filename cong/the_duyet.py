"""Thẻ duyệt: thứ người admin đọc trước khi duyệt PR cần họ (mức Cao, quá cỡ, hoặc chạm trần L4). Hàm thuần.

Đề xuất điểm duyệt §2 (Alex, 06/11): mỗi lượt duyệt Cao dưới 5 phút. Thẻ gồm vì sao cần duyệt, các phiếu phản bác,
trạng thái test, rồi CHỈ diff của tệp làm PR thành Cao. Tệp Thường chỉ có tên và số dòng, kèm câu nói rõ ai đã soát
phần đó (phiếu phản bác đúng SHA) hay chưa ai soát.
Mọi chữ từ PR (tên tệp, diff, thân phiếu) do người mở PR viết: đưa vào khối mã có rào dài hơn mọi chuỗi ` bên trong,
ký tự điều khiển và ký tự ẩn (bidi, zero-width) hiện thành \\uXXXX để người duyệt thấy thứ máy thấy.
Diff đặt cuối thẻ, mỗi tệp Cao có trần riêng: một tệp dài không đẩy được tệp Cao khác, phiếu hay test ra khỏi thẻ.
"""
import hashlib
import re
import unicodedata

from . import rui_ro

GIOI_HAN = 60000          # byte UTF-8; output.text của check run tối đa 65535
DONG_MOI_TEP = 200        # diff dài hơn thì cắt, ghi rõ đã cắt
KY_TU_MOI_DONG = 400      # dòng dài hơn thì cắt, ghi rõ đã cắt
TRAN_PHIEU = 10           # phiếu không bác hiện tối đa (mỗi người phiếu mới nhất)
TRAN_PHIEU_BAC_HIEN = 20  # phiếu bác hiện tối đa, mới nhất; còn lại báo số
TRAN_BYTE_TEN = 160       # mỗi tên tệp trong thẻ
TRAN_BYTE_TAI_HIEN = 400  # mỗi dòng tái hiện của phiếu
TRAN_TEN = 50


def _byte(chu):
    return len(chu.encode("utf-8"))


def _cat_byte(chu, so_byte):
    return chu.encode("utf-8")[:max(0, so_byte)].decode("utf-8", "ignore")


def _hien_ky_tu(dong):
    return "".join(c if c == "\t" or (c.isprintable() and unicodedata.category(c) != "Cf") else "\\u%04x" % ord(c)
                   for c in dong)


def _khoi_ma(dong, ngon_ngu="diff"):
    """Rào dài hơn chuỗi ` dài nhất bên trong: nội dung không thoát ra ngoài khối mã được."""
    than = "\n".join(dong)
    dai = max([3] + [len(m) + 1 for m in re.findall(r"`+", than)])
    return "%s%s\n%s\n%s" % ("`" * dai, ngon_ngu, than, "`" * dai)


def _rao_dang_mo(chu):
    """Độ dài rào ` của khối mã còn mở ở cuối chu, 0 nếu không có. Rào mở có hay không có tên ngôn ngữ đều tính."""
    mo = 0
    for dong in chu.split("\n"):
        m = re.fullmatch(r" {0,3}(`{3,})([^`]*)", dong)
        if not m:
            continue
        if not mo:
            mo = len(m.group(1))
        elif not m.group(2).strip() and len(m.group(1)) >= mo:
            mo = 0
    return mo


def _diff_tep(tep, ngan_sach):
    """Diff một tệp, không quá ngan_sach byte. Cắt theo dòng, theo độ dài dòng, theo ngân sách: chỗ nào cắt cũng ghi."""
    patch = tep.get("patch") if isinstance(tep, dict) else None
    if not isinstance(patch, str) or not patch:
        return "_GitHub không gửi diff dạng chữ cho tệp này (nhị phân hoặc quá lớn): mở tab Files của PR._"
    goc = patch.split("\n")
    dong, cat_dai = [], 0
    for d in goc[:DONG_MOI_TEP]:
        d = _hien_ky_tu(d)
        if len(d) > KY_TU_MOI_DONG:
            cat_dai += 1
            d = d[:KY_TU_MOI_DONG] + " …[cắt %d ký tự]" % (len(d) - KY_TU_MOI_DONG)
        dong.append(d)
    ghi = []
    if cat_dai:
        ghi.append("%d dòng quá %d ký tự bị cắt đuôi" % (cat_dai, KY_TU_MOI_DONG))
    giu = len(dong)
    while giu and _byte(_khoi_ma(dong[:giu])) > ngan_sach - 300:
        giu = giu * 3 // 4 if giu > 8 else giu - 1
    bo = len(goc) - giu
    if bo > 0:
        ghi.append("đã cắt %d dòng cuối" % bo)
    if not giu:
        return "_Diff quá dài để đưa vào thẻ: mở tab Files của PR. Không được duyệt khi chưa đọc tệp này._"
    return _khoi_ma(dong[:giu]) + ("\n_%s: xem đủ ở tab Files._" % "; ".join(ghi).capitalize() if ghi else "")


def _so(tep):
    them, xoa = (tep.get("additions"), tep.get("deletions")) if isinstance(tep, dict) else (None, None)
    return "+%s −%s" % (them if type(them) is int else "?", xoa if type(xoa) is int else "?")


def _gon(gia_tri, tran_byte):
    """hien_thi nhưng giữ dưới tran_byte: rút đầu và đuôi chuỗi gốc, ký tự ẩn hiện thành \\uXXXX nên tính sau khi làm sạch."""
    goc = str(gia_tri)
    chu, n = rui_ro.hien_thi(goc), len(goc)
    while _byte(chu) > tran_byte and n > 8:
        n = n * 3 // 4
        dau = n * 2 // 5
        chu = rui_ro.hien_thi(goc[:dau] + "…" + goc[len(goc) - (n - dau):])
    return chu


def _ten(tep, so):
    """Tên tệp trong thẻ, mở đầu bằng số thứ tự trong danh sách tệp của PR. Số thứ tự là thứ làm hai dòng khác nhau:
    dấu băm 8 hex của tên bị cắt vẫn dò trùng được, số thứ tự thì không (để PR sau từ phản bác lượt 4, 06/11)."""
    # Cắt tên chứ không bỏ tệp: tệp nào cũng phải còn tên trong thẻ (phản bác lượt 3, 06/11).
    goc = tep.get("filename") if isinstance(tep, dict) else "?"
    ten = _gon(goc, TRAN_BYTE_TEN)
    if ten != rui_ro.hien_thi(goc):  # đã cắt: dấu băm giúp tìm tệp ở tab Files
        ten += " #" + hashlib.sha256(str(goc).encode("utf-8", "surrogatepass")).hexdigest()[:8]
    return "[%d] %s" % (so, ten)


def _trong_tran(dong, tran_byte):
    """Các dòng đầu vừa trần byte, và số dòng bị bỏ."""
    giu, dung = [], 0
    for d in dong:
        if dung + _byte(d) + 2 > tran_byte:
            break
        giu.append(d)
        dung += _byte(d) + 2
    return giu, len(dong) - len(giu)


def _phieu(du_lieu, phieu, sha):
    """Phiếu bác: TRAN_PHIEU_BAC_HIEN phiếu mới nhất. Phiếu không bác: mỗi người chỉ phiếu mới nhất, tối đa TRAN_PHIEU. Phiếu của tác giả
    hoặc người có commit trong PR được gắn nhãn: không phải phản bác độc lập."""
    tac_gia = {str(x).casefold() for x in [du_lieu.get("tac_gia")] + list(du_lieu.get("nguoi_commit") or []) if x}
    bac = sorted((p for p in phieu if p[0] == "bac"), key=lambda p: str(p[1].get("submitted_at") or ""))
    bo_bac = max(0, len(bac) - TRAN_PHIEU_BAC_HIEN)
    bac = bac[bo_bac:]
    moi_nhat = {}
    for p in phieu:
        if p[0] != "bac":
            moi_nhat[str(p[1].get("user") or "").casefold()] = p
    khong_bac = sorted(moi_nhat.values(), key=lambda p: str(p[1].get("submitted_at") or ""))
    bo = max(0, len(khong_bac) - TRAN_PHIEU)
    dong = []
    for ket, r, tai_hien in sorted(bac + khong_bac[bo:], key=lambda p: str(p[1].get("submitted_at") or "")):
        dung = "đúng SHA" if r.get("commit_id") == sha else "SHA cũ `%s`" % rui_ro.hien_thi(r.get("commit_id"))[1:8]
        nhan = " (**tác giả PR, không độc lập**)" if str(r.get("user") or "").casefold() in tac_gia else ""
        dong.append("- **%s** của %s%s, %s. Tái hiện: %s" % (ket, _gon(r.get("user"), 80), nhan, dung,
                                                            _gon(tai_hien, TRAN_BYTE_TAI_HIEN)))
    if bo or bo_bac:
        dong.append("_Còn %d phiếu bác và %d phiếu không bác cũ hơn ở tab Conversation._" % (bo_bac, bo))
    return dong


def lap_the(du_lieu, q, phieu, nhanh):
    """du_lieu: đầu vào quyet_dinh. q: kết quả quyet_dinh (cần rui_ro, so_dong, qua_co, theo_tep, nguoi_duyet).
    phieu: [(bac|khong-bac, review, tai_hien)] đã lọc người có quyền ghi. nhanh: (xanh|do|cho, lý do)."""
    sha = str(du_lieu.get("sha_dau") or "")
    ds_tep = du_lieu.get("tep") if isinstance(du_lieu.get("tep"), list) else []
    theo_tep = list(q.get("theo_tep") or [])
    if q.get("tran_l4"):
        # Trần L4: duyệt là merge cả phần Thường mà không phiếu nào soát, nên thẻ đưa diff mọi tệp.
        theo_tep = [ly or ["mức Thường, chưa có phiếu không bác: anh duyệt là merge tệp này không ai soát"]
                    for ly in theo_tep + [[]] * (len(ds_tep) - len(theo_tep))]
    # Số thứ tự đi kèm tệp từ đầu, không tra lại theo id(): cùng một đối tượng xuất hiện hai lần vẫn mang hai số.
    cao = [(i, t, ly) for i, (t, ly) in enumerate(zip(ds_tep, theo_tep), 1) if ly]
    thuong = [(i, t) for i, (t, ly) in enumerate(zip(ds_tep, theo_tep), 1) if not ly]
    phan = ["## Thẻ duyệt", "SHA `%s` · %d tệp · %d dòng. Duyệt là duyệt đúng SHA này; có commit mới thì duyệt lại."
            % (sha[:12], len(ds_tep), q.get("so_dong", 0))]
    if q.get("so_dong_test"):
        phan[-1] += (" (gồm %d dòng test, mức Cao tính đủ)" if q.get("rui_ro") == rui_ro.CAO
                     else " (chưa tính %d dòng test)") % q["so_dong_test"]

    phan.append("### 1. Vì sao cần anh duyệt")
    vi_sao = []
    if q.get("rui_ro") == rui_ro.CAO:
        vi_sao.append("mức Cao: %d tệp chạm cổng, bảo mật, tiền, test có sẵn hoặc phụ thuộc" % len(cao))
        if not ds_tep:
            vi_sao.append("cổng không đọc được danh sách tệp")
    if q.get("tran_l4"):
        vi_sao.append("**chạm trần L4**: đã bác trên đủ số SHA, không còn phiếu không bác; anh duyệt là anh quyết thay phiếu "
                      "cho **mọi tệp**, nên diff mọi tệp ở mục 4. "
                      "Lượt duyệt phải ghi sau phiếu bác cuối và có dòng `quyet-l4: <lý do>`")
    if q.get("qua_co") and q.get("rui_ro") == rui_ro.CAO:
        vi_sao.append("quá %d dòng: lượt duyệt phải có dòng `ngoai-le-co: <lý do>`" % rui_ro.NGUONG_CO_DONG)
    phan += ["- " + x for x in vi_sao]
    if cao:
        # Danh sách nào do người mở PR làm dài cũng có trần byte, để phiếu, test và diff còn chỗ.
        ds_dong, con = _trong_tran(["- %s %s: %s" % (_ten(t, i), _so(t), "; ".join(ly)) for i, t, ly in cao[:TRAN_TEN]],
                                   GIOI_HAN // 6)
        con += max(0, len(cao) - TRAN_TEN)
        phan.append("Tệp cần anh đọc (diff ở mục 4):\n" + "\n".join(ds_dong)
                    + ("\n- và %d tệp nữa: tên ở mục 4 hoặc tab Files" % con if con else ""))
    if thuong:
        dung_sha = [p for p in phieu if p[1].get("commit_id") == sha]
        if dung_sha and all(p[0] == "khong-bac" for p in dung_sha):
            ai_soat = "đã có phiếu không bác trên đúng SHA (mục 2)"
        else:
            ai_soat = "**chưa có phiếu không bác trên đúng SHA: phần này chưa ai soát, cổng còn chặn**"
        ten_thuong, con = _trong_tran(["%s %s" % (_ten(t, i), _so(t)) for i, t in thuong[:TRAN_TEN]], GIOI_HAN // 10)
        con += max(0, len(thuong) - TRAN_TEN)
        phan.append("Tệp mức Thường, thẻ không đưa diff, %s: " % ai_soat + ", ".join(ten_thuong)
                    + (" và %d tệp nữa" % con if con else ""))

    phan.append("### 2. Phản bác đã thử")
    # Bỏ từ phía cũ: phiếu mới nhất (thường là phiếu trên đúng SHA) phải còn trong thẻ (phản bác lượt 4).
    dong_phieu, con = _trong_tran(_phieu(du_lieu, phieu, sha)[::-1], GIOI_HAN // 6)
    dong_phieu.reverse()
    if con:
        dong_phieu.append("_Còn %d dòng phiếu không đưa vào thẻ: xem tab Conversation._" % con)
    phan += dong_phieu or ["_Chưa có phiếu phản bác nào: cổng chặn tới khi có phiếu `khong-bac` trên đúng SHA._"]

    phan.append("### 3. Test")
    trang_thai, ly_do = nhanh
    phan.append("- `cong-nhanh` trên đúng SHA: " + {"xanh": "xanh", "do": "**đỏ**"}.get(trang_thai, "đang chờ") +
                ("" if trang_thai == "xanh" else " (%s)" % ly_do))
    moi = [(i, t) for i, t in enumerate(ds_tep, 1) if isinstance(t, dict) and t.get("status") == "added"
           and rui_ro._la_test(rui_ro._chuan_hoa(str(t.get("filename") or "")), str(t.get("filename") or ""))]
    phan.append("- Tệp test mới: %s" % (", ".join("%s %s" % (_ten(t, i), _so(t)) for i, t in moi[:20]) + (" và %d tệp nữa" % (len(moi) - 20) if len(moi) > 20 else "")
                                  if moi else "không có"))
    phan.append("- Đỏ trước, xanh sau: cổng chưa đo (cần chạy test mới trên nhánh gốc).")
    if q.get("nguoi_duyet"):
        phan.append("_Đã có lượt duyệt hợp lệ của %s._" % ", ".join(q["nguoi_duyet"]))

    phan.append("### 4. Diff của tệp cần anh đọc (%d/%d tệp)" % (len(cao), len(ds_tep)))
    if not cao:
        phan.append("_Không tệp nào ở mức Cao._")
    dau = "\n\n".join(phan)
    hien, dong_ten = [], []
    for i, t, _ in cao[:TRAN_TEN]:  # dòng tên của mục 4 cũng có trần byte, để còn chỗ cho diff
        d = "\n\n**%s** %s\n\n" % (_ten(t, i), _so(t))
        if sum(map(_byte, dong_ten)) + _byte(d) > GIOI_HAN // 4:
            break
        hien.append(t)
        dong_ten.append(d)
    # Chia dần: tệp ngắn dùng ít thì phần dư sang tệp sau.
    con_lai = GIOI_HAN - _byte(dau) - 1500 - sum(map(_byte, dong_ten))
    for i, (t, ten_tep) in enumerate(zip(hien, dong_ten)):
        khoi = _diff_tep(t, con_lai // (len(hien) - i))
        con_lai -= _byte(khoi)
        dau += ten_tep + khoi
    if len(cao) > len(hien):
        dau += "\n\n_Còn %d tệp không đưa diff vào thẻ: đọc ở tab Files trước khi duyệt._" % (len(cao) - len(hien))
    if _byte(dau) > GIOI_HAN:  # phòng hờ: ngân sách từng tệp đã giữ dưới trần
        dau = _cat_byte(dau, GIOI_HAN - 300)
        mo = _rao_dang_mo(dau)
        dau += ("\n" + "`" * mo if mo else "") + "\n\n_Thẻ quá dài, đã cắt: đọc tab Files trước khi duyệt._"
    return dau
