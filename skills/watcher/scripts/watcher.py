#!/usr/bin/env python3
"""CLI đọc Sentry self-hosted: list issue, xem stacktrace, ra báo cáo."""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(SKILL_DIR, ".cache")
PROJ_CACHE = os.path.join(CACHE_DIR, "projects.json")
PROJ_TTL = 24 * 3600


def load_env():
    path = os.path.join(SKILL_DIR, ".env")
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


load_env()
BASE = os.environ.get("WATCHER_URL", "").rstrip("/") + "/api/0"
ORG = os.environ.get("WATCHER_ORG", "sentry")
TOKEN = os.environ.get("WATCHER_TOKEN", "")


def api(path, params=None, timeout=90):
    url = BASE + path
    if params:
        flat = []
        for k, v in params.items():
            for item in (v if isinstance(v, list) else [v]):
                if item is not None:
                    flat.append((k, str(item)))
        url += "?" + urllib.parse.urlencode(flat)
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + TOKEN})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode()[:300]
            if e.code == 429 and attempt < 2:
                time.sleep(3 * (attempt + 1))
                continue
            raise SystemExit("HTTP %s %s\n%s" % (e.code, url, body))
        except Exception as e:
            if attempt < 2:
                time.sleep(2)
                continue
            raise SystemExit("ERR %s %s" % (type(e).__name__, e))


def projects(refresh=False):
    if not refresh and os.path.exists(PROJ_CACHE) and time.time() - os.path.getmtime(PROJ_CACHE) < PROJ_TTL:
        return json.load(open(PROJ_CACHE))
    data = api("/organizations/%s/projects/" % ORG)
    slim = [{"id": p["id"], "slug": p["slug"], "platform": p.get("platform"),
             "team": (p.get("team") or {}).get("slug")} for p in data]
    os.makedirs(CACHE_DIR, exist_ok=True)
    json.dump(slim, open(PROJ_CACHE, "w"))
    return slim


def resolve_target(target):
    """target -> (list project id, nhãn). Nhận 'all', 'team:x', hoặc slug phân tách bằng dấu phẩy."""
    if not target or target == "all":
        return ["-1"], "all projects"
    ps = projects()
    if target.startswith("team:"):
        team = target[5:]
        sel = [p for p in ps if p["team"] == team]
        if not sel:
            raise SystemExit("Không có project nào thuộc team '%s'" % team)
        return [p["id"] for p in sel], "team:%s (%d project)" % (team, len(sel))
    by_slug = {p["slug"]: p for p in ps}
    ids, names = [], []
    for slug in target.split(","):
        slug = slug.strip()
        if slug not in by_slug:
            near = [s for s in by_slug if slug in s][:5]
            raise SystemExit("Không thấy project '%s'. Gần giống: %s" % (slug, ", ".join(near) or "(không có)"))
        ids.append(by_slug[slug]["id"])
        names.append(slug)
    return ids, ",".join(names)


def window(period):
    """statsPeriod -> (start, end) cửa sổ liền trước, dùng cho so sánh delta."""
    unit, n = period[-1], int(period[:-1])
    delta = timedelta(hours=n) if unit == "h" else timedelta(days=n)
    end = datetime.now(timezone.utc).replace(microsecond=0)
    return (end - 2 * delta).strftime("%Y-%m-%dT%H:%M:%S"), (end - delta).strftime("%Y-%m-%dT%H:%M:%S")


def fetch_issues(pids, period=None, query="is:unresolved", sort="freq", limit=25, start=None, end=None):
    params = {"project": pids, "query": query, "sort": sort, "limit": min(limit, 100)}
    if start and end:
        params["start"], params["end"] = start, end
    else:
        params["statsPeriod"] = period
    return api("/organizations/%s/issues/" % ORG, params)


def ago(iso):
    if not iso:
        return "-"
    t = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    s = (datetime.now(timezone.utc) - t).total_seconds()
    for div, u in ((86400, "d"), (3600, "h"), (60, "m")):
        if s >= div:
            return "%d%s" % (s // div, u)
    return "%ds" % s


def fmt(n):
    for div, u in ((1e6, "M"), (1e3, "k")):
        if n >= div:
            return "%.1f%s" % (n / div, u)
    return str(int(n))


def issue_rows(issues, delta_map=None, new_ids=None):
    rows = []
    for i in issues:
        row = {"shortId": i["shortId"], "project": i["project"]["slug"], "level": i["level"],
               "count": int(i["count"]), "users": i["userCount"], "lastSeen": ago(i["lastSeen"]),
               "firstSeen": ago(i["firstSeen"]), "unhandled": i.get("isUnhandled"),
               "title": " ".join(i["title"].split())[:110], "culprit": (i.get("culprit") or "")[:70],
               "id": i["id"], "url": i["permalink"]}
        if delta_map is not None:
            prev = delta_map.get(i["id"], 0)
            row["prev"] = prev
            if prev:
                row["delta"] = "%+d%%" % round((row["count"] - prev) * 100.0 / prev)
            else:
                row["delta"] = "NEW" if row["id"] in (new_ids or ()) else "?"
        rows.append(row)
    return rows


def print_table(rows, cols):
    if not rows:
        print("(không có kết quả)")
        return
    widths = {c: max(len(c), max(len(str(r.get(c, ""))) for r in rows)) for c in cols}
    print(" | ".join(c.ljust(widths[c]) for c in cols))
    print("-+-".join("-" * widths[c] for c in cols))
    for r in rows:
        print(" | ".join(str(r.get(c, "")).ljust(widths[c]) for c in cols))


# ---------- commands ----------

def cmd_projects(a):
    ps = projects(refresh=a.refresh)
    if a.team:
        ps = [p for p in ps if p["team"] == a.team]
    if a.grep:
        ps = [p for p in ps if a.grep.lower() in p["slug"].lower()]
    if a.json:
        print(json.dumps(ps, indent=2))
        return
    print_table(sorted(ps, key=lambda p: (p["team"] or "", p["slug"])), ["slug", "team", "platform", "id"])
    print("\n%d project" % len(ps))


def cmd_issues(a):
    pids, label = resolve_target(a.target)
    issues = fetch_issues(pids, a.period, a.query, a.sort, a.limit)
    if a.json:
        print(json.dumps(issues, indent=2))
        return
    print("# %s | %s | query: %s | sort: %s\n" % (label, a.period, a.query, a.sort))
    print_table(issue_rows(issues), ["shortId", "project", "level", "count", "users", "lastSeen", "title"])
    print("\n%d issue" % len(issues))


def cmd_new(a):
    a.query = "is:unresolved firstSeen:-%s" % a.period
    a.sort = "new"
    cmd_issues(a)


def cmd_search(a):
    a.query = '%s "%s"' % (a.filter, a.text) if a.filter else '"%s"' % a.text
    cmd_issues(a)


def _entry(event, etype):
    for e in event.get("entries", []):
        if e["type"] == etype:
            return e["data"]
    return None


def cmd_issue(a):
    ident = a.ident
    if not ident.isdigit():
        ident = api("/organizations/%s/shortids/%s/" % (ORG, ident.upper()))["groupId"]
    detail = api("/issues/%s/" % ident)
    event = api("/issues/%s/events/latest/" % ident)
    tags = api("/issues/%s/tags/" % ident)
    if a.json:
        print(json.dumps({"issue": detail, "latestEvent": event, "tags": tags}, indent=2))
        return

    print("=" * 100)
    print("%s  [%s]  %s" % (detail["shortId"], detail["level"], " ".join(detail["title"].split())))
    print("=" * 100)
    print("project   : %s" % detail["project"]["slug"])
    print("status    : %s / %s | unhandled=%s | priority=%s" % (
        detail["status"], detail.get("substatus"), detail.get("isUnhandled"), detail.get("priority")))
    print("events    : %s | users: %s" % (fmt(int(detail["count"])), detail["userCount"]))
    print("first/last: %s ago  ->  %s ago" % (ago(detail["firstSeen"]), ago(detail["lastSeen"])))
    print("culprit   : %s" % detail.get("culprit"))
    print("url       : %s" % detail["permalink"])

    print("\n--- TAG BREAKDOWN (top values) ---")
    for tag in tags[:12]:
        vals = ", ".join("%s(%s)" % (str(v["value"])[:45], fmt(v["count"])) for v in tag.get("topValues", [])[:3])
        print("  %-16s %s" % (tag["key"], vals))

    req = _entry(event, "request")
    if req:
        print("\n--- REQUEST ---")
        print("  %s %s" % (req.get("method"), req.get("url")))
        if req.get("data"):
            print("  data: %s" % str(req["data"])[:400])

    exc = _entry(event, "exception")
    if exc:
        print("\n--- EXCEPTION (event %s) ---" % event["eventID"])
        for v in exc.get("values", [])[-2:]:
            print("  %s: %s" % (v.get("type"), " ".join(str(v.get("value") or "").split())[:400]))
            frames = (v.get("stacktrace") or {}).get("frames") or []
            app = [f for f in frames if f.get("inApp")] or frames
            for f in app[-a.frames:]:
                print("    %s:%s in %s" % (f.get("filename"), f.get("lineNo"), f.get("function")))
                if f.get("context"):
                    for ln, code in f["context"]:
                        if ln == f.get("lineNo"):
                            print("       > %s" % code.strip()[:150])

    crumbs = _entry(event, "breadcrumbs")
    if crumbs:
        print("\n--- BREADCRUMBS (last %d) ---" % a.crumbs)
        for c in crumbs.get("values", [])[-a.crumbs:]:
            msg = " ".join(str(c.get("message") or c.get("data") or "").split())
            print("  [%s] %-10s %s" % (c.get("level"), c.get("category"), msg[:160]))


def cmd_trend(a):
    pids, label = resolve_target(a.target)
    data = api("/organizations/%s/events-stats/" % ORG,
               {"project": pids, "statsPeriod": a.period, "interval": a.interval,
                "yAxis": "count()", "query": a.query, "dataset": "errors"})
    series = [(ts, pts[0]["count"] if pts else 0) for ts, pts in data["data"]]
    if a.json:
        print(json.dumps(series))
        return
    peak = max((c for _, c in series), default=1) or 1
    print("# trend %s | %s | interval %s\n" % (label, a.period, a.interval))
    for ts, c in series:
        t = datetime.fromtimestamp(ts, timezone.utc).astimezone().strftime("%m-%d %H:%M")
        print("%s  %7s %s" % (t, fmt(c), "#" * int(40.0 * c / peak)))
    print("\ntotal: %s" % fmt(sum(c for _, c in series)))


def by_project(pids, period=None, start=None, end=None, limit=15):
    params = {"project": pids, "dataset": "errors", "field": ["project", "count()"],
              "sort": "-count()", "per_page": limit, "query": "event.type:error"}
    if start and end:
        params["start"], params["end"] = start, end
    else:
        params["statsPeriod"] = period
    return api("/organizations/%s/events/" % ORG, params)["data"]


def cmd_top(a):
    pids, label = resolve_target(a.target)
    cur = by_project(pids, a.period, limit=a.limit)
    s, e = window(a.period)
    prev = {r["project"]: r["count()"] for r in by_project(pids, start=s, end=e, limit=100)}
    rows = []
    for r in cur:
        p, c = r["project"], r["count()"]
        pv = prev.get(p, 0)
        rows.append({"project": p, "events": fmt(c), "prev": fmt(pv),
                     "delta": "NEW" if pv == 0 else "%+d%%" % round((c - pv) * 100.0 / pv)})
    if a.json:
        print(json.dumps(rows, indent=2))
        return
    print("# error events theo project | %s | %s\n" % (label, a.period))
    print_table(rows, ["project", "events", "prev", "delta"])


def cmd_report(a):
    pids, label = resolve_target(a.target)
    s, e = window(a.period)
    out = []
    w = out.append
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    w("# Watcher report — %s" % label)
    w("")
    w("- Thời điểm: %s (local) | Cửa sổ: %s | So sánh với %s trước đó" % (now, a.period, a.period))
    w("- Nguồn: %s/organizations/%s/issues/" % (BASE.replace("/api/0", ""), ORG))
    w("")

    cur_proj = by_project(pids, a.period, limit=20)
    prev_proj = {r["project"]: r["count()"] for r in by_project(pids, start=s, end=e, limit=100)}
    tot_cur = sum(r["count()"] for r in cur_proj)
    tot_prev = sum(prev_proj.values())
    dpct = "n/a" if not tot_prev else "%+d%%" % round((tot_cur - tot_prev) * 100.0 / tot_prev)
    w("## 1. Tổng quan")
    w("")
    w("| Chỉ số | Kỳ này | Kỳ trước | Delta |")
    w("|---|---|---|---|")
    w("| Error events | %s | %s | %s |" % (fmt(tot_cur), fmt(tot_prev), dpct))
    w("")
    w("| Project | Kỳ này | Kỳ trước | Delta |")
    w("|---|---|---|---|")
    for r in cur_proj[:12]:
        pv = prev_proj.get(r["project"], 0)
        d = "NEW" if pv == 0 else "%+d%%" % round((r["count()"] - pv) * 100.0 / pv)
        w("| %s | %s | %s | %s |" % (r["project"], fmt(r["count()"]), fmt(pv), d))
    w("")

    top = fetch_issues(pids, a.period, "is:unresolved", "freq", a.limit)
    prev_top = fetch_issues(pids, None, "is:unresolved", "freq", 100, start=s, end=e)
    prev_counts = {i["id"]: int(i["count"]) for i in prev_top}
    w("## 2. Top issue theo số event")
    w("")
    w("| Issue | Project | Lvl | Events | Delta | Users | Last | Tiêu đề |")
    w("<!-- Delta: NEW = issue mới; ? = không lọt top-100 kỳ trước, không so được -->")
    w("|---|---|---|---|---|---|---|---|")
    new_ids = {i["id"] for i in fetch_issues(pids, a.period, "is:unresolved firstSeen:-%s" % a.period, "new", 100)}
    for r in issue_rows(top, prev_counts, new_ids):
        w("| [%s](%s) | %s | %s | %s | %s | %s | %s | %s |" % (
            r["shortId"], r["url"], r["project"], r["level"], fmt(r["count"]),
            r["delta"], r["users"], r["lastSeen"], r["title"].replace("|", "\\|")))
    w("")

    new = fetch_issues(pids, a.period, "is:unresolved firstSeen:-%s" % a.period, "new", 100)
    shown = new[:a.limit]
    w("## 3. Issue mới trong kỳ (%d%s)" % (len(new), "+" if len(new) == 100 else ""))
    w("")
    if len(new) > len(shown):
        w("_Hiển thị %d/%d mới nhất (tăng `-n` để xem thêm)._" % (len(shown), len(new)))
        w("")
    if not new:
        w("_Không có issue mới._")
    else:
        w("| Issue | Project | Lvl | Events | First | Tiêu đề |")
        w("|---|---|---|---|---|---|")
        for r in issue_rows(shown):
            w("| [%s](%s) | %s | %s | %s | %s | %s |" % (
                r["shortId"], r["url"], r["project"], r["level"], fmt(r["count"]),
                r["firstSeen"], r["title"].replace("|", "\\|")))
    w("")

    regressed = [r for r in issue_rows(top, prev_counts, new_ids)
                 if r["delta"] != "NEW" and r["prev"] and (r["count"] - r["prev"]) * 100.0 / r["prev"] >= 50]
    w("## 4. Cần chú ý")
    w("")
    unhandled = [r for r in issue_rows(top) if r["unhandled"]]
    fatal = [r for r in issue_rows(top) if r["level"] in ("fatal", "error") and r["users"] > 0]
    w("- Tăng >=50%% so với kỳ trước: %s" % (", ".join(r["shortId"] for r in regressed[:10]) or "không có"))
    w("- Unhandled: %s" % (", ".join(r["shortId"] for r in unhandled[:10]) or "không có"))
    w("- Có user bị ảnh hưởng: %s" % (", ".join("%s(%d)" % (r["shortId"], r["users"]) for r in fatal[:10]) or "không có"))
    w("")
    text = "\n".join(out)
    if a.out:
        open(a.out, "w").write(text)
        print("Đã ghi %s (%d dòng)" % (a.out, len(out)))
    else:
        print(text)


def main():
    p = argparse.ArgumentParser(prog="watcher", description="Đọc Sentry self-hosted")
    sub = p.add_subparsers(dest="cmd", required=True)

    def common(sp, target=True):
        if target:
            sp.add_argument("target", nargs="?", default="all",
                            help="slug project, 'a,b', 'team:bss', hoặc 'all'")
        sp.add_argument("-p", "--period", default="24h", help="24h / 7d / 14d / 30d (mặc định 24h)")
        sp.add_argument("--json", action="store_true")

    sp = sub.add_parser("projects", help="liệt kê project")
    sp.add_argument("--team")
    sp.add_argument("--grep")
    sp.add_argument("--refresh", action="store_true")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_projects)

    sp = sub.add_parser("issues", help="list issue")
    common(sp)
    sp.add_argument("-q", "--query", default="is:unresolved")
    sp.add_argument("-s", "--sort", default="freq", choices=["freq", "new", "date", "user", "trends"])
    sp.add_argument("-n", "--limit", type=int, default=25)
    sp.set_defaults(func=cmd_issues)

    sp = sub.add_parser("new", help="issue mới xuất hiện trong kỳ")
    common(sp)
    sp.add_argument("-n", "--limit", type=int, default=25)
    sp.set_defaults(func=cmd_new)

    sp = sub.add_parser("search", help="tìm issue theo text")
    sp.add_argument("text")
    common(sp)
    sp.add_argument("--filter", default="is:unresolved", help="phần query Sentry ghép thêm")
    sp.add_argument("-s", "--sort", default="freq")
    sp.add_argument("-n", "--limit", type=int, default=25)
    sp.set_defaults(func=cmd_search)

    sp = sub.add_parser("issue", help="chi tiết 1 issue + stacktrace event mới nhất")
    sp.add_argument("ident", help="numeric id hoặc SHORT-ID (vd API-PRODUCTION-1Z)")
    sp.add_argument("--frames", type=int, default=8)
    sp.add_argument("--crumbs", type=int, default=8)
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_issue)

    sp = sub.add_parser("trend", help="biểu đồ số error theo thời gian")
    common(sp)
    sp.add_argument("-i", "--interval", default="1h")
    sp.add_argument("-q", "--query", default="event.type:error")
    sp.set_defaults(func=cmd_trend)

    sp = sub.add_parser("top", help="xếp hạng project theo error events + delta")
    common(sp)
    sp.add_argument("-n", "--limit", type=int, default=15)
    sp.set_defaults(func=cmd_top)

    sp = sub.add_parser("report", help="báo cáo markdown đầy đủ")
    common(sp)
    sp.add_argument("-n", "--limit", type=int, default=15)
    sp.add_argument("-o", "--out", help="ghi ra file .md")
    sp.set_defaults(func=cmd_report)

    a = p.parse_args()
    if not TOKEN or not os.environ.get("WATCHER_URL"):
        raise SystemExit(
            "Thiếu WATCHER_URL/WATCHER_TOKEN — copy .env.example sang %s/.env rồi điền"
            % SKILL_DIR
        )
    a.func(a)


if __name__ == "__main__":
    main()
