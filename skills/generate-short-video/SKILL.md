---
name: generate-short-video
description: Generate short Vietnamese-narrated UI walkthrough videos (≈40s .mp4 + .vtt) for BA feature docs. Uses Playwright for capture, gTTS for narration, and ffmpeg for muxing.
---

# /generate-short-video — Short UI Walkthrough Pipeline

## Mục đích

Sinh video hướng dẫn ngắn (30–45 giây) minh hoạ một luồng thao tác UI của portal:
- **Lời kể tiếng Việt** (gTTS) + phụ đề **VTT** đồng bộ từng câu.
- **Overlay con trỏ giả** với hiệu ứng click/highlight để người xem dễ theo dõi.
- Xuất **MP4 H.264** nhúng thẳng vào `docs/` bằng thẻ `<video>`.

Khi hoàn tất, video + VTT được đặt tại `docs/requirements/<domain>/<feature>/docs/videos/` và tham chiếu trong draft docs.

## Khi nào dùng

- BA muốn bổ sung clip minh hoạ cho một guide / reference doc.
- UI vừa đổi wording (label, dropdown, banner), cần quay lại cho đúng.
- Bổ sung hướng dẫn cho tính năng chưa có video (download, refresh, exclusion…).

## Khi nào KHÔNG dùng

- Video dài (> 60s), có dựng, voice-over người thật → dùng công cụ edit ngoài.
- Video yêu cầu demo tạo/xoá dữ liệu thật trên prod → cần approval riêng.
- Screenshot tĩnh đủ để giải thích → dùng `docs/images/` thay video.

---

## Pipeline tổng quan

```
narration/<id>-<slug>.txt                  (kịch bản tiếng Việt — mỗi câu 1 dòng)
  ↓ tts.py  (gTTS, ffmpeg concat với gap 400ms)
narration/<id>-<slug>.mp3  +  .vtt         (cue theo từng câu)
  ↓ record_v3.py  (Playwright + cursor overlay + Step(at_cue, fn))
raw/<id>-<slug>.webm  +  .load.txt         (độ dài trim intro)
  ↓ merge.sh  (ffmpeg trim + mux mp3 + libx264 aac)
docs/.../videos/<id>-<slug>.mp4 + .vtt     (sẵn sàng embed)
```

Tất cả chạy trong `.venv-video` (Python 3.12 + `playwright`, `gtts`, `ffmpeg` local).

---

## Quy ước đặt tên & nội dung

- **ID**: `vNNN` chạy tuần tự theo thứ tự tạo trong feature (v001, v002, …).
- **Slug**: kebab-case ngắn mô tả tác vụ (`dashboard-tour`, `exclude-resource`, `download-report`).
- **Độ dài**: 5–8 câu, tổng 30–45 giây sau khi TTS.
- **Lời kể**:
  - Ngắn, rõ, mỗi câu một ý.
  - Dùng đúng chữ UI hiện tại (ví dụ **Exclude and Refresh**, không dùng "exclude").
  - Không tuyên bố tính năng chưa ship (ví dụ Monthly frequency).
- **Con trỏ**: điều hướng mượt, highlight 2.5–4 s mỗi element để người xem kịp theo dõi.

---

## Các bước khi được gọi

### 1. Xác định feature và nội dung

Input tối thiểu:
- `<feature-folder>` — folder chứa `docs/drafts/` và `docs/videos/`.
- `<task>` — mô tả clip cần sinh (ví dụ "download report ở 3 scope").

Liệt kê video hiện có (`ls .../docs/videos/`), kiểm tra ID kế tiếp.

### 2. Viết narration script

Tạo `tools/video/narration/<id>-<slug>.txt`:
- Mỗi dòng là một câu hoàn chỉnh kết thúc bằng dấu `.` hoặc `?` hoặc `!`.
- Không dùng emoji, không dùng markdown.
- **Đối chiếu**:
  - Label UI (translation bundle `en/*.json` hoặc `vi/*.json`).
  - Tên route, nút, thông báo trong `pages/<feature>/`.
  - Known issues (bug, roadmap) — nếu liên quan, đề cập nhẹ để người xem biết workaround.

### 3. Sinh TTS + VTT

```bash
cd <repo-root>
source .venv-video/bin/activate
python tools/video/tts.py
```

Lệnh này regen toàn bộ các script trong `tools/video/narration/` (an toàn — overwrite mp3+vtt). Nếu chỉ muốn chạy cho 1 file, tạm thời đổi tên hoặc chỉnh `main()` — nhưng regen toàn bộ thường nhanh hơn.

Kiểm tra VTT: độ dài tổng khớp với kỳ vọng (30–45s).

### 4. Soạn clip function trong `record_v3.py`

Thêm `clip_v<NNN>(browser)` theo pattern hiện có:

```python
async def clip_v00X(browser):
    name = "v00X-<slug>"
    cues = parse_vtt(NARR / f"{name}.vtt")
    ctx, page, t0 = await make_context(browser, name)
    await page.goto(f"{BASE}/<path>", wait_until="domcontentloaded")
    await wait_for_content(page, '<ready-selector>', t0, name)

    async def c1(p): await hover_highlight(p, ['<sel>'])
    async def c2(p):
        await click_at(p, ['<sel>'])
        await p.wait_for_timeout(2500)
    # ... một Step cho mỗi cue cần action

    await run_timeline(page, cues, [
        Step(1, c1), Step(2, c2), ...
    ])
    await finalize(ctx, name)
```

Đăng ký vào `clips` list trong `main()`.

**Helper có sẵn**:
- `smooth_move(page, x, y)` — di chuyển cursor overlay mượt.
- `hover_highlight(page, selectors, hold_ms=3500)` — highlight vùng element.
- `click_at(page, selectors)` — click thật + hiệu ứng ring.
- `type_into(page, selectors, text)` — gõ từng ký tự.

**Nguyên tắc an toàn dữ liệu**:
- Không click nút mutate (Exclude and Refresh, Update, Delete) trừ khi có cơ chế revert ngay sau (xem `clip_v003`, `clip_v004`).
- Nút Refresh tạo scan thật → chỉ **hover**, không click.
- Nút Download ghi log truy cập → hover là đủ.
- Form sau khi edit → luôn bấm **Cancel** thay vì **Update** (xem `clip_v004`).

### 5. Chạy record

```bash
python tools/video/record_v3.py v00X   # chỉ clip này
# hoặc
python tools/video/record_v3.py        # tất cả
```

Output: `tools/video/raw/v00X-<slug>.webm` + `.load.txt`.

**Troubleshoot**:
- `click skip` / `ready miss`: selector không tìm thấy — check DOM trong browser thường trước.
- Staging đang down → mở `auth.json` trong headed mode, login lại, `python tools/video/auth.py` (nếu có).
- Timing lệch → kéo dài `hold_ms` hoặc dời cue.

### 6. Merge → MP4

```bash
./tools/video/merge.sh v00X-<slug>
# hoặc merge tất cả
./tools/video/merge.sh
```

Kiểm tra output: `docs/requirements/<domain>/<feature>/docs/videos/v00X-<slug>.mp4` (+ `.vtt`).

### 7. Embed vào draft doc

Chèn ngay trước hoặc sau section đang minh hoạ:

```markdown
<video controls width="100%" preload="metadata">
  <source src="../videos/v00X-<slug>.mp4" type="video/mp4" />
  <track kind="captions" src="../videos/v00X-<slug>.vtt" srclang="vi" label="Tiếng Việt" default />
  Trình duyệt của bạn không hỗ trợ thẻ video.
</video>

*Video hướng dẫn: <tiêu đề> (khoảng <N> giây, có phụ đề tiếng Việt)*
```

Path `../videos/` tính từ file markdown trong `docs/drafts/`.

### 8. Sync sang Docusaurus (khi BA cần publish)

Draft BA viết bằng MkDocs convention (`<video src="../videos/...">`, link `../../SRS.md`…). Docusaurus build sẽ fail với 3 vấn đề nếu copy trực tiếp:

1. **JSX video src**: Docusaurus chỉ rewrite Markdown `![](./img.png)` cho asset pipeline, **không** rewrite attribute JSX. Video trong `static/` phải được tham chiếu bằng URL tuyệt đối `/videos/<slug>/...`.
2. **Sidebar translation key collision**: khi folder lồng cùng tên (`docs/<slug>/<slug>/`), auto sidebar sinh 2 category cùng `sidebar.tutorialSidebar.category.<slug>` → i18n build lỗi. Fix: `_category_.json` với `"key": "<parent>-<self>"` unique.
3. **Link đến file BA-internal** (`../../SRS.md#...`, `../../DOMAIN_MODEL.md`) sẽ thành broken-link warning vì file không được copy sang.

Dùng script `tools/sync-to-docusaurus.sh` để tự động hoá cả 3 transform:

```bash
tools/sync-to-docusaurus.sh <feature-slug> <src-docs-root> <dst-docusaurus-repo>

# ví dụ
tools/sync-to-docusaurus.sh cloud-advisor \
  docs/requirements/compute/cloud-advisor/docs \
  ~/path/to/docusaurus-repo
```

Script sẽ:
- Copy `drafts/*.md` + `drafts/guides/` + `drafts/reference/` → `docs/<slug>/<slug>/`
- Copy `images/` → `docs/<slug>/<slug>/images/`
- Copy `videos/*.mp4` + `*.vtt` → `static/videos/<slug>/`
- Sed rewrite `../videos/` → `/videos/<slug>/` trong mọi md đã copy
- Ghi `_category_.json` với label title-case và `"key": "<slug>-<slug>"`
- Cảnh báo (không xoá) các link `](../../[A-Z_]+.md` còn sót — BA tự sửa draft rồi chạy lại.

Sau khi sync, chạy `cd <docusaurus-repo> && npx docusaurus build` để xác nhận.

**Phòng trước cho draft mới**: nếu muốn đỡ phải scrub link, chuyển tham chiếu sang SRS.md/DOMAIN_MODEL.md thành plain text (ví dụ "tracked as known issue BUG-CA-01") ngay trong draft — cả MkDocs lẫn Docusaurus đều chấp nhận.

### 9. (Tuỳ chọn) Lint + commit

```bash
prc/tools/lint <feature>/docs/drafts/<file>.md
git add tools/video/narration/ tools/video/record_v3.py \
        <feature>/docs/videos/ <feature>/docs/drafts/<file>.md
```

Không tự commit trừ khi user yêu cầu.

---

## Checklist xuất bản

- [ ] Narration đã đọc qua — không có label sai, không có tính năng chưa ship.
- [ ] VTT cue tổng 30–45s.
- [ ] Record chạy xong không có `FAILED` hoặc `click skip` ở step chính.
- [ ] MP4 phát được, audio khớp visual.
- [ ] Draft md đã nhúng `<video>` đúng relative path.
- [ ] Dữ liệu mutate đã revert (unchecked checkbox, Cancel form, switch OFF).
- [ ] (Nếu publish Docusaurus) chạy `tools/sync-to-docusaurus.sh`, build sạch không warning.

---

## File quan trọng

| File | Vai trò |
|------|---------|
| `tools/video/tts.py` | gTTS → mp3 + VTT |
| `tools/video/record_v3.py` | Playwright capture + cursor overlay |
| `tools/video/merge.sh` | ffmpeg trim + mux → mp4 |
| `tools/video/auth.json` | Playwright storage state (login) |
| `tools/video/narration/*.txt` | Kịch bản tiếng Việt |
| `tools/video/narration/*.{mp3,vtt}` | TTS output |
| `tools/video/raw/*.webm` | Capture thô |
| `docs/.../docs/videos/*.mp4` | Output cuối cùng |

---

## Ghi chú mở rộng

- **Đổi base URL**: sửa `BASE` trong `record_v3.py` nếu feature nằm module khác.
- **Đổi viewport**: `viewport` và `record_video_size` trong `make_context` (mặc định 1280×720).
- **Đổi giọng / tốc độ TTS**: gTTS chỉ có `lang="vi"` chuẩn; để đổi giọng, cân nhắc `edge-tts` (đã cài trong venv).
- **Subtitle ngôn ngữ khác**: tạo thêm file `.vtt` song song (`srclang="en"`) và khai báo trong `<track>`.
