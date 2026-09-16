# FPT Cloud Template Definitions

> **Master template definition for FPT Cloud documentation.** Source of truth for content standards, voice rules, structure requirements, and quality scorecard.

> **Status (v1.6.0)**: Currently covers User Guide doc type only. Other doc types (API Reference, Deployment Guide, Runbook, Release Notes, Knowledge Base, Operation Document) deferred to future versions.

This file is the authoritative reference docsmith follows when generating FPT Cloud documentation. Every command (audience, plan, voice, draft, edit, verify, score) consults this file to ensure compliance with CSO-defined standards.

---

## Part 1 — Document Types

FPT Smart Cloud defines 7 document types. Each has its own template definition.

| Type | Purpose | docsmith status (v1.6.0) |
|---|---|---|
| User Guide | Product usage guide for end users | ✅ Fully supported |
| API Reference | API technical documentation | ❌ Deferred |
| Deployment Guide | Deployment instructions | ❌ Deferred |
| Runbook | Internal operations document | ❌ Deferred |
| Release Notes | Version change notes | ❌ Deferred |
| Knowledge Base | Knowledge base articles | ❌ Deferred |
| Operation Document | Internal ops document | ❌ Deferred |

This file defines only User Guide. Other types follow same FPT_TEMPLATES.md pattern when added.

---

## Part 2 — Required Structure (User Guide)

### Mandatory sections (must be present)

Every User Guide module MUST have these 4 sections:

1. **Overview** — Product/feature intro, value proposition
2. **Initial setup** — Pre-conditions, account/permission/env setup
3. **Quick starts** — 5-10 min get-started flow
4. **Tutorials** — Step-by-step learning guides

### Optional sections

Can be added per product needs:

- **Samples** — Code samples, ready-to-use examples
- **FAQs** — Common questions and answers
- **Reference** — Lookup tables, configurations

Optional sections may have different names per product (e.g., "Examples", "Common questions", "API reference") — name is flexible, purpose is what matters.

### Section type mapping (docsmith)

When `plan` runs with `sitemap_pattern: D` (FPT User Guide):

| docsmith section | FPT required equivalent |
|---|---|
| overview | Overview ✓ |
| getting-started | Initial setup ✓ |
| quick-starts | Quick starts ✓ |
| tutorials | Tutorials ✓ |
| samples | Samples (optional) |
| faqs | FAQs (optional) |
| reference | Reference (optional) |
| troubleshooting | (not in FPT spec, optional) |

`verify` Check 8 (sitemap pattern compliance) enforces this: missing mandatory section → STOP.

---

## Part 3 — Metadata Standards

> v1.6.0: deferred per user decision. Will be addressed in future version. Last Updated, Editor, Owner derivable from git history at deploy time.

---

## Part 4 — Content Writing Rules

These rules apply to every draft. AI follows during `draft`; `edit` and `verify` enforce.

### 4.1 Page titles

- **Sentence case**: `[Action] [Object]` — NEVER ALL CAPS
- Max 60 characters
- Guide → imperative: `Tạo [resource] mới`
- Concept → noun phrase: `Tổng quan [feature]`
- No period or colon at end

✓ Do: `Khởi tạo resource mới` | `Tổng quan về [feature]`
✗ Don't: `HƯỚNG DẪN KHỞI TẠO RESOURCE MỚI.` | `[Feature] là gì?`

### 4.2 Section headings

- Sentence case, use H2-H3 (avoid H4+)
- Parallel structure: same-level headings have same grammatical form
- NO numbering in headings — hierarchy already shows order

✓ Do: `## Gắn [tag] khi tạo [resource]` + `## Quản lý [tag] sau khi tạo`
✗ Don't: `## 1. Tạo` + `## BƯỚC 2: MANAGE`

### 4.3 Introductions

- Max 2 sentences: `[Feature] giúp bạn [benefit cụ thể]. Dùng [feature] khi [use case].`
- Lead with user benefit, NOT system description
- Second person (`bạn`)
- NO trailing clauses like "...đặc biệt khi X mở rộng qua Y" (AI-tell)

✓ Do: `[Feature] giúp bạn [benefit cụ thể]. Dùng [feature] khi [use case ngắn gọn].`
✗ Don't: `[Feature] là tính năng cung cấp các gợi ý và khuyến nghị để...`

### 4.4 Prerequisites

- Always a separate section if pre-conditions exist
- Format: plain bullet list, NO ✅ emoji (looks AI-generated)
- Link to setup guide if not met

✓ Do:
```
- Có tài khoản FPT Cloud với role Admin hoặc Editor
- Đã enable [Feature X]
```

✗ Don't:
```
- ✅ Có tài khoản FPT Cloud
- ✅ Role Admin
```

### 4.5 Procedures

- Numbered list, 1 action per step
- Start each step with verb: `Chọn`, `Nhấn`, `Điền`, `Kiểm tra`
- Max 10 steps — if longer, split into sub-procedure
- Verification step at end: `[Object] xuất hiện trong danh sách.`
- Screenshot placed right after the step it illustrates
- Alt text mô tả nội dung

✓ Do:
```
1. Chọn [Menu] → [Action].
2. Điền [field A] và [field B].
3. Nhấn [Button]. [Object] mới hiển thị trong danh sách.
```

✗ Don't:
```
1. Vào menu bên trái, tìm mục X, click vào, sau đó tìm nút Y và click.
```

### 4.6 Callouts / Admonitions

4 callout types with specific emojis:

- 💡 **Tip**: Optimization tips, best practices
- 📝 **Note**: Supplementary info, clarifications
- ⚠️ **Warning**: Risky actions, potential consequences
- 🚨 **Danger**: Irreversible actions (delete, format, permanent changes)

Rules:
- Max 1-2 callouts per section
- Each callout 1-2 sentences only

### 4.7 Button / action labels

- Short imperative verbs: `Create`, `Delete`, `Save`, `Apply`, `Refresh`
- Pair with object if needed: `Create [Object]`, `Delete [Object]`
- NEVER: `Click here`, `Press this button`, `Nhấn vào đây`

### 4.8 Status messages

Templates:

- **Success**: `[Object] đã được [action] thành công.`
- **Error**: `Không thể [action]. Kiểm tra [nguyên nhân] hoặc liên hệ Admin.`
- **Loading**: `Đang xử lý...` (NOT `Vui lòng chờ`)

Always solution-oriented in error messages.

### 4.9 Empty states

- Describe state + guide next action
- Template: `Chưa có [object] nào. Chọn [Action] để bắt đầu [benefit].`
- NEVER: `No data`, `Empty`, `Không có dữ liệu`

### 4.10 Cross-references

- Descriptive link text: `Xem [Hướng dẫn action]` — NOT `Click here`
- Inline when relevant + "Bước tiếp theo" section at end
- Avoid circular references
- Don't link to same page twice per section

### 4.11 Screenshots

- Place right after illustrated step
- Alt text describes content: `![Hộp thoại [Action] với trường [Field A] và [Field B]]`
- Format: PNG for static, GIF for multi-step flow
- Descriptive filename: `[action]-[object]-form.png` — NOT `screenshot1.png`

### 4.12 UI references

- Bold for buttons/menus: `chọn **[Button Name]**`
- Match UI exactly — don't paraphrase
- Navigation path uses `→`: `[Menu] → [Sub-menu] → [Action]`

### 4.13 Code examples

- Always include language tag (`bash`, `json`, `python`)
- Copy-paste runnable, no pseudocode
- Placeholders in SCREAMING_SNAKE_CASE: `YOUR_API_KEY`, `YOUR_TOKEN`
- NEVER use real tokens/keys
- Max 20 lines per block — split if longer

### 4.14 Breadcrumb / navigation

- Format: `[Menu] → [Sub-menu] → [Action]`
- Bold for menu/button names

### 4.15 Anti-AI-tells — CRITICAL

Readers should NOT recognize doc was AI-generated. AVOID these patterns:

1. **Emoji ✅ ❌ in content** — only allowed in callout blocks (💡 ⚠️ 🚨). Bullet lists and prerequisites use plain dashes.

2. **Em-dash density** — max 1 em-dash per paragraph. For longer explanations, line break or use sub-bullet.

3. **Fixed intro formula** — never use `"...đặc biệt khi [X] mở rộng qua [Y]"`. Intros are short, direct, no trailing clause.

4. **Perfect parallel structure** — not every bullet needs same length. Break 1-2 items if natural content is shorter.

5. **"Bước tiếp theo" always 3 items** — use 2-4 items depending on actual content. Don't pad to fill 3.

6. **Rigid verification step** — don't include `[Object] xuất hiện trong danh sách` in every flow. Use when truly needed, omit when obvious.

These are detected by `verify` Check 22 (anti-AI-tells). Each violation found → block deploy.

---

## Part 5 — Voice Chart Rules

### Product Principles

1. **Clear (Rõ ràng)** — Clear instructions so reader self-serves without calling support
2. **Practical (Thực dụng)** — Focus on real value: WHY before HOW, link to business benefit
3. **Consistent (Nhất quán)** — Same style, pattern throughout — terminology, structure, tone unified

### Voice Chart Matrix (3 principles × 6 aspects)

| Aspect | Clear | Practical | Consistent |
|---|---|---|---|
| **Concepts** | Self-service, reduce support dependency | ROI, cost savings, security, risk reduction | Same mental model across modules, familiar UX |
| **Vocabulary** | Concrete, terse words. `Chọn [Action]` not `Thực hiện thao tác [Action]` | Business value: `giảm chi phí X%` not `tối ưu hóa` | Tech terms in EN unchanged (see Vocabulary Guide) |
| **Verbosity** | Terse: 1 sentence/step, max 2 lines | Moderate: intro max 2 sentences explaining WHY, no trailing clauses | Prerequisites thorough, steps terse, callouts 1-2 sentences |
| **Grammar** | Active voice, imperative: `Nhấn [Button]` not `Nút [Button] được nhấn` | Second person: `bạn chọn`, `bạn có thể`. Present tense | Same sentence structure for all procedure steps |
| **Punctuation** | Period at end of each step. NO exclamation marks | Em-dash (—) for short inline explanations | Bullet lists no semicolons at end. Heading sentence case |
| **Capitalization** | Feature/product names follow UI capitalization | Heading sentence case | NO ALL CAPS. NEVER lowercase product names |

### Vocabulary Guide

**Technical terms — KEEP English (don't translate)**:
Instance, VPC, Subnet, Floating IP, Snapshot, Load Balancer, Security Group, Container, Pod, Cluster, Namespace, Volume, Bucket, Region, Zone

**Actions — USE Vietnamese**:
- Tạo (Create)
- Xóa (Delete)
- Chỉnh sửa (Edit)
- Lưu (Save)
- Mở (Open)
- Đóng (Close)
- Khởi động (Start)
- Dừng (Stop)
- Triển khai (Deploy)

**FPT product names — KEEP unchanged**:
FPT Cloud Console, Cloud Advisor, Cost Explorer, FPT Object Storage, FPT Container Service

**Never translate**:
API, SDK, CLI, Dashboard, Webhook, Token, OAuth, JWT, REST, GraphQL, SSH, HTTPS

### Voice vs Tone

Voice consistent across all docs. Tone shifts by context:

| Context | Tone | Example |
|---|---|---|
| Onboarding | Warm, encouraging | `Hãy bắt đầu bằng việc [action] để [benefit].` |
| Error messages | Calm, solution-oriented | `Không thể [action]. Kiểm tra [cause] hoặc liên hệ Admin.` |
| Success | Concise, positive | `[Object] đã được [action] thành công.` |
| Technical reference | Precise, neutral | `[Concept] gồm [component A] và [component B].` |
| Warnings | Direct, clear consequences | `Khi [action], [consequence]. Hành động không thể hoàn tác.` |

---

## Part 6 — Versioning Rules

> v1.6.0: deferred per user decision. May be addressed via Docusaurus native versioning in future version.

---

## Part 7 — Content Scorecard

10 criteria, each scored 0-2 (0 = missing/violated, 1 = partial, 2 = meets). Max total: 20.

### Scoring tiers

- **0-8**: Poor — rewrite needed
- **9-13**: Fair — major edits needed
- **14-17**: Good — publishable, optimization recommended
- **18-20**: Excellent — ready to publish

**Deploy gate**: Score ≥14 required to deploy (override with `--force-deploy`).

### Criteria

#### Group A: Clear (Rõ ràng) — 4 criteria

**1. Context-setting intro (0-2)**
- Description: Opening 1-2 sentences explaining what feature/article solves and value to reader
- 2 pts: Opening answers "tính năng giúp gì" before jumping to steps
- 1 pt: Has intro but vague or describes system not user benefit
- 0 pts: No intro, jumps straight to steps OR copy of system description
- Fix: Rewrite intro as `[Tính năng] giúp bạn [kết quả]` + brief impact example

**2. Standard guide structure (0-2)**
- Description: Has Prerequisites (if needed), clear headings, numbered steps, 1 action per step
- 2 pts: Has clear subsections (Overview, Prerequisites, Steps) per template
- 1 pt: Some sections present, some missing OR multiple actions per step
- 0 pts: Wall of text, no clear structure
- Fix: Split steps, add headings per template, convert long lists to numbered

**3. Active voice with "bạn" (0-2)**
- Description: Written in active voice, second-person, no passive/`vui lòng`
- 2 pts: `Bạn chọn`, `Nhấn`, `Bật`; no `được thực hiện`
- 1 pt: Mostly active but few passive sentences
- 0 pts: Heavy passive voice OR third-person OR excessive `vui lòng`
- Fix: Convert to active voice, replace `vui lòng` with direct imperative

**4. Visual support (0-2)**
- Description: Screenshots/callouts used when they aid understanding; alt text correct
- 2 pts: Screenshots match current UI, callouts for tips/warnings present
- 1 pt: Has visuals but some not relevant OR alt text missing
- 0 pts: No visuals where needed OR misleading visuals
- Fix: Replace with current UI screenshots, add alt text + callouts

#### Group B: Practical (Thực dụng) — 3 criteria

**5. WHY before HOW (0-2)**
- Description: Each important section explains why action is needed, links to business value
- 2 pts: Lead sentence states benefit (cost reduction, security) before steps
- 1 pt: Some sections have WHY, others jump to HOW
- 0 pts: Only describes actions, no rationale
- Fix: Add `Điều này giúp bạn...` or cite SLA/cost impact

**6. Next-action guidance (0-2)**
- Description: Doc guides reader to next steps (related tasks, clear CTAs)
- 2 pts: Has `Tiếp theo`/`Xem thêm` linking to related tasks
- 1 pt: Has links but unclear what to do next
- 0 pts: Abrupt end, no follow-up guidance
- Fix: Add related docs links or post-completion checklist

**7. Value/risk callouts (0-2)**
- Description: Uses Note/Warning/Info for optimization tips, downtime warnings, limits
- 2 pts: At least one callout for noteworthy info
- 1 pt: Some callouts but missing where critical
- 0 pts: Important info in plain text, easy to miss
- Fix: Move critical info into callouts with standard emojis

#### Group C: Consistent (Nhất quán) — 3 criteria

**8. Terminology & capitalization (0-2)**
- Description: Tech terms in English, feature names capitalized per Voice Chart
- 2 pts: `Cloud Advisor`, `Security Group` correctly cased; tech terms in EN
- 1 pt: Mostly correct but few inconsistencies
- 0 pts: All translated to Vietnamese OR random casing
- Fix: Check Vocabulary Guide, find/replace across doc

**9. Punctuation & formatting (0-2)**
- Description: Period at sentence end, correct bullet/number rules, sentence case headings
- 2 pts: Steps end with period, bullets consistent
- 1 pt: Mix of bullet/paragraph, missing periods OR heading ALL CAPS
- 0 pts: Wildly inconsistent formatting
- Fix: Review markdown, use linter

**10. Links & references (0-2)**
- Description: Internal links follow docs structure, anchors work, no dead links
- 2 pts: Relative links work, breadcrumbs correct
- 1 pt: Most links work, some absolute/broken
- 0 pts: Broken links, 404 anchors
- Fix: Test in dev server, use Docusaurus-standard relative paths

### Scoring example

See `documentation/score/<module>/<doc>.md` after running `/docsmith score`.

### Anti-AI-tells checklist (bonus, not scored)

Check after 10 criteria:

- [ ] No ✅ ❌ emoji outside callouts
- [ ] No `...đặc biệt khi X mở rộng qua Y` intro formula
- [ ] Em-dashes ≤1 per paragraph
- [ ] `Bước tiếp theo` not rigidly 3 items
- [ ] Verification step not rigidly in every flow
- [ ] Parallel structure not unnaturally perfect

Detected by `verify` Check 22. Each violation → block deploy (override with `--force-deploy`).

---

## Document version

This template definition: v1.0 (initial — 2026-05-12)

Last updated for docsmith v1.6.0.
