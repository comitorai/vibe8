# Hồ sơ `account` — Comitor.Account (IdP OIDC)

`comitor-account`: IdP chuẩn OIDC dùng chung của hệ Comitor — Next.js App Router full-stack + Better Auth
1.7.1 + `@better-auth/oauth-provider` + Prisma, kèm gói `packages/account-sdk` (`@comitor/account-sdk`) mà mọi
module cài qua registry. Repo khai `.claude/comitor-repo.json` = `{"profile": "account"}`.

Khác module ở GỐC: ba câu hỏi mà module coi là "của Account" (*bạn là ai* · *thuộc workspace nào với vai trò
thô gì* · *workspace được dùng app nào*) là việc CHÍNH của repo này. Vì vậy vài luật module lật ngược: bảng
định danh, màn hình tài khoản, import `better-auth`, bộ giới hạn 429 đều HỢP LỆ ở đây — thứ bị canh là chúng
không rò ra ngoài ba câu đó. Không có `AGENTS.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, docs/migration.md;
luật nằm ở `CLAUDE.md` (dài, đọc theo mục) và `docs/kien-truc-ung-dung.md` (số mục KHÁC starter).

```json profile
{
  "docs": {
    "CL": "CLAUDE.md",
    "KT": "docs/kien-truc-ung-dung.md",
    "RD": "README.md",
    "SDK": "packages/account-sdk/README.md",
    "TK": "docs/trien-khai.md",
    "HG": "docs/handoff-webhook-gui-ngam.md"
  },
  "table": "references/profiles/account.md",
  "pitfalls": "references/profiles/account.md",
  "pitfallSections": {
    "Kiến trúc": ["Bẫy › Một luật và tầng"],
    "Dữ liệu & bảo mật": ["Bẫy › Token và đường ghi", "Bẫy › Better Auth", "Bẫy › Dữ liệu và thời gian", "Bẫy › Hướng hỏng"],
    "Quy ước": ["Bẫy › Đa ngôn ngữ", "Bẫy › Giao diện"],
    "Chất lượng": ["Bẫy › API giả và kiểm chứng", "Bẫy › Tài liệu và phiên bản"]
  }
}
```

## Tài liệu quy định

Thay `references/governing-docs.md`. Cách đọc giống hệt (khớp ĐẦU TIÊN, bốn hàng cuối CỘNG THÊM, đọc bằng
`sections.mjs`, nháy kép = gạch đầu dòng). Viết tắt: **CL** `CLAUDE.md` · **KT** `docs/kien-truc-ung-dung.md` ·
**RD** `README.md` · **SDK** `packages/account-sdk/README.md` · **TK** `docs/trien-khai.md` · **HG**
`docs/handoff-webhook-gui-ngam.md`. ⚠ `CL § Cạm bẫy` trần là ~620 dòng — chỉ hàng tầng OIDC đòi cả mục.

| Đường dẫn đổi (glob) | Đọc | Mục quyết định |
|---|---|---|
| `lib/auth.ts`, `lib/auth-client.ts`, `lib/permissions.ts`, `lib/totp-replay.ts`, `lib/two-factor-enroll-guard.ts`, `lib/audit-plugin.ts`, `lib/workspace-hooks.ts`, `lib/oauth*.ts`, `lib/oidc-metadata.ts`, `app/api/auth/**`, `app/.well-known/**` | CL; KT | CL § Cạm bẫy (toàn bộ, kể cả mục con), § Quy ước bắt buộc giữ ("Workspace KHÔNG nằm trong token", "Ghim phiên bản Better Auth chính xác"), § Ranh giới Account / App · KT § 8 8.7, § 13 |
| `proxy.ts`, `next.config.ts`, `lib/core/csp.ts` | CL | CL § CSP, § CAPTCHA, § Kiểm chứng thay đổi › MỖI LẦN ĐẨY LÊN `main` |
| `lib/api-client/fake/**`, `app/dev/**`, `app/fake-screens*.ts`, `lib/fake-mode.ts`, `lib/core/fake-routes.ts` | KT; CL; skill `comitor-test` | KT § 8, § 9, § 15 · CL § Kiến trúc giao diện › API giả + Playwright · `comitor-test/references/fake-api.md` |
| `lib/core/**` | KT; CL; skill `comitor-test` | KT § 4 Tầng 1, § 11 · CL § Kiến trúc giao diện, § Test đơn vị · `comitor-test/references/unit-core.md` |
| `lib/contracts/**` | KT | KT § 4 Tầng 0, § 6 |
| `lib/api-client/**` | KT; CL | KT § 4 Tầng 2 · CL § Kiến trúc giao diện ("Cổng API là MỘT PHƯƠNG THỨC CHO MỘT ENDPOINT", "Ba endpoint trả HTTP 200") |
| `stores/**` | KT; skill `comitor-test` | KT § 4 Tầng 3, § 15 · `comitor-test/references/stores.md` |
| `hooks/**` | KT | KT § 4 Tầng 4 |
| `lib/api/**` | CL; KT | CL § Cạm bẫy › Ranh giới TOKEN, § Giới hạn tần suất cho API tự viết · KT § 4 Rìa B, § 15 |
| `app/api/**/route.ts` | KT; CL | KT § 4 Rìa B · CL § Cạm bẫy › Ranh giới TOKEN, § Cạm bẫy › Hai đường ghi, § Cạm bẫy › Vòng qua một chốt, § Cạm bẫy › Vài điều nhỏ hơn, § Cạm bẫy › Cạm bẫy MỚI — đo được khi dựng nhóm C, § Giới hạn tần suất cho API tự viết · RD § Hợp đồng API |
| `app/**/page.tsx`, `app/**/layout.tsx` | KT; CL | KT § 4 Rìa A · CL § Kiến trúc giao diện › Server Component đọc, § Kiến trúc giao diện › Chặn vai trò bằng route group |
| `app/(auth)/**` | CL | CL § Cạm bẫy › Cạm bẫy MỚI — đo được khi ghép giao diện xác thực, § Cạm bẫy › Cạm bẫy MỚI — soát trợ năng, § CAPTCHA |
| `app/**/*.tsx`, `components/**` | KT; CL; skill `comitor-ui` | KT § 4 Tầng 5, § 7 · CL § Đa ngôn ngữ › Chuỗi nào ở đâu, § `@comitor/ui` 3.x, § `FormField` trong hộp thoại, § Hộp thoại dài, § Cạm bẫy › Cạm bẫy MỚI — soát trợ năng · `comitor-ui/SKILL.md` bảng "Cần gì → dùng gì" |
| `lib/webhooks/**`, `app/api/cron/**`, `lib/after-response.ts` | CL; HG | CL § Cạm bẫy › Vài điều nhỏ hơn ("`localhost.`", "`NULL <= now`") · HG § 2 |
| `lib/mail.ts` | CL | CL § Email |
| `lib/storage.ts`, `app/api/account/avatar/**`, `app/api/**/logo/**` | CL | CL § Lệnh ("Kho đối tượng"), § Tải tệp |
| `lib/*.ts` (máy chủ, còn lại) | KT; CL | KT § 6 · CL § Kiến trúc giao diện › Server Component đọc, § Cạm bẫy › Vài điều nhỏ hơn, § Cache phiên trong cookie |
| `prisma/**` | CL; TK | CL § Ranh giới Account / App, § Cạm bẫy › danh mục ứng dụng đa ngôn ngữ, § Cạm bẫy › Vài điều nhỏ hơn ("Ràng buộc duy nhất phải ở DATABASE") · TK § A.2 |
| `messages/**`, `i18n/**`, `lib/i18n/**` | CL; KT | CL § Đa ngôn ngữ · KT § 7 |
| `verify/**` | CL; KT | CL § Kiểm chứng thay đổi · KT § 10 `verify/` không bị thay thế, § 10 Đối chứng âm tính |
| `tests/**`, `**/*.test.ts`, `playwright.config.ts`, `vitest.config.ts` | CL; KT; skill `comitor-test` | CL § Test đơn vị · KT § 10 · `comitor-test/SKILL.md` |
| `packages/account-sdk/**` | SDK; CL | SDK § Đây không chỉ là tiện ích, § Nguyên tắc phiên, § Bốn lớp guard · CL § Kiến trúc ("`@comitor/account-sdk` là lớp cách ly") |
| `scripts/seed.ts` | CL | CL § Lệnh, § Cạm bẫy › Cạm bẫy MỚI — `client_name` |
| `.github/**`, `scripts/check-*.ts` | CL; chính file đó | CL § Kiểm chứng thay đổi · comment đầu file |
| `.claude/skills/<tên>/**` | `MAINTAINING.md` của skill đó | toàn bộ; ở đây là BẢN CHÉP (`quality.md` F4) |
| `.claude/settings.json` | skill này | `MAINTAINING.md` §2 |
| `package.json`, `pnpm-workspace.yaml`, `pnpm-lock.yaml`, `biome.json` | CL; KT | CL § Ghim công cụ, § Ghim công cụ › Nâng phụ thuộc, § `@comitor/ui` 3.x, § Hộp thoại dài ("`pnpm add @comitor/ui@<bản mới>`") · KT § 11 |
| `docs/**`, `README.md`, `CLAUDE.md` | — | không có mục riêng: hàng **Tài liệu** (F3) áp nguyên |
| `poc/**` | — | bằng chứng ĐÔNG LẠNH về Better Auth 1.7.1 (đầu `CLAUDE.md`, khối «Trạng thái repo»): diff đụng nó là ❓ |
| **cộng thêm:** mọi `*.ts`/`*.tsx` | CL; KT | CL § Quy ước bắt buộc giữ ("MÁY nói tiếng Anh") · KT § 11 11.4 |
| **cộng thêm:** mọi file có chuỗi người dùng đọc | CL; KT | CL § Đa ngôn ngữ › Chuỗi nào ở đâu · KT § 7 |
| **cộng thêm:** mọi file chạm lời mời, auto-join hay phép so email | CL | CL § Cạm bẫy › Cạm bẫy MỚI — lời mời gặp |
| **cộng thêm:** mọi commit vào `main` | `scripts/check-version.ts`; CL | comment đầu file · CL § Kiểm chứng thay đổi › MỖI LẦN ĐẨY LÊN `main` |

Không có "file khung": không repo nào sinh từ Account. Tài liệu lệch nhau thì `CLAUDE.md` thắng (KT tự nói §3
và §12 của nó là luật, nhưng bảng trạng thái ở KT § 13 đã cũ — ghi dưới **Đã kiểm**, không là phát hiện).

## Phạm vi diff

- `-U0` loại `pnpm-lock.yaml` như module. Không loại gì thêm: `verify/output/`, `scripts/seed-output*.json`,
  `.env*` đã gitignore — chúng xuất hiện trong danh sách file là 🔴 (token, cookie phiên, mật khẩu seed THẬT).
- Diff dài thì chia: `… -- lib/ stores/ hooks/ packages/`, `… -- app/ components/ proxy.ts next.config.ts`,
  `… -- prisma/ verify/ scripts/ tests/`, `… -- '*.md' docs/ .claude/ messages/`.
- `packages/account-sdk/dist/**` không commit; thấy nó trong diff là ❓.

## Bản gốc hay bản chép

`"name": "comitor-account"`. Repo này là GỐC của `@comitor/account-sdk` (`packages/account-sdk/`) — module chỉ
cài bản đã publish (CL § Kiến trúc, D4), nên SDK ở đây được sửa thẳng và F4 không áp cho nó. Cả bốn skill
(`comitor-ui`, `comitor-page`, `comitor-test`, `comitor-review`) là BẢN CHÉP từ `comitor-starter` → F4 áp cho cả
bốn. `comitor-page` có mặt nhưng từ chối sinh mã ở hồ sơ này (`scaffold.mjs` thoát 2 kèm chỗ phải đọc thay).

## Đường nhanh

Thay danh sách đường dẫn nhạy cảm (ba điều kiện còn lại như SKILL.md): `app/api/**`, `app/.well-known/**`,
`app/(auth)/**`, `lib/**`, `stores/**`, `prisma/**`, `scripts/**`, `verify/**`, `packages/account-sdk/src/**`,
`messages/**` (khoá thiếu là trắng trang — Quy ước › i18n), `i18n/**`, `.github/**`, `.claude/settings.json`,
`.claude/skills/comitor-review/scripts/**`, `proxy.ts`, `instrumentation.ts`, `next.config.ts`, `biome.json`,
`package.json`, `pnpm-lock.yaml`, `pnpm-workspace.yaml`.

## Lockfile

Như module, TRỪ dòng `better-auth`, lật ngược:

- `better-auth`/`@better-auth/*` có trong repo là ĐÚNG. Đổi bản mà commit không phải đợt nâng riêng kèm kết quả
  `pnpm verify` → 🟠; dải `^`/`~` thay số chính xác → 🟠 (CL § Quy ước bắt buộc giữ, § Ghim công cụ › Nâng phụ
  thuộc).
- `jose` đổi → hỏi ❓ đã chạy kc1, kc2, kc10 và `pnpm why jose` ra MỘT bản chưa (nó là thư viện better-auth ký
  token bằng).
- `@types/node` lệch major của `.nvmrc` → 🟡. `@aws-sdk/*` không nâng cùng nhau → 🟡. `next-intl` đổi → ❓ đã
  đi vòng `vi` lẫn `en` chưa.
- `@comitor/ui` đổi → `quality.md` § A, cộng CL § `@comitor/ui` 3.x (mục đó phải được cập nhật — F6).

## Hàng

Bốn nhóm, **22 hàng**: hai mươi mốt hàng module, cộng hàng **Better Auth** ở nhóm Dữ liệu & bảo mật. Mã luật
(T1, G1…) giữ như reference nhóm; cột cuối nói chỗ nào khác.

| Nhóm | Hàng | Áp/Đổi/Bỏ/Thêm | Luật ở repo này (nguồn) |
|---|---|---|---|
| Kiến trúc | **Tầng** | Đổi | T1–T5, T7–T8 áp (KT § 3, § 4; lõi còn cấm `better-auth/*`, `zustand` — Biome canh, KT § 11). T8: `grep -rn 'await fetch(' app/ components/ --include='*.tsx'` phải rỗng; Uppy tải tệp đi thẳng là ngoại lệ đã ghi. **T6 sai ở đây**: KT § 3 hàng B cho route import `lib/` máy chủ và repo cố ý để route ghi Prisma trực tiếp trong giao dịch — Prisma trong `route.ts` KHÔNG là phát hiện; phát hiện là câu `if` nghiệp vụ viết tại route (T3/M1), và phép ĐỌC mà `page.tsx` cũng cần phải tách ra `lib/<x>.ts` (CL § Kiến trúc giao diện › Server Component đọc). T7: không có thư mục lib/catalog, bảng khai là `lib/navigation.ts`, `lib/ui-status.ts` |
| Kiến trúc | **Một luật** | Áp | M1–M2: route gọi CÙNG hàm lõi với giao diện (`blockChangeRole`, `checkSeatGrant`, `checkTeamName`…), `verify/kc16-luat-chung.ts` khoá (CL § Kiến trúc giao diện). M3: router giả gọi cùng hàm lõi, `verify/kc17-fake-contract.ts` so hợp đồng. M4: `href:` chỉ ở `lib/navigation.ts`; `?w={slug}` chỉ dựng ở `appLaunchUrl()`/`appUrlFor()` (CL § Quy ước bắt buộc giữ); regex email chỉ ở `isEmailShaped` |
| Kiến trúc | **Ranh giới** | Áp | R1 ngoại lệ: `lib/auth-client.ts` là `"use client"`, KHÔNG `server-only` (KT § 6). R4: `locale` date-fns, `messages` có khoá hàm không qua ranh giới (CL § Cạm bẫy › Cạm bẫy MỚI — đo được khi dựng nhóm C). R7 → `lib/navigation.ts` |
| Kiến trúc | **Chỗ đặt** | Đổi | P1, P6 áp. **P2 sai ở đây**: docs/them-mot-thuc-the.md không có → bỏ. **P4**: README không có bản đồ route (có § Bản đồ mã nguồn) → chỉ hỏi route mới có nằm trong RD § Bản đồ mã nguồn không, 🟡. P3: khu quản trị workspace chặn ở `app/(shell)/w/[slug]/(admin)/layout.tsx`, không bằng `if` lặp; layout khu workspace KHÔNG ghép `nav` (CL § Kiến trúc giao diện › Chặn vai trò bằng route group). **P5 sai ở đây** (không có hàng đợi `jobs`): việc nền sau phản hồi đi `runAfterResponse`, không `void promise` 🟠 (HG § 2); cron là `app/api/cron/**` tự xác thực |
| Kiến trúc | **Account** → *ba câu* | Đổi | **A1, A2, A5 sai ở đây**: `user`/`organization`/`member`/`team` là bảng CỦA repo này, màn tài khoản sống ở đây, và `better-auth` là thư viện lõi. Luật thay: mỗi bảng/cột mới nói nó phục vụ câu nào trong BA câu, không trả lời được → 🟠; không RBAC của app, vai trò thứ năm, cây nhóm lồng, mã nhân viên/phòng ban, feature flag trong entitlement (CL § Ranh giới Account / App, § Quy ước bắt buộc giữ ("Bốn vai trò thô", "`team` là MỘT CẤP", "Entitlement là THÔ", "Seat theo từng app")). Cột hồ sơ mới: nullable không `@default`, KHÔNG vào `additionalFields` (🔴 — mở `update-user`). `better-auth/*` được import ở `lib/*.ts` máy chủ, `app/api/**`, `app/.well-known/**`; giao diện chỉ qua `lib/auth-client.ts`; ở `lib/core`, `lib/contracts`, `stores`, `hooks`, `lib/api-client`, `components`, `.tsx` → 🔴; kiểu/hàm `better-auth` lộ qua API công khai của SDK → 🔴 (CL § Kiến trúc). A6 → hàng **Đường ghi** |
| Dữ liệu & bảo mật | **Workspace** | Đổi | **W1 sai khi áp nguyên văn**: cột là `organizationId`, không có `tenant:check`, và IdP giữ bảng chéo workspace hợp lệ (`user`, `session`, `account`, `verification`, `jwks`, `oauth*`, `app`, `rateLimit`, `apiRateLimit`, `webhookEndpoint` có `organizationId = NULL`). Luật thay: truy vấn chạm bảng thuộc workspace (`member`, `invitation`, `team`, `teamMember`, `workspaceApp`, `workspaceAppSeat`, `auditLog`, endpoint/lịch sử webhook của workspace, `oauthClient` có `organizationId`) lọc theo `organizationId` lấy từ `requireMembership`/`requireWorkspaceAdmin` (W2: không từ thân); bản ghi con tra bằng `{ id, organizationId }`. W3: workspace khác → 404 `NOT_A_MEMBER` (`lib/workspaces.ts`); endpoint hệ thống ⇄ workspace 404 hai chiều; NGOẠI LỆ có lý do: `/api/admin/**` trả 403 (`requirePlatformAdminActor`). W4: bảng thuộc workspace có `organizationId` + chỉ mục + `onDelete: Cascade`. W5: user id từ thân đi vào đường ghi được kiểm là `member` CÙNG `organizationId`. Thêm: route M2M chạm một workspace gọi `assertMachineWorkspace` 🔴 (CL § Cạm bẫy › Cạm bẫy MỚI — đo được khi dựng nhóm C) |
| Dữ liệu & bảo mật | **Đường ghi** | Đổi | **G1–G3 sai ở đây**: không có `requirePermission`/`@api-guard`; `lib/permissions.ts` là access control của Better Auth. Chuỗi thay: `withApiErrors` → `requireSessionActor` cho MỌI GHI và mọi ĐỌC chứa dữ liệu cá nhân người khác (`requireUserActor` ở đó = 🔴, CL § Cạm bẫy › Ranh giới TOKEN) / `requireMachineActor(scope)` / `requirePlatformAdminActor` → `requireMembership` / `requireWorkspaceAdmin` → `canGovernWorkspace` cho việc CHỈ chủ sở hữu (vành đai tin cậy, chuyển sở hữu, xoá) → kiểm thân → ghi. "Sai quyền" = sai bậc vai trò, sai loại actor, thiếu scope. G2 thay: route dùng `require*Actor(request)`, không dùng helper của trang (`requireWorkspaceContext` — `redirect()`/`notFound()`; `assertPlatformAdmin` — bỏ qua `assertTrustedOrigin` và hạn mức). Route không có `require*Actor` (health, cron, csp-report, GET lời mời) ghi lý do ở đầu file. G4: giao diện gọi CÙNG `canAdministerWorkspace`/`canGovernWorkspace`. G6 áp, ngoại lệ duy nhất `lib/i18n/actions.ts` (KT § 4 Rìa B). Thêm: route ghi mới mà endpoint trần của plugin ghi cùng bảng chưa vào `disabledPaths` 🔴 (CL § Cạm bẫy › Hai đường ghi); chốt một endpoint mà có đường khác tới cùng trạng thái 🔴 (CL § Cạm bẫy › Vòng qua một chốt); không nới `assertTrustedOrigin` (KT § 15) |
| Dữ liệu & bảo mật | **Toàn vẹn** | Đổi | **I1 trỏ khuôn không có** (`lib/core/version-token.ts`, `STALE_WRITE`): giữ câu hỏi — đường ghi ghi đè CẢ tập mà hai quản trị viên cùng sửa được, không có phép so phiên bản → ❓. I2–I5, I8 áp (`lockAndCountOwners`/`lockWorkspaceApp` + đọc lại sau khoá, `@@unique` ở database — CL § Cạm bẫy › Vài điều nhỏ hơn). I3: audit là best-effort / `auditAsync`, webhook gửi sau phản hồi; hook chạy SAU commit không ném. I6 áp nguyên (Account không có `docs/migration.md`; đổi `String`→`Json` mà Prisma sinh `DROP`+`ADD` 🔴 — CL § Cạm bẫy › danh mục ứng dụng đa ngôn ngữ). **I7 trỏ hàm không có** (`todayIso`, `iso-date`): ngày chỉ-có-ngày dựng `new Date(y, m-1, d)` hoặc `zonedDayBounds` (`lib/core/date-window.ts`). Thêm: `mode: "insensitive"` ở phép tra RA QUYẾT ĐỊNH 🔴 — so `.toLowerCase()` bằng (CL § Cạm bẫy › Cạm bẫy MỚI — lời mời gặp); hàm `list*` không dọn dữ liệu |
| Dữ liệu & bảo mật | **Tiêm & bí mật** | Đổi | S1, S3–S8, S10 áp. **S2 trỏ `appFrameAccentFor`, không có**: `iconColor` là tên token trong tập đóng `lib/core/app-appearance.ts`. **S9 trỏ bộ CSV của `comitor-page`, không có**: xuất mới dùng lại bộ chặn `= + - @` + BOM của `app/api/workspaces/[idOrSlug]/audit/export/route.ts`. S3: đích sau đăng nhập chỉ `?next=` qua `lib/core/return-path.ts`. S4: một bộ kiểm SSRF duy nhất `lib/webhooks/endpoints.ts` — bộ thứ hai 🟠, lọc theo tên không theo địa chỉ / quên `localhost.` 🔴. S5: thêm `scripts/seed-output*.json`, `verify/output/` vào danh sách "không bao giờ trong diff"; `client_secret` băm SHA-256, tiền tố `comitor_cs_` NGOÀI phần băm (CL § Lệnh ("`client_secret` trong DB là")). S10: CL § CSP (không `'strict-dynamic'`, `'unsafe-eval'` chỉ khi `NODE_ENV === "development"`, tên miền Turnstile chỉ khi có khoá). Thêm: biểu mẫu xác thực có `method="post"` 🔴 (mật khẩu lên URL — CL § Cạm bẫy › Cạm bẫy MỚI — soát trợ năng); logo/URL ảnh từ người dùng qua `parseLogo` |
| Dữ liệu & bảo mật | **Hướng hỏng** | Đổi | **H1 trỏ `memberDirectory` — module không giữ danh bạ, Account thì giữ**: bỏ. **H5 sai ở đây**: Account TỰ sinh 429 (`lib/api/rate-limit.ts`, gắn vào `require*Actor`, khoá theo ACTOR không theo IP, `cost` theo tác động cho endpoint lô, phép đếm NGOÀI `try` của `requireDirectoryActor`) — CL § Giới hạn tần suất cho API tự viết; 429 nhận về thì không đổi thành 500. Hướng đã chọn, đổi chiều là 🟠/🔴: hạn mức FAIL-OPEN; audit best-effort, không bao giờ làm hỏng đăng nhập; thư nuốt lỗi GỬI, nổ lỗi CẤU HÌNH (CL § Email › Lỗi cấu hình phải NỔ); CAPTCHA và HIBP KHÔNG được phủ `/sign-in/email` 🔴 (CL § CAPTCHA, § Chặn mật khẩu đã rò rỉ); `/forgot-password` nuốt mọi lỗi trừ 429. H2–H4, H6–H8 áp; H6 thêm `[auth] KHỞI TẠO HỎNG`, `[rate-limit] KHÔNG ĐẾM ĐƯỢC`, `[members] KHÔNG DỌN ĐƯỢC` |
| Dữ liệu & bảo mật | **Better Auth** | Thêm | Phạm vi: dòng đổi ở hàng đầu bảng Tài liệu quy định, và mọi lời gọi `auth.api.*`. Kiểm, mức 🔴: hook `before` trả giá trị truthy / hook `after` trả giá trị hay ném không bọc; chốt bảo mật đặt ở `after` thay `before` (TOTP replay, 2FA enroll, `beforeAcceptInvitation`); `databaseHooks.session.delete.before`; `advanced.database.generateId`; khai `roles` của organization thiếu ba vai trò gốc; `clientPrivileges`/`resourcePrivileges` để mặc định; `auth.api.*` ở chỗ mới mà tưởng được router middleware che (origin, rate limit, `disabledPaths` không áp). Mức 🟠: `resourceSeedMode` khác `"merge"`; `additionalFields` lệch ba nơi (`schema.prisma`, `user.additionalFields`, `ACCOUNT_USER_FIELDS`); giữ tham chiếu con của `auth` hay tách object cấu hình (mất tự hồi phục); tự ghép query rồi gọi `/oauth2/authorize`; `organizationHooks` ghi `user.id` làm actor; workspace vào claim token. Nguồn: CL § Cạm bẫy và các mục con · KT § 8 8.7. **Xong** khi mỗi dòng đổi ở các file trên có câu trả lời, và thân commit/PR nêu kết quả `pnpm verify` (không nêu → ❓) |
| Quy ước | **i18n** | Đổi | **Câu mở của `conventions.md` § A ("`t()` KHÔNG ném") sai ở đây**: CL § Đa ngôn ngữ › Bốn cái bẫy đã gặp thật ghi `t()` và `t.has()` NÉM khi thiếu khoá — trắng cả cây React. N3 (khoá động không qua `t.has()`) lên 🔴; khoá scope đổi qua `toScopeMessageKey()`/`scopeMessageKeys()`, tra khoá LÁ (`t.has` trả `true` cho object). **N1 khác**: `message` tiếng Việt của lỗi API trong route là bản dự phòng, không phải phát hiện; nội dung email ở `lib/mail.ts` (`Record<Locale,…>`); `LOCALE_LABELS` cố ý không dịch (CL § Đa ngôn ngữ › Chuỗi nào ở đâu, § Đa ngôn ngữ › Bốn quyết định). Thêm: mã lỗi tới qua `authClient` phải có ở CẢ `errors.auth` lẫn `errors.code`; `admin.clients.*` ≠ `ws.clients.*` có chủ đích. N2, N4–N8 áp |
| Quy ước | **Màu & UI** | Đổi | **U1 sai ở chỗ "`color:check` bắt hex"**: repo không có cổng đó — review grep cả hex (`grep -rnE "#[0-9A-Fa-f]{3,8}" app lib components hooks --exclude=icon.svg`). `app/globals.css` đúng hai `@import`. U2–U7 áp, thêm các bẫy gói đã đo ở CL § `@comitor/ui` 3.x, § `FormField` trong hộp thoại, § Hộp thoại dài, § Tải tệp (logo `editable={canEdit}`, không `disabled`), § Cạm bẫy › Cạm bẫy MỚI — soát trợ năng (`FormControl` bọc đúng control); thẻ lựa chọn dùng `components/choice-card.tsx`; danh sách "cố ý KHÔNG dùng" ở CL § `@comitor/ui` 3.x không là phát hiện "tự dựng" |
| Quy ước | **Ngôn ngữ & tên** | Áp | L1–L3, L5 áp (CL § Quy ước bắt buộc giữ ("MÁY nói tiếng Anh") — URL `/sign-in`, `/consent`, `/invitations/{id}`). **L4 áp như module** (chỉ chặn tên dự án, đối tác khác của đội): tài liệu của Account tự gọi tên sản phẩm khác để so sánh (CL § Quy ước bắt buộc giữ ("Seat theo từng app")) — đó không phải tên đối tác, nên không là phát hiện; dịch vụ thật của repo (Cloudflare Turnstile, Have I Been Pwned, AWS) là phụ thuộc có thật |
| Quy ước | **Comment** | Áp | như module; khuôn đính chính "⚠ Bản trước … SAI" dày đặc ở CL — giữ dấu vết (C5) |
| Quy ước | **Kiểu** | Áp | như module; K4 phủ cả khối `overrides` của `biome.json` (KT § 11) — nới nó cho vừa một file là 🟠 |
| Chất lượng | **Đúng** | Đổi | Bảng anh em của `quality.md` § A trỏ lib/catalog, `FAKE_SUPPORTED` của module — thay: route ↔ phương thức `lib/api-client/` ↔ `lib/contracts/` ↔ `lib/api-client/fake/router.ts` (kc17); luật lõi ↔ route + giao diện (kc16); hai hộp thoại tạo OAuth client (workspace + nền tảng) là anh em; `lib/navigation.ts` + `workspaceAdminNav` + `nav.*`; `MeView` và hợp đồng `/api/workspaces/me` ↔ app ở repo KHÁC (KT § 13); route ↔ RD § Hợp đồng API; khoá seed `tasks-web`/`mobile`/`directory` ↔ `verify/kc1-oidc-e2e.ts`, `kc2`, `kc10`, `kc11` |
| Chất lượng | **Test** | Đổi | E1–E4, E7–E8 áp; E2 thêm: phép thử nguyên tử chạy trên Postgres thật, không `memoryAdapter`. **E5 trỏ `router.test.ts`, không có**: route đổi mà router giả không đổi → kc17 đỏ, hỏi ❓ đã chạy chưa. **Unit test cho route handler KHÔNG đòi** — cố ý, `verify/` là tầng mạnh hơn (CL § Test đơn vị). E6: màn có thao tác GHI cần ít nhất một test `@real` (KT § 15). Thêm: đổi tầng OIDC hay API riêng → kết quả `pnpm verify` (CL § Kiểm chứng thay đổi); script `verify/` mới có đối chứng âm tính (KT § 10 Đối chứng âm tính) |
| Chất lượng | **Hợp đồng** | Đổi | H1, H2, H4, H5, H7 áp (H5: `check-slug`, `POST invitations`, `POST teams/{id}/members`). **H6 khác**: hợp đồng liên module ở đây là SDK (API công khai + `version` của `packages/account-sdk` khi `src/` đổi, publish thật), `MeView`, `/api/workspaces/me`, `/api/entitlements/{id}`, danh bạ, sự kiện + chữ ký webhook, scope/claim, discovery, `?w={slug}`, liên kết sâu RD § Hợp đồng API › Liên kết sâu mà MODULE trỏ vào — đổi bất kỳ cái nào không tương thích ngược 🔴. H3: `/sign-in`, `/consent` ghim ở `lib/auth.ts`, `redirect_uri` đã đăng ký, liên kết trong thư — dời route là 404 cho mọi module (`proxy.ts` không có rewrite). `x-request-id` chưa cài ở đây; thêm thì đúng tên đó |
| Chất lượng | **Trạng thái** | Đổi | D1, D4, D5 áp. **D2 sai ở đây** (Account giữ chính danh bạ; không có ca "id tra không ra tên") → bỏ. D3 áp không kèm `<NotYetActive />`: tính năng thiếu cấu hình thì TẮT và nói rõ (khuôn `storageEnabled`, CL § Lệnh ("Kho đối tượng")) |
| Chất lượng | **Tối giản** | Áp | như module |
| Chất lượng | **Tài liệu** | Đổi | F1 → mục **Số bản**. **F2, F5 sai ở đây** (không file khung, không phải starter) → bỏ. F3 áp cho `CLAUDE.md`, `README.md`, `docs/**`, SDK README; số đếm trong tài liệu ("mười ba script", "41 endpoint") đổi theo mã. F4 áp cho bốn skill chép. F6 → CL § `@comitor/ui` 3.x. F7: khuôn đang dùng `type(scope): mô tả — x.y.z` (`git log`), ⚪ |

Mẫu số bảng Kiểm: Kiến trúc /5 · Dữ liệu & bảo mật /6 (thêm **Better Auth**) · Quy ước /5 · Chất lượng /6.

## Công cụ máy

Như module: `audit.mjs` của `comitor-ui` khi có `.tsx`/`.css`; `check-refs.mjs` của `comitor-test` cho
`.claude/skills/comitor-test` và `.claude/skills/comitor-review`; `pnpm exec biome check <file>` chỉ khi `--fix`.
Không chạy `pnpm verify`/`e2e` (cần máy chủ + Postgres thật) — hỏi kết quả của chúng ở hàng **Better Auth** và **Test**.
`pnpm check` không tồn tại; cổng của tác giả là chuỗi ở CL § Kiểm chứng thay đổi, và `check.yml` chỉ chạy tay.

## Không bao giờ sửa

Như module (file bẩn; `messages/*.json`; `prisma/migrations/**`; bản chép skill — ở đây cả bốn
`comitor-*`), bỏ hai khoản không tồn tại (khuôn `.tpl`, file khung), cộng:

- cấu hình và hook của Better Auth: `lib/auth.ts`, `lib/permissions.ts`, `lib/totp-replay.ts`,
  `lib/audit-plugin.ts`, `lib/workspace-hooks.ts`, `lib/two-factor-enroll-guard.ts` — "mỗi dòng ở đó là một cạm
  bẫy đã đo được" (KT § 13);
- `verify/**` (cổng hồi quy tầng OIDC), `poc/**` (bằng chứng đông lạnh);
- `packages/account-sdk/**` — đổi là đổi hợp đồng đã publish;
- `scripts/seed.ts` (khoá seed), `biome.json`, `.github/workflows/**`, `scripts/seed-output*.json`.

## Mức

Đổi và thêm vào danh sách Mức của SKILL.md § 6:

- **🔴 thay** "route ghi thiếu chốt quyền, chốt SAI quyền, hoặc `@api-guard` ngoài hai họ lý do" bằng: route
  ghi (hay đọc dữ liệu cá nhân người khác) không qua `requireSessionActor`, sai bậc vai trò (`requireWorkspaceAdmin`
  cho việc chỉ chủ sở hữu), route M2M thiếu scope hay `assertMachineWorkspace`.
- **🔴 thay** "import `better-auth/*`" bằng: import ở tầng/phía bị cấm (hàng **Account**), hay rò qua SDK.
- **🔴 thêm**: các khoản 🔴 của hàng **Better Auth**; endpoint trần chưa vào `disabledPaths`; chốt vòng qua được
  bằng đường khác; workspace vào claim token; `mode: "insensitive"` ở phép tra ra quyết định; biểu mẫu xác thực
  thiếu `method="post"`; `/sign-in/email` vào `endpoints` của CAPTCHA hay `paths` của HIBP; đổi không tương
  thích ngược một hợp đồng của hàng **Hợp đồng** (H6).
- **🟠 bỏ** "đường ghi tin danh bạ rỗng", "file khung đổi mà CHANGELOG không có mục…"; **🟠 thay** "vượt ranh
  giới Account" bằng: bảng/cột mới không nói phục vụ câu nào trong ba câu, RBAC/vai trò/cây tổ chức của app.
- **🟠 thêm**: `void promise` cho việc nền thay `runAfterResponse`; bộ kiểm SSRF thứ hai; đẩy lên `main` không tăng
  `version` (mục **Số bản**).
- **❓ thêm**: đổi tầng OIDC/API riêng mà không có bằng chứng `pnpm verify`; nâng `better-auth` hay `jose`.

## Số bản

Thay F1 của `quality.md`:

- **Không có `CHANGELOG.md`, cố ý** (`scripts/check-version.ts`, comment đầu file) — đừng đòi.
- `version` của `package.json` ở HEAD phải LỚN hơn ở gốc nhánh (`git show <gốc nhánh>:package.json`) — mỗi lần
  vào `main` là một lần deploy, và số đó hiện ở chân thanh bên lẫn `/api/health`. `minor` khi có tính năng hay
  đổi hành vi, `patch` cho sửa lỗi, tài liệu, CI (CL § Kiểm chứng thay đổi › MỖI LẦN ĐẨY LÊN `main`).
- Thiếu tăng: 🟠 khi diff có file NGOÀI `paths-ignore` của `deploy.yml` (`docs/**`, `.claude/**`, `**/*.md`);
  🟡 khi cả diff nằm trong đó (deploy không chạy, nhưng CL vẫn đòi `patch`). Tăng nhiều bậc trong một PR không
  là phát hiện.
- `check.yml` chỉ chạy tay (`workflow_dispatch`), nên `version:check` KHÔNG tự chạy ở PR — review là chốt duy
  nhất. Workflow hạ `fetch-depth` khỏi `2` → 🟠 (cổng in ✓ mà không kiểm).
- `packages/account-sdk/src/**` đổi hành vi hay API công khai mà `packages/account-sdk/package.json` không tăng
  `version` → 🟠 (app cài theo bản đã phát hành — CL § Kiến trúc).

## Bẫy

Thay `references/pitfalls.md`. Mỗi dòng là lỗi ĐÃ XẢY RA ở Account, ghi trong tài liệu của chính nó. Như ở
module: gần như không dòng nào làm cổng máy đỏ.

### Một luật và tầng

| Lỗi | Thấy trong diff thế nào | Nguồn |
|---|---|---|
| Lõi chỉ được giao diện gọi, route giữ bản viết tay: quản trị viên nhắm chủ sở hữu duy nhất — giao diện `last-owner`, máy chủ 403; tên nhóm máy chủ so `ILIKE` | Điều kiện vai trò/chỗ ngồi/tên viết trong `route.ts` thay vì gọi hàm lõi | CL § Kiến trúc giao diện |
| Bốn màn gọi `fetch()` thẳng — mọi lỗi mạng hiện "lỗi không xác định"; `checkSlug` có sẵn ở cổng mà hộp thoại không dùng | `await fetch(` ngoài `lib/api-client/`; phương thức cổng trùng cái đã có | CL § Kiến trúc giao diện ("Component TUYỆT ĐỐI không `fetch()`") |
| Ba phép đọc trả `user.image`/`organization.logo` NGUYÊN VĂN — đó là khoá object, ảnh 404 ở mọi màn | Cột khoá trả ra ngoài không ký URL | CL § Kiến trúc giao diện › Server Component đọc |
| Ghép `nav` lần hai ở layout khu workspace — hai nguồn sự thật cho thanh bên | `layout.tsx` dưới `w/[slug]` đụng `nav` | CL § Kiến trúc giao diện › Chặn vai trò bằng route group |
| Store ở phía máy chủ dùng chung giữa mọi người dùng | Rìa A import `stores/` | KT § 15 |

### Token và đường ghi

| Lỗi | Thấy trong diff thế nào | Nguồn |
|---|---|---|
| Token `openid profile email` của app bên thứ ba đọc nhật ký kèm IP/email và CHUYỂN quyền sở hữu workspace | Route ghi hay đọc PII dùng `requireUserActor` | CL § Cạm bẫy › Ranh giới TOKEN |
| `/organization/remove-member` không dọn chỗ ngồi; `/organization/update` bỏ `parseLogo` → `javascript:` vào `src` ở mọi app | Route ghi mới, endpoint trần cùng bảng chưa trong `disabledPaths` | CL § Cạm bẫy › Hai đường ghi |
| `PATCH` chặn ghi `status`, nhưng `DELETE` rồi `POST` lại là nợ biến mất | Chốt trên một endpoint | CL § Cạm bẫy › Vòng qua một chốt |
| Client M2M do workspace tự đăng ký đọc danh bạ MỌI workspace | Route M2M thiếu `assertMachineWorkspace` | CL § Cạm bẫy › Cạm bẫy MỚI — đo được khi dựng nhóm C |
| Quyền `invitation:create` cho `member` mà không tắt đường trần — ai cũng mời được bất kỳ ai | `lib/permissions.ts` đổi mà `disabledPaths` không đổi, hay ngược lại | CL § Cạm bẫy › Cạm bẫy MỚI — đo được khi dựng nhóm C |
| `clientPrivileges`/`resourcePrivileges` mặc định MỞ — mọi phiên tạo/xoá được OAuth client của cả hệ | Cấu hình oauth-provider mới không khai | CL § Cạm bẫy › Cạm bẫy MỚI — đo được khi dựng app thật |
| Mở app ở `127.0.0.1` → mọi ghi 403, và cách sửa hấp dẫn nhất là nới `requireSessionActor` | Diff nới `assertTrustedOrigin` hay hạ actor | KT § 15 |
| Endpoint mời nhận lô 50 địa chỉ: 20 request/giờ = 1000 thư | Hạn mức cho endpoint lô không có `cost` | CL § Giới hạn tần suất cho API tự viết |
| `/two-factor/enable` ghi đè bí mật TOTP khi 2FA đang bật — khoá ngoài người dùng | Đường đổi thiết bị gọi `/enable`; chốt đọc `session.user` thay database | CL § Cạm bẫy › `/two-factor/enable` GHI ĐÈ |

### Better Auth

| Lỗi | Thấy trong diff thế nào | Nguồn |
|---|---|---|
| `hooks.before` trả object truthy được dùng LÀM phản hồi — `/sign-up/email` 200 mà không user nào; `hooks.after` trả giá trị thay body | `return <giá trị>` trong hook | CL § Cạm bẫy › Cạm bẫy MỚI — đo được khi dựng app thật |
| Chặn replay TOTP ở `after` là GIẢ: 401 kèm `Set-Cookie` phiên hợp lệ | Chốt bảo mật trong `after` | CL § Cạm bẫy ("TOTP KHÔNG bị") |
| `databaseHooks.session.delete.before` trả `false`: back-channel logout im, cookie cũ vẫn xác thực | Khai `session.delete.before` | CL § Cạm bẫy › Cạm bẫy MỚI — đo được khi dựng app thật |
| `roles` của organization THAY THẾ — `owner`/`admin`/`member` mất sạch quyền | Khai `roles` thiếu ba vai trò gốc | CL § Cạm bẫy ("`roles` của `organization` là THAY THẾ") |
| Init reject VĨNH VIỄN sau một nhịp database — `/` 500 tới khi khởi động lại | Tham chiếu con của `auth` ở scope module; tách object cấu hình | CL § Cạm bẫy › MỘT NHỊP DATABASE |
| `additionalFields` lệch — `zod` loại trường im lặng, thư sai ngôn ngữ; `oauthProviderClient()` thay thân phản hồi giữa luồng OIDC | Cột `user` mới; tự gọi `/oauth2/authorize` sau đăng nhập | CL § Cạm bẫy › Cạm bẫy MỚI — đo được khi ghép giao diện xác thực |
| Chốt lời mời ở `after` để lại trạng thái hỏng — phải `beforeAcceptInvitation` | Hook `after*` dùng làm chốt | CL § Cạm bẫy › Cạm bẫy MỚI — lời mời gặp |

### Dữ liệu và thời gian

| Lỗi | Thấy trong diff thế nào | Nguồn |
|---|---|---|
| `mode: "insensitive"` (ILIKE, `_` là ký tự đại diện): quản trị viên thêm SAI NGƯỜI vào workspace | `insensitive` ở phép tra ra quyết định | CL § Cạm bẫy › Cạm bẫy MỚI — lời mời gặp |
| Auto-join ăn mất lời mời; `return` thay `continue` để workspace A chặn lối vào B | Vòng lặp auto-join, lời mời | CL § Cạm bẫy › Cạm bẫy MỚI — lời mời gặp |
| `member` trùng thật trước `@@unique`; đếm-rồi-ghi đua dưới `READ COMMITTED` | `findFirst` rồi `create`; `count` không `FOR UPDATE` | CL § Cạm bẫy › Vài điều nhỏ hơn |
| `NULL <= now` là UNKNOWN — webhook mới nằm `pending` mãi | Cột thời gian nullable trong `lte` | CL § Cạm bẫy › Vài điều nhỏ hơn ("`NULL <= now`") |
| `localhost.` có dấu chấm cuối vượt bộ lọc SSRF — máy chủ POST vào chính nó | So `hostname` không bỏ dấu chấm cuối | CL § Cạm bẫy › Vài điều nhỏ hơn ("`localhost.`") |
| `2026-08-20` là 00:00 UTC — bộ lọc nhật ký mất bảy tiếng đầu ngày | `new Date(` trên chuỗi chỉ-có-ngày | CL § Cạm bẫy › Vài điều nhỏ hơn |
| `orderBy` theo cột `Json` chạy mà sai thứ tự; đổi `String`→`Json` Prisma sinh `DROP COLUMN` | `orderBy: { name }`; migration tự sinh đổi kiểu | CL § Cạm bẫy › danh mục ứng dụng đa ngôn ngữ |
| `client_name` làm khoá seed — đổi tên là seed tạo client THỨ HAI, app khách `invalid_client` | Seed tra theo `name`; đổi khoá seed | CL § Cạm bẫy › Cạm bẫy MỚI — `client_name` |
| Biểu mẫu đăng ký bấm trước hydrate gửi GET — mật khẩu lên thanh địa chỉ | `<form` xác thực thiếu `method="post"` | CL § Cạm bẫy › Cạm bẫy MỚI — soát trợ năng |

### Hướng hỏng

| Lỗi | Thấy trong diff thế nào | Nguồn |
|---|---|---|
| CAPTCHA mặc định phủ `/sign-in/email` và hỏng theo hướng ĐÓNG — Cloudflare sập là không ai đăng nhập được sản phẩm nào | `endpoints` có `/sign-in/email` | CL § CAPTCHA |
| HIBP hỏng theo hướng ĐÓNG | `/sign-in/email` vào `paths` | CL § Chặn mật khẩu đã rò rỉ |
| `resolveTransport()` trong `try` — transport gõ sai bị nuốt, không lá thư nào đi | `try` bọc bước chọn transport | CL § Email › Lỗi cấu hình phải NỔ |
| `void promise` trên Vercel chết cùng instance — webhook "timeout", chỗ ngồi hứa lúc mời mất | Việc sau phản hồi không qua `runAfterResponse` | HG § 2 |
| 429 bị tính là "mã sai" — ba lần là khoá cứng 2FA | Nhánh lỗi giữ `error.code ?? …` | CL § Cạm bẫy › Cạm bẫy MỚI — soát trợ năng |
| Cấp chỗ ngồi trong `afterAcceptInvitation` ném sau khi `member` đã commit — trang lỗi cho thao tác đã thành công | Bước phụ sau commit không bọc | CL § Cạm bẫy › Cạm bẫy MỚI — đo được khi dựng nhóm C |
| Bảng đếm hạn mức hỏng mà chặn hết = sự cố database thành sự cố toàn hệ | Limiter fail-closed | CL § Giới hạn tần suất cho API tự viết ("HỎNG THÌ CHO QUA") |

### Đa ngôn ngữ

| Lỗi | Thấy trong diff thế nào | Nguồn |
|---|---|---|
| Tên scope có dấu chấm làm khoá — hỏng cả app lúc nạp, kể cả `/sign-in`; `t()` thiếu khoá làm trắng cây | Khoá `a.b`; khoá động không `t.has()` | CL § Đa ngôn ngữ › Bốn cái bẫy đã gặp thật |
| `t.has()` `true` cho khoá OBJECT — thẻ hiện `consent.scopes.openid`; `format.dateTime(d, "long")` rơi về `Date.toString()` | Tra khoá không lá; đối số thứ hai là chuỗi | CL § Cạm bẫy › Cạm bẫy MỚI — soát trợ năng |
| `ALREADY_MEMBER` chỉ ở `errors.code` trong khi nơi gọi tra `errors.auth` — chốt chạy, người dùng đọc "lỗi không xác định" | Mã mới chỉ ở một nhóm | CL § Cạm bẫy › Cạm bẫy MỚI — lời mời gặp |
| `nav.adminClients` trùng `nav.wsClients` từng byte — hai dòng không phân biệt được | Hai namespace "sửa cho đồng bộ" | CL § Cạm bẫy › Cạm bẫy MỚI — `client_name` |
| Cột `locale` có `@default` — trình duyệt `en` chưa từng chọn vẫn bị gieo `vi` | Cột hồ sơ mới có `@default` | CL § Ranh giới Account / App |

### Giao diện

| Lỗi | Thấy trong diff thế nào | Nguồn |
|---|---|---|
| `FormControl` dán `id`/`aria-*` lên thẻ bọc — ô nhập thật không tên | Thẻ bố cục giữa `FormControl` và control | CL § Cạm bẫy › Cạm bẫy MỚI — soát trợ năng |
| `col-span-12` trong `DialogContent` đẻ 11 track ngầm | Trường gói cũ trong hộp thoại | CL § `FormField` trong hộp thoại |
| Hộp thoại dài tràn khung, nút Gửi không chạm tới | Thiếu `DialogBody` | CL § Hộp thoại dài |
| Icon lucide 24px trong nút 36px; `ActionBar` đóng và xoá vùng chọn trước khi hộp thoại đọc | Icon `Button` thiếu `size-4`; `onSelect` thiếu `preventDefault()` | CL § `@comitor/ui` 3.x |
| Nâng gói không khởi động lại dev — class mới không có rule, lớp phủ trong suốt | `@comitor/ui` đổi bản | CL § Tải tệp ("Nâng `@comitor/ui` xong") |
| `icons[tenTuDb]` kéo ~1500 icon vào bundle; `iconColor` tuỳ ý đi vào `style` | Tra `lucide-react` động; màu từ database | CL § Cạm bẫy › danh mục ứng dụng đa ngôn ngữ |

### API giả và kiểm chứng

| Lỗi | Thấy trong diff thế nào | Nguồn |
|---|---|---|
| Điều kiện build import từ `mode.ts` không được gấp — router giả lọt bốn file `.next/static`; thiếu `refreshKey` thì lời mời vừa gửi không hiện | `import()` mã giả không viết nguyên văn `process.env.…`; vỏ client không nạp theo khoá | CL § Kiến trúc giao diện › API giả + Playwright |
| Handler giả trả fixture cố định — qua Playwright-fake và nói dối | `return FIXTURE` | KT § 15 |
| Test replay trên `memoryAdapter` XANH GIẢ | Phép thử nguyên tử không chạy trên database thật | CL § Cạm bẫy ("TOTP KHÔNG bị") |
| Bỏ một trong hai chốt `status: "pending"` mà kc13 vẫn xanh; dữ liệu thử email chữ hoa kiểm điều không xảy ra | Đối chứng âm tính chỉ gỡ một lớp | CL § Cạm bẫy › Cạm bẫy MỚI — lời mời gặp |
| `run-all.sh` dọn một bảng đếm — `verify` tự đỏ ngẫu nhiên; test ghim `"Asia/Saigon"` đỏ khi nâng Node | Dọn thiếu `api_rate_limits`; ghim chuỗi phụ thuộc runtime | CL § Test đơn vị |

### Tài liệu và phiên bản

| Lỗi | Thấy trong diff thế nào | Nguồn |
|---|---|---|
| `version` đứng `0.2.0` qua cả nhóm A, B, C — người dùng báo lỗi kèm bản không chứa lỗi; clone nông làm cổng in ✓ | Không tăng `version`; `fetch-depth` khác `2` | CL § Kiểm chứng thay đổi › MỖI LẦN ĐẨY LÊN `main` |
| `.claude/launch.json` bị ghi lại pretty-print — `main` đỏ hai ngày | File `.json` đổi định dạng | CL § Kiểm chứng thay đổi |
| Tài liệu ghi `client_secret` "mã hoá bằng `BETTER_AUTH_SECRET`" — sai, gợi ý có đường đọc ngược | Khẳng định về thư viện không kèm phép đo | CL § Lệnh ("`client_secret` trong DB là") |
| Tài liệu CSP ghi "khoảng cách còn lại là ĐÚNG MỘT VIỆC" — làm xong việc đó không đổi gì | Câu "chỉ còn X" không kiểm | CL § CSP |
| `pnpm add @comitor/ui@<bản mới>` thoát 0 mà không nâng | Phiên bản thêm vào `minimumReleaseAgeExclude` | CL § Hộp thoại dài ("`pnpm add @comitor/ui@<bản mới>`") |
