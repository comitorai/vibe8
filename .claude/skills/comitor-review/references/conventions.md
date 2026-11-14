# Quy ước — năm hàng

**Phạm vi:** mọi file mã (`.ts`, `.tsx`, `.css`, `.mjs`, khuôn `.tpl`) và `messages/*.json`. Không có → cả
nhóm n/a. ⚠ Hàng **Comment** chỉ phủ comment TRONG MÃ; tài liệu `.md` lệch mã là hàng **Tài liệu**
(`quality.md` F3) — một phát hiện, một hàng, không ghi cả hai.

Nguồn luật: `AGENTS.md` (AG) § Quy ước bắt buộc giữ, § Cạm bẫy › Đa ngôn ngữ, › `@comitor/ui`;
`docs/kien-truc-ung-dung.md` (KT) § 5; skill `comitor-ui` (bảng "Cần gì → dùng gì", `references/pitfalls.md`).

## A. Đa ngôn ngữ — hàng **i18n**

`t()` KHÔNG ném lỗi: khoá thiếu, khoá chứa dấu chấm, tham số ICU lệch đều trả về chính tên khoá, `pnpm
build` vẫn xanh, và cái sót chỉ hiện với người dùng đúng ngôn ngữ đó. `pnpm i18n:check` bắt phần đối chiếu
được; review bắt phần còn lại.

| # | Kiểm | Cách thấy | Mức |
|---|---|---|---|
| N1 | Không chuỗi người dùng đọc ngoài `messages/` — kể cả `aria-label`, `title`, `placeholder`, `alt`, `metadata`, toast, chuỗi trong `lib/catalog/**` | Chuỗi chữ trong JSX hay trong thuộc tính trên dòng thêm. Ngoại lệ DUY NHẤT: `global-error.tsx`, nếu có ngày phải viết (nó thay cả `<html>`, không provider nào) | 🟠 |
| N2 | Câu dịch đúng nghĩa và đúng giọng ở CẢ HAI ngôn ngữ — đọc giá trị `en` lẫn `vi` bạn thấy thêm | `i18n:check` chỉ so KHOÁ, không so NGHĨA: bản `en` chép nguyên tiếng Việt, hay ngược lại, đi qua | 🟡 |
| N3 | Khoá ĐỘNG (mã lỗi, mã quyền, trạng thái) đi qua `t.has()` và có câu dự phòng; khoá không chứa dấu chấm (mã quyền `activity.view` đổi qua `toPermissionMessageKey()`) | ``t(`errors.code.${code}`)`` không `t.has` | 🟠 |
| N4 | Không ghép câu: dấu câu hay chuỗi nối vào kết quả `t()`; số, đơn vị, số nhiều đi qua ICU | `{t("x")}.`, `t("a") + " " + t("b")`, `` `${n} ${t("items")}` `` | 🟠 |
| N5 | `messages/` không có markdown (`**đậm**`, backtick, `[chữ](url)`) — dùng thẻ ICU + `t.rich`; `t.rich` đặt trong flex container thì bọc MỘT `<span>` | Giá trị mới trong `messages/`; `t.rich` là con trực tiếp của `flex` | 🟡 |
| N6 | Chuỗi CHUNG của `@comitor/ui` ("Huỷ", "Xoá lựa chọn", phân trang) để `ComitorLocaleProvider` lo; prop nhãn chỉ khi nói theo NGHIỆP VỤ ("Xoá vĩnh viễn", "Tìm thành viên…") | `cancelLabel={t("common.cancel")}` — một bản dịch thứ hai sẽ lệch âm thầm khi gói sửa chữ | 🟡 |
| N7 | Ngày giờ: `format.dateTime(d, { dateStyle: "long" })` (đối tượng tuỳ chọn, không TÊN định dạng); `<RelativeTime>` có `timeZone`, không có `locale=` | `format.dateTime(d, "long")`; `<RelativeTime` thiếu `timeZone` (`i18n:check` § 8 bắt một phần) | 🟠 |
| N8 | JSX in đúng kết quả `t()` | `<>t("x")</>` thiếu cặp `{}` in NGUYÊN VĂN `t("x")` — `i18n:check` bắt dạng sau thẻ; review bắt dạng khác (sau chữ, trong ternary) | 🟠 |

**Xong** khi mọi chuỗi chữ trên dòng thêm của `.tsx`/`lib/catalog/**` đã được xếp loại (người đọc → phải
qua `t()`; máy đọc → được), và mọi khoá `messages/` mới đã đọc ở cả hai ngôn ngữ.

## B. Màu & `@comitor/ui` — hàng **Màu & UI**

| # | Kiểm | Cách thấy | Mức |
|---|---|---|---|
| U1 | App KHÔNG sở hữu màu: không hex/`rgb(`/`hsl(`/`oklch(`, không class tuỳ ý `bg-[#…]`, không `style={{ color }}`, không khai token màu; `app/globals.css` đúng HAI dòng `@import` | `color:check` bắt hex; review bắt phần còn lại | 🟠 |
| U2 | Vai trò màu đúng: chữ lên nền trang là `-ink`, chữ lên nền màu là `-foreground`, viền ô nhập là `border-input`; icon không tô màu có alpha (`text-x/NN` cạnh `size-*`) — dùng bậc đặc hoặc `opacity-*` | Lệnh grep icon-alpha ở AG § Cạm bẫy › `@comitor/ui`. Chọn sai vai trò không có gì báo đỏ | 🟡 |
| U3 | Dùng component của gói trước khi tự dựng — nút, thẻ, badge, ô nhập, bảng, hộp thoại, `StatusPill`, `EmptyState`, `PageHeader`, `FormField`, `DataTable`/`DataGrid`, `ConfirmDialog`, `ActionBar` | `<button`, `<input`, `<select`, `<table`, `div` mang `rounded`+`border`+`shadow`, lớp phủ tự viết (`role="dialog"`, nền mờ `fixed`). Đối chiếu bảng "Cần gì → dùng gì" của `comitor-ui` trước khi kết luận gói thiếu — thiếu thật thì sửa ở GÓI | 🟠 |
| U4 | Không chép mã component từ `node_modules/@comitor/ui`; không thư viện UI thứ hai; không `react-hook-form` khi chưa thật cần | File mới giống hệt mã gói; phụ thuộc UI mới | 🟠 |
| U5 | Cạm bẫy gói đã đo (AG § Cạm bẫy › `@comitor/ui`): icon trong `Button` đi qua `leftIcon` hoặc, khi gói dưới 3.13.0, mang `size-4` (`size-3.5` cho `size="sm"`) — từ 3.13.0 gói tự cỡ icon chưa có `size-*`, nên thiếu `size-4` không còn là phát hiện; `ConfirmDialog` không lồng trong `DropdownMenuItem`; hộp thoại dài bọc `DialogBody`; lưới đáp ứng có `grid-cols-1` ở bậc cơ sở; icon trong flex có `shrink-0`; `Combobox` đặt bề rộng bằng THẺ BỌC; nội dung portal dùng màu app thì gán lại `appAccentStyle`; `<SonnerToaster />` ngoài `<AppShell>` | Đọc JSX mới theo danh sách | 🟡 |
| U6 | `audit.mjs` của `comitor-ui` không có ERROR mới rơi vào dòng diff | `node .claude/skills/comitor-ui/scripts/audit.mjs` | 🟠 |
| U7 | Trợ năng: control có tên trợ năng; ô chỉ-icon mang `role="img"` + `aria-label` (tooltip KHÔNG phải tên); icon trang trí cạnh chữ mang `aria-hidden="true"`; không phần tử trơ trông như bấm được | Control và icon mới | 🟡 |

**Xong** khi mọi phần tử JSX tương tác mới và mọi container mới đã được đối chiếu với gói, và mọi class
màu mới đã được xếp vai trò.

## C. Ngôn ngữ & tên — hàng **Ngôn ngữ & tên**

| # | Kiểm | Cách thấy | Mức |
|---|---|---|---|
| L1 | MÁY nói tiếng Anh: biến, hàm, kiểu, trường dữ liệu, tên file/thư mục, **đường dẫn URL**, giá trị union/enum, `id`/`htmlFor` trong DOM, khoá JSON | Định danh tiếng Việt không dấu (`danhSach`, `trangThai`), route `/cai-dat`, union `"dang-xu-ly"` | URL/union 🟠 · còn lại 🟡 |
| L2 | NGƯỜI đọc tiếng Việt: comment và tài liệu viết tiếng Việt | Comment tiếng Anh mới trong mã của app (trừ chỗ chép nguyên văn thông điệp lỗi của công cụ) | ⚪ |
| L3 | Tên file kebab-case; component và kiểu PascalCase; hàm, biến camelCase; hook tên `use*` trong `hooks/use-*.ts` | File `A` (thêm mới) trong danh sách | 🟡 |
| L4 | **Chỉ nói về Comitor** (AG § Quy ước): không tên các dự án, thương hiệu, đối tác KHÁC mà đội làm cùng — tên sản phẩm, scope gói, tên mã nội bộ — trong mã, comment, tài liệu, dữ liệu mẫu; bài học từ đó giữ, tên bỏ, nguồn nói theo loại. KHÔNG chặn: phụ thuộc CÓ THẬT (Next, React, Prisma, Radix, Tailwind, Biome, Uppy…); tên doanh nghiệp, tên miền là DỮ LIỆU của tính năng nói về chính website hay doanh nghiệp đó (site tham chiếu, bộ chuẩn site để đo, khảo sát ngành, site thử của công cụ quét); hồ sơ review của repo khác; ngoại lệ repo tự khai (`profiles/module.md` § Ngoại lệ khai trong repo) | Một tên riêng mới trên dòng thêm KHÔNG tự nó là phát hiện. Hỏi: đây là tên một dự án hay đối tác khác của đội — thường đi cùng mã chép sang, comment "lấy từ…", scope gói lạ, tên mã nội bộ — hay dữ liệu của tính năng? Chỉ cái trước là L4 | 🟡 |
| L5 | Một khái niệm một tên trong diff | Cùng thứ gọi hai cách | ⚪ |

**Xong** khi mọi file thêm mới và mọi định danh export mới đã có câu trả lời L1/L3, và mọi tên riêng mới
đã có câu trả lời L4: tên đối tác/dự án khác (phát hiện), hay dữ liệu, phụ thuộc, ngoại lệ đã khai (không).

## D. Comment — hàng **Comment**

Repo này viết comment DÀI có chủ ý — đầu file `check.yml`, `scripts/check-version.ts` là ví dụ — và chúng
trả lời VÌ SAO, thường kèm phép đo. Viết khớp mật độ ấy; đừng ép một trần số dòng. Cái bị bắt là comment
VÔ ÍCH hoặc SAI, không phải comment dài.

| # | Kiểm | Cách thấy | Mức |
|---|---|---|---|
| C1 | Comment trả lời VÌ SAO (lý do, phép đo, cạm bẫy), không kể lại mã | Comment nhắc lại tên hàm hay dòng ngay dưới nó | 🟡 · sửa được ở bước 4 khi có `--fix` |
| C2 | Comment nói ĐÚNG mã: tên file, hàm, route, lệnh, và đúng với chính hàm bên dưới (đầu file cấm một cách làm mà hàm mới dùng → ghi ngoại lệ ngay ở đó); không ghim con số đếm tay khi đếm được bằng lệnh ("ba ngoại lệ") | Đối chiếu tên và khẳng định trong comment mới với mã | 🟡 (🟠 khi nó chỉ dẫn làm sai) |
| C3 | Một cơ chế giải thích ở MỘT chỗ trong mã; chỗ khác trỏ sang — hai bản của cùng một quy tắc thì bản sai là bản người khác đang đọc | Cùng lời giải thích ở hai file mã trong diff | 🟡 |
| C4 | `biome-ignore` mang lý do thật, không "tạm thời" | Dòng thêm | 🟡 |
| C5 | Đính chính giữ dấu vết khi sửa một khẳng định sai đã công bố ("⚠ Bản trước ghi … SAI vì …") — đó là khuôn của repo, không phải rác | Comment bị sửa ngược mà xoá sạch dấu vết của khẳng định cũ, trong khi module có thể đang làm theo nó (ở `.md` thì ghi dưới F3) | ⚪ |

**Xong** khi mọi comment và đoạn tài liệu thêm vào đã được xếp: lý do · kể lại mã · sai · trùng.

## E. Kiểu — hàng **Kiểu**

| # | Kiểm | Cách thấy | Mức |
|---|---|---|---|
| K1 | Không `any`, `as` không có căn cứ, `!` non-null, `@ts-ignore`/`@ts-expect-error` để né lỗi thật | Dòng thêm (Biome chỉ bắt `any`) | 🟡 (🟠 khi nó giấu lỗi thật) |
| K2 | `noUncheckedIndexedAccess`: nhánh `undefined` được XỬ LÝ, không bị `!`/`as` dập — nó vừa tìm ra một ca biên | `arr[i]!`, `obj[k] as T` | 🟡 |
| K3 | Spread có điều kiện `...(c ? { x } : {})` LỌT phép kiểm thuộc tính thừa: đọc lại chữ ký hàm bằng mắt | Mỗi spread có điều kiện mới: tên khoá có trong kiểu tham số không | 🟠 khi tên sai |
| K4 | Không nới công cụ để cho qua: tắt luật lint, hạ `strict`, gỡ `import "server-only"`, sửa `biome.json` cho vừa một file | `biome.json`, `tsconfig.json` đổi | 🟠 |
| K5 | Kiểu đi qua JSON khai ở `lib/contracts/`, không khai lại ở client; phản hồi đọc qua phương thức cổng có kiểu, không `request<T>(path)` chung | Kiểu trùng tên ở hai chỗ | 🟡 |

**Xong** khi mọi `as`, `!`, `any`, `ignore`, spread có điều kiện và đổi cấu hình công cụ trên dòng thêm đã
có câu trả lời.
