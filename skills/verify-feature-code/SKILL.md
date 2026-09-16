---
name: verify-feature-code
description: Verify a BA feature folder against actual code in one or more indexed repos; produce a gap report and persist it as a dated markdown file in the feature's verifications/ subfolder.
---

# /verify-feature-code — Code vs Doc Verification

## Mục đích

Mỗi khi BA cần biết **doc có khớp code không**, chạy skill này. Nó:

1. Đọc toàn bộ doc của 1 feature folder
2. Đọc code trong 1 hoặc nhiều repo đã index qua GitNexus
3. Sinh **gap report** (md) phân loại Critical/High/Medium/Low
4. **Lưu report** vào `<feature>/verifications/YYYY-MM-DD-code-vs-doc-verification.md`
5. Không tự update doc — BA đọc report rồi quyết định

## Khi nào dùng

- Trước release / review feature để đảm bảo spec đã phản ánh code thật
- Sau khi dev MR xong, doc cần update theo code
- Audit định kỳ (quý/tháng)

## Khi nào KHÔNG dùng

- Nếu feature chưa có code (brand new spec) → dùng `/project:review-feature` thay
- Nếu chỉ cần gen `api-design.md` từ doc → dùng `/project:write-api-design`
- Nếu cần explore code (no doc yet) → dùng `/codebase-doc`

---

## Inputs

| Param | Bắt buộc | Mô tả |
|-------|----------|-------|
| `<feature-folder>` | ✅ | Path đến feature folder (vd `docs/requirements/compute/cloud-advisor`) |
| `--repos <list>` | ✅ | Comma-separated repo names đã index (vd `portal-ui-user,portal-api-dev`) |
| `--exclude <area>` | ⬜ | Skip một phần (vd `admin`, `billing-callback`) |
| `--focus <area>` | ⬜ | Chỉ kiểm tra 1 phần cụ thể |
| `--format md\|docx` | ⬜ | Default `md`. `docx` gọi skill `issue-discovery-report` để gen BDR file |

Ví dụ:
```
/verify-feature-code docs/requirements/compute/cloud-advisor --repos portal-ui-user,portal-api-dev --exclude admin
```

---

## Workflow (Claude MUST follow)

### Step 0 — Precheck

1. Gọi `list_repos` (GitNexus) → confirm repos đã index.
   - Check `~/.gitnexus/registry.json`: `indexedAt` phải mới hơn last commit của repo.
   - Nếu repo chưa có trong registry: **ưu tiên** chạy binary trực tiếp thay vì `npx`:
     ```bash
     node ~/.npm/_npx/*/node_modules/gitnexus/dist/cli/index.js analyze < /dev/null 2>&1
     ```
     Chạy từ thư mục repo, `run_in_background=true`, timeout 10 phút.
   - **Tại sao không dùng `npx gitnexus analyze`:** `npx` re-verify package mỗi lần gọi → thường treo không output, exit 0 mà không làm gì. Chạy binary node trực tiếp bypass được.
     - Nếu `~/.npm/_npx/*/node_modules/gitnexus/` chưa có: `npx --yes gitnexus status` 1 lần để cache package, sau đó dùng node trực tiếp.
   - **Progress indicator:** analyze KHÔNG stream log qua pipe; xem process bằng `ps aux | grep gitnexus` và folder `<repo>/.gitnexus/` (có `lbug`, `lbug.wal` = đang ghi DB). Thời gian: ~5–10 phút cho repo vừa (5k files), dài hơn cho repo lớn.
   - **Fallback:** Nếu GitNexus index chưa xong sau 10 phút, vẫn có thể tiếp tục verify bằng Grep/Read trực tiếp — ghi chú trong report "GitNexus index in progress, findings from direct grep".
2. Đọc `<feature-folder>/` để biết file nào tồn tại.
3. Đọc `<feature-folder>/verifications/` (nếu có) để biết các lần verify trước — tránh duplicate findings, chỉ report mới/khác.

### Step 1 — Read docs

Đọc theo thứ tự:

1. `OVERVIEW.md` hoặc `SRS.md` (functional requirements)
2. `DATA_DICTIONARY.md` (field specs, defaults, enums)
3. `DOMAIN_MODEL.puml` hoặc `data-design.md` (entities + relationships)
4. `api-design.md` nếu có
5. `workflow-design.md` nếu có
6. `architecture.md` / `test-case.md` nếu có

Trích xuất:
- Entity names, enum values, defaults
- API endpoints (method + path)
- Business rules, state machines
- RBAC roles / permissions
- External system dependencies

### Step 2 — Query code (GitNexus first, Grep fallback)

Ưu tiên theo thứ tự:

1. **Resource** `gitnexus://repo/{name}/context` — check staleness, get stats
2. **Resource** `gitnexus://repo/{name}/clusters` — find cluster matching feature name
3. **Tool** `query` — với concept keywords từ doc
4. **Tool** `cypher` — direct graph query nếu cần specific symbol
5. **Fallback** `Grep` + `Read` khi GitNexus không có kết quả

Với mỗi entity/endpoint/rule trong doc, tìm:
- File thực tế chứa implementation
- Enum values / default values thực tế
- Route registrations (blueprints, route tables)
- Migrations (initial seed data)

### Step 3 — Cross-reference

Lập bảng 3 cột **Doc | Code | Status**:

| Aspect | Doc says | Code shows | Match? |
|--------|----------|-----------|--------|
| Entity names | ... | ... | ✅ / ❌ |
| Enum values | ... | ... | ✅ / ❌ |
| API endpoints | ... | ... | ✅ / ❌ |
| Defaults | ... | ... | ✅ / ❌ |
| RBAC | ... | ... | ✅ / ❌ |
| State machine | ... | ... | ✅ / ❌ |

### Step 4 — Classify issues

| Severity | Criterion |
|----------|-----------|
| **Critical** | Code hoặc doc gây lỗi runtime / data loss / bypass security / bug đã ship |
| **High** | Endpoint/entity đã ship nhưng không có doc, hoặc enum/default không khớp gây confusion |
| **Medium** | State machine / RBAC / lifecycle thiếu doc, naming không nhất quán |
| **Low** | Cosmetic, glossary, minor clarification |

### Step 5 — Write report

File: `<feature-folder>/verifications/YYYY-MM-DD-code-vs-doc-verification.md`

Template:

````markdown
# <Feature> — Code vs Doc Verification Report

| Field | Value |
|-------|-------|
| **Date** | YYYY-MM-DD |
| **Feature** | `<path>` |
| **Verifier** | Claude (BA assist) |
| **Scope** | <what was covered; what excluded> |
| **Codebases** | <repo@commit or @index-date> |
| **Tools** | GitNexus <status> / Grep fallback |

## Docs Reviewed
- ...

## Code Reviewed
- ...

## Summary

| Severity | Count | Description |
|----------|-------|-------------|
| Critical | N | ... |
| High | N | ... |
| Medium | N | ... |
| Low | N | ... |

**Overall:** <1-line verdict — DOC = CODE / DOC ⊃ CODE / DOC ⊂ CODE / DIVERGED>

---

## Section A — Critical Issues

### C1. <title>
**Where:** `path/to/file.py:LINE`

<what doc says> vs <what code does>

**Recommended:** <action>

---

## Section B — High Issues
## Section C — Medium Issues
## Section D — Low Issues

## Action Plan

| # | Action | File | Owner |
|---|--------|------|-------|
| 1 | ... | ... | BA/Dev |

## Excluded
- <areas deferred, why, who follows up>

<!-- verification-meta:
  generated_by: verify-feature-code
  schema_version: 1
  codebases_indexed:
    - <repo>@<date>
-->
````

### Step 6 — DO NOT update feature docs

Skill chỉ **báo cáo**, không tự sửa. BA review rồi chạy `/project:write-overview`, `/project:write-api-design`, hoặc sửa manual.

---

## Report Conventions

### File naming
```
<feature-folder>/verifications/YYYY-MM-DD-code-vs-doc-verification.md
```

Nếu nhiều lần 1 ngày: thêm suffix `-v2`, `-v3`.

### Issue ID format
- `C1, C2, C3...` — Critical
- `H1, H2, H3...` — High
- `M1, M2, M3...` — Medium
- `L1, L2, L3...` — Low

Mỗi issue có:
- **Where:** file path (tuyệt đối hoặc từ repo root) + line number nếu có
- **Doc says** vs **Code reality** — phải trích câu/entity/enum cụ thể
- **Recommended** — hành động, ai làm

### Anti-patterns

- ❌ Generic claim "doc doesn't match code" — phải chỉ rõ file/line
- ❌ Recommend sửa code — skill này audit doc, không chỉ đạo engineering
- ❌ Tự update OVERVIEW.md / PUML — chỉ sinh report
- ❌ Đoán entity thuộc repo nào khi chưa index
- ❌ Skip Critical issues "để báo sau" — phải list hết

---

## Output Checklist

```
□ File verifications/YYYY-MM-DD-code-vs-doc-verification.md đã tạo
□ Header đầy đủ: Date, Feature, Scope, Codebases, Tools
□ Summary table có số issue mỗi severity
□ Mỗi issue: Where (file:line), Doc says vs Code reality, Recommended
□ Action Plan có owner rõ ràng (BA / Dev / Ops)
□ Excluded section ghi rõ scope bị skip
□ HTML comment metadata ở cuối (generated_by, indexed repos)
□ KHÔNG sửa file doc nào khác ngoài file report
```

---

## Integration with other skills

| Cần làm tiếp | Skill |
|--------------|-------|
| Gen .docx BDR từ report | `issue-discovery-report` |
| Update OVERVIEW.md từ gaps | `/project:write-overview` |
| Gen api-design.md từ endpoints chưa doc | `/project:write-api-design` |
| Explore code của endpoint cụ thể | `gitnexus-exploring` |
| Trace bug trong code | `gitnexus-debugging` |
| Lập kế hoạch refactor để khớp doc | `gitnexus-refactoring` |

---

## Example: Cloud Advisor (2026-04-18, 2026-04-19)

**Run 1 (non-admin):**
```
/verify-feature-code docs/requirements/compute/cloud-advisor --repos portal-ui-user,portal-api-dev --exclude admin
```

Kết quả:
- File: `docs/requirements/compute/cloud-advisor/verifications/2026-04-18-code-vs-doc-verification.md`
- 3 Critical, 3 High, 4 Medium, 3 Low
- Verdict: DOC ⊃ CODE (doc describes 5 categories / 17 rules; code ships 3 / 10)

**Run 2 (admin follow-up):**
```
/verify-feature-code docs/requirements/compute/cloud-advisor --repos portal-ui-admin,portal-api-dev --focus admin
```

Kết quả:
- File: `docs/requirements/compute/cloud-advisor/verifications/2026-04-19-admin-code-vs-doc-verification.md`
- 0 Critical, 3 High, 1 Medium, 0 Low
- Verdict: DOC ⊃ CODE (admin side) — UFR-680/681/682 chưa implement; ResourceTypeKey & RBAC actions đã định nghĩa nhưng chưa wire

Pattern: **mỗi focus/scope = 1 report file riêng**, không overwrite file cũ.
