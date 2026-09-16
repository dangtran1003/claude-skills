# Deploy Reference

Detailed logic for the `deploy` command. SKILL.md references this file.

## Mental model

Docsmith has two modes that differ only in the target:

```
WORKSPACE (always present)              TARGET (varies by preset)
documentation/                          standalone:    no target
├── plan/                               docusaurus:    user's docusaurus repo
├── drafts/{locale}/                    in-place:      same dir as workspace
├── images/
└── videos/
```

The `deploy` command moves artifacts from workspace to target with transforms.
For `preset: standalone`, deploy is a no-op. For `docusaurus`, it does the
work described below.

## Detection phase (Docusaurus preset)

Before any write, deploy reads the target to understand its conventions.
Order of precedence (highest first):

1. **`<target>/CLAUDE.md`** — read if present. Look for:
   - Custom paths (any line matching `docs_path:`, `static_path:`, etc.)
   - Image conventions (e.g. "All images go in `static/screenshots/`")
   - i18n notes
   - Forbidden directories
   Treat content as advisory; show user what was extracted and confirm.

2. **`<target>/docusaurus.config.{ts,js,mjs}`** — parse if present:
   - `i18n.defaultLocale` → expected source locale
   - `i18n.locales` → allowed translation targets
   - `presets[0][1].docs.path` → custom `docs_path`
   - `staticDirectories[0]` → custom `static_path`
   If parse fails (TypeScript, complex config), fall back to step 3 and warn.

3. **Folder structure inference**:
   - `<target>/i18n/` exists → multi-locale enabled
   - `<target>/static/img/` exists → standard static dir
   - `<target>/docs/` exists → standard docs dir
   - Anything missing → ask user.

4. **`.docsmithrc.yaml` `docusaurus.*` overrides** — explicit user settings
   always win.

After detection, show **detected target config** to user for confirmation
before doing any writes. This is non-skippable on first deploy to a target.
Subsequent deploys cache detection in `documentation/deployments/<timestamp>/target-config.yaml`.

## Plan phase

Build the deploy plan. Each entry has:

| Field            | Example                                                           |
| ---------------- | ----------------------------------------------------------------- |
| `source_file`    | `documentation/drafts/en/getting-started.md`                      |
| `target_file`    | `<target>/docs/getting-started.md`                                |
| `transforms`     | `[inject_frontmatter, rewrite_image_refs, escape_mdx_specials]`   |
| `action`         | `create` / `update` / `skip` / `conflict`                         |
| `reason`         | `target file does not exist` / `content hash differs` / etc.      |

### Action determination

For each candidate file:

```
target file does not exist                    → create
target file exists, content hash matches      → skip
target file exists, hash differs, no --force  → conflict (block)
target file exists, hash differs, --force     → update
target file exists, hash differs, on_collision = overwrite  → update
target file exists, hash differs, on_collision = skip       → skip
target file exists, hash differs, on_collision = prompt     → ask
```

`conflict` always blocks the deploy. User must resolve via `--force`,
configure `on_collision`, or move the conflicting file out.

### Image namespacing

Workspace markdown:
```markdown
![Form filled with demo-vm name](/images/instances/create-form-filled.png)
```

After `rewrite_image_refs` with `product.slug = mycloud`:
```markdown
![Form filled with demo-vm name](/img/mycloud/instances/create-form-filled.png)
```

The image file is also copied:
- From: `documentation/images/instances/create-form-filled.png`
- To:   `<target>/static/img/mycloud/instances/create-form-filled.png`

This is why `product.slug` must be globally unique across all your products
that share a Docusaurus target. If two products both use slug `mycloud`,
their images collide.

### Frontmatter injection

For each markdown file, prepend Docusaurus frontmatter if absent:

```yaml
---
id: getting-started
title: Getting Started
sidebar_position: 1
---
```

- `id` derived from path: `getting-started.md` → `getting-started`,
  `instances/create.md` → `instances/create`
- `title` taken from first `# H1` in body (and the H1 is then *removed*
  from body to avoid double-titling — Docusaurus auto-renders frontmatter title)
- `sidebar_position` from sitemap order if available, else alphabetical
- If frontmatter already exists, merge — never overwrite user's explicit fields

### MDX escaping

Only applied to body prose (not code, not frontmatter, not raw HTML blocks).
Curly braces `{` and `}` are escaped to `\{` and `\}`. Angle brackets in
prose that look like JSX (`<Component>`) trigger a warning rather than auto-fix.

## Dry-run

`deploy --dry-run` runs detect + plan, prints the plan, then exits without
writing. Output structure:

```
Target: ../mycloud-docusaurus (docusaurus 3.x)
Detected config:
  docs_path: docs
  i18n_path: i18n
  static_path: static
  default_locale: en
  locales: [en, vi]

Plan summary:
  43 files to create
  8 files to update
  12 files unchanged (skip)
  2 conflicts (BLOCKING)

Conflicts:
  ! docs/getting-started.md
    Reason: target hash 9af3... differs from workspace hash bb12...
    Resolve: re-run with --force, or set on_collision: overwrite

New files:
  + docs/getting-started.md
  + docs/instances/create.md
  + i18n/vi/docusaurus-plugin-content-docs/current/getting-started.md
  + static/img/mycloud/instances/create-form-filled.png
  ...

Categories to generate:
  + docs/instances/_category_.json (label: "Instances", position: 2)
  + docs/storage/_category_.json   (label: "Storage", position: 3)

Undocumented folders in target (not in sitemap, will be left alone):
  ? docs/legacy/
  ? docs/internal-notes/
  → To hide these, see hide_undocumented in preset docs

Use --apply to execute, or --force to override conflicts.
```

## Apply phase

Only runs without `--dry-run` AND with no unresolved conflicts.

1. Create `documentation/deployments/<timestamp>-<target-name>/` audit folder
2. Write `manifest.yaml` with planned actions
3. Execute each action in order:
   - Markdown: read source → apply transforms → write target
   - Binaries (images, videos): copy bytes
   - Generated (`_category_.json`): write per categorize logic
4. After each batch, update `manifest.yaml` with actual results
5. Generate `diff.md` summarizing what changed
6. Print summary

## Audit trail

Every deploy creates `documentation/deployments/<timestamp>-<target>/`:

```
documentation/deployments/2026-04-26-103044-mycloud-docusaurus/
├── manifest.yaml          # planned + actual actions
├── target-config.yaml     # detected target config
├── diff.md                # human-readable summary
└── pre-deploy-state.txt   # target file hashes BEFORE deploy (for rollback)
```

Rollback (manual): use `pre-deploy-state.txt` to reset target files. Docsmith
does not auto-rollback — git on the target project is the proper safety net.

## In-place mode

When `deploy.default_target = .` or running `deploy --target .`:
- Detection runs against current directory
- Workspace and target are the same project
- Mappings still apply: `documentation/drafts/en/foo.md` → `docs/foo.md`
- Audit trail still created

This works because workspace files (`documentation/`) and Docusaurus files
(`docs/`, `static/`, etc.) are sibling subtrees that don't overlap.

## Categorize subcommand

`deploy` calls `categorize` internally if `generate_categories: true`.
Standalone `categorize` command is for re-running just this step:

1. Read `documentation/plan/sitemap.md`
2. Walk target `docs_path/` (after deploy) or workspace drafts (before deploy)
3. For each folder that appears in sitemap:
   - Generate `_category_.json` with normalized title from sitemap
   - Use `link.type: generated-index` so Docusaurus creates an index page
4. For folders NOT in sitemap:
   - List them, do not touch
   - Suggest user add to sitemap, exclude in docusaurus.config, or delete folder
5. Normalize titles in sitemap itself: title-case, consistent across siblings

### Title normalization rules

- Acronyms stay uppercase: `API`, `CLI`, `SQL`, `JSON`, `URL`, `HTTP`, `SSH`, `SSL`, `TLS`, `DNS`, `IP`, `TCP`, `UDP`, `XML`, `HTML`, `CSS`, `JS`, `TS`, `OS`, `IO`, `UI`, `UX`, `ID`
- Articles/conjunctions/prepositions lowercase mid-title: `a`, `an`, `the`, `and`, `or`, `but`, `to`, `of`, `for`, `with`, `in`, `on`
- First and last word always capitalized regardless
- Existing user titles in sitemap that pass these rules are preserved as-is
- Conflicts reported (e.g., sibling pages with inconsistent capitalization)

## Limitations (known)

1. **Sidebar control is opt-in**. Hiding undocumented folders requires
   `generate_sidebars: true`, which overrides user's `sidebars.js`. Default
   is to leave sidebars alone and only generate `_category_.json`.

2. **No automatic rollback**. Use git on target project.

3. **MDX edge cases**. Auto-escape handles `{}`. Angle brackets that look
   like JSX components are warned, not auto-fixed. Review the build log of
   your Docusaurus target after first deploy.

4. **TypeScript config detection** uses regex, not a real parser. If your
   `docusaurus.config.ts` is highly dynamic, set explicit values in
   `.docsmithrc.yaml` `docusaurus.*` to bypass detection.

5. **Translation auto-deploys empty if drafts missing**. v1.2.0 only scaffolds
   locale folder structure. Deploying with locale targets but no translation
   files will skip those locales and warn. Auto-translation is on the v1.6
   roadmap.
