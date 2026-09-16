<!--
  PROJECT INTAKE — Configures the WHOLE documentation project.

  ┌─────────────────────────────────────────────────────────────────┐
  │  HOW TO FILL THIS FILE                                          │
  │                                                                 │
  │  1. Tick a checkbox: [ ] → [x]                                  │
  │  2. Fill a backtick field: `value here`                         │
  │  3. Sections labeled "Advanced" are collapsed by default.       │
  │     Most projects skip these. Click ▶ to expand if needed.      │
  │                                                                 │
  │  WHEN YOU'RE DONE: save the file, run /docsmith run             │
  │                                                                 │
  │  FIRST PROJECT? Fill ONLY sections 1-6. Leave Advanced alone.   │
  │  Defaults work for ~80% of cases.                               │
  └─────────────────────────────────────────────────────────────────┘
-->

# Project Intake — `Product Name Here`

## 1. Product (REQUIRED)

> What product is this documentation for? AI uses these for titles, image namespaces, and walkthrough automation.

- Product slug: `your-product-slug`
  > Lowercase, kebab-case. No spaces. Used in URLs, image folder names.
  > Example: `mycloud`, `acme-app`

- Product display name: `Your Product`
  > Human-readable name shown in titles.
  > Example: `MyCloud`, `Acme App`

- Product URL: `https://console.example.com`
  > Where the product runs. Walkthrough opens this URL to capture screenshots.
  > Leave blank if you won't use the walkthrough command.

- One-line description: `What does this product do?`
  > One sentence. Used in landing page intros.
  > Example: `Cloud platform for hosting Docker apps`

## 2. Audience (REQUIRED)

> Who reads the docs? AI uses this to set tone, vocabulary, and assumed prior knowledge.

### Primary persona

- Role / job title: `e.g., DevOps Engineer`
  > What they do for work. Example: `Marketing Manager`, `Junior Developer`, `Sysadmin`.

- Technical level:
  - [ ] Low (general users, non-technical)
  - [ ] Medium (semi-technical, comfortable with web apps)
  - [ ] High (developers, sysadmins, command-line users)
  > Affects vocabulary. Tick ONE.

- Primary goal: `Why do they use this?`
  > What they want to achieve when reading. Example: `Deploy a service to production within 30 minutes`.

<details>
<summary><b>Advanced — secondary personas</b> (skip if only one audience)</summary>

Only add if you have clearly DIFFERENT audience segments (e.g., developers AND business managers). Each persona makes content harder to write for everyone.

### Secondary persona 1

- Role: ``
- Technical level:
  - [ ] Low
  - [ ] Medium
  - [ ] High
- Primary goal: ``

</details>

## 3. Languages (REQUIRED)

> What language do you write in, and what to translate to.

Source language (the language you draft in):
- [ ] English (en)
- [ ] Vietnamese (vi)
- [ ] Japanese (jp)
- [ ] Other: ``
> Tick ONE. This is the language AI generates first drafts in.

Target languages (translate to — leave all unchecked for single-locale):
- [ ] None (single-locale project)
- [ ] Vietnamese (vi)
- [ ] Japanese (jp)
- [ ] Other: ``
> Tick MULTIPLE if needed. Glossary file auto-created at `documentation/standards/glossary.<locale>.yaml` for each target.

<details>
<summary><b>Advanced — glossary settings</b> (using defaults)</summary>

Glossary at `documentation/standards/glossary.<locale>.yaml` enforces consistent terminology in translations. Auto-created when target languages are set.

Glossary required for translation:
- [x] No, run translation even without glossary (default — AI uses general knowledge)
- [ ] Yes, fail translate if glossary missing for a target language
> Recommend "No" until you've built up a glossary from review corrections.

</details>

## 4. Deploy (REQUIRED)

> Where do the finished docs go?

Preset:
- [ ] Standalone (no deploy target — workspace IS the artifact)
- [ ] Docusaurus
> Tick ONE. Standalone if you're just drafting. Docusaurus if you have a docs site.

If Docusaurus, target path: `../path-to-docusaurus`
> Relative path (`../my-docs`), absolute path (`/home/user/sites/docs`), or `.` for in-place mode (running docsmith inside Docusaurus repo).
> Skip this field if Standalone.

<details>
<summary><b>Advanced — collision behavior</b> (using defaults)</summary>

When deploying, if a target file already exists with different content:
- [x] Warn (default — block deploy, ask user to resolve)
- [ ] Skip (keep target as-is)
- [ ] Overwrite (replace target)
- [ ] Prompt (ask per file)

</details>

<details>
<summary><b>Advanced — voice and tone</b> (using defaults — friendly-professional, second-person, 8th grade)</summary>

These defaults work for ~80% of technical products. Override only for specific styles (regulated industry needs formal, marketing tone is casual).

Tone:
- [ ] Casual
- [x] Friendly-professional (default)
- [ ] Technical-direct
- [ ] Formal

Perspective:
- [x] Second-person — "you create an instance" (default)
- [ ] First-person plural — "we create an instance"
- [ ] Third-person — "the user creates an instance"

Reading level:
- [ ] 6th grade (broadest audience)
- [x] 8th grade (default)
- [ ] 10th grade
- [ ] College

Custom terms to AVOID: ``
> Comma-separated. Example: `utilize, leverage, robust, seamless`. AI won't use these words.

</details>

<details>
<summary><b>Advanced — compliance preset</b> (v1.6.0+) — using "none" by default</summary>

Force docs to comply with a specific organization's content standards:

- [x] None (default — use generic voice, generic sitemap, no enforcement)
- [ ] `fpt-user-guide` — FPT Cloud User Guide template

When `fpt-user-guide` selected:
- `plan` uses Sitemap Pattern D (mandatory: overview, initial-setup, quick-starts, tutorials)
- `voice` generates FPT Cloud voice chart (3 principles × 6 aspects matrix)
- `verify` runs 22 checks (11 default + 11 FPT-specific including anti-AI-tells)
- `score` becomes REQUIRED (10 criteria × 0-2 = 20; ≥14 to deploy)
- `deploy` runs FPT compliance gate (verify checks 12-22 + score) before sync
- Override compliance gate: `deploy --force-deploy`

See [templates/FPT_TEMPLATES.md](skills/docsmith/templates/FPT_TEMPLATES.md) for full rules.

</details>

## 5. Credentials for product walkthrough

> Required only if you'll use `/docsmith walkthrough` or `/docsmith record`. Put ENV VAR NAMES here, never actual passwords.

- Username env var: `MYPRODUCT_TEST_USER`
  > The NAME of an environment variable. AI reads `os.environ.get(MYPRODUCT_TEST_USER)` at runtime.
  > Set the env var before running: `export MYPRODUCT_TEST_USER="qa@example.com"`

- Password env var: `MYPRODUCT_TEST_PASS`
  > Same pattern. NEVER put the actual password here.

<details>
<summary><b>Advanced — MFA / SSO</b> (skip for plain login)</summary>

- Multi-factor auth env var: ``
  > For TOTP-based 2FA: `MYPRODUCT_TEST_TOTP_SECRET`
- Test account note: ``
  > Free-text reminder. Example: `qa-bot account, free tier, no production data`

</details>

## 6. Knowledge sources

> Where AI fetches content from when drafting docs. Skip entirely if AI should draft from scratch using only your intake info.

### Source 1

- Type:
  - [ ] Notion page
  - [ ] GitHub repo
  - [ ] Google Drive doc
  - [ ] Public URL
  - [ ] Local file
  > Tick ONE.

- URL or path or ID: ``
  > For Notion: `https://notion.so/abc123` or just the ID.
  > For GitHub: `owner/repo` (e.g., `mycloud/cloud`). Add paths in Notes if specific files: `api/instances/*.ts`.
  > For Google Drive: file ID from URL.
  > For Public URL: full URL.
  > For Local file: relative or absolute path.

- Name (for reference): ``
  > Free-text label. Example: `Instances PRD`, `API spec`.

- Auth env var (if private): ``
  > Env var NAME. Common: `NOTION_TOKEN`, `GITHUB_TOKEN`, `GOOGLE_DRIVE_TOKEN`.
  > Leave empty for public sources.

<details>
<summary><b>Advanced — additional sources</b> (skip if you only have 1 source)</summary>

Copy "Source 1" block format below for each additional source. Increment N.

### Source 2

- Type:
  - [ ] Notion page
  - [ ] GitHub repo
  - [ ] Google Drive doc
  - [ ] Public URL
  - [ ] Local file
- URL or path or ID: ``
- Name: ``
- Auth env var (if private): ``

### Source 3

- Type:
  - [ ] Notion page
  - [ ] GitHub repo
  - [ ] Google Drive doc
  - [ ] Public URL
  - [ ] Local file
- URL or path or ID: ``
- Name: ``
- Auth env var (if private): ``

</details>

<details>
<summary><b>Advanced — auto-run behavior</b> (using defaults)</summary>

Where AI pauses for human review during `/docsmith run`:
- [ ] After plan (before draft)
- [x] After draft (before walkthrough) — default; safest for first run
- [ ] Before deploy
- [ ] Never (full auto)
> Recommend "After draft" for first project — you see what AI wrote before product verification.

Drift detection action (when product UI changes):
- [x] Prompt per item (default — safest)
- [ ] Auto-apply HIGH confidence fixes (faster, requires good caption discipline)

Translation review mode (only matters with target languages):
- [ ] Per-block (review each block individually — slowest, safest)
- [x] Batch (review whole-file diff — default, faster)
- [ ] Auto-approve (no review — only for trusted glossary)

</details>

<details>
<summary><b>Advanced — sitemap pattern</b> (using Pattern A default)</summary>

Determines navigation structure across modules. Picked once at project level.

Sitemap pattern:
- [x] Pattern A — Learning path (default)
  > overview → setup → quickstarts → tutorials → reference → troubleshooting → glossary
  > Best for: technical products with conceptual depth
- [ ] Pattern B — Task-first
  > overview → quickstarts → guides → reference → troubleshooting
  > Best for: mature products where users come knowing what they want
- [ ] Pattern C — Custom (you define the order below)

If Pattern C, list section types in order:
```
overview
initial-setup
quickstarts
tutorials
reference
troubleshooting
glossary
```

### Section display name overrides (optional)

Leave empty to use defaults. Override only if you want different labels (e.g., "Hands-on guides" instead of "Quick Starts").

- overview: ``
- initial-setup: ``
- quickstarts: ``
- tutorials: ``
- guides: ``
- concepts: ``
- dashboard: ``
- reference: ``
- api-reference: ``
- glossary: ``
- troubleshooting: ``

</details>

<details>
<summary><b>Advanced — media policy</b> (using defaults: silent video + source-only screenshots = ~$0 cost)</summary>

Default: capture screenshots once in source language UI (reused for translated docs), generate silent videos with on-screen captions.

Cost preview:
- Default config (3 locales, 30 docs): ~1 hour, $0 TTS, ~65 MB storage
- Premium config (AI voice + per-locale screenshots): ~3 hours, $5-10 TTS, ~200 MB

### Screenshots

Density per content type:
- Tutorial: `1 per major step` (default)
- How-to: `1 per heading` (default)
- Reference: `none` (default)
- Concept: `optional` (default)
- Troubleshooting: `1 per error case` (default)
- Quickstart: `1 per heading + 1 final state` (default)
> Backtick-edit to override. Example: `2 per major step` for image-heavy tutorials.

Style:
- [x] viewport-only — clean, no browser chrome (default)
- [ ] full-window — includes URL bar, tabs
- [ ] cropped-element — focus on relevant element + 20px padding
- [ ] annotated — overlay arrows / numbered callouts (manual edit needed)

Aspect ratio:
- [x] 16:9 desktop / 1280×720 (default)
- [ ] 4:3 legacy / 1024×768
- [ ] mobile portrait / 375×812
- [ ] square / 1080×1080
- [ ] custom: ``

Per-locale strategy:
- [x] Source-only — capture in source UI, reuse for translated docs (default — cheapest)
- [ ] Per-locale — re-capture for each target locale (3× cost, native UX)
- [ ] Hybrid — source full + selective per-locale for important touchpoints

### Videos

Density per content type:
- Tutorial: `required, ≤ 90s` (default)
- How-to: `optional if >5 steps, ≤ 30s` (default)
- Reference: `never` (default)
- Concept: `optional, ≤ 2min` (default)
- Troubleshooting: `never` (default)
- Quickstart: `optional, ≤ 60s` (default)

Voiceover strategy:
- [x] Silent + on-screen captions (default — cheapest, no TTS needed)
- [ ] AI synthetic voice per locale
- [ ] Source voice + per-locale subtitles
- [ ] Human recorded voiceover
- [ ] No video at all (skip `record` command entirely)

#### TTS provider (only if "AI synthetic voice")

- [x] local-piper — free, offline (default)
- [ ] local-coqui — free, more voices, slower
- [ ] openai — paid (~$15/1M chars)
- [ ] elevenlabs — paid ($5-99/mo), highest quality
- [ ] google-cloud — paid (~$4/1M chars), good Vietnamese
- [ ] azure-cognitive — paid

Voice ID/name per locale:
- en: ``
  > Browse provider's voice list. Piper: `en_US-amy-medium`. OpenAI: `alloy`. Google: `en-US-Wavenet-D`.
- vi: ``
- jp: ``

Auth env var (only if non-local TTS):
- TTS provider env var: ``
  > `OPENAI_API_KEY`, `ELEVENLABS_API_KEY`, etc.

### Subtitles / captions

Generate `.vtt` subtitle files:
- [ ] No subtitles
- [ ] Source-only `.vtt`
- [x] Per-locale `.vtt` (default if multi-locale)

Generation method:
- [x] Auto from script (default — works for Silent and AI voice)
- [ ] STT after recording (needs Whisper, only for human voiceover)
- [ ] Manual user-provided `.vtt`

Caption packaging:
- [x] Sidecar `.vtt` files (default — one video, multiple subtitle files)
- [ ] Burned into video (one video per locale, larger files)

</details>

## 7. Module intake files (auto-managed)

Modules registered (created via `/docsmith module <name>`):

<!-- BEGIN MODULES LIST -->

(none yet)

<!-- END MODULES LIST -->

---

<!--
  Validation: when /docsmith run triggers, AI checks:
  - REQUIRED fields filled (sections 1, 2, 3, 4, 5 if walkthrough used)
  - At least one source-type ticked per Source N block (or no Source N)
  - Advanced sections: defaults applied if not customized

  Missing critical → AI stops with clear error. Missing nice-to-have → defaults applied silently.
-->
