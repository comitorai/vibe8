#!/usr/bin/env node
/**
 * Hook Claude Code của skill `comitor-review` — một file cho cả hai sự kiện, khai ở `.claude/settings.json`.
 *
 *   PreToolUse  — từ chối `gh pr create` / `gh pr new`, kể cả qua `gh-agent` hay đường dẫn đầy đủ (và công cụ
 *                 tạo PR qua MCP) khi HEAD chưa được
 *                 /comitor-review APPROVE: `.claude-tmp/comitor-review-ok` phải chứa ĐÚNG sha của HEAD, VÀ
 *                 `.claude-tmp/comitor-review-open.md` (các hàng "Phải sửa" lần review đó còn để ngỏ) phải CÓ
 *                 và RỖNG — tức B = 0, kết luận APPROVE (`gateDecision`).
 *   PostToolUse — ngay sau khi PR ra đời, đăng các báo cáo đang xếp hàng (`comitor-review-unposted.md`) lên
 *                 nó, bằng đúng công cụ đã tạo PR (`gh-agent` thì `gh-agent`). Thiếu bước này thì báo cáo viết TRƯỚC
 *                 khi có PR không tới PR nào, và người dùng phải chạy review thêm một lần chỉ để đăng. Không đăng được
 *                 thì báo lý do, báo cáo nằm lại hàng đợi.
 *   node pr-gate.mjs --self-test — chạy các ca mẫu, kể cả đối chứng âm tính (ca mới: `tests/pr-gate-cases.mjs`).
 *
 * ── VÌ SAO ĐÒI APPROVE NGAY LÚC MỞ PR, KHÔNG CHỈ ĐÒI "ĐÃ REVIEW" ───────────────────────────────────────
 * Bản trước chỉ so marker: mở PR được với một báo cáo REQUEST CHANGES, và chốt "phải sửa" dồn hết cho một trạng
 * thái lúc merge. Chốt đó cần branch protection, mà repo riêng tư trên gói GitHub Free KHÔNG có (đo 18.10.2026 ở
 * comitor-tasks: API branch protection trả 403 "Upgrade to GitHub Pro"), nên lỗi chặn đi thẳng tới `main` mà không
 * máy nào cản. Nay chốt "sửa hết lỗi chặn" đứng ở chỗ còn chạy được; trạng thái kia đã bỏ ở v0.39.0.
 * Kết luận đọc từ SIDECAR, không từ hàng đợi báo cáo: sidecar là thứ bước 5 của SKILL.md ghi CÙNG LÚC với marker
 * ở mọi lần review, kể cả khi đã có PR (hàng đợi thì rỗng ngay khi báo cáo đăng được). Sidecar THIẾU HẲN file là
 * "không ai biết lượt trước để ngỏ gì" → chặn, đúng nghĩa nó có ở bước 1.4. 🟡/⚪ ("Nên sửa") không vào sidecar
 * nên không chặn — cùng ranh giới APPROVE của SKILL.md § 6.
 *
 * ── VÌ SAO CHẶN Ở `gh pr create` MÀ KHÔNG Ở `git push` ──────────────────────────────────────────────
 * Luật là "APPROVE trước khi MỞ PR, APPROVE trên đỉnh cuối trước khi MERGE". Đẩy một nhánh chưa review không hại
 * gì; mở PR thì đồng đội bắt đầu đọc. Lần review trên đỉnh cuối không phải việc của hook này — đẩy thêm commit
 * lên PR đã mở không có lệnh nào để hook chặn.
 *
 * ── XÉT REPO CỦA LỆNH, KHÔNG PHẢI CỦA PHIÊN ─────────────────────────────────────────────────────────
 * `payload.cwd` là thư mục của PHIÊN Claude Code. Repo được xét là repo mà LỆNH nhắm tới (`resolveTarget`):
 * thư mục sau mọi `cd` đứng trước `gh pr create` trong cùng chuỗi lệnh, rồi đối chiếu `-R`/`--repo`/`GH_REPO=`
 * (hay `owner`/`repo` của công cụ MCP) với remote `origin` của thư mục đó. Lệch, hay không xét được (`cd $X`,
 * `cd -`, không có `origin`) → CHẶN, kèm cách viết lại lệnh. Bản cũ xét theo thư mục của phiên và hỏng cả hai
 * chiều, đo 10/2026: chặn nhầm `cd ../starter && gh pr create` bằng HEAD của module, và CHO QUA
 * `gh pr create -R org/module` từ starter bằng marker của starter.
 *
 * ── GIỚI HẠN ĐÃ BIẾT (đều cố ý) ─────────────────────────────────────────────────────────────────────
 * · Hook chỉ thấy việc làm QUA Claude Code. Mở PR ở terminal hay trên web thì hook không biết. Chốt lúc merge là việc của
 *   công cụ merge của đội (`merge-an-toan`), không phải của hook; repo nào không dùng công cụ đó thì chỉ còn kỷ luật.
 * · Nhận dạng lệnh bằng một lượt duyệt biết dấu nháy (`echo "gh pr create"` không bị chặn). Lệnh nằm sau một
 *   wrapper ngoài danh sách, trong `sh -c "…"`, hay trong một alias thì lọt — cùng loại với mở PR ở terminal.
 *   Cũng lọt: `pr "create"`, `pr --repo X create`, tạo PR bằng `api -X POST …/pulls`, `export GH_REPO=org/b; gh pr
 *   create`, lệnh tạo PR thứ hai trong cùng chuỗi (chỉ xét lệnh đầu). Cũng lọt: `"cd" ../b`,
 *   `cd -- ../b`, `cd -P ../b`, và chuyển hướng dính lệnh (`>out gh pr create -R org/b`, `gh pr create 2>&1 -R org/b`, `gh pr create<<A`).
 *   Cũng lọt: lệnh trong nháy kép, vì nháy kép đọc là chữ: `URL="$(gh pr create)"`, `eval "gh pr create"`.
 *   Cũng lọt: `bash -o pipefail gh-agent pr create` (giá trị của cờ đọc thành tên lệnh), `=gh pr create` của zsh, và ghi lệnh ra tệp rồi chạy (`sh s.sh`), cùng loại với mở PR ở terminal.
 *   Cũng lọt: chạy gián tiếp qua alias, `git config alias.x '!gh pr create'; git x`, `git -c alias.y='!gh pr create' y`, `gh alias set y 'pr create'; gh y`, hay `cat >>.git/config` cùng nội dung: `gh` không đứng đầu lệnh nào nên không lần đọc nào thấy.
 *   Heredoc nhắc tới `gh pr create` ở ĐẦU DÒNG hay trong cặp backtick (backtick là dấu tách) thì bị chặn nhầm, và
 *   bị xét theo thư mục của phiên — gặp thật 18.10.2026 khi viết thân PR bằng heredoc. Hỏng theo hướng chặn, không
 *   theo hướng lọt; viết thân PR ra file riêng (`--body-file`) rồi chạy lệnh tạo PR riêng. 11.2026 đã thử bỏ thân heredoc theo danh sách trắng cả lệnh, rồi rút: mỗi vòng review lại tìm ra đường lọt mới. Cũng chặn dư vì các lần đọc lệch
 *   nhau, ít gặp: `cd a\ b && gh pr create`, `cd \⏎ sub && …`, comment có dấu tách (`# Mở PR; cd sub⏎gh pr create`).
 * · PostToolUse đăng báo cáo bằng đúng công cụ đã tạo PR, nhưng không mang theo biến đứng trước lệnh (`GH_TOKEN=… gh pr create`).
 *   Công cụ gọi bằng đường tương đối, hay nằm trong repo, thì đăng bằng tên cuối qua PATH; PATH không có thì báo lỗi, báo cáo
 *   nằm lại hàng đợi. Đường tuyệt đối tới tệp đúng tên `gh`/`gh-agent` ngoài repo vẫn được chạy, kể cả khi chỉ nêu trong văn bản.
 *   Công cụ MCP không có lệnh để theo nên dùng `gh`. Lỗi khi gọi công cụ (`gh` lỗi, PR không mở, PR nhánh khác, hết giờ) được báo,
 *   báo cáo nằm lại hàng đợi. Chưa báo: báo cáo có sha ngoài lịch sử bị bỏ khỏi hàng đợi, đoạn không có dòng chân bị mất, hàng đợi
 *   không ghi được thì thoát 1 và lần sau đăng trùng.
 *   Thân heredoc nêu `gh pr create` đứng trước lệnh `gh-agent pr create` thật thì đăng bằng `gh` trần: đọc công cụ theo lần nêu đầu tiên.
 * · `gh pr create --head <nhánh khác>` vẫn bị xét theo HEAD của thư mục đích.
 * · `cd` chỉ được đọc khi đứng TRƯỚC lệnh tạo PR trong cùng chuỗi; `pushd`, `git -C`, `cd` trong một hàm hay
 *   alias thì không — hook xét thư mục của phiên như cũ.
 * · Node hỏng thì hook lỗi và Claude Code cho đi tiếp — hướng MỞ. Không gì đỡ ca này, nên `--self-test`
 *   (MAINTAINING.md §4) là lưới duy nhất.
 * · Agent có Bash nên ghi được marker và sidecar bằng tay. Thông điệp từ chối dặn đừng; đó là kỷ luật, không
 *   phải chốt.
 */
import { execFileSync } from "node:child_process";
import { readFileSync, realpathSync, statSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";

const MARKER = ".claude-tmp/comitor-review-ok";
const OPEN = ".claude-tmp/comitor-review-open.md";
const QUEUE = ".claude-tmp/comitor-review-unposted.md";
const FOOTER = /^COMITOR-REVIEW ([0-9a-f]{7,40}): (APPROVE|REQUEST CHANGES)\b/;

const SEPARATORS = new Set([";", "&", "|", "(", ")", "{", "}", "`", "\n"]);
const KEYWORDS = new Set(["if", "then", "else", "elif", "do", "while", "until", "!"]);
const SHELLS = new Set(["bash", "sh", "zsh", "dash"]);
const WRAPPERS = new Set(["env", "command", "exec", "time", "nohup", "nice", "timeout"]);
// Hai cách nhận wrapper, cả hai đều được đọc (`pullRequestTarget`). Rộng: theo tên cuối đường dẫn và tính cả trình thông
// dịch, nên thấy `bash ~/bin/gh-agent pr create`; `bash script.sh` không khớp gì nên vẫn cho qua. Hẹp: đúng tên trần.
const isWrapper = (word) => WRAPPERS.has(baseName(word)) || SHELLS.has(baseName(word));
const isBareWrapper = (word) => WRAPPERS.has(word);
// So theo tên cuối đường dẫn: `gh-agent` là `gh` bọc của máy agent, và lệnh hay gọi nó bằng đường dẫn đầy đủ.
// Ghi cứng trong khung: nơi không có `gh-agent` thì tên này không bao giờ khớp, không hại gì.
const GH_COMMANDS = new Set(["gh", "gh-agent"]);

/**
 * Tách một lệnh shell thành các lệnh đơn, mỗi lệnh là một mảng từ. Một lượt duyệt ký tự, không regex trên cả
 * chuỗi (regex quay lui trên lệnh dài là cách một hook vượt thời hạn — và hook quá hạn thì KHÔNG chặn).
 * Nháy lệch cặp → `null`, để nơi gọi quét lại không cần biết nháy (hướng chặn).
 * `comments` = bỏ từ `#` đầu từ tới hết dòng.
 */
function scan(command, quoteAware, comments) {
  const segments = [];
  let words = [];
  let word = "";
  let inWord = false;
  let quote = null;
  const endWord = () => {
    if (inWord) words.push(word);
    word = "";
    inWord = false;
  };
  const endSegment = () => {
    endWord();
    if (words.length > 0) segments.push(words);
    words = [];
  };
  for (let p = 0; p < command.length; p++) {
    const ch = command[p];
    if (quote) {
      word += ch;
      if (ch === quote) quote = null;
      continue;
    }
    if (quoteAware && (ch === "'" || ch === '"')) {
      quote = ch;
      word += ch;
      inWord = true;
      continue;
    }
    if (comments && ch === "#" && !inWord) {
      while (p + 1 < command.length && command[p + 1] !== "\n") p++;
      continue;
    }
    if (SEPARATORS.has(ch)) {
      endSegment();
      continue;
    }
    if (ch === " " || ch === "\t") {
      endWord();
      continue;
    }
    word += ch;
    inWord = true;
  }
  endSegment();
  return quote ? null : segments;
}

/** Bản lệnh đã đọc `\\`: `\\` + LF là nối dòng, `\\'` và `\\"` không phải dấu nháy, `\\x` là `x`. Không biết nháy. */
function unescaped(command) {
  let out = "";
  for (let p = 0; p < command.length; p++) {
    if (command[p] !== "\\") {
      out += command[p];
      continue;
    }
    const next = command[++p] ?? "";
    if (next !== "\n" && next !== "'" && next !== '"') out += next;
  }
  return out;
}

const unquote = (word) => (/^(["']).*\1$/s.test(word) ? word.slice(1, -1) : word);

const baseName = (word) =>
  unquote(word ?? "")
    .split("/")
    .pop();

/**
 * Lệnh có tạo PR không, và tạo cho repo NÀO. `null` = không tạo PR. Ngược lại `{ cds, repo }`:
 * · `cds` — đối số của mọi `cd` đứng TRƯỚC `gh pr create` trong cùng chuỗi lệnh, theo thứ tự (nơi gọi `resolve` chúng
 *   từ thư mục của phiên); `null` khi một `cd` không suy ra được tĩnh (`$BIEN`, `$(…)`, `` ` ``, `cd -`; `cd` trần là `~`);
 * · `repo` — `owner/name` của `-R`/`--repo`/`GH_REPO=`, hay `null` khi lệnh không nêu;
 * · `cli` — công cụ đã gọi, để PostToolUse đăng báo cáo bằng chính nó: `{ command, via }`, `via` là trình thông dịch nếu có.
 * Chỉ đọc tĩnh, cùng lượt duyệt của `scan` — không chạy gì trong shell.
 *
 * Đọc nhiều lần, vì hook không đoán nổi `\` hay `#` nào shell thật sự đọc thế nào: `gh pr create \⏎ -R org/b` cần nối dòng,
 * `# x \⏎ cd ../b` thì không; `#` trong `${#a}`, `$((#a))` không mở comment. Đọc lệnh nguyên văn và bản đã đọc `\`, mỗi bản
 * có và không có comment, rồi đọc thêm một lần chỉ nhận đúng tên `gh`: `targetIn` dừng ở lệnh tạo PR đầu tiên, nên nhận thêm
 * tên thì `gh-agent pr create -R org/a; gh pr create -R org/b` che mất lệnh sau. Cả năm lần đọc đều làm hai lượt: wrapper
 * rộng rồi wrapper hẹp, cùng lý do: nhận thêm wrapper thì `/usr/bin/env cd /tmp && gh pr create` đọc `cd` thành lệnh thật,
 * còn shell chỉ cho `cd` đó chạy trong tiến trình con. Một lần thấy lệnh tạo PR là đủ để xét; các lần ra thư mục khác nhau,
 * hay nêu hai repo khác nhau, thì CHẶN. Lượt hẹp giữ nguyên cách đọc của bản trước, nên nhận thêm dạng lệnh không được
 * đổi kết quả của lệnh bản đó đã đọc ra; lưới so lệnh tổ hợp với bản đó là chỗ kiểm tính chất này, không phải lập luận.
 */
export function pullRequestTarget(command) {
  const nameIsGh = (name) => name === "gh";
  const readings = [isWrapper, isBareWrapper].flatMap((wrapper) => [
    ...[command, unescaped(command)].flatMap((text) =>
      [false, true].map((comments) =>
        targetIn(scan(text, true, comments) ?? scan(text, false, false), isGhCommand, wrapper)
      )
    ),
    targetIn(scan(command, true, false) ?? scan(command, false, false), nameIsGh, wrapper)
  ]);
  const seen = readings.filter((target) => target !== null);
  if (seen.length === 0) return null;
  const repos = new Set(seen.map((target) => target.repo).filter((repo) => repo !== null));
  const cds = JSON.stringify(seen[0].cds);
  if (repos.size > 1 || seen.some((target) => JSON.stringify(target.cds) !== cds)) {
    return { cds: null, repo: null, cli: seen[0].cli };
  }
  return { cds: seen[0].cds, repo: [...repos][0] ?? null, cli: seen[0].cli };
}

const isGhCommand = (name) => GH_COMMANDS.has(baseName(name));

function targetIn(segments, isGh, isWrap) {
  let cds = [];
  for (const words of segments) {
    let i = 0;
    let repo = null;
    let via = null;
    while (i < words.length && KEYWORDS.has(words[i])) i++;
    while (i < words.length && (/^[A-Za-z_][A-Za-z0-9_]*=/.test(words[i]) || isWrap(words[i]))) {
      if (words[i].startsWith("GH_REPO=")) repo = unquote(words[i].slice("GH_REPO=".length));
      if (SHELLS.has(baseName(words[i]))) via = unquote(words[i]);
      i++;
      while (i < words.length && /^(-|[0-9])/.test(words[i])) {
        if (words[i].startsWith("-") && /^[A-Z_][A-Z0-9_]*$/.test(words[i + 1] ?? "")) i++; // `env -u NAME`
        i++;
      }
    }
    if (words[i] === "cd") {
      // `cd` trần là về `$HOME`, đúng ngữ nghĩa shell — và là thứ heredoc/chuỗi văn bản hay để lại ("đọc `cd` …"),
      // nên chặn nó là chặn nhầm cả lệnh chỉ GHI CHỮ có nhắc tới lệnh tạo PR (gặp thật khi sửa CHANGELOG).
      const arg = words[i + 1] === undefined ? "~" : unquote(words[i + 1]);
      cds = cds === null || arg === "-" || /[$`]/.test(arg) ? null : [...cds, arg];
      continue;
    }
    if (!isGh(words[i])) continue;
    const takeRepo = (k) => {
      const w = words[k];
      if (w === "-R" || w === "--repo") return { value: unquote(words[k + 1] ?? ""), width: 2 };
      if (w.startsWith("--repo=")) return { value: unquote(w.slice("--repo=".length)), width: 1 };
      if (/^-R./.test(w)) return { value: unquote(w.slice(2)), width: 1 };
      return null;
    };
    let j = i + 1;
    while (j < words.length && words[j].startsWith("-")) {
      const r = takeRepo(j);
      if (r) repo = r.value;
      j += r ? r.width : 1;
    }
    if (words[j] !== "pr" || (words[j + 1] !== "create" && words[j + 1] !== "new")) continue;
    for (let k = j + 2; k < words.length; k++) {
      const r = takeRepo(k);
      if (r) repo = r.value;
    }
    return { cds, repo, cli: { command: unquote(words[i]), via } };
  }
  return null;
}

/**
 * Đường tuyệt đối tới một tệp có thật ngoài repo (cả đường nêu lẫn đích của symlink); còn lại `null`.
 * So danh tính thư mục (`dev`/`ino`), không so chuỗi: APFS mặc định không phân biệt hoa thường và
 * `realpathSync` không chuẩn hoá chữ, nên đường viết HOA tới repo so chuỗi sẽ ra "ngoài repo".
 * Phải là `.native`: bản JS lùi `..` theo chữ trước khi đọc symlink, nên `<repo>/l/../../gh` với `l -> d/e` ra `<cha>/gh`
 * trong khi kernel đi symlink rồi mới lùi và chạy `<repo>/gh`.
 */
function pathOutsideRepo(path, top) {
  if (!path.startsWith("/") || /[$`]/.test(path)) return null;
  try {
    const root = statSync(top);
    const inside = (start) => {
      for (let p = start; ; p = dirname(p)) {
        const s = statSync(p);
        if (s.dev === root.dev && s.ino === root.ino) return true;
        if (p === dirname(p)) return false;
      }
    };
    if (inside(resolve(path)) || inside(realpathSync.native(path))) return null;
  } catch {
    return null;
  }
  return path;
}

/**
 * Lời gọi công cụ đã tạo PR, chạy được từ hook. Hook chạy ngoài hệ thống hỏi quyền, và `cli` đọc từ VĂN BẢN lệnh, có thể là
 * thân heredoc: `cat > n.md <<'EOF'⏎./gh pr create⏎EOF`. Nên không bao giờ chạy tệp trong repo: chỉ tin đường tuyệt đối
 * (`~`, `$HOME` mở ra) tới tệp ngoài repo, còn lại gọi tên cuối qua PATH, kể cả trình thông dịch. Không gọi `[via, tên trần]`:
 * `bash gh` tìm `./gh` trước PATH. Công cụ MCP (`cli` rỗng) không có lệnh nào để theo nên dùng `gh`.
 */
function ghRunner(cli, top, home = process.env.HOME ?? "") {
  if (!cli) return ["gh"];
  const expanded = cli.command.replace(/^(?:~|\$HOME|\$\{HOME\})(?=\/)/, () => home);
  const path = pathOutsideRepo(expanded, top);
  if (path === null) return [baseName(expanded)];
  return cli.via ? [baseName(cli.via), path] : [path];
}

export function createsPullRequest(command) {
  return pullRequestTarget(command) !== null;
}

/** `owner/name` của một URL remote GitHub (https hay ssh), chữ thường; `null` khi không đọc ra. */
export function repoSlug(url) {
  const m = /github\.com[:/]([^/\s]+)\/([^/\s]+?)(?:\.git)?\/?$/i.exec(url.trim());
  return m ? `${m[1]}/${m[2]}`.toLowerCase() : null;
}

/** Tách hàng đợi thành từng báo cáo — mỗi báo cáo kết thúc ở dòng chân `COMITOR-REVIEW <sha>: …`. */
export function splitReports(text) {
  const reports = [];
  let lines = [];
  for (const line of text.split("\n")) {
    lines.push(line);
    const match = FOOTER.exec(line);
    if (match) {
      reports.push({ sha: match[1], body: lines.join("\n").trim() });
      lines = [];
    }
  }
  return reports;
}

function git(args, cwd) {
  return execFileSync("git", args, { cwd, encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] }).trim();
}

function readOr(path, fallback) {
  try {
    return readFileSync(path, "utf8");
  } catch {
    return fallback;
  }
}

/**
 * Repo mà lời gọi tạo PR nhắm tới → `{ top }` (gốc checkout cục bộ), `{ deny }` (không xét được — hướng CHẶN), hay `null`
 * (không phải lời gọi tạo PR, hoặc thư mục đích không phải repo git — `gh` sẽ tự hỏng ở đó).
 *
 * ⚠ Đừng quay về `payload.cwd` trần: đó là thư mục của PHIÊN, không phải của LỆNH. Phiên đứng ở repo A chạy
 * `cd ../b && gh pr create` thì bị chặn bằng HEAD của A; tệ hơn, `gh pr create -R org/b` từ A được CHO QUA bằng
 * marker của A — cổng mở cho một nhánh chưa ai review. Cả hai đã xảy ra thật (10/2026, phiên làm chéo hai repo).
 */
export function resolveTarget(payload, gitTop = (dir) => git(["rev-parse", "--show-toplevel"], dir), originOf) {
  const cwd = payload.cwd || process.cwd();
  let dir = cwd;
  let repo = null;
  let cli = null;
  if (/create_pull_request$/.test(payload.tool_name ?? "")) {
    const { owner, repo: name } = payload.tool_input ?? {};
    if (owner && name) repo = `${owner}/${name}`;
  } else if (payload.tool_name === "Bash") {
    const t = pullRequestTarget(payload.tool_input?.command ?? "");
    if (!t) return null;
    if (t.cds === null) {
      return {
        deny:
          "Không xác định được lệnh tạo PR chạy ở đâu (một `cd` dùng biến, `$(…)`, `cd -`, hay một `#`, `\\` làm lệnh có nhiều cách đọc). " +
          "Viết `cd <đường dẫn thật> && gh pr create …` trên một dòng, không kèm comment, để hook xét đúng repo đã được /comitor-review."
      };
    }
    const home = process.env.HOME ?? "";
    dir = resolve(cwd, ...t.cds.map((d) => (d === "~" || d.startsWith("~/") ? home + d.slice(1) : d)));
    repo = t.repo;
    cli = t.cli;
  } else {
    return null;
  }
  let top;
  try {
    top = gitTop(dir);
  } catch {
    return null;
  }
  let have = null;
  try {
    have = repoSlug((originOf ?? ((t) => git(["remote", "get-url", "origin"], t)))(top));
  } catch {
    // không có remote `origin` → không chứng minh được là cùng repo → chặn (nhánh dưới)
  }
  if (repo) {
    const want = repo.toLowerCase().replace(/^(?:https?:\/\/)?github\.com\//, "");
    if (want !== have) {
      return {
        deny:
          `Lệnh tạo PR cho ${repo}, nhưng thư mục ${top} là repo ${have ?? "không rõ"} — hook không xét được marker ` +
          `/comitor-review của ${repo} từ đây. Chạy lệnh trong checkout của ${repo}: \`cd <checkout> && gh pr create …\`.`
      };
    }
  }
  return { top, cli, slug: have };
}

const NO_HAND_WRITE =
  "Đừng tự ghi marker hay sidecar trong `.claude-tmp/` — chúng là lời khai của lần review, ghi tay là mở cổng " +
  "cho một nhánh chưa ai duyệt.";

/**
 * Cho mở PR hay không, từ sha HEAD, nội dung marker và nội dung sidecar (`null` = file vắng mặt). `null` = cho qua;
 * chuỗi = lý do từ chối. Hàm thuần — `--self-test` gọi thẳng nó.
 */
export function gateDecision(head, marker, open, top = ".") {
  const short = head.slice(0, 7);
  if ((marker ?? "").trim() !== head) {
    return (
      `Chưa mở PR được: commit ${short} của ${top} chưa được /comitor-review. ` +
      `Chạy /comitor-review, sửa hết lỗi chặn nó báo, rồi tạo PR lại. ${NO_HAND_WRITE}`
    );
  }
  if (open === null) {
    return (
      `Chưa mở PR được: commit ${short} đã review nhưng thiếu ${OPEN}, nên không biết kết luận. ` +
      `Chạy lại /comitor-review (nó sẽ review cả nhánh). ${NO_HAND_WRITE}`
    );
  }
  if (open.trim() === "") return null;
  const rows = open.split("\n").filter((line) => /^\|\s*(?:🔴|🟠)/u.test(line));
  const blocking = rows.length;
  // Trần ba lượt (SKILL.md § 1 "Trần ba lượt"): hàng còn mở tới `mang sang ×3` thì sửa tiếp là đốt token — dừng, leo thang.
  const stuck = rows.filter((line) => Number(/\([^()]*mang sang ×(\d+)\)\s*\|\s*$/u.exec(line)?.[1] ?? 0) >= 3).length;
  if (stuck > 0) {
    return (
      `Chưa mở PR được: /comitor-review của ${short} còn ${stuck} lỗi chặn đã 3 lượt chưa sửa được (mang sang ×3) ` +
      `trong ${OPEN}. DỪNG sửa tiếp — báo người điều phối chọn một trong năm: đổi người làm · chia việc nhỏ hơn · ` +
      `đổi cách làm · sửa đặc tả · dời việc. ${NO_HAND_WRITE}`
    );
  }
  return (
    `Chưa mở PR được: /comitor-review của ${short} kết luận REQUEST CHANGES — còn ` +
    `${blocking > 0 ? `${blocking} ` : ""}lỗi chặn (🔴/🟠) trong ${OPEN}. Sửa chúng, commit, chạy lại /comitor-review ` +
    `(chỉ review phần thêm và kiểm lại từng lỗi mang sang) tới khi APPROVE, rồi tạo PR lại. ${NO_HAND_WRITE}`
  );
}

function preToolUse(top) {
  const head = git(["rev-parse", "HEAD"], top);
  const reason = gateDecision(head, readOr(join(top, MARKER), ""), readOr(join(top, OPEN), null), top);
  if (reason) deny(reason);
}

function deny(reason) {
  process.stdout.write(
    JSON.stringify({
      hookSpecificOutput: { hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: reason }
    })
  );
}

function postToolUse({ top, cli, slug }) {
  const queuePath = join(top, QUEUE);
  const reports = splitReports(readOr(queuePath, ""));
  if (reports.length === 0) return;
  // Hook bị giết ở 60 giây (`.claude/settings.json`) thì không báo gì và không ghi lại hàng đợi, lượt sau đăng trùng.
  const deadline = Date.now() + 50_000;
  const [bin, ...prefix] = ghRunner(cli, top);
  const run = (args, input) =>
    execFileSync(bin, [...prefix, ...args], {
      cwd: top,
      encoding: "utf8",
      input,
      stdio: [input === undefined ? "ignore" : "pipe", "pipe", "pipe"],
      timeout: 15_000
    });
  const why = (e) => `${e.stderr || e.message}`.trim().replace(/\s+/g, " ").slice(0, 200);
  const say = (message) =>
    process.stdout.write(
      JSON.stringify({
        systemMessage: message,
        hookSpecificOutput: { hookEventName: "PostToolUse", additionalContext: message }
      })
    );
  const stuck = (reason) =>
    say(`comitor-review: chưa đăng ${reports.length} báo cáo, còn trong ${QUEUE}: ${reason}. Đăng tay theo SKILL.md.`);
  // Có `-R` thì `gh` đòi nêu PR; `gh-agent` thì không cho thiếu `-R`. Không đọc được repo thì để công cụ tự báo lỗi.
  const repoArgs = slug ? ["-R", slug] : [];
  let pr;
  try {
    const branch = git(["branch", "--show-current"], top);
    pr = JSON.parse(
      run(["pr", "view", ...(slug ? [branch, ...repoArgs] : []), "--json", "number,state,url,headRefName"])
    );
    // `gh pr view 123` đọc số thành số PR: nhánh tên toàn số sẽ đăng nhầm sang PR khác.
    if (slug && pr.headRefName !== branch) {
      stuck(`\`pr view\` trả PR #${pr.number} của nhánh ${pr.headRefName}, không phải ${branch}`);
      return;
    }
  } catch (e) {
    stuck(`không đọc được PR của nhánh bằng ${bin}: ${why(e)}`);
    return;
  }
  if (pr.state !== "OPEN") {
    stuck(`PR #${pr.number} đang ${pr.state}`);
    return;
  }

  const unposted = [];
  let posted = 0;
  let failure = "";
  for (const report of reports) {
    if (Date.now() + 15_000 > deadline) {
      unposted.push(report.body);
      failure ||= "hết giờ của hook";
      continue;
    }
    try {
      git(["merge-base", "--is-ancestor", report.sha, "HEAD"], top);
    } catch {
      continue; // báo cáo của một lịch sử đã rebase mất — không bao giờ đăng nhầm PR
    }
    try {
      run(["pr", "comment", String(pr.number), ...repoArgs, "--body-file", "-"], report.body);
      posted++;
    } catch (e) {
      unposted.push(report.body);
      failure = why(e);
    }
  }
  writeFileSync(queuePath, unposted.length > 0 ? `${unposted.join("\n\n")}\n` : "");

  const left = unposted.length > 0 ? ` ${unposted.length} báo cáo chưa đăng được, còn trong hàng đợi: ${failure}.` : "";
  say(`comitor-review: đã đăng ${posted} báo cáo lên PR #${pr.number} (${pr.url}).${left}`);
}

async function selfTest() {
  const ca = await import("./tests/pr-gate-cases.mjs");
  const blocked = [
    // Chặn dư có từ bản gốc, cố ý giữ: cổng không được cho qua lệnh mà bản gốc đã chặn.
    "echo x \\\ngh pr create",
    "echo a\\; gh pr create",
    "gh pr create --fill",
    "git push -u origin feat/x && gh pr create --title 'x' --body-file b.md",
    "GH_PROMPT_DISABLED=1 gh pr create",
    "env -u FOO gh pr new",
    "cd app; gh -R comitor-ai/x pr create",
    "if true; then gh pr create; fi",
    // `gh` được bọc, hay gọi bằng đường dẫn đầy đủ: vẫn là lệnh tạo PR.
    "gh-agent pr create --fill",
    "~/bin/gh-agent pr create -R comitor-ai/x --body-file b.md",
    '"$HOME/bin/gh-agent" pr create -R comitor-ai/x',
    "git push -u origin x && ~/bin/gh-agent pr new -R comitor-ai/x",
    "/opt/homebrew/bin/gh pr create",
    "gh-agent pr \\\n  create --fill",
    "g\\\nh pr create",
    "\\gh pr create",
    // `\` đã bị thoát, nằm trong comment hay đứng trước CRLF thì KHÔNG nối dòng: shell chạy dòng sau như một lệnh riêng.
    "echo a\\\\\ngh pr create",
    "# x \\\ngh-agent pr create",
    "echo a \\\r\ngh pr create",
    // `#` chỉ mở comment ở đầu từ; dính sau `${`, `}`, `)` hay backtick thì vẫn là một phần của từ.
    // biome-ignore lint/suspicious/noTemplateCurlyInString: lệnh shell, không phải template.
    "echo ${#a} && gh pr create",
    // biome-ignore lint/suspicious/noTemplateCurlyInString: lệnh shell, không phải template.
    "echo ${a}#b && gh pr create",
    "echo $(x)#b && gh pr create",
    "echo `x`#b && gh pr create",
    "echo $((#a)); gh pr create --fill",
    "echo (#i)foo*(N); gh pr create --fill",
    "a=1; echo $(( 1 + #a )); gh pr create -R org/b",
    // biome-ignore lint/suspicious/noTemplateCurlyInString: lệnh shell, không phải template.
    "echo ${a/ #/x}; gh pr create",
    // biome-ignore lint/suspicious/noTemplateCurlyInString: lệnh shell, không phải template.
    "echo ${a:- #b}; gh pr create",
    // biome-ignore lint/suspicious/noTemplateCurlyInString: lệnh shell, không phải template.
    "echo ${a}\\\n#;gh pr create --fill",
    "echo $(date)\\\n#;gh pr create --fill",
    "echo `date`\\\n#;gh pr create --fill",
    // Hook không phân biệt nổi comment thật với `#` trên, nên comment có dấu tách cũng bị chặn: hướng an toàn.
    "echo a # ; gh pr create"
  ];
  const allowed = [
    'echo "gh pr create"',
    "gh pr view --json number",
    "gh pr list",
    "gh pr comment 12 --body-file r.md",
    'git commit -m "gh pr create sau"',
    "ghx pr create",
    "echo gh-agent pr create",
    "gh-agent pr view 12 -R comitor-ai/x",
    "gh-agent-x pr create",
    "~/bin/gh-agent-x pr create",
    "cat ~/bin/gh-agent",
    // Comment không phải lệnh ở mọi lần đọc.
    "echo a # gh pr create",
    "# gh pr create",
    "gh \\\r\n  pr create --fill"
  ];
  blocked.push(...ca.BLOCKED);
  allowed.push(...ca.ALLOWED);
  const failures = [
    ...blocked.filter((c) => !createsPullRequest(c)).map((c) => `phải CHẶN: ${c}`),
    ...allowed.filter((c) => createsPullRequest(c)).map((c) => `phải CHO QUA: ${c}`)
  ];
  const queue = [
    "## ❌ REQUEST CHANGES",
    "COMITOR-REVIEW abc1234: REQUEST CHANGES · 2 findings (1 blocking, 0 fixed)",
    "",
    "## ✅ APPROVE",
    "> COMITOR-REVIEW 0000000: APPROVE (trích dẫn — không phải dòng chân)",
    "COMITOR-REVIEW def5678: APPROVE · 0 findings (0 blocking, 0 fixed)"
  ].join("\n");
  const reports = splitReports(queue);
  if (reports.length !== 2 || reports[0].sha !== "abc1234" || reports[1].sha !== "def5678") {
    failures.push(`splitReports: ${JSON.stringify(reports.map((r) => r.sha))}`);
  }
  // Cổng APPROVE: marker khớp CHƯA đủ, sidecar phải có và rỗng. Hai ca đầu là đối chứng âm tính của bản cũ
  // (chỉ so marker) — bản đó cho qua cả hai.
  const sha = "8d41e07aa0000000000000000000000000000000";
  const openRows = "| 🔴 | `route.ts:31` | Chốt sai quyền. (G1) |\n| 🟠 | `grid.tsx:88` | Luật viết hai lần. (M2) |\n";
  const gates = [
    ["REQUEST CHANGES", `${sha}\n`, openRows, /còn 2 lỗi chặn/],
    [
      "mang sang ×2 vẫn sửa tiếp",
      sha,
      "| 🟠 | `a.ts:1` | Lệch đặc tả. (DT1, mang sang ×2) |\n",
      /còn 1 lỗi chặn \(🔴\/🟠\)/
    ],
    [
      "mang sang ×3 → leo thang",
      sha,
      `${openRows}| 🟠 | \`a.ts:1\` | Lệch đặc tả. (DT1, mang sang ×3) |\n`,
      /3 lượt.*DỪNG/
    ],
    [
      "×3 trong lời, không trong ngoặc mã luật",
      sha,
      "| 🟠 | `a.ts:1` | Chuỗi «mang sang ×3» bị cắt. (DT1) |\n",
      /còn 1 lỗi chặn \(🔴\/🟠\)/
    ],
    ["×3 ở hàng 🟡 không tính", sha, "| 🟡 | `a.ts:1` | Tên. (N1, mang sang ×3) |\n", /REQUEST CHANGES/],
    ["sidecar vắng mặt", sha, null, /không biết kết luận/],
    ["sidecar lạ, không hàng 🔴/🟠", sha, "ghi chú\n", /REQUEST CHANGES/],
    ["marker cũ", "0".repeat(40), "", /chưa được \/comitor-review/],
    ["không marker", "", "", /chưa được \/comitor-review/],
    ["APPROVE", `${sha}\n`, "\n", null]
  ];
  for (const [name, marker, open, want] of gates) {
    const got = gateDecision(sha, marker, open);
    if (want === null ? got !== null : !want.test(got ?? "")) failures.push(`cổng «${name}»: ${got ?? "CHO QUA"}`);
  }
  // Xét ĐÚNG repo của lệnh. Phiên đứng ở /w/a; /w/b là repo khác; /tmp/x không phải repo; /w/c không có `origin`.
  const tops = { "/w/a": "/w/a", "/w/a/app": "/w/a", "/w/b": "/w/b", "/w/c": "/w/c" };
  const origins = { "/w/a": "git@github.com:Org/A.git", "/w/b": "https://github.com/org/b" };
  const gitTop = (dir) => {
    if (!tops[dir]) throw new Error("not a git repository");
    return tops[dir];
  };
  const originOf = (top) => {
    if (!origins[top]) throw new Error("no origin");
    return origins[top];
  };
  const target = (command, cwd = "/w/a", tool = "Bash", input = { command }) => {
    const r = resolveTarget({ cwd, tool_name: tool, tool_input: input }, gitTop, originOf);
    return r === null ? "bỏ qua" : r.deny ? "CHẶN" : r.top;
  };
  const targets = [
    ["gh pr create", "/w/a"],
    ["cd app && gh pr create", "/w/a"],
    // Đối chứng âm tính của lỗi cũ: xét theo thư mục của phiên thì hai ca này ra /w/a.
    ["cd ../b && gh pr create", "/w/b"],
    ["cd /w/b; git push && gh pr create --fill", "/w/b"],
    ["gh -R ORG/A pr create", "/w/a"],
    ["gh pr create -R org/b", "CHẶN"],
    ["gh-agent pr create -R org/a", "/w/a"],
    ["cd ../b && ~/bin/gh-agent pr create -R org/b", "/w/b"],
    ["gh-agent pr create -R org/b", "CHẶN"],
    ["~/bin/gh-agent pr create -R org/b", "CHẶN"],
    ["gh-agent pr view -R org/a", "bỏ qua"],
    // Xuống dòng bằng `\`: `-R` ở dòng sau vẫn là đối số của lệnh. Đối chứng âm tính: tách thành hai lệnh thì ra /w/a.
    ["gh-agent pr create \\\n  -R org/b --fill", "CHẶN"],
    ["gh pr create --fill \\\n  --repo org/b", "CHẶN"],
    ["gh-agent pr create \\\n  -R org/a --fill", "/w/a"],
    ["gh pr create -R org/\\\nb", "CHẶN"],
    // `\` không nối thì `cd` ở dòng sau vẫn chạy: nuốt nó là xét sai repo.
    ["# x \\\ncd ../b && gh pr create", "CHẶN"],
    ["echo a\\\\\ncd ../b && gh pr create", "/w/b"],
    ["cd ../a # x \\\ncd ../b && gh pr create", "CHẶN"],
    ["( # x \\\ncd ../b && gh pr create )", "CHẶN"],
    // Một lần đọc thấy `cd`, lần kia không: hai đích khác nhau.
    ["echo $((#a)) && cd ../b\ngh pr create", "CHẶN"],
    // Nhận thêm tên `gh-agent` không được che lệnh `gh` đứng sau: bản gốc đã chặn các lệnh này.
    ["gh-agent pr create -R org/a --fill; gh pr create -R org/b", "CHẶN"],
    ["/nope/gh pr create; gh pr create -R org/b", "CHẶN"],
    ['"gh" pr create -R org/a; gh pr create -R org/b', "CHẶN"],
    ["gh-agent pr create -R org/a; cd ../b && gh pr create", "CHẶN"],
    ["gh-agent pr create -R org/a; echo xong", "/w/a"],
    ["gh pr create -R org/a # chú thích", "/w/a"],
    // Lần đọc nguyên văn giữ nguyên bản gốc: nháy `\\'`, heredoc lạ không giấu được lệnh, comment có `'` không chặn dư.
    ["echo $'it\\'s'; gh pr create -R org/b; echo '\\'", "CHẶN"],
    ["cat <<'X\\'\na\nX\\\ngh pr create -R org/b", "CHẶN"],
    ["# Don't forget\ngh pr create \\\n  -R org/a --fill", "/w/a"],
    ["echo a \\\r\ncd ../b && gh pr create", "/w/b"],
    ["# x \\\ncd $X && gh pr create", "CHẶN"],
    ["# x \\\ncd - && gh pr create", "CHẶN"],
    ["cd ../\\\nb && gh pr create", "CHẶN"],
    // Nội dung comment không phải đối số, và lệnh đầu không bị lệnh sau che.
    ["gh pr create -R org/b # x \\\necho -R org/a", "CHẶN"],
    ["gh pr create -R org/b # -R org/a", "CHẶN"],
    ["# x \\\ngh pr create -R org/b; gh pr create", "CHẶN"],
    ["gh pr create --repo=org/b", "CHẶN"],
    ["GH_REPO=org/b gh pr create", "CHẶN"],
    ["cd ../b && gh pr create -R org/a", "CHẶN"],
    ["cd $DIR && gh pr create", "CHẶN"],
    ["cd - && gh pr create", "CHẶN"],
    // `cd` trần = `$HOME` (không phải repo ở đây) — không chặn nhầm một lệnh chỉ ghi chữ nhắc tới `cd`.
    ["cd /w/a && cat <<X\nđọc `cd` rồi\ngh pr create sau\nX", "bỏ qua"],
    ["cd /tmp/x && gh pr create", "bỏ qua"],
    ["gh pr view", "bỏ qua"],
    ["bash ~/bin/gh-agent pr create -R org/b", "CHẶN"],
    ["bash ~/bin/gh-agent pr create -R org/a", "/w/a"]
  ];
  targets.push(...ca.TARGETS);
  for (const [command, want] of targets) {
    const got = target(command);
    if (got !== want) failures.push(`đích của «${command}»: ${got} (cần ${want})`);
  }
  const mcp = (owner, repo) => target("", "/w/a", "mcp__github__create_pull_request", { owner, repo });
  if (mcp("org", "b") !== "CHẶN") failures.push(`MCP org/b từ /w/a: ${mcp("org", "b")} (cần CHẶN)`);
  if (mcp("org", "a") !== "/w/a") failures.push(`MCP org/a từ /w/a: ${mcp("org", "a")} (cần /w/a)`);
  if (target("gh pr create -R org/c", "/w/c") !== "CHẶN") failures.push("repo không có origin + -R: phải CHẶN");
  const slugs = [
    ["git@github.com:Comitor-AI/comitor-starter.git", "comitor-ai/comitor-starter"],
    ["https://github.com/comitor-ai/comitor-marketing", "comitor-ai/comitor-marketing"],
    ["https://example.com/a/b.git", null]
  ];
  for (const [url, want] of slugs) if (repoSlug(url) !== want) failures.push(`repoSlug(${url}): ${repoSlug(url)}`);
  failures.push(...ca.postToolUseFailures(process.argv[1], QUEUE));

  if (failures.length > 0) {
    console.error(`✗ pr-gate tự kiểm HỎNG:\n  ${failures.join("\n  ")}`);
    process.exit(1);
  }
  console.info(
    `✓ pr-gate: ${blocked.length} lệnh bị chặn, ${allowed.length} lệnh cho qua, ${gates.length} ca cổng APPROVE ` +
      `(kể cả đối chứng âm tính của bản chỉ so marker), ${targets.length + 3} ca đích repo ` +
      "(kể cả đối chứng âm tính của lỗi xét theo thư mục phiên), hàng đợi tách đúng, PostToolUse gọi đúng công cụ và báo lỗi."
  );
}

if (process.argv.includes("--self-test")) {
  await selfTest();
} else {
  let payload;
  try {
    payload = JSON.parse(readFileSync(0, "utf8"));
  } catch {
    process.exit(0);
  }
  const target = resolveTarget(payload);
  if (target?.deny) {
    if (payload.hook_event_name === "PreToolUse") deny(target.deny);
  } else if (target) {
    if (payload.hook_event_name === "PreToolUse") preToolUse(target.top);
    else if (payload.hook_event_name === "PostToolUse") postToolUse(target);
  }
}
