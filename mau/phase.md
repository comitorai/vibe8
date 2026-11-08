# Phase <MÃ>-<số>: <tên>

**Xong khi:** <một câu> · **Hạn:** <ngày> · **Cổng 2:** <ngày, lựa chọn của chủ dự án>
**Điều phối:** <id phiên hiện hành> · **Vỏ:** <nhóm thanh bên của luồng> · **Ngân sách:** <token>, đã dùng <token>
**Trạng thái:** Chưa bắt đầu · Đang làm · Hoàn thành · Đã huỷ · **Phạm vi lúc mở Cổng 2:** <số task> · **Cập nhật:** issue #<số>, nhãn `phase`

Sức khoẻ, tuổi, %, dự báo không ghi tay vào sổ: máy tính từ sổ này, GitHub và comment ba mốc trên issue cập nhật (`luat/hien-thi-tien-do.md` mục 3, 4).

## Sổ giữ chỗ (chỉ Điều phối ghi)

| Task | Yêu cầu | Tệp/thư mục giữ | Máy | Phiên | Nhánh | Model | Mức | Trạng thái | Cờ | PR | Ghi chú |
|---|---|---|---|---|---|---|---|---|---|---|---|
| T1 | YC-1 | `src/a/` | chính | <id làn> | `t1-…` | <theo L12> | Thường | Chưa bắt đầu · Đang làm · Hoàn thành · Đã huỷ | Chờ duyệt · Chờ bạn · Chờ CI · Bị chặn · trống | — | |

Trạng thái và cờ lấy từ GitHub và CI, không từ lời tự báo của làn. Một trạng thái một tên (`luat/hien-thi-tien-do.md` mục 2): PR chờ người duyệt là Đang làm kèm cờ Chờ duyệt; task đã tách thì task gốc là Đã huỷ, Ghi chú `tách → Tx.a, Tx.b`. Cột Phiên: id phiên làn đang giữ task (`luat/vai/dieu-phoi.md` §5); thay làn thì ghi id mới.
Tệp dùng chung (lockfile, migration, cấu hình gốc) mỗi lúc chỉ một dòng được giữ.

## Tiêu chí từng task

### T1
- [ ] <tiêu chí kiểm được>
- **Hợp đồng giao diện:** <tên hàm, API, màn>

## Cổng 3

**Demo:** <link> · **Từng tiêu chí phase:** đạt / chưa
**Chủ dự án chọn:** đạt · sửa (vòng <1|2>) · bỏ
