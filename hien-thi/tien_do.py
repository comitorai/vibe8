#!/usr/bin/env python3
"""Xuất trang tiến độ từ sổ phase (luat/hien-thi-tien-do.md: HT-01…HT-05, HT-11…HT-13). Chỉ đọc; không ghi vào repo.

Dùng: tien_do.py --repo-dir <repo git> --ra <trang.html> [--github chu/repo] [--lan lan.json] [--ten Tên]
Nguồn: docs/phase/<MÃ>-<n>.md · lịch sử git của sổ · PR và comment `cap-nhat:` trên GitHub (có --github).
Hàng làn (HT-13) đọc từ tệp JSON do bên ngoài đưa vào: {"lan":[{"phase","task","ten","may","nhip","cho":[],"co":[],
"cau","cau_tuoi_phut","buoc","da_chay_phut","ngu_canh_nghin","pr"}]}. Chưa làm: dự báo HT-06, cờ Chờ phiếu/Chờ duyệt/Chờ bạn.
"""
import argparse, datetime as dt, html, json, re, subprocess, sys
from pathlib import Path
from zoneinfo import ZoneInfo

HUY, XONG, DANG, CHUA = "Đã huỷ", "Hoàn thành", "Đang làm", "Chưa bắt đầu"
MOC = [(8, 30), (11, 30), (17, 30)]  # HT-11, theo múi giờ của chủ dự án
SK = {"dung-huong": "Đúng hướng", "co-rui-ro": "Có rủi ro", "cham": "Chậm"}
FILE_PHASE = re.compile(r"^[A-Z]+-\d+-\d+\.md$")


def chuan(tt, ghi_chu=""):
    t = tt.lower().strip("*_ ")
    if t.startswith(("đã huỷ", "đã hủy")): return HUY
    if t.startswith(("hoàn thành", "xong")): return XONG
    if t.startswith(("đang làm", "chờ duyệt")): return DANG
    return CHUA


def doc_so(text):
    """-> (đầu sổ, {mã task: dòng}). Cột lấy theo tên nên thêm cột không làm gãy."""
    han = re.search(r"\*\*Hạn:\*\*\s*(\d\d)/(\d\d)/(\d{4})", text)
    issue = re.search(r"Cập nhật:\*\*\s*issue #(\d+)", text)
    dau = {"han": dt.date(int(han[3]), int(han[2]), int(han[1])) if han else None,
           "issue": int(issue[1]) if issue else None,
           "ten": (re.match(r"# Phase [^:]+:\s*(.*)", text) or [0, ""])[1]}
    cot, rows = None, {}
    for ln in text.splitlines():
        if not ln.startswith("|"): continue
        c = [x.strip() for x in re.split(r"(?<!\\)\|", ln.strip().strip("|"))]
        if "Task" in c and "Trạng thái" in c: cot = c; continue
        if cot and re.match(r"T\d", c[0]) and len(c) == len(cot):
            r = dict(zip(cot, c))
            r["tt"] = chuan(r["Trạng thái"])
            pr = re.search(r"#(\d+)", r.get("PR", ""))
            r["pr"] = int(pr[1]) if pr else None
            rows[c[0]] = r
    return dau, rows


def dem(rows):
    d = {XONG: 0, DANG: 0, CHUA: 0, HUY: 0}
    for r in rows.values(): d[r["tt"]] += 1
    return d


def pham_vi(truoc, sau):
    """HT-05: +1 task mới kèm doi-yc; -1 task chuyển Đã huỷ cùng commit thêm doi-yc. Tách/gộp không vào ±n."""
    n = 0
    for k, r in sau.items():
        cu = truoc.get(k)
        if "doi-yc" not in r.get("Ghi chú", "") or (cu and "doi-yc" in cu.get("Ghi chú", "")): continue
        if cu is None: n += 1
        elif r["tt"] == HUY and cu["tt"] != HUY: n -= 1
    return n


def lich_su(repo, rel, tz):
    """-> [(ngày, rows)] từ commit đầu tiên có bảng task; rỗng nếu sổ chưa vào git."""
    def git(*a): return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True).stdout
    out = []
    for ln in git("log", "--reverse", "--format=%H %aI", "--", rel).splitlines():
        h, t = ln.split(" ", 1)
        rows = doc_so(git("show", f"{h}:{rel}"))[1]
        if rows: out.append((dt.datetime.fromisoformat(t).astimezone(tz).date(), rows))
    return out


def phan_tich_su(ls, hom_nay):
    """-> (±n, đứng yên n ngày | None). Đứng yên tính từ lần cuối số Hoàn thành tăng, hay từ lúc sổ có bảng."""
    pm, moc, xong = 0, None, -1
    for i, (ngay, rows) in enumerate(ls):
        if i: pm += pham_vi(ls[i - 1][1], rows)
        x = dem(rows)[XONG]
        if x > xong: moc = ngay
        xong = x
    return pm, ((hom_nay - moc).days if moc else None)


def tuoi_cap_nhat(t, now):
    """HT-11: số mốc giờ đã qua kể từ comment cuối."""
    n, d = 0, t.date()
    while d <= now.date():
        for h, m in MOC:
            mo = dt.datetime(d.year, d.month, d.day, h, m, tzinfo=now.tzinfo)
            n += t < mo <= now
        d += dt.timedelta(1)
    return n


def doc_cap_nhat(comments, tz):
    """Comment mới nhất có khuôn `cap-nhat:` của người có quyền ghi."""
    for c in sorted(comments, key=lambda c: c["created_at"], reverse=True):
        if c.get("author_association") not in ("OWNER", "MEMBER", "COLLABORATOR"): continue
        kv = dict(re.findall(r"^(cap-nhat|suc-khoe|ly-do):\s*(.+)$", c["body"], re.M))
        if "cap-nhat" in kv:
            return {"cau": kv["cap-nhat"], "sk": SK.get(kv.get("suc-khoe")), "ly_do": kv.get("ly-do", ""),
                    "luc": dt.datetime.fromisoformat(c["created_at"].replace("Z", "+00:00")).astimezone(tz),
                    "xn": c.get("reactions", {}).get("+1", 0) > 0}


def gh(*a):
    r = subprocess.run(["gh", *a], capture_output=True, text=True)
    return json.loads(r.stdout) if r.returncode == 0 and r.stdout.strip() else None


def lay_pr(repo, n):
    d = gh("pr", "view", str(n), "--repo", repo, "--json", "state,statusCheckRollup")
    if not d: return None
    ci = [c for c in d["statusCheckRollup"] or [] if "cong-nhanh" in (c.get("workflowName"), c.get("name"))]
    return {"state": d["state"], "cho_ci": any(c.get("status") != "COMPLETED" for c in ci)}


def lay_comment(repo, n):
    return gh("api", f"repos/{repo}/issues/{n}/comments", "--paginate") or []


def tuoi(p):
    p = int(p)
    return f"{p} phút" if p < 90 else f"{p // 60} giờ" if p < 2880 else f"{p // 1440} ngày"


def tinh_phase(ten, text, ls, now, pr_of, comments_of):
    dau, rows = doc_so(text)
    lech = []
    for k, r in rows.items():
        p = pr_of(r["pr"]) if r["pr"] and pr_of else None
        r["co"] = []
        if p:
            moi = {"MERGED": XONG, "OPEN": DANG}.get(p["state"], r["tt"])
            if moi != r["tt"]: lech.append(f"{k}: sổ {r['tt']}, GitHub {moi}")
            r["tt"] = moi
            if p["cho_ci"]: r["co"].append("Chờ CI")
        if r["tt"] != XONG and r.get("Chờ task", "-").strip(" —-"): r["co"].append("Chờ task khác")
    d = dem(rows)
    mau = d[XONG] + d[DANG] + d[CHUA]
    tt = XONG if mau and d[XONG] == mau else DANG if d[XONG] or d[DANG] else CHUA
    pm, yen = phan_tich_su(ls, now.date()) if ls else (0, None)
    cn = doc_cap_nhat(comments_of(dau["issue"]), now.tzinfo) if comments_of and dau["issue"] else None
    mo = tuoi_cap_nhat(cn["luc"], now) if cn else None
    co = []
    if tt == DANG and (mo is None or mo >= 2): co.append("Thiếu cập nhật")
    if tt == DANG and yen is not None and yen >= 2: co.append(f"đứng yên {yen} ngày")
    return {"ten": ten, "tieu_de": dau["ten"], "han": dau["han"], "tt": tt, "d": d, "mau": mau, "pm": pm, "rows": rows,
            "cn": cn, "mo": mo, "co": co, "lech": lech}


def pct(d, mau): return round(100 * d[XONG] / mau) if mau else None


def vong(tt, p=0):
    ky = {XONG: "✓", HUY: "✕", CHUA: ""}.get(tt, "")
    return f'<span class="v" role="img" aria-label="{tt}" title="{tt}" style="--p:{p}">{ky}</span>'


def chip(t, k=""): return f'<span class="chip {k}">{html.escape(t)}</span>'


def thanh(d, mau):
    if not mau: return '<span class="muted">Chưa có số</span>'
    w = lambda n: f"{100 * n / mau:.1f}%"
    return (f'<span class="tb" role="img" aria-label="{d[XONG]}/{mau} xong"><i class="x" style="width:{w(d[XONG])}"></i>'
            f'<i class="d" style="width:{w(d[DANG])}"></i></span> {d[XONG]}/{mau} · {pct(d, mau)}%')


def hang_lan(l, may_cha=None):
    cho = "".join(chip(c) for c in l.get("cho", [])) + "".join(chip(c, "do") for c in l.get("co", []))
    may = f" · {html.escape(l['may'])}" if l.get("may") and l["may"] != may_cha else ""  # HT-04
    cau = (f'{html.escape(l["cau"])} <span class="muted">({tuoi(l["cau_tuoi_phut"])})</span>' if l.get("cau")
           else '<span class="muted">Chưa có câu cập nhật</span>')
    buoc = f' · bước {html.escape(l["buoc"])} <span class="muted">tự khai</span>' if l.get("buoc") else ""
    cuoi = " · ".join(x for x in [f'chạy {tuoi(l["da_chay_phut"])}' if "da_chay_phut" in l else "",
                                   f'ngữ cảnh {l["ngu_canh_nghin"]} nghìn' if "ngu_canh_nghin" in l else "",
                                   f'PR #{l["pr"]}' if l.get("pr") else ""] if x)
    return (f'<div class="h lan"><div class="l1">{vong(DANG)}<b>{html.escape(l.get("ten", ""))}</b>{may}{cho}'
            f'<span class="sk">{html.escape(l.get("nhip", ""))}</span></div>'
            f'<div class="l2">{cau}{buoc}</div><div class="l2 muted">{cuoi}</div></div>')


def hang_phase(p, lan):
    cn, d = p["cn"], p["d"]
    sk = (f'<span class="sk s-{cn["sk"]}{" cu" if p["mo"] else ""}" title="{html.escape(cn["ly_do"])}">{cn["sk"]} · '
          f'{"đã xác nhận" if cn["xn"] else "chưa xác nhận"}</span>' if cn and cn["sk"] else '<span class="sk">Chưa đánh giá</span>')
    if p["mo"] is not None and p["mo"] >= 2: sk = '<span class="sk xam">Thiếu cập nhật</span>'
    cau = (f'{html.escape(cn["cau"])}' if cn else "Chưa có câu cập nhật")
    pv = f" · phạm vi {p['pm']:+d}" if p["pm"] else " · phạm vi ±0"
    han = f" · hạn {p['han']:%d/%m/%Y}" if p["han"] else ""
    chips = "".join(chip(c, "do" if c == "Lệch" else "") for c in p["co"])
    xong = [k for k, r in p["rows"].items() if r["tt"] == XONG]
    viec = "".join(hang_viec(k, r) for k, r in p["rows"].items() if r["tt"] != XONG)
    gap = f'<details><summary>{len(xong)} việc đã xong</summary>{"".join(hang_viec(k, p["rows"][k]) for k in xong)}</details>' if xong else ""
    lech = "".join(f'<div class="l2 muted">⚠ {html.escape(x)}</div>' for x in p["lech"])
    return (f'<div class="h"><div class="l1">{vong(p["tt"], pct(d, p["mau"]) or 0)}<b>{p["ten"]}</b> {html.escape(p["tieu_de"])}{chips}{sk}</div>'
            f'<div class="l2">{cau}</div><div class="l2">{thanh(d, p["mau"])}{pv}{han} · <span class="muted">chưa có dự báo</span></div>{lech}'
            f'<div class="con">{"".join(hang_lan(l) for l in lan)}{viec}{gap}</div></div>')


def hang_viec(k, r):
    pr = chip(f"PR #{r['pr']}") if r["pr"] else ""
    cc = "".join(chip(c) for c in r["co"])
    return (f'<div class="h viec"><div class="l1">{vong(r["tt"])}<b>{k}</b> {html.escape(r.get("Yêu cầu", ""))[:110]}{pr}{cc}</div></div>')


def dem_ngoai_le(phases):
    c = {"Chậm": 0, "Có rủi ro": 0, "Thiếu cập nhật": 0, "Đứng yên": 0, "Lệch GitHub": 0}
    for p in phases:
        if p["tt"] != DANG: continue
        if p["cn"] and p["cn"]["sk"] in c: c[p["cn"]["sk"]] += 1
        c["Thiếu cập nhật"] += "Thiếu cập nhật" in p["co"]
        c["Đứng yên"] += any(x.startswith("đứng yên") for x in p["co"])
        c["Lệch GitHub"] += len(p["lech"])
    return c


CSS = """body{overflow-wrap:anywhere;font:15px/1.5 system-ui,sans-serif;margin:0;padding:12px 16px;background:#fff;color:#1b1b1f}
.h{border-top:1px solid #ddd;padding:8px 0}.con{margin-left:22px}.l2{margin-left:26px;font-size:13px}.muted{color:#666}
.v{display:inline-grid;place-items:center;width:16px;height:16px;border-radius:50%;margin-right:8px;font-size:10px;vertical-align:-2px;
background:conic-gradient(#2a6fdb calc(var(--p)*1%),#fff 0);border:2px solid #2a6fdb}
.chip{margin-left:6px;padding:0 7px;border:1px solid #777;border-radius:9px;font-size:12px;color:#444}.chip.do{border-color:#b3261e;color:#b3261e}
.sk{margin-left:8px;padding:0 7px;border:2px solid #777;border-radius:4px;font-size:12px}.sk.xam{background:#eee;color:#666}
.s-Đúng\\ hướng{border-color:#1a7f37}.s-Có\\ rủi\\ ro{border-color:#9a6700}.s-Chậm{border-color:#b3261e}.sk.cu{border-style:dashed}
.tb{display:inline-block;width:140px;height:8px;background:#e5e5e5;border-radius:4px;vertical-align:middle;overflow:hidden;white-space:nowrap}
.tb i{display:inline-block;height:100%}.tb .x{background:#2a6fdb}.tb .d{background:repeating-linear-gradient(45deg,#2a6fdb 0 3px,#cfe0fb 3px 6px)}
details summary{margin-left:26px;cursor:pointer;color:#666;font-size:13px}.tong{font-size:13px;margin:4px 0}
@media(prefers-color-scheme:dark){body{background:#17181c;color:#e8e8ea}.h{border-color:#333}.muted{color:#aaa}.tb{background:#333}.v{border-color:#6ea0f5}}"""


def xuat(ten, phases, lan, now):
    nhom = {}
    for p in phases: nhom.setdefault(p["ten"].rsplit("-", 1)[0], []).append(p)
    mo = [p for p in phases if p["tt"] != XONG]
    d = {k: sum(p["d"][k] for p in mo) for k in (XONG, DANG, CHUA, HUY)}
    mau = d[XONG] + d[DANG] + d[CHUA]
    nl = dem_ngoai_le(phases)
    ngoai = " · ".join(f"{v} {k}" for k, v in nl.items() if v) or "không có ngoại lệ"
    body = [f'<div class="h"><div class="l1">{vong(DANG if mo else XONG, pct(d, mau) or 0)}<b>{html.escape(ten)}</b></div>'
            f'<div class="l2">{thanh(d, mau)} · {len(mo)} giai đoạn đang mở</div><div class="l2 tong">{ngoai}</div></div>']
    for m, ps in nhom.items():
        dm = {k: sum(p["d"][k] for p in ps if p["tt"] != XONG) for k in (XONG, DANG, CHUA, HUY)}
        mm = dm[XONG] + dm[DANG] + dm[CHUA]
        con = "".join(hang_phase(p, [l for l in lan if l.get("phase") == p["ten"]]) for p in ps)
        body.append(f'<div class="h"><div class="l1">{vong(DANG, pct(dm, mm) or 0)}<b>Module {m}</b></div>'
                    f'<div class="l2">{thanh(dm, mm)}</div><div class="con">{con}</div></div>')
    return (f'<!doctype html><html lang="vi"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>Tiến độ — {html.escape(ten)}</title><style>{CSS}</style><body>{"".join(body)}'
            f'<p class="muted">Cập nhật {now:%d/%m/%Y %H:%M}</p></body></html>')


def main(argv=None):
    a = argparse.ArgumentParser()
    a.add_argument("--repo-dir", required=True); a.add_argument("--ra", required=True)
    a.add_argument("--github"); a.add_argument("--lan"); a.add_argument("--ten")
    a.add_argument("--mui-gio", default="Asia/Ho_Chi_Minh")
    o = a.parse_args(argv)
    tz, repo = ZoneInfo(o.mui_gio), Path(o.repo_dir)
    now = dt.datetime.now(tz)
    pr_of = (lambda n: lay_pr(o.github, n)) if o.github else None
    cm_of = (lambda n: lay_comment(o.github, n)) if o.github else None
    lan = json.loads(Path(o.lan).read_text())["lan"] if o.lan else []
    phases = []
    for f in sorted((repo / "docs" / "phase").iterdir()):
        if FILE_PHASE.match(f.name):
            phases.append(tinh_phase(f.stem, f.read_text(), lich_su(repo, f"docs/phase/{f.name}", tz), now, pr_of, cm_of))
    Path(o.ra).write_text(xuat(o.ten or repo.resolve().name, phases, lan, now))
    return 0


if __name__ == "__main__":
    sys.exit(main())
