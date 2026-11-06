#!/usr/bin/env python3
"""Máy ghi token của một PR từ bản ghi phiên Claude Code và Codex vào một comment của PR (luật mục 4 và 8.3).

    GH_TOKEN=$(gh auth token) python3 nghiem-thu/ghi_token.py --repo chu/repo [--pr N] [--kho]

Chạy sau khi đẩy commit cuối, và một lần nữa ngay trước khi merge. Không có --pr thì lấy PR của nhánh đang mở.
Đọc các tệp .jsonl dưới ~/.claude/projects có nhắc đường dẫn repo, chỉ lấy lượt gọi model có cwd nằm trong repo
(kể cả worktree trong repo) và gitBranch là nhánh của PR. Một lượt gọi chỉ tính một lần theo cặp
(message.id, requestId), vì bản ghi chép một lượt gọi thành nhiều dòng.
Lượt gọi ở nhánh gốc hay HEAD rời được tính cho nhánh kế tiếp mà cùng phiên chuyển sang: đó là việc làm trước
khi tạo nhánh. Bảng ghi riêng phần này.
Token mới = input + cache_creation + output. Đọc lại bộ nhớ đệm (cache_read) ghi riêng, không cộng.
Codex: đọc ~/.codex/sessions, mỗi bản ghi token_usage_record một lần theo response_id; token mới = input − cached_input
+ output (input của Codex đã gồm phần đọc đệm, output đã gồm reasoning). Codex chỉ ghi nhánh lúc mở phiên, nên cả phiên
tính cho nhánh đó; cwd lấy theo turn_context của từng lượt. Dòng Codex mang tên "<máy> codex".
Tên nhánh dùng lại: chỉ tính lượt gọi sau lúc PR trước cùng tên nhánh đóng (mốc ghi trong comment).
Mỗi máy một dòng: chạy ở máy khác thì thêm dòng của máy đó, dòng các máy khác giữ nguyên.
Theo model (luật L12): mỗi lượt Claude Code ghi thêm model và bốn loại token, quy ra USD theo bảng GIA; tài khoản
gói tháng không trả đúng số này, số chỉ để so model với nhau. Model không có trong bảng ghi "chưa có giá", không quy USD.
Giới hạn: việc ở nhánh gốc sau khi merge PR trước (dọn, kiểm) bị tính cho PR kế tiếp của phiên; việc ở nhánh gốc
sau nhánh cuối của phiên không tính cho PR nào; phiên Codex đổi nhánh giữa chừng
vẫn tính cho nhánh lúc mở; lượt tóm tắt ngữ cảnh chưa tính; người có quyền ghi vẫn sửa tay được comment.
"""
import argparse
import datetime
import json
import os
import platform
import re
import subprocess
import sys
import time
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cong.gate_app import TOKEN_HOP_LE, GitHub, LoiApi  # noqa: E402

DAU = "<!-- token-may-ghi -->"
TOKEN_MOI = re.compile(r"^token-moi: (\d+)$", re.M)  # do_vong.py đọc dòng này
_DU_LIEU = re.compile(r"^<!-- du-lieu (\{.*\}) -->$", re.M)
_TEN_MAY = re.compile(r"[^\w .-]")
TIN = {"OWNER", "MEMBER", "COLLABORATOR"}  # repo công khai: ai cũng comment được, chỉ tin người trong repo
_SO = ("phien", "luot", "moi", "doc_dem", "moi_truoc")
USD = re.compile(r"^usd-quy-doi: (\d+\.\d+)$", re.M)  # do_vong.py đọc dòng này
_USD_MODEL = re.compile(r"^<!-- usd-model (\{.*\}) -->$", re.M)
# $ cho 1 triệu token: (vào, ra, đọc lại bộ đệm). Ghi bộ đệm 5 phút = 1,25 × vào, 1 giờ = 2 × vào.
# Nguồn: tài liệu giá Anthropic qua skill claude-api, kiểm 06/11/2026. Haiku 5.5: bậc lời nhắc ≤ 100 nghìn token.
GIA_NGAY = "2026-11-06"
GIA = {"claude-fable-5-1": (10, 50, 0.25), "claude-fable-5": (10, 50, 1.0), "claude-opus-5-5": (4, 20, 0.20),
       "claude-opus-5": (5, 25, 0.5), "claude-opus-4-8": (5, 25, 0.5), "claude-sonnet-5-5": (2, 10, 0.20),
       "claude-sonnet-5": (2, 10, 0.20), "claude-haiku-5-5": (0.10, 0.50, 0.01)}
TRAN_SO = 10 ** 13  # trần mỗi số theo model đọc lại từ comment (sửa tay được): đủ lớn cho số thật, đủ nhỏ để đổi ra float
_LOAI = ("luot", "vao", "ghi_5m", "ghi_1h", "ra", "doc")


def cac_tep(goc_repo, nha=None, tu_luc=0.0):
    """Tệp .jsonl sửa từ tu_luc (giây epoch) có nhắc đường dẫn repo. Quét mọi thư mục dự án, vì phiên mở ở
    thư mục khác rồi mới chuyển vào repo thì bản ghi nằm dưới thư mục mở ban đầu."""
    cha = Path(nha or Path.home() / ".claude" / "projects")
    dau = str(goc_repo).encode()
    kq = []
    for t in sorted(cha.rglob("*.jsonl")) if cha.is_dir() else []:
        try:
            if t.stat().st_mtime >= tu_luc and dau in t.read_bytes():
                kq.append(t)
        except OSError:
            continue
    return kq


def _luot_goi(cac_tep, goc):
    """Mỗi lượt gọi model trong repo đúng một lần: (phiên, lúc, nhánh, token mới, đọc đệm, chi tiết).
    Chi tiết = (model, vào, ghi đệm 5 phút, ghi đệm 1 giờ, ra); thiếu phần tách ghi đệm thì tính cả là 5 phút."""
    da_tinh, kq = set(), []
    for tep in cac_tep:
        with open(tep, encoding="utf-8", errors="replace") as f:
            for dong in f:
                try:
                    e = json.loads(dong)
                except ValueError:
                    continue
                if not isinstance(e, dict) or e.get("type") != "assistant":
                    continue
                cwd, nhanh, tin, luc = e.get("cwd"), e.get("gitBranch"), e.get("message"), e.get("timestamp")
                if not isinstance(cwd, str) or not (cwd == goc or cwd.startswith(goc + "/")):
                    continue
                if not (isinstance(nhanh, str) and nhanh and isinstance(tin, dict) and isinstance(luc, str)):
                    continue
                u = tin.get("usage")
                khoa = (tin.get("id"), e.get("requestId"))
                if not isinstance(u, dict) or None in khoa or khoa in da_tinh:
                    continue
                da_tinh.add(khoa)
                so = lambda k, d=u: d.get(k) if isinstance(d.get(k), int) and d.get(k) >= 0 else 0  # noqa: E731
                ghi = so("cache_creation_input_tokens")
                tach = u.get("cache_creation") if isinstance(u.get("cache_creation"), dict) else {}
                ghi_1h = min(so("ephemeral_1h_input_tokens", tach), ghi)
                model = tin.get("model") if isinstance(tin.get("model"), str) else ""
                kq.append((str(e.get("sessionId")), luc, nhanh,
                           so("input_tokens") + ghi + so("output_tokens"), so("cache_read_input_tokens"),
                           (_ten_model(model), so("input_tokens"), ghi - ghi_1h, ghi_1h, so("output_tokens"))))
    return kq


def _luot_goi_codex(cac_tep, goc):
    """Mỗi lượt gọi model của Codex trong repo đúng một lần: (phiên, lúc, nhánh, token mới, đọc đệm)."""
    da_tinh, kq = set(), []
    for tep in cac_tep:
        phien, nhanh, cwd_luot = None, None, {}
        with open(tep, encoding="utf-8", errors="replace") as f:
            for dong in f:
                try:
                    e = json.loads(dong)
                except ValueError:
                    continue
                p = e.get("payload") if isinstance(e, dict) else None
                if not isinstance(p, dict):
                    continue
                loai = e.get("type")
                if loai == "session_meta":
                    g = p.get("git")
                    phien = p.get("session_id") or p.get("id")
                    nhanh = g.get("branch") if isinstance(g, dict) else None
                elif loai == "turn_context":
                    cwd_luot[p.get("turn_id")] = p.get("cwd")
                elif loai == "token_usage_record":
                    cwd, u, khoa, luc = cwd_luot.get(p.get("turn_id")), p.get("usage"), p.get("response_id"), e.get("timestamp")
                    if not isinstance(cwd, str) or not (cwd == goc or cwd.startswith(goc + "/")):
                        continue
                    if not (isinstance(nhanh, str) and nhanh and isinstance(u, dict) and isinstance(luc, str)):
                        continue
                    if not isinstance(khoa, str) or khoa in da_tinh:
                        continue
                    da_tinh.add(khoa)
                    so = lambda k: u.get(k) if isinstance(u.get(k), int) and u.get(k) >= 0 else 0  # noqa: E731
                    doc = min(so("cached_input_tokens"), so("input_tokens"))
                    kq.append((str(p.get("session_id") or phien), luc, nhanh,
                               so("input_tokens") - doc + so("output_tokens"), doc))
    return kq


def _ten_model(model):
    """Tên model gọn, an toàn để in vào bảng: bỏ hậu tố như `[1m]`, chỉ giữ chữ, số, gạch."""
    return re.sub(r"[^a-z0-9.-]", "", model.split("[")[0].lower())[:40] or "khong-ro"


def chi_phi(model, so):
    """USD quy đổi của một model theo bảng GIA; None nếu model chưa có giá."""
    g = GIA.get(model)
    if not g:
        return None
    vao, ra, doc = g
    return (so["vao"] * vao + so["ghi_5m"] * 1.25 * vao + so["ghi_1h"] * 2 * vao + so["ra"] * ra + so["doc"] * doc) / 1e6


def cong_theo_nhanh(cac_tep, goc_repo, nhanh_goc=("main",), doc_luot=_luot_goi, sau_luc=None, theo_model=False):
    """{nhánh: {phien, luot, moi, doc_dem, moi_truoc}}. Lượt gọi ở nhánh gốc hay HEAD rời được tính cho nhánh
    kế tiếp mà cùng phiên chuyển sang (việc làm trước khi tạo nhánh); moi_truoc là phần đó.
    Lượt ở nhánh gốc sau nhánh cuối của phiên không tính cho nhánh nào. doc_luot=_luot_goi_codex cho Codex.
    sau_luc (ISO 8601, UTC): bỏ lượt gọi từ lúc đó trở về trước, so tới giây.
    theo_model=True: thêm khoá "model" = {model: {luot, vao, ghi_5m, ghi_1h, ra, doc}} cho lượt có chi tiết."""
    goc_cung = set(nhanh_goc) | {"HEAD"}
    theo_phien = {}
    for l in doc_luot(cac_tep, str(goc_repo).rstrip("/")):
        if sau_luc and l[1][:19] <= sau_luc[:19]:
            continue
        theo_phien.setdefault(l[0], []).append(l)
    kq = {}
    for phien, ds in theo_phien.items():
        ke_tiep = None
        for l in sorted(ds, key=lambda l: l[1], reverse=True):
            nhanh, moi, doc_dem = l[2], l[3], l[4]
            truoc = nhanh in goc_cung
            if not truoc:
                ke_tiep = nhanh
            if ke_tiep is None:
                continue
            o = kq.setdefault(ke_tiep, {"phien": set(), "luot": 0, "moi": 0, "doc_dem": 0, "moi_truoc": 0})
            o["phien"].add(phien)
            o["luot"] += 1
            o["moi"] += moi
            o["doc_dem"] += doc_dem
            o["moi_truoc"] += moi if truoc else 0
            if theo_model and len(l) > 5:
                m = o.setdefault("model", {}).setdefault(l[5][0], dict.fromkeys(_LOAI, 0))
                for k, v in zip(_LOAI, (1, *l[5][1:], doc_dem)):
                    m[k] += v
    for o in kq.values():
        o["phien"] = len(o["phien"])
    return kq


def doc_comment(than):
    """Dữ liệu theo máy trong một comment cũ; hỏng thì coi như rỗng."""
    m = _DU_LIEU.search(than or "")
    try:
        d = json.loads(m.group(1)) if m else {}
    except ValueError:
        return {}
    if not isinstance(d, dict):
        return {}
    kq = {}
    for k, v in d.items():
        if not (isinstance(v, dict) and all(type(v.get(s)) is int for s in _SO)):
            continue
        o = kq[_TEN_MAY.sub("", str(k))[:60]] = dict({s: v[s] for s in _SO}, luc=re.sub(r"[^\d :-]", "", str(v.get("luc", "")))[:16])
        theo = v.get("model")
        if isinstance(theo, dict):
            gom = o["model"] = {}
            for m, so in theo.items():
                if isinstance(so, dict) and all(type(so.get(s)) is int and 0 <= so[s] <= TRAN_SO for s in _LOAI):
                    g = gom.setdefault(_ten_model(str(m)), dict.fromkeys(_LOAI, 0))
                    for s in _LOAI:
                        g[s] += so[s]
    return kq


def bang_model(theo_may):
    """Dòng bảng theo model (cộng mọi máy), dòng `usd-quy-doi` và dữ liệu USD theo model; rỗng nếu không máy nào có."""
    tong = {}
    for v in theo_may.values():
        for m, so in (v.get("model") or {}).items():
            o = tong.setdefault(m, dict.fromkeys(_LOAI, 0))
            for k in _LOAI:
                o[k] += so[k]
    if not tong:
        return []
    usd = {m: chi_phi(m, so) for m, so in tong.items()}
    d = ["", "**Theo model** · USD quy đổi theo giá API ngày %s (gói tháng không trả đúng số này)" % GIA_NGAY, "",
         "| Model | Lượt gọi | Token mới | Đọc lại bộ đệm | USD quy đổi |", "|---|---|---|---|---|"]
    for m, so in sorted(tong.items(), key=lambda x: -(usd[x[0]] or 0)):
        d.append("| %s | %d | %d | %d | %s |" % (m, so["luot"], so["vao"] + so["ghi_5m"] + so["ghi_1h"] + so["ra"],
                                              so["doc"], "chưa có giá" if usd[m] is None else "%.2f" % usd[m]))
    co_gia = {m: round(u, 4) for m, u in usd.items() if u is not None}
    return d + ["", "usd-quy-doi: %.4f" % sum(co_gia.values()),
                "<!-- usd-model %s -->" % json.dumps(co_gia, ensure_ascii=True, sort_keys=True)]


def than_comment(nhanh, theo_may, moc=None):
    tong = {s: sum(v[s] for v in theo_may.values()) for s in _SO}
    d = [DAU, "**Token máy ghi** cho nhánh `%s`: đọc từ bản ghi phiên Claude Code và Codex, không do agent tự báo. "
         "Cách ghi: `nghiem-thu/ghi_token.py`." % re.sub(r"[^\w./-]", "", nhanh), "",
         "| Máy | Phiên | Lượt gọi | Token mới | trong đó trước khi tạo nhánh | Đọc lại bộ đệm | Lúc ghi |",
         "|---|---|---|---|---|---|---|"]
    for may, v in sorted(theo_may.items()):
        d.append("| %s | %d | %d | %d | %d | %d | %s |" % (
            may, v["phien"], v["luot"], v["moi"], v["moi_truoc"], v["doc_dem"], v.get("luc", "")))
    if moc:
        d += ["", "Chỉ tính lượt gọi sau %s UTC, lúc PR #%d cùng tên nhánh đóng." % (
            re.sub(r"[^\d:-]", " ", moc[1][:19]), moc[0])]
    d += bang_model(theo_may)
    d += ["", "token-moi: %d" % tong["moi"], "",
          "<!-- du-lieu %s -->" % json.dumps(theo_may, ensure_ascii=True, sort_keys=True)]
    return "\n".join(d)


def comment_cu(ds):
    """Comment máy ghi mới nhất của người trong repo, None nếu chưa có."""
    hop = [c for c in ds if DAU in (c.get("body") or "") and c.get("author_association") in TIN]
    return max(hop, key=lambda c: c.get("updated_at") or "") if hop else None


def _git(goc, *lenh):
    return subprocess.run(["git", "-C", str(goc), *lenh], capture_output=True, text=True, check=True).stdout.strip()


def tim_pr(gh, repo, so_pr, nhanh_dang_mo):
    if so_pr:
        p = gh.goi("GET", "/pulls/%d" % so_pr)
    else:
        ds = gh.goi("GET", _hoi_nhanh(repo, nhanh_dang_mo))
        if not ds:
            raise LoiApi("nhánh %s chưa có PR" % nhanh_dang_mo)
        p = max(ds, key=lambda x: x.get("created_at") or "")
    if ((p.get("head") or {}).get("repo") or {}).get("full_name", "").lower() != repo.lower():
        raise LoiApi("PR %d mở từ repo khác: bản ghi máy này không ứng với nhánh đó" % p["number"])
    return p["number"], p["head"]["ref"], p["base"]["ref"]


def _hoi_nhanh(repo, nhanh):
    """Đường hỏi các PR của một nhánh; tên nhánh được mã hoá để `#`, `&`, `+` không cắt hay đổi câu hỏi."""
    return "/pulls?state=all&head=%s:%s&per_page=100" % (
        urllib.parse.quote(repo.split("/")[0], safe=""), urllib.parse.quote(nhanh, safe="/"))


def moc_dung_lai(gh, repo, so_pr, nhanh):
    """(số PR, lúc đóng) của PR trước mới nhất đã đóng mà cùng tên nhánh, None nếu nhánh chưa từng dùng.
    PR số nhỏ hơn là PR mở trước. Chỉ nhận PR đóng trước lúc PR này được tạo: PR cùng nhánh mở song song
    mà đóng sau thì không được cắt mất lượt gọi của PR này."""
    ds = [p for p in (gh.goi("GET", _hoi_nhanh(repo, nhanh)) or []) if isinstance(p, dict)]
    tao = next((p.get("created_at") for p in ds if p.get("number") == so_pr and type(p.get("number")) is int), None)
    tao = tao if isinstance(tao, str) and tao else None
    cu = [(p["number"], p["closed_at"]) for p in ds if type(p.get("number")) is int
          and p["number"] < so_pr and isinstance(p.get("closed_at"), str) and p["closed_at"]
          and (tao is None or p["closed_at"][:19] <= tao[:19])]
    return max(cu, key=lambda x: x[1]) if cu else None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", required=True)
    ap.add_argument("--pr", type=int)
    ap.add_argument("--goc", help="gốc repo trên đĩa; mặc định repo chứa thư mục đang đứng")
    ap.add_argument("--ban-ghi", help="thư mục chứa các thư mục bản ghi; mặc định ~/.claude/projects")
    ap.add_argument("--ban-ghi-codex", help="thư mục bản ghi Codex; mặc định ~/.codex/sessions")
    ap.add_argument("--ngay", type=int, default=30, help="chỉ đọc bản ghi sửa trong ngần này ngày")
    ap.add_argument("--kho", action="store_true", help="chỉ in comment, không ghi lên GitHub")
    a = ap.parse_args(argv)
    token = (os.environ.get("GH_TOKEN") or "").strip()
    if not TOKEN_HOP_LE.fullmatch(token):  # không in giá trị
        print("Thiếu biến GH_TOKEN hoặc token có ký tự lạ.", file=sys.stderr)
        return 2
    gh = GitHub(a.repo, token)
    try:
        # Gốc của bản làm việc chính, để tính cả worktree nằm trong repo.
        goc = Path(a.goc or Path(_git(Path.cwd(), "rev-parse", "--path-format=absolute", "--git-common-dir")).parent).resolve()
        so_pr, nhanh, nhanh_goc = tim_pr(gh, a.repo, a.pr, None if a.pr else _git(Path.cwd(), "rev-parse", "--abbrev-ref", "HEAD"))
        tu_luc = time.time() - a.ngay * 86400
        moc = moc_dung_lai(gh, a.repo, so_pr, nhanh)
        sau = moc[1] if moc else None
        moi = cong_theo_nhanh(cac_tep(goc, a.ban_ghi, tu_luc), goc, (nhanh_goc,), sau_luc=sau, theo_model=True).get(nhanh)
        tep_codex = cac_tep(goc, a.ban_ghi_codex or Path.home() / ".codex" / "sessions", tu_luc)
        moi_codex = cong_theo_nhanh(tep_codex, goc, (nhanh_goc,), _luot_goi_codex, sau).get(nhanh)
        ds = gh.goi("GET", "/issues/%d/comments?per_page=100" % so_pr)
        cu = comment_cu(ds)
        theo_may = doc_comment(cu["body"]) if cu else {}
        may = _TEN_MAY.sub("", platform.node())[:60] or "may-khong-ten"
        luc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")
        for ten, so in ((may, moi), (may + " codex", moi_codex)):
            if so:
                theo_may[ten] = dict(so, luc=luc)
        if not theo_may:
            print("Máy này không có lượt gọi nào trên nhánh %s; không ghi." % nhanh, file=sys.stderr)
            return 1
        than = than_comment(nhanh, theo_may, moc)
        if a.kho:
            print(than)
            return 0
        try:
            if not cu:
                raise LoiApi("chưa có comment", 404)
            gh.goi("PATCH", "/issues/comments/%d" % cu["id"], {"body": than})
        except LoiApi as loi:
            if loi.ma not in (403, 404):
                raise
            gh.goi("POST", "/issues/%d/comments" % so_pr, {"body": than})  # comment của người khác: ghi comment mới
    except (LoiApi, subprocess.CalledProcessError, OSError) as loi:
        print(gh.che(str(loi)), file=sys.stderr)
        return 1
    print("PR %d · nhánh %s · token mới %s" % (so_pr, nhanh, TOKEN_MOI.search(than).group(1)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
