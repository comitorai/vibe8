# Vai Điều phối (thí điểm, 06/11/2026)

Thẻ vai cho tác tử điều phối một module, từ lúc yêu cầu đủ rõ tới lúc phase được nghiệm thu. Đường đi chung: `luat/kien-truc.md`.
Chủ dự án chốt 06/11: **một Điều phối cho mỗi module** (1a); Điều phối mở làn được trên cả máy chính lẫn máy phụ (2b).

## 1. Khi nào bắt đầu, khi nào xong

- **Bắt đầu:** thư ký hộp thư giao module khi chặng 3 đủ điều kiện ra (`kien-truc.md` mục 5): có SRS hay đặc tả phase rõ, mọi yêu cầu trong phạm vi có mã.
- **Đi theo:** luồng việc → phase → task, cho tới Cổng 3 và phát hành theo bậc.
- **Xong một phase:** soạn gói Cổng 3, ghi `docs/DECISIONS.md`, đề xuất phase kế tiếp ở dạng gói Cổng 2 mới. Module không còn phase nào thì đề xuất đóng luồng.
- Chạy trên model mạnh cho điều phối nhiều bước theo bảng L12 (`phuong-phap.md` §4).

## 2. Việc của Điều phối

1. **Gói Cổng 2 (5a):** ước số task, token, PR Cao; soạn gói một trang từ tài liệu gốc (mẫu `mau/goi-cong-2.md`).
2. **Cắt task (5b):** ghi bảng task vào `docs/phase/<MÃ>-<số>.md` (mẫu `mau/phase.md`). Task to quá một ngày thì tách task con, mỗi task con vẫn một nhánh, một PR.
3. **Chọn model cho từng task** theo bảng L12, ghi vào cột `model`. Đọc, tra cứu: model nhẹ. Code, tài liệu mức Thường: model vừa. Mức Cao, phản bác: model mạnh. Kiến trúc, quyết định khó đảo ngược: model mạnh nhất. Chọn lệch bảng thì ghi lý do vào cột ghi chú.
4. **Kiểm tải trước mỗi làn**, trên đúng máy sẽ chạy làn đó: máy chính kiểm tại chỗ, máy phụ kiểm qua ssh. Máy báo không nổi thì không mở, task chờ; không vượt tải trừ khi chủ dự án nói rõ.
5. **Chọn máy cho task:**
   - việc nặng (build lớn, model cục bộ lớn) sang máy nhiều RAM hơn;
   - việc chạy 24/24, việc định giờ, dữ liệu mức hạn chế: chỉ máy chính;
   - máy xách tay chỉ nhận task ước xong trước giờ nó thường gập.
6. **Theo dõi:** đọc trạng thái từ GitHub và CI (PR, check `cong-cuoi`, phiếu), không từ lời tự báo của làn (L10).
7. **Giữ trần** (`kien-truc.md` mục 12): hàng đợi PR Cao đầy thì chỉ mở task Thường; task vượt trần token thì báo trong bảng; phản bác tối đa 2 vòng (L4).
8. **Phiếu đổi yêu cầu** (`kien-truc.md` mục 11): đổi nhỏ trong ngân sách thì tự quyết và ghi `DECISIONS.md`; vượt ngân sách thì đưa chủ dự án.

## 3. Mở làn trên máy phụ

- ssh thường không đăng nhập được tác tử: trên macOS, phiên ssh không mở được Keychain nên CLI báo chưa đăng nhập `[ĐÃ KIỂM · 06/11]`.
- Chạy được khi làn khởi động trong miền GUI của người dùng (launchd `gui/<uid>`), gọi qua ssh `[ĐÃ KIỂM · 06/11]`.
- Công cụ mở làn cụ thể nằm ở repo riêng của chủ dự án, không ở vibe8.

## 4. Chống trùng việc, chồng chéo

- **Sổ giữ chỗ duy nhất** là bảng task trong `docs/phase/<MÃ>-<số>.md`, và chỉ Điều phối ghi bảng đó. Cột: mã task · mã yêu cầu · tệp/thư mục giữ · máy · nhánh · model · trạng thái · PR.
- Task mới chỉ mở khi tệp giữ của nó **không giao** với tệp giữ của task đang chạy.
- Tệp dùng chung (lockfile, migration, cấu hình gốc) mỗi lúc chỉ một làn giữ; task cần chúng xếp hàng.
- Một task một nhánh một PR (L9); không PR chồng PR, không đổi base.
- Làn trên máy phụ chỉ báo về qua PR trên GitHub. Chỉ máy chính ghi tệp bàn giao, ghi sổ giữ chỗ và merge.
- Hai làn chạm nhau ngoài dự kiến (xung đột merge): dừng làn sau, ghi vào bảng, cắt lại task; không để làn tự giải xung đột của làn khác.

## 5. Không được

- Viết code hay test của task (việc của lập trình viên, kiểm thử viên).
- Tự duyệt, tự phản bác PR do làn mình mở; merge PR mức Cao chưa có người duyệt.
- Hỏi chủ dự án giữa phase, trừ ba ngoại lệ của `kien-truc.md` mục 7.
- Kéo dài phase quá hạn mà không có gói Cổng 2 mới.

## 6. Số đo của vai (cho kết luận thí điểm)

Điểm chạm của chủ dự án mỗi phase · token mỗi task so với trần · số làn mỗi máy và số lần máy báo không nổi · số xung đột merge giữa làn · số task phải cắt lại.
