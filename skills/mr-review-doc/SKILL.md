---
name: mr-review-doc
description: "Use when the user asks to create/update a reviewer-facing Confluence page on $WIKI_URL — an MR/PR review doc, OR a bug/security/analysis report wiki page (\"tài liệu review\", \"trang wiki cho MR\", \"tạo report wiki\", \"page wiki báo cáo lỗi/bảo mật\", \"giải thích cho team\"). Produces an objective, outsider-readable page: context → how-it-works flow → why-it's-a-problem → how-fixed/impact → prioritized fixes; MR variant ends with REAL git diffs. Also covers the FCI Confluence house style + storage-format gotchas + PNG-diagram-via-REST pipeline. Examples: \"tạo tài liệu review cho MR này\", \"update thêm vào trang wiki\", \"tạo page wiki report vấn đề này\", \"viết report bảo mật lên wiki\"."
---

# MR Review Doc (Confluence)

Create a wiki page that lets a reviewer who did **not** write the code understand
*what changed, why it was a problem, and how it was fixed* — backed by **real git
diffs**, not prose. Tuned for the FCI on-prem Confluence (`$WIKI_URL`, Server/DC).

## Core principles

- **Viết cho người ngoài đọc — giọng tài liệu, không giọng cá nhân.** Trang là
  tài liệu tham chiếu, không phải nhật ký điều tra. Mô tả khách quan *"luồng X
  hoạt động thế nào"* (fact → hệ quả), KHÔNG dùng ngôi thứ nhất hay lời kể của
  người phát hiện. Chuyển mọi quan sát cá nhân thành phát biểu trung tính:
  - ❌ *"tôi click logout không thấy call gì / token cũ vẫn sống"*
  - ✅ *"Logout thực hiện bằng điều hướng cả trang (`window.location.href`) nên
    không xuất hiện ở tab XHR/Fetch của DevTools — request vẫn được gửi, dưới
    dạng Doc. Backend chỉ ghi blacklist chứ không đọc lại khi validate, nên cặp
    JWT portal vẫn hợp lệ sau logout."*

  Mỗi mục mở đầu bằng 1 câu nói mục đích (*"Phần này mô tả…"*). Bối cảnh cá nhân
  (ai/khi nào phát hiện) nếu cần thì gói **1 dòng** trong `info` banner đầu
  trang, đừng rải vào thân bài. Đặt tiêu đề mục theo chức năng (*"Luồng logout
  hoạt động thế nào"*), tránh tiêu đề theo cảm nhận (*"Chỗ này lạ"*).
- **Explain WHY before HOW.** Lead with the bug/cost and evidence (measured
  numbers, span durations, N+1 counts), then the fix.
- **Grounded in real diffs, rendered as rationale.** Read every hunk
  (`git diff base..tip -- <file>`) but do NOT paste hunks onto the page —
  GitLab already shows them. The page's job is the WHY per change (see
  template item 8). User's words: "git diff từng file tôi có thể xem trên
  git… tôi cần biết lý do mỗi dòng tại sao lại change như thế này".
- **Scale sections to the change.** A 1-file fix needs less than a multi-commit MR.

## Inputs to gather first

- The branch / commit range (e.g. `git log --oneline <base>..<tip>`). Find the
  MR base with `git merge-base master <branch>`.
- Which Confluence space + parent page. **Default for this user:** space `BSS`,
  parent `$REVIEW_PARENT_PAGE` ("MR Reviews", under your personal space) — all review
  pages live here. Confirm if unsure.
- Whether this is a NEW page or an UPDATE to an existing one (user often says
  "update thêm vào trang wiki" → expand an existing page).
- This repo uses the **reftable** git backend → use `git.exe` (Windows git), not
  Linux `git`.
- **Local artifacts folder:** save any HTML diagram / rendered PNG into
  `~/fci/notes/bdr/reviews/` (the user's dedicated review-files folder). Name
  them `<TICKET>-<topic>.html` / `.png`.

## Process

1. **Read the diffs.** For each changed file that matters:
   `git.exe show <commit> -- <path>` or `git.exe diff <base>..<tip> -- <path>`.
   Pull the real hunks. Identify 3–6 change *themes* (e.g. "drop full sync",
   "wipe-safe", "persist by PK").
2. **Draft the prose** following the content template below. Add inline comments
   to the diffs pointing at the hot spot (`# 384x servers() = 436s`) and the
   risk (`# push from stale DB -> can WIPE`).
3. **Add a before/after flow diagram** (see Diagrams).
4. **Publish** with `confluence_create_page` / `confluence_update_page`
   (`content_format="storage"`).
5. **Verify** (see Verify) — do not skip; this catches render bugs.

## Content template (scale to the change)

1. **`info` banner** — one-line result + scope + platforms + commit ids.
2. **TL;DR table** — before/after rows; use `status` macros (Red/Green) for the
   headline metrics.
3. **Luồng cũ** — how it worked (table of steps).
4. **Sơ đồ data-flow theo hàm — TRƯỚC vs SAU** (not just task-level). Rules:
   - **Function-level**: every function the MR removes/modifies/adds appears as
     a node, marked `(X)`=bỏ `(~)`=sửa `(+)`=mới; show the data flowing between
     nodes (`vm_data -> instance_id(PK) -> server_id -> vm_infra -> sg_ids`).
   - **Platform branches inline** when the flow touches both: `[OSP] ...` /
     `[VMW] ...` lines under the node (no-op, fallback, different mechanism).
   - **One diagram per flow** (create / delete / standalone task that other
     flows still call) — TRƯỚC and SAU as separate code blocks.
   - **Edge cases must appear as nodes/branches**, not be dropped: fallback
     paths, guards (None -> []), IntegrityError safety nets, SKIP/no-op
     branches, error-propagation (status_action=...).
   - Follow with **2 tables**: (a) mapping `Hàm bỏ (X) -> Thay bằng -> OSP/VMW`
     — including rows for "không thay (dead code)" and "chưa có thay thế (rủi
     ro còn lại ⚠️)"; (b) đối xử OSP vs VMW per hàm + cột "vì sao khác".
   - **Anti-lủng checklist**: after drafting, verify every changed file of the
     MR maps to ≥1 node/row, and grep the published page for the case markers
     (fallback, no-op, IntegrityError, guard, whitelist, …). Mẫu chuẩn: trang
     <page-id> (v6) mục 2.
5. **Vì sao tốn / sinh bug** — `warning` panel with the *evidence* (numbers).
6. **Đã fix thế nào** — per change-theme, prose, NO diffs here. Use a table when
   there are parallel platform branches (OSP vs VMW) or symmetric ops (add/remove).
7. **Đảm bảo data & phạm vi an toàn** — `panel`: data parity, side-effects kept,
   fallback, what is NOT touched. (Reviewers trust this section.)
8. **Giải trình theo file — lý do TỪNG thay đổi** (mục trung tâm của trang;
   user đọc song song với tab Changes trên GitLab). Per file một `<h4>` + bảng
   2 cột `Thay đổi (khối/dòng) | Tại sao đổi như vậy`. Mỗi khối diff trên
   GitLab phải có một dòng lý do ở đây. Trong lý do phải cover khi áp dụng:
   - **Chuỗi gọi cũ → mới**: hàm chạy trước/sau hàm nào, ai gọi, ai tiêu thụ
     giá trị trả về (task → controller → boundary).
   - **Xoá X vì sao an toàn**: bằng chứng 0-caller / route không đăng ký /
     cái gì thay vai trò.
   - **Invariant cũ → mới**: bước bị bỏ từng bảo vệ gì (kèm điều kiện cũ như
     whitelist/env), cơ chế mới giữ điều đó bằng cách nào.
   - **Contract đổi**: return shape mới, vì sao caller cần.
   - **Rủi ro còn lại**: nói thẳng (race window, mất wait_for_idle, …).
   Rule: nếu user từng hỏi "tại sao xoá/đổi cái này?" trong lúc làm MR, câu
   trả lời PHẢI nằm ở mục này.
9. **Test** — what was TDD'd + which suites pass.
10. **Code diff** — KHÔNG dán diff per-file lên trang (user xem trên GitLab).
    Chỉ 1 đoạn: link `$GITLAB_URL/.../merge_requests/<iid>/diffs` +
    base→tip. Ngoại lệ duy nhất được giữ `code` macro: sơ đồ ASCII TRƯỚC/SAU
    và snippet ngắn minh hoạ 1 ý trong prose (≤10 dòng). Mẫu chuẩn: trang
    <page-id> (v5).

## Diagrams (before/after flow)

**PNG is fully automatable** (verified 2026-06-12 on page <page-id> v7).
The MCP tool `confluence_upload_attachment` fails, but **direct REST upload
works** with Basic auth:

```
POST {URL}/rest/api/content/{page_id}/child/attachment
Headers: Authorization: Basic <user:token>, X-Atlassian-Token: nocheck
Body: multipart/form-data, field name="file"
```
(Credentials: same CONFLUENCE_USERNAME/API_TOKEN the mcp-atlassian server uses,
readable from `~/.claude.json`.)

Full PNG pipeline:
1. **Preferred style: graphviz dataflow** (user's reference: dataflow.png on
   page <page-id> — components are functions). No local `dot` binary → render
   DOT in the browser via viz.js CDN:
   `<script src="https://cdn.jsdelivr.net/npm/@viz-js/viz@3.2.4/lib/viz-standalone.js"></script>`
   then `Viz.instance().then(v => document.body.appendChild(v.renderSVGElement(dot)))`
   and set `document.title="ready"` when done (visible in the navigate result).
   DOT conventions: `rankdir=LR`; one yellow cluster (`bgcolor="#fefee0"`) per
   layer (celery task / controller / boundary / hạ tầng+DB); nested clusters
   `[OSP]` blue `#e3f2fd` / `[VMW]` orange `#fff3e0`; nodes = functions
   (lavender `#e8e8fb` default, red `#ffe3e3` = (X) bỏ, amber `#fff3c8` = (~)
   sửa, green `#dcf3dc` = (+) mới); removed paths as dashed red edges; DB as
   `shape=cylinder`, infra as `shape=box3d`; edge labels carry the data
   (`vm.ip`, `[sg_ids]`, `live ipAddresses ± vm.ip`). Save the .html (with the
   embedded DOT source, editable later) to
   `~/fci/notes/bdr/reviews/<TICKET>-<flow>-dataflow.html`.
   **Anti-clutter rules** (user: "quá nhiều mũi tên, rối mắt" — NHƯNG vẫn muốn
   TRƯỚC + SAU trong MỘT hình để thấy đủ thông tin):
   - **One digraph, two state bands**: `cluster_truoc` (bgcolor `#fff6f6`) on
     top, `cluster_sau` (`#f4fff4`) below — each band a SELF-CONTAINED LR
     pipeline (old edges never enter the new band). Link old→new with only
     2-3 dashed red `thay bang` edges using `constraint=false` (so they don't
     warp the layout). Needs `compound=true; newrank=true`.
   - Side-flows (sync_vms hardened, dead code) = standalone nodes inside the
     relevant band, dotted edge at most.
   - **Force a pure LR pipeline**: if a layer is both upstream AND downstream
     of another (call ping-pong, e.g. controller→boundary→controller), split
     that layer into 2 clusters ("X — tạo" / "X — finalize") so ranks flow
     left→right with no backward swooping edges.
   - **Fold DB-writes into node labels** (`-> DB: INSERT ...`) instead of
     drawing every write as an edge — a shared DB cylinder becomes an arrow
     magnet; keep ≤2-3 edges into it.
   - **Merge per-platform step chains into one node** per platform (e.g.
     "create_vm → server.id → get_vm_infra" as one [OSP] box).
   - Budget: ~12 edges per digraph; if more, split the flow.
   (Flexbox-column TRƯỚC|SAU HTML is the fallback if CDN is unreachable.)
2. Serve: `python3 -m http.server 8765` (run_in_background) — `file://` is
   blocked in Playwright.
3. Playwright: `browser_navigate` → `browser_resize` (w≈1620) →
   `browser_take_screenshot(fullPage, png, filename=...)`. The PNG lands in
   the Playwright output dir (e.g. `/mnt/c/Users/<user>/<filename>.png`) —
   `find` it, then Read it to QA the render before uploading.
4. Upload via the REST call above, then embed in storage:
   `<ac:image ac:width="1200"><ri:attachment ri:filename="x.png"/></ac:image>`
5. Keep the ASCII versions wrapped in an `expand` macro right under the
   images ("Bản text (ASCII) — copy/diff được") as the greppable fallback.
6. Verify with `body.view`: count `<img` and check the expand rendered.

**Fallback không cần browser (concept/flow diagram, không phải dataflow git):**
khi máy không có `dot`/`mmdc` và hình chỉ là sơ đồ khối/luồng (login → refresh →
logout, lane so sánh…), vẽ thẳng bằng **PIL** (`python3` + Pillow, font
DejaVuSans hỗ trợ tiếng Việt) rồi upload qua REST như trên. Nhanh, tất định,
Read lại PNG để QA trước khi embed. Dùng cho report/security page; dataflow
theo-hàm của MR vẫn nên đi đường graphviz ở trên.

ASCII-only (no PNG) is still fine for small/quick pages.

## Git diff extraction recipe

```bash
BASE=$(git.exe merge-base master <branch>)
git.exe log --oneline ${BASE}..<branch>            # the MR commits
git.exe show <commit> -- <path> | sed -n '/^@@/,$p' # hunks of one file/commit
git.exe diff ${BASE}..<branch> -- <path>           # net change of one file
```
Trim each hunk to the few lines that tell the story; add `# comment` callouts.
For pure additions (new method) show it as a `python` block, not a diff.

## Confluence storage-format gotchas (these bit me — encode them)

- **NEVER wrap the whole page body in `<![CDATA[ ... ]]>`.** It escapes all
  markup → the page renders as literal `<ac:...>` text. Pass clean storage XHTML.
- **`<![CDATA[ ]]>` IS correct *inside* a code macro body** — only there.
- **Escape raw `&` as `&amp;`** in prose/headings/list items, or you get
  `Error parsing xhtml: Unexpected character ' ' (missing name?)`. (Diacritics
  inside CDATA are fine; `&` outside CDATA is not.)
- **Title field is plain text** — pass a literal `&` or use `+`. Passing `&amp;`
  shows the literal "&amp;" in the title. Prefer `+`/`va` to dodge it entirely.
- **Cross-page links:** prefer a plain `<a href="$WIKI_URL/pages/viewpage.action?pageId=ID">…</a>`
  over `<ac:link><ri:page .../></ac:link>` (the latter is finicky).
- Code macro shape:
  `<ac:structured-macro ac:name="code"><ac:parameter ac:name="language">diff</ac:parameter><ac:parameter ac:name="title">…</ac:parameter><ac:plain-text-body><![CDATA[ … ]]></ac:plain-text-body></ac:structured-macro>`
- **`language` phải là brush Confluence hỗ trợ.** Giá trị lạ (`jsx`, `tsx`,
  `vue`, `js`, …) → `Error rendering macro 'code': Invalid value specified for
  parameter`. Dùng: `javascript` (cho cả JS/JSX/TS), `python`, `bash`, `sql`,
  `xml`/`html`, `yaml`, `diff`, `text`. Khi nghi ngờ → `text`.
- Useful macros: `status` (colour + title) for metrics, `info`/`note`/`warning`/`tip`
  for callouts, `panel` (`bgColor` `#e3fcef`) for the "what we gained" box,
  `<hr/>` between major parts.
- Optional but tidy: strip Vietnamese diacritics *inside code blocks* for clean
  monospace alignment; keep full diacritics in the prose.

## Publish

```
confluence_create_page(space_key="BSS", parent_id="$REVIEW_PARENT_PAGE",
    title="BDR-XXXX · <topic>", content=<storage>, content_format="storage",
    emoji="🧩")
# or confluence_update_page(page_id=..., title=..., content=..., content_format="storage",
#     version_comment="...")
```

## Verify (mandatory)

After publishing, fetch the raw storage and confirm it rendered, don't trust the
create call's 200:

```
confluence_get_page(page_id=..., convert_to_markdown=false, include_metadata=true)
```
Check: (a) every `<ac:structured-macro ac:name="code"...>` now has an
`ac:macro-id` (= server parsed it, not escaped text); (b) the `title` has no
literal `&amp;`; (c) no stray `<![CDATA[` wrapping the whole body; (d) fetch the
**rendered** view and assert **zero** macro errors — this is what catches a bad
code `language` or a broken image embed that the storage view hides:
```bash
curl -s -u "$USER:$TOKEN" "$URL/rest/api/content/$PAGE?expand=body.view" \
 | grep -c "Error rendering macro"   # must be 0; also count <img == #diagrams
``` If the
markdown view (`convert_to_markdown=true`) mangles code blocks but the *storage*
shows real macros with macro-ids, it renders fine in the browser — that's just
the markdown exporter being weak; trust the storage.

## Is this "enough"?

Yes for a single MR. The recurring failure modes are storage escaping and the
no-attachment limitation — both are covered above. Don't over-template: a short
fix gets a short page. The one thing never to cut is the **real git-diff section**.
