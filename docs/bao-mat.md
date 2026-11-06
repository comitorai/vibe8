# Bảo mật: đã kiểm gì, chưa kiểm gì

## Đã kiểm, chỉ ở mức cục bộ

Bằng unittest và `nghiem-thu/kiem_cuc_bo.py`, dữ liệu mô phỏng. Bộ test đã chạy trên Python 3.9, 3.10, 3.12, 3.13, 3.14:

- Logic quyết định: SHA lệch, đổi base, tự duyệt, bot, người không có quyền admin, yêu cầu sửa bị gỡ, thân PR chèn lệnh, tên tệp lạ, xoá test.
- `gate_app`: phát đúng một check trên đúng SHA sự kiện, head đổi giữa chừng, PR fork cùng SHA, hỏng API, không đi theo chuyển hướng,
  che token, chỉ `success` hoặc `failure`.
- Workflow: qua actionlint và zizmor.

## Đã kiểm trên GitHub thật, bằng khoá giả

Vai cộng tác viên quyền ghi, trên repo thật đã bật cổng:

- Đẩy thẳng `main`, kể cả `--force`, và xoá `main`: bị từ chối.
- Workflow lạ đòi environment `gate` không lấy được secret, qua mọi đường đã thử: nhánh `main-2`, `Main`, `thu/main`, tag tên `main`,
  PR thường, `workflow_dispatch`, `deployment` tạo bằng API với ref lạ.
- `pull_request_target` và `workflow_run` của cổng trên `main` qua được `gate`, đến bước tạo token. Có khoá giả nên dừng ở đó.
- **Cộng tác viên ghi được biến và secret trong `gate`.** Vì vậy cổng không đọc danh sách người duyệt từ biến nữa: hỏi GitHub ai có quyền admin.
- Bật log chi tiết (`ACTIONS_STEP_DEBUG`, `ACTIONS_RUNNER_DEBUG`) không làm khoá nhiều dòng lộ qua `create-github-app-token`: không dòng nào của khoá giả xuất hiện trong log.

Trên repo thử do agent làm chủ: ghim `app_id` chặn check và status giả cùng tên, kể cả `gh pr merge --admin` và API merge.

Cũng trên repo thử, bằng token giả:

- Tag tên `main` không làm `actions/checkout` lấy nhầm mã cổng.
- Symlink `json` đã vào nhánh gốc, trỏ tới gói giả, runner `ubuntu-latest`: checkout cả repo thì `python3 -m cong.gate_app` chạy mã của gói đó,
  với token trong tay. Nghĩa là merge lọt một lần thì giữ được token về sau, nên cổng chỉ lấy `/cong/` và symlink như vậy phải có người duyệt.
  Checkout thưa chỉ `/cong/` thì thư mục làm việc chỉ còn `.git`, `cong`, và cổng chạy đúng mã của nó.
- Merge kiểu rebase một nhánh lặp lại rồi đảo thay đổi đã vào `main`, 5 biến thể: GitHub đều trả `rebaseable: false` và 405. Rebase thường
  vẫn merge được. Tài liệu GitHub Enterprise Server gọi rebase "unsafe" khi kết quả khác merge thường, các trang của github.com không nêu; có áp cho github.com
  không thì chưa kiểm, nên cổng không dựa vào hành vi này: xem giới hạn 21.

## Đã kiểm trên GitHub thật, bằng khoá thật

- Cổng tạo được token App và phát check đúng App. L1-L8 và các ca thêm: kết quả từng lượt ghi ở `nghiem-thu/ket-qua.md`.
- Token App đọc được API quyền cộng tác viên, cả người quyền ghi lẫn người quyền admin: lượt bình luận của cộng tác viên cho ra `chan`, lượt duyệt của người có quyền admin cho ra `cho_qua`, không lỗi API.
- Bản vá L8, một lần thử: PR đổi base có hai lượt xanh, cổng không tính lượt nào, merge bị từ chối. Token App đọc được `/issues/N/events`: không đọc được thì cổng báo lỗi API, không báo chờ.
- Quyền App đủ để đọc PR, lượt chạy, lượt duyệt và phát check: các ca trên ra đúng kết luận.
- Job Actions phát check cùng tên `cong-cuoi` `success` bên cạnh `failure` của App: PR vẫn bị chặn. Status API cùng tên: GitHub nhận, PR vẫn bị chặn, merge bị từ chối.
  Check run bằng token thường: 403, vì phải là GitHub App. Hai ca kia có `failure` của App trên cùng SHA, nên riêng chúng không chứng minh được ghim `app_id`; bằng chứng tách riêng là ca trên repo thử ở trên.

Đo trên repo đối chứng, token thường, không phải khoá thật:

- `cong-nhanh` chỉ chạy lúc mở PR và đẩy commit: 11 lượt loại này, đẩy cách nhau 3 và 15 giây, đều checkout đúng merge của head mới. Mẫu nhỏ, không phải cam kết của GitHub.
- Lượt `edited` 1-2 giây sau khi đổi base lại merge vào base cũ, trên base khác SHA với `main`: tái hiện đúng nguyên nhân L8.
- Đổi base bằng REST và GraphQL: sự kiện hiện ở lần đọc đầu trong 6/6 lần đo. Mẫu nhỏ, token thường.
- GitHub tự đổi base của stacked PR khi nhánh cha tự xoá sau merge: có sự kiện `automatic_base_change_succeeded`. Lần đọc 0,83 giây chưa đổi gì, lần 4,22 giây đã đổi cả base lẫn sự kiện. Xoá bằng `gh pr merge --delete-branch` thì PR con đóng, base không đổi.
- Đẩy commit khi đã xung đột: 2/2 không có lượt trên SHA đó. Đẩy commit lúc PR đóng: 1/1 không có lượt.
- Chạy lại lượt: giữ id và `created_at`, `run_attempt` thành 2, dùng commit merge cũ kể cả khi PR đã xung đột.
- Đổi tên nhánh đầu: xem giới hạn 23.
- `gh pr merge --admin` bằng tài khoản chủ repo thật, PR 23 cổng đỏ: GitHub từ chối vì required check `cong-cuoi` đỏ, `enforce_admins` chặn cả admin. Một lần thử.

## Chưa kiểm

- `head_sha` của lượt `workflow_run` có đúng là head của PR không, và GitHub chọn check mới nhất của App trên SHA thế nào.
- Trường `head_repository` của lượt chạy có đúng như cách cổng dùng để lọc PR fork không.
- Hiệu lực của `can_admins_bypass: false` với chủ repo: API nhận và đọc lại đúng, chưa thử bằng tài khoản chủ.
- Tìm `head=` có đúng với nhánh có ký tự lạ không; sai thì cổng đóng.
- API có trễ không ngay sau `workflow_run`. Sự kiện đổi base hiện ở lần đọc đầu trong 6/6 lần đo, bằng token thường, không phải token App; chưa dựng được đúng lượt đang xếp hàng lúc đổi base. Nếu API trễ đúng lúc cổng đọc thì `success` sai không được sửa, vì sau khi đổi base `cong-nhanh` không chạy lại, cổng chỉ được đánh thức một lần.
  `tin-hieu-duyet` trên PR fork có cần phê duyệt mới chạy không.
- Giữ nhóm concurrency bằng lượt treo của PR, quyền xoá lượt, `/cancel`, secret cấp repo trùng tên trong environment.
- `workflow_run.head_sha` của `tin-hieu-duyet` có đúng head PR không.
- Required check với `strict: False`: PR xanh trên base cũ có merge được không (là chủ ý, cần xác nhận).

## Giới hạn đã biết

1. **Cổng chống đi tắt, không chống cộng tác viên cố ý ác.** Trên repo cá nhân, cộng tác viên có quyền ghi và xoá được lượt
   CI đỏ. Repo cá nhân cũng không có danh sách giới hạn người push. PR đã lỡ được duyệt sai có thể làm hỏng cổng cho PR sau.
   Lượt chạy lọc theo repo đầu, nhánh đầu và thời điểm, không dùng `pull_requests[]` của API vì trường đó tính lúc đọc: ghi base hiện tại và mọi
   PR mở cùng nhánh, kể cả khi lượt đã test với base khác. Nhánh đầu từng có PR khác thì không lượt nào tính. PR từng đổi base cũng vậy: bản trước
   lọc theo mốc đổi base và đã lọt trên GitHub thật, vì lượt tạo 2 giây sau khi đổi vẫn checkout ref merge của base cũ, base đó có workflow in pass.
   Lượt không ghi nó chạy ref merge nào, và cổng không có cách đọc: log do workflow của ref đó viết. Nên `cong-nhanh` chỉ chạy lúc mở PR và đẩy commit, và
   tin vào ref merge do GitHub dựng. PR xung đột hoặc đẩy commit lúc đang đóng thì không có lượt trên SHA đó, cổng báo chờ. Khe cố ý còn lại, chưa thử trên GitHub:
   commit trung gian thêm `edited` vào workflow, commit cuối xung đột và trả workflow về như cũ nên diff không thấy gì, PR khác merge làm hết xung đột, rồi sửa
   tiêu đề. Lượt đó chạy workflow của ref cũ mà mang SHA cuối. Cần cộng tác viên cố ý và nhiều bước.
2. **PR mức thường merge không có người đọc.** Đây là chính sách, Alex chốt 06/11 (1a): cần cổng xanh và phiếu phản bác không bác trên đúng SHA
   của người có quyền ghi. Máy không phân biệt được hai agent chung tài khoản, nên tác giả cũng tự ghi phiếu được. Muốn mọi PR phải có người duyệt thì phải đổi `kiem_pr.py`. PR mức Cao cần cả phiếu lẫn người admin duyệt; thẻ duyệt chỉ đưa diff của tệp Cao, nên phần Thường trong PR Cao cũng chỉ có phiếu soát.
3. **Khoảng hở nhỏ giữa yêu cầu sửa và lượt xét mới.** Check cũ còn `success` cho tới khi `tin-hieu-duyet` và `cong-cuoi` chạy xong.
   Nếu bước tạo token hỏng hoặc khoá hết hạn thì không phát được gì, `success` cũ ở lại đến lần xét sau. Cộng tác viên gây được việc này
   có chủ ý: xem giới hạn 18.
4. **`tin-hieu-duyet` chạy theo bản của PR.** PR xoá tệp đó thì lượt duyệt không đánh thức cổng. Đổi `.github/` đã là rủi ro cao nên cần
   người duyệt; sau khi được duyệt, yêu cầu sửa về sau của PR đó không đánh thức cổng, `success` có thể ở lại cho tới sự kiện kế tiếp.
5. **Repo private gói Free không có cổng.** Không đặt được required check.
6. **Admin có thể vượt environment,** trừ khi bỏ tick «Allow administrators to bypass» trên giao diện. `enforce_admins` chỉ áp cho nhánh.
7. **Force push A, B, rồi về A** làm lượt duyệt cũ trên A còn tính, và thu hồi trên A bị lượt xét mới ghi đè. Cây mã giống thứ đã duyệt,
   nhưng `main` có thể đã khác, nên kết quả merge có thể khác thứ đã đọc.
8. **API files không cho biết mode của tệp.** Symlink mới hiện như tệp một dòng có nội dung là đích, nên chỉ bị bắt khi trùng tên mô-đun chuẩn.
   Đổi quyền tệp thuần không có diff dạng chữ: loại `changed` xếp mức thường. Tệp không có diff dạng chữ thì cần duyệt, trừ ảnh, PDF và phông chữ.
   Đổi tên kèm sửa tệp nhị phân trông giống hệt đổi tên thuần (0 dòng, không patch) nên là mức thường.
9. **Cổng không chứng minh phần mềm đúng.** Tệp test mới hoặc mã thường vẫn có thể gọi `os._exit(0)`, hay gán đè `unittest.TestCase.run`, và
   CI xanh giả mà không có gì báo rủi ro cao. Luật test chỉ bịt các đường đi tắt qua test có sẵn, và nhận test theo tên nên không bao giờ đủ:
   thư mục hay đuôi lạ lọt, còn `docs/specs/x.md`, `test_utils.py` thì bị báo oan. Bước sau có thể đếm số test chạy so với nhánh gốc.
   Tệp trùng tên gói bên thứ ba (`yaml.py`) cũng che được gói đó trong CI mà vẫn là mức thường: cổng không biết repo dùng gói nào, và lớp lỗi này không
   nặng hơn `os._exit(0)` ở trên. Job cổng không bị ảnh hưởng, vì chỉ dùng thư viện chuẩn và chỉ lấy thư mục `cong/`.
10. **Agent lỡ dùng email của người duyệt để commit** thì người đó thành «tự duyệt». Cổng đóng và ghi lý do, không mở sai.
11. **Xoá hoặc đổi tên `cong-nhanh.yml` không qua được:** cổng không có lượt CI để đọc, nên mọi PR kẹt. Đường thoát: chủ repo tạm gỡ bảo vệ nhánh.
12. **Cổng báo chờ, không qua, khi không có lượt tính được:** PR xung đột với nhánh gốc, PR mở lại sau khi đẩy commit lúc đóng, nhánh đầu từng có PR khác (kể cả đã
    đóng, nên PR lành dùng lại nhánh cũ vẫn kẹt), hoặc PR từng đổi base, kể cả stacked PR do GitHub tự đổi. Hai trường hợp đầu thì đẩy một commit mới, kể cả khi
    xung đột tự hết vì PR khác đã merge. Hai trường hợp sau thì đóng PR đó, đẩy sang nhánh tên mới rồi mở PR mới: PR cũ còn mở cùng SHA sẽ làm PR mới kẹt, xem giới hạn 14.
13. **Yêu cầu sửa gắn theo PR.** Mở PR mới cùng nội dung thì yêu cầu sửa cũ không theo; nếu là mức thường thì qua khi có phiếu không bác trên SHA mới.
14. **Hai PR trong repo cùng SHA vào `main` làm cả hai kẹt.** PR thứ hai mở có chủ ý thì giữ được SHA đó không qua được, đến khi đóng.
15. **PR quá 3000 tệp bị chặn:** API không trả đủ, cổng đóng. Commit có author không gắn tài khoản, và commit merge, không tính vào «người có commit».
16. **`workflow_run` trễ sau khi PR đã merge** có thể ghi `failure` lên commit đã vào `main`. Chỉ là hiển thị, không ảnh hưởng PR khác có SHA khác.
17. **PR từ fork đã xoá** không có repo đầu để so nên không lượt nào được tính, PR kẹt. Mở lại từ nhánh còn tồn tại.
18. **Cộng tác viên quyền ghi làm kẹt được cổng.** Họ ghi đè được `XUONG_APP_KEY`, `XUONG_APP_CLIENT_ID` dù không đọc được khoá.
    Check do App khác phát không được tính vì ghim `app_id`, nên SHA chưa có `success` không qua được. SHA đã có `success` thì giữ được nó dù
    người duyệt yêu cầu sửa sau đó, vì cổng không phát được `failure` để thu hồi. Không đưa được thay đổi chưa từng xét vào `main`. Chủ repo đặt lại khoá.
19. **Chỉ quyền admin mới duyệt được.** Trên repo tổ chức, vai `maintain` không tính. Quyền đọc lúc xét: mất quyền admin thì lượt duyệt cũ hết tính.
20. **Lỗi đọc quyền làm cổng đóng.** API quyền hỏng thì lượt đó ra `failure`, tự lành ở sự kiện sau.
21. **Merge kiểu rebase phải tắt.** Cổng đọc diff so với điểm rẽ nhánh; rebase phát lại từng commit nên có thể đảo thay đổi đã vào `main` mà diff không
    cho thấy. Chưa tái hiện được trên GitHub: đây là biện pháp phòng, vì điều kiện GitHub từ chối chỉ thấy ghi ở tài liệu Enterprise Server. `bat_cong.py` tắt và đọc lại.
22. **Hai PR xanh riêng có thể ghép lại gãy `main`.** `strict: False` nên PR không phải chạy lại khi `main` tiến. Hai PR mức thường, mỗi PR xanh trên `main` lúc nó chạy,
    có thể cùng vào và làm `main` đỏ. Không PR nào vượt cổng, và PR kế tiếp sẽ đỏ nên hỏng lộ ra ngay. Đổi lấy: `strict: True` buộc chạy lại và duyệt lại mỗi lần `main` tiến;
    hàng đợi merge chỉ có ở repo tổ chức.
23. **Đổi tên nhánh đầu vòng qua được luật một nhánh một PR.** PR đã đóng vẫn mang tên cũ, nên tìm `head=` theo tên mới chỉ thấy PR mới. Đo trên repo đối chứng, 1 mẫu:
    lượt cũ giữ tên cũ nên bị lọc, đẩy commit mới sinh đúng 1 lượt mang tên mới, merge đúng head mới. Chưa đo: PR đang mở khi đổi tên, và sửa PR đã đóng sau khi đổi tên;
    đường sau cần workflow có `edited` ở ref merge, trùng khe ở giới hạn 1.

## Vì sao dùng hai sự kiện đặc quyền

zizmor báo `dangerous-triggers` ở `pull_request_target` và `workflow_run`. Chấp nhận vì `cong-cuoi` không checkout mã PR,
không đưa dữ liệu PR vào `run:`, chỉ dùng SHA đã kiểm dạng. Không dùng `pull_request_review` trực tiếp: sự kiện đó
xét environment theo `refs/pull/N/merge`, muốn chạy được phải nới `gate`, mà nới thì workflow của PR lấy được khoá App.

## Nguyên tắc giữ

- Không checkout, không chạy mã PR trong `cong-cuoi`. Không đưa dữ liệu PR vào `run:`.
- `cong-cuoi` chỉ lấy thư mục `/cong/` từ nhánh gốc, và chỉ dùng thư viện chuẩn.
- Khoá App chỉ nằm trong environment. Token không in, không đi qua chuyển hướng.
- Check run do App phát, required check có expected source là App, để job của PR không giả tên được.
- Sự kiện chỉ đánh thức cổng. Quyết định chỉ lấy từ API, kể cả kết quả CI.
- Mọi đường hỏng đều không phát `success`.
