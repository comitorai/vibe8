# Kết quả nghiệm thu trên GitHub thật

Ngày 2026-11-05. Repo thật đã bật cổng, khoá App thật, mã cổng `2bf203e` (trừ dòng ghi khác). Tác nhân là cộng tác viên quyền ghi.
Tệp này chỉ ghi lại đã thử gì, không phải điều kiện của cổng. Bài cục bộ ở `kiem_cuc_bo.py` không thay được các dòng dưới.

| Ca | PR | Làm gì | Kết quả cổng | Merge |
|---|---|---|---|---|
| L1 | 4 | Logic sai, test đỏ | `chan (thap)`: có lượt `cong-nhanh` không xanh | từ chối |
| L2 | 5 | Xoá test | `chan (cao)`: đổi test có sẵn; `cong-nhanh` xanh | từ chối |
| L3 | 6 | Sửa `cong-nhanh.yml` để in pass | `chan (cao)`: đổi `.github/`; `cong-nhanh` xanh giả | từ chối |
| L4 | 7 | Workflow nhánh tạo check tên `cong-cuoi` | App `failure`, check giả `success`, PR vẫn bị chặn | từ chối |
| L5 đẩy thẳng | — | `git push` lên `main` | «Changes must be made through a pull request» | `main` không đổi |
| L5 `--admin` | 4, 11 | `gh pr merge --admin` bằng cộng tác viên | «Required status check "cong-cuoi" is expected / is failing» | từ chối |
| L5 `--admin` admin thật | 23 | Lỗi L1, `gh pr merge 23 --admin --merge` bằng tài khoản chủ `comitorai`, ngày 05/11 | `chan (thap)`; «Required status check "cong-cuoi" is failing. (mergePullRequest)» | từ chối, `main` vẫn `21aaa81` |
| L6 | 8 | Workflow nhánh đòi `environment: gate`, in độ dài khoá | `chan (cao)`; job lấy khoá `failure`, log không có khoá | từ chối |
| L7 | 12 | Lỗi L1, tiêu đề và thân chèn lệnh | `chan (thap)` như L1, không đổi vì thân PR | từ chối |
| Giả `cong-nhanh` | 9 | Tệp workflow khác, cùng tên hiển thị `cong-nhanh`, nghe `push` và `pull_request`, in pass, kèm lỗi L1 | `chan (cao)`; lượt giả không tính | từ chối |
| **L8** | 10 | Đổi base sang nhánh có workflow in pass, đổi lại `main` | **LỌT** ở mã `2bf203e`: `cho_qua (thap)`, `CLEAN` | không merge, đã đóng |
| L8 sau bản vá | 14 | Như trên, mã `c0ead46`. Base lạ in pass và nghe thêm `edited`, kèm lỗi L1 | `cho (thap)`: hai lượt `cong-nhanh` xanh, không lượt nào tính vì PR có `base_ref_changed` | từ chối |
| Che mô-đun chuẩn | 16 | Symlink `pprint.py`, tệp `cong/json.py`, mã `5ff6558` | `chan (cao)`; job cổng vẫn chạy xong, mã PR không vào job cổng | từ chối |
| **Đối chứng thấp** | 15 | Thêm một tệp công cụ, mã `c0ead46` | `cho_qua (thap)`, `CLEAN`, đọc thấy ở giây 29 sau khi mở PR | merge bằng cộng tác viên, không người duyệt |
| Vùng nhạy cảm | 28 | Sửa `nghiem-thu/ket-qua.md`, vùng khai ở `main` từ PR 27, mã `35dc4cf`. Không có vùng thì tệp tài liệu này là thấp | `chan (cao)` sau ~22 giây: «chạm vùng nhạy cảm `nghiem-thu/ket-qua.md`», summary «2 mẫu» | chờ người duyệt |

Có người duyệt:

- PR 3, mã trước `2bf203e`, người duyệt lấy từ biến chứ chưa hỏi quyền admin: trước duyệt `chan (cao)`, người đó duyệt đúng SHA thì `cho_qua (cao)` sau 19 giây.
- PR 13, mã `2bf203e`, cổng hỏi GitHub quyền người duyệt bằng token App: trước duyệt `chan (cao)`, người có quyền admin duyệt đúng SHA thì `cho_qua (cao)` sau 24 giây, cộng tác viên merge được mà không cần `--admin`.
- PR 17, mã `5ff6558`: trước duyệt `chan (cao)`, người có quyền admin duyệt đúng SHA thì `cho_qua (cao)` sau 32 giây, cộng tác viên merge được mà không cần `--admin`.

Yêu cầu sửa bị gỡ, PR 18, rủi ro thấp, logic cổng không đổi: trước đó `cho_qua (thap)`. Người có quyền admin yêu cầu sửa thì `chan (thap)` sau 28 giây. Cộng tác viên gỡ được lượt đó, GitHub ghi `DISMISSED`, cổng xét lại 24 giây sau và vẫn `chan (thap)`, merge bị từ chối. Đóng PR, không merge.

Ô merge của PR 17 khi `cong-cuoi` còn đỏ, xem bằng tài khoản chủ repo: nút merge bị khoá, không hiện ô bỏ qua yêu cầu. Đây là ảnh giao diện, chưa phải lần chạy `gh pr merge --admin`.

Một lần chạy lại kịch bản thử đẩy đè nhánh của PR 4 sau khi đã ghi kết quả, nên head hiện tại của PR 4 khác SHA lúc thử. Không ảnh hưởng `main`.

PR từ fork cùng SHA, PR 20 (fork của cộng tác viên) và PR 21 (nội bộ), một tệp rủi ro thấp: PR 20 mở một mình thì `cong-nhanh` chạy không cần phê duyệt, lượt ghi đúng `head_repository` của fork, cổng `cho_qua (thap)` sau 35 giây. Mở PR 21 cùng SHA thì cổng xét lại, vẫn `cho_qua (thap)`, cả hai `CLEAN`. Check gắn theo SHA nên hai PR dùng chung một kết quả, nội dung merge như nhau. Không merge, đã đóng cả hai. Fork từ người không phải cộng tác viên chưa thử.

## Phiếu phản bác trên PR mức Vừa thật

PR 38 (06/11), PR Vừa đầu tiên ngoài nhóm đối chứng (`boc_tham_bo` = False; PR 35–37 thuộc nhóm đối chứng). Sửa `nghiem-thu/ghi_token.py` kèm tệp test mới, cổng xếp `trung_binh`. Phiếu do agent độc lập viết, đăng dưới dạng review COMMENT bằng tài khoản `phanbinhdcna` (tác giả PR, có quyền ghi).

| Bước | SHA | Kết quả |
|---|---|---|
| Mở PR, chưa có phiếu | `0eb6b62` | `chan (trung_binh)`: «cần phiếu phản bác trên đúng SHA» |
| Phiếu 1 (không đăng) | `0eb6b62` | `khong-bac`, kèm 2 lỗi nhẹ: mốc lấy PR song song đóng sau, tên nhánh có `#` bị cắt trong `head=` |
| Sửa 2 lỗi, đẩy commit | `fa92fb8` | `chan (trung_binh)` lại, vì phiếu phải trên SHA mới |
| Phiếu 2, lượt hẹp trên diff sửa, đăng lên PR | `fa92fb8` | `khong-bac`; 3 điểm nhẹ để PR sau. Tín hiệu duyệt chạy, `cong-cuoi` → `cho_qua (trung_binh)` sau ~2 phút |

Ghi nhận: phiếu 1 bắt được lỗi thật trước merge (`#` trong tên nhánh làm `head=` khớp nhầm nhánh, đã tái hiện bằng GET thật), nhãn `bat-truoc-merge`. Phiếu 2 lấy GitHub thật làm bằng chứng GitHub giải mã `head=` đã mã hoá. Token máy ghi PR 38: 381 216; script đọc cả thư mục `subagents/` nên có thể đã gồm hai agent phản bác, chưa tách riêng.

## Giả mạo kết quả

- Tác giả tự duyệt, tự yêu cầu sửa: GitHub từ chối.
- `POST check-runs` bằng token thường: 403, phải là GitHub App.
- `POST statuses` context `cong-cuoi`, `success`: GitHub nhận, PR 4 vẫn bị chặn, merge bị từ chối. PR này cũng có `failure` của App, nên riêng ca này không tách được tác dụng của ghim `app_id`.

## Vì sao L8 lọt, và số đo sau đó

Lượt `pull_request` sự kiện `edited` tạo 2 giây sau khi đổi base vẫn checkout ref merge của base cũ, log ghi rõ `refs/pull/10/merge` và merge vào base cũ.
Lượt không ghi nó đã chạy ref nào nên cổng không lọc được theo mốc thời gian. Sửa: PR từng đổi base thì không lượt nào tính, `cong-nhanh` bỏ `edited`, `reopened`.

Đo trên repo đối chứng, token thường:

- Mở PR và đẩy 10 commit, cách nhau 3 và 15 giây: 11/11 lượt checkout đúng merge của head mới.
- Đổi base 3 lần, đọc `/issues/N/events` ngay sau lệnh: 3/3 lần thấy sự kiện ở lần đọc đầu, 0,55-0,58 giây.
- Đổi base bằng REST, GraphQL, và ngay sau khi mở PR: 3/3 thấy sự kiện ở lần đọc đầu. Lượt `edited` tạo 1-2 giây sau khi đổi vẫn merge vào base cũ, dù base mới khác SHA.
- Stacked PR, nhánh cha tự xoá sau merge: có `automatic_base_change_succeeded`, base đổi cùng lúc với sự kiện ở hai lần đọc 0,83 và 4,22 giây. Xoá bằng `gh pr merge --delete-branch`: PR con đóng, base không đổi.
- Đẩy commit khi đã xung đột: 2/2 không có lượt, kể cả khi ngay trước đó API còn báo `clean`. Đẩy commit lúc PR đóng: 1/1 không có lượt.
- Chạy lại lượt trên PR đã xung đột: giữ id và `created_at`, `run_attempt` thành 2, cùng commit merge cũ.
- Đổi tên nhánh đầu có PR đã đóng, mở PR mới từ tên mới: `head=` chỉ thấy PR mới. Lượt cũ giữ tên cũ. Đẩy commit sinh 1 lượt mang tên mới, merge đúng head mới.

## Chưa thử trên repo thật

PR từ fork của người không phải cộng tác viên.
