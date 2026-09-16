# Intake Reference

Detailed logic for the intake system introduced in v1.5.0: project-level + module-level intake markdown forms, layered config resolution, source fetch/update, and the `run` / `continue` orchestration commands.

SKILL.md references this file. Read alongside [translate-reference.md](translate-reference.md), [deploy-reference.md](deploy-reference.md), and [update-reference.md](update-reference.md).

## Why intake exists

Before v1.5.0, every command asked the user for context interactively. This works for one-off use but doesn't scale:

- BAs who don't know YAML can't fill `.docsmithrc.yaml` confidently
- Re-running a command repeats the same questions
- No single place to see what AI knows about the project
- Hard to share context across modules without copy-paste

v1.5.0 introduces **two markdown intake files** that BAs can fill comfortably (checkboxes, fillable backtick fields), and an **AI parser** that reads them deterministically. Project intake is global; module intake is per-feature-area.

## File layout

```
documentation/
├── intake/
│   ├── project.md                    # Layer 1 — global config
│   ├── modules/
│   │   ├── instances.md              # Layer 2 — per-module override
│   │   └── storage.md
│   └── sources.lock.yaml             # Auto-managed — fetch state
├── .cache/
│   └── sources/                      # Gitignored — fetched content cache
│       ├── notion-abc123.md
│       └── github-mycloud-cloud-arch/
└── ... (drafts/, plan/, walkthrough/, etc.)
```

`project.md` is created by `init`. Module files are created by `module <name>`. The lock file is created on first `fetch` or `run`.

---

## 1. Markdown form parsing

Forms use 3 input primitives that AI parses deterministically:

### Backtick fields

```markdown
- Product slug: `mycloud`
```

Regex: `^- (?:[*\d.\s]*)?(.+?):\s*\`(.*)\`\s*$`

Extracted: key = `Product slug`, value = `mycloud`.

If the value is the placeholder default (e.g., `your-product-slug`, `Product Name Here`, `e.g., DevOps Engineer`), treat as empty.

### Checkboxes

```markdown
- [x] Docusaurus
- [ ] Standalone
```

Regex per line: `^\s*-\s*\[([ x])\]\s*(.+?)$`

In a single-select group (group of consecutive `- [ ]` lines under one section), exactly one MUST be checked. If zero or multiple checked → validation error.

In a multi-select group (e.g., target locales), zero or more may be checked.

The header preceding the group disambiguates single vs multi-select. Forms in this skill use natural-language hints: "Source language" implies single, "Target languages (translate to)" implies multi. Module/feature templates make the type explicit in template comments.

### Repeating sections

```markdown
### Source 1

- Type:
  - [ ] Notion page
  - [x] GitHub repo
- URL or path or ID: `mycloud/cloud`

### Source 2

- Type:
  - [x] Notion page
- URL or path or ID: `https://notion.so/abc123`
```

Pattern: `### Source N` (or `#### Feature N`) where N is a positive integer. AI iterates through these blocks in order, stops when it hits a section that has only empty backticks AND zero ticked checkboxes (treats as "user copy-pasted the template but didn't fill it").

### What AI does NOT parse

- Free prose between fields (treated as comments, ignored unless inside an `auto-update` region)
- HTML comments `<!-- ... -->` (treated as instructions to the BA, ignored by parser)
- Code fences (preserved verbatim if a field type is "script", e.g. pre-walkthrough setup)

### `<details>` / `<summary>` blocks (v1.5.6+)

Project and module intake templates use HTML `<details>` blocks to collapse advanced sections. Render behavior:

- GitHub / VS Code preview: `<summary>` text shown; content collapsed, expandable on click
- Plain markdown viewer: all content shown
- Cursor / GitHub.dev: collapsed by default

AI parser treats `<details>` blocks as transparent:

1. Strip `<details>` opening tag and matching `</details>` closing tag
2. Strip `<summary>...</summary>` line entirely
3. Parse content inside as if no wrapper existed

Result: BA sees ~100 lines top-level (essential sections); ~250 lines total exists in file (advanced sections collapsed). AI sees full content for parsing.

When BA expands a `<details>` block and edits a field, AI picks up the edit normally. When BA leaves it collapsed, AI uses defaults documented in the section.

Example:

```markdown
## 4. Deploy (*)

Preset:
- [x] Standalone
- [ ] Docusaurus

<details>
<summary><b>Advanced — collision behavior</b> (using defaults)</summary>

When target file exists with different content:
- [x] Warn (default)
- [ ] Skip
- [ ] Overwrite
- [ ] Prompt

</details>
```

AI parses:
- `deploy.preset = standalone` (from top section)
- `deploy.on_collision = warn` (from inside `<details>`)
- BA didn't expand the details block; default tick `Warn` is taken

## 2. Layered config resolution

When a command runs `/docsmith run instances`, AI resolves config in this order:

```
1. Defaults (from preset standalone or docusaurus)
2. Project intake (documentation/intake/project.md)
3. Module intake (documentation/intake/modules/instances.md)
4. Command-line flags (highest priority)
```

Higher layers override lower for the SAME key. Sources are CUMULATIVE (project + module sources are concatenated, not replaced).

### Override examples

```
project.md:        voice.tone = friendly-professional
module.md:         voice.tone = technical-direct
                   ↓
resolved:          voice.tone = technical-direct
```

```
project.md:        sources = [notion-prd, github-arch]
module.md:         sources = [notion-instances-prd]
                   ↓
resolved:          sources = [notion-prd, github-arch, notion-instances-prd]
```

```
project.md:        deploy.preset = docusaurus
                   deploy.target_path = ../mycloud-docusaurus
module.md:         (not specified)
                   ↓
resolved:          deploy.preset = docusaurus
                   deploy.target_path = ../mycloud-docusaurus
```

### Resolved config snapshot

For audit, AI writes the resolved config to `documentation/deployments/<ts>/resolved-config.yaml` on every `run`. This lets you reconstruct what AI saw when generating any output.

### Path mapping: how module fields become folder paths

When `module.folder = instances` (defaulting from `module.slug = instances`), this single value drives multiple paths:

| Artifact                  | Path                                                                |
| ------------------------- | ------------------------------------------------------------------- |
| Module intake             | `documentation/intake/modules/instances.md`                         |
| Source-locale drafts      | `documentation/drafts/<source-locale>/instances/<doc>.md`           |
| Translated drafts         | `documentation/drafts/<target-locale>/instances/<doc>.md`           |
| Screenshot folder         | `documentation/images/instances/<asset>.png`                        |
| Video script (v1.5.7+)    | `documentation/scripts/instances/<asset-id>.md`                     |
| Video file                | `documentation/videos/<asset-id>.mp4`                               |
| Voiceover audio per locale| `documentation/videos/voiceover/<asset-id>.<locale>.mp3`            |
| Subtitle per locale       | `documentation/videos/subtitles/<asset-id>.<locale>.vtt`            |
| Test cases                | `documentation/walkthrough/test-cases/instances/<test>.md`          |
| Drift reports             | `documentation/walkthrough/drift/<ts>/instances-*.md`               |
| Run state                 | `documentation/.run-state/instances.yaml`                           |
| Deploy target (Docusaurus)| `<deploy_target>/docs/instances/<doc>.md`                           |
| Deploy target images      | `<deploy_target>/static/img/<product.slug>/instances/<asset>.png`   |
| Deploy target videos      | `<deploy_target>/static/videos/<product.slug>/<asset-id>.mp4`       |
| Deploy target i18n        | `<deploy_target>/i18n/<locale>/.../current/instances/<doc>.md`      |

**Each module produces multiple docs** (tutorial, how-to, reference, concept). The `Features to document` section in module intake drives how many. Example for `instances` module with two features:

- `Create instance` → `tutorial`, `how-to` content types → produces 2 docs
- `Auto-scaling` → `how-to`, `reference` content types → produces 2 docs

Final draft tree:
```
documentation/drafts/en/instances/
├── create-instance-tutorial.md
├── create-instance.md          (how-to)
├── auto-scaling.md             (how-to)
└── auto-scaling-reference.md
```

AI names files based on feature + content type, normalizing to kebab-case.

## 3. Validation (hybrid strictness)

Validation runs at the start of every command that consumes intake. Two levels:

### Critical fields → STOP

Missing → command halts with a list of fixes needed:

```
Cannot run /docsmith run: required intake fields missing.

Project intake (documentation/intake/project.md):
  ✗ Section 1 "Product": product slug is empty (placeholder unchanged)
  ✗ Section 4 "Deploy": no preset selected
  ✗ Section 6 "Credentials": username env var empty (required for walkthrough)

Module intake (documentation/intake/modules/instances.md):
  ✗ Section 2 "Scope": no features added (need at least one)
  ✗ Section 2 "Scope > Feature 1": no content type checked

Fix these and re-run, or run /docsmith intake-help for field reference.
```

Critical fields per intake type:

**project.md**:
- Section 1 (Product): slug, name
- Section 2 (Audience): primary persona role, technical level, primary goal
- Section 3 (Languages): source language exactly one ticked
- Section 4 (Deploy): preset exactly one ticked
- Section 6 (Credentials): username and password env vars (only if walkthrough is in pipeline)

**module.md**:
- Section 1 (Module identity): slug, display name, folder
- Section 2 (Scope): at least one feature with at least one content type ticked

### Nice-to-have fields → DEFAULT

Missing → AI applies a default and prints a note:

```
Note: voice.tone not specified in project.md. Using default: "friendly-professional".
Note: voice.perspective not specified. Using default: "second-person".
Note: reading_level not specified. Using default: "8th grade".
Note: 0 secondary personas defined. Proceeding with primary only.
```

Defaults table:

| Field                          | Default                       |
| ------------------------------ | ----------------------------- |
| `voice.tone`                   | `friendly-professional`       |
| `voice.perspective`            | `second-person`               |
| `voice.reading_level`          | `8th grade`                   |
| `voice.terms_to_avoid`         | (empty list)                  |
| `secondary_personas`           | (empty list)                  |
| `deploy.on_collision`          | `warn`                        |
| `deploy.sync_deletes`          | `false`                       |
| `auto_run.pause_at`            | `after-draft`                 |
| `auto_run.drift_action`        | `prompt`                      |
| `translate.review_mode`        | `batch`                       |
| `behavior.on_existing`         | `prompt`                      |

### `intake-help` command

```bash
/docsmith intake-help            # Show all intake fields and meanings
/docsmith intake-help <section>  # Show a specific section
```

Prints a reference of every field, what it does, validation rules, and default value. Useful when BA doesn't know what a field means.

---

## 4. External source fetching

Sources declared in intake forms are fetched by `/docsmith fetch` (manual) or automatically by `/docsmith run` / `/docsmith update`.

### Source types

| Type     | Required env var       | Auth method                             | Fetch what                          |
| -------- | ---------------------- | --------------------------------------- | ----------------------------------- |
| `notion` | `NOTION_TOKEN`         | Internal integration token              | Page content as markdown            |
| `github` | `GITHUB_TOKEN` (private) | PAT or app token (public: no auth)    | Files at paths, current commit SHA  |
| `gdrive` | `GOOGLE_DRIVE_TOKEN` or `GOOGLE_APPLICATION_CREDENTIALS` | OAuth2 token or service account | Doc content exported as markdown |
| `url`    | (none)                 | (none — public only)                    | HTML/markdown at URL                |
| `file`   | (none)                 | (none — local filesystem)               | File content                        |

### Fetch workflow

```
/docsmith fetch                  # Fetch all sources for project + all modules
/docsmith fetch --module instances
/docsmith fetch --source notion-abc123
```

For each source:
1. Look up auth env var (if needed); error if not set
2. Call API/HTTP/filesystem to fetch metadata + content
3. Compute content hash (SHA-256)
4. Write content to `.cache/sources/<source-id>.md` (or directory for multi-file sources)
5. Update entry in `sources.lock.yaml`

### Per-type fetch details

**Notion**:
- Use Notion API `pages/{id}` + `blocks/{id}/children` recursively
- Convert to markdown via standard converter (preserve headings, lists, code blocks, tables)
- Cache result; record `version` (Notion's edit version) and `last_edited_time`

**GitHub**:
- For paths with globs (`api/instances/*.ts`): use `repos/{owner}/{repo}/git/trees/{branch}?recursive=true`, filter by glob
- Fetch each matching file via `repos/{owner}/{repo}/contents/{path}`
- Cache as directory: `.cache/sources/<source-id>/<path>`
- Record `commit_sha` of latest commit on default branch (or specified branch)
- Per-file hashes for granular change detection

**Google Drive**:
- Use Drive API `files.export` with `mimeType=text/markdown` (or `text/plain` if doc has tables/images that don't export cleanly to MD)
- Record `revisionId` and `modifiedTime`

**URL**:
- HTTP GET with `User-Agent: docsmith/1.5.0`
- Save response body
- Record `ETag` and `Last-Modified` headers if present
- Content-Type matters: HTML → strip to readable text; markdown → save as-is

**File**:
- `cat` the file; record `mtime` and `size`
- No cache (read live each time it's needed)

### Auth env var resolution

Auth env vars are NEVER stored in intake or lock files. Only the env var NAME is. At fetch time:

```
1. Read source entry, get auth_env field
2. os.environ.get(auth_env) → token
3. If empty/missing → fail with clear error: "Set $NOTION_TOKEN before fetching"
```

Tokens never appear in logs, audit trails, or commits.

---

## 5. The `update` command — change detection

```bash
/docsmith update                 # Check all sources across all modules
/docsmith update <module>        # One module
```

Workflow:

1. Read `sources.lock.yaml` to get last-known state
2. For each source, do a CHEAP metadata check:
   - Notion: `GET /pages/{id}` → check `last_edited_time` vs locked
   - GitHub: `GET /repos/{owner}/{repo}/commits?path=...&per_page=1` → check latest SHA vs locked
   - GDrive: `files.get?fields=modifiedTime,headRevisionId` → check vs locked
   - URL: `HEAD` request → check `ETag` / `Last-Modified` vs locked
   - File: `stat` → check `mtime` vs locked
3. Build a change report:
   ```
   Module: instances
   
   Source changes detected:
     ~ notion://abc123 "Instances PRD"
       Version: v47 → v52 (5 edits since last sync 2 days ago)
     
     ~ github://mycloud/cloud api/instances/*.ts
       New commits: 3 (deadbeef → cafe1234)
       Files changed: create.ts, list.ts
     
     = gdrive://xyz789 "UX research notes" (no change)
     
     = file://../product-docs/feature-list.md (no change)
   
   Affected docs (will re-evaluate):
     documentation/drafts/en/instances/create.md
     documentation/drafts/en/instances/list.md
     documentation/drafts/en/instances/auto-scaling.md  (uses overall PRD context)
   
   Continue? [y/n/show-diff]
   ```
4. If user confirms:
   - Full-fetch changed sources; update cache and lock entry
   - Re-run `draft` in Update mode for affected docs (KB inheritance — read existing, propose deltas based on new source content)
   - Re-run `wt --check` to detect doc-vs-product drift on top of source-vs-doc drift
5. Print summary and what to do next

### Tracking which docs are affected by which sources

In v1.5.0 minimal: AI assumes ALL docs in a module are potentially affected by ANY source change in that module. Conservative but correct.

A future enhancement (v1.6+) is to track per-doc source provenance — "doc X was generated using sources A, B" — for surgical re-evaluation.

---

## 6. The `run` and `continue` commands

### `run` — orchestrated pipeline

```bash
/docsmith run                    # Run for all active modules
/docsmith run <module>           # One module
/docsmith run --pause-at <gate>  # Override pause_at from intake
```

Workflow:
1. Validate project + module intake (stop on critical errors)
2. Resolve config (layered)
3. Fetch sources (calls `fetch` internally; uses lock if recent enough)
4. Run pipeline stages in sequence:
   ```
   audience  →  plan  →  voice  →  draft  →  edit  →  walkthrough  →  record  →  translate
   ```
5. PAUSE at the configured gate (default: `after-draft`)
6. Save state to `documentation/.run-state.yaml`:
   ```yaml
   started_at: 2026-04-26T15:30:00Z
   module: instances
   completed_stages: [audience, plan, voice, draft, edit]
   paused_at: after-draft
   next_stage: walkthrough
   resolved_config_path: documentation/deployments/2026-04-26-153000/resolved-config.yaml
   ```
7. Print resume instructions: `Run /docsmith continue when ready`

### `continue` — resume after gate

```bash
/docsmith continue
/docsmith continue <module>
```

Workflow:
1. Read `.run-state.yaml`
2. If state stale (>7 days old): warn user, suggest re-validation before continuing
3. Resume from `next_stage`
4. Run remaining stages until next pause or end of pipeline
5. Update state on completion or new pause

### Pause gates

| Gate              | When pause occurs                      | What user does                          |
| ----------------- | -------------------------------------- | --------------------------------------- |
| `after-plan`      | After `plan` writes plan + sitemap     | Review plan, edit if needed             |
| `after-draft`     | After `edit` finishes                  | Review drafts, edit; default            |
| `before-walkthrough` | Before browser opens                | Confirm test account ready              |
| `after-walkthrough` | After capture, before record/translate | Review captured screenshots             |
| `before-deploy`   | After translate, before deploy plan    | Review final state                      |
| `never`           | Never pause                            | Full auto; risky for first runs         |

User can also Ctrl-C any time; `run` saves state and prints resume instructions.

### State invalidation

If user runs an individual command (e.g. `/docsmith draft instances`) outside of `run`, state may go stale. State file tracks last-modified time; `continue` checks if any draft has been modified after `state.completed_stages` includes `draft` — if yes, suggests re-running from `walkthrough` to verify.

---

## 7. The `module` command

```bash
/docsmith module <name>          # Create a new module intake
/docsmith module <name> --from <existing>  # Clone from existing module
/docsmith module list            # List modules and their status
/docsmith module archive <name>  # Mark module as archived
```

`/docsmith module instances` does:
1. Check `documentation/intake/modules/instances.md` doesn't already exist (re-run protocol if it does)
2. Copy `templates/MODULE_INTAKE_TEMPLATE.md` to that path
3. Pre-fill the module name and slug from the command argument
4. Update project.md `Module intake files` section with the new entry
5. Print: "Module 'instances' created. Edit documentation/intake/modules/instances.md and run /docsmith run instances when ready."

`--from <existing>` copies field values from another module file (useful when modules share structure: same sources, same voice override).

`module list` reads the project.md modules list and prints status:
```
Modules registered (3):
  ✓ instances     active     last run 2026-04-25 (2 days ago)
  ⏸ storage       paused     last run 2026-03-15 (40 days ago)
  ✗ networking    archived   last run 2026-01-10 (deploy --sync-deletes will not delete)
```

`module archive <name>` flips the module's "Module status" checkbox to Archived in its intake file. Archived modules:
- Skipped by `/docsmith run` (no implicit processing)
- Not deleted from target on `/docsmith deploy --sync-deletes` (orphan filter excludes them)
- Source entries kept in `sources.lock.yaml` for reference

---

## 8. Validation field reference (concrete)

Critical (CRT) and nice-to-have (NTH) fields:

### project.md

| Section | Field                         | Critical | Default if missing             |
| ------- | ----------------------------- | -------- | ------------------------------ |
| 1       | product.slug                  | CRT      | (stop)                         |
| 1       | product.name                  | CRT      | (stop)                         |
| 1       | product.url                   | NTH      | empty (walkthrough won't auto-login if also empty) |
| 2       | audience.primary.role         | CRT      | (stop)                         |
| 2       | audience.primary.tech_level   | CRT      | (stop)                         |
| 2       | audience.primary.goal         | CRT      | (stop)                         |
| 2       | audience.secondary            | NTH      | (empty list)                   |
| 3       | locales.source                | CRT      | (stop)                         |
| 3       | locales.targets               | NTH      | (empty)                        |
| 4       | deploy.preset                 | CRT      | (stop)                         |
| 4       | deploy.target_path            | CRT (if Docusaurus) | (stop)              |
| 4       | deploy.on_collision           | NTH      | `warn`                         |
| 5       | voice.tone                    | NTH      | `friendly-professional`        |
| 5       | voice.perspective             | NTH      | `second-person`                |
| 5       | voice.reading_level           | NTH      | `8th grade`                    |
| 5       | voice.terms_to_avoid          | NTH      | (empty)                        |
| 6       | credentials.username_env      | CRT (if walkthrough in pipeline) | (stop)        |
| 6       | credentials.password_env      | CRT (if walkthrough in pipeline) | (stop)        |
| 7       | sources                       | NTH      | (empty — AI works from intake alone) |
| 8       | auto_run.pause_at             | NTH      | `after-draft`                  |
| 8       | auto_run.drift_action         | NTH      | `prompt`                       |
| 8       | translate.review_mode         | NTH      | `batch`                        |

### modules/<n>.md

| Section | Field                    | Critical | Default if missing             |
| ------- | ------------------------ | -------- | ------------------------------ |
| 1       | module.slug              | CRT      | (stop)                         |
| 1       | module.display_name      | CRT      | (stop)                         |
| 1       | module.priority          | NTH      | `3`                            |
| 1       | module.folder            | CRT      | (default to module.slug)       |
| 2       | features                 | CRT (≥1) | (stop)                         |
| 2       | features[N].name         | CRT      | (stop)                         |
| 2       | features[N].content_types | CRT (≥1 ticked) | (stop)                  |
| 2       | out_of_scope             | NTH      | (empty)                        |
| 3       | voice override           | NTH      | (inherit from project)         |
| 4       | sources                  | NTH      | (empty — adds to project sources) |
| 5       | walkthrough.test_account | NTH      | (inherit)                      |
| 5       | walkthrough.setup_script | NTH      | (none)                         |
| 6       | redact.fields            | NTH      | (none)                         |
| 6       | module.status            | NTH      | `Active`                       |

---

## 9. Source-driven intake auto-fill (v1.5.9+)

`init --from-source` and `module --from-source` let AI pre-fill intake from external source documents (BA docs, PRDs, existing docs). This section documents the inference logic, confidence levels, interactive Q&A flow, and re-run behavior.

### 9.1 When to use

Use `--from-source` when:

- BA already has a written PRD / spec / BA doc and you don't want to re-enter the same info
- Source is in Notion, GitHub, Google Drive, public URL, or local markdown file
- You're updating an existing project after BA doc revisions

Don't use `--from-source` when:

- Source content is too vague (one-paragraph idea — AI will guess too much)
- Project has unusual structure not implied by source (custom sitemap pattern, multi-product taxonomy)
- BA prefers manual control

### 9.2 Inference confidence model

AI categorizes every field by confidence:

| Confidence | Description | Marker in intake |
|---|---|---|
| **Fact** | Direct quote or unambiguous data point in source | (no marker — same as user-typed) |
| **Guess** | Inferred from context with reasoning | `← AI guess, please verify` |
| **Default** | No source data; template default applied | `← default applied` |
| **Asked** | User answered during interactive Q&A | (no marker) |

Each marker is a standalone comment on its own line, so BA can scan visually. Removing the marker (e.g., after verifying) is OK; AI doesn't depend on markers for re-runs (uses field-level hash check instead).

### 9.3 Inference logic per field

#### Product section

| Field | Inference logic |
|---|---|
| `product.slug` | Slugify product name (title in BA doc heading or PRD title). If conflict (existing slug in workspace), prompt user. |
| `product.display_name` | Title from BA doc heading. |
| `product.url` | Regex search for `https?://[a-z0-9.-]+(\.com\|\.io\|\.app\|...)` in source. Filter docs/marketing URLs (skip github.com, notion.so). If multiple, pick first or ask user. |
| `product.description` | First sentence of source that contains product name AND verb describing what it does ("MyCloud is a cloud platform that..."). Trim to one line. |

#### Audience section

| Field | Inference logic |
|---|---|
| `audience.primary.role` | Look for "target audience", "users", "personas" sections. Extract role title. |
| `audience.primary.tech_level` | Heuristic: if source mentions "command-line", "API", "CLI" → High. If "non-technical", "business users" → Low. Otherwise Medium (default). |
| `audience.primary.primary_goal` | Look for "users want to...", "the goal is...", "intended outcome" patterns. Always marked as guess. |
| `audience.secondary` | Skip unless source explicitly lists multiple personas. Don't guess secondary personas. |

#### Languages section

| Field | Inference logic |
|---|---|
| `locales.source` | Detect language of source content (script analysis: Latin → en, Vietnamese diacritics → vi, etc.). Always asks user to confirm. |
| `locales.targets` | Always asked (Q&A). Never inferred — translation strategy is project decision, not in BA doc. |

#### Deploy section

| Field | Inference logic |
|---|---|
| `deploy.preset` | Always asked (Q&A) unless current directory has docusaurus.config (then suggest docusaurus). |
| `deploy.target_path` | Asked if preset is docusaurus. If `init` is run inside Docusaurus repo, suggest `.` (in-place). |

#### Voice section

| Field | Inference logic |
|---|---|
| `voice.tone` | Heuristic: if source uses contractions, exclamations, casual language → casual. If technical jargon, formal sentence structure → technical-direct. Otherwise friendly-professional (default). Always marked guess. |
| `voice.perspective` | Detect dominant pronoun in source ("you" → second-person; "we" → first-person plural; "the user" → third-person). Marked guess. |
| `voice.reading_level` | Default 8th-grade unless source has very long technical sentences (→ college) or very short instructional bursts (→ 6th-grade). Marked guess. |
| `voice.terms_to_avoid` | Skip — never inferred. User must add explicitly if desired. |

#### Credentials section

| Field | Inference logic |
|---|---|
| All credential env vars | Always asked (Q&A) when walkthrough/record will be used. Never inferred — credentials are environment-specific. |

#### Sources section

| Field | Inference logic |
|---|---|
| Source 1 | The source passed to `--from-source` is auto-registered as Source 1. URL/path, type, and auth env var pre-filled. |
| Additional sources | Only added if source content references other docs (e.g., "see also: <URL>"). Otherwise skip. |

#### Auto-run, sitemap, media

| Field | Inference logic |
|---|---|
| All auto-run fields | Always default. Never inferred from source. |
| `sitemap.pattern` | Always default Pattern A unless source explicitly describes a different navigation structure. |
| `media.*` | Always default. Source rarely mentions media policy. |

#### Module detection

When source has clear section structure:
- Each top-level section ("Instances", "Storage", "Billing") → candidate module
- AI lists detected modules and asks: "Create module intake for each? Y/N/select"
- For each module, AI infers features from sub-headings and bullet lists

When source is flat (one long doc):
- AI asks: "Source seems to be one feature. Create one module called '<inferred-name>'?"

### 9.4 Interactive Q&A flow

After parsing source, AI asks the user 5-10 questions:

```
Field 1: Source language for drafts?
> Detected: English. Confirm? Y/N (or specify another)

Field 2: Target languages for translation?
> [ ] None  [ ] Vietnamese (vi)  [ ] Japanese (jp)  [ ] Other: ___
> Tick multiple or none

Field 3: Deploy preset?
> [ ] Standalone  [ ] Docusaurus
> Detected docusaurus.config in `..` — suggest Docusaurus + `..` target?

Field 4: Will you use walkthrough (capture screenshots from product UI)?
> Y/N
> If Y: env var name for username? Password?

Field 5: Voiceover for videos?
> [ ] Silent (default — recommended for first try)
> [ ] AI synthetic voice per locale
> [ ] No videos at all

Field 6: Pause gate for first run?
> [ ] After plan
> [ ] After draft (default — safest)
> [ ] Before deploy
> [ ] Never
```

Questions are skipped if AI has high confidence inference for that field. User can answer "use default" to skip any question.

### 9.5 Inference report

After auto-fill, AI writes a transparency report:

```
documentation/intake/.inference/<timestamp>-<scope>.md
```

Format defined in [templates/INTAKE_INFERENCE_REPORT_TEMPLATE.md](templates/INTAKE_INFERENCE_REPORT_TEMPLATE.md).

Contents:
- Frontmatter with metadata + confidence summary
- "Facts" table: field, value, source line/quote
- "Guesses" table: field, value, reasoning, verify? marker
- "Defaults applied" table: field, value, why default
- "Asked user" table: question, answer
- "Open items" (still need user input — empty if intake is runnable)
- "Sources used" appendix

Reports retained for audit. Each `--from-source` re-run creates a new file with new timestamp; old reports kept.

### 9.6 Re-run with `--from-source`

When user runs `init --from-source` again on existing workspace:

1. Fetch sources fresh (compare with sources.lock to detect external changes)
2. Re-infer all fields
3. For each field, compute hash of current intake value vs hash at last inference time
   - **Hash matches**: BA didn't manually edit since last inference. Safe to re-infer if source data changed.
   - **Hash differs**: BA manually edited. Preserve current value (don't overwrite manual edits).
4. Generate diff: what AI would change, what BA edited, what stays the same
5. Re-run protocol gate per field group:
   - **Update** (default): only re-infer fields BA didn't edit
   - **Overwrite**: discard BA edits (rare; for major source rewrites)
   - **Skip**: don't update intake; just regenerate inference report
6. Write new inference report

Hash storage: AI stores per-field hash in `.inference/<latest>.hashes.yaml`:

```yaml
# Per-field hashes from last inference
fields:
  product.slug: sha256:abc123...
  product.display_name: sha256:def456...
  audience.primary.role: sha256:...
  ...
```

On re-run, AI reads this file. If a field's current value hash differs from stored hash, BA edited it.

### 9.7 Limitations

- **Heuristic detection** — module names, audience tech level, voice tone are all heuristic. AI labels them "guess" so BA reviews.
- **No deep code analysis** — when source is GitHub repo, AI reads README and surface code structure; doesn't analyze every function. For deep code-driven docs, refine scope manually after auto-fill.
- **No semantic merge** — when re-running, AI uses field-level hash. If BA reformatted a field (added whitespace, reordered sub-items), hash changes and AI may not re-infer even if BA didn't change semantic content. Acceptable trade-off; semantic merge would require LLM re-reading every field.
- **No multi-source merge** — passing 3 sources merges them as 3 inputs but AI may pick fields from one source over another with no user control. Future v1.6+ may add per-field source preference.
- **Conservative defaults** — AI defaults to safest choice (silent video, standalone deploy) even when source hints at other strategies. Override explicitly during Q&A or after.

### 9.8 Example: full session

```
$ /docsmith init --from-source documentation/sources/ba-doc.md

[1/4] Fetching source...
✓ Read documentation/sources/ba-doc.md (180 lines)

[2/4] Inferring fields...
- 8 facts extracted
- 4 guesses inferred
- 7 defaults applied
- 3 fields need your input

[3/4] Quick questions:

Source language for drafts?
> Detected: English. Confirm? [Y/n]: y

Target languages for translation?
> Tick: [ ] none [x] vi [ ] jp [ ] other:
✓ Vietnamese added

Deploy preset?
> [ ] Standalone  [x] Docusaurus
> Target path? [../my-docs]: ../mycloud-docs
✓ Docusaurus + ../mycloud-docs

[4/4] Writing intake files...
✓ documentation/intake/project.md (8 facts, 4 guesses, 7 defaults, 3 asked)
✓ Detected 2 modules: instances, storage
  Create module intakes? [Y/n]: y
✓ documentation/intake/modules/instances.md (3 features detected)
✓ documentation/intake/modules/storage.md (2 features detected)
✓ documentation/intake/.inference/2026-04-29T16-00-00-project.md

⚠ 4 fields marked "← AI guess" in project.md — please review:
  - audience.primary.primary_goal
  - voice.tone
  - modules[0].features (3 features inferred)
  - modules[1].features (snapshot uncertain)

Next: edit project.md to verify guesses, then /docsmith run
```



If you have an existing v1.4.x workspace:

1. Run `/docsmith init --upgrade-from-1.4` (new flag in v1.5.0)
2. AI:
   - Reads existing `.docsmithrc.yaml`
   - Generates `documentation/intake/project.md` pre-filled with values from yaml
   - Keeps `.docsmithrc.yaml` for backward-compat reading (deprecated, will be removed in v1.6)
3. Manually create modules: `/docsmith module <existing-feature-area>` for each feature in your old plan
4. Edit each module file to refine scope
5. Run `/docsmith run` to verify everything resolves correctly

If you have NO existing workspace, just run `/docsmith init` normally.

---

### 9.9 Multi-module performance (v1.5.10+)

When `init --from-source` or `update --from-source` detects a large number of candidate modules, generation can be sped up using parallel sub-agents.

**Threshold**: >5 modules.

**Approach**: AI MAY use the Task tool to spawn parallel sub-agents, one per module. Each sub-agent:

1. Reads the same source(s) (already fetched into local cache by main agent)
2. Focuses on its assigned module's section in the source
3. Generates the module intake file independently
4. Returns an inference fragment (facts, guesses, defaults for that module)

Main agent then:

1. Waits for all sub-agents to complete
2. Consolidates inference fragments into a single `documentation/intake/.inference/<ts>-multi.md` report
3. Updates `project.md` `Module intake files` list with all detected modules

**Important caveat**: actual parallelism depends on the Claude runtime. The skill spec says "MAY", not "MUST". Possible behaviors:

- True parallel execution (multi-instance runtime)
- Interleaved execution (single instance with context switching)
- Sequential despite spec hint

In all cases, the OUTCOME is correct (all module intakes generated). Only PERFORMANCE varies.

**When parallel fails**: if a sub-agent fails (network, parsing error, ambiguous source), main agent:

1. Retries that module sequentially
2. If retry succeeds → continue
3. If retry fails → report partial completion:
   ```
   ✗ Module 'billing' failed: source section ambiguous
   ✓ 4 of 5 modules completed
   Run /docsmith init --from-source --resume to retry failed modules
   ```

**Sequential fallback**: below the >5 threshold, AI uses sequential processing. Avoids spawn overhead for small projects. ≤5 modules ≈ 30-60s total; not worth parallel coordination.

**Cost note**: parallel sub-agents consume tokens in parallel. For a 30-module project, expect ~2× token usage compared to sequential (overhead per spawn). Trade-off: ~3× speed improvement for ~2× token cost.

**Benchmark guidance** (rough, from synthetic tests):

| Module count | Sequential | Parallel (MAY) | Saving |
|---|---|---|---|
| 5 | ~2 min | ~1 min | 1 min |
| 15 | ~6 min | ~2 min | 4 min |
| 30 | ~12 min | ~4 min | 8 min |
| 50 | ~20 min | ~6 min | 14 min |

Real numbers depend on source complexity, network latency to Claude, and runtime characteristics.

**Configuration**: no user-facing knob in v1.5.10. Threshold is hardcoded. Future v1.6+ may add `init --max-concurrent N` flag.

### 9.10 Missing module detection (v1.5.10+)

Beyond initial fill, `update --from-source` compares current workspace modules with source structure to surface gaps.

**Behavior**:

1. Re-fetch source(s)
2. Detect candidate modules from source structure (top-level sections, headings, file paths)
3. Read existing `documentation/intake/modules/*.md` files
4. Categorize into 3 buckets:

   **In source AND in workspace**: existing modules. Check if scope drifted (features in source vs features in module intake).

   **In source, NOT in workspace**: new candidate modules. List for user to optionally create.

   **In workspace, NOT in source**: orphan modules. Possible reasons:
   - Module deprecated, source removed reference (suggest archive)
   - Module is internal/admin (BA doc focuses on user-facing only — keep)
   - Source out of sync (update source first)

5. Interactive prompt:

   ```
   Source has 7 modules. Workspace has 4.

   📋 New in source (not yet documented):
     [ ] billing — BA doc § 5, "Manage billing and invoices"
     [ ] audit-logs — BA doc § 6, "View account audit trail"
     [ ] api-keys — BA doc § 7, "Manage API keys"

   ⚠️ In workspace, not in source (consider archiving?):
     - legacy-vpn — last in source 2025-10; not in current BA doc

   ⚪ Scope drift detected:
     - instances — source mentions 'auto-scaling' but module doesn't tick it

   Action:
     1. Create intake for selected new modules
     2. Archive removed modules
     3. Update scope drift modules
     4. Show diffs only (no changes)
     5. Skip
   ```

6. User picks action(s); AI applies:
   - **Action 1**: scaffold new module intakes (with `--from-source` auto-fill applied per module)
   - **Action 2**: mark orphan modules as `status: archived` in module intake (don't delete; preserve for git history)
   - **Action 3**: update existing module intake's features list to match source
   - **Action 4**: print diffs to stdout, no changes
   - **Action 5**: exit without changes

7. Generate update inference report at `documentation/intake/.inference/<ts>-update.md` with:
   - Source comparison summary
   - Action taken per module
   - Hash diffs for scope drift cases

**No `--from-source` argument needed**: `update` reads sources from `documentation/intake/sources.lock.yaml` (registered during initial `init --from-source` or first manual `fetch`). User can override:

```bash
/docsmith update                                    # use registered sources
/docsmith update --from-source <path>               # use new source (re-register)
/docsmith update --from-source <path> --no-modules  # update content only, skip module diff
```

**Re-run safety**: same per-field hash protection as `init --from-source`. BA's manual edits to existing module intakes preserved unless user explicitly chooses Overwrite.

**Limitation**: orphan detection is heuristic. If source restructured (renamed sections, merged modules), AI may falsely flag valid modules as orphan. User decision wins in interactive prompt.

---

## 10. Interactive fill protocol (v1.5.13+)

When a pipeline command runs and finds critical intake fields empty, AI asks the user inline rather than failing. Answers are written back to the intake file, so the next run finds the fields already populated.

This pattern lets users skip the upfront 354-line intake fill and instead answer minimal questions just-in-time, distributed across the pipeline stages they actually run.

### 10.1 When does interactive fill activate?

When ALL of these are true:

1. User runs a stage command (`audience`, `plan`, `voice`, `draft`, `edit`, `walkthrough`, `record`, `translate`)
2. Stage requires fields that resolve to "empty" via the layered config (module → project → defaults)
3. The empty field is **critical** for that stage (not a nice-to-have with a safe default)

Otherwise: stage proceeds normally with available fields.

### 10.2 Per-stage required fields (interactive prompts)

Each stage has a minimal set of fields it must have before proceeding. Below is the canonical list. If any is empty when stage runs, AI prompts and writes back.

#### `audience`

Critical:
- Audience > Primary persona > Role
- Audience > Primary persona > Technical level
- Audience > Primary persona > Primary goal

Prompt example:
```
Stage: audience for module 'instances'

I need a few details before I can write the audience profile.

Q1: Who is the primary user? Job title or role.
> DevOps Engineer

Q2: Technical level? [low / medium / high]
> medium

Q3: What's their primary goal when using MyCloud?
> Deploy services to production with minimal ops overhead

✓ Saved to documentation/intake/project.md (§ 2 Audience)
✓ Continuing audience generation...
```

#### `plan`

Critical:
- Module > Scope > At least one feature with at least one content type
- Project > Sitemap pattern (defaults to A if missing)

Plan rarely triggers prompts because `module` command already enforces feature definition. If pattern empty, defaults to A silently.

#### `voice`

Critical:
- Project > Voice > Tone (defaults to friendly-professional silently — NO prompt)
- Project > Voice > Perspective (defaults to second-person silently)
- Project > Voice > Reading level (defaults to 8th-grade silently)

`voice` does NOT trigger prompts. All voice fields have defaults that work for most projects. User can still override by editing intake before running `voice` if desired.

#### `draft`

Critical:
- Module > Scope > Features with content types (caught earlier by `plan`)
- Project > Sources (at least one source OR explicit "no sources" confirmation)

Prompt example when no sources defined:
```
Stage: draft for module 'instances'

You haven't added knowledge sources to project.md.
AI will draft from intake info only (no external context).

Continue? [Y/n]: y
✓ Marked "no external sources" in project.md (§ 6)
✓ Continuing draft generation...
```

#### `edit`

No prompts. Edit operates on existing drafts only.

#### `walkthrough`

Critical:
- Project > Credentials > Username env var
- Project > Credentials > Password env var
- Product URL

Prompt example:
```
Stage: walkthrough for module 'instances'

I need product credentials and URL before I can verify against the live UI.

Q1: What's the product URL? (where the user-facing app runs)
> https://console.mycloud.com

Q2: Test account username — provide the env var NAME (not the username itself)
> MYCLOUD_TEST_USER

Q3: Test account password env var NAME
> MYCLOUD_TEST_PASS

✓ Saved to documentation/intake/project.md (§ 1, § 5)

Verifying env vars are set in your shell...
✗ MYCLOUD_TEST_USER is empty
✗ MYCLOUD_TEST_PASS is empty

Please run before retrying:
  export MYCLOUD_TEST_USER="qa-bot@example.com"
  export MYCLOUD_TEST_PASS="..."

Then run /docsmith walkthrough instances again.
```

#### `record`

Critical (only if VIDEO markers present in drafts):
- Project > Media > Voiceover strategy (defaults to silent silently — NO prompt)
- TTS provider (only if voiceover = AI, and only first time)
- Voice ID per locale (only if voiceover = AI per-locale, and only for unticked locales)

Prompt only fires when AI voiceover selected and provider/voice not yet specified.

#### `translate`

Critical:
- Project > Languages > Target languages (at least one ticked)

Prompt example when no targets:
```
Stage: translate for module 'instances'

No target languages set in project.md (§ 3).
What languages should I translate to?

[ ] Vietnamese (vi)
[ ] Japanese (jp)
[ ] Other: ___

Tick one or more (comma-separated): vi
✓ Saved to documentation/intake/project.md (§ 3 Languages)
✓ Translating to vi...
```

### 10.3 Write-back format

When AI writes user's answer back to intake, it preserves the existing markdown structure:

- For backtick fields: replace placeholder with answer
- For checkboxes: change `[ ]` → `[x]` for the chosen option
- For nested structures (Source N, Feature N): append new block at correct location

Example diff after audience prompt:

```markdown
# BEFORE
- Role / job title: `e.g., DevOps Engineer`
- Technical level:
  - [ ] Low
  - [ ] Medium
  - [ ] High
- Primary goal: `Why do they use this?`

# AFTER (AI wrote back)
- Role / job title: `DevOps Engineer`
- Technical level:
  - [ ] Low
  - [x] Medium
  - [ ] High
- Primary goal: `Deploy services to production with minimal ops overhead`
```

The hint comment lines (`> Lowercase, kebab-case...`) are preserved untouched. Same parsing applies on next run.

### 10.4 Write-back idempotency

If user re-runs the stage after answering prompts:
1. AI re-reads intake
2. Sees fields now have values
3. Skips prompts
4. Proceeds with stage

If user wants to RE-answer (correct a typo, change strategy):
1. Edit intake manually OR run `/docsmith intake-help <field>` for guided edit
2. Re-run stage; new value is used

There's no "undo" for AI-written answers. They become normal intake values. User edits override.

### 10.5 Skip prompt with --no-prompt flag

If user wants the old "fail with missing-field error" behavior (e.g., for CI scripts that shouldn't pause):

```bash
/docsmith audience instances --no-prompt
# Behavior: if any required field empty, fail immediately
# (does NOT prompt user)
```

`--no-prompt` available on all stage commands. Default behavior is interactive prompt (since v1.5.13).

### 10.6 Mixed flows (auto-fill + interactive)

User can combine:

- `init --from-source` fills 80% of fields from BA doc
- Some fields marked "← AI guess" — user can verify or leave
- Some critical fields still empty (deploy target, credentials, locales)
- User runs `/docsmith audience instances`
- AI sees audience filled (from source), skips Audience prompts
- User runs `/docsmith walkthrough instances`
- AI sees credentials empty, prompts them, writes back
- Continues

Each command checks ITS required fields, doesn't try to validate the whole intake at once. Distributes the prompting load.

### 10.7 Validation order: critical → safe defaults → silent fallback

When checking fields:

1. **Critical for this stage** (table above) → prompt user if empty
2. **Has safe default** (voice tone, sitemap pattern, screenshot density) → use default silently, don't prompt
3. **Optional** (secondary persona, advanced media options) → skip unless explicitly set

This keeps prompts minimal. User answers only what's strictly needed.

### 10.8 Limitations

- **No partial answer recovery** — if user types `n` or aborts during a multi-question prompt, AI exits the stage. No "save what you've answered so far" mode. User can re-run; previously-answered fields are remembered.
- **No prompt for module-specific fields** in stages run at project level — `voice` is project-level; if user wants per-module voice override, must edit module intake manually
- **No semantic validation of free-text answers** — AI accepts any string for "Primary goal", doesn't verify it's coherent
- **Order assumption** — AI assumes user runs stages in canonical order. Running `draft` before `audience` triggers more prompts than needed because `draft` would re-ask audience info if missing. Recommend `run` flow OR manual order.

---

## 11. Known limitations (v1.5.0)

1. **No conditional field display** — all sections always shown. BA fills 50 fields even if 30 don't apply. Future: `--minimal` template variant for simple projects.
2. **Source fetching is synchronous** — large repos can be slow. No parallel fetching in 1.5.0. Future: parallel fetcher with progress bar.
3. **Notion conversion** uses standard markdown — complex Notion features (databases, embeds) become inline references, not first-class. Future: better databases handling.
4. **Per-doc source provenance not tracked** — `update` re-evaluates ALL docs in a module when ANY source changes. Conservative. Future: track which doc used which source for surgical updates.
5. **No incremental fetch on cache hit** — `fetch` always re-downloads even if cache is fresh. Future: respect `Cache-Control` / `ETag`.
6. **GDrive token refresh not handled** — long-lived OAuth2 tokens may expire. User must refresh manually. Future: refresh flow integrated.
7. **Source content cache is gitignored** — meaning across machines, every dev re-fetches. Future: optional shared cache via S3 or similar.
