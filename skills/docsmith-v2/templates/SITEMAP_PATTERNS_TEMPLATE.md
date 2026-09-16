# Sitemap Patterns Template

Defines the canonical sitemap structure docsmith uses across all modules in a project. Read by `plan` command. Picked once in project intake; applied to every module.

## Why this exists (v1.5.4+)

Before v1.5.4, AI generated each module's sitemap independently. Result: module A had `Quick Starts → Tutorials`, module B had `Guides → Reference`. Same project, inconsistent navigation. Users felt lost when moving between modules.

v1.5.4 fixes this with:

1. **Fixed section types** — every section in every sitemap maps to one of these types (no ad-hoc category names)
2. **3 project-level patterns** — pick once, applied everywhere
3. **AI suggestions** — when a module is missing a section that the project pattern includes, AI suggests adding it

---

## 1. Canonical section types

Every sitemap section must map to one of these. The `slug` is what becomes the folder name in deploy. The `display_name` is what users see.

| Slug              | Default display name       | Purpose                                              | Content style                       |
| ----------------- | -------------------------- | ---------------------------------------------------- | ----------------------------------- |
| `overview`        | Overview                   | Module landing page; what is this, who it's for      | 1 doc; ~200-400 words               |
| `initial-setup`   | Initial setup              | Prerequisites, account/permission setup              | 1 doc; checklist + steps            |
| `quickstarts`     | Quick Starts               | Group of short task-focused docs (5-10 mins each)    | List of how-tos                     |
| `tutorials`       | Tutorials                  | Group of step-by-step learning docs (hand-holding)   | List of tutorials                   |
| `guides`          | Guides                     | Group of how-to docs (task-focused, no hand-holding) | List of how-tos                     |
| `concepts`        | Concepts                   | Explanation docs (how things work, why)              | List of concept docs                |
| `dashboard`       | Dashboard                  | Doc(s) about a specific dashboard or report          | 1+ doc                              |
| `reference`       | Reference                  | Reference tables, parameter lists, schema specs      | List of reference docs              |
| `api-reference`   | API Reference              | Auto-generated API docs                              | Often auto-generated                |
| `glossary`        | Glossary                   | Term definitions                                     | 1 doc; alphabetical                 |
| `troubleshooting` | Troubleshooting            | Common issues and fixes                              | 1 doc OR list of FAQ                |

### Rules

- **Pick `quickstarts` OR `guides`, not both.** They overlap. Quick starts are typically beginner-friendly with full context; guides assume context. Most projects pick one based on their audience tech-level.
- **`tutorials` is for hand-holding learning.** Use only if you have multi-step learning content. Otherwise skip.
- **`concepts` only if non-obvious.** If your domain is conceptually simple (a CRUD product), skip it.
- **Display names can be customized** in project intake (e.g., rename `Quick Starts` to `Hands-on guides`). The slug stays canonical for deploy paths.

---

## 2. The three patterns

### Pattern A: Learning path (default)

Best for: **technical products with conceptual depth** where users need to learn before they can use. Examples: cloud platforms, observability tools, dev frameworks.

```
1. overview
2. initial-setup
3. quickstarts
4. tutorials
5. guides              (optional — only if both quickstarts AND tutorials present)
6. concepts            (optional)
7. reference
8. api-reference       (optional)
9. troubleshooting
10. glossary           (optional but recommended for jargon-heavy products)
```

Reasoning: surface entry points first (overview → setup → quickstart). Tutorials for those who want to learn. Reference at the end for lookup. Glossary last as appendix.

### Pattern B: Task-first

Best for: **mature products where users come knowing what they want**. Examples: established SaaS, pricing pages, support docs.

```
1. overview
2. quickstarts
3. guides              (or tutorials, pick one)
4. concepts            (optional)
5. reference
6. troubleshooting
7. glossary            (optional)
```

Reasoning: skip lengthy initial-setup (assume user already onboarded). Get them to actions fast. Reference for power users.

### Pattern C: Custom

User defines order in project intake `Custom sitemap order`. Format:

```yaml
custom_order:
  - overview
  - dashboard            # custom: dashboard before setup
  - initial-setup
  - quickstarts
  - reference
  - troubleshooting
```

Sections not listed are excluded entirely. Pattern C requires the user to think about IA but provides flexibility for unusual products.

### Pattern D: FPT User Guide (v1.6.0+)

Strict pattern enforcing FPT Cloud template requirements (see [FPT_TEMPLATES.md § Part 2](FPT_TEMPLATES.md)). Use this pattern when the documentation is for FPT Smart Cloud products and must comply with CSO-defined standards.

**Mandatory sections** (every module MUST have):

```yaml
mandatory:
  - overview         # Maps to FPT "Overview"
  - initial-setup    # Maps to FPT "Initial setup"
  - quick-starts     # Maps to FPT "Quick starts"
  - tutorials        # Maps to FPT "Tutorials"
```

**Optional sections** (may add per product):

```yaml
optional:
  - samples          # Maps to FPT "Samples"
  - faqs             # Maps to FPT "FAQs"
  - reference        # FPT-friendly extension
  - troubleshooting  # FPT-friendly extension
```

**Section name flexibility**: Optional sections can be renamed per product needs (e.g., "Samples" → "Examples", "FAQs" → "Common questions"). Mandatory sections keep canonical names for AI sitemap generation.

**Enforcement**:
- If a module is missing ANY mandatory section, `plan` STOPS and prompts user.
- `verify` Check 8 (sitemap pattern compliance) confirms mandatory presence.
- Cannot deploy a module that lacks mandatory sections (override with `--force-deploy`).

**Example sitemap output (Pattern D)**:

```markdown
# Sitemap

## Pattern: D (FPT User Guide)

## instances/
1. Overview                               (concept, mandatory)
2. Initial setup                          (how-to, mandatory)
3. Quick starts
   - Tạo instance đầu tiên                (tutorial, mandatory)
4. Tutorials
   - Deploy ứng dụng với Docker           (tutorial, mandatory)
   - Cấu hình auto-scaling                (tutorial, mandatory)
5. Samples                                (optional)
   - Sample: Node.js app
   - Sample: Python Flask
6. FAQs                                   (optional)
```

**When to use Pattern D**:
- Target deploy: FPT Cloud docs (the public docs site)
- Owner/CSO requires FPT template compliance
- Project intake `compliance: fpt-user-guide` set

---

## 3. Per-module section selection

Each module declares which sections it includes. Module intake has a "Sitemap sections" subsection with checkboxes:

```markdown
## Sitemap sections

For this module, include:
- [x] overview          (always required)
- [x] initial-setup     (skip if module has no specific setup)
- [x] quickstarts       (or guides — see project pattern)
- [ ] tutorials
- [ ] guides
- [ ] concepts
- [ ] dashboard
- [x] reference
- [ ] api-reference
- [x] troubleshooting
- [x] glossary
```

### AI suggestions

When user runs `/docsmith plan`, AI checks each module against the project pattern:

- If project pattern has `quickstarts` but a module didn't tick it → AI suggests:
  ```
  Module 'instances' is missing 'quickstarts' section.
  Project pattern A includes quickstarts.
  Suggest: tick [x] quickstarts in modules/instances.md, OR explicitly skip if module has no quick-task content.
  ```
- If user added a section the project pattern doesn't include → AI warns:
  ```
  Module 'storage' has 'concepts' ticked but project pattern A doesn't include concepts in default order.
  This module's concepts section will appear, but other modules without concepts will look incomplete.
  Suggest: add 'concepts' to project pattern OR remove from this module.
  ```

User decides per warning. AI does NOT auto-fix.

---

## 4. Sitemap generation logic

`plan` command produces `documentation/plan/sitemap.md`:

```markdown
# Sitemap

## Pattern: A (Learning path)

## instances/
1. Overview                               (1 doc)
2. Initial setup                          (1 doc)
3. Quick Starts
   - Create instance                      (how-to)
   - Edit instance settings               (how-to)
   - Delete instance                      (how-to)
4. Tutorials
   - Deploy your first app                (tutorial)
   - Set up auto-scaling                  (tutorial)
5. Reference
   - Instance types                       (reference)
   - Instance lifecycle                   (reference)
6. Troubleshooting                        (1 doc)
7. Glossary                               (1 doc)

## storage/
1. Overview                               (1 doc)
2. Initial setup                          (1 doc)
3. Quick Starts
   - Create a volume                      (how-to)
   - Attach volume to instance            (how-to)
4. Reference
   - Volume types                         (reference)
   - IOPS and throughput                  (reference)
5. Troubleshooting                        (1 doc)

⚠ INCONSISTENCY DETECTED:
- Module 'instances' includes Tutorials, module 'storage' does not.
- Per project Pattern A, both should include Tutorials if applicable.
- Recommendation: either add Tutorials to 'storage' (if it has step-by-step learning content),
  or explicitly mark 'storage' as not needing tutorials in modules/storage.md.

⚠ MISSING SECTIONS:
- Module 'storage' missing 'glossary' section (Pattern A includes glossary).
- Suggestion: tick [x] glossary in modules/storage.md if this module has domain-specific terms.
```

Warnings are informational. Plan still gets generated. User can:
- Update module intakes and re-run `plan`
- Update project pattern (rare; project-level decision)
- Document the exception explicitly in module intake notes

---

## 5. Display name customization

By default, slugs map to standard display names (table above). Project intake allows overriding:

```markdown
## Section display names (optional)

For each section type, you can override the default display name:

- overview: `Overview`                    (default)
- initial-setup: `Getting started`        (custom — was "Initial setup")
- quickstarts: `Hands-on guides`          (custom — was "Quick Starts")
- tutorials: `Tutorials`                  (default)
- guides: ``                              (n/a — not used in this project)
- reference: `API & reference`            (custom — was "Reference")
- glossary: `Glossary`                    (default)
- troubleshooting: `Troubleshooting`      (default)
```

These names appear in:
- `documentation/plan/sitemap.md`
- Generated `_category_.json` files (`label` field) on Docusaurus deploy
- Module index page headings

The slugs (lowercase, kebab-case) stay canonical and become folder names in deploy target.

---

## 6. Validation in `verify`

`/docsmith verify` (post v1.5.4) adds a sitemap consistency check:

```
[10/10] Sitemap consistency...
  ✓ All modules use project pattern A
  ✓ All modules have 'overview' section
  ⚠ Module 'storage' missing 'glossary' (project pattern A includes it)
  ⚠ Module 'instances' has 'concepts' but pattern A doesn't include it

  2 warnings — non-blocking. Fix or document exceptions in module intakes.
```

Sitemap inconsistency is a `warn` (non-blocking) by design — sometimes a module legitimately doesn't need a section. The user is the IA authority.

---

## 7. Migration from v1.5.3 and earlier

If you have an existing workspace from v1.5.3:

1. Run `/docsmith plan --migrate-sitemap`
2. AI proposes Pattern A as default (most common fit)
3. AI shows current per-module sections (extracted from existing drafts) and suggests which sections to tick
4. User confirms; AI updates project intake and module intakes
5. AI re-generates `sitemap.md` per new rules

Existing drafts are NOT modified. Only intake files and sitemap.md change.

For new projects (created with v1.5.4+): `init` adds the sitemap pattern selection to project intake automatically.
