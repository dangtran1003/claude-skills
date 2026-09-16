#!/usr/bin/env python3
"""Đọc Grafana qua service-account token. Chỉ GET, không ghi."""
import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request

ENV = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")


def cfg():
    out = {}
    with open(ENV) as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                out[k.strip()] = v.strip()
    return out


C = cfg()


def call(path, params=None, timeout=60):
    url = C["GRAFANA_URL"] + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + C["GRAFANA_TOKEN"]})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:400]
        sys.exit(f"HTTP {e.code} {path}\n{body}")


def ds_proxy(uid, sub, params=None, timeout=90):
    return call(f"/api/datasources/proxy/uid/{uid}/{sub.lstrip('/')}", params, timeout)


def cmd_datasources(a):
    for d in call("/api/datasources"):
        print(f"{d['type']:<11} {d['uid']:<40} {d['name']}{'  (default)' if d.get('isDefault') else ''}")


def cmd_dashboards(a):
    p = {"type": "dash-db", "limit": a.limit}
    if a.query:
        p["query"] = a.query
    rows = call("/api/search", p)
    print(f"{len(rows)} dashboard")
    for x in rows:
        print(f"  {x['uid']:<40} {x.get('folderTitle', '-'):<26} {x['title']}")


def cmd_panels(a):
    d = call(f"/api/dashboards/uid/{a.uid}")["dashboard"]
    print(f"# {d.get('title')}  (uid={a.uid})")
    for p in d.get("panels", []):
        if p.get("type") == "row":
            print(f"\n## {p.get('title')}")
            continue
        print(f"\n[{p.get('id')}] {p.get('title')}  ({p.get('type')})")
        for t in p.get("targets", []) or []:
            expr = t.get("expr") or t.get("query") or t.get("rawSql") or ""
            if expr:
                print("    " + " ".join(str(expr).split())[:400])


def cmd_promql(a):
    uid = a.uid or C["PROM_UID"]
    if a.range:
        end = int(time.time())
        start = end - a.range * 60
        r = ds_proxy(uid, "api/v1/query_range",
                     {"query": a.query, "start": start, "end": end, "step": a.step})
    else:
        r = ds_proxy(uid, "api/v1/query", {"query": a.query})
    if a.json:
        print(json.dumps(r, indent=1)[:20000])
        return
    res = r.get("data", {}).get("result", [])
    print(f"{len(res)} series")
    for s in res[:a.limit]:
        m = s.get("metric", {})
        label = ", ".join(f"{k}={v}" for k, v in m.items() if k != "__name__") or "(no labels)"
        if "value" in s:
            print(f"  {s['value'][1]:>18}  {label}")
        else:
            vals = s.get("values", [])
            last = vals[-1][1] if vals else "-"
            print(f"  last={last:>14}  n={len(vals):<5} {label}")


def cmd_labels(a):
    uid = a.uid or C["PROM_UID"]
    sub = f"api/v1/label/{a.label}/values" if a.label else "api/v1/labels"
    print("\n".join(ds_proxy(uid, sub).get("data", [])))


def cmd_logql(a):
    uid = a.uid or C["LOKI_UID"]
    end = int(time.time() * 1e9)
    start = end - a.minutes * 60 * int(1e9)
    r = ds_proxy(uid, "loki/api/v1/query_range",
                 {"query": a.query, "start": start, "end": end, "limit": a.limit,
                  "direction": "backward"})
    res = r.get("data", {}).get("result", [])
    if a.json:
        print(json.dumps(r)[:20000])
        return
    for s in res:
        lb = json.dumps(s.get("stream", {}), ensure_ascii=False)
        for ts, line in s.get("values", [])[:a.limit]:
            print(f"{lb[:110]}\n  {line[:400]}")


def cmd_alerts(a):
    gs = call("/api/prometheus/grafana/api/v1/rules")["data"]["groups"]
    n = 0
    for g in gs:
        for r in g["rules"]:
            if a.firing and r.get("state") != "firing":
                continue
            n += 1
            print(f"[{r.get('state'):<8}] {g.get('file')} / {r['name']}")
            for inst in (r.get("alerts") or [])[:5]:
                lb = {k: v for k, v in (inst.get("labels") or {}).items() if k != "alertname"}
                print(f"      {inst.get('state')}  {json.dumps(lb, ensure_ascii=False)[:200]}")
    print(f"\n{n} rule" + (" đang firing" if a.firing else ""))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("datasources").set_defaults(fn=cmd_datasources)

    p = sub.add_parser("dashboards")
    p.add_argument("query", nargs="?")
    p.add_argument("--limit", type=int, default=500)
    p.set_defaults(fn=cmd_dashboards)

    p = sub.add_parser("panels", help="dump panel + query của 1 dashboard")
    p.add_argument("uid")
    p.set_defaults(fn=cmd_panels)

    p = sub.add_parser("promql")
    p.add_argument("query")
    p.add_argument("--range", type=int, help="phút gần nhất (bỏ trống = instant query)")
    p.add_argument("--step", default="60s")
    p.add_argument("--uid")
    p.add_argument("--limit", type=int, default=30)
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_promql)

    p = sub.add_parser("labels", help="liệt kê label, hoặc giá trị của 1 label")
    p.add_argument("label", nargs="?")
    p.add_argument("--uid")
    p.set_defaults(fn=cmd_labels)

    p = sub.add_parser("logql")
    p.add_argument("query")
    p.add_argument("--minutes", type=int, default=30)
    p.add_argument("--limit", type=int, default=50)
    p.add_argument("--uid")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_logql)

    p = sub.add_parser("alerts")
    p.add_argument("--firing", action="store_true")
    p.set_defaults(fn=cmd_alerts)

    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
