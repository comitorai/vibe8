#!/usr/bin/env python3
"""Hook Claude Code tự chạy máy ghi token (ghi_token.py) đúng hai lúc luật mục 8.3 đòi, để agent khỏi phải nhớ.

Khai trong .claude/settings.json của repo:
- PostToolUse, lệnh Bash có `git push` hoặc `gh pr create`: ghi token của PR nhánh đang mở. Nhánh chưa có PR thì
  im lặng, vì lúc `gh pr create` chạy xong hook sẽ ghi.
- PreToolUse, lệnh Bash có `gh pr merge`, hoặc `gh api` gọi `repos/<chủ>/<repo>/pulls/<số>/merge`: ghi lần cuối
  trước khi merge, khi nhánh còn đang mở. Có số PR trong lệnh thì ghi cho đúng PR đó. Lệnh `gh api` nhắm repo khác
  remote `origin` thì không ghi, vì bản ghi phiên đọc theo repo trên đĩa.

Không bao giờ chặn lệnh: hook luôn thoát 0. Ghi hỏng thì báo agent (PostToolUse) hoặc người dùng (PreToolUse) để chạy tay.
Token GitHub lấy từ `gh auth token`, không in ra. Repo lấy từ remote `origin`.
Giới hạn: lệnh gọi qua script khác (vd `sh day.sh` bên trong có `git push`) thì hook không thấy; merge bằng nút trên
GitHub thì không có lần ghi trước merge, chỉ còn lần ghi sau lần đẩy cuối.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

GHI_TOKEN = Path(__file__).resolve().parent / "ghi_token.py"
_PUSH = re.compile(r"(^|[;&|(\s])git(\s+-[Cc]\s+\S+)*\s+push\b")
_TAO_PR = re.compile(r"(^|[;&|(\s])gh\s+pr\s+create\b")
_MERGE = re.compile(r"(^|[;&|(\s])gh\s+pr\s+merge\b(?P<sau>[^;&|\n]*)")
# `gh api` merge một PR: đường dẫn REST, có hay không `/` đầu, `{owner}/{repo}` là repo hiện tại.
_MERGE_API = re.compile(r"(^|[;&|(\s])gh\s+api\b[^;&|\n]*?(?:^|[\s'\"/])repos/(?P<chu>[\w.{}-]+)/(?P<repo>[\w.{}-]+)"
                        r"/pulls/(?P<so>\d+)/merge(?=[\s'\"?]|$)")
_SO_PR = re.compile(r"(?:^|\s)#?(\d+)(?=\s|$)")
_REMOTE = re.compile(r"github\.com[:/]([\w.-]+/[\w.-]+?)(?:\.git)?/?$")
CHUA_CO_PR = "chưa có PR"
KHAC_REPO = "lệnh merge repo khác origin"


def repo_merge_api(lenh):
    """`chủ/repo` mà lệnh `gh api … /pulls/N/merge` nhắm tới; None nếu không phải lệnh đó hoặc dùng `{owner}/{repo}`."""
    m = _MERGE_API.search(lenh) if isinstance(lenh, str) else None
    if not m or "{" in m.group("chu") + m.group("repo"):
        return None
    return "%s/%s" % (m.group("chu"), m.group("repo"))


def can_ghi(su_kien, ten_tool, lenh):
    """(có ghi không, số PR hoặc None). Chỉ xét lệnh Bash."""
    if ten_tool != "Bash" or not isinstance(lenh, str):
        return False, None
    if su_kien == "PreToolUse":
        m = _MERGE.search(lenh)
        if not m:
            api = _MERGE_API.search(lenh)
            return (True, int(api.group("so"))) if api else (False, None)
        so = _SO_PR.search(m.group("sau"))
        return True, int(so.group(1)) if so else None
    if su_kien == "PostToolUse":
        return bool(_PUSH.search(lenh) or _TAO_PR.search(lenh)), None
    return False, None


def repo_tu_remote(url):
    m = _REMOTE.search((url or "").strip())
    return m.group(1) if m else None


def _chay(lenh, cwd, env=None):
    return subprocess.run(lenh, cwd=cwd, capture_output=True, text=True, timeout=50, env=env)


def ghi(cwd, so_pr, repo_lenh=None):
    """(thành công?, câu báo). Không đưa token vào câu báo. `repo_lenh`: repo lệnh merge nhắm tới, khác origin thì bỏ."""
    try:
        url = _chay(["git", "remote", "get-url", "origin"], cwd).stdout
        repo = repo_tu_remote(url)
        if not repo:
            return False, "không đọc được repo GitHub từ remote origin"
        if repo_lenh and repo_lenh.lower() != repo.lower():
            return False, KHAC_REPO
        tk = _chay(["gh", "auth", "token"], cwd)
        token = tk.stdout.strip()
        if tk.returncode or not token:
            return False, "`gh auth token` không trả token; đăng nhập gh rồi chạy tay"
        env = dict(os.environ, GH_TOKEN=token)
        lenh = [sys.executable, str(GHI_TOKEN), "--repo", repo] + (["--pr", str(so_pr)] if so_pr else [])
        kq = _chay(lenh, cwd, env)
    except (OSError, subprocess.SubprocessError) as loi:
        return False, "không chạy được: %s" % type(loi).__name__
    if kq.returncode == 0:
        return True, kq.stdout.strip()
    bao = (kq.stderr or kq.stdout).strip().splitlines()
    return False, (bao[-1] if bao else "thoát mã %d" % kq.returncode).replace(token, "***")


def tra_loi(su_kien, ok, bao):
    """JSON cho Claude Code, hoặc None nếu không cần nói gì."""
    if ok:
        cau = "Máy ghi token: " + bao
    elif CHUA_CO_PR in bao:
        return None  # đẩy trước khi mở PR: `gh pr create` sẽ ghi
    elif bao == KHAC_REPO:
        return None  # merge PR của repo khác: không phải việc của repo này
    else:
        cau = "Máy ghi token chưa ghi được (%s). Chạy tay: GH_TOKEN=$(gh auth token) python3 nghiem-thu/ghi_token.py --repo <chủ/repo>" % bao
    if su_kien == "PostToolUse":
        return {"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": cau}}
    return None if ok else {"systemMessage": cau}


def main(stdin=None):
    try:
        vao = json.load(stdin or sys.stdin)
    except ValueError:
        return 0
    if not isinstance(vao, dict):
        return 0
    su_kien = vao.get("hook_event_name")
    co, so_pr = can_ghi(su_kien, vao.get("tool_name"), (vao.get("tool_input") or {}).get("command"))
    if not co:
        return 0
    lenh = (vao.get("tool_input") or {}).get("command")
    repo_lenh = repo_merge_api(lenh) if su_kien == "PreToolUse" and not _MERGE.search(lenh) else None
    ok, bao = ghi(vao.get("cwd") or ".", so_pr, repo_lenh) if repo_lenh else ghi(vao.get("cwd") or ".", so_pr)
    ra = tra_loi(su_kien, ok, bao)
    if ra:
        print(json.dumps(ra, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
