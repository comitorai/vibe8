# Hồ sơ `library-web-ui` — repo `comitor-web-ui` (gói `@comitor-ai/web-ui`)

Gói npm PRIVATE (GitHub Packages): block web trình bày + primitive + token `--wb-*` + manifest (shadcn
registry), cộng `apps/docs` (Next.js xem block — không xác thực, không database, không publish). CÙNG mã chạy
ở hai nơi: app Redesign cài gói; dự án export của khách nhận BẢN CHÉP mã nguồn (QD #13). Không có Prisma,
workspace, Account, `messages/`, API giả, route handler. Repo chọn hồ sơ này bằng `.claude/comitor-repo.json`
= `{"profile": "library-web-ui"}`.

```json profile
{
  "docs": {
    "AG": "AGENTS.md",
    "CL": "CLAUDE.md",
    "KT": "docs/KIEN-TRUC.md",
    "QD": "docs/QUYET-DINH.md",
    "MF": "docs/MANIFEST.md",
    "RD": "README.md",
    "SK": "skills/comitor-web-ui/SKILL.md",
    "SM": "skills/comitor-web-ui/MAINTAINING.md",
    "NG": "docs/NGUON-GOC.md"
  },
  "table": "references/profiles/library-web-ui.md",
  "pitfalls": "references/profiles/library-web-ui.md",
  "pitfallSections": {
    "Kiến trúc": ["Ranh giới server/client", "Bản chép và manifest"],
    "Dữ liệu & bảo mật": ["Nội dung và nơi nhận dữ liệu"],
    "Quy ước": ["Token và màu"],
    "Chất lượng": ["Bố cục và trạng thái", "Phát hành và CI", "Tài liệu lệch mã"]
  }
}
```

## Tài liệu quy định

Thay `governing-docs.md`. Viết tắt: **AG** `AGENTS.md` · **CL** `CLAUDE.md` · **KT** `docs/KIEN-TRUC.md` · **QD**
`docs/QUYET-DINH.md` · **MF** `docs/MANIFEST.md` · **RD** `README.md` · **SK** / **SM** `SKILL.md` / `MAINTAINING.md`
của `skills/comitor-web-ui/` · **NG** `docs/NGUON-GOC.md` · **SP** `skills/comitor-web-ui/references/pitfalls.md`
(một bảng, không đề mục — Read cả file, 20 dòng). Đọc bằng
`node .claude/skills/comitor-review/scripts/sections.mjs docs/KIEN-TRUC.md '§ 4, § 9'` như module. QD (52 dòng) và NG
(20 dòng) đọc cả file: các đề mục "Đã chốt" của QD trùng tiền tố nên selector chỉ tới được cái đầu.

⚠ **AG viết TRƯỚC khi có mã** (§ 3 "Kiến trúc dự kiến", § 5 "Lệnh dự kiến"). Chỗ AG mâu thuẫn với cấu hình đã
có — `package.json` (`exports`, peer, `scripts`), `.github/workflows/*`, `.npmrc` — thì CẤU HÌNH là thực tế và AG đã
cũ: ghi dưới **Đã kiểm**, không phải phát hiện của PR (danh sách đã biết: § Bẫy › Tài liệu lệch mã). Ngoài các chỗ
đó, AG thắng như module. Diff SỬA tài liệu cho lệch mã vẫn là hàng **Tài liệu**.

Hàng khớp ĐẦU TIÊN, cộng các hàng "cộng thêm":

| Đường dẫn đổi (glob) | Đọc | Mục quyết định |
|---|---|---|
| `src/content/**`, `src/blocks/**/schema.ts`, `src/blocks/**/meta.ts`, `src/blocks/types.ts` | KT; AG; MF; CL | KT § 2 2.1, 2.2, 2.3, 2.4 · AG § 4 ("API props là hợp đồng", "Mọi block đọc được"), § 8 ("Nội dung thật của khách") · MF § 3, § 5 · CL § Khi viết một block |
| `src/blocks/**/*.tsx` (variant, `parts.tsx`, lá client) | KT; AG; CL | KT § 2 2.1, § 3 3.2, § 4, § 6, § 9 · AG § 4 ("Không chép nội dung", "Chuỗi mẫu"), § 8 ("use client chỉ ở block", "Nội dung thật của khách") · CL § Khi viết một block · NG toàn bộ |
| `src/primitives/**` | KT; AG | KT § 2 2.1, § 3 3.2, § 4, § 6, § 9 · AG § 8 ("use client chỉ ở block") |
| `src/tokens/**`, `styles.css` | KT; AG; RD | KT § 3 · AG § 3 ("Theme:"), § 8 ("Tailwind v4 CSS-first") · RD § Dùng › 1 · NG toàn bộ (công thức màu) |
| `src/manifest/**`, `src/registry/**`, `scripts/build-manifest.mjs`, `scripts/lib/imports.mjs`, `scripts/check-manifest.mjs` | MF; KT; AG | MF § 1, § 2, § 3, § 4, § 5 · KT § 5 · AG § 4 ("Mọi block đọc được") |
| `src/lib/**` | KT | KT § 2 2.3 (`inline.ts`: link an toàn), § 9 (`dates.ts`, `format.ts` không `Intl`) |
| `apps/docs/**` | KT | KT § 7, § 8, § 9 ("Ảnh mẫu", "pnpm dev:pkg") |
| `skills/comitor-web-ui/**` | SM; SK | SM § 1, § 2, § 3, § 4 · SK § Mười luật, § Prop của dev |
| `.changeset/**`, `CHANGELOG.md` | AG; RD; MF | `.changeset/README.md` toàn bộ · AG § 4 ("API props là hợp đồng"), § 6 · RD § Phát hành · MF § 5 |
| `docs/khao-sat/**`, `docs/NGHIEN-CUU-BLOCKS.md`, `docs/NGUON-GOC.md` | CL; AG | CL § Khi khảo sát website · AG § 4 ("Không chép nội dung") |
| `package.json`, `pnpm-lock.yaml` | AG; CL; KT; RD | AG § 4 ("Chỉ peerDependencies") · CL § Giới hạn khi sửa ("Không thêm dependency nặng") · KT § 5 · RD § Entry |
| `.github/**`, `scripts/**`, `tsup.config.ts`, `biome.json`, `tsconfig.json`, `pnpm-workspace.yaml`, `.npmrc` | chính file đó; AG; RD | comment đầu file (lý do từng dòng ở đó) · AG § 6 · RD § Lệnh |
| `.claude/skills/comitor-review/**` | skill này | `MAINTAINING.md` §1, §7 của skill — bản CHÉP từ starter (`quality.md` F4) |
| `.claude/settings.json` | skill này | `MAINTAINING.md` §2 (hook) |
| `docs/**` (còn lại), `README.md`, `AGENTS.md`, `CLAUDE.md`, `TASKS.md` | CL; QD | CL § Trước khi viết dòng mã đầu tiên · QD § Còn mở · `quality.md` F3 |
| **cộng thêm:** mọi `src/**/*.ts`, `src/**/*.tsx` | AG; KT | AG § 4 ("Không import", "Chỉ peerDependencies") · KT § 5 |
| **cộng thêm:** mọi file có chữ người đọc | KT; AG | KT § 2 2.1 · AG § 4 ("Chuỗi mẫu") · comment đầu `src/primitives/ui-text.ts` |
| **cộng thêm:** `src/**/index.ts`, `exports` của `package.json` | RD; AG; KT | RD § Entry · AG § 3 ("Exports:") · KT § 4 (barrel không re-export vòng qua file client) |
| **cộng thêm:** mọi PR đổi API công khai (props, slot, variant, token, export, khoá manifest) | MF; AG | `.changeset/README.md` toàn bộ · MF § 5 · AG § 4 ("API props là hợp đồng") |
| **cộng thêm:** block mới, đổi `uses` hay mô tả variant | SM; KT | SM § 2 (`blocks.md` sinh) · KT § 8 (trang `/blocks/<type>`) |

## Phạm vi diff

`-U0` loại thêm, ngoài `pnpm-lock.yaml`: `':(exclude)skills/comitor-web-ui/references/blocks.md'` (SINH bằng `pnpm
skill:sync` — chỉ xét nó có đổi CÙNG block hay không, SM § 2) và `':(exclude)apps/docs/public/**'` (SVG mẫu tự vẽ).
Hai thứ đó vẫn ở `--name-status`. Khối `/* @generated default-theme:start */ … end */` của `styles.css` không loại
được bằng pathspec: đọc lướt, chỉ hỏi nó có đổi CÙNG `src/tokens/default-theme.ts` không.

`dist/`, `r/`, `manifest.json` bị gitignore: chúng xuất hiện trong `--name-status` là 🔴 (CL § Giới hạn khi sửa).

Diff dài thì chia nhóm: `-- src/lib src/content src/tokens styles.css` · `-- src/primitives` · `-- src/blocks` ·
`-- src/manifest src/registry src/index.ts scripts` · `-- apps/docs` · `-- '*.md' .changeset skills .claude .github`.

## Bản gốc hay bản chép

`"name": "@comitor-ai/web-ui"` — repo không phải starter, nên `.claude/skills/comitor-review/**` là BẢN CHÉP (F4
như module: sửa ở `comitor-starter` rồi chép lại). Ngược lại `skills/comitor-web-ui/**` là BẢN GỐC của skill đó
(SM § 1; `comitor-ui/MAINTAINING.md` §5 của starter): sửa được, và phải đi CÙNG PR với block đổi; bản chép nằm ở
`.claude/skills/comitor-web-ui/` của `comitor-redesign`. Repo không có `comitor-ui`, `comitor-page`, `comitor-test`.

## Đường nhanh

Thay danh sách đường dẫn nhạy cảm của module bằng: `src/content/**`, `src/lib/inline.ts`, `src/lib/video.ts`,
`src/tokens/**`, `styles.css`, `src/manifest/**`, `src/registry/**`, `src/blocks/types.ts`, `src/blocks/**/schema.ts`,
`src/blocks/**/meta.ts`, `src/**/index.ts`, `src/primitives/map-embed.tsx`, `src/primitives/video-embed.tsx`,
`scripts/**`, `.github/**`, `.changeset/config.json`, `tsup.config.ts`, `biome.json`, `tsconfig.json`, `package.json`,
`pnpm-lock.yaml`, `pnpm-workspace.yaml`, `.npmrc`, `.claude/settings.json`, `.claude/skills/comitor-review/scripts/**`
— chỗ của an toàn nội dung, hợp đồng công khai, ranh giới server/client, token, phụ thuộc và cổng. Cộng hai điều
kiện không viết được bằng glob: diff không THÊM hay XOÁ dòng `"use client"`, và không `.changeset/*.md` nào mang
`major`. Ba điều kiện còn lại (≤ 150 dòng, sidecar, `--full`) như module.

## Lockfile

Như module, với ba dòng thay cho `better-auth` và `@comitor/ui`:

- `@comitor/ui` xuất hiện mới trong importer `.` (gói gốc) → 🔴 (AG § 4 "Không import"; QD #7).
- Gói mới trong `dependencies` của gói gốc = gói mới cho MỌI dự án export (KT § 5: dependency của khách là
  `dependencies` của các mục đã chép) → 🟠 khi docs không có lý do (CL § Giới hạn khi sửa; AG § 4 "Chỉ
  peerDependencies" — thư viện tương tác cần lý do trong docs).
- Phụ thuộc của importer `apps/docs` (Next, PostCSS) đổi bản → chỉ nêu dưới **Đã kiểm**; không chạm gói phát hành.

## Hàng

| Nhóm | Hàng | Áp/Đổi/Bỏ/Thêm | Luật ở repo này (nguồn) |
|---|---|---|---|
| Kiến trúc | **Tầng** | Đổi | Tầng của gói: `src/lib` (thuần) → `src/content` (bộ dựng schema), `src/tokens` → `src/primitives` → `src/blocks/<type>/` → `src/manifest`, `src/registry` (AG § 3; KT § 2). Block ghép primitive + token, không tự vẽ lại thứ primitive đã có (CL § Khi viết một block); bố cục khác = FILE khác, không một component với 40 prop điều kiện (AG § 3 "Variant:"; KT § 2); `schema.ts` theo LOẠI, không theo variant (QD #15; KT § 2.2); không `fetch`, không gọi AI trong `src/` (AG § 1; QD #5). Module sai vì T1–T8 nói `lib/core`, `stores`, `hooks`, `route.ts`, `lib/api-client` — không có thư mục nào, áp nguyên văn là cả hàng n/a. Mức 🟠 (schema theo variant, dựng lại primitive) · 🟡 còn lại |
| Kiến trúc | **Một luật** | Đổi | Mỗi luật một chỗ: giới hạn độ dài + an toàn của slot ở bộ dựng `src/content`, không zod trần (KT § 2.3); chữ dựng sẵn ở `ui-text.ts`; ngày/tiền ở `src/lib/dates.ts`, `format.ts` (KT § 9); tone → màu ở bảng khối 4 của `styles.css`, block không viết nhánh màu theo tone (KT § 3.2); danh sách đóng `ICON_NAMES`, `FIELD_NAMES`, `FLIGHT_PARAMS`, `TOUR_PARAMS`, `TONES` khai MỘT lần; tên trường dùng chung (`eyebrow`, `title`, `primaryCta`, `items`…) không đặt tên thứ hai cho cùng vai (KT § 2.2); app Redesign đọc manifest bằng CHÍNH `manifestSchema`, không schema thứ hai (MF đầu file). Module sai vì M1–M4 nói route ⇄ page ⇄ API giả ⇄ `navigation.ts`. Mức 🟠 |
| Kiến trúc | **Ranh giới** | Đổi | Server/client: `"use client"` chỉ ở lá tương tác; block tĩnh render được từ Server Component và `renderToStaticMarkup` (AG § 8; KT § 4). Hằng thuần không ở file `"use client"`, barrel không re-export vòng qua file client — máy canh (`verify:directives`); review canh block tĩnh mới tự gắn `"use client"`, lá client không cần thiết, và prop qua ranh giới: chỉ DỮ LIỆU, hàm duy nhất là Server Action cho `action` của `form/*` (SP). Chữ client vẽ không dùng `Intl`, "hôm nay" tính ở server (KT § 9); bảng nổi chỉ vẽ khi mở (KT § 9). Module sai vì R1 đòi `import "server-only"` mà gói chạy CẢ hai phía, và R3, R5–R7 (cookie, `page.tsx`, `searchParams`, bảng khai) không có. Mức: mất directive / hằng qua proxy client 🔴 · `"use client"` trên block tĩnh 🟠 · còn lại 🟡 |
| Kiến trúc | **Chỗ đặt** | Đổi | Block = `src/blocks/<type>/{schema.ts, meta.ts, <variant>.tsx, index.ts}` + lá client và `parts.tsx` cạnh nó (KT § 2); primitive dùng ở nhiều loại → `src/primitives/`. Đầu file block: bố cục (máy tính / điện thoại) + "Nguồn cảm hứng: <tên bộ \| khảo sát ngành X>", không URL site khách, khớp `inspiration` của meta (AG § 4 "Không chép nội dung"; NG; `src/blocks/types.ts`). App docs đọc registry (`generateStaticParams` từ `BLOCK_TYPES`) — không danh sách block viết tay thứ hai trong `apps/docs` (KT § 8). Khảo sát ở `docs/khao-sat/<nganh>.md`, chỉ bố cục/hành vi, ảnh chụp ngoài repo (CL § Khi khảo sát website). Module sai vì P1–P6 nói `components/`, `navigation.ts`, bản đồ route, job nền. Mức 🟡 · thiếu dòng nguồn cảm hứng 🟠 |
| Kiến trúc | **Ranh giới gói** | Đổi (thay **Account**) | Hai gói không import nhau: `@comitor/ui` trong `src/` do máy chặn (`check:boundaries`); review canh phần máy KHÔNG quét — `apps/docs`, dependency mới kéo nó bắc cầu, mã CHÉP từ `@comitor/ui` (AG § 4 "Không import"; QD #7). Gói không làm app chrome (sidebar, bảng dữ liệu, form nhập liệu phức tạp), không gọi AI, không chứa chữ/ảnh/logo/CSS của site khảo sát (AG § 1). File chép sang dự án export đứng được một mình: import tương đối có `.js`, không alias, chỉ gói đã khai, không mã sinh lúc build (AG § 2 mục 7; KT § 5); `next/*` không import trong `src/` (`next` không phải peer — block render cả ngoài Next). Module sai vì A1–A6 là ranh giới Comitor.Account, gói không có xác thực; ranh giới thật của gói là với `@comitor/ui` và với dự án export. Mức: import `@comitor/ui` 🔴 · bản chép không đứng được 🟠 |
| Dữ liệu & bảo mật | **Workspace** | Bỏ | Không database, không tenant, không phiên: `src/` không Prisma; `apps/docs` không xác thực, không database (KT § 8). W1–W5 không có gì để hỏi. Diff THÊM database hay phiên vào `apps/docs` → hàng **Ranh giới gói** 🟠 |
| Dữ liệu & bảo mật | **Nơi nhận dữ liệu** | Đổi (thay **Đường ghi**) | Nơi dữ liệu của khách đi là prop CỦA DEV, không bao giờ là `content`: `action` của `form/*`; `action`, `params`, `dateFormat`, `airports` của `search/*`; `selectAction`, `selectParam`, `query` của `flight-results/*` (KT § 4 4.1, 4.2, 4.3; SK § Prop của dev; SK § Mười luật, luật 7). Trường mới trong schema nội dung quyết định đích gửi, tên tham số hay `method` → 🔴: nội dung đến từ AI và site khác. Tên ô gửi đi theo danh sách đóng `FIELD_NAMES`, ô bẫy `_hp`, `consent=on`; bỏ trống `action` = xem trước, không gửi đi đâu (KT § 4.1). Module sai vì G1–G6 là `requirePermission` trên route handler — gói không có đường ghi phía máy chủ; đường ghi thật là form trên site của KHÁCH. Mức 🔴 · còn lại 🟠 |
| Dữ liệu & bảo mật | **Toàn vẹn** | Đổi | Toàn vẹn của MÔ HÌNH TRANG: đổi variant không mất nội dung — trường riêng của variant là tuỳ chọn trong schema loại, chỉ variant đó liệt nó trong `uses` (KT § 2.2; QD #15). Mọi slot chữ có `max`, danh sách có `min`/`max` (KT § 2.3; AG § 8 "Nội dung thật của khách"). Giá chuyến bay ĐÃ GỒM thuế phí, `baseFare` chỉ ở Chi tiết (KT § 4.3). Siết schema đã phát hành (trường bắt buộc mới, `max` nhỏ hơn, enum bớt giá trị) làm mô hình trang đã lưu thôi `parse` → hàng **Hợp đồng**. Module sai vì I1–I8 nói `PUT` có thẻ phiên bản, `$transaction`, migration, múi giờ của phiên. Mức 🟠 |
| Dữ liệu & bảo mật | **Tiêm & bí mật** | Đổi | S1 áp MẠNH hơn module: MỌI `content` là dữ liệu không tin được (AI, site khác). Không `dangerouslySetInnerHTML`; nội dung giàu là khối có kiểu, không HTML (KT § 2.3; QD #19); link qua `url()`/`link()` (chặn `javascript:`, `data:`), chữ trong câu qua `src/lib/inline.ts` (link không an toàn chỉ còn chữ); ảnh chỉ `http(s)` hay `/đường-dẫn`; `src` của iframe dựng từ nội dung — `VideoEmbed` qua allowlist host (`src/content/fields.ts`, `src/lib/video.ts`), `MapEmbed` `embedUrl` chỉ qua `url()` nên một iframe tới host mới là ❓/🟠; `target="_blank"` kèm `rel="noopener noreferrer"`. S2: không `style`/class dựng từ chuỗi nội dung; màu site chỉ qua `createTheme()` → `themeToStyle`/`themeToCss`; class động bị cấm (`check:boundaries` luật 5). S5: không token trong `.npmrc` (comment đầu file), không `NODE_AUTH_TOKEN`/khoá trong diff. `inspiration`, comment, mẫu không chứa URL site khách (AG § 4; `check:manifest` luật 4). S3, S4, S6–S10 n/a — gói không có máy chủ. Module sai vì S2/S5/S6 trỏ `appFrameAccentFor`, `lib/env.ts`, `withApiErrors`, và coi người đăng nhập là nguồn dữ liệu — ở đây nguồn là AI và site lạ. Mức 🔴 |
| Dữ liệu & bảo mật | **Hướng hỏng** | Đổi | Block hỏng theo hướng ĐỌC ĐƯỢC: thiếu ảnh → khung giữ chỗ có nhãn (KT § 6; QD #9); link không an toàn → chữ trần; màu người dùng chọn không đạt → `createTheme` sửa và ghi `theme.warnings`, không ném (KT § 3.3); nội dung không chờ hiệu ứng cuộn mới hiện (KT § 4); form chạy cả khi chưa có JS (`method="post"`), `action` hàm trả `{ ok: false }` → hiện lỗi (KT § 4.1); video, bản đồ chỉ tải khi bấm. H7 (`catch` rỗng) áp. Module sai vì H1–H6, H8 nói danh bạ Account, 429, `lib/env.ts`, `sendMail`. Mức 🟠 · H7 🟡 |
| Quy ước | **i18n** | Đổi | Không `messages/`, không `next-intl`. Chữ DỰNG SẴN (nhãn trợ năng, "Xem thêm", nút điều hướng) chỉ ở `src/primitives/ui-text.ts`, đủ `vi` (mặc định) và `en`, chọn theo prop `locale` (KT § 2.1; đầu `ui-text.ts`); mọi chữ khác đến từ `content` — chữ cứng trong JSX của block/primitive là 🟠. Thiếu khoá `en` thì `tsc` đỏ (`const en: UiText`); NGHĨA thì review đọc (N2). Chữ có số/đơn vị là hàm trong `ui-text.ts`, không ghép ở block (N4). Nhãn trường (`title`) của bộ dựng tiếng Việt (KT § 2.3); `sample` tiếng Việt, ngắn, trung tính (AG § 4 "Chuỗi mẫu"); ngày/tháng/tiền qua `src/lib`, không `Intl` (KT § 9). Module sai vì N1, N3, N5–N8 nói `messages/`, `t()`, `ComitorLocaleProvider` — áp nguyên văn là báo mọi chuỗi của `ui-text.ts`. Mức 🟠 · N2 🟡 |
| Quy ước | **Màu & UI** | Đổi | NGƯỢC module ở U1, U3, U4. Gói SỞ HỮU token `--wb-*` (KT § 3): khai token là đúng chỗ, nhưng khối `:root` của `styles.css` SINH từ `src/tokens/default-theme.ts` (`pnpm tokens:sync`; `check:tokens`) — sửa tay là 🟠; token mới có ở `src/tokens/names.ts` và cặp đo ở `src/tokens/pairs.ts`. Block: chữ, viền, nền chỉ token BỀ MẶT; token theme chỉ theo cặp nền + chữ tự đủ tương phản (KT § 3.2); không nhánh màu theo tone; không màu cứng (máy: `check:boundaries` luật 4 — miễn trừ mới ở `COLOR_EXEMPTIONS` phải có lý do). Ba vai trò `--wb-x` / `-foreground` / `-ink` như U2. Trợ năng nằm trong block: WCAG 2.2 AA mọi tone × theme khó (`lint:a11y`), mục tiêu chạm ≥ 44px (`--wb-control-height`), `wb-focus-ring`, `<label>` thật, cấp tiêu đề tách khỏi cỡ, băng trượt có nút dừng + `prefers-reduced-motion` (KT § 6; AG § 3 "a11y và responsive"). KHÔNG `@comitor/ui` (→ **Ranh giới gói**); primitive của gói trước khi tự vẽ; không thư viện tương tác — `<details>`, `<dialog>`, Popover API (KT § 4). `apps/docs` ngoài các luật màu này (khung trang docs, không phải block). Module sai vì U1 cấm khai token và U3 buộc dùng `@comitor/ui` — ở đây ngược lại; U5–U6 (`audit.mjs`, cạm bẫy `@comitor/ui`) bỏ. Mức 🟠 · U2, U7 🟡 · mục tiêu chạm < 44px 🟠 |
| Quy ước | **Ngôn ngữ & tên** | Đổi (L4) | L1–L3, L5 áp: id block `<type>/<variant>` kebab-case tiếng Anh, giá trị knob/enum tiếng Anh, comment tiếng Việt (KT § 2). L4 áp như module (chặn tên dự án, đối tác khác của đội; dữ liệu của tính năng thì không) — ở repo này nó cụ thể thành bốn chỗ gọi tên thương hiệu khác mà KHÔNG là phát hiện: (a) `src/primitives/brand-icons.ts`, `brand-icon.tsx` — simple-icons CC0, chỉ để link tới kênh của chính thương hiệu đó (NG; KT § 9 "Logo thương hiệu"); (b) dòng "Nguồn cảm hứng" đầu file block và `inspiration` — tên bộ tham khảo hay "khảo sát ngành X", không URL site khách (AG § 4 "Không chép nội dung"); (c) `docs/NGUON-GOC.md`, `docs/NGHIEN-CUU-BLOCKS.md`, `docs/khao-sat/**`; (d) dữ liệu nghiệp vụ có thật (sân bay, hãng bay trong mẫu kết quả, nhà cung cấp bản đồ/video, văn bản luật). (a) và (d) là dữ liệu của tính năng; (b), (c) là ghi nguồn mà repo BẮT BUỘC (NG). Ngoài bốn chỗ đó repo CHẶT hơn module: chuỗi mẫu trung tính (AG § 4 "Chuỗi mẫu") — tên thương hiệu thật trong `sample` hay ví dụ là 🟡 dù không phải đối tác. Mức như module |
| Quy ước | **Comment** | Áp | như module |
| Quy ước | **Kiểu** | Đổi (K5) | K1–K4 áp (`strict` + `noUncheckedIndexedAccess` ở `tsconfig.json`). Biome TẮT `noNonNullAssertion` và `noArrayIndexKey` có lý do (KT § 9 "Luật noArrayIndexKey"), nên `!` không bị máy bắt — review vẫn hỏi K2. K5 ĐỔI: kiểu `content`/`style` SUY từ zod (`z.infer` của `schema.ts`), không interface thứ hai; kiểu manifest từ `manifestSchema` (MF đầu file). Module sai vì K5 trỏ `lib/contracts/`, không có ở đây. Mức như module |
| Chất lượng | **Đúng** | Đổi (bảng anh em) | Logic, luật React, `null` như module. Bán kính ảnh hưởng của gói: `schema.ts`/`meta.ts` của loại → `uses`, `sample` của MỌI variant → `manifest.json` (`check:manifest`) → `r/<mục>.json` → `skills/comitor-web-ui/references/blocks.md` (sinh, `check:skill`) → trang `/blocks/<type>` và `/mau/*` của app docs (`apps/docs/app/mau/pages.ts`) → changeset. Token → `names.ts`, bảng tone của `styles.css`, `pairs.ts`, `meta.comitor.themeTokens`. Khoá `ui-text.ts` → `vi` + `en`. Primitive client hay hằng mới → barrel `index.ts` (KT § 4). Export mới → `exports` của `package.json`, `smoke:entries`, RD § Entry. `parts` của variant ↔ khoá `classNames`. Prop của dev đổi → SK § Prop của dev. Đổi cách đọc import (`scripts/lib/imports.mjs`) hay bao đóng file của `build-manifest.mjs` → `check:manifest` (mỗi mục `r/` đóng import, đọc lại mã đã chép như dự án export nhận) cộng `pnpm export:verify` bên comitor-redesign. Module sai vì bảng anh em nói `lib/api-client`, API giả, `navigation.ts`, `messages/`. Mức như module |
| Chất lượng | **Test** | Đổi | E1, E2, E7 áp cho `src/lib`, `src/tokens`, `src/content`, `src/manifest` (vitest, `*.test.ts` cạnh file). Block: render × tone × `vi`/`en` × chữ dài gấp đôi do `check:blocks` canh, nhưng CHỈ trên `sample` — variant mà mẫu chung không cho thấy bố cục cần `sample` riêng (KT § 2.2); `uses` khai trường mà variant không vẽ là lời hứa sai (`check:blocks` mục 2). Đổi `createTheme` hay phép đo tương phản → ca theme khó mới trong test token hay `lint:a11y`. E3–E6, E8 (danh sách khung, store, API giả, Playwright) n/a. Module sai vì E4–E6 nói store, router giả, Playwright chế độ giả. Mức 🟠 · E7 🟡 |
| Chất lượng | **Hợp đồng** | Đổi | Hợp đồng công khai = props (`content`, `style`, prop của dev), tên/kiểu slot, variant, id block, nút style và giá trị enum của nó, token `--wb-*`, `parts`/`classNames`, entry của `exports`, `FIELD_NAMES`/`FLIGHT_PARAMS`/`TOUR_PARAMS`, khoá `meta.comitor` (AG § 2 mục 5; AG § 4 "API props là hợp đồng"; KT đầu file; MF § 5). Đổi tên, đổi kiểu, bỏ, thêm trường BẮT BUỘC = BREAKING → changeset `major` + "Cách chuyển" (`.changeset/README.md`; CL § Giới hạn khi sửa "Không đổi tên hay kiểu"); đổi nghĩa/tên khoá manifest → `MANIFEST_FORMAT` + 1 (MF § 5). Thêm tuỳ chọn = minor. Mô hình trang của Redesign và mã đã chép ở dự án export gãy IM LẶNG — không typecheck nào của repo này đỏ. H4 (giá trị đã lưu) chính là enum của knob trong mô hình trang; H2, H3, H5–H7 (mã lỗi API, route, `x-request-id`, testid) n/a. Module sai vì hợp đồng module là route/JSON/liên module; hợp đồng gói là API props. Mức: phá vỡ mà không `major` + "Cách chuyển" 🔴 · thêm mà thiếu changeset 🟠 |
| Chất lượng | **Trạng thái** | Đổi | Trạng thái của BLOCK, không của màn: thiếu ảnh, chữ dài gấp đôi mẫu, danh sách ở `min` và `max`, 375px không tràn ngang, theme tối/khó, không JS, `prefers-reduced-motion`, mỗi trang một `h1` (`headingLevel`, `defaultHeadingLevel` — KT § 2.1), dữ liệu lúc chạy rỗng (`flight-results` không chuyến nào) (AG § 8; KT § 6; SK § Mười luật, luật 10). D2, D3 (`formerMember`, `NotYetActive`) n/a. Module sai vì D1–D3 nói màn nạp dữ liệu từ máy chủ. Mức: vỡ ở chữ dài / tràn 375px 🟠 · còn lại 🟡 · không thấy trên diff → ❓ đã xem 375px + chữ dài chưa |
| Chất lượng | **Tối giản** | Áp | như module |
| Chất lượng | **Tài liệu** | Đổi | F1 → § **Số bản**. F2 (file khung) bỏ — không có module sinh từ repo này. F3 áp: RD (Entry, Lệnh), AG, CL, `docs/`, skill gốc khớp mã và khớp nhau; câu "Còn mở" không tự chọn (CL § Trước khi viết dòng mã đầu tiên; QD § Còn mở). F4 NGƯỢC cho `skills/comitor-web-ui/**`: bản GỐC (SM § 1), sửa được và PHẢI cùng PR với block đổi; `references/blocks.md` sinh, không sửa tay (SM § 2); "Viết cho gói x.y.z" chỉ ở đầu `SKILL.md` (SM § 3); luật mới từ lỗi thật → SP (SM § 4). F4 áp nguyên cho `.claude/skills/comitor-review/**`. F5: sửa skill gốc hay block → `pnpm check:skill` xanh (thân commit hay PR ghi) — ❓. F6 bỏ (không `@comitor/ui`). F7: khuôn log thực tế `type: mô tả tiếng Việt` (thường kèm mã việc `Wxxx` của TASKS.md), repo không có CONTRIBUTING — ⚪. Module sai vì F1, F2, F6 nói `version:check`, file khung, `@comitor/ui`; F4 cấm sửa một skill mà ở đây là bản gốc. Mức như module |

Mẫu số bảng Kiểm: Kiến trúc **5** (Tầng, Một luật, Ranh giới, Chỗ đặt, Ranh giới gói) · Dữ liệu & bảo mật **4**
(Nơi nhận dữ liệu, Toàn vẹn, Tiêm & bí mật, Hướng hỏng — Workspace bỏ) · Quy ước **5** · Chất lượng **6** — 20 hàng.
Bảng Kiểm in `<n>/4` ở hàng Dữ liệu & bảo mật và dùng tên hàng mới (**Ranh giới gói**, **Nơi nhận dữ liệu**).

## Công cụ máy

- `audit.mjs` của `comitor-ui` — **bỏ**: repo không có skill đó, và luật của nó là luật DÙNG `@comitor/ui`, ngược
  repo này. Thay bằng hai phép đọc — `scripts/*.mjs` nằm ngoài `allowed-tools` của skill nên review không chạy được
  chúng, chỉ đọc được:
  · **màu**: mẫu grep trên dòng thêm của `src/`, lấy nguyên regex từ `scripts/check-boundaries.mjs` (`PALETTE`,
    `HEX_IN_STRING`, `FN_COLOR`, `DYNAMIC_CLASS`);
  · **import**: KHÔNG còn regex để chép. Từ 0.4.1, `check-boundaries.mjs`, `build-manifest.mjs` và `check-manifest.mjs`
    đọc import bằng parser của TypeScript (`moduleSpecifiers` ở `scripts/lib/imports.mjs`). Review đọc CẢ câu import —
    kể cả câu trải nhiều dòng, `export … from`, `import()` và `import("x").T` trong kiểu — rồi xét theo ba luật import
    ở đầu `check-boundaries.mjs`: không `@comitor/ui`; tương đối có đuôi `.js` và không alias `@/`·`~/`; bare chỉ tới
    gói đã khai (cộng `react/jsx-runtime`). Grep một dòng `from "./x"` bỏ sót đúng loại import đã làm 0.4.0 phát hành
    thiếu file (§ Bẫy › Bản chép và manifest).
- `check-refs.mjs` của `comitor-test` — **bỏ**: repo không có skill đó. Thay bằng
  `node .claude/skills/comitor-review/scripts/sections.mjs --check-table` khi diff đổi đề mục của AG, CL, KT, MF, RD,
  SK, SM: một mục bảng trỏ tới không còn → phát hiện của hàng **Tài liệu** (sửa đề mục, hoặc báo người bảo trì hồ
  sơ ở `comitor-starter`).
- `pnpm exec biome check <file đã sửa>` — như module (chỉ khi `--fix`).

`pnpm check` không chạy, như module (mười ba cổng, phần lớn đọc `dist/`; `ci.yml` chỉ chạy tay). Diff đổi block,
token hay manifest mà PR không nói đã chạy `pnpm check` → ❓, nhất là `check:skill` và `check:tokens`: hai cổng đỏ
vì file SINH chưa ghi lại.

## Không bao giờ sửa

Từ danh sách module giữ: file bước 1.6 thấy bẩn; `.claude/skills/comitor-review/**` (bản chép). Bỏ: `messages/*.json`,
`prisma/migrations/**`, khuôn `.tpl`, file khung — không có ở đây. Thêm:

- khối `@generated default-theme` của `styles.css` (`pnpm tokens:sync`) và `skills/comitor-web-ui/references/blocks.md`
  (`pnpm skill:sync`) — file SINH;
- `CHANGELOG.md` (do `changeset version` sinh) và `.changeset/*.md` (mức bump, "Cách chuyển" là quyết định của tác giả);
- `src/primitives/brand-icons.ts` (dữ liệu simple-icons) và `COLOR_EXEMPTIONS` của `scripts/check-boundaries.mjs`;
- `docs/QUYET-DINH.md` (lời chủ sản phẩm), `docs/MA-TRAN-V1.md`, `docs/khao-sat/**` (ma trận đã duyệt, dữ liệu khảo sát);
- tên EXPORT, slot, variant, token, nút style — kể cả khi trông như mã chết: dự án export và mô hình trang dùng thứ
  repo này không thấy, nên "Mã chết" của hàng **Tối giản** chỉ áp cho thứ KHÔNG export.

## Mức

Giữ của module: hành vi/nơi gọi gãy; XSS, tiêm; bí mật vào diff (🔴); khả năng lỗi, luật viết hai lần, nơi gọi/anh em
không đổi theo, tự dựng thứ gói đã có (🟠); 🟡, ⚪, ❓ như module. Bỏ: workspace, chốt quyền, `@api-guard`, migration,
hợp đồng liên module, `better-auth`, ranh giới Account, `messages/`, API giả, `fetch` ngoài `lib/api-client/`, Server
Action, file khung.

Thêm **🔴**: đổi tên/kiểu/bỏ slot, variant, token, nút style, entry hay khoá manifest mà changeset không `major` +
"Cách chuyển"; `content` quyết định nơi dữ liệu đi; link, `src`, iframe từ nội dung không qua bộ lọc; import
`@comitor/ui`; mất directive hay hằng thuần qua proxy client; chép mã, CSS, chữ, ảnh của site khảo sát hay bộ blocks
thương mại (AG § 4 — giấy phép); `dist/`, `r/`, `manifest.json` bị commit.

Thêm **🟠**: màu cứng, nhánh màu theo tone, sửa tay khối sinh; cặp chữ/nền dưới 4,5:1 (viền ô nhập, focus dưới 3:1)
ở một tone; mục tiêu chạm < 44px; chữ dựng sẵn ngoài `ui-text.ts`; slot chữ thiếu `max`, danh sách thiếu `min`/`max`,
zod trần; bản chép không đứng được; `"use client"` trên block tĩnh; `Intl` trong chữ client vẽ; block không có trong
manifest, `uses` hứa trường không vẽ; đổi variant làm mất nội dung; dependency nặng hay thư viện tương tác không có lý
do trong docs; thiếu changeset cho phần thêm vào API; thiếu dòng nguồn cảm hứng; workflow thêm trigger tự chạy
(`push`, `pull_request`) — phút Actions là tiền thật, và `release.yml` đã chạy ở MỖI merge (đầu `ci.yml`).

## Số bản

Thay F1. Phát hành bằng changesets (`.changeset/README.md`, `.changeset/config.json`; AG § 6; RD § Phát hành; đầu
`release.yml`) — không có `version:check`, không tăng tay:

- PR đổi API công khai (props, slot, variant, token, export, khoá manifest, hành vi nhìn thấy của block) có `.changeset/*.md`
  cho thay đổi đó; commit sau trong cùng nhánh sửa file đó thay vì thêm file trùng nội dung.
- Mức bump đúng: `major` cho đổi tên/kiểu/bỏ/thêm bắt buộc, kèm dòng "Cách chuyển"; `minor` cho block, variant, trường
  tuỳ chọn, export mới; `patch` cho sửa không đổi hợp đồng.
- KHÔNG tăng tay `version` của `package.json`, KHÔNG sửa tay `CHANGELOG.md`: `changeset version` làm việc đó trong PR
  "Version Packages" mà `release.yml` mở. Diff đổi hai thứ đó ngoài PR ấy → 🟠. PR "Version Packages" chỉ được chứa
  `version`, `CHANGELOG.md` và việc xoá `.changeset/*.md` — kiểm mức bump khớp các changeset bị xoá.
- Không cần changeset: `apps/docs` (private, `privatePackages.version: false`), `scripts/`, tài liệu, test, CI.

Mức: thiếu changeset 🟠 · thay đổi phá vỡ mà bump dưới `major` 🔴.

## Bẫy

Mỗi dòng là lỗi ĐÃ XẢY RA ở repo này hay ở `comitor-ui` mà repo này chép khung, kèm nguồn. Như `pitfalls.md` của
module: gần như không dòng nào làm cổng máy đỏ lúc nó xảy ra.

### Ranh giới server/client

| Lỗi | Thấy trong diff thế nào | Đã gặp ở |
|---|---|---|
| Hằng export từ file `"use client"` đọc ở Server Component ra `undefined` / mảng rỗng — không ném, không cảnh báo, kiểu vẫn đúng (10/11 hằng của gói hỏng) | `export const X = { … }` hay mảng hằng trong file client | `comitor-ui` 0.2.2 — đầu `scripts/verify-directives.mjs` (phép kiểm 2); KT § 4 |
| Hằng ở file thuần nhưng barrel lấy nó VÒNG QUA file client — lỗi trên quay lại khi phép kiểm 1 và 2 đều xanh | `index.ts` re-export qua file `"use client"` | `comitor-ui` — đầu `scripts/verify-directives.mjs` (phép kiểm 3) |
| Directive bị nuốt hay đẩy vào giữa file khi gộp bundle — "useState only works in a Client Component" chỉ lộ sau publish | `tsup.config.ts` bật `bundle`, đổi `entry` | `comitor-ui` — comment `tsup.config.ts`, đầu `scripts/verify-directives.mjs` (phép kiểm 1) |
| "Functions cannot be passed directly to Client Components" | Prop hàm (render prop, handler) mới trên block/primitive client | SP (dòng 7) |
| Hydration lệch quanh ngày, tên thứ, giá: Node và trình duyệt ra "Thứ 4" / "Th 4" | `Intl`, `toLocaleString` trong component client | KT § 9 ("Chữ do component CLIENT") · SP |

### Bản chép và manifest

| Lỗi | Thấy trong diff thế nào | Đã gặp ở |
|---|---|---|
| Import tương đối không đuôi: Node ESM thuần không nạp được entry | Import tương đối không `.js` trong `src/` — đọc cả câu, kể cả câu trải nhiều dòng, `export … from`, `import()`; grep `from "./x"` trên một dòng là không đủ | `comitor-ui` 0.2.1 — đầu `scripts/check-boundaries.mjs` (luật 2) |
| 0.4.0 phát hành chín mục `r/*.json` thiếu `parts.tsx` của loại: bao đóng file đọc import bằng regex một dòng, bỏ sót import trải nhiều dòng — dự án export nhận bản chép không biên dịch được, và luật đuôi `.js` cũng không thấy các import đó | Đổi cách đọc import hay bao đóng file (`scripts/lib/imports.mjs`, `build-manifest.mjs`); một script mới đọc import bằng regex thay vì `moduleSpecifiers`; diff đổi `src/registry/**` hay một block có `parts.tsx` mà PR không nói đã chạy `check:manifest` và `export:verify` (`r/` gitignore nên không bao giờ vào diff) | `comitor-web-ui` 0.4.0 → 0.4.1 (`scripts/lib/imports.mjs` đầu file) |
| Đổi variant xong mất nội dung | Mã ghép trang xoá trường ngoài `uses`; trường riêng variant khai bắt buộc | SP; KT § 2 2.2 |
| `parse` ném lúc lưu mô hình trang: chữ vượt `maxLength`, giá là chuỗi, link `javascript:` | Siết giới hạn của slot đã phát hành; `sample` mới không qua schema | SP |

### Nội dung và nơi nhận dữ liệu

| Lỗi | Thấy trong diff thế nào | Đã gặp ở |
|---|---|---|
| Form tìm vé gửi sai tên tham số cho trang kết quả của đại lý | Tên tham số cứng thay vì qua `params`; `FLIGHT_PARAMS` đổi | SP; KT § 4 4.2 |
| Bấm Tìm không đi đâu, hiện "Bản xem trước…" ở dự án thật | `action` bị đưa vào `content` hay bị bỏ ở mã ghép trang | SP |
| Giá ở trang kết quả thấp hơn giá phải trả | `price.amount` nhận giá chưa thuế phí | SP; KT § 4 4.3 |

### Token và màu

| Lỗi | Thấy trong diff thế nào | Đã gặp ở |
|---|---|---|
| Giá và lỗi trên tone `brand-soft` chỉ đạt 3,9–4,4:1 — mọi test token xanh, `lint:a11y` bắt ở lần chạy đầu | Bảng ánh xạ bề mặt ← theme trong `styles.css` đổi; tone hay cặp mới | KT § 3 3.3 · đầu `scripts/check-contrast.mjs` |
| Mũi tên của `Select`: các lớp nền chồng nhau thành khối đen | Vẽ icon bằng nhiều lớp `background-image` | CHANGELOG 0.1.0 (6b57354) |
| Block hiện chữ trần, không màu, không lưới | `styles.css` import trong `layout.tsx` hay trước `@import "tailwindcss"` | AG § 8 ("Tailwind v4 CSS-first") · SP (dòng 1) |
| Màu chỉnh qua `className` không đạt tương phản ở tone khác | Class màu cố định trên chữ/nền của block | SP |

### Bố cục và trạng thái

| Lỗi | Thấy trong diff thế nào | Đã gặp ở |
|---|---|---|
| Chữ `sr-only` ở trang ngoài khung của `Carousel` kéo trang tràn ngang | Phần tử `absolute` trong slide không phải khối định vị | CHANGELOG 0.1.0 (a0042dd); SP |
| Nhãn mục mất ở thẻ không ảnh | Nhánh "không ảnh" của thẻ vẽ thiếu trường trong `uses` | commit f3b3f60 (`check:blocks` bắt) |
| Trang trắng khi chụp vì chữ chờ hiệu ứng cuộn | Nội dung ẩn tới khi `IntersectionObserver`/animation chạy | KT § 4 ("Nội dung không được phụ thuộc") · `docs/khao-sat/` |
| Nút liên hệ nổi, header dính bay ra ngoài khung mockup, đè giao diện app Redesign | `position: fixed`/`sticky` mới; khung `.docs-frame` đổi | KT § 7 · SP |
| Hai `h1` trên một trang | Block mở đầu mới không có `defaultHeadingLevel` đúng | SP; KT § 2 2.1 |

### Phát hành và CI

| Lỗi | Thấy trong diff thế nào | Đã gặp ở |
|---|---|---|
| Sinh `.d.ts` chết `ERR_WORKER_OUT_OF_MEMORY` ngay SAU "Build success" — log trông như xong | Workflow bỏ `NODE_OPTIONS=--max-old-space-size=4096` | `comitor-ui` — comment `ci.yml`, `release.yml` |
| Cạn 2.000 phút Actions/tháng: `ci.yml` thành chạy tay, Actions chỉ còn cho phát hành | Thêm `push`/`pull_request` vào `on:` | commit 9c03eed; đầu `ci.yml` |
| `overrides` trong `package.json` bị pnpm 11 bỏ qua im lặng | `overrides` thêm vào `package.json` thay vì `pnpm-workspace.yaml` | comment `pnpm-workspace.yaml` |
| Thiếu `"."` trong `packages` của workspace: `changeset version` báo "not in the workspace", phát hành hỏng | `pnpm-workspace.yaml` đổi `packages` | comment `pnpm-workspace.yaml` |
| pnpm 11 không thay `${NODE_AUTH_TOKEN}` trong `.npmrc` của repo — và file commit được là đường lộ token | Dòng `_authToken` thêm vào `.npmrc` | comment `.npmrc` |
| `pnpm dev:pkg` xoá `.d.ts`: `tsc` của app docs và `docs:build` đỏ | Lệnh hay workflow chạy `docs:build` sau `dev:pkg` | KT § 9 ("pnpm dev:pkg") |
| Turbopack giữ module cũ của `app/mau/pages.ts` — trang hiện bản cũ, không lỗi | Kết luận "sửa không có tác dụng" dựa trên `docs:dev` | KT § 8 |

### Tài liệu lệch mã

Trạng thái 18.10.2026 — ghi dưới **Đã kiểm** khi chạm tới, không phải phát hiện của PR; diff CHÉP lại một câu sai này
sang chỗ mới thì là hàng **Tài liệu**.

| Lỗi | Thấy trong diff thế nào | Đã gặp ở |
|---|---|---|
| AG ghi `.npmrc` có `//npm.pkg.github.com/:_authToken=${NODE_AUTH_TOKEN}`; `.npmrc` thật cấm đặt token ở đó | Ai đó "sửa" `.npmrc` cho khớp AG | AG § 6 |
| AG ghi `ci.yml` chạy cổng kiểm ở mọi push và PR; nó là `workflow_dispatch` từ 9c03eed | Câu đó được trích làm lý do bỏ chạy `pnpm check` ở máy | AG § 6 |
| AG liệt `next` trong `peerDependencies`; `package.json` không có, và `check:boundaries` cấm import gói chưa khai | `next` thêm vào peer "cho khớp tài liệu" | AG § 4 ("Chỉ peerDependencies") |
| AG liệt entry `./blocks/<type>`; `exports` không có | Tài liệu mới chép danh sách entry từ AG thay vì RD § Entry | AG § 3 ("Exports:") |
| AG § 5 "Lệnh dự kiến (chưa có…)" — lệnh đã có, đủ ở RD § Lệnh | Tài liệu mới trỏ AG § 5 làm danh sách lệnh | AG § 5 |
