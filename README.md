# Cổng cuối cho PR do agent viết

Cổng chạy ở phía GitHub: quyết định chỉ dựa trên diff, kết quả CI và lượt duyệt theo đúng commit,
không đọc lời khai trong thân PR. Tên `xuong` và `cong` là tên tạm, gom ở `cong/ten.py`.

**Trạng thái: đã bật trên một repo thật. L1-L8 bị chặn ở đó, L8 sau bản vá cũng vậy, PR rủi ro thấp tự qua đúng. Riêng `--admin` của L5 chưa thử bằng admin thật.**
Mới chạy với các ca thử và PR của chính repo này, chưa qua PR việc thật của sản phẩm nào. Kết quả từng ca: [nghiem-thu/ket-qua.md](nghiem-thu/ket-qua.md). Đã kiểm gì, giới hạn gì: [docs/bao-mat.md](docs/bao-mat.md).

## Gồm gì

| Đường dẫn | Việc |
|---|---|
| `cong/rui_ro.py` | Phân rủi ro thấp, trung bình, cao từ diff |
| `cong/kiem_pr.py` | Hàm thuần: dữ liệu PR vào, quyết định và lý do ra |
| `cong/gate_app.py` | Đọc REST, phát một check run `cong-cuoi` |
| `.github/workflows/` | `cong-nhanh` chạy test, `cong-cuoi` chạy cổng, `tin-hieu-duyet` đánh thức cổng khi có lượt duyệt |
| `nghiem-thu/` | App mẫu, bản vá lỗi L1-L7, bài cục bộ, script bật cổng, công cụ đo nhịp PR, kết quả trên GitHub thật |

Python 3.9 trở lên, chỉ stdlib.

## Chạy

```sh
sh ./kiem-tra.sh                                   # test lõi, test app mẫu, bài L1-L7 cục bộ
python3 -m cong.gate_app --kho cong/tests/pr_mau.json --sha aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
python3 nghiem-thu/bat_cong.py --repo chu/repo --app-id 123 --kho
python3 nghiem-thu/ghi_token.py --repo chu/repo --kho     # token máy ghi của PR nhánh đang mở
```

Chủ repo bật cổng: bỏ `--kho`, đặt `GH_TOKEN`, rồi làm các bước tay script in ra.

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
  Đổi README tự qua: tệp này chỉ mô tả, cổng không đọc nó.
- **Test có sẵn là điều kiện nghiệm thu:** sửa, đổi tên, xoá đều là rủi ro cao, cần duyệt. Muốn thêm test thì tạo tệp mới, tự qua.
  Thêm `__init__.py` trong vùng test cũng cần duyệt, vì nó quyết định test nào được nạp.
- Thêm tệp hay symlink trùng tên mô-đun chuẩn của Python (`pprint.py`, `app/json.py`, symlink `json`; tệp không đuôi nhiều dòng thì không tính) cũng cần duyệt, vì đủ làm CI xanh giả.
  Có thể báo oan với tệp vô hại như `app/calendar.py`; người duyệt bấm qua. Gói bên thứ ba thì không bắt được: xem giới hạn 9.
- Tệp không có diff dạng chữ cần duyệt, vì không ai đọc được bên trong: tệp nhị phân, tệp rỗng, và mọi mã máy như `.pyc`, `.so`, `.wasm`.
  Trừ ảnh, PDF, phông chữ: rủi ro trung bình. Thêm `__init__.py` thì ghi một dòng chú thích để khỏi phải duyệt.
  Đổi tên kèm sửa tệp nhị phân thì tự qua, vì API không phân biệt được với đổi tên thuần: xem giới hạn 8.
- Một số tệp vô hại có thể bị báo oan vì trùng tên tệp nhạy cảm (`docs/check.md`, `docs/requirements-q4.txt`, thư mục `docs/specs/`); người duyệt bấm qua.
- Rủi ro thấp chỉ gồm tài liệu, thêm test mới và tệp tĩnh. Mọi tệp khác, gồm mã và cấu hình chạy được, là trung bình.
- **Vùng nhạy cảm do repo tự khai** trong `cong/vung-nhay-cam.txt`: chạm vùng là rủi ro cao. Mỗi dòng một mẫu, `#` là chú thích;
  `*` khớp cả `/`, `**/` là không hoặc nhiều thư mục, `[id]` là chữ thường. Mẫu khớp chính nó và mọi thứ bên dưới; mẫu không có `/` như `auth.py` khớp ở mọi tầng.
  Cổng đọc tệp ở nhánh gốc, nên PR không tự gỡ vùng được. Tệp hỏng, hay có mẫu không bao giờ khớp được (`!x`, dấu cách lạ), thì cổng báo lỗi.
  Khai vùng mới trên `main` không xét lại PR đang mở: PR đó xét lại ở lần đẩy kế tiếp.
  Một số tệp chạy được vẫn ra Thấp, vd `dev-requirements.txt`, tệp mới trong `tests/`.
- Rủi ro thấp tự qua khi đủ các điều kiện khác.
- **Rủi ro trung bình cần một phiếu phản bác** (luật L3) trên đúng head SHA: một lượt review, thường là `gh pr review <số> --comment`, thân có hai dòng đứng đầu dòng:
  `phieu-phan-bac: khong-bac` (hoặc `bac`) và `tai-hien: <cách tái hiện, hay đã thử gì>`, tối thiểu 10 ký tự. Chỉ tính phiếu của người có quyền ghi trên repo, không tính máy.
  Phiếu mới nhất trên SHA quyết. Đủ 2 phiếu `bac` trên PR (L4) thì chỉ người admin duyệt mới mở được. Người admin duyệt đúng SHA thì không cần phiếu.
  Máy rút thăm theo số PR, bỏ phiếu ở khoảng 1/5 PR làm nhóm đối chứng; đẩy commit mới không rút lại được.
  Giới hạn: máy không phân biệt được hai agent dùng chung một tài khoản, nên chính tác giả ghi phiếu cũng tính. Vì vậy phải có ô tái hiện để người đọc lại kiểm.
- Merge kiểu rebase phải tắt: cổng xét theo diff, còn rebase phát lại từng commit. Chưa tái hiện được kết quả lệch, đây là biện pháp phòng. `bat_cong.py` tắt và đọc lại.
- Quá 400 dòng (không tính lockfile): chặn, trừ khi người duyệt hợp lệ ghi dòng `ngoai-le-co: <lý do>` trong lượt duyệt.
  Dòng đó phải đứng đầu dòng, đúng chữ thường, không gạch đầu dòng hay in đậm; sai định dạng thì cổng coi như chưa ghi.
- Duyệt hợp lệ: người có quyền admin trên repo (cổng hỏi GitHub lúc xét), không phải tác giả hay người có commit
  trong PR (không tính commit merge, ví dụ bấm Update branch), không phải bot, đúng SHA.
- PR quá 250 commit bị chặn, vì API chỉ trả tới đó nên không đọc đủ được người có commit.
- Yêu cầu sửa của người có quyền admin chặn bất kể SHA và mức rủi ro trên **PR đó**. Lượt của họ bị gỡ thì vẫn chặn đến khi họ duyệt lại.
  Yêu cầu sửa không theo sang PR mới cùng nội dung; người duyệt phải đóng cả nhánh nếu không muốn nội dung đó vào.
- Mỗi lần cổng được đánh thức mà SHA không còn là head của PR mở vào `main`, ví dụ PR vừa đóng: cổng ghi `failure` thay `success` cũ. Đổi base từ `main` đi nơi khác không đánh thức cổng; đổi về thì cổng xét lại và chặn, vì PR đã từng đổi base.
