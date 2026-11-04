# Bảo mật: đã kiểm gì, chưa kiểm gì

## Đã kiểm, chỉ ở mức cục bộ

Bằng unittest và `nghiem-thu/kiem_cuc_bo.py`, dữ liệu mô phỏng, trên Python 3.9 và mới hơn:

- Logic quyết định: SHA lệch, duyệt trước push cuối, tự duyệt, bot, người ngoài, thân PR chèn lệnh, tên tệp lạ, xoá test.
- `gate_app`: phát đúng một check, head đổi giữa chừng, hỏng API, không đi theo chuyển hướng, che token, chỉ `success` hoặc `failure`.
- Workflow: rà bằng chữ và parse YAML. **Không phải actionlint, và chưa chạy lần nào.**

## Chưa kiểm: cần GitHub thật

- Mọi hành vi của Actions, GitHub App, environment, branch protection, gồm cả `bat_cong.py` khi chạy thật.
- L3-L6 thực sự bị chặn. Bài cục bộ không chứng minh được những lỗi này.
- Giờ tạo check suite có đúng là giờ push cuối không.
- Quyền Checks write và Pull requests read của App có đủ không.
- Request bảo vệ nhánh chỉ có `checks`, không có `contexts`, có được nhận không.

## Giới hạn đã biết

1. **Lượt duyệt chưa tự cập nhật check.** Với `pull_request_review`, luật environment xét theo `refs/pull/N/merge`, nên job bị
   `gate` từ chối theo docs. Cổng vẫn đóng, người duyệt xong phải kích lại bằng cách sửa PR hoặc đóng mở lại.
   Không được nới `gate` ra `refs/pull/*/merge`: làm vậy thì workflow của PR lấy được khoá App. Cần quyết cách sửa.
2. **Cổng chờ CI bằng thăm dò**, tối đa 600 giây. Hết giờ thì phát `failure`, tốn phút runner với repo private.
3. **Repo private gói Free không có cổng.** Không đặt được required check.
4. **Admin có thể vượt environment.** API environment không có tham số cấm. `enforce_admins` chỉ áp cho nhánh.
5. **Force push A, B, rồi về A** có thể làm lượt duyệt cũ trên A còn tính. Nội dung vẫn đúng là thứ đã duyệt.
6. **Symlink và đổi quyền tệp** không thấy qua API files, chỉ được xếp trung bình.
7. **Cổng không chứng minh phần mềm đúng.** Sửa logic cùng sửa test theo hướng thêm, hay chèn `sys.exit(0)` vào mã, không bị rủi ro cao bắt được.
8. **Lockfile tính vào ngưỡng 400 dòng**, nên PR nâng phụ thuộc có thể cần ngoại lệ.

## Nguyên tắc giữ

- Không checkout, không chạy mã PR trong `cong-cuoi`. Không đưa dữ liệu PR vào `run:`.
- Khoá App chỉ nằm trong environment. Token không in, không đi qua chuyển hướng.
- Check run do App phát, required check có expected source là App, để job của PR không giả tên được.
- Mọi đường hỏng đều không phát `success`.
