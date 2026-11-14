# Tài liệu nào quyết định đường dẫn nào

Bước 0 của SKILL.md § 2. Với mỗi đường dẫn đổi, lấy hàng KHỚP ĐẦU TIÊN, đọc các mục được nêu, rồi báo
một vi phạm dưới hàng của nhóm tương ứng kèm `tài liệu § mục`. Bốn hàng cuối là CỘNG THÊM — áp chúng
ngoài hàng khớp đầu tiên. Bảng này chỉ trỏ; chữ của luật nằm ở tài liệu.

Viết tắt: **KT** = `docs/kien-truc-ung-dung.md` · **AG** = `AGENTS.md` · **CT** = `CONTRIBUTING.md`.

**Đọc bằng `.claude/skills/comitor-review/scripts/sections.mjs`, không Read cả file.** Dán nguyên phần chữ sau tên tài liệu:
`node .claude/skills/comitor-review/scripts/sections.mjs AGENTS.md '§ Cạm bẫy › Next.js (…)'`. Nó in đúng mục
đó kèm khoảng dòng. Chữ trong NHÁY KÉP là đầu một gạch đầu dòng cấp 1 của mục: có nháy thì chỉ những gạch
đó được in — nên mọi ý muốn đọc phải nằm trong nháy. Ngoặc không nháy là ghi chú cho người, không lọc gì;
trích dẫn không phải gạch thì viết «…». Không thấy đề mục → nó báo `✗ … đọc cả file`, và bạn Read cả file.
Sửa bảng này hay đổi đề mục của một tài liệu nó trỏ tới → chạy `sections.mjs --check-table`.

| Đường dẫn đổi (glob) | Đọc | Mục quyết định |
|---|---|---|
| `lib/core/**` | KT; skill `comitor-test` | KT § 2 (hàng 1), § 3 tầng 1, § 5, § 8 · `comitor-test/references/unit-core.md` |
| `lib/contracts/**` | KT | § 3 tầng 0; AG § Cạm bẫy › Next.js (`Date`, `Decimal` qua ranh giới) |
| `lib/catalog/**` | KT; AG | KT § 2 (hàng ★); AG § Quy ước › "`lib/catalog/navigation.ts` là nguồn sự thật DUY NHẤT" |
| `lib/api-client/**` | KT; skill `comitor-test` | KT § 3 tầng 2, § 10 · `comitor-test/references/fake-api.md` |
| `stores/**` | KT; skill `comitor-test` | KT § 3 tầng 3 (bốn điều kiện) · `comitor-test/references/stores.md` |
| `hooks/**` | KT | § 3 tầng 4 |
| `app/api/**/route.ts` | KT; AG | KT § 3 rìa B, rìa B′, § 7 · AG § Ranh giới Account / app (`requirePermission`, `@api-guard`), § Quy ước ("Đường GHI đi route handler", "Nghiệp vụ nằm ở `lib/*.ts`", "Ranh giới `$transaction`", "Đường ghi gửi CẢ giá trị phải mang THẺ PHIÊN BẢN") |
| `app/**/page.tsx`, `app/**/layout.tsx` | KT; AG | KT § 3 rìa A, § 4 · AG § Quy ước ("BẢN GHI đi vào app ở đúng HAI cửa"), § Thêm một trang mới |
| `app/**/*.tsx`, `components/**` | KT; AG; skill `comitor-ui` | KT § 3 tầng 5, § 4 · AG § Quy ước ("App KHÔNG sở hữu màu", "Mỗi màu có ba vai trò", "Không có chuỗi hiển thị nào nằm ngoài `messages/`", "Đổi chuỗi của gói bằng prop", "Chỗ đặt cụm tự viết", "Không chép mã nguồn component"), § Cạm bẫy › `@comitor/ui` · `comitor-ui/SKILL.md` bảng "Cần gì → dùng gì" |
| `lib/account/**`, `app/api/auth/**`, `proxy.ts`, `instrumentation.ts` | AG; CT | AG § Xác thực, § Cạm bẫy › Bảo mật và hạ tầng · CT § Thay đổi chạm FILE KHUNG |
| `lib/*.ts` (tầng D) | KT; AG; skill `comitor-page` | KT § 2 (hàng D) · AG § Ranh giới Account / app (bất biến `workspaceId`, đường đọc fail-open), § Quy ước ("Ranh giới `$transaction`", "Con số nào suy được thì suy"), § Cạm bẫy › Dữ liệu và thời gian · `comitor-page/references/data-layer.md` |
| `lib/api/**` | KT | § 2 (hàng C) |
| `prisma/**` | `docs/migration.md`; AG | migration.md toàn bộ · AG § Quy ước ("Mọi migration phải tương thích ngược MỘT bản") · AG § Ranh giới Account / app (không bảng định danh; khoá ngoại kép) |
| `messages/**`, `i18n/**`, `lib/i18n/**` | KT; AG | KT § 5 · AG § Cạm bẫy › Đa ngôn ngữ |
| `scripts/jobs/**` | AG; skill `comitor-page` | AG § Quy ước ("Job nền") · `comitor-page/references/jobs-and-mail.md` |
| `tests/**`, `**/*.test.ts`, `playwright.config.ts`, `vitest.config.ts` | skill `comitor-test` | `SKILL.md` (tháp, mười hai luật) · `references/playwright.md` · `references/pitfalls.md` |
| `app/dev/**`, `app/fake-screens*.ts`, `lib/api-client/fake/**` | KT; skill `comitor-test` | KT § 10 · `comitor-test/references/fake-api.md` §4–§6 |
| `.github/**`, `scripts/check-*.ts` | CT; chính file đó | CT § Thay đổi chạm FILE KHUNG · comment đầu file (lý do của từng dòng nằm ở đó) |
| `.claude/skills/comitor-page/templates/**` | như file nó SINH ra (bỏ `.tpl`, thay tên thực thể — SKILL.md § 2), cộng `comitor-page/MAINTAINING.md` | hàng của đường dẫn sinh ra + `quality.md` F5 (`verify.mjs`) |
| `.claude/skills/<tên>/**` (còn lại) | `MAINTAINING.md` của skill đó | toàn bộ; ở MODULE thêm `quality.md` § F (bản chép) |
| `.claude/settings.json` | skill này | `MAINTAINING.md` §2 (hook) |
| `docs/**`, `README.md`, `AGENTS.md`, `CLAUDE.md` | `CLAUDE.md` | § Giới hạn khi sửa (tài liệu khớp mã) |
| `package.json`, `pnpm-workspace.yaml`, `pnpm-lock.yaml` | `CLAUDE.md`; AG | CLAUDE.md § Giới hạn khi sửa (nâng `@comitor/ui`) · AG § Cạm bẫy › `@comitor/ui` (nâng gói, `minimumReleaseAge`) |
| **cộng thêm:** mọi `*.ts`/`*.tsx` | AG | § Quy ước ("Tiếng Anh cho MỌI thứ máy đọc", "Chỉ nói về Comitor", "Warning LÀ lỗi", "Spread có điều kiện", "`strict` + `noUncheckedIndexedAccess`") |
| **cộng thêm:** mọi file có chuỗi người dùng đọc | KT; AG | KT § 5 · AG § Quy ước ("Không có chuỗi hiển thị nào nằm ngoài `messages/`") |
| **cộng thêm:** mọi file ngoài phần module thêm (file KHUNG) | CT | § Thay đổi chạm FILE KHUNG (CHANGELOG có mục «Module đã sinh ra phải làm gì», không format lại) |
| **cộng thêm:** mọi commit vào `main` | `scripts/check-version.ts` | comment đầu file (tăng `version` + mục CHANGELOG) |

"File khung" là thứ mọi module chép nguyên và không sửa — danh sách và quy tắc nhận biết ở CT § Thay đổi
chạm FILE KHUNG và README § "Ranh giới: cái gì giữ, cái gì THÊM vào".

Một đường dẫn không có hàng là bình thường — ghi vậy. Tài liệu thiếu hoặc mâu thuẫn với `AGENTS.md`
**không** phải phát hiện của PR: `AGENTS.md` thắng, và **Đã kiểm** nêu tên tài liệu đã cũ. Ngoại lệ: chính
diff này sửa tài liệu cho lệch mã — đó là phát hiện của hàng **Tài liệu**.
