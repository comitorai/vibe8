"""Phân rủi ro CHỈ từ diff. Hàm thuần: không nhận thân PR, nhãn hay tiêu đề.

Đầu vào: danh sách tệp đúng dạng GET /pulls/N/files
(filename, previous_filename, status, additions, deletions, patch).
Thiếu dữ liệu thì nghiêng về rủi ro cao hơn, không bao giờ thấp hơn.
"""
import os
import pkgutil
import re
import sys
import sysconfig
import unicodedata

from . import ten

# Hai mức (Alex 1a, 06/11): Cao là chạm bảo mật hay tiền, cần người duyệt; còn lại là Thường, cần phiếu phản bác.
THUONG, CAO = "thuong", "cao"
NGUONG_CO_DONG = 400

_THU_TU = {THUONG: 0, CAO: 1}
_GOC_BAO_VE = ("cong/", "luat/", "docs/bao-mat.md", "nghiem-thu/kiem_cuc_bo.py", "nghiem-thu/bat_cong.py", "nghiem-thu/loi/")
_TEP_BAO_VE = {ten.TEP_CAU_HINH, "codeowners", "makefile", "justfile", "noxfile.py", "tox.ini", "pytest.ini", "conftest.py",
               ".gitattributes", ".gitmodules", "sitecustomize.py", "usercustomize.py"}
_TEP_AGENT = {".mcp.json"}
# Mã máy chạy được mà diff không đọc được: Python nạp `.pyc` hash-based thay cho `.py` mà không so với mã nguồn.
_MA_MAY = (".pyc", ".pyo", ".pyd", ".so", ".dylib", ".dll", ".node", ".wasm", ".jar", ".class")
_KHONG_CHAY = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".woff", ".woff2", ".ttf")  # Tệp không chữ nhưng không tự chạy.
# Tài liệu và tệp tĩnh: không đổi mức, chỉ để ghi lý do «tệp mã chạy được». Danh sách cho phép: đuôi lạ là mã hoặc cấu hình chạy được.
_TAI_LIEU = (".md", ".markdown", ".rst", ".txt", ".adoc")
_TEN_TAI_LIEU = {"license", "licence", "notice", "authors", "contributors", "changelog", "copying", "readme"}
_TXT_CHAY = {"cmakelists.txt"}
TRAN_MAU_VUNG = 200
# Tệp trùng tên mô-đun chuẩn che được thư viện chuẩn khi chạy test. Chỉ Python 3.9 không có danh sách: mới quét thư mục, bỏ `test` cho khớp bản sau.
_MO_DUN_CHUAN = {m.casefold() for m in {"pytest", "_pytest", "json", "os", "re"}.union(sys.builtin_module_names, getattr(sys, "stdlib_module_names", None) or (
    m.name for m in pkgutil.iter_modules([sysconfig.get_path("stdlib"), sysconfig.get_path("stdlib") + "/lib-dynload"]) if m.name != "test"))}
_MAU_SCRIPT_CHECK = re.compile(r"^(check|kiem-tra)(\.[a-z0-9]+)?$|^(vitest|jest|playwright|karma)\.config\.")
_LOCKFILE = {"package-lock.json", "npm-shrinkwrap.json", "pnpm-lock.yaml", "yarn.lock", "bun.lock", "bun.lockb", "poetry.lock", "uv.lock",
             "pipfile.lock", "cargo.lock", "go.sum", "gemfile.lock", "composer.lock", "pdm.lock"}
_MANIFEST = re.compile(r"(^|/)(package\.json|pyproject\.toml|go\.mod|requirements[^/]*\.(txt|in)|requirements/[^/]*\.(txt|in)"
                       r"|constraints[^/]*\.txt|setup\.py|setup\.cfg|cargo\.toml|gemfile|composer\.json|pipfile|\.npmrc"
                       r"|pnpm-workspace\.yaml|dockerfile[^/]*|\.python-version|\.tool-versions|\.pre-commit-config\.yaml"
                       r"|\.nvmrc|\.node-version|\.bun-version|\.ruby-version|\.yarnrc(\.yml)?|\.pnpmfile\.cjs|bunfig\.toml|rust-toolchain(\.toml)?|pom\.xml|(build|settings)\.gradle(\.kts)?)$")
# Dữ liệu kỳ vọng (golden, snapshot, fixture) cũng là điều kiện nghiệm thu: đổi nó là đổi test.
_THU_MUC_TEST = {"test", "tests", "testing", "__tests__", "spec", "specs", "e2e", "cypress", "integration_tests",
                 "testdata", "__snapshots__", "__fixtures__", "fixtures"}
_TEN_TEST = re.compile(r"(^|[._-])(tests?|spec)([._-][^/]*)?\.(py|go|rb|rs|java|kt|cs|php|swift|scala|dart|exs?|c|cc|cpp|sh|[cm]?[jt]sx?)$"
                       r"|^test[^/]*\.py$|\.(bats|snap)$")
_TEN_TEST_HOA = re.compile(r"[a-z0-9](Tests?|Spec)\.(java|kt|cs|rb|php|swift|scala|go|py|[cm]?[jt]sx?)$"  # FooTest.java, UserSpec.rb, TestFoo.java: xét trên tên gốc.
                           r"|(^|/)Tests?[A-Z][^/]*\.(java|kt|cs)$")


def hien_thi(duong):
    """Tên tệp do người mở PR đặt: làm sạch trước khi đưa vào log hay check run."""
    duong = str(duong)
    if len(duong) > 200:  # giữ cả đầu lẫn đuôi: phần đuôi thường nói tệp nằm ở đâu
        duong = duong[:80] + "…" + duong[-119:]
    chu = [c if c.isprintable() and unicodedata.category(c) != "Cf" else "\\u%04x" % ord(c) for c in duong]
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


def _la_cau_hinh_agent(duong):
    """Hook, MCP, lệnh của Claude Code tự chạy trên máy ai mở repo bằng agent: như workflow CI, phải có người đọc."""
    return ".claude" in duong.split("/") or duong.split("/")[-1] in _TEP_AGENT


def _che_thu_vien(duong, trang_thai, them):
    doan = duong.split("/")
    mo_dun = doan[-2] if doan[-1] == "__init__.py" and len(doan) > 1 else doan[-1].split(".")[0]
    # Tên không đuôi: symlink `json` trỏ tới thư mục khác cũng che được mô-đun, API chỉ cho thấy một dòng là đích của nó. Nhiều dòng thì không phải symlink.
    return trang_thai not in ("modified", "removed") and (doan[-1].endswith(".py") or ("." not in doan[-1] and them <= 1)) and mo_dun in _MO_DUN_CHUAN


def _la_test(duong, goc):
    doan = duong.split("/")
    return bool(_THU_MUC_TEST.intersection(doan[:-1])) or bool(_TEN_TEST.search(doan[-1])) or bool(_TEN_TEST_HOA.search(goc))


def _la_tep_test(tep):
    ten_moi, ten_cu = tep.get("filename"), tep.get("previous_filename")
    if not isinstance(ten_moi, str) or _la_ten_la(ten_moi) or (ten_cu is not None and _la_ten_la(ten_cu)):
        return False
    return _la_test(_chuan_hoa(ten_moi), ten_moi) or (ten_cu is not None and _la_test(_chuan_hoa(ten_cu), ten_cu))


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


def _la_tai_lieu(duong):
    cuoi = duong.split("/")[-1]
    return cuoi in _TEN_TAI_LIEU or (cuoi.endswith(_TAI_LIEU + _KHONG_CHAY) and cuoi not in _TXT_CHAY)


def _la_ma_chay(tep, moi, cu):
    """Thêm tệp test mới không tính là mã chạy được; còn lại, tên mới hay tên cũ không phải tài liệu, tệp tĩnh thì là mã chạy được."""
    if tep.get("status") == "added" and _la_test(moi, tep["filename"]) and moi.split("/")[-1] != "__init__.py":
        return False
    return any(not _la_tai_lieu(d) for d in [moi] + ([] if cu is None else [cu]))


class LoiVung(ValueError):
    """Tệp vùng nhạy cảm hỏng. Thông báo hiện trên check: tệp nằm ở nhánh gốc, đã được bảo vệ."""


def _khop_vung(duong, mau):
    """Gần gitignore: `*` khớp cả `/`, `**/` là không hoặc nhiều thư mục, mọi ký tự khác là chữ thường (kể cả `[id]` của Next.js).
    Mẫu khớp chính nó và mọi thứ bên dưới (nên khớp cả con trỏ submodule); mẫu không có `/` khớp ở mọi tầng."""
    loi = mau.rstrip("/")
    than = "".join("(?:.*/)?" if t == "**/" else ".*" if t.startswith("*") else re.escape(t)
                   for t in re.findall(r"\*\*/|\*+|[^*]+", loi))
    return re.fullmatch(("" if "/" in loi else "(?:.*/)?") + than + "(?:/.*)?", duong, re.S) is not None


def doc_vung(duong):
    """Mẫu đường dẫn nhạy cảm repo tự khai, mỗi dòng một mẫu; `#` đầu dòng hoặc sau dấu cách là chú thích. Cú pháp: _khop_vung.
    Không có tệp thì trả None: repo chưa khai, cổng chặn mọi PR. Tệp có mà không mẫu nào là đã khai «không có vùng».
    Tệp có mà hỏng, hay có mẫu không bao giờ khớp được, thì báo lỗi: lặng lẽ bỏ qua là mở cổng."""
    if not duong or not os.path.lexists(duong):
        return None
    if os.path.islink(duong) or not os.path.isfile(duong):
        raise LoiVung("tệp vùng nhạy cảm không phải tệp thường")
    with open(duong, "rb") as f:
        try:
            dong = f.read().decode("utf-8").splitlines()
        except UnicodeDecodeError:
            raise LoiVung("tệp vùng nhạy cảm không phải UTF-8") from None
    mau = [re.sub(r"(^|\s)#.*", "", d).strip() for d in dong]
    mau = [m for m in mau if m]
    for m in mau:
        # `!` phủ định của gitignore, dấu cách lạ, chữ toàn khổ: đường dẫn đã chuẩn hoá không bao giờ khớp được.
        if (_la_ten_la(m.rstrip("/")) or m.startswith(("/", "!")) or "***" in m
                or unicodedata.normalize("NFKC", m) != m or any(c.isspace() and c != " " for c in m)):
            raise LoiVung("mẫu vùng nhạy cảm không hợp lệ: " + hien_thi(m))
    if len(mau) > TRAN_MAU_VUNG:
        raise LoiVung("quá %d mẫu vùng nhạy cảm" % TRAN_MAU_VUNG)
    return mau


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
        if _la_cau_hinh_agent(duong):
            ket.append((CAO, "đổi cấu hình agent, chạy lệnh trên máy người mở repo " + hien_thi(goc)))
        # Phụ thuộc mới chạy trong CI và app, diff không nói được gói đó làm gì: phải có người xem.
        if duong.split("/")[-1] in _LOCKFILE:
            ket.append((CAO, "đổi lockfile " + hien_thi(goc)))
        if _MANIFEST.search(duong):
            ket.append((CAO, "đổi tệp khai phụ thuộc " + hien_thi(goc)))
    if trang_thai != "removed" and moi.endswith(_MA_MAY):
        ket.append((CAO, "có mã máy, diff không đọc được " + hien_thi(ten_moi)))
    so = _so_dong(tep)
    if so is None:
        return ket + [(CAO, "số dòng không hợp lệ " + hien_thi(ten_moi))]
    them, xoa = so
    if _che_thu_vien(moi, trang_thai, them):
        ket.append((CAO, "thêm tệp trùng tên mô-đun chuẩn " + hien_thi(ten_moi)))
    if _la_test(moi, ten_moi) or (cu is not None and _la_test(cu, ten_cu)):
        ket += _xet_test(tep, moi)
    if trang_thai not in ("added", "modified", "removed", "renamed"):
        ket.append((THUONG, "loại thay đổi khác thường " + hien_thi(ten_moi)))
    elif trang_thai in ("added", "modified") and not (them + xoa and tep.get("patch")):
        ket.append((THUONG if moi.endswith(_KHONG_CHAY) else CAO, "không có diff dạng chữ " + hien_thi(ten_moi)))
    return ket


def _xet_muc_moi(tep, vung):
    """Mã chạy được và vùng nhạy cảm. Tên lạ, dữ liệu hỏng đã là Cao ở _xet_tep. Trả (mã chạy được?, [lý do Cao])."""
    if not isinstance(tep, dict):
        return False, []
    if any(_la_ten_la(d) for d in [tep.get("filename")] + ([] if tep.get("previous_filename") is None else [tep["previous_filename"]])):
        return False, []
    moi = _chuan_hoa(tep["filename"])
    cu = None if tep.get("previous_filename") is None else _chuan_hoa(tep["previous_filename"])
    cao = ["chạm vùng nhạy cảm %s: %s" % (hien_thi(m), hien_thi(goc))
           for duong, goc in [(moi, tep["filename"])] + ([] if cu is None else [(cu, tep["previous_filename"])])
           for m in vung if _khop_vung(duong, _chuan_hoa(m))]
    return _la_ma_chay(tep, moi, cu), cao


def phan_loai(ds_tep, vung=()):
    """Trả {muc, ly_do, so_dong, so_dong_test, qua_co, theo_tep}. so_dong không tính lockfile; mức Thường còn trừ tệp test, mức Cao tính đủ (Alex 1a, 09/11);
    so_dong_test là số dòng test, để thẻ duyệt hiện. theo_tep[i]: lý do Cao của ds_tep[i]. vung: mẫu đường dẫn nhạy cảm đọc từ nhánh gốc (doc_vung)."""
    if not isinstance(ds_tep, list):
        return {"muc": CAO, "ly_do": ["không có danh sách tệp"], "so_dong": 0, "so_dong_test": 0, "qua_co": False, "theo_tep": []}
    muc, ly_do, tong, tong_test, ma_chay, theo_tep = THUONG, [], 0, 0, [], []
    for tep in ds_tep:
        la_ma, cao = _xet_muc_moi(tep, vung)
        if la_ma:
            ma_chay.append(tep["filename"])
        cua_tep = _xet_tep(tep) + [(CAO, x) for x in cao]
        # Thẻ duyệt cần biết tệp nào làm PR thành Cao để chỉ đưa diff của tệp đó cho người duyệt.
        theo_tep.append([vi_sao for muc_tep, vi_sao in cua_tep if muc_tep == CAO])
        for muc_tep, vi_sao in cua_tep:
            ly_do.append(vi_sao)
            if _THU_TU[muc_tep] > _THU_TU[muc]:
                muc = muc_tep
        so = _so_dong(tep) if isinstance(tep, dict) else None
        # Lockfile do máy sinh và tệp test không tính vào cỡ (test tách riêng: người đọc diff là AI phản bác, không phải người).
        if so and not _la_lockfile(tep):
            if _la_tep_test(tep):
                tong_test += sum(so)
            else:
                tong += sum(so)
    if ma_chay:
        ly_do.append("%d tệp mã hoặc cấu hình chạy được, vd %s" % (len(ma_chay), hien_thi(ma_chay[0])))
    # Chỉ mức Thường được trừ dòng test: mức Cao tính đủ, vì tệp tên test có thể chứa mã thật (tests/payments_core.py)
    # hay nằm trong vùng nhạy cảm, mà cổng chỉ thấy đường dẫn.
    if muc == CAO:
        tong += tong_test
    return {"muc": muc, "ly_do": ly_do, "so_dong": tong, "so_dong_test": tong_test, "qua_co": tong > NGUONG_CO_DONG, "theo_tep": theo_tep}
