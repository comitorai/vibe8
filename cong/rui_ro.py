"""Phân rủi ro CHỈ từ diff. Hàm thuần: không nhận thân PR, nhãn hay tiêu đề.

Đầu vào: danh sách tệp đúng dạng GET /pulls/N/files
(filename, previous_filename, status, additions, deletions, patch).
Thiếu dữ liệu thì nghiêng về rủi ro cao hơn, không bao giờ thấp hơn.
"""
import pkgutil
import re
import sys
import sysconfig
import unicodedata

from . import ten

THAP, TRUNG_BINH, CAO = "thap", "trung_binh", "cao"
NGUONG_CO_DONG = 400

_THU_TU = {THAP: 0, TRUNG_BINH: 1, CAO: 2}
_GOC_BAO_VE = ("cong/", "luat/", "docs/bao-mat.md", "nghiem-thu/kiem_cuc_bo.py", "nghiem-thu/bat_cong.py", "nghiem-thu/loi/")
_TEP_BAO_VE = {ten.TEP_CAU_HINH, "codeowners", "makefile", "justfile", "noxfile.py", "tox.ini", "pytest.ini", "conftest.py",
               ".gitattributes", ".gitmodules", "sitecustomize.py", "usercustomize.py"}
# Mã máy chạy được mà diff không đọc được: Python nạp `.pyc` hash-based thay cho `.py` mà không so với mã nguồn.
_MA_MAY = (".pyc", ".pyo", ".pyd", ".so", ".dylib", ".dll", ".node", ".wasm", ".jar", ".class")
_KHONG_CHAY = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".woff", ".woff2", ".ttf")  # Tệp không chữ nhưng không tự chạy.
# Tệp trùng tên mô-đun chuẩn che được thư viện chuẩn khi chạy test. Python 3.9 không có danh sách: quét thư mục thư viện chuẩn.
_MO_DUN_CHUAN = {"pytest", "_pytest"}.union(sys.builtin_module_names, getattr(sys, "stdlib_module_names", ()), (m.name for m in pkgutil.iter_modules(
    [sysconfig.get_path("stdlib"), sysconfig.get_path("stdlib") + "/lib-dynload"])))
_MAU_SCRIPT_CHECK = re.compile(r"^(check|kiem-tra)(\.[a-z0-9]+)?$|^(vitest|jest|playwright|karma)\.config\.")
_LOCKFILE = {"package-lock.json", "npm-shrinkwrap.json", "pnpm-lock.yaml", "yarn.lock", "bun.lock", "bun.lockb", "poetry.lock", "uv.lock",
             "pipfile.lock", "cargo.lock", "go.sum", "gemfile.lock", "composer.lock", "pdm.lock"}
_MANIFEST = re.compile(r"(^|/)(package\.json|pyproject\.toml|go\.mod|requirements[^/]*\.(txt|in)|requirements/[^/]*\.(txt|in)"
                       r"|constraints[^/]*\.txt|setup\.py|setup\.cfg|cargo\.toml|gemfile|composer\.json|pipfile|\.npmrc"
                       r"|pnpm-workspace\.yaml|dockerfile[^/]*|\.python-version|\.tool-versions|\.pre-commit-config\.yaml"
                       r"|\.nvmrc|\.node-version|\.yarnrc\.yml|pom\.xml|(build|settings)\.gradle(\.kts)?)$")
# Dữ liệu kỳ vọng (golden, snapshot, fixture) cũng là điều kiện nghiệm thu: đổi nó là đổi test.
_THU_MUC_TEST = {"test", "tests", "testing", "__tests__", "spec", "specs", "e2e", "cypress", "integration_tests",
                 "testdata", "__snapshots__", "__fixtures__", "fixtures"}
_TEN_TEST = re.compile(r"(^|[._-])(tests?|spec)([._-][^/]*)?\.(py|go|rb|rs|java|kt|cs|php|swift|scala|dart|exs?|c|cc|cpp|sh|[cm]?[jt]sx?)$"
                       r"|^test[^/]*\.py$|\.(bats|snap)$")
_TEN_TEST_HOA = re.compile(r"[a-z0-9](Tests?|Spec)\.(java|kt|cs|rb|php|swift|scala|go|py|[cm]?[jt]sx?)$"  # FooTest.java, UserSpec.rb, TestFoo.java: xét trên tên gốc.
                           r"|(^|/)Tests?[A-Z][^/]*\.(java|kt|cs)$")


def hien_thi(duong):
    """Tên tệp do người mở PR đặt: làm sạch trước khi đưa vào log hay check run."""
    chu = [c if c.isprintable() and unicodedata.category(c) != "Cf" else "\\u%04x" % ord(c) for c in str(duong)[:200]]
    return "`" + "".join(chu).replace("`", "'") + "`"


def _chuan_hoa(duong):
    return unicodedata.normalize("NFKC", duong).casefold()


def _la_ten_la(duong):
    if not isinstance(duong, str) or not duong or duong.startswith("/") or "\\" in duong:
        return True
    return any(unicodedata.category(c) in ("Cc", "Cf", "Cs", "Co", "Zl", "Zp") for c in duong) or any(doan in ("", ".", "..") for doan in duong.split("/"))


def _la_bao_ve(duong):
    """Duong đã chuẩn hoá: đổi được tệp này là đổi được chính cổng."""
    doan = duong.split("/")
    if ".github" in doan or duong.startswith(_GOC_BAO_VE):
        return True
    return doan[-1] in _TEP_BAO_VE or bool(_MAU_SCRIPT_CHECK.search(doan[-1]))


def _che_thu_vien(duong, trang_thai):
    doan = duong.split("/")
    mo_dun = doan[-2] if doan[-1] == "__init__.py" and len(doan) > 1 else doan[-1].split(".")[0]
    # Tên không đuôi: symlink `json` trỏ tới thư mục khác cũng che được mô-đun, API chỉ cho thấy một dòng là đích của nó.
    return trang_thai not in ("modified", "removed") and (doan[-1].endswith(".py") or "." not in doan[-1]) and mo_dun in _MO_DUN_CHUAN


def _la_test(duong, goc):
    doan = duong.split("/")
    return bool(_THU_MUC_TEST.intersection(doan[:-1])) or bool(_TEN_TEST.search(doan[-1])) or bool(_TEN_TEST_HOA.search(goc))


def _so_dong(tep):
    them, xoa = tep.get("additions"), tep.get("deletions")
    return (them, xoa) if all(type(so) is int and so >= 0 for so in (them, xoa)) else None


def _xet_test(tep, moi):
    """Test có sẵn là điều kiện nghiệm thu: đổi kỳ vọng, đổi tên, chèn dòng tắt test đều làm nó mất tác dụng mà diff
    không nói được. Nên chỉ thêm tệp test mới là tự qua; `__init__.py` trong vùng test quyết định test nào được nạp."""
    if tep.get("status") == "added" and moi.split("/")[-1] != "__init__.py":
        return []
    return [(CAO, "đổi test có sẵn (%s) %s" % (hien_thi(tep.get("status")), hien_thi(tep["filename"])))]


def _la_lockfile(tep):
    return isinstance(tep.get("filename"), str) and _chuan_hoa(tep["filename"]).split("/")[-1] in _LOCKFILE


def _xet_tep(tep):
    if not isinstance(tep, dict):
        return [(CAO, "dữ liệu tệp không hợp lệ")]
    ten_moi, ten_cu = tep.get("filename"), tep.get("previous_filename")
    cac_ten = [ten_moi] + ([] if ten_cu is None else [ten_cu])
    if any(_la_ten_la(d) for d in cac_ten):
        return [(CAO, "tên tệp lạ " + ", ".join(hien_thi(d) for d in cac_ten))]
    moi = _chuan_hoa(ten_moi)
    cu = None if ten_cu is None else _chuan_hoa(ten_cu)
    ket, trang_thai = [], tep.get("status")
    for duong, goc in [(moi, ten_moi)] + ([] if cu is None else [(cu, ten_cu)]):
        if _la_bao_ve(duong):
            ket.append((CAO, "đổi tệp của cổng " + hien_thi(goc)))
        # Phụ thuộc mới chạy trong CI và app, diff không nói được gói đó làm gì: phải có người xem.
        if duong.split("/")[-1] in _LOCKFILE:
            ket.append((CAO, "đổi lockfile " + hien_thi(goc)))
        if _MANIFEST.search(duong):
            ket.append((CAO, "đổi tệp khai phụ thuộc " + hien_thi(goc)))
    if trang_thai != "removed" and moi.endswith(_MA_MAY):
        ket.append((CAO, "có mã máy, diff không đọc được " + hien_thi(ten_moi)))
    if _che_thu_vien(moi, trang_thai):
        ket.append((CAO, "thêm tệp trùng tên mô-đun chuẩn " + hien_thi(ten_moi)))
    so = _so_dong(tep)
    if so is None:
        return ket + [(CAO, "số dòng không hợp lệ " + hien_thi(ten_moi))]
    them, xoa = so
    if _la_test(moi, ten_moi) or (cu is not None and _la_test(cu, ten_cu)):
        ket += _xet_test(tep, moi)
    if trang_thai not in ("added", "modified", "removed", "renamed"):
        ket.append((TRUNG_BINH, "loại thay đổi khác thường " + hien_thi(ten_moi)))
    elif trang_thai in ("added", "modified") and not (them + xoa and tep.get("patch")):
        ket.append((TRUNG_BINH if moi.endswith(_KHONG_CHAY) else CAO, "không có diff dạng chữ " + hien_thi(ten_moi)))
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
        # Lockfile do máy sinh, không tính vào cỡ: đã là rủi ro cao, không cần thêm `ngoai-le-co`.
        tong += sum(so) if so and not _la_lockfile(tep) else 0
    return {"muc": muc, "ly_do": ly_do, "so_dong": tong, "qua_co": tong > NGUONG_CO_DONG}
