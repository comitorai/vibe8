# Phương pháp làm phần mềm với agent — bản 1 (nháp, 05/11/2026)

Áp cho mọi repo cài vibe8, từ một PR lẻ tới cả một module (mô-đun) hay một phase (giai đoạn).
Nhãn căn cứ: `[ĐÃ KIỂM: …]` · `[SUY LUẬN từ …]` · `[CHƯA KIỂM]`. «Nội bộ» là số đo trên repo riêng của chủ dự án, không đăng ở đây.

## 0. Mục tiêu (chủ dự án chốt 05/11, xếp theo thứ tự)

1. **Ít lỗi lọt tới người dùng**, tốc độ không chậm hơn mốc của repo trước khi áp.
2. **Nhanh ra bản bán được**: việc nào đẩy bản bán được tới gần hơn thì làm trước.
3. **Token tối ưu nhất**: chi tiêu theo mức rủi ro, không chi đều cho mọi PR.

Khi va nhau: lỗi lọt mức nặng thắng tốc độ; tốc độ thắng token; token thắng sự đầy đủ của giấy tờ.

## 1. Luật về luật

- **Một luật chỉ vào file này khi ghi đủ bốn thứ:** chặn loại lỗi nào · đo bằng gì (máy đo, không tự khai) · mức giữ và mức bỏ · ngày xét.
  Thiếu một thứ thì là lời khuyên, đưa vào mục 7.
- **Mức giữ, mức bỏ khoá trước khi xem số.** Đến ngày xét, luật nhận một trong ba kết quả:
  **GIỮ** (đủ mẫu, đạt) · **BỎ** (đủ mẫu, không đạt) · **CHƯA ĐỦ MẪU** (giữ nguyên, gia hạn một lần; lần sau vẫn thiếu mẫu thì chủ dự án quyết).
  Không bỏ luật chỉ vì thiếu dữ liệu.
- **Không đo tuân thủ thay cho tác dụng.** «Agent có làm theo không» chỉ để biết luật có chạy; giữ hay bỏ xét theo lỗi chặn được.
  Bảng chấm bộ cách cũ: «không mã nào đạt GIU», phần lớn chỉ có số tuân thủ `[ĐÃ KIỂM: nội bộ · 04/11]`.
- **Luật máy kiểm được thì giao cho máy phía GitHub.** Hook trên máy agent chỉ là trợ giúp, không tính là hàng rào.
- **Luật nền** (L1, L5, L10) giữ an toàn cho cổng nên không bỏ theo số; vẫn đo độ đúng để chỉnh.
- **Trần: 15 luật.** Muốn thêm luật thứ 16 thì bỏ một luật có số kém nhất.

## 2. Hai mức việc — người chỉ duyệt chỗ chạm bảo mật hay tiền

Alex chốt 06/11 (1a): chỉ có **đạt** hoặc **không đạt**; không đạt thì sửa tới khi đạt rồi merge. Người chỉ cần nhìn chỗ có thể mất an toàn hay mất tiền.

**Mức do máy xếp theo đường dẫn tệp, agent không tự khai.**
- **Cao** (chạm bảo mật hay tiền): những gì `cong/rui_ro.py` xếp cao vì đủ làm cổng hay CI (tích hợp liên tục) báo sai, hoặc chạy lệnh trên máy người mở repo: tệp của cổng và `.github/`, cấu hình agent (tác tử) `.claude/`, sửa hay xoá test có sẵn, tệp khai phụ thuộc và lockfile, tệp trùng tên mô-đun chuẩn, mã máy và tệp không có diff dạng chữ (trừ ảnh, PDF, phông chữ), tên tệp lạ; **cộng** các mẫu đường dẫn repo tự khai trong `cong/vung-nhay-cam.txt`: thanh toán, xác thực, quyền, khoá bí mật, xoá dữ liệu, migration (giải nghĩa: tệp đổi cấu trúc database theo từng bước).
- **Thường**: mọi thứ còn lại, gồm tài liệu, test mới, mã và cấu hình chạy được.
- **Repo chưa có `cong/vung-nhay-cam.txt` trên nhánh gốc thì cổng chặn mọi PR**: không biết đâu là tiền thì không phân được hai mức. Repo không có vùng nào thì để tệp chỉ có chú thích. Tệp này thuộc `cong/` nên khai hay sửa đều là Cao.

`[ĐÃ KIỂM: test cổng · 06/11]` Cổng xếp hai mức như trên và đọc vùng từ nhánh gốc, nên PR không tự gỡ vùng được. Mọi PR, cả mức Cao, cần phiếu phản bác của L3 trên đúng SHA, không còn rút thăm; trần L4 là bác trên 2 SHA khác nhau, khi đó người admin quyết bằng lượt duyệt ghi sau phiếu bác cuối, có dòng `quyet-l4:`, và thẻ đưa diff mọi tệp; phiếu bác trên một SHA thì phiếu không bác ghi sau không gỡ được, phải có commit mới; cách ghi phiếu ở README. Máy không phân biệt được hai agent chung tài khoản, nên «agent khác» vẫn là lời dặn, chưa là hàng rào. Chưa làm tài khoản thứ hai cho người phản bác (Alex 1a, 06/11): khi token của nó nằm cùng máy với agent viết code thì hai tài khoản chỉ khác tên. Làm khi một trong hai điều sau xảy ra: lỗi lọt từ PR Thường tăng trong bản đo tuần của `do_vong.py`, hoặc người phản bác chạy ngoài máy với token mà agent viết code không đọc được. Mức Cao cần cả phiếu lẫn người duyệt (Alex 1a, 06/11): thẻ duyệt chỉ đưa diff của tệp Cao, phần Thường của PR đó do phiếu soát.
`[ĐÃ KIỂM: PR 28 · 05/11]` PR thật chỉ sửa một tệp tài liệu trong vùng đã khai ra `chan (cao)`.
Giới hạn đã biết: cổng chỉ thấy đường dẫn, nên mã tiền đặt ngoài vùng đã khai thì là Thường; vùng khai thiếu là lỗ của repo, người duyệt PR khai vùng phải soát. Tách một thay đổi lớn thành nhiều PR nhỏ vẫn lọt qua trần cỡ của L2.

| | Thường | Cao |
|---|---|---|
| Trước khi code | 3–5 dòng tiêu chí nghiệm thu trong thân PR | như Thường + mục «KHÔNG được phá» |
| Test | test có sẵn xanh; thêm test cho hành vi mới | như Thường; sửa lỗi thì có test đỏ trước khi sửa |
| Phản bác của agent | 1 lượt (L3) | 1 lượt + 1 lượt hẹp sau khi sửa logic |
| Người duyệt | không | admin, khác tác giả, đúng SHA |
| Merge | tự, khi cổng xanh và phiếu không bác | sau duyệt và phiếu không bác |

**Làn sửa gấp** (lỗi đang hại người dùng): mức nào vẫn giữ mức đó. Cổng không biết PR nào là sửa gấp và chặn mọi PR chưa có phiếu `khong-bac` trên đúng SHA (Alex 1a, 06/11), nên trước merge chỉ cần một lượt phản bác hẹp trên chỗ sửa; lượt đầy đủ chạy sau merge, trong 24 giờ. Người duyệt của mức Cao vẫn bắt buộc trước merge.

## 3. Các luật

| # | Luật | Chặn lỗi gì | Đo bằng | Giữ nếu · Bỏ nếu | Xét |
|---|---|---|---|---|---|
| L1 | Mọi thay đổi vào `main` qua PR và qua cổng `cong-cuoi` | đẩy thẳng, CI giả xanh, tự duyệt | sổ chặn của cổng | luật nền | 30 ngày |
| L2 | PR ≤ 400 dòng, trừ khi người duyệt ghi `ngoai-le-co:` | PR lớn không ai đọc nổi | số vòng sửa và lỗi bắt trước merge theo cỡ PR | PR nhỏ ít vòng sửa hơn · không khác; cần ≥ 60 PR | 60 ngày |
| L3 | Một lượt **phản bác** cho mọi PR: agent khác tìm cách làm hỏng, phải kèm cách tái hiện. Bỏ rút thăm đối chứng (Alex 1a, 06/11) | lỗi hành vi, lỗi quyền mà test xanh | lỗi thật bắt được / lượt; sửa gấp trong 7 ngày sau merge | ≥ 1 lỗi thật / 10 lượt, cần ≥ 30 lượt · dưới mức đó | 60 ngày |
| L4 | Trần 2 vòng phản bác mỗi PR; lượt sau khi sửa chỉ xét phần vừa sửa | vòng sửa không dứt, token đọc lại | token mới / PR và số vòng, máy ghi | trung vị token không tăng, L3 không giảm · ngược lại | 30 ngày |
| L5 | Test có sẵn là điều kiện nghiệm thu; sửa, đổi tên, xoá cần người duyệt | agent sửa test cho xanh | cổng đã chặn | luật nền | 30 ngày |
| L6 | Sửa lỗi có test đỏ trước khi sửa, xanh sau khi sửa, cùng PR | sửa sai chỗ, lỗi tái phát | lỗi tái phát trong 30 ngày | tái phát thấp hơn nhóm không có · không khác; cần ≥ 20 đơn mỗi nhóm | 90 ngày |
| L7 | Chạy thật sớm: ngay lát đầu, chạy trên môi trường thật nhất có được (app thật, GitHub thật), không đợi xong vòng cục bộ | lỗi chỉ lộ ở môi trường thật | lỗi thấy lần đầu ở môi trường thật / 10 lát | ≥ 1 · 0 thì chỉ chạy thật ở lát cuối | 30 ngày |
| L8 | CI chỉ có bài tất định: không phụ thuộc ngày giờ, mạng ngoài; `main` đỏ thì sửa `main` trước mọi PR | CI đỏ oan, người quen bỏ qua đỏ | đỏ oan / 100 lượt | ≤ 3 · trên 3 thì sửa bài, không thêm cổng | 14 ngày |
| L9 | Làn song song: một làn một worktree (bản làm việc song song cùng một repo) một PR; số làn theo tải máy; merge xong máy tự dọn | làn giẫm nhau, đầy đĩa | xung đột / tuần, GB tồn | xung đột ≤ 1 / tuần · trên mức đó thì giảm làn | 14 ngày |
| L10 | Bằng chứng duy nhất là lượt CI trên đúng head SHA mà cổng đọc; thân PR không có mục tự khai «đã chạy» | khai xanh mà chưa chạy | cổng đã đọc lượt | luật nền | 30 ngày |
| L11 | Mỗi module có tệp **điều kiện bán được** trong repo, thuộc vùng cần người duyệt; mỗi PR ghi điều kiện nó đẩy, PR không đẩy điều kiện nào thì xếp sau | làm nhiều mà không ra bản bán được | số điều kiện đạt / tuần, máy đếm từ tệp | tăng mỗi tuần · 2 tuần liền không tăng thì chủ dự án xem lại danh sách | 14 ngày |

Trích dẫn cho bảng: lượt phản bác có bắt lỗi thật trước merge (độ tin trung bình), **chưa chứng minh giảm lỗi lọt** `[ĐÃ KIỂM: nội bộ · 04/11]`. L7: ca L8 của cổng vibe8 qua hết vòng thử cục bộ, chỉ lọt khi thử trên GitHub thật `[ĐÃ KIỂM: nghiem-thu/ket-qua.md:18 · 05/11]`.

## 4. Token — chi theo việc, không chi theo thói quen

- Một lượt phản bác mỗi PR, không chạy lượt review thường song song: phản bác đã có lỗi thật kèm tái hiện, còn review thường chưa có số tách riêng `[ĐÃ KIỂM: nội bộ · 04/11]`. PR chỉ sửa tài liệu thì lượt phản bác ngắn: đọc diff, xác nhận không chạm mã.
- Đọc nhiều tệp, tìm kiếm: agent con model rẻ; quyết định, viết mã khó: model mạnh.
- File nạp sẵn mỗi phiên (`CLAUDE.md`, `AGENTS.md`) càng ngắn càng tốt; trần đặt theo số đo «token nạp sẵn mỗi phiên» `[CHƯA KIỂM: chưa có số]`.
- Một phiên một việc; xong thì đóng. Phiên dài chiếm phần lớn chi phí `[SUY LUẬN từ số đo theo bước · nội bộ · 04/11]`.
- Token ghi theo PR, máy ghi từ bản ghi phiên (mục 8.3); không dùng số agent tự báo.

## 5. Đo — năm con số, máy tính

| Số | Định nghĩa | Đủ để kết luận |
|---|---|---|
| Lỗi lọt | issue nhãn `loi-lot` (mục 8), trên 100 PR, theo mức nặng và khâu lẽ ra chặn | ≥ 10 lỗi mỗi kỳ |
| Tỉ lệ thay đổi gây hỏng | % PR phải sửa gấp, hoàn lại trong 7 ngày | ≥ 30 PR đủ 7 ngày |
| Thời gian ra | mở PR → lên production; trung vị và mức chậm nhất của 1/10 số PR; theo mức rủi ro | ≥ 30 PR mỗi mức |
| Token mỗi PR đã merge | token mới (không tính đọc lại bộ nhớ đệm), tính cả PR bị bỏ | ≥ 30 PR |
| Độ đúng của từng luật | lần chặn đúng / mọi lần chặn | ≥ 30 lần chặn |

Lỗi lọt cần nhiều tháng mới đủ mẫu, nên luật nhỏ xét bằng số sớm hơn (lỗi bắt trước merge, sửa gấp, tái phát); lỗi lọt dùng để xét cả bộ.
Mốc trước khi áp: đo 30 ngày gần nhất của repo, ghi vào sổ riêng của repo đó, không ghi vào repo công khai này.

## 6. Đã bỏ từ bộ cách cũ, và vì sao

Theo bảng chấm nội bộ 04/11:
- **Vòng 9 bước bắt buộc cho mọi việc:** chưa tách được công; thay bằng ba mức ở mục 2.
- **Công cụ merge an toàn phía máy agent:** chủ yếu đẩy tuân thủ, không có sổ chặn; thay bằng cổng phía GitHub (L1).
- **Mục «Đã chạy» do agent tự khai:** hầu như không có output thật; thay bằng L10.
- **Gác PR tự động, merge theo lô, bất biến chạy mỗi PR, tự lái:** chưa chặn được lỗi thật nào, hoặc đã đo không hơn.
  Muốn đưa lại thì đi đường mục 1.

## 7. Lời khuyên (chưa phải luật)

- Hướng dẫn thao tác tay cho người: đúng màn hiện tại, một bước một dòng.
- Đặc tả trước code có mục «KHÔNG được phá» cho mức Thường: đang chờ số đo.
- Kiểm thử đột biến cho mã cổng và mã quyền: 0 token, vài phút, bắt được bài test yếu.

## 8. Vòng cải tiến — nhận diện, phân loại, đo, đề xuất

Thiếu khâu nào trong bốn khâu dưới đây thì mục 1 và mục 5 không chạy được: không có sổ lỗi thì không có số, không có số thì không xét giữ hay bỏ luật nào.

**8.1 Nhận diện — sổ lỗi lọt là issue GitHub, không phải tệp tự ghi.**
- Lỗi lọt = lỗi đã tới bản người dùng chạy. Ai thấy (người dùng, giám sát, người trong nhóm) thì mở issue nhãn `loi-lot` trong 24 giờ.
- Thân issue có một dòng riêng `pr-gay-loi: #<số PR>` (chưa truy được thì `pr-gay-loi: chưa rõ`), kèm cách tái hiện và ngày lộ. Máy đọc dòng này để tính tỉ lệ thay đổi gây hỏng; PR hoàn lại bằng nút Revert của GitHub (thân `Reverts chu/repo#<số>`) cũng được tính.
- PR sửa ghi `sua-loi-lot: #<issue>` để người đọc nối lỗi với bản sửa.
- Lỗi bắt được trước merge (phản bác, cổng, test) không phải lỗi lọt; ghi nhãn `bat-truoc-merge` để đo L3.

**8.2 Phân loại — ba trường bắt buộc trên mỗi issue `loi-lot`.**

Hai trường đầu là **nhãn** trên issue, đúng một nhãn mỗi trường: `N1` · `N2` · `N3`, và `khau:<giá trị>`. Thiếu, thừa hoặc sai giá trị thì máy xếp vào «chưa phân loại» và liệt kê số issue, không đoán.

| Trường | Giá trị | Ai điền |
|---|---|---|
| Mức nặng | **N1** mất hoặc sai dữ liệu, lộ dữ liệu, sai tiền, vượt quyền · **N2** chức năng chính hỏng, không có đường vòng · **N3** có đường vòng hoặc chỉ sai giao diện | agent không viết PR gây lỗi đề xuất; người duyệt chốt N1 |
| Khâu lẽ ra chặn | khâu **sớm nhất** lẽ ra bắt được, chỉ một: `dac-ta` (tiêu chí thiếu) · `test` (thiếu test) · `phan-bac` (có lượt mà sót) · `khong-phan-bac` (merge không phiếu, vd người admin vượt cổng) · `cong` (xếp sai mức) · `chay-that` (L7) · `ngoai-tam` (môi trường, bên thứ ba) | như trên |
| Mức rủi ro của PR gây lỗi | Thường · Cao (PR trước 06/11: Thấp · Vừa · Cao) | máy, từ kết luận của cổng trên PR đó |

**8.3 Đo — máy đọc nhãn, không đếm tay.**
`GH_TOKEN=... python3 nghiem-thu/do_vong.py --repo chu/repo --ngay 30` chỉ gọi GET, ra bảng Markdown để dán vào issue `xet-vong`: năm số của mục 5 và bảng «lỗi lọt theo mức nặng · khâu». `[ĐÃ KIỂM: chạy trên comitorai/vibe8 · 05/11; 10 test ở nghiem-thu/tests/test_do_vong.py]`
- Số nào dưới ngưỡng «đủ để kết luận» của mục 5 thì bảng ghi «chưa đủ mẫu».
- PR thuộc kỳ khi mở hoặc merge trong kỳ. Issue `loi-lot` thiếu hoặc viết lệch dòng `pr-gay-loi` được liệt kê riêng, không đoán.
- **Độ đúng:** lý do chặn đọc từ mục «Lý do» của check `cong-cuoi` trên mọi commit của PR (mục «Chi tiết» là phân loại rủi ro, không tính). Người duyệt thấy chặn oan thì gắn nhãn `chan-oan` lên PR; mọi lý do chặn của PR đó tính là oan. Nhãn do chính tác giả PR gắn thì không tính và được liệt kê.
- **Thời gian ra** tính mở PR → merge, vì repo chưa có bước phát hành riêng.
- **Token:** agent chạy `GH_TOKEN=... python3 nghiem-thu/ghi_token.py --repo chu/repo` sau khi đẩy commit cuối và một lần nữa ngay trước khi merge. Script đọc bản ghi phiên Claude Code và Codex trên máy, cộng token mới của các lượt gọi trong repo theo nhánh của PR, ghi vào một comment có dấu `token-may-ghi`; việc làm ở `main` trước khi tạo nhánh tính cho nhánh đó. Mỗi máy một dòng. `do_vong.py` lấy trung vị trên PR merge có comment, liệt kê PR merge chưa có, và chỉ tin comment của người trong repo. Codex có dòng riêng `<máy> codex` và cả phiên tính cho nhánh lúc mở phiên, vì Codex chỉ ghi nhánh lúc đó. Lượt tóm tắt ngữ cảnh chưa tính; người có quyền ghi vẫn sửa tay được comment.
- **Giới hạn:** mỗi danh sách đọc 100 mục mới nhất (bảng cảnh báo khi chạm trần); PR sửa gấp mà không có issue hay Revert thì máy không thấy; người có quyền ghi vẫn gỡ được nhãn `loi-lot`, hạ mức nặng hay sửa dòng `pr-gay-loi` mà máy không thấy (chỉ `chan-oan` được kiểm người gắn); hai PR chung một SHA thì lượt check của SHA đó tính cho cả hai.

**8.4 Xét và đề xuất.**
- **Lịch:** 14 ngày một lần, việc định giờ chạy script và mở issue `xet-vong` kèm bảng số. Luật nào tới ngày ở cột «Xét» của mục 3 thì xét trong buổi đó. Script không chạy được thì hoãn buổi xét, không đoán số.
- **Không chờ lịch:** mỗi lỗi N1 có buổi xét riêng trong 3 ngày, tìm khâu hở, không tìm người có lỗi.
- **Mỗi buổi tối đa 3 đề xuất**, ưu tiên khâu có nhiều lỗi N1 và N2 nhất. Mỗi đề xuất ghi: khâu hở và các issue làm căn cứ · thay đổi gì (sửa máy, thêm, sửa hay bỏ luật) · đủ bốn thứ của mục 1 · tốn thêm bao nhiêu token và thời gian.
- **Sửa máy trước, thêm chữ sau:** khâu hở mà cổng hoặc test chặn được thì sửa cổng hoặc test, không thêm luật.
- Đề xuất đi qua PR sửa file này, mức Cao, người duyệt chốt.
- **Kỳ không có lỗi lọt nào:** trước khi kết luận tốt, đối chiếu các PR sửa gấp trong kỳ với sổ; có PR sửa gấp mà không có issue thì sổ đang bị bỏ sót.
