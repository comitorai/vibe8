# Hồ sơ `vibe8` — cổng PR cho agent và bộ luật làm việc

`comitorai/vibe8`: cổng `cong-cuoi` (Python 3.9+, CHỈ thư viện chuẩn) quyết định PR có vào `main` được không, dựa trên
diff, lượt CI và lượt duyệt theo đúng SHA; cộng bộ luật làm việc (`luat/`), mẫu tài liệu (`mau/`) và bộ nghiệm thu
(`nghiem-thu/`). Không Next, không database, không Account, không giao diện, không workspace, không `package.json`.
Repo chọn hồ sơ này bằng `.claude/comitor-repo.json` (`{"profile": "vibe8"}`).

Hai luật đứng trên mọi hàng (BM § Nguyên tắc giữ): **mọi đường hỏng đều không phát `success`**, và **quyết định chỉ lấy
từ API GitHub** — không từ thân PR, nhãn, tiêu đề hay lời khai. Hàng nào không chắc thuộc nhóm nào thì hỏi: diff này
có làm cổng mở ở một ca nó từng đóng không?

```json profile
{
  "docs": {
    "RD": "README.md",
    "BM": "docs/bao-mat.md",
    "PP": "luat/phuong-phap.md",
    "KT": "luat/kien-truc.md",
    "HT": "luat/hien-thi-tien-do.md",
    "DP": "luat/vai/dieu-phoi.md",
    "KQ": "nghiem-thu/ket-qua.md"
  },
  "table": "references/profiles/vibe8.md",
  "pitfalls": "references/profiles/vibe8.md",
  "pitfallSections": {
    "Kiến trúc": ["Cổng đọc GitHub"],
    "Dữ liệu & bảo mật": ["Cổng đọc GitHub", "Xếp mức rủi ro"],
    "Quy ước": ["Luật và tài liệu"],
    "Chất lượng": ["Xếp mức rủi ro", "Luật và tài liệu"]
  }
}
```

**Ngoại lệ khai trong repo.** Định danh Python tiếng Việt không dấu (`kiem_pr`, `rui_ro`, `nguoi_tin`, `_doc_theo_sha`)
là quy ước CỦA REPO, không phải lỗi L1 — mọi mã có sẵn viết thế. Tên tạm `xuong`/`cong` gom ở `cong/ten.py` (RD dòng 4).
Luật ghi «Alex 1a, 06/11» là quyết định của chủ dự án: trích lại được, không «sửa» được.

## Tài liệu quy định

Thay `references/governing-docs.md` ở bước 0. Cùng luật: lấy hàng KHỚP ĐẦU TIÊN, cộng các hàng **cộng thêm**; đọc
bằng `sections.mjs`, không Read cả file. Viết tắt: **RD** `README.md` · **BM** `docs/bao-mat.md` · **PP**
`luat/phuong-phap.md` · **KT** `luat/kien-truc.md` · **HT** `luat/hien-thi-tien-do.md` · **DP** `luat/vai/dieu-phoi.md`
· **KQ** `nghiem-thu/ket-qua.md`. Docstring đầu module (`rui_ro.py`, `kiem_pr.py`, `gate_app.py`) giữ lý do và giới
hạn — đọc nó như tài liệu quy định.

| Đường dẫn đổi (glob) | Đọc | Mục quyết định |
|---|---|---|
| `cong/rui_ro.py`, `cong/vung-nhay-cam.txt` | PP; RD; BM | PP § 2 · RD § Luật ("Đổi `.github/`", "Test có sẵn", "Thêm tệp hay symlink", "Tệp không có diff", "Hai mức", "Vùng nhạy cảm") · BM § Giới hạn đã biết · docstring `rui_ro.py` |
| `cong/kiem_pr.py`, `cong/the_duyet.py` | RD; PP; BM | RD § Luật · PP § 2, § 3 · BM § Giới hạn đã biết, § Nguyên tắc giữ |
| `cong/gate_app.py`, `cong/ten.py`, `cong/__init__.py` | BM; RD | BM § Nguyên tắc giữ, § Vì sao dùng hai sự kiện đặc quyền, § Giới hạn đã biết · RD § Luật ("Duyệt hợp lệ", "Mọi PR, cả mức Cao") |
| `cong/tests/**`, `nghiem-thu/tests/**` | RD; PP | RD § Luật ("Test có sẵn") · PP § 3 |
| `.github/**` | BM; RD | BM § Nguyên tắc giữ, § Vì sao dùng hai sự kiện đặc quyền, § Giới hạn đã biết · RD § Luật ("Mọi lượt của tệp workflow", "`cong-nhanh` chỉ chạy") |
| `kiem-tra.sh`, `nghiem-thu/kiem_cuc_bo.py`, `nghiem-thu/bat_cong.py` | RD; BM | RD § Chạy · BM § Đã kiểm, chỉ ở mức cục bộ |
| `nghiem-thu/ket-qua.md`, `nghiem-thu/loi/**` | KQ; RD | KQ § Chưa thử trên repo thật · RD § Luật ("Vùng nhạy cảm") |
| `nghiem-thu/**` (còn lại) | RD | RD § Chạy, § Gồm gì |
| `.claude/**`, `.mcp.json` | RD; skill này | RD § Chạy · `MAINTAINING.md` §1, §7 |
| `luat/phuong-phap.md` | PP | PP § 1, § 2, § 3 |
| `luat/kien-truc.md` | KT; PP | KT § 14, § 15 · PP § 1 |
| `luat/hien-thi-tien-do.md` | HT | HT § 0, § 7 |
| `luat/vai/**` | DP; KT | DP § 1, § 6 · KT § 13 |
| `docs/bao-mat.md` | BM | BM § Nguyên tắc giữ, § Giới hạn đã biết |
| `mau/**`, `docs/**`, `README.md`, `hien-thi/**` | RD; KT | RD § Gồm gì · KT § 15 |
| **cộng thêm:** mọi `cong/*.py` | BM | BM § Nguyên tắc giữ |
| **cộng thêm:** mọi `luat/*.md` | PP | PP § 1 |

## Phạm vi diff

Như module: không lockfile, không mã sinh. Bỏ `':(exclude)pnpm-lock.yaml'` hay giữ cũng như nhau. Diff dài thì chia:
`… -- cong .github kiem-tra.sh` · `… -- cong/tests nghiem-thu` · `… -- luat docs mau README.md .claude`.

## Bản gốc hay bản chép

Bước 1.7 (`git show HEAD:package.json`) **thoát khác 0 ở repo này, và đó KHÔNG phải lệnh git hỏng**: repo Python chỉ
stdlib, không `package.json` ở gốc. Đi tiếp, đừng NOT REVIEWED. Repo không phải `comitor-starter`: mọi
`.claude/skills/comitor-*/**` ở đây là BẢN CHÉP → `quality.md` F4 áp nguyên. Ba mảnh ngoài thư mục skill
(`MAINTAINING.md` §1) thiếu mảnh nào thì ghi dưới **Đã kiểm**. Chú ý: `.claude/settings.json` của repo này còn khối hook
`nghiem-thu/hook_ghi_token.py` — GỘP, không chép đè (RD § Chạy).

## Đường nhanh

Thay danh sách đường dẫn nhạy cảm (ngưỡng 150 dòng và ba điều kiện kia giữ nguyên):

`cong/**`, `.github/**`, `.claude/**`, `.mcp.json`, `kiem-tra.sh`, `nghiem-thu/kiem_cuc_bo.py`,
`nghiem-thu/bat_cong.py`, `nghiem-thu/ghi_token.py`, `nghiem-thu/hook_ghi_token.py`, `nghiem-thu/loi/**`,
`nghiem-thu/ket-qua.md`, `luat/**`, `docs/bao-mat.md` — chỗ của cổng, khoá App, CI, sổ bằng chứng và luật.

## Lockfile

Repo không có lockfile hay tệp khai phụ thuộc (RD «Python 3.9 trở lên, chỉ stdlib»). Đoạn Lockfile của module n/a.
Thêm `requirements*.txt`, `pyproject.toml`, `package.json` hay lockfile → ❓ vì sao repo cần phụ thuộc; một `import`
ngoài thư viện chuẩn trong `cong/` → 🔴 (BM § Nguyên tắc giữ: `cong-cuoi` chỉ dùng thư viện chuẩn).

## Hàng

Phạm vi nhóm (thay dòng **Phạm vi** đầu bốn reference): **Kiến trúc** — `cong/**` trừ `tests/`, `.github/**`,
`nghiem-thu/*.py`, `hien-thi/*.py`. **Dữ liệu & bảo mật** — `cong/**`, `.github/**`, `.claude/**`, `.mcp.json`,
`nghiem-thu/ghi_token.py`, `nghiem-thu/hook_ghi_token.py`, `nghiem-thu/bat_cong.py`. **Quy ước** — mọi `.py`, `.sh`,
YAML, `luat/**`. **Chất lượng** — mọi diff.

Mã luật trong ngoặc của báo cáo: hàng **Áp**/**Đổi** dùng mã của reference module khi ô đó còn áp, không thì
`(RD § Luật)` / `(BM § n)` / `(PP L3)`; hàng **Thêm** dùng mã nêu trong ô.

| Nhóm | Hàng | Áp/Đổi/Bỏ/Thêm | Luật ở repo này (nguồn) |
|---|---|---|---|
| Kiến trúc | **Tầng** | Đổi | Module nói `lib/core`, `stores`, `route.ts` — không có ở đây, áp nguyên văn là n/a mọi file. Luật: `rui_ro.py` và `kiem_pr.py` là HÀM THUẦN (dữ liệu vào, quyết định ra; docstring đầu file), chỉ `gate_app.py` đọc REST và phát check run. Gọi mạng, đọc biến môi trường hay giờ hệ thống trong hàm thuần 🟠. |
| Kiến trúc | **Một luật** | Áp | M1/M2 với hằng của repo: tên tạm gom ở `cong/ten.py`; mức rủi ro chỉ do `rui_ro.py` xếp; người duyệt hợp lệ chỉ do `nguoi_tin` của `gate_app.py` + `kiem_pr.py` quyết. Một danh sách tệp bảo vệ hay một ngưỡng (400 dòng, 250 commit) viết lần hai 🟠. M3 (API giả) n/a. |
| Kiến trúc | **Ranh giới** | Đổi | Ranh giới của module (Account, `lib/api-client`) n/a. Ranh giới ở đây: workflow `cong-cuoi` KHÔNG checkout, KHÔNG chạy mã PR, chỉ lấy `/cong/` từ nhánh gốc (BM § Nguyên tắc giữ) 🔴. `nghiem-thu/` nằm ngoài vùng bảo vệ, nên mã cổng không được import từ đó 🟠. |
| Kiến trúc | **Chỗ đặt** | Đổi | Test của script đo đặt ở `nghiem-thu/tests/` (ngoài vùng bảo vệ, comment `kiem-tra.sh`); test cổng ở `cong/tests/`. Mẫu tài liệu ở `mau/`, luật ở `luat/` (RD § Gồm gì). Đặt sai 🟡. |
| Kiến trúc | **Account** | Bỏ | Không có Account, workspace, seat. |
| Dữ liệu & bảo mật | **Workspace** | Bỏ | Không tenant. Phạm vi tương đương là «đúng repo, đúng PR, đúng SHA» — ở hàng **Quyết định**. |
| Dữ liệu & bảo mật | **Quyết định** | Đổi (thay **Đường ghi**) | Module nói `requirePermission` trên route — n/a. Luật (RD § Luật, BM § Nguyên tắc giữ): mọi lượt duyệt, phiếu, lượt CI chỉ tính khi đúng head SHA, đúng PR mở vào `main`, đúng người hợp lệ (khác tác giả, khác người có commit, không bot); lượt `bac` không bị `khong-bac` sau gỡ. Nới một trong các điều đó mà không có quyết định của Alex ghi trong diff 🔴. Đường hỏng (API lỗi, thiếu trường, quá trần trang) phát `success` 🔴; thiếu dữ liệu xếp mức THẤP hơn 🔴 (docstring `rui_ro.py`). |
| Dữ liệu & bảo mật | **Toàn vẹn** | Đổi | Không database. Toàn vẹn ở đây là sổ bằng chứng: `nghiem-thu/ket-qua.md` và `nghiem-thu/loi/**` là vùng Cao (`cong/vung-nhay-cam.txt`) — sửa kết quả đã đo không kèm lượt đo mới 🟠. Test có sẵn sửa/đổi tên/xoá = điều kiện nghiệm thu bị đổi (RD § Luật "Test có sẵn"; PP L5): nêu dưới **Đã kiểm**, 🟠 khi bản sửa làm ca đó dễ qua hơn. |
| Dữ liệu & bảo mật | **Tiêm & bí mật** | Áp | T1–T5 nguyên văn, cộng: dữ liệu PR (tên nhánh, tiêu đề, tên tệp) vào `run:` của workflow 🔴; tên tệp do người mở PR đặt vào log/check run mà không qua `hien_thi()` 🟠; token/khoá App in ra hay đi qua chuyển hướng 🔴 (BM § Nguyên tắc giữ); sự kiện mới loại `pull_request_target`/`workflow_run` không kèm lý do ở BM § Vì sao dùng hai sự kiện đặc quyền 🟠. |
| Dữ liệu & bảo mật | **Hướng hỏng** | Áp | Nguyên văn với hướng của repo: cổng hỏng ĐÓNG. Lỗi đọc quyền → `failure` (BM § Giới hạn 20); thiếu `owner.type` → xét như tổ chức (BM § Giới hạn 19); không có lượt CI tính được → chờ, không qua. `except` nuốt lỗi rồi đi tiếp tới `success` 🔴. |
| Quy ước | **i18n** | Bỏ | Không giao diện, không `messages/`. |
| Quy ước | **Màu & UI** | Bỏ | Không giao diện. |
| Quy ước | **Ngôn ngữ & tên** | Đổi | L1 (định danh tiếng Anh) SAI ở repo này: định danh tiếng Việt không dấu là quy ước có sẵn (ngoại lệ khai ở đầu hồ sơ) — định danh tiếng Anh MỚI trộn vào mô-đun tiếng Việt 🟡. Hợp đồng máy giữ nguyên chữ: tên check `cong-cuoi`, tên job `cong-nhanh`, khoá phiếu `phieu-phan-bac:`, `tai-hien:`, `quyet-l4:`, `ngoai-le-co:` — đổi chữ ở hàng **Hợp đồng**. Thông điệp check run tiếng Việt có dấu, nói người đọc phải làm gì. |
| Quy ước | **Comment** | Áp | C1–C5 nguyên văn; comment ở đây giữ LÝ DO và giới hạn đã đo (`kiem-tra.sh`, `cong-nhanh.yml`, docstring `rui_ro.py`). Xoá một comment lý do mà không xoá hành vi nó giải thích 🟡. |
| Quy ước | **Kiểu** | Đổi | K1–K5 viết cho TS — n/a. RD hứa «Python 3.9 trở lên»: cú pháp hay API của bản sau (`match`, `X \| Y` lúc chạy, `zip(strict=)`) 🟠; `assert` canh an toàn trong mã cổng 🟠 (mất dưới `python -O`). |
| Quy ước | **Luật viết** | Thêm | PP § 1: một luật mới ở `luat/phuong-phap.md` phải đủ bốn thứ (chặn lỗi gì · đo bằng gì · mức giữ/bỏ · ngày xét), thiếu thì là lời khuyên ở mục 7 🟠 (LV1); vượt trần 15 luật mà không bỏ luật khác 🟠 (LV2); khẳng định mới thiếu nhãn `[ĐÃ KIỂM: … · ngày]`/`[SUY LUẬN]` 🟡 (LV3); quyết định của chủ dự án không ghi mã + ngày («Alex 1b 14/11») 🟡 (LV4). |
| Chất lượng | **Đúng** | Đổi | Bán kính ảnh hưởng — bảng anh em của module n/a. Anh em ở đây: điều kiện trong `kiem_pr.py` ⇄ `nguoi_tin`/dữ liệu của `gate_app.py` ⇄ thông điệp check run ⇄ RD § Luật ⇄ BM § Giới hạn đã biết ⇄ PP § 2 bảng ⇄ `cong/tests/`. Một luật cổng đổi mà một anh em không đổi theo 🟠. Ca biên phải nghĩ: PR đóng/mở lại, đổi base, nhánh dùng lại, force push, repo tổ chức vs cá nhân, phân trang API. |
| Chất lượng | **Test** | Đổi | E3–E8 (store, API giả, Playwright) n/a. `unittest` stdlib (`kiem-tra.sh`). Giữ E1 (hàm thuần mới có test), E2 (sửa lỗi có test đỏ trước — PP L6), E7. Thêm: luật cổng mới phải có ca CHẶN chạy thật, không chỉ ca qua 🟠 (ET1); test phụ thuộc giờ, mạng ngoài hay thứ tự chạy 🟠 (PP L8); muốn thêm test cho ca có sẵn thì tạo tệp MỚI, không sửa tệp test có sẵn (RD § Luật "Test có sẵn") 🟡. |
| Chất lượng | **Hợp đồng** | Đổi | H2–H7 của module n/a. Hợp đồng ở đây là với người và agent ghi phiếu, và với GitHub: khoá dòng phiếu (`phieu-phan-bac:`, `tai-hien:`, `quyet-l4:`, `ngoai-le-co:`), tên check `cong-cuoi`/`cong-nhanh` (required check của repo đã bật cổng), định dạng `cong/vung-nhay-cam.txt`. Đổi một trong số đó mà RD § Luật không đổi cùng PR 🟠; đổi tên check là gãy mọi repo đã bật 🔴. |
| Chất lượng | **Trạng thái** | Bỏ | Không màn hình. |
| Chất lượng | **Tối giản** | Áp | Nguyên văn. |
| Chất lượng | **Tài liệu** | Đổi | F1 thay bằng mục **Số bản**. F2, F5, F6 bỏ. F3 áp: RD § Luật, BM § Giới hạn đã biết, PP § 2 bảng phải khớp hành vi của `kiem_pr.py`/`rui_ro.py`/`gate_app.py` ở HEAD; RD § Gồm gì khớp thư mục; KQ chỉ ghi ca đã chạy thật. F4 áp (bản chép skill). |

Mẫu số bảng Kiểm: **Kiến trúc /4** (Tầng, Một luật, Ranh giới, Chỗ đặt) · **Dữ liệu & bảo mật /4** (Quyết định,
Toàn vẹn, Tiêm & bí mật, Hướng hỏng) · **Quy ước /4** (Ngôn ngữ & tên, Comment, Kiểu, Luật viết) · **Chất lượng /5**
(Đúng, Test, Hợp đồng, Tối giản, Tài liệu) — 17 hàng thay cho 21 của SKILL.md § 2.

## Công cụ máy

Thay ba công cụ của bước 2:

- `audit.mjs` của `comitor-ui` — **bỏ**: không `.tsx`/`.css`, skill đó không chép sang đây.
- `check-refs.mjs` của `comitor-test` — **bỏ**: skill đó không có ở đây. Thay bằng
  `node .claude/skills/comitor-review/scripts/sections.mjs --check-table --profile vibe8` khi diff đổi một tài liệu
  trong khối `docs` của hồ sơ — một ✗ là phát hiện của hàng **Tài liệu**.
- Kiểm sau `--fix` (chỉ khi có cờ): `python3 -m py_compile <file>`; sửa chạm chữ ký hàm thì nói rõ cần
  `sh ./kiem-tra.sh`.

`sh ./kiem-tra.sh` thì **không** — nó là `cong-nhanh`, cổng riêng chạy trên PR (PP L10: bằng chứng duy nhất là lượt CI
trên đúng SHA).

## Không bao giờ sửa

Thay danh sách của bước 4 (luật «file bẩn ở bước 1.6» và «bản chép skill» giữ nguyên):

- test có sẵn ở `cong/tests/**`, `nghiem-thu/tests/**` — sửa là đổi điều kiện nghiệm thu (PP L5);
- `nghiem-thu/ket-qua.md`, `nghiem-thu/loi/**` — sổ bằng chứng;
- `cong/vung-nhay-cam.txt`, `.github/**`, `kiem-tra.sh` — cổng và CI;
- `luat/**` ngoài lỗi chính tả hiển nhiên — chữ của luật là quyết định của chủ dự án;
- mọi con số đo và nhãn `[ĐÃ KIỂM: …]` — «sửa» một số đo là bịa số đo.

## Mức

Thay các dòng sau của danh sách Mức (SKILL.md § 6); dòng không nêu giữ nguyên.

- **🔴** — BỎ: `workspaceId`, route ghi, `@api-guard`, chốt chỉ ở giao diện, XSS, open redirect, bundle, migration,
  hợp đồng liên module, `better-auth`. THÊM: một đường hỏng phát `success`; quyết định đọc thân PR, nhãn hay tiêu đề;
  nới người duyệt hợp lệ (tác giả, người có commit, bot, sai SHA) không có quyết định ghi tên; `cong-cuoi` checkout
  hay chạy mã PR, dữ liệu PR vào `run:`; khoá/token in ra; `import` ngoài stdlib trong `cong/`; tệp từng xếp Cao bị xếp
  Thường không có quyết định ghi tên; đổi tên check `cong-cuoi`/`cong-nhanh`. Giữ: hành vi hay nơi gọi gãy; tiêm; bí
  mật trong diff.
- **🟠** — BỎ: các dòng về `lib/core`, `messages/`, danh bạ, 403/404, thẻ phiên bản, Server Action, gói UI, màu,
  `fetch`, API giả, Account, file khung. THÊM: luật cổng đổi mà RD § Luật / BM / PP không đổi theo; luật cổng mới không
  có ca chặn; test không tất định; luật mới thiếu bốn thứ của PP § 1; sửa sổ bằng chứng không kèm lượt đo; cú pháp
  sau Python 3.9. Giữ: khả năng lỗi, hồi quy, một luật viết hai lần, anh em không đổi theo, fail-open, test không thể đỏ.
- **🟡** — thêm: khẳng định mới thiếu nhãn căn cứ; quyết định của chủ dự án thiếu mã/ngày; định danh tiếng Anh mới
  trong mô-đun tiếng Việt.

## Số bản

Thay hàng F1 của `quality.md`. Repo **không có CHANGELOG, không có số bản, không có `changes/`** — đừng đòi. Ngày ở
dòng đầu tài liệu luật («bản thí điểm, 06/11/2026») là ngày ra bản, không phải số bản: đừng đòi đổi khi sửa nội dung.
Lịch sử là `git log` cộng mã quyết định ghi ngay trong câu luật (LV4).

## Bẫy

Thay `references/pitfalls.md`. Mỗi dòng là lỗi ĐÃ XẢY RA hay đã đo được ở repo này, kèm mục tài liệu ghi nó.

### Cổng đọc GitHub

| Lỗi | Thấy trong diff thế nào | Đã gặp ở |
|---|---|---|
| Lượt CI tạo 2 giây sau khi đổi base vẫn checkout ref merge của base cũ — lọc theo mốc đổi base đã lọt trên GitHub thật | Lọc lượt chạy theo thời điểm, hay dùng `pull_requests[]` của API (tính lúc đọc) | BM § Giới hạn đã biết (1) · KQ § Vì sao L8 lọt, và số đo sau đó |
| `edited`/`reopened` chạy ref merge cũ mà mang SHA mới | Thêm loại sự kiện vào `on.pull_request.types` của `cong-nhanh.yml` | comment `cong-nhanh.yml` · RD § Luật |
| Repo cá nhân chỉ chủ có admin: chỉ tin admin thì PR do chủ làm tác giả không ai duyệt được | Điều kiện người duyệt chỉ xét `admin` mà không xét `owner.type` | BM § Giới hạn đã biết (19) |
| `pull_request_review` xét environment theo `refs/pull/N/merge` — muốn chạy phải nới `gate`, nới thì workflow của PR lấy được khoá App | Workflow mới nghe `pull_request_review` trực tiếp | BM § Vì sao dùng hai sự kiện đặc quyền |
| API trả tối đa 250 commit / 3000 tệp: đọc thiếu thì «người có commit» thiếu | Bỏ chốt trần, hay đọc một trang | BM § Giới hạn đã biết (15) · RD § Luật |

### Xếp mức rủi ro

| Lỗi | Thấy trong diff thế nào | Đã gặp ở |
|---|---|---|
| Tệp trùng tên mô-đun chuẩn (`json.py`, symlink `json`) làm CI xanh giả | Nới `_MO_DUN_CHUAN` hay luật tên tệp | RD § Luật · BM § Giới hạn đã biết (8) |
| `.pyc` hash-based được nạp thay `.py` mà không so mã nguồn | Bớt đuôi ở `_MA_MAY` | comment `rui_ro.py` |
| Thêm `__init__.py` trong vùng test đổi tập test được nạp | Gỡ luật `__init__.py` cần duyệt | RD § Luật ("Test có sẵn") |
| PR chỉ sửa một tài liệu trong vùng đã khai vẫn ra `chan (cao)` — đúng, không phải báo oan | «Sửa» để tài liệu trong vùng thành Thường | PP § 2 (`[ĐÃ KIỂM: PR 28]`) |

### Luật và tài liệu

| Lỗi | Thấy trong diff thế nào | Đã gặp ở |
|---|---|---|
| Bộ cách cũ: «không mã nào đạt GIỮ», phần lớn chỉ có số tuân thủ | Luật mới đo «agent có làm theo không» thay cho lỗi chặn được | PP § 1 |
| Luật cổng đổi trong mã mà README § Luật còn chữ cũ — người ghi phiếu làm theo chữ cũ | `kiem_pr.py` đổi, `README.md` không có trong diff | RD § Luật · PP § 2 |
