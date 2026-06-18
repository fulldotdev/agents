#!/usr/bin/env python3
import argparse, importlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from productive_common import add_common_args, emit, error_obj, iso_utc, window_from_args

LANES = ["moneybird", "productive", "calendar", "notion", "github"]

def run_lane(name, args, a, b):
    mod = importlib.import_module(f"collect_{name}")
    if name == "moneybird":
        period = args.moneybird_period or f"{a:%Y%m%d}..{b:%Y%m%d}"
        return name, mod.collect(args.customer, period), None
    if name == "productive":
        items = mod.collect(a, b)
        return name, {"items": items, "total_hours": round(sum(x.get("hours") or 0 for x in items), 2)}, None
    if name == "github":
        repos = args.repo or mod.find_repos(args.repo_root)
        items = []
        for repo in repos:
            items.extend(mod.collect_repo(repo, a, b, args.author))
        return name, {"items": items, "repos": repos}, None
    if name == "calendar":
        items = []
        sources = []
        for account in args.calendar_account:
            account_items = mod.collect_account(account, a, b, args.calendar_query or args.customer)
            sources.append({"source": account, "ok": True, "items": account_items})
            items.extend(account_items)
        return name, {"items": items, "sources": sources}, None
    if name == "notion":
        items = []
        for query in args.notion_query or [args.customer]:
            items.extend(mod.collect(query, args.notion_page_size))
        return name, {"items": items}, None
    raise ValueError(name)

def main():
    p = argparse.ArgumentParser(); add_common_args(p)
    p.add_argument("--lane", action="append", choices=LANES)
    p.add_argument("--repo", action="append")
    p.add_argument("--repo-root", default="/Users/otis/projects")
    p.add_argument("--author", default="Sil")
    p.add_argument("--calendar-account", action="append", default=["sil@full.dev", "silveltman@gmail.com"])
    p.add_argument("--calendar-query")
    p.add_argument("--notion-query", action="append")
    p.add_argument("--notion-page-size", type=int, default=25)
    p.add_argument("--moneybird-period")
    args = p.parse_args(); a, b = window_from_args(args.after, args.before)
    lanes = args.lane or LANES
    r = {"generated_at": iso_utc(datetime.now(timezone.utc)), "mode": "productive_context", "after": iso_utc(a), "before": iso_utc(b), "customer": args.customer, "ok": True, "errors": [], "lanes": {}}
    with ThreadPoolExecutor(max_workers=len(lanes)) as ex:
        futures = {ex.submit(run_lane, lane, args, a, b): lane for lane in lanes}
        for future in as_completed(futures):
            lane = futures[future]
            try:
                name, value, error = future.result()
                if error:
                    raise RuntimeError(error)
                r["lanes"][name] = {"ok": True, **value}
            except Exception as exc:
                err = error_obj(lane, exc); r["ok"] = False; r["errors"].append(err)
    emit(r, args.pretty, args.format)

if __name__ == "__main__":
    main()
