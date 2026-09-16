# Video Script Template

Per-video script file used by `record` (audio generation) and `translate` (multi-locale script translation). Lives at `documentation/scripts/<module>/<asset-id>.md`. One file per video, regardless of how many locales the project has.

> Introduced in v1.5.7. Replaces earlier inline-script approach (script embedded in VIDEO markers) which polluted draft markdown.

## File location

```
documentation/scripts/<module>/<asset-id>.md
```

`<asset-id>` matches the `id` field of the corresponding `<!-- VIDEO ... -->` marker in the draft. `<module>` matches the module folder.

Example:
- Marker in `documentation/drafts/en/instances/create.md`:
  ```markdown
  <!-- VIDEO id: instance-create-tour -->
  ```
- Script file: `documentation/scripts/instances/instance-create-tour.md`

## Format

```markdown
---
id: instance-create-tour
module: instances
asset_path: documentation/videos/instance-create-tour.mp4
duration_target: 75s
voiceover_strategy: ai            # silent | ai | source-with-sub | human | inherit
voiceover_provider: local-piper   # only when voiceover_strategy = ai
generated_at: 2026-04-29T10:00:00Z
generated_by: docsmith-1.5.7
source_locale: en                 # matches project locales.source
---

# Source script (en)

<!--
  Edit this section for the source-language voiceover script.
  Each paragraph = one audio segment with timing markers in subtitle output.
  Aim for ~150 words per minute speaking rate (~2 seconds per short sentence).

  Use Markdown bold/italic to mark UI elements. The AI voiceover treats
  **Create Instance** as a UI label and reads it slightly emphasized.
-->

Welcome to MyCloud. In this video we'll create your first instance.

First, click the **Create Instance** button at the top right.

Fill in the name field. Choose a region from the dropdown.

Click **Submit**. Your instance will start within 30 seconds.

# Translation (auto-managed by /docsmith translate)

<!--
  Translated scripts go below as ## <locale> sections. The translate
  command populates these. Re-run translate after editing source script.

  Glossary at documentation/standards/glossary.<locale>.yaml applies.
  Per-block review gate (default batch mode) applies same as draft translation.
-->

## vi

(empty — run `/docsmith translate` to populate)

## jp

(empty — run `/docsmith translate` to populate)

# Notes

<!--
  Optional. Notes for video producer or future BA.
  NOT voiced. NOT translated. NOT included in any output.
-->

- Test with new account, no existing instances
- Speed: target 145-160 wpm
- Avoid ambient music if voiceover present
```

## Field reference

### Frontmatter

| Field                | Required | Default                     | Notes                                           |
| -------------------- | -------- | --------------------------- | ----------------------------------------------- |
| `id`                 | Yes      | —                           | Matches VIDEO marker `id`. Used as filename.    |
| `module`             | Yes      | —                           | Matches module folder name.                     |
| `asset_path`         | Auto     | inferred from id            | Where final video file lives.                   |
| `duration_target`    | Yes      | inherited from marker       | "75s", "1m30s", etc. Soft cap.                  |
| `voiceover_strategy` | No       | `inherit`                   | Per-video override of project policy.           |
| `voiceover_provider` | Conditional | inherits from project    | Only when strategy = `ai`.                      |
| `generated_at`       | Auto     | timestamp                   | Set when AI first creates this file.            |
| `source_locale`      | Auto     | from project intake         | Source language; defaults match `locales.source`. |

### Body sections

| Section heading            | Purpose                                              | Edit by      |
| -------------------------- | ---------------------------------------------------- | ------------ |
| `# Source script (<lang>)` | The source-language script                           | BA / writer  |
| `## <locale>`              | Translated script for one target locale              | translate AI |
| `# Notes`                  | Internal notes; not voiced, not translated           | BA / writer  |

## Workflow integration

### Initial creation (`record` command)

1. `record` scans drafts for `<!-- VIDEO id: <id> -->` markers
2. For each marker, looks up `documentation/scripts/<module>/<id>.md`
3. If file missing:
   - AI reads surrounding draft prose (the section containing the marker)
   - Generates initial source-language script (smooth, action-focused, target duration)
   - Writes to script file with `## <target-locale>` empty placeholders
   - Pauses for user review (similar to draft review gate)
4. User edits script if needed
5. On confirm, `record` proceeds: TTS generates audio, captures screen, encodes video

### Translate integration

When user runs `/docsmith translate`, AI processes BOTH drafts AND script files:

1. For each script file at `documentation/scripts/<module>/<id>.md`
2. For each target locale in `locales.targets`:
   - If `## <locale>` section is empty → translate source section
   - If `## <locale>` section has content → re-run protocol gate (Update / Overwrite / Skip)
3. Per-block review (or batch — depends on project intake) applies
4. Glossary applies same as draft translation

### Re-record after script edit

If user edits source script:

1. AI detects via file mtime + content hash (similar to source change detection)
2. On next `record`, asks: "Source script edited. Re-record? Y/N"
3. If yes: re-generate audio for source + all target locales (uses cached translated scripts if `## <locale>` sections still match)

If user edits a `## <locale>` section directly (overrides AI translation):

1. AI marks that locale's translation as "manually edited" in metadata
2. Re-translate command in Update mode preserves manual edit (KB inheritance)
3. Re-record uses the manually-edited script

### Source change in draft prose

If draft prose around VIDEO marker changes significantly:

1. `record --check` flags: "Draft section near `<id>` changed >20%; script may be stale"
2. User reviews script, decides if it needs update
3. AI does NOT auto-rewrite script (preserve user intent)

## Path mapping

| Artifact                           | Path                                                              |
| ---------------------------------- | ----------------------------------------------------------------- |
| Script source file                 | `documentation/scripts/<module>/<id>.md`                          |
| Source-locale audio                | `documentation/videos/voiceover/<id>.<source>.mp3`                |
| Per-locale audio                   | `documentation/videos/voiceover/<id>.<locale>.mp3`                |
| Subtitle (sidecar VTT)             | `documentation/videos/subtitles/<id>.<locale>.vtt`                |
| Final video (silent)               | `documentation/videos/<id>.mp4`                                   |
| Final video (with locale audio)    | `documentation/videos/<id>.<locale>.mp4` (when burn-in selected)  |

## Multi-locale strategies and script file behavior

### Strategy: Silent (default per v1.5.5)

Script file still useful — its content becomes on-screen text overlays:

- Source section drives default text overlays (English text, with timing)
- `## <locale>` sections drive per-locale text overlays
- No audio generation (silent video)

### Strategy: AI synthetic voice per locale

Script file is canonical:

- Source section → TTS for source locale
- Each `## <locale>` section → TTS for that locale
- Result: 3 audio files for 3-locale project

### Strategy: Source voice + per-locale subtitles

- Source section → TTS for source locale (single audio)
- Each `## <locale>` section → `.vtt` subtitle file
- Result: 1 audio file + N subtitle files

### Strategy: Human recorded

- Source script: ignored by `record` (BA/PM records manually)
- BA places recordings at `documentation/videos/voiceover/<id>.<locale>.mp3`
- `record` only does screen capture + encoding
- Translation: BA can fill `## <locale>` sections to track what should be recorded; not enforced by tool

## VIDEO marker simplified

Old format (pre-v1.5.7):
```markdown
<!-- VIDEO
id: instance-create-tour
duration: 75s
script: |
  Welcome to MyCloud...
  [40 lines of script in marker]
-->
```

New format (v1.5.7+):
```markdown
<!-- VIDEO id: instance-create-tour -->
```

That's it. All other config in script file frontmatter.

For backward compatibility (v1.5.4 markers), `record` reads old-style markers, extracts inline script, creates the new script file format, then suggests removing inline script from marker.

## Migration from v1.5.6

For new projects: just use v1.5.7. `record` creates script files automatically.

For existing v1.5.6 workspaces with inline scripts in VIDEO markers:
```bash
/docsmith record --migrate-scripts
```
- Scans drafts for inline-script VIDEO markers
- Creates `documentation/scripts/<module>/<id>.md` files from inline scripts
- Updates draft VIDEO markers to short form
- Backup old drafts to `documentation/archive/<ts>/`

## Limitations (v1.5.7)

- **No script versioning UI** — git history is the source of truth for script changes
- **No automatic script re-write** when draft prose changes — user must manually update
- **No timing track** for individual paragraphs in source script — TTS handles timing internally; only sentence-level timestamps exposed in VTT
- **No SSML support** — TTS providers that support SSML (pause, emphasis, prosody) accept full markdown but ignore SSML tags. v1.6+ may add SSML passthrough for power users
- **No multiple voices per script** — entire script uses one voice per locale. Dialog-style scripts with multiple speakers not supported
- **No audio mixing** — voiceover only, no background music or sound effects (user can post-process video manually)

## Cost implications

Adding script file per video has near-zero cost:

- File size: ~2-5 KB per video × 30 videos = ~150 KB total project
- Translation cost: same as before (translate command was always going to translate scripts; just clearer where they live now)
- Generation cost: AI initial script generation = 1 LLM call per video × number of new videos

The benefit is structural: scripts are reviewable, translatable, version-controllable as separate artifacts. Worth the small overhead.
