# Hồ sơ `python-service` — `comitor-image-service`

Dịch vụ Python/uv FastAPI xử lý ảnh panorama 360° (enhance quang trắc, sau này mặt nạ trời, làm mờ, hình học),
cộng SDK TypeScript `@comitor-ai/image-client` ở `client-ts/`. Không Next, không Prisma, không database, không
Account, không giao diện, không workspace. Repo chọn hồ sơ này bằng `.claude/comitor-repo.json`
(`{"profile": "python-service"}`).

Hai luật đứng trên mọi hàng (AG § Luật thứ nhất, § Luật thứ hai): **không phép xử lý nào được đổi vật thể trong
ảnh**, và **mọi thay đổi có số đo**. Hàng nào không chắc thuộc nhóm nào thì hỏi: diff này có làm hai luật đó yếu đi
không?

```json profile
{
  "docs": {
    "AG": "AGENTS.md",
    "RD": "README.md",
    "TK": "docs/trien-khai.md",
    "ADR": "docs/adr/0001-bo-cuc-repo.md",
    "TD": "docs/TODO.md",
    "SDK": "client-ts/README.md"
  },
  "table": "references/profiles/python-service.md",
  "pitfalls": "references/profiles/python-service.md",
  "pitfallSections": {
    "Kiến trúc": ["Vòng gói và ảnh Docker"],
    "Dữ liệu & bảo mật": ["Bảo mật và tải ảnh", "Ảnh 360 và metadata"],
    "Quy ước": ["Công cụ và định dạng"],
    "Chất lượng": ["Cổng chất lượng và số đo", "Hợp đồng và SDK"]
  }
}
```

**Ngoại lệ khai trong repo.** `docs/babrik-image-service-handoff.md` là tài liệu bàn giao GỐC của Babrik, không phải
luật: chỗ nó nói khác AGENTS.md (trần residual 4,0, trần 36 MP, 20 tên phòng, dấu vĩ độ, đoạn mã `sharp`), AGENTS.md
và mã thắng — đã hiệu chỉnh có số đo (TD "Đã hiệu chỉnh theo dữ liệu thật"). Diff làm theo handoff ngược AGENTS.md
mới là phát hiện.

## Tài liệu quy định

Thay `references/governing-docs.md` ở bước 0. Cùng luật: lấy hàng KHỚP ĐẦU TIÊN, cộng các hàng **cộng thêm**; đọc
bằng `sections.mjs`, không Read cả file. Viết tắt: **AG** `AGENTS.md` · **RD** `README.md` · **TK**
`docs/trien-khai.md` · **ADR** `docs/adr/0001-bo-cuc-repo.md` · **TD** `docs/TODO.md` (627 dòng — chỉ đọc mục nêu)
· **SDK** `client-ts/README.md`. Comment đầu file và docstring module ở repo này là nơi giữ lý do và số đo — mục
"comment đầu" là bắt buộc đọc, không phải ghi chú.

| Đường dẫn đổi (glob) | Đọc | Mục quyết định |
|---|---|---|
| `service/pano_core/version.py`, `service/tests/test_quality.py`, `service/tests/test_quality/**` | AG | AG § Luật thứ nhất, § Luật thứ hai, § Cạm bẫy đã trả giá › Ảnh 360 ("Cổng đường nối mới hiệu chỉnh") · docstring `version.py`, `RESIDUAL_CEILING`, `SEAM_GROWTH_CEILING` |
| `service/pano_core/**` | AG; ADR | AG § Luật thứ nhất, § Cạm bẫy đã trả giá › Ảnh 360, § Cạm bẫy đã trả giá › Bộ nhớ · ADR § 5 · khối `[tool.importlinter]` của `pyproject.toml` |
| `service/pano_io/**` | AG; ADR; TK | AG § Cạm bẫy đã trả giá › Metadata, § Cạm bẫy đã trả giá › Bộ nhớ · ADR § 2, § 5 · TK § 3 Bộ nhớ · docstring `jpeg.py` (`MAX_PIXELS`, khoá chỉ-đọc) |
| `service/pano_api/image_fetch.py`, `service/pano_api/observability.py` | AG; TK; TD | AG § Cạm bẫy đã trả giá › Hợp đồng với Babrik ("URL presigned là thông tin xác thực") · TK § 2, § 7 · TD § 2.2 Tải ảnh qua URL · docstring đầu `image_fetch.py` |
| `service/pano_api/main.py`, `service/pano_api/contract.py`, `service/pano_api/errors.py` | AG; TK | AG § Cạm bẫy đã trả giá › Hợp đồng với Babrik · TK § 4 · docstring `contract.py` (`API_VERSION`, `REQUIRES_API_KEY`), `errors.py` (`PROBLEM_TYPES`) |
| `service/pano_api/**` (còn lại: `config`, `admission`, `pool`) | TK; AG | TK § 1, § 2, § 3 · AG § Cạm bẫy đã trả giá › Bộ nhớ |
| `service/tests/**` (còn lại) | AG | AG § Luật thứ hai ("Một cổng chưa từng thấy đỏ"), § Cạm bẫy đã trả giá › Metadata ("Kiểm ở mức byte") |
| `openapi.json`, `scripts/openapi.py` | SDK | SDK § Sinh lại khi hợp đồng đổi · docstring `scripts/openapi.py`, `contract.API_VERSION` |
| `client-ts/src/generated/**` | SDK | SDK § Sinh lại khi hợp đồng đổi (mã SINH, không sửa tay) |
| `client-ts/**` | SDK | SDK § Lỗi, § Không bao giờ log URL presigned, § Công cụ, § Phát hành · comment đầu `client.ts`, `errors.ts`, `retry.ts` |
| `Dockerfile`, `.dockerignore`, `compose.yaml` | TK; ADR | TK § 1, § 2, § 5, § 6 · ADR § 3, § 4 · comment trong chính file đó |
| `pyproject.toml`, `uv.lock`, `.python-version` | ADR; AG | ADR § 1, § 3, § 4 · AG § Ranh giới giấy phép model · comment trong `pyproject.toml` |
| `Makefile`, `.github/**`, `scripts/**` | AG; RD | AG § Quy ước ("Thêm cổng", "astral-sh/setup-uv", "make arch cần") · RD § Chạy thử · comment đầu file |
| `models/**`, `workshop/**` | AG; TD; ADR | AG § Ranh giới giấy phép model, § Quy ước ("Không commit") · TD § Ranh giới dùng trọng số · ADR § 6 |
| `fixtures/**` | AG | AG § Quy ước ("Không commit") · `fixtures/SOURCES.md` |
| `docs/**`, `README.md`, `AGENTS.md` | RD; AG; TD | RD § Tài liệu, § Chạy thử › Hiệu năng · AG § Luật thứ hai · TD § Quy ước |
| `.claude/**` | skill này | `MAINTAINING.md` §2, §7 |
| **cộng thêm:** mọi `*.py` | AG | AG § Quy ước ("Tài liệu tiếng Việt") · `[tool.ruff]`, `[tool.pyright]` của `pyproject.toml` |
| **cộng thêm:** mọi commit vào `main` | AG | AG § Quy ước ("Commit"), § Luật thứ hai |

## Phạm vi diff

Thay hai lệnh của bước 1.5 (và `--numstat` của đường nhanh) bằng cùng bộ loại trừ:

```
git diff -U0 <gốc>..HEAD -- ':(exclude)uv.lock' ':(exclude)client-ts/pnpm-lock.yaml' ':(exclude)client-ts/src/generated/**' ':(exclude)fixtures/**'
```

- **GIỮ trong diff** `openapi.json` và `service/tests/test_quality/gia_tri_vang.yml`: chúng được commit ĐÚNG để
  thay đổi hợp đồng và giá trị vàng hiện ra thành diff đọc được (docstring `scripts/openapi.py`; comment
  `pytest-regressions` trong `pyproject.toml`). Đọc chúng như mã.
- `client-ts/src/generated/**` ra khỏi `-U0` nhưng vẫn ở `--name-status`: nó đổi ⇔ `openapi.json` đổi, trong CÙNG
  commit (SDK § Sinh lại khi hợp đồng đổi). Một bên đổi mà bên kia không → hàng **Hợp đồng**.
- `fixtures/**` là JPEG nhị phân; nêu file thêm/xoá dưới **Đã kiểm**, kèm `SOURCES.md` có đổi theo không.
- Diff dài thì chia: `… -- service/pano_core service/pano_io` · `… -- service/pano_api scripts openapi.json` ·
  `… -- service/tests` · `… -- client-ts` · `… -- Dockerfile .dockerignore compose.yaml Makefile pyproject.toml .github`
  · `… -- '*.md' docs .claude`.

## Bản gốc hay bản chép

Bước 1.7 (`git show HEAD:package.json`) **thoát khác 0 ở repo này, và đó KHÔNG phải lệnh git hỏng**: gốc repo không
có `package.json` (dự án Python, `pyproject.toml`); `client-ts/package.json` là của gói SDK, tên
`@comitor-ai/image-client`, không nói gì về repo. Đi tiếp, đừng NOT REVIEWED.

Repo không phải `comitor-starter` và không phải module: mọi `.claude/skills/comitor-*/**` ở đây là BẢN CHÉP (gốc ở
starter) → `quality.md` F4 áp nguyên. Ba mảnh ngoài thư mục skill (`MAINTAINING.md` §1: khối `hooks` của
`.claude/settings.json`, dòng `/.claude-tmp/` của `.gitignore`, và
`.claude/comitor-repo.json` của chính hồ sơ này) thiếu mảnh nào thì ghi dưới **Đã kiểm** — cổng hỏng theo hướng MỞ.

## Đường nhanh

Thay danh sách đường dẫn nhạy cảm (ngưỡng 150 dòng và ba điều kiện kia giữ nguyên):

`service/pano_api/**`, `service/pano_io/jpeg.py`, `service/pano_core/version.py`, `service/tests/test_quality*`,
`pyproject.toml`, `uv.lock`, `Dockerfile`, `.dockerignore`, `compose.yaml`, `Makefile`, `scripts/**`, `.github/**`,
`openapi.json`, `models/**`, `client-ts/package.json`, `client-ts/pnpm-lock.yaml`, `client-ts/pnpm-workspace.yaml`,
`client-ts/src/client.ts`, `client-ts/src/errors.ts`, `client-ts/src/retry.ts`, `.claude/settings.json`,
`.claude/skills/comitor-review/scripts/**` — chỗ của xác thực, SSRF, bom ảnh, cổng chất lượng, hợp đồng với Babrik,
nội dung ảnh Docker, cổng máy và phụ thuộc.

## Lockfile

Thay đoạn Lockfile. HAI lockfile: `uv.lock` (dịch vụ) và `client-ts/pnpm-lock.yaml` (SDK). Cả hai ra khỏi `-U0`,
không ra khỏi review: có trong danh sách file thì nêu dưới **Đã kiểm** các gói đổi bản.

- Lock đổi mà manifest của nó (`pyproject.toml` / `client-ts/package.json`) không đổi → ❓.
- Gói xưởng model (`torch`, `torchvision`, `transformers`, `onnx`, `timm`, `accelerate`, `datasets`, `nvidia-*`)
  vào `[project].dependencies` hay nhóm phục vụ → 🔴 (AG § Ranh giới giấy phép model; ADR § 3, § 6). `make closure`
  chỉ so TÊN; bản `numpy` bị torch kéo lệch thì không cổng nào đỏ (ADR § 3) — nêu khi `numpy` đổi bản.
- `httpx`/`httpcore` đổi bản hay nới trần → 🟠 nếu PR không nói đã kiểm lại dây bẫy `_POOL_ATTR`
  (`image_fetch.py`, comment `httpx` trong `pyproject.toml`): cơ chế chống SSRF dựa vào thuộc tính riêng tư `_pool`.
- `pillow`/`simplejpeg` đổi bản → ❓ đã chạy cổng chất lượng chưa: giải mã trùng khít từng bit với giá trị vàng là
  tính chất được KHOÁ bằng test (ADR § 2 Bổ sung).
- `fastapi`/`starlette` đổi bản → `openapi.json` có thể đổi theo; `make openapi` bắt, review hỏi có phải đổi hợp đồng.
- `@hey-api/openapi-ts`, `ruff`, `pyright` ghim CHÍNH XÁC; đổi bản là đổi có chủ ý (SDK § Công cụ; comment `dev`
  trong `pyproject.toml`), không phải `update` — thiếu lý do trong thân commit → 🟡.
- Đoạn `better-auth` / `@comitor/ui` của module: n/a.

## Hàng

Phạm vi nhóm (thay dòng **Phạm vi** đầu bốn reference): **Kiến trúc** — `service/**` trừ `tests/`, `client-ts/src/**`
trừ `generated/`, `Dockerfile`, `.dockerignore`, `pyproject.toml`, `models/**`, `workshop/**`. **Dữ liệu & bảo mật**
— `service/pano_api/**`, `service/pano_io/**`, `service/pano_core/**`, `client-ts/src/**`, `Dockerfile`,
`compose.yaml`, `.github/**`, `pyproject.toml`. **Quy ước** — mọi `.py`, `.ts`, `.mjs`, `Makefile`, `pyproject.toml`,
YAML. **Chất lượng** — mọi diff.

Mã luật trong ngoặc của báo cáo: hàng **Áp**/**Đổi** dùng mã của reference module khi ô đó còn áp, không thì
`(AG § <mục>)` / `(TK § n)`; hàng **Thêm** dùng mã nêu trong ô.

| Nhóm | Hàng | Áp/Đổi/Bỏ/Thêm | Luật ở repo này (nguồn) |
|---|---|---|---|
| Kiến trúc | **Tầng** | Đổi | Module nói `lib/core`, `stores`, `hooks`, `route.ts`, `lib/api-client` — không thư mục nào có ở đây, nên áp nguyên văn là n/a ở mọi file trong khi ranh giới thật không ai canh. Luật: ba vòng `pano_core` < `pano_io` < `pano_api` (ADR § 5; `[tool.importlinter]`). `make arch` chỉ cấm tên đã liệt kê — danh sách `forbidden` THIẾU `os`, `io`, `socket`, `pathlib`, `urllib`, `httpcore`, `simplejpeg`, `asyncio`, `open(`, `np.load`/`np.save`/`np.fromfile`/`np.memmap`: grep dòng thêm của `pano_core/**` tìm chúng 🟠 (V1, AG § Luật thứ nhất mục 2). Thư viện ảnh (`PIL`, `simplejpeg`, `cv2`) ngoài gói `pano_io` 🟠 (V2, ADR § 5). Chạm mạng (`socket`, `httpx`, `httpcore`, `urllib.request`) ngoài `pano_api/image_fetch.py` 🟠 (V3, docstring dòng 3) — vòng qua `ImageFetcher` là 🔴 ở **Tiêm & bí mật**. Việc nặng CPU trên vòng lặp sự kiện thay vì `EnhancePool` 🟠 (V4, docstring `pool.py`). `client-ts/src/**`: HTTP chỉ qua hàm sinh ở `generated/sdk.gen`, không `fetch(` tự viết 🟠 (V5, comment đầu `client.ts`). |
| Kiến trúc | **Một luật** | Đổi | M1/M2/M4 áp với hằng của repo: `PROBLEM_TYPES` là danh mục DUY NHẤT của `type` (`errors.py`); `REQUEST_ID_PATTERN` một chuỗi cho ba chỗ (`contract.py`); trần byte đi từ `Config.max_upload_bytes` xuống `FetchPolicy`, không hằng thứ hai (`main.py` `AppState`). M3 (API giả) không có; thay bằng bản chép phía SDK: đổi tiền tố `type` (`TYPE_PREFIX` ⇄ `PROBLEM_TYPE_BASE`), dạng request id, mã mang `Retry-After` (`RETRY_AFTER_STATUSES` ⇄ `retry.ts`) mà bên kia không đổi CÙNG lần 🟠. Đã có HAI hàm che URL (`image_fetch.redact`, `observability.redact_url` — docstring cái sau tự nhận là "chỗ DUY NHẤT"): diff thêm bản thứ ba, hay thêm nơi gọi mà không hợp về MỘT, là M2 🟠; bản thân cặp đó là *Có từ trước*. |
| Kiến trúc | **Ranh giới** | Đổi | Module canh `server-only`/`"use client"`/cookie — không tồn tại ở đây, n/a ở mọi file. Ranh giới thật là TIẾN TRÌNH và dịch vụ ⇄ SDK: thứ đi qua hồ tiến trình là `bytes`, không `ndarray` (B1, docstring `pool.py`); hàm chạy trong hồ ở cấp module (pickle); mảng giải mã giữ CHỈ-ĐỌC — gỡ `flags.writeable = False` là cổng Rule #1 mù mà vẫn xanh 🟠 (B2, `jpeg.py`, ADR § 2 Bổ sung (b)); biến luồng của thư viện số đặt trong initializer TRƯỚC khi numpy nạp (`_init_worker`) 🟠. SDK chỉ chạy ở máy chủ: không CORS, khoá không tới trình duyệt — mã SDK dùng API trình duyệt hay gợi ý gọi từ client 🟠 (B3, `SECURITY_SCHEMES` ở `contract.py`). |
| Kiến trúc | **Chỗ đặt** | Đổi | P2–P6 (thực thể, điều hướng, route `page.tsx`, job) n/a. Luật: gói Python MỚI dưới `service/` phải có ở NĂM chỗ trong cùng diff — `COPY` của `Dockerfile` (thiếu = container chết lúc import 🔴), danh sách mở lại của `.dockerignore`, `root_packages` (+ `layers`) của `[tool.importlinter]` (thiếu = hợp đồng vòng không phủ nó 🟠), `[tool.coverage.run] source_pkgs` khi nó là lõi/vào-ra, `known-first-party` của ruff isort và `known_first_party` của deptry 🟡. Công cụ repo ở `scripts/`, xưởng model ở `workshop/` — cả hai KHÔNG vào ảnh (RD § Bố cục); ảnh CC0 ở `fixtures/` kèm dòng `SOURCES.md`; `fixtures-private/`, trọng số (`*.onnx`, `*.pt`), HDRI không bao giờ commit (AG § Quy ước "Không commit") — `fixtures-private/` là dữ liệu cá nhân 🔴, còn lại 🟠. P1 (đầu file nói VÌ SAO nó tồn tại) áp. |
| Kiến trúc | **Account** | Bỏ | Không Account, không phiên, không vai trò, không `better-auth`: bên gọi là máy chủ Babrik với một khoá dùng chung. A1–A6 áp ở đây là n/a vĩnh viễn; xác thực thật nằm ở hàng **Xác thực**. |
| Kiến trúc | **Giấy phép** | Thêm | Mọi model có mặt ở `models/allowlist.yaml` kèm giấy phép của MÃ, TRỌNG SỐ, DỮ LIỆU HUẤN LUYỆN; vùng xám ghi `GREY` (AG § Ranh giới giấy phép model). Trọng số NC (HorizonNet/LGT-Net/HoHoNet, SegFormer NVIDIA, SuperPoint/SuperGlue, DUSt3R/MASt3R) và bốn bẫy "trông dùng được" (Ultralytics, InsightFace, `pylsd`, LightGlue mặc định kéo SuperPoint) vào đường phục vụ, làm nhãn huấn luyện hay khởi tạo trọng số production 🔴 (GP1). Model nạp mà không có dòng allowlist 🟠 (GP2; trước khi file có — Phase 5 — mọi nạp model ở đường phục vụ là ❓). `transformers` vào `serving-ml` 🟠: nó kéo torch vào ảnh (ADR § 6). Mọi dòng `[project].dependencies` đi vào ảnh production — dòng mới không nêu lý do 🟡 (comment khung đầu khối). |
| Dữ liệu & bảo mật | **Workspace** | Bỏ | Không tenant, không database, không `workspaceId`: W1–W5 n/a. Cô lập giữa khách đến từ việc KHÔNG GIỮ GÌ — hàng **Không trạng thái**. |
| Dữ liệu & bảo mật | **Không trạng thái** | Thêm | URL presigned là thông tin xác thực DUY NHẤT; dịch vụ không giữ ảnh, không giữ URL, không có credential AWS. 🔴: ghi vào ảnh nguồn hay bất cứ PUT/POST nào về bucket (ST1, AG § Cạm bẫy đã trả giá › Hợp đồng với Babrik "Không bao giờ ghi vào ảnh nguồn"); trả URL thay byte ("Trả bytes"); cache ảnh hay URL (`functools.cache`, dict cấp module, đĩa) giữa các request (ST2, TD § 2.2 "không cache"); ghi ảnh khách ra đĩa (`tempfile`, `open(…, "w")`). 🟠: bỏ `cache-control: no-store` của câu trả lời ảnh (`main.py`, header khai trong `contract.py`); thêm `boto3`/SDK đám mây, IAM role, `COMITOR_AWS_*` (TK § 1 mục 3, TK § 2 "Không cấp IAM role") — máy không credential thì một lỗ SSRF cũng không lấy được gì từ `169.254.169.254`. |
| Dữ liệu & bảo mật | **Đường ghi** | Bỏ | Không có đường ghi dữ liệu: hai route enhance nhận byte/URL và trả byte. `requirePermission`, `@api-guard`, `withApiErrors`, `ReadOnlyFieldset`, Server Action không tồn tại; chốt duy nhất là khoá API — hàng **Xác thực**. |
| Dữ liệu & bảo mật | **Xác thực** | Thêm | Middleware `request_context` (`main.py`) đòi `X-API-Key` ở MỌI đường trừ `PUBLIC_PATHS` — kể cả `/docs`, `/openapi.json`. 🔴: thêm đường vào `PUBLIC_PATHS`, dời phép kiểm sang dependency/route (đường mới quên là đường mở), nhánh bỏ qua khi `auth_required` sai điều kiện (XT1). So khoá bằng `secrets.compare_digest` trên BYTE latin-1 — đổi sang `==` hay so `str` 🟠 (XT2; `str` ngoài ASCII ném TypeError trước khối `try`, 8e3a836). Route mới cần khoá khai `openapi_extra=REQUIRES_API_KEY` — thiếu thì SDK sinh ra không gửi khoá và 401 lúc chạy 🟠 (XT3, docstring `REQUIRES_API_KEY`). `/v1/health`, `/v1/ready` không khoá, không phép kiểm nặng (TK § 4) 🟠. `load_config()`: khoá ≥ 32 ký tự, từ chối placeholder, bắt buộc ở `uat`/`production` — nới bất kỳ điều nào 🔴 (TK § 3). |
| Dữ liệu & bảo mật | **Toàn vẹn** | Đổi | I1–I8 (thẻ phiên bản, giao dịch, migration, giờ) n/a — không database (TK § 1 mục 1). Toàn vẹn ở đây là của ẢNH ĐẦU RA (AG § Luật thứ nhất). 🟠: đổi một hằng hay một phép của `pano_core` (điểm kẹp gain, stretch, lift, vibrance, bề rộng đo) mà `PIPELINE_VERSION` không đổi CÙNG commit (TV1, docstring `version.py`); `gia_tri_vang.yml` đổi mà thân commit không nêu số đo và vì sao (TV2); nâng `RESIDUAL_CEILING` 10,0, `SEAM_GROWTH_CEILING` 1,26 hay ngưỡng độ nét mà không có quyết định của người — thân commit/PR nêu người quyết thì hạ ❓ (TV3, AG § Luật thứ nhất mục 3, › Ảnh 360 "Cổng đường nối"); phép CỤC BỘ mới (CLAHE, guided filter, gain theo ô) không kèm số đo residual + seam và không tự thêm mình làm ca phía xanh (TV4); mất metadata gốc — ảnh ra dựng từ buffer nên EXIF/ICC/XMP/GPano phải chép tường minh, mất GPano mà không vào `X-Degraded` (TV5, AG › Metadata); `cv2.imread/imwrite/imdecode/imencode` (ruff `banned-api` bắt). |
| Dữ liệu & bảo mật | **Tiêm & bí mật** | Đổi | S1–S3, S8–S10 (XSS, CSS, redirect của trình duyệt, kho ảnh, CSV, CSP) n/a. **SSRF** (TS1, docstring `image_fetch.py`, TD § 2.2) — 🔴 cho: tải phía máy chủ không qua `ImageFetcher`; ghim IP rời `connect_tcp` sang viết lại URL + `sni_hostname` (pool khoá theo IP, chứng chỉ tên miền thứ hai không bao giờ được kiểm); phân giải hai lần; chỉ lọc bản ghi xấu thay vì từ chối cả tên; nới `https`/cổng 443/userinfo; `follow_redirects=True` hay bỏ kiểm lại từng chặng (≤ 3); bỏ hạ IPv4-mapped/6to4/NAT64; cho unix socket; bớt vùng cấm. **Bí mật** (TS2, AG › Hợp đồng với Babrik; TK § 7): URL presigned ra log chỉ qua `redact` (host + băm); khoá không bao giờ log; `detail` không chứa URL/khoá/đầu vào; 500 `INTERNAL` không `detail`; 422 không dội `input`/`ctx` (`problem_for_validation`); ngoại lệ lạ log TÊN lớp + vị trí, không thông điệp (`_where`) — `log_event(…, x=str(exc))` hay `detail=str(exc)` với lỗi có thể mang URL 🔴. **Bom ảnh** (TS3, docstring `jpeg.py`): magic byte trước khi mở; kiểm `MAX_PIXELS` từ header của CẢ Pillow lẫn libjpeg TRƯỚC khi cấp phát — bỏ lớp nào 🔴; đếm byte khi đọc luồng, không tin `Content-Length`; `Accept-Encoding: identity`; nâng `MAX_PIXELS` không kèm đo lại bộ nhớ 🟠. **SDK** (TS4, comment đầu `errors.ts`, SDK § Không bao giờ log URL presigned): `message`/`stack`/thuộc tính lỗi và sự kiện không mang URL ảnh hay khoá; lỗi gốc không gắn `cause`; `redirect: "manual"` — nới bất kỳ điều nào 🔴. S5 áp: cấu hình chỉ đọc ở `config.py` (`os.environ` khác chỉ là biến luồng trong `pool.py`), không `.env`/khoá trong diff 🔴. |
| Dữ liệu & bảo mật | **Hướng hỏng** | Đổi | H1 (danh bạ), H3 (giao diện tra `code`) n/a. **H5 ĐẢO**: dịch vụ TỰ sinh 429 `overloaded` kèm `Retry-After` từ `AdmissionGate` — đúng thiết kế (docstring `admission.py`); báo module H5 ở đây là báo sai. Chống lụt theo IP vẫn ở ingress, miễn trừ health/ready (TK § 1 mục 4). 🟠: cấu hình sai không nổ lúc khởi động (`load_config` trong factory, không lúc import — HH1, TK § 3); liveness trỏ `/v1/ready`, hay năng lực tuỳ chọn làm `ready` đỏ (HH2, TK § 4); bỏ `queue_limit` hay `Retry-After` (HH3); `PoolBroken` không dựng lại hồ, hay thử lại CHÍNH ảnh vừa giết worker (HH4, `pool.py`); lỗi của bên gọi (IDNA, URL sai) thành 500 — SDK coi 500 là lỗi dịch vụ: thử lại, đếm cầu dao, đổ sang nhà cung cấp dự phòng (HH5, 94c501f); mất một phần lời hứa mà vẫn trả ảnh mà không ghi `X-Degraded` (HH6); số worker tính theo đường tốt 851 MB thay vì đường lùi 1337 MB, hay đọc `sysconf` trước cgroup (HH7, TK § 3 Bộ nhớ). 🔴: `CMD` dạng shell, hay `--timeout-graceful-shutdown` ≥ `stop_grace_period` (HH8, TK § 5 — hỏng ở MỌI lần deploy). H4 (lỗi cấu hình nổ, lỗi gửi nuốt có log), H7, H8 áp. |
| Quy ước | **i18n** | Bỏ | Không giao diện, không `messages/`, không `next-intl`. Chữ cho người duy nhất là `title`/`detail` của problem — tiếng Việt cố định, bên gọi KHÔNG so khớp trên nó (mô tả `title` trong `PROBLEM_SCHEMA`); đổi `type` thuộc hàng **Hợp đồng**. |
| Quy ước | **Màu & UI** | Bỏ | Không `.tsx`, không `.css`, không `@comitor/ui`; SDK không có giao diện. U1–U7 n/a. |
| Quy ước | **Ngôn ngữ & tên** | Đổi | L1: định danh MỚI tiếng Anh (AG § Quy ước "Tài liệu tiếng Việt") 🟡 — nhưng mã đã có định danh tiếng Việt không dấu (`_giai_ma_diem_anh`, `theo_cpu`, `gia_tri`, `test_gia_tri_vang`, khoá giá trị vàng như `tang_duong_noi`, sự kiện log `khoi_dong`, trường `loi`/`vi_tri`/`nguon`): KHÔNG báo cái đã có, KHÔNG đòi đổi tên — đổi khoá vàng là viết lại file vàng, đổi tên sự kiện/trường log là đổi thứ người vận hành grep. Đường dẫn `/v1/…`, slug `type` (kebab), `operation_id` (camelCase) tiếng Anh 🟠. L3 theo PEP 8 (module snake_case, lớp PascalCase, hằng HOA); tên ma trận một chữ HOA (`M`, `R`, `K`) là cố ý — ruff không bật `N` (comment `[tool.ruff.lint]`); TS camelCase. L4 ĐỔI: dịch vụ này làm cho khách và đối tác cụ thể, và tài liệu của nó gọi tên họ (RD § Tài liệu; AG § Ranh giới giấy phép model) — đúng loại ngoại lệ mà L4 cho repo tự khai, dù `AGENTS.md` của repo chưa ghi nó thành một dòng ngoại lệ (review không báo việc gọi tên; thiếu dòng khai thì ⚪ đề xuất thêm): Babrik, Imagtor, babrik-engine, Deep Image (nhà cung cấp dự phòng), Photo Sphere Viewer, AWS/EC2/S3/GHCR/Vercel, `sharp`, tên model và bộ dữ liệu ở mục giấy phép đều được gọi tên. Thay vào đó báo: đặc thù Babrik đi vào `pano_core` 🟡 (RD dòng 7–8: bộ từ vựng tên phòng là cấu hình theo khách). L2, L5 áp. |
| Quy ước | **Comment** | Áp | C1–C5 nguyên văn; repo viết comment/docstring DÀI kèm số đo có chủ ý (`Dockerfile`, `Makefile`, `pyproject.toml`, `jpeg.py`). Docstring tiếng Việt; gạch nối ASCII `-`, không `−` (ruff `RUF002` bắt — máy). Đính chính giữ dấu vết ("⚠ Trần cũ là 36 MP … **Con số đó sai.**") là khuôn của repo (C5). |
| Quy ước | **Kiểu** | Đổi | K2, K3 viết cho TS `noUncheckedIndexedAccess`/spread — chỉ áp cho `client-ts/`. Python (pyright `strict`): `Any` mới (ruff tắt `ANN401` nên máy không bắt), `cast(…)` không kèm comment lý do (khuôn ở `PinningBackend.__init__`), `# type: ignore`/`# pyright: ignore`/`# noqa` không lý do 🟡 (🟠 khi nó giấu lỗi thật). `assert` canh an toàn trong mã phục vụ 🟠 — biến mất dưới `python -O`; dùng `raise` (docstring `_PinnedTransport`). K4: nới `[tool.ruff]`, `[tool.pyright]` (kể cả `executionEnvironments`), `fail_under`, hợp đồng import-linter, `per_rule_ignores` của deptry, `client-ts/biome.json`, `tsconfig.json` 🟠. K5: kiểu đi qua JSON khai ở model pydantic / lược đồ, SDK dùng `generated/types.gen` không khai lại 🟡. |
| Quy ước | **Công cụ** | Thêm | `Makefile` là cổng DUY NHẤT: thêm cổng thì sửa `Makefile`, YAML chỉ gọi `make` — cổng viết trong YAML 🟠 (CC1, AG § Quy ước "Thêm cổng"; ngoại lệ duy nhất có lý do: `image.yml`). Ghim: `ruff`/`pyright`/`@hey-api/openapi-ts`/`typescript` chính xác, `setup-uv` đủ số (không `@v10`), action ghim SHA — nới ghim 🟠 (CC2). `uv sync --locked` không `--frozen`, `prerelease = "disallow"`, `pnpm install --frozen-lockfile` — gỡ 🟠 (CC3, comment `env` của `Makefile`, `[tool.uv]`). Thêm/bớt nhóm phụ thuộc của ảnh thì `closure` của `Makefile` và `uv sync` của `Dockerfile` đổi CÙNG commit 🟠 (CC4). Mục ngoại lệ deptry có lý do 🟡. `make arch` giữ `PYTHONPATH=service` (AG § Quy ước "make arch cần"). |
| Chất lượng | **Đúng** | Đổi | Bán kính ảnh hưởng — bảng anh em của module (`lib/api-client`, API giả, `messages/`, điều hướng) không có ở đây. Anh em của repo này: route ở `main.py` → `contract.py` (responses, header), `PROBLEM_TYPES`, `openapi.json`, `client-ts/src/generated/**`, `client.ts`/`errors.ts`/`retry.ts`, `test_contract.py`; hằng `pano_core` → `PIPELINE_VERSION`, `gia_tri_vang.yml`, các trần ở `test_quality.py`; `FetchPolicy.max_bytes` ⇄ `Config.max_upload_bytes`; nhóm phụ thuộc ⇄ `closure` ⇄ `Dockerfile`; gói mới → năm danh sách (hàng **Chỗ đặt**); mục tiêu `Makefile` ⇄ `.PHONY`, `check:`, bảng mục tiêu ở RD § Chạy thử; biến môi trường ⇄ bảng TK § 3. Ảnh 360 (AG § Cạm bẫy đã trả giá › Ảnh 360): phép cửa sổ/chia ô quấn ngang (cột 0 kề cột W-1); thống kê cân `cos_latitude_weights`, không đếm điểm ảnh; pitch dương nhìn LÊN, vĩ độ trả ra dương ở trên — dấu nội bộ của `stats` không chép sang toạ độ trả Babrik 🟠. Bộ nhớ: đường cong tông bằng LUT 256 mục, không nâng cả ảnh lên float (AG › Bộ nhớ) 🟠. Async: lời gọi chặn (`getaddrinfo`, giải mã) không chạy thẳng trên vòng lặp (`asyncio.to_thread`, hồ tiến trình) 🟠. |
| Chất lượng | **Test** | Đổi | E3–E6, E8 (khung, store, API giả, Playwright) n/a. Giữ E1 cho `pano_core`/`pano_io` (sàn 90 % chỉ đo hai gói đó — `source_pkgs`; tầng HTTP cố ý không sàn), E2, E7. Thêm: cổng MỚI (chất lượng, cấu trúc, hợp đồng) phải có ca ĐỎ chạy thật — tự tiêm vi phạm rồi đòi cổng đỏ, như `test_quality.py` 🟠 (ET1, AG § Luật thứ hai "Một cổng chưa từng thấy đỏ"); test metadata kiểm ở mức BYTE (`b'GPano:ProjectionType' in img.info['xmp']`), không `getxmp()` — xanh giả khi thiếu `defusedxml` 🟠 (ET2, AG › Metadata); `make check` chạy offline — test không gọi mạng thật, TLS dùng `trustme` cục bộ 🟠 (ET3, comment `check.yml`); test chậm (suy luận model) mang `@pytest.mark.slow`, ngân sách lượt ấm < 1 phút (RD § Chạy thử) 🟡; đổi lời khai hợp đồng mà `test_contract.py` (so lược đồ với câu trả lời thật, hai chiều) không đổi 🟠; SDK: Vitest cạnh file, sàn độ phủ 90 trên mã viết tay. |
| Chất lượng | **Hợp đồng** | Đổi | H2–H7 của module (mã lỗi `errors.code.*`, route `page.tsx`, `x-request-id` liên module, testid) n/a. Luật (docstring `contract.py`, `errors.py`, `scripts/openapi.py`; AG › Hợp đồng với Babrik): `openapi.json` SINH từ mã và commit cùng thay đổi mã (`make openapi` bắt lệch — máy); `client-ts/src/generated/**` sinh lại CÙNG commit (SDK § Sinh lại khi hợp đồng đổi) 🟠; `operation_id` tường minh camelCase — đổi một cái đã có là đổi tên hàm SDK 🔴. Chuỗi `type` đã có KHÔNG BAO GIỜ đổi; bỏ route, bỏ/đổi header, đổi kiểu → bộ route `/v2` chạy song song, không sửa tại chỗ 🔴 (HD1, `API_VERSION`). Header của 200 (`X-Pipeline-Version`, `X-Structural-Residual`, `X-Alteration-Class`, `X-Illuminant-Gains`, `X-Degraded`, `Cache-Control`) là lời hứa: gửi mà không khai hay khai mà không gửi 🟠 (HD2). Hợp đồng Babrik: trả byte; không ghi ảnh nguồn; tên phòng theo `PREDEFINED_ROOMS` (33), không 20 tên của handoff; wireframe `lines[]`; cân nghiêng trả `segments[]` + `estimate` 🟠. API công khai của SDK (`createImageClient`, `isFallbackEligible`, kiểu lỗi) đổi phá vỡ → changeset `major` 🟠. H1 áp nguyên (nơi tiêu thụ gãy 🔴). |
| Chất lượng | **Trạng thái** | Bỏ | Không màn hình: bốn trạng thái, "id tra không ra tên", `NotYetActive`, 375px n/a. Trạng thái ĐỌC ĐƯỢC của dịch vụ (health/ready, `X-Degraded`) ở hàng **Hướng hỏng**. |
| Chất lượng | **Số đo** | Thêm | AG § Luật thứ hai. Thay đổi xuất phát từ phép đo (hiệu năng, bộ nhớ, residual, ngưỡng, recall) ghi CON SỐ vào thân commit — thiếu 🟡, 🟠 khi nó dời một hằng `pano_core`, một trần hay một ngưỡng (SD1). Con số kèm máy, ngày, tải ("máy rảnh"/"máy bận"); số đo máy dev không được viết như số production — c7i.xlarge 4 vCPU phải đo trên EC2 🟡 (SD2). Bảng hiệu năng của RD không chép sang tài liệu khác 🟡 (SD3, RD § Chạy thử › Hiệu năng). Mục TODO đánh ✅ kèm số đo hoặc test + link PR, không "trông ổn" (TD § Quy ước) 🟡. Cổng mới: thân commit ghi đã thấy nó đỏ thế nào (cùng luật với ET1). |
| Chất lượng | **Tối giản** | Áp | Nguyên văn. Cộng: không khai phụ thuộc chưa dùng (deptry bắt — máy; comment cuối `[project].dependencies`). |
| Chất lượng | **Tài liệu** | Đổi | F1 thay bằng mục **Số bản** dưới đây. F2, F5, F6 bỏ — repo không có file khung cho module chép, không khuôn `comitor-page`, không `@comitor/ui`. F3 áp với tài liệu của repo: danh sách cổng `make check` và bảng mục tiêu ở RD § Chạy thử khớp `check:` của `Makefile`; RD § Bố cục khớp thư mục; bảng biến ở TK § 3 khớp `config.py`; RD § Trạng thái, TD khớp việc đã làm; AGENTS.md, SDK README khớp mã. Lệnh `sections.mjs --check-table --profile python-service` đỏ vì diff đổi một đề mục hồ sơ này trỏ tới 🟡 — sửa hồ sơ ở starter. F4 áp (bản chép skill — mục **Bản gốc hay bản chép**). F7 áp: `type(scope): mô tả tiếng Việt`, chữ thường, không chấm cuối; nhánh `type/mo-ta-khong-dau` (AG § Quy ước "Commit"). Handoff lệch AGENTS.md không phải phát hiện (đầu file này). |

Mẫu số bảng Kiểm: **Kiến trúc /5** (Tầng, Một luật, Ranh giới, Chỗ đặt, Giấy phép) · **Dữ liệu & bảo mật /5** (Không
trạng thái, Xác thực, Toàn vẹn, Tiêm & bí mật, Hướng hỏng) · **Quy ước /4** (Ngôn ngữ & tên, Comment, Kiểu, Công cụ) ·
**Chất lượng /6** (Đúng, Test, Hợp đồng, Số đo, Tối giản, Tài liệu) — 20 hàng thay cho 21 của SKILL.md § 2.

## Công cụ máy

Thay ba công cụ của bước 2:

- `node .claude/skills/comitor-ui/scripts/audit.mjs` — **bỏ**: không `.tsx`/`.css`, và skill `comitor-ui` không chép
  sang repo này.
- `check-refs.mjs` của `comitor-test` — **bỏ**: skill đó không có ở đây. Thay bằng
  `node .claude/skills/comitor-review/scripts/sections.mjs --check-table --profile python-service` khi diff đổi
  AGENTS.md, README.md, `docs/trien-khai.md`, `docs/adr/0001-bo-cuc-repo.md`, `docs/TODO.md` hay `client-ts/README.md`
  — một ✗ là phát hiện của hàng **Tài liệu**.
- Kiểm sau `--fix` (chỉ khi có cờ): `.py` → `uv run ruff check <file>` và `uv run ruff format --check <file>`;
  `client-ts/**` → `biome check` chạy TRONG `client-ts/` (cấu hình và `node_modules` ở đó; `pnpm exec biome check` ở
  gốc không chạy được) — dạng được phép là `pnpm --dir client-ts exec biome check <file>`. Lệnh bị từ chối thì ghi
  dưới **Đã kiểm** "chưa kiểm format bản sửa — tác giả chạy `make fmt lint check-client`", không bỏ qua im lặng. Sửa chạm import hay chữ ký
  hàm thì nói rõ cần `make types arch`.

`make check` thì **không** — như `pnpm check` ở module: cổng của tác giả (`check.yml`, `image.yml` chỉ chạy tay —
phút Actions có hạn).

## Không bao giờ sửa

Thay danh sách của bước 4 (luật "file bẩn ở bước 1.6" và "bản chép skill" giữ nguyên):

- `openapi.json` — sinh từ mã (`make openapi-write`); sửa tay là đúng ca cổng `make openapi` sinh ra để chặn;
- `client-ts/src/generated/**` — sinh từ `openapi.json` (`pnpm generate`);
- `service/tests/test_quality/gia_tri_vang.yml` và mọi file giá trị vàng — đổi nó là quyết định có số đo (hàng
  **Toàn vẹn**);
- `uv.lock`, `client-ts/pnpm-lock.yaml`;
- `fixtures/**` (ảnh CC0 + `SOURCES.md`), `client-ts/.changeset/*.md` (ghi chú phát hành của tác giả);
- `docs/babrik-image-service-handoff.md` — tài liệu gốc của bên khác;
- `Dockerfile`, `.dockerignore`, `compose.yaml`, `Makefile`, `.github/**` — một "đơn giản hoá" ở đây đổi ảnh, cổng
  hay deploy; mỗi dòng mang lý do đã đo ngay cạnh nó;
- mọi con số đo trong tài liệu và comment — "sửa" một số đo là bịa số đo.

## Mức

Thay các dòng sau của danh sách Mức (SKILL.md § 6); dòng không nêu giữ nguyên.

- **🔴** — BỎ: `workspaceId`, route ghi thiếu/sai chốt quyền, `@api-guard`, chốt chỉ ở giao diện, XSS, open redirect,
  bí mật vào bundle, migration, hợp đồng liên module, `better-auth`. THÊM: đường mới vào `PUBLIC_PATHS` hay phép kiểm
  khoá vòng qua được; tải phía máy chủ không qua `ImageFetcher` hay nới một chốt SSRF; URL presigned/khoá vào log,
  `detail`, thông điệp lỗi trả ra, hay lỗi/sự kiện của SDK; ghi vào ảnh nguồn, cache ảnh/URL, trả URL thay byte; bỏ
  kiểm trần điểm ảnh trước khi cấp phát; đổi `type` problem đã có, đổi `operation_id`, bỏ route/header không qua
  `/v2`; trọng số NC hay gói xưởng model vào đường phục vụ; `fixtures-private/` vào git hay vào ảnh; gói mới thiếu
  ở `COPY` của `Dockerfile`; `CMD` dạng shell. Giữ: hành vi hay nơi gọi gãy; tiêm; SSRF; bí mật trong diff.
- **🟠** — BỎ: luật ngoài `lib/core/`, chuỗi ngoài `messages/`, danh bạ, 403/404, thẻ phiên bản, Server Action, component
  gói, mã màu, `fetch` ngoài `lib/api-client/` (thay bằng V5), API giả, ranh giới Account, file khung. THÊM: vi phạm
  vòng (V1–V4); `PIPELINE_VERSION` không đổi theo `pano_core`; nâng trần/ngưỡng chất lượng không có người quyết;
  giá trị vàng đổi không số đo; phép cục bộ mới không đo lại trần; mất metadata không `X-Degraded`; mảng giải mã hết
  chỉ-đọc; cổng mới chưa thấy đỏ; việc nặng trên vòng lặp sự kiện; route mới thiếu `REQUIRES_API_KEY`; `generated/`
  lệch `openapi.json`; lỗi của bên gọi thành 500; nới ghim công cụ hay cổng; cổng viết trong YAML. Giữ: khả năng lỗi,
  hồi quy, một luật viết hai lần, nơi gọi/anh em không đổi theo, fail-open, test không thể đỏ.
- **🟡** — thêm: thân commit thiếu số đo cho thay đổi dựa trên phép đo (🟠 khi dời hằng/trần — hàng **Số đo**); số đo
  dev viết như số production; định danh tiếng Việt MỚI.

## Số bản

Thay hàng F1 của `quality.md`. Repo **không có CHANGELOG và không có `version:check`** — đừng đòi. `version = "0.1.0"`
trong `pyproject.toml` không được dùng ở đâu (`package = false`); đừng đòi tăng nó. Ba số bản, mỗi cái đổi vì một lý
do riêng (docstring `contract.API_VERSION`):

| Số | Ở đâu | Đổi khi | Thiếu thì |
|---|---|---|---|
| `PIPELINE_VERSION` | `service/pano_core/version.py`, `enhance@YYYY-MM-DD` (ngày hành vi đổi) | ĐIỂM ẢNH đầu ra đổi — mọi hằng hay phép của `pano_core`, kể cả bước mã hoá của `pano_io` | 🟠 — Babrik lưu nó vào `EnhanceVersion.settings`; một báo cáo "ảnh trông khác" không truy được |
| `API_VERSION` | `service/pano_api/contract.py`, semver | MAJOR = `/v1` → route `/v2` song song; MINOR: thêm route, header, trường, loại lỗi; PATCH: khai bù cho khớp hành vi có sẵn; sửa câu chữ mô tả: KHÔNG đổi | 🟠 khi `openapi.json` đổi hình dạng mà số không đổi đúng bậc |
| `@comitor-ai/image-client` | `client-ts/package.json` qua changesets (`client-ts/.changeset/*.md`) | PR đổi hành vi của gói: `pnpm changeset`, mô tả tiếng Việt kèm số đo (SDK § Phát hành); không bao giờ sửa tay `version` hay publish tay | 🟠 khi `client-ts/src/**` (trừ test) đổi hành vi mà không có changeset |

⚠ `release-client.yml` chạy khi đẩy lên `main` mà `client-ts/**` hay `openapi.json` đổi — đó là phút Actions thật; PR
chỉ-tài-liệu không đụng hai đường đó.

## Bẫy

Thay `references/pitfalls.md`. Mỗi dòng là lỗi ĐÃ XẢY RA hay đã đo được ở repo này, kèm commit hoặc mục tài liệu ghi
nó. Như ở module: gần như không dòng nào làm `make check` đỏ.

### Vòng gói và ảnh Docker

| Lỗi | Thấy trong diff thế nào | Đã gặp ở |
|---|---|---|
| `make arch` thiếu `PYTHONPATH=service` đỏ với «Could not find package» — nghe như lỗi cấu hình import-linter | Đổi dòng `arch:` của `Makefile` | `19a63db` · AG § Quy ước ("make arch cần") |
| Hồ tiến trình vỡ VĨNH VIỄN sau một lần OOM: health vẫn ok, mọi request hỏng tới khi khởi động lại tay | `BrokenExecutor` không bắt, hay bắt mà không dựng lại hồ | `24177ab` · TK § 5 |
| `CMD` dạng shell: `docker stop` 30,29 s, exit 137, vẫn trả 200 cho request mới 0,7 s sau SIGTERM — ở mọi lần deploy | `CMD uvicorn …` không phải mảng JSON | `24177ab` · TK § 5 |
| `init: true`/tini đổi exit code dừng 0 → 143, hỏng smoke test và policy restart, mà chỉ giảm mồ côi 2 → 1 | `init: true`, `ENTRYPOINT ["tini"…]` | `24177ab` · TK § 5 |
| Tag `uv:python3.14-bookworm-slim` pull được nhưng chứa uv 0.9.30; `COPY --from=<chuỗi>` bỏ qua digest đã ghim | Ảnh nền không digest; `COPY --from=ghcr.io/…` viết thẳng | `24177ab` · comment `Dockerfile` |
| `.dockerignore` danh sách cấm: thư mục dữ liệu khách mới lọt vào layer, đọc lại bằng `docker history` | Dòng cấm thay cho dòng mở lại; mở cả `service/` | `24177ab` · comment `.dockerignore` |
| Thiếu `python-multipart`: ảnh dựng xanh, container lên, hỏng ở request có tệp đầu tiên | Gỡ phụ thuộc deptry báo "không import" | `f353125` · comment `pyproject.toml` |
| N tiến trình con × N luồng BLAS: CPU 100 % mà thông lượng tụt | Bỏ `_init_worker` hay đặt biến luồng sau khi nạp numpy | `f353125` · docstring `pool.py` |

### Bảo mật và tải ảnh

| Lỗi | Thấy trong diff thế nào | Đã gặp ở |
|---|---|---|
| Viết URL thành `https://<ip>/` + `sni_hostname`: pool khoá theo IP, chứng chỉ của tên miền thứ hai không bao giờ được kiểm | Ghim IP ngoài `connect_tcp` | `4433fcd` · TD § 2.2 Tải ảnh qua URL |
| Resolver tuỳ biến của aiohttp bị ngắn mạch với IP literal — `https://10.0.0.5/` đi thẳng | Đổi thư viện HTTP của `image_fetch` | `4433fcd` |
| 422 mặc định của FastAPI dội nguyên `input` — chữ ký `X-Amz-Signature` nằm trong thân lỗi, Babrik chuyển nó lên trình duyệt | Trình xử lý 422 dùng `exc.errors()` nguyên văn | `03a12fb` · AG § Cạm bẫy đã trả giá › Hợp đồng với Babrik |
| Ngoại lệ lạ thành `text/plain` 500 không `x-request-id`, traceback mang thông điệp có thể chứa URL | Ném tiếp khỏi middleware; log `str(exc)` | `03a12fb` · TK § 7 |
| `compare_digest` trên `str` ngoài ASCII ném TypeError trước `try`: ai chạm cổng cũng sinh được 500 | So khoá dạng `str` | `8e3a836` |
| Nhãn IDNA sai, nhãn > 63 ký tự ra 500 `internal`: SDK thử lại, đếm cầu dao, đổ sang dự phòng | Chỉ bắt `OSError`/lỗi httpx quanh phân giải, `URL.host`, `send` | `94c501f` |
| SDK theo redirect sang origin khác mang `X-API-Key` và thân chứa URL presigned | `redirect` khác `"manual"` | `8e3a836` · SDK § Không bao giờ log URL presigned |
| `scrub()` bình phương: 100 000 ký tự trong `detail` chặn vòng lặp sự kiện của Babrik 15 s | Regex hay vòng lặp lồng trên chữ do máy chủ gửi | `94c501f` |
| `release-client.yml` để mặc định `persist-credentials`: token ghi nằm trong `.git/config` suốt lúc cả cây devDependency chạy | `actions/checkout` thiếu `persist-credentials: false`; quyền ở mức workflow | `8e3a836` · comment `release-client.yml` |

### Ảnh 360 và metadata

| Lỗi | Thấy trong diff thế nào | Đã gặp ở |
|---|---|---|
| Ngược dấu pitch: mặt chiếu nhìn xuống, dải mặt nạ dưới đường mái — "đủ hợp lý để tốn một giờ" | Dấu `lat`/`pitch` chép từ `stats` hay handoff A.2 sang toạ độ trả ra | AG § Cạm bẫy đã trả giá › Ảnh 360 ("Pitch dương nhìn LÊN") |
| `getxmp()` trả `{}` khi thiếu `defusedxml` — test GPano xanh giả | Test metadata qua `getxmp()` | AG § Cạm bẫy đã trả giá › Metadata ("Kiểm ở mức byte") |
| `sharp` xoá sạch metadata; con số 74–95 ms của handoff đo trên đường không chép metadata | So hiệu năng với handoff như cùng phép việc | AG § Cạm bẫy đã trả giá › Metadata ("sharp") |
| Trần 36 MP theo handoff trả 413 cho 76/164 ảnh thật (11008×5504 = 60,6 MP) | Hằng lấy từ tài liệu bàn giao, không từ kho ảnh | `9a9330d` · docstring `MAX_PIXELS` |
| `sysconf` trong container báo RAM của host: 30 worker rồi bị cgroup giết lúc khởi động, không log | Đọc RAM không qua `/sys/fs/cgroup` | `9a9330d` · TK § 3 Bộ nhớ |
| Đường float32 ngây thơ 645 MB đỉnh mỗi ảnh 15 MP, LUT 297 MB — nửa số request đồng thời | Nâng cả ảnh lên float cho một phép tông | AG § Cạm bẫy đã trả giá › Bộ nhớ |
| Giải mã bằng Pillow 987 MB cho một ảnh 60,6 MP, simplejpeg 229 MB | Đổi thư viện/cách giải mã ở `pano_io` không kèm số đo đỉnh RSS | `2b417b5` · ADR § 2 Bổ sung |

### Cổng chất lượng và số đo

| Lỗi | Thấy trong diff thế nào | Đã gặp ở |
|---|---|---|
| Trần residual 5,0 hiệu chỉnh chỉ trên CC0 đỏ trên ảnh thật hợp lệ (5,36 và 7,22); handoff đề xuất 4,0 | Trần/ngưỡng mới hiệu chỉnh trên một bộ ảnh | `9a9330d` · AG § Luật thứ nhất |
| Cổng không nhìn byte đã giao: JPEG q92 → 40 làm byte teo 66–71 % mà 0/11 giá trị vàng nhúc nhích | Phép đo mới chạy TRƯỚC `encode()` | `8fbb412` |
| Residual mù với làm mờ: mờ Gauss lọt 11/11; độ nét toàn cục lọt mờ cục bộ 20 % 11/11 | Chỉ số toàn cục thay cho chia ô; một thống kê thay cho hai | `8fbb412` |
| Gain cục bộ 8 ô hợp lệ tới x1,220, cách trần đường nối 1,26 có 3 % | Phép cục bộ mới không đo lại `SEAM_GROWTH_CEILING` | `cd89bab` · AG § Cạm bẫy đã trả giá › Ảnh 360 ("Cổng đường nối mới hiệu chỉnh") |
| Số đo lúc máy bận chép vào README rồi phải thay bằng trung vị lúc máy rảnh | Số đo không ghi máy, ngày, tải | `824aa93` · RD § Chạy thử › Hiệu năng |

### Hợp đồng và SDK

| Lỗi | Thấy trong diff thế nào | Đã gặp ở |
|---|---|---|
| `openapi.json` không khai header, problem+json hay khoá; 404/405/422/500 không phải problem+json — SDK tin từng chữ | Route/header mới mà `contract.py` không khai | `03a12fb` · SDK § Sinh lại khi hợp đồng đổi |
| `{"model": P, "content": {"application/problem+json": {}}}` đặt lược đồ dưới `application/json` thừa | Khai lỗi qua `model=` thay vì `problem_responses()` | `03a12fb` · docstring `ServiceApp` |
| `image/jpeg` không `format: binary` cho kiểu SDK `unknown`/`string` thay vì `Blob` | Đổi `IMAGE_RESPONSE` | `03a12fb` · comment `IMAGE_RESPONSE` |
| `X-Request-Id` chiều vào không khai: dịch vụ dội lại mọi giá trị, dài bao nhiêu cũng được | Header đọc trong middleware mà không qua `REQUEST_ID_PATTERN` | `8e3a836` |
| Proxy trả 3xx: SDK cho `unexpected` + dự phòng, lời gọi thứ 6 mở cầu dao — `baseUrl` sai lặng lẽ đẩy mọi ảnh sang nhà cung cấp dự phòng | Đổi phân loại lỗi hay `isFallbackEligible` | `94c501f` · SDK § Lỗi |
| `apiKey` ngoài ASCII: `Headers.set` ném trước `fetch` thành `network` ×3 và dự phòng — khoá hỏng mà không ai biết | Kiểm khoá dời khỏi lúc tạo client | `8e3a836` |
| 200 `image/jpeg` rỗng hay HTML dán nhãn ảnh được trả như ảnh, cầu dao ghi thành công | Bỏ kiểm SOI `FF D8 FF` ở SDK | `8e3a836` |
| PR #8 merge nhầm base, phải mở #9 để đưa Phase 4 vào `main` | PR có base khác `main` | `96c6553` |

### Công cụ và định dạng

| Lỗi | Thấy trong diff thế nào | Đã gặp ở |
|---|---|---|
| ruff `RUF002` bắt dấu trừ Unicode `−` trong docstring tiếng Việt | Ký tự giống ASCII trong docstring | `19a63db` · AG § Quy ước ("Tài liệu tiếng Việt") |
| `astral-sh/setup-uv@v10` trả 404 — không có tag major di động | Action ghim bằng tag ngắn | `19a63db` · AG § Quy ước ("astral-sh/setup-uv") |
| `httpx>=0.29` bất khả thi được uv giải bằng bản tiền phát hành `1.0.dev6`, mọi cổng xanh | Gỡ `prerelease = "disallow"` | `4433fcd` · comment `[tool.uv]` |
| uv báo ràng buộc bất khả thi bằng cách đổ cho nhóm `workshop` — trỏ sai hướng | Ràng buộc `httpx` mới; dòng 2.x là gói `httpx2` | `f353125` · comment nhóm `dev` |
| `--frozen` im lặng cài lock cũ và thoát 0 | `uv sync --frozen` ở `Makefile`/`Dockerfile`/CI | comment `env` của `Makefile` |
| `make fix` thiếu tiền tố `-`: `ruff check --fix` thoát lỗi, bước format không chạy, `fmt` đỏ với thông điệp lạc đề | Đổi mục tiêu `fix` | comment `fix` của `Makefile` |
| pyright 1.1.414 không nhận `typeCheckingMode` trong `executionEnvironments` — «unrecognized setting» rồi đỏ | Nới pyright theo thư mục bằng `typeCheckingMode` | comment `[tool.pyright]` |
| `AsyncIterator` cho `@asynccontextmanager` báo «asynccontextmanager is deprecated» | Chú thích kiểu trả về của lifespan | `f353125` · comment `lifespan` ở `main.py` |
| Script đánh dấu TODO cắt `line[5:]` trên tiền tố 4 ký tự, ăn mất backtick của nhãn `[M]` | Cắt chuỗi theo số byte/ký tự trên chữ có emoji | `542a514` |
| `pnpm/action-setup` không `package_json_file` đọc `package.json` ở gốc — repo không có — đỏ «No pnpm version is specified» | Bước setup pnpm mới ở CI | comment `check.yml` |
