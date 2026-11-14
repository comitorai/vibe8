# Chất lượng — sáu hàng

**Phạm vi:** mọi diff. Hàng **Test** n/a khi diff không đổi mã chạy được; hàng **Trạng thái** n/a khi
không đổi màn hình.

Nguồn luật: skill `comitor-test` (tháp, mười hai luật, `references/review.md`); `docs/kien-truc-ung-dung.md`
(KT) § 6–§ 8, § 10; `AGENTS.md` (AG) § Kiểm chứng thay đổi; `CONTRIBUTING.md` (CT); `CLAUDE.md` § Giới hạn
khi sửa.

## A. Đúng — hàng **Đúng**

Logic sai, nơi gọi gãy, luật React (thứ tự hook, mảng phụ thuộc không ổn định), `null`/`undefined`, đua,
lệch một. Kiểm trên nơi gọi THẬT — không bao giờ phán một hunk đứng riêng.

**Bán kính ảnh hưởng.** Với mỗi hàm, component, hook, route hay hằng export bị đổi, liệt kê nơi gọi, các
BẢN ANH EM và nơi tiêu thụ, rồi đọc từng cái xem có cần cùng thay đổi không. Anh em quen thuộc của Comitor:

| Đổi ở | Anh em phải xem |
|---|---|
| route `app/api/**` | phương thức ở `lib/api-client/`, kiểu ở `lib/contracts/`, handler ở `lib/api-client/fake/router.ts` + test, nơi tiêu thụ giao diện |
| quy tắc ở `lib/core/` | mọi nơi gọi (route, `page.tsx`, component, store, API giả) — hàng **Một luật** |
| lưới danh sách của một thực thể | biểu mẫu tạo, trang chi tiết, thẻ ở Tổng quan, bảng lệnh ⌘K, xuất CSV — cùng bộ lọc, cùng luật |
| mục điều hướng | `lib/catalog/navigation.ts`, dải tab Cài đặt (suy từ `children`), ⌘K, `nav.*` ở cả hai ngôn ngữ, quyền gác route |
| chuỗi ở tệp `vi` của `messages/` | cùng khoá ở tệp `en` (repo tách `messages/` thành tệp phần thì ở tệp phần cùng tên) |
| màn chạy ở chế độ giả | vỏ `fake-<màn>.tsx`, `FAKE_SUPPORTED` (`lib/core/fake-routes.ts`), kịch bản, page object `tests/e2e/pages/**` |
| file khung mà khuôn `comitor-page` vá vào | khuôn `.tpl` tương ứng (`verify.mjs` — § F) |
| mục "Cạm bẫy" của AGENTS.md | khoản tương ứng trong skill `comitor-ui`/`comitor-page`/`comitor-test` |

Hai mục luôn có trong danh sách: mọi `href` hay `redirect` mới trỏ tới một `page.tsx` có thật dưới `app/` và
có trong bản đồ route của README; và nâng `@comitor/ui` thì đã đọc "App phải làm gì" của MỌI bản nằm giữa
(`.claude/skills/comitor-ui/references/upgrading.md`) — nhiều khoản phá vỡ KHÔNG làm `typecheck` đỏ.

**Đặc tả của việc.** "Đúng" là đúng THEO ĐẶC TẢ đã duyệt, không theo điều người viết thấy hợp lý. Tìm đặc tả
một lần: dòng `Đặc tả:` (hay `Spec:`) trong mô tả PR hoặc thân commit; không có thì file làn `docs/lan/<làn>.md`
của nhánh và spec nó trỏ tới (`docs/san-pham/**`). Đọc phần hợp đồng, luật ngữ nghĩa và tiêu chí chấp nhận —
không đọc cả tài liệu. Không thấy đặc tả nào → hai ô dưới n/a, và **Đã kiểm** ghi "không thấy đặc tả".

| # | Kiểm | Cách thấy | Mức |
|---|---|---|---|
| DT1 | Mã làm đúng điều đặc tả viết, không hơn, không kém: không thêm giới hạn, kiểm tra, giá trị mặc định, làm tròn hay dời ngày mà đặc tả không viết; không bỏ ca đặc tả có; không đổi ngữ nghĩa, mã lỗi, thứ tự | Đặt từng điều của đặc tả cạnh dòng diff hiện thực nó; một hằng số, `throw` hay nhánh `if` mới không truy được về điều nào | 🟠 — **kể cả khi bản lệch trông an toàn hơn**. Lệch đặc tả không bao giờ là 🟡/⚪ |
| DT2 | Chỗ đặc tả im lặng hoặc hiểu được hai cách mà mã buộc phải chọn: mô tả PR hoặc thân commit ghi lựa chọn và lý do | Ca biên (ngày nghỉ, rỗng, âm, trùng, vượt cỡ) mà đặc tả không nói tới | đã ghi ở mô tả PR hoặc thân commit (cổng chạy khi CHƯA có PR) → ❓ kèm một câu đề xuất bổ sung đặc tả · chọn im lặng → 🟠 (DT1) |

Muốn khác đặc tả thì sửa ĐẶC TẢ trước (commit cùng nhánh, người duyệt đặc tả duyệt lại), rồi mã theo — không
sửa im trong mã. Lần gặp: `references/pitfalls.md` § Lệch đặc tả.

**Xong** khi mỗi mục trong danh sách hoặc đã được đổi trong diff, hoặc đã được chỉ ra là không cần; và mỗi điều
của đặc tả mà diff chạm có câu trả lời khớp/lệch, mỗi nhánh mới trong mã truy được về một điều hoặc đã thành
phát hiện.

## B. Test — hàng **Test**

Chi tiết cách viết ở skill `comitor-test`; ở đây là câu hỏi cho người review.

| # | Kiểm | Cách thấy | Mức |
|---|---|---|---|
| E1 | Hàm lõi mới/đổi có `*.test.ts` cạnh nó: ca thường · biên · hỏng · (đối chứng, khi có cách "hiển nhiên" mà sai) | Hàm export mới trong `lib/core/` không có test gọi nó | 🟠 |
| E2 | Test có thể ĐỎ: import đúng đơn vị (không chép lại logic), tự sở hữu state, không `vi.mock` module, không mock Prisma, không HTTP thật, thời gian/múi giờ là THAM SỐ | Test mới: xoá dòng thân hàm được test trong đầu — test có đỏ không? | 🟠 |
| E3 | Test của KHUNG không ghim danh sách mà module mở rộng (mã quyền, mục điều hướng) — dùng `arrayContaining` hoặc dựng dữ liệu từ chính lược đồ | `toEqual([...])` trên danh sách khung | 🟡 |
| E4 | Store mới/đổi có test với API TIÊM vào: đang bay, lưu chồng, lỗi giữa chừng, phản hồi cũ về muộn sau khi đổi ngữ cảnh | `stores/**` đổi mà `*.test.ts` không đổi | 🟠 |
| E5 | Route mà API giả bắt chước đổi → handler giả + `lib/api-client/fake/router.test.ts` đổi CÙNG lúc; đường chưa làm trả 501 `FAKE_NOT_IMPLEMENTED`, không trả một fixture cố định | Route đổi, router giả không đổi | 🟠 |
| E6 | Màn mới cần e2e chạy được ở chế độ giả (vỏ client + `FAKE_SUPPORTED` + `refreshKey`); bài Playwright chọn phần tử theo VAI TRÒ + TÊN lấy từ `t()`, không `waitForTimeout` chờ dữ liệu, có ít nhất một bài cho nhánh hỏng | `tests/e2e/**` mới | 🟡 |
| E7 | Sửa lỗi kèm một test ĐỎ trên mã cũ; thân commit hay mô tả PR nói "bỏ bản sửa thì đỏ: <tên test>" | `fix:` không kèm test | 🟡 · không chứng minh được thì ❓ |
| E8 | Không hack mã app (state thừa, hook chỉ để test chờ được) để phục vụ e2e | Thuộc tính/trạng thái mới chỉ test đọc | 🟡 |

**Xong** khi mỗi hàm lõi, store, route có bản giả và bài e2e thêm/đổi có câu trả lời của ô tương ứng.

## C. Hợp đồng — hàng **Hợp đồng**

| # | Kiểm | Cách thấy | Mức |
|---|---|---|---|
| H1 | Đổi hình dạng phản hồi thì `lib/contracts/`, phương thức `lib/api-client/`, handler giả và mọi nơi tiêu thụ đổi CÙNG lúc | Trường đổi tên/xoá trong kiểu hay trong `apiOk(…)` | nơi tiêu thụ gãy 🔴 · còn lại 🟠 |
| H2 | Mã lỗi mới: ném `ApiError` có `code` tiếng Anh viết HOA; có ở `errors.code.*` cả hai ngôn ngữ | Mã mới không có khoá | 🟠 |
| H3 | Đường dẫn URL là API công khai — Account chuyển hướng tới, email và deep link mang nó: đổi/xoá route cần chuyển hướng hoặc mục CHANGELOG | `page.tsx` bị dời/xoá | 🟠 |
| H4 | Giá trị union/enum đã lưu database hoặc đã đi qua JSON không đổi tên mà không có migration dữ liệu | Đổi chữ của một giá trị trạng thái | 🔴 |
| H5 | Endpoint trả HTTP 200 cho thất bại nghiệp vụ (`failed[]`, `code` trong thân) thì nơi gọi ĐỌC phần đó — `if (!res.ok) throw` hiểu sai nó | Nơi gọi mới của endpoint kiểu đó | 🟠 |
| H6 | Hợp đồng liên module giữ nguyên: tên header `x-request-id`, chuỗi log viết HOA, `?w={slug}`, đường webhook, hợp đồng `@comitor/account-sdk` | Đổi bất kỳ thứ nào trong số đó | 🔴 |
| H7 | `data-testid` của `/dev/fixtures` và page object ở `tests/e2e/pages/**` khớp nhau; `data-testid` chỉ ở bàn điều khiển giả | `data-testid` mới trong giao diện sản phẩm; testid bị đổi | 🟡 |

**Xong** khi mọi export đổi tên/đổi hình dạng có nơi tiêu thụ trong diff, và mọi mã lỗi, route, giá trị
union mới/đổi có câu trả lời H2–H4.

## D. Trạng thái — hàng **Trạng thái**

| # | Kiểm | Cách thấy | Mức |
|---|---|---|---|
| D1 | Đủ bốn trạng thái: đang tải · rỗng · lỗi · có dữ liệu — và HAI câu rỗng: "chưa có gì" khác "lọc không ra kết quả" (KT § 7) | Màn mới thiếu nhánh lỗi, hay dùng chung một câu rỗng | thiếu lỗi 🟠 · còn lại 🟡 |
| D2 | "id tra không ra tên" là trạng thái THỨ BA (`common.formerMember`), không gộp vào "chưa giao" — gộp là in lời mời nhận một việc đã có chủ | `name ?? t("unassigned")` trên kết quả tra danh bạ | 🟠 |
| D3 | Tính năng chưa nối thì đánh dấu `<NotYetActive />` — một cài đặt không làm gì tệ hơn một cài đặt còn thiếu | Trường cài đặt mới không có gì đọc | 🟠 |
| D4 | 375px và chuỗi `en` dài hơn: không bề rộng cố định gây tràn, nút không vỡ khi chữ dài | `w-[NNNpx]`, `min-w-*` lớn, `whitespace-nowrap` trên chữ dịch | 🟡 *(đề xuất — không thấy được bằng mắt trên diff thì hỏi ❓ đã đi 375px chưa)* |
| D5 | Phím tắt riêng của trang gợi ý ngay tại chỗ; không trùng ⌘K / ⌘⇧K / ⌘B của `AppShell` | Phím mới | ⚪ |

**Xong** khi mỗi màn hình hay thành phần nạp dữ liệu mới có câu trả lời D1–D3.

## E. Tối giản — hàng **Tối giản**

Tiêu chuẩn: mã ít nhất giải được bài toán, chỉ chạm thứ yêu cầu cần.

- **Dùng lại** — viết lại logic mà một hàm lõi, hook hay component của gói đã có.
- **Đơn giản hoá** — trừu tượng có một nơi gọi; tuỳ chọn không ai đặt; bọc chung quanh một ca cụ thể; một
  store hay hook nơi một prop là đủ (store không thoả điều kiện nào là T4 của hàng **Tầng**). Xử lý lỗi cho
  trạng thái không xảy ra: trước khi chấp nhận một `try/catch`, timeout hay `null` guard quanh một lời gọi,
  đọc hàm được gọi và trích hợp đồng của nó — guard cho một thứ được ghi là không ném là phát hiện. 200
  dòng mà 50 là đủ thì nói 50 dòng nào.
- **Hiệu năng hiển nhiên** — tính lại trong render thứ tính một lần là đủ; effect nơi state suy ra là đủ;
  truy vấn trong vòng lặp (N+1) nơi một `findMany` + `in` là đủ.
- **Độ cao** — mã giải bài toán tổng quát hơn bài được yêu cầu.
- **Mã chết** — class, khoá chuỗi, module, prop mà diff thêm vào và không gì đọc.
- **Trung gian** — hook, wrapper hay module chỉ chuyển tiếp một hàm khác, không thêm gì → gọi thẳng.

Mức 🟡. Sửa được ở bước 4 theo luật của SKILL.md § 4 — chỉ khi lời gọi mang cờ `--fix`; không có cờ thì
chỉ báo cáo.

## F. Tài liệu & phát hành — hàng **Tài liệu**

| # | Kiểm | Cách thấy | Mức |
|---|---|---|---|
| F1 | ⟨hồ sơ: **Số bản**⟩ Mỗi PR (mỗi lô vào `main`) tăng `version` MỘT lần và có MỘT mục CHANGELOG cùng số (`version:check` so với gốc nhánh) — commit sau trong cùng nhánh sửa mục đó, không thêm mục mới; PR chỉ-tài-liệu (mọi file trong `paths-ignore` của deploy) được miễn tăng, ghi chú vào mục đang có; đổi FILE KHUNG thì mục đó có phần "Module đã sinh ra phải làm gì" | Diff đụng file khung (CT § Thay đổi chạm FILE KHUNG) mà CHANGELOG không nói module phải làm gì | 🟠 |
| F2 | File khung không bị format lại — chỉ những dòng cần đổi | Hunk chỉ đổi khoảng trắng/thứ tự trên file khung | 🟠 |
| F3 | Tài liệu `.md` (README bản đồ route, AGENTS.md, CLAUDE.md, `docs/`, skill) khớp mã và khớp NHAU: tên file, route, lệnh, số đếm; lệnh tự kiểm trong tài liệu chạy ra đúng điều nó hứa ("phải RỖNG" thì chạy trên cây sạch phải rỗng); không ghi trạng thái hiện hành ("hôm nay chưa…") như một luật. Comment trong mã là hàng **Comment** | Grep tên cũ trong `*.md`; chạy thử lệnh tự kiểm mới | 🟡 (🟠 khi tài liệu chỉ dẫn làm sai) |
| F4 | Ở MODULE: không sửa bản chép của skill `comitor-*` — sửa ở `comitor-starter` rồi chép lại (trừ commit chính là lần chép nguyên thư mục) | `.claude/skills/comitor-*/**` đổi ở repo không phải starter | 🟡 |
| F5 | Ở STARTER: sửa khuôn `comitor-page` hay file khung mà khuôn vá vào → `verify.mjs` đã chạy (thân commit ghi kết quả); sửa một skill → script kiểm của skill đó xanh (`check-refs.mjs`, `verify-skill.mjs`, `audit.mjs`) | Thân commit không nhắc | ❓ |
| F6 | Mục "Cạm bẫy" của AGENTS.md soát lại khi nâng MINOR/MAJOR `@comitor/ui` | `package.json` đổi bản gói | 🟡 |
| F7 | Khuôn commit `type(scope): mô tả tiếng Việt`; thân trả lời VÌ SAO, ghi con số khi dựa trên phép đo (CT § Khuôn commit) | `git log <gốc>..HEAD --format=%B` | ⚪ |

**Xong** khi mỗi file khung đổi có câu trả lời F1–F2, mỗi tên/route/lệnh đổi đã grep trong tài liệu (F3),
và mỗi file skill đổi có câu trả lời F4–F5.
