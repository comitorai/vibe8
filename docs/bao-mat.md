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
- `created_at` của lượt có giữ nguyên khi bấm chạy lại không. Cổng lọc lượt theo mốc này; nếu nó đổi thì lượt của base cũ có thể được tính.
  Mốc đổi base so với lượt do chính lần đổi đó tạo ra có lệch giây không. Tìm `head=` có đúng với nhánh có ký tự lạ không; sai thì cổng đóng.
  Đổi tên nhánh đầu: PR đã đóng của tên cũ có lượt mới mang tên nhánh nào.
- Token App quyền `issues: read` đọc được `/issues/N/events` trên PR không, hay chỉ cần `pull_requests: read`.
- API có trễ không ngay sau `workflow_run`. `tin-hieu-duyet` trên PR fork có cần phê duyệt mới chạy không.
- Status API và check run do token thường tạo cùng tên `cong-cuoi` có qua được required check gắn App không. Hai check cùng tên, một `failure`
  một `success`, GitHub chọn cái nào.
- Giữ nhóm concurrency bằng lượt treo của PR, quyền xoá lượt, `/cancel`, `workflow_dispatch`, secret cấp repo trùng tên trong environment.
- `workflow_run.head_sha` của `tin-hieu-duyet` có đúng head PR không. Duyệt có còn tính sau đổi base không, kể cả stacked PR.
- Required check với `strict: False`: PR xanh trên base cũ có merge được không (là chủ ý, cần xác nhận).

## Giới hạn đã biết

1. **Cổng chống đi tắt, không chống cộng tác viên cố ý ác.** Trên repo cá nhân, cộng tác viên có quyền ghi và xoá được lượt
   CI đỏ. Repo cá nhân cũng không có danh sách giới hạn người push. PR đã lỡ được duyệt sai có thể làm hỏng cổng cho PR sau.
   Lượt chạy lọc theo repo đầu, nhánh đầu và thời điểm, không dùng `pull_requests[]` của API vì trường đó tính lúc đọc: ghi base hiện tại và mọi
   PR mở cùng nhánh, kể cả khi lượt đã test với base khác. Nhánh đầu từng có PR khác thì không lượt nào tính. Còn một khe hẹp: sửa tiêu đề rồi đổi
   base về `main` trong vài giây thì lượt của base cũ có thể tạo sau mốc. Lượt trên `main` vẫn phải xanh, nên khe này chỉ dùng được khi PR
   xung đột (không có lượt trên `main`) và `main` sau đó hết xung đột mà SHA không đổi.
2. **PR rủi ro thấp tự merge, không có người đọc.** Đây là chính sách, người dùng quyết. Trung bình cũng được đối xử như thấp về
   điều kiện qua. Muốn mọi PR phải có người duyệt thì phải đổi `kiem_pr.py`.
3. **Khoảng hở nhỏ giữa yêu cầu sửa và lượt xét mới.** Check cũ còn `success` cho tới khi `tin-hieu-duyet` và `cong-cuoi` chạy xong.
   Nếu bước tạo token hỏng hoặc khoá hết hạn thì không phát được gì, `success` cũ ở lại đến lần xét sau.
4. **`tin-hieu-duyet` chạy theo bản của PR.** PR xoá tệp đó thì lượt duyệt không đánh thức cổng. Đổi `.github/` đã là rủi ro cao nên cần
   người duyệt; sau khi được duyệt, yêu cầu sửa về sau của PR đó không đánh thức cổng, `success` có thể ở lại cho tới sự kiện kế tiếp.
5. **Repo private gói Free không có cổng.** Không đặt được required check.
6. **Admin có thể vượt environment,** trừ khi bỏ tick «Allow administrators to bypass» trên giao diện. `enforce_admins` chỉ áp cho nhánh.
7. **Force push A, B, rồi về A** làm lượt duyệt cũ trên A còn tính, và thu hồi trên A bị lượt xét mới ghi đè. Cây mã giống thứ đã duyệt,
   nhưng `main` có thể đã khác, nên kết quả merge có thể khác thứ đã đọc. Đổi base đi rồi đổi lại cũng vậy, kể cả với stacked PR hợp lệ.
8. **Symlink và đổi quyền tệp** không thấy qua API files, chỉ được xếp trung bình. Tệp không có diff dạng chữ thì cần duyệt, trừ ảnh, PDF và phông chữ.
9. **Cổng không chứng minh phần mềm đúng.** Tệp test mới hoặc mã thường vẫn có thể gọi `os._exit(0)`, hay gán đè `unittest.TestCase.run`, và
   CI xanh giả mà không có gì báo rủi ro cao. Luật test chỉ bịt các đường đi tắt qua test có sẵn, và nhận test theo tên nên không bao giờ đủ:
   thư mục hay đuôi lạ lọt, còn `docs/specs/x.md`, `test_utils.py` thì bị báo oan. Bước sau có thể đếm số test chạy so với nhánh gốc.
10. **Agent lỡ dùng email của người duyệt để commit** thì người đó thành «tự duyệt». Cổng đóng và ghi lý do, không mở sai.
11. **Xoá hoặc đổi tên `cong-nhanh.yml` không qua được:** cổng không có lượt CI để đọc, nên mọi PR kẹt. Đường thoát: chủ repo tạm gỡ bảo vệ nhánh.
12. **Cổng báo chờ, không qua, khi không có lượt tính được:** PR xung đột với nhánh gốc, nhánh đầu từng có PR khác (kể cả đã đóng, nên PR lành dùng
    lại nhánh cũ vẫn kẹt), hoặc vừa đổi base mà lượt mới chưa có. Giải xung đột rồi sửa tiêu đề để chạy CI và đánh thức; dùng lại nhánh thì đẩy sang nhánh tên mới.
13. **Yêu cầu sửa gắn theo PR.** Mở PR mới cùng nội dung thì yêu cầu sửa cũ không theo; nếu là rủi ro thấp thì tự qua.
14. **Hai PR trong repo cùng SHA vào `main` làm cả hai kẹt.** PR thứ hai mở có chủ ý thì giữ được SHA đó không qua được, đến khi đóng.
15. **PR quá 3000 tệp bị chặn:** API không trả đủ, cổng đóng. Commit có author không gắn tài khoản, và commit merge, không tính vào «người có commit».
16. **`workflow_run` trễ sau khi PR đã merge** có thể ghi `failure` lên commit đã vào `main`. Chỉ là hiển thị, không ảnh hưởng PR khác có SHA khác.
17. **PR từ fork đã xoá** không có repo đầu để so nên không lượt nào được tính, PR kẹt. Mở lại từ nhánh còn tồn tại.

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
