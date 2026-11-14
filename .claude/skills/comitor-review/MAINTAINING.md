# Bảo trì skill `comitor-review`

Dành cho NGƯỜI bảo trì skill và người dựng repo, không phải cho agent đang review.

## 1. Bản gốc ở `comitor-starter`, mọi app Comitor chép ra

Cùng chỗ với `comitor-ui`, `comitor-page`, `comitor-test`. Module sinh từ starter mang sẵn; module cũ hơn chép
theo lệnh ở `.claude/skills/comitor-ui/MAINTAINING.md` §5. Repo Comitor KHÔNG phải module (Account, thư viện,
site tài liệu, dịch vụ Python, cổng PR `vibe8`) cũng nhận skill này, với một HỒ SƠ (§7) — bảng repo ↔ hồ sơ ở §5 của `comitor-ui/MAINTAINING.md`. Skill này khác ba skill kia ở chỗ nó có BA mảnh nằm
NGOÀI thư mục của nó, và thiếu một mảnh là cổng hỏng theo hướng MỞ mà không gì báo:

| Mảnh | Thiếu thì |
|---|---|
| `.claude/skills/comitor-review/` | không có review |
| `.claude/settings.json` (khối `hooks`) | `gh pr create` không bị chặn (kể cả khi review còn lỗi chặn), báo cáo xếp hàng không tự đăng sau khi mở PR |
| dòng `/.claude-tmp/` trong `.gitignore` | marker và hàng đợi bị commit, và marker của người này mở cổng cho người khác |
| `.claude/comitor-repo.json` — CHỈ repo không phải module | review dùng luật module cho một repo khác loại: báo sai hàng loạt, hoặc bỏ sót luật riêng của repo (§7) |

Module đã có `.claude/settings.json` riêng thì GỘP khối `hooks`, đừng chép đè.

Thấy skill sai ở một module → sửa ở starter, chạy §4, rồi chép lại. Đừng sửa bản chép: luật review lệch giữa các
module là luật review không ai tin.

## 2. Hook — `.claude/skills/comitor-review/scripts/pr-gate.mjs`

Lúc chạy là một file (ca thử mới của `--self-test` ở `.claude/skills/comitor-review/scripts/tests/pr-gate-cases.mjs`, chỉ nạp khi tự kiểm) cho cả `PreToolUse` (chặn tạo PR khi `HEAD` chưa được review APPROVE) và `PostToolUse` (đăng hàng đợi
lên PR vừa tạo). Giới hạn đã biết ghi ở đầu file — đọc trước khi "vá" một ca lọt. Hook là chốt
"sửa hết lỗi chặn" DUY NHẤT nằm trong repo: không có branch protection thì GitHub không có cổng merge, cổng lúc merge
nằm ngoài repo (§3).

Sáu điều đừng đổi:

- **Nhận dạng lệnh không dùng regex trên cả chuỗi.** Hook có thời hạn (10 giây ở `settings.json`) và hook quá hạn
  thì KHÔNG chặn — một regex quay lui trên một lệnh dài là đường lọt.
- **Marker chỉ chứa sha.** Hook so NGUYÊN VĂN nội dung với `git rev-parse HEAD`.
- **Kết luận đọc từ sidecar `comitor-review-open.md`, và vắng mặt là CHẶN** (`gateDecision`). Đừng chuyển sang đọc
  hàng đợi `comitor-review-unposted.md`: nó rỗng ngay khi báo cáo đăng được lên PR, nên đọc nó là cho qua mọi lần
  review chạy khi PR đã có. Đừng cho "vắng mặt" qua cho tiện: đó là đúng ca bước 1.4 của SKILL.md gọi là "không ai
  biết lượt trước để ngỏ gì".
- **Báo cáo chỉ đăng khi sha ở chân là tổ tiên của HEAD** — báo cáo của một lịch sử đã rebase không bao giờ tới
  nhầm PR.
- **Xét repo của LỆNH, không của PHIÊN** (`resolveTarget`). `payload.cwd` là thư mục phiên Claude Code đang đứng;
  một phiên làm chéo hai repo chạy `cd ../b && gh pr create` hay `gh pr create -R org/b`. Quay về `payload.cwd`
  trần là chặn nhầm ca đầu và CHO QUA ca sau bằng marker của repo kia — đo được 10/2026. Không xét được đích thì
  CHẶN, đừng rơi về thư mục phiên.
- **PostToolUse đăng bằng đúng công cụ đã tạo PR, và lỗi khi gọi công cụ thì báo** (`ghRunner`, `postToolUse`). `gh` trần có thể
  đang là tài khoản khác; im lặng thì báo cáo nằm lại hàng đợi mà không ai biết. Công cụ MCP không có lệnh để theo
  nên mới dùng `gh`. Các lỗi ở hàng đợi chưa báo hết, khai ở đầu `pr-gate.mjs`.

## 3. Skill không có cổng merge — và vì sao

Skill này chốt ở lúc MỞ PR, không chốt ở lúc merge. Trạng thái commit `comitor-review` (`review.yml` +
`ci-status.mjs`) đã bỏ ở v0.39.0: repo riêng tư gói GitHub Free không đặt được required check, nên trạng thái đó chưa
bao giờ chặn được merge, và từ 10/2026 nó chỉ chạy tay. Repo nào có branch protection và muốn lại cổng này thì lấy hai
tệp từ commit trước v0.39.0.

Số đo API: `rules/branches/main` trả 403 Upgrade (03.11.2026); `branches/main/protection` đọc bằng token agent trả 404
ở `comitor-starter` và `comitor-tasks` (04.11.2026), chưa rõ do không có protection hay do token không đủ quyền. Hai
kết quả này chỉ nói GitHub không chặn được, không nói cách merge của đội.

Cổng lúc merge của đội nằm ngoài repo: `merge-an-toan` ở `Comitor-JSC/.github` đọc CI, cỡ PR, nhãn rủi ro và hai phiếu
review; mức `cao-san-pham` đòi thêm Alex quyết, bằng APPROVE của người duyệt hoặc phiếu quyết. Nó chỉ có tác dụng khi PR đi qua nó; merge bằng nút trên web hay `gh pr merge` thì GitHub vẫn cho, lúc đó chỉ còn kỷ luật.

## 4. Kiểm

```bash
node .claude/skills/comitor-review/scripts/pr-gate.mjs --self-test     # nhận dạng lệnh + cổng APPROVE + tách hàng đợi + PostToolUse
node .claude/skills/comitor-test/scripts/check-refs.mjs .claude/skills/comitor-review   # mọi đường dẫn skill nhắc tới có thật
grep -c -- '--full' .claude/skills/comitor-review/SKILL.md CLAUDE.md   # cờ `--full` ở ĐỦ ba chỗ: SKILL.md ≥ 3 (description chiếm 2 dòng, nên ≥ 3 mới chứng minh bước 1.4 còn nó), CLAUDE.md ≥ 1
node .claude/skills/comitor-review/scripts/sections.mjs --self-test      # cú pháp mục + đối chứng âm tính
node .claude/skills/comitor-review/scripts/sections.mjs --check-table    # mọi mục bảng + bẫy của HỒ SƠ repo này có thật Ở REPO NÀY (§7)
```

Chạy sau mỗi lần sửa skill, và sau mỗi lần ĐỔI TÊN/XOÁ một file mà reference nhắc tới.

⚠ **Dòng chân `COMITOR-REVIEW <sha>: <kết luận> · …` là hợp đồng giữa HAI chỗ**: khuôn báo cáo ở `SKILL.md` § 6
và regex ở `pr-gate.mjs`. Đổi hình dạng ở một chỗ mà không đổi chỗ kia thì hàng đợi không tách được báo cáo và báo
cáo không tới PR — đổi cả hai trong cùng một commit, rồi chạy self-test.

## 5. Những thứ giữ chi phí mỗi lượt xuống — đừng lùi lại

Review là cổng BẮT BUỘC, nên chi phí của nó nhân với số lượt của mọi PR. Đã đo trên 8 PR của
comitor-marketing: 3–16 lượt mỗi PR, phần lớn là delta 2–7 file, và chi phí mỗi lượt gần như KHÔNG
đổi theo cỡ delta (vẫn đọc đủ tài liệu quy định, vẫn chạy đủ mọi hàng). Các khoản dưới đây giữ phần cố
định đó nhỏ, và khoản nào cũng dễ bị lùi lại vì mỗi cái nghe có vẻ "an toàn hơn":

| Khoản | Đừng | Vì sao |
|---|---|---|
| `context: fresh` ở frontmatter | đổi về `fork` | `fork` chép CẢ phiên làm việc vào prompt, và review luôn chạy lúc phiên dài nhất. Không hàng nào cần ngữ cảnh đó — bước 1 tự lấy diff bằng `git` |
| Bước 4 opt-in (`--fix`) — người REVIEW không sửa; phiên gọi review sửa hết rồi làm tiếp (SKILL.md § 8) | bật mặc định; hay ngược lại, để phiên gọi coi báo cáo là câu trả lời cuối và dừng | bản sửa → tác giả commit → HEAD đổi → marker hết hiệu lực → một lượt đầy đủ nữa chỉ để xác nhận bản sửa của chính review (đo ở comitor-marketing PR #88: `1 fixed` lúc 02:09:29, `0 findings` lúc 02:10:37) |
| Gốc PHẢI là marker khi hai phép kiểm của bước 1.4 qua | "review lại cả nhánh cho chắc" | làm lại đúng việc các lượt delta trước đã làm; APPROVE ở đỉnh đã nghĩa là cả nhánh sạch lỗi chặn (SKILL.md §6). Hai lối thoát, và chỉ hai: người dùng yêu cầu tường minh (`--full`), hoặc sidecar `comitor-review-open.md` THIẾU HẲN FILE — không ai biết lượt trước để ngỏ gì thì không mang sang được |
| Bước 0 trích mục bằng `.claude/skills/comitor-review/scripts/sections.mjs` | Read cả `AGENTS.md` / `docs/kien-truc-ung-dung.md` | hai file đó ~1800 dòng cho mỗi lượt; một ô của bảng thường cần 30–230 dòng. Script hỏng theo hướng ĐỌC NHIỀU HƠN: không thấy đề mục thì bảo Read cả file, không thấy gạch thì in cả mục |
| Đường nhanh (SKILL.md § 1) | nới ngưỡng 150 dòng hay bớt đường dẫn nhạy cảm | nó chỉ cắt phần ĐỌC (mục `pitfalls` ngoài phạm vi, Read cả file thay `-U25`), không cắt hàng nào. Danh sách nhạy cảm là chỗ của quyền, workspace, dữ liệu, cổng và phụ thuộc — một dòng ở đó đáng cả lượt đầy đủ |

Hai khoản cuối có máy canh một phần: `sections.mjs --check-table` (§4) đỏ khi một mục bảng trỏ tới không
còn — chạy nó ở MỌI repo sau khi chép, vì bảng `governing-docs.md` đi chung còn `AGENTS.md` thì mỗi module
một bản. Một gạch đầu dòng đổi chữ mà bảng còn nêu bằng nháy cũng làm nó đỏ; sửa bảng, đừng bỏ nháy.

Chưa làm, và là chỗ tiếp theo nếu còn chậm: chạy bốn nhóm song song (bốn subagent, gộp báo cáo).

## 6. Thêm một luật

- Mỗi luật là lỗi ĐÃ XẢY RA ở một repo Comitor, kèm cách nhận ra nó trên một dòng diff. Ghi nguồn vào
  `references/pitfalls.md`. Luật lý thuyết không vào đây.
- Luật mà MÁY kiểm được thì đưa vào máy (một script `check-*`, một override Biome), không vào review — review là
  cho phần cần phán đoán. Rồi xoá dòng tương ứng ở đây, hoặc đổi nó thành "phần máy không thấy".
- Một luật ở MỘT chỗ: chữ của luật nằm ở `AGENTS.md` / `docs/kien-truc-ung-dung.md` / skill tương ứng; reference
  ở đây chỉ nói CÁCH THẤY nó trên diff và MỨC của nó, rồi trỏ sang. `references/governing-docs.md` là bảng trỏ.
- Mỗi hàng có điều kiện **xong** — "đã nhìn" không phải điều kiện xong.
- Không ghim số đếm ("21 hàng") ngoài `SKILL.md` § 2 và bảng Kiểm ở § 6, và hai chỗ đó phải sửa cùng nhau.

## 7. Hồ sơ repo — review cả repo KHÔNG phải module

Từ starter v0.28.0 skill review được mọi repo Comitor, không chỉ module sinh từ starter. Repo khai loại của nó ở
`.claude/comitor-repo.json` (`{"profile": "<tên>"}`) — NGOÀI thư mục skill, nên `rsync --delete` lúc chép
không xoá nó. Thiếu file = `module`, nên module cũ không phải làm gì. Bảng repo ↔ hồ sơ ↔ skill được chép ở
`comitor-ui/MAINTAINING.md` §5 (một bản duy nhất).

**Một hồ sơ là một file `references/profiles/<tên>.md`, và có ĐỦ các mục dưới đây, đúng tên** — trừ `module`: nó
không thay gì nên chỉ có khối profile và các luật riêng của nó (SKILL.md trỏ tới
chúng bằng tên ở chỗ đánh dấu ⟨hồ sơ⟩). Mục không đổi gì so với module thì ghi "như module" — đừng bỏ mục, vì
người review không phân biệt được "giống module" với "người viết hồ sơ quên".

| Mục | Thay chỗ nào của SKILL.md |
|---|---|
| khối ```json profile (đầu file) | `docs` (viết tắt → đường dẫn trong repo), `table`, `pitfalls`, `pitfallSections` — `sections.mjs` đọc khối này; `table`/`pitfalls` thường trỏ về CHÍNH file hồ sơ |
| `## Tài liệu quy định` | bảng ba cột như `governing-docs.md` (bước 0) |
| `## Phạm vi diff` | thứ loại khỏi `-U0`, cách chia nhóm khi diff dài (bước 1.5) |
| `## Bản gốc hay bản chép` | bước 1.7 |
| `## Đường nhanh` | danh sách đường dẫn nhạy cảm |
| `## Lockfile` | đoạn Lockfile |
| `## Hàng` | bảng `Nhóm · Hàng · Áp/Đổi/Bỏ/Thêm · Luật ở repo này (nguồn)`, rồi dòng "Mẫu số bảng Kiểm: …" |
| `## Công cụ máy` | ba công cụ của bước 2 |
| `## Không bao giờ sửa` | danh sách của bước 4 |
| `## Mức` | thêm hay đổi dòng của danh sách Mức (§6) |
| `## Số bản` | hàng F1 của `quality.md` |
| `## Bẫy` | mục bẫy của repo (đường nhanh đọc theo `pitfallSections`) — mỗi bẫy là lỗi đã xảy ra, kèm nguồn |

Bốn luật khi viết hồ sơ:

- **Nguồn là tài liệu của CHÍNH repo đó**, kèm `file:dòng` hay `tài liệu § mục`. Hồ sơ trỏ, không chép luật — cùng
  luật "một luật ở MỘT chỗ" của §6.
- **Hàng "Đổi" phải nói hàng module SAI ở đâu** khi áp nguyên văn (một câu), không chỉ nói luật mới. Đó là thứ
  giữ hồ sơ khỏi lặng lẽ yếu hơn module.
- **Hướng hỏng của hồ sơ là ĐÒI NHIỀU HƠN**: không chắc một hàng module có áp không thì để "Áp".
- Sửa hồ sơ hay đề mục của một tài liệu nó trỏ tới → `sections.mjs --check-table --profile <tên>` **trong checkout
  của repo đó** (bảng trỏ vào tài liệu của nó). Ở starter, chỉ `module` kiểm được; hồ sơ khác kiểm ở repo đích.
