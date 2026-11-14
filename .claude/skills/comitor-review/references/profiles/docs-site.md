# Hồ sơ `docs-site` — site tài liệu `comitor-ds`

Site tài liệu của `@comitor/ui` (Next.js 16, App Router). Mọi trang ở `app/(docs)/<mục>/<slug>/page.tsx`, gần như
trang nào cũng là `"use client"` vì trang chính là demo sống. Một route duy nhất: `app/api/demo-upload/route.ts`.
KHÔNG có `lib/`, `stores/`, `hooks/`, `messages/`, database, phiên, Account, API giả, test, CHANGELOG. Chữ của site
là tiếng Anh viết thẳng trong JSX, cố ý (RD § How it is wired, đoạn **Language**).

Luật thật của repo nằm ở `README.md` (4 mục) và ở comment đầu file (`check-version.mjs`, `check.yml`,
`next.config.mjs`, `pnpm-workspace.yaml`, `globals.css`, `route.ts`, `releases.ts`). `AGENTS.md` chỉ là khối do
`next dev` sinh (một đề mục cấp 1, không chọn mục được); `CLAUDE.md` chỉ là `@AGENTS.md`.

```json profile
{
  "docs": {
    "RD": "README.md",
    "AG": "AGENTS.md",
    "SK": ".claude/skills/comitor-ui/SKILL.md",
    "SKM": ".claude/skills/comitor-ui/MAINTAINING.md"
  },
  "table": "references/profiles/docs-site.md",
  "pitfalls": "references/profiles/docs-site.md",
  "pitfallSections": {
    "Kiến trúc": ["Gói thật, không bản chép", "Điều hướng và URL"],
    "Dữ liệu & bảo mật": ["Route demo và cổng phiên bản"],
    "Quy ước": ["Văn bản JSX và ngôn ngữ", "Màu, icon, bố cục demo"],
    "Chất lượng": ["Trang dạy sai", "Tài liệu và commit nói sai"]
  }
}
```

## Tài liệu quy định

Viết tắt: **RD** = `README.md` · **AG** = `AGENTS.md` · **SK** = `.claude/skills/comitor-ui/SKILL.md` (bản chép) ·
**SKM** = `.claude/skills/comitor-ui/MAINTAINING.md`. Đọc mục bằng `sections.mjs` như `governing-docs.md`; ô ghi
"comment đầu file" thì Read file đó tới dòng `import`/`name:` đầu tiên. Lấy hàng khớp ĐẦU TIÊN; ba hàng cuối CỘNG THÊM.

| Đường dẫn đổi (glob) | Đọc | Mục quyết định |
|---|---|---|
| `app/api/**/route.ts` | chính file đó; `components/editor-demo.ts` | comment đầu file (không giữ gì, không log nội dung, 700 ms nói thẳng) |
| `app/(docs)/changelog/releases.ts` | chính file đó | comment đầu file (mới nhất trước; không nói gì CHANGELOG của gói không nói) |
| `app/(docs)/**/page.tsx` | RD; SK | RD § Writing a page · RD § Colour · SK § Cần gì → dùng gì · SK § Mười luật không thương lượng |
| `components/**` | RD; SK | RD § Writing a page · RD § Colour · SK § Cần gì → dùng gì |
| `app/layout.tsx`, `app/(docs)/layout.tsx`, `app/page.tsx`, `app/globals.css` | RD | RD § How it is wired · RD § Colour · comment đầu file |
| `next.config.mjs` | chính file đó | comment trong file (hai con số ở rail; redirect cho trang đã dời) |
| `package.json`, `pnpm-workspace.yaml`, `pnpm-lock.yaml` | RD; SKM | RD § How it is wired · SKM § 3 · `.claude/skills/comitor-ui/references/upgrading.md` · comment `pnpm-workspace.yaml` |
| `.github/**`, `scripts/**` | chính file đó | comment đầu file (`fetch-depth: 2`, `--frozen-lockfile`, hai chế độ mốc) |
| `.claude/skills/comitor-ui/**` | SKM | SKM § 1 · SKM § 2 · SKM § 5 |
| `.claude/skills/comitor-review/**`, `.claude/settings.json`, `.claude/comitor-repo.json` | `MAINTAINING.md` của skill review | toàn bộ; bản chép (F4) |
| `README.md`, `AGENTS.md`, `CLAUDE.md` | RD; AG | RD § Getting started · AG toàn bộ (khối `next dev` sinh, đừng sửa tay) |
| **cộng thêm:** mọi `*.tsx` có chữ hiển thị | RD | RD § Writing a page (luật 3: ngôn ngữ, `labels`, WCAG 2.5.3) |
| **cộng thêm:** mọi class/style màu | RD | RD § Colour |
| **cộng thêm:** mọi lô vào `main` | `scripts/check-version.mjs` | comment đầu file (tăng `version`, không CHANGELOG) |

`public/**`, `app/icon.svg` không có hàng (tài sản thương hiệu).

## Phạm vi diff

- `-U0` loại `pnpm-lock.yaml` như module; không loại gì khác (`tsconfig.tsbuildinfo`, `next-env.d.ts` không được track).
- Diff dài thì chia nhóm: `… -- 'app/(docs)/components/' 'app/(docs)/foundations/' 'app/(docs)/get-started/'` ·
  `… -- 'app/(docs)/composites/'` · `… -- 'app/(docs)/patterns/' 'app/(docs)/shell/'` ·
  `… -- components/ app/api/ app/layout.tsx app/page.tsx app/globals.css 'app/(docs)/changelog/' 'app/(docs)/resources/' next.config.mjs` ·
  `… -- '*.md' .claude/ .github/ scripts/ package.json pnpm-workspace.yaml`.
- Trang dài hàng nghìn dòng (Patterns): kể cả lượt đầy đủ, KHÔNG Read cả `page.tsx` — lấy `git diff -U40 <gốc>..HEAD -- <file>`
  và `grep -n` hằng/import; Read cả file chỉ khi hunk đổi một hằng, hàm hay component định nghĩa chỗ khác trong file.
  Trang độc lập nhau, nên nơi gọi của một trang là chính nó; nơi gọi của `components/**` là mọi trang (grep tên).
- Commit chép lại skill (`.claude/skills/<tên>/**`): không review từng dòng — kiểm thân commit nêu bản starter, không file
  nào khác lẫn vào cùng commit (bẫy 072dbbb), `verify-skill.mjs` xanh.

## Bản gốc hay bản chép

`"name": "comitor-ds"` → không phải repo gốc của skill nào. Cả `comitor-ui` lẫn `comitor-review` ở đây là bản CHÉP
từ `comitor-starter` (SKM § 1, § 5): F4 áp. `releases.ts` cũng là bản chắt từ `CHANGELOG.md` của `comitor-ui` —
CHANGELOG của gói thắng (comment đầu `releases.ts`).

## Đường nhanh

Danh sách nhạy cảm thay cho của module: `app/api/**`, `app/layout.tsx`, `app/(docs)/layout.tsx`, `app/globals.css`,
`components/**` (khung của MỌI trang), `next.config.mjs`, `scripts/**`, `.github/**`, `.claude/settings.json`,
`.claude/comitor-repo.json`, `.claude/skills/**`, `package.json`, `pnpm-lock.yaml`, `pnpm-workspace.yaml`,
`biome.json`, `tsconfig.json`, `postcss.config.mjs`. Ba điều kiện kia như module.

## Lockfile

Như module, cộng:

- `@comitor/ui` đổi bản → `references/quality.md` § A với bảng anh em ở hàng **Đúng** dưới đây; bản ĐÃ CÀI (không phải
  dải `^`) là thứ demo render (`next.config.mjs`). `pnpm add` có thể thoát 0 mà không nâng — `minimumReleaseAgeExclude`
  phải liệt kê theo TÊN gói (comment `pnpm-workspace.yaml`); thấy một phiên bản bị thêm vào danh sách đó → 🟡.
- Bộ `@tiptap/*` cùng MỘT số chính xác; `@tanstack/react-table` giữ `^8`; lệch → 🟠 (peer của entry gói, RD § How it is wired).
- Thư viện xác thực bất kỳ xuất hiện mới (`better-auth` hay khác) → 🔴: site không có phiên, không có lý do để có nó.

## Hàng

| Nhóm | Hàng | Áp/Đổi/Bỏ/Thêm | Luật ở repo này (nguồn) |
|---|---|---|---|
| Kiến trúc | Tầng | Đổi | T1–T7 Bỏ: không có `lib/core`, store, hook, tầng D. T8 Đổi: không có `lib/api-client/` nên luật module báo nhầm mọi lời gọi; ở đây `fetch(` trong chuỗi mã mẫu không phải lời gọi, lời gọi THẬT chỉ tới route có thật trong `app/api/` (hôm nay chỉ `components/editor-demo.ts` → `/api/demo-upload`); demo gọi route không tồn tại hay host ngoài → 🟠 (demo hỏng khi bấm — RD § Writing a page luật 1) |
| Kiến trúc | Một luật | Đổi | M1, M3 Bỏ (không lõi, không API giả). M2 Đổi: sự thật ở đây là của GÓI — hằng, bảng mặc định, danh sách export mà gói export thì import (như `foundations/server-client`), không chép tay; chép tay → 🟠 (d4617dc: cột default lấy từ bảng nguồn). M4 Đổi: luật "`href` chỉ ở `navigation.ts`" không có đối tượng; danh sách trang CÓ ba chỗ theo thiết kế (`sidebar-nav.tsx` `NAV_SECTIONS`, `top-nav.tsx` `NAV_LINKS`, trang index của mục) — đổi một chỗ mà không đổi chỗ kia → 🟠 |
| Kiến trúc | Ranh giới | Đổi | R1, R3, R7 Bỏ (không `lib/`, không dữ liệu máy chủ). R2 Bỏ: module coi `"use client"` trên `page.tsx` là lỗi, ở đây trang LÀ demo có state, tiêu đề đi từ `title.template` của root, không có dữ liệu để lộ xuống bundle. R4–R6 Áp (Server Component như `changelog/page.tsx` không truyền hàm/`Date`/object date-fns xuống client — `components/home/language-demo.tsx`). Thêm: trang giữ được prerender tĩnh — `cookies()`/`headers()`/`searchParams` thật ở trang → 🟡 (RD § Getting started «prerenders every page statically»; trong chuỗi mẫu thì được) |
| Kiến trúc | Chỗ đặt | Đổi | P1 Đổi: không có route nghiệp vụ; khung và helper dùng nhiều trang ở `components/`, fixture chung của ≥ 2 trang ở `components/<tên>-demo.ts`, mảnh chỉ trang chủ ở `components/home/`, còn lại nằm trong chính `page.tsx`; đầu file ghi vì sao (như `editor-demo.ts`, `hero-showcase.tsx`). P2, P5, P6 Bỏ. P3 Đổi: trang mới phải có mục ở `sidebar-nav.tsx` và ở trang index của mục (`components`, `composites`, `shell`) → thiếu 🟠. P4 Đổi: không có bản đồ route ở README — đối chiếu bảng route của `pnpm build` với `NAV_SECTIONS` |
| Kiến trúc | Account | Bỏ | Không xác thực, không Account, không workspace |
| Dữ liệu & bảo mật | Workspace | Bỏ | Không database, không workspace |
| Dữ liệu & bảo mật | Đường ghi | Đổi | G1 Đổi: `demo-upload` `POST` không phiên, không quyền — đúng vì nó KHÔNG GIỮ GÌ (comment đầu file); luật module sẽ đòi `requirePermission` không tồn tại. Route mới phải giữ đúng thế: đọc, đo, trả, bỏ. Route lưu, chuyển tiếp hay log dữ liệu người gửi → 🔴 (site công khai, không ai xác thực). G2–G5 Bỏ. G6 Áp (`"use server"` mới → 🟠) |
| Dữ liệu & bảo mật | Toàn vẹn | Đổi | I1–I6, I8 Bỏ (không database). I7 Đổi: không có `lib/core/iso-date.ts`/`todayIso` để trỏ tới; ngày lịch tách chuỗi + `Date.UTC` + `timeZone: "UTC"` (`changelog/page.tsx` `formatDate`); demo có giờ ghim `timeZone` tường minh (262f3e8); `new Date("YYYY-MM-DD")` → 🟠 |
| Dữ liệu & bảo mật | Tiêm & bí mật | Đổi | S1–S4, S7 Áp — `dangerouslySetInnerHTML` trong chuỗi mẫu không phải phát hiện S1 (xét ở hàng **Mẫu**). S5 Đổi: không `lib/env.ts`; `process.env` chỉ `NEXT_PUBLIC_UI_VERSION`/`NEXT_PUBLIC_APP_VERSION` do `next.config.mjs` tiêm; site không có bí mật và CI không có khối `env` (check.yml) — biến mới cần bí mật → 🔴. S6 Đổi: không `withApiErrors`; lỗi trả `{ error: { code, message } }` bằng câu cố định (`fail()`), không vọng `e.message`. S8 Đổi: không có kho; demo phải dạy đúng hợp đồng — trả KHOÁ, không URL (`editor-demo.ts`). S9, S10 Bỏ (không CSV, không `proxy.ts`) |
| Dữ liệu & bảo mật | Hướng hỏng | Đổi | H1, H3–H6, H8 Bỏ (không danh bạ, `useErrorMessage`, env, thư, limiter, chuỗi log). H2 xét ở **Trạng thái**. H7 Áp. Thêm: cổng không được hỏng theo hướng MỞ — `fetch-depth: 2` và `--frozen-lockfile` của `check.yml`, nhánh "không đọc được mốc → bỏ qua" của `check-version.mjs` chỉ cho ca thật sự không có mốc; nới một trong ba → 🟠 (comment đầu hai file) |
| Quy ước | i18n | Đổi | Không `messages/`, không `t()`: N1 module bắt MỌI chữ JSX — ở đây chữ tiếng Anh trong JSX là đúng (RD § How it is wired). N1 Đổi: tiếng Việt chỉ qua `<ComitorLocaleProvider locale="vi">` quanh demo; chữ Việt viết tay trong demo → 🟠. N2 Đổi: chữ hiển thị và tên trợ năng CÙNG ngôn ngữ (WCAG 2.5.3) → lệch 🟠. N6 Đổi: không truyền `labels`/`*Label` chỉ để nói lại mặc định tiếng Anh; được khi demo nói VỀ cơ chế hay chữ là nội dung → 🟡 (RD § Writing a page luật 3). N5 Đổi: `PropsTable` chữ trơn, backtick hiện nguyên → 🟡. N7 Áp (`<RelativeTime>` có `timeZone`, không `locale=`). N3, N4, N8 Bỏ. Thêm: không HTML entity (`&apos;`…) trong văn bản JSX nhiều dòng — dùng chính ký tự; giữ `&lt; &gt; &amp; &#123; &#125;` → 🟡 (fbec028) |
| Quy ước | Màu & UI | Đổi | U1 Đổi: module cấm mọi hex/`rgb(` — ở đây hex còn là DỮ LIỆU tài liệu. Được: `.dot-grid` ở `globals.css`, `themeColor` ở `app/layout.tsx` (khớp `--background`), hex/`rgb(` hiển thị cho người đọc (văn xuôi, `<code>`, bảng swatch, số đo, `releases.ts`), và trong chuỗi mã mẫu. Màu thô trong `className`/`style` mà trình duyệt VẼ ở khung hay demo → 🟠. U2 Đổi, nặng hơn: thang thô (`gold-*`, `ash-*`, `red`, `green`, `gray-*`) thay token vai trò → 🟠 — nó cứng vào một bảng màu và sai ở bảng tương phản cao (RD § Colour; 072dbbb, 7b5aaaf); icon alpha như module; chip/StatCard `primary` vàng là QUYẾT ĐỊNH thiết kế, đừng báo theo số đo (bf0445c). U3 Đổi: demo phải là component THẬT, mô phỏng vẽ tay → 🟠 (RD § Writing a page luật 1); khung tự dựng chỉ khi gói không có (khung thiết bị — `hero-showcase.tsx`). U4 Áp, mức 🔴 (§ Mức). U5 Đổi: thêm ba bẫy của site (§ Bẫy › Màu, icon, bố cục demo). U6 Đổi: `audit.mjs` đã có sẵn nhiều ERROR trên dữ liệu tài liệu; chỉ ERROR rơi vào dòng diff mà trình duyệt VẼ là phát hiện. U7 Áp |
| Quy ước | Ngôn ngữ & tên | Đổi | L1, L3, L5 Áp (URL là API công khai — xem H3). L2 Đổi: module đòi comment tiếng Việt, ở đây hai thứ tiếng cùng có (`layout.tsx`, `globals.css` Việt; `route.ts`, `next.config.mjs`, `check-version.mjs`, `components/**` Anh) và không tài liệu nào chọn; giữ ngôn ngữ của file đang sửa, trộn trong một khối → ⚪. L4 Đổi: luật như module (chỉ chặn tên dự án, đối tác khác của đội), cộng một chỗ được gọi tên: nguồn gốc mà gói ghi nhận (shadcn/ui, Dice UI, Radix) — đó là ghi công, không phải nguồn giấu tên; phụ thuộc thật (Next, React, Tailwind, TanStack, Tiptap, Uppy, Recharts, lucide, date-fns, Biome) như module. Ví dụ trên trang tài liệu không nói về một doanh nghiệp thật nào nên dùng tên miền `.example` (262f3e8 gỡ tên thương hiệu ngoài khỏi ví dụ) |
| Quy ước | Comment | Áp | như module (C1–C5) |
| Quy ước | Kiểu | Đổi | K1, K3 Áp. K4 Áp: `pnpm lint` KHÔNG có `--error-on-warnings` nên warning không chặn — warning MỚI trên dòng diff là phát hiện 🟡. K2 Bỏ: `tsconfig.json` không bật `noUncheckedIndexedAccess`. K5 Bỏ (không `lib/contracts`) |
| Chất lượng | Đúng | Đổi | Như module, bảng anh em thay bằng bảng dưới đây |
| Chất lượng | Test | Đổi | Không có test; cổng là `pnpm build` (prerender mọi trang — đã bắt crash `Badge asChild` của gói, 391a474) + `typecheck` + `lint`. E1–E6, E8 Bỏ. E7 Đổi: không có test nào đỏ được, nên `fix:` ghi phép đo DOM trước/sau (c9e855e, 33bdd0b, f8bfa1a) → thiếu 🟡. Đổi trang/demo mà thân commit không nêu `build` đã chạy → ❓ |
| Chất lượng | Hợp đồng | Đổi | H1 Đổi: hợp đồng duy nhất là `demo-upload` (`{ name, size, type }` / `{ error: { code, message } }`) ↔ `components/editor-demo.ts` ↔ trang `/composites/upload` → đổi một mà không đổi cả ba 🟠. H3 Áp, cách chữa riêng: trang dời/xoá → redirect `permanent` trong `next.config.mjs` (`/patterns/marketing`) → thiếu 🟠. H6 Đổi: không có hợp đồng liên module; hợp đồng của site là HAI con số có nhãn ở rail, bản gói đọc từ cây đã cài chứ không từ dải (comment `next.config.mjs`) → đổi 🟠. H2, H4, H5, H7 Bỏ |
| Chất lượng | Trạng thái | Đổi | D1 Đổi: không có màn nạp dữ liệu; trang của component có trạng thái tải/lỗi/rỗng thì demo cho thấy cả nhánh hỏng (`route.ts`: «success and failure branches») → 🟡. D2, D3 Bỏ. D4 Áp (thiếu `flex-wrap` cắt nút cuối ở màn hẹp — 072dbbb). D5 Đổi: không có `AppShell` của site; demo không được chiếm phím của trình duyệt hay của trang (`DataGrid` `enableSearch` bắt Ctrl/⌘+F trên window — `live-showcase.tsx`; phím chuỗi chỉ khi bật — 391a474) → 🟠 |
| Chất lượng | Tối giản | Áp | như module; mã chết kể cả hằng mã mẫu không trang nào hiện |
| Chất lượng | Tài liệu | Đổi | F1 → § Số bản. F2 Bỏ (không file khung; site không bị chép). F3 Đổi: không bản đồ route, không AGENTS.md có luật — tài liệu là RD + comment đầu file; con số và lệnh trong đó khớp mã (README đang ghi cổng 3000, `launch.json` ghim 3400). F4 Áp (hai skill bản chép). F5 Đổi: không phải starter; commit chép lại skill nêu bản starter và kết quả `verify-skill.mjs` → thiếu ❓. F6 Đổi: không có mục Cạm bẫy; nâng MINOR/MAJOR thì áp "App phải làm gì" của MỌI bản nằm giữa lên demo VÀ mã mẫu (391a474) → 🟠. F7 Đổi: tiêu đề mang số bản site — `type(scope): mô tả — <version>` (hoặc `…, docs <version>`) → ⚪ |
| Chất lượng | Mẫu | Thêm | Trang là thứ module CHÉP. Q1 mã mẫu khớp preview cạnh nó và khớp `.d.ts`/nguồn của bản đang cài (RD § Writing a page luật 2; c9e855e sửa cả code sample) → 🟠. Q2 trang/mẫu không dạy điều module bị cấm hay gói đã đổi (múi workspace, `onRowsDelete` resolve sai, token thô, `toast.error(e.message)`, `dangerouslySetInnerHTML` với dữ liệu, "mặc định tiếng Việt") → 🟠 (262f3e8, d4617dc, 47f1e35). Q3 `releases.ts` có mục cho MỌI bản nằm giữa, mới nhất trước, không nói gì CHANGELOG gói không nói → 🟠. Q4 cột default của `PropsTable` lấy từ nguồn gói, không chép tay → 🟡. Q5 số đếm về gói trong chữ (số entry, số khoá nhãn) đếm lại khi nâng gói → 🟡 |

Mẫu số bảng Kiểm: Kiến trúc **4** · Dữ liệu & bảo mật **4** · Quy ước **5** · Chất lượng **7**.

Anh em của hàng **Đúng** (thay bảng ở `quality.md` § A):

| Đổi ở | Anh em phải xem |
|---|---|
| thêm/dời/xoá một `page.tsx` | `NAV_SECTIONS` (`sidebar-nav.tsx`), trang index của mục, `NAV_LINKS` (`top-nav.tsx`) khi là mục mới, redirect ở `next.config.mjs` khi dời |
| nâng `@comitor/ui` | `releases.ts` (mọi bản nằm giữa), trang có "App phải làm gì", mã mẫu cạnh demo, số đếm trong chữ, `SKILL.md`/`verify-skill.mjs` của bản chép `comitor-ui` (chép lại từ starter, đừng sửa tại chỗ), `version` site tăng |
| một tab `content` của `PreviewCode` | tab `code` của cùng khối, và ngược lại |
| `app/api/demo-upload/route.ts` | `components/editor-demo.ts`, `/composites/upload`, hai trang editor |
| `components/**` | mọi trang dùng nó (grep tên) |
| `next.config.mjs` `env` | rail (`sidebar-nav.tsx`), `app/page.tsx`, `get-started/introduction` |

## Công cụ máy

- `node .claude/skills/comitor-ui/scripts/audit.mjs` khi diff có `.tsx`/`.css` — như module, đọc theo U6 (ERROR trên dữ
  liệu tài liệu không phải phát hiện).
- `check-refs.mjs` KHÔNG có (site không chép `comitor-test`) — bỏ, đừng ghi nó là lệnh hỏng.
- `node .claude/skills/comitor-ui/scripts/verify-skill.mjs` khi diff đụng `.claude/skills/comitor-ui/**` hay đổi bản
  `@comitor/ui` — tên thiếu là phát hiện của hàng **Tài liệu**. Cần `node_modules`; chưa cài (thoát 2) → ghi dưới **Đã kiểm**.
- `pnpm exec biome check <file đã sửa>` chỉ khi `--fix`, như module; warning mới trên file đã sửa = bản sửa hỏng.

## Không bao giờ sửa

Thay danh sách module (`messages/`, migration, `.tpl`, file khung không có ở đây):

- file bước 1.6 thấy bẩn;
- `.claude/skills/comitor-ui/**`, `.claude/skills/comitor-review/**` (bản chép);
- chuỗi mã mẫu và chữ hiển thị trên trang — đổi chúng là đổi điều trang DẠY; **Tối giản** chỉ sửa mã chạy của demo;
- `app/(docs)/changelog/releases.ts` (chắt từ CHANGELOG gói);
- khối `nextjs-agent-rules` của `AGENTS.md` (`next dev` ghi lại — 6aea64f);
- `pnpm-lock.yaml`, `public/**`, `app/icon.svg`.

## Mức

Các dòng module về workspace, Account, `messages/`, `lib/core/`, API giả, CHANGELOG/file khung không áp (n/a). Thêm:

- **🔴** chép mã component của gói vào site (d6743dc gỡ 60 file `components/ui` — RD đoạn mở đầu: bản chép lệch
  im lặng và người đọc tin bản chép); route API lưu, chuyển tiếp hay log dữ liệu người gửi; bí mật hay khối `env` cần
  bí mật.
- **🟠** trang/mẫu dạy sai API hay luật (hàng **Mẫu**); thang màu thô thay token vai trò; demo mô phỏng thay component
  thật; chữ Việt viết tay trong demo; chữ hiển thị và tên trợ năng lệch ngôn ngữ; trang mới thiếu ở `sidebar-nav`;
  dời URL không redirect; demo chiếm phím trình duyệt; nới cổng theo hướng mở; `version` không tăng ở lô đổi bản build.
- **🟡** `labels` nói lại mặc định; HTML entity trong văn bản JSX; `fix:` không ghi phép đo; warning Biome mới.

## Số bản

Thay F1: mỗi PR (mỗi lô vào `main`) tăng `version` trong `package.json` so với `git show <gốc nhánh>:package.json` —
mọi lần đẩy lên `main` là một lần deploy (Vercel nối Git; không có workflow deploy trong repo) và con số in ở rail
(comment đầu `check-version.mjs`). `patch` cho sửa, `minor` cho trang mới (thông điệp của chính script). KHÔNG có
CHANGELOG, cố ý — tạo `CHANGELOG.md` → 🟡 (file viết cho không ai đọc, cùng comment đó). Số bản đi trong tiêu đề commit
(F7). Lô không tăng: đổi thứ vào bản build (`app/`, `components/`, `public/`, `package.json`, lockfile,
`next.config.mjs`) → 🟠; chỉ `.github/`, `.claude/`, `*.md` → 🟡 — luật chữ không miễn, e94e4a5 lọt chứ không phải
được miễn. Ở máy, `pnpm version:check` so với `HEAD` (chạy TRƯỚC commit); sau commit thì `BASE_REF=origin/main
pnpm version:check` (391a474).

## Bẫy

Mỗi dòng là lỗi đã xảy ra ở `comitor-ds`, nguồn là commit hay comment trong repo. Như `pitfalls.md`: gần như không
dòng nào làm cổng máy đỏ.

### Gói thật, không bản chép

| Lỗi | Thấy trong diff thế nào | Nguồn |
|---|---|---|
| Site giữ bản chép của mọi component: trang mô tả variant gói không còn, thiếu `primary`/`asChild` của Badge, default `aria-label` của Spinner sai | File mới giống mã gói; import từ `@/components/ui` | d6743dc |
| ~55 trang vẫn khẳng định "gói mặc định tiếng Việt" sau 3.0.0 — trình biên dịch im lặng | Nâng gói mà chữ trên trang không đổi theo "App phải làm gì" | d4617dc |
| `ShellLabels` 33 → 34 khoá phải sửa tay ở năm trang | Số đếm về gói viết thẳng trong chữ | 391a474 |

### Điều hướng và URL

| Lỗi | Thấy trong diff thế nào | Nguồn |
|---|---|---|
| `/patterns/marketing` đổi tên — link ngoài kia chết nếu không có redirect | `page.tsx` dời mà `next.config.mjs` không đổi | `next.config.mjs` `redirects` (docs 1.5.0) |
| Tám mục top-nav không vừa 1024px nên header cuộn ngang | Thêm mục vào `NAV_LINKS` mà không đo ở `lg` | 7b5aaaf |

### Route demo và cổng phiên bản

| Lỗi | Thấy trong diff thế nào | Nguồn |
|---|---|---|
| Phần multipart trùng tên trường file là CHUỖI (`allowedMetaFields` của Uppy) — kiểm truthy rồi `.size` là sập | Bỏ `instanceof File` | comment `route.ts` |
| Clone một commit thì `HEAD^` không có, cổng phiên bản in ✓ mà không kiểm gì | `fetch-depth` khác `2`; nới nhánh "skip" | comment `check.yml`, `check-version.mjs` |
| Không workflow nào, số bản đứng yên trên trang | Lô vào `main` không tăng `version` | 84ffbdb |

### Văn bản JSX và ngôn ngữ

| Lỗi | Thấy trong diff thế nào | Nguồn |
|---|---|---|
| SWC mất dấu cách đầu node JSX nhiều dòng có HTML entity — chữ dính ở 55 trang; `{" "}` bị Biome gộp lại | `&apos;`, `&quot;`… trong văn bản JSX | fbec028 |
| Chữ Việt (`aria-label`, `sr-only`) lọt ra trang tiếng Anh; về sau là `labels` thừa lặp mặc định | Prop nhãn mới; chữ Việt trong demo | 072dbbb, 7b5aaaf, d4617dc |
| Hai `AppShell` sống trên một trang trùng `id="main-content"` | Demo khung thứ hai thiếu `mainId` riêng | 391a474 |

### Màu, icon, bố cục demo

| Lỗi | Thấy trong diff thế nào | Nguồn |
|---|---|---|
| `className="hidden sm:block"` trên `ComitorLockup`: tailwind-merge thay `flex` của component, logo xếp chồng | Utility display truyền vào component tự đặt display — dùng `sm:flex` | 33bdd0b |
| Dải chip `flex-nowrap` cuộn ngang: chip bị bóp, chữ xuống dòng, cao 50px | `flex-nowrap` thiếu `[&>button]:shrink-0` | f8bfa1a |
| Icon con của `Button` 24px cạnh chữ 14px | Icon trong `Button` không `size-4` (sửa cả mã mẫu) — chỉ khi site dưới `@comitor/ui` 3.13.0; từ 3.13.0 gói tự cỡ | c9e855e |
| Alpha trên màu nét icon lộ vệt nối; `opacity-60` trên `text-muted-foreground` làm chìm hai lần ở dark | `text-x/NN` cạnh `size-*`; `opacity-*` chồng lên bậc đã chìm | 4cf48bd, e81eedd |
| `text-gold-400`, `text-red` không đổi ở bảng tương phản cao | Thang thô trong `className` | 072dbbb, 7b5aaaf |
| Đổi chip vàng sang tông khác theo số đo rồi phải hoàn lại — vàng thương hiệu là quyết định thiết kế | Đừng báo `STATUS_TONES.primary` là sai | bf0445c |

### Trang dạy sai

| Lỗi | Thấy trong diff thế nào | Nguồn |
|---|---|---|
| Trang mẫu dạy múi giờ workspace, `onRowsDelete` resolve sai, tên thương hiệu ngoài — module chép theo | Mã mẫu trái luật module | 262f3e8 |
| Luật con trỏ 1.7.0 chép sang trang có lỗi; sáu ca đo đều chọn đúng selector có guard nên đều đạt | Bảng ca đo không có ca phải trả sai | 47f1e35 |
| `Badge asChild` của 3.7.0 sập lúc prerender — chỉ `build` bắt được | Nâng gói mà không nêu `build` đã chạy | 391a474 |

### Tài liệu và commit nói sai

| Lỗi | Thấy trong diff thế nào | Nguồn |
|---|---|---|
| Commit tả 3/56 file vì `git add -A` gom việc của phiên song song | Thân commit không khớp `--name-status` | 072dbbb |
| Thân commit tả bước deploy không có trong repo (chỉ `check.yml` đổi, repo không có workflow deploy) | Thân commit nói về file không có trong diff | e94e4a5 |
| README "Getting started" ghi `localhost:3000`, dev server đã ghim 3400 | Đổi cổng/lệnh ở một chỗ | 6eaad9b, `.claude/launch.json` |
| Trang chủ ghi "v1.0.0 — May 2026" khi gói đã qua nhiều bản | Số bản viết tay thay cho `NEXT_PUBLIC_UI_VERSION` | 7b5aaaf |
