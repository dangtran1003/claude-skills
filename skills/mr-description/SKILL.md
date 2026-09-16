---
name: mr-description
description: "Use when the user asks to write/update a GitLab MR description (\"update description MR\", \"sửa description giống MR !5849\", \"viết mô tả MR\"). Produces the standard FCI MR description: vì sao → sơ đồ → thay đổi theo mảng → API ảnh hưởng → dual-platform → bảng test → lưu ý review. Examples: \"update mr description giống mr này\", \"tạo description cho !NNNN\"."
---

# MR Description (GitLab — chuẩn FCI)

Viết description MR để reviewer nắm trọn WHY/WHAT/RISK không cần hỏi lại.
Chuẩn mẫu: MR !5849 và !5761 của `bss/portal-api-dev`.

## Mechanics ($GITLAB_URL)

- Token: `TOKEN=$(printf "protocol=https\nhost=$GITLAB_URL\n\n" | git.exe credential fill | sed -n 's/^password=//p')`
- Đọc/ghi MR: `GET|PUT /api/v4/projects/bss%2Fportal-api-dev/merge_requests/<iid>`
  với body JSON `{"title": ..., "description": ...}` (PUT qua python urllib, KHÔNG
  curl -d với heredoc lồng quote).
- **Ảnh trong description**: upload `POST /projects/:id/uploads` (`-F "file=@x.png"`)
  → response có sẵn `markdown` (`![name](/uploads/<hash>/x.png)`) — dán thẳng vào
  description. **Dùng chung đúng file PNG** đã render cho trang wiki review
  (nguồn DOT ở `~/fci/notes/bdr/reviews/*-dataflow.html`, pipeline render
  trong skill `mr-review-doc`).
- Sau PUT, check `detailed_merge_status`; nếu `not_open` → MR đã closed/merged,
  báo user (description vẫn lưu được trên MR closed).
- Title: conventional commit (`fix(scope): ...`), mô tả ĐỦ scope thật của MR —
  GitLab auto-lấy commit đầu làm title nên thường sai/thiếu khi MR gộp nhiều mảng.

## Template description (markdown)

```
## Jira / BDR
<ticket/BDR liên quan>. Trang review: [<tên trang>](<link wiki>).

## Vì sao (N bug/gap gốc)
1. **<tên gap>:** <triệu chứng → cơ chế → hậu quả>. (số đo nếu có)
2. ...

## Sơ đồ data-flow
![...](/uploads/...)        <- cùng PNG với trang wiki

## Thay đổi (N mảng)
### A. <mảng>
- <thay đổi> — <vì sao, 1 dòng>
### B. ...

## API / luồng bị ảnh hưởng
| Luồng | Entry | Thay đổi |
|---|---|---|

## Dual-platform (OSP vs VMW)   <- BẮT BUỘC nếu MR đụng infra/boundary
| Hàm | [OSP] | [VMW] |
|---|---|---|
(ghi rõ no-op/fallback CÓ CHỦ ĐÍCH)

## Test cases
**X mới · Y xoá · Z giữ** (đối chiếu master).
| File | Trạng thái (thêm file/sửa/xoá file) | Mới | Xoá | Giữ |
### Test MỚI — từng case kiểm tra gì
(per mảng, BẮT BUỘC bảng 2 cột — user dùng cột này để judge đủ case hay chưa)
| Test | Kiểm tra gì |
Mô tả lấy từ docstring/assert THẬT của test (đọc file, không đoán từ tên);
in đậm case quan trọng (happy-path, wiring, case chống over-reject/regression).
Kết bảng bằng đoạn **"Đánh giá độ phủ"**: ✅ các nhóm đã phủ (happy-path /
guard-no-op / wiring / cả 2 chiều pass-reject) + *nói thẳng gap còn lại* và vì
sao chấp nhận được (vd thiếu integration end-to-end, chỗ gọi 4 dòng chưa test).
### Test XOÁ (nếu có) — kèm LÝ DO (cơ chế cũ bị thay bằng gì)
### Phủ theo rủi ro
| Rủi ro | Test khoá |

## Lưu ý review
- <side-effect có chủ đích, harness thiếu, rủi ro còn lại — nói thẳng>
```

## Cách lấy số liệu test (đừng đếm tay)

```bash
BASE=$(git.exe merge-base origin/master <branch>)
git.exe diff --name-status $BASE..<branch>   # A/M/D file test
# per file: so sánh set `def test_\w+` giữa origin/master:<path> và <branch>:<path>
# → mới = branch−master, xoá = master−branch, giữ = giao
```
Lưu ý artifact "branch sau master": test bị "xoá" có thể do master mới thêm —
check commit xoá thuộc nhánh nào trước khi nhận là của MR (đã từng dính ở !5868).

## Quy tắc nội dung (rút từ feedback user)

- Mục "Vì sao" phải nêu **cơ chế** (gate nào bypass, đọc stale ở đâu), không chỉ triệu chứng.
- Bảng test: cái nào **mới/xoá/giữ** + xoá phải kèm lý do — user review bằng bảng này.
- "Phủ theo rủi ro" map rủi ro → test khoá nó (regression test cho root-cause phải nổi bật).
- Không ghi mã nội bộ kiểu `BDR-xxx`/`Fix #N` vào code; trong description thì ĐƯỢC (đây là tài liệu).
- Luôn link trang wiki review (tạo bằng skill `mr-review-doc` nếu chưa có) và để
  diff cho GitLab — description không dán diff.
