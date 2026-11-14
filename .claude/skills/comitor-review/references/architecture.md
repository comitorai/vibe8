# Kiến trúc — năm hàng

**Phạm vi:** file đổi dưới `lib/`, `stores/`, `hooks/`, `components/`, `app/`, `prisma/`, cùng `proxy.ts`.
Không có → cả nhóm n/a.

Nguồn luật: `docs/kien-truc-ung-dung.md` (KT) § 1–§ 4, § 7–§ 8, § 10; `AGENTS.md` (AG) § Kiến trúc, § Ranh
giới Account / app, § Quy ước bắt buộc giữ. Mỗi hàng: mẫu cơ học chạy trên dòng THÊM của diff `-U0` (kết
quả là ứng viên, xác nhận trong ngữ cảnh) và câu hỏi phán đoán trả lời có/không cho từng file.

⚠ **Cột CẤM của KT § 2 do máy canh** (Biome `overrides`, `server-only`, `core:check`,
`core-loads-clean.test.ts`, `server-load:check`) — đừng báo lại thứ `pnpm lint` đã đỏ. Review canh phần máy không thấy: import
BẮC CẦU, ý nghĩa của một câu `if`, và chỗ máy được miễn (`app/`, `components/` không có override Biome).

## A. Tầng — hàng **Tầng**

| # | Kiểm | Cách thấy | Mức |
|---|---|---|---|
| T1 | Lõi thuần: `lib/core/**` không kéo vào `react`, `next/*`, `@prisma/*`, `@comitor/ui`, `next-intl`, `server-only`, hay `@/lib/**` ngoài `lib/core`·`lib/contracts` — kể cả BẮC CẦU | Đọc từng file mà file lõi mới import; module lõi mới có nằm trong vùng `lib/core/core-loads-clean.test.ts` quét không | 🟠 |
| T2 | Lõi KHÔNG trả chuỗi hiển thị — chỉ `code`/`level`/`kind`, nơi gọi tra nhãn | Trong `lib/core/**`: chuỗi chữ làm giá trị trả về hay thuộc tính `label`/`title`/`message`/`description`. `core:check` chỉ bắt chuỗi CÓ DẤU — "Too weak" lọt | 🟠 |
| T3 | Không phép tính nghiệp vụ trong `.tsx`, hook hay `route.ts` | Trong component/page/hook/route: `if`/`switch`/ternary, `.filter`/`.reduce`/`.sort`/`.some` trên dữ liệu nghiệp vụ; so ngày, ngưỡng, vai trò; ánh xạ trạng thái → tone/nhãn. Chuỗi trình tự thuần (gọi lõi rồi gán) không phải phát hiện | 🟠 |
| T4 | Store chỉ khi thoả MỘT trong bốn điều kiện (KT § 3 tầng 3), và store là TRÌNH TỰ chứ không là LUẬT | Store mới mà mô tả PR/thân commit không nêu điều kiện nào; câu `if` trả lời câu hỏi nghiệp vụ mà không gọi `lib/core/`; `zustand` bản React thay `zustand/vanilla`; thiếu `import "client-only"`; cổng API import thẳng thay vì nhận qua đối số `createXxxStore(api)`; store trả câu chữ hay gọi toast | 🟠 |
| T5 | Hook là cầu nối store → lõi → component | Trong `hooks/**`: phép tính nghiệp vụ, `fetch`, Prisma | 🟡 |
| T6 | Rìa B làm đúng bốn việc: phiên → quyền → hình dạng thân → gọi tầng D | `route.ts` chứa nghiệp vụ (vòng lặp nhiều bước, Prisma trực tiếp, tính toán) thay vì gọi `lib/<thực-thể>.ts` — nghiệp vụ ở route thì `pnpm seed`, job nền và script không gọi lại được (AG § Quy ước) | 🟠 |
| T7 | Tầng D (`lib/*.ts`) không import `@comitor/ui`, không import bảng khai mang icon/màu (`lucide-react`, `@comitor/ui`) trực tiếp hay bắc cầu, và không import TĨNH `next/navigation`·`next/link`·`next/image`. Bảng khai không mang icon/màu thì được (`lib/permissions.ts` đọc `lib/catalog/permissions.ts`); `import type` không tính (KT § 2 hàng D) | Bảng khai và đường bắc cầu: `pnpm server-load:check` NẠP từng file tầng D dưới `--conditions=react-server` — review không lần đường import bằng mắt; đọc dòng ✗ của nó. Repo chưa có cổng đó (module chưa chép, CHANGELOG v0.38.0) thì nạp từng file đổi: `pnpm exec tsx --conditions=react-server --env-file=.env -e 'import("./lib/<file>.ts")'`. Phần cổng không thấy: import TĨNH `next/*` (grep dòng thêm của `lib/*.ts` — cổng nạp được chúng); helper của Next cần ở tầng D thì `import()` ĐỘNG trong chính hàm, kèm `biome-ignore` có lý do | 🟠 |
| T8 | Không `fetch(` ngoài `lib/api-client/` — kể cả `navigator.sendBeacon`, `EventSource`, `new WebSocket` | `grep -rn 'fetch(' app components hooks --include='*.tsx' --include='*.ts' \| grep -v lib/api-client \| grep -vE '^[^:]+:[0-9]+: *\*'` (lệnh của KT § 2 — vế cuối loại dòng comment). Một lời gọi trần là vô hình với API giả: nó gọi máy chủ THẬT giữa phiên giả | 🟠 |

**Xong** khi mỗi file đổi có câu trả lời cho các ô của tầng nó: T1–T2 `lib/core/`, T4 `stores/`, T5
`hooks/`, T3 mọi `.tsx`/hook/route, T6 `app/api/**`, T7 `lib/*.ts`, T8 mọi file.

## B. Một luật, hai nơi gọi — hàng **Một luật**

Đây là hàng đắt nhất của nhóm: lỗi của nó đi qua mọi cổng, vì mỗi bản viết tay đều ĐÚNG lúc được viết.

| # | Kiểm | Cách thấy | Mức |
|---|---|---|---|
| M1 | Mỗi câu hỏi nghiệp vụ (được/không, hợp lệ/không, quá hạn, ngưỡng, thứ tự, ai thấy gì) có MỘT hàm `lib/core/`, và MỌI nơi hỏi câu đó gọi nó: route, `page.tsx`, component, store, API giả | Với mỗi hàm lõi diff thêm hoặc đổi: `grep -rn "<tên hàm>" app components hooks stores lib`. Thấy ở route mà không thấy ở giao diện (hay ngược lại) trong khi phía kia vẫn trả lời CÙNG câu hỏi bằng mã riêng → phát hiện | 🟠 |
| M2 | Không bản viết tay thứ hai của một luật đã có | Điều kiện viết lại inline mà lõi đã có hàm: so vai trò, so ngày với hôm nay, regex email/slug, danh sách mã lỗi/mã chặn, độ dài tối đa. Grep tên hằng hoặc literal trong `lib/core/` | 🟠 |
| M3 | API giả gọi CÙNG hàm lõi với route thật, cùng thứ tự chốt (401 → 403 → 400 → 409) | `lib/api-client/fake/router.ts` đổi mà không import hàm lõi route dùng; route đổi luật mà handler giả không đổi | 🟠 |
| M4 | Hằng dùng chung khai MỘT lần | Cùng một mảng literal (giá trị trạng thái, mã quyền) ở hai file; `href:` ngoài `lib/catalog/navigation.ts` (`grep -rn 'href: "/' lib/catalog/*.ts` chỉ được ra file đó) | 🟠 |

**Xong** khi mỗi hàm lõi thêm/đổi đã grep đủ nơi gọi, và mỗi điều kiện nghiệp vụ mới viết ngoài lõi đã
được so với `lib/core/` (có hàm tương đương thì M2, chưa có thì T3).

## C. Ranh giới máy chủ ⇄ trình duyệt — hàng **Ranh giới**

| # | Kiểm | Cách thấy | Mức |
|---|---|---|---|
| R1 | File máy chủ mới trong `lib/` mang `import "server-only"` | `lib/*.ts`, `lib/account/**`, `lib/api/**` mới thiếu dòng đó. Ngoại lệ có lý do: `lib/format.ts`, `lib/today.ts` (lý do ở đầu file), và tầng 0/1/2/★ | 🟠 |
| R2 | `"use client"` thấp nhất có thể | `page.tsx`/`layout.tsx` gắn `"use client"` (mất `generateMetadata`, đẩy dữ liệu xuống bundle); vỏ client quanh cây không có hook hay handler | 🟡 |
| R3 | BẢN GHI vào app ở hai cửa (`page.tsx`, `app/(shell)/layout.tsx`); file client nhận prop thuần | File `"use client"` import `lib/<thực-thể>.ts` hay Prisma; Server Component `fetch("/api/…")` chính app (thêm một vòng mạng và một lần xác thực lại) | 🟠 |
| R4 | Prop qua ranh giới server → client tuần tự hoá được | Truyền `Date`, `Decimal`, hàm, component icon, `messages` có khoá là hàm; kiểu ở `lib/contracts/**` dùng `Date` thay chuỗi ISO (Next đổi thành chuỗi mà kiểu vẫn nói `Date` — sai ÂM THẦM) | 🟠 |
| R5 | Không ghi cookie lúc render | `cookies().set(` ngoài route handler và `proxy.ts` — không hỏng lúc build, nổ ở lần đầu cần ghi | 🔴 |
| R6 | `params`/`searchParams` được `await` và chuẩn hoá (mảng → phần tử đầu; rỗng sau `trim` = không có) | Dùng thẳng `searchParams.x` | 🟡 |
| R7 | Bảng khai (`lib/catalog/**`) không nhận dữ liệu từ máy chủ, chỉ hằng giao diện | Bảng khai đọc Prisma, phiên, `process.env` không `NEXT_PUBLIC_` | 🟠 |

**Xong** khi mỗi file `lib/` mới có câu trả lời R1, mỗi `"use client"` mới và mỗi prop mới đi qua ranh
giới có câu trả lời R2–R4.

## D. Chỗ đặt — hàng **Chỗ đặt**

| # | Kiểm | Cách thấy | Mức |
|---|---|---|---|
| P1 | Cụm tự viết: phục vụ MỘT route → cạnh route đó; nhiều route hoặc là mảnh của khung → `components/`. Đầu file ghi VÌ SAO nó tồn tại (gói thiếu gì, hay nó chỉ nối component nào) | File mới sai chỗ; file `components/` mới chỉ một route dùng; thiếu dòng lý do ở đầu | 🟡 |
| P2 | Thực thể mới đủ khuôn: `lib/core/<x>.ts` + test, `lib/<x>.ts`, route, `lib/api-client/`, `lib/contracts/`, bảng khai, chuỗi, quyền | Đối chiếu bảng ở `docs/them-mot-thuc-the.md` — cột cuối nói bước nào KHÔNG cổng nào bắt nếu quên | 🟡 |
| P3 | Mục điều hướng mới: `lib/catalog/navigation.ts` + `nav.*` ở cả hai ngôn ngữ, gác cùng quyền với route; tab Cài đặt SUY từ `children` | Trang mới không có mục, hoặc mục không có quyền; danh sách tab khai lại `href` | 🟠 |
| P4 | Không route lạ: thử nghiệm dưới `_scratch/`; trang mới có trong bản đồ route của README | `page.tsx` mới không có dòng ở README § Bản đồ route | 🟡 |
| P5 | Job nền: `scripts/jobs/<tên>.ts` mỏng, nghiệp vụ ở `lib/`, chạy kèm `--conditions=react-server`, lịch do HẠ TẦNG (không `setInterval` trong tiến trình Next), một workspace hỏng không làm chết cả vòng | Job mới | 🟠 |
| P6 | Thao tác của một khu là nút chính ở header + lệnh ⌘K, không là mục riêng ở thanh bên | Mục `NAV_ITEMS` kiểu "Tạo …" | 🟡 |

**Xong** khi mỗi file thêm mới (`git diff --name-status` cột `A`) có câu trả lời P1, mỗi `page.tsx` mới có
câu trả lời P3–P4.

## E. Ranh giới Account / module — hàng **Account**

Account trả lời đúng BA câu: *bạn là ai* · *bạn thuộc workspace nào với vai trò thô gì* · *workspace đó
được dùng app nào*. Mọi câu khác là của module, dữ liệu ở database của module (AG § Ranh giới Account / app).

| # | Kiểm | Cách thấy | Mức |
|---|---|---|---|
| A1 | `prisma/schema.prisma` không có bảng `User`/`Workspace`/`Member`/`Role`; không cột chép định danh sang tên (`assignee_name`, `owner_email`) — module giữ ĐỊNH DANH, tên đọc từ `lib/account/directory.ts` | Model/cột mới | 🟠 |
| A2 | Không dựng lại màn hình của Account: thành viên, lời mời, hồ sơ, mật khẩu, cài đặt workspace, gói/chỗ ngồi, tuỳ chọn hiển thị (sáng/tối, ngôn ngữ, mật độ, cỡ chữ) | Trang hay tab Cài đặt mới; trường mới không trả lời được "nó đổi cách ỨNG DỤNG NÀY làm việc à?" | 🟠 |
| A3 | URL sang Account qua `lib/account/links.ts`; liên kết sang sản phẩm khác mang `?w={slug}`, không `/w/{slug}` | Chuỗi URL của Account hay sản phẩm anh em ghép tay | 🟡 |
| A4 | Không vai trò thô thứ năm; quyền chi tiết ở `lib/catalog/permissions.ts` + bảng `role_permissions`; hai hằng của ma trận giữ nguyên (chủ sở hữu luôn có mọi quyền, khách không bao giờ có quyền GHI) | So sánh với một chuỗi vai trò mới; đổi `permissionLock` | 🟠 |
| A5 | Không import `better-auth/*`; xác thực đi qua `@comitor/account-sdk` | Grep dòng thêm | 🔴 |
| A6 | Không gọi API quản trị của Account bằng access token của app — app ĐỌC ngữ cảnh, người dùng QUẢN TRỊ tại Account | Lời gọi ghi tới Account từ module | 🟠 |

**Xong** khi mỗi model/cột mới, mỗi trang mới và mỗi URL mới có câu trả lời A1–A3, và mỗi chuỗi vai trò
hay import mới có câu trả lời A4–A5.
