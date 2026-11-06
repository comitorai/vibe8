#!/usr/bin/env python3
"""Đo nhịp PR trên repo đã bật cổng, để biết chậm ở đâu thay vì đoán. Chỉ đọc, chỉ gọi GET.

Với mỗi PR vào nhánh gốc: từ lúc mở tới kết luận đầu của cổng, thời gian chạy CI, số lượt CI đỏ,
từ lúc mở tới lượt duyệt đầu, từ lúc mở tới merge. Cuối bảng là trung vị và tỉ lệ PR tự qua không cần người.

    GH_TOKEN=... python3 nghiem-thu/do_nhip.py --repo chu/repo [--so 30] [--json]

Giới hạn: check và lượt CI chỉ đọc theo head hiện tại của PR, nên PR đẩy nhiều commit chỉ phản ánh commit cuối.
"""
import argparse
import datetime
import json
import os
import re
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cong import ten  # noqa: E402
from cong.gate_app import TOKEN_HOP_LE, GitHub, LoiApi  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from do_vong import app_ghim, loc_app  # noqa: E402

_WORKFLOW_CI = ".github/workflows/%s.yml" % ten.CHECK_NHANH
_MUC = re.compile(r"\((thuong|cao|thap|trung_binh)\)")
COT = ("mo_toi_cong", "ci_giay", "mo_toi_duyet", "mo_toi_merge")


def _gio(chuoi):
    return datetime.datetime.fromisoformat(chuoi.replace("Z", "+00:00")) if chuoi else None


def _cach(dau, cuoi):
    return round((cuoi - dau).total_seconds()) if dau and cuoi else None


def chi_so(pr, check_cuoi, luot_ci, duyet):
    """Hàm thuần: dữ liệu REST của một PR vào, một dòng số đo ra. Thiếu dữ liệu thì để None, không đoán."""
    mo = _gio(pr["created_at"])
    xong_cong = sorted(_gio(c["completed_at"]) for c in check_cuoi if c.get("completed_at"))
    moi_nhat = max(check_cuoi, key=lambda c: c.get("completed_at") or "", default=None)
    muc = _MUC.search(((moi_nhat or {}).get("output") or {}).get("title") or "")
    da_duyet = sorted(_gio(d["submitted_at"]) for d in duyet if d.get("state") == "APPROVED" and d.get("submitted_at"))
    ci = [_cach(_gio(r.get("run_started_at") or r["created_at"]), _gio(r["updated_at"]))
          for r in luot_ci if r.get("status") == "completed"]
    merge = _gio(pr.get("merged_at"))
    return {
        "pr": pr["number"],
        "trang_thai": "merged" if merge else pr["state"],
        "muc": muc.group(1) if muc else None,
        "mo_toi_cong": _cach(mo, xong_cong[0]) if xong_cong else None,
        "ci_giay": max(ci) if ci else None,
        "ci_do": sum(1 for r in luot_ci if r.get("status") == "completed" and r.get("conclusion") != "success"),
        "mo_toi_duyet": _cach(mo, da_duyet[0]) if da_duyet else None,
        "mo_toi_merge": _cach(mo, merge),
        "tu_qua": bool(merge) and not da_duyet,
    }


def tong_hop(dong):
    merged = [d for d in dong if d["trang_thai"] == "merged"]
    ket = {"so_pr": len(dong), "so_merged": len(merged), "so_tu_qua": sum(d["tu_qua"] for d in merged)}
    ket["ti_le_tu_qua"] = round(ket["so_tu_qua"] / len(merged), 2) if merged else None
    for cot in COT:
        so = [d[cot] for d in dong if d[cot] is not None]
        ket["trung_vi_" + cot] = statistics.median(so) if so else None
    return ket


def doc_pr(gh, pr, app_id):
    sha = pr["head"]["sha"]
    # filter=all: mặc định API chỉ trả check mới nhất, sẽ mất kết luận đầu của cổng.
    check = gh.goi("GET", "/commits/%s/check-runs?check_name=%s&filter=all&per_page=100" % (sha, ten.CHECK_CUOI))["check_runs"]
    check = loc_app(check, app_id)
    luot = gh.goi("GET", "/actions/runs?head_sha=%s&event=pull_request&per_page=100" % sha)["workflow_runs"]
    luot = [r for r in luot if r.get("path") == _WORKFLOW_CI]
    return chi_so(pr, check, luot, gh.goi("GET", "/pulls/%d/reviews?per_page=100" % pr["number"]))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", required=True)
    ap.add_argument("--so", type=int, default=30, help="số PR gần nhất, tối đa 100")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--app-id", type=int, help="App phát check cổng; mặc định đọc từ bảo vệ nhánh gốc")
    a = ap.parse_args(argv)
    token = (os.environ.get("GH_TOKEN") or "").strip()
    if not TOKEN_HOP_LE.fullmatch(token):  # không in giá trị
        print("Thiếu biến GH_TOKEN hoặc token có ký tự lạ.", file=sys.stderr)
        return 2
    gh = GitHub(a.repo, token)
    try:
        ds = gh.goi("GET", "/pulls?state=all&base=%s&sort=created&direction=desc&per_page=%d" % (ten.NHANH_GOC, min(a.so, 100)))
        app_id = a.app_id or app_ghim(gh)
        if app_id is None:
            print("Cảnh báo: %s chưa ghim App cho %s: bỏ mọi check, cột mở→cổng và mức để trống." % (
                ten.NHANH_GOC, ten.CHECK_CUOI), file=sys.stderr)
        dong = [doc_pr(gh, pr, app_id) for pr in ds]
    except LoiApi as loi:
        print(gh.che(str(loi)), file=sys.stderr)
        return 1
    tong = tong_hop(dong)
    if a.json:
        print(json.dumps({"pr": dong, "tong": tong}, ensure_ascii=False, indent=1))
        return 0
    print("PR\ttrạng thái\tmức\tmở→cổng\tCI\tCI đỏ\tmở→duyệt\tmở→merge\ttự qua")
    for d in dong:
        print("\t".join(str("-" if d[k] is None else d[k]) for k in (
            "pr", "trang_thai", "muc", "mo_toi_cong", "ci_giay", "ci_do", "mo_toi_duyet", "mo_toi_merge", "tu_qua")))
    print(json.dumps(tong, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
