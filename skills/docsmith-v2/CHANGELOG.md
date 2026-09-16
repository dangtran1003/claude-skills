# Changelog — dangtran1003/docsmith-v2

All notable changes to this skill are documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/).

## [1.6.0] - 2026-05-12

FPT Cloud template compliance — first version with organization-specific compliance preset. Adds Sitemap Pattern D, 11 new verify checks (including 6 anti-AI-tells sub-checks), FPT voice chart matrix, and new `score` command with 10-criteria 20-point quality scoring.

### Why

User shared CSO-defined template definition document for FPT Cloud User Guide (7-part spec covering structure, writing rules, voice chart matrix, anti-AI-tells, content scorecard).

Decision: implement Parts 2 (Required Structure), 4 (Content Writing Rules), 5 (Voice Chart), and 7 (Content Scorecard). Skip Parts 1 (focus User Guide only), 3 (metadata governance — derivable from git), 6 (versioning — Docusaurus native).

This is MINOR (not patch) because it adds a new compliance preset and a new command (`score`). Existing projects without `compliance: fpt-user-guide` are unaffected.

### Added

- **`templates/FPT_TEMPLATES.md`** — Master authoritative source for FPT Cloud documentation standards. Covers Parts 1, 2, 4, 5, 7 of CSO template. Parts 3, 6 marked deferred.

- **`templates/SCORECARD_TEMPLATE.md`** — 10-criteria 20-point scorecard template. Per-doc reports + module summaries. Anti-AI-tells bonus checklist (6 patterns, separate from score).

- **Sitemap Pattern D — "FPT User Guide"** in `templates/SITEMAP_PATTERNS_TEMPLATE.md`:
  - Mandatory: overview, initial-setup, quick-starts, tutorials
  - Optional: samples, faqs, reference, troubleshooting
  - Strict enforcement (missing mandatory blocks deploy)

- **FPT Cloud preset in `templates/VOICE_CHART_TEMPLATE.md`**:
  - 3 Product Principles (Clear / Practical / Consistent)
  - 6 Aspects × 3 Principles matrix (18 cells)
  - Vocabulary Guide (EN tech terms, VN actions, FPT product names)
  - 5 Tone variants (Onboarding / Error / Success / Reference / Warnings)
  - Quick reference line

- **New `score` command**:
  - 10 criteria × 0-2 points (max 20)
  - 4 tiers: Poor (0-8) / Fair (9-13) / Good (14-17) / Excellent (18-20)
  - Per-doc reports at `documentation/score/<module>/<doc>.md`
  - Module summary at `documentation/score/<module>/_summary.md`
  - Deploy gate: ≥14 required when `compliance: fpt-user-guide`
  - Anti-AI-tells checklist (6 patterns) — separate from score, blocks deploy on violation
  - Flags: `<module>`, `<doc-glob>`, `--locale`, `--no-anti-ai-tells`, `--fix` (experimental)

- **`verify` extended to 22 checks** (was 11):
  - Checks 1-11 unchanged
  - Checks 12-22 activated only when `compliance: fpt-user-guide`:
    - 12: Page titles (4.1)
    - 13: Section headings (4.2)
    - 14: Introductions (4.3)
    - 15: Prerequisites (4.4)
    - 16: Procedures (4.5)
    - 17: Code examples (4.13)
    - 18: Button labels (4.7)
    - 19: UI references (4.12)
    - 20: Callouts (4.6)
    - 21: Status messages (4.8-4.9)
    - 22: Anti-AI-tells (4.15) — 6 sub-checks
  - New flags: `--fpt-only`, `--no-fpt`

- **`deploy` FPT compliance gate**:
  - Auto-runs `verify --fpt-only` + `score` before sync (when `compliance: fpt-user-guide`)
  - Blocks deploy if either fails
  - Override: `--force-deploy`

- **Project intake `compliance` field** in PROJECT_INTAKE_TEMPLATE.md § 4 advanced:
  - Default: `none` (no enforcement, backward compatible)
  - Option: `fpt-user-guide` (activates Pattern D + FPT voice + checks 12-22 + score gate)

### Changed

- **`SKILL.md` `verify` section** — documents 22 checks, new flags
- **`SKILL.md`** — adds `score` command between `verify` and `update`
- **`SKILL.md` `deploy` section** — documents FPT compliance gate + `--force-deploy`
- **`PROJECT_INTAKE_TEMPLATE.md`** — adds compliance preset advanced subsection
- **`SITEMAP_PATTERNS_TEMPLATE.md`** — adds Pattern D section
- **`VOICE_CHART_TEMPLATE.md`** — appends FPT preset (existing generic template unchanged)

### Backward compatibility

Default `compliance: none` keeps all v1.5.14 behavior. Plugin functionality identical for projects that don't opt into FPT compliance.

Existing v1.5.14 projects continue to work without modification. To opt in: edit `project.md` § 4 advanced, tick `fpt-user-guide`, re-run `plan` and `voice`.

### Limitations (v1.6.0)

- **AI scoring is heuristic** — AI evaluates each criterion via prose reasoning. Real human scoring may differ. Recommend BA review scorecard reports before trusting deploy gate.
- **Anti-AI-tells detection by regex/heuristic** — sophisticated AI patterns may slip through.
- **No automated fix mode (yet)** — `score --fix` experimental. Most fixes require human edit.
- **Only User Guide compliance** — API Reference, Deployment Guide, etc. not supported. Future versions.
- **No versioning support** (Part 6 of template) — Docusaurus has native versioning; recommend using directly.
- **No metadata governance** (Part 3) — derivable from git at deploy time but not enforced in v1.6.0.

### Migration from v1.5.14

No migration required. Default `compliance: none`. To opt into FPT:
1. Edit `project.md` § 4 advanced; tick `fpt-user-guide`
2. Re-run `/docsmith plan` (regenerates sitemap with Pattern D)
3. Re-run `/docsmith voice` (regenerates voice chart with FPT matrix)
4. Run `/docsmith verify --fpt-only` to see drafts' compliance issues
5. Run `/docsmith score <module>` to assess quality
6. Fix until all docs ≥14, no anti-AI-tells violations
7. `/docsmith deploy` (or `--force-deploy` to bypass gate)

### Testing recommendation

Largest behavior change since v1.5.0. STRONGLY recommend testing on 1 real FPT Cloud doc before relying on compliance gate for production. Compare AI scorecard judgment against human scoring on same doc.

## [1.5.14] - 2026-04-30

Templates cleanup — remove redundant template files. Pure refactor with no behavior change.

### Why

After 19 versions, templates folder accumulated overlap:
- `SCREENSHOT_POLICY_TEMPLATE.md` (108 lines) — caption rules, density, naming. 80% covered by `MEDIA_POLICY_TEMPLATE.md` (which was added in v1.5.5 specifically to consolidate media rules).
- `VIDEO_MARKER_TEMPLATE.md` (155 lines) — explained marker syntax. But marker is now just `<!-- VIDEO id: <id> -->` since v1.5.7. 155 lines for a 1-line spec is overkill. The format is now documented in `VIDEO_SCRIPT_TEMPLATE.md § VIDEO marker simplified`.
- `WALKTHROUGH_VIDEO_PLAN_TEMPLATE.md` (72 lines) — capture plan format. Already covered by SKILL.md `record` command workflow.

Three template files removed. Caption rules merged into MEDIA_POLICY § 3.5. Marker syntax retained in VIDEO_SCRIPT.

### Removed

- `templates/SCREENSHOT_POLICY_TEMPLATE.md`
- `templates/VIDEO_MARKER_TEMPLATE.md`
- `templates/WALKTHROUGH_VIDEO_PLAN_TEMPLATE.md`

### Changed

- **`templates/MEDIA_POLICY_TEMPLATE.md`** — new section 3.5 "Caption writing rules (consolidated)" containing:
  - When to include / not include screenshots
  - Rule A: state-not-action
  - Rule B: specific data and state
  - Rule C: label-not-appearance
  - Rule D: placeholder placement
  - File naming conventions
  - State that cannot be reproduced
  - Pre-walkthrough caption review
  - "When in doubt" check
  Internal references in MEDIA_POLICY updated from old template names.
- **`SKILL.md`** — `draft` command refers to `MEDIA_POLICY_TEMPLATE.md § 3.5` for caption rules and `VIDEO_SCRIPT_TEMPLATE.md § VIDEO marker` for marker syntax. `record` command refers only to `VIDEO_SCRIPT_TEMPLATE.md`.

### Templates count

- Before v1.5.14: 17 templates (16 .md + 1 .yaml)
- After v1.5.14: 14 templates (13 .md + 1 .yaml)
- Net: -3 .md files

Total spec lines reduced ~335 (caption rules retained in MEDIA_POLICY but at lower verbosity; redundant content removed entirely).

### Backward compat

- For users referencing old template paths in custom scripts: SCREENSHOT_POLICY/VIDEO_MARKER/WALKTHROUGH_VIDEO_PLAN are GONE. Update references to new locations.
- For users with existing workspaces: nothing changes. These templates were AI-internal references; users never directly consumed them.
- For CHANGELOG history: kept references to old template names in v1.1.0-1.5.13 entries (historically accurate).

### Why this is a patch (not minor)

Pure refactor. No new commands, no new behavior, no schema changes. Plugin functionality identical to 1.5.13.

### Migration

None needed for users with workspaces. Custom scripts referencing deleted template paths must update to new locations.

## [1.5.13] - 2026-04-30

Interactive fill protocol — pipeline stages now prompt user inline when intake fields are empty, write answers back, continue. No upfront 354-line form fill required.

### Why

User raised: "Tôi nghĩ là ở bước init hay module, nếu có from-source thì sẽ đánh dấu là có file intake, sử dụng chạy luồng như .11; còn không có thì sẽ vẫn gen ra file intake, nhưng sẽ đánh dấu đầu file là module đó, là manual, rồi launch từng bước như follow ban đầu, và qua mỗi bước tự fill vào file intake — chứ không phải người điền."

Original proposal: mode marker + conditional behavior per command. Analysis showed simpler approach achieves same UX outcome: detect empty critical fields per stage, prompt user, write back. No marker needed.

This patch implements that simpler approach.

### Added

- **Interactive fill behavior** for all stage commands (`audience`, `plan`, `voice`, `draft`, `edit`, `walkthrough`, `record`, `translate`):
  - Stage checks its required fields
  - If empty AND critical → prompt user inline
  - If empty AND has safe default → use default silently
  - If empty AND optional → skip
  - Answer written back to intake (preserves markdown structure, hint comments untouched)
  - Stage continues
- **`--no-prompt` flag** on all stage commands — fail immediately if required field empty (old behavior). Useful for CI scripts.
- **`intake-reference.md` § 10** "Interactive fill protocol" with:
  - Activation rules (when prompts fire)
  - Per-stage required field tables (audience, plan, voice, draft, edit, walkthrough, record, translate)
  - Concrete prompt examples for each stage
  - Write-back format (idempotent, preserves structure)
  - Mixed flow scenarios (auto-fill + interactive)
  - Validation order (critical → safe defaults → silent fallback)
  - 4 limitations called out

### Changed

- **`SKILL.md` stage commands** — added "Interactive fill (v1.5.13+)" note to:
  - audience/plan/voice/draft/edit (merged section)
  - walkthrough
  - record
  - translate
- **Stage commands document `--no-prompt` flag** uniformly
- **`README.md` step-by-step alternative section** — refreshed to highlight 2 ways to drive intake:
  - Pre-fill mode (traditional)
  - Interactive mode (v1.5.13+)
  - Workflow example shows which prompts fire when
  - `--no-prompt` flag mentioned
- **README requirements simplified**: only `project.md` and `modules/<n>.md` need to EXIST (created by `init` and `module` commands). Filling them is optional with interactive fill.

### Per-stage required fields

| Stage | Critical fields prompt-able |
|---|---|
| `audience` | Primary persona role, technical level, primary goal |
| `plan` | (none — feature definition enforced by `module` command) |
| `voice` | (none — all fields have safe defaults) |
| `draft` | Sources confirmation (or "no sources" explicit) |
| `edit` | (none — operates on existing drafts) |
| `walkthrough` | Product URL, credentials env var names |
| `record` | TTS provider + voice IDs (only if AI voiceover) |
| `translate` | Target languages |

Most stages don't trigger prompts because either:
- Defaults are safe (voice, sitemap, media policy)
- Earlier stages enforce dependencies (`module` enforces features for `plan` and `draft`)

### How it works

Behavior is detect-and-ask, not mode-flag:

1. AI runs stage command
2. AI reads intake (project + module + defaults via layered config)
3. AI checks ITS required fields (per-stage table)
4. If any empty AND critical → prompt user with concrete question
5. User answers; AI writes to correct intake file at correct location
6. AI re-validates; if all critical fields now present → continue stage

No mode marker. No "manual" vs "auto" distinction. Each stage checks what it needs, asks if missing.

### Mixed flow example

```bash
# User runs init without source
/docsmith init
/docsmith module myproduct

# project.md and modules/myproduct.md exist but mostly empty
# User runs first stage:
/docsmith audience myproduct
# AI prompts: role? tech level? goal?
# User answers; AI writes to project.md § 2

/docsmith plan myproduct
# No prompts (audience already populated, sitemap pattern defaults to A)

/docsmith draft myproduct
# AI: "No sources defined. Continue draft from intake info only? Y/n"
# User: y
# AI marks "no external sources" in project.md § 6, drafts

/docsmith walkthrough myproduct
# AI prompts: product URL? credentials env vars?
# User answers; AI writes to project.md § 1, § 5
# AI verifies env vars set in shell; reports if missing
```

Each stage minimal Q&A, distributed across pipeline. User never sees 354-line form.

### Backward compatibility

For users who DID pre-fill intake (workflow before v1.5.13):
- AI sees fields filled
- Skips prompts
- Behavior identical to v1.5.12

For users who run with `--no-prompt`:
- Same behavior as v1.5.12 (fail-fast on missing field)
- For CI / scripts

For users using `init --from-source`:
- AI auto-fills 80% of fields
- Stage prompts only fire for uncovered critical fields (deploy target, credentials)
- Same as v1.5.9-1.5.12

### Limitations (v1.5.13)

- **No partial answer recovery** — if user aborts mid-prompt, stage exits. Re-run remembers answered fields.
- **No prompt for module-specific fields in project-level stages** (`voice` is project-level)
- **No semantic validation** of free-text answers
- **Order-sensitive** — running `draft` before `audience` prompts more (would re-ask audience info)

### Migration from v1.5.12

For new projects: just use v1.5.13. New behavior is additive.

For existing v1.5.12 projects: works identically. If intake fields were already filled, no prompts will fire. Interactive fill only activates for NEW empty fields.

### Why this is a patch (not minor)

No new commands. No schema changes. New behavior on existing commands (interactive prompts when fields empty). Behavior is additive: previously stages would fail on missing critical field; now they prompt. With `--no-prompt`, behavior identical to before.

Plugin functionality identical to 1.5.12 for users with filled intakes OR users who use `--no-prompt`.

## [1.5.12] - 2026-04-29

Documentation patch — explicit "step-by-step alternative" section in README for users who prefer running each pipeline stage manually instead of using `run` to auto-chain.

### Why

User raised: "Tôi đã hướng dẫn user chạy theo version đầu tiên, đi từng bước 1; user vẫn muốn chạy theo cách đó được không?"

Answer: yes, every individual stage command (`audience`, `plan`, `voice`, `draft`, `edit`, `walkthrough`, `record`, `translate`, `verify`, `deploy`) still works in v1.5.x. The `run` command is just an orchestrator on top of these.

But the README and HOW_IT_WORKS guides positioned `run` as the primary workflow. Step-by-step path was implicit, not documented. Users coming from v1.4.x or earlier tutorials might not realize the granular flow is supported.

This patch adds an explicit subsection making the step-by-step flow first-class.

### Changed

- **`README.md`** — added "Step-by-step alternative (granular control)" subsection in Quick start. Covers:
  - Full sequence of individual commands (10 stages) with inline output paths
  - 2 requirements before running any stage (`project.md` filled, module created)
  - Comparison table: step-by-step vs `run` orchestration
  - Note that both flows produce identical artifacts

### Unchanged

- All commands behave identically — no code/spec change to any individual command
- `run` workflow unchanged (still default for new users via Quick start)
- HOW_IT_WORKS already documented step-by-step in cheat-sheet section
- INTAKE_GUIDE already covers minimum-fill checklist

### Why this is a patch (not minor)

Pure documentation. No new commands, behavior, schema, templates, or flags. Plugin functionality identical to 1.5.11.

### Migration

None needed. Existing users continue to work either way.

## [1.5.11] - 2026-04-29

Documentation refresh — sync top-level guides with v1.5.10.

### Why

After v1.5.10 added `update --from-source` module diff, parallel sub-agent guidance, and `--resume` flag, the top-level guides (HOW_IT_WORKS, COMPARISON) were stale:

- HOW_IT_WORKS still showed v1.4.0-era pipeline (`.docsmithrc.yaml`, no source-driven intake, no script files)
- COMPARISON compared v1.1 vs v1.5.1 (8 versions out of date)
- PUBLISHING used v1.5.2 examples in version-bump instructions

This patch refreshes top-level docs to match SKILL.md and the templates.

### Changed

- **`HOW_IT_WORKS.md`** — full rewrite for v1.5.10:
  - 12 sections covering: 2-layer config model, 20 commands, init workflow, intake forms (manual + `--from-source`), full pipeline diagram, deploy, update with 3-layer change report, multi-locale, re-run protocol, mental model, daily cheat-sheet, troubleshooting
  - Replaced `.docsmithrc.yaml` references with markdown intake form descriptions
  - Added `--from-source` AI auto-fill workflow
  - Added video script files (v1.5.7+) in record stage
  - Added 11 troubleshooting rows (was 6 in v1.4)
  - Added `--resume` flag mention
- **`HOW_IT_WORKS.vi.md`** — full Vietnamese translation, mirrors English structure
- **`COMPARISON.md`** — refresh to compare v1.1.0 vs v1.5.10:
  - 5-phase chronological breakdown (initial → hardening → big refactor → UX polish → source-driven intake)
  - Updated stats table (41 files, 9000 spec lines, etc.)
  - Honest weaknesses list including "Real-world tested: never (16 versions, 0 production runs)"
  - Self-assessment of methodology (user-driven ✓, untested ❌)
  - "What I'd do differently if starting over" reflection
- **`COMPARISON.vi.md`** — full Vietnamese translation
- **`PUBLISHING.md`** — version examples updated to v1.5.10 (was v1.5.2)
- **`README.md`** — current version bumped to 1.5.11

### Unchanged

- `INTAKE_GUIDE.md` / `.vi.md` — already refreshed in v1.5.8 + v1.5.9 + v1.5.10 patterns
- `SETUP.md` / `.vi.md` — version-agnostic prerequisites guide
- `CHANGELOG.md` — append-only
- All template files — already reflect current behavior
- All reference docs (`intake-reference.md`, etc.) — already current

### Why this is a patch (not minor)

Pure documentation. No new commands, no behavior changes, no schema changes, no new templates. Plugin functionality identical to 1.5.10.

### Migration

None needed.

## [1.5.10] - 2026-04-29

Multi-module operations — detect new/orphan modules in `update`, document parallel processing as MAY (not MUST).

### Why

User raised: with 30 modules at init time and 5 modules/week update cadence, two needs:

1. **Missing module detection in update** — when BA doc has 7 modules but workspace only has 4, AI should surface the gap and offer to create the missing intakes
2. **Multi-agent parallel processing** — for first-time init with 30 modules, sequential is slow

For (1): real pain, clear solution. Implemented as feature.

For (2): user described as "conceptual" — wanted parallel for future-proofing, not from felt pain. Implemented as documentation guidance ("AI MAY use Task tool when >5 modules") rather than mandatory parallel orchestration. Avoids over-promising performance the runtime may not deliver.

### Added

- **Module diff in `update`** — `update` (without flags) now also detects:
  - **New modules in source** not yet in workspace
  - **Orphan modules in workspace** no longer in source
  - **Scope drift** — features in source vs features in module intake
- **Interactive prompt for module diff** with 5 actions (create new / archive orphan / update scope / show diff only / skip)
- **`update --from-source <path>`** — re-register source URL/path (overrides sources.lock entry)
- **`update --no-modules`** — content drift only; skip module structure detection (faster for daily use)
- **`update --resume`** and **`init --from-source --resume`** — retry previously failed parallel sub-agents (when last run reported partial completion)
- **Update inference report** at `documentation/intake/.inference/<ts>-update.md` — same format as init inference report, scoped to update operation
- **Parallel sub-agent guidance (Cấp 1)** in `intake-reference.md` § 9.9:
  - Threshold >5 modules
  - "MAY use Task tool" — not mandatory; runtime decides actual parallelism
  - Sequential fallback always valid
  - Error handling: failed sub-agent retried sequentially; if fails again → partial completion + `--resume` instructions
  - Cost note: ~2× tokens for ~3× speed
  - Benchmark guidance (rough estimates)
- **Missing module detection (B)** documented in `intake-reference.md` § 9.10:
  - 3-bucket categorization logic
  - Interactive prompt format
  - Re-run safety with hash protection
  - Heuristic limitation flagged

### Changed

- **`update` command in SKILL.md** — workflow expanded to 7 steps (was 5); 3-layer change report (content drift + module diff + scope drift); inference report generation
- **`init` command in SKILL.md** — added `--resume` flag for parallel partial-completion retry
- **INTAKE_GUIDE en/vi** — added pattern "Source has new modules I didn't document yet" / "Source có module mới chưa documented"

### Behavior nuances

**Parallel is opportunistic, not guaranteed**:

The skill spec uses "MAY" deliberately. Spawning sub-agents requires runtime support. If Claude runtime can't truly parallelize, sequential interleaving still works — just no speedup. User-facing outcome identical.

**Threshold avoids overhead for small projects**:

≤5 modules: sequential. Spawn overhead > sequential time.
>5 modules: parallel attempted. Worth coordination cost.

**Error handling preserves work**:

If 4 of 5 sub-agents complete and 1 fails:
- 4 module intakes written successfully
- 1 module reported as failed
- User can `--resume` to retry just the failed one
- Re-run protocol prevents accidentally redoing successful ones

**Orphan detection is heuristic**:

If source restructured (renamed sections, merged modules), AI may flag valid modules as orphan. Interactive prompt always shows reasoning; user decides.

### Limitations (v1.5.10)

- **Parallel performance not guaranteed** — depends on Claude runtime
- **No `--max-concurrent N` flag** — threshold and concurrency hardcoded; defer to v1.6+ if usage shows need
- **Update inference report format same as init** — could differ (update should highlight diffs more prominently); defer minor templating
- **Scope drift detection is feature-list level** — doesn't detect changes in feature description quality. AI compares feature names, not semantics
- **Orphan detection conservative** — won't auto-archive; always asks user

### Migration from v1.5.9

For new projects: just use v1.5.10. New behavior is additive.

For existing v1.5.9 projects: nothing to migrate. Run `/docsmith update` next time you check sources — will surface module diffs if any exist.

### Why this is a patch (not minor)

No new commands. New flags only (`--from-source`, `--no-modules`, `--resume` on update; `--resume` on init). Existing `update` workflow extended, not replaced. Plugin functionality identical to 1.5.9 for users with tightly synced sources (no module gap detected → no new behavior surfaced).

## [1.5.9] - 2026-04-29

AI auto-fill intake from source documents. BAs no longer have to type intake fields manually when they already have a BA doc / PRD.

### Why

User raised: "Việc điền intake này có require không, AI có thể tự điền và tôi review từ các nguồn khác (BA doc, doc hiện tại)."

Realistic answer: the intake form was the ONLY way to configure docsmith, requiring BAs to manually transfer info from their existing BA doc into a 354-line form. This is duplicate work — the BA already wrote a doc explaining the product.

v1.5.9 adds source-driven auto-fill: AI reads BA doc, infers fields, asks BA only for what source can't cover. Intake form remains source of truth (single audit trail), but BA reviews instead of types.

### Added

- **`/docsmith init --from-source <path-or-url>`** — AI auto-fills `project.md` from external source(s)
- **`/docsmith module <n> --from-source <path-or-url>`** — AI auto-fills module intake from source, scoped to one module
- **Inference confidence model** — every field marked one of:
  - `Fact` (no marker — direct quote from source)
  - `← AI guess, please verify` (inferred from context, BA should review)
  - `← default applied` (no source data, conservative fallback)
  - `Asked` (BA answered during interactive Q&A)
- **Interactive Q&A flow** — after parsing source, AI asks 5-10 questions for fields source can't cover:
  - Source language (confirm detection)
  - Target languages
  - Deploy preset and target path
  - Walkthrough credentials env var names (if walkthrough used)
  - Voiceover strategy (if videos planned)
  - Pause gate preference for first run
- **Module detection** from source structure (sections, headings) with user confirmation
- **`templates/INTAKE_INFERENCE_REPORT_TEMPLATE.md`** — transparency report format:
  - Frontmatter with metadata + confidence summary
  - "Facts" table with field, value, source line, exact quote
  - "Guesses" table with reasoning per guess
  - "Defaults applied" with why each default
  - "Asked user" with Q&A log
  - "Open items" (still need user input)
  - "Sources used" appendix
  - Saved at `documentation/intake/.inference/<timestamp>-<scope>.md` (audit retained)
- **Re-run safety with `--from-source`** — per-field hash check:
  - Hash matches → BA didn't edit; safe to re-infer if source data changed
  - Hash differs → BA edited manually; preserve current value
  - Diff shown before applying; re-run protocol gate (Update / Overwrite / Skip)

### Changed

- **`init` command** — adds `--from-source` flag; existing flags unchanged
- **`module` command** — adds `--from-source` flag for module-scoped auto-fill
- **`intake-reference.md`** — new § 9 "Source-driven intake auto-fill" with:
  - When to use / when not to use
  - Inference confidence model explained
  - Per-field inference logic (product, audience, languages, deploy, voice, credentials, sources, modules)
  - Interactive Q&A flow with sample dialog
  - Inference report format reference
  - Re-run with `--from-source` and hash storage
  - 5 limitations called out
  - Full session example
- **README Quick start** — step 3 and 4 now mention `--from-source` as alternative
- **README current version** — bumped to 1.5.9
- **INTAKE_GUIDE en/vi** — added 2 new patterns:
  - "I have a BA doc / PRD already; don't want to re-type info"
  - "BA doc updated; want to refresh intake"

### Inference logic highlights

| Field | Inference approach |
|---|---|
| `product.slug` / `display_name` | Slugify / extract from source heading |
| `product.url` | Regex search for product URL (filter out github/notion/etc) |
| `audience.tech_level` | Heuristic: CLI/API mentions → High; "non-technical" → Low; else Medium |
| `audience.primary_goal` | Pattern match "users want to...", "the goal is..." — always marked guess |
| `voice.tone` | Detect contractions/exclamations (casual) vs technical jargon (technical-direct) |
| `voice.perspective` | Count dominant pronoun ("you" / "we" / "the user") |
| `locales.source` | Script analysis (Vietnamese diacritics → vi, etc.) — always confirms with user |
| `locales.targets` | Always asked — translation strategy is project decision |
| `deploy.*` | Always asked — environment-specific |
| `credentials.*` | Always asked — environment-specific |
| `sitemap.pattern` | Default Pattern A unless source explicitly specifies different structure |
| `media.*` | Always default — source rarely mentions |
| Module detection | Top-level sections in source → candidate modules; user confirms |

### Limitations (v1.5.9)

- **Heuristic detection** — AI labels uncertain fields as "guess" but heuristics are imperfect. BAs should review every "← AI guess" marker.
- **No deep code analysis** — source as GitHub repo: AI reads README and structure, not every function
- **No semantic merge on re-run** — uses field-level hash. BA reformatting (whitespace, reorder) breaks hash and may prevent re-inference even when content unchanged
- **No multi-source merge precedence** — passing 3 sources merges them as 3 inputs but AI may pick fields from one source over another with no user control. Defer to v1.6+
- **Conservative defaults override source hints** — AI defaults to safest choice even when source hints at other strategies (e.g., source mentions "video tutorials" but media.voiceover defaults to silent). User overrides during Q&A or after.

### Migration from v1.5.8

For new projects: just use v1.5.9. Use `--from-source` if you have BA doc, omit if you'll fill manually.

For existing projects: nothing to migrate. v1.5.8 intake files still work. Adding `--from-source` to existing projects:
- Re-runs `init --from-source` on existing workspace
- Per-field hash check preserves your manual edits
- Diff shown before applying
- Inference report logged

### Why this is a patch (not minor)

1 new template (INTAKE_INFERENCE_REPORT), 2 modified commands (added flags), 1 new reference section. No new commands. No schema-breaking changes. Existing workflow (manual intake fill) unchanged. `--from-source` is fully opt-in.

For users who don't use `--from-source`, plugin functionality identical to 1.5.8.

## [1.5.8] - 2026-04-29

Documentation refresh — inline hints in intake templates, concise guides for v1.5.7.

### Why

After 7 minor patches accumulating features (sitemap consistency, media policy, video scripts), the docs were stale and bloated:
- README still described v1.5.0 quickstart
- INTAKE_GUIDE was 516 lines duplicating template explanations
- Templates required users to flip back and forth between template and guide
- v1.5.7 video scripts feature wasn't reflected in user-facing guides

Solution: put hints WHERE users need them (in templates), keep guides concise for context/decisions only.

### Changed

- **`templates/PROJECT_INTAKE_TEMPLATE.md`** — every field now has an inline `>` hint immediately below it explaining:
  - What to put (with examples)
  - When to skip
  - How AI uses the value
  - Common values for the field
  - Header at top: minimum-fill instructions for first project
- **`templates/MODULE_INTAKE_TEMPLATE.md`** — same inline-hint treatment. BA can fill module without consulting external guide.
- **`README.md`** — refreshed for v1.5.7:
  - Quick start uses current command flow (`init` → `module` → fill → `run` → `continue` → `deploy`)
  - "All commands at a glance" table (20 commands)
  - "Key concepts" section explains layered config, re-run safety, drift detection, source change detection, multi-locale, sitemap consistency, media policy, video scripts
  - "What gets generated" section shows full output tree
  - "Documentation map" routes users to right doc by question
  - File structure reflects plugin marketplace layout
- **`INTAKE_GUIDE.md`** — rewritten as decision/context guide, not field reference (templates do that now):
  - Three editing rules
  - Minimum-fill checklist
  - 7 common patterns with concrete commands
  - Decision matrix tables for voiceover, screenshots, TTS provider
  - "AI uses each field for..." reference table
  - Mistake recovery table
  - When to expand Advanced sections
  - 7 tips for first-time success
  - Reduced from 516 lines to 258 lines (-50%)
- **`INTAKE_GUIDE.vi.md`** — full Vietnamese translation, same structure

### Benefits

For BAs filling intake first time:
- Open template → every field has explanation right there
- Don't need to flip to INTAKE_GUIDE
- INTAKE_GUIDE only consulted for decisions ("which voiceover strategy?")

For experienced users:
- Quick refresher in README "All commands at a glance"
- Decision matrices in INTAKE_GUIDE for second-project tweaks
- Reference docs (in skills/docsmith/) unchanged for deep technical lookups

For maintainers (you):
- Templates are self-documenting
- When you add a new field, just add a `>` hint inline
- Guide doesn't accumulate field descriptions over time

### What didn't change

- SETUP.md — already covered v1.5.5 TTS providers and v1.5.7 setup; unchanged
- HOW_IT_WORKS.md — last updated v1.4.0 multi-locale; could use refresh but lower priority
- Reference docs (intake-reference, deploy-reference, translate-reference, etc.) — technical detail, unchanged
- Plugin schema — same
- Commands — same (no new flags or behaviors)

### Migration from v1.5.7

For new projects: `init` scaffolds the new self-explaining templates.

For existing projects with old templates:
- Old templates still parse correctly (inline hints are markdown blockquotes, ignored by parser)
- To upgrade existing intake files in place:
  ```bash
  /docsmith init --reformat-intake
  ```
  Re-renders project.md and modules/*.md with v1.5.8 inline hints. Your filled values preserved. Backup at `documentation/intake/.backup-pre-v1.5.8/`.

### Why this is a patch (not minor)

Pure documentation. No new commands, no new fields, no new templates, no schema changes. Plugin functionality identical to 1.5.7.

## [1.5.7] - 2026-04-29

Per-video script files. Voiceover content lives in dedicated script files instead of inline VIDEO marker comments.

### Why

After v1.5.5 added voiceover/TTS, the question "where do scripts live?" was unresolved. Inline scripts in VIDEO markers (the implicit assumption) had problems:
- Bloated drafts (VIDEO marker with 40-line script comment)
- Hard to translate scripts independently of prose
- Multi-locale scripts had no clear home

v1.5.7 externalizes scripts to per-video files at `documentation/scripts/<module>/<id>.md`.

### Added

- **`templates/VIDEO_SCRIPT_TEMPLATE.md`** — definitive format for per-video script files:
  - Frontmatter: id, module, asset_path, duration_target, voiceover_strategy, voiceover_provider, source_locale, generation timestamp
  - `# Source script (<lang>)` section: BA-edited source-language script
  - `## <locale>` sections: per-locale translations (auto-managed by translate command)
  - `# Notes` section: internal notes, NOT voiced, NOT translated
  - Workflow integration with `record` and `translate` commands
  - Multi-locale strategy mapping (silent, AI per-locale, source+sub, human)
  - Path mapping table for source script + audio files + subtitles
- **`/docsmith record --check`** flag — validate script files exist for all VIDEO markers
- **`/docsmith record --re-record <id>`** flag — force re-record one video
- **`/docsmith record --migrate-scripts`** flag — extract inline scripts from old VIDEO markers, create new script files, simplify markers

### Changed

- **VIDEO marker simplified to** `<!-- VIDEO id: <id> -->` only. All other config moved to script file frontmatter.
- **Old expanded VIDEO marker syntax** still parsed by `record` for backward compatibility with v1.5.4-1.5.6 drafts. New drafts use simplified marker.
- **`record` command workflow updated**:
  1. Scan drafts for VIDEO markers
  2. Look up script file at `documentation/scripts/<module>/<id>.md`
  3. If missing → AI generates initial script from surrounding draft prose, pauses for user review
  4. If exists but stale → warn user
  5. User reviews/edits
  6. TTS generates audio per locale (skipped if silent), capture screen, encode video
- **`translate` command extended** to process script files alongside drafts. Translates `# Source script` content into `## <locale>` sections. Same per-block / batch review gate. Same glossary.
- **VIDEO_MARKER_TEMPLATE.md** — added v1.5.7+ note at top about marker simplification
- **MEDIA_POLICY_TEMPLATE § 5** — added reference to script files as voiceover content source
- **translate-reference.md § 1** — clarifies what gets translated (drafts AND scripts)
- **intake-reference.md path mapping table** — added rows for script file, voiceover audio, subtitle paths
- **SKILL.md `record` command section** — full workflow update
- **SKILL.md File organization** — adds `documentation/scripts/<module>/` directory
- **INTAKE_GUIDE en/vi § 11** — added script file note in Videos section

### Migration from v1.5.6

For new projects: just use v1.5.7. `record` creates script files automatically when needed.

For existing v1.5.6 workspaces with inline scripts in VIDEO markers:
```bash
/docsmith record --migrate-scripts
```

This:
1. Scans drafts for inline-script VIDEO markers
2. Creates `documentation/scripts/<module>/<id>.md` files from inline content
3. Updates draft VIDEO markers to short form `<!-- VIDEO id: <id> -->`
4. Backs up old drafts to `documentation/archive/<ts>/`

For drafts without VIDEO markers: nothing to migrate.

### Limitations (v1.5.7)

- **No automatic script re-write** when draft prose changes — user manually updates scripts. v1.6+ may add change detection with diff suggestions.
- **No SSML support** — TTS providers that support SSML (pause, emphasis, prosody) accept full markdown but ignore SSML tags. Adding SSML passthrough is roadmap.
- **No multiple voices per script** — entire script uses one voice per locale. Dialog-style scripts not supported.
- **No audio mixing** — voiceover only, no background music or SFX in `record`. User can post-process video manually.

### Why this is a patch (not minor)

1 new template, 5 modified templates/references, 3 new flags on `record`. No new commands. No schema-breaking changes for new projects. Old VIDEO marker format still parses for backward compat. Plugin functionality identical to 1.5.6 for users who don't use video.

## [1.5.6] - 2026-04-29

Smart defaults UX patch — collapse advanced sections by default in intake forms. Same fields, same parsing logic, just less visual noise for BAs.

### Why

After v1.5.5, intake templates accumulated to 356 lines (project) + 245 lines (module) with 71 + 41 checkboxes. BAs filling first project felt overwhelmed. They didn't need to see TTS provider list, sitemap pattern selection, or 6 other Advanced fields when defaults work for 80% of cases.

Solution: wrap Advanced sections in HTML `<details>` blocks. GitHub/VS Code/Cursor render these as collapsed clickable headers. BA sees ~80 lines top-level (essentials only). Power user clicks to expand and customize.

No new fields, no new logic, no new commands. Pure UX.

### Changed

- **`PROJECT_INTAKE_TEMPLATE.md`** — wrapped 7 Advanced sections in `<details>` blocks:
  - Secondary personas (under § 2 Audience)
  - Glossary settings (under § 3 Languages)
  - Collision behavior (under § 4 Deploy)
  - Voice and tone (separated from § 4)
  - MFA / SSO (under § 5 Credentials)
  - Additional sources (under § 6 Knowledge sources)
  - Auto-run behavior, Sitemap pattern, Media policy (whole top-level sections)
- **`MODULE_INTAKE_TEMPLATE.md`** — wrapped 7 Advanced sections in `<details>` blocks:
  - Add more features (under § 2 Scope)
  - Out of scope, Module priority (under § 2)
  - Voice override
  - Module-specific sources
  - Walkthrough setup
  - Special handling (sensitive fields, status)
  - Sitemap sections, Media override
- **`intake-reference.md` § 1** — added subsection explaining `<details>` parsing rule (AI strips wrapper, parses content, treats collapsed defaults as canonical)
- **`INTAKE_GUIDE.md` and `.vi.md`** — added "Rule 4: Skip Advanced sections" with explicit minimum-fill checklist for first project (only § 1, 2, 3, 4, 5, 6 essentials)

### Default tick state

All Advanced sections have defaults pre-ticked. Examples:

```markdown
<details>
<summary><b>Advanced — voice and tone</b> (using defaults)</summary>

Tone:
- [ ] Casual
- [x] Friendly-professional (default)
- [ ] Technical-direct
- [ ] Formal

</details>
```

When BA leaves Advanced section collapsed, AI uses ticked default. When BA expands and changes a tick, AI uses new value. Same parsing, no special-case logic.

### Visual impact

Before v1.5.6 in default GitHub render:
- Project intake: ~356 lines all visible. BA scrolls through every section.
- Module intake: ~245 lines all visible.

After v1.5.6:
- Project intake: ~80 lines essentials visible. 7 collapsed `<details>` headers indicate Advanced sections.
- Module intake: ~50 lines essentials visible. 7 collapsed `<details>` headers.

Total file size barely changed (354 / 242 lines now). Perceived complexity dropped ~75%.

### Editor compatibility

| Editor | Renders `<details>` collapsed? |
|---|---|
| GitHub web preview | ✅ Yes |
| VS Code markdown preview | ✅ Yes |
| Cursor | ✅ Yes |
| GitHub.dev | ✅ Yes |
| Plain text editor | ❌ Shows raw markup (still readable) |

For editors that don't render `<details>`, BA sees `<details>` and `<summary>` tags as plain text. Not ideal but parseable. AI still parses correctly regardless of editor rendering.

### Migration from v1.5.5

For new projects: just use v1.5.6. New init scaffolds collapsed templates.

For existing v1.5.5 workspaces:
- Existing intake files keep flat structure — no `<details>` wrapping
- AI parser still works (it ignores `<details>` whether present or not)
- To convert existing intake to collapsed form, run `/docsmith init --reformat-intake`
  - Re-renders project.md / modules/*.md with `<details>` wrappers
  - User content (filled values, ticked checkboxes) preserved
  - Backup at `documentation/intake/.backup-pre-v1.5.6/`

OR just leave existing intakes as-is. Both render correctly; only new projects benefit from collapsed default.

### Why this is a patch (not minor)

No schema changes, no new fields, no new commands, no new templates. Pure markup change to existing templates. Plugin functionality identical to 1.5.5.

## [1.5.5] - 2026-04-28

Comprehensive media policy — screenshot density rules, per-locale strategy, video voiceover/TTS configuration, subtitle generation.

### Why

User raised real gap: docsmith had screenshot caption rules and video markers but no policy for:
- How many screenshots per content type (density)
- Style options (viewport, full window, cropped, annotated)
- Aspect ratio (desktop, mobile, square)
- Per-locale screenshot strategy (1 EN ảnh dùng chung hay capture riêng cho VI/JP?)
- Video density per content type
- Voiceover language strategy (silent? AI per locale? human?)
- TTS provider abstraction
- Subtitle generation method

These decisions affect cost/effort by 3-10× depending on choice. Can't be inferred — must be explicit project decision.

### Added

- **`templates/MEDIA_POLICY_TEMPLATE.md`** — definitive reference covering:
  - Screenshot density per content type (Tutorial=1/step, How-to=1/heading, etc.)
  - 4 screenshot styles (viewport-only, full-window, cropped-element, annotated)
  - 5 aspect ratios (16:9 desktop default, 4:3, mobile, square, custom)
  - 3 per-locale strategies (source-only default, per-locale, hybrid)
  - Video density rules with length caps per content type (Tutorial ≤90s, How-to ≤30s, etc.)
  - 5 voiceover strategies (silent default, AI per locale, source+sub, human, none)
  - 6 TTS providers with config schemas (local-piper default, local-coqui, openai, elevenlabs, google-cloud, azure-cognitive)
  - 3 subtitle generation methods (auto from script, STT, manual)
  - Sidecar vs burn-in caption packaging
  - Cost estimation tables (default vs premium config)
  - Migration guide
- **Project intake § 11 "Media policy"** — full media config block in PROJECT_INTAKE_TEMPLATE
- **Module intake § 8 "Media override"** — per-module overrides for screenshot density, video density, per-locale forcing, voiceover override
- **TTS provider install instructions** in SETUP.md / SETUP.vi.md (Piper, Coqui, OpenAI, ElevenLabs, Google Cloud, Azure)
- **Whisper STT install** for human voiceover subtitle generation
- **INTAKE_GUIDE en/vi § 11** explanation for BAs (decision matrix, cost reality check)
- **INTAKE_GUIDE en/vi § 8** explanation of module media override common cases

### Changed

- **`walkthrough` command** — respects screenshot density rules and per-locale strategy from project intake § 11
- **`record` command** — respects video density rules, length caps, voiceover strategy, TTS provider config; warns on length cap exceeded; checks TTS prerequisites
- **`verify` command** — added check #11: media compliance (screenshots match density policy, videos within length caps, voiceover/subtitle files exist when expected)
- **File organization** in SKILL.md — adds `documentation/videos/voiceover/` and `documentation/videos/subtitles/` paths; per-locale image namespace under `images/<module>/<locale>/`
- **Project intake validation** — if "AI synthetic voice" selected, TTS provider must be selected; if non-local TTS, auth env var required
- **Module intake validation** — media overrides reference valid content types and providers

### Default decisions (designed for cheap-first, upgrade-later)

| Config | Default | Reason |
|---|---|---|
| Screenshot per-locale | Source-only | 1× capture cost; note "EN UI" in translated docs |
| Screenshot style | viewport-only | Clean for Docusaurus content |
| Aspect ratio | 16:9 desktop (1280×720) | Standard |
| Voiceover | Silent + on-screen captions | No TTS needed; multi-locale via text overlay |
| TTS provider | local-piper | Free, offline, no API key |
| Subtitle generation | Auto from script | Deterministic for Silent + AI voice strategies |
| Subtitle packaging | Sidecar `.vtt` | Flexibility, smaller storage |

User can upgrade strategy by re-editing project intake § 11 and re-running `walkthrough`/`record`. Existing media not regenerated unless explicit re-run.

### Deferred (v1.5.5 limitations)

- **Pixel-perfect annotation** for `annotated` style — requires manual edit (Figma, Photoshop)
- **Video editing** — record produces single-take captures; no transitions, intros/outros
- **Music library** — ambient music must be user-provided file
- **Lip-sync verification** — when AI voice + screen capture, no check that timing matches
- **Background blur** for general aesthetic (only for redaction)
- **STT subtitle from voiceover audio** — works only with text-script paths in v1.5.5

### Cost reality

Default config (silent + source-only) for 3 locales × 5 modules × 30 docs:
- ~1 hour total time, $0 TTS cost, ~65 MB storage

Premium config (AI voice per locale + per-locale screenshots):
- ~3 hours first run, ~$5-10 TTS cost, ~200 MB storage

Documented explicitly in MEDIA_POLICY_TEMPLATE § 11 so users can budget.

### Migration from v1.5.4

For new projects: just use v1.5.5. Project intake template includes Media policy section.

For existing v1.5.4 workspaces:
```bash
/docsmith plan --migrate-media
```
AI:
1. Inspects existing screenshots and videos in workspace
2. Proposes default config (silent + source-only screenshots + viewport-only style)
3. User confirms or adjusts
4. AI updates project intake § 11

Existing screenshots and videos NOT regenerated. Only new captures from next walkthrough/record follow new policy.

### Why this is a patch (not minor)

1 new template (MEDIA_POLICY), 2 modified templates, 2 modified guide files, 2 modified setup files, 4 SKILL.md sections updated. No new commands. No schema-breaking changes. Behavior is additive: project intake without § 11 falls back to all-default media policy; module intake without § 8 inherits from project.

Plugin functionality identical to 1.5.4 for projects that don't fill in the new sections.

## [1.5.4] - 2026-04-28

Sitemap consistency feature — fixes navigation drift across modules.

### Why

Real-world example from a Cloud Advisor doc + Tagging doc: same project, two modules with completely different sitemap structures. Tagging used "Quick Starts → Tutorials"; Cloud Advisor used "Guides → Reference → Glossary → Troubleshooting". Users navigating between modules felt lost. AI generated each sitemap independently with no consistency rules.

v1.5.4 adds:

1. **Canonical section types** — fixed list of 11 types every section must map to (overview, initial-setup, quickstarts, tutorials, guides, concepts, dashboard, reference, api-reference, glossary, troubleshooting)
2. **3 project patterns**:
   - **Pattern A** (Learning path, default): `overview → initial-setup → quickstarts → tutorials → guides → concepts → reference → api-reference → troubleshooting → glossary`
   - **Pattern B** (Task-first): `overview → quickstarts → guides → concepts → reference → troubleshooting → glossary`
   - **Pattern C** (Custom): user defines order in project intake
3. **Per-module section selection** — module intake has explicit "Sitemap sections" subsection with checkboxes for which canonical types this module includes
4. **AI suggestions** — `plan` warns when a module is missing a section the project pattern includes (e.g., "Pattern A includes glossary but module 'storage' didn't tick it; suggest adding")
5. **Display name overrides** — both project-level and module-level allow renaming canonical sections (slugs stay canonical for deploy paths)

### Added

- `templates/SITEMAP_PATTERNS_TEMPLATE.md` — definitive reference for section types, patterns, generation logic, validation rules
- Project intake § 9 "Sitemap pattern" — pick A/B/C and optional display name overrides
- Module intake § 7 "Sitemap sections" — per-module checkbox list of canonical types + per-module display name overrides
- New `verify` check #10: sitemap consistency (was "no orphan test cases" before; consolidated into other checks)
- INTAKE_GUIDE en/vi: added § 9 (project sitemap pattern) and § 7 (module sitemap sections) explanations
- `plan --migrate-sitemap` flag for v1.5.3-or-earlier workspaces

### Changed

- **`plan` command** — now reads project pattern and per-module sections; generates `sitemap.md` with consistency warnings inline
- **`categorize` command** — uses sitemap pattern order to compute Docusaurus `position` fields; respects display name overrides for `label`
- **`verify` command** — check #10 replaced: was "no orphan test cases" (rarely actionable), now "sitemap consistency" (actionable, surfaces real navigation drift)
- **SKILL.md** — `plan`, `verify`, `categorize` sections updated with sitemap pattern references

### Deferred

- **Auto-fix mode** for sitemap inconsistency — explicitly NOT implemented per user decision. AI warns but doesn't rename or restructure without user input. User remains the IA authority.
- **Pattern templates for specific industries** (B2B SaaS, dev tools, infrastructure) — could be Pattern D/E/F. Defer until real demand.
- **Cross-locale sitemap consistency** — translated docs follow source sitemap automatically; per-locale customization deferred.

### Migration from v1.5.3

For new projects: just use v1.5.4. Project intake template includes sitemap pattern selection.

For existing v1.5.3 workspaces:
```bash
/docsmith plan --migrate-sitemap
```
AI:
1. Inspects existing sitemap.md and modules
2. Proposes Pattern A as default
3. Suggests per-module section selections based on existing draft folder structure
4. User confirms; AI updates project intake (§ 9) and module intakes (§ 7)
5. Re-runs `plan` to regenerate sitemap.md per new rules

Existing drafts are NOT modified. Only intake files and sitemap.md change.

If you skip migration: `plan` still works (uses Pattern A defaults) but warnings about missing pattern config will appear until you complete intakes.

### Why this is a patch (not minor)

Adds 1 template, modifies 2 templates, 1 verify check changes meaning. No new commands. No schema-breaking changes for existing workspaces. Behavior is additive: project intake without § 9 falls back to Pattern A; module intake without § 7 falls back to AI inferring sections from drafts.

## [1.5.3] - 2026-04-28

Documentation patch — adds prerequisites guide for `walkthrough` and `record` commands. Bridges a gap between SKILL.md and operational reality.

### Added

- **`SETUP.md`** (English) — comprehensive prerequisites guide:
  - Path 1: Claude in Chrome extension install (recommended for beginners)
  - Path 2: Playwright MCP server (for headless / CI use)
  - Path 3: ffmpeg setup for `record` (video tutorials)
  - Environment variables for sources (NOTION_TOKEN, GITHUB_TOKEN, GOOGLE_DRIVE_TOKEN) and credentials (test account)
  - How to obtain auth tokens for each source type (step-by-step Notion integration setup, GitHub fine-grained PAT, Google Drive service account)
  - Per-project `.env` setup with direnv support
  - Pre-walkthrough and pre-record checklists
  - Common errors and fixes (login failures, browser timeouts, missing ffmpeg, wrong locale captures)
  - Network/firewall allowlist requirements
  - Performance tuning for slow walkthrough/fetch/translate
  - "docsmith without browser" path for users who only need drafts + translation
- **`SETUP.vi.md`** (Vietnamese) — full Vietnamese translation
- **README "How it works" section** now links SETUP.md as required reading before first walkthrough/record run

### Changed

- **SKILL.md** — Prerequisites notes added to:
  - `walkthrough` command (links to SETUP § Path 1 or Path 2)
  - `record` command (links to SETUP § Path 3)
  - `fetch` command (links to SETUP § Environment variables)
- **README Quick start** — fully refreshed to v1.5+ flow:
  - Step 1: SETUP reference (one-time)
  - Step 2: init
  - Step 3: module commands per feature
  - Step 4: fill intake forms (links INTAKE_GUIDE)
  - Step 5: run + continue
  - Step 6: deploy
  - Update flow section
  - In-place section consolidated
- **README "What's new"** — v1.5.3 entry added
- Removed leftover content from old Quick start

### Why this is a patch (not minor)

No new commands, no schema changes, no new templates. Pure documentation gap-fill. Skill functionality identical to 1.5.2.

### Migration from 1.5.2

None needed. SETUP.md describes existing prerequisites that were always there but undocumented. Users who already have Claude in Chrome / Playwright / ffmpeg installed don't need to do anything.

For users who tried v1.5.2 walkthrough/record and got confused by missing tools: read SETUP.md and install per Path 1/2/3 as needed.

## [1.5.2] - 2026-04-28

Plugin format compliance — restructure to follow official Claude Code plugin marketplace specification. Required to fix `/plugin marketplace add dangtran1003/docsmith-v2` failing with "Marketplace file not found".

### Changed (BREAKING for direct-clone installs only)

- **Repository restructured** to plugin marketplace layout:
  ```
  docsmith-v2/                       (was: skill files at root)
  ├── .claude-plugin/                ← new
  │   ├── marketplace.json           ← new (catalog)
  │   └── plugin.json                ← new (manifest, replaces root plugin.json)
  ├── skills/
  │   └── docsmith/                  ← new (skill content moved here)
  │       ├── SKILL.md
  │       ├── deploy-reference.md
  │       ├── intake-reference.md
  │       ├── translate-reference.md
  │       ├── process-reference.md
  │       ├── tools-reference.md
  │       ├── presets/
  │       └── templates/
  └── (top-level docs unchanged: README, CHANGELOG, etc.)
  ```
- **Old root `plugin.json` removed** — replaced by `.claude-plugin/plugin.json` with the same purpose. Marketplace integration was broken without this restructure.
- **Reference docs and templates moved into `skills/docsmith/`** — they're referenced from SKILL.md by relative path, must be siblings.

### Added

- `.claude-plugin/marketplace.json` — marketplace catalog with one plugin entry pointing to `./` (the same repo)
- `.claude-plugin/plugin.json` — official plugin manifest format
- README "Update" section showing how to update for each install method
- PUBLISHING.md rewritten with new install commands using marketplace + alternative manual install paths

### Fixed

- `/plugin marketplace add dangtran1003/docsmith-v2` now works (was failing pre-1.5.2 because no `.claude-plugin/marketplace.json`)
- Install command syntax corrected: `/plugin install docsmith@dangtran1003-docsmith-v2` (the `@<marketplace-name>` form was missing in v1.5.1 docs)

### Migration

For users who installed v1.5.x via `/plugin marketplace add` (impossible — install was broken until 1.5.2):
- N/A; v1.5.2 is the first version that actually works as a marketplace plugin.

For users who direct-cloned v1.5.x into `~/.claude/skills/docsmith/`:
1. Pull latest: `cd ~/.claude/skills/docsmith && git pull`
2. Reinstall from new path:
   ```bash
   rm -rf ~/.claude/skills/docsmith
   git clone https://github.com/dangtran1003/docsmith-v2.git ~/repos/docsmith-v2
   ln -s ~/repos/docsmith-v2/skills/docsmith ~/.claude/skills/docsmith
   ```
   Or copy: `cp -r ~/repos/docsmith-v2/skills/docsmith ~/.claude/skills/`

For users who didn't install yet: just use `/plugin marketplace add dangtran1003/docsmith-v2` directly.

### Why this is a patch (not minor)

No new commands, no new features, no new templates, no schema changes. Pure restructuring required by the platform. Plugin functionality identical to 1.5.1.

## [1.5.1] - 2026-04-26

Patch release — bug fixes for path conflicts + comprehensive intake usage guide. No new commands or breaking changes.

### Fixed

- **Issue 1: `<feature>` path ambiguity resolved.** Drafts go to `documentation/drafts/<source-locale>/<module.folder>/<doc>.md`. `<module.folder>` defaults to `module.slug`. Documented explicitly in SKILL.md § "Path rules" and intake-reference.md § "Path mapping".
- **Issue 2: in-place mode collision detection.** `init` now pre-checks for existing `documentation/` content, recognizes when running inside a Docusaurus repo (suggests in-place mode), refuses to scaffold silently next to user content. New `--in-place` flag for explicit opt-in.
- **Issue 3: re-run protocol on `module` create.** Already worked, but now documented explicitly in SKILL.md and INTAKE_GUIDE.
- **Issue 4: per-module run state.** `documentation/.run-state/<module>.yaml` (one file per module) replaces single `documentation/.run-state.yaml`. Fixes loss of state when running multiple modules sequentially through different pause gates.
- **Issue 5: deployments folder moved inside workspace.** `documentation/deployments/` instead of root-level `deployments/`. docsmith's footprint at the project root is now exactly one folder: `documentation/`. Reduces collision risk in in-place mode.
- **Issue 6: glossary path explicit in intake.** Project intake template now has a § Languages > Glossary files subsection clarifying that AI looks for `documentation/standards/glossary.<locale>.yaml` at a fixed path. Auto-created (empty) by `init` when target languages are set.
- **`.gitignore` smart append.** `init` no longer overwrites existing `.gitignore`. It appends a `# BEGIN docsmith ... # END docsmith` block, idempotent on re-run.

### Added

- **`INTAKE_GUIDE.md` and `INTAKE_GUIDE.vi.md`** — comprehensive practical guide for BAs filling intake forms. Covers: what each section means, how AI uses each field, common patterns (single-feature, in-place, multilingual, Notion sources, post-UI-change updates, source-change updates), error recovery.
- **README link** to INTAKE_GUIDE in How it works section.

### Changed

- **File organization in SKILL.md** updated to reflect new paths (`documentation/deployments/`, per-module `.run-state/<module>.yaml`).
- **Path scoping rules** updated: writes only inside `documentation/` (workspace, includes deployments + run-state) and `deploy.target_path` (deploy command only).
- **`init` behavior** documented with pre-checks and `--in-place` flag.
- **Project intake template** § Languages now has glossary path note + glossary_required option.

### Migration from 1.5.0

Existing v1.5.0 workspaces (if any beta users):

1. Move `deployments/` (root level) into `documentation/deployments/`: `mv deployments documentation/deployments`
2. Move `.run-state.yaml` into per-module files: `mkdir documentation/.run-state && mv documentation/.run-state.yaml documentation/.run-state/<module>.yaml` (rename per the module the state was for)
3. Update `.gitignore`: replace any standalone `documentation/.run-state.yaml` entry with `documentation/.run-state/`

Or simpler: fresh `init` if you don't have unsaved progress.

For v1.4.x users following `--upgrade-from-1.4`: the upgrade automatically applies the new layout.

## [1.5.0] - 2026-04-26

Lean refactor + intake-driven config. Largest release in the v1.x line. Originally planned as v1.5 + v1.6 combined.

### Added

- **Markdown intake forms** — `documentation/intake/project.md` and `documentation/intake/modules/<n>.md` replace `.docsmithrc.yaml` as primary config. BA-friendly: checkboxes, fillable backtick fields, no YAML syntax.
- **Layered config** — defaults → project intake → module intake → CLI flags. Higher layers override lower for the same field; sources are cumulative.
- **`module` command** — manage per-feature module intakes. Sub-commands: `<n>`, `--from`, `list`, `archive`, `unarchive`. Updates project.md modules list automatically.
- **`fetch` command** — pull external knowledge sources into local cache. Types: Notion, GitHub, Google Drive, URL, local file. Auth via env var references (never plaintext).
- **`run` command** — orchestrated pipeline that auto-chains stages with configurable pause gate (default `after-draft`). Saves state to `.run-state.yaml`.
- **`continue` command** — resume `run` from saved state.
- **`update` command** — detect external source changes via cheap metadata calls (Notion edit time, GitHub commit SHA, GDrive revision, URL ETag, file mtime). Propose targeted draft re-runs.
- **`intake-help` command** — print field reference for intake forms with validation rules and defaults.
- **`sources.lock.yaml`** — auto-managed lock file tracking fetched state per source (versions, hashes, cache paths).
- **External source cache** — `documentation/.cache/sources/` (gitignored) holds fetched content for offline runs.
- **`intake-reference.md`** — comprehensive reference for intake parsing, layered config resolution, validation, fetch/update workflow.
- **3 new templates**: `PROJECT_INTAKE_TEMPLATE.md`, `MODULE_INTAKE_TEMPLATE.md`, `SOURCES_LOCK_TEMPLATE.md`.

### Changed

- **`init` command** — scaffolds intake forms instead of writing yaml. New flag `--upgrade-from-1.4` reads existing `.docsmithrc.yaml` and pre-fills `project.md`.
- **`voice` command** — Quick mode default (1 file: voice-chart.md). `--full` flag opt-in for legacy 3-file output (UX patterns + scorecard).
- **`translate` command** — Default review mode is now `batch` (whole-file diff) instead of `per-block`. `--per-block` flag for opt-in safer mode.
- **Default `behavior.on_existing`** — kept as `prompt` (safer for new users). Power users can switch via intake `Auto-run behavior`.
- **Process flow** — now starts at intake-fill rather than interactive prompts. Stages still individually invokable; `run` chains them.
- **20 commands** total. v1.4.0 had 21 commands (with overlap). Lean cuts: removed `start`, `validate`, `test`, `tech-review`, `peer-review` as separate commands (merged into others or replaced by intake/run). Added: `module`, `fetch`, `run`, `continue`, `update`, `intake-help`.

### Removed

- **`start` command** — duplicated `init`. Use `init` to scaffold; use `run` to execute pipeline.
- **`validate` command** — replaced by `walkthrough --check` (already does the same job).
- **`test` command** — folded into `walkthrough` (test cases auto-built from drafts).
- **`peer-review` and `tech-review` commands** — these are inherently human steps. Now part of the natural pause-and-review flow between `run` and `continue`. No separate command needed.
- **`review-plan` command** — removed; review happens inline with `--pause-at after-plan`.
- **`incorporate` command** — folded into `edit --from-review`.
- **`sitemap` command** — output of `plan` (combined into one stage).
- **5 templates removed** as redundant or no longer needed: `MERGE_DECISION_TEMPLATE.md`, `TRANSLATION_DECISIONS_TEMPLATE.md`, `UX_CONTENT_SCORECARD_TEMPLATE.md` (use `voice --full` if needed), `UX_TEXT_PATTERNS_TEMPLATE.md` (use `voice --full`), `TRACEABILITY_MATRIX_TEMPLATE.md` (inlined into documentation-plan), `WALKTHROUGH_TEST_EXECUTION_TEMPLATE.md` (folded into test-case template).
- **2 reference docs removed**: `subprocess-010a.md` (folded into `process-reference.md`), `update-reference.md` (folded into SKILL.md re-run protocol section).

### Deferred / not in 1.5.0

- **Visual regression** in walkthrough (pixel-diff between captured and previous screenshots): future, no version assigned. Was originally on v1.5 plan but de-prioritized after user feedback that re-run safety + intake matter more.
- **`migrate` command** for config schema changes: removed from roadmap. Since docsmith has no production users yet, breaking config changes are handled in CHANGELOG migration notes only.
- **`adopt` command** (convert existing Docusaurus docs into workspace): future. v1.5.0 has `init --upgrade-from-1.4` for migrating from prior docsmith versions, but not for converting existing untracked docs.
- **`health` command** (one-shot wrapper of verify + drift + compare): future. Use `/docsmith verify` and `/docsmith update` separately for now.
- **Translation drift tracking** (`translate --check` mode): future. Workaround: re-run `translate` in Update mode.
- **`<!-- translation-locked -->` markers**: future.
- **Per-locale image namespacing** for products with localized UI screenshots: future.
- **Per-doc source provenance tracking** in `update` (which doc uses which source for surgical updates): future. Currently `update` re-evaluates all docs in a module on any source change.

### Migration from 1.4.x

For existing v1.4.x workspaces:

1. Pull v1.5.0
2. Run `/docsmith init --upgrade-from-1.4` — reads `.docsmithrc.yaml` and pre-fills `documentation/intake/project.md`
3. Edit `project.md` to fill remaining fields (audience, sources, voice details that weren't in yaml)
4. Run `/docsmith module <n>` for each feature area (`instances`, `storage`, etc.)
5. Edit each module file
6. Run `/docsmith run` to verify everything resolves correctly

Old yaml is read for backward compat but deprecated. v1.6 will remove yaml support.

For NEW projects: just `/docsmith init` directly produces the new structure.

### Why this large release

User feedback during v1.4.0 design: "22 commands too many, intake configuration unfriendly to BAs". Lean refactor addresses both:
- Commands cut/merged from 21 to 20 (number similar but functional overlap removed)
- YAML replaced with markdown forms
- New `run`/`continue`/`update` automate the boring parts

Combined with v1.6's planned translate command (already shipped in v1.4.0), the v1.x line is feature-complete enough for early production trial.

## [1.4.0] - 2026-04-26

Multi-locale translation lands. Originally planned as v1.6 but promoted because translation gates the "done" definition for any multi-locale project.

### Added

- **`translate` command** — AI translation from `locales.source` to each entry in `locales.targets`. Per-block review gate by default; `--auto-approve` flag for speed. See [translate-reference.md](translate-reference.md).
- **Per-block review gate** — for each translatable block (heading, paragraph, list, table cell, alt text, link text, frontmatter title), AI proposes translation. User decides: `y` approve / `e` edit / `s` skip (keep source) / `n` remove / `a` approve all remaining / `q` quit.
- **Glossary support** — optional per-locale `documentation/standards/glossary.<locale>.yaml` with longest-match-wins lookup, case sensitivity, context disambiguation, UI label preservation. Built iteratively from per-block review corrections. See [templates/GLOSSARY_TEMPLATE.yaml](templates/GLOSSARY_TEMPLATE.yaml).
- **Translation metadata** in frontmatter — `translated_from`, `translated_at`, `source_hash`, `glossary_version`, `translation_status`. Forward-compatible with v1.6.x drift tracking.
- **Block-level preserve rules** — code blocks, inline code, file paths, URLs, frontmatter `id`/`slug`, image src paths, video markers, MDX component tags are NEVER translated.
- **Re-run protocol integration** — translate honors the 4-option gate. Update mode preserves manually-edited translations when source unchanged; only proposes changes for modified/new/removed source blocks.
- **Translation completeness check in `deploy`** — when `locales.targets` non-empty, deploy verifies each target has translated drafts for all source files. Missing translations emit a warning per locale.
- **`--locale <locale>` flag** for `translate` and `walkthrough` — scope to single target locale.
- **Process Flow update** — `translate` is positioned after `incorporate` and before `categorize`/`deploy`. Required for multi-locale projects; no-op for single-locale.
- 2 new templates: `GLOSSARY_TEMPLATE.yaml`, `TRANSLATION_DECISIONS_TEMPLATE.md`. New: `translate-reference.md`.

### Changed

- **`init` command** — for each target locale, scaffolds empty `glossary.<locale>.yaml` from template (replaces v1.2.x README placeholders). Target draft folders remain empty for `translate` to populate.
- **`deploy` command workflow** — adds translation completeness check as step 1 before detection. Warns and lists incomplete locales but does not block.
- **`.docsmithrc.yaml` schema** — added `translate:` block (`enabled`, `glossary_required`, `default_review_mode`, `preserve_frontmatter_fields`, `translate_frontmatter_fields`, `warn_on_deploy_if_incomplete`).
- **Docusaurus preset** — comment clarifies non-source-locale drafts come from `translate` command, not direct authoring.
- **File Organization** — `glossary.<locale>.yaml` listed under `standards/`; target locale draft folders contain real `.md` files (not README placeholders) once `translate` has run.

### Deferred to future versions

- **Translation drift tracking** (`translate --check` mode listing source-changed sections without prompting): v1.6.x roadmap. Workaround: re-run `translate` in Update mode.
- **`<!-- translation-locked -->` markers** for protecting blocks from re-translation: v1.6.x roadmap.
- **Per-locale image namespacing** for products with localized UI screenshots: v1.5+ roadmap.
- **Voice chart per locale** (`voice-chart.<locale>.md`) for tone consistency in translations: v1.5+ roadmap.
- **Visual regression in walkthrough** (pixel-diff): v1.5+ roadmap.
- **`migrate` command** for config schema changes: v1.5+ roadmap if schema changes.
- **`adopt` command** + **`health` command**: v1.5+ roadmap (unchanged).

### Migration from 1.3.x

No breaking changes for single-locale projects. For multi-locale projects:

1. Pull v1.4.0
2. (Optional) Create `documentation/standards/glossary.<locale>.yaml` from [templates/GLOSSARY_TEMPLATE.yaml](templates/GLOSSARY_TEMPLATE.yaml) for each target locale
3. Replace v1.2.x README placeholders in target draft folders with actual translations: `/docsmith translate <product>`
4. Per-block review gate ensures no garbage gets into target drafts
5. Add `translate` to your CI pipeline if applicable
6. Future deploys verify translation completeness before applying

If you previously hand-translated files into `drafts/<target-locale>/`, those files are detected by `translate` re-run protocol and treated as existing — Update mode preserves them as KB.

### Roadmap revision

Numbering compressed: what was planned as v1.4 + v1.5 + v1.6 is now redistributed:

- **v1.4.0** (this release): translation (was v1.6)
- **v1.5.0** (next): visual regression + migrate command + per-locale image namespacing + voice chart per locale (was v1.4 + parts of v1.5)
- **v1.6.0** (later): translation drift tracking + lock markers + adopt command + health command (deferred items from v1.4 + originals from v1.5/v1.6)

## [1.3.0] - 2026-04-26

Re-run safety + drift detection + delete propagation. Doc CRUD becomes deterministic.

### Added

- **Re-run protocol**: every command checks output existence before writing. 4-option gate when exists: Update / Overwrite / Side-by-side / Cancel. Default `prompt`; configurable via `behavior.on_existing` in `.docsmithrc.yaml`.
- **KB inheritance**: in Update mode, AI reads existing artifact in full as canonical knowledge base. Generates 4-kind delta proposal (NEW / UPDATE / REMOVE / KEEP). User approves per-item. Untouched content (KEEP) is NEVER regenerated — preserves team's manual edits.
- **Per-artifact merge logic**: detailed rules per artifact type (audience, plan, sitemap, voice, drafts, test cases) in [update-reference.md](update-reference.md).
- **Walkthrough 3-phase pipeline**:
  - Phase A (`--check`): VERIFY only — read drafts, run assertions, output drift report. Read-only, fast (~30s for moderate doc set).
  - Gate: user reviews drift report, sets per-item decisions in `decisions.yaml` (auto-fix / manual-fix / product-bug / skip).
  - Phase B (`--apply`): UPDATE drafts per decisions.
  - Phase C: CAPTURE screenshots.
  - Default mode (no flags): runs A → interactive gate → B → C in sequence.
  - `--skip-drift` flag: Phase C only (backward compatible with 1.2.x usage).
  - `--auto-apply-high-confidence` flag: skip gate, auto-apply HIGH confidence fixes only.
- **Product-bug tracking** (optional, non-blocking): drift items can be marked `product-bug` (doc is correct, UI has regression). Tracked in `walkthrough/active-product-bugs.yaml` across runs. Auto-resolved when UI matches doc again.
- **Delete propagation**: `deploy` always lists "Orphan files in target" in plan output. With `--sync-deletes` flag, executes deletes after copies (with backup to `deployments/<ts>/deleted/`). Default: never delete (safe).
- **Drift report template** ([templates/DRIFT_REPORT_TEMPLATE.md](templates/DRIFT_REPORT_TEMPLATE.md)): format spec, confidence rubric, decision values.
- **Merge decision template** ([templates/MERGE_DECISION_TEMPLATE.md](templates/MERGE_DECISION_TEMPLATE.md)): on-disk format for re-run protocol audit.
- **Update reference doc** ([update-reference.md](update-reference.md)): full re-run + KB inheritance + drift + delete propagation logic.
- **Archive folder**: `documentation/archive/<timestamp>/` for re-run backups.
- **Drift folder**: `documentation/walkthrough/drift/<timestamp>/` for drift detection runs.

### Changed

- **`draft` / `plan` / `sitemap` / `voice`**: now subject to re-run protocol gate when output already exists. Update mode reads existing as KB and proposes deltas only.
- **`walkthrough`**: refactored from single-pass to 3-phase pipeline. Default mode unchanged externally (still works without flags), but internally adds drift verification before fix-and-capture.
- **`deploy`**: plan output always includes "Orphan files in target" section. New `--sync-deletes` flag opts into actual deletion.
- **`.docsmithrc.yaml` schema**: added `behavior.on_existing`, `behavior.drift_default_action`, `behavior.side_by_side_suffix_style`, `deploy.sync_deletes`, `deploy.audit_retention_days`.

### Deferred to future versions

- **Visual regression** in walkthrough (pixel-diff between captured screenshots and previous): on v1.4 roadmap.
- **`migrate` command** for `.docsmithrc.yaml` schema changes between major versions: on v1.4 roadmap if needed.
- **`health` command** as a one-shot wrapper of verify + drift + compare: v1.5 roadmap.
- **Translation** (auto-translate from source locale): v1.6 roadmap (unchanged).
- **`adopt` command** (convert existing Docusaurus docs into workspace): v1.5 roadmap (unchanged).

### Migration from 1.2.x

No breaking changes. New behavior is opt-in via flags:

- All v1.2.x command invocations continue to work without modification
- First re-run of any command on existing output will trigger the new gate; choose Update mode to merge with existing
- `walkthrough --skip-drift` mimics v1.2.x behavior exactly if you want to defer adopting drift detection

To adopt fully:

1. Pull v1.3.0 (`git pull` or `/plugin marketplace update`)
2. Optionally edit `.docsmithrc.yaml` to add `behavior:` block (see [.docsmithrc.example.yaml](.docsmithrc.example.yaml))
3. Run `/docsmith walkthrough <product> --check` after your next product release to see drift detection in action
4. Use `/docsmith deploy <product> --sync-deletes --dry-run` after deleting any drafts to preview cleanup

## [1.2.1] - 2026-04-26

### Added

- **`HOW_IT_WORKS.md`**: end-user walkthrough of the skill's operating model — 12 sections covering the two-layer model, command pipeline, init, config, authoring loop, deploy, categorize, locales, mental model, daily cheat-sheet, troubleshooting, and reading list. Read this before using docsmith on a real project.
- **`HOW_IT_WORKS.vi.md`**: Vietnamese translation of the same document.
- README "How it works" section linking to both language versions.

### Notes

Patch release — documentation only. No SKILL.md or command logic changes from v1.2.0.

## [1.2.0] - 2026-04-26

Standalone-first refactor + deploy to host project (Docusaurus preset).
This release combines what was originally planned as v1.2 (foundation) and v1.3 (deploy).

### Added

- **`init` command**: scaffold workspace with `.docsmithrc.yaml` config, `documentation/` folder tree, locale-aware draft directories. Detects host project context (`docusaurus.config.*`, `CLAUDE.md`) and suggests preset.
- **`deploy` command**: copy/sync workspace to host project with transforms. Supports `--dry-run`, `--target <path>`, `--force`, `--locale <locale>`. Detects target via `CLAUDE.md` then `docusaurus.config.*`. Generates audit trail in `deployments/<timestamp>-<target>/`.
- **`categorize` command**: generate Docusaurus `_category_.json` files from sitemap. Normalizes titles (acronyms uppercase, articles lowercase). Flags undocumented folders.
- **`.docsmithrc.yaml` config schema**: source of truth for product slug, locales, paths, deploy preset, collision strategy, validation rules. Every command reads it before writing. See [.docsmithrc.example.yaml](.docsmithrc.example.yaml).
- **Path scoping enforcement**: every write validated against allowed roots (workspace + deploy target). Reject writes outside.
- **Standalone preset** (`presets/standalone.yaml`): default. No deploy target. Workspace is the publishable artifact.
- **Docusaurus preset** (`presets/docusaurus.yaml`): full deploy mappings, frontmatter injection, image namespacing, MDX escaping, category generation.
- **Locale-aware draft structure**: `documentation/drafts/<locale>/` per locale. Source locale gets actual drafts; target locales get scaffolded folders for v1.6 auto-translation.
- **In-place mode**: `deploy.default_target = .` runs deploy within same project (workspace + Docusaurus folders coexist).
- **Image namespacing**: `product.slug` becomes URL prefix `/img/<slug>/`. Globally unique across products sharing a target.
- **Deploy reference doc** ([deploy-reference.md](deploy-reference.md)): detection, plan, action determination, dry-run output format, audit trail, in-place mode, categorize subcommand, title normalization rules, known limitations.
- **Category file template** ([templates/CATEGORY_FILE_TEMPLATE.md](templates/CATEGORY_FILE_TEMPLATE.md)): `_category_.json` schema, examples, acronym preservation.

### Changed

- **`draft` command**: now writes to `documentation/drafts/<locales.source>/<path>.md` (locale-aware). Image refs use workspace-absolute paths `/images/<feature>/<asset>.png`. Note: drafts in non-source locales are NOT auto-generated in 1.2.0 (deferred to v1.6 auto-translation).
- **`publish` command**: now positions itself after `deploy` (was the only deployment step before). Checklist updated to reflect deploy-driven workflow ending in `git commit/push` on target.
- **Process Flow diagram**: includes `init`, `categorize`, and `deploy`.
- **File Organization section**: split into Workspace + Target + In-place mode for clarity.
- **plugin.json description and keywords**: reflect Docusaurus, i18n, deploy capabilities.

### Deferred to future versions

- **`translate` command**: scaffolding the locale folder structure is in 1.2.0; AI auto-translation is on the **v1.6** roadmap. Until then, users with multi-locale needs must populate `drafts/<target-locale>/` manually.
- **`adopt` command**: convert existing Docusaurus docs into a docsmith workspace. Targeting **v1.5**.
- **Sidebar generation** (`sidebars.generated.js` from sitemap): config flag exists (`generate_sidebars`) but generator unimplemented in 1.2.0. Default false, so no impact. Targeting **v1.4**.
- **Hide undocumented folders**: report-only in 1.2.0. Auto-hide via sidebars on **v1.4** roadmap.

### Migration from 1.1.0

If you were using docsmith 1.1.0 with the old flat layout (`docs/drafts/`, `docs/images/`):

1. Run `/docsmith init` in your project to create `.docsmithrc.yaml` and the new `documentation/` workspace
2. Move existing files: `docs/drafts/*.md` → `documentation/drafts/<source-locale>/`, `docs/images/` → `documentation/images/`, `docs/walkthrough/` → `documentation/walkthrough/`
3. Update image refs in markdown: change relative `./images/foo.png` to workspace-absolute `/images/foo.png`
4. Run `/docsmith verify <product>` to confirm no broken references
5. (Docusaurus users) Run `/docsmith deploy <product> --dry-run` to preview the new flow

The 1.1.0 layout is no longer recommended but will still work with the existing commands; only `init`, `deploy`, and `categorize` require the new layout.

## [1.1.0] - 2026-04-26

### Added

- New `record` command (alias `rec`) for capturing short tutorial videos from `<!-- VIDEO ... -->` markers via browser screen recording
- `templates/SCREENSHOT_POLICY_TEMPLATE.md` — caption rules (state-not-action, specific data, label-not-appearance, placement-after-step), density rules, file naming conventions
- `templates/VIDEO_MARKER_TEMPLATE.md` — marker syntax with structured fields (id, duration, type, start, actions, end, highlight, pacing, caption), good/bad examples, re-record metadata convention
- `templates/WALKTHROUGH_VIDEO_PLAN_TEMPLATE.md` — capture plan format mirroring screenshot capture plan, blocked-marker handling, execution notes
- `videos/` and `videos/raw/` folders in the documented file organization
- `walkthrough/video-plan/` folder for video capture plans
- `standards/screenshot-policy.md` listed in standards directory

### Changed

- `draft` command now references `SCREENSHOT_POLICY_TEMPLATE.md` and enforces explicit caption rules and density rules inline
- `walkthrough` command now documents caption-driven matching mechanism and pre-execution caption review; explicitly skips `<!-- VIDEO ... -->` markers (handled by `record`)
- Process Flow diagram includes `[record (AI, optional)]` between `walkthrough` and `peer-review`

### Notes

- `process-reference.md`, `subprocess-010a.md`, `tools-reference.md` unchanged in this release; the `record` command is documented self-contained in SKILL.md

## [1.0.0] - 2026-03-11

### Added
- Initial skill structure based on PRC-010 Documentation Creation Process
- Command-based invocation with aliases: `start`, `audience`, `plan`, `review-plan`, `sitemap`, `voice`, `draft`, `edit`, `walkthrough`, `validate`, `test`, `verify`, `peer-review`, `tech-review`, `incorporate`, `publish`
- `help` command showing full command reference
- `verify` command with 10 verification checks (technical accuracy, completeness, structure, clarity, voice compliance, link audit, placeholder audit, traceability, sitemap consistency, template compliance) — supports project-wide or scoped to specific docs via path/glob
- `validate` command for re-running walkthrough test cases without modifying docs
- `test` command for generating test cases from existing docs without executing them
- 9 templates: audience profile, documentation plan, traceability matrix, content type templates, voice chart, UX text patterns, UX content scorecard, walkthrough test cases, walkthrough test execution
- Process reference (PRC-010), subprocess reference (PRC-010A), tools reference (browser automation)
- File organization convention under `docs/`
- Versioning with YAML frontmatter and this changelog

### Sources
- *Docs for Developers* (Bhatti et al., 2021)
- *Strategic Writing for UX* (Podmajersky, 2019)
