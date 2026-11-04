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
    def __init__(self, thong_bao, ma=None):
        super().__init__(thong_bao)
        self.ma = ma


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
                loi.close()  # Không đưa thân phản hồi vào thông báo: có thể phản chiếu dữ liệu lạ.
                if loi.code < 500 or lan == 2:
                    raise LoiApi("%s %s: HTTP %d" % (phuong_thuc, duong, loi.code), loi.code)
            except urllib.error.URLError:
                if lan == 2:
                    raise LoiApi("%s %s: lỗi mạng" % (phuong_thuc, duong))
            time.sleep(2 ** lan)


class GiaLap:
    """Thay GitHub khi chạy khô: GET lấy từ từ điển, POST chỉ ghi lại, không có mạng."""

    def __init__(self, du_lieu):
        self.du_lieu, self.da_phat = du_lieu, []

    def che(self, chuoi):
        return chuoi

    def goi(self, phuong_thuc, duong, body=None):
        if phuong_thuc != "GET":
            self.da_phat.append((phuong_thuc, duong, body))
            return {}
        goc, _, truy_van = duong.partition("?")
        if goc not in self.du_lieu:
            raise LoiApi("GET %s: không có trong dữ liệu giả" % goc, 404)
        return self.du_lieu[goc] if re.search(r"(^|&)page=1$", truy_van) or "page=" not in truy_van else []


def _trang(gh, duong, khoa=None, toi_da=30):
    ket = []
    for so in range(1, toi_da + 1):
        phan = gh.goi("GET", "%s%sper_page=100&page=%d" % (duong, "&" if "?" in duong else "?", so))
        muc = (phan or {}).get(khoa, []) if khoa else phan
        ket.extend(muc)
        if len(muc) < 100:
            break
    return ket


def _doc_theo_sha(gh, so_pr, pr):
    sha = pr["head"]["sha"]
    commit = _trang(gh, "/pulls/%s/commits" % so_pr)
    nguoi_commit = {(c.get(k) or {}).get("login") for c in commit for k in ("author", "committer")}
    runs = _trang(gh, "/commits/%s/check-runs?check_name=%s&filter=latest" % (sha, ten.CHECK_NHANH), "check_runs")
    suites = _trang(gh, "/commits/%s/check-suites" % sha, "check_suites")
    # Giờ tạo check suite do máy chủ ghi; ngày trong commit thì người push tự đặt được.
    gio_suite = sorted(s["created_at"] for s in suites if s.get("created_at"))
    return {
        "sha_dau": sha, "trang_thai_pr": pr.get("state"), "so_tep_khai": pr.get("changed_files"),
        "tac_gia": (pr.get("user") or {}).get("login"),
        "nguoi_commit": sorted(x for x in nguoi_commit if x),
        "tep": _trang(gh, "/pulls/%s/files" % so_pr),
        "check_nhanh": [{
            "head_sha": r.get("head_sha"), "status": r.get("status"), "conclusion": r.get("conclusion"),
            "app_slug": (r.get("app") or {}).get("slug"),
        } for r in runs if r.get("name") == ten.CHECK_NHANH],
        "duyet": [{
            "user": (r.get("user") or {}).get("login"), "user_type": (r.get("user") or {}).get("type"),
            "association": r.get("author_association"), "state": r.get("state"),
            "commit_id": r.get("commit_id"), "submitted_at": r.get("submitted_at"), "body": r.get("body"),
        } for r in _trang(gh, "/pulls/%s/reviews" % so_pr)],
        "push_cuoi": gio_suite[0] if gio_suite else None,
    }


def thu_thap(gh, so_pr):
    """/files trả theo head hiện tại, nên đọc PR hai lần kẹp giữa: SHA đổi thì đọc lại."""
    for _ in range(3):
        du_lieu = _doc_theo_sha(gh, so_pr, gh.goi("GET", "/pulls/%s" % so_pr))
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


def chay(gh, so_pr, cho_giay, nghi=15, ngu=time.sleep, dong_ho=time.monotonic):
    """0: đã phát check. 1: hỏng hạ tầng (PR vẫn bị chặn, vì không có check thành công)."""
    han, sha = dong_ho() + cho_giay, None
    try:
        while True:
            du_lieu = thu_thap(gh, so_pr)
            sha = du_lieu["sha_dau"]
            q = kiem_pr.quyet_dinh(du_lieu)
            if q["ket_luan"] != kiem_pr.CHO:
                break
            if dong_ho() >= han:
                q["ly_do"].append("hết %d giây chờ, chưa đủ điều kiện" % cho_giay)
                break
            ngu(nghi)
        if not kiem_pr.SHA_HOP_LE.fullmatch(str(sha)):
            raise LoiApi("head SHA không hợp lệ, không phát check")
        print("%s: %s" % (ten.CHECK_CUOI, phat_check(gh, sha, q)))
        print(tom_tat(q))
        return 0
    except Exception as loi:  # noqa: BLE001 - mọi lỗi đều phải kết thúc đóng
        print("lỗi hạ tầng: " + gh.che("%s: %s" % (type(loi).__name__, loi)))
        try:
            # Vẫn phải phát failure: `success` cũ trên cùng SHA không được ở lại khi lần xét mới hỏng.
            sha = sha or gh.goi("GET", "/pulls/%s" % so_pr)["head"]["sha"]
            if kiem_pr.SHA_HOP_LE.fullmatch(str(sha)):
                phat_check(gh, sha, {"ket_luan": "loi_ha_tang", "rui_ro": "chua_ro", "so_dong": 0, "chi_tiet": [],
                                     "ly_do": ["cổng không đọc đủ dữ liệu, PR chưa được xét"]})
        except Exception as loi_phat:  # noqa: BLE001
            print("không phát được check: " + gh.che(type(loi_phat).__name__))
        return 1


def main(argv=None):
    p = argparse.ArgumentParser(description="Phát check run cổng cuối.")
    p.add_argument("--cho-giay", type=int, default=600, help="thời gian chờ cong-nhanh xong")
    p.add_argument("--kho", metavar="TEP_JSON", help="chạy khô bằng dữ liệu giả, không gọi mạng")
    p.add_argument("--pr", default=os.environ.get(ten.BIEN_PR, ""))
    a = p.parse_args(argv)
    if not re.fullmatch(r"[1-9][0-9]{0,9}", a.pr or ""):
        print("thiếu số PR hợp lệ")
        return 2
    if a.kho:
        with open(a.kho, encoding="utf-8") as tep:
            gh = GiaLap(json.load(tep))
        ma = chay(gh, a.pr, cho_giay=0)
        print("CHẠY KHÔ, không gọi GitHub. Sẽ gọi:\n" + json.dumps(gh.da_phat, ensure_ascii=False, indent=2))
        return ma
    repo, token = os.environ.get("GITHUB_REPOSITORY", ""), os.environ.get(ten.BIEN_TOKEN_APP, "")
    if not re.fullmatch(r"[\w.-]+/[\w.-]+", repo) or not token:
        print("thiếu GITHUB_REPOSITORY hoặc %s" % ten.BIEN_TOKEN_APP)
        return 2
    return chay(GitHub(repo, token, os.environ.get("GITHUB_API_URL", API_GOC)), a.pr, a.cho_giay)


if __name__ == "__main__":
    sys.exit(main())
