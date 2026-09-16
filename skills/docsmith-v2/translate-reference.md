# Translate Reference

Detailed logic for the `translate` command. SKILL.md references this file.

## Why this exists in v1.4.0

Until v1.3.0, drafting only happened in source locale (`documentation/drafts/en/`). Target locales (`drafts/vi/`, `drafts/jp/`) stayed empty placeholders. Deploy with multi-locale enabled would copy empty folders, producing a Docusaurus site with broken locale switcher.

v1.4.0 fills this gap. **`translate` is now a required step** in the process flow when `locales.targets` is non-empty, positioned between `incorporate` and `categorize`/`deploy`.

```
... → walkthrough → record → incorporate → translate → categorize → deploy → publish
                                              ↑
                                              required if locales.targets non-empty
```

## Quality model: AI translate full + user review

User chose this profile in the v1.4.0 design conversation. Concretely:

- AI translates entire file from source to target
- User reviews **per block** before save (block = paragraph, list, heading, table, etc.)
- User can: approve / edit / skip-block / approve-all-remaining
- Decisions are recorded for audit
- Translation can be re-run; existing translation becomes KB (Update mode)

This is intentionally NOT a "scaffolding only" or "auto-approve" mode. The default makes review explicit because:

- AI translation quality varies wildly per language pair
- Technical docs have specific terms that must be consistent (glossary catches some, not all)
- UI labels in translated doc must match actual UI labels in target language (which the AI doesn't know unless told)

Power users can opt into `--auto-approve` for speed; v1.6.x will refine quality.

---

## 1. Translate workflow (high level)

### What gets translated

Starting v1.5.7, `translate` processes BOTH:

- **Drafts**: `documentation/drafts/<source>/**/*.md` → `documentation/drafts/<target>/**/*.md`
- **Video scripts**: `documentation/scripts/<module>/<asset-id>.md` — translates `# Source script` content into `## <locale>` sections within same file

Same per-block / batch review gate applies. Same glossary (`documentation/standards/glossary.<locale>.yaml`).

For script files specifically:
- Source section is read as one logical block (or split by paragraph for per-block mode)
- Translated content goes under `## <locale>` heading in the same file
- Frontmatter is preserved verbatim
- Notes section is NOT translated (internal-only)

```
/docsmith translate MyProduct
       │
       ▼
1. Read .docsmithrc.yaml
   - locales.source (e.g. "en")
   - locales.targets (e.g. ["vi", "jp"])
   - documentation/standards/glossary.<target>.yaml (optional, per-locale)
       │
       ▼
2. For each target locale:
   2a. For each source file in drafts/<source>/**/*.md:
       │
       ▼
   2b. Re-run protocol check:
       - target file in drafts/<target>/<path>.md exists?
       - YES → 4-option gate (Update / Overwrite / Side-by-side / Cancel)
       - NO  → fresh translation
       │
       ▼
   2c. Block-parse the source file:
       - Frontmatter (translate title/description; preserve other fields)
       - Headings (translate)
       - Prose paragraphs (translate)
       - Lists (translate items)
       - Tables (translate cell text, not column structure)
       - Code blocks (PRESERVE verbatim)
       - Inline code (PRESERVE verbatim)
       - Image refs `![alt](path)` (translate alt text, preserve path)
       - Video markers `<!-- VIDEO ... -->` (PRESERVE verbatim — user comment is internal spec, not displayed)
       - HTML/MDX components (PRESERVE structure; translate only string children)
       - Links `[text](url)` (translate text, preserve url)
       │
       ▼
   2d. For each translatable block:
       - Look up terms in glossary, mark for substitution
       - AI generates translation
       - Show side-by-side: source / translation
       - User: y / e / s / n / a / q
         y = approve (apply translation)
         e = edit (user provides corrected translation)
         s = skip (keep source as-is in target file — for terms not yet ready to translate)
         n = skip and remove from target (don't include this block in target file)
         a = approve all remaining (use with caution)
         q = quit (save progress, exit)
       │
       ▼
   2e. Reassemble translated file:
       - Inject translation metadata into frontmatter
       - Write to drafts/<target>/<path>.md
       - Backup original (if Update mode) → archive/<ts>/
       - Save decisions → archive/<ts>/translation-decisions.yaml
       │
       ▼
3. Print summary per locale:
   - N files translated
   - M blocks approved as-is
   - K blocks edited
   - L blocks skipped
```

---

## 2. Block-level translation rules

### Preserve verbatim (NEVER translate)

| Element                          | Reason                                                  |
| -------------------------------- | ------------------------------------------------------- |
| Code blocks (```...```)          | Code is universal                                       |
| Inline code (`foo`)              | Likely identifiers, commands                            |
| File paths (`/etc/foo`, `./bar`) | Paths don't translate                                   |
| URLs                             | Same target                                             |
| Frontmatter `id`, `slug`         | Used for routing; must match across locales             |
| Image src paths                  | Files are the same                                      |
| Video markers `<!-- VIDEO ... -->` | Internal authoring directive, never rendered          |
| HTML/MDX component tags          | `<Tabs>`, `<Admonition>` etc. — structure preserved     |
| Inline HTML                      | Browser-displayed HTML; translate text content only     |
| Code identifiers in prose        | When prose mentions `npm install foo` — keep verbatim   |

### Translate

| Element                          | Notes                                                  |
| -------------------------------- | ------------------------------------------------------ |
| Headings (`# H1` through `###### H6`) | Apply title-case rules of target language        |
| Prose paragraphs                 | Full translate                                         |
| List items                       | Translate text; preserve `- ` `* ` `1. ` markers       |
| Table cell text                  | Header row: translate. Data rows: translate.           |
| Image alt text `![alt](url)`     | The `alt` portion translates; URL never                |
| Link text `[text](url)`          | The `text` portion translates; URL never               |
| Frontmatter `title`, `description`, `keywords` | User-visible; translate                |
| Admonition titles in MDX         | E.g., `<Admonition type="note" title="Note">` → translate `title` attribute |

### Apply glossary first

Before AI translation of any block, scan for glossary terms and substitute. Glossary entries always win over AI's natural translation choice.

---

## 3. Glossary file

Optional but strongly recommended. Lives at `documentation/standards/glossary.<locale>.yaml`. Read by `translate` command at start of run.

Format: see [templates/GLOSSARY_TEMPLATE.yaml](templates/GLOSSARY_TEMPLATE.yaml). Quick example:

```yaml
# documentation/standards/glossary.vi.yaml
version: "2026-04-26"

terms:
  # Technical terms — keep verbatim
  "instance":
    translation: "instance"
    case_sensitive: false
    keep_verbatim: true
    note: "Cloud term, kept in English"

  "API":
    translation: "API"
    case_sensitive: true
    keep_verbatim: true

  # Common terms — translate
  "compute":
    translation: "máy ảo"
    case_sensitive: false

  "create":
    translation: "tạo"
    case_sensitive: false
    contexts:
      imperative: "Tạo"      # "Create an instance" → "Tạo một instance"
      noun: "việc tạo"

  # Multi-word
  "availability zone":
    translation: "vùng khả dụng"

  # UI labels — must match actual product UI in target language
  "Create Instance":
    translation: "Tạo Instance"
    is_ui_label: true        # Replace anywhere this exact text appears
                             # Useful when doc says "Click the **Create Instance** button"
```

### Rules

- **Match longest first**: glossary lookup uses longest-match-wins. "availability zone" matches before "zone" alone.
- **Case sensitivity** per entry. Defaults to `false` (case-insensitive match) unless specified.
- **Context disambiguation**: optional. When provided, AI selects context based on syntactic role (e.g., imperative verb vs noun). When AI is uncertain, falls back to default `translation`.
- **Conflict detection**: if two entries match the same span at the same position, fail with clear error before any translation.

### When glossary is missing

Translate runs without glossary — AI uses its general knowledge. Quality is more variable. `verify` command (post-translate) flags inconsistent term usage so user can build glossary iteratively.

---

## 4. Per-block review gate

This is the safety mechanism. AI proposes; user disposes.

### Display format

```
─────────────────────────────────────────────────────────────────
File: drafts/vi/instances/create.md
Block: 7/23 (heading H2)

SOURCE (en):
  ## Creating your first instance

TRANSLATION (vi):
  ## Tạo instance đầu tiên

[y] Approve   [e] Edit   [s] Skip (keep source in target)
[n] Remove block   [a] Approve all remaining   [q] Quit

→
─────────────────────────────────────────────────────────────────
```

For prose blocks, side-by-side multi-line:

```
─────────────────────────────────────────────────────────────────
File: drafts/vi/instances/create.md
Block: 12/23 (paragraph)

SOURCE (en):
  An instance is a virtual machine that runs in the cloud. You can
  start, stop, and configure instances through the Compute service.

TRANSLATION (vi):
  Instance là một máy ảo chạy trên đám mây. Bạn có thể khởi động,
  dừng, và cấu hình instance qua dịch vụ Compute.

Glossary applied:
  • "instance" → "instance" (kept verbatim, technical term)
  • "compute" → "Compute" (UI label, kept as proper noun)

[y] Approve   [e] Edit   [s] Skip (keep source in target)
[n] Remove block   [a] Approve all remaining   [q] Quit

→
─────────────────────────────────────────────────────────────────
```

### Decision behaviors

| Key | Action                                                                          |
| --- | ------------------------------------------------------------------------------- |
| `y` | Apply AI translation. Move to next block.                                       |
| `e` | Open editor (or inline prompt) with AI translation pre-filled. User edits.      |
| `s` | Use SOURCE text in the target file. Marks block as "translation pending".       |
| `n` | Omit this block from target file entirely. Use for source-only content.         |
| `a` | Apply AI translation to all remaining blocks in this file. Warns first.         |
| `q` | Save progress to-date. Mark file as "translation in progress". Resume later.    |

### Resume support

If user quits with `q`, file gets `translation_status: in-progress` in metadata. Re-running `translate` on the same file picks up where left off.

### `--auto-approve` flag

Skips the per-block gate entirely. AI translation is applied to all blocks. File metadata gets `translation_status: auto-approved` flag for `verify` to flag.

Use cases:
- Daily CI to keep translations fresh on stable docs
- Post-glossary-update bulk re-translate where you trust the glossary

NOT recommended for first translation of new docs.

---

## 5. Translation metadata

Every translated file gets metadata in frontmatter:

```yaml
---
# Existing user fields preserved
id: instances/create
title: Tạo instance              # Translated from "Create an instance"
sidebar_position: 2

# Translation metadata (managed by docsmith)
translated_from: drafts/en/instances/create.md
translated_at: 2026-04-26T11:50:32Z
translated_by: docsmith-1.4.0
source_hash: abc123def456...
glossary_version: "2026-04-26"
translation_status: complete    # complete | in-progress | auto-approved
review_gates_passed: 23         # how many blocks went through review
review_blocks_edited: 4         # how many user manually edited
---
```

The `source_hash` field enables drift tracking in v1.6.x: when source EN file changes, the hash mismatches and `translate --check` (future) flags which sections of VI need re-translation.

In v1.4.0, drift tracking is NOT implemented. The metadata is recorded for forward compatibility only.

---

## 6. Re-run protocol integration

`translate` honors the same 4-option gate as other content commands:

### Update mode (most common for re-translation)

1. Read existing target file in full (it's a translation that may have manual edits)
2. Read current source file
3. For each block in source:
   - Find corresponding block in existing target (by position + content similarity)
   - If source block unchanged AND target block exists → KEEP (don't re-translate)
   - If source block changed → propose UPDATE: show old translation, new translation, user decides
   - If source block is new → propose NEW translation
4. For target blocks with no matching source block → propose REMOVE (block was deleted from source)

This is critical: in Update mode, **manually-edited translations are preserved** unless source content changed. Without this, every `translate` re-run would discard user's manual fixes.

### Overwrite mode

Discard existing target file. Translate from scratch. Original archived to `archive/<ts>/`.

### Side-by-side mode

Existing target preserved. New translation written as `<file>-v2.md`. User can diff and merge manually.

---

## 7. Walkthrough on translated docs (basic support in 1.4.0)

After translate, target locale drafts have content. To verify them:

```bash
# Run drift check on Vietnamese drafts
/docsmith walkthrough MyProduct --locale vi --check
```

This needs the product UI to be in Vietnamese during the browser session. Assumes user can switch product UI locale (most products have a language toggle).

### Image strategy (1.4.0 minimal)

Same image path for all locales: `/img/mycloud/instances/create-form-filled.png`. The image displayed is whatever was captured (typically EN UI).

For products with localized UI where screenshots must show the target language:
- Per-locale capture is supported in 1.4.0 via `walkthrough --locale vi`
- BUT: with default config, second capture overwrites the first (single image namespace)
- Workaround: set `images.collision_strategy` per-locale, OR manually capture per-locale and place in `static/img/<slug>/<locale>/...` (Docusaurus supports per-locale static assets)

Per-locale image namespacing is a 1.5+ feature.

### Video strategy

Same as image: single set per product, captured in source locale UI. Localized videos require manual recording (no auto-translate of video content).

---

## 8. Limitations (1.4.0 minimal scope)

### Not implemented (deferred to 1.6.x)

1. **Drift tracking** when source updates after translation. Current behavior: re-run `translate` in Update mode and review proposed changes block-by-block.
2. **`<!-- translation-locked -->` markers** for protecting manual translations from re-translation.
3. **`translate --check` mode** that lists drift without prompting to fix.
4. **Auto-translation of image alt text** with localized image variant generation.
5. **Localized UI screenshots** as a first-class workflow (workaround documented above).
6. **Glossary inheritance** between locales (e.g., shared technical terms across `vi` and `jp`).

### Quality limitations

1. **AI translation accuracy** varies by language pair. Vietnamese and Japanese both work well but technical terminology may need glossary coverage.
2. **Tone consistency** is harder than vocabulary. Voice chart was authored in source locale only; translated docs may have tone drift.
3. **MDX component title attributes** are detected via regex — complex JSX prop expressions may be missed.
4. **Markdown structure preservation** is high but not 100%. Edge cases: deeply nested lists with code blocks, definition lists, footnotes.

### Operational limitations

1. **Browser session for `walkthrough --locale vi`** needs product to support Vietnamese UI. If not, walkthrough captures whatever the product shows.
2. **Per-block review gate is interactive** — not suitable for fully automated CI without `--auto-approve` (which has its own quality cost).
3. **Translation cost**: each block is an LLM call. For large docs (1000+ blocks across 3 target locales), this is 3000+ calls per full re-translate. Consider Update mode for incremental change.

---

## 9. Config additions in v1.4.0

```yaml
# .docsmithrc.yaml additions

translate:
  enabled: true                  # 1.4.0+: feature gate. Default true if locales.targets non-empty
  glossary_required: false       # If true, fail translate when glossary missing for a target
  default_review_mode: per-block # per-block | auto-approve
  preserve_frontmatter_fields:   # Fields NEVER translated even if present
    - id
    - slug
    - sidebar_position
    - tags
  translate_frontmatter_fields:  # Fields translated explicitly
    - title
    - description
    - keywords

  # Quality gates (used by `verify` after translate)
  verify:
    glossary_consistency: true   # Flag if same term translated differently within doc
    code_block_preservation: true # Flag if code block content modified
    image_ref_preservation: true # Flag if image src changed
    metadata_present: true       # Flag if translated_from/translated_at missing
```

All optional. Defaults are pragmatic for 1.4.0 minimal scope.

---

## 10. Process Flow update

### Old (1.3.0)

```
init → audience → plan → review-plan → sitemap → voice → draft → edit → walkthrough → [record] → peer-review → [tech-review] → incorporate → [categorize] → deploy → publish
```

### New (1.4.0)

```
init → audience → plan → review-plan → sitemap → voice → draft → edit → walkthrough → [record] → peer-review → [tech-review] → incorporate → [translate] → [categorize] → deploy → publish
```

`translate` is bracketed because it's only required when `locales.targets` is non-empty. For source-locale-only projects, the step is a no-op (skipped automatically).

For multi-locale projects, "done" definition is now: **all target locales translated and reviewed**, then deploy. Deploy without translate (when targets non-empty) emits a warning and lists locales with missing/incomplete translations.
