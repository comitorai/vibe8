# Phase <MÃ>-<số>: <tên>

**Xong khi:** <một câu> · **Hạn:** <ngày> · **Cổng 2:** <ngày, lựa chọn của chủ dự án>
**Điều phối:** <id phiên hiện hành> · **Vỏ:** <nhóm thanh bên của luồng> · **Ngân sách:** <token>, đã dùng <token>
**Trạng thái:** <Chưa bắt đầu | Đang làm | Hoàn thành | Đã huỷ> (Cổng 3 đạt → Hoàn thành, bỏ → Đã huỷ) · **Cập nhật:** issue #<số>, nhãn `phase`

Sức khoẻ, tuổi, %, phạm vi, dự báo không ghi tay vào sổ: máy tính từ sổ này, lịch sử git của nó, GitHub và comment ba mốc giờ trên issue cập nhật (`luat/hien-thi-tien-do.md` mục 3, 4).

## Sổ giữ chỗ (chỉ Điều phối ghi)

| Task | Mã | Cha | Yêu cầu | Tệp/thư mục giữ | Máy | Phiên | Nhánh | Model | Mức | Trạng thái | Chờ task | PR | Ghi chú |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T1 | <KHOÁ>-<số> | <KHOÁ>-<số> | YC-1 | `src/a/` | chính | <id làn> | `t1-…` | <theo L12> | Thường | <Chưa bắt đầu \| Đang làm \| Hoàn thành \| Đã huỷ> | <mã task phải merge trước, hay trống> | — | |

Trạng thái lấy từ GitHub và CI, không từ lời tự báo của làn; sổ lệch GitHub thì tin GitHub. Một trạng thái một tên (`luat/hien-thi-tien-do.md` mục 2): PR chờ phiếu hay người duyệt vẫn là Đang làm; cờ Chờ CI, Chờ phiếu, Chờ duyệt do máy tính từ PR, không ghi vào sổ. Đã huỷ phải có bằng chứng ở Ghi chú: task gốc đã tách ghi `tách → Tx.a, Tx.b`, task bị gộp ghi `gộp vào Ty`, task huỷ vì phiếu đổi yêu cầu ghi `doi-yc <tệp phiếu đổi yêu cầu>`; task thêm vì phiếu đổi yêu cầu cũng ghi như vậy, để máy đếm «phạm vi ±n». Cột Phiên: id phiên làn đang giữ task (`luat/vai/dieu-phoi.md` §5); thay làn thì ghi id mới.
Cột Task là số thứ tự trong phase (`T1`, `T2`…), dùng để nối với mục tiêu chí bên dưới. Cột Mã là mã việc dùng chung toàn dự án, cấp khi task bắt đầu làm:
một khoá dự án và **một dãy số cho mọi việc** (luồng, task, lỗi), không quay lại, không dùng lại; mã không mang nghĩa (phase, máy, mức là cột riêng);
máy cấp số có khoá tệp để hai phiên không lấy trùng. Cột Cha là mã luồng hay việc cha. Task chưa bắt đầu để Mã trống; mã đã cấp không đổi,
task chuyển sang dự án khác thì được mã mới và Ghi chú ghi `chuyển → <mã mới>`. Tên phiên làn mang cột Mã (`luat/vai/dieu-phoi.md` §5, thao tác Mở).
Tệp dùng chung (lockfile, migration, cấu hình gốc) mỗi lúc chỉ một dòng được giữ.

## Tiêu chí từng task

### T1
- [ ] <tiêu chí kiểm được>
- **Hợp đồng giao diện:** <tên hàm, API, màn>

## Cổng 3

**Demo:** <link> · **Từng tiêu chí phase:** đạt / chưa
**Chủ dự án chọn:** đạt · sửa (vòng <1|2>) · bỏ
