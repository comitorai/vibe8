# Audit Điều phối và làn: vì sao Điều phối không biết làn bị kẹt

*09/11/2026 · phiên MB «🟠 MB · Tasks · Audit Điều phối kẹt · COM-24» · phạm vi: mọi phiên **trên MB** từ 06/11 đến 09/11. Phiên MN chưa audit: tool phiên chỉ thấy phiên của máy này, còn Bash ở phiên đó bị hook vibe8 chặn nên không ssh sang MN được.*

## 1. Kiểm kê

| Luồng | Điều phối | Làn | Tình trạng lúc audit |
|---|---|---|---|
| COM-24 · Tasks | `995a1093` «Chuẩn hiển thị» (tên không ghi Điều phối, không có vỏ 📂) | `a64f68b3` Hiển thị làn → PR #56 OPEN · `9b08a96c` Sửa phiếu 56 → PR #57 OPEN, phiếu **bác** (trạng thái lúc audit; ngày 09/11 cả #56 và #57 đã merge) | **Kẹt.** Lúc 00:18 Điều phối tin rằng «làn chưa sửa gì». Thực tế 00:26 làn đã mở #57 và bị bác. Không ai báo lại Điều phối. |
| COM-8 · Hành chính (lần 1) | `4ccaf04c` Google Play (phiên thường, không phải Điều phối) | `d130037b` Xác minh Google Play | Làn hỏi thẳng Alex chọn tệp; khi đóng bảo Alex «tự mở phiên mới, gõ làm tiếp» |
| COM-8 · Hành chính (lần 2) | `9b7b9279` Điều phối COM-8 (mở từ `de795232`, đã tách cây, có vỏ) | T1 `e5d52ce6`, T2 `d35d4fb8`, T3 `e51daf61`, T6 `c8640d73` | **Chạy tốt.** T1 tự nhắn Điều phối, Điều phối merge, nhắn lại T2/T3. Vướng duy nhất: T6 phải chờ Alex bấm thẻ. |

## 2. Nguyên nhân gốc (xếp theo mức hại)

### N1 · Làn mở làn, nên làn cháu nằm ngoài tầm Điều phối `[ĐÃ KIỂM: get_session · list_events · 09/11]`
- `9b08a96c` có `parentSessionId = a64f68b3` (một làn), không phải `995a1093` (Điều phối). Làn `a64f` đề xuất thẻ `task_f20d3f68`, Alex bấm, thế là sinh ra làn cháu.
- App chỉ gửi thông báo «hết lượt» cho **phiên cha trực tiếp**. Khi `9b08` xong lúc 00:26, thông báo đi tới `a64f` (đang nghỉ từ 23:23), không tới Điều phối.
- `dieu-phoi.md` §5 «Thay làn» đã cấm việc này, nhưng chỉ bằng chữ. Chưa có hàng rào nào chặn làn gọi `start_session`.

### N2 · Luật app nói ngược luật vibe8 về việc báo về `[ĐÃ KIỂM: search transcript · 09/11]`
- App dặn phiên con: chỉ `SendMessage` cho cha khi bị chặn, «never for progress or results».
- vibe8 §5 thì yêu cầu làn báo **mọi** phát sinh về Điều phối.
- Kết quả: cả hai làn COM-24 gửi **0** tin cho Điều phối. Làn COM-8 có nhắn (T1 → Điều phối), vì lời giao của Điều phối COM-8 ghi rõ việc báo về `[SUY LUẬN từ nội dung tin T1]`.

### N3 · Thông báo chỉ có khi làn **hết lượt**; kẹt giữa lượt thì Điều phối không biết gì `[ĐÃ KIỂM: ảnh chụp Alex 09/11]`
- Ảnh chụp: làn treo ở hộp «Cho phép một lần» cho lệnh commit. Lượt chưa xong thì app không gửi note.
- Làn còn hỏi thẳng Alex ở hộp cuối lượt, ví dụ `a64f` («duyệt merge #56 rồi nhắn phiên kia làm tiếp») và `d130037b` («anh tự mở phiên mới»). Như vậy làn đã vòng qua Điều phối, trái §5.

### N4 · Điều phối chỉ thức khi có tin; GitHub đổi trạng thái thì không ai đánh thức nó `[SUY LUẬN từ §2.6 + lịch sử 995a]`
- Không có nhịp kiểm định giờ, và PR không được gắn (`bind_pr`) vào phiên Điều phối.
- Hậu quả: phiếu bác, merge, CI đổi màu đều không đánh thức Điều phối.

### N5 · COM-24 dựng thiếu khung `[ĐÃ KIỂM: get_session · 09/11]`
- Ba phiên COM-24 đều có `cwd = ~`: không worktree, không vỏ `📂 COM-24`, Điều phối không mang chữ «Điều phối» trong tên.
- `9b08` dùng chung thư mục, rồi cắt PR #57 chồng lên #56, trái §4.
- Điều phối COM-8 lần 2 dựng đúng khung và gần như không kẹt.

### N6 · «Mở Agent điều phối» đẻ thêm một phiên `[ĐÃ KIỂM: list_events de795232 · 09/11]`
- Alex mở phiên «Agent điều phối CN8 Thiện Minh». Phiên đó lại `start_session` ra một Điều phối COM-8 riêng, nên thành hai phiên.
- Nguyên do: luật chỉ có cách Điều phối mở làn, chưa có câu nào nói Điều phối tự hình thành thế nào.
- **Alex chốt 09/11:** phiên Alex mở chính là Điều phối. Nó tự đổi tên, tự vào repo, tự vào vỏ, không đẻ phiên Điều phối khác.

### Phụ · Bash hỏng khi đổi thư mục phiên vào vibe8 `[ĐÃ KIỂM · 09/11]`
- Hook `.claude/settings.json` gọi `$CLAUDE_PROJECT_DIR/nghiem-thu/hook_ghi_token.py`. Sau `change_directory` biến này vẫn là `~`, nên mọi lệnh Bash bị chặn.

## 3. Đề xuất sửa (Alex chốt 09/11: sửa lần lượt, xong thì áp cho mọi module/phase/task đang chạy)

| # | Sửa | Chặn được |
|---|---|---|
| S6 | Hook vibe8 tự tìm gốc repo thay cho `$CLAUDE_PROJECT_DIR`. Làm trước để mở lại Bash. | phụ |
| S1 | Hàng rào `PreToolUse` cho `start_session` / `hand_off_to_session`: phiên làn gọi thì từ chối, và in ra «nhắn Điều phối <id>». | N1 |
| S2 | Mẫu lời giao làn: mỗi lần dừng (xong, chặn, chờ người, chờ quyền) → `SendMessage` tới id Điều phối trước khi hết lượt; luật này đè luật mặc định của app. | N2, N3 |
| S3 | Làn chạy chế độ quyền `auto` hoặc `acceptEdits`. | N3 |
| S4 | Điều phối tự hẹn giờ 20–30 phút để đối chiếu `list_sessions {linked}` + PR, và `bind_pr` mỗi PR của làn. | N4 |
| S5 | Cổng dựng khung trước làn đầu: cwd là repo, có vỏ, tên có «Điều phối», làn `use_worktree: true`. Thêm luật khởi tạo của N6. | N5, N6 |
