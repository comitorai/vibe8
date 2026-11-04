"""Phân rủi ro CHỈ từ diff. Hàm thuần: không nhận thân PR, nhãn hay tiêu đề.

Đầu vào: danh sách tệp đúng dạng GET /pulls/N/files
(filename, previous_filename, status, additions, deletions, patch).
Thiếu dữ liệu thì nghiêng về rủi ro cao hơn, không bao giờ thấp hơn.
"""
import re
import unicodedata

from . import ten

THAP, TRUNG_BINH, CAO = "thap", "trung_binh", "cao"
NGUONG_CO_DONG = 400

_THU_TU = {THAP: 0, TRUNG_BINH: 1, CAO: 2}
_GOC_BAO_VE = ("cong/", "luat/")
_TEP_BAO_VE = {
    ten.TEP_CAU_HINH, "codeowners", "makefile", "justfile", "noxfile.py", "tox.ini",
    "pytest.ini", "conftest.py", ".gitattributes", ".gitmodules",
}
_MAU_SCRIPT_CHECK = re.compile(r"^(check|kiem-tra)(\.[a-z0-9]+)?$|^(vitest|jest|playwright|karma)\.config\.")
_LOCKFILE = {
    "package-lock.json", "npm-shrinkwrap.json", "pnpm-lock.yaml", "yarn.lock", "bun.lock",
    "bun.lockb", "poetry.lock", "uv.lock", "pipfile.lock", "cargo.lock", "go.sum",
    "gemfile.lock", "composer.lock",
}
_MANIFEST = re.compile(r"^(package\.json|pyproject\.toml|go\.mod|requirements[^/]*\.txt)$")
_KHOA_SCRIPT = re.compile(r'"(scripts|(pre|post)?(check|test|lint|typecheck|build)[^"]*)"\s*:')
_THU_MUC_TEST = {"test", "tests", "__tests__", "spec", "specs", "e2e"}
_TEN_TEST = re.compile(r"^test_.*\.py$|_test\.(py|go|rb)$|\.(test|spec)\.[cm]?[jt]sx?$")
_KHANG_DINH = re.compile(r"\bassert\w*\b|\bexpect\(|\bdef test\w*|\b(it|test)\(")
_BO_QUA_TEST = re.compile(r"unittest\.skip|skipTest|mark\.(skip|xfail)|\.(skip|only)\(|\b(xit|xdescribe|xtest)\(")


def hien_thi(duong):
    """Tên tệp do người mở PR đặt: làm sạch trước khi đưa vào log hay check run."""
    chu = [c if c.isprintable() and unicodedata.category(c) != "Cf" else "\\u%04x" % ord(c) for c in str(duong)[:200]]
    return "`" + "".join(chu).replace("`", "'") + "`"


def _chuan_hoa(duong):
    return unicodedata.normalize("NFKC", duong).casefold()


def _la_ten_la(duong):
    if not isinstance(duong, str) or not duong or duong.startswith("/") or "\\" in duong:
        return True
    if any(unicodedata.category(c) in ("Cc", "Cf", "Cs", "Co", "Zl", "Zp") for c in duong):
        return True
    return any(doan in ("", ".", "..") for doan in duong.split("/"))


def _la_bao_ve(duong):
    """Duong đã chuẩn hoá: đổi được tệp này là đổi được chính cổng."""
    doan = duong.split("/")
    if ".github" in doan or duong.startswith(_GOC_BAO_VE):
        return True
    return doan[-1] in _TEP_BAO_VE or bool(_MAU_SCRIPT_CHECK.search(doan[-1]))


def _la_test(duong):
    doan = duong.split("/")
    return bool(_THU_MUC_TEST.intersection(doan[:-1])) or bool(_TEN_TEST.search(doan[-1]))


def _so_dong(tep):
    them, xoa = tep.get("additions"), tep.get("deletions")
    return (them, xoa) if all(type(so) is int and so >= 0 for so in (them, xoa)) else None


def _dong_doi(patch):
    them, xoa = [], []
    for dong in patch.splitlines():
        if dong.startswith("+"):
            them.append(dong[1:])
        elif dong.startswith("-"):
            xoa.append(dong[1:])
    return them, xoa


def _xet_test(tep, moi, cu, them, xoa):
    ky_hieu = hien_thi(tep["filename"])
    if tep.get("status") == "removed":
        return [(CAO, "xoá test " + ky_hieu)]
    if cu is not None and _la_test(cu) and not _la_test(moi):
        return [(CAO, "đổi tên test ra ngoài vùng test " + ky_hieu)]
    if them + xoa == 0:
        return []
    patch = tep.get("patch")
    if not isinstance(patch, str):
        return [(CAO, "không đọc được diff của test " + ky_hieu)]
    ket = []
    dong_them, dong_xoa = _dong_doi(patch)
    if xoa > them:
        ket.append((CAO, "giảm dòng test (-%d/+%d) %s" % (xoa, them, ky_hieu)))
    mat = sum(len(_KHANG_DINH.findall(d)) for d in dong_xoa)
    if mat > sum(len(_KHANG_DINH.findall(d)) for d in dong_them):
        ket.append((CAO, "giảm số khẳng định trong test " + ky_hieu))
    if any(_BO_QUA_TEST.search(d) for d in dong_them):
        ket.append((CAO, "thêm bỏ qua test " + ky_hieu))
    return ket


def _xet_manifest(tep, ten_tep, them, xoa):
    ky_hieu = hien_thi(tep["filename"])
    ket = [(TRUNG_BINH, "đổi tệp khai phụ thuộc " + ky_hieu)]
    if ten_tep == "package.json" and them + xoa > 0:
        patch = tep.get("patch")
        if not isinstance(patch, str):
            ket.append((CAO, "không đọc được diff của " + ky_hieu))
        elif any(_KHOA_SCRIPT.search(d) for phan in _dong_doi(patch) for d in phan):
            ket.append((CAO, "đổi script check trong " + ky_hieu))
    return ket


def _xet_tep(tep):
    if not isinstance(tep, dict):
        return [(CAO, "dữ liệu tệp không hợp lệ")]
    ten_moi, ten_cu = tep.get("filename"), tep.get("previous_filename")
    cac_ten = [ten_moi] + ([] if ten_cu is None else [ten_cu])
    if any(_la_ten_la(d) for d in cac_ten):
        return [(CAO, "tên tệp lạ " + ", ".join(hien_thi(d) for d in cac_ten))]
    moi = _chuan_hoa(ten_moi)
    cu = None if ten_cu is None else _chuan_hoa(ten_cu)
    ket = []
    for duong, goc in ((moi, ten_moi), (cu, ten_cu)):
        if duong is not None and _la_bao_ve(duong):
            ket.append((CAO, "đổi tệp của cổng " + hien_thi(goc)))
    so = _so_dong(tep)
    if so is None:
        return ket + [(CAO, "số dòng không hợp lệ " + hien_thi(ten_moi))]
    them, xoa = so
    if _la_test(moi) or (cu is not None and _la_test(cu)):
        ket += _xet_test(tep, moi, cu, them, xoa)
    ten_tep = moi.split("/")[-1]
    if ten_tep in _LOCKFILE:
        ket.append((TRUNG_BINH, "đổi lockfile " + hien_thi(ten_moi)))
    if _MANIFEST.search(ten_tep):
        ket += _xet_manifest(tep, ten_tep, them, xoa)
    trang_thai = tep.get("status")
    if trang_thai not in ("added", "modified", "removed", "renamed"):
        ket.append((TRUNG_BINH, "loại thay đổi khác thường " + hien_thi(ten_moi)))
    elif trang_thai in ("added", "modified") and not (them + xoa and tep.get("patch")):
        ket.append((TRUNG_BINH, "không có diff dạng chữ " + hien_thi(ten_moi)))
    return ket


def phan_loai(ds_tep):
    """Trả {muc, ly_do, so_dong, qua_co}."""
    if not isinstance(ds_tep, list):
        return {"muc": CAO, "ly_do": ["không có danh sách tệp"], "so_dong": 0, "qua_co": False}
    muc, ly_do, tong = THAP, [], 0
    for tep in ds_tep:
        for muc_tep, vi_sao in _xet_tep(tep):
            ly_do.append(vi_sao)
            if _THU_TU[muc_tep] > _THU_TU[muc]:
                muc = muc_tep
        so = _so_dong(tep) if isinstance(tep, dict) else None
        tong += sum(so) if so else 0
    return {"muc": muc, "ly_do": ly_do, "so_dong": tong, "qua_co": tong > NGUONG_CO_DONG}
