#!/usr/bin/env python3
"""Đo năm con số của luật (luat/phuong-phap.md mục 5 và 8) từ API GitHub. Chỉ đọc, chỉ gọi GET.

    GH_TOKEN=... python3 nghiem-thu/do_vong.py --repo chu/repo [--ngay 30] [--json]

Ra bảng Markdown để dán vào issue `xet-vong`. Số nào chưa đủ mẫu thì ghi «chưa đủ mẫu», không kết luận.
Giới hạn: mỗi danh sách chỉ đọc 100 mục mới nhất (bảng báo khi chạm trần). PR thuộc kỳ khi mở hoặc merge trong kỳ.
Hai PR chung một SHA thì lượt check của SHA đó tính cho cả hai.
Thời gian ra tính tới lúc merge: repo chưa có bước phát hành riêng.
"""
import argparse
import datetime
import json
import math
import os
import re
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cong import ten  # noqa: E402
from cong.gate_app import TOKEN_HOP_LE, GitHub, LoiApi  # noqa: E402

NANG = ("N1", "N2", "N3")
KHAU = ("dac-ta", "test", "phan-bac", "khong-phan-bac", "cong", "chay-that", "ngoai-tam")
MUC = ("thuong", "cao", "thap", "trung_binh")  # thap, trung_binh: PR trước 06/11, khi cổng còn ba mức
MUC_CU = ("thap", "trung_binh")  # bảng chỉ in khi kỳ còn PR mang mức này, ghi rõ là mức cũ
DU_MAU = {"loi_lot": 10, "ti_le_hong": 30, "thoi_gian_ra": 30, "do_dung": 30, "token": 30}
_MUC_TIEU_DE = re.compile(r"\((thuong|cao|thap|trung_binh)\)")
_GAY_LOI = re.compile(r"^pr-gay-loi:\s*#(\d+)\s*$", re.M)
_CHUA_RO = re.compile(r"^pr-gay-loi:\s*chưa rõ\s*$", re.M)
_HOAN_LAI = re.compile(r"^Reverts ([\w.-]+/[\w.-]+)#(\d+)\s*$", re.M)  # thân mặc định của nút Revert trên GitHub
_TOKEN = re.compile(r"^token-moi: (\d+)$", re.M)  # dòng do nghiem-thu/ghi_token.py ghi
_DAU_TOKEN = "<!-- token-may-ghi -->"
_USD = re.compile(r"^usd-quy-doi: (\d+\.\d+)$", re.M)  # luật L12, cũng do ghi_token.py ghi
TRAN_USD = 1e6  # một PR quá 1 triệu USD là số bị sửa tay, không phải số đo
_USD_MODEL = re.compile(r"^<!-- usd-model (\{.*\}) -->$", re.M)
_TIN = {"OWNER", "MEMBER", "COLLABORATOR"}  # repo công khai: ai cũng comment được
_CHUNG = "rủi ro cao"  # dòng lý do chung của mọi PR mức cao, không phải một luật


def _gio(chuoi):
    return datetime.datetime.fromisoformat(chuoi.replace("Z", "+00:00")) if chuoi else None


def doc_check(ds_check):
    """Các lượt check `cong-cuoi` của một PR -> (mức theo lượt mới nhất, nhóm lý do của mọi lượt chặn)."""
    if not ds_check:
        return None, []
    muc = None
    # Lượt `khong_xet (chua_ro)` không mang mức: lấy lượt mới nhất có mức.
    for c in sorted(ds_check, key=lambda c: c.get("completed_at") or ""):
        m = _MUC_TIEU_DE.search((c.get("output") or {}).get("title") or "")
        muc = m.group(1) if m else muc
    nhom = set()
    for c in ds_check:
        out = c.get("output") or {}
        if not (out.get("title") or "").startswith("chan"):
            continue
        trong = False  # chỉ đọc mục «Lý do»; «Chi tiết» là phân loại rủi ro, không phải luật đã chặn
        for dong in (out.get("summary") or "").splitlines():
            if dong.startswith("**"):
                trong = dong.startswith("**Lý do")
            elif trong and dong.startswith("- "):
                # Bỏ tên tệp trong dấu `…` và thay số bằng N để gom theo luật, không theo tệp hay cỡ.
                ly_do = re.sub(r"\d+", "N", re.sub(r"\s+", " ", re.sub(r"`[^`]*`", "·", dong[2:]))).rstrip(" ·:")
                if ly_do and not ly_do.startswith(_CHUNG):
                    nhom.add(ly_do)
    return muc, sorted(nhom)


def app_ghim(gh):
    """app_id mà bảo vệ nhánh gốc ghim cho check cổng cuối, None nếu chưa ghim.
    Chỉ check của App này là thật: check cùng tên do workflow hay App khác phát thì branch protection cũng không nhận."""
    bao_ve = (gh.goi("GET", "/branches/%s" % ten.NHANH_GOC) or {}).get("protection") or {}
    cac_id = {c.get("app_id") for c in (bao_ve.get("required_status_checks") or {}).get("checks") or []
              if c.get("context") == ten.CHECK_CUOI}
    cac_id -= {None, -1}  # -1 là «nguồn nào cũng được»: chưa ghim
    return cac_id.pop() if len(cac_id) == 1 else None


def loc_app(ds_check, app_id):
    """Giữ check do đúng App phát. Chưa biết App thì không tin check nào: số đo cổng để trống, không đoán."""
    return [c for c in ds_check if app_id is not None and (c.get("app") or {}).get("id") == app_id]


def _phan_loai(nhan):
    nang = [n for n in nhan if n in NANG]
    khau = [n[5:] for n in nhan if n.startswith("khau:")]
    return ("%s · %s" % (nang[0], khau[0])) if len(nang) == 1 and len(khau) == 1 and khau[0] in KHAU else None


def _than_token(ds_comment):
    """Thân comment `token-may-ghi` mới nhất của người trong repo, "" nếu chưa có."""
    hop = [c for c in ds_comment if _DAU_TOKEN in (c.get("body") or "") and c.get("author_association") in _TIN]
    return max(hop, key=lambda c: c.get("updated_at") or "")["body"] if hop else ""


def doc_token(ds_comment):
    """Token mới máy ghi cho một PR, None nếu chưa có."""
    m = _TOKEN.search(_than_token(ds_comment))
    return int(m.group(1)) if m else None


def doc_usd(ds_comment):
    """(USD quy đổi, {model: USD}) máy ghi cho một PR (luật L12), None nếu comment chưa có phần theo model.
    Comment người trong repo sửa tay được: số phải hữu hạn, trong khoảng 0..TRAN_USD; tên trùng sau làm sạch thì cộng."""
    than = _than_token(ds_comment)
    m, mm = _USD.search(than), _USD_MODEL.search(than)
    if not m:
        return None
    tong = float(m.group(1))
    if not 0 <= tong <= TRAN_USD:
        return None
    try:
        theo = json.loads(mm.group(1), parse_constant=_tu_choi) if mm else {}
    except ValueError:
        theo = {}
    kq = {}
    for k, v in (theo.items() if isinstance(theo, dict) else ()):
        if type(v) in (int, float) and 0 <= v <= TRAN_USD:
            ten = re.sub(r"[^a-z0-9.-]", "", str(k).lower())[:40]
            kq[ten] = kq.get(ten, 0.0) + float(v)
    return tong, kq


def _tu_choi(hang):
    raise ValueError(hang)


def _p90(so):
    return sorted(so)[math.ceil(0.9 * len(so)) - 1]


def tinh(ds_pr, ds_issue, nay, ngay, repo=None):
    """Hàm thuần. ds_pr: {so, mo, merge, muc, ly_do_chan, nhan, than, oan_tu_gan?, dong?, token?};
    ds_issue: {so, mo, nhan, than, la_pr?}; thời điểm ISO. PR thuộc kỳ khi mở HOẶC merge trong kỳ."""
    nay = _gio(nay)
    dau = nay - datetime.timedelta(days=ngay)
    trong = lambda t: t is not None and dau <= _gio(t) <= nay  # noqa: E731
    ds_pr = [p for p in ds_pr if trong(p["mo"]) or trong(p["merge"])]
    ds_issue = [i for i in ds_issue if trong(i["mo"])]
    merged = [p for p in ds_pr if trong(p["merge"])]

    loi = [i for i in ds_issue if "loi-lot" in i["nhan"] and not i.get("la_pr")]
    bang = {}
    for i in loi:
        o = _phan_loai(i["nhan"])
        if o:
            bang[o] = bang.get(o, 0) + 1
    loi_lot = {"so": len(loi), "tren_100_pr": round(100 * len(loi) / len(merged), 1) if merged else None,
               "bang": bang, "chua_phan_loai": sorted(i["so"] for i in loi if not _phan_loai(i["nhan"])),
               "du_mau": len(loi) >= DU_MAU["loi_lot"]}

    bay_ngay = datetime.timedelta(days=7)
    mau = [p for p in merged if _gio(p["merge"]) <= nay - bay_ngay]
    theo_so = {p["so"]: p for p in ds_pr if p["merge"]}
    trong_7 = lambda luc, so: so in theo_so and datetime.timedelta(0) <= _gio(luc) - _gio(theo_so[so]["merge"]) <= bay_ngay  # noqa: E731
    hong, khong_doc, theo_muc = set(), [], {}
    for i in loi:
        so_gay = [int(x) for x in _GAY_LOI.findall(i["than"] or "")]
        if len(so_gay) != 1 and not (not so_gay and _CHUA_RO.search(i["than"] or "")):
            khong_doc.append(i["so"])  # thiếu, viết lệch hoặc nhiều dòng: không đoán, liệt kê để người sửa
        muc = theo_so[so_gay[0]]["muc"] if len(so_gay) == 1 and so_gay[0] in theo_so else None
        theo_muc[muc or "chưa rõ"] = theo_muc.get(muc or "chưa rõ", 0) + 1
        if len(so_gay) == 1 and trong_7(i["mo"], so_gay[0]):
            hong.add(so_gay[0])
    for p in merged:
        for ten_repo, so in _HOAN_LAI.findall(p["than"] or ""):
            if (repo is None or ten_repo.lower() == repo.lower()) and trong_7(p["merge"], int(so)):
                hong.add(int(so))
    hong &= {p["so"] for p in mau}
    loi_lot["theo_muc_pr"] = theo_muc
    ti_le_hong = {"so_pr": len(mau), "gay_hong": sorted(hong), "ti_le": round(len(hong) / len(mau), 2) if mau else None,
                  "khong_doc_duoc": sorted(khong_doc), "du_mau": len(mau) >= DU_MAU["ti_le_hong"]}

    thoi_gian_ra = {}
    for muc in MUC + ("chua_ro",):
        gio = [(_gio(p["merge"]) - _gio(p["mo"])).total_seconds() / 3600 for p in merged if (p["muc"] or "chua_ro") == muc]
        if gio:
            thoi_gian_ra[muc] = {"so": len(gio), "trung_vi_gio": round(statistics.median(gio), 1),
                                 "p90_gio": round(_p90(gio), 1), "du_mau": len(gio) >= DU_MAU["thoi_gian_ra"]}

    do_dung = {}
    for p in ds_pr:
        for ly_do in p["ly_do_chan"]:
            o = do_dung.setdefault(ly_do, {"so_chan": 0, "so_oan": 0})
            o["so_chan"] += 1
            o["so_oan"] += "chan-oan" in p["nhan"] and not p.get("oan_tu_gan")
    for o in do_dung.values():
        o["do_dung"] = round(1 - o["so_oan"] / o["so_chan"], 2)
        o["du_mau"] = o["so_chan"] >= DU_MAU["do_dung"]

    # Token: trung vị theo PR đã merge, và bình quân tính cả PR bị bỏ (đóng không merge) chia cho số PR merge.
    co = [p for p in merged if p.get("token") is not None]
    bo = [p for p in ds_pr if p.get("dong") and not p["merge"] and p.get("token") is not None]
    token = {"co_ghi": len(co), "so_merge": len(merged), "thieu": sorted(p["so"] for p in merged if p.get("token") is None),
             "trung_vi": round(statistics.median(p["token"] for p in co)) if co else None,
             "binh_quan_ca_bo": round(sum(p["token"] for p in co + bo) / len(co)) if co else None,
             "so_bo": len(bo), "du_mau": len(co) >= DU_MAU["token"]}
    # Chi phí quy đổi theo model (luật L12): trung vị USD mỗi PR merge và tỉ trọng từng model trong kỳ.
    co_usd = [p for p in merged if p.get("usd")]
    theo_model = {}
    for p in co_usd:
        for m, u in p["usd"][1].items():
            theo_model[m] = theo_model.get(m, 0) + u
    tong_usd = sum(theo_model.values())
    token.update(usd_co_ghi=len(co_usd), usd_du_mau=len(co_usd) >= DU_MAU["token"],
                 usd_trung_vi=round(statistics.median(p["usd"][0] for p in co_usd), 2) if co_usd else None,
                 usd_ti_trong={m: round(u / tong_usd, 2) for m, u in theo_model.items()} if tong_usd else {})

    return {"ky": [dau.date().isoformat(), nay.date().isoformat()], "so_pr": len(ds_pr), "so_merged": len(merged),
            "loi_lot": loi_lot, "bat_truoc_merge": sum("bat-truoc-merge" in i["nhan"] for i in ds_issue),
            "ti_le_hong": ti_le_hong, "thoi_gian_ra": thoi_gian_ra, "token": token, "do_dung": do_dung,
            "oan_tu_gan": sorted(p["so"] for p in ds_pr if p.get("oan_tu_gan"))}


def _mau(o):
    return "" if o["du_mau"] else " · chưa đủ mẫu"


def bang(k):
    """Bảng Markdown cho issue `xet-vong`."""
    ll, th = k["loi_lot"], k["ti_le_hong"]
    d = ["## Năm con số · %s → %s" % tuple(k["ky"]), "",
         "PR mở hoặc merge trong kỳ: %d · merge trong kỳ: %d · lỗi bắt trước merge: %d" % (k["so_pr"], k["so_merged"], k["bat_truoc_merge"]), "",
         "| Số | Giá trị |", "|---|---|",
         "| Lỗi lọt | %d lỗi, %s trên 100 PR%s |" % (ll["so"], "-" if ll["tren_100_pr"] is None else ll["tren_100_pr"], _mau(ll)),
         "| Tỉ lệ thay đổi gây hỏng | %s (%d / %d PR đủ 7 ngày)%s |" % (
             "-" if th["ti_le"] is None else "%d%%" % round(100 * th["ti_le"]), len(th["gay_hong"]), th["so_pr"], _mau(th))]
    for muc in MUC + ("chua_ro",):
        o = k["thoi_gian_ra"].get(muc)
        if muc in MUC_CU + ("chua_ro",) and not o:
            continue
        d.append("| Thời gian ra · %s | %s |" % (muc + (" (mức cũ, trước 06/11)" if muc in MUC_CU else ""), "không có PR" if not o else "trung vị %s giờ, 1/10 chậm nhất %s giờ, %d PR%s" % (
            o["trung_vi_gio"], o["p90_gio"], o["so"], _mau(o))))
    tk = k["token"]
    d.append("| Token mỗi PR đã merge | %s |" % (
        "chưa đo: 0 / %d PR merge có comment `token-may-ghi`" % tk["so_merge"] if not tk["co_ghi"] else
        "trung vị %d token mới, bình quân %d khi tính cả %d PR bị bỏ, %d / %d PR merge có số máy ghi%s" % (
            tk["trung_vi"], tk["binh_quan_ca_bo"], tk["so_bo"], tk["co_ghi"], tk["so_merge"], _mau(tk))))
    if tk.get("usd_co_ghi"):
        d.append("| USD quy đổi mỗi PR đã merge (L12) | trung vị %.2f, %d / %d PR merge có số theo model%s; tỉ trọng: %s |" % (
            tk["usd_trung_vi"], tk["usd_co_ghi"], tk["so_merge"], _mau({"du_mau": tk["usd_du_mau"]}),
            ", ".join("%s %d%%" % (m, round(100 * t)) for m, t in sorted(tk["usd_ti_trong"].items(), key=lambda x: -x[1]))))
    d += ["", "**Lỗi lọt theo mức nặng · khâu lẽ ra chặn**", ""]
    d += ["- %s: %d" % (o, n) for o, n in sorted(ll["bang"].items())] or ["- chưa có"]
    if ll["chua_phan_loai"]:
        d.append("- chưa phân loại (thiếu nhãn N1-N3 hoặc `khau:`): " + ", ".join("#%d" % s for s in ll["chua_phan_loai"]))
    if ll["theo_muc_pr"]:
        d.append("- theo mức rủi ro của PR gây lỗi: " + ", ".join("%s %d" % x for x in sorted(ll["theo_muc_pr"].items())))
    if th["khong_doc_duoc"]:
        d.append("- không đọc được dòng `pr-gay-loi: #N | chưa rõ`, tỉ lệ hỏng có thể thiếu: "
                 + ", ".join("#%d" % s for s in th["khong_doc_duoc"]))
    if tk["co_ghi"] and tk["thieu"]:
        d += ["", "**PR merge chưa có token máy ghi** (không vào trung vị): " + ", ".join("#%d" % s for s in tk["thieu"])]
    d += ["", "**Độ đúng của cổng theo lý do chặn** (chặn oan = PR có nhãn `chan-oan`)", ""]
    d += ["- %s: %d lần chặn, %d oan, đúng %d%%%s" % (ly, o["so_chan"], o["so_oan"], round(100 * o["do_dung"]), _mau(o))
          for ly, o in sorted(k["do_dung"].items())] or ["- chưa có lần chặn"]
    if k["oan_tu_gan"]:
        d.append("- nhãn `chan-oan` do tác giả PR tự gắn, không tính: " + ", ".join("#%d" % s for s in k["oan_tu_gan"]))
    if "app_cong" in k and k["app_cong"] is None:
        d += ["", "**Cảnh báo:** nhánh %s chưa ghim App cho `%s` và không có `--app-id`: không tin check nào, "
              "mức rủi ro và độ đúng của cổng để trống." % (ten.NHANH_GOC, ten.CHECK_CUOI)]
    if k.get("cham_tran"):
        d += ["", "**Cảnh báo:** danh sách chạm trần 100 mục, số có thể thiếu: " + ", ".join(k["cham_tran"])]
    return "\n".join(d)


def thu_thap(gh, ngay, nay, app_id):
    dau = (_gio(nay) - datetime.timedelta(days=ngay)).strftime("%Y-%m-%dT%H:%M:%SZ")
    tran = []
    # Sắp theo lần cập nhật: PR mở trước kỳ mà merge trong kỳ vẫn lọt vào trang đầu.
    ds = gh.goi("GET", "/pulls?state=all&base=%s&sort=updated&direction=desc&per_page=100" % ten.NHANH_GOC)
    if len(ds) == 100:
        tran.append("PR")
    ds_pr = []
    for p in ds:
        if p["created_at"] < dau and (p.get("merged_at") or "") < dau:
            continue
        # Check gắn với SHA: đọc mọi commit của PR, không chỉ đầu nhánh.
        cac_sha = [c["sha"] for c in gh.goi("GET", "/pulls/%d/commits?per_page=100" % p["number"])] or [p["head"]["sha"]]
        check = []
        for sha in cac_sha:
            check += gh.goi("GET", "/commits/%s/check-runs?check_name=%s&filter=all&per_page=100" % (sha, ten.CHECK_CUOI))["check_runs"]
        muc, ly_do = doc_check(loc_app(check, app_id))
        nhan = [n["name"] for n in p.get("labels") or []]
        oan_tu_gan = False
        if "chan-oan" in nhan:
            gan = [e for e in gh.goi("GET", "/issues/%d/events?per_page=100" % p["number"])
                   if e.get("event") == "labeled" and (e.get("label") or {}).get("name") == "chan-oan"]
            oan_tu_gan = not gan or (gan[-1].get("actor") or {}).get("login") == (p.get("user") or {}).get("login")
        ds_comment = gh.goi("GET", "/issues/%d/comments?per_page=100" % p["number"])
        token, usd = doc_token(ds_comment), doc_usd(ds_comment)
        ds_pr.append({"so": p["number"], "mo": p["created_at"], "merge": p.get("merged_at"), "muc": muc, "ly_do_chan": ly_do,
                      "nhan": nhan, "than": p.get("body") or "", "oan_tu_gan": oan_tu_gan,
                      "dong": p.get("state") == "closed", "token": token, "usd": usd})
    ds_issue = []
    for nhan in ("loi-lot", "bat-truoc-merge"):
        ds = gh.goi("GET", "/issues?labels=%s&state=all&since=%s&per_page=100" % (nhan, dau))
        if len(ds) == 100:
            tran.append(nhan)
        ds_issue += [{"so": i["number"], "mo": i["created_at"], "nhan": [n["name"] for n in i.get("labels") or []],
                      "than": i.get("body") or "", "la_pr": "pull_request" in i}
                     for i in ds if "pull_request" not in i or nhan == "bat-truoc-merge"]
    # Một mục mang cả hai nhãn chỉ tính một lần.
    return ds_pr, list({i["so"]: i for i in ds_issue}.values()), tran


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", required=True)
    ap.add_argument("--ngay", type=int, default=30)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--app-id", type=int, help="App phát check cổng; mặc định đọc từ bảo vệ nhánh gốc")
    a = ap.parse_args(argv)
    token = (os.environ.get("GH_TOKEN") or "").strip()
    if not TOKEN_HOP_LE.fullmatch(token):  # không in giá trị
        print("Thiếu biến GH_TOKEN hoặc token có ký tự lạ.", file=sys.stderr)
        return 2
    gh = GitHub(a.repo, token)
    nay = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        app_id = a.app_id or app_ghim(gh)
        ds_pr, ds_issue, tran = thu_thap(gh, a.ngay, nay, app_id)
    except LoiApi as loi:
        print(gh.che(str(loi)), file=sys.stderr)
        return 1
    k = dict(tinh(ds_pr, ds_issue, nay, a.ngay, repo=a.repo), cham_tran=tran, app_cong=app_id)
    print(json.dumps(k, ensure_ascii=False, indent=1) if a.json else bang(k))
    return 0


if __name__ == "__main__":
    sys.exit(main())
