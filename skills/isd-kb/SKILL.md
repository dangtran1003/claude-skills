---
name: isd-kb
description: Từ 1 ticket ISD ($ISD_URL) viết trang KB trên $WIKI_URL, gắn link KB vào ticket rồi đẩy ticket qua Resolve → KB Update → W/A for KB → W/A FOR CLOSE. Dùng khi user nói "tạo KB cho ticket ISD-xxxxx", "viết KB rồi đóng ticket", "gắn KB vào task", "kéo ticket sang W/A for close". Trigger - /isd-kb, "tạo trang kb cho ISD-xxxxx".
allowed-tools: Bash(python3 *), Read, Write, Edit
---

# ISD → KB → W/A FOR CLOSE

Một lệnh cho cả luồng: đọc ticket → viết KB → gắn KB vào ticket → chuyển trạng thái.

```bash
K=~/.claude/skills/isd-kb/scripts/isd_kb.py
python3 $K --help
```

Config (token ISD + creds wiki + space/parent/group mặc định) ở `~/.claude/skills/isd-kb/.env` (chmod 600). **Không in token ra output.**

## Lệnh

| Lệnh | Dùng khi |
|---|---|
| `info ISD-99558 --download /tmp/isd-99558` | đọc description + comment + tải ảnh đính kèm |
| `next-id [--date YYYYMMDD]` | lấy số KB kế tiếp trong ngày (quét title trong space ISD) |
| `create --title "..." --body file.xhtml [--attach a.png,b.png]` | tạo page KB + upload ảnh |
| `close ISD-99558 --kb <url\|pageId>` | gắn KB + chạy hết chuỗi transition (`--dry-run` để xem trước) |
| `status ISD-99558` | trạng thái hiện tại + transition khả dụng |
| `delete-page <id>` | xoá page (chỉ để dọn page test) |

## Quy trình chuẩn

1. `info <TICKET> --download /tmp/<ticket>` — đọc ticket, xem ảnh bằng tool Read để nắm đúng triệu chứng. Chat Zalo/Teams trong ảnh thường là chỗ duy nhất ghi cách xử lý thật và câu xác nhận của khách.
2. `next-id` — lấy ID `KB<YYYYMMDD>-NNN`.
3. Soạn body theo `reference/kb-template.xhtml`, ghi ra file `.xhtml`.
4. `create --title "[KB...] ..." --body ... --attach ...` — trả về pageId + URL.
5. Đưa link cho user xem trước, rồi `close <TICKET> --kb <url>`.

## Nội dung KB — nguyên tắc

- Bám khung của KB mẫu space ISD: **KB Revise → KB Title → Environment/Scope → Symptoms → Nguyên nhân → Resolution Steps → Kết quả → Lưu ý → Tags**.
- Chỉ viết cái **verify được từ ticket** (mô tả, comment, ảnh chat). Không suy diễn URL/nút bấm/nguyên nhân — chỗ nào chưa chắc thì viết chung chung và nói rõ với user là chưa verify.
- Environment/Scope nêu: môi trường, đối tượng (L1/L2/End-user), loại sự cố, link ticket, khách hàng/VPC/region.
- Resolution Steps là **các bước L1 làm lại được**, kèm workaround nếu chưa fix gốc.
- Kết quả: trích đúng câu xác nhận của khách + thời điểm + kênh.
- Ô "Kiểm duyệt / Xuất bản" trong bảng KB Revise để trống — người duyệt điền.
- Đính kèm ảnh triệu chứng + ảnh khách xác nhận lấy thẳng từ ticket, đổi tên `<TICKET>-<mô-tả>.png`.

## Bẫy storage format (Confluence Server)

- Body là **XHTML nghiêm ngặt**; script tự validate trước khi PUT, sai là fail sớm chứ không tạo page hỏng.
- Placeholder kiểu `<trạng thái>` bị coi là tag → escape `&lt;` `&gt;`.
- Nhúng ảnh: `<ac:image ac:width="700"><ri:attachment ri:filename="tên-file.png"/></ac:image>` — tên file phải khớp file `--attach` (upload sau khi tạo page vẫn render đúng).
- `confluence_update_page` của MCP **hỏng** trên $WIKI_URL; sửa page đã tạo thì dùng REST PUT (xem memory `confluence-update-via-rest`). Tạo page mới thì OK.

## Luồng trạng thái (issuetype SR Cloud Support) — đã verify 10/09/2026

```
Customer Checking --[521 Customer Approval]--> Resolved Approval
  --[271 Resolve, bắt buộc resolution]--> KB Update
  --[541 Request to Close, bắt buộc Assignment Group; set luôn KB + KB Approvers]--> W/A for KB
  --[duyệt KB]--> W/A FOR CLOSE --> Closed
```

Field: `customfield_14302` KB (URL) · `customfield_14303` Assignment Group (select, mặc định BSS) · `customfield_14318` KB Approvers (multi user) · `customfield_14313` L3 Assignee.

**Mẹo tự đẩy tới W/A FOR CLOSE:** ở bước `Request to Close`, set **KB Approvers = chính mình** → ngay sau đó tài khoản mình có transition duyệt KB nên đi thẳng `W/A for KB → W/A FOR CLOSE` (automation CSO DEV vẫn nới KB Approvers ra full list sau đó). Nếu không phải approver, `close` sẽ dừng ở `W/A for KB` và báo cần người duyệt — đó là hành vi đúng, không cố lách.

`close` idempotent: đọc trạng thái hiện tại rồi chỉ chạy các bước còn thiếu; chạy lại trên ticket đã ở W/A FOR CLOSE thì chỉ in ra trạng thái.

`KB Update` mang statusCategory = **Done** dù ticket chưa đóng → JQL `statusCategory != Done` lọc mất nó (memory `isd-sr-cloud-support-flow-kb`).

## Ví dụ đã chạy thật

ISD-99558 (Edit Role UI v2 treo → hướng dẫn khách dùng UI v1): KB `<page-id>`, ticket đi Customer Checking → W/A FOR CLOSE, KB Approvers tự set → duyệt luôn.
