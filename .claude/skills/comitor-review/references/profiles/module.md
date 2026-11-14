# Hồ sơ `module` — mặc định

Module sinh từ `comitor-starter` (và chính starter). Đây là hồ sơ mà mọi phần còn lại của skill viết cho:
`SKILL.md`, bốn reference nhóm, `governing-docs.md`, `pitfalls.md` áp NGUYÊN VĂN, không có mục nào bị thay.
Repo không có `.claude/comitor-repo.json` thì dùng hồ sơ này.

```json profile
{
  "docs": {
    "KT": "docs/kien-truc-ung-dung.md",
    "AG": "AGENTS.md",
    "CT": "CONTRIBUTING.md",
    "CLAUDE.md": "CLAUDE.md",
    "migration.md": "docs/migration.md"
  },
  "table": "references/governing-docs.md",
  "pitfalls": "references/pitfalls.md",
  "pitfallSections": {
    "Kiến trúc": ["Một luật, viết hai lần"],
    "Dữ liệu & bảo mật": ["Phân quyền và đường ghi", "Workspace, dữ liệu, toàn vẹn", "Thời gian", "Hướng hỏng"],
    "Quy ước": ["Đa ngôn ngữ", "Giao diện"],
    "Chất lượng": ["API giả", "Test không thể đỏ", "Tài liệu nói dối", "Lệch đặc tả"]
  }
}
```

## Ngoại lệ khai trong repo

Một module được lệch luật của skill ở ĐÚNG chỗ mà tài liệu quy định của chính nó (`AGENTS.md`, ADR trong `docs/`)
ghi thành ngoại lệ có lý do — ví dụ vùng mockup của `comitor-redesign` dùng `@comitor-ai/web-ui` và màu theo theme
khách (ADR R010). Review đọc ngoại lệ đó ở bước 0 và KHÔNG báo nó là phát hiện; chỉ báo khi mã đi ra ngoài phạm vi
ngoại lệ đã ghi, hoặc ngoại lệ được viện dẫn mà tài liệu không có.

## Repo chưa có mã

Module vừa tạo repo mà chưa sao starter (chưa có `package.json` ở gốc): bước 1.7 không đọc được tên gói — đó
KHÔNG phải lệnh git hỏng. Chỉ nhóm **Chất lượng** (hàng **Tài liệu**) áp; ba nhóm kia n/a, và **Đã kiểm** ghi
"repo chưa có mã".
