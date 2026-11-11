# Vai Điều phối (thí điểm, 06/11/2026)

Thẻ vai cho tác tử điều phối một module, từ lúc yêu cầu đủ rõ tới lúc phase được nghiệm thu. Đường đi chung: `luat/kien-truc.md`.
Chủ dự án chốt 06/11: **một vai Điều phối cho mỗi module** (1a); Điều phối mở làn được trên cả máy chính lẫn máy phụ (2b).

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
  của **Thay làn** — thay bằng việc Điều phối mới đọc dòng sổ, nhánh và PR của làn (việc đổi đầu sổ ở bước 5 vẫn làm).

## 4. Chống trùng việc, chồng chéo

- **Sổ giữ chỗ duy nhất** là bảng task trong `docs/phase/<MÃ>-<số>.md`, và chỉ phiên Điều phối ở đầu sổ (§5) ghi bảng đó. Cột: mã task trong phase · mã việc (dãy số chung của dự án) · cha · mã yêu cầu · tệp/thư mục giữ · máy · phiên · nhánh · model · trạng thái · PR.
- Task mới chỉ mở khi tệp giữ của nó **không giao** với tệp giữ của task đang chạy.
- Tệp dùng chung (lockfile, migration, cấu hình gốc) mỗi lúc chỉ một làn giữ; task cần chúng xếp hàng.
- Một task một làn một nhánh một PR (L9 và `kien-truc.md` mục 1); không PR chồng PR, không đổi base.
- Làn trên máy phụ báo về qua hộp báo và PR trên GitHub (§5). Chỉ máy chính ghi tệp bàn giao, ghi sổ giữ chỗ và merge.
- Hai làn chạm nhau ngoài dự kiến (xung đột merge): dừng làn sau, ghi vào bảng, cắt lại task; không để làn tự giải xung đột của làn khác.

## 5. Cây làn: bảy thao tác của làn

Chủ dự án chốt 07/11: làn của một module nằm dưới Điều phối của module đó, và khi Điều phối bàn giao thì làn đi theo Điều phối mới (chỗ lệch đang chờ duyệt: «Làn sau chuyển» cuối mục).
Mục này nói **cái gì phải đúng**; cách làm cụ thể trên từng công cụ nằm ở bảng cuối mục.

**Hai lớp, vì lớp lồng không bền.** Lớp lồng: phiên làn là con của phiên Điều phối đã mở nó, trừ làn đã gỡ khỏi cây cha ở bước 3
của **Chuyển** và làn launchd (không có phiên, §3). Lớp này cho thấy ai mở ai, nhưng gắn chặt với một phiên; Điều phối đổi thì lớp
này không tự đổi theo. Lớp vỏ: một nhóm mang mã luồng việc (vd `📂 COM-24 · Tasks`), chứa mọi phiên Điều phối còn sống trên máy có
vỏ và mọi làn còn sống; **không ghim** Điều phối. Vỏ không gắn với phiên nào, nên sống qua mọi lần bàn giao. **Vỏ là nguồn sự thật để nhìn;
sổ giữ chỗ là nguồn sự thật để quyết** — mỗi dòng sổ ghi id phiên của làn (cột `Phiên`, `mau/phase.md`).

**Một vai, nhiều phiên, một phiên có quyền.** Vai vẫn là một cho mỗi module (đầu tệp), nhưng số phiên giữ vai có thể nhiều cùng
lúc, vd lúc bàn giao (chủ dự án chốt 07/11). Chỉ phiên ghi ở `Điều phối:` đầu sổ phase (`mau/phase.md`) làm việc của vai: ghi sổ
giữ chỗ, kiểm tải và mở làn, merge, nhận báo của làn. Phiên khác giữ vai chỉ đọc, tới khi đầu sổ đổi sang nó (bước 5 của
**Chuyển**). Chỗ nào trong tệp này nói Điều phối ghi, mở, merge hay nhận báo là nói phiên ở đầu sổ.

| Thao tác | Khi nào | Làm gì | Sổ ghi |
|---|---|---|---|
| **Mở** | task chờ, tệp giữ không giao, máy nổi (§2.4) | mở làn từ chính phiên Điều phối ở đầu sổ, trong bản làm việc riêng (worktree), không chung với Điều phối hay làn khác, ở nơi chủ dự án nhìn thấy được (thanh bên app), không chạy ngầm (ngoại lệ: làn launchd, §3); tên phiên mang mã việc ở cột Mã của sổ, task chưa có mã thì mang mã luồng — mẫu tên đầy đủ là luật của repo chủ dự án (`luat/`, `mau/` không có mẫu tên phiên — [ĐÃ KIỂM: grep · 07/11/2026]); đưa vào vỏ | task · phiên · nhánh · máy · `đang làm` |
| **Tách** | task phình quá một ngày, hoặc tệp giữ rộng hơn dự kiến | làn dừng, đẩy nhánh, báo Điều phối; Điều phối cắt task con trong sổ; phần còn lại mở làn mới từ `main` — phần nào cần phần kia thì chờ phần kia merge, không PR chồng PR | task gốc `tách → Tx.a, Tx.b` |
| **Gộp** | hai task giao tệp giữ, hoặc một task quá nhỏ đứng riêng | giữ làn tiến xa hơn; làn kia đẩy nhánh, làn giữ nhặt commit sang (cherry-pick) hoặc làm lại; đóng PR và lưu trữ làn bị gộp | task bị gộp `gộp vào Ty` |
| **Gom** | luôn luôn (trừ làn launchd, §3) | mọi làn của một module nằm trong đúng một vỏ; làn của module khác không vào vỏ này | — |
| **Chuyển** | Điều phối bàn giao (ngữ cảnh > 80 %, đổi máy) | theo bảy bước dưới | cột Phiên giữ nguyên, đầu sổ đổi `Điều phối` (bước 5) |
| **Thay làn** | làn vượt 150 nghìn token ngữ cảnh | làn **không tự mở phiên kế** (phiên đó sẽ lồng dưới làn, ra khỏi tầm Điều phối): làn ghi bàn giao vào nhánh, đẩy, báo; Điều phối mở làn kế từ nhánh đó; chỉ lưu trữ làn cũ khi nhánh đã đẩy và làn kế đã xác nhận nhận bàn giao | phiên mới thay phiên cũ |
| **Xong** | PR của làn qua cổng (`kien-truc.md` mục 8 điểm 4: phiếu phản bác đúng SHA, check `cong-cuoi` xanh) | Điều phối merge ngay theo mức (Thường: tự merge; Cao: chờ người duyệt), không để PR xanh nằm chờ; PR Cao còn chờ duyệt thì làn sống tới khi merge; ngay trước khi merge, làn dừng dịch vụ đã bật (dev server), vì app có thể tự lưu trữ làn khi PR đóng (dưới bảng công cụ); sau merge lưu trữ làn nếu app chưa làm, sổ `xong` | PR · `xong` |

**Chuyển làn khi Điều phối bàn giao — bảy bước, đúng thứ tự:**

1. Điều phối cũ cập nhật sổ: cột Phiên, việc dở của từng làn, câu hỏi còn treo.
2. Mở Điều phối mới; lời giao chỉ trỏ tới sổ và tệp bàn giao, không chép lại.
3. Tách Điều phối mới và mọi làn còn sống ra khỏi cây của Điều phối cũ. **Bước này phải đi trước khi Điều phối cũ đóng:** công cụ có
   thể đóng, lưu trữ luôn phiên con khi đóng phiên cha `[ĐÃ KIỂM: Điều phối COM-24 cũ lưu trữ và kéo theo Điều phối mới · 07/11]`.
4. Đưa tất cả vào vỏ (không ghim). Điều phối mới làm bước này ngay lượt đầu nhận ca, kể cả khi chưa định mở làn nào
   `[ĐÃ KIỂM: Điều phối COM-24 nhận ca 11/11 chỉ gom chính nó; sáu làn nằm ngoài vỏ tới khi chủ dự án chỉ ra]`.
5. Điều phối cũ đổi `Điều phối:` đầu sổ sang id phiên mới. Quyền chuyển lúc thay đổi này lên `main`; từ đó Điều phối cũ chỉ đọc.
   Rồi viết một bình luận vào hộp báo «Điều phối mới là <id>» (dưới; chủ dự án 1c 11/11).
   **Không nhắn từng làn** (chủ dự án 1a 13/11): làn tự tra người nhận ở đầu sổ mỗi lần báo (đường báo dưới), nên đổi đầu
   sổ là đủ; mỗi tin gửi đi đánh thức một làn chạy cả lượt trên toàn ngữ cảnh của nó, tốn token mà không thêm gì
   `[SUY LUẬN từ cách app chạy tin đến: tin mở một lượt mới của làn; chưa đo số token]`.
6. Điều phối mới đối chiếu sổ với danh sách phiên đang sống (cột Phiên, vỏ). Chỉ nhắn làn nào sổ ghi lệch thực tế, và làn mở
   trước 13/11 mà lời giao ghi cứng id Điều phối cũ; không xác nhận từng làn.
7. Điều phối cũ kiểm lại không còn phiên con nào cần sống, rồi đóng phiên. Không để Điều phối cũ sống sau khi đầu sổ đã đổi: Điều phối mới thấy nó còn sống thì nhắc nó đóng (hàng rào `dp-cu` dưới).

**Hai kiểu đóng Điều phối** (chủ dự án 1a 11/11): *đóng cuối phase*: mọi làn xong (merge, lưu trữ), Điều phối đóng sau cùng;
*bàn giao*: bảy bước trên. Không bắt Điều phối cũ chờ mọi làn xong khi bàn giao, vì nó bàn giao chính vì đã gần đầy ngữ cảnh.

**Hàng rào của bảy bước** (`~/ai/os/bin/hook-dieu-phoi.py`, chủ dự án 1a 11/11) — vì ngày đó bước 3 làm muộn và bước 6 bị bỏ
`[ĐÃ KIỂM: ~/.cache/ai-os/hook-dieu-phoi.log — hook chặn một lần mở làn mã «auto,khung» lúc 10:05 · 11/11]`
`[SUY LUẬN từ ảnh chụp thanh bên của chủ dự án và bản tóm tắt phiên Điều phối cũ: phiên bị chặn là Điều phối COM-24 mới, hai làn nằm ngoài vỏ tới khi được chỉ ra]`.
Hành vi dưới đây `[ĐÃ KIỂM: bin/test-hook-dieu-phoi.py 49/49 trên bản ghi giả và repo git giả · 11/11; hàng 6 sửa 13/11: 59/59]`, chưa chặn lần bàn giao thật nào:

| Bước | Máy làm gì | Không làm |
|---|---|---|
| 3 | Khi một Điều phối (tên đúng mẫu) gọi `start_session` mở phiên có chữ «Điều phối» trong tên: nhắc `detach_session` phiên đó. `wrap_up` của Điều phối bị từ chối khi còn phiên con là Điều phối chưa tách | Không canh làn thường còn là con; không áp cho `hand_off_to_session` |
| 5 | Sổ = `docs/phase/<MÃ>-<số lớn nhất>.md` gần nhất khi đi ngược từ thư mục làm việc của phiên, số lớn nhất tính trên cả bản làm việc lẫn `origin/main`; đọc dòng `Điều phối:` ở cả hai. Điều phối gọi `start_session` mà không nguồn nào ghi id của nó: từ chối. Điều phối gọi `wrap_up` hay `archive_session self` mà mọi nguồn còn ghi id của nó trong khi đã có Điều phối kế (tạo sau nó) cùng MÃ và Sản phẩm: từ chối | Không `git fetch` (main ở máy có thể cũ); không thấy sổ thì cho qua; không kiểm phần còn lại của sổ |
| 6 | Khi một Điều phối gọi `start_session`, và ở mỗi `wrap_up` của nó (chủ dự án 2a 11/11: Điều phối nhận ca rồi chỉ theo dõi PR, không mở làn, nên kiểm lúc mở làn không chạy): từ chối nếu còn phiên chưa lưu trữ cùng MÃ và Sản phẩm (không phải Điều phối, không phải con trực tiếp chưa tách) mà nằm ngoài vỏ (điều kiện «chưa từng nhận tin `SendMessage` từ Điều phối này» đã bỏ, chủ dự án 1a 13/11, CN-64: hook báo về của làn tự đọc đầu sổ để chỉ ra id người nhận) | Chỉ xét phiên có tên đúng mẫu; kiểm «ngoài vỏ» chỉ khi Điều phối đã ở trong vỏ; không đọc sổ; không kiểm nội dung tin |
| 7 | `archive_session self` của Điều phối bị từ chối khi còn phiên con chưa tách, chưa lưu trữ | `wrap_up` không xét làn con thường |

Mỗi lý do chỉ từ chối tối đa 2 lần trong 6 giờ rồi cho qua (tool app hỏng không được khoá phiên). Hook cũng cho qua khi lỗi, khi phiên chạy
từ máy khác. Đây là gờ giảm tốc, không phải khoá.

**Ngưỡng ngữ cảnh và đường báo** (chủ dự án chốt 07/11):

- **Điều phối > 80 % cửa sổ ngữ cảnh thì bàn giao** theo bảy bước trên, không chờ hết phase. Lý do: phiên điều phối bị nén
  nhiều lần sẽ quên quyết định cũ, và sai thêm còn đắt hơn mở phiên mới `[ĐÃ KIỂM: Điều phối COM-24-1 nén hơn 20 lần, quên
  quyết định đã chốt · 07/11]`.
- **Làn > 150 nghìn token thì Thay làn** (hàng trên), không tự mở phiên kế.
- **Làn báo mọi phát sinh về Điều phối** qua **hộp báo** của luồng việc (dưới; đây là bản tính), và nhắn thêm tới id phiên
  Điều phối ở đầu sổ, **đọc lại mỗi lần báo** từ `origin/main`
  (sau `git fetch`), không nhớ id từ lời giao — nhờ vậy làn đang dở tự về dưới quyền Điều phối mới khi bàn giao (chủ dự án 1a 13/11).
  Hook báo về của làn (S2) nêu id lấy từ đầu sổ phase mới nhất khi làn có id ở cột Phiên `[ĐÃ KIỂM: đọc lan_theo_so(), la_lan()
  và chan_bao_ve() ở ~/ai/os origin/main · 13/11]`. Hook vẫn có thể chỉ về id cũ khi: máy chưa `git fetch` sau lúc đổi đầu sổ
  (hook không fetch); làn không có dòng ở cột Phiên (hook dự phòng theo phiên cha, tức Điều phối cũ, hoặc theo Điều phối đầu
  tiên trong vỏ, mà vỏ có thể còn cả Điều phối cũ); làn chạy ở máy khác. Báo khi: đổi phạm vi, chạm tệp ngoài phần giữ, bị chặn,
  cần quyết định, xong lượt. Làn không hỏi chủ dự án qua hộp cuối lượt; Điều phối gom lại, tự quyết trong ngân sách, chỉ đưa lên chủ dự án
  ba ngoại lệ của `kien-truc.md` mục 7 (PR mức Cao, việc khó đảo ngược mới phát sinh, lệch đặc tả).
- **Điều phối tự chạy tới hết phase** trong ba ngoại lệ đó; không dừng giữa chừng để hỏi «làm tiếp thế nào».

**Hộp báo — kênh báo không dựa vào quan hệ cha–con** (chủ dự án 1c 11/11). Vì sao: tin «làn xong lượt» của app chỉ đi tới **phiên cha**,
và app không có công cụ đổi cha. Bàn giao Điều phối vì thế cắt mọi làn đang chạy khỏi kênh báo tự động: Điều phối mới không được đánh thức,
làn chờ một câu trả lời không tới `[ĐÃ KIỂM: cả 7 làn COM-24 còn sống có cha là Điều phối đã lưu trữ; làn T10b chặn hơn 20 phút không ai thấy;
tin nhắn từ làn chạy qua ssh trên máy phụ về Điều phối báo «không tìm thấy phiên» · 11/11]`.

- **Hộp báo** là một issue GitHub trên repo sản phẩm, mỗi luồng việc một cái, tên `Hộp báo <MÃ>`; dòng `Hộp báo:` ở đầu sổ ghi số issue.
  Chọn issue chứ không chọn tệp: làn trên máy phụ không ghi được tệp của máy chính, còn tệp trên nhánh làn sẽ theo PR vào `main`.
- **Làn viết vào hộp báo**: `gh issue comment <số> --body "[<id phiên 8 ký tự> · <task>] <loại>: <nội dung>"`, loại là một trong
  `xong-luot` · `chan` · `hoi` · `pr` · `doi-pham-vi`. Mỗi lần báo một bình luận; có PR thì vẫn báo vào hộp, PR chỉ là chỗ chứa phiếu.
  `SendMessage` về Điều phối vẫn được gửi thêm cho nhanh, nhưng hộp báo là bản tính.
- **Điều phối trả lời trong hộp báo** (trích `[<id> · <task>]` ở đầu) và nhắn thêm cho làn; làn bị chặn thì đọc hộp báo
  (`gh issue view <số> --comments`) trước mỗi lần chờ.
- **Điều phối canh hộp báo** bằng một vòng đọc bình luận mới (cùng chỗ canh CI), từ lượt đầu nhận ca. Điều phối mới chỉ cần số issue ở
  đầu sổ: không cần là cha của làn nào.
- Bước 5 của bảy bước: đổi `Điều phối:` đầu sổ, rồi viết một bình luận vào hộp báo «Điều phối mới là <id>»; không nhắn từng làn (1a 13/11).

**Gần đầy thì chờ làn sắp xong** (chủ dự án 1c 11/11): Điều phối quá 80 % cửa sổ ngữ cảnh thì **ngừng mở làn mới**; làn đã mở PR
(chờ phiếu, chờ CI) thì Điều phối cũ merge xong rồi mới bàn giao; làn còn đang viết mã thì chuyển cho Điều phối mới qua hộp báo,
không chờ.

**Làn sau chuyển — lệch chốt 07/11, chờ chủ dự án duyệt** (CN-64, 13/11). Chốt 07/11 là «làn đi theo Điều phối mới». App không
gắn được phiên vào cha khác (bảng công cụ dưới), nên mục này hạ chốt đó thành «vỏ thay chỗ lớp lồng» cho làn **đang dở**. Đây là
lệch luật, không phải cách hiểu; tới khi chủ dự án duyệt, áp đúng như sau và không suy rộng thêm:

- **Làn chưa có commit** (nhánh không có commit nào ngoài `main`, cả bản cục bộ lẫn `origin`; hoặc chưa có nhánh): Điều phối mới
  **bắt buộc** lưu trữ nó và mở lại từ phiên mình, trước khi mở bất kỳ làn mới nào — **trừ** khi bản làm việc của làn còn thay
  đổi chưa commit (lưu trữ là mất việc): khi đó làn commit, đẩy trước rồi mới tính. Không thừa kế làn này
  `[ĐÃ KIỂM: COM-24-6 13/11 — làn chưa commit được thừa kế, nằm ngoài lớp lồng]`.
- **Làn đang dở** (có commit): giữ, ở cấp cao nhất trong vỏ, vì mất ngữ cảnh đắt hơn mất lớp lồng. Hết việc thì không mở tiếp từ
  làn đó; phần kế mở từ Điều phối mới.
- **Mỗi làn một bản làm việc riêng.** Làn không bao giờ chạy trong bản làm việc của Điều phối (bản giữ sổ, vd `.wt/so-…`) hay của
  làn khác: hai phiên một bản làm việc thì đóng phiên này lưu trữ luôn phiên kia, và cùng sửa đè tệp
  `[ĐÃ KIỂM: COM-24-6 13/11 — hai làn chạy chung bản làm việc giữ sổ của Điều phối]`.

**Hàng rào cho cây làn** (CN-64, chủ dự án 2a 13/11 «cả 5 hàng rào»; mã ở `~/ai/os/bin/hook-dieu-phoi.py` và `doi-ten-lan.py`,
đã merge vào `main` của repo đó qua PR phanbinhdcna/vibe8#8; `[ĐÃ KIỂM: bin/test-hook-dieu-phoi.py 59/59 · bin/test-doi-ten-lan.py
đạt hết · 13/11]`, trên bản ghi giả, chưa chặn lần bàn giao thật nào). Vì ở COM-24-6 cả bốn điều trên và bước 7 chỉ là lời dặn, không máy nào bắt. Cùng kiểu
gờ giảm tốc như bảng trên (tối đa 2 lần mỗi lý do trong 6 giờ; đọc hỏng hay đo không được thì cho qua):

| Mã | Lúc | Máy làm gì |
|---|---|---|
| `wt` | Điều phối gọi `start_session` | từ chối khi `use_worktree` không phải `true`; miễn khi chạy ở `cloud`/`ssh`/`host` khác, hoặc phiên mới tên «Điều phối» (bàn giao) (G3) |
| `lan-trang` | Điều phối gọi `start_session` | từ chối khi còn làn tạo trước nó, cùng MÃ, chưa lưu trữ, nhánh không có commit ngoài `origin/main` (hoặc chưa ghi nhánh): lưu trữ rồi mở lại (G1). Cho qua khi bản làm việc của làn còn thay đổi chưa commit, làn ghi hơn 3 nhánh, hoặc đo không được |
| `dp-cu` | Điều phối mà đầu sổ ghi id nó gọi `wrap_up` | từ chối khi còn Điều phối cũ hơn cùng MÃ chưa lưu trữ, không có trong sổ: nhắn nó đóng (bước 7), không đáp thì `archive_session` (G2). Chỉ kiểm ở `wrap_up` của Điều phối mới, không ở `start_session`, để không vướng thứ tự bàn giao |
| `luu-tru` | như trên | từ chối khi mọi dòng sổ của một phiên ở cột Phiên đều xong (✅, `xong`, merged) mà phiên chưa lưu trữ (G4) |
| `ten` | như trên | `doi-ten-lan.py` `canh_bao()`: làn **lạc sổ** (mang mã luồng hay mã task của sổ mà không có dòng ở cột Phiên) hoặc tên **sai mẫu** → từ chối, kèm lệnh chạy `doi-ten-lan.py` rồi `set_session_title` (G4). Phần nấc PR cần GitHub, quá 5 giây của hook, nên vẫn là script Điều phối chạy |

`doi-ten-lan.py` trước đây bỏ qua im lặng mọi phiên không có id ở cột Phiên, nên làn mở ngoài sổ không bao giờ được đổi tên
`[ĐÃ KIỂM: đọc mã de_xuat() và sổ COM-24-6 · 13/11 — làn «⬛️ Phiếu delta Mermaid COM-24» không có dòng]`. Nay `--day-du` in
`{doi, lac_so, sai_mau}`; chạy thường thì cảnh báo ra stderr, đầu ra cũ giữ nguyên.

**Trên app Claude Code desktop** `[ĐÃ KIỂM: danh sách công cụ của app · 07/11]`:

| Cần | Công cụ |
|---|---|
| Mở làn lồng dưới Điều phối | `start_session` gọi từ phiên Điều phối, `use_worktree: true` (dùng chung bản làm việc thì làn bị lưu trữ cùng cha) |
| Vỏ | nhóm thanh bên: `create_group`, `move_sessions`; không ghim (xem tự lưu trữ dưới bảng) |
| Tách khỏi cây cha | `detach_session` — một chiều: **app không có công cụ gắn phiên vào cha khác** |
| Nhắn làn | `SendMessage` tới id `local_…` |
| Kiểm phiên con trước khi đóng | `list_sessions {"linked": true}` |

**Tự lưu trữ khi PR đóng.** App có thể tự lưu trữ một phiên khi PR của phiên đó merge hay đóng `[ĐÃ KIỂM: cài đặt «tự lưu trữ
phiên khi PR đóng» của app đang bật, danh sách công cụ có unarchive_session · 09/11]`. Điều này áp cho mọi phiên có PR: làn, và
cả Điều phối, vì PR sửa sổ do chính phiên Điều phối ở đầu sổ mở (chỉ nó ghi sổ, §4). Nên:

- làn dừng dịch vụ đã bật trước khi merge (hàng **Xong**);
- Điều phối mở PR (sổ, bàn giao) thì gỡ PR khỏi phiên mình ngay (`unbind_pr`); hook từ chối `wrap_up` khi Điều phối còn gắn PR
  đang mở. Công cụ gỡ bị chặn quyền thì báo chủ dự án gỡ tay (nút × trên thanh PR của phiên)
  `[ĐÃ KIỂM: PR sổ #369 của comitor-tasks gắn vào Điều phối, unbind_pr bị chế độ auto từ chối · 11/11]`;
- Điều phối ở đầu sổ kiểm `list_sessions` ngay sau mỗi lần merge, trước khi hết lượt; thấy chính nó hay một làn còn việc đã bị
  lưu trữ thì mở lại bằng `unarchive_session` rồi làm tiếp từ sổ. Bị lưu trữ lúc đã nghỉ thì phiên không tự thấy được: chủ dự án
  thấy nó mất khỏi vỏ thì mở lại `[CHƯA KIỂM: phiên mở lại có chạy tiếp được không]`.

Nhóm thanh bên chỉ có trên máy đang chạy phiên, không đồng bộ sang máy khác: tên phiên vẫn phải mang mã (cột Mã của sổ, chưa có thì mã luồng).

## 6. Không được

- Viết code hay test của task (việc của lập trình viên, kiểm thử viên).
- Tự duyệt, tự phản bác PR do làn mình mở; merge PR mức Cao chưa có người duyệt.
- Hỏi chủ dự án giữa phase, trừ ba ngoại lệ của `kien-truc.md` mục 7.
- Kéo dài phase quá hạn mà không có gói Cổng 2 mới.

## 7. Số đo của vai (cho kết luận thí điểm)

Điểm chạm của chủ dự án mỗi phase · token mỗi task so với trần · số làn mỗi máy và số lần máy báo không nổi · số xung đột merge giữa làn · số task phải cắt lại.
