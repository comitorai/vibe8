---
name: comitor-review
description: >-
  Review the current branch of a Comitor web app (comitor-starter, or a module generated from it)
  before opening a pull request: Humble Pattern layers and "one rule, two callers", the
  Account/module boundary, workspace scoping and the permission guard on every write, failure
  direction, i18n, colour roles and @comitor/ui, tests and the fake API, docs and release notes.
  Mandatory: a Claude Code hook refuses `gh pr create` until this review has
  run on HEAD and APPROVEd it (no open blocking finding). Use it when the user asks for a code review,
  before creating or updating a PR, and whenever the hook says the
  review is missing or stale. By default the reviewer itself only REPORTS (the calling session fixes,
  § 8); pass `--fix` (`/comitor-review
  --fix`) to also apply small behaviour-preserving quality fixes to the working tree, uncommitted —
  then review and commit them and re-run, since committing moves HEAD and costs a whole extra
  review round. A re-run reviews only what was added since the last one; pass `--full`
  (`/comitor-review --full`) to force a review of the whole branch against `main` instead. The
  report is posted on the branch's open PR (queued until one exists). The result is a markdown
  report — show it to the user verbatim, outside any code fence, so its tables render; it is NOT
  the end of your turn: then fix every finding yourself (§ 8), commit and re-run until APPROVE when
  the task includes committing (otherwise leave the fixes uncommitted and say so), and carry on
  with the task you were doing before the review. Works in non-module Comitor repos too (comitor-account, the comitor-ui and comitor-web-ui
  libraries, the comitor-ds site, the Python comitor-image-service) through a repo profile declared in
  `.claude/comitor-repo.json`. Tiếng Việt: review mã trước khi mở PR — bắt buộc, phải APPROVE mới mở PR.
context: fresh
background: false
allowed-tools: Bash(git fetch *) Bash(git diff *) Bash(git merge-base *) Bash(git rev-parse *) Bash(git log *) Bash(git show *) Bash(git status *) Bash(git ls-files *) Bash(git grep *) Bash(grep *) Bash(pnpm exec biome check *) Bash(node .claude/skills/*) Bash(gh pr view *) Bash(gh pr comment *) Bash(uv run ruff check *) Bash(uv run ruff format --check *) Bash(pnpm --dir client-ts exec biome check *) Read Grep Glob Edit Write
---

# Review mã Comitor

Review những gì nhánh này thêm lên trên `main`, báo cáo, ghi lại rằng review đã chạy, rồi đăng báo cáo
lên PR. Bạn là NGƯỜI REVIEW, không phải tác giả: bạn chỉ thấy diff và bộ luật này, không thấy phiên làm
việc đã lập luận cho đoạn mã đó — `context: fresh` là cố ý. Nó còn là khoản tiết kiệm lớn nhất của mỗi
lượt: review luôn chạy đúng lúc phiên làm việc dài nhất (vừa viết xong, sắp mở PR), và `fork` sẽ chép
TOÀN BỘ phiên đó vào prompt. Bước 1 tự lấy diff bằng `git`, nên không hàng nào cần ngữ cảnh ấy.

**Vì sao cần review khi đã có `pnpm check`.** Các cổng máy chặn được thứ viết ra được bằng regex: import
sai tầng, chuỗi có dấu trong lõi, truy vấn thiếu `workspaceId`, route ghi thiếu `requirePermission(`, mã
màu viết thẳng. Những lỗi đắt nhất của Comitor đều ĐI QUA mọi cổng đó: một luật viết hai lần ở hai nơi
(dải tab Cài đặt hiện mọi tab trong khi thanh bên lọc theo quyền), `requirePermission` gọi với SAI quyền,
403 thay cho 404, đường ghi tin một danh bạ rỗng, API giả lệch route thật, một test không thể đỏ. Đó là
việc của review này — đọc `references/pitfalls.md` để thấy chúng đã xảy ra ở đâu.

**Bắt buộc bằng máy, không bằng lời nhắc:**

| Lớp | Ở đâu | Chặn gì |
|---|---|---|
| Hook Claude Code | `.claude/settings.json` → `.claude/skills/comitor-review/scripts/pr-gate.mjs` | `gh pr create` / `gh pr new`, kể cả qua `gh-agent` (và công cụ tạo PR qua MCP) khi `HEAD` chưa được review, HOẶC lần review của nó còn lỗi chặn (sidecar `comitor-review-open.md` thiếu hay không rỗng); ngay sau khi PR ra đời, đăng báo cáo đang xếp hàng lên nó |

Marker ghi **commit nào đã được review**, sidecar ghi **lần đó còn để ngỏ lỗi chặn nào** — hook đọc CẢ
HAI: mở PR chỉ được khi marker là `HEAD` và sidecar có mặt mà rỗng, tức kết luận APPROVE. Báo cáo REQUEST
CHANGES không mở được PR: sửa, commit, chạy lại (chỉ review phần thêm, lỗi cũ được mang sang và kiểm lại)
tới khi APPROVE. 🟡/⚪ không chặn. Vì sao chốt ở lúc MỞ: cổng merge phía GitHub cần branch protection, mà repo riêng tư
trên gói GitHub Free không có (`MAINTAINING.md` §3) — lý do đầy đủ ở đầu `pr-gate.mjs`. Đẩy thêm commit
lên PR đã mở thì không có lệnh nào để hook chặn: phải tự chạy lại review.

**Review chạy ở HAI mốc, không phải sau mỗi commit.** Trước khi **MỞ** PR (hook đòi APPROVE), và trên đỉnh
CUỐI CÙNG trước khi **MERGE** (trong repo không máy nào đòi; cổng ở mốc này là công cụ merge của đội, `merge-an-toan`, và PR merge ngoài công cụ đó thì chỉ còn kỷ luật). Giữa hai mốc đó, cứ commit tiếp — không luật nào
bắt chạy một lượt cho mỗi commit, và mỗi lượt mang một phần chi phí KHÔNG đổi theo cỡ delta (tài liệu
quy định, reference, bẫy — `sections.mjs` và đường nhanh ở bước 1 cắt bớt nó, không xoá được nó). Đã đo ở comitor-marketing: một PR 199 dòng tốn 5 lượt, cả 5
đều APPROVE với 0 lỗi chặn; một PR khác tốn 16 lượt. Đó là chi phí tự nguyện. Mỗi lượt chỉ review phần
thêm, nên gom nhiều commit vào một lượt KHÔNG làm mất phạm vi nào.

Nếu một lệnh git ở bước 1 hỏng: dừng, in đúng dòng `NOT REVIEWED` ở bước 6 kèm lý do, **không** ghi
marker. Một lần review không thấy diff không bao giờ được mở cổng. (`git merge-base --is-ancestor` thoát
khác 0 là một câu trả lời, không phải lỗi — bước 1.4 dựa vào nó.)

**Hồ sơ repo — chữ ⟨hồ sơ⟩ bên dưới.** Skill viết cho module sinh từ starter, nhưng cũng review repo
Comitor khác loại (IdP, thư viện, site tài liệu, dịch vụ Python, cổng PR `vibe8`). Repo khai loại của nó ở
`.claude/comitor-repo.json` (`{"profile": "<tên>"}`, thiếu file = `module`); luật riêng của từng loại ở
`references/profiles/<tên>.md`. Hồ sơ `module` không thay gì. Hồ sơ khác THAY đúng những chỗ đánh dấu
⟨hồ sơ⟩ dưới đây bằng mục cùng tên của nó, và chỉ những chỗ đó: phần còn lại (marker, sidecar, gốc, báo
cáo, dòng chân, đăng PR) giống nhau ở mọi repo — `pr-gate.mjs` không biết hồ sơ.

## 1. Lấy diff

0. **Hồ sơ.** `node .claude/skills/comitor-review/scripts/sections.mjs --profile`. Thoát 2 (tên lạ, file
   hồ sơ không có, khối hỏng) → dừng, NOT REVIEWED kèm dòng lỗi: đoán luật của repo khác là review sai mà
   không ai biết. Rồi Read `references/profiles/<tên>.md` MỘT lần — ở MỌI repo, kể cả `module` (nó có luật riêng: ngoại lệ khai
   trong repo, repo chưa có mã) — và giữ nó cho cả lượt.

`<top>` = đầu ra của `git rev-parse --show-toplevel`. Ba file trạng thái nằm ở `<top>/.claude-tmp/`
(gitignore, theo từng worktree — không đặt trong `.git/` vì Claude Code chặn ghi vào đó):

| File | Giữ gì |
|---|---|
| `comitor-review-ok` | sha ĐẦY ĐỦ của commit vừa review, và chỉ thế — hook so nguyên văn nội dung |
| `comitor-review-open.md` | các hàng "Phải sửa" mà lần review đó còn để ngỏ — rỗng khi APPROVE; hook đọc nó |
| `comitor-review-unposted.md` | báo cáo chưa đăng được lên PR nào, mỗi cái kết ở dòng chân của nó |

1. `git fetch origin main --quiet`. Hỏng (mất mạng) thì đi tiếp với `origin/main` đang có và ghi dưới
   **Đã kiểm**: "origin/main có thể cũ".
2. `git rev-parse HEAD` — giữ sha này; bước 5 ghi ĐÚNG nó.
3. `git merge-base origin/main HEAD` — gốc nhánh. Không ra gì = dừng (NOT REVIEWED); không bao giờ diff
   với một gốc rỗng.
4. Đọc marker, sidecar và hàng đợi bằng Read (thiếu file — hay thiếu cả thư mục `.claude-tmp/` — là bình
   thường; đọc cũng là thứ cho phép bước 5 và 7 ghi đè chúng). Dùng sha marker làm gốc CHỈ KHI cả `git merge-base --is-ancestor <marker> HEAD` lẫn
   `git merge-base --is-ancestor <gốc nhánh> <marker>` thoát 0 — viết sha nguyên văn, không `$(…)`. Khi đó
   bạn review lại đúng những commit thêm từ lần trước. Mọi kết quả khác (không có marker, rỗng, bị rebase
   mất, cũ hơn gốc nhánh) → gốc là gốc nhánh.
   ⚠ **Marker hợp lệ nhưng sidecar `comitor-review-open.md` THIẾU HẲN FILE → gốc cũng là gốc nhánh.**
   File VẮNG MẶT và file RỖNG là hai chuyện khác nhau: rỗng nghĩa là lượt trước có B = 0 (không còn gì
   mang sang, review delta là đúng), còn vắng mặt nghĩa là không ai biết lượt trước để ngỏ những gì —
   review delta khi đó làm lỗi chặn cũ biến mất và lượt này APPROVE sai. Ghi dưới **Đã kiểm**: "sidecar
   thiếu, review lại cả nhánh".
   ⚠ **Hai phép kiểm đó qua thì gốc PHẢI là sha marker.** Không được lấy gốc nhánh để "review lại cho
   chắc": bước 6 đã nói APPROVE ở đỉnh nghĩa là cả nhánh không còn lỗi chặn nào mà review đã thấy, và
   lỗi chặn còn mở được mang sang qua sidecar. Một lượt `cả PR` sau một chuỗi delta hợp lệ làm lại đúng
   việc các lượt trước đã làm — đã đo một lượt 14 file như vậy ở comitor-marketing. Có HAI lối thoát, và
   chỉ hai: sidecar thiếu hẳn file (đoạn ngay trên), và người dùng yêu cầu tường minh một lượt toàn bộ
   (`/comitor-review --full`, hay nói thẳng ra). Cả hai đều bỏ qua marker, gốc là gốc nhánh, và dòng
   phạm vi ghi `cả nhánh so với main`. (Cờ `--full` cũng nêu ở `description` và ở CLAUDE.md
   § "Trước khi mở PR" — ba chỗ đó phải nói cùng một thứ.)
5. `git diff --name-status <gốc>..HEAD` (danh sách file, có lockfile) và
   `git diff -U0 <gốc>..HEAD -- ':(exclude)pnpm-lock.yaml'` (các dòng thêm) — ⟨hồ sơ: **Phạm vi diff**⟩. Mỗi lệnh chạy **một** lần;
   mọi mẫu cơ học trong các reference chạy trên đầu ra `-U0` này. Grep hay Read file chỉ để xác nhận ngữ
   cảnh mà một hàng đòi. Diff quá dài cho một lần đọc thì chia theo đường dẫn — mỗi nhóm một lần
   (`… -- lib/ stores/ hooks/`, `… -- app/ components/`, `… -- '*.md' .claude/`) — không ghi nó ra file.
6. `git status --porcelain`. File trong diff mà còn sửa chưa commit → đánh giá nó theo
   `git show HEAD:<đường dẫn>` chứ không theo Read, bước 4 không đụng nó, và **Đã kiểm** nêu tên nó. Tài
   liệu QUY ĐỊNH (bước 0) mà bẩn cũng đọc ở HEAD: commit được xét theo luật của chính nó. Tìm trong file bẩn
   thì `git grep <mẫu> HEAD -- <đường dẫn>`.
7. `git show HEAD:package.json`: `"name": "comitor-starter"` là repo GỐC của các skill `comitor-*`; tên khác
   là một module — ở đó skill là bản CHÉP (`references/quality.md` § F). ⟨hồ sơ: **Bản gốc hay bản chép**⟩
   — repo không có `package.json` ở gốc thì lệnh này thoát khác 0 mà KHÔNG phải lệnh git hỏng.

Đó là đúng phạm vi PR sẽ hiện (hoặc phần thêm từ lần review trước). **Phát hiện phải nằm trên dòng diff
thêm hoặc đổi.** Đọc trọn file đổi cùng nơi gọi nó để có ngữ cảnh (đường nhanh: `-U25`, xem dưới) — một hunk giấu mất nơi gọi bị gãy —
nhưng lỗi có sẵn ở mã xung quanh nằm ngoài phạm vi: chỉ ghi ở *Có từ trước* (bước 6). Diff rỗng vì gốc
bằng HEAD → ghi marker (bước 5, giữ nguyên sidecar) và in đúng dòng `NO NEW COMMITS`.

**Lỗi chặn mang sang.** Gốc là marker → các hàng trong sidecar là danh sách "Phải sửa" ban đầu: kiểm lại
TỪNG hàng trên HEAD — bản sửa hay nằm ở file anh em, không ở file của hàng — bỏ hàng đã sửa, hàng còn thì
cuối cột luật ghi `mang sang ×k` — k là số lượt hàng đó đã còn mở, tính cả lượt này (hàng sidecar không ghi
gì → `×2`; ghi `×2` → `×3`). Hàng mang sang tính vào B như mọi hàng khác. Gốc là gốc nhánh → bỏ qua
sidecar; review đầy đủ tự tìm lại những gì còn mở — nhưng sidecar CÓ MẶT thì hàng tìm lại được mà có trong
sidecar vẫn đếm k như hàng mang sang, tức tăng một (`--full` không xoá bộ đếm).

**Trần ba lượt.** Một hàng tới `mang sang ×3` mà vẫn còn → báo cáo thêm dòng
`⛔ Leo thang: <mã luật> đã 3 lượt chưa sửa được` ngay dưới dòng phạm vi (dòng thứ hai, như khuôn ở bước 6), và
tác giả DỪNG sửa hàng đó.
Người điều phối việc — không phải tác giả — chọn một trong năm: đổi người làm · chia việc nhỏ hơn · đổi cách
làm · sửa đặc tả (đổi hành vi sản phẩm thì chủ sản phẩm quyết) · dời việc. `.claude/skills/comitor-review/scripts/pr-gate.mjs` thấy `×3`
trong sidecar thì nói đúng điều này khi chặn. Vì sao: vòng sửa không trần là chỗ tốn token lớn nhất mà không
ai đếm; ở comitor-tasks 31.10.2026 ba lượt là vừa đủ (`references/pitfalls.md` § Lệch đặc tả).

**Đường nhanh — delta nhỏ, rủi ro thấp.** Mỗi lượt trả một chi phí cố định (tài liệu quy định, reference,
bẫy) mà không đổi theo cỡ delta, nên lượt sửa vặt hai file tốn gần bằng lượt cả nhánh. Đường nhanh cắt
phần cố định đó, KHÔNG cắt hàng nào: mọi hàng có file trong phạm vi vẫn phải **xong** như thường. Áp dụng
khi CẢ BỐN điều đúng:

- tổng cột đầu của `git diff --numstat <gốc>..HEAD -- ':(exclude)pnpm-lock.yaml'` ≤ **150** dòng thêm (⟨hồ sơ:
  cùng danh sách loại trừ của **Phạm vi diff**⟩);
- ⟨hồ sơ: **Đường nhanh**⟩ không file nào trong danh sách ở bước 5 khớp `app/api/**`, `lib/**`, `stores/**`, `prisma/**`,
  `scripts/**`, `.github/**`, `.claude/settings.json`, `.claude/skills/comitor-review/scripts/**`,
  `proxy.ts`, `instrumentation.ts`, `package.json`, `pnpm-lock.yaml`, `pnpm-workspace.yaml` — chỗ của
  quyền, workspace, dữ liệu, cổng (kể cả chính cổng review) và phụ thuộc; một dòng ở đó đáng cả lượt
  đầy đủ;
- sidecar rỗng hoặc gốc là gốc nhánh — có lỗi chặn mang sang thì kiểm lại nó cần đủ ngữ cảnh;
- không có `--full`.

Đường nhanh đổi đúng hai chỗ, ở bước 2: (a) file bẫy của hồ sơ (`references/pitfalls.md` ở hồ sơ module) chỉ đọc các mục của NHÓM có file trong
phạm vi — bảng `pitfallSections` trong khối ```json profile của hồ sơ (`references/profiles/<tên>.md`; file bẫy là
khoá `pitfalls` của cùng khối), in bằng
`node .claude/skills/comitor-review/scripts/sections.mjs .claude/skills/comitor-review/<pitfalls> '§ <mục>, § <mục>'`;
(b) ngữ cảnh lấy bằng `git diff -U25 <gốc>..HEAD -- <file>` thay vì Read cả file — Read cả file và Grep nơi
gọi CHỈ khi một hunk đổi thứ được export, chữ ký hàm, prop hay kiểu, hoặc 25 dòng không đủ trả lời một hàng.
Dòng phạm vi ở bước 6 thêm `· đường nhanh`; **Đã kiểm** ghi số dòng thêm và mục `pitfalls` đã bỏ. Một điều
kiện sai → lượt đầy đủ; không có "gần đủ".

**Lockfile** ⟨hồ sơ: **Lockfile**⟩. `pnpm-lock.yaml` ra khỏi diff `-U0`, không ra khỏi review. Có nó trong danh sách file thì nêu
dưới **Đã kiểm** những gói đổi bản; lockfile đổi mà `package.json` không đổi → ❓. `better-auth` xuất hiện
mới → 🔴 (chỉ Comitor.Account được import nó). `@comitor/ui` đổi bản → `references/quality.md` § A.

## 2. Review

**Bước 0, trước mọi hàng.** Với mỗi đường dẫn đổi, tìm hàng của nó ở `references/governing-docs.md`
(⟨hồ sơ: bảng **Tài liệu quy định** của hồ sơ, và tài liệu theo viết tắt của hồ sơ⟩) và
đọc các mục được nêu **bằng `.claude/skills/comitor-review/scripts/sections.mjs`, không Read cả tài liệu** — cách gọi ở đầu bảng đó; mỗi
tài liệu một lần gọi, gộp mọi mục các hàng khớp đòi. `AGENTS.md` và `docs/kien-truc-ung-dung.md` dài cả
nghìn dòng, và đọc trọn chúng là phần lớn chi phí cố định của một lượt. Script báo `✗ … đọc cả file` thì
Read cả file đó. Giữ danh sách `tài liệu § mục` đã đọc. Bước 0 xong khi mọi đường dẫn có hàng khớp hoặc
ghi rõ "không có hàng". Rồi đọc `references/pitfalls.md` một lần (đường nhanh: chỉ mục của nhóm trong phạm
vi — bước 1) — mọi hàng bên dưới mặc định bạn đã đọc nó.

Bốn nhóm, hai mươi mốt hàng (⟨hồ sơ: bảng **Hàng** giữ, đổi, bỏ hay thêm hàng — và nói mẫu số của bảng
Kiểm⟩). Luật, mẫu cơ học, mức và điều kiện **xong** của từng hàng nằm ở reference
của nhóm; tên ngắn in đậm là tên dùng trong bảng Kiểm (bước 6):

| Nhóm | Hàng | Reference |
|---|---|---|
| Kiến trúc | **Tầng** · **Một luật** · **Ranh giới** · **Chỗ đặt** · **Account** | `references/architecture.md` |
| Dữ liệu & bảo mật | **Workspace** · **Đường ghi** · **Toàn vẹn** · **Tiêm & bí mật** · **Hướng hỏng** | `references/data-security.md` |
| Quy ước | **i18n** · **Màu & UI** · **Ngôn ngữ & tên** · **Comment** · **Kiểu** | `references/conventions.md` |
| Chất lượng | **Đúng** · **Test** · **Hợp đồng** · **Trạng thái** · **Tối giản** · **Tài liệu** | `references/quality.md` |

Mỗi reference ghi phạm vi ở đầu; diff không có file nào trong phạm vi thì cả nhóm tính n/a và bạn không
cần đọc nó. **Khuôn `.tpl` của `comitor-page`** (`templates/**`) là MÃ sẽ sinh ra trong mọi module: xét nó như
file nó sinh ra — bỏ `.tpl`, thay `__entity_kebab__`… bằng một tên thực thể — cho cả phạm vi nhóm lẫn bảng
tài liệu quy định. Mẫu cơ học `grep` trong reference chạy bằng công cụ Grep, `grep` hay `git grep` đều được. Một hàng **xong** khi điều kiện xong của nó đã có câu trả lời có/không cho từng file nó phủ —
đừng dừng ở phát hiện đầu tiên.

**Ba công cụ máy được chạy trong review** (⟨hồ sơ: **Công cụ máy**⟩), vì chúng rẻ và đọc đúng cây làm việc:

- `node .claude/skills/comitor-ui/scripts/audit.mjs` khi diff có `.tsx` hoặc `.css` — một ERROR rơi đúng
  vào dòng diff là phát hiện của hàng **Màu & UI** (nó quét mã của app, không quét khuôn `.tpl`);
- `node .claude/skills/comitor-test/scripts/check-refs.mjs .claude/skills/comitor-test .claude/skills/comitor-review`
  khi diff đụng một trong hai thư mục đó — một đường dẫn chết là phát hiện của hàng **Tài liệu**. Chỉ hai
  skill này: `comitor-ui` và `comitor-page` nêu đường dẫn tương đối và file sẽ SINH ra, nên script báo nhầm
  ở đó — cổng của chúng là `verify-skill.mjs` và `verify.mjs` (`references/quality.md` F5);
- `pnpm exec biome check <file đã sửa>` sau bước 4 — **chỉ khi có `--fix`**; lượt mặc định không sửa
  file nào nên không có gì để kiểm.

`pnpm check` thì **không**: nó là cổng riêng trước khi merge. Tuỳ repo mà `check.yml` chỉ chạy tay (starter: phút
Actions tốn tiền thật, tác giả chạy ở máy) hay tự chạy trên PR bằng runner riêng (`comitor-tasks`); đọc `on:` của nó. Review này phủ phần nó không thấy, không chạy lại nó. Cây làm việc bẩn thì kết quả hai công cụ đầu là của cây làm việc chứ
không của HEAD — ghi vậy dưới **Đã kiểm**.

## 3. Tự soát phát hiện

Trước khi báo cáo, kiểm lại từng phát hiện trên mã thật và nơi gọi nó. Mỗi phát hiện phải trích được
dòng mã hay đầu ra lệnh chứng minh nó; không trích được thì bỏ, còn suy đoán thì hạ thành câu hỏi (❓ — in
ở bước 6, không bao giờ tính). Một phát hiện sai làm tác giả mất nhiều hơn cái nó cứu được. Rồi soát từng
ô theo giới hạn ở bước 6 (`Ở đâu` ≤ 32 ký tự, chữ ≤ 120): quá thì cắt chữ, không cắt dữ kiện.

## 4. Sửa sẵn phần chất lượng — CHỈ khi được gọi kèm `--fix`

**Mặc định bước này KHÔNG chạy: review chỉ BÁO CÁO, không đụng một file nào.** Nó chỉ chạy khi lời gọi
skill mang cờ `--fix` (`/comitor-review --fix`), hoặc người dùng nói thẳng là muốn sửa sẵn.

Vì sao opt-in: bản sửa nằm trong cây làm việc → tác giả commit nó → HEAD đổi → marker hết hiệu lực →
BẮT BUỘC thêm một lượt review đầy đủ chỉ để xác nhận bản sửa của chính review. Đã đo ở PR #88 của
comitor-marketing: lượt `02:09:29` báo `1 fixed`, lượt `02:10:37` một phút sau báo `0 findings`. Một
lượt trọn vẹn cho một bản sửa 🟡 là cái giá sai.

**Không có cờ thì**: phát hiện của hàng **Tối giản** và **Comment** vẫn được BÁO CÁO bình thường — vào
bảng *Nên sửa* như mọi phát hiện 🟡/⚪ khác — còn bảng *Đã sửa sẵn* vắng mặt và F = 0. Bỏ qua phần còn
lại của mục này và đi thẳng sang bước 5.

Có cờ thì phát hiện của hàng **Tối giản** (dùng lại, đơn giản hoá, hiệu năng hiển nhiên, mã chết) và
**Comment** là của bạn để sửa: sửa thẳng vào file. Mã chết chỉ sửa được khi nó KHÔNG export và Grep cả repo (kể cả truy
cập động: ``t(`x.${k}`)``, `obj[key]`) cho thấy không gì đọc nó. Mọi hàng khác chỉ báo cáo — chúng cần
phán đoán của tác giả.

Không bao giờ sửa (⟨hồ sơ: **Không bao giờ sửa**⟩): một file bước 1.6 thấy bẩn; `messages/*.json`; `prisma/migrations/**`; khuôn `.tpl` của
`comitor-page` (không nằm trong `tsc` — sửa nó cần `verify.mjs`); bản chép skill ở MODULE; và file khung
ngoài đúng những dòng diff đã đổi (CONTRIBUTING.md § "Thay đổi chạm FILE KHUNG": một lần format lại file
khung là xung đột ở mọi module). Đổi thứ có thể đổi cách hiển thị là quyết định của tác giả.

- Chỉ sửa thứ giữ nguyên hành vi và bạn chắc chắn; còn ngờ thì để là phát hiện.
- Kiểm bằng `pnpm exec biome check <file đã sửa>`; sửa chạm import hay chữ ký hàm thì nói rõ cần
  `pnpm typecheck` trước khi commit.
- **Không bao giờ commit.** Bản sửa nằm trong cây làm việc để người dùng đọc lại.

## 5. Ghi lại lần review

Làm bước này mỗi khi review thật sự chạy — kể cả khi tìm ra lỗi — và **trước khi viết báo cáo**, để báo
cáo là thứ cuối cùng bạn in ra. Dùng Write ghi sha của bước 1.2 (không gọi lại `git rev-parse` — HEAD có
thể đã đổi) làm nội dung DUY NHẤT của `<top>/.claude-tmp/comitor-review-ok`, và các hàng "Phải sửa" của
lần này, nguyên văn, làm nội dung duy nhất của `<top>/.claude-tmp/comitor-review-open.md` (rỗng khi
B = 0). Đừng đổi định dạng marker — hook so nguyên văn nội dung với một sha. **Sidecar là kết luận mà hook
đọc**: có mặt và rỗng (chỉ khoảng trắng) = APPROVE = mở PR được; còn một hàng = chặn. Luôn ghi nó, kể cả khi
rỗng — vắng mặt là chặn. Báo cáo không nhắc tới hai file này; dòng chân đã nêu sha.

Bản sửa ở bước 4 (chỉ có khi gọi kèm `--fix`) chưa commit nên không làm HEAD đổi, marker vẫn đúng. Commit bất cứ thứ gì — kể cả chính
bản sửa đó — là HEAD đổi, marker hết hiệu lực, và lần chạy sau chỉ review phần thêm từ sha này. Đó là chủ ý.

**Không bao giờ ghi marker hay sidecar ở chỗ nào khác ngoài bước này**, và không ghi chúng khi chưa review:
hook tin nội dung hai file đó.

## 6. Báo cáo

Toàn bộ thông điệp cuối cùng của bạn là khối dưới đây, điền đủ, dạng markdown thường — hàng rào mã ở đây
chỉ để khoanh khuôn mẫu; đừng bao báo cáo thật trong hàng rào, nếu không bảng không hiện. Đây là bình luận
review trên PR, người đọc là người review PR — nên nó trả lời "merge được chưa?" trước khi liệt kê gì.
Không có gì trước dòng đầu, không có gì sau dòng cuối ngoài dòng `PR` của bước 7. "Cuối cùng" là của
**lượt review**, không phải của lượt làm việc: phiên đã gọi review đi tiếp ở bước 8.

Đếm trước: N phát hiện, B lỗi chặn (🔴 + 🟠 còn mở sau bước 4), F đã sửa (luôn 0 khi không có `--fix`). Kết luận suy từ B — không đoán,
không sửa giữa chừng. Câu hỏi (❓) không phải phát hiện và không bao giờ tính. Bước 4 chỉ sửa 🟡 và ⚪, nên
không có 🟠 nào được "sửa mất".

Sau dòng kết luận và dòng phạm vi, mỗi phát hiện là một hàng ở một trong bốn bảng, xếp theo việc người
đọc phải làm: **Phải sửa** (🔴/🟠 còn mở), **Nên sửa** (🟡/⚪ còn mở), **Câu hỏi** (❓), **Đã sửa sẵn** (bước
4 — vắng mặt khi không có `--fix`). Hàng nặng nhất trước, rồi theo file. Bỏ bảng rỗng cùng tiêu đề của
nó, trừ "Phải sửa" — bảng đó in "Không có.". Rồi bảng **Kiểm** và **Ghi chú review**.

```
## <✅ APPROVE — merge được   khi B = 0 | ❌ REQUEST CHANGES — còn <B> lỗi chặn   khi B > 0>
Đã review <gốc>..<sha> · <cả nhánh so với main | phần thêm từ lần review trước> · <số file> file<· đường nhanh — khi bước 1 chọn nó><· hồ sơ <tên> — khi không phải module>
<⛔ Leo thang: <mã luật> đã 3 lượt chưa sửa được — chỉ khi một hàng tới `mang sang ×3`>

## Phải sửa trước khi merge (<B>)
| | Ở đâu | Phát hiện |
| :-: | --- | --- |
| <🔴 hoặc 🟠> | `<file>:<dòng>` | <Sai gì.> <Làm gì.> (<mã luật><, mang sang ×k — hàng mang sang>) |
<một dòng "Không có." thay cho bảng khi B = 0>

## Nên sửa (<số>)
| | Ở đâu | Phát hiện |
| :-: | --- | --- |
| <🟡 hoặc ⚪> | `<file>:<dòng>` | <Sai gì.> <Làm gì.> (<mã luật>) |

## Câu hỏi cho tác giả (<số>)
| Ở đâu | Câu hỏi |
| --- | --- |
| `<file>:<dòng>` | <Mã đang làm gì.> <Câu hỏi?> |

## Đã sửa sẵn trong cây làm việc (<F>)
Chưa commit. Đọc lại rồi commit — HEAD đổi nên chạy lại /comitor-review (chỉ review phần thêm) trước khi đẩy.

| Ở đâu | Đã đổi gì |
| --- | --- |
| `<file>:<dòng>` | <Sai gì, và bản sửa làm gì.> |

## Kiểm
| Nhóm | Hỏng | Đạt |
| --- | --- | --- |
| Kiến trúc | <tên hàng hỏng, cách nhau dấu phẩy> | <n>/5 |
| Dữ liệu & bảo mật | | <n>/5 |
| Quy ước | | <n>/5 |
| Chất lượng | | <n>/6 |
```

Mẫu số 5/5/5/6 là của hồ sơ `module`; hồ sơ khác dùng dòng "Mẫu số bảng Kiểm" ở mục **Hàng** của nó, kể cả tên
hàng đã đổi hay thêm.

**Mọi bảng phải vừa terminal.** Claude Code xuống dòng trong ô, nhưng hễ một ô quá 4 dòng là cả bảng bị
vẽ lại thành thẻ `Ở đâu: / Phát hiện:`. Giới hạn dưới đây giữ bảng là bảng tới cỡ khung ~90 cột:

- `Ở đâu` là tên file cộng `:dòng`, tối đa 32 ký tự. Hai file trong diff trùng tên (khác thư mục) thì
  thêm thư mục cha tới khi khác nhau (`api/invoices/route.ts:31`, `[id]/route.ts:12`). Không bao giờ đường
  dẫn đầy đủ: nó không có khoảng trắng nên không xuống dòng được.
- Mỗi ô chữ tối đa 120 ký tự khi hiện ra (dấu backtick không tính): sai gì, rồi làm gì, rồi mã luật trong
  ngoặc — `(T3)`, `(G1)`, `(W3)`, `(N1)`; luật không có mã thì `(AGENTS § Quy ước)`. Quá thì cắt chữ, không
  cắt dữ kiện; vị trí phụ ghi "cả `x.ts:12`" khi còn chỗ.
- Một emoji mỗi hàng: mức. Bảng Câu hỏi và Đã sửa không cần emoji.
- Ký tự `|` trong ô — kể cả trong backtick — viết `\|`, nếu không hàng bị tách.

**Kiểm**: một hàng hỏng khi nó có hàng ở "Phải sửa" hoặc "Nên sửa"; hàng "Đã sửa" và câu hỏi không làm nó
hỏng, n/a tính là đạt.

Sau bảng Kiểm, **Ghi chú review**: "Tài liệu đã đọc" luôn có, ba mục kia chỉ khi có nội dung. Mỗi ý một
gạch đầu dòng.

```
## Ghi chú review
**Tài liệu đã đọc**
- <tài liệu § mục, § mục — một gạch cho mỗi tài liệu bước 0 đã đọc, hoặc "không có">

**Đã sửa** — chỉ khi bước 4 sửa file
- <đường dẫn đầy đủ>

**Đã kiểm**
- <một thứ đã xác minh ngoài các phát hiện, hoặc một tài liệu thấy đã cũ>

**Có từ trước, ngoài diff này** — chỉ khi bước 1 thấy
- <một lỗi, kèm `file:dòng`>
```

Rồi dòng chân, luôn có, đứng riêng một dòng — nó là **hợp đồng máy** (`pr-gate.mjs` đọc
nó), nên viết tiếng Anh và giữ đúng hình dạng:

```
COMITOR-REVIEW <sha>: <APPROVE | REQUEST CHANGES> · <N> findings (<B> blocking, <F> fixed)
```

N đếm hàng của "Phải sửa", "Nên sửa" và "Đã sửa"; B đếm hàng "Phải sửa"; F đếm hàng "Đã sửa". `<sha>` là
`git rev-parse --short` của sha bước 1.2 ở mọi chỗ trong báo cáo (marker ở bước 5 giữ sha đầy đủ). Một lần
review phần thêm duyệt PHẦN THÊM, không duyệt cả PR — dòng phạm vi nói rõ là cái nào; lỗi chặn của lần
trước đã được mang sang và kiểm lại, nên APPROVE ở đỉnh vẫn có nghĩa là cả nhánh không còn lỗi chặn nào
mà review đã thấy.

**Mức** (⟨hồ sơ: **Mức** thêm hay đổi dòng của danh sách này⟩)**:**

- **🔴** hành vi hoặc nơi gọi gãy; dữ liệu đi sang workspace khác (truy vấn chọn hàng thiếu
  `workspaceId`, `workspaceId` lấy từ thân request); route ghi thiếu chốt quyền, chốt SAI quyền, hoặc
  `@api-guard` ngoài hai họ lý do; chốt chỉ ở giao diện; XSS, tiêm, SSRF, open redirect; bí mật vào bundle
  hay vào diff; migration làm gãy bản đang chạy; đổi một hợp đồng liên module; import `better-auth/*`.
- **🟠** khả năng lỗi hoặc hồi quy; quy tắc nghiệp vụ nằm ngoài `lib/core/` (`.tsx`, hook, store,
  `route.ts`); một luật viết hai lần; lõi trả chuỗi hiển thị; chuỗi hiển thị ngoài `messages/` hoặc thiếu
  ở một ngôn ngữ; nơi gọi/anh em không đổi theo; đường lỗi fail-open; đường ghi tin danh bạ rỗng; 403
  thay 404; thiếu thẻ phiên bản ở `PUT` ghi đè; Server Action ghi dữ liệu; tự dựng component gói đã có;
  mã màu; `fetch` ngoài `lib/api-client/`; API giả lệch route thật; quy tắc mới không test, hoặc test
  không thể đỏ; vượt ranh giới Account (bảng định danh, màn hình của Account, vai trò thô thứ năm); mã
  lệch đặc tả của việc, kể cả bản lệch «an toàn hơn» (DT1); file khung đổi mà CHANGELOG không có mục "Module đã sinh ra phải làm gì".
- **🟡** các hàng kiến trúc còn lại (chỗ đặt, `"use client"` quá cao); tên, ngôn ngữ của mã, comment; xói
  mòn kiểu; tài liệu lệch mã; lãng phí nhỏ; quá tay; `catch` rỗng không log.
- **⚪** nit về phong cách, và mọi thứ ghi *(đề xuất)*.
- **❓** câu hỏi tác giả phải trả lời; không phải phát hiện.

Ví dụ đã điền — một lần review phần thêm, gọi kèm `--fix`, hai lỗi chặn:

```
## ❌ REQUEST CHANGES — còn 2 lỗi chặn
Đã review 3f2a9c1..8d41e07 · phần thêm từ lần review trước · 6 file

## Phải sửa trước khi merge (2)
| | Ở đâu | Phát hiện |
| :-: | --- | --- |
| 🔴 | `[invoiceId]/route.ts:31` | `DELETE` chốt bằng `invoice.update`. Đổi sang `invoice.delete` — người chỉ được sửa đang xoá được. (G1) |
| 🟠 | `invoice-grid.tsx:88` | Tính "quá hạn" ngay trong component, lệch `isOverdueInvoice` ở lõi. Gọi hàm lõi. (M2) |

## Nên sửa (1)
| | Ở đâu | Phát hiện |
| :-: | --- | --- |
| 🟡 | `invoice-form.tsx:12` | `"use client"` đặt trên cả biểu mẫu chỉ vì một nút. Tách nút thành đảo client riêng. (R2) |

## Đã sửa sẵn trong cây làm việc (2)
Chưa commit. Đọc lại rồi commit — HEAD đổi nên chạy lại /comitor-review (chỉ review phần thêm) trước khi đẩy.

| Ở đâu | Đã đổi gì |
| --- | --- |
| `invoice-grid.tsx:40` | Xoá comment nhắc lại tên biến. |
| `invoices.ts:118` | Xoá `formatTotal`, hàm nội bộ không ai gọi. |

## Kiểm
| Nhóm | Hỏng | Đạt |
| --- | --- | --- |
| Kiến trúc | Một luật, Ranh giới | 3/5 |
| Dữ liệu & bảo mật | Đường ghi | 4/5 |
| Quy ước | | 5/5 |
| Chất lượng | | 6/6 |

## Ghi chú review
**Tài liệu đã đọc**
- docs/kien-truc-ung-dung.md § 2, § 3 rìa B, § 7
- AGENTS.md § Ranh giới Account / app

**Đã sửa**
- app/(shell)/invoices/invoice-grid.tsx
- lib/invoices.ts

**Đã kiểm**
- handler giả `DELETE /api/invoices/:id` gọi cùng `requirePermission`
- cả `vi` lẫn `en` có `errors.code.INVOICE_LOCKED`

COMITOR-REVIEW 8d41e07: REQUEST CHANGES · 5 findings (2 blocking, 2 fixed)
```

**Lối thoát không phải một lần review** in đúng một dòng, không kết luận, không bảng:

- Gốc bằng HEAD (bước 1): `COMITOR-REVIEW <sha>: NO NEW COMMITS` — marker đã ghi; bước 7 vẫn đăng hàng đợi
  nếu có, và dòng `PR` của nó theo sau.
- Lệnh git hỏng hoặc gốc rỗng (bước 1): `COMITOR-REVIEW <sha>: NOT REVIEWED — <lý do>` — không marker,
  không đăng gì. Một lần bỏ dở không bao giờ in `APPROVE`.

## 7. Đăng lên PR

Mọi báo cáo có kết luận đi lên PR của nhánh dưới dạng một bình luận, nên PR luôn mang báo cáo mới nhất.
Đăng là một bước của skill này, nên làm không cần hỏi.
Làm sau khi soạn xong báo cáo và trước khi in nó; hỏng ở đây không bao giờ đổi kết luận, marker hay báo cáo.

1. **Nhánh.** `git rev-parse --abbrev-ref HEAD`. Là `main` hoặc `HEAD` (tách rời) → không có PR để đăng và
   không xếp hàng; dòng cuối là `PR: không áp dụng — <main | HEAD tách rời>`.
2. **Danh sách chờ.** Hàng đợi (đã đọc ở bước 1.4) giữ những báo cáo chưa PR nào nhận, mỗi cái kết ở dòng
   chân. Chỉ giữ báo cáo mà sha ở chân qua đúng phép kiểm của bước 1.4 — `--is-ancestor <sha> HEAD` và
   `--is-ancestor <gốc nhánh> <sha>` — để báo cáo của một nhánh đã merge hay đã rebase không bao giờ tới PR
   này. Danh sách chờ = các báo cáo giữ lại, cũ trước, rồi báo cáo lần này (không có ở lối `NO NEW COMMITS`).
3. **PR.** `gh pr view --json number,state,url` (không đối số = PR của nhánh hiện tại). Báo "no pull
   requests found" = chưa có PR. Phiên mở PR bằng `gh-agent` thì gọi `gh-agent` ở đây và ở bước 4, kèm nhánh và
   `-R <owner>/<repo>` như nó đòi: `gh` trần có thể đang là tài khoản khác.
4. **Đăng.** PR `OPEN` → với từng báo cáo chờ: Write nó vào `<top>/.claude-tmp/comitor-review-post.md` rồi
   `gh pr comment <number> --body-file <top>/.claude-tmp/comitor-review-post.md`. Rồi MỘT lần Write: hàng
   đợi thành những gì chưa đăng được — rỗng khi thành công, cả danh sách chờ khi chưa có PR hoặc lệnh hỏng.
   Chưa có PR thì không sao: hook `PostToolUse` đăng hàng đợi ngay sau `gh pr create`.

Dòng cuối của báo cáo khi đó được nối thêm đúng một dòng:
`PR #<n>: đã đăng <k> báo cáo — <url>` · `PR: chưa có PR cho <nhánh> — đã xếp hàng, sẽ đăng ngay sau gh pr create` ·
`PR: không đăng được — <lỗi>` (`gh` chưa đăng nhập → `gh auth login`).

## 8. Sau báo cáo — phiên gọi review SỬA HẾT rồi LÀM TIẾP

Bước 1–7 là việc của người review (`context: fresh`). Mục này là việc của **phiên đã gọi** `/comitor-review` —
phiên tác giả, có đủ ngữ cảnh để sửa. Báo cáo là một bước giữa chừng, **không phải điểm dừng**: hiện nó cho
người dùng (nguyên văn, ngoài hàng rào mã), rồi đi tiếp ngay trong cùng lượt, không hỏi lại.

Vì sao: người dùng hay giao "làm liên tục tới mốc X" (mở PR, merge, xong cả lộ trình), và review chạy giữa
đường tới mốc đó. Một agent coi báo cáo là câu trả lời cuối thì dừng ở đúng chỗ chưa ai bảo dừng — người dùng
quay lại thấy một bảng phát hiện chưa ai sửa và một việc bỏ dở.

1. **Sửa MỌI phát hiện** — "Phải sửa" (🔴/🟠) trước, rồi "Nên sửa" (🟡/⚪). Đọc lại mã trước khi sửa: phát
   hiện có thể sai, và một phát hiện chứng minh được là sai thì ghi lý do vào câu trả lời thay vì sửa theo.
   Giới hạn của bước 4 (không sửa `messages/*.json` …) là giới hạn của NGƯỜI REVIEW, không của tác giả — tác
   giả sửa ở đâu cần sửa, theo luật của repo (migration mới thay vì sửa migration cũ, đổi chuỗi ở CẢ `vi` lẫn
   `en`…).
2. **Câu hỏi (❓)**: trả lời được từ mã hay từ việc đang làm thì tự trả lời và sửa nếu cần. Chỉ dừng hỏi người
   dùng khi câu hỏi thật sự là quyết định của họ (đổi hành vi sản phẩm, đặc tả mâu thuẫn — DT1).
3. **Kiểm bản sửa** bằng cổng của phần đã đụng (`pnpm check` hay phần của nó, cổng skill nếu đụng skill).
4. **Commit và chạy lại `/comitor-review`** (chỉ review phần thêm) tới khi APPROVE — khi việc đang làm đã
   gồm commit (người dùng giao mốc mở PR / merge, hay bảo commit). Chưa ai cho commit thì để bản sửa trong cây
   làm việc, và nói rõ trong câu trả lời rằng phải commit + chạy lại review trước khi mở PR. Gom bản sửa vào
   MỘT commit rồi chạy một lượt — đừng một lượt cho mỗi phát hiện.
5. **Làm tiếp việc trước review**: mở PR, merge, sang gói việc kế tiếp… — tới đúng mốc người dùng đã giao.

Chỉ có ba lý do được dừng sau báo cáo: dòng `⛔ Leo thang` (trần ba lượt, bước 1 — báo người điều phối, đừng
sửa tiếp hàng đó); một quyết định chỉ người dùng đưa ra được (bước 2 trên); người dùng đã nói rõ chỉ muốn
review, không muốn sửa. Ngoài ba lý do đó, dừng sau báo cáo là bỏ dở việc.
