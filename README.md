# Cổng cuối cho PR do agent viết

Cổng chạy ở phía GitHub: quyết định chỉ dựa trên diff, kết quả CI và lượt duyệt theo đúng commit,
không đọc lời khai trong thân PR. Tên `xuong` và `cong` là tên tạm, gom ở `cong/ten.py`.

**Trạng thái: đã bật trên một repo thật. L1-L8 bị chặn ở đó, L8 sau bản vá cũng vậy, PR rủi ro thấp tự qua đúng (hồi đó chưa đòi phiếu; nay là mức thường, cần phiếu phản bác). `--admin` của L5 bằng admin thật cũng bị chặn (PR 23).**
Mới chạy với các ca thử và PR của chính repo này, chưa qua PR việc thật của sản phẩm nào. Kết quả từng ca: [nghiem-thu/ket-qua.md](nghiem-thu/ket-qua.md). Đã kiểm gì, giới hạn gì: [docs/bao-mat.md](docs/bao-mat.md).

## Gồm gì

| Đường dẫn | Việc |
|---|---|
| `cong/rui_ro.py` | Xếp hai mức thường, cao từ diff và vùng nhạy cảm |
| `cong/kiem_pr.py` | Hàm thuần: dữ liệu PR vào, quyết định và lý do ra |
| `cong/gate_app.py` | Đọc REST, phát một check run `cong-cuoi` |
| `.github/workflows/` | `cong-nhanh` chạy test, `cong-cuoi` chạy cổng, `tin-hieu-duyet` đánh thức cổng khi có lượt duyệt |
| `nghiem-thu/` | App mẫu, bản vá lỗi L1-L7, bài cục bộ, script bật cổng, công cụ đo nhịp PR, kết quả trên GitHub thật |
| `luat/` | Phương pháp một PR (`phuong-phap.md`); đường đi từ ý tưởng tới phát hành (`kien-truc.md`), cách hiển thị tiến độ (`hien-thi-tien-do.md`) và thẻ vai (`vai/`), bản thí điểm |
| `mau/` | Mẫu tài liệu cho từng chặng: thẻ ý tưởng, tờ khung, yêu cầu, thiết kế, gói Cổng 2, sổ giữ chỗ phase, phiếu đổi, hậu kiểm |

Python 3.9 trở lên, chỉ stdlib.

## Chạy

```sh
sh ./kiem-tra.sh                                   # test lõi, test app mẫu, bài L1-L7 cục bộ
python3 -m cong.gate_app --kho cong/tests/pr_mau.json --sha aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
python3 nghiem-thu/bat_cong.py --repo chu/repo --app-id 123 --kho
python3 nghiem-thu/ghi_token.py --repo chu/repo --kho     # token máy ghi của PR nhánh đang mở
```

Chủ repo bật cổng: bỏ `--kho`, đặt `GH_TOKEN`, rồi làm các bước tay script in ra.

Mở repo bằng Claude Code thì `.claude/settings.json` tự chạy `ghi_token.py` sau mỗi `git push`, `gh pr create` và trước `gh pr merge`
hay `gh api … /pulls/<số>/merge`
(`nghiem-thu/hook_ghi_token.py`), không chặn lệnh nào. Ghi hỏng thì hook báo cách chạy tay. Đổi `.claude/` hay `.mcp.json` là rủi ro cao,
vì chúng chạy lệnh trên máy người mở repo.

## Luật

- PR phải nhắm `main`, và là PR mở duy nhất vào `main` ở SHA đó.
- Mọi lượt của tệp workflow `cong-nhanh`, sự kiện `pull_request`, trên đúng head SHA và nhánh đầu, tạo sau khi PR mở, phải
  `success`. Lượt đỏ không bị lượt xanh che. Đỏ vì lỗi thoáng qua thì bấm chạy lại lượt đó; đỏ vì `main` lúc đó còn hỏng thì chạy
  lại không chữa được, vì lượt chạy lại dùng commit merge cũ: đẩy một commit mới.
- `cong-nhanh` chỉ chạy lúc mở PR và đẩy commit. PR xung đột, hoặc đẩy commit lúc PR đang đóng, thì không có lượt trên SHA đó: cổng báo chờ, đẩy một commit mới.
- **Một nhánh đầu một PR:** nhánh từng có PR khác, kể cả đã đóng, thì không lượt nào được tính, vì PR đã đóng vẫn sinh lượt mới mà không biết
  lượt đó test với base nào. Cổng báo chờ. Đóng PR đó nếu còn mở, đẩy sang nhánh tên mới rồi mở PR mới.
- **PR từng đổi base không qua được,** kể cả đổi đi rồi đổi lại và GitHub tự đổi base của stacked PR: lượt sau khi đổi vẫn có thể chạy ref merge
  của base cũ. Đóng PR đó, đẩy sang nhánh tên mới rồi mở PR mới thẳng vào `main`.
- Đổi `.github/`, `xuong.yml`, thư mục `luat/`, `docs/bao-mat.md`, CODEOWNERS, script check, tệp khai phụ thuộc, lockfile: rủi ro cao, cần duyệt.
  Đổi README là mức thường: tệp này chỉ mô tả, cổng không đọc nó.
- **Test có sẵn là điều kiện nghiệm thu:** sửa, đổi tên, xoá đều là rủi ro cao, cần duyệt. Muốn thêm test thì tạo tệp mới, là mức thường.
  Thêm `__init__.py` trong vùng test cũng cần duyệt, vì nó quyết định test nào được nạp.
- Thêm tệp hay symlink trùng tên mô-đun chuẩn của Python (`pprint.py`, `app/json.py`, symlink `json`; tệp không đuôi nhiều dòng thì không tính) cũng cần duyệt, vì đủ làm CI xanh giả.
  Có thể báo oan với tệp vô hại như `app/calendar.py`; người duyệt bấm qua. Gói bên thứ ba thì không bắt được: xem giới hạn 9.
- Tệp không có diff dạng chữ cần duyệt, vì không ai đọc được bên trong: tệp nhị phân, tệp rỗng, và mọi mã máy như `.pyc`, `.so`, `.wasm`.
  Trừ ảnh, PDF, phông chữ: mức thường. Thêm `__init__.py` thì ghi một dòng chú thích để khỏi phải duyệt.
  Đổi tên kèm sửa tệp nhị phân thì là mức thường, vì API không phân biệt được với đổi tên thuần: xem giới hạn 8.
- Một số tệp vô hại có thể bị báo oan vì trùng tên tệp nhạy cảm (`docs/check.md`, `docs/requirements-q4.txt`, thư mục `docs/specs/`); người duyệt bấm qua.
- **Hai mức** (Alex 1a, 06/11): **cao** là chạm bảo mật hay tiền, cần người duyệt; còn lại là **thường**, cần phiếu phản bác. Không còn mức thấp.
- **Vùng nhạy cảm do repo tự khai** trong `cong/vung-nhay-cam.txt`: chạm vùng là rủi ro cao. Mỗi dòng một mẫu, `#` là chú thích;
  `*` khớp cả `/`, `**/` là không hoặc nhiều thư mục, `[id]` là chữ thường. Mẫu khớp chính nó và mọi thứ bên dưới; mẫu không có `/` như `auth.py` khớp ở mọi tầng.
  Cổng đọc tệp ở nhánh gốc, nên PR không tự gỡ vùng được. Tệp hỏng, hay có mẫu không bao giờ khớp được (`!x`, dấu cách lạ), thì cổng báo lỗi.
  Khai vùng mới trên `main` không xét lại PR đang mở: PR đó xét lại ở lần đẩy kế tiếp.
  **Repo chưa có tệp vùng ở nhánh gốc thì cổng chặn mọi PR.** Repo không có vùng nào thì để tệp chỉ có chú thích.
- **Mọi PR, cả mức Cao, cần một phiếu phản bác** (luật L3) trên đúng head SHA: một lượt review, thường là `gh pr review <số> --comment`, thân có hai dòng đứng đầu dòng:
  `phieu-phan-bac: khong-bac` (hoặc `bac`) và `tai-hien: <cách tái hiện, hay đã thử gì>`, tối thiểu 10 ký tự. Chỉ tính phiếu của người có quyền ghi trên repo, không tính máy.
  Có một phiếu `bac` trên SHA thì SHA đó bị chặn: phiếu `khong-bac` ghi sau không gỡ được, phải sửa bằng commit mới. Phiếu bị gỡ (dismiss) thì không tính. Đã bác trên 2 SHA khác nhau (L4 đếm vòng: bác hai lần trên một SHA vẫn là một vòng) thì chỉ người admin duyệt đúng SHA mới mở được, và lượt duyệt đó phải ghi sau phiếu bác cuối, có dòng `quyet-l4: <lý do>` (sửa review cũ thành bác không đổi giờ ghi, nên chỉ so giờ là chưa đủ). Chỉ ghi `quyet-l4` khi thẻ đã báo chạm trần L4; ghi sẵn từ trước thì cách sửa review cũ lại mở được cổng; khi đó thẻ duyệt đưa diff mọi tệp, kể cả PR Thường, vì không phiếu nào soát phần đó. Ngoài trường hợp đó, lượt duyệt của người admin không thay phiếu: PR mức Cao cần cả hai (Alex 1a, 06/11), vì thẻ duyệt chỉ đưa diff của tệp Cao, phần Thường do phiếu soát.
  Giới hạn: máy không phân biệt được hai agent dùng chung một tài khoản, nên chính tác giả ghi phiếu cũng tính. Vì vậy phải có ô tái hiện để người đọc lại kiểm. Khi nào làm tài khoản riêng cho người phản bác: `luat/phuong-phap.md` §2.
- Merge kiểu rebase phải tắt: cổng xét theo diff, còn rebase phát lại từng commit. Chưa tái hiện được kết quả lệch, đây là biện pháp phòng. `bat_cong.py` tắt và đọc lại.
- Quá 400 dòng (không tính lockfile; mức Thường còn trừ tệp test, mức Cao tính đủ): mức Cao bị chặn, mức Thường chỉ cảnh báo. Mức Cao được qua khi người duyệt hợp lệ ghi dòng `ngoai-le-co: <lý do>` trong lượt duyệt.
  Dòng đó phải đứng đầu dòng, đúng chữ thường, không gạch đầu dòng hay in đậm; sai định dạng thì cổng coi như chưa ghi.
- Duyệt hợp lệ: repo của Organization là người có quyền admin; repo của tài khoản cá nhân (`owner.type` User, nơi chỉ chủ có admin)
  là chủ repo hoặc người có quyền ghi (cổng hỏi GitHub lúc xét, Alex 1b 14/11). Cả hai: không phải tác giả hay người có commit
  trong PR (không tính commit merge, ví dụ bấm Update branch), không phải bot, đúng SHA.
- PR quá 250 commit bị chặn, vì API chỉ trả tới đó nên không đọc đủ được người có commit.
- Yêu cầu sửa của người duyệt hợp lệ (theo dòng trên) chặn bất kể SHA và mức rủi ro trên **PR đó**. Lượt của họ bị gỡ thì vẫn chặn đến khi họ duyệt lại.
  Yêu cầu sửa không theo sang PR mới cùng nội dung; người duyệt phải đóng cả nhánh nếu không muốn nội dung đó vào.
- Mỗi lần cổng được đánh thức mà SHA không còn là head của PR mở vào `main`, ví dụ PR vừa đóng: cổng ghi `failure` thay `success` cũ. Đổi base từ `main` đi nơi khác không đánh thức cổng; đổi về thì cổng xét lại và chặn, vì PR đã từng đổi base.
