# Kiến trúc làm việc — từ cuộc trò chuyện tới phát hành (bản thí điểm, 06/11/2026)

Áp cho mọi repo cài vibe8. `luat/phuong-phap.md` lo **một PR** (cổng, phiếu, mức); tệp này lo **cả đường đi**: ý tưởng → project, module → phase (giai đoạn) → task → PR → phát hành → bài học.
Nhãn căn cứ như `phuong-phap.md`. Chủ dự án (Alex) chốt 06/11: ba cổng mỗi phase cộng lượt duyệt PR Cao (2a), trần tải ở mục 12 (3a), phiên thảo luận để lại dấu (4a), một vai Điều phối cho mỗi module (1a).

**Trạng thái: thí điểm.** Mọi mục ở đây là quy trình và lời dặn, chưa là luật của `phuong-phap.md` §3. Mục nào muốn thành luật thì đi đường §1 của tệp đó: chặn lỗi gì, máy đo gì, mức giữ và bỏ, ngày xét. Thí điểm trên một phase thật của một module; kết luận sớm lúc đóng phase, kết luận muộn 14 ngày sau phát hành (mục 15).

## 0. Toàn cảnh

```
 Cuộc trò chuyện ─► thẻ ý tưởng ─► [CỔNG 1: làm / để kho / bỏ · sống ở đâu]
                                          │
        ┌─────────────────────────────────┼─────────────────────────────┐
        ▼                                 ▼                             ▼
  project / module mới            luồng việc mới                 task trong phase đang chạy
  (chặng 2: tờ khung)             trong module có sẵn            (xuống thẳng chặng 6)
        └──────────► chặng 3: YÊU CẦU (có SRS → bảng mã · chưa có → đặc tả phase)
                              │
                     chặng 4: THIẾT KẾ (phản biện độc lập) + 5a: ƯỚC LƯỢNG THÔ
                              │
                 [CỔNG 2: mở phase — yêu cầu · thiết kế · ngân sách]  ◄── Điều phối soạn gói
                              │
                     5b: CẮT TASK (mỗi task gắn mã yêu cầu, giữ chỗ tệp)
                              │
                     chặng 6: LÀM → PR → cổng vibe8 (máy + phiếu; mức Cao: người duyệt)
                              │
                 [CỔNG 3: demo trên môi trường thử — đóng phase]
                              │
                     chặng 7: PHÁT HÀNH THEO BẬC → chặng 8: ĐO VÀ HỌC ─► về chặng 0
```

Hai đường phụ: **đường khẩn** cho lỗi đang hại người dùng (mục 10) và **phiếu đổi yêu cầu** khi yêu cầu đổi giữa phase (mục 11).
Giữa các cổng, các vai AI tự đi; vai viết không bao giờ tự duyệt việc của mình.

## 1. Sáu đơn vị việc, và phiên

| Tầng | Là gì | Phép thử | Ai mở, đóng |
|---|---|---|---|
| Project (dự án) | thứ bán hoặc dùng được riêng, có thể nhiều repo | có tên trong danh sách dự án của chủ dự án | chủ dự án |
| Module | phần của project, phát hành và đo được riêng, thường là một repo | có tệp điều kiện bán được (L11) | chủ dự án |
| Luồng việc (mã, vd `ABC-7`) | mục tiêu dài hơi của một module, qua nhiều phase; mã giữ suốt luồng | trả lời được «xong luồng thì module có gì mới» | chủ dự án mở, AI đề xuất đóng |
| Phase | một mốc kiểm được bằng máy hay demo, ≤ 2 tuần lịch; không cấp mã mới | có một câu «xong khi…» và một buổi nghiệm thu | Cổng 2 mở, Cổng 3 đóng |
| Task | một làn, một nhánh, một PR (L9), ≤ 1 ngày; việc cần nhiều PR thì tách task con | có 3–5 dòng tiêu chí nghiệm thu | Điều phối mở trong phase đã duyệt |
| PR | đơn vị cổng kiểm, ≤ 400 dòng mã (L2; mức Thường không tính dòng test, mức Cao tính đủ) | `cong-cuoi` đọc được | AI mở; máy hay người cho merge theo mức |
| Phiên | một lần AI chạy, **không** phải đơn vị việc; một phiên làm một task | — | — |

## 2. Chặng 0 — Cuộc trò chuyện để lại dấu

Phiên bàn ý tưởng kết thúc thì ý tưởng nằm lại trong transcript, không ai nhặt `[SUY LUẬN từ hộp thư chưa có luật bắt phiên thảo luận ghi vào]`. Vì vậy **mọi phiên thảo luận, khi đóng, để lại đúng một trong ba thứ**:

| Phiên đã sinh ra | Để lại | Ở đâu |
|---|---|---|
| ý tưởng mới (sản phẩm, module, tính năng, cách làm) | thẻ ý tưởng, mẫu `mau/the-y-tuong.md` | hộp thư của chủ dự án, mục Ý tưởng |
| quyết định về thứ đã có | một dòng quyết định kèm vì sao | `docs/DECISIONS.md` của repo đó |
| chỉ hỏi đáp | không gì | — |

**Thư ký hộp thư** gom thẻ, gộp thẻ trùng, nhắc thẻ đứng yên quá 14 ngày, đưa thẻ có độ chín «đủ để qua cổng» ra Cổng 1. Thẻ thô bàn tiếp ở phiên khác thì sửa thẻ cũ, không tạo thẻ mới.

## 3. Cổng 1 — Làm hay không, và nó sống ở đâu

*Người thẩm định* trả lời 6 câu (Ai dùng · Đo bằng gì · Trùng gì · Tốn gì · Dừng khi nào · Có đụng AI) và **câu 7: sống ở đâu**, có nhãn căn cứ. Chủ dự án chọn **làm / để kho / bỏ** và xác nhận câu 7; đây là câu hỏi duy nhất ở chặng này.

| Câu 7 | Đi tới |
|---|---|
| project mới · module mới | chặng 2 |
| luồng việc mới trong module có sẵn (cấp mã mới) | chặng 3 |
| task vừa với tiêu chí phase đang chạy | chặng 6, không qua cổng |
| thêm phạm vi nhưng ngoài phase đang chạy | hàng chờ **phase sau** của luồng đó, xét ở Cổng 2 kế tiếp; không chen vào phase đang chạy |
| ý kiến về cách làm (quy trình, luật) | vòng cải tiến, `phuong-phap.md` §8 |

## 4. Chặng 2 — Tờ khung (chỉ project hoặc module mới)

Một trang `docs/khung.md`, mẫu `mau/to-khung.md`: mục tiêu, người dùng, điều kiện bán được (L11), ranh giới (cái gì **không** thuộc module), mức dữ liệu, vùng Cao khai vào `cong/vung-nhay-cam.txt`. *Phân tích viên* viết, *phản biện* đọc lạnh. Chủ dự án duyệt cùng Cổng 2 của phase đầu, không thêm điểm chạm.

## 5. Chặng 3 — Yêu cầu, hai đường

Mục đích: viết đúng thứ cần làm, mỗi yêu cầu một **mã ổn định** để task, PR và test trỏ về.

**Đường A — đã có SRS (đặc tả yêu cầu phần mềm) hay đặc tả có mã.**
- Không viết lại SRS. Mã đã có trong SRS thì dùng thẳng. SRS chưa có mã thì lập bảng mã riêng `docs/ma-yeu-cau.md` (mẫu `mau/ma-yeu-cau.md`): mã · trỏ về mục SRS · một câu. Cần mịn hơn thì thêm hậu tố (`F.1.4.a`).
- SRS có thể cũ hơn code. Trước khi dựa vào, chạy characterization test (giải nghĩa: test ghi lại hành vi hiện có của code, để sửa không làm đổi nó ngoài ý muốn) ở phần sắp sửa, và ghi chỗ SRS lệch code.

**Đường B — chưa có SRS.**
- Đặc tả phase 1–2 trang, mẫu `mau/dac-ta-phase.md`, chỉ cho phạm vi phase: không viết SRS cho cả hệ thống trước.
- Mở đầu bằng 5 dòng «khách được gì» và 3–5 câu hỏi khó, kiểu PR/FAQ (giải nghĩa: viết như thể sản phẩm đã ra, kèm câu khách sẽ hỏi).
- Mỗi yêu cầu theo mẫu EARS (giải nghĩa: cú pháp câu yêu cầu có khuôn): «Khi <sự kiện>, hệ thống phải <phản ứng>», «Nếu <lỗi> thì hệ thống phải…»; mã `YC-<số>`. Yêu cầu tích luỹ qua các phase thành `docs/yeu-cau.md`.

*Phản biện yêu cầu* (ngữ cảnh sạch) tìm chỗ mơ hồ, mâu thuẫn, thiếu ca lỗi. **Ra chặng khi:** mọi yêu cầu trong phạm vi có mã, có ít nhất một tiêu chí kiểm được, phản biện không còn ý «chặn».
**Đây là lúc thư ký hộp thư giao việc cho Điều phối** (`luat/vai/dieu-phoi.md`).

## 6. Chặng 4 — Thiết kế

| Cỡ | Ở đâu | Dài |
|---|---|---|
| Vừa | mục «Thiết kế» trong đặc tả phase | ≤ 1 trang |
| Lớn, hoặc chạm dữ liệu khách, tiền, đăng nhập, schema chính | `docs/thiet-ke/<ten>.md`, mẫu `mau/thiet-ke.md` | ≤ 6 trang |

Bắt buộc có: mục tiêu và **không-mục-tiêu** · phương án chọn · **phương án đã loại và vì sao** · rủi ro · cách quay lui · ước token. Đã có tài liệu thiết kế thì chỉ ghi phần thay đổi và trỏ về mục gốc.
*Kiến trúc sư* viết; *phản biện thiết kế* là vai khác, ngữ cảnh sạch. Chủ dự án không duyệt chi tiết kỹ thuật, chỉ quyết điểm **khó đảo ngược** mà phản biện gắn cờ, và quyết ở Cổng 2.

## 7. Cổng 2 — Mở phase (5a ước lượng, 5b cắt task)

**5a, trước cổng:** Điều phối ước số task, token, số PR Cao từ yêu cầu và thiết kế, rồi soạn gói một trang (mẫu `mau/goi-cong-2.md`) **từ tài liệu gốc**, không từ lời tóm của vai viết. Gói có: phase xong khi nào (một câu kiểm được) và hạn ≤ 2 tuần · mã yêu cầu trong phạm vi · 1–3 điểm khó đảo ngược dạng chọn nhanh · ngân sách · ý còn lại của phản biện.

Chủ dự án trả lời kiểu `1a 2b` là phase mở. **Từ đây tới Cổng 3, AI không hỏi**, trừ PR mức Cao, việc khó đảo ngược mới phát sinh, hay việc lệch đặc tả. Chạm hạn mà chưa xong thì không tự kéo dài: Điều phối soạn gói Cổng 2 mới (thu hẹp, hay gia hạn có lý do).

**5b, sau cổng:** Điều phối cắt phase thành task trong `docs/phase/<MÃ>-<số>.md` (mẫu `mau/phase.md`). Mỗi task ghi: mã yêu cầu · 3–5 tiêu chí · hợp đồng giao diện (tên hàm, API, màn) để test viết được trước code · mức dự kiến, tách tệp Cao và tệp Thường ra task khác nhau khi được · tệp giữ chỗ · model · máy.

## 8. Chặng 6 — Làm, PR, cổng

1. *Kiểm thử viên* viết test từ tiêu chí và hợp đồng giao diện, **trước code**; test phải đỏ khi chưa có code. Tên test chứa mã yêu cầu.
2. *Lập trình viên* viết code tới khi test qua; không sửa test cho xanh (L5).
3. Thân PR có dòng `yeu-cau: F.1.4, YC-3` và tiêu chí nghiệm thu (`phuong-phap.md` §2).
4. Cổng vibe8 như hiện có (`phuong-phap.md` §2, §3): phiếu phản bác đúng SHA, mức do máy xếp; luật nào máy kiểm, luật nào là lời dặn xem mục 14. Mức Thường máy cho merge; mức Cao chờ người duyệt.

## 9. Cổng 3 và chặng 7 — Demo, phát hành theo bậc

**Cổng 3:** *Người phát hành* dựng bản trên môi trường thử và quay demo theo từng tiêu chí của phase. Chủ dự án chọn **đạt / sửa / bỏ**. Sửa tối đa 2 vòng, quá thì về Cổng 2. Bỏ thì phần đã merge được tắt bằng cờ tính năng (giải nghĩa: công tắc bật tắt tính năng mà không cần deploy lại) hay gỡ bằng PR revert, ghi lý do vào `DECISIONS.md`.

| Bậc | Ai thấy | Ở bao lâu | Lùi khi |
|---|---|---|---|
| 1 | nội bộ | ≥ 1 ngày | có lỗi chặn |
| 2 | một nhóm người dùng nhỏ · dự án khách: khách nghiệm thu trên môi trường thử (UAT — kiểm thử chấp nhận của người dùng) | ≥ 2 ngày | lỗi tăng, khách báo |
| 3 | tất cả | — | theo số đo chặng 8 |

Thay đổi người dùng không thấy thì đi thẳng bậc 3. Repo chưa có môi trường thử thì bậc 1–2 chạy trên máy thử cục bộ và ghi rõ là chưa đủ.

## 10. Chặng 8 — Đo và học; đường khẩn

- Năm số đo của `phuong-phap.md` §5, cộng **lỗi lọt gắn mã yêu cầu**: lỗi thuộc yêu cầu nào, lọt ở chặng nào. Ý tưởng mới sinh ra lúc đo quay về chặng 0 dưới dạng thẻ.
- **Đường khẩn** (lỗi đang hại người dùng): bỏ qua chặng 1–5, PR nhỏ nhất kèm test tái hiện đỏ trước xanh sau, theo **làn sửa gấp** của `phuong-phap.md` §2 (phiếu hẹp trước merge, lượt đầy đủ trong 24 giờ; mức Cao vẫn cần người duyệt trước merge). Trong 24 giờ có hậu kiểm một trang (mẫu `mau/hau-kiem.md`) và thẻ bài học.

## 11. Phiếu đổi yêu cầu

Yêu cầu đổi giữa phase, hay khách sửa SRS: phiếu theo mẫu `mau/phieu-doi-yeu-cau.md` (mã nào đổi · task, PR bị ảnh hưởng · ngân sách thêm · đổi trong phase này hay đẩy phase sau). Đổi nhỏ trong ngân sách thì Điều phối tự quyết, ghi `DECISIONS.md`. Đổi vượt ngân sách hay đổi điều kiện xong của phase thì chủ dự án quyết: cộng một điểm chạm.

## 12. Cỡ việc, điểm chạm, trần tải

| Cỡ | Ví dụ | Chặng chạy | Điểm chạm chủ dự án |
|---|---|---|---|
| Nhỏ | sửa lỗi, task trong phase đã duyệt | 6 → 8 | 0 cổng |
| Vừa | một tính năng của module có sẵn | Cổng 1 → 3 → 4 (mục trong đặc tả) → Cổng 2 → 6 → Cổng 3 → 7 → 8 | 3 cổng |
| Lớn | module, project mới; chạm dữ liệu khách, tiền, đăng nhập | 0 → 8 đủ, có tờ khung và tài liệu thiết kế riêng | 3 cổng |

**Cách đếm:** cổng là lượt quyết hướng; lượt duyệt PR Cao đếm riêng; phiếu đổi vượt ngân sách cộng một cổng.

| Trần (Alex 3a, 06/11) | Mức | Máy đếm |
|---|---|---|
| PR Cao chờ duyệt **cùng lúc**, tính trên mọi repo | ≤ 5; đầy thì làn mới chỉ làm task Thường | số PR mở có `cong-cuoi` báo `chan (cao)` `[CHƯA CÓ máy đếm gộp]` |
| Token mới mỗi task | Thường 300 k · Cao 600 k; vượt thì báo, không chặn | `ghi_token.py` `[CHƯA CÓ cảnh báo]` |
| Câu hỏi giữa phase | 0, trừ ba ngoại lệ ở mục 7 | lời dặn |
| Tỉ lệ PR Cao của repo sản phẩm | ≤ 30% (vibe8 không áp, vì repo này là cổng) | `do_vong.py` theo mức `[CHƯA CÓ dòng tỉ lệ]` |
| Giấy tờ | đặc tả phase ≤ 2 trang · thiết kế ≤ 6 · tờ khung ≤ 1 · dòng tài liệu mới / dòng code mới ≤ 1 mỗi phase | `[CHƯA CÓ]` |

Số 5 chưa có căn cứ đo. 300 k là trung vị token mỗi PR cộng chừng một nửa; 600 k là gấp đôi mức Thường, vì task Cao viết bằng model mạnh (L12) và thường có lượt vá kèm phản bác lại `[SUY LUẬN từ số đo nội bộ · 06/11]`. Cả ba là mốc khởi đầu, đặt lại sau 30 PR có số.

## 13. Vai

| Vai | Chặng | Viết gì | Không được |
|---|---|---|---|
| Thư ký hộp thư | 0 | gom, gộp, nhắc thẻ; giao việc cho Điều phối | quyết làm hay bỏ |
| Người thẩm định | 1 | 7 câu cổng | chọn thay chủ dự án |
| Phân tích viên | 2, 3 | tờ khung, yêu cầu | tự duyệt yêu cầu |
| Phản biện yêu cầu, thiết kế | 3, 4 | ý chặn, ý góp | viết lại tài liệu |
| Kiến trúc sư | 4 | thiết kế | tự chấm |
| **Điều phối** | 5 → 7 | gói cổng, bảng task, chọn model, mở làn | viết code, viết test |
| Kiểm thử viên | 6 | test từ tiêu chí | đọc code trước khi viết test |
| Lập trình viên | 6 | code | sửa test cho qua |
| Người phản bác PR | 6 | phiếu đúng SHA (L3) | phản bác PR của chính phiên mình |
| Người phát hành | 7 | demo, phát hành theo bậc | bỏ bậc khi chưa đủ thời gian |

**Tách vai:** vai viết và vai duyệt chạy ở hai ngữ cảnh khác nhau; phản biện nhận tài liệu, không nhận lời giải thích của vai viết; tối đa 2 vòng phản biện mỗi chặng, còn ý chặn thì đưa lên cổng kế tiếp kèm lý lẽ hai bên. **Model** theo bảng L12 (`phuong-phap.md` §4), không đặt bảng riêng ở đây.
**Gộp vai theo cỡ:** cỡ Vừa dùng 4 tác tử: người viết (phân tích, kiến trúc), phản biện, kiểm thử viên, lập trình viên; cộng Điều phối và người phản bác PR. Cỡ Lớn mới tách đủ bảng.

## 14. Máy kiểm và lời dặn

| Kiểm | Loại | Có chưa |
|---|---|---|
| Phiếu phản bác đúng SHA, hai mức, L1–L5, L10 | check `cong-cuoi` | có |
| L6–L9, L11, L12 | lời dặn, số đo trong `phuong-phap.md` §3 | chưa có máy chặn |
| Mã trong dòng `yeu-cau:` có thật trong SRS, `docs/ma-yeu-cau.md` hay `docs/yeu-cau.md` | check `cong-cuoi` | chưa |
| Mỗi mã được nhắc có test mang mã, đỏ ở commit trước code; mã đã đổi thì báo, không chặn | check `cong-cuoi` | chưa |
| Ma trận truy vết mã → task → PR → test sinh từ thân PR và tên test | script | chưa |
| Phiên đóng mà chưa để lại dấu (mục 2) | hook đóng phiên của máy agent, chỉ là trợ giúp | chưa |
| Phiên mới không biết repo đang theo kiến trúc này, đang ở phase nào, mình giữ vai gì | dòng trỏ ở `CLAUDE.md` / `AGENTS.md` (mục 15) · hook mở phiên của máy agent đọc `docs/phase/`, chỉ là trợ giúp | dòng trỏ: lời dặn · hook: chưa |
| Hàng đợi PR Cao, trần token, tỉ lệ tài liệu / code | script báo | chưa |
| Tách vai ở chặng 3–4, câu hỏi giữa phase, độ chín của thẻ | lời dặn | — |

Thứ tự làm máy: theo «sửa máy trước, thêm chữ sau» (`phuong-phap.md` §8.4), sau khi thí điểm cho thấy chặng nào giúp.

## 15. Áp vào một repo

1. Cài cổng như README; viết tệp điều kiện bán được (L11) và khai chính tệp đó cùng vùng Cao vào `cong/vung-nhay-cam.txt`, trên nhánh gốc.
2. Có SRS thì đi đường A, chưa có thì đường B (mục 5); dựng `docs/phase/` và `docs/DECISIONS.md` nếu chưa có.
   Thêm vào `CLAUDE.md` và `AGENTS.md` của repo một dòng trỏ tới `luat/kien-truc.md` và `luat/vai/dieu-phoi.md` của vibe8, kèm đường tới `docs/phase/`: phiên mới chỉ đọc những gì được nạp sẵn, không có dòng này thì nó làm theo thói quen cũ.
3. Thư ký hộp thư giao module cho **một** Điều phối khi chặng 3 đủ điều kiện ra.
4. Phase đầu tiên là thí điểm. Đo: điểm chạm của chủ dự án · token mỗi task · tỉ lệ tài liệu / code · lỗi bắt ở demo · lỗi lọt 14 ngày sau phát hành.
   **Chỉ báo để giữ** (một phase chưa đủ làm đường cơ sở): đúng 3 cổng, không phiếu đổi vượt ngân sách, không lỗi lọt mức N1 trong 14 ngày.
5. Đưa vào từng repo một: repo sau chỉ áp khi repo trước đóng xong một phase.
