---
name: docsmith-v2
description: "Build documentation from filled markdown intake forms. AI fetches knowledge from Notion/GitHub/GDrive/URL/files, drafts content, captures screenshots via browser walkthrough, translates to multiple locales, and deploys to Docusaurus. Layered intake (project + module). Re-run safe; source change detection via lock file. Commands: init, module, fetch, run, continue, audience, plan, voice, draft, edit, walkthrough, record, translate, verify, update, categorize, deploy, publish, intake-help, help."
---

# docsmith

Documentation skill following the PRC-010 process. Standalone-first workspace; deploys to Docusaurus or other targets via preset. v1.5.0 introduces a **layered intake system** so BAs can configure docs by filling markdown forms (no YAML) — and an `update` command that detects when external knowledge sources change.

Reading order:

- This file (catalog of commands and high-level rules)
- [intake-reference.md](intake-reference.md) — intake forms, layered config, `run`/`continue`/`update`/`fetch`/`module` commands, source fetching
- [process-reference.md](process-reference.md) — PRC-010 process detail
- [deploy-reference.md](deploy-reference.md) — deploy and categorize logic
- [translate-reference.md](translate-reference.md) — translation block-level rules and review modes
- [tools-reference.md](tools-reference.md) — browser automation reference

## Commands

20 commands. Most users typically run only `init`, `module`, `run`, and `deploy` for the happy path.

| Command         | Alias | Owner  | Purpose                                                                                                |
| --------------- | ----- | ------ | ------------------------------------------------------------------------------------------------------ |
| `help`          | `h`   | —      | Show this command reference                                                                            |
| `init`          | `i`   | **AI** | Initialize workspace: scaffold `documentation/intake/project.md`, folders, gitignore                    |
| `module`        | `m`   | **AI** | Create / list / archive a module intake at `documentation/intake/modules/<n>.md`                       |
| `intake-help`   | `ih`  | —      | Print intake field reference (what each section/field means, defaults)                                 |
| `fetch`         | `f`   | **AI** | Fetch external sources (Notion/GitHub/GDrive/URL/file). Updates cache + `sources.lock.yaml`.          |
| `run`           | `r`   | **AI** | Orchestrated pipeline: validate intake → fetch → audience → plan → voice → draft → edit → wt → record → translate. Pauses at the configured gate. |
| `continue`      | `c`   | **AI** | Resume `run` after a gate (read `.run-state.yaml`)                                                     |
| `audience`      | —     | **AI** | Generate audience profile from intake (use intake `Audience` section)                                  |
| `plan`          | `pl`  | **AI** | Generate documentation plan + sitemap from intake `Scope`                                              |
| `voice`         | `vc`  | **AI** | Generate voice chart from intake `Voice`. Quick mode by default; `--full` adds UX patterns + scorecard.|
| `draft`         | `dr`  | **AI** | Draft docs in `documentation/drafts/<source-locale>/`. Uses fetched sources as KB.                     |
| `edit`          | `ed`  | **AI** | Self-review (5 passes). With `--from-review`, applies feedback file.                                   |
| `walkthrough`   | `wt`  | **AI** | Verify against live product + capture screenshots. Phases: VERIFY → gate → APPLY → CAPTURE.            |
| `record`        | `rec` | **AI** | Record short tutorial videos from `<!-- VIDEO ... -->` markers (browser screen recording)              |
| `translate`     | `tr`  | **AI** | Translate from source locale to each `locales.targets`. Batch review by default; `--per-block` opt-in. |
| `verify`        | `vf`  | **AI** | 10-check audit (placeholders, voice score, links, glossary consistency, etc.)                          |
| `update`        | `up`  | **AI** | Detect changed external sources; propose draft updates                                                 |
| `categorize`    | `cat` | **AI** | Generate `_category_.json` from sitemap (Docusaurus preset)                                            |
| `deploy`        | `dep` | **AI** | Sync workspace to host project. `--dry-run`, `--target`, `--force`, `--locale`, `--sync-deletes`.      |
| `publish`       | `pub` | Human  | Final checklist: review deploy, `git commit && push` on target                                         |

### Examples

```
/docsmith help
/docsmith init                                       # one-time setup
/docsmith module instances                           # add a module
/docsmith intake-help                                # browse intake field reference

# Edit documentation/intake/project.md and modules/instances.md, then:
/docsmith run                                        # full pipeline, pauses at after-draft
/docsmith continue                                   # resume after review
/docsmith deploy --dry-run
/docsmith deploy

# Update flow when sources change:
/docsmith update                                     # check all modules
/docsmith update instances                           # one module
```

## Process flow

```
init (once) → module <n> (per module) → fill intakes → run → [pause: review] → continue → deploy → publish
                                                   │
                                                   └─ Underlying stages (auto-chained by run):
                                                      audience → plan → voice → draft → edit
                                                      → walkthrough → [record] → translate → categorize
```

For multi-locale projects, `translate` runs as part of the pipeline and is required before `deploy`. Deploy with empty target locale drafts emits a warning.

For maintenance: `/docsmith update` detects external source changes and proposes targeted re-drafts.

## Configuration

v1.5.0 splits config into 3 layers:

1. **Defaults** — from preset (`standalone` or `docusaurus`)
2. **Project intake** — `documentation/intake/project.md` ([template](templates/PROJECT_INTAKE_TEMPLATE.md))
3. **Module intake** — `documentation/intake/modules/<n>.md` ([template](templates/MODULE_INTAKE_TEMPLATE.md))

Higher layers override lower for the same field. Sources are cumulative.

Intake forms are markdown with checkboxes and backtick fields — no YAML to write. AI parses them deterministically. See [intake-reference.md](intake-reference.md) for parsing rules.

A legacy `.docsmithrc.yaml` is still read for backward compat with v1.4.x but deprecated; new projects use intake forms only.

## Path scoping (safety)

Every command validates that absolute write paths fall inside one of:

- `documentation/` (workspace — includes `documentation/deployments/` audit trail and `documentation/.run-state/` orchestration state)
- `deploy.target_path` from project intake (or `--target` override) — for `deploy` command only

Writes outside these roots are rejected. This is the core safety guarantee.

**Why deployments lives inside `documentation/`** (changed in v1.5.1): in in-place mode where `deploy.target_path = .`, having a top-level `deployments/` folder would clutter the host project root and risk colliding with user-named folders. Keeping it nested ensures docsmith's footprint at the project root is exactly one folder: `documentation/`.

## Re-run protocol (safety)

Every command that produces output checks for existence first. If output exists:

1. **Update** (recommended for content) — read existing as KB, propose deltas, apply per item. Untouched content preserved verbatim.
2. **Overwrite** — discard existing (archived to `archive/<ts>/`), generate fresh. Requires explicit "OVERWRITE" confirmation.
3. **Side-by-side** — keep both, new file gets suffix `-v2` / `-v3`.
4. **Cancel** — abort.

Default: `prompt` (always ask). Configurable via intake `Auto-run behavior` or legacy `behavior.on_existing`.

**Critical rule for Update mode**: read existing as canonical KB and propose deltas only (NEW / UPDATE / REMOVE / KEEP). Do NOT regenerate untouched sections — that loses team's manual edits.

## Command details

### `help`

Print the command table above. No other action.

### `init` (AI)

**Purpose**: scaffold a docsmith workspace at the current directory. One-time setup.

**Pre-checks** (1.5.1+):

1. If a `documentation/` folder already exists at the current directory:
   - Inspect its contents. If it has files NOT matching docsmith's structure (e.g., user-authored docs), STOP and report. Suggest `--force` only after the user moves or backs up content.
   - If contents match docsmith structure (intake/, plan/, etc.) → re-run protocol gate.
2. If running in a directory with a `docusaurus.config.{js,ts,mjs}` AND user did NOT specify `--target`:
   - Suggest in-place mode and confirm with user
   - If confirmed: set `deploy.target_path = .` in pre-fill
   - If declined: ask for sibling target path
3. If running in a directory with a `package.json` AND no `docusaurus.config`:
   - This is an unrelated Node project. Confirm intent before scaffolding.
4. If running in a non-empty directory with no recognizable config:
   - List existing folders/files. Ask user to confirm or move first. Refuse to scaffold next to user content silently.

**Behavior**:

1. Detect host project context (per pre-checks): `docusaurus.config.{js,ts,mjs}` present → suggest `docusaurus` preset; otherwise `standalone`
2. Inspect target if Docusaurus: read `<target>/CLAUDE.md`, parse `docusaurus.config` for paths
3. Create directory structure (see § File organization below). All paths are inside `documentation/`.
4. Create or update `.gitignore` (1.5.1+):
   - If `.gitignore` exists at project root: APPEND a docsmith block (between `# BEGIN docsmith` and `# END docsmith` markers). Don't duplicate entries on re-run.
   - If no `.gitignore`: create one with the docsmith block.
   - Entries added:
     ```
     # BEGIN docsmith
     documentation/.cache/
     documentation/videos/raw/
     documentation/.run-state/
     # END docsmith
     ```
5. Pre-fill `project.md` with detected values (product slug from package.json or directory name; deploy target from inspected Docusaurus path; etc.)
6. Print: "Workspace scaffolded. Edit documentation/intake/project.md, then run `/docsmith module <n>` for each feature area."

**Flags**:
- `--upgrade-from-1.4` — read existing `.docsmithrc.yaml` and pre-fill `project.md` from it; keep yaml for compat (deprecated)
- `--force` — overwrite existing intake files (requires confirm)
- `--in-place` — explicitly request in-place mode (skip prompt when in Docusaurus repo)
- `--reformat-intake` — re-render existing intake files with current template (preserves filled values; backup at `.backup-pre-<version>/`)
- `--from-source <path-or-url>` (v1.5.9+) — AI auto-fills intake from source document(s). Multiple sources comma-separated. See "From-source mode" below.
- `--resume` (v1.5.10+) — retry previously failed parallel sub-agents from last `init --from-source` run with >5 modules. Only applicable when last run reported partial completion.

#### From-source mode (v1.5.9+)

Use `--from-source` to skip manual intake authoring. AI reads BA doc / PRD / existing docs, infers fields, and writes `project.md`. Workflow:

1. **Fetch source(s)** using existing fetch logic (Notion / GitHub / GDrive / URL / file)
2. **Infer fields** by category:
   - **Facts** (high confidence): direct quotes from source — product name, audience role, module names, feature lists
   - **Guesses** (medium confidence): inferred from context — primary goal, voice tone, scope details. Marked `← AI guess` in intake
   - **Defaults** (no source data): conservative fallback per template default. Marked `← default applied`
3. **Interactive Q&A** for fields that source doesn't cover:
   - Source language (from BA doc language, but always asks to confirm)
   - Target locales (translation strategy)
   - Deploy preset and target path
   - Walkthrough credentials (env var names)
   - Voiceover strategy (if videos planned)
   - Pause gate preference for first run
4. **Write `project.md`** with inline `> Auto-filled from <source>: "<quote>"` annotations and `← AI guess` markers on uncertain fields
5. **Detect modules** from source structure (sections, headings) and prompt user: "Create module intake for each? Y/N/select"
6. **Generate inference report** at `documentation/intake/.inference/<timestamp>-project.md` (see [templates/INTAKE_INFERENCE_REPORT_TEMPLATE.md](templates/INTAKE_INFERENCE_REPORT_TEMPLATE.md))
7. **Print summary**:
   ```
   ✓ Created project.md (8 facts, 4 guesses, 7 defaults, 3 asked)
   ✓ Detected 2 modules: instances, storage
   ⚠ 4 fields marked "← AI guess" — please verify before /docsmith run
   📋 Inference report: documentation/intake/.inference/<timestamp>-project.md
   ```

**Re-run with `--from-source`** (when source updates):
- Existing intake values that match AI's last inference → safe to re-infer
- Existing intake values BA edited manually → preserved (hash check)
- Show diff before applying. Re-run protocol gate (Update / Overwrite / Skip).

### `module` (AI)

**Purpose**: manage module intake files.

**Sub-commands**:

```
/docsmith module <n>                          # create new module
/docsmith module <n> --from <existing>        # clone from another module
/docsmith module <n> --from-source <path>     # AI auto-fill from source (v1.5.9+)
/docsmith module list                         # list modules with status
/docsmith module archive <n>                  # mark as archived (skip in run)
/docsmith module unarchive <n>                # un-archive
```

**Create behavior**:
1. Re-run protocol check on `documentation/intake/modules/<n>.md`
2. Copy `templates/MODULE_INTAKE_TEMPLATE.md` to that path
3. Pre-fill module slug, display name from argument
4. If `--from <existing>`: copy non-identity fields from `<existing>` (sources, voice override, etc.)
5. If `--from-source <path>`: AI auto-fills features and content types from source (same logic as `init --from-source` but scoped to one module). Generates inference report at `.inference/<timestamp>-<module>.md`. Asks user about scope when ambiguous: "Source mentions 'snapshot' under Storage — include in this module's scope? Y/N"
6. Update project.md `Module intake files` section (between BEGIN/END MODULES LIST markers)
7. Print: "Module '<n>' created. Edit and run `/docsmith run <n>` when ready."

### `intake-help` (—)

Print intake field reference. No file changes.

```
/docsmith intake-help                # all fields
/docsmith intake-help product        # one section
/docsmith intake-help sources        # source types and auth
```

For each field: name, what it controls, validation rules, default value.

### `fetch` (AI)

**Purpose**: pull content from external knowledge sources declared in intakes. Manual; usually called automatically by `run` and `update`.

**Prerequisites**: env vars set for any auth-required sources (Notion, private GitHub, GDrive). See [SETUP.md](../../SETUP.md) — section "Environment variables for sources and credentials".

**Flags**:
- (no args) — fetch all sources for project + all active modules
- `--module <n>` — only this module
- `--source <id>` — only this source

**Per-type behavior**: see [intake-reference.md](intake-reference.md) § "External source fetching".

After fetch: writes content to `documentation/.cache/sources/<source-id>.{md,dir}`, updates `sources.lock.yaml`.

### `run` (AI) — orchestrated pipeline

**Requires**: filled project + module intake; env vars set for sources/credentials in scope.

**Workflow**:

1. Validate intakes (see [intake-reference.md](intake-reference.md) § Validation). Stop on critical errors.
2. Resolve layered config; snapshot to `documentation/deployments/<ts>/resolved-config.yaml`.
3. Call `fetch` internally (uses lock file if recent).
4. Run pipeline stages in sequence: `audience` → `plan` → `voice` → `draft` → `edit` → `walkthrough` → `record` → `translate`.
5. Pause at the configured gate (default: `after-draft`).
6. Save state to `documentation/.run-state/<module>.yaml` (per-module, not global — allows multiple modules to be in different stages simultaneously). For multi-module runs, each module gets its own state file.
7. Print resume instructions.

**Flags**:
- `[<module>]` — single module instead of all
- `--pause-at <gate>` — override the configured pause point
- `--from <stage>` — start from a specific stage (e.g. `--from walkthrough` to skip planning)

**Pause gates**: `after-plan`, `after-draft` (default), `before-walkthrough`, `after-walkthrough`, `before-deploy`, `never`.

### `continue` (AI)

Resume from `documentation/.run-state/<module>.yaml`.

- `/docsmith continue` (no args): if exactly one module has paused state, resume it. If multiple, list them and ask which to resume. If none, error.
- `/docsmith continue <module>`: resume specific module's state.

If state stale (>7 days) or workspace modified outside docsmith since last `run`, warn before resuming.

### `audience` / `plan` / `voice` / `draft` / `edit`

Individual pipeline stages. Each:

- Reads resolved config from intake
- **Interactive fill** (v1.5.13+): if a stage requires an empty intake field, AI prompts user inline and writes the answer back to intake. Avoids upfront full-form fill. See [intake-reference.md § 10](intake-reference.md) for per-stage required fields and prompt format.
- Re-run protocol applies (if output exists, gate)
- Writes to its conventional output path
- Returns control (does NOT chain to next stage; that's `run`'s job)

**Skip prompts with `--no-prompt`**: any stage command accepts `--no-prompt` flag. Behavior: fail immediately if a required field is empty (old behavior). Useful for CI scripts that shouldn't pause for user input.

Specific behaviors:

**`audience`** — output: `documentation/plan/audience-profile.md` from [templates/AUDIENCE_PROFILE_TEMPLATE.md](templates/AUDIENCE_PROFILE_TEMPLATE.md). Uses intake `Audience` section.

**`plan`** — outputs: `documentation/plan/documentation-plan.md` (from [templates/DOCUMENTATION_PLAN_TEMPLATE.md](templates/DOCUMENTATION_PLAN_TEMPLATE.md)) AND `documentation/plan/sitemap.md`. Uses intake `Scope` (from each module). Sitemap follows the project pattern (Pattern A/B/C from project intake § Sitemap pattern) and the per-module section selection. AI warns when a module is missing a section the project pattern includes, but doesn't auto-fix. See [templates/SITEMAP_PATTERNS_TEMPLATE.md](templates/SITEMAP_PATTERNS_TEMPLATE.md) for canonical section types and patterns.

Flags:
- `--migrate-sitemap` — for v1.5.3-or-earlier workspaces: AI proposes a pattern, asks to confirm, and updates project + module intakes to use the new sitemap system.

**`voice`** — outputs: `documentation/standards/voice-chart.md` from [templates/VOICE_CHART_TEMPLATE.md](templates/VOICE_CHART_TEMPLATE.md). With `--full`, also generates UX text patterns and content scorecard (these were standard in v1.4.x; now opt-in for lean default).

**`draft`** — outputs: `documentation/drafts/<source-locale>/<feature>/<doc>.md`. Reads cached sources from `.cache/sources/`. Uses [templates/CONTENT_TYPE_TEMPLATES.md](templates/CONTENT_TYPE_TEMPLATES.md). Image refs: workspace-absolute paths `/images/<feature>/<asset>.png`. Caption rules per [templates/MEDIA_POLICY_TEMPLATE.md § 3.5](templates/MEDIA_POLICY_TEMPLATE.md). Video markers per [templates/VIDEO_SCRIPT_TEMPLATE.md § VIDEO marker](templates/VIDEO_SCRIPT_TEMPLATE.md).

**`edit`** — five passes: voice match, UX patterns, clarity, accuracy markers, link/cross-ref. With `--from-review <file>`, applies a reviewer's feedback file (Markdown with `// FEEDBACK:` annotations or block comments).

### `walkthrough` (AI)

**Prerequisites**: browser automation tool (Claude in Chrome extension OR Playwright MCP) AND test account credentials set as env vars. See [SETUP.md](../../SETUP.md) — section "Path 1: Claude in Chrome" or "Path 2: Playwright MCP".

**Interactive fill (v1.5.13+)**: if product URL or credentials env vars are empty in intake, AI prompts user inline and writes back. Verifies env vars are actually set in shell before proceeding. See [intake-reference.md § 10](intake-reference.md) — section "walkthrough" required fields.

**Media policy**: respects screenshot density rules and per-locale strategy from project intake § 11 (and module intake § 8 overrides). Default behavior is "source-only" capture (one screenshot reused across all locales). See [templates/MEDIA_POLICY_TEMPLATE.md](templates/MEDIA_POLICY_TEMPLATE.md) for density rules per content type, style options, and aspect ratio.

Three-phase pipeline:

```
A: VERIFY    /docsmith wt --check         → drift report (read-only)
   ↓
   GATE      Edit decisions.yaml          (auto-fix / manual-fix / product-bug / skip)
   ↓
B: APPLY     /docsmith wt --apply         → update drafts per decisions
   ↓
C: CAPTURE                                 → screenshots, replace placeholders
```

**Default mode** (no flag): runs A → interactive gate → B → C.

**Flags**:
- `--check` — Phase A only; fast (~30s); for drift monitoring
- `--apply` — B + C with existing decisions
- `--skip-drift` — C only; for first runs or known-clean drafts
- `--auto-apply-high-confidence` — skip gate, auto-apply HIGH-confidence fixes
- `--locale <locale>` — verify against a translated locale (requires product UI in that locale)

Drift report format: [templates/DRIFT_REPORT_TEMPLATE.md](templates/DRIFT_REPORT_TEMPLATE.md). Test cases: [templates/WALKTHROUGH_TEST_CASE_TEMPLATE.md](templates/WALKTHROUGH_TEST_CASE_TEMPLATE.md).

Items marked `product-bug` tracked in `walkthrough/active-product-bugs.yaml` across runs; auto-resolved when UI matches doc.

### `record` (AI)

**Prerequisites**: same as `walkthrough` PLUS ffmpeg installed for video encoding. If voiceover strategy is "AI synthetic voice", also need TTS provider configured (project intake § 11). For local TTS (default): Piper or Coqui binaries installed. For remote TTS: API auth env var set. See [SETUP.md](../../SETUP.md) — section "Path 3: For `record` (tutorial videos)".

**Interactive fill (v1.5.13+)**: if voiceover strategy = "AI synthetic voice" and TTS provider/voice ID not set, AI prompts inline and writes back. Silent strategy (default) requires no prompts. See [intake-reference.md § 10](intake-reference.md) — section "record" required fields.

**Media policy**: respects video density rules, length caps, voiceover strategy, and TTS provider from project intake § 11 (and module intake § 8 overrides). Default behavior is "Silent + on-screen captions" (no audio, no TTS needed). See [templates/MEDIA_POLICY_TEMPLATE.md](templates/MEDIA_POLICY_TEMPLATE.md) § 4-7 for full options.

**Script files (v1.5.7+)**: each video has its own script file at `documentation/scripts/<module>/<id>.md`. Script contains source-language narration plus per-locale translations. Voiceover (TTS or human) reads from this file. See [templates/VIDEO_SCRIPT_TEMPLATE.md](templates/VIDEO_SCRIPT_TEMPLATE.md) for format.

**Workflow**:

1. Scan drafts for `<!-- VIDEO id: <id> -->` markers
2. For each marker, look up `documentation/scripts/<module>/<id>.md`:
   - If missing → AI generates initial script from surrounding draft prose, saves to file, pauses for user review
   - If exists but stale (draft section changed >20%) → warn user
3. User reviews/edits script file
4. On confirm: TTS generates audio per locale (skipped if silent), capture screen, encode video
5. Replace VIDEO marker with `<video>` embed; preserve marker as comment for re-record

**Translate integration (v1.5.7+)**: `translate` command processes script files alongside drafts. Translates `# Source script` content into `## <locale>` sections in same file. Same per-block / batch review gate.

**Flags**:
- `--migrate-scripts` — for v1.5.6-or-earlier drafts: extract inline scripts from VIDEO markers, create new script files, simplify markers
- `--check` — validate script files exist for all VIDEO markers; report missing/stale; no audio/video generation
- `--re-record <id>` — force re-record of one video even if cached. See [templates/VIDEO_SCRIPT_TEMPLATE.md](templates/VIDEO_SCRIPT_TEMPLATE.md) for marker syntax and per-video script format.

After recording: replaces marker with `<video>` embed, preserves marker as comment for re-record.

### `translate` (AI)

**Required** when `locales.targets` non-empty. Position: after `edit`, before `deploy`.

**Interactive fill (v1.5.13+)**: if `locales.targets` is empty, AI prompts user to pick target languages and writes back to project intake § 3. See [intake-reference.md § 10](intake-reference.md) — section "translate" required fields.

**Default review mode**: `batch` (whole-file diff review). User can opt into `--per-block` for safer per-block review.

**Block-level rules** and full workflow: [translate-reference.md](translate-reference.md).

Glossary file (per locale): `documentation/standards/glossary.<locale>.yaml` ([templates/GLOSSARY_TEMPLATE.yaml](templates/GLOSSARY_TEMPLATE.yaml)). Optional but recommended.

**Flags**:
- `[<module>]` — single module
- `--locale <locale>` — single target locale
- `--per-block` — per-block review gate (slower, safer)
- `--auto-approve` — skip review entirely (CI/bulk only)
- `--glob <pattern>` — only matching files

### `verify` (AI)

**Default 11 checks** (always run):

1. No `placehold.co` URLs remain
2. No broken image refs
3. Voice consistency score ≥ threshold
4. Glossary consistency (translated docs)
5. Code blocks unchanged across translations
6. Frontmatter complete
7. Links resolve (internal)
8. Cross-references valid
9. Sitemap entries match draft files
10. Sitemap consistency: all modules use the project pattern; warns when module is missing a section the project pattern includes (non-blocking; **blocking with Pattern D — FPT mandatory sections enforced**)
11. Media compliance (v1.5.5+): screenshots match density policy per content type; videos within length caps; voiceover/subtitle files exist when strategy expects them; per-locale media follows project strategy

**FPT compliance checks 12-22** (v1.6.0+): activated when project intake has `compliance: fpt-user-guide`. See [templates/FPT_TEMPLATES.md § Part 4](templates/FPT_TEMPLATES.md) for full rules.

12. **Page titles** (4.1): sentence case, ≤60 chars, no period/colon at end
13. **Section headings** (4.2): not numbered, parallel structure within same level
14. **Introductions** (4.3): ≤2 sentences, lead with user benefit, second person
15. **Prerequisites** (4.4): plain bullets, no ✅ emoji
16. **Procedures** (4.5): numbered list, ≤10 steps, each step starts with verb
17. **Code examples** (4.13): language tag present, SCREAMING_SNAKE_CASE placeholders, ≤20 lines per block
18. **Button labels** (4.7): no `Click here`, `Nhấn vào đây`
19. **UI references** (4.12): buttons in bold, navigation paths use `→`
20. **Callouts** (4.6): ≤2 per section, correct emoji per type (💡/📝/⚠️/🚨)
21. **Status messages** (4.8-4.9): success/error/loading/empty-state use canonical templates
22. **Anti-AI-tells** (4.15) — CRITICAL: 6 sub-checks
    - No ✅ ❌ emoji outside callouts
    - Em-dashes ≤1 per paragraph
    - No `...đặc biệt khi X mở rộng qua Y` intro formula
    - Parallel structure varies naturally (not all bullets ±10% same length)
    - `Bước tiếp theo` not rigidly 3 items
    - Verification step used when needed, not rigid in every flow

Checks 12-22 BLOCK deploy when `compliance: fpt-user-guide`. Override: `--force-deploy`. For non-FPT projects, checks 12-22 are skipped.

**Flags**:
- `[<doc-glob>]` — scope to specific docs (faster iteration)
- `--locale <locale>` — verify a target locale's drafts
- `--fpt-only` — run only checks 12-22 (skip 1-11; faster iteration when fixing FPT violations)
- `--no-fpt` — run only checks 1-11 (skip 12-22; for non-FPT projects regardless of compliance field)

### `score` (AI) — v1.6.0+

**Purpose**: quality scoring against FPT Cloud content standards. 10 criteria × 0-2 = max 20 points. See [templates/SCORECARD_TEMPLATE.md](templates/SCORECARD_TEMPLATE.md) and [templates/FPT_TEMPLATES.md § Part 7](templates/FPT_TEMPLATES.md).

**When to use**:
- Required when project intake has `compliance: fpt-user-guide` (deploy blocked until pass)
- Optional otherwise (still useful as quality check)
- Run after `verify` passes, before `deploy`

**Behavior**:

1. For each draft in scope (module or specific doc):
   - AI reads draft
   - Evaluates each of 10 criteria, assigns 0/1/2
   - Lists evidence per criterion
   - Lists fix suggestions for criteria scoring <2
   - Runs anti-AI-tells checklist (6 patterns)
2. Writes per-doc report: `documentation/score/<module>/<doc>.md`
3. Writes module summary: `documentation/score/<module>/_summary.md`
4. Exit:
   - All docs ≥14 AND no anti-AI-tells violations → success, deploy unblocked
   - Any doc <14 OR any anti-AI-tells violation → fail, list issues, deploy blocked

**Deploy gate**:
- `deploy` runs `score` automatically if `compliance: fpt-user-guide` set
- If gate fails, `deploy` refuses (override: `deploy --force-deploy`)
- Score reports persisted for audit

**Scoring tiers**:
- 0-8: Poor — rewrite needed
- 9-13: Fair — major edits needed
- 14-17: Good — publishable (deploy-ready)
- 18-20: Excellent — ready to publish

**Flags**:
- `<module>` — score one module (default: all modules)
- `[<doc-glob>]` — scope to specific docs
- `--locale <locale>` — score translated locale (default: source locale only)
- `--no-anti-ai-tells` — skip anti-AI-tells checklist (still scores 10 criteria)
- `--fix` — when criterion <2, AI auto-attempts fix and re-scores (experimental)

### `update` (AI)

**Purpose**: detect external source changes and propose draft updates without re-fetching everything. As of v1.5.10, also detects new/orphan modules in source structure.

**Workflow**:
1. Read `sources.lock.yaml`
2. For each source, do cheap metadata check (Notion edit time, GitHub commit SHA, GDrive revision, URL ETag, file mtime)
3. Build change report (3 layers):
   - **Content drift**: source content changed → affected drafts to re-evaluate
   - **Module diff** (v1.5.10+): modules in source vs in workspace; categorize as new/orphan/scope-drift
   - **Scope drift** (v1.5.10+): existing module's features list lags source
4. User reviews via interactive prompt; picks actions
5. On confirm:
   - Full-fetch changed sources
   - Create new module intakes (with `--from-source` auto-fill)
   - Archive orphan modules (`status: archived`)
   - Update scope-drift module features
   - Re-run `draft` in Update mode for affected docs (KB inheritance)
   - Re-run `wt --check` for new drift
6. Update lock file
7. Generate update inference report at `documentation/intake/.inference/<ts>-update.md`

See [intake-reference.md](intake-reference.md) § 9.10 "Missing module detection" and § 5 "The `update` command — change detection".

**Multi-module performance** (v1.5.10+): when ≥5 modules need processing (new + scope-drift combined), AI MAY use Task tool to spawn parallel sub-agents. Sequential fallback for ≤5 modules. See [intake-reference.md](intake-reference.md) § 9.9.

**Flags**:
- (no args) — check all sources from sources.lock; full diff (content + module structure)
- `<module>` — one module only (skip module structure detection)
- `--from-source <path>` — re-register a source URL/path (overrides sources.lock entry)
- `--no-modules` — content drift only; skip module structure detection (faster)
- `--auto-apply` — fetch and apply all changes without prompt (CI use)
- `--resume` — retry previously failed parallel sub-agents (if last run had partial completion)

### `categorize` (AI) — Docusaurus categories

Generate `_category_.json` from sitemap. Normalize titles (acronyms uppercase: API, CLI, JSON, etc.; articles lowercase mid-title; first/last word capitalized).

Sidebar position is computed from the sitemap pattern: section types appear in the project pattern's defined order (Pattern A/B/C from project intake). Within a section, individual docs are ordered per the sitemap entries (typically by feature priority).

Display labels respect project intake `Section display names` overrides. Slugs (folder names) stay canonical.

Auto-runs on `deploy` if `generate_categories: true` (Docusaurus preset default). Can run standalone for re-categorization.

See [deploy-reference.md](deploy-reference.md) § "Categorize subcommand", [templates/CATEGORY_FILE_TEMPLATE.md](templates/CATEGORY_FILE_TEMPLATE.md), and [templates/SITEMAP_PATTERNS_TEMPLATE.md](templates/SITEMAP_PATTERNS_TEMPLATE.md) for section ordering.

### `deploy` (AI)

Copy/sync workspace to host project with transforms (frontmatter injection, image namespacing `/img/<slug>/`, MDX escape, category generation).

**FPT compliance gate (v1.6.0+)**: when project intake has `compliance: fpt-user-guide`:
1. `verify` checks 12-22 must pass (anti-AI-tells included)
2. `score` must show all docs ≥14 (Good tier minimum)
3. Both auto-run before deploy starts
4. Failure → deploy refuses; lists issues
5. Override: `--force-deploy` (logs warning, proceeds anyway)

**Flags**:
- `--dry-run` — detect + plan, exit without writes
- `--target <path>` — override `deploy.target_path` for this run
- `--force` — override conflicts
- `--force-deploy` (v1.6.0+) — skip FPT compliance gate (verify checks 12-22 + score). Use with caution; logs warning to deployment manifest.
- `--locale <locale>` — single locale
- `--sync-deletes` — propagate workspace deletions to target (default: report orphans only)

**Workflow** (full detail: [deploy-reference.md](deploy-reference.md)):
1. **FPT compliance gate (if applicable)**: run `verify --fpt-only` + `score`; block on fail
2. Translation completeness check (warn if `locales.targets` has incomplete translations)
3. Detect target context (CLAUDE.md, docusaurus.config.*, folder signals)
4. Plan file actions (create / update / skip / conflict / delete-if-sync)
5. Show plan; if `--dry-run`, exit
6. Apply if no unresolved conflicts; create audit folder under `documentation/deployments/`
7. Save manifest, target-config snapshot, diff, pre-deploy hashes

### `publish` (Human)

Final checklist:
1. Review the deploy summary and target diff
2. Coordinate with code/product release if applicable
3. In target project: `git diff` → `git add` → `git commit` → `git push`
4. Trigger documentation platform build if not auto-triggered
5. Verify live site
6. Announce

AI does NOT auto-commit. Git on target is the safety net.

## File organization

docsmith's footprint at the project root is **exactly one folder: `documentation/`**. Everything else lives inside it.

```
<project-root>/
└── documentation/
    ├── intake/
    │   ├── project.md                  # Layer 1
    │   ├── modules/
    │   │   ├── instances.md            # Layer 2
    │   │   └── storage.md
    │   └── sources.lock.yaml           # Auto-managed
    ├── plan/
    │   ├── audience-profile.md
    │   ├── documentation-plan.md
    │   └── sitemap.md
    ├── standards/
    │   ├── voice-chart.md
    │   ├── screenshot-policy.md
    │   ├── glossary.vi.yaml            # Optional, per locale (path is fixed: documentation/standards/glossary.<locale>.yaml)
    │   └── glossary.jp.yaml
    ├── drafts/
    │   ├── en/                         # Source locale
    │   │   ├── instances/              # = module.folder (default = module.slug)
    │   │   │   ├── create.md
    │   │   │   ├── list.md
    │   │   │   └── auto-scaling.md     # Multiple docs per module
    │   │   └── storage/
    │   │       └── overview.md
    │   └── vi/                         # Translated by `translate`, mirrors EN structure
    │       └── instances/
    │           └── create.md
    ├── walkthrough/
    │   ├── test-cases/
    │   ├── video-plan/
    │   ├── executions/
    │   ├── drift/<ts>/
    │   └── active-product-bugs.yaml
    ├── archive/<ts>/                   # Re-run protocol backups
    ├── images/
    │   └── instances/                  # = module.folder
    │       ├── create-form-filled.png       # source-locale (default)
    │       └── vi/                          # per-locale override (when project = per-locale)
    │           └── create-form-filled.png
    ├── scripts/                        # v1.5.7+: per-video scripts
    │   └── instances/                  # = module.folder
    │       ├── instance-create-tour.md      # source script + per-locale translations
    │       └── auto-scaling-tour.md
    ├── videos/
    │   ├── raw/                        # Gitignored
    │   ├── instance-create-tour.mp4    # final video (silent default)
    │   ├── voiceover/                  # When voiceover strategy = AI or human
    │   │   ├── instance-create-tour.en.mp3
    │   │   ├── instance-create-tour.vi.mp3
    │   │   └── instance-create-tour.jp.mp3
    │   └── subtitles/                  # When subtitles enabled
    │       ├── instance-create-tour.en.vtt
    │       ├── instance-create-tour.vi.vtt
    │       └── instance-create-tour.jp.vtt
    ├── deployments/                    # Audit trail (1.5.1+: moved INSIDE documentation/)
    │   └── <ts>-<target>/
    │       ├── manifest.yaml
    │       ├── target-config.yaml
    │       ├── diff.md
    │       ├── resolved-config.yaml
    │       ├── pre-deploy-state.txt
    │       └── deleted/                # Backup of removed target files (--sync-deletes)
    ├── .cache/
    │   └── sources/                    # Gitignored
    │       ├── notion-abc123.md
    │       └── github-mycloud-cloud-arch/
    └── .run-state/                     # 1.5.1+: per-module orchestration state
        ├── instances.yaml              # Run state for `instances` module
        └── storage.yaml                # Run state for `storage` module
```

### Path rules

- **`<feature>` = `module.folder`** (which defaults to `module.slug`). For module `instances` with default folder, drafts go in `drafts/en/instances/`, images in `images/instances/`, target in `<deploy_target>/docs/instances/`.
- **Multiple docs per module** are normal: tutorial, how-to, reference, concept docs all live under the same module folder. The `Features to document` section in module intake drives how many.
- **Glossary path is fixed**: `documentation/standards/glossary.<locale>.yaml`. Not configurable in v1.5.x. AI looks for it at exactly this path.
- **In-place mode** (`deploy.target_path = .`): workspace `documentation/` and target `docs/`/`i18n/`/`static/` are siblings inside the Docusaurus repo. Both managed by docsmith but only `documentation/` is fully owned.

Standalone preset: workspace IS the publishable artifact, no target.
