# Media Policy Template

Definitive reference for screenshot and video rules in docsmith. Read by `walkthrough` (capture screenshots) and `record` (capture videos) commands. Configured once in project intake § 11; overridable per module in module intake § 8.

## Why this exists (v1.5.5+)

Before v1.5.5, screenshot and video rules were scattered:
- Caption rules in `MEDIA_POLICY_TEMPLATE.md § 3.5`
- Video markers in `VIDEO_SCRIPT_TEMPLATE.md § VIDEO marker`
- Privacy fields in module intake
- No density rules (1 ảnh / N từ?), no length rules, no voiceover policy, no per-locale strategy

Result: AI generated different screenshot densities per module, videos with inconsistent length, no clear story for multi-locale.

v1.5.5 consolidates all media decisions into one config block + this reference.

---

## 1. Screenshot density per content type

How many screenshots a doc should have, by content type:

| Content type     | Density rule                                  | Required?     | Reasoning                                            |
| ---------------- | --------------------------------------------- | ------------- | ---------------------------------------------------- |
| `tutorial`       | 1 / major step (5-10 ảnh / doc)              | **Required**  | Hand-holding learning needs visual confirmation      |
| `how-to`         | 1 / heading (3-5 ảnh / doc)                  | **Required**  | Task-focused; visual anchor per stage                |
| `reference`      | 0 (text + tables only)                       | Optional       | Tables/code blocks are the content                   |
| `concept`        | 0-1 (illustration only if abstract concept)  | Optional       | Prose-driven; ảnh chỉ khi cần                        |
| `troubleshooting`| 1 / error case                               | Recommended   | User comparing their error to doc — needs visual     |
| `quickstart`     | 1 / heading + 1 final state                  | **Required**  | Quick-glance guidance                                |

Override per module in module intake § 8 if a specific module needs different density.

### When to break the rule

- **Repetitive screenshots** — if 5 screenshots in a tutorial differ only by 1 field value, AI consolidates to 2 (start + end state)
- **Dense UIs** — if UI has many fields, 1 screenshot may need annotation overlay (arrows, callouts) instead of multiple plain screenshots
- **Sensitive workflows** — if every screenshot needs heavy redaction (account IDs, emails), AI suggests reducing count

---

## 2. Screenshot style

### Style options (single-select per project)

| Style              | Description                                       | When to use                                  |
| ------------------ | ------------------------------------------------- | -------------------------------------------- |
| `viewport-only`    | Just the rendered viewport, no browser chrome    | **Default** — clean, fits Docusaurus content |
| `full-window`      | Includes URL bar, tabs                           | When URL is part of the instruction          |
| `cropped-element`  | Crop to relevant element + 20px padding          | UI is dense; focus on one component          |
| `annotated`        | Viewport + overlay arrows / numbered callouts    | Requires manual edit step OR AI annotation   |

### Aspect ratio

| Ratio              | Resolution        | When to use                                  |
| ------------------ | ----------------- | -------------------------------------------- |
| `16:9-desktop`     | 1280×720          | **Default** — standard desktop UIs           |
| `4:3-legacy`       | 1024×768          | Legacy admin panels                          |
| `mobile-portrait`  | 375×812           | Mobile-first products                        |
| `square`           | 1080×1080         | Marketing-style social-media-ready           |
| `custom`           | User-specified    | Edge cases                                   |

### File format

- **PNG** (default) — lossless, works for UI screenshots
- **JPEG** — only when file size critical (large illustration screenshots)
- **WebP** — modern, smaller; only if Docusaurus build supports it

docsmith always saves as PNG. Conversion to other formats happens at deploy if configured.

---

## 3. Per-locale screenshot strategy

When project has multiple locales, decide if screenshots are localized:

### Option A: Source-only (default in v1.5.5)

- Capture in `locales.source` (e.g., EN) UI only
- Translated docs (VI, JP) reuse the same screenshots
- Add note in target docs: *"Screenshots are shown in English UI"*
- **Cost**: 1× walkthrough run
- **UX cost**: target users see English UI in their language doc — confusing if they don't read EN

### Option B: Per-locale capture

- Walkthrough runs N times (once per locale), product UI must support locale switching
- Each translated doc has its own screenshot
- **Cost**: N× walkthrough run time + storage + per-locale image namespace
- **UX cost**: zero — native experience

### Option C: Hybrid

- Source locale: full capture (every screenshot)
- Target locales: only re-capture screenshots showing **user-visible UI text** (login form, error messages, onboarding)
- Skip re-capture for: dashboards, lists, generic flows
- **Cost**: medium
- **UX cost**: low for important touchpoints

### How to switch (project intake)

```markdown
Per-locale screenshots:
- [x] Source-only — capture EN, reuse for VI/JP (default)
- [ ] Per-locale — capture per target locale
- [ ] Hybrid — see MEDIA_POLICY § 3 for "important touchpoints" list
```

### Image namespacing per locale

When per-locale (Options B or C), images go to:

```
documentation/images/<module>/<asset>.png            ← source locale (default)
documentation/images/<module>/<locale>/<asset>.png   ← target locale override
```

Deploy maps these to:
```
<target>/static/img/<slug>/<module>/<asset>.png            ← shared
<target>/static/img/<slug>/<locale>/<module>/<asset>.png   ← per-locale
```

In v1.5.5 minimal scope, default is **source-only**. Per-locale paths are supported but require explicit opt-in.

---

## 3.5 Caption writing rules (consolidated v1.5.14+)

The caption is the **contract** between the doc and the screenshot. The walkthrough uses the caption to match content. Vague captions cause wrong screenshots.

### When to include a screenshot

Include when AT LEAST ONE applies:
- UI element has to be located (saves the user from "the small icon in the top right corner with three dots")
- State changes visibly (modal opens, form submitted, item moves)
- Confirmation of success (end of procedure)
- Layout matters (dashboards, list views with key columns)

Do NOT include when:
- Content is a definition/concept/list (use table or diagram)
- Content is CLI input/output (use code block — searchable, accessible)
- Screenshot would only show generic chrome (browser tabs, OS taskbar)
- State shown is identical to a screenshot two paragraphs above

### Rule A: Describe what is on screen, not what the user does

| Bad (action) | Good (state) |
|---|---|
| `![Click the Create button](...)` | `![Compute Instances list with empty state and Create button visible at top right](...)` |
| `![Filling out the form](...)` | `![Create Instance form with Name field set to "demo-vm" and Ubuntu 22.04 selected](...)` |
| `![Submit the form](...)` | `![Create Instance form fully filled, Submit button enabled](...)` |

### Rule B: Be specific about data and state

| Vague | Specific |
|---|---|
| `![Instance list](...)` | `![Instance list with 3 running instances sorted by creation date](...)` |
| `![Settings page](...)` | `![Settings > Network tab with "Auto-assign IP" enabled](...)` |
| `![Dashboard](...)` | `![Dashboard showing 0 alerts and 5 active resources](...)` |

### Rule C: Reference UI by label, not by appearance

Labels are stable across themes; colors and positions are not.

| Bad | Good |
|---|---|
| `![The blue button at the top](...)` | `![Page header with "Create Instance" button](...)` |
| `![Icon in the corner](...)` | `![Page header with Help icon (question mark)](...)` |

### Rule D: Place the placeholder AFTER the step it illustrates

The walkthrough builds context from the lines above the placeholder. Putting the screenshot before the step leaves the placeholder context-free.

```markdown
3. Click **Create Instance**.

   ![Compute Instances list with Create Instance button highlighted](https://placehold.co/600x400)

4. In the form, enter the instance name and select an image.

   ![Create Instance form with Name and Image fields filled](https://placehold.co/600x400)
```

### File naming conventions

- Lowercase, hyphen-separated, no spaces
- Named for **what the asset is**, not what it looks like
- Folder by module, not by doc

```
documentation/images/
├── instances/
│   ├── instances-list-empty.png
│   ├── instance-create-form-empty.png
│   ├── instance-create-form-filled.png
│   └── instance-create-success.png
├── storage/
│   └── ...
```

Bad: `screenshot-of-blue-button.png`, `step-3.png`, `image1.png`
Good: `instance-create-form-filled.png`, `network-settings-firewall-rules.png`

### State that cannot be reproduced

If a screenshot requires data state AI cannot create reliably (long-running process, specific historical data, customer records), **keep the placeholder** in the doc and document the reason in the walkthrough execution record. Don't delete; don't capture inaccurate substitute.

### Pre-walkthrough caption review

Before `walkthrough` captures, it presents the screenshot capture plan for review. Captions that fail Rules A–C are flagged. Fix in draft, re-run.

### When in doubt

A good caption is one where someone reading ONLY the caption (no surrounding text) could roughly imagine what the screenshot shows. If you cannot, neither can the AI.

---

## 4. Video density per content type

| Content type      | Video required?   | Length cap | Reasoning                                  |
| ----------------- | ----------------- | ---------- | ------------------------------------------ |
| `tutorial`        | **Required**      | ≤ 90 s     | Tutorials benefit most from video tour     |
| `how-to`          | Optional (if >5 steps) | ≤ 30 s | Short tasks: ảnh đủ; >5 steps: video helps |
| `reference`       | Never             | —          | Reference is lookup, not flow              |
| `concept`         | Optional (animation) | ≤ 2 min | Abstract concepts benefit from animation   |
| `troubleshooting` | Never             | —          | Error fixes are quick; ảnh đủ              |
| `quickstart`      | Optional          | ≤ 60 s     | If "see the whole flow at once" valuable   |

Override per module in module intake § 8.

### Why length caps matter

- > 2 min videos: completion rate drops below 40%
- < 30 s videos: not enough time to actually demonstrate
- 60-90 s sweet spot for instructional content

docsmith warns when a `record` plan exceeds the cap; user can override but should justify.

---

## 5. Voiceover strategy

User picks in project intake. Affects video production cost dramatically.

**Source for voiceover content (v1.5.7+)**: voiceover audio (TTS or human) reads from per-video script files at `documentation/scripts/<module>/<asset-id>.md`. Scripts have source-language content + per-locale translations under `## <locale>` headings. See [VIDEO_SCRIPT_TEMPLATE.md](VIDEO_SCRIPT_TEMPLATE.md) for the script file format.

### Strategy A: Silent + on-screen captions (default in v1.5.5)

- No audio track
- Text overlays on video describe the action ("Click Create", "Enter name")
- Music: optional ambient (off by default)
- **Cost**: cheapest, instant
- **Accessibility**: high (no audio dependency)
- **Multi-locale**: 1 video file per content; captions are per-locale text overlays generated from translated drafts
- **Caveat**: requires good text overlay design; user can't multitask

### Strategy B: AI synthetic voice per locale

- One audio track per locale (3 locales = 3 audio files = 3 video outputs)
- Generated from script via TTS (see § 6)
- **Cost**: TTS API calls + N× generation
- **Quality**: depends on TTS provider
- **Multi-locale**: native voice per locale

### Strategy C: Source voice + per-locale subtitles

- One audio track in source locale (e.g., EN voiceover)
- Per-locale `.vtt` subtitle files
- **Cost**: 1× voiceover + N× translation of script
- **UX**: target users hear EN, read translated subtitle
- **Caveat**: not ideal for non-EN-speaking audiences

### Strategy D: Human recorded voiceover

- Manual recording step (out of docsmith)
- docsmith expects audio file at `documentation/videos/voiceover/<asset>.<locale>.mp3`
- **Cost**: human time
- **Quality**: highest
- **Use case**: marketing videos, premium content

### Decision matrix

| Use case                          | Recommended       |
| --------------------------------- | ----------------- |
| Multi-locale, internal docs       | A (silent)        |
| Multi-locale, marketing-grade     | B (AI per-locale) |
| Single-locale, casual            | A or D            |
| Compliance / regulated content    | D (human)         |
| Tight budget, multi-locale        | C (source + sub)  |

---

## 6. TTS providers (when Strategy B selected)

Pick one TTS provider. docsmith doesn't switch providers per module.

### Provider list

| Provider             | Quality        | Cost          | Latency  | Local? | Notes                                    |
| -------------------- | -------------- | ------------- | -------- | ------ | ---------------------------------------- |
| `local-piper`        | Medium         | Free          | Fast     | ✅     | **Default** — offline, no API key       |
| `local-coqui`        | Medium-High    | Free          | Medium   | ✅     | More voices, slower                      |
| `openai`             | High           | $15/1M chars  | Fast     | ❌     | Wide language support                    |
| `elevenlabs`         | Highest        | $5-99/mo      | Fast     | ❌     | Best for marketing-grade                 |
| `google-cloud`       | High           | $4/1M chars   | Fast     | ❌     | Wide language support, good Vietnamese   |
| `azure-cognitive`    | High           | $4/1M chars   | Fast     | ❌     | Many neural voices                       |

### Why local-first default

- No API key required → fewer setup blockers
- Free → no cost surprise
- Offline → CI works without internet
- Quality: medium but acceptable for instructional content
- Trade-off: voice less natural than ElevenLabs/OpenAI

If user wants better quality, opt into a paid provider via project intake.

### Per-provider config

#### local-piper (default)

```markdown
TTS provider: local-piper
Voice model: en_US-amy-medium  (default for EN)
Voice models per locale (override default):
- en: en_US-amy-medium
- vi: vi_VN-25hours_single-low
- jp: ja_JP-nemo-low
Auth env var: (none — local)
Install: pip install piper-tts && piper --download-voice <model>
```

#### local-coqui

```markdown
TTS provider: local-coqui
Voice model: tts_models/en/vctk/vits  (default for EN)
Auth env var: (none — local)
Install: pip install TTS && python -m TTS.bin.list_models
```

#### openai

```markdown
TTS provider: openai
Voice ID: alloy  (or: echo, fable, onyx, nova, shimmer)
Auth env var: OPENAI_API_KEY
Speed: 1.0  (range: 0.25-4.0)
Model: tts-1  (or: tts-1-hd for higher quality)
```

#### elevenlabs

```markdown
TTS provider: elevenlabs
Voice ID: 21m00Tcm4TlvDq8ikWAM  (Rachel default)
Auth env var: ELEVENLABS_API_KEY
Stability: 0.5  (range: 0-1)
Similarity boost: 0.75  (range: 0-1)
Model: eleven_multilingual_v2
```

#### google-cloud

```markdown
TTS provider: google-cloud
Voice name: en-US-Wavenet-D  (or many others)
Auth env var: GOOGLE_APPLICATION_CREDENTIALS  (path to service account JSON)
Speaking rate: 1.0
Pitch: 0
```

#### azure-cognitive

```markdown
TTS provider: azure-cognitive
Voice name: en-US-JennyNeural
Auth env vars:
  - AZURE_SPEECH_KEY
  - AZURE_SPEECH_REGION
Style: chat  (or: cheerful, sad, etc.)
```

### Voice selection per locale

When voiceover strategy is B (AI per-locale), each locale needs a voice:

```markdown
Voice per locale:
- en: alloy / en_US-amy-medium / etc.  (depending on provider)
- vi: vi_VN-25hours_single-low (Piper) or vi-VN-Wavenet-A (Google)
- jp: ja_JP-nemo-low (Piper) or ja-JP-Wavenet-A (Google)
```

Provider must support all listed locales. Azure has best Vietnamese; Google has good multi-language; ElevenLabs limited to ~30 langs.

---

## 7. Subtitles / captions

When to generate `.vtt` subtitle files alongside videos.

### Generation strategies

#### From AI script (when voiceover Strategy A or B)

When voiceover is silent (A) or AI-generated (B), the script is known text. Generate `.vtt`:

- Word-level timestamps from TTS API (most providers expose them)
- Sentence-level fallback (split script by punctuation, distribute timestamps evenly across video duration)
- Result: deterministic, accurate

```vtt
WEBVTT

00:00:00.000 --> 00:00:03.500
Welcome to MyCloud. In this video we'll create your first instance.

00:00:03.500 --> 00:00:07.000
Click the Create Instance button in the top right.
```

#### From STT (when voiceover Strategy D — human)

When human recorded, transcribe with Whisper / Vosk / cloud STT:

- Less reliable
- May need manual correction
- Cost: STT API or local compute

### Per-locale subtitles

Strategy A (silent): `.vtt` per locale generated from translated drafts (the on-screen-text becomes the subtitle).

Strategy B (AI voice per locale): `.vtt` per locale generated from per-locale script.

Strategy C (source voice + sub): `.vtt` per locale generated from translated script; audio is source-locale only.

Strategy D (human): user must provide `.vtt` files manually OR docsmith runs STT.

### Burn-in vs sidecar

- **Burn-in** captions: text rendered ONTO video frames (one video per locale)
- **Sidecar** `.vtt`: separate file, browser/player overlays them (one video for all locales)

docsmith default: **sidecar `.vtt`** — flexibility, smaller storage. Docusaurus video plugin supports VTT tracks.

---

## 8. Project intake config (full schema)

Add this section to `documentation/intake/project.md`:

```markdown
## 11. Media policy (v1.5.5+)

### Screenshots

Density (override per module if needed):
- Tutorial: `1 per major step` (default)
- How-to: `1 per heading` (default)
- Reference: `none` (default)
- Concept: `optional` (default)
- Troubleshooting: `1 per error case` (default)
- Quickstart: `1 per heading + 1 final state` (default)

Style:
- [ ] viewport-only (default)
- [ ] full-window
- [ ] cropped-element
- [ ] annotated

Aspect ratio:
- [ ] 16:9 desktop (1280×720) (default)
- [ ] 4:3 legacy (1024×768)
- [ ] mobile-portrait (375×812)
- [ ] square (1080×1080)
- [ ] custom: ``

Per-locale strategy:
- [ ] Source-only (default — capture EN, reuse for VI/JP, note "EN UI" in translated docs)
- [ ] Per-locale (capture once per target locale)
- [ ] Hybrid (source full + selective per-locale for important touchpoints)

### Videos

Density (override per module if needed):
- Tutorial: `required, ≤ 90s` (default)
- How-to: `optional if >5 steps, ≤ 30s` (default)
- Reference: `never` (default)
- Concept: `optional, ≤ 2min` (default)
- Troubleshooting: `never` (default)
- Quickstart: `optional, ≤ 60s` (default)

Voiceover strategy:
- [ ] Silent + on-screen captions (default — cheapest)
- [ ] AI synthetic voice per locale
- [ ] Source voice + per-locale subtitles
- [ ] Human recorded voiceover
- [ ] No video at all (skip record command)

If "AI synthetic voice" — TTS provider:
- [ ] local-piper (default — free, offline)
- [ ] local-coqui (free, offline, more voices)
- [ ] openai (paid, high quality, wide languages)
- [ ] elevenlabs (paid, highest quality, ~30 languages)
- [ ] google-cloud (paid, wide languages, good Vietnamese)
- [ ] azure-cognitive (paid, many neural voices)

Voice ID/name per locale (only if AI voice):
- en: ``
- vi: ``
- jp: ``

Auth env var (only if non-local TTS):
- TTS provider env var: ``

### Subtitles / captions

Generate `.vtt`:
- [ ] No subtitles
- [ ] Source-only `.vtt`
- [ ] Per-locale `.vtt` (default if multi-locale)

VTT generation method (only if generating):
- [ ] Auto from script (default — works for Silent + AI voice strategies)
- [ ] STT after recording (only for human voiceover; needs Whisper or cloud STT)
- [ ] Manual user-provided `.vtt`

Burn-in or sidecar:
- [ ] Sidecar `.vtt` files (default — one video, multiple subtitle files)
- [ ] Burned into video (one video per locale, larger files)
```

---

## 9. Module intake override (§ 8)

Module intake adds:

```markdown
## 8. Media override (optional, inherit from project)

If this module's media policy differs from project, override below.
Leave checkboxes ticked under "Inherit from project" to use project defaults.

### Screenshot density

- [ ] Inherit from project (default)
- [ ] Override per content type:
  - Tutorial: ``
  - How-to: ``
  - Reference: ``
  - Concept: ``
  - Troubleshooting: ``
  - Quickstart: ``

### Video density

- [ ] Inherit from project (default)
- [ ] Skip videos for this module entirely
- [ ] Override per content type:
  - Tutorial: ``
  - How-to: ``
  - Concept: ``
  - Quickstart: ``

### Per-locale screenshots (this module only)

- [ ] Inherit from project (default)
- [ ] Force per-locale capture (when this module's UI varies significantly across locales)
- [ ] Force source-only (when this module's UI is identical across locales — skip per-locale even if project does it)

### Voiceover (this module only)

- [ ] Inherit from project (default)
- [ ] Skip voiceover for this module (silent only, even if project has AI voice)
- [ ] Use different TTS voice ID for this module: ``  (e.g., a more formal voice for compliance modules)
```

---

## 10. Validation

When `walkthrough` runs:
- Check screenshot density matches policy. If a draft has 0 screenshots but content type requires some, warn.
- Check screenshot style is one valid value
- Check aspect ratio is supported
- Check per-locale strategy matches project locales config

When `record` runs:
- Check video markers' content type matches policy (e.g., reference doc with `<!-- VIDEO -->` → warn; reference shouldn't have video)
- Check planned length ≤ cap
- If voiceover strategy = AI: check TTS provider env var is set (if non-local) OR local TTS binary is installed
- If voice ID per locale set: check provider supports that voice for that locale

When `verify` runs (post v1.5.5):
- Check #11: media compliance (consistent across modules, files actually exist, captions match drafts when sidecar VTT)

---

## 11. Cost estimation

For project with 3 locales (EN/VI/JP), 5 modules, 30 docs:

### Default config (silent + sidecar VTT)

- Screenshots: 1× walkthrough EN = ~30 min runtime
- Videos: 0 (silent gen instant, no TTS)
- Storage: ~15 MB images + ~50 MB videos
- TTS cost: $0
- Total time: ~1 hour

### Premium config (AI voice per locale + per-locale screenshots)

- Screenshots: 3× walkthrough = ~90 min runtime
- Videos: 30 docs × 3 locales = 90 audio files via OpenAI TTS = ~$5
- Storage: ~45 MB images + ~150 MB videos
- TTS cost: ~$5-10 first run; ~$1-2 per update
- Total time: ~3 hours first run, ~30 min update

User can start default and upgrade strategy later. Switch is non-destructive — old screenshots/videos stay until next walkthrough/record run.

---

## 12. Limitations (v1.5.5)

- **No pixel-perfect annotation** — `annotated` style requires manual edit step (Figma, Photoshop). v1.6+ may add AI annotation.
- **No video editing** — record produces single-take captures. No splicing, transitions, intros/outros.
- **No music library** — ambient music must be user-provided audio file.
- **No lip-sync verification** — when AI voice + screen capture, no check that voice timing matches actions on screen.
- **Per-locale subtitle generation from STT not yet implemented** — only from script (works for Silent + AI voice strategies).
- **Background blur in screenshots** — automatic for redaction fields only; not for general "blur backgrounds" aesthetic.

---

## 13. Migration from v1.5.4 and earlier

For new projects: `init` includes Media policy section in project intake.

For existing projects: run `/docsmith plan --migrate-media`. AI:
1. Inspects existing screenshots and videos
2. Proposes default config (silent + source-only screenshots + viewport-only style)
3. User confirms or adjusts
4. AI updates project intake § 11

Existing screenshots and videos NOT regenerated. Only new captures follow new policy.
