---
name: signoz-weekly
description: Run weekly SignOz + code pattern scan for BSS portal IaaS modules. Compares with previous week, flags regressions, posts delta report to Confluence. Triggered by /signoz-weekly.
---

# SignOz Weekly Scan

## Mục đích

Scan SignOz prod + code base mỗi tuần để track:
- Endpoint performance regression (P90 tăng > 20%)
- Error rate increase (> 2% delta)
- New endpoints xuất hiện slow / error
- Anti-pattern code count (task.wait, silent except, raw exception)

## Scope

Modules trong scope user (Dang TH):
- IAM, Project, Tagging, Cloud Advisor
- Compute Engine (VM, Snapshot, Custom Image, Scaling)
- Network (VPC, VPN, Firewall, LB, FIP, IPSet, NIC, Security Group)

Out of scope: HPC, Bucket/S3, Backup, Database, Kubernetes, Billing, Freshdesk

## Tools available

- **Scan toolkit:** `~/fci/notes/signoz-scan/`
- **SignOz prod:** `$SIGNOZ_URL`
- **Confluence parent page:** `$BDR_PARENT_PAGE` (Bottleneck Issues — BDR-2026)

## Steps

### 1. Run scan scripts

```bash
cd ~/fci/notes/signoz-scan
./run_weekly_scan.sh
```

Output:
- `baselines/<DATE>.json` — Snapshot metrics
- `reports/weekly_<DATE>.md` — Delta report
- `reports/code_pattern_<DATE>.md` + `.json` — Code anti-patterns

### 2. Review delta report

Read the latest `reports/weekly_<DATE>.md`:

```bash
cat $(ls -t ~/fci/notes/signoz-scan/reports/weekly_*.md | head -1)
```

Highlight:
- 🔺 **Regressions** — endpoints worse than last week, list top 5
- 🆕 **New issues** — endpoints lần đầu xuất hiện slow/error
- 🟢 **Improvements** — endpoints fix work tốt

### 3. Diff code pattern counts (nếu có baseline cũ)

So sánh `code_pattern_<TODAY>.json` với baseline cũ nhất từ `reports/code_pattern_*.json`. Flag nếu:
- Số `task.wait()` instances tăng (regression — có code mới thêm pattern xấu)
- Số silent except tăng
- Số raw exception tăng

Mục tiêu: chỉ có giảm theo thời gian (sau fix BDR).

### 4. Báo cáo cho user

User cần xem nhanh:
- Bao nhiêu regression?
- Top 3 endpoint cần check
- Code pattern có thay đổi không?

Format compact (under 300 words):

```markdown
## Weekly Scan — YYYY-MM-DD

### 📊 SignOz Delta
- 🔺 Regression: X endpoints (top: ...)
- 🆕 New: Y endpoints
- 🟢 Improved: Z endpoints

### 🔧 Code Patterns
- task.wait(): A (vs prev B) [trend]
- silent except: C (vs prev D)
- raw exception: E (vs prev F)

### 🚨 Action needed
[1-3 items if any]
```

### 5. Post to Confluence (optional)

Nếu user muốn, post report lên Confluence với title `Weekly Scan <DATE>`, parent page `$BDR_PARENT_PAGE`.

Use `mcp__mcp-atlassian__confluence_create_page` với:
- `space_key`: BSS
- `title`: `Weekly Scan YYYY-MM-DD`
- `parent_id`: `$BDR_PARENT_PAGE`
- `content`: Markdown từ `reports/weekly_<DATE>.md`

### 6. Update BDR status (manual review)

For each BDR with major regression/improvement detected, suggest user update BDR status:
- 🔴 Open + worsening → escalate
- 🟢 Improved significantly → consider close

## Output format

Default: terse summary (300 words max) + offer to drill into specifics.

## Error handling

- Nếu scripts fail: check SignOz API reachable (`curl $SIGNOZ_URL`)
- Nếu trace queries return empty: verify time range, check API key

## Memory references

- `reference_signoz_fci.md` — SignOz endpoint + API key + instrumentation
- `user_modules_scope.md` — scope filter
- `reference_osp_vmw_architecture.md` — platform differences (nếu cần check fix theo platform)

## Frequency

Recommend: chạy mỗi **thứ Hai sáng** để có data tuần trước. Schedule có thể via cron:

```bash
# Crontab: every Monday 8 AM
0 8 * * 1 ~/fci/notes/signoz-scan/run_weekly_scan.sh
```

Hoặc user trigger manual qua `/signoz-weekly`.
