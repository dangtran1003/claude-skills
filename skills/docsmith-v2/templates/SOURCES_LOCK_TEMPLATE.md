# Sources Lock Template

Tracks fetched state of external knowledge sources for change detection. Auto-generated and managed by `fetch` and `update` commands. Users typically don't edit directly.

## File location

`documentation/intake/sources.lock.yaml`

## Format

```yaml
# Auto-generated. Do not edit manually.
# Updated by: /docsmith fetch, /docsmith update
generated: 2026-04-26T15:20:00Z
schema_version: "1.5.0"

# Per-module source tracking
modules:

  # Project-level sources (from project.md "Knowledge sources" section)
  _project:
    sources:
      - id: notion-abc123
        type: notion
        page_id: abc123
        name: "Project PRD"
        url: https://notion.so/abc123
        auth_env: NOTION_TOKEN
        last_fetched: 2026-04-25T09:30:00Z
        version: "v47"                       # Notion edit version number
        last_edited_remote: 2026-04-25T08:15:00Z
        content_hash: sha256:f9a8b7c6d5e4...  # hash of fetched content
        cache_path: documentation/.cache/sources/notion-abc123.md

      - id: github-mycloud-cloud-arch
        type: github
        repo: mycloud/cloud
        paths: ["docs/architecture.md"]
        auth_env: GITHUB_TOKEN
        last_fetched: 2026-04-25T09:30:00Z
        commit_sha: deadbeef1234567890abcdef
        files_hashes:
          "docs/architecture.md": sha256:1a2b3c...
        cache_path: documentation/.cache/sources/github-mycloud-cloud-arch/

  # Module-specific sources (added on top of project-level for this module)
  instances:
    sources:
      - id: notion-prd-instances
        type: notion
        page_id: xyz789
        name: "Instances PRD"
        url: https://notion.so/xyz789
        auth_env: NOTION_TOKEN
        last_fetched: 2026-04-25T09:30:00Z
        version: "v12"
        last_edited_remote: 2026-04-24T14:00:00Z
        content_hash: sha256:abc123...
        cache_path: documentation/.cache/sources/notion-prd-instances.md

      - id: github-mycloud-cloud-instances
        type: github
        repo: mycloud/cloud
        paths:
          - "api/instances/*.ts"
          - "docs/instances/*.md"
        auth_env: GITHUB_TOKEN
        last_fetched: 2026-04-25T09:30:00Z
        commit_sha: cafe1234567890abcdef
        files_hashes:
          "api/instances/create.ts": sha256:...
          "api/instances/list.ts": sha256:...
          "api/instances/delete.ts": sha256:...
          "docs/instances/overview.md": sha256:...
        cache_path: documentation/.cache/sources/github-mycloud-cloud-instances/

      - id: gdrive-ux-research
        type: gdrive
        file_id: 1AbCdEf
        name: "Instances UX research"
        auth_env: GOOGLE_DRIVE_TOKEN
        last_fetched: 2026-04-25T09:30:00Z
        revision_id: rev45
        modified_time_remote: 2026-04-20T14:30:00Z
        content_hash: sha256:def456...
        cache_path: documentation/.cache/sources/gdrive-ux-research.md

      - id: file-feature-list
        type: file
        path: ../product-docs/feature-list.md
        last_fetched: 2026-04-25T09:30:00Z
        mtime: 2026-04-22T10:00:00Z
        content_hash: sha256:ghi789...
        # No cache_path; file is read directly when needed

      - id: url-public-changelog
        type: url
        url: https://example.com/changelog
        last_fetched: 2026-04-25T09:30:00Z
        etag: '"a1b2c3d4"'                   # if server provided
        last_modified_remote: 2026-04-23T00:00:00Z
        content_hash: sha256:jkl012...
        cache_path: documentation/.cache/sources/url-public-changelog.html

  storage:
    sources:
      - id: notion-prd-storage
        # ... similar shape
```

## Field reference

### Common to all source types

| Field             | Description                                                            |
| ----------------- | ---------------------------------------------------------------------- |
| `id`              | Stable identifier; used as filename in cache. Format: `<type>-<slug>`. |
| `type`            | One of: `notion`, `github`, `gdrive`, `url`, `file`                    |
| `name`            | Human-readable name from intake form                                   |
| `auth_env`        | Env var name (not the token itself); empty for public sources          |
| `last_fetched`    | When `fetch` last pulled this source                                   |
| `content_hash`    | SHA-256 of fetched content; used for change detection                  |
| `cache_path`      | Where fetched content is cached locally                                |

### Type-specific fields

**notion**:
- `page_id` — Notion page ID (extracted from URL)
- `version` — Notion edit version
- `last_edited_remote` — Notion's `last_edited_time` field

**github**:
- `repo` — `owner/repo` form
- `paths` — list of paths or globs included
- `commit_sha` — full SHA of the commit at fetch time
- `files_hashes` — per-file content hashes (for partial change detection)

**gdrive**:
- `file_id` — Google Drive file ID
- `revision_id` — Drive's revision ID at fetch time
- `modified_time_remote` — Drive's `modifiedTime` field

**url**:
- `url` — full URL
- `etag` — server-provided ETag if available
- `last_modified_remote` — server-provided Last-Modified header

**file**:
- `path` — relative or absolute path
- `mtime` — local file modification time at fetch
- (No `cache_path`; file is read live when needed)

## How `update` uses this

```bash
/docsmith update instances
```

1. Read current `sources.lock.yaml`
2. For each source under `modules.instances`:
   - Fetch CURRENT remote metadata (cheap call: HEAD/metadata API, not full content)
     - Notion: `GET /pages/{id}` → check `last_edited_time`
     - GitHub: `GET /repos/{owner}/{repo}/commits?path={path}&per_page=1` → check latest SHA
     - GDrive: `files.get` → check `modifiedTime`
     - URL: `HEAD` → check `Last-Modified` / `ETag`
     - File: `stat` → check `mtime`
   - Compare with locked version
3. For changed sources, full-fetch new content, update hash, list as "changed"
4. Show user: which sources changed, which are unchanged
5. If user proceeds → re-run pipeline for affected module with fresh content
6. After re-run, write new lock entry

## Cache management

- `documentation/.cache/sources/` is gitignored by default (added to `.gitignore` in `init`)
- Cache invalidation: when source changes (hash mismatch), cache is overwritten
- Manual purge: delete `.cache/sources/` to force full re-fetch on next `fetch`

## When lock file is created/updated

| Event                              | Lock file action                        |
| ---------------------------------- | --------------------------------------- |
| `/docsmith fetch` (initial)        | Create lock file with all sources       |
| `/docsmith fetch` (incremental)    | Update entries for fetched sources      |
| `/docsmith update <module>`        | Update entries for that module's sources after re-fetch |
| `/docsmith run`                    | Calls `fetch` internally; updates lock  |
| Source removed from intake.md      | Entry removed from lock on next `fetch` |
| Module archived (status: Archived) | Module's entries kept but skipped in update |

## What the lock file does NOT track

- Caption changes in screenshots (handled by walkthrough drift)
- Doc draft changes (those are in git directly)
- Translation drift (separate metadata in translated file frontmatter)
- Voice chart updates (project-level, not source-level)
