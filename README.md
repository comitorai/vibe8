# Cổng cuối cho PR do agent viết

Cổng chạy ở phía GitHub: quyết định chỉ dựa trên diff, kết quả CI và lượt duyệt theo đúng commit,
không đọc lời khai trong thân PR. Tên `xuong` và `cong` là tên tạm, gom ở `cong/ten.py`.

**Trạng thái: mới kiểm cục bộ, CHƯA chạy trên GitHub thật.** Chưa dùng được làm cổng thật khi chưa qua
nghiệm thu trên repo thật và chưa giải giới hạn số 1 trong [docs/bao-mat.md](docs/bao-mat.md).

## Gồm gì

| Đường dẫn | Việc |
|---|---|
| `cong/rui_ro.py` | Phân rủi ro thấp, trung bình, cao từ diff |
| `cong/kiem_pr.py` | Hàm thuần: dữ liệu PR vào, quyết định và lý do ra |
| `cong/gate_app.py` | Đọc REST, phát một check run `cong-cuoi` |
| `.github/workflows/` | `cong-nhanh` chạy test, `cong-cuoi` chạy cổng |
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

- `cong-nhanh` phải `success` trên đúng head SHA, do Actions phát. `neutral`, `skipped` không tính.
- Đổi `.github/`, `xuong.yml`, luật, CODEOWNERS, script check, hoặc xoá, giảm test: rủi ro cao, cần duyệt.
- Lockfile: tối thiểu trung bình. Hiện mức trung bình chưa khác mức thấp về điều kiện qua.
- Quá 400 dòng: chặn, trừ khi người duyệt hợp lệ ghi dòng `ngoai-le-co: <lý do>` trong lượt duyệt.
- Duyệt hợp lệ: người có quyền trong repo, không phải tác giả hay người có commit trong PR, không phải bot,
  đúng SHA, sau lần push cuối.
