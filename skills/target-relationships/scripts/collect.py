#!/usr/bin/env python3
"""Collect what the daily network list needs: Target companies with notes, Dex contacts there, people already suggested, and Sil's DM examples."""

import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

COMPANIES_DATA_SOURCE = "2635979e-268c-8191-b322-000bd3109d1c"
DM_EXAMPLES_PAGE = "3db5979e-268c-8193-a787-dbd704257d2f"
CRON_JOB_NAME = "target-relationships"
LOOKBACK_DAYS = 21
OUT = Path.home() / ".local/state/fulldev/target-relationships/batch.md"
LINK = re.compile(r"\[([^\]]+)\]\((https://www\.linkedin\.com/in/[^)\s]+)\)")


def run(cmd, timeout=120):
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode:
        raise RuntimeError(f"{' '.join(cmd[:3])}: {result.stderr.strip()[:200]}")
    return result.stdout


def text_of(prop):
    kind = prop.get("type")
    values = prop.get(kind) if kind in ("title", "rich_text") else None
    return "".join(part.get("plain_text", "") for part in values or [])


def target_companies():
    rows, cursor = [], None
    while True:
        cmd = ["ntn", "datasources", "query", COMPANIES_DATA_SOURCE, "--json", "--limit", "100",
               "--filter", json.dumps({"property": "Status", "status": {"equals": "Target"}})]
        if cursor:
            cmd += ["--start-cursor", cursor]
        data = json.loads(run(cmd))
        rows += data.get("results", [])
        cursor = data.get("next_cursor")
        if not data.get("has_more") or not cursor:
            break
    companies = []
    for row in rows:
        props = row.get("properties", {})
        website = next((f.get("external", {}).get("url") for f in props.get("Resources", {}).get("files", [])
                        if f.get("name", "").lower() == "website"), None)
        companies.append({"name": text_of(props.get("Name", {})), "website": website, "url": row.get("url"), "id": row["id"]})
    return companies


def notes(company):
    try:
        body = run(["ntn", "pages", "get", company["id"]])
        body = body.split("\n---\n", 2)[-1].strip() if body.count("\n---\n") >= 1 else body.strip()
        return body[:6000]
    except Exception as exc:
        return f"(notities niet leesbaar: {exc})"


def dex_contacts(company):
    try:
        data = json.loads(run(["dex", "dex-filter-contacts", "--company", company["name"], "--limit", "25"], timeout=60))
    except Exception as exc:
        return [f"(Dex niet gelezen: {str(exc)[:80]})"]
    people = []
    for item in data.get("items", []):
        name = item.get("full_name") or " ".join(filter(None, [item.get("first_name"), item.get("last_name")]))
        title = item.get("job_title") or item.get("title") or ""
        linkedin = item.get("linkedin") or item.get("linkedin_url") or ""
        people.append(" · ".join(filter(None, [name, title, linkedin])))
    return people


def previous_lists():
    jobs = json.loads(run(["openclaw", "cron", "list", "--json"])).get("jobs", [])
    job = next(j for j in jobs if j["name"] == CRON_JOB_NAME)
    runs = json.loads(run(["openclaw", "cron", "runs", "--id", job["id"], "--json"]))
    since = (datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)).timestamp() * 1000
    suggested = {}
    for entry in runs.get("entries") or runs.get("runs") or []:
        if entry.get("action") != "finished" or (entry.get("runAtMs") or 0) < since:
            continue
        day = (entry.get("runAtIso") or "")[:10]
        for name, url in LINK.findall(entry.get("summary") or ""):
            url = url.rstrip("/")
            suggested.setdefault(url, {"name": name.strip("* "), "url": url, "dates": []})["dates"].append(day)
    return sorted(suggested.values(), key=lambda p: max(p["dates"]), reverse=True)


def main():
    companies = target_companies()
    with ThreadPoolExecutor(max_workers=6) as pool:
        bodies = list(pool.map(notes, companies))
    dex = [dex_contacts(c) for c in companies]  # sequential: the Dex API rate-limits
    try:
        suggested = previous_lists()
    except Exception as exc:
        suggested = [{"name": f"(eerdere lijsten niet gelezen: {str(exc)[:100]})", "url": "", "dates": []}]
    try:
        examples = run(["ntn", "pages", "get", DM_EXAMPLES_PAGE]).strip()
    except Exception as exc:
        examples = f"(DM-voorbeelden niet leesbaar: {exc})"

    lines = [f"# Netwerklijst-input · {datetime.now().strftime('%Y-%m-%d')}", "",
             f"## Targetbedrijven ({len(companies)})", ""]
    for company, body, people in zip(companies, bodies, dex):
        lines += [f"### {company['name']}", f"Website: {company['website'] or 'onbekend'} · Notion: {company['url']}", "",
                  body or "(geen notities)", "", "Bekend in Dex: " + ("; ".join(people) if people else "niemand"), ""]
    lines += [f"## Al gesuggereerd in de laatste {LOOKBACK_DAYS} dagen ({len(suggested)})", ""]
    lines += [f"- {p['name']} · {p['url']} · {', '.join(sorted(set(p['dates'])))}" for p in suggested] or ["- niemand"]
    lines += ["", "## Sils LinkedIn DM-voorbeelden", "", examples, ""]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines))
    print(f"{OUT} · {len(companies)} targetbedrijven · {len(suggested)} eerder gesuggereerd · {OUT.stat().st_size:,} bytes")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"collect failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
