# Dữ liệu & bảo mật — năm hàng

**Phạm vi:** file đổi dưới `app/api/`, `lib/` (kể cả `lib/core/` — ngày giờ ở I7, CSP ở S10, CSV ở S9), `prisma/`,
`proxy.ts`, `scripts/`, và mọi `.tsx` dựng `href`/`src`/`style` từ dữ liệu hay đọc `process.env`. Không có
→ cả nhóm n/a.

Nguồn luật: `AGENTS.md` (AG) § Ranh giới Account / app, § Quy ước bắt buộc giữ, § Cạm bẫy › Dữ liệu và
thời gian, › Bảo mật và hạ tầng; `docs/kien-truc-ung-dung.md` (KT) § 3 rìa B, § 7; `docs/migration.md`.

⚠ Ba cổng máy chỉ hỏi DẠNG: `tenant:check` hỏi "truy vấn có `workspaceId` không", `api:check` hỏi "route
ghi có GỌI `requirePermission(` không", `color:check` hỏi "có mã màu không". Không cổng nào hỏi "workspace
NÀO", "quyền NÀO", hay "403 hay 404". Đó là phần của bạn.

## A. Workspace — hàng **Workspace**

| # | Kiểm | Cách thấy | Mức |
|---|---|---|---|
| W1 | Mọi truy vấn CHỌN HÀNG lọc theo `workspaceId` — cả `update`/`delete`/`upsert`/`count`/`aggregate`/`groupBy`/`updateMany`/`deleteMany`, cả `$queryRaw`/`$executeRaw` | `tenant:check` đọc tĩnh; nó không thấy `where` dựng ở biến khác, SQL thô, hay `update({ where: { id } })` chạy SAU một `findFirst` có lọc (hai câu, chỉ câu đầu lọc) | 🔴 |
| W2 | `workspaceId` lấy từ PHIÊN, không từ thân request, query hay header | `body.workspaceId`, `searchParams.get("workspace…")` dùng làm bộ lọc | 🔴 |
| W3 | Bản ghi của workspace khác (hay không tồn tại) trả **404**, không 403 — 403 xác nhận rằng nó tồn tại | `findFirst` không thấy → `forbidden()`; phân nhánh "có nhưng không phải của bạn" | 🟠 |
| W4 | Bảng mới có cột `workspace_id` + chỉ mục; quan hệ cha–con dùng khoá ngoại KÉP `(workspace_id, cha_id) → (workspace_id, id)`; bảng thật sự không thuộc workspace thì có lý do trong `UNSCOPED_MODELS` (`scripts/check-tenant-scope.ts`) | `prisma/schema.prisma` | 🟠 |
| W5 | Định danh từ Account (user id) đi vào đường GHI được kiểm là thành viên của workspace, bằng `requireMemberDirectory()` | Ghi `assigneeUserId` từ thân request mà không tra danh bạ | 🟠 |

**Xong** khi mọi lời gọi Prisma và SQL thô thêm/đổi có câu trả lời W1–W2, mọi nhánh "không thấy" W3, mọi
model mới W4.

## B. Đường ghi — hàng **Đường ghi**

| # | Kiểm | Cách thấy | Mức |
|---|---|---|---|
| G1 | Route `POST`/`PUT`/`PATCH`/`DELETE`: `requireApiSession()` → `requirePermission(session, "<ĐÚNG quyền>")` → kiểm thân (lược đồ ở `lib/core/<x>-input.ts`) → gọi tầng D, tất cả trong `withApiErrors` | So mã quyền với HÀNH ĐỘNG: xoá chốt bằng quyền xoá, không bằng quyền sửa; đọc mã quyền ở `lib/catalog/permissions.ts`. Thiếu chốt, hay chốt sai quyền | 🔴 |
| G2 | `requireApiSession()`, KHÔNG `requireSession()` ở rìa B — bản kia `redirect()`, `withApiErrors` biến nó thành 500 | Grep route đổi | 🟠 |
| G3 | `// @api-guard: <lý do>` chỉ cho hai họ: (a) không có phiên người dùng (webhook tự xác thực bằng chữ ký, health/ready); (b) chỉ chạm phiên hay dữ liệu của CHÍNH người gọi, định danh lấy từ phiên | Lý do ngoài hai họ ("quyền này bỏ qua được", "chỉ admin dùng") | 🔴 |
| G4 | Ẩn nút không phải phân quyền; control còn bấm được thì giao diện nói dối — nhóm trường của module bọc `<ReadOnlyFieldset canEdit>` | Nút ẩn theo `can(…)` mà route tương ứng không chốt; trường cài đặt mới ngoài `ReadOnlyFieldset` | 🟠 |
| G5 | Phép ĐỌC lộ dữ liệu người khác (nhật ký kèm email/IP, xuất dữ liệu) cũng chốt quyền đọc | `GET` mới không chốt | 🟠 |
| G6 | Thao tác GHI đi route handler, không Server Action (`"use server"`) — Server Action mất `withApiErrors`, `ApiError`, hợp đồng `lib/api-client/`, và không gì nhắc `requirePermission()` | `"use server"` mới chạm database | 🟠 |

**Xong** khi mỗi export ghi thêm/đổi trong `app/api/**` có câu trả lời G1–G3, mỗi nút hay control mới bị
ẩn/khoá theo quyền có câu trả lời G4.

## C. Toàn vẹn — hàng **Toàn vẹn**

| # | Kiểm | Cách thấy | Mức |
|---|---|---|---|
| I1 | `PUT` ghi đè CẢ giá trị mang thẻ phiên bản: client gửi `version` trong thân; máy chủ tính lại từ bản ĐANG LƯU, TRONG cùng giao dịch ghi; thiếu → 400; lệch → 409 `STALE_WRITE`; thẻ là băm nội dung (`lib/core/version-token.ts`) | `PUT` mới không đọc `version`; so ngoài giao dịch; tính thẻ từ payload (luôn khớp với chính nó) | 🟠 |
| I2 | `PATCH` gửi từng trường; KHÔNG mang danh sách con (ghi đè cả mảng là đúng lớp lỗi I1 chặn) | Lược đồ `PATCH` có mảng | 🟠 |
| I3 | `$transaction`: bản ghi + con BẮT BUỘC ở trong; nhật ký, thông báo, thư ở NGOÀI; vòng thử lại mã ở NGOÀI | `sendMail`/`recordActivity` trong giao dịch; con bắt buộc tạo ngoài | 🟠 |
| I4 | Đếm-rồi-ghi dưới đua: khoá hàng (`FOR UPDATE`) rồi ĐỌC LẠI sau khoá; ràng buộc duy nhất ở DATABASE, không ở tầng ứng dụng | `count` rồi `create` trong cùng nhánh; kiểm trùng bằng `findFirst` thay `@@unique` | 🟠 |
| I5 | Số suy được thì suy; không cột đếm sẵn (tiến độ, số con, `overdue`) | Cột `xxxCount`, `isOverdue` mới | 🟡 |
| I6 | Migration tương thích ngược MỘT bản: không đổi tên/xoá cột hay `SET NOT NULL` không backfill trong một bước (mở rộng → backfill → thu hẹp, `docs/migration.md`); migration commit CÙNG `schema.prisma`; không sửa migration đã áp | `prisma/migrations/**` mới; `schema.prisma` đổi mà không có migration (`pnpm db:check` của CI bắt, nhưng nêu sớm) | gãy bản đang chạy 🔴 · còn lại 🟠 |
| I7 | Thời gian: ngày chỉ-có-ngày CẮT CHUỖI (`lib/core/iso-date.ts`), "hôm nay" là `todayIso(timeZone)` (`lib/today.ts`), `timeZone` truyền TƯỜNG MINH từ `page.tsx`/route — `lib/*.ts` không tự đọc phiên | `new Date("YYYY-MM-DD")`; `toISOString().slice(0, 10)`; hàm đọc dựa vào `DEFAULT_TIME_ZONE` ở đường request | 🟠 |
| I8 | Tầng dữ liệu giữ GIÁ TRỊ (`kind` + định danh), không câu chữ đã định dạng | Cột `verb`/`label`/`message` tiếng Việt trong bảng | 🟠 |

**Xong** khi mỗi `PUT`/`PATCH`/giao dịch/migration thêm/đổi có câu trả lời của ô tương ứng, và mỗi phép
tạo `Date` từ chuỗi có câu trả lời I7.

## D. Tiêm & bí mật — hàng **Tiêm & bí mật**

| # | Kiểm | Cách thấy | Mức |
|---|---|---|---|
| S1 | XSS: không `dangerouslySetInnerHTML` với dữ liệu; `href`/`src`/`action` từ dữ liệu người dùng có allowlist scheme (chặn `javascript:`, `data:`) | Grep dòng thêm | 🔴 |
| S2 | Tiêm CSS: `style`/`var(--${…})` không dựng từ dữ liệu — chỉ qua bảng ĐÓNG (`appFrameAccentFor()` ở `lib/catalog/apps.ts`) | Chuỗi từ database vào `style=` | 🔴 |
| S3 | Open redirect: `?next=`/`returnTo`/`callbackUrl` chỉ nhận đường dẫn NỘI BỘ (bắt đầu `/`, không `//`) | `redirect(searchParams…)` | 🔴 |
| S4 | SSRF: URL người dùng nhập mà máy chủ gọi (webhook, ảnh từ xa) có lọc — lọc theo ĐỊA CHỈ, không chỉ theo tên; `localhost.` có dấu chấm cuối vượt phép so tên | `fetch(url)` ở máy chủ với `url` từ thân | 🔴 |
| S5 | Bí mật: biến không `NEXT_PUBLIC_` không ở file client; cấu hình đọc qua `lib/env.ts` (ngoại lệ chỉ là bảng ở AG § Cạm bẫy › Bảo mật và hạ tầng); `NEXT_PUBLIC_*` viết NGUYÊN VĂN; không token, khoá, mật khẩu hay `.env` trong diff | Grep `process.env`, chuỗi giống khoá | 🔴 |
| S6 | `withApiErrors` bọc route — `error.message` của Prisma (tên bảng, tên cột) không ra ngoài; lỗi trả `{ error: { code, message } }` | Route trả `e.message` thô | 🟠 |
| S7 | Log: không dữ liệu cá nhân hay token vào `console.*`; giá trị từ client vào log đi qua bộ làm sạch (một ký tự xuống dòng bẻ một dòng log thành hai dòng giả — `lib/core/request-id.ts`) | `console.*` mới | 🟠 |
| S8 | Kho ảnh: database lưu KHOÁ object, không lưu URL đã ký; khoá mang tiền tố `{app}/{tính-năng}` | Cột `imageUrl` ghi URL ký | 🟠 |
| S9 | CSV xuất: có BOM, vô hiệu ô bắt đầu bằng `= + - @`, xuất đúng tập ĐANG LỌC | Hàm xuất mới không qua bộ CSV mà khuôn `comitor-page` sinh cùng thực thể đầu tiên | 🟠 |
| S10 | CSP (`proxy.ts`, `lib/core/csp.ts`): không nonce ở `style-src`; `script-src` đứng trước mọi `script-src-*`; đúng MỘT header CSP | Đổi chính sách | 🔴 |

**Xong** khi mọi `dangerouslySetInnerHTML`, `href`/`src`/`style`/`redirect` dựng từ dữ liệu, `process.env`,
`fetch` phía máy chủ, `console.*` và cột lưu file thêm vào đều đã được lần ngược về nguồn của nó.

## E. Hướng hỏng — hàng **Hướng hỏng**

Mỗi đường hỏng phải hỏng theo hướng đã CHỌN. Câu hỏi không phải "có xử lý lỗi không" mà "khi hỏng, người
dùng tin vào điều gì?".

| # | Kiểm | Cách thấy | Mức |
|---|---|---|---|
| H1 | Đường ĐỌC fail-open, đường GHI fail-closed: `memberDirectory()` (trả `Map` rỗng khi Account chập chờn) chỉ ở đường đọc; đường ghi dùng `requireMemberDirectory()` (503) — danh bạ rỗng trả lời "không phải thành viên" cho MỌI người | `memberDirectory()` trong route ghi hay trong phép kiểm trước khi ghi | 🟠 |
| H2 | Lỗi nạp dữ liệu màn hình thành TRẠNG THÁI LỖI có đường thử lại — không thành danh sách rỗng, "không có kết quả", hay im lặng | `.catch(() => [])`, `catch { return null }` ở đường dữ liệu màn hình | 🟠 |
| H3 | Giao diện tra `code` (và `status` cho 429 — limiter thường trả 429 trần) qua `useErrorMessage()`; không in `message` của máy chủ; mã mới có ở `errors.code.*` cả hai ngôn ngữ | `toast.error(error.message)`; ép lỗi thành `{ code }` làm rơi `status` | 🟠 |
| H4 | Lỗi CẤU HÌNH nổ lúc khởi động (`lib/env.ts`); lỗi GỬI (thư, webhook) thì nuốt kèm một dòng log CỐ ĐỊNH viết HOA để grep/alert — bước đọc cấu hình nằm NGOÀI `try` | `try` bọc cả bước chọn transport | 🟠 |
| H5 | Module KHÔNG tự sinh 429 (`ApiError.rateLimited()` chỉ để chuyển tiếp 429 của Account); nhận 429 thì trả 429, không nuốt, không đổi thành 500 | Limiter trong module; `catch` đổi 429 thành 500 | 🟡 |
| H6 | Chuỗi sự kiện log viết HOA (`[auth] KHÔNG XOAY ĐƯỢC TOKEN`, `[i18n] KHOÁ HỎNG`, `[mail] KHÔNG GỬI ĐƯỢC`) giữ NGUYÊN chữ — chúng là hợp đồng grep/alert | Sửa chữ của một chuỗi như thế | 🟠 |
| H7 | `catch` rỗng hay nuốt lỗi mà không log | `catch {}` | 🟡 |
| H8 | Thao tác có bước sau đã commit (ghi phụ sau khi bản ghi chính đã lưu) không ném ra người dùng — một lỗi ở đó cho trang lỗi sau một thao tác ĐÃ thành công | `await` bước phụ không bọc, sau `create` | 🟠 |

**Xong** khi mỗi `catch`, mỗi nhánh lỗi mới của một màn hình, và mỗi lời gọi danh bạ thêm/đổi có câu trả
lời "hỏng thì người dùng thấy gì".
