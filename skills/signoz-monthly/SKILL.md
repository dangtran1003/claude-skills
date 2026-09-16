---
name: signoz-monthly
description: Run monthly deep audit for BSS portal — full BDR refresh, update Confluence pages, identify new bottlenecks, close/update existing BDRs. Triggered by /signoz-monthly.
---

# SignOz Monthly Deep Audit

## Mục đích

Monthly comprehensive review — sâu hơn weekly scan:
- Full 30-day data analysis
- Update tất cả 27 BDRs với evidence mới
- Identify new issues chưa có BDR
- Close BDRs đã fix
- Re-validate platform-specific fixes (OSP vs VMW)
- Update parent page Bottleneck Issues

## Scope

Same as `/signoz-weekly` — IAM/Project/Tag/CloudAdvisor/Compute/Network.

## Tools available

- **Scan toolkit:** `~/fci/notes/signoz-scan/`
- **SignOz prod:** `$SIGNOZ_URL`
- **Confluence parent:** `$BDR_PARENT_PAGE` + 27 child BDRs
- **Backend code:** `~/fci/portal-api-dev/portal-api-svc-iaas-vmw/`
- **Worker code:** `~/fci/portal-api-dev/portal-celery/`
- **UI code:** `~/fci/portal-ui-user/`

## Steps

### 1. Run extended scan (30 days)

```bash
cd ~/fci/notes/signoz-scan
DAYS_BACK=30 python3 scripts/01_collect_metrics.py
python3 scripts/02_weekly_delta.py  # Vẫn compare với baseline cũ
python3 scripts/03_code_pattern_scan.py
```

### 2. List existing BDRs trên Confluence

Use `mcp__mcp-atlassian__confluence_get_page_children` với `parent_id=$BDR_PARENT_PAGE` để lấy danh sách 27 BDR child pages.

### 3. Cross-check BDR vs current evidence

For each BDR, check evidence still exists:

```python
# Example pseudocode
for bdr in bdrs:
    if bdr_has_endpoint_evidence(bdr):
        latest_metrics = query_signoz(bdr.endpoint, days=30)
        if latest_metrics.p90 < baseline.p90 * 0.5:
            mark_bdr_for_close(bdr, reason="P90 giảm 50%")
        elif latest_metrics.error_rate < baseline.error_rate * 0.3:
            mark_bdr_for_close(bdr, reason="Error rate giảm 70%")
```

Flag:
- 🟢 **Candidates for close** — Evidence cũ không còn hoặc giảm mạnh
- 🔴 **Still active** — Evidence vẫn xuất hiện ở mức tương đương
- ⚠️ **Worsening** — Evidence tệ hơn baseline

### 4. Identify new candidate issues

Scan top 20 endpoints theo:
- Highest P90 latency
- Highest error rate
- Highest total time burned

Cross-check với danh sách BDR hiện tại. Nếu có endpoint nào trong top mà KHÔNG nằm trong BDR nào → candidate cho BDR mới.

### 5. Update BDRs

For each BDR cần update:
- Refresh "Evidence" section với metrics mới
- Refresh "Sample traces" với trace IDs mới
- Update "Status" nếu candidate close
- Add new section "Update YYYY-MM" với so sánh

Use `mcp__mcp-atlassian__confluence_update_page` với:
- `page_id`: BDR page ID
- `version_comment`: "Monthly audit YYYY-MM — update evidence"

### 6. Generate monthly summary page

Create Confluence page:
- Title: `Monthly Audit YYYY-MM`
- Parent: `$BDR_PARENT_PAGE`
- Content:
  - Executive summary (BDRs closed, still open, worsening)
  - Top 5 trend (worst regression, best improvement)
  - New candidate issues (top 5)
  - Action items cho next month

### 7. Update parent page

Update `$BDR_PARENT_PAGE` (parent) với:
- Updated severity counts
- Latest action plan
- New trace evidence links
- Status of each BDR (Open/In Progress/Closed)

## Memory references

- `reference_signoz_fci.md`
- `user_modules_scope.md`
- `reference_osp_vmw_architecture.md`

## Output format

Báo cáo cho user (under 500 words):

```markdown
## Monthly Audit — YYYY-MM

### 📈 BDR Status Update
- 🟢 Closed/improved: X BDRs (list IDs)
- 🔴 Still active: Y BDRs
- ⚠️ Worsening: Z BDRs (escalate!)

### 🆕 New candidate issues
[Top 3 endpoints không có BDR nhưng cần BDR mới]

### 🔧 Code Pattern Trend
- task.wait(): A this month (vs B last month, Δ -10)
- silent except: C (Δ -5)
- raw exception: D (Δ -50, good!)

### 📋 Recommended action items for next month
[Top 5 actions]

### 🔗 Updated pages
- Parent: <link>
- New summary: <link>
- BDRs updated: X pages
```

## Frequency

Recommend: chạy **đầu mỗi tháng** (sau khi data 30 ngày trước đầy đủ).

## Notes

- Monthly audit thay đổi BDR content nên cần user **review trước khi push** (không auto-update Confluence trừ khi user confirm).
- Memory ghi nhớ baseline để compare cross-month.
- Có thể schedule via cron hoặc tự trigger qua `/signoz-monthly`.
