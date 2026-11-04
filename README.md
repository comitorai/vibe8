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
python3 -m cong.gate_app --kho cong/tests/pr_mau.json --pr 7
python3 nghiem-thu/bat_cong.py --repo chu/repo --app-id 123 --kho
```

Chủ repo bật cổng: bỏ `--kho`, đặt `GH_TOKEN`, rồi làm các bước tay script in ra.

## Luật

- PR phải nhắm `main`, và là PR mở duy nhất vào `main` ở SHA đó.
- Mọi lượt của tệp workflow `cong-nhanh`, sự kiện `pull_request`, trên đúng head SHA phải `success`.
  Lượt đỏ không bị lượt xanh che: phải bấm chạy lại chính lượt đó.
- Đổi `.github/`, `xuong.yml`, luật, CODEOWNERS, script check, tệp khai phụ thuộc, lockfile, hoặc xoá, giảm test:
  rủi ro cao, cần duyệt. Rủi ro thấp và trung bình tự qua khi đủ các điều kiện khác.
- Quá 400 dòng (không tính lockfile): chặn, trừ khi người duyệt hợp lệ ghi dòng `ngoai-le-co: <lý do>` trong lượt duyệt.
- Duyệt hợp lệ: người trong biến `XUONG_NGUOI_DUYET` của environment `gate`, không phải tác giả hay người có commit
  trong PR, không phải bot, đúng SHA. Danh sách rỗng thì mọi PR đều bị chặn.
- Yêu cầu sửa của người trong danh sách chặn bất kể SHA và mức rủi ro. Lượt của họ bị gỡ thì vẫn chặn đến khi họ duyệt lại.
