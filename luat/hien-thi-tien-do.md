# Hiển thị tiến độ — một khuôn cho mọi dự án (bản thí điểm, 08/11/2026)

Áp cho mọi repo cài vibe8. `phuong-phap.md` lo **một PR**, `kien-truc.md` lo **cả đường đi**; tệp này lo **cách nhìn thấy đường đi**: tới đâu, khoẻ hay không, ai đang chờ ai, làn nào kẹt.
Nhãn căn cứ như `phuong-phap.md`. Chủ dự án (Alex) chốt 08/11: áp cho cả sản phẩm có giao diện lẫn thanh bên phiên (1c), sức khoẻ ba màu (2b), «Chờ bạn» là cờ chứ không là trạng thái (3a), trạng thái xong tên «Hoàn thành» (4a), cập nhật 3 mốc mỗi ngày kể cả cuối tuần (5d, 1b), làn viết và người xác nhận (2a); % = xong ÷ (tổng − huỷ) (2a); sổ phase đổi từ vựng theo tệp này (4a).

**Trạng thái: thí điểm.** Mọi mục là quy trình và lời dặn, chưa là luật của `phuong-phap.md` §3. Đề xuất L13 (máy đo trong `hien-thi/`, mức giữ và bỏ, xét ngày 06/12/2026) đi PR sau, theo §1 của tệp đó. Mã `HT-…` để review và test trỏ tới.

## 0. Cam kết

1. Mở một màn, trong **≤ 10 giây** biết giai đoạn nào Chậm, Có rủi ro, Thiếu cập nhật hay đang chờ chủ dự án. Đo: chủ dự án bấm giờ trên 3 dự án.
2. **0 con số tiến độ do làn tự khai.** %, tuổi, dự báo tính từ sổ phase và GitHub, khớp L10.
3. Mỗi mốc 08:30 · 11:30 · 17:30, **100%** giai đoạn đang mở có câu cập nhật; lỡ 2 mốc liền thì máy đánh «Thiếu cập nhật».
4. Một trạng thái **một tên**, trên mọi dự án, mọi màn, mọi ngôn ngữ.

## 1. Bốn cấp hiển thị

| Cấp hiển thị | Đơn vị việc (`kien-truc.md` mục 1) | % tính trên |
|---|---|---|
| Tổng thể | Project; hoặc một luồng việc khi xem riêng luồng đó (vỏ `📂 <MÃ>`) | task của mọi giai đoạn đang mở |
| Module | Module; các giai đoạn của cùng một luồng việc gom thành nhóm bên trong | task của mọi giai đoạn đang mở trong module |
| Giai đoạn | Phase | task trong sổ phase |
| Việc | Task | không có %; có làn đang chạy thì tô theo bước k/n (mục 5) |

PR và Phiên không phải cấp hiển thị: PR là chip trên hàng Việc; phiên làm task (làn) có hàng riêng ở mục 5.

## 2. Khuôn hàng và ký hiệu

- **HT-01 Một khuôn hàng cho mọi cấp.** Dòng 1 là danh tính: vòng trạng thái · vạch ưu tiên · tên · cờ · nhãn sức khoẻ kèm tuổi. Dòng 2 là câu cập nhật mới nhất kèm tuổi, thanh tiến độ, «phạm vi ±n», dự báo. Cùng loại tín hiệu luôn ở cùng chỗ.
- **HT-02 Một kênh, một nghĩa.** Hình của vòng là trạng thái · phần tô trong vòng là % xong · màu là sức khoẻ · vạch là ưu tiên · màu nhấn là «cần bạn». Không kênh nào mang hai nghĩa.
- **HT-03 Màu không đứng một mình.** Mọi màu đi kèm chữ hoặc hình (WCAG 2.2 — chuẩn trợ năng web của W3C — mục 1.4.1).
- **HT-04 Con chỉ hiện phần khác cha.** Không lặp sản phẩm, mã, repo, máy khi đã giống hàng cha; làn chạy ở máy khác cha thì hiện tên máy.
- **HT-10 Một loại trạng thái, một tên.** Bảng dưới là tên duy nhất; «đã xong» chỉ dùng trong câu đếm («12 việc đã xong»), không làm nhãn.

| Trạng thái | Cấp | Nghĩa | Từ cũ trong sổ phase |
|---|---|---|---|
| Tiếp nhận | Việc | chờ phân loại | — |
| Tồn đọng | Việc | chưa xếp lịch | — |
| Chưa bắt đầu | mọi cấp | đã xếp, chưa làm | `chờ` |
| Đang làm | mọi cấp | vòng tô theo % xong | `đang làm`; `chờ duyệt` thành Đang làm + cờ Chờ duyệt |
| Tạm dừng | Tổng thể, Module | dừng có chủ đích | — |
| Hoàn thành | mọi cấp | xong | `xong` |
| Đã huỷ | mọi cấp | ra khỏi mẫu số | task gốc đã `tách → Tx.a, Tx.b` (ghi ở cột Ghi chú) |
| Chưa có số | mọi cấp | chưa nối dữ liệu | — |

**Sức khoẻ:** Chưa đánh giá (màu mực) · Đúng hướng (xanh) · Có rủi ro (vàng) · Chậm (đỏ). Luôn kèm tuổi (HT-11).
**Ưu tiên:** Khẩn (P0, ô vuông có «!») · Cao (P1) · Vừa (P2) · Thấp (P3) · Không đặt. Mức cao nhất chỉ gọi là «Khẩn».
**Cờ** gắn lên trạng thái, không thay nó; việc giữ trạng thái và % của nó:

| Cờ | Khi nào | Màu |
|---|---|---|
| Chờ bạn | người đang xem phải làm gì đó: duyệt PR Cao, trả lời Cổng | màu nhấn |
| Chờ duyệt | PR đã có phiếu không bác, chờ người duyệt | trung tính |
| Chờ CI | chờ máy | trung tính |
| Bị chặn | chờ task khác merge | trung tính |
| Lệch | nhãn Đúng hướng mà dự báo 85% sau hạn (HT-07) | đỏ |
| Thiếu cập nhật | lỡ 2 mốc liền (HT-11) | xám |

## 3. Con số

- **HT-05 Tiến độ = xong ÷ (tổng − huỷ), kèm phạm vi.** Có điểm ước lượng thì tính theo điểm. Task Đang làm không cộng nửa: vẽ thành đoạn riêng trên thanh. Số task khác số lúc mở Cổng 2 thì ghi «phạm vi +n» (hay «−n») cạnh %. Biểu đồ dùng burn-up (giải nghĩa: đường việc xong cộng dồn đặt cạnh đường tổng phạm vi), không dùng burn-down, để thấy % tụt vì phạm vi tăng chứ không vì chậm.
- **HT-06 Dự báo là một khoảng; không dữ liệu thì không vẽ.** Ngày xong ở mức 50% và 85%, đặt cạnh hạn, ghi «dự báo». Tính bằng Monte Carlo (giải nghĩa: lấy mẫu ngẫu nhiên lặp nhiều lần) trên số task Hoàn thành mỗi ngày của 14 ngày gần nhất. Dưới 7 ngày lịch sử thì không dự báo; không có mẫu số thì không có thanh.
- **HT-07 Người chốt, máy đối chiếu.** Sức khoẻ do người chốt, kèm một câu lý do. Máy không tự sửa nhãn; dự báo 85% sau hạn mà nhãn vẫn Đúng hướng thì hiện cờ «Lệch».
- **HT-08 Cha nổi ngoại lệ, gập cái đã yên.** Hàng cha đếm con Chậm, Có rủi ro, Thiếu cập nhật, Chờ bạn; không lấy trung bình sức khoẻ của con. Con Hoàn thành gập thành một dòng đếm.
- **HT-12 Đứng yên là tín hiệu.** Giai đoạn đang mở mà ≥ 2 ngày lịch không có task Hoàn thành thì hàng ghi «đứng yên n ngày» `[SUY LUẬN từ trần task ≤ 1 ngày, kien-truc.md mục 1; ngưỡng chưa đo]`. Đứng yên nghĩa là cần giúp, không phải là ổn.

Căn cứ `[ĐÃ KIỂM: tài liệu công khai · 08/11]`: Plane loại task huỷ khỏi mẫu số; Linear vẽ đường phạm vi và dự báo có biên, làm xám dự án lâu không cập nhật; Scrum.org, ProKanban dùng mức 85% thay vì 50%; «ngoài xanh trong đỏ» (hiệu ứng dưa hấu) ghi ở ≥ 3 nguồn độc lập.

## 4. Cập nhật ba mốc

- **Mốc:** 08:30 · 11:30 · 17:30 theo giờ của chủ dự án, mọi ngày kể cả cuối tuần.
- **Ai viết:** Điều phối của luồng việc, cho từng giai đoạn đang mở; giai đoạn không có Điều phối thì phiên đang giữ nó.
- **HT-09 Dòng 2 viết cho người, có tuổi.** Một câu bắt đầu bằng việc vừa xảy ra («T3 merge, còn 2 task, T4 chờ CI»), kèm tuổi. Không dán log máy; chưa có câu thì ghi «Chưa có câu cập nhật».
- **Ở đâu:** comment trên issue theo dõi của giai đoạn (nhãn `phase`; số issue ghi ở đầu sổ phase). Giờ của câu là giờ GitHub ghi comment, không phải giờ tự khai; không cần PR nên không tốn lượt cổng. Chỉ tính comment của người có quyền ghi trên repo. Khuôn để máy đọc, mỗi dòng đứng đầu dòng:
  ```
  cap-nhat: <câu dòng 2>
  suc-khoe: dung-huong | co-rui-ro | cham
  ly-do: <một câu>
  ```
- **Xác nhận:** chủ dự án bấm 👍 trên comment (một chạm, làm được trên điện thoại); muốn đổi thì trả lời bằng dòng `suc-khoe:` và `ly-do:` mới. Chưa bấm thì nhãn vẫn hiện, kèm chữ «chưa xác nhận». Xác nhận không phải câu hỏi giữa phase (`kien-truc.md` mục 7): không bấm thì việc vẫn chạy.
- **HT-11 Sức khoẻ có hạn dùng.** Tuổi tính từ comment cập nhật mới nhất. Qua 1 mốc không có comment mới: viền đứt. Qua 2 mốc liền: xám, ghi «Thiếu cập nhật».
- **Chỉ ngoại lệ mới báo về điện thoại:** Chậm, Lệch, Thiếu cập nhật, Chờ bạn, cờ mức Kẹt của mục 5.

## 5. Hàng làn

- **HT-13 Làn phải có nhịp tim và bước.** Mỗi làn hiện: hành động cuối cách đây bao lâu, đã chạy bao lâu, bước k/n trong kế hoạch của nó, đang chờ gì (CI, duyệt, chủ dự án, chạy nền). Số lấy từ transcript (giải nghĩa: bản ghi nguyên văn phiên) trên máy chạy làn, từ tmux và GitHub; không lấy lời làn tự khai.
- **Nhịp tim:** chạy (hành động cuối ≤ 5 phút) · lặng (> 5 phút, không chờ gì) · chờ (đang chờ CI, duyệt, chủ dự án) · im (K1) · đã dừng (phiên kết thúc).
- **Khuôn hàng** theo HT-01: dòng 1 vòng tô theo k/n, tên, máy, chip chờ kèm số phút, nhịp tim; dòng 2 câu của làn kèm tuổi, thanh bước; có cờ thì thêm một dòng cờ kèm lý do; dòng cuối thời gian đã chạy · ngữ cảnh · bước đang làm · PR.

| Cờ | Khi nào | Mức |
|---|---|---|
| K1 | không chờ gì mà im > 20 phút | Kẹt |
| K2 | một bước kéo dài > 45 phút | Kẹt |
| K3 | chờ CI > 30 phút | Rủi ro |
| K4 | cùng một lỗi lặp ≥ 3 lần trong 50 lượt gần nhất | Kẹt |
| K5 | ngữ cảnh ≥ 120 nghìn token: Rủi ro · ≥ 150 nghìn: Kẹt, Thay làn (`vai/dieu-phoi.md` §5); Điều phối theo ngưỡng «> 80 % cửa sổ» của chính nó | Rủi ro / Kẹt |
| Chưa có kế hoạch | làn chưa lập danh sách bước | Rủi ro |
| Xong bước, chưa đóng | đủ k/n bước mà phiên chưa đóng | Rủi ro |

Ngưỡng khoá 08/11, đo 1 tuần trên làn thật rồi chủ dự án xét. Mỗi cờ báo Điều phối ngay; cờ mức Kẹt báo điện thoại, không chờ tới mốc.

## 6. Áp vào một repo

1. Sổ phase theo `mau/phase.md`: từ vựng của mục 2, cột Cờ, đầu sổ có phạm vi lúc mở Cổng 2 và số issue cập nhật. Sổ đang chạy đổi từ ở lần sửa sổ kế tiếp; tới ngày xét, máy đọc cả từ cũ theo cột «Từ cũ» của mục 2. Bảng thao tác ở `vai/dieu-phoi.md` §5 còn ghi `đang làm`, `xong`: đọc theo cột đó, sửa chữ ở một PR riêng.
2. Thêm dòng `Chuẩn hiển thị: bản 2` vào `CLAUDE.md` và `AGENTS.md`, cạnh dòng trỏ của `kien-truc.md` mục 15, để máy biết repo áp bản nào.
3. Repo có sản phẩm giao diện riêng thì áp tệp này vào sản phẩm; cập nhật lưu trong sản phẩm, miễn giữ ba điều: giờ do máy ghi, người xác nhận được, máy đọc được.
4. Thanh bên phiên của app không sửa được giao diện: áp qua tên phiên (luật của repo chủ dự án) và trang do `hien-thi/` xuất.

## 7. Máy kiểm và lời dặn

| Kiểm | Loại | Có chưa |
|---|---|---|
| %, phạm vi, tuổi, dự báo, Lệch, đứng yên tính từ sổ phase, issue cập nhật và GitHub; xuất trang theo khuôn | `hien-thi/` | chưa — PR sau |
| Nhắc 3 mốc | launchd (giải nghĩa: bộ khởi chạy và lập lịch việc nền của macOS) trên máy chạy 24/24 | chưa — PR sau |
| Nhịp tim, bước k/n, K1–K5 của làn | `hien-thi/` đọc transcript, tmux, GitHub | chưa có máy; đã chạy tay một lần trên 7 làn thật `[ĐÃ KIỂM: nội bộ · 08/11]` |
| Comment cập nhật đúng khuôn, đúng giờ | `hien-thi/` báo, không chặn | chưa |
| HT-01…HT-04, HT-10 trên giao diện | test của sản phẩm áp dụng | theo từng repo |

Trước khi có máy, các mục trên là lời dặn: Điều phối tự viết comment ba mốc. Kết luận sớm khi đóng phase đầu tiên áp tệp này; L13 xét ngày 06/12/2026.
