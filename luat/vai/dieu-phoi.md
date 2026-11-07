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

- ssh thường không đăng nhập được tác tử: trên macOS, phiên ssh không mở được Keychain nên CLI báo chưa đăng nhập `[ĐÃ KIỂM: chạy CLI qua ssh trên máy phụ · 06/11]`.
- Chạy được khi làn khởi động trong miền GUI của người dùng (launchd `gui/<uid>`), gọi qua ssh `[ĐÃ KIỂM: job launchd chạy một lần, CLI trả lời được · 06/11]`.
- Công cụ mở làn cụ thể nằm ở repo riêng của chủ dự án, không ở vibe8.
- Làn chạy bằng launchd là **ngoại lệ duy nhất của «không chạy ngầm»** (§5 Mở): nó không có phiên trong app, không có id phiên,
  không nhận tin nhắn. Nên ở §5: **Mở** — «nhìn thấy được» là một dòng sổ ghi máy, nhãn job launchd và nhánh, thay cho thanh bên;
  **Gom** — không áp; **báo về** — chỉ qua nhánh và PR (§4), không qua tin nhắn; **Chuyển** bước 3–6 và chốt «làn kế đã xác nhận»
  của **Thay làn** — thay bằng việc Điều phối mới đọc dòng sổ, nhánh và PR của làn.

## 4. Chống trùng việc, chồng chéo

- **Sổ giữ chỗ duy nhất** là bảng task trong `docs/phase/<MÃ>-<số>.md`, và chỉ Điều phối ghi bảng đó. Cột: mã task · mã yêu cầu · tệp/thư mục giữ · máy · phiên · nhánh · model · trạng thái · PR.
- Task mới chỉ mở khi tệp giữ của nó **không giao** với tệp giữ của task đang chạy.
- Tệp dùng chung (lockfile, migration, cấu hình gốc) mỗi lúc chỉ một làn giữ; task cần chúng xếp hàng.
- Một task một làn một nhánh một PR (L9 và `kien-truc.md` mục 1); không PR chồng PR, không đổi base.
- Làn trên máy phụ chỉ báo về qua PR trên GitHub. Chỉ máy chính ghi tệp bàn giao, ghi sổ giữ chỗ và merge.
- Hai làn chạm nhau ngoài dự kiến (xung đột merge): dừng làn sau, ghi vào bảng, cắt lại task; không để làn tự giải xung đột của làn khác.

## 5. Cây làn: bảy thao tác của làn

Chủ dự án chốt 07/11: làn của một module nằm dưới Điều phối của module đó, và khi Điều phối bàn giao thì làn đi theo Điều phối mới.
Mục này nói **cái gì phải đúng**; cách làm cụ thể trên từng công cụ nằm ở bảng cuối mục.

**Hai lớp, vì lớp lồng không bền.** Lớp lồng: phiên làn là con của phiên Điều phối đã mở nó. Nó cho thấy ai mở ai, nhưng gắn chặt
với một phiên; Điều phối đổi thì lớp này không tự đổi theo. Lớp vỏ: một nhóm mang mã luồng việc (vd `📂 COM-24 · Tasks`), chứa
Điều phối hiện hành và mọi làn còn sống. Vỏ không gắn với phiên nào, nên sống qua mọi lần bàn giao. **Vỏ là nguồn sự thật để nhìn;
sổ giữ chỗ là nguồn sự thật để quyết** — mỗi dòng sổ ghi id phiên của làn (cột `Phiên`, `mau/phase.md`).

| Thao tác | Khi nào | Làm gì | Sổ ghi |
|---|---|---|---|
| **Mở** | task chờ, tệp giữ không giao, máy nổi (§2.4) | mở làn từ chính phiên Điều phối, trong bản làm việc riêng (worktree), ở nơi chủ dự án nhìn thấy được (thanh bên app), không chạy ngầm (ngoại lệ: làn launchd, §3); tên phiên mang mã luồng việc (vd `COM-24`) — mẫu tên đầy đủ là luật của repo chủ dự án, vibe8 không quy định; đưa vào vỏ | task · phiên · nhánh · máy · `đang làm` |
| **Tách** | task phình quá một ngày, hoặc tệp giữ rộng hơn dự kiến | làn dừng, đẩy nhánh, báo Điều phối; Điều phối cắt task con trong sổ; phần còn lại mở làn mới từ `main` — phần nào cần phần kia thì chờ phần kia merge, không PR chồng PR | task gốc `tách → Tx.a, Tx.b` |
| **Gộp** | hai task giao tệp giữ, hoặc một task quá nhỏ đứng riêng | giữ làn tiến xa hơn; làn kia đẩy nhánh, làn giữ nhặt commit sang (cherry-pick) hoặc làm lại; đóng PR và lưu trữ làn bị gộp | task bị gộp `gộp vào Ty` |
| **Gom** | luôn luôn (trừ làn launchd, §3) | mọi làn của một module nằm trong đúng một vỏ; làn của module khác không vào vỏ này | — |
| **Chuyển** | Điều phối bàn giao (ngữ cảnh > 80 %, đổi máy) | theo bảy bước dưới | cột Phiên giữ nguyên, đầu sổ đổi `Điều phối` |
| **Thay làn** | làn vượt 150 nghìn token ngữ cảnh | làn **không tự mở phiên kế** (phiên đó sẽ lồng dưới làn, ra khỏi tầm Điều phối): làn ghi bàn giao vào nhánh, đẩy, báo; Điều phối mở làn kế từ nhánh đó; chỉ lưu trữ làn cũ khi nhánh đã đẩy và làn kế đã xác nhận nhận bàn giao | phiên mới thay phiên cũ |
| **Xong** | PR của làn qua cổng (`kien-truc.md` mục 8.4: phiếu phản bác đúng SHA, check của cổng cho merge) | Điều phối merge ngay theo mức (Thường: tự merge; Cao: chờ người duyệt), không để PR xanh nằm chờ; PR Cao còn chờ duyệt thì làn sống tới khi merge; sau merge mới dừng dịch vụ làn đã bật (dev server), lưu trữ làn, sổ `xong` | PR · `xong` |

**Chuyển làn khi Điều phối bàn giao — bảy bước, đúng thứ tự:**

1. Điều phối cũ cập nhật sổ: cột Phiên, việc dở của từng làn, câu hỏi còn treo.
2. Mở Điều phối mới; lời giao chỉ trỏ tới sổ và tệp bàn giao, không chép lại.
3. Tách Điều phối mới và mọi làn còn sống ra khỏi cây của Điều phối cũ. **Bước này phải đi trước khi Điều phối cũ đóng:** công cụ có
   thể đóng, lưu trữ luôn phiên con khi đóng phiên cha `[ĐÃ KIỂM: Điều phối COM-24 cũ lưu trữ và kéo theo Điều phối mới · 07/11]`.
4. Đưa tất cả vào vỏ, Điều phối mới đặt đầu.
5. Nhắn từng làn: «Điều phối mới là <id>; báo về đó từ giờ».
6. Điều phối mới đối chiếu sổ với danh sách phiên đang sống, xác nhận với từng làn.
7. Điều phối cũ kiểm lại không còn phiên con nào cần sống, rồi đóng phiên.

**Ngưỡng ngữ cảnh và đường báo** (chủ dự án chốt 07/11):

- **Điều phối > 80 % cửa sổ ngữ cảnh thì bàn giao** theo bảy bước trên, không chờ hết phase. Lý do: phiên điều phối bị nén
  nhiều lần sẽ quên quyết định cũ, và sai thêm còn đắt hơn mở phiên mới `[ĐÃ KIỂM: Điều phối COM-24-1 nén hơn 20 lần, quên
  quyết định đã chốt · 07/11]`.
- **Làn > 150 nghìn token thì Thay làn** (hàng trên), không tự mở phiên kế.
- **Làn báo mọi phát sinh về Điều phối** bằng tin nhắn tới id phiên Điều phối: đổi phạm vi, chạm tệp ngoài phần giữ, bị chặn,
  cần quyết định. Làn không hỏi chủ dự án qua hộp cuối lượt; Điều phối gom lại, tự quyết trong ngân sách, chỉ đưa lên chủ dự án
  ba ngoại lệ của `kien-truc.md` mục 7 (PR mức Cao, việc khó đảo ngược mới phát sinh, lệch đặc tả).
- **Điều phối tự chạy tới hết phase** trong ba ngoại lệ đó; không dừng giữa chừng để hỏi «làm tiếp thế nào».

Làn cũ sau chuyển nằm ở cấp cao nhất, không lồng dưới Điều phối mới: vỏ thay chỗ cho lớp lồng. Làn chưa bắt đầu viết mã thì Điều
phối mới lưu trữ nó và mở lại từ phiên mình (lồng đúng, mất ít); làn đang dở thì giữ, vì mất ngữ cảnh đắt hơn mất lớp lồng.

**Trên app Claude Code desktop** `[ĐÃ KIỂM: danh sách công cụ của app · 07/11]`:

| Cần | Công cụ |
|---|---|
| Mở làn lồng dưới Điều phối | `start_session` gọi từ phiên Điều phối, `use_worktree: true` (dùng chung bản làm việc thì làn bị lưu trữ cùng cha) |
| Vỏ | nhóm thanh bên: `create_group`, `move_sessions`; Điều phối hiện hành ghim lên đầu |
| Tách khỏi cây cha | `detach_session` — một chiều: **app không có công cụ gắn phiên vào cha khác** |
| Nhắn làn | `SendMessage` tới id `local_…` |
| Kiểm phiên con trước khi đóng | `list_sessions {"linked": true}` |

Nhóm thanh bên chỉ có trên máy đang chạy phiên, không đồng bộ sang máy khác: tên phiên vẫn phải mang mã luồng việc.

## 6. Không được

- Viết code hay test của task (việc của lập trình viên, kiểm thử viên).
- Tự duyệt, tự phản bác PR do làn mình mở; merge PR mức Cao chưa có người duyệt.
- Hỏi chủ dự án giữa phase, trừ ba ngoại lệ của `kien-truc.md` mục 7.
- Kéo dài phase quá hạn mà không có gói Cổng 2 mới.

## 7. Số đo của vai (cho kết luận thí điểm)

Điểm chạm của chủ dự án mỗi phase · token mỗi task so với trần · số làn mỗi máy và số lần máy báo không nổi · số xung đột merge giữa làn · số task phải cắt lại.
