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
import urllib.request

from . import kiem_pr, ten

API_GOC = "https://api.github.com"
_GIOI_HAN_TOM_TAT = 60000


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
    ket = []
    for so in range(1, toi_da + 1):
        phan = gh.goi("GET", "%s%sper_page=100&page=%d" % (duong, "&" if "?" in duong else "?", so))
        muc = (phan or {}).get(khoa, []) if khoa else phan
        ket.extend(muc)
        if len(muc) < 100:
            break
    return ket


def _pr_vao_goc(gh, sha):
    """Số các PR mở vào nhánh gốc có head đúng SHA. PR nhắm nhánh khác không liên quan tới cổng."""
    ds = _trang(gh, "/pulls?state=open&base=%s" % ten.NHANH_GOC)
    return [str(p["number"]) for p in ds if (p.get("head") or {}).get("sha") == sha]


def _doc_theo_sha(gh, so_pr, pr, nguoi_tin):
    sha = pr["head"]["sha"]
    if not kiem_pr.SHA_HOP_LE.fullmatch(str(sha)):
        raise LoiApi("head SHA không hợp lệ, không phát check")
    commit = _trang(gh, "/pulls/%s/commits" % so_pr)
    # Commit merge từ nhánh gốc (chủ bấm Update branch) không làm họ thành đồng tác giả.
    nguoi_commit = {(c.get(k) or {}).get("login") for c in commit if len(c.get("parents") or []) < 2
                    for k in ("author", "committer")}
    # Theo TỆP workflow và sự kiện: workflow tệp khác đặt cùng tên, hay chạy on: push, không vào đây.
    lan_chay = _trang(gh, "/actions/workflows/%s.yml/runs?head_sha=%s&event=pull_request" % (ten.CHECK_NHANH, sha),
                      "workflow_runs")
    return {
        "sha_dau": sha, "trang_thai_pr": pr.get("state"), "nhanh_dich": (pr.get("base") or {}).get("ref"),
        "so_pr_vao_goc": len(_pr_vao_goc(gh, sha)), "so_tep_khai": pr.get("changed_files"),
        "so_commit_khai": pr.get("commits"), "so_commit_doc": len(commit),
        "tac_gia": (pr.get("user") or {}).get("login"), "nguoi_tin": nguoi_tin,
        "nguoi_commit": sorted(x for x in nguoi_commit if x),
        "tep": _trang(gh, "/pulls/%s/files" % so_pr),
        "lan_chay_nhanh": [{"head_sha": r.get("head_sha"), "status": r.get("status"),
                            "conclusion": r.get("conclusion")} for r in lan_chay],
        "duyet": [{
            "user": (r.get("user") or {}).get("login"), "user_type": (r.get("user") or {}).get("type"),
            "state": r.get("state"), "commit_id": r.get("commit_id"), "submitted_at": r.get("submitted_at"),
            "body": r.get("body"),
        } for r in _trang(gh, "/pulls/%s/reviews" % so_pr)],
    }


def thu_thap(gh, so_pr, nguoi_tin):
    """/files trả theo head hiện tại, nên đọc PR hai lần kẹp giữa: SHA đổi thì đọc lại."""
    for _ in range(3):
        du_lieu = _doc_theo_sha(gh, so_pr, gh.goi("GET", "/pulls/%s" % so_pr), nguoi_tin)
        if gh.goi("GET", "/pulls/%s" % so_pr)["head"]["sha"] == du_lieu["sha_dau"]:
            return du_lieu
    raise LoiApi("head SHA đổi liên tục trong lúc đọc")


def tom_tat(q):
    dong = ["**Kết luận:** %s" % q["ket_luan"], "**Rủi ro từ diff:** %s" % q["rui_ro"],
            "**Số dòng đổi:** %d" % q["so_dong"], "", "**Lý do:**"]
    dong += ["- " + x for x in q["ly_do"][:50]]
    if q["chi_tiet"]:
        dong += ["", "**Chi tiết:**"] + ["- " + x for x in q["chi_tiet"][:50]]
    return "\n".join(dong)[:_GIOI_HAN_TOM_TAT]


def phat_check(gh, sha, q):
    # Chỉ hai giá trị: neutral và skipped có thể được coi như qua, nên không bao giờ dùng.
    ket_luan = "success" if q["ket_luan"] == kiem_pr.CHO_QUA else "failure"
    gh.goi("POST", "/check-runs", {
        "name": ten.CHECK_CUOI, "head_sha": sha, "status": "completed", "conclusion": ket_luan,
        "output": {"title": "%s (%s)" % (q["ket_luan"], q["rui_ro"]), "summary": tom_tat(q)},
    })
    return ket_luan


def chay(gh, nguoi_tin, so_pr=None, sha=None):
    """0: đã phát, hoặc SHA không thuộc PR nào. 1: hỏng hạ tầng. Không chờ CI: CI xong sẽ đánh thức cổng."""
    try:
        if so_pr is None:
            ds = _pr_vao_goc(gh, sha)
            if not ds:
                print("SHA này không có PR mở vào nhánh gốc, không xét.")
                return 0
            so_pr = ds[0]
        du_lieu = thu_thap(gh, so_pr, nguoi_tin)
        sha = du_lieu["sha_dau"]
        q = kiem_pr.quyet_dinh(du_lieu)
        print("%s: %s" % (ten.CHECK_CUOI, phat_check(gh, sha, q)))
        print(tom_tat(q))
        return 0
    except Exception as loi:  # noqa: BLE001 - mọi lỗi đều phải kết thúc đóng
        print("lỗi hạ tầng: " + gh.che("%s: %s" % (type(loi).__name__, loi)))
        try:
            # Vẫn phải phát failure: `success` cũ trên cùng SHA không được ở lại khi lần xét mới hỏng.
            sha = gh.goi("GET", "/pulls/%s" % so_pr)["head"]["sha"] if so_pr else sha
            if kiem_pr.SHA_HOP_LE.fullmatch(str(sha)):
                phat_check(gh, sha, {"ket_luan": "loi_ha_tang", "rui_ro": "chua_ro", "so_dong": 0, "chi_tiet": [],
                                     "ly_do": ["cổng không đọc đủ dữ liệu, PR chưa được xét"]})
        except Exception as loi_phat:  # noqa: BLE001
            print("không phát được check: " + gh.che(type(loi_phat).__name__))
        return 1


def main(argv=None):
    p = argparse.ArgumentParser(description="Phát check run cổng cuối.")
    p.add_argument("--kho", metavar="TEP_JSON", help="chạy khô bằng dữ liệu giả, không gọi mạng")
    p.add_argument("--pr", default=os.environ.get(ten.BIEN_PR, ""))
    p.add_argument("--sha", default=os.environ.get(ten.BIEN_SHA, ""))
    a = p.parse_args(argv)
    if bool(a.pr) == bool(a.sha):
        print("cần đúng một trong số PR hoặc SHA")
        return 2
    if a.pr and not re.fullmatch(r"[1-9][0-9]{0,9}", a.pr) or a.sha and not kiem_pr.SHA_HOP_LE.fullmatch(a.sha):
        print("số PR hoặc SHA không hợp lệ")
        return 2
    nguoi_tin = re.findall(r"[^\s,]+", os.environ.get(ten.BIEN_NGUOI_DUYET, ""))
    if a.kho:
        with open(a.kho, encoding="utf-8") as tep:
            gh = GiaLap(json.load(tep))
        ma = chay(gh, nguoi_tin, a.pr or None, a.sha or None)
        print("CHẠY KHÔ, không gọi GitHub. Sẽ gọi:\n" + json.dumps(gh.da_phat, ensure_ascii=False, indent=2))
        return ma
    repo, token = os.environ.get("GITHUB_REPOSITORY", ""), os.environ.get(ten.BIEN_TOKEN_APP, "")
    if not re.fullmatch(r"[\w.-]+/[\w.-]+", repo) or not token:
        print("thiếu GITHUB_REPOSITORY hoặc %s" % ten.BIEN_TOKEN_APP)
        return 2
    gh = GitHub(repo, token, os.environ.get("GITHUB_API_URL", API_GOC))
    return chay(gh, nguoi_tin, a.pr or None, a.sha or None)


if __name__ == "__main__":
    sys.exit(main())
