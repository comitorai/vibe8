/**
 * Ca thử của `pr-gate.mjs --self-test`. Hook chỉ nạp tệp này khi tự kiểm, nên chạy thường vẫn là một tệp.
 */
import { execFileSync, spawnSync } from "node:child_process";
import { mkdirSync, mkdtempSync, readFileSync, realpathSync, rmSync, symlinkSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, relative } from "node:path";

export const BLOCKED = [
  // Gọi qua trình thông dịch: `gh-agent` là script nên `bash <đường dẫn>` chạy được y như gọi thẳng.
  "bash ~/bin/gh-agent pr create -R comitor-ai/x",
  "bash -x ~/bin/gh-agent pr create",
  "sh ~/bin/gh-agent pr new",
  "/bin/bash ~/bin/gh-agent pr create",
  "/usr/bin/env gh pr create",
  // Dòng tạo PR trong thân heredoc vẫn bị chặn. Chặn dư, cố ý: đọc shell để bỏ thân đã lộ đường lọt ở mỗi vòng review.
  "cat > f.md <<'EOF'\ngh pr create --fill\nEOF",
  "python3 - <<'A'\ngh pr create\nA",
  // biome-ignore lint/suspicious/noTemplateCurlyInString: lệnh shell, không phải template
  "cat > a.md <<A\n${a[b[${d:-$}(gh pr create)]]}\nA",
  // biome-ignore lint/suspicious/noTemplateCurlyInString: lệnh shell, không phải template
  'cat > a.md <<A\n${(e):-"$"(gh pr create)}\nA',
  "git branch -m gh\ngit commit --allow-empty -F - <<A\nx; gh pr create\nA\ncd .git/logs/refs/heads\nbash ./gh pr view",
  "git branch -m gh\ngit commit --allow-empty -F - <<A\nx; gh pr create\nA\nbash .git/logs/refs/heads/gh pr view"
];

export const ALLOWED = [
  // Từ gần giống tên shell không tính; đọc PR qua trình thông dịch không cần review.
  "bash script.sh",
  "bash ~/bin/gh-agent pr view 1 -R comitor-ai/x"
];

/**
 * Đích của lệnh mà bản gốc đã chặn: nhận thêm trình thông dịch và tên đường dẫn của wrapper không được đổi các lệnh này.
 * Phiên đứng ở /w/a, /w/b là repo khác, /tmp không phải repo.
 */
export const TARGETS = [
  // `cd` đứng sau wrapper không đổi thư mục của shell cha.
  ["bash cd /tmp; gh pr create --fill", "CHẶN"],
  ["bash cd ../b; gh pr create --fill", "CHẶN"],
  ["bash cd; gh pr create --fill", "CHẶN"],
  ["bash -e cd /tmp; gh pr create --fill", "CHẶN"],
  ["env bash cd /tmp; gh pr create --fill", "CHẶN"],
  ["/usr/bin/env cd /tmp && gh pr create --fill", "CHẶN"],
  ["/usr/bin/env cd ../b && gh pr create --fill", "CHẶN"],
  ["/usr/bin/env FOO=1 cd /tmp; gh pr create --fill", "CHẶN"],
  ["/usr/bin/time cd /tmp; gh pr create --fill", "CHẶN"],
  // Lệnh đầu vừa được nhận ra không được che lệnh sau.
  ["/usr/bin/env gh pr create -R org/a; gh pr create -R org/b", "CHẶN"],
  ["bash gh pr create -R org/a; gh pr create -R org/b", "CHẶN"],
  ["/usr/bin/env gh pr create --fill; cd ../b && gh pr create --fill", "CHẶN"],
  // Đối chứng: nhận đúng lệnh có wrapper mới khi không có gì mâu thuẫn.
  ["/usr/bin/env gh pr create -R org/a --fill", "/w/a"],
  ["bash scripts/x.sh && gh pr create --fill", "/w/a"]
];

/**
 * Chạy PostToolUse như Claude Code gọi (JSON qua stdin) trên repo git TẠM, với `gh` và `gh-agent` giả ghi lại lời gọi.
 * `gh` giả mặc định lỗi như đang đăng nhập sai tài khoản, nên hook gọi nhầm `gh` trần là ca đỏ.
 */
export function postToolUseFailures(gate, queue) {
  const failures = [];
  const dir = mkdtempSync(join(tmpdir(), "pr-gate-"));
  try {
    const bin = join(dir, "home/bin");
    mkdirSync(join(dir, "repo/.claude-tmp"), { recursive: true });
    mkdirSync(join(dir, "noexec"));
    mkdirSync(bin, { recursive: true });
    const log = join(dir, "log");
    const fake = (name) =>
      [
        "#!/bin/sh",
        `echo "${name} $*" >> "${log}"`,
        `case "$*:${name}" in *:gh) [ -z "$GH_OK" ] && { echo "sai tài khoản" >&2; exit 1; };; esac`,
        'case "$*" in',
        `  "pr view"*) [ -n "$VIEW_FAIL" ] && { echo "$VIEW_FAIL" >&2; exit 1; }; echo '{"number":7,"state":"'"\${STATE:-OPEN}"'","url":"u","headRefName":"'"\${HEAD_REF:-feat}"'"}';;`,
        '  "pr comment"*) [ -n "$COMMENT_FAIL" ] && { echo "$COMMENT_FAIL" >&2; exit 1; }; cat > /dev/null;;',
        "esac",
        ""
      ].join("\n");
    writeFileSync(join(bin, "gh"), fake("gh"), { mode: 0o755 });
    writeFileSync(join(bin, "gh-agent"), fake("gh-agent"), { mode: 0o755 });
    writeFileSync(join(dir, "noexec/gh-agent"), fake("gh-agent"), { mode: 0o644 });
    const repo = join(dir, "repo");
    // Tệp thực thi trong repo: hook chạy ngoài hệ thống hỏi quyền nên không bao giờ được gọi chúng.
    writeFileSync(join(repo, "gh"), fake("repo-gh"), { mode: 0o755 });
    writeFileSync(join(repo, "bash"), fake("repo-bash"), { mode: 0o755 });
    // Ngoài PATH: chỉ tới được khi hook mở đúng `~`, `$HOME`.
    mkdirSync(join(dir, "home/rieng"));
    writeFileSync(join(dir, "home/rieng/gh-agent"), fake("rieng"), { mode: 0o755 });
    mkdirSync(join(repo, "l"));
    symlinkSync(join(dir, "home/rieng/gh-agent"), join(repo, "l/gh"));
    // Symlink ngoài repo trỏ vào tệp trong repo: đường nêu ở ngoài, đích ở trong.
    mkdirSync(join(dir, "home/vao-repo"));
    symlinkSync(join(repo, "gh"), join(dir, "home/vao-repo/gh"));
    // `ll/../../gh`: Node lùi `..` theo chữ ra `<dir>/gh`, kernel đi symlink rồi mới lùi nên tới `<repo>/gh`.
    mkdirSync(join(repo, "d/e"), { recursive: true });
    symlinkSync("d/e", join(repo, "ll"));
    writeFileSync(join(dir, "gh"), "");
    const fromRunner = relative(process.cwd(), join(dir, "home/rieng/gh-agent"));
    const gitEnv = { ...process.env, GIT_AUTHOR_NAME: "t", GIT_AUTHOR_EMAIL: "t@x.test" };
    Object.assign(gitEnv, { GIT_COMMITTER_NAME: "t", GIT_COMMITTER_EMAIL: "t@x.test" });
    const inRepo = (...args) => execFileSync("git", args, { cwd: repo, env: gitEnv, stdio: "ignore" });
    inRepo("init", "-q", "-b", "feat");
    inRepo("remote", "add", "origin", "https://github.com/org/x");
    inRepo("commit", "-q", "--allow-empty", "-m", "c");
    // Thẻ trùng tên nhánh: `rev-parse --abbrev-ref HEAD` sẽ trả `heads/feat`.
    inRepo("tag", "feat");
    const sha = execFileSync("git", ["rev-parse", "HEAD"], { cwd: repo, encoding: "utf8" }).trim();
    const queuePath = join(repo, queue);
    const cases = [
      // tên ca · lệnh · biến môi trường · công cụ phải dùng · còn trong hàng đợi không · thông điệp
      ["gh-agent đường dẫn đầy đủ", `${bin}/gh-agent pr create -R org/x --fill`, {}, "gh-agent", false, /đã đăng 1/],
      ["gh-agent qua ~", "~/bin/gh-agent pr create -R org/x", {}, "gh-agent", false, /đã đăng 1/],
      ["gh-agent qua $HOME", "$HOME/bin/gh-agent pr create -R org/x", {}, "gh-agent", false, /đã đăng 1/],
      ["gh-agent qua PATH", "gh-agent pr create -R org/x", {}, "gh-agent", false, /đã đăng 1/],
      ["ngoài PATH qua ~", "~/rieng/gh-agent pr create -R org/x", {}, "rieng", false, /đã đăng 1/],
      ["ngoài PATH qua $HOME", "$HOME/rieng/gh-agent pr create -R org/x", {}, "rieng", false, /đã đăng 1/],
      // biome-ignore lint/suspicious/noTemplateCurlyInString: lệnh shell, `${HOME}` là chữ. Nháy kép vì `{` là dấu tách của `scan`.
      ["ngoài PATH qua ${HOME}", '"${HOME}/rieng/gh-agent" pr create -R org/x', {}, "rieng", false, /đã đăng 1/],
      ["đường tương đối có thật: theo PATH", `${fromRunner} pr create -R org/x`, {}, "gh-agent", false, /đã đăng 1/],
      [
        "symlink trong repo: không theo",
        `${realpathSync(repo)}/l/gh pr create --fill`,
        { GH_OK: "1" },
        "gh",
        false,
        /đã đăng 1/
      ],
      ["gh-agent qua biến", "$X/gh-agent pr create -R org/x", {}, "gh-agent", false, /đã đăng 1/],
      [
        "bash + tệp không có quyền chạy",
        `bash ${dir}/noexec/gh-agent pr create -R org/x`,
        {},
        "gh-agent",
        false,
        /đã đăng 1/
      ],
      ["không nêu -R vẫn đọc repo từ origin", "gh-agent pr create --fill", {}, "gh-agent", false, /đã đăng 1/],
      ["gh trần đúng tài khoản", "gh pr create --fill", { GH_OK: "1" }, "gh", false, /đã đăng 1/],
      ["gh trần sai tài khoản phải báo", "gh pr create --fill", {}, "gh", true, /sai tài khoản/],
      ["đọc PR lỗi phải báo", "gh-agent pr create -R org/x", { VIEW_FAIL: "hết hạn" }, "gh-agent", true, /hết hạn/],
      ["PR không còn mở phải báo", "gh-agent pr create -R org/x", { STATE: "MERGED" }, "gh-agent", true, /MERGED/],
      ["đăng lỗi phải báo", "gh-agent pr create -R org/x", { COMMENT_FAIL: "cấm ghi" }, "gh-agent", true, /cấm ghi/],
      [
        "thân heredoc nêu ./gh: không chạy tệp của repo",
        "cat > n.md <<'EOF'\n./gh pr create --fill\nEOF",
        { GH_OK: "1" },
        "gh",
        false,
        /đã đăng 1/
      ],
      ["lệnh ./gh: đăng bằng gh theo PATH", "./gh pr create --fill", { GH_OK: "1" }, "gh", false, /đã đăng 1/],
      ["đường tuyệt đối trong repo", `${repo}/gh pr create --fill`, { GH_OK: "1" }, "gh", false, /đã đăng 1/],
      // Hai ca chữ HOA chỉ đỏ được trên hệ tệp không phân biệt hoa thường (APFS mặc định); hệ tệp khác thì đường này không tồn tại.
      [
        "đường viết HOA tới repo: không chạy tệp của repo",
        `cat > n.md <<'EOF'\n${repo.toUpperCase()}/gh pr create --fill\nEOF`,
        { GH_OK: "1" },
        "gh",
        false,
        /đã đăng 1/
      ],
      [
        "đường viết HOA tới symlink trong repo: không theo",
        `${repo.toUpperCase()}/l/gh pr create --fill`,
        { GH_OK: "1" },
        "gh",
        false,
        /đã đăng 1/
      ],
      [
        "symlink ngoài repo trỏ vào repo: không theo",
        `${dir}/home/vao-repo/gh pr create --fill`,
        { GH_OK: "1" },
        "gh",
        false,
        /đã đăng 1/
      ],
      [
        "đường có .. đi qua symlink trong repo: không theo",
        `cat > n.md <<'EOF'\n${repo}/ll/../../gh pr create --fill\nEOF`,
        { GH_OK: "1" },
        "gh",
        false,
        /đã đăng 1/
      ],
      [
        "bash + tên trần: bash không tìm trong repo",
        "bash gh pr create --fill",
        { GH_OK: "1" },
        "gh",
        false,
        /đã đăng 1/
      ],
      ["trình thông dịch trong repo", `./bash ${bin}/gh-agent pr create -R org/x`, {}, "gh-agent", false, /đã đăng 1/],
      ["đường tương đối: theo PATH", "../home/bin/gh-agent pr create -R org/x", {}, "gh-agent", false, /đã đăng 1/],
      [
        "PR của nhánh khác (nhánh tên toàn số): không đăng",
        "gh-agent pr create -R org/x",
        { HEAD_REF: "khac" },
        "gh-agent",
        true,
        /khac/
      ]
    ];
    for (const [name, command, extra, tool, kept, message] of cases) {
      writeFileSync(queuePath, `## ✅ APPROVE\nCOMITOR-REVIEW ${sha}: APPROVE · 0 findings (0 blocking, 0 fixed)\n`);
      writeFileSync(log, "");
      const r = spawnSync(process.execPath, [gate], {
        input: JSON.stringify({
          hook_event_name: "PostToolUse",
          tool_name: "Bash",
          tool_input: { command },
          cwd: repo
        }),
        encoding: "utf8",
        env: { ...process.env, HOME: join(dir, "home"), PATH: `${bin}:${process.env.PATH}`, ...extra }
      });
      const calls = readFileSync(log, "utf8");
      const left = readFileSync(queuePath, "utf8").trim() !== "";
      const wrongTool = calls.split("\n").some((line) => line !== "" && !line.startsWith(`${tool} `));
      const noTarget = !calls.includes(`${tool} pr view feat -R org/x --json number,state,url,headRefName`);
      if (wrongTool || noTarget) failures.push(`PostToolUse «${name}»: lời gọi sai: ${calls.trim() || "(không gọi)"}`);
      if (left !== kept)
        failures.push(`PostToolUse «${name}»: hàng đợi ${left ? "còn" : "rỗng"}, cần ${kept ? "còn" : "rỗng"}`);
      if (!message.test(r.stdout)) failures.push(`PostToolUse «${name}»: thông điệp «${r.stdout.trim()}»`);
      if (!kept && !calls.includes(`${tool} pr comment 7 -R org/x --body-file -`)) {
        failures.push(`PostToolUse «${name}»: không đăng đúng PR: ${calls.trim()}`);
      }
    }
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
  return failures;
}
