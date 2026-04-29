#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timedelta, timezone

from collect_projects import collect_projects
from collect_tasks import RECENTLY_CLOSED_LOOKBACK_HOURS, collect_tasks
from task_triage_common import day_bounds_utc, iso_utc, parse_iso


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--after")
    ap.add_argument("--before")
    ap.add_argument("--recently-closed-after")
    ap.add_argument("--recently-closed-lookback-hours", type=int, default=RECENTLY_CLOSED_LOOKBACK_HOURS)
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args()

    _, before_dt = day_bounds_utc(args.after, args.before)
    recently_closed_after_dt = parse_iso(args.recently_closed_after) if args.recently_closed_after else before_dt - timedelta(hours=args.recently_closed_lookback_hours)

    result = {
        "generated_at": iso_utc(datetime.now(timezone.utc)),
        "lane": "work",
        "recently_closed_after": iso_utc(recently_closed_after_dt),
        "lanes": {
            "tasks": collect_tasks(recently_closed_after_dt=recently_closed_after_dt),
            "projects": collect_projects(),
        },
    }
    print(json.dumps(result, indent=2 if args.pretty else None, ensure_ascii=False))


if __name__ == "__main__":
    main()
