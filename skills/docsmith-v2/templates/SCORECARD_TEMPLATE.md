# Content Scorecard Template

> Used by `/docsmith score` command to assess each doc against FPT Cloud quality standards. Authority: [FPT_TEMPLATES.md § Part 7](FPT_TEMPLATES.md).

## When to use

After `verify` passes structural checks, before `deploy`. Optional for non-FPT projects, REQUIRED for projects with `compliance: fpt-user-guide` in project intake.

## Scoring system

- 10 criteria × 0-2 points = max 20
- Tiers:
  - **0-8**: Poor — rewrite needed
  - **9-13**: Fair — major edits needed
  - **14-17**: Good — publishable, optimization recommended
  - **18-20**: Excellent — ready to publish
- **Deploy gate**: ≥14 required (override: `--force-deploy`)

## Output file format

Saved at `documentation/score/<module>/<doc>.md` for each doc in the module.

```markdown
---
generated_at: 2026-05-12T10:30:00Z
generated_by: docsmith-1.6.0
doc_path: documentation/drafts/en/instances/create-instance.md
module: instances
score: 18
tier: Excellent
deploy_ready: true
anti_ai_tells_pass: true
---

# Score report: drafts/en/instances/create-instance.md

**Final score**: 18/20 — Excellent
**Deploy ready**: ✓ Yes (threshold: 14)
**Anti-AI-tells**: ✓ Pass (0 violations)

## Group A: Clear (Rõ ràng) — 7/8

### 1. Context-setting intro (2/2)
**Evidence**: Opens with `Cloud Advisor giúp bạn ưu tiên vấn đề bảo mật và chi phí` — clear benefit before steps.

### 2. Standard guide structure (2/2)
**Evidence**: Has Overview, Prerequisites, Steps (numbered), and Bước tiếp theo. Follows Pattern D mandatory sections.

### 3. Active voice with "bạn" (2/2)
**Evidence**: Consistent imperative throughout: `Chọn`, `Nhấn`, `Điền`. No passive voice detected.

### 4. Visual support (1/2)
**Evidence**: 2 screenshots present, alt text correct. **Issue**: Missing screenshot for verification step (Step 5).
**Fix**: Add screenshot of success state after Step 5, alt text `![Instance list showing newly created my-vm with status Running]`

## Group B: Practical (Thực dụng) — 5/6

### 5. WHY before HOW (2/2)
**Evidence**: Section 2 leads with `Điều này giúp giảm thời gian khôi phục từ vài giờ xuống vài phút.`

### 6. Next-action guidance (1/2)
**Evidence**: Has `Bước tiếp theo` section. **Issue**: Only 1 follow-up link; could add link to monitoring setup.
**Fix**: Add 1-2 more relevant next steps (e.g., `Cấu hình monitoring cho instance`, `Thiết lập auto-scaling`).

### 7. Value/risk callouts (2/2)
**Evidence**: 1 ⚠️ Warning callout for delete action consequences. Well-placed.

## Group C: Consistent (Nhất quán) — 6/6

### 8. Terminology & capitalization (2/2)
**Evidence**: `Instance`, `VPC`, `Security Group` correctly capitalized in EN. Actions in VN.

### 9. Punctuation & formatting (2/2)
**Evidence**: All steps end with period, bullets consistent, headings sentence case.

### 10. Links & references (2/2)
**Evidence**: All 3 internal links use relative paths, anchors verified working.

---

## Anti-AI-tells checklist

- [x] No ✅ ❌ emoji outside callouts
- [x] No `...đặc biệt khi X mở rộng qua Y` intro formula
- [x] Em-dashes ≤1 per paragraph (max found: 1)
- [x] `Bước tiếp theo` not rigidly 3 items (has 2 items)
- [x] Verification step used where needed, not rigidly everywhere
- [x] Parallel structure varies naturally

**Result**: 0/6 violations — Pass.

---

## Summary

- **Score**: 18/20 (Excellent tier)
- **Deploy ready**: Yes
- **Suggested improvements** (optional):
  - Add screenshot for Step 5 verification
  - Expand `Bước tiếp theo` with 1-2 more related tasks
```

## Group A: Clear criteria

### 1. Context-setting intro

**Description**: Opening 1-2 sentences explain what feature/article solves and value to reader.

**Scoring**:
- **2 pts**: Opening answers "feature giúp gì" before jumping to steps. Format: `[Tính năng] giúp bạn [kết quả]`.
- **1 pt**: Has intro but vague OR describes system not user benefit.
- **0 pts**: No intro, jumps straight to steps OR copy of system description.

**Fix**: Rewrite intro as `[Tính năng] giúp bạn [kết quả]` + brief impact example.

### 2. Standard guide structure

**Description**: Has Prerequisites (if needed), clear headings, numbered steps, 1 action per step.

**Scoring**:
- **2 pts**: Clear subsections (Overview, Prerequisites, Steps) per Pattern D mandatory list.
- **1 pt**: Some sections present, some missing OR multiple actions in one step.
- **0 pts**: Wall of text, no clear structure.

**Fix**: Split steps, add Pattern D mandatory headings, convert long prose to numbered lists.

### 3. Active voice with "bạn"

**Description**: Written in active voice, second-person, no passive/`vui lòng`.

**Scoring**:
- **2 pts**: `Bạn chọn`, `Nhấn`, `Bật`; no `được thực hiện`.
- **1 pt**: Mostly active but few passive sentences slipped in.
- **0 pts**: Heavy passive voice OR third-person OR excessive `vui lòng`.

**Fix**: Convert to active voice, replace `vui lòng` with direct imperative.

### 4. Visual support

**Description**: Screenshots/callouts used when they aid understanding; alt text correct.

**Scoring**:
- **2 pts**: Screenshots match current UI, callouts for tips/warnings present, alt text descriptive.
- **1 pt**: Has visuals but some not relevant OR alt text missing/weak.
- **0 pts**: No visuals where needed OR misleading visuals.

**Fix**: Replace with current UI screenshots, add alt text + callouts.

## Group B: Practical criteria

### 5. WHY before HOW

**Description**: Each important section explains why action is needed, links to business value.

**Scoring**:
- **2 pts**: Lead sentence states benefit (cost reduction, security) before steps.
- **1 pt**: Some sections have WHY, others jump to HOW.
- **0 pts**: Only describes actions, no rationale.

**Fix**: Add `Điều này giúp bạn...` or cite SLA/cost impact.

### 6. Next-action guidance

**Description**: Doc guides reader to next steps (related tasks, clear CTAs).

**Scoring**:
- **2 pts**: Has `Tiếp theo`/`Xem thêm` linking to 2-4 related tasks.
- **1 pt**: Has links but unclear or too few.
- **0 pts**: Abrupt end, no follow-up guidance.

**Fix**: Add related docs links or post-completion checklist.

### 7. Value/risk callouts

**Description**: Uses Note/Warning/Info for optimization tips, downtime warnings, limits.

**Scoring**:
- **2 pts**: At least one callout for noteworthy info, correctly typed (💡 📝 ⚠️ 🚨).
- **1 pt**: Some callouts but missing where critical OR wrong type.
- **0 pts**: Important info in plain text, easy to miss.

**Fix**: Move critical info into callouts with standard emojis.

## Group C: Consistent criteria

### 8. Terminology & capitalization

**Description**: Tech terms in English, feature names capitalized per Voice Chart.

**Scoring**:
- **2 pts**: `Cloud Advisor`, `Security Group` correctly cased; tech terms in EN.
- **1 pt**: Mostly correct but few inconsistencies.
- **0 pts**: All translated to Vietnamese OR random casing.

**Fix**: Check Vocabulary Guide in FPT_TEMPLATES.md § Part 5, find/replace.

### 9. Punctuation & formatting

**Description**: Period at sentence end, correct bullet/number rules, sentence case headings.

**Scoring**:
- **2 pts**: Steps end with period, bullets consistent, headings sentence case.
- **1 pt**: Mix of bullet/paragraph, missing periods OR heading ALL CAPS in places.
- **0 pts**: Wildly inconsistent formatting.

**Fix**: Review markdown, run formatter/linter.

### 10. Links & references

**Description**: Internal links follow docs structure, anchors work, no dead links.

**Scoring**:
- **2 pts**: Relative links work, breadcrumbs correct, no 404s.
- **1 pt**: Most links work, some absolute/broken.
- **0 pts**: Broken links, 404 anchors.

**Fix**: Test in dev server, use Docusaurus-standard relative paths.

## Anti-AI-tells (bonus, separate from score)

Checked independently after 10 criteria. Each violation tracked separately. Does NOT affect score, but blocks deploy when projects have `compliance: fpt-user-guide`.

| # | Pattern | Detection rule |
|---|---|---|
| 1 | Emoji ✅ ❌ outside callouts | Regex `[✅❌]` in non-callout lines |
| 2 | Em-dash density | More than 1 em-dash (`—`) per paragraph |
| 3 | Fixed intro formula | Match `đặc biệt khi.*mở rộng qua` or similar |
| 4 | Perfect parallel | All bullets in section have ±10% same length |
| 5 | "Bước tiếp theo" rigid 3 items | Section header `Bước tiếp theo` followed by exactly 3 bullets/links |
| 6 | Rigid verification step | Final step `[Object] xuất hiện trong danh sách` in every procedure section |

When 1+ violations found:
- `score` command marks `anti_ai_tells_pass: false` in frontmatter
- Block list of file:line locations
- Suggest fix per pattern
- `deploy` command refuses to proceed (override: `--force-deploy`)

## Aggregate score for module

When `score` runs on a module, it produces per-doc reports AND an aggregate at `documentation/score/<module>/_summary.md`:

```markdown
# Score summary: instances

| Doc | Score | Tier | Deploy ready |
|---|---|---|---|
| overview.md | 16/20 | Good | ✓ |
| create-instance.md | 18/20 | Excellent | ✓ |
| edit-instance.md | 13/20 | Fair | ✗ Block |
| delete-instance.md | 17/20 | Good | ✓ |

**Module average**: 16.0/20
**Deploy gate**: 1 doc below threshold (14) — module BLOCKED
**Anti-AI-tells**: 0 violations across module

**Required actions**:
1. Fix edit-instance.md (see score/instances/edit-instance.md for details)
2. Re-run `/docsmith score instances`
3. When all docs ≥14 → `/docsmith deploy`
```

The module gate is per-doc, not average: even if average ≥14, any single doc below 14 blocks deploy.

## Re-run protocol

`score` is idempotent. Re-running:
- Reads current state of drafts
- Re-scores from scratch
- Overwrites previous score reports (timestamp updated)
- Archive previous: not kept automatically (use git for history)

Score reports are not committed by default (they're in `documentation/score/` which can be `.gitignore`'d if team prefers ephemeral reports).
