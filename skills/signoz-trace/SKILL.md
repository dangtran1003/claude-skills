---
name: signoz-trace
description: Analyze a SigNoz trace by trace ID (full or partial). Queries spans, finds errors, and generates a detailed bug report. Usage - /signoz-trace <trace_id>
allowed-tools: Bash(curl *), Bash(date *), Bash(python3 *), Read, Write
---

# SigNoz Trace Analyzer

Analyze a trace from SigNoz and produce a detailed bug/performance report.

## Connection Info

Credentials live in `.env` next to this file (copy from `.env.example`, never commit it).
Load them before the first curl:

```bash
set -a; . "$(dirname "$0")/.env" 2>/dev/null || . ~/.claude/skills/signoz-trace/.env; set +a
```

- **SigNoz URL**: `$SIGNOZ_URL` (prod default `$SIGNOZ_URL`)
- **API Key**: `$SIGNOZ_API_KEY`
- **API Endpoint**: `POST /api/v3/query_range`
- **Headers**: `SIGNOZ-API-KEY: $SIGNOZ_API_KEY` and `Content-Type: application/json`

## Input

The user provides a trace ID — either full 32-char hex or a partial substring (e.g. `b9eea20e`).

## Steps

### Step 1: Resolve full trace ID

If the input is shorter than 32 characters, it's a partial trace ID. Search for it using the `contains` operator on `traceID`.

Use this query template to find matching traces (dataSource: `traces`, panelType: `list`):

```bash
END_NS=$(date +%s)000000000
START_NS=$(date -d '7 days ago' +%s)000000000

curl -s -k "$SIGNOZ_URL/api/v3/query_range" \
  -H "SIGNOZ-API-KEY: $SIGNOZ_API_KEY" \
  -H "Content-Type: application/json" \
  -X POST \
  -d "{
    \"compositeQuery\": {
      \"builderQueries\": {
        \"A\": {
          \"dataSource\": \"traces\",
          \"queryName\": \"A\",
          \"expression\": \"A\",
          \"filters\": {
            \"items\": [
              {
                \"key\": {\"key\": \"traceID\", \"dataType\": \"string\", \"type\": \"tag\", \"isColumn\": true},
                \"op\": \"contains\",
                \"value\": \"<PARTIAL_TRACE_ID>\"
              }
            ],
            \"op\": \"AND\"
          },
          \"selectColumns\": [
            {\"key\": \"traceID\", \"dataType\": \"string\", \"type\": \"tag\", \"isColumn\": true},
            {\"key\": \"serviceName\", \"dataType\": \"string\", \"type\": \"tag\", \"isColumn\": true}
          ],
          \"aggregateOperator\": \"noop\",
          \"limit\": 5,
          \"offset\": 0,
          \"orderBy\": [{\"columnName\": \"timestamp\", \"order\": \"desc\"}]
        }
      },
      \"queryType\": \"builder\",
      \"panelType\": \"list\"
    },
    \"start\": $START_NS,
    \"end\": $END_NS
  }"
```

Extract the full `traceID` from the result. If multiple distinct trace IDs match, show them and ask the user which one.

### Step 2: Get all spans with full details

Query all spans for the resolved trace ID using `op: "="` on `traceID`:

```bash
curl -s -k "$SIGNOZ_URL/api/v3/query_range" \
  -H "SIGNOZ-API-KEY: $SIGNOZ_API_KEY" \
  -H "Content-Type: application/json" \
  -X POST \
  -d "{
    \"compositeQuery\": {
      \"builderQueries\": {
        \"A\": {
          \"dataSource\": \"traces\",
          \"queryName\": \"A\",
          \"expression\": \"A\",
          \"filters\": {
            \"items\": [
              {
                \"key\": {\"key\": \"traceID\", \"dataType\": \"string\", \"type\": \"tag\", \"isColumn\": true},
                \"op\": \"=\",
                \"value\": \"<FULL_TRACE_ID>\"
              }
            ],
            \"op\": \"AND\"
          },
          \"selectColumns\": [
            {\"key\": \"serviceName\", \"dataType\": \"string\", \"type\": \"tag\", \"isColumn\": true},
            {\"key\": \"name\", \"dataType\": \"string\", \"type\": \"tag\", \"isColumn\": true},
            {\"key\": \"durationNano\", \"dataType\": \"float64\", \"type\": \"tag\", \"isColumn\": true},
            {\"key\": \"httpMethod\", \"dataType\": \"string\", \"type\": \"tag\", \"isColumn\": true},
            {\"key\": \"responseStatusCode\", \"dataType\": \"string\", \"type\": \"tag\", \"isColumn\": true},
            {\"key\": \"traceID\", \"dataType\": \"string\", \"type\": \"tag\", \"isColumn\": true},
            {\"key\": \"spanID\", \"dataType\": \"string\", \"type\": \"tag\", \"isColumn\": true},
            {\"key\": \"parentSpanID\", \"dataType\": \"string\", \"type\": \"tag\", \"isColumn\": true},
            {\"key\": \"statusCode\", \"dataType\": \"float64\", \"type\": \"tag\", \"isColumn\": true},
            {\"key\": \"statusMessage\", \"dataType\": \"string\", \"type\": \"tag\", \"isColumn\": true},
            {\"key\": \"httpUrl\", \"dataType\": \"string\", \"type\": \"tag\", \"isColumn\": true},
            {\"key\": \"httpRoute\", \"dataType\": \"string\", \"type\": \"tag\", \"isColumn\": true},
            {\"key\": \"httpHost\", \"dataType\": \"string\", \"type\": \"tag\", \"isColumn\": true},
            {\"key\": \"hasError\", \"dataType\": \"bool\", \"type\": \"tag\", \"isColumn\": true}
          ],
          \"aggregateOperator\": \"noop\",
          \"limit\": 100,
          \"offset\": 0,
          \"orderBy\": [{\"columnName\": \"timestamp\", \"order\": \"asc\"}]
        }
      },
      \"queryType\": \"builder\",
      \"panelType\": \"list\"
    },
    \"start\": $START_NS,
    \"end\": $END_NS
  }"
```

### Step 3: Get correlated logs

Query logs correlated to this trace:

```bash
curl -s -k "$SIGNOZ_URL/api/v3/query_range" \
  -H "SIGNOZ-API-KEY: $SIGNOZ_API_KEY" \
  -H "Content-Type: application/json" \
  -X POST \
  -d "{
    \"compositeQuery\": {
      \"builderQueries\": {
        \"A\": {
          \"dataSource\": \"logs\",
          \"queryName\": \"A\",
          \"expression\": \"A\",
          \"filters\": {
            \"items\": [
              {
                \"key\": {\"key\": \"trace_id\", \"dataType\": \"string\", \"type\": \"tag\", \"isColumn\": false},
                \"op\": \"=\",
                \"value\": \"<FULL_TRACE_ID>\"
              }
            ],
            \"op\": \"AND\"
          },
          \"selectColumns\": [
            {\"key\": \"body\", \"dataType\": \"string\", \"type\": \"tag\", \"isColumn\": true},
            {\"key\": \"severity_text\", \"dataType\": \"string\", \"type\": \"tag\", \"isColumn\": true}
          ],
          \"aggregateOperator\": \"noop\",
          \"limit\": 50,
          \"offset\": 0,
          \"orderBy\": [{\"columnName\": \"timestamp\", \"order\": \"asc\"}]
        }
      },
      \"queryType\": \"builder\",
      \"panelType\": \"list\"
    },
    \"start\": $START_NS,
    \"end\": $END_NS
  }"
```

### Step 4: Analyze and report

From the collected data, build a report with:

#### Header
- **Trace ID** (full)
- **Time** (from first span timestamp)
- **Total Duration** (from root span's durationNano, convert to human readable: ms or seconds)
- **Service(s)** involved
- **Root endpoint** (httpMethod + httpRoute or name of root span where parentSpanID is empty)
- **Status**: OK or ERROR (from root span hasError + responseStatusCode)

#### Span Tree
Build and display a simplified span tree showing parent-child relationships. Highlight:
- Error spans (hasError=true) with responseStatusCode
- Slow spans (> 1 second)
- The root span

#### Issues Found
Create a numbered table of issues detected:

| # | Issue | Severity | Detail |
|---|-------|----------|--------|

Look for these patterns:
1. **HTTP 4xx/5xx responses** — especially on root or internal spans
2. **hasError=true spans** — with statusMessage if available
3. **Slow spans** — durationNano > 1s, especially if sequential
4. **N+1 query patterns** — many similar DB queries in logs
5. **Duplicate calls** — same URL called multiple times
6. **Missing filters** — API calls without query parameters that should have them
7. **Sequential batching** — many similar calls done one-by-one instead of parallel
8. **Large payloads** — extremely long URLs with many query params (pagination issues)
9. **Redundant auth** — multiple auth token requests in one trace

#### Correlated Logs Summary
Summarize interesting log entries — especially errors, warnings, SQL queries, and exception messages.

#### Recommendations
Actionable suggestions to fix the identified issues.

## Output Format

Output the report directly as markdown in the conversation. Be concise but thorough. Use tables for structured data. Convert nanoseconds to human-readable durations (ms/s).

## Notes
- Time range defaults to last 7 days. If no results, try 30 days.
- If the trace has too many spans (>100), paginate with offset.
- Always pipe curl output through `python3 -m json.tool` for readability when debugging.
- durationNano is in nanoseconds: divide by 1,000,000 for ms, by 1,000,000,000 for seconds.
