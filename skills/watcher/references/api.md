# Watcher Sentry API — endpoint thô

Base: `$WATCHER_URL/api/0` · Org: `sentry` · Header: `Authorization: Bearer $WATCHER_TOKEN`

Chỉ dùng file này khi `scripts/watcher.py` không phủ được nhu cầu.

```bash
set -a; . ~/.claude/skills/watcher/.env; set +a
B=$WATCHER_URL/api/0
curl -s -G -H "Authorization: Bearer $WATCHER_TOKEN" "$B/..." --data-urlencode "k=v"
```

## Đã verify hoạt động

| Endpoint | Ghi chú |
|---|---|
| `GET /organizations/` | org duy nhất: `sentry` |
| `GET /organizations/sentry/projects/` | 100 project, mỗi cái có `id`, `slug`, `team.slug` |
| `GET /organizations/sentry/issues/` | cross-project; **bắt buộc** `project=<id>` (lặp nhiều lần) hoặc `project=-1` |
| `GET /projects/sentry/<slug>/issues/` | 1 project, không cần param `project` |
| `GET /issues/<id>/` | detail; `tags[]` ở đây **không có `topValues`** |
| `GET /issues/<id>/tags/` | tag kèm `topValues` — dùng cái này để breakdown |
| `GET /issues/<id>/tags/<key>/values/` | phân bố đầy đủ 1 tag |
| `GET /issues/<id>/events/latest/` | event mới nhất: `entries[]` type `exception` / `breadcrumbs` / `request` |
| `GET /organizations/sentry/shortids/<SHORT-ID>/` | SHORT-ID → `groupId` |
| `GET /organizations/sentry/events/` | aggregate; `dataset=errors`, `field=project&field=count()`, `sort=-count()` |
| `GET /organizations/sentry/events-stats/` | time series; `yAxis=count()`, `interval=1h`, `dataset=errors` |
| `GET /projects/sentry/<slug>/stats/?stat=received&resolution=1h` | counter thô theo project |

## Bẫy

- `statsPeriod` và cặp `start`/`end` **loại trừ nhau**. `start`/`end` định dạng `YYYY-MM-DDTHH:MM:SS` (UTC).
- `statsPeriod` chấp nhận tới `90d`.
- Org-level issues thiếu `project` → 400. Script tự resolve slug → id.
- Token read-only: mọi `PUT`/`POST`/`DELETE` lên issue trả **403**.
- Rate limit trả 429 — script retry 3 lần có backoff.
- `entries[].data.values[].stacktrace.frames[]` xếp từ ngoài vào trong: frame **cuối** là nơi ném lỗi. Lọc `inApp=true` để bỏ frame thư viện.

## Ví dụ ngoài phạm vi script

Đếm event theo `transaction` trong 7 ngày:

```bash
curl -s -G -H "Authorization: Bearer $WATCHER_TOKEN" "$B/organizations/sentry/events/" \
  --data-urlencode "project=8" --data-urlencode "statsPeriod=7d" --data-urlencode "dataset=errors" \
  --data-urlencode "field=transaction" --data-urlencode "field=count()" \
  --data-urlencode "sort=-count()" --data-urlencode "query=event.type:error" --data-urlencode "per_page=20"
```

Danh sách release của 1 project:

```bash
curl -s -H "Authorization: Bearer $WATCHER_TOKEN" "$B/projects/sentry/api-production/releases/?per_page=10"
```
