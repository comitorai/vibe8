# Cổng cuối cho PR do agent viết

Cổng chạy ở phía GitHub: quyết định chỉ dựa trên diff, kết quả CI và lượt duyệt theo đúng commit,
không đọc lời khai trong thân PR. Tên `xuong` và `cong` là tên tạm, gom ở `cong/ten.py`.

**Trạng thái: mới kiểm cục bộ, CHƯA chạy trên GitHub thật.** Chưa dùng được làm cổng thật khi chưa qua
nghiệm thu trên repo thật. Đã kiểm gì, giới hạn gì: [docs/bao-mat.md](docs/bao-mat.md).

## Gồm gì

| Đường dẫn | Việc |
|---|---|
| `cong/rui_ro.py` | Phân rủi ro thấp, trung bình, cao từ diff |
| `cong/kiem_pr.py` | Hàm thuần: dữ liệu PR vào, quyết định và lý do ra |
| `cong/gate_app.py` | Đọc REST, phát một check run `cong-cuoi` |
| `.github/workflows/` | `cong-nhanh` chạy test, `cong-cuoi` chạy cổng, `tin-hieu-duyet` đánh thức cổng khi có lượt duyệt |
| `nghiem-thu/` | App mẫu, bản vá lỗi L1-L6, bài cục bộ, script bật cổng |

Python 3.9 trở lên, chỉ stdlib.

## Chạy

```sh
sh ./kiem-tra.sh                                   # test lõi, test app mẫu, bài L1-L6 cục bộ
python3 -m cong.gate_app --kho cong/tests/pr_mau.json --sha aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
python3 nghiem-thu/bat_cong.py --repo chu/repo --app-id 123 --kho
```

Chủ repo bật cổng: bỏ `--kho`, đặt `GH_TOKEN`, rồi làm các bước tay script in ra.

## Luật

- PR phải nhắm `main`, và là PR mở duy nhất vào `main` ở SHA đó.
- Mọi lượt của tệp workflow `cong-nhanh`, sự kiện `pull_request`, trên đúng head SHA và nhánh đầu, tạo sau khi PR mở và sau lần đổi base
  cuối, phải `success`. Lượt đỏ không bị lượt xanh che. Đỏ vì lỗi thoáng qua thì bấm chạy lại lượt đó; đỏ vì `main` lúc đó còn hỏng thì chạy
  lại không chữa được, vì lượt chạy lại dùng commit merge cũ: đẩy một commit mới.
- **Một nhánh đầu một PR:** nhánh từng có PR khác, kể cả đã đóng, thì không lượt nào được tính, vì PR đã đóng vẫn sinh lượt mới mà không biết
  lượt đó test với base nào. Cổng báo chờ. Đẩy sang nhánh tên mới rồi mở PR mới.
- Đổi `.github/`, `xuong.yml`, luật, CODEOWNERS, script check, tệp khai phụ thuộc, lockfile: rủi ro cao, cần duyệt.
- **Test có sẵn là điều kiện nghiệm thu:** sửa, đổi tên, xoá đều là rủi ro cao, cần duyệt. Muốn thêm test thì tạo tệp mới, tự qua.
  Thêm `__init__.py` trong vùng test cũng cần duyệt, vì nó quyết định test nào được nạp.
- Thêm tệp trùng tên mô-đun chuẩn của Python (`pprint.py`, `app/json.py`) cũng cần duyệt, vì đủ làm CI xanh giả. Có thể báo oan
  với tệp vô hại như `app/calendar.py`; người duyệt bấm qua.
- Tệp không có diff dạng chữ cần duyệt, vì không ai đọc được bên trong: tệp nhị phân, tệp rỗng, và mọi mã máy như `.pyc`, `.so`, `.wasm`.
  Trừ ảnh, PDF, phông chữ: rủi ro trung bình. Thêm `__init__.py` thì ghi một dòng chú thích để khỏi phải duyệt.
- Một số tệp vô hại có thể bị báo oan vì trùng tên tệp nhạy cảm (`docs/check.md`, `docs/requirements-q4.txt`, thư mục `docs/specs/`); người duyệt bấm qua.
- Rủi ro thấp và trung bình tự qua khi đủ các điều kiện khác.
- Quá 400 dòng (không tính lockfile): chặn, trừ khi người duyệt hợp lệ ghi dòng `ngoai-le-co: <lý do>` trong lượt duyệt.
  Dòng đó phải đứng đầu dòng, đúng chữ thường, không gạch đầu dòng hay in đậm; sai định dạng thì cổng coi như chưa ghi.
- Duyệt hợp lệ: người trong biến `XUONG_NGUOI_DUYET` của environment `gate`, không phải tác giả hay người có commit
  trong PR (không tính commit merge, ví dụ bấm Update branch), không phải bot, đúng SHA. Danh sách rỗng thì mọi PR đều bị chặn.
- PR quá 250 commit bị chặn, vì API chỉ trả tới đó nên không đọc đủ được người có commit.
- Yêu cầu sửa của người trong danh sách chặn bất kể SHA và mức rủi ro trên **PR đó**. Lượt của họ bị gỡ thì vẫn chặn đến khi họ duyệt lại.
  Yêu cầu sửa không theo sang PR mới cùng nội dung; người duyệt phải đóng cả nhánh nếu không muốn nội dung đó vào.
- SHA không còn là head của PR mở vào `main`: cổng thu hồi bằng `failure`, để `success` cũ không chờ sẵn khi đổi base đi rồi đổi lại.
x
