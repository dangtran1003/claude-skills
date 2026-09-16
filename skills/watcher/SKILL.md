---
name: watcher
description: Check bug và lấy báo cáo lỗi từ Sentry $WATCHER_URL (self-hosted, org "sentry", 100 project). Dùng khi user hỏi về lỗi/exception/crash trên portal hay service bất kỳ, muốn xem stacktrace của một issue, so sánh lỗi tuần này vs tuần trước, hoặc xin báo cáo error. Trigger - /watcher, "check bug trên watcher", "sentry có lỗi gì", "báo cáo lỗi api-production", "issue API-PRODUCTION-XXX là gì".
allowed-tools: Bash(python3 *), Bash(curl *), Read, Write
---

# Watcher — Sentry FCI

Đọc lỗi từ `$WATCHER_URL` (Sentry self-hosted, org slug `sentry`).

**Token là READ-ONLY** (scope `event:read`, `project:read`, `org:read`; PUT trả 403). Không resolve/ignore/assign issue được qua API — nếu user muốn đổi trạng thái issue, đưa link `permalink` để họ tự bấm trên UI.

## Công cụ

Mọi thứ đi qua 1 script, stdlib Python, không cần cài gì:

```bash
W=~/.claude/skills/watcher/scripts/watcher.py
python3 $W --help
```

Config (URL/org/token) nằm ở `~/.claude/skills/watcher/.env` (chmod 600). **Không in token ra output, không paste token vào file khác, không commit.**

## Tham số chung

- `target`: slug project (`api-production`), nhiều slug (`api-stg,api-dev`), cả team (`team:bss`), hoặc `all`. Mặc định `all`.
- `-p/--period`: `24h`, `7d`, `14d`, `30d`, tối đa `90d`. Mặc định `24h`.
- `--json`: xuất JSON thô để tự xử lý tiếp.

## Lệnh

| Lệnh | Dùng khi |
|---|---|
| `projects [--team X] [--grep X]` | tìm slug project (cache 24h, `--refresh` để nạp lại) |
| `issues <target> -p 24h -q <query> -s freq -n 25` | list issue theo bộ lọc |
| `new <target> -p 24h` | issue mới xuất hiện trong kỳ |
| `search "<text>" <target> -p 7d` | tìm issue theo chuỗi trong tiêu đề |
| `issue <ID|SHORT-ID>` | chi tiết 1 issue: tag breakdown + stacktrace + breadcrumbs |
| `trend <target> -p 24h -i 1h` | biểu đồ số error theo giờ |
| `top <target> -p 24h` | xếp hạng project theo error events + delta vs kỳ trước |
| `report <target> -p 7d [-o file.md]` | báo cáo markdown đầy đủ |

## Query syntax (đã verify trên instance này)

Hợp lệ: `is:unresolved`, `is:new`, `is:regressed`, `is:escalating`, `is:ignored`, `is:assigned`,
`level:fatal|error|warning`, `error.unhandled:true`, `timesSeen:>1000`, `firstSeen:-24h`,
`lastSeen:-1h`, `environment:production`, `transaction:"/api/v1/..."`, `release:X`, và chuỗi tự do trong ngoặc kép.

**`is:unhandled` KHÔNG hợp lệ** ở version này → trả HTTP 400. Dùng `error.unhandled:true`.

`sort`: `freq` (nhiều event nhất), `new` (mới nhất), `date` (vừa xảy ra), `user`, `trends`.

## Quy trình chuẩn

### Hỏi "có bug gì mới / hôm nay thế nào"
1. `top <target> -p 24h` — xem project nào bùng lỗi.
2. `new <target> -p 24h` — issue mới.
3. `issues <target> -q "is:unresolved is:escalating" -p 7d` — issue đang leo thang.
4. Tóm tắt: cái nào đáng lo (mới + tăng mạnh + có user bị ảnh hưởng), cái nào là noise cũ.

### Hỏi về một issue cụ thể
`issue <SHORT-ID>` → đọc exception, frame in-app cuối cùng, tag `server_name`/`transaction`
→ map sang code repo tương ứng rồi mới kết luận.

### Xin báo cáo
`report <target> -p 7d -o /tmp/watcher-<target>-<date>.md`, đọc lại file rồi trình bày phần quan trọng.

## Bối cảnh project (đã verify)

- Team `bss` (portal BSS của user): `api-production`, `api-production-jp`, `api-stg`, `api-dev`, `api-pilot`, `cmp-be`, `cmp-ui`, `react-ui-dev`, `ui-console-prod`, `ui-console-prod-jp`.
- Team `iaas`: `infra-dev`, `migration-dev`.
- Cẩn thận nhánh ↔ môi trường: `api-stg` map với nhánh nào phải check lại, xem [[portal-api-branch-env-mapping]].

## Đọc số cho đúng

- Cột `Delta` trong report: `NEW` = issue mới trong kỳ; `?` = issue cũ nhưng không lọt top-100 kỳ trước nên **không so sánh được** — đừng đọc thành "tăng vô hạn".
- `report` chỉ so top-N issue, không phải toàn bộ; số issue mới hiện `100+` nghĩa là bị chặn ở trang đầu.
- Event count cao ≠ nghiêm trọng. Nhiều issue top là log noise lặp trong cron (vd `WHITELIST IP`). Đối chiếu `users` > 0 và `error.unhandled:true` trước khi gọi là bug.
- **Không kết luận root cause chỉ từ tiêu đề Sentry.** Mở stacktrace, xác nhận bằng code hoặc trace SigNoz (`/signoz-trace`) rồi mới chốt.

## Xem thêm

- `references/api.md` — endpoint thô nếu cần query ngoài phạm vi script.
