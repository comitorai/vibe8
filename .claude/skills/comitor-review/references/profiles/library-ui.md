# Hồ sơ `library-ui` — gói `@comitor/ui` (repo `comitor-ui`)

Design system dùng chung: React 19 + Tailwind v4 CSS-first, ESM-only, `tsup` `bundle: false`, chín entry, publish npm
theo tag `v*`. Không có database, phiên, route, `messages/` hay test runner — nên mọi hàng module về workspace, quyền,
API giả, `next-intl` hoặc bỏ, hoặc đổi sang luật thật của một THƯ VIỆN: bề mặt công khai, SemVer, peer, directive
theo file, token màu. Luật nằm ở tài liệu của chính repo; hồ sơ này chỉ trỏ. Mã luật riêng của hồ sơ mang tiền tố
**X** (`X1`…); mã module (`S1`, `N4`, `C2`…) giữ nguyên nghĩa ở chỗ hồ sơ ghi "Áp".

```json profile
{
  "docs": {
    "CL": "CLAUDE.md",
    "RD": "README.md",
    "SP": "docs/spec-package.md",
    "HM": "docs/hop-dong-mau.md",
    "QD": "docs/quyet-dinh-tich-hop.md",
    "DG": "docs/data-grid.md",
    "ED": "docs/editor.md",
    "DU": "docs/diceui.md"
  },
  "table": "references/profiles/library-ui.md",
  "pitfalls": "references/profiles/library-ui.md",
  "pitfallSections": {
    "Kiến trúc": ["Bẫy › Entry, peer và build", "Bẫy › Ranh giới server/client"],
    "Dữ liệu & bảo mật": ["Bẫy › Định dạng lưu và danh tính dòng"],
    "Quy ước": ["Bẫy › Màu và token", "Bẫy › Ngôn ngữ", "Bẫy › Port từ thượng nguồn"],
    "Chất lượng": ["Bẫy › API công khai và phát hành", "Bẫy › Cổng không kiểm gì", "Bẫy › Tài liệu nói dối"]
  }
}
```

## Tài liệu quy định

Thay `governing-docs.md`. Cách đọc giữ nguyên (hàng KHỚP ĐẦU TIÊN, cộng các hàng **cộng thêm**, đọc bằng
`sections.mjs <file> '<ô>'`). Viết tắt: **CL** `CLAUDE.md` · **RD** `README.md` · **SP** `docs/spec-package.md` ·
**HM** `docs/hop-dong-mau.md` · **QD** `docs/quyet-dinh-tich-hop.md` · **DG** `docs/data-grid.md` · **ED**
`docs/editor.md` · **DU** `docs/diceui.md`. Mâu thuẫn: CL thắng SP (SP là bản thiết kế ban đầu, nhiều đoạn
"⟳ ĐÃ ĐỔI" — vd SP § 2 còn ghi mặc định tiếng Việt, đã hết hiệu lực từ `3.0.0`); **Đã kiểm** nêu tài liệu cũ.

| Đường dẫn đổi (glob) | Đọc | Mục quyết định |
|---|---|---|
| `src/index.ts`, `src/*/index.ts`, `src/form.ts` | CL; RD; QD | CL § Kiến trúc 3 tầng + 9 entry · CL § Thêm component mới · CL § Cạm bẫy ("bundle: false + peer optional", "export * chỉ bắt trùng tên", "Barrel phải lấy hằng THẲNG") · RD § 3, § 5 · QD § 1, § 2 |
| `styles.css`, `src/tokens.ts` | CL; HM; RD; QD | CL § Quy ước ("Hợp đồng BA VAI TRÒ", "HAI BẢNG MÀU", "--border ⇄ --input", "Dùng token SEMANTIC", "styles.css là nguồn sự thật") · CL § Cạm bẫy ("@theme inline", "Bóng đi qua HAI lớp tên", "--red là màu TÔ", "--app-accent là màu NỀN", "var() tiêu thụ biến của app") · HM § 1, § 2, § 3, § 5 · RD § 6 · QD § 21, § 22 |
| `src/i18n/**` | CL; QD | CL § Quy ước ("Tiếng Việt", "App Comitor LUÔN truyền ngôn ngữ") · CL § Thêm component mới · QD § 36 |
| `src/lib/**` | CL | CL § Kiến trúc 3 tầng + 9 entry · CL § Cạm bẫy ("Màu avatar chỉ có MỘT nguồn", "⚠ Con có autoFocus") |
| `src/shell/**` | CL; SP; RD | CL § Quy ước ("NĂM TRỤC HIỂN THỊ") · CL § Cạm bẫy ("shell-context.tsx import", "WorkspaceSwitcher và AppLauncher", "ThemeProvider phải nằm ở root layout") · SP § 7 · RD § 4 |
| `src/chart/**` | CL; RD; QD | CL § Cạm bẫy ("Biểu đồ") · RD § 4 · QD § 33.1 |
| `src/data-grid/**` | DG; CL | DG § 9, § 10, § 11 · CL § Cạm bẫy ("⚠ PORT TỪ REPO KHÁC", "⚠ DataGrid có HAI hệ chỉ số dòng") |
| `src/editor/**` | ED; CL | ED § 3, § 4, § 5, § 9 · CL § Cạm bẫy ("⚠ @comitor/ui/editor") |
| `src/uploader/**` | CL; RD | CL § Kiến trúc 3 tầng + 9 entry · RD § 3 |
| `src/components/ui/**` | CL; DU; SP | CL § Kiến trúc 3 tầng + 9 entry · CL § Cạm bẫy ("⚠ Bản port Dice UI") · DU § 2, § 3 · SP § 5 |
| `src/components/composite/**` | CL; SP; QD | CL § Cạm bẫy ("Hai FormField", "Hằng dữ liệu thuần", "Checkbox") · SP § 6 · QD § 15 |
| `scripts/check-contrast.mjs`, `scripts/a11y/**`, `scripts/contrast-exemptions.json` | HM; QD | HM § 8 · QD § 34 |
| `scripts/**` (còn lại), `.github/**` | CL; chính file đó | CL § Lệnh · CL § Publish · comment đầu file (lý do từng bước nằm ở đó) |
| `package.json`, `pnpm-lock.yaml`, `pnpm-workspace.yaml`, `tsup.config.ts`, `tsconfig.json`, `biome.json`, `.npmrc` | CL; SP | CL § Publish · CL § Cạm bẫy ("⚠ Bước .d.ts", "esbuild từng có bug", "attw báo", "ERR_PNPM_IGNORED_BUILDS") · SP § 3.4, § 8, § 10 |
| `CHANGELOG.md` | CL; `scripts/check-version.mjs` | CL § Publish · comment đầu `scripts/check-version.mjs` |
| `README.md`, `CLAUDE.md`, `docs/**` | CL; RD | CL § Thêm component mới · CL § Publish · RD § 5, § 7 |
| `.claude/skills/comitor-review/**`, `.claude/settings.json`, `.claude/comitor-repo.json` | `MAINTAINING.md` của skill | `MAINTAINING.md` §1, §2, §7 (bản gốc ở `comitor-starter`) |
| **cộng thêm:** mọi `src/**/*.ts`/`*.tsx` | CL | CL § Quy ước ("Import nội bộ LUÔN có đuôi", "use client đặt per-file", "Tiếng Việt", "Không sinh class động", "Không hardcode hex") · CL § Cạm bẫy ("Hằng dữ liệu thuần") |
| **cộng thêm:** file có chuỗi hiển thị (kể cả `aria-label`, `sr-only`, lời thông báo) | CL | CL § Thêm component mới · CL § Quy ước ("Tiếng Việt") |
| **cộng thêm:** mọi class màu, `style` inline, SVG | CL; HM | CL § Quy ước ("Thang xám là", "Dùng token SEMANTIC") · CL § Cạm bẫy ("⚠ Icon KHÔNG được tô", "Hover đừng dùng", "⚠ Tailwind v4") · HM § 1, § 7b |
| **cộng thêm:** thêm/xoá/đổi tên export, prop, kiểu, giá trị mặc định, peer | CL; RD | CL § Publish · CL § Cạm bẫy ("export * chỉ bắt trùng tên", "Đo bề mặt API bằng trình biên dịch") · RD § 3, § 5 |
| **cộng thêm:** mọi PR | `scripts/check-version.mjs` | comment đầu file · `## Số bản` của hồ sơ này |

## Phạm vi diff

Như module, trừ: lockfile là `pnpm-lock.yaml` (loại khỏi `-U0`, đọc ở `## Lockfile`); `dist/` không có trong git
(`.gitignore`). `CHANGELOG.md` dài ~5000 dòng nhưng GIỮ trong `-U0` — `## Số bản` đọc đúng các dòng thêm của nó.
Diff dài thì chia: `… -- src/components/ src/lib/ src/i18n/` · `… -- src/shell/ src/chart/ src/data-grid/
src/editor/ src/uploader/ src/index.ts src/form.ts src/tokens.ts styles.css` · `… -- scripts/ .github/ package.json
tsup.config.ts tsconfig.json biome.json` · `… -- '*.md'`.

## Bản gốc hay bản chép

`git show HEAD:package.json` ra `"name": "@comitor/ui"` — repo GỐC của gói; không phải starter, không phải module.
Repo không mang skill `comitor-ui`/`comitor-page`/`comitor-test` (bản tài liệu của gói này là skill `comitor-ui` ở
`comitor-starter`), nên **F4/F5 n/a**, TRỪ `.claude/skills/comitor-review/**`: thư mục đó (khi đã cài để chạy review)
là bản CHÉP từ starter — sửa ở đây là F4 🟡. `.claude/comitor-repo.json` là của repo này, sửa được.

## Đường nhanh

Đổi danh sách đường dẫn nhạy cảm thành (chỗ của bề mặt công khai, token, ranh giới directive, cổng và phụ thuộc):
`src/index.ts`, `src/*/index.ts`, `src/form.ts`, `src/tokens.ts`, `styles.css`, `src/i18n/*.ts` (ngoài
`namespaces/`), `src/lib/**`, `src/shell/types.ts`, `src/shell/shell-context.tsx`, `src/editor/markdown-*.ts`,
`src/**/*-constants.ts`, `package.json`, `pnpm-lock.yaml`, `pnpm-workspace.yaml`, `tsup.config.ts`, `tsconfig.json`,
`biome.json`, `.npmrc`, `scripts/**`, `.github/**`, `.claude/settings.json`, `.claude/comitor-repo.json`,
`.claude/skills/comitor-review/scripts/**`.

Cộng HAI điều kiện nữa (đều phải đúng mới được đường nhanh), vì ở gói mọi export là API công khai bất kể file nào:
- không file `src/**` nào có trạng thái `D` hay `R` trong `--name-status`;
- không dòng thêm/xoá nào của `src/**` trong `-U0` khớp `^[+-]\s*export\b` hoặc chạm dòng `"use client"`.

Ngưỡng 150 dòng, sidecar, `--full` như module.

## Lockfile

`pnpm-lock.yaml` đổi → nêu gói đổi bản dưới **Đã kiểm**; đổi mà `package.json` không đổi → ❓. `better-auth` xuất hiện
→ 🔴 (như module). Đoạn "`@comitor/ui` đổi bản → quality.md § A" n/a — đây là chính gói. Thay bằng, đọc trên
`package.json`:
- **`dependencies` mới** → nó cài vào MỌI app: cần lý do ghi ở `docs/` (SP § 2, nguyên tắc 6), thiếu → 🟠. Gỡ một
  dependency mà không file nào import vẫn có thể gãy app (`@floating-ui/react`, Bẫy › Entry) → 🟠 nếu không kèm phép đo.
- **`peerDependencies`/`peerDependenciesMeta` đổi** → hàng **Hợp đồng** (X23): thu hẹp dải, nâng sàn, peer bắt buộc
  mới, optional → bắt buộc = BREAKING.
- **`@tiptap/*` ở `devDependencies` không cùng MỘT số chính xác** → 🟠 (CL § Cạm bẫy, mục editor).
- `pnpm-workspace.yaml` mất `allowBuilds: { esbuild: true }` → 🟠 (`pnpm build` hỏng).

## Hàng

| Nhóm | Hàng | Áp/Đổi/Bỏ/Thêm | Luật ở repo này (nguồn) |
|---|---|---|---|
| Kiến trúc | Tầng | Đổi | Module T1–T8 nói về `lib/core`, `stores`, `hooks`, `route.ts` — không tầng nào có ở đây, áp nguyên văn là n/a và bỏ sót luật tầng thật. **X1** tầng dưới không nhập tầng trên: `components/ui` không nhập `composite`/`shell`, `composite` không nhập `shell`; mọi tầng lấy `src/lib`, `src/i18n` (Tier 1 cần tìm không dấu thì lấy `lib/text-search`, không nhập ngược Tier 2). **X2** `src/lib/**` không vào barrel nào (trừ `cn` qua `.`). **X3** `data-grid`, `editor` đứng riêng vì peer; `declare module "@tanstack/react-table"` chỉ ở `data-grid`. 🟠 (CL § Kiến trúc 3 tầng + 9 entry; SP § 3) |
| Kiến trúc | Một luật | Đổi | M3 (API giả) và M4 (`navigation.ts`) trỏ vào thứ không có; luật vẫn là MỘT nguồn: **X4** một bảng, một thân hàm cho một thứ — màu avatar chỉ ở `AVATAR_TONES` (`src/lib/avatar-tone.ts`, hai cửa ra), helper `src/lib/*` không có bản song song ở tầng khác, `editor-core.tsx` là bản DUY NHẤT của menu/ảnh/liên kết cho cả hai trình soạn, `DEFAULT_*_LABELS` là bảng `…En` chứ không là bản dịch thứ hai. 🟠 (CL § Kiến trúc 3 tầng + 9 entry; CL § Cạm bẫy "Màu avatar chỉ có MỘT nguồn"; QD § 7, § 23) |
| Kiến trúc | Ranh giới | Đổi | R1/R3/R5–R7 nói về `server-only`, cookie, `searchParams`, hai cửa dữ liệu — gói không có mã máy chủ; ranh giới thật là directive theo FILE trong `dist/`. **X5** `"use client"` ở dòng ĐẦU mọi file dùng hook/handler/`ref`/API trình duyệt; không thêm ở primitive tĩnh, module thuần; component tĩnh nhận prop component thì giữ tĩnh và tách lá client (khuôn `route-tabs-nav.tsx`). **X6** hằng dữ liệu thuần không nằm trong file `"use client"`; barrel xuất THẲNG từ `*-constants.ts`/module thuần, không vòng qua file client. **X7** import nội bộ có đuôi `.js`; `next/link.js`, `next/navigation.js` giữ đuôi. Thiếu directive, hằng kẹt sau ranh giới 🔴 · thiếu `.js` 🟠 · directive thừa 🟡 (CL § Quy ước "use client đặt per-file", "Import nội bộ LUÔN có đuôi"; CL § Cạm bẫy "Hằng dữ liệu thuần", "Barrel phải lấy hằng THẲNG"; SP § 9) |
| Kiến trúc | Chỗ đặt | Đổi | P1–P6 nói về route, `navigation.ts`, job — không có. **X8** file mới đúng tầng; thêm MỘT dòng `export * from "./<tên>.js";` vào đúng barrel, giữ a-z (`data-grid`, `editor` liệt kê TÊN tường minh — export mới thì thêm dòng tên); chạm peer optional thì không ở `src/index.ts`; bản port mở đầu bằng dòng ghi công và đánh dấu `⚠ Khác thượng nguồn:`. 🟡 · thiếu dòng barrel 🟠 (CL § Thêm component mới; DU § 2) |
| Kiến trúc | Dữ liệu app (thay Account) | Đổi | A1–A6 nói về bảng định danh, màn hình Account, `better-auth` — gói không có database hay đăng nhập; áp nguyên văn là mọi hàng n/a và bỏ sót câu thật. **X9** gói không chứa dữ liệu app: `Workspace[]`, `AppDescriptor[]`, `NavItem[]`, `ShellUser` là KIỂU, app truyền một lần qua `AppShell`/`ShellProvider`; không `fetch`, không URL dịch vụ Comitor viết cứng (gốc Account đi qua prop `accountUrl`), không `process.env`. 🟠 (SP § 2; CL § Cạm bẫy "WorkspaceSwitcher và AppLauncher") |
| Kiến trúc | Entry & peer | Thêm | **X10** `src/index.ts` chỉ chạm peer BẮT BUỘC (react, react-dom, lucide-react, tailwindcss) — kể cả BẮC CẦU qua file nó re-export; tầng kéo peer optional mới thì thành entry mới: `exports` map + barrel + RD § 3 + số entry ở `smoke:entries` cùng lúc. **X11** một tên ở nhiều entry phải là CÙNG binding (ngoại lệ có chủ ý duy nhất: `FormField`/`FormFieldProps`); đừng "dọn trùng" `Toaster`/`SonnerToaster`. **X12** `exports`, `files`, `sideEffects` (chỉ CSS), `type: module`, ESM-only (không thêm CJS): đổi là đổi cách mọi app resolve. Peer optional lọt `.` 🔴 · hai binding cùng tên 🔴 · `exports`/`sideEffects`/`files` đổi không lý do 🟠 (CL § Cạm bẫy "bundle: false + peer optional", "export * chỉ bắt trùng tên", "attw báo"; QD § 2; SP § 3.4) |
| Dữ liệu & bảo mật | Workspace | Bỏ | Không database, không phiên, không truy vấn nào để lọc — n/a thật, không tính vào mẫu số. |
| Dữ liệu & bảo mật | Đường ghi | Bỏ | Không route, không quyền: chốt quyền là của app. Component chỉ nhận cờ (`canEdit`, `readOnly`, `disabled`); control còn bấm được khi read-only là hàng **Trạng thái** (X24), không phải hàng này. |
| Dữ liệu & bảo mật | Toàn vẹn | Đổi | I1–I6, I8 nói về `PUT`, giao dịch, migration — không có; "dữ liệu đã lưu" của gói là thứ app LƯU từ component. **X13** định dạng lưu của trình soạn — markdown GFM, HTML, nhắc `[@Tên](mention:<id>)` / `mention:<kind>/<id>`, `src` ảnh là giá trị app trả (không URL đã ký) — không đổi theo cách làm dữ liệu cũ thôi đọc ra; `renderHTML` là thứ GHI xuống, giá trị chỉ để vẽ đi ở node view; ô bảng markdown một đoạn. **X14** `DataGrid`: `rowIndex` là thứ tự ĐANG HIỆN, `row.index` là vị trí trong `data` — không trộn; tra bằng `rows[rowIndex].original`. I7 Áp (không `new Date("YYYY-MM-DD")`, mốc tuyệt đối theo `timeZone` truyền vào). Đổi định dạng lưu 🔴 · trộn hệ chỉ số 🔴 (app xoá NHẦM bản ghi) · I7 🟠 (ED § 4, § 5; CL § Cạm bẫy "⚠ @comitor/ui/editor", "⚠ DataGrid có HAI hệ chỉ số dòng") |
| Dữ liệu & bảo mật | Tiêm & bí mật | Đổi | S4, S6–S10 nói về máy chủ, log, kho ảnh, CSV, CSP — n/a. Giữ **S1** (không `dangerouslySetInnerHTML` với dữ liệu; HTML đã lưu hiển thị lại qua `RichTextEditor editable={false}`; liên kết chặn `javascript:`), **S2** (`style`/biến CSS không dựng từ chuỗi dữ liệu ngoài bảng ĐÓNG), **S5** (không token/khoá trong diff; publish qua OIDC, không `NPM_TOKEN`). **X15** script mang `nonce` (`DisplayPrefsSeedScript`, script chống nháy của provider) chỉ nhúng HẰNG đã lọc qua tập đóng — nonce làm CSP không chặn thứ chèn vào. Thêm vào `files` của `package.json` là ship cho mọi app — đọc từng mục. 🔴 (ED § 4, § 7; RD § 5; CL § Publish) |
| Dữ liệu & bảo mật | Hướng hỏng | Đổi | H1, H3–H6 nói về danh bạ, mã lỗi API, env, 429, log viết HOA của module — n/a. **X16** lỗi của LẬP TRÌNH VIÊN dùng gói phải NÉM TO, không im lặng: helper client gọi ở server ném, không trả `undefined`; không trả một mặc định trông hợp lệ (`length === 0`); thông điệp `throw`/`console.*` tiếng Việt. H2 Áp cho component tự nạp (uploader: lỗi tải là trạng thái lỗi có thử lại). H7 Áp. X16 🟠 · H7 🟡 (CL § Cạm bẫy "Hằng dữ liệu thuần"; CL § Quy ước "Tiếng Việt") |
| Quy ước | i18n | Đổi | N1–N8 nói về `messages/`, `next-intl`, `t()` — gói không có cả hai; áp nguyên văn là báo mọi chuỗi hợp lệ trong bảng `…En`/`…Vi` là sai chỗ. **X17** mọi chuỗi hiển thị (kể cả `aria-label`, `sr-only`, `title`, lời thông báo kéo thả) ở `src/i18n/namespaces/<ns>.ts`: `<ns>En` định hình dạng, `<ns>Vi` chú thích cùng kiểu; ghi vào `messages.ts`; đọc bằng `useComitorMessages`/`useComitorLabels`; ưu tiên prop → provider → `"en"`; mặc định TIẾNG ANH. Chỗ máy không nhận ra: `i18n-ignore: <lý do>`. Nước, tiền tệ không suy từ ngôn ngữ. N2 Áp (đọc cả hai bảng), N4 Áp (khoá có số là HÀM). Thêm khoá vào namespace làm đỏ typecheck của app tự cấp ngôn ngữ thứ ba → "App phải làm gì" (X25). 🟠 (CL § Quy ước "Tiếng Việt", "App Comitor LUÔN truyền ngôn ngữ"; CL § Thêm component mới; QD § 36) |
| Quy ước | Màu & UI | Đổi | U1 "app KHÔNG sở hữu màu" NGƯỢC ở đây — gói là chủ token, áp nguyên văn thì mọi dòng `styles.css` thành phát hiện; U6 (`audit.mjs`) n/a. **X18** token: `styles.css` là nguồn, `src/tokens.ts` mirror — sửa cùng nhau (thứ cố ý không mirror: QD § 21); màu mới khai đủ vai trò `--x`/`--x-foreground`/`--x-ink` có dùng, ĐO từng vai trò trên đúng nền và ghi số; hai bảng màu chỉ khác ở khai báo biến; `@theme inline` giữ; bóng qua `--elevation-*`; `var()` biến của app có fallback. **X19** component chỉ dùng token VAI TRÒ: không thang thô (`bg-gold-300`, `bg-ash-300`, `bg-input/30`), không hex (trừ vector logo), không class động, `ash-*` không `gray-*`, không `shadow-[…]`, hover không `/90`, `--x` không làm chữ, viền control `border-input`/`border-control-edge`, icon không màu alpha (`opacity-*` được), `style` chỉ `var(--x)` TRẦN. **X20** miễn trừ `contrast-exemptions.json` có `reason` nói vì sao không chịu ngưỡng, số đo lại. U3 thành: dùng primitive của chính gói trước khi viết mới; port không trùng component đã có. U7 Áp. Vai trò sai 🟠 (module để 🟡: ở app nó hỏng một màn, ở gói nó hỏng mọi app) · thang thô/hex/class động 🟠 · `tokens.ts` lệch 🟠 (CL § Quy ước "Hợp đồng BA VAI TRÒ", "HAI BẢNG MÀU", "Dùng token SEMANTIC"; HM § 1, § 3, § 7b, § 8; RD § 6) |
| Quy ước | Ngôn ngữ & tên | Đổi (chỉ L4) | L1–L3, L5 Áp, thêm: tên script `package.json` và khoá JSON cấu hình tiếng Anh; chuỗi cổng IN RA vẫn tiếng Việt — đừng "đồng bộ". L4 (chặn tên dự án, đối tác khác của đội) va với ghi công BẮT BUỘC của giấy phép MIT khi thượng nguồn là một dự án như thế: tên thượng nguồn đã port (tablecn, Dice UI, shadcn/ui, `@stmjsc/ui`) và phụ thuộc thật (Radix, Tiptap, Uppy, recharts, TanStack, dnd-kit…) ĐƯỢC viết ở dòng ghi công đầu file, `⚠ Khác thượng nguồn:`, `LICENSE`, `docs/`, README, CHANGELOG. KHÔNG được ở chuỗi hiển thị (`namespaces/`), dữ liệu mẫu, ví dụ JSDoc, tên token/kiểu/prop. Xoá dòng ghi công 🟠 · tên lạ trong chuỗi hiển thị 🟡 (CL § Quy ước "Tiếng Việt", "App Comitor LUÔN truyền ngôn ngữ"; DU § 6; DG § 12) |
| Quy ước | Comment | Áp | C1–C5 nguyên văn. Thêm: JSDoc của thứ được export đi vào `.d.ts` — app đọc nó trong trình soạn mã, sai là C2 🟠; năm chỗ cảnh báo của `ChartContainer` giữ đủ; không ghim số đếm (đo bằng lệnh) (CL § Cạm bẫy "Biểu đồ", "export * chỉ bắt trùng tên") |
| Quy ước | Kiểu | Đổi | K1 coi `!` là 🟡 — repo này TẮT `noNonNullAssertion` (`biome.json`), nên `!` đơn thuần không là phát hiện; chỉ báo khi nó dập một nhánh `undefined` có thật (K2). K5 (`lib/contracts/`) n/a: kiểu export LÀ API — thu hẹp kiểu prop/tham số, đổi union, bỏ trường của `shell/types.ts` là BREAKING (hàng **Hợp đồng**). K3, K4 Áp (`biome.json`, `tsconfig.json`, `tsup.config.ts` đổi để cho qua 🟠) (SP § 10) |
| Chất lượng | Đúng | Đổi (bảng anh em) | Bảng anh em của module (route, api-client, router giả, `navigation.ts`) n/a. Ở đây: đổi component → barrel, RD § 5, namespace i18n + `messages.ts`, `docs/<tầng>.md`, CHANGELOG; `styles.css` ⇄ `tokens.ts`; `editor-core.tsx` → cả `MarkdownEditor` lẫn `RichTextEditor`; `userMenuProps` header ⇄ `MobileMenu`; lưới → thử trên dữ liệu ĐANG SẮP; `Button` → bản port Dice UI tự đặt cỡ `svg`; effect chạy lại dưới StrictMode (`use-modal-return-focus`). Còn lại Áp (CL § Cạm bẫy "⚠ DataGrid có HAI hệ chỉ số dòng", "⚠ Con có autoFocus", "⚠ Bản port Dice UI") |
| Chất lượng | Test | Đổi | E1, E3–E6, E8 đòi `*.test.ts`, store, API giả, Playwright — repo KHÔNG có test runner; cổng là script. **X21** thay đổi có cổng tương ứng thì cổng có ca mới: hàm thuần `shell/utils.ts` → `test:nav-active`; lược đồ trình soạn → `test:editor-markdown`; `style`/màu `DataGrid` → `test:grid-render`; entry mới hay ca từng đổ trang → `smoke:entries` (render khói); luật cổng màu → `test:a11y-gate`; luật i18n → `--self-test` của `check-i18n.mjs`. E2 Áp cho ca mới (phải ĐỎ trên mã cũ), E7 Áp (dòng `Kiểm thế nào:` nói đã thấy đỏ). Thiếu ca 🟡 · nới cổng hay xoá ca đối chứng 🟠 (CL § Lệnh; QD § 33.5) |
| Chất lượng | Hợp đồng | Đổi | H1–H7 nói về `lib/contracts`, `errors.code`, route, `x-request-id` — n/a; hợp đồng của gói là BỀ MẶT CÔNG KHAI. **X22** mọi thứ app chạm được: tên export, prop (tên, kiểu, mặc định), kiểu export, hành vi mặc định app THẤY (ngôn ngữ, vị trí mục, hiệu ứng), tên token/biến CSS và utility Tailwind sinh từ nó, `data-slot`/`data-*` app nhắm CSS, định dạng lưu (X13), tên entry. Xoá/đổi tên/thu hẹp/đổi mặc định = BREAKING → MAJOR + "cách chuyển"; thêm tương thích = MINOR. Nhiều khoản BREAKING không làm `typecheck` của app đỏ — xét HÀNH VI, không xét kiểu. **X23** dải peer: thu hẹp, nâng sàn, thêm peer bắt buộc = BREAKING. BREAKING không MAJOR 🔴 · MAJOR thiếu cách chuyển 🟠 (CL § Publish; RD § 3, § 5; SP § 2) |
| Chất lượng | Trạng thái | Đổi | D2 (`formerMember`), D3 (`NotYetActive`), D5 (phím của app) n/a. **X24** component đúng ở NĂM trục hiển thị (sáng/tối · tương phản cao · mật độ compact · cỡ chữ sm/lg · bộ màu theme `data-palette` — từ comitor-ui 3.15.0; tô theo màu thương hiệu bằng `brand-*`/token semantic, không `gold-*`) và các trạng thái control (hover, focus-visible, disabled, readonly, bật/đã chọn, indeterminate); trục mới không dựng bằng `next-themes` thứ hai; cỡ Vừa GỠ thuộc tính chứ không ghi cỡ tuyệt đối. D1 Áp cho component có dữ liệu (rỗng, lọc không ra, lỗi), D4 Áp (chữ `en` dài, 375px). 🟡 · thiếu nhánh lỗi 🟠 (CL § Quy ước "NĂM TRỤC HIỂN THỊ"; HM § 4) |
| Chất lượng | Tối giản | Đổi (mã chết) | Module coi thứ "không gì đọc" là mã chết — ở gói, export không ai TRONG repo gọi vẫn là API công khai: xoá nó là BREAKING (X22). Mã chết chỉ là thứ không export và không tới được từ entry nào. Đừng "dọn trùng" `FormField`/`Toaster`, `composite/text-utils.ts` xuất lại từ `lib/text-search`, hay `prepublishOnly` trùng workflow (cố ý). Còn lại Áp, 🟡 (CL § Cạm bẫy "Hai FormField"; CL § Publish) |
| Chất lượng | Tài liệu | Đổi | F1 → `## Số bản`; F2 (file khung) n/a — repo không sinh module; F4 chỉ cho `.claude/skills/comitor-review/**`; F5 n/a; F6 thay bằng **X25**: đổi hợp đồng (X22) mà app phải làm gì → mục CHANGELOG có `### App phải làm gì` (skill `comitor-ui` ở starter đọc mục đó của MỌI bản nằm giữa khi nâng gói); component hay entry mới → dòng ở RD § 5 (kèm số file) và RD § 3. F3 Áp (danh sách cổng ở CL § Lệnh, RD § 7, `prepublishOnly`, hai workflow phải khớp nhau). F7 đổi khuôn: `feat: X.Y.Z — mô tả`, `fix: X.Y.Z — …`, `ci: …` (`git log`). Thiếu "App phải làm gì" cho đổi hành vi 🟠 · RD § 5 lệch 🟡 (CL § Thêm component mới, § Publish; RD § 5) |

Mẫu số bảng Kiểm: Kiến trúc /6 · Dữ liệu & bảo mật /3 · Quy ước /5 · Chất lượng /6 — bỏ Workspace và Đường ghi, Account
đổi tên thành **Dữ liệu app**, thêm **Entry & peer**. Hai hàng bỏ KHÔNG in thành n/a: chúng không có trong bảng.

## Công cụ máy

- `node .claude/skills/comitor-ui/scripts/audit.mjs` → **Bỏ**: nó quét cách APP dùng gói, và repo không mang skill đó.
  Phần tương ứng ở đây là `lint:a11y` + `test:i18n` của chính repo.
- `check-refs.mjs` → **Bỏ**: skill `comitor-test` không có ở repo này; đường dẫn của bản chép `comitor-review` kiểm ở starter.
- `pnpm exec biome check <file đã sửa>` sau bước 4 → **Áp** (chỉ khi `--fix`).
- **Thêm:** `node .claude/skills/comitor-review/scripts/sections.mjs --check-table` khi diff đổi một đề mục, hay đầu một
  gạch đầu dòng được nháy ở bảng `## Tài liệu quy định`/`## Bẫy`, của CL/RD/SP/HM/QD/DG/ED/DU. Đỏ → 🟡 hàng **Tài liệu**:
  "đề mục đổi, hồ sơ `library-ui` ở starter phải sửa theo".

Cổng của repo (`lint`, `typecheck`, `test:i18n`, `lint:a11y`, `test:a11y-gate`, `test:nav-active`, `test:grid-*`,
`test:editor-markdown`, `verify:directives`, `smoke:entries`, `check:exports`, `version:check`) KHÔNG chạy trong review:
không có `pnpm check` gộp, `allowed-tools` không gồm chúng, và `ci.yml` chỉ chạy tay — `prepublishOnly` (cộng `lint`,
`version:check` chạy tay) mới là cổng, và nó lên tiếng lúc PUBLISH, không lúc merge. Vì vậy thứ cổng bắt được mà thấy
trên diff thì VẪN báo (khác module, nơi "đừng báo lại thứ `pnpm lint` đã đỏ"): không có gì bảo đảm nó đã chạy.

## Không bao giờ sửa

Như module (file bẩn), trong đó `messages/*.json`, `prisma/migrations/**`, khuôn `.tpl`, file khung → n/a; thay bằng:
- `src/i18n/namespaces/**` — chữ mọi app hiển thị;
- `styles.css`, `src/tokens.ts`, `scripts/contrast-exemptions.json` — giá trị đã đo, miễn trừ là quyết định;
- mọi barrel (`src/index.ts`, `src/*/index.ts`, `src/form.ts`) và mọi khai báo được export — xoá hay đổi tên là BREAKING
  dù không gì trong repo gọi nó;
- dòng ghi công đầu file, `⚠ Khác thượng nguồn:`, `LICENSE`;
- `CHANGELOG.md` và `package.json` `version` — bậc phiên bản là quyết định của tác giả;
- `.claude/skills/comitor-review/**` (bản chép).

## Mức

Thêm vào danh sách Mức (§6); các dòng module về `workspaceId`, `@api-guard`, migration, hợp đồng liên module, ranh giới
Account, Server Action, API giả, file khung → không áp.

- **🔴** thêm: BREAKING (X22, X23) mà không bump MAJOR; peer optional lọt đồ thị import của `src/index.ts` (X10); hai
  binding khác nhau cùng tên ở hai entry (X11); đổi định dạng lưu làm dữ liệu cũ thôi đọc ra (X13); trộn hệ chỉ số dòng
  (X14); file dùng hook/handler thiếu `"use client"` dòng đầu, hằng thuần kẹt trong file client (X5, X6); chuỗi không
  phải hằng vào script mang nonce (X15); thứ bí mật vào `files`.
- **🟠** thêm: BREAKING có MAJOR mà thiếu "cách chuyển"; đổi hành vi app thấy mà thiếu `### App phải làm gì` (X25);
  thang màu thô, hex, class động, `gray-*`, `shadow-[…]`, `/90`, vai trò màu sai (X19 — module để vai trò sai ở 🟡);
  `styles.css` ⇄ `tokens.ts` lệch (X18); import nội bộ thiếu `.js` (X7); chuỗi hiển thị ngoài `…En`/`…Vi` (X17);
  dependency mới không lý do; component mới thiếu dòng barrel; tầng dưới nhập tầng trên (X1); lỗi lập trình viên im
  lặng (X16); nới một cổng hay xoá ca đối chứng của nó.
- **🟡** thêm: RD § 3/§ 5 lệch (dòng, số file, số entry); barrel không a-z; `"use client"` thừa; JSDoc export sai mà
  không dẫn làm sai.

## Số bản

Thay F1. `version:check` (`scripts/check-version.mjs`) đòi đúng HAI điều: `package.json` = mục `## [X.Y.Z]` ĐẦU TIÊN của
CHANGELOG (Keep a Changelog, có ngoặc vuông), và số đó CHƯA có trên npm (fail-open khi npm không trả lời). KHÔNG có
"mỗi PR tăng một lần so với gốc nhánh": gói phát hành theo tag, giữa hai lần có thể nhiều commit, và ép tăng mỗi PR là
đẻ số ma không có trên npm (comment đầu file) — nên F1 nguyên văn báo sai ở mọi PR thứ hai trước một lần phát hành.
Luật ở đây:

- PR đổi thứ đi vào tarball (`src/**`, `styles.css`, `package.json` phụ thuộc/peer/`exports`/`files`) ghi vào mục ĐẦU
  còn CHƯA phát hành; mục đầu đã có trên npm → mở mục mới VÀ tăng `version` trong cùng PR. PR chỉ-tài-liệu (`docs/**`,
  `CLAUDE.md`, `scripts/**` không đổi cổng) không cần mục.
- Bậc là bậc của khoản MẠNH NHẤT từ bản đã phát hành gần nhất (gộp cả mục): BREAKING → MAJOR · thêm tương thích → MINOR
  · sửa → PATCH (CL § Publish, SemVer thật từ `1.0.0`; luật "0.x breaking → MINOR" chỉ cho lịch sử). Một PR đưa BREAKING
  vào mục MINOR chưa phát hành phải nâng số của mục lên MAJOR.
- Mỗi khoản BREAKING có dòng "cách chuyển" (tên cũ → tên mới → sửa thế nào); khoản không viết được cách chuyển thì chưa
  đủ điều kiện phát hành. Mục có đổi app thấy được có `### App phải làm gì`; dòng `Kiểm thế nào:` là khuôn của các mục 3.x.
- Không sửa nội dung mục đã phát hành (trừ đính chính có dấu vết); không đè version đã publish (SP § 11).

Mức: bậc thấp hơn khoản mạnh nhất 🔴 (`^X` kéo nó vào mọi app) · lệch `package.json`/CHANGELOG, mục đã phát hành bị
viết thêm, thiếu cách chuyển, thiếu "App phải làm gì" 🟠 · thiếu `Kiểm thế nào:` ⚪.

## Bẫy

Thay `references/pitfalls.md`. Mỗi dòng là lỗi ĐÃ XẢY RA ở `@comitor/ui`, kèm cách thấy trên diff. Gần như dòng nào
cũng có chung một điểm: mọi cổng xanh, vì mỗi mảnh đúng khi đứng riêng.

### Entry, peer và build

| Lỗi | Thấy trong diff thế nào | Nguồn |
|---|---|---|
| `0.2.1` publish với entry `/shell` hỏng cho Node ESM: `next/link` thiếu đuôi, bundler tha nên mọi cổng xanh | Specifier tới gói không có `exports` map viết không đuôi `.js` | CL § Cạm bẫy ("shell-context.tsx import") · QD § 6 |
| Re-export một file có `import "recharts"` từ `src/index.ts` buộc mọi app cài recharts — gãy ở bước resolve của bundler | Dòng barrel mới ở `src/index.ts` trỏ tới file (hay file nó nhập) chạm peer optional | CL § Cạm bẫy ("bundle: false + peer optional") · QD § 2 |
| `useIsMac` ở `.` và `/shell` là HAI thân hàm cùng tên; `normalizeVi` hai khai báo giống nhau | Tên export mới trùng tên ở entry khác mà không re-export cùng binding | CL § Cạm bẫy ("export * chỉ bắt trùng tên") · QD § 18, § 23 |
| Gỡ `@floating-ui/react` "cho gọn" (không file nào import) thì pnpm strict gãy ngay ở entry chính — `@diceui/shared` import nó dù khai là peer | `dependencies` mất một gói không thấy import nào | CL § Cạm bẫy ("⚠ Bản port Dice UI") |
| Tag `3.5.0` đỏ vì bước `.d.ts` hết heap; log in "Build success" ngay trước đó | Tầng mới nặng kiểu, hay workflow mất `NODE_OPTIONS` | CL § Cạm bẫy ("⚠ Bước .d.ts") |

### Ranh giới server/client

| Lỗi | Thấy trong diff thế nào | Nguồn |
|---|---|---|
| `0.2.1`: 10 hằng thuần nằm trong file `"use client"` — Server Component đọc ra `undefined`, `DEFAULT_DATE_PRESETS.length` ra `0` | `export const` dữ liệu trong file mở đầu bằng `"use client"` | CL § Cạm bẫy ("Hằng dữ liệu thuần") |
| Hằng đúng chỗ mà barrel re-export VÒNG qua file client — phép kiểm 1, 2 xanh, RSC vẫn `undefined` | Barrel lấy hằng từ file component thay vì `*-constants.ts` | CL § Cạm bẫy ("Barrel phải lấy hằng THẲNG") · QD § 33.4 |
| esbuild nuốt directive ở đầu file; build xanh mà `dist/` mất `"use client"` | Đổi `tsup`/esbuild mà không nhắc `verify:directives` | CL § Cạm bẫy ("esbuild từng có bug") |
| Hằng của trục hiển thị đặt cạnh provider client: root layout đọc `undefined`, không lỗi | Hằng trục mới trong file provider | CL § Quy ước ("NĂM TRỤC HIỂN THỊ") |

### Định dạng lưu và danh tính dòng

| Lỗi | Thấy trong diff thế nào | Nguồn |
|---|---|---|
| `3.3.4`: `Ctrl+Backspace` trên lưới đang sắp đưa NHẦM dòng vào `onRowsDelete` — hộp hỏi xoá CV-007 khi đã tick CV-019 | `row.index` dùng ở chỗ mà API nói `rowIndex` | CL § Cạm bẫy ("⚠ DataGrid có HAI hệ chỉ số dòng") |
| Ô bảng markdown nhiều khối mục dần thành `&lt;br&gt;` qua từng lần lưu | Lược đồ markdown mở `block+` cho ô, hay luật nhập chèn KHỐI mới chưa thử trong ô | CL § Cạm bẫy ("⚠ @comitor/ui/editor") · ED § 5 |
| Trên lược đồ Tiptap gốc chưa vá, vòng tài liệu ↔ markdown trượt 16/46 ca — lỗi chỉ lộ ở lần MỞ sau | Đổi `markdown-extensions.ts`/`markdown-syntax.ts` | RD § 7 · ED § 5 |
| Bơm bộ tách từ vào `marked` TOÀN CỤC ở mỗi lần mount: parse chậm 15× sau 200 lần | Bỏ `createMarkedInstance` | CL § Cạm bẫy ("⚠ @comitor/ui/editor") |

### Màu và token

| Lỗi | Thấy trong diff thế nào | Nguồn |
|---|---|---|
| `0.1.0`: 19 chỗ `shadow-[…rgba]` — dialog, popover mất tín hiệu độ cao ở dark | `shadow-[` trong component | CL § Cạm bẫy ("Bóng đi qua HAI lớp tên") · QD § 13 |
| `AppLauncher` tô icon bằng `--app-accent` lên tint `/15` của chính nó: 1,69:1 | `text-app-accent` (không `-ink`, không `-foreground`) | CL § Cạm bẫy ("--app-accent là màu NỀN") · QD § 8 |
| Icon `sidebar-menu-item.tsx` tô màu alpha — lộ vệt nối ở nét cắt nhau, dù có sẵn mục miễn trừ đã duyệt | `text-x/NN` cạnh `size-*` | CL § Cạm bẫy ("⚠ Icon KHÔNG được tô") · HM § 7b |
| Hai bảng tone avatar viết tay: một người ra hai màu giữa web và email | Bảng màu thứ hai cạnh `AVATAR_TONES` | CL § Cạm bẫy ("Màu avatar chỉ có MỘT nguồn") · QD § 7 |
| `var(--font-inter-mono)` không fallback: app không khai biến thì CẢ khai báo vô hiệu | `var(--…)` biến của app không có đối số thứ hai | CL § Cạm bẫy ("var() tiêu thụ biến của app") · QD § 20 |
| `animate-in duration-250` làm `ActionBar` trượt ngang 120px mỗi lần mở (`3.3.0`) | `duration-*` trên phần tử chỉ cần keyframe, thiếu `transition-none` | CL § Cạm bẫy ("⚠ Tailwind v4") |
| Mục miễn trừ ghi "7,03:1" cho một cặp thật ra 5,78:1 | Số trong `reason` không kèm phép đo lại | HM § 8 Miễn trừ |

### Ngôn ngữ

| Lỗi | Thấy trong diff thế nào | Nguồn |
|---|---|---|
| `3.0.0` đổi mặc định sang tiếng Anh mà không đổi một kiểu — app quên `ComitorLocaleProvider` hiện "Cancel" giữa màn hình tiếng Việt | Đổi mặc định của provider hay bảng chữ, không nằm trong mục MAJOR | CL § Quy ước ("App Comitor LUÔN truyền ngôn ngữ") · QD § 36 |
| Script cổng đặt tên biến tiếng Việt (`tokenTrangTri`, `hinhRo`); khoá JSON miễn trừ `mienTru`/`lyDo` — đã đổi hết | Định danh tiếng Việt không dấu trong `scripts/**` | CL § Quy ước ("App Comitor LUÔN truyền ngôn ngữ") · HM § 8 Miễn trừ |

### Port từ thượng nguồn

| Lỗi | Thấy trong diff thế nào | Nguồn |
|---|---|---|
| `DataGrid` chép `hsl(var(--card))` từ hệ token HSL 3 kênh: `hsl(#ffffff)` vô hiệu, cột ghim trong suốt; `opacity: 0.97` cùng object `style` sống tới `3.3.2` | `hsl(`/`rgb(` bọc `var()` trong `style`; khoá `style` không phải màu chép nguyên | CL § Cạm bẫy ("⚠ PORT TỪ REPO KHÁC") |
| Mã Dice UI giả định `Button` tự đặt cỡ `svg`: icon ra 24px | Icon trong `<Button>` không `size-*`, phần tử chứa không đặt cỡ | CL § Cạm bẫy ("⚠ Bản port Dice UI") |
| `Stepper`/`Timeline` tự đăng ký vị trí trong layout effect: HTML server ghi "0" | Đọc DOM hay đếm trong render | CL § Cạm bẫy ("⚠ Bản port Dice UI") |

### API công khai và phát hành

| Lỗi | Thấy trong diff thế nào | Nguồn |
|---|---|---|
| `3.7.1`: `Badge asChild` của `3.7.0` ném `React.Children.only` — đổ cả trang prerender; `smoke:entries` chỉ NẠP module nên không thấy | Thêm phần tử con cạnh `children` trong nhánh `asChild`/`Slot` | CL § Lệnh |
| `1.8.0` lên npm bằng tay, không tag — mất truy ngược version → commit | Publish ngoài `npm version` + `git push --follow-tags` | CL § Publish |
| Thêm `--provenance` trên repo private: publish đỏ ở bước CUỐI (`E422`) | Cờ `--provenance` trong `publish.yml` | CL § Publish |

### Cổng không kiểm gì

| Lỗi | Thấy trong diff thế nào | Nguồn |
|---|---|---|
| `test:grid-contract` nằm trong `prepublishOnly` mà vắng khỏi mọi danh sách, và khỏi `ci.yml` tới `1.11.0` | Script cổng mới không có ở CL § Lệnh, RD § 7, hai workflow | CL § Lệnh |
| `test:a11y-gate` không ở CI trước `0.2.2` — cổng canh cổng chỉ lên tiếng lúc phát hành | Cổng chỉ thêm vào `prepublishOnly` | QD § 33.5 |
| Cổng tương phản in ✓ cho bảng màu mặc định mà nó chưa từng đo (trước `1.6.0`) | Phép kiểm chỉ chạy trên một tổ hợp bảng × theme | QD § 34 |
| `verify:directives` phép 2 mù với `const X = {…}; export { X }` | Phép kiểm chỉ khớp một dạng khai báo | QD § 33.3 |

### Tài liệu nói dối

| Lỗi | Thấy trong diff thế nào | Nguồn |
|---|---|---|
| README liệt kê 2/13 helper kẹt sau ranh giới client | Danh sách tay của thứ đếm được bằng lệnh | QD § 33.2 |
| CL ghi "13" helper `cva`/hook sau ranh giới client — sai từ lúc `progress.tsx` thêm hai | Con số ghim trong tài liệu | CL § Cạm bẫy ("Hằng dữ liệu thuần") |
| Ba cách đếm tên trùng xuyên entry ra ba con số | Số đếm tên export trong `.md` | CL § Cạm bẫy ("export * chỉ bắt trùng tên") |
| "dải 0.x: breaking → MINOR" còn sống sau `1.0.0`; câu "1.8.0 không qua `lint`" sai | Luật cũ không đánh dấu hết hiệu lực | CL § Publish |
| SP mô tả một pipeline CI không tồn tại | Tài liệu tả workflow mà `.github/` không có | SP § 11 |
