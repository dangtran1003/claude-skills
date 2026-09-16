#!/usr/bin/env python3
"""Tạo KB trên Confluence từ ticket ISD rồi gắn KB + đẩy ticket tới W/A FOR CLOSE."""
import argparse
import base64
import json
import mimetypes
import os
import re
import ssl
import sys
import urllib.parse
import urllib.request
import uuid
import xml.etree.ElementTree as ET

ENV = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

CF_GROUP = "customfield_14303"
CF_KB = "customfield_14302"
CF_APPROVERS = "customfield_14318"
CF_L3 = "customfield_14313"
FLOW = ["Customer Checking", "Resolved Approval", "KB Update", "W/A for KB", "W/A FOR CLOSE"]


def cfg():
    d = {}
    with open(ENV) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                d[k.strip()] = v.strip()
    return d


C = cfg()


def call(url, data=None, method=None, headers=None, raw=False):
    body = None
    if data is not None:
        body = data if isinstance(data, bytes) else json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, method=method or ("POST" if data else "GET"))
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        r = urllib.request.urlopen(req, context=CTX)
    except urllib.error.HTTPError as e:
        sys.exit("HTTP %s %s\n%s" % (e.code, url, e.read().decode("utf8", "replace")[:2000]))
    out = r.read()
    if raw:
        return out
    return json.loads(out) if out else {}


def jira(path, data=None, method=None):
    h = {"Authorization": "Bearer " + C["ISD_TOKEN"], "Content-Type": "application/json"}
    return call(C["ISD_URL"] + path, data, method, h)


def wiki(path, data=None, method=None, headers=None, raw=False):
    h = {"Authorization": "Basic " + base64.b64encode(
        ("%s:%s" % (C["WIKI_USER"], C["WIKI_PASS"])).encode()).decode()}
    if data is not None and not isinstance(data, bytes):
        h["Content-Type"] = "application/json"
    h.update(headers or {})
    return call(C["WIKI_URL"] + path, data, method, h, raw)


# ---------------------------------------------------------------- ticket


def cmd_info(a):
    f = "summary,description,status,resolution,created,updated,assignee,reporter,priority,attachment,comment," \
        + ",".join([CF_GROUP, CF_KB, CF_APPROVERS, CF_L3])
    d = jira("/rest/api/2/issue/%s?fields=%s" % (a.ticket, f))["fields"]
    print("== %s — %s" % (a.ticket, f_get(d, "summary")))
    print("status      : %s | resolution: %s" % (d["status"]["name"], (d.get("resolution") or {}).get("name")))
    print("assignee/L3 : %s / %s" % (user(d.get("assignee")), user(d.get(CF_L3))))
    print("group / KB  : %s / %s" % ((d.get(CF_GROUP) or {}).get("value"), d.get(CF_KB)))
    print("created/upd : %s / %s" % (d["created"][:19], d["updated"][:19]))
    print("\n-- description --\n%s" % (d.get("description") or "").strip())
    for c in (d.get("comment") or {}).get("comments", []):
        print("\n-- comment %s %s --\n%s" % (c["created"][:19], user(c["author"]), c["body"].strip()))
    atts = d.get("attachment") or []
    if atts:
        print("\n-- attachments --")
    outdir = a.download
    if outdir:
        os.makedirs(outdir, exist_ok=True)
    for at in atts:
        line = "%s  (%s bytes)" % (at["filename"], at["size"])
        if outdir:
            p = os.path.join(outdir, at["filename"])
            with open(p, "wb") as fh:
                fh.write(call(at["content"], headers={"Authorization": "Bearer " + C["ISD_TOKEN"]}, raw=True))
            line += " -> " + p
        print(line)


def user(u):
    return (u or {}).get("name") or "-"


def f_get(d, k):
    return d.get(k) or ""


def cmd_status(a):
    d = jira("/rest/api/2/issue/%s?fields=status,%s" % (a.ticket, CF_KB))
    print("%s: %s | KB: %s" % (a.ticket, d["fields"]["status"]["name"], d["fields"].get(CF_KB)))
    for t in transitions(a.ticket):
        print("   %s %-24s -> %s" % (t["id"], t["name"], t["to"]["name"]))


def transitions(key):
    try:
        return jira("/rest/api/2/issue/%s/transitions?expand=transitions.fields" % key)["transitions"]
    except SystemExit:
        return jira("/rest/api/2/issue/%s/transitions" % key)["transitions"]


def pick(trs, name=None, to=None):
    for t in trs:
        if (name and t["name"].lower() == name.lower()) or (to and t["to"]["name"].lower() == to.lower()):
            return t
    return None


# ---------------------------------------------------------------- confluence


def cmd_next_id(a):
    date = a.date or __import__("datetime").date.today().strftime("%Y%m%d")
    cql = 'space=%s and title ~ "KB%s*"' % (C["KB_SPACE"], date)
    r = wiki("/rest/api/content/search?limit=100&cql=" + urllib.parse.quote(cql))
    used = []
    for p in r.get("results", []):
        m = re.search(r"KB%s-(\d+)" % date, p["title"])
        if m:
            used.append(int(m.group(1)))
    nxt = max(used) + 1 if used else 1
    print("KB%s-%03d" % (date, nxt))
    if used:
        print("(đã có: %s)" % ", ".join("%03d" % u for u in sorted(used)), file=sys.stderr)


def validate(xhtml):
    probe = xhtml.replace("&nbsp;", " ").replace("&mdash;", "-").replace("&agrave;", "a")
    probe = re.sub(r"&(?!(amp|lt|gt|quot|apos);)[a-zA-Z]+;", " ", probe)
    ET.fromstring('<root xmlns:ac="a" xmlns:ri="r">' + probe + "</root>")


def cmd_create(a):
    body = open(a.body, encoding="utf8").read()
    validate(body)
    page = wiki("/rest/api/content", {
        "type": "page",
        "title": a.title,
        "space": {"key": a.space or C["KB_SPACE"]},
        "ancestors": [{"id": str(a.parent or C["KB_PARENT"])}],
        "body": {"storage": {"value": body, "representation": "storage"}},
    })
    url = "%s/pages/viewpage.action?pageId=%s" % (C["WIKI_URL"], page["id"])
    print("created %s\n%s" % (page["id"], url))
    for path in filter(None, (a.attach or "").split(",")):
        upload(page["id"], path.strip())


def upload(page_id, path):
    name = os.path.basename(path)
    ctype = mimetypes.guess_type(name)[0] or "application/octet-stream"
    b = str(uuid.uuid4())
    with open(path, "rb") as fh:
        data = fh.read()
    payload = b"".join([
        ("--%s\r\nContent-Disposition: form-data; name=\"file\"; filename=\"%s\"\r\n"
         "Content-Type: %s\r\n\r\n" % (b, name, ctype)).encode(),
        data,
        ("\r\n--%s\r\nContent-Disposition: form-data; name=\"comment\"\r\n\r\nfrom ISD ticket\r\n"
         "--%s--\r\n" % (b, b)).encode(),
    ])
    wiki("/rest/api/content/%s/child/attachment" % page_id, payload, "POST",
         {"Content-Type": "multipart/form-data; boundary=" + b, "X-Atlassian-Token": "nocheck"})
    print("  attached %s" % name)


def cmd_delete_page(a):
    wiki("/rest/api/content/%s" % a.page_id, method="DELETE")
    print("deleted page %s" % a.page_id)


# ---------------------------------------------------------------- close flow


def cmd_close(a):
    kb = a.kb
    if kb and kb.isdigit():
        kb = "%s/pages/viewpage.action?pageId=%s" % (C["WIKI_URL"], kb)
    group = a.group or C["ASSIGNMENT_GROUP"]
    approver = a.approver or C["KB_APPROVER"]
    for _ in range(6):
        d = jira("/rest/api/2/issue/%s?fields=status,%s" % (a.ticket, CF_KB))
        st = d["fields"]["status"]["name"]
        if st == "W/A FOR CLOSE":
            print("%s: đã ở W/A FOR CLOSE | KB: %s" % (a.ticket, d["fields"].get(CF_KB)))
            return
        trs = transitions(a.ticket)
        if st == "Customer Checking":
            t, fields = pick(trs, name="Customer Approval"), {}
        elif st == "Resolved Approval":
            t, fields = pick(trs, name="Resolve"), {"resolution": {"name": a.resolution}}
        elif st in ("KB Update", "KB Create"):
            t = pick(trs, name="Request to Close") or pick(trs, to="KB Update")
            fields = {CF_GROUP: {"value": group}}
            if t and t["to"]["name"] == "W/A for KB":
                if not kb:
                    sys.exit("thiếu --kb: cần URL trang KB trước khi Request to Close")
                fields[CF_KB] = kb
                fields[CF_APPROVERS] = [{"name": approver}]
        elif st == "W/A for KB":
            t, fields = pick(trs, to="W/A FOR CLOSE"), {}
            if not t:
                print("%s đang ở W/A for KB nhưng tài khoản này không có transition duyệt KB.\n"
                      "→ nhờ KB Approver duyệt (hoặc set mình vào KB Approvers ở bước Request to Close)." % a.ticket)
                return
        else:
            sys.exit("%s đang ở '%s' — ngoài luồng Customer Checking→W/A FOR CLOSE, xử lý tay." % (a.ticket, st))
        if not t:
            sys.exit("không tìm thấy transition hợp lệ ở trạng thái '%s'" % st)
        print("%s: %s --[%s]--> %s %s" % (a.ticket, st, t["name"], t["to"]["name"],
                                          json.dumps(fields, ensure_ascii=False) if fields else ""))
        if a.dry_run:
            return
        jira("/rest/api/2/issue/%s/transitions" % a.ticket,
             {"transition": {"id": t["id"]}, "fields": fields} if fields else {"transition": {"id": t["id"]}})
    print("dừng sau 6 bước — kiểm tra lại bằng `status`")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    s = p.add_subparsers(dest="cmd", required=True)

    x = s.add_parser("info", help="đọc ticket + tải attachment")
    x.add_argument("ticket")
    x.add_argument("--download", help="thư mục lưu attachment")
    x.set_defaults(func=cmd_info)

    x = s.add_parser("status", help="trạng thái + transition khả dụng")
    x.add_argument("ticket")
    x.set_defaults(func=cmd_status)

    x = s.add_parser("next-id", help="số KB kế tiếp trong ngày")
    x.add_argument("--date", help="YYYYMMDD, mặc định hôm nay")
    x.set_defaults(func=cmd_next_id)

    x = s.add_parser("create", help="tạo page KB (storage format)")
    x.add_argument("--title", required=True)
    x.add_argument("--body", required=True, help="file XHTML storage format")
    x.add_argument("--attach", help="danh sách file, phân tách bằng dấu phẩy")
    x.add_argument("--space")
    x.add_argument("--parent")
    x.set_defaults(func=cmd_create)

    x = s.add_parser("delete-page", help="xoá page (dọn page test)")
    x.add_argument("page_id")
    x.set_defaults(func=cmd_delete_page)

    x = s.add_parser("close", help="gắn KB + đẩy ticket tới W/A FOR CLOSE")
    x.add_argument("ticket")
    x.add_argument("--kb", help="URL trang KB hoặc pageId")
    x.add_argument("--group", help="Assignment Group, mặc định lấy từ .env")
    x.add_argument("--approver", help="KB Approver (username), mặc định lấy từ .env")
    x.add_argument("--resolution", default="Done")
    x.add_argument("--dry-run", action="store_true")
    x.set_defaults(func=cmd_close)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
