# Bảo mật: đã kiểm gì, chưa kiểm gì

## Đã kiểm, chỉ ở mức cục bộ

Bằng unittest và `nghiem-thu/kiem_cuc_bo.py`, dữ liệu mô phỏng. Bộ test đã chạy trên Python 3.9, 3.10, 3.12, 3.13, 3.14:

- Logic quyết định: SHA lệch, đổi base, tự duyệt, bot, người ngoài danh sách, yêu cầu sửa bị gỡ, thân PR chèn lệnh, tên tệp lạ, xoá test.
- `gate_app`: phát đúng một check trên đúng SHA sự kiện, head đổi giữa chừng, PR fork cùng SHA, hỏng API, không đi theo chuyển hướng,
  che token, chỉ `success` hoặc `failure`.
- Workflow: qua actionlint và zizmor. **Chưa chạy lần nào trên GitHub.**

## Chưa kiểm: cần GitHub thật

- Mọi hành vi của Actions, GitHub App, environment, branch protection, gồm cả `bat_cong.py` khi chạy thật.
- L3-L6 thực sự bị chặn. Bài cục bộ không chứng minh được những lỗi này.
- `pull_request_target` và `workflow_run` có qua được environment `gate` chỉ cho nhánh `main` không.
- `head_sha` của lượt `workflow_run` có đúng là head của PR không, và GitHub chọn check mới nhất của App trên SHA thế nào.
- Quyền Actions read, Checks write và Pull requests read của App có đủ không.
- Request bảo vệ nhánh chỉ có `checks`, không có `contexts`, có được nhận không, và `app_id` có thực thi không khi có hai check cùng tên.
- Environment `gate` có giữ được khoá trước nhánh tên `main-2`, `Main`, tag tên `main`, lượt `deployment` (tạo bằng `POST /deployments`
  với `required_contexts: []`) và `deployment_status` không. Phải thử bằng secret giả trước khi đặt khoá thật.
- Trường `head_repository` của lượt chạy có đúng như cách cổng dùng để lọc PR fork không.
- Environment có nhận cấm admin vượt không (`can_admins_bypass` chưa thấy trong tài liệu, giao diện có ô tương ứng).

## Giới hạn đã biết

1. **Cổng chống đi tắt, không chống cộng tác viên cố ý ác.** Trên repo cá nhân, cộng tác viên có quyền ghi và xoá được lượt
   CI đỏ. Xoá lượt đỏ của base lạ rồi đổi base có thể thành giả xanh. Cũng có khe thời gian khi base lạ có `cong-nhanh` in pass, đổi base
   và lượt thật chưa đăng ký. Repo cá nhân cũng không có danh sách giới hạn người push. PR đã lỡ được duyệt sai có thể làm hỏng cổng cho PR sau.
2. **PR rủi ro thấp tự merge, không có người đọc.** Đây là chính sách, người dùng quyết. Trung bình cũng được đối xử như thấp về
   điều kiện qua. Muốn mọi PR phải có người duyệt thì phải đổi `kiem_pr.py`.
3. **Khoảng hở nhỏ giữa yêu cầu sửa và lượt xét mới.** Check cũ còn `success` cho tới khi `tin-hieu-duyet` và `cong-cuoi` chạy xong.
   Nếu bước tạo token hỏng hoặc khoá hết hạn thì không phát được gì, `success` cũ ở lại đến lần xét sau.
4. **`tin-hieu-duyet` chạy theo bản của PR.** PR xoá tệp đó thì lượt duyệt không đánh thức cổng. Đổi `.github/` đã là rủi ro cao nên cần
   người duyệt; sau khi được duyệt, yêu cầu sửa về sau của PR đó không đánh thức cổng, `success` có thể ở lại cho tới sự kiện kế tiếp.
5. **Repo private gói Free không có cổng.** Không đặt được required check.
6. **Admin có thể vượt environment,** trừ khi bỏ tick «Allow administrators to bypass» trên giao diện. `enforce_admins` chỉ áp cho nhánh.
7. **Force push A, B, rồi về A** có thể làm lượt duyệt cũ trên A còn tính. Nội dung vẫn đúng là thứ đã duyệt.
8. **Symlink và đổi quyền tệp** không thấy qua API files, chỉ được xếp trung bình.
9. **Cổng không chứng minh phần mềm đúng.** Sửa logic cùng sửa test theo hướng thêm, hay chèn `sys.exit(0)` vào mã, không bị rủi ro cao bắt được.
   Tệp đổ bóng mô-đun khác (ngoài `unittest` và `sitecustomize`) cùng loại giới hạn này.
10. **Agent lỡ dùng email của người duyệt để commit** thì người đó thành «tự duyệt». Cổng đóng và ghi lý do, không mở sai.
11. **Xoá hoặc đổi tên `cong-nhanh.yml` không qua được:** cổng không có lượt CI để đọc, nên mọi PR kẹt. Đường thoát: chủ repo tạm gỡ bảo vệ nhánh.
12. **PR xung đột với nhánh gốc không có CI** nên cổng báo chờ. Giải xung đột, hoặc sửa tiêu đề hay đóng rồi mở lại để đánh thức.

## Vì sao dùng hai sự kiện đặc quyền

zizmor báo `dangerous-triggers` ở `pull_request_target` và `workflow_run`. Chấp nhận vì `cong-cuoi` không checkout mã PR,
không đưa dữ liệu PR vào `run:`, chỉ dùng SHA đã kiểm dạng. Không dùng `pull_request_review` trực tiếp: sự kiện đó
xét environment theo `refs/pull/N/merge`, muốn chạy được phải nới `gate`, mà nới thì workflow của PR lấy được khoá App.

## Nguyên tắc giữ

- Không checkout, không chạy mã PR trong `cong-cuoi`. Không đưa dữ liệu PR vào `run:`.
- Khoá App chỉ nằm trong environment. Token không in, không đi qua chuyển hướng.
- Check run do App phát, required check có expected source là App, để job của PR không giả tên được.
- Sự kiện chỉ đánh thức cổng. Quyết định chỉ lấy từ API, kể cả kết quả CI.
- Mọi đường hỏng đều không phát `success`.
