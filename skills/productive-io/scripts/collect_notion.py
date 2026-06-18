#!/usr/bin/env python3
import argparse, json
from productive_common import add_common_args, base_result, emit, error_obj, json_cmd, window_from_args

def title_of(row):
    props = row.get("properties") or {}
    for prop in props.values():
        if prop.get("type") == "title":
            return "".join(t.get("plain_text", "") for t in prop.get("title") or [])
    return None

def collect(query, page_size):
    data = json_cmd(["ntn", "api", "v1/search", "--data", json.dumps({"query": query, "page_size": page_size})]) or {}
    items = []
    for row in data.get("results") or []:
        items.append({
            "id": row.get("id"),
            "object": row.get("object"),
            "title": title_of(row),
            "url": row.get("url"),
            "created_time": row.get("created_time"),
            "last_edited_time": row.get("last_edited_time"),
        })
    return items

def main():
    p = argparse.ArgumentParser(); add_common_args(p); p.add_argument("--query", action="append"); p.add_argument("--page-size", type=int, default=25)
    args = p.parse_args(); a, b = window_from_args(args.after, args.before, require=False)
    r = base_result("notion", "search", a, b)
    for q in args.query or [args.customer]:
        try:
            r["items"].extend(collect(q, args.page_size))
        except Exception as exc:
            err = error_obj(q, exc); r["ok"] = False; r["errors"].append(err)
    emit(r, args.pretty, args.format)

if __name__ == "__main__":
    main()
