# Bảo mật: đã kiểm gì, chưa kiểm gì

## Đã kiểm, chỉ ở mức cục bộ

Bằng unittest và `nghiem-thu/kiem_cuc_bo.py`, dữ liệu mô phỏng, trên Python 3.9 và mới hơn:

- Logic quyết định: SHA lệch, đổi base, tự duyệt, bot, người ngoài danh sách, yêu cầu sửa bị gỡ, thân PR chèn lệnh, tên tệp lạ, xoá test.
- `gate_app`: phát đúng một check, head đổi giữa chừng, hỏng API, không đi theo chuyển hướng, che token, chỉ `success` hoặc `failure`.
- Workflow: qua actionlint và zizmor. **Chưa chạy lần nào trên GitHub.**

## Chưa kiểm: cần GitHub thật

- Mọi hành vi của Actions, GitHub App, environment, branch protection, gồm cả `bat_cong.py` khi chạy thật.
- L3-L6 thực sự bị chặn. Bài cục bộ không chứng minh được những lỗi này.
- `pull_request_target` và `workflow_run` có qua được environment `gate` chỉ cho nhánh `main` không.
- `head_sha` của lượt `workflow_run` có đúng là head của PR không, và GitHub chọn check mới nhất của App trên SHA thế nào.
- Quyền Actions read, Checks write và Pull requests read của App có đủ không.
- Request bảo vệ nhánh chỉ có `checks`, không có `contexts`, có được nhận không.

## Giới hạn đã biết

1. **Cổng chống đi tắt, không chống cộng tác viên cố ý ác.** Trên repo cá nhân, cộng tác viên có quyền ghi và xoá được lượt
   CI đỏ. Xoá lượt đỏ của base lạ rồi đổi base có thể thành giả xanh. Repo cá nhân cũng không có danh sách giới hạn người push.
2. **PR rủi ro thấp tự merge, không có người đọc.** Đây là chính sách, người dùng quyết. Trung bình cũng được đối xử như thấp về
   điều kiện qua. Muốn mọi PR phải có người duyệt thì phải đổi `kiem_pr.py`.
3. **Khoảng hở nhỏ giữa yêu cầu sửa và lượt xét mới.** Check cũ còn `success` cho tới khi `tin-hieu-duyet` và `cong-cuoi` chạy xong.
4. **`tin-hieu-duyet` chạy theo bản của PR.** PR xoá tệp đó thì lượt duyệt không đánh thức cổng. Đổi `.github/` đã là rủi ro cao
   nên `cong-cuoi` đã chặn; `check` cũ ở lại là `failure`, không mở cổng.
5. **Repo private gói Free không có cổng.** Không đặt được required check.
6. **Admin có thể vượt environment.** API environment không có tham số cấm. `enforce_admins` chỉ áp cho nhánh.
7. **Force push A, B, rồi về A** có thể làm lượt duyệt cũ trên A còn tính. Nội dung vẫn đúng là thứ đã duyệt.
8. **Symlink và đổi quyền tệp** không thấy qua API files, chỉ được xếp trung bình.
9. **Cổng không chứng minh phần mềm đúng.** Sửa logic cùng sửa test theo hướng thêm, hay chèn `sys.exit(0)` vào mã, không bị rủi ro cao bắt được.
10. **Agent lỡ dùng email của người duyệt để commit** thì người đó thành «tự duyệt». Cổng đóng và ghi lý do, không mở sai.

## Vì sao dùng hai sự kiện đặc quyền

zizmor báo `dangerous-triggers` ở `pull_request_target` và `workflow_run`. Chấp nhận vì `cong-cuoi` không checkout mã PR,
không đưa dữ liệu PR vào `run:`, chỉ dùng số PR và SHA đã kiểm dạng. Không dùng `pull_request_review` trực tiếp: sự kiện đó
xét environment theo `refs/pull/N/merge`, muốn chạy được phải nới `gate`, mà nới thì workflow của PR lấy được khoá App.

## Nguyên tắc giữ

- Không checkout, không chạy mã PR trong `cong-cuoi`. Không đưa dữ liệu PR vào `run:`.
- Khoá App chỉ nằm trong environment. Token không in, không đi qua chuyển hướng.
- Check run do App phát, required check có expected source là App, để job của PR không giả tên được.
- Sự kiện chỉ đánh thức cổng. Quyết định chỉ lấy từ API, kể cả kết quả CI.
- Mọi đường hỏng đều không phát `success`.
