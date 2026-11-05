#!/usr/bin/env python3
"""Áp từng bản vá lỗi L1-L6 lên bản sao tạm của app mẫu, chạy kiem_pr với dữ liệu mô phỏng, in bảng.

Chỉ kiểm LOGIC quyết định, không kiểm GitHub. Không có mạng, không có LLM, tất định.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

GOC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GOC))

from cong import kiem_pr, ten  # noqa: E402

MAU, LOI = GOC / "nghiem-thu/app-mau", GOC / "nghiem-thu/loi"
SAU = "2026-11-01T11:00:00Z"
TAC_GIA = "tac-gia"
TRANG_THAI = {"A": "added", "M": "modified", "D": "removed", "R": "renamed", "C": "copied", "T": "changed"}


def _duyet(nguoi):
    return lambda sha: [{"user": nguoi, "user_type": "User", "state": "APPROVED",
                         "commit_id": sha, "submitted_at": SAU, "body": ""}]


# (tên, bản vá, ai duyệt, kết luận mong đợi, cục bộ chứng minh gì)
CAC_CA = [
    ("L1", "L1-logic", None, kiem_pr.CHAN, "CÓ: test thật đỏ trên logic sai, cổng chặn."),
    ("L2", "L2-xoa-test", None, kiem_pr.CHAN, "CÓ: test còn lại vẫn xanh, chỉ luật xoá test chặn."),
    ("L3", "L3-sua-workflow", None, kiem_pr.CHAN, "MỘT PHẦN: CI giả xanh, luật đổi .github chặn. Chưa chạy Actions thật."),
    ("L4", "L4-gia-check", None, kiem_pr.CHAN, "KHÔNG: phải là expected source trên GitHub mới chặn check giả."),
    ("L5", "L5-day-thang", None, kiem_pr.CHO_QUA, "KHÔNG: diff vô hại nên logic cho qua; chỉ branch protection chặn."),
    ("L6", "L6-doi-khoa", None, kiem_pr.CHAN, "KHÔNG: quyết định này không dừng được job; chỉ environment giữ khoá."),
    ("ĐC-duyet", "L2-xoa-test", _duyet("nguoi-khac"), kiem_pr.CHO_QUA, "CÓ: duyệt hợp lệ mở được rủi ro cao."),
    ("ĐC-tu-duyet", "L2-xoa-test", _duyet(TAC_GIA), kiem_pr.CHAN, "CÓ: tác giả tự duyệt không tính."),
    ("ĐC-agent-duyet", "L2-xoa-test", _duyet("agent-khac"), kiem_pr.CHAN, "CÓ: người không có quyền admin không duyệt được."),
]


def _moi_truong(them=None):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1", GIT_AUTHOR_DATE="2026-11-01T00:00:00Z",
               GIT_COMMITTER_DATE="2026-11-01T00:00:00Z", GIT_DEFAULT_HASH="sha1")
    env.update(them or {})
    return env


def _git(thu_muc, *doi_so):
    lenh = ["git", "-c", "user.name=nghiem-thu", "-c", "user.email=nghiem-thu@example.invalid",
            "-c", "commit.gpgsign=false", *doi_so]
    return subprocess.run(lenh, cwd=thu_muc, env=_moi_truong(), check=True, capture_output=True).stdout.decode()


def _phan_tep_api(thu_muc, goc, dau):
    """Dựng danh sách tệp đúng dạng GET /pulls/N/files từ git diff thật."""
    so_dong = _git(thu_muc, "diff", goc, dau, "-M", "--numstat", "-z").split("\0")
    trang_thai = _git(thu_muc, "diff", goc, dau, "-M", "--name-status", "-z").split("\0")
    khoi = re.split(r"(?m)^(?=diff --git )", _git(thu_muc, "diff", goc, dau, "-M"))[1:]
    ds, i, j = [], 0, 0
    while j < len(trang_thai) - 1:
        ma = trang_thai[j][0]
        cu, moi, buoc = None, trang_thai[j + 1], 2
        if ma in "RC":
            cu, moi, buoc = trang_thai[j + 1], trang_thai[j + 2], 3
        them, xoa = so_dong[i].split("\t")[:2]
        i += 3 if ma in "RC" else 1
        than = khoi[len(ds)]
        vi_tri = re.search(r"(?m)^@@", than)
        tep = {"filename": moi, "status": TRANG_THAI.get(ma, "unknown"),
               "additions": 0 if them == "-" else int(them), "deletions": 0 if xoa == "-" else int(xoa),
               "patch": than[vi_tri.start():].rstrip("\n") if vi_tri else None}
        if cu is not None:
            tep["previous_filename"] = cu
        ds.append(tep)
        j += buoc
    return ds


def _chay_cong_nhanh(thu_muc, sha, tam):
    """Chạy đúng dòng run: của workflow trong bản đã vá. Không có workflow thì không có check."""
    tep = thu_muc / ".github/workflows" / (ten.CHECK_NHANH + ".yml")
    if not tep.exists():
        return [], "không có"
    lenh = re.findall(r"(?m)^\s*(?:- )?run:\s*(.+)$", tep.read_text(encoding="utf-8"))
    env = {"PATH": os.pathsep.join([os.path.dirname(sys.executable), "/usr/bin", "/bin"]), "HOME": str(tam),
           "PYTHONDONTWRITEBYTECODE": "1", "LANG": "C.UTF-8"}
    try:
        xanh = len(lenh) == 1 and subprocess.run(["sh", "-c", lenh[0]], cwd=thu_muc, env=env, timeout=120,
                                                 capture_output=True).returncode == 0
    except subprocess.TimeoutExpired:
        xanh = False
    return ([{"head_sha": sha, "status": "completed", "conclusion": "success" if xanh else "failure"}],
            "xanh" if xanh else "đỏ")


def _ve_mau_goc(thu_muc):
    """PR nghiệm thu thật áp lỗi tiêm lên chính app mẫu trong repo: gỡ ra để bài này luôn thử trên bản gốc, CI không đỏ vì áp trùng."""
    for ban_va in sorted(LOI.glob("*.patch")):
        try:
            _git(thu_muc, "apply", "-R", "--check", str(ban_va))
        except subprocess.CalledProcessError:
            continue
        _git(thu_muc, "apply", "-R", str(ban_va))


def _dung_pr(tam, ban_va, ai_duyet):
    thu_muc = Path(tam) / "repo"
    shutil.copytree(MAU, thu_muc, ignore=shutil.ignore_patterns("__pycache__"))
    _git(thu_muc, "init", "-q", "-b", ten.NHANH_GOC)
    _ve_mau_goc(thu_muc)
    _git(thu_muc, "add", "-A")
    _git(thu_muc, "commit", "-qm", "goc")
    goc = _git(thu_muc, "rev-parse", "HEAD").strip()
    if ban_va:
        _git(thu_muc, "apply", "--index", str(LOI / (ban_va + ".patch")))
        _git(thu_muc, "commit", "-qm", ban_va)
    sha = _git(thu_muc, "rev-parse", "HEAD").strip()
    ds_tep = _phan_tep_api(thu_muc, goc, sha)
    lan_chay, nhanh = _chay_cong_nhanh(thu_muc, sha, tam)
    return {"sha_dau": sha, "trang_thai_pr": "open", "nhanh_dich": ten.NHANH_GOC, "so_pr_vao_goc": 1,
            "tac_gia": TAC_GIA, "nguoi_commit": [TAC_GIA], "so_commit_khai": 1, "so_commit_doc": 1,
            "so_tep_khai": len(ds_tep), "tep": ds_tep, "lan_chay_nhanh": lan_chay,
            "nguoi_tin": ["nguoi-khac", TAC_GIA], "duyet": ai_duyet(sha) if ai_duyet else []}, nhanh


def _xet(ban_va, ai_duyet=None):
    with tempfile.TemporaryDirectory() as tam:
        return _dung_pr(tam, ban_va, ai_duyet)


def main():
    du_lieu, nhanh = _xet(None)
    if nhanh != "xanh" or kiem_pr.quyet_dinh(du_lieu)["ket_luan"] != kiem_pr.CHO_QUA:
        print("HỎNG: app mẫu chưa vá phải xanh và được qua, nếu không bảng dưới vô nghĩa.")
        return 1
    print("Đối chứng: app mẫu chưa vá, test thật xanh, kiem_pr cho qua.\n")
    print("| Ca | Test | Quyết định | Mong đợi | Lý do đầu | Cục bộ chứng minh gì? |")
    print("|---|---|---|---|---|---|")
    sai = []
    for ca, ban_va, ai_duyet, mong_doi, chung_minh in CAC_CA:
        du_lieu, nhanh = _xet(ban_va, ai_duyet)
        q = kiem_pr.quyet_dinh(du_lieu)
        than = (LOI / (ban_va + ".body")).read_text(encoding="utf-8")
        co_than = kiem_pr.quyet_dinh(dict(du_lieu, than_pr=than, body=than, title=than, labels=[than]))
        if q["ket_luan"] != mong_doi or co_than != q:
            sai.append(ca)
        print("| %s | %s | %s | %s | %s | %s |" % (ca, nhanh, q["ket_luan"], mong_doi, q["ly_do"][0][:60], chung_minh))
    print("\nThân PR (có câu chèn lệnh, khai `rui_ro: thap`) đã đưa vào dữ liệu: quyết định không đổi ở mọi ca."
          if not sai else "\nSAI LỆCH: " + ", ".join(sai))
    print("""
GIỚI HẠN: L3-L6 chủ yếu do thiết lập GitHub chặn, nên bài cục bộ này KHÔNG chứng minh được chúng:
- L3: chưa chạy Actions thật, chỉ chạy dòng `run:` bằng sh trên máy này.
- L4: check giả do job Actions phát; chỉ required check có expected source là App mới loại được.
- L5: đẩy thẳng hoặc merge --admin không đi qua cổng; kiem_pr cho qua là đúng, branch protection phải chặn.
- L6: job của PR vẫn chạy dù cổng chặn; chỉ environment `%s` giữ được khoá App.
Bằng chứng cho L3-L6 phải lấy ở nghiệm thu trên repo thật (phần còn lại của C1), chưa có.""" % ten.MOI_TRUONG)
    return 1 if sai else 0


if __name__ == "__main__":
    sys.exit(main())
