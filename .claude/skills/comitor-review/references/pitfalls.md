# Lỗi lặp lại ở Comitor — và chúng trông thế nào trong một diff

Mỗi dòng là một lỗi ĐÃ XẢY RA ở một repo Comitor — phần lớn ở `comitor-starter` (ghi phiên bản hoặc "bản mẫu
cũ") hay `comitor-account` (ghi "Account"), còn lại ghi tên repo — kèm cách nhận ra nó trên dòng diff. Đọc một lần trước khi review; điều kiện **xong** của
từng hàng mới quyết định khi nào hàng đó xong — bảng này cho biết một phát hiện TRÔNG ra sao khi bạn tới đó.

Điểm chung của gần như mọi dòng: **không cổng máy nào đỏ.** `tsc`, Biome, `i18n:check`, test đều xanh, vì
mỗi mảnh đều đúng khi đứng riêng.

## Một luật, viết hai lần

| Lỗi | Thấy trong diff thế nào | Đã gặp ở |
|---|---|---|
| Thanh bên lọc mục theo quyền, dải tab Cài đặt thì không — tab của quyền người xem không có vẫn bấm được rồi ra 404 | Một danh sách thứ hai được lọc (hoặc không lọc) bằng mã riêng thay vì `visibleNavItems` | starter v0.21.0 |
| Danh sách tab khai LẠI bốn `href` của Cài đặt — đổi đường dẫn một chỗ thì dải tab trỏ vào 404 | `href:` ngoài `lib/catalog/navigation.ts` | starter (`SETTINGS_TABS`) |
| Bốn mã chặn của Account khai ở hai file | Mảng mã/hằng trùng nội dung ở hai file | starter v0.21.0 |
| Hai bản `toErrorLike` cùng ba chỗ ép lỗi thành `{ code }` — `status` rơi mất, 429 hiện "máy chủ gặp sự cố" | Hàm thu hẹp lỗi viết tại chỗ thay vì `errorMessageChoice` | starter v0.21.0 |
| Quản trị viên nhắm vào chủ sở hữu duy nhất: giao diện nói `last-owner`, máy chủ trả 403; tên nhóm: máy chủ so bằng `ILIKE` | Route kiểm bằng mã riêng một điều giao diện đã kiểm bằng hàm lõi | Account 1.4.0 |

## Phân quyền và đường ghi

| Lỗi | Thấy trong diff thế nào | Đã gặp ở |
|---|---|---|
| Route ghi gọi `requireSession()` — `redirect()` bị `withApiErrors` biến thành `500 INTERNAL_ERROR` cho một phiên hết hạn bình thường | `requireSession(` trong `app/api/**` | starter (route nháp của bản mẫu cũ) |
| Người chỉ-đọc bấm công tắc, công tắc LẬT, thanh Lưu ẩn nên không gì nói thay đổi không đi đâu — họ tin là đã đổi | Thanh lưu ẩn theo quyền, control không nằm trong `ReadOnlyFieldset` | starter (tab Thông báo bản mẫu cũ) |
| Access token mang `openid profile email` đọc được nhật ký kèm IP/email của mọi thành viên và CHUYỂN được quyền sở hữu workspace | Đường ghi/đọc nhạy cảm chấp nhận token của app thay vì phiên của người dùng | Account |
| Hai đường ghi vào cùng một bảng; đường thứ hai không làm việc phụ (dọn chỗ ngồi, kiểm logo) | Route mới ghi bảng mà một route khác đã ghi kèm bước phụ | Account |
| Chốt đặt trên MỘT endpoint bị vòng qua bằng hai lời gọi (xoá rồi tạo lại để xoá trạng thái nợ) | Chốt trên `PATCH`; hỏi "còn đường nào khác tới cùng trạng thái không?" | Account |

## Workspace, dữ liệu, toàn vẹn

| Lỗi | Thấy trong diff thế nào | Đã gặp ở |
|---|---|---|
| Tra người dùng bằng `mode: "insensitive"` (Prisma dịch thành `ILIKE`, `_` là ký tự đại diện): quản trị viên gõ một email, hệ thống thêm SAI NGƯỜI vào workspace | `mode: "insensitive"` ở một phép tra RA QUYẾT ĐỊNH (ô tìm kiếm thì được) | Account |
| Bản ghi trùng lặp thật trong database trước khi có `@@unique` | Kiểm trùng bằng `findFirst` rồi `create` | Account |
| Đếm-rồi-ghi trong giao dịch vẫn đua dưới `READ COMMITTED` | `count` rồi ghi mà không khoá hàng và đọc lại | Account |
| Spread có điều kiện truyền `targetName` cho hàm nhận `targetUserId` — biên dịch sạch, nhật ký "đã giao việc cho {target}" thiếu chủ ngữ | `...(c ? { x } : {})` với tên khoá không có trong kiểu | starter |
| `NULL <= now` là UNKNOWN: bản ghi mới có `nextRetryAt = NULL` không bao giờ được cron quét | Cột thời gian nullable dùng trong `lte` | Account |
| Cột ảnh giữ KHOÁ object, route trả nguyên văn làm `src` — ảnh 404 im lặng ở mọi màn hình dùng API ấy | Trả cột khoá ra ngoài mà không ký URL | Account |
| `Date`/`Decimal` qua ranh giới server → client: lỗi lúc chạy ở chỗ cách xa nguyên nhân, hoặc sai kiểu âm thầm | Prop hay trường hợp đồng mang `Date`/`Decimal` | starter |

## Thời gian

| Lỗi | Thấy trong diff thế nào | Đã gặp ở |
|---|---|---|
| `new Date("2026-08-20")` là 00:00 UTC — bộ lọc ngày của nhật ký mất bảy tiếng đầu ngày ở GMT+7 | `new Date(` trên chuỗi chỉ-có-ngày | Account |
| `toISOString().slice(0, 10)` trả ngày HÔM QUA trong bảy tiếng đầu mỗi ngày ở GMT+7 | Đúng biểu thức đó | starter |
| Tooltip giờ tuyệt đối của `<RelativeTime>` in giờ MÁY CHỦ và giữ mãi sau hydrate | `<RelativeTime` thiếu `timeZone` | starter (gói 3.4.0) |

## Đa ngôn ngữ

| Lỗi | Thấy trong diff thế nào | Đã gặp ở |
|---|---|---|
| `<>t("x")</>` in NGUYÊN VĂN `t("x")` lên màn hình | `t(` trong văn bản JSX, không có `{}` | starter (tab Nâng cao bản mẫu cũ) |
| Markdown và backtick trong `messages/` hiện nguyên dấu sao cho người dùng — kèm cả đường dẫn mã nguồn | `**`, `` ` `` trong giá trị chuỗi | starter (`settings.notYetActive`) |
| Hàm lõi gắn `label: "Quá yếu"` — không ở `messages/` nên `i18n:check` không thấy, chạy đúng ở tiếng Việt nên không ai báo | Thuộc tính chuỗi hiển thị trong `lib/core/` | Account |
| `t.has()` trả `true` cho khoá là OBJECT rồi `t()` in đường dẫn khoá | Tra khoá động không tới khoá lá | Account |
| `format.dateTime(d, "long")` là TÊN định dạng — không khai thì rơi về `Date.toString()` ở cả hai ngôn ngữ | Đối số thứ hai là chuỗi | Account |
| Mã lỗi khai ở nhóm `errors.code` trong khi nơi gọi tra nhóm `errors.auth` — chốt chạy đúng mà người dùng đọc "lỗi không xác định" | Mã mới chỉ có ở một nhóm | Account |

## Hướng hỏng

| Lỗi | Thấy trong diff thế nào | Đã gặp ở |
|---|---|---|
| 429 bị đếm là "mã sai" — ba lần là khoá cứng người dùng khỏi 2FA | Nhánh lỗi không tách `status === 429` | Account |
| Bước đọc cấu hình thư nằm TRONG `try` của bước gửi — một biến gõ sai bị nuốt, hệ thống êm ru mà không lá thư nào đi | `try` bọc cả bước chọn transport | Account |
| Danh bạ rỗng (Account chập chờn) dùng ở đường ghi trả lời "không phải thành viên" cho MỌI người | `memberDirectory()` trước một lần ghi | starter |

## API giả

| Lỗi | Thấy trong diff thế nào | Đã gặp ở |
|---|---|---|
| Nút Đăng xuất gọi thẳng `fetch` — ở chế độ giả nó bắn vào máy chủ THẬT | `fetch(` ngoài `lib/api-client/` | starter v0.21.0 |
| Điều kiện build import từ module khác không được bundler gấp — router giả lọt vào bốn file `.next/static` | `import()` mã giả với điều kiện không viết nguyên văn `process.env.…` tại chỗ | Account |
| Thiếu `refreshKey` — ở chế độ giả lời mời vừa gửi không bao giờ hiện ra | Vỏ client không nạp lại theo khoá | Account |
| Handler giả trả một fixture cố định — biên dịch được, qua Playwright-fake, và NÓI DỐI | `return FIXTURE` trong router giả | Account (bản v0) |

## Test không thể đỏ, cổng không kiểm gì

| Lỗi | Thấy trong diff thế nào | Đã gặp ở |
|---|---|---|
| Test chạy trên một adapter bộ nhớ không nguyên tử — phép thử đua xanh GIẢ | Test về tính nguyên tử không chạy trên database thật | Account |
| Test của hàm đọc giờ ĐỊA PHƯƠNG xanh ở CI (UTC) với chính cách cài sai nó canh | Test không ghim `process.env.TZ`, hay chỉ khẳng định khi máy ở múi dương | starter v0.21.1 (lần chạy thử đầu của skill này) |
| `version:check` trên clone nông: không tìm được mốc, rơi vào nhánh "bỏ qua" và in ✓ (nay ĐỎ ở CI) | Workflow hạ `fetch-depth` khỏi `0`, hay bỏ `origin/main` khỏi checkout | starter |
| Dấu hiệu của `fake:bundle-check` là chuỗi ghép lúc chạy — không bao giờ có trong bundle, phép kiểm xanh vô điều kiện | Dấu hiệu không phải chuỗi nguyên văn trong mã | starter v0.21.0 |
| Test của khung ghim đúng hai mã quyền — đỏ ngay khi một thực thể thêm sáu mã | `toEqual([...])` trên danh sách module mở rộng | starter v0.21.0 |

## Giao diện

| Lỗi | Thấy trong diff thế nào | Đã gặp ở |
|---|---|---|
| Icon làm con của `<Button>` render 24px, gấp rưỡi mọi icon nút khác | Icon trong `Button` không `size-4` — chỉ khi gói dưới 3.13.0 (từ 3.13.0 gói tự cỡ icon chưa có `size-*`) | starter |
| Lưới `lg:grid-cols-3` thiếu `grid-cols-1`: ở 375px card thò ra 86px | `grid` đáp ứng không có bậc cơ sở | starter (`/`) |
| `className="w-56"` trên `Combobox` — cụm icon trôi cách nút 350px | Bề rộng đặt trên component thay vì thẻ bọc | starter |
| `col-span-12` trong `DialogContent` đẻ 11 track ngầm, header/footer bị bóp | Trường của gói cũ trong hộp thoại | Account |
| Truyền `locale` date-fns (object chứa hàm) từ Server Component — cả trang tổng quan rơi vào `error.tsx` | Prop là object có hàm qua ranh giới | Account |
| `FormControl` dán `id`/`aria-*` lên thẻ bọc — ô nhập thật không có tên, câu lỗi không gắn vào ô nào | Thẻ bố cục đặt giữa `FormControl` và control | Account |

## Tài liệu nói dối

| Lỗi | Thấy trong diff thế nào | Đã gặp ở |
|---|---|---|
| Bảng ngoại lệ `process.env` đếm thiếu ba lần — người đọc đi "sửa" một chỗ vốn đúng | Con số đếm tay trong tài liệu | starter |
| Tiêu đề tài liệu SDK ghi "ba lớp guard" trên một bảng bốn hàng; module chép nguyên con số | Số trong tiêu đề | starter (`CLAUDE.md`) |
| `version` đứng yên qua nhiều đợt phát hành — người dùng báo lỗi kèm một phiên bản không chứa lỗi | Commit vào `main` không tăng `version` | Account; starter (tag `v0.2.0`, `package.json` còn `0.1.0`) |
| Comment khẳng định ngược với mã (một endpoint "không xoá" hàng mà thật ra có xoá) | Comment mới về hành vi của thư viện, không kèm phép đo | Account |

## Lệch đặc tả

| Lỗi | Thấy trong diff thế nào | Đã gặp ở |
|---|---|---|
| Đặc tả lịch dự án không đặt giới hạn độ dài việc; mã tự thêm trần 3.700 ngày làm việc và trả lỗi. Review xếp 🟡 "hợp lý" rồi APPROVE; một QA đặt từng điều đặc tả cạnh mã thì cho TRƯỢT và bắt sửa — ba lượt mới hết | Hằng số hay `throw` mới không truy được về điều nào của đặc tả; comment "phòng hờ", "cho an toàn" | comitor-tasks 31.10.2026 (thí nghiệm T4.5, PR nháp #202) |
| Cùng việc: đặc tả nói "đặt ngày xong = ngày trễ mới"; mã tự dời ngày đó sang ngày làm việc kế khi nó rơi vào ngày nghỉ — lệch một ngày mọi việc phía sau | Ca biên đặc tả không nói tới được xử lý im lặng, mô tả PR không ghi lựa chọn | comitor-tasks 31.10.2026 (cùng PR) |

