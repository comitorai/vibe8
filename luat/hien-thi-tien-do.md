# Hiển thị tiến độ — một khuôn cho mọi dự án (bản thí điểm, 08/11/2026)

Áp cho mọi repo cài vibe8. `phuong-phap.md` lo **một PR**, `kien-truc.md` lo **cả đường đi**; tệp này lo **cách nhìn thấy đường đi**: tới đâu, khoẻ hay không, ai đang chờ ai, làn nào kẹt.
Nhãn căn cứ như `phuong-phap.md`. Chủ dự án (Alex) chốt 08/11 qua ba lượt hỏi:
- **Chuẩn:** áp cho cả sản phẩm có giao diện lẫn thanh bên phiên; sức khoẻ ba màu; «Chờ bạn» là cờ, không là trạng thái; trạng thái xong tên «Hoàn thành»; cập nhật 3 mốc mỗi ngày.
- **Nhịp:** 3 mốc cả cuối tuần; AI viết cập nhật, người xác nhận.
- **Áp vào vibe8:** mục nào muốn thành luật thì có máy đo, hẹn xét 06/12/2026; % = xong ÷ (tổng − huỷ); công cụ chung ở `hien-thi/`; sổ phase đổi từ vựng theo tệp này.

**Trạng thái: thí điểm.** Mọi mục là quy trình và lời dặn, chưa là luật của `phuong-phap.md` §3. Đề xuất L13 (máy đo trong `hien-thi/`, mức giữ và bỏ) đi PR sau theo §1 của tệp đó; khi vào bảng §3, cột Xét tính như các luật khác. Mã `HT-…` để review và test trỏ tới.

## 0. Cam kết

1. Mở một màn, trong **≤ 10 giây** biết giai đoạn nào Chậm, Có rủi ro, Thiếu cập nhật hay đang chờ chủ dự án. Đo: chủ dự án bấm giờ trên 3 dự án.
2. **0 con số tiến độ do làn tự khai.** %, phạm vi, tuổi, dự báo và vòng của Việc tính từ sổ phase, lịch sử git của sổ và GitHub, khớp L10. Bước k/n do làn tự lập chỉ hiện dạng chữ, có nhãn «tự khai» (mục 5).
3. Mỗi mốc 08:30 · 11:30 · 17:30, **100%** giai đoạn đang mở có câu cập nhật; lỡ 2 mốc liền thì máy đánh «Thiếu cập nhật».
4. Một trạng thái **một tên** trên mọi dự án, mọi màn; mỗi ngôn ngữ một tên, theo các bảng ở mục 2.

## 1. Bốn cấp hiển thị

| Cấp hiển thị | Đơn vị việc (`kien-truc.md` mục 1) | % tính trên |
|---|---|---|
| Tổng thể | Project | task của mọi giai đoạn đang mở |
| Module | Module; bên trong, giai đoạn của cùng một luồng việc gom thành một nhóm | task của mọi giai đoạn đang mở trong module |
| Giai đoạn | Phase | task trong sổ phase |
| Việc | Task | không có %; vòng tô theo 5 mốc GitHub (mục 5) |

Xem riêng một luồng việc (vỏ `📂 <MÃ>`) thì nhóm của luồng đó đứng đầu màn, vẫn theo khuôn hàng. PR và Phiên không phải cấp hiển thị: PR là chip trên hàng Việc; phiên làm task (làn) có hàng riêng ở mục 5.

## 2. Khuôn hàng và ký hiệu

- **HT-01 Một khuôn hàng cho mọi cấp.** Dòng 1 là danh tính: vòng trạng thái · vạch ưu tiên · tên · chip cờ · nhãn sức khoẻ kèm tuổi. Dòng 2 là câu cập nhật mới nhất kèm tuổi, thanh tiến độ, «phạm vi ±n», dự báo. Cùng loại tín hiệu luôn ở cùng chỗ.
- **HT-02 Mỗi kênh một nghĩa.** Hình của vòng là trạng thái · phần tô trong vòng là % xong · màu của vòng và nhãn là sức khoẻ · viền nhãn là tuổi (liền: còn hạn, đứt: lỡ 1 mốc) · vạch là ưu tiên · chip cờ là chờ gì, nghĩa nằm ở chữ. Nhãn hết hạn thì xám, vì màu cũ không còn là sức khoẻ thật. Chip cờ chỉ có ba màu: màu nhấn (cần bạn), trung tính (đang chờ), đỏ cho «Lệch» (báo sức khoẻ thật có thể là Chậm).
- **HT-03 Màu không đứng một mình.** Mọi màu đi kèm chữ hoặc hình (WCAG 2.2 — chuẩn trợ năng web của W3C — mục 1.4.1).
- **HT-04 Con chỉ hiện phần khác cha.** Không lặp sản phẩm, mã, repo, máy khi đã giống hàng cha; làn chạy ở máy khác cha thì hiện tên máy.
- **HT-10 Một loại trạng thái, một tên.** Bảng dưới là tên duy nhất; «đã xong» chỉ dùng trong câu đếm («12 việc đã xong»), không làm nhãn.

| Trạng thái | English | Cấp | Nghĩa | Từ cũ trong sổ phase |
|---|---|---|---|---|
| Tiếp nhận | Triage | Việc | chờ phân loại | — |
| Tồn đọng | Backlog | Việc | chưa xếp lịch | — |
| Chưa bắt đầu | Todo | mọi cấp | đã xếp, chưa làm | `chờ` |
| Đang làm | In progress | mọi cấp | vòng tô theo % xong | `đang làm`; `chờ duyệt` (cờ Chờ duyệt do máy tính) |
| Tạm dừng | Paused | Tổng thể, Module | dừng có chủ đích | — |
| Hoàn thành | Done | mọi cấp | xong; giai đoạn: Cổng 3 đạt | `xong` |
| Đã huỷ | Canceled | mọi cấp | ra khỏi mẫu số; giai đoạn: Cổng 3 bỏ | task gốc đã `tách → Tx.a, Tx.b`; task đã `gộp vào Ty` |
| Chưa có số | No data | mọi cấp | chưa nối dữ liệu | — |

Đã huỷ phải có bằng chứng ở cột Ghi chú: `tách → …`, `gộp vào Ty`, `phiếu <số>` (phiếu đổi yêu cầu) hay PR đóng không merge; máy liệt kê dòng Đã huỷ thiếu bằng chứng.

**Sức khoẻ:** Chưa đánh giá · Not assessed (màu mực) · Đúng hướng · On track (xanh) · Có rủi ro · At risk (vàng) · Chậm · Off track (đỏ). Luôn kèm tuổi (HT-11).
**Ưu tiên:** Khẩn · Urgent (P0, ô vuông có «!») · Cao · High (P1) · Vừa · Medium (P2) · Thấp · Low (P3) · Không đặt · No priority. Mức cao nhất chỉ gọi là «Khẩn».
**Cờ** gắn lên trạng thái, không thay nó; việc giữ trạng thái và % của nó:

| Cờ | English | Khi nào | Ai tính | Màu chip |
|---|---|---|---|---|
| Chờ bạn | Needs you | người đang xem là người phải làm: duyệt PR Cao đang Chờ duyệt, trả lời Cổng | màn hình, theo người xem; không ghi vào sổ | màu nhấn |
| Chờ duyệt | Awaiting review | PR Cao có phiếu không bác trên head SHA, `cong-cuoi` còn báo `chan (cao)` | máy, từ PR | trung tính |
| Chờ CI | Waiting on CI | lượt `cong-nhanh` trên head SHA chưa xong | máy, từ PR | trung tính |
| Chờ task khác | Waiting on task | cần task khác merge trước | Điều phối ghi mã task ở cột «Chờ task» của sổ | trung tính |
| Lệch | Mismatch | nhãn Đúng hướng mà dự báo 85% sau hạn (HT-07) | máy | đỏ |
| Thiếu cập nhật | Update missing | lỡ 2 mốc liền (HT-11) | máy | xám |

Người xem là người phải duyệt thì thấy Chờ bạn thay cho Chờ duyệt; người khác thấy Chờ duyệt. Sổ lệch GitHub thì tin GitHub; máy báo dòng lệch.

## 3. Con số

- **HT-05 Tiến độ = xong ÷ (tổng − huỷ), kèm phạm vi.** Có điểm ước lượng thì tính theo điểm. Task Đang làm không cộng nửa: vẽ thành đoạn riêng trên thanh. «Phạm vi ±n» đếm task thêm hay huỷ vì phiếu đổi yêu cầu (`kien-truc.md` mục 11; Ghi chú `phiếu <số>`); tách và gộp không đổi phạm vi. Đường phạm vi của biểu đồ là (tổng − huỷ) qua lịch sử git của sổ, máy đọc từ commit đầu tiên sau 5b. Biểu đồ dùng burn-up (giải nghĩa: đường việc xong cộng dồn đặt cạnh đường tổng phạm vi), không dùng burn-down, để thấy % tụt vì phạm vi tăng chứ không vì chậm.
- **HT-06 Dự báo là một khoảng; không dữ liệu thì không vẽ.** Ngày xong ở mức 50% và 85%, đặt cạnh hạn, ghi «dự báo». Tính bằng Monte Carlo (giải nghĩa: lấy mẫu ngẫu nhiên lặp nhiều lần) trên số task Hoàn thành mỗi ngày của luồng việc chứa giai đoạn, 14 ngày gần nhất; luồng có dưới 7 ngày lịch sử thì không dự báo. Không có mẫu số thì không có thanh.
- **HT-07 Người chốt, máy đối chiếu.** Sức khoẻ do người chốt, kèm một câu lý do. Máy không tự sửa nhãn; dự báo 85% sau hạn mà nhãn vẫn Đúng hướng thì hiện cờ «Lệch».
- **HT-08 Cha nổi ngoại lệ, gập cái đã yên.** Hàng cha đếm con Chậm, Có rủi ro, Lệch, Thiếu cập nhật và (theo người xem) Chờ bạn; không lấy trung bình sức khoẻ của con. Con Hoàn thành gập thành một dòng đếm.
- **HT-12 Đứng yên là tín hiệu.** Giai đoạn đang mở mà ≥ 2 ngày lịch không có task Hoàn thành thì hàng ghi «đứng yên n ngày» `[SUY LUẬN từ trần task ≤ 1 ngày, kien-truc.md mục 1; ngưỡng chưa đo]`. Đứng yên nghĩa là cần giúp, không phải là ổn.

Căn cứ `[ĐÃ KIỂM: đọc tài liệu công khai · 08/11]`:
- Plane bỏ task huỷ khỏi mẫu số của module: https://docs.plane.so/core-concepts/modules
- Linear vẽ đường phạm vi và dự báo có biên: https://linear.app/docs/project-graph ; làm xám dự án thiếu cập nhật: https://linear.app/docs/initiative-and-project-updates
- Dự báo ở mức 85%: https://prokanban.org/kanban-playbook/forecasting-delivery , https://www.scrum.org/resources/blog/release-planning-done-scrum-managing-stakeholder-expectations-forecasting
- «Ngoài xanh trong đỏ» (hiệu ứng dưa hấu): https://learn.microsoft.com/en-us/archive/blogs/anitag/theres-no-room-for-watermelons , https://builtin.com/articles/poisonous-watermelon-project-management-fable , https://eleco.com/pm3/knowledge-centre/is-your-project-a-watermelon-project-or-a-kiwi-fruit/
- Đứng yên là xin giúp: https://basecamp.com/shapeup/3.4-chapter-13

## 4. Cập nhật ba mốc

- **Mốc:** 08:30 · 11:30 · 17:30 theo múi giờ của chủ dự án (khai một lần trong cấu hình của `hien-thi/`), mọi ngày kể cả cuối tuần. Comment ghi trong 90 phút sau một mốc thì tính cho mốc đó `[CHƯA CHỐT: chốt cùng máy đo]`.
- **Ai viết:** AI. Điều phối của module viết cho từng giai đoạn đang mở của module (`vai/dieu-phoi.md`: một Điều phối mỗi module); làn chỉ viết dòng 2 của việc nó đang giữ.
- **HT-09 Dòng 2 viết cho người, có tuổi.** Một câu bắt đầu bằng việc vừa xảy ra («T3 merge, còn 2 task, T4 chờ CI»), kèm tuổi. Không dán log máy; chưa có câu thì ghi «Chưa có câu cập nhật».
- **Ở đâu:** comment trên issue theo dõi của giai đoạn (nhãn `phase`; số issue ghi ở đầu sổ phase). Giờ của câu là giờ GitHub ghi comment, không phải giờ tự khai; không cần PR nên không tốn lượt cổng. Chỉ tính comment của người có quyền ghi trên repo. Khuôn để máy đọc, mỗi dòng đứng đầu dòng:
  ```
  cap-nhat: <câu dòng 2>
  suc-khoe: dung-huong | co-rui-ro | cham
  ly-do: <một câu>
  ```
- **Xác nhận:** chủ dự án bấm 👍 trên comment (một chạm, làm được trên điện thoại); muốn đổi thì trả lời bằng dòng `suc-khoe:` và `ly-do:` mới. Chưa bấm thì nhãn vẫn hiện, kèm chữ «chưa xác nhận». Xác nhận không phải câu hỏi giữa phase (`kien-truc.md` mục 7): không bấm thì việc vẫn chạy. Giới hạn: như phiếu phản bác (README, mục Luật), máy không phân biệt chủ dự án với agent dùng chung tài khoản, nên «đã xác nhận» là tín hiệu, không phải hàng rào.
- **HT-11 Sức khoẻ có hạn dùng.** Tuổi tính từ comment cập nhật mới nhất. Qua 1 mốc không có comment mới: viền đứt. Qua 2 mốc liền: xám, ghi «Thiếu cập nhật».
- **Chỉ ngoại lệ mới báo về điện thoại:** Chậm, Lệch, Thiếu cập nhật, Chờ bạn; cờ Kẹt của mục 5 khi Điều phối chưa xử lý sau một mốc, hoặc khi chính Điều phối có cờ Kẹt.

## 5. Hàng làn

- **HT-13 Làn phải có nhịp tim và bước.** Mỗi làn hiện: hành động cuối cách đây bao lâu, đã chạy bao lâu, đang đợi gì (CI, duyệt, task khác, chạy nền), và hai loại tiến độ:
  - **Mốc của việc** (tô vòng): 5 mốc máy thấy trên GitHub — có commit trên nhánh → PR mở → `cong-nhanh` xanh → phiếu không bác trên head SHA → merge. PR Cao hiện cờ Chờ duyệt giữa mốc 4 và 5.
  - **Bước k/n** (chỉ chữ, nhãn «tự khai»): danh sách bước làn tự lập, đọc từ transcript (giải nghĩa: bản ghi nguyên văn phiên). Không tô vòng, không vào %.
  Thời gian, lỗi, ngữ cảnh lấy từ transcript trên máy chạy làn, từ tmux và GitHub.
- **Nhịp tim:** chạy (hành động cuối ≤ 5 phút) · lặng (> 5 phút, không đợi gì) · đợi (đang đợi CI, duyệt, task khác) · im (K1) · đã dừng (phiên kết thúc).
- **Khuôn hàng** theo HT-01: dòng 1 vòng mốc, tên, máy, chip đợi kèm số phút, nhịp tim; dòng 2 câu của làn kèm tuổi, bước k/n «tự khai»; có cờ thì thêm một dòng cờ kèm lý do; dòng cuối thời gian đã chạy · ngữ cảnh · PR.

| Cờ | Khi nào | Mức |
|---|---|---|
| K1 | không đợi gì mà im > 20 phút | Kẹt |
| K2 | một bước tự khai kéo dài > 45 phút; làn chia bước nhỏ thì né được, nên K1 và mốc GitHub là chỗ dựa chính | Kẹt |
| K3 | đợi CI > 30 phút | Cảnh báo |
| K4 | cùng một lỗi lặp ≥ 3 lần trong 50 lượt gần nhất; «cùng lỗi» là cùng tên tool và cùng dòng lỗi đầu, đã bỏ số và đường dẫn `[CHƯA CHỐT: chốt cùng máy đo]` | Kẹt |
| K5 | ngữ cảnh ≥ 120 nghìn token: Cảnh báo · > 150 nghìn: Kẹt, Thay làn (`vai/dieu-phoi.md` §5). Điều phối: > 80 % cửa sổ là Kẹt, bàn giao (`vai/dieu-phoi.md`, Ngưỡng ngữ cảnh) | Cảnh báo / Kẹt |
| Chưa có kế hoạch | làn chưa lập danh sách bước | Cảnh báo |
| Xong bước, chưa đóng | đủ k/n bước tự khai, task không còn PR mở, mà phiên chưa đóng | Cảnh báo |

Ngưỡng khoá 08/11, đo 1 tuần trên làn thật rồi chủ dự án xét. Mỗi cờ báo Điều phối ngay, theo đường báo của `vai/dieu-phoi.md`; đường lên điện thoại ở mục 4.

## 6. Áp vào một repo

1. Sổ phase theo `mau/phase.md`: từ vựng của mục 2, cột «Chờ task», số issue cập nhật ở đầu sổ. Sổ đang chạy đổi từ ở lần sửa sổ kế tiếp; tới ngày xét 06/12/2026, máy đọc cả từ cũ theo cột «Từ cũ» của mục 2. Bảng thao tác ở `vai/dieu-phoi.md` §5 còn ghi `đang làm`, `xong`, `gộp vào Ty`: đọc theo cột đó, sửa chữ ở một PR riêng.
2. Thêm dòng `Hiển thị tiến độ: luat/hien-thi-tien-do.md, bản 08/11/2026` vào `CLAUDE.md` và `AGENTS.md`, cạnh dòng trỏ của `kien-truc.md` mục 15, để máy biết repo áp bản nào.
3. Repo có sản phẩm giao diện riêng thì áp tệp này vào sản phẩm; cập nhật lưu trong sản phẩm, miễn giữ ba điều: giờ do máy ghi, người xác nhận được, máy đọc được.
4. Thanh bên phiên của app không sửa được giao diện: áp qua tên phiên (luật của repo chủ dự án) và trang do `hien-thi/` xuất.

## 7. Máy kiểm và lời dặn

| Kiểm | Loại | Có chưa |
|---|---|---|
| %, phạm vi, tuổi, dự báo, cờ do máy tính, đứng yên; xuất trang theo khuôn | `hien-thi/` đọc sổ, lịch sử git, issue cập nhật, GitHub | chưa — PR sau |
| Nhắc 3 mốc | launchd (giải nghĩa: bộ khởi chạy và lập lịch việc nền của macOS) trên máy chạy 24/24 | chưa — PR sau |
| Nhịp tim, mốc, bước k/n, K1–K5 của làn | `hien-thi/` đọc transcript, tmux, GitHub | chưa có máy; đã chạy tay một lần trên 7 làn thật `[ĐÃ KIỂM: nội bộ · 08/11]` |
| Comment cập nhật đúng khuôn, đúng giờ; Đã huỷ có bằng chứng; sổ khớp GitHub | `hien-thi/` báo, không chặn | chưa |
| HT-01…HT-04, HT-10 trên giao diện | test của sản phẩm áp dụng | theo từng repo |

Trước khi có máy, các mục trên là lời dặn: Điều phối tự viết comment ba mốc. Kết luận sớm khi đóng phase đầu tiên áp tệp này; buổi xét thí điểm ngày 06/12/2026.
