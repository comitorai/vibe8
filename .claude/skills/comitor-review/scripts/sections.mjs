#!/usr/bin/env node
/**
 * In ĐÚNG những mục tài liệu mà bước 0 của `/comitor-review` cần, thay vì để agent Read cả file.
 *
 *   node sections.mjs <file> '<ô "Mục quyết định">'   — in các mục, mỗi khối mang tên + khoảng dòng
 *   node sections.mjs --list <file>                     — in dàn đề mục (để tự chọn khi bảng không nêu)
 *   node sections.mjs --check-table [--profile <tên>]  — mọi mục bảng tài liệu quy định + `pitfalls` của HỒ SƠ
 *                                                         phải tìm thấy trong tài liệu CỦA REPO ĐANG ĐỨNG
 *   node sections.mjs --profile                         — in hồ sơ của repo đang đứng và nơi nó lấy (`--json` để máy đọc)
 *   node sections.mjs --self-test                       — các ca mẫu, kể cả đối chứng âm tính
 *
 * ── HỒ SƠ REPO ──────────────────────────────────────────────────────────────────────────────────────
 * Bảng tài liệu, viết tắt và mục bẫy KHÔNG viết cứng ở đây: chúng thuộc HỒ SƠ của repo
 * (`references/profiles/<tên>.md`, khối ```json profile ở đầu file). Repo chọn hồ sơ bằng
 * `.claude/comitor-repo.json` — NGOÀI thư mục skill, nên `rsync --delete` lúc chép skill không xoá nó.
 * Thiếu file → hồ sơ `module` (mọi module sinh từ starter giữ nguyên hành vi cũ). Tên lạ hay khối hỏng →
 * thoát 2: review dừng ở NOT REVIEWED chứ không đoán luật của một repo khác.
 *
 * ── VÌ SAO ──────────────────────────────────────────────────────────────────────────────────────────
 * Bước 0 trỏ tới MỤC (`AG § Cạm bẫy › Next.js`), nhưng Read không đọc được một mục — nó đọc cả file. Với
 * `AGENTS.md` (~1100 dòng) và `docs/kien-truc-ung-dung.md` (~700 dòng) đó là phần lớn chi phí cố định của
 * MỖI lượt review, kể cả lượt chỉ có hai file đổi. Đo ở comitor-marketing (10/2026): 3–16 lượt mỗi PR.
 *
 * ── CÚ PHÁP: chính chữ của cột "Mục quyết định" ───────────────────────────────────────────────────
 * Agent dán nguyên phần chữ sau tên tài liệu, không phải dịch sang một cú pháp thứ hai:
 *   `§ 3 tầng 1, § 5`                       → mục đánh số "3." › đề mục con chứa "tầng 1"; mục "5."
 *   `§ 3 rìa B, rìa B′`                     → hai đề mục con của "3."
 *   `§ Cạm bẫy › Next.js`                   → đề mục "Cạm bẫy…" › đề mục con "Next.js…"
 *   `§ Quy ước ("Job nền", "Warning LÀ lỗi")` hay `§ Quy ước › "Job nền"`
 *                                           → CHỈ các gạch đầu dòng cấp 1 của mục đó bắt đầu bằng chữ trong nháy
 *   `§ Quy ước (màu, chuỗi)`                → ngoặc KHÔNG có nháy là ghi chú cho người, bị bỏ qua: in cả mục
 *
 * ── HƯỚNG HỎNG: ĐỌC NHIỀU HƠN, KHÔNG BAO GIỜ ÍT HƠN ────────────────────────────────────────────────
 * · Không thấy đề mục → dòng `✗ … đọc cả file` ra stderr, mã thoát 1. Agent rơi về Read cả file.
 * · Thấy đề mục nhưng không thấy gạch đầu dòng trong nháy → in CẢ mục, kèm ghi chú.
 * Một selector khớp NHẦM chỗ (in mục sai) là hỏng duy nhất theo hướng đọc ít — `--check-table` canh nó.
 * So khớp: bỏ `*`, backtick, nháy; không phân biệt hoa thường; đề mục BẮT ĐẦU bằng chữ được ưu tiên hơn
 * đề mục CHỨA chữ; đề mục cấp 1 (tên tài liệu) không bao giờ khớp. Đề mục trong khối ``` bị bỏ qua.
 */
import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const SKILL_DIR = join(dirname(fileURLToPath(import.meta.url)), "..");

const REPO_CONFIG = ".claude/comitor-repo.json";

/**
 * Khối ```json profile đầu tiên của một file hồ sơ → object; ném lỗi khi thiếu hay hỏng. Bốn khoá bắt buộc:
 * `docs` (viết tắt → đường dẫn trong repo), `table` (bảng tài liệu quy định, đường dẫn trong skill),
 * `pitfalls` (file bẫy trong skill), `pitfallSections` (nhóm review → tên mục của file bẫy).
 */
export function parseProfile(md) {
  const m = /^```json profile\n([\s\S]*?)\n```/m.exec(md);
  if (!m) throw new Error("thiếu khối ```json profile");
  const p = JSON.parse(m[1]);
  for (const k of ["docs", "table", "pitfalls", "pitfallSections"]) {
    if (!(k in p)) throw new Error(`khối profile thiếu khoá «${k}»`);
  }
  return p;
}

/**
 * Tên hồ sơ của repo: cờ `--profile`, rồi `.claude/comitor-repo.json`, rồi `module`. Cùng luật đọc với
 * `comitor-test/scripts/check-refs.mjs` và `comitor-page/scripts/scaffold.mjs` (`repoProfile`) — sửa một chỗ thì sửa
 * cả ba. Lỗi ném ở đây (JSON hỏng, tên sai) và ở `loadProfile` (không có file hồ sơ) thành thoát 2 ở khối `try`
 * ngay dưới `loadProfile`.
 */
function profileName(explicit) {
  if (explicit) return { name: explicit, from: "--profile" };
  if (!existsSync(REPO_CONFIG)) return { name: "module", from: `mặc định (không có ${REPO_CONFIG})` };
  const cfg = JSON.parse(readFileSync(REPO_CONFIG, "utf8"));
  if (typeof cfg.profile !== "string" || !/^[a-z][a-z0-9-]*$/.test(cfg.profile)) {
    throw new Error(`${REPO_CONFIG}: \`profile\` phải là tên hồ sơ (chữ thường, gạch ngang)`);
  }
  return { name: cfg.profile, from: REPO_CONFIG };
}

function loadProfile(explicit) {
  const { name, from } = profileName(explicit);
  const file = join(SKILL_DIR, "references/profiles", `${name}.md`);
  if (!existsSync(file)) throw new Error(`hồ sơ «${name}» (${from}) không có: ${file}`);
  return { name, from, file, ...parseProfile(readFileSync(file, "utf8")) };
}

let PROFILE;
try {
  const at = process.argv.indexOf("--profile");
  const value = at >= 0 ? process.argv[at + 1] : undefined;
  PROFILE = loadProfile(value && !value.startsWith("--") ? value : null);
} catch (e) {
  if (!process.argv.includes("--self-test")) {
    console.error(`✗ hồ sơ repo: ${e.message}`);
    process.exit(2);
  }
}

/** Viết tắt của bảng tài liệu quy định → đường dẫn trong repo. Theo hồ sơ; self-test dùng bảng module. */
const MODULE_DOCS = {
  KT: "docs/kien-truc-ung-dung.md",
  AG: "AGENTS.md",
  CT: "CONTRIBUTING.md",
  "CLAUDE.md": "CLAUDE.md",
  "migration.md": "docs/migration.md"
};
const DOCS = PROFILE?.docs ?? MODULE_DOCS;

const norm = (s) =>
  s
    .normalize("NFC")
    .replace(/[*`"“”]/g, "")
    .replace(/\s+/g, " ")
    .trim()
    .toLowerCase();

/** Đề mục ngoài khối mã: `{ level, text, line }` (line đánh từ 0). */
function headings(lines) {
  const out = [];
  let fence = false;
  lines.forEach((line, i) => {
    if (/^\s*```/.test(line)) fence = !fence;
    const m = !fence && /^(#{1,6})\s+(.*)$/.exec(line);
    if (m) out.push({ level: m[1].length, text: m[2], line: i });
  });
  return out;
}

/** Khoảng [đầu, cuối) của một đề mục: tới đề mục kế tiếp cùng cấp hoặc cao hơn. */
function sectionEnd(hs, h, total) {
  const next = hs.find((x) => x.line > h.line && x.level <= h.level);
  return next ? next.line : total;
}

function findHeading(hs, part, start, end, minLevel) {
  const inRange = hs.filter((h) => h.line >= start && h.line < end && h.level >= minLevel);
  const num = /^(\d+)$/.exec(part.trim());
  if (num) return inRange.find((h) => norm(h.text).startsWith(`${num[1]}.`));
  const p = norm(part);
  return inRange.find((h) => norm(h.text).startsWith(p)) ?? inRange.find((h) => norm(h.text).includes(p));
}

/** Gạch đầu dòng CẤP 1 (`- ` ở cột 0) trong khoảng, dòng đầu bắt đầu/chứa `hint`. */
function findBullet(lines, hint, start, end) {
  const h = norm(hint);
  const starts = [];
  let fence = false;
  for (let i = start; i < end; i++) {
    if (/^\s*```/.test(lines[i])) fence = !fence;
    if (!fence && /^- /.test(lines[i])) starts.push(i);
  }
  const pick =
    starts.find((i) => norm(lines[i].slice(2)).startsWith(h)) ?? starts.find((i) => norm(lines[i]).includes(h));
  if (pick === undefined) return undefined;
  let stop = end;
  fence = false;
  for (let i = pick + 1; i < end; i++) {
    if (/^\s*```/.test(lines[i])) fence = !fence;
    if (!fence && (/^- /.test(lines[i]) || /^#{1,6}\s/.test(lines[i]))) {
      stop = i;
      break;
    }
  }
  return [pick, stop];
}

/**
 * Chữ của một ô → danh sách selector `{ path: string[], bullets: string[] }`.
 * Tách tại `§` ngoài ngoặc; chữ trong nháy kép là gạch đầu dòng; ngoặc không nháy bị bỏ.
 */
function parseCell(cell) {
  const pieces = [];
  let depth = 0;
  let cur = "";
  for (const ch of cell) {
    if (ch === "(") depth++;
    if (ch === ")") depth = Math.max(0, depth - 1);
    if (ch === "§" && depth === 0) {
      pieces.push(cur);
      cur = "";
      continue;
    }
    cur += ch;
  }
  pieces.push(cur);
  const selectors = [];
  for (const raw of pieces.slice(1)) {
    const bullets = [...raw.matchAll(/"([^"]+)"/g)].map((m) => m[1]);
    const base = raw
      .replace(/"[^"]*"/g, "")
      .replace(/\([^)]*\)/g, "")
      .replace(/[›,;.\s]+$/u, "")
      .trim();
    if (!base) continue;
    const num = /^(\d+)(?:\s+(.*))?$/.exec(base);
    if (num) {
      const children = (num[2] ?? "")
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
      if (children.length === 0) selectors.push({ path: [num[1]], bullets });
      for (const c of children) selectors.push({ path: [num[1], c], bullets });
      continue;
    }
    selectors.push({
      path: base
        .split("›")
        .map((s) => s.trim())
        .filter(Boolean),
      bullets
    });
  }
  return selectors;
}

/** Một selector → `{ ranges: [đầu, cuối)[], notes: string[] }`, hoặc `{ miss }` khi không thấy đề mục. */
function resolve(text, selector) {
  const lines = text.split("\n");
  const hs = headings(lines);
  let start = 0;
  let end = lines.length;
  let minLevel = 2;
  let label = [];
  for (const part of selector.path) {
    const h = findHeading(hs, part, start, end, minLevel);
    if (!h) {
      // Phần cuối không phải đề mục → có thể là gạch đầu dòng viết không nháy (`§ Quy ước › Job nền`).
      if (label.length > 0 && part === selector.path.at(-1)) {
        const b = findBullet(lines, part, start, end);
        if (b) return { ranges: [b], notes: [], label: [...label, part].join(" › ") };
      }
      return { miss: part };
    }
    label = [...label, h.text];
    start = h.line;
    end = sectionEnd(hs, h, lines.length);
    minLevel = h.level + 1;
  }
  if (selector.bullets.length === 0) return { ranges: [[start, end]], notes: [], label: label.join(" › ") };
  const ranges = [];
  const notes = [];
  for (const hint of selector.bullets) {
    const b = findBullet(lines, hint, start, end);
    if (b) ranges.push(b);
    else notes.push(hint);
  }
  if (notes.length > 0) return { ranges: [[start, end]], notes, label: label.join(" › ") };
  return { ranges: [[start, start + 1], ...ranges], notes, label: label.join(" › ") };
}

/** Gộp khoảng: bỏ khoảng nằm trong khoảng khác, nối khoảng chồng/kề nhau. */
function merge(ranges) {
  const sorted = [...ranges].sort((a, b) => a[0] - b[0] || b[1] - a[1]);
  const out = [];
  for (const r of sorted) {
    const last = out.at(-1);
    if (last && r[0] <= last[1]) last[1] = Math.max(last[1], r[1]);
    else out.push([...r]);
  }
  return out;
}

function extract(file, cell) {
  const text = readFileSync(file, "utf8");
  const lines = text.split("\n");
  const ranges = [];
  let failed = false;
  for (const sel of parseCell(cell.trim().startsWith("§") ? cell : `§ ${cell}`)) {
    const r = resolve(text, sel);
    if (r.miss) {
      console.error(`✗ ${file} § ${sel.path.join(" › ")}: không thấy đề mục «${r.miss}» — đọc cả file`);
      failed = true;
      continue;
    }
    for (const n of r.notes) console.error(`· ${file} § ${r.label}: không thấy gạch «${n}» — in cả mục`);
    ranges.push(...r.ranges);
  }
  let total = 0;
  for (const [a, b] of merge(ranges)) {
    total += b - a;
    console.log(`──── ${file} · dòng ${a + 1}–${b} ────`);
    console.log(lines.slice(a, b).join("\n").trimEnd());
    console.log();
  }
  console.log(`──── ${total}/${lines.length} dòng của ${file} ────`);
  return failed ? 1 : 0;
}

/**
 * Mọi (tài liệu, selector) mà bảng `governing-docs.md` nêu. Cột "Mục quyết định" tách theo ` · ` thành nhóm;
 * nhóm mở bằng viết tắt (KT/AG/CT/…) đổi tài liệu, nhóm mở bằng `§` dùng tài liệu ĐẦU TIÊN của cột "Đọc";
 * trong một nhóm, `; AG § …` cũng đổi tài liệu. Nhóm là đường dẫn file (`comitor-test/…`) thì không phải mục.
 */
function tableEntries(md, docs = DOCS) {
  const entries = [];
  const keys = Object.keys(docs).sort((a, b) => b.length - a.length);
  const alt = keys.map((k) => k.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|");
  const short = keys.filter((k) => !k.includes(".")).map((k) => k.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
  for (const row of md.split("\n").filter((l) => l.startsWith("| ") && !l.startsWith("| Đường dẫn"))) {
    const cells = row.split(" | ").map((c) => c.replace(/^\|\s*|\s*\|$/g, ""));
    if (cells.length < 3) continue;
    const firstDoc =
      Object.keys(docs)
        .filter((k) => cells[1].includes(k))
        .sort((x, y) => cells[1].indexOf(x) - cells[1].indexOf(y))[0] ?? null;
    for (const group of cells[2].split(" · ")) {
      const splitter = short.length > 0 ? new RegExp(`;\\s*(?=(?:${short.join("|")})\\s*§)`) : /$^/;
      for (const chunk of group.split(splitter)) {
        const m = new RegExp(`^\\s*(${alt})?\\s*(§.*)$`, "s").exec(chunk);
        if (!m) continue;
        const doc = m[1] ?? firstDoc;
        if (doc && docs[doc]) entries.push({ doc: docs[doc], cell: m[2] });
      }
    }
  }
  return entries;
}

function checkTable() {
  if (PROFILE.name === "module" && !existsSync("package.json")) {
    console.info(
      "· bỏ qua: repo chưa có mã (không có package.json) — hồ sơ module chỉ xét hàng Tài liệu (profiles/module.md)."
    );
    return;
  }
  const md = readFileSync(join(SKILL_DIR, PROFILE.table), "utf8");
  const failures = [];
  let ok = 0;
  const check = (file, cell) => {
    let text;
    try {
      text = readFileSync(file, "utf8");
    } catch {
      failures.push(`${file}: không đọc được (${cell})`);
      return;
    }
    for (const sel of parseCell(cell)) {
      const r = resolve(text, sel);
      if (r.miss) failures.push(`${file} § ${sel.path.join(" › ")}: không thấy «${r.miss}»`);
      else if (r.notes.length > 0)
        failures.push(`${file} § ${r.label}: không thấy gạch ${r.notes.map((n) => `«${n}»`)}`);
      else ok++;
    }
  };
  for (const { doc, cell } of tableEntries(md)) check(doc, cell);
  const pitfalls = join(SKILL_DIR, PROFILE.pitfalls);
  for (const names of Object.values(PROFILE.pitfallSections)) for (const n of names) check(pitfalls, `§ ${n}`);
  if (failures.length > 0) {
    console.error(
      `✗ ${failures.length} mục không tìm thấy — sửa bảng hoặc đề mục cho khớp:\n  ${failures.join("\n  ")}`
    );
    process.exit(1);
  }
  console.info(
    `✓ sections: hồ sơ ${PROFILE.name} — ${ok} mục của ${PROFILE.table} và ${PROFILE.pitfalls} đều tìm thấy trong repo này.`
  );
}

function selfTest() {
  const doc = [
    "# Tài liệu — quy ước chung", // cấp 1: không bao giờ khớp, dù chứa "quy ước"
    "## 2. Bảng",
    "bảng",
    "## 3. Từng tầng",
    "### Tầng 1 · Lõi",
    "lõi",
    "### Rìa B · Route",
    "route",
    "### Rìa B′ · Action",
    "action",
    "## Quy ước bắt buộc giữ",
    "- **Job nền: `scripts/jobs`**, mỏng.",
    "  tiếp dòng",
    "- **Warning LÀ lỗi.** Không cờ.",
    "```",
    "## không phải đề mục",
    "```",
    "## Cạm bẫy",
    "### Next.js và ranh giới",
    "next",
    "### Đa ngôn ngữ",
    "i18n"
  ].join("\n");
  const failures = [];
  const expect = (cell, want) => {
    const got = parseCell(cell).flatMap((s) => {
      const r = resolve(doc, s);
      return r.miss ? [`MISS:${r.miss}`] : merge(r.ranges).map(([a, b]) => `${a}-${b}`);
    });
    if (got.join(",") !== want) failures.push(`${cell} → ${got.join(",")} (cần ${want})`);
  };
  expect("§ 3 tầng 1", "4-6");
  expect("§ 3 rìa B, rìa B′", "6-8,8-10");
  expect("§ 2 (hàng 1), § 3 tầng 1", "1-3,4-6");
  expect("§ Quy ước", "10-17");
  expect('§ Quy ước ("Warning LÀ lỗi")', "10-11,13-17");
  expect('§ Quy ước › "Job nền"', "10-13");
  expect("§ Quy ước › Job nền", "11-13");
  expect("§ Cạm bẫy › Next.js", "18-20");
  expect("§ Cạm bẫy › `Next.js` (Date, Decimal)", "18-20");
  // Đối chứng âm tính: số không khớp tiền tố số khác, đề mục trong khối mã không tồn tại.
  expect("§ 1", "MISS:1");
  expect("§ không phải đề mục", "MISS:không phải đề mục");
  // Gạch đầu dòng không thấy → in CẢ mục (hướng đọc nhiều hơn), không bao giờ in rỗng.
  expect('§ Quy ước ("Không có thật")', "10-17");
  const rows = tableEntries(
    [
      "| `x/**` | KT; AG | § 3 tầng 0; AG § Cạm bẫy › Next.js (`Date`) |",
      "| `y/**` | KT; skill | KT § 5 · `comitor-test/references/a.md` |",
      "| `w/**` | AG; KT | § Quy ước |", // tài liệu ĐẦU TIÊN của cột, không phải khoá đầu tiên của `DOCS`
      '| `z/**` | `docs/migration.md`; AG | migration.md toàn bộ · AG § Quy ước ("Job nền") |'
    ].join("\n"),
    MODULE_DOCS
  ).map((e) => `${e.doc}:${e.cell}`);
  const want = [
    "docs/kien-truc-ung-dung.md:§ 3 tầng 0",
    "AGENTS.md:§ Cạm bẫy › Next.js (`Date`)",
    "docs/kien-truc-ung-dung.md:§ 5",
    "AGENTS.md:§ Quy ước",
    'AGENTS.md:§ Quy ước ("Job nền")'
  ];
  if (JSON.stringify(rows) !== JSON.stringify(want)) failures.push(`tableEntries: ${JSON.stringify(rows)}`);
  // Viết tắt của hồ sơ khác: `CL` đổi tài liệu giữa ô, `CLAUDE.md` (có dấu chấm) thì không làm dấu tách.
  const other = tableEntries("| `src/**` | CL; RD | § Quy ước; RD § 5 · CL § Cạm bẫy |", {
    CL: "CLAUDE.md",
    RD: "README.md"
  }).map((e) => `${e.doc}:${e.cell}`);
  if (JSON.stringify(other) !== JSON.stringify(["CLAUDE.md:§ Quy ước", "README.md:§ 5", "CLAUDE.md:§ Cạm bẫy"])) {
    failures.push(`tableEntries (hồ sơ khác): ${JSON.stringify(other)}`);
  }
  // Khối profile: đủ khoá thì đọc được; thiếu khoá hay thiếu khối thì NÉM (review dừng, không đoán).
  const block = (body) => `# Hồ sơ\n\n\`\`\`json profile\n${body}\n\`\`\`\n`;
  try {
    const p = parseProfile(block('{"docs":{},"table":"t.md","pitfalls":"p.md","pitfallSections":{}}'));
    if (p.table !== "t.md") failures.push("parseProfile: đọc sai `table`");
  } catch (e) {
    failures.push(`parseProfile hợp lệ mà ném: ${e.message}`);
  }
  for (const [name, md] of [
    ["thiếu khoá", block('{"docs":{},"table":"t.md"}')],
    ["thiếu khối", "# Hồ sơ\n"],
    ["JSON hỏng", block("{docs:")]
  ]) {
    try {
      parseProfile(md);
      failures.push(`parseProfile «${name}»: phải ném`);
    } catch {}
  }
  if (failures.length > 0) {
    console.error(`✗ sections tự kiểm HỎNG:\n  ${failures.join("\n  ")}`);
    process.exit(1);
  }
  console.info(
    "✓ sections: 12 ca selector (3 đối chứng âm tính), tách bảng (kể cả thứ tự cột Đọc và viết tắt của hồ sơ khác), " +
      "khối profile (3 đối chứng âm tính) đều đúng."
  );
}

const args = process.argv.slice(2);
if (args[0] === "--self-test") selfTest();
else if (args[0] === "--check-table") checkTable();
else if (args[0] === "--profile" && args.length <= 2 && !args.includes("--json")) {
  console.log(
    `${PROFILE.name} — ${PROFILE.from} · ${PROFILE.file.replace(`${SKILL_DIR}/`, ".claude/skills/comitor-review/")}`
  );
} else if (args[0] === "--profile" && args.includes("--json")) {
  console.log(JSON.stringify({ name: PROFILE.name, from: PROFILE.from }));
} else if (args[0] === "--list" && args[1]) {
  const hs = headings(readFileSync(args[1], "utf8").split("\n"));
  for (const h of hs) console.log(`${String(h.line + 1).padStart(5)}  ${"  ".repeat(h.level - 1)}${h.text}`);
} else if (args.length === 2) process.exit(extract(args[0], args[1]));
else {
  console.error("Dùng: sections.mjs <file> '<§ mục…>' | --list <file> | --check-table | --self-test");
  process.exit(2);
}
