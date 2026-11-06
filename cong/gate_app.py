"""Đọc PR qua REST, xét bằng kiem_pr, phát MỘT check run `cong-cuoi`.

Token App nhận qua biến môi trường, không bao giờ in. Mọi đường hỏng đều không phát `success`.
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from . import kiem_pr, rui_ro, ten

API_GOC = "https://api.github.com"
# Token chỉ gồm ký tự in được, không khoảng trắng. Ký tự lạ (vd xuống dòng cuối khi dán) làm http.client
# ném ValueError có in nguyên header Authorization, tức in token: chặn trước khi gửi.
TOKEN_HOP_LE = re.compile(r"[\x21-\x7e]+")
_GIOI_HAN_TOM_TAT = 60000
_QUYEN_GHI = {"admin", "maintain", "write"}


class LoiApi(Exception):
    def __init__(self, thong_bao, ma=None, than=""):
        super().__init__(thong_bao)
        self.ma, self.than = ma, than


class _KhongChuyenHuong(urllib.request.HTTPRedirectHandler):
    """urllib giữ nguyên Authorization khi chuyển hướng: không đi theo, để khỏi lộ token."""
    def redirect_request(self, *a, **k):
        return None


class GitHub:
    def __init__(self, repo, token, goc=API_GOC):
        if not goc.startswith("https://"):
            raise LoiApi("API phải dùng https")
        if not TOKEN_HOP_LE.fullmatch(token or ""):
            raise LoiApi("token rỗng hoặc có ký tự lạ")  # không kèm giá trị
        self.goc_repo = "%s/repos/%s" % (goc.rstrip("/"), repo)
        self.token = token
        self._mo = urllib.request.build_opener(_KhongChuyenHuong).open

    def che(self, chuoi):
        return chuoi.replace(self.token, "***") if self.token else chuoi

    def goi(self, phuong_thuc, duong, body=None):
        """duong bắt đầu bằng / và nối sau /repos/<repo>."""
        yeu_cau = urllib.request.Request(
            self.goc_repo + duong, method=phuong_thuc,
            data=None if body is None else json.dumps(body).encode(),
            headers={"Authorization": "Bearer " + self.token, "User-Agent": "cong-cuoi",
                     "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"})
        for lan in range(3):
            try:
                with self._mo(yeu_cau, timeout=30) as phan_hoi:
                    return json.loads(phan_hoi.read().decode() or "null")
            except urllib.error.HTTPError as loi:
                # Thân phản hồi có thể phản chiếu dữ liệu lạ: không vào thông báo, cổng không in.
                than = loi.read(500).decode(errors="replace") if loi.fp else ""
                loi.close()
                if loi.code < 500 or lan == 2:
                    raise LoiApi("%s %s: HTTP %d" % (phuong_thuc, duong, loi.code), loi.code, than)
            except urllib.error.URLError:
                if lan == 2:
                    raise LoiApi("%s %s: lỗi mạng" % (phuong_thuc, duong))
            time.sleep(2 ** lan)


class GiaLap:
    """Thay GitHub khi chạy khô: GET lấy từ từ điển theo đúng query (trừ phân trang), POST chỉ ghi lại."""

    def __init__(self, du_lieu):
        self.du_lieu, self.da_phat = du_lieu, []

    def che(self, chuoi):
        return chuoi

    def goi(self, phuong_thuc, duong, body=None):
        if phuong_thuc != "GET":
            self.da_phat.append((phuong_thuc, duong, body))
            return {}
        khop = re.search(r"[?&]per_page=100&page=(\d+)$", duong)
        goc = duong[:khop.start()] if khop else duong
        if goc not in self.du_lieu:
            raise LoiApi("GET %s: không có trong dữ liệu giả" % goc, 404)
        return [] if khop and khop.group(1) != "1" else self.du_lieu[goc]


def _trang(gh, duong, khoa=None, toi_da=30):
    ket, tong = [], 0
    for so in range(1, toi_da + 1):
        phan = gh.goi("GET", "%s%sper_page=100&page=%d" % (duong, "&" if "?" in duong else "?", so))
        muc = (phan or {}).get(khoa, []) if khoa else phan
        ket.extend(muc)
        tong = max(tong, (phan or {}).get("total_count", 0) if khoa else 0)
        if not muc:  # đọc tới trang rỗng: trang thiếu mục giữa chừng không được làm rơi trang sau
            break
    else:
        raise LoiApi("GET %s: quá %d trang, không đọc đủ" % (duong, toi_da))
    # /runs chỉ trả tới 1000 lượt, trang vượt trần ghi total_count 0: lấy số lớn nhất, lượt đỏ cũ không được rơi.
    if tong > len(ket):
        raise LoiApi("GET %s: không đọc đủ %s" % (duong, khoa))
    return ket


def _repo(pr, dau):
    return ((pr.get(dau) or {}).get("repo") or {}).get("full_name")


def _pr_vao_goc(gh, sha):
    """PR mở vào nhánh gốc có head đúng SHA. Có PR trong repo thì bỏ PR từ fork: người lạ đưa cùng SHA lên fork không làm kẹt được."""
    ds = [p for p in _trang(gh, "/pulls?state=open&base=%s" % ten.NHANH_GOC) if (p.get("head") or {}).get("sha") == sha]
    noi_bo = [p for p in ds if _repo(p, "head") == _repo(p, "base")]
    return [str(p["number"]) for p in (noi_bo or ds)]


def _luot_cua_pr(gh, so_pr, pr, lan_chay):
    """Lượt không bị các lọc dưới đây loại; cổng không biết nó chạy ref merge nào. Lượt không ghi nó test với base nào: `pull_requests[]` tính lúc đọc, còn
    PR đã đóng vẫn sinh lượt mới (sửa tiêu đề, tạo trễ). Nên nhánh đầu từng có PR khác thì không lượt nào tính, kể cả khi danh sách
    không có chính PR này. PR từng đổi base cũng vậy: lượt sau khi đổi vẫn chạy ref merge của base trước (L8). Bỏ lượt của repo, nhánh đầu khác và lượt trước khi PR mở."""
    dau = pr["head"]
    if not (dau.get("repo") and dau.get("label")):
        return []
    if {str(p.get("number")) for p in _trang(gh, "/pulls?state=all&head=" + urllib.parse.quote(dau["label"], safe=":/"))} != {so_pr}:
        return []
    if any(e.get("event") in ("base_ref_changed", "automatic_base_change_succeeded") for e in _trang(gh, "/issues/%s/events" % so_pr)):
        return []
    return [r for r in lan_chay if (r.get("head_repository") or {}).get("full_name") == _repo(pr, "head")
            and r.get("head_branch") == dau.get("ref") and (r.get("created_at") or "") >= (pr.get("created_at") or "~")]


def _doc_theo_sha(gh, so_pr, pr):
    sha = pr["head"]["sha"]
    duyet = _trang(gh, "/pulls/%s/reviews" % so_pr)
    commit = _trang(gh, "/pulls/%s/commits" % so_pr)
    # Commit merge từ nhánh gốc (chủ bấm Update branch) không làm họ thành đồng tác giả.
    nguoi_commit = {(c.get(k) or {}).get("login") for c in commit if len(c.get("parents") or []) < 2
                    for k in ("author", "committer")}
    # Theo TỆP workflow và sự kiện: workflow tệp khác đặt cùng tên, hay chạy on: push, không vào đây.
    quyen = {x: gh.goi("GET", "/collaborators/%s/permission" % urllib.parse.quote(x, safe=""))["permission"]
             for x in sorted({r["user"]["login"] for r in duyet if (r.get("user") or {}).get("type") == "User"})}
    lan_chay = _luot_cua_pr(gh, so_pr, pr, _trang(
        gh, "/actions/workflows/%s.yml/runs?head_sha=%s&event=pull_request" % (ten.CHECK_NHANH, sha), "workflow_runs"))
    return {
        "sha_dau": sha, "trang_thai_pr": pr.get("state"), "nhanh_dich": (pr.get("base") or {}).get("ref"),
        "so_pr_vao_goc": len(_pr_vao_goc(gh, sha)), "so_tep_khai": pr.get("changed_files"),
        "so_commit_khai": pr.get("commits"), "so_commit_doc": len(commit),
        "tac_gia": (pr.get("user") or {}).get("login"), "so_pr": pr.get("number"),
        # Người duyệt là người có quyền admin. Không lấy từ biến environment: cộng tác viên quyền ghi sửa được biến đó.
        "nguoi_tin": sorted(x for x, q in quyen.items() if q == "admin"),
        # Người ghi được phiếu phản bác: có quyền ghi. Repo công khai thì người lạ cũng gửi được review.
        "nguoi_ghi": sorted(x for x, q in quyen.items() if q in _QUYEN_GHI),
        "nguoi_commit": sorted(x for x in nguoi_commit if x),
        "tep": _trang(gh, "/pulls/%s/files" % so_pr),
        "lan_chay_nhanh": [{"head_sha": r.get("head_sha"), "status": r.get("status"),
                            "conclusion": r.get("conclusion")} for r in lan_chay],
        "duyet": [{
            "user": (r.get("user") or {}).get("login"), "user_type": (r.get("user") or {}).get("type"),
            "state": r.get("state"), "commit_id": r.get("commit_id"), "submitted_at": r.get("submitted_at"), "body": r.get("body"),
        } for r in duyet],
    }


def thu_thap(gh, so_pr, sha):
    """/files trả theo head hiện tại, nên đọc PR hai lần kẹp giữa. Head đã đổi thì trả None: lượt của head mới tự xét."""
    pr = gh.goi("GET", "/pulls/%s" % so_pr)
    if pr["head"]["sha"] != sha:
        return None
    du_lieu = _doc_theo_sha(gh, so_pr, pr)
    return du_lieu if gh.goi("GET", "/pulls/%s" % so_pr)["head"]["sha"] == sha else None


def tom_tat(q):
    dong = ["**Kết luận:** %s" % q["ket_luan"], "**Rủi ro từ diff:** %s" % q["rui_ro"],
            "**Số dòng đổi:** %d" % q["so_dong"], "**Vùng nhạy cảm đã khai:** %d mẫu" % q.get("so_mau_vung", 0), "", "**Lý do:**"]
    dong += ["- " + x for x in q["ly_do"][:50]]
    if q["chi_tiet"]:
        dong += ["", "**Chi tiết:**"] + ["- " + x for x in q["chi_tiet"][:50]]
    if q.get("the_duyet"):
        dong += ["", "**Thẻ duyệt ở ngay dưới:** lý do, phiếu phản bác, test và diff của tệp mức Cao."]
    return "\n".join(dong)[:_GIOI_HAN_TOM_TAT]


def phat_check(gh, sha, q):
    # Chỉ hai giá trị: neutral và skipped có thể được coi như qua, nên không bao giờ dùng.
    ket_luan = "success" if q["ket_luan"] == kiem_pr.CHO_QUA else "failure"
    output = {"title": "%s (%s)" % (q["ket_luan"], q["rui_ro"]), "summary": tom_tat(q)}
    if q.get("the_duyet"):
        output["text"] = q["the_duyet"]  # thẻ duyệt hiện ngay dưới tóm tắt trên trang check
    gh.goi("POST", "/check-runs", {
        "name": ten.CHECK_CUOI, "head_sha": sha, "status": "completed", "conclusion": ket_luan, "output": output,
    })
    return ket_luan


def chay(gh, sha, tep_vung=None):
    """Chỉ xét và phát trên SHA sự kiện. 0: đã phát, hoặc SHA không còn là head PR nào. 1: hỏng hạ tầng.
    tep_vung: tệp vùng nhạy cảm trong bản checkout nhánh gốc, không phải của PR: PR không tự gỡ được vùng."""
    try:
        vung = rui_ro.doc_vung(tep_vung)
        ds = _pr_vao_goc(gh, sha)
        du_lieu = thu_thap(gh, ds[0], sha) if ds else None
        if du_lieu:
            du_lieu["vung_nhay_cam"] = vung
        # Không còn PR: vẫn phát, để `success` cũ của SHA này không còn đứng sau khi PR đóng.
        q = kiem_pr.quyet_dinh(du_lieu) if du_lieu else {
            "ket_luan": "khong_xet", "rui_ro": "chua_ro", "so_dong": 0, "chi_tiet": [],
            "ly_do": ["SHA này không còn là head của PR mở vào nhánh gốc"]}
        print("%s: %s" % (ten.CHECK_CUOI, phat_check(gh, sha, q)))
        print(tom_tat(q))
        return 0
    except Exception as loi:  # noqa: BLE001 - mọi lỗi đều phải kết thúc đóng
        print("lỗi hạ tầng: " + gh.che("%s: %s" % (type(loi).__name__, loi)))
        try:
            # Vẫn phải phát failure: `success` cũ trên SHA này không được ở lại khi lần xét mới hỏng.
            ly_do = [str(loi)] if isinstance(loi, rui_ro.LoiVung) else []
            phat_check(gh, sha, {"ket_luan": "loi_ha_tang", "rui_ro": "chua_ro", "so_dong": 0, "chi_tiet": [],
                                 "ly_do": ["cổng không đọc đủ dữ liệu, PR chưa được xét"] + ly_do})
        except Exception as loi_phat:  # noqa: BLE001
            print("không phát được check: " + gh.che(type(loi_phat).__name__))
        return 1


def main(argv=None):
    p = argparse.ArgumentParser(description="Phát check run cổng cuối.")
    p.add_argument("--kho", metavar="TEP_JSON", help="chạy khô bằng dữ liệu giả, không gọi mạng")
    p.add_argument("--sha", default=os.environ.get(ten.BIEN_SHA, ""))
    a = p.parse_args(argv)
    if not kiem_pr.SHA_HOP_LE.fullmatch(a.sha):
        print("SHA không hợp lệ")
        return 2
    if a.kho:
        with open(a.kho, encoding="utf-8") as tep:
            gh = GiaLap(json.load(tep))
        ma = chay(gh, a.sha, ten.TEP_VUNG)
        print("CHẠY KHÔ, không gọi GitHub. Sẽ gọi:\n" + json.dumps(gh.da_phat, ensure_ascii=False, indent=2))
        return ma
    repo, token = os.environ.get("GITHUB_REPOSITORY", ""), os.environ.get(ten.BIEN_TOKEN_APP, "")
    if not re.fullmatch(r"[\w.-]+/[\w.-]+", repo) or not TOKEN_HOP_LE.fullmatch(token):
        print("thiếu GITHUB_REPOSITORY, hoặc %s rỗng hay có ký tự lạ" % ten.BIEN_TOKEN_APP)
        return 2
    gh = GitHub(repo, token, os.environ.get("GITHUB_API_URL", API_GOC))
    return chay(gh, a.sha, ten.TEP_VUNG)


if __name__ == "__main__":
    sys.exit(main())
