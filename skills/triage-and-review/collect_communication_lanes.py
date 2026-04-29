#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone

from task_triage_common import (
    RUN_LOG_DIR,
    day_bounds_utc,
    filename_time_tag,
    iso_utc,
    load_config,
)
from collect_calendar import collect_calendar as collect_calendar_lane
from collect_gmail import collect_gmail as collect_gmail_lane
from collect_meetings import collect_meetings
from collect_slack import collect_slack as collect_slack_lane
from collect_whatsapp import collect_whatsapp as collect_whatsapp_lane


def save_run(result):
    RUN_LOG_DIR.mkdir(parents=True, exist_ok=True)
    after_tag = filename_time_tag(result["after"])
    before_tag = filename_time_tag(result["before"])
    saved_at_tag = filename_time_tag(result["generated_at"])
    path = RUN_LOG_DIR / f"collect-communication-lanes_saved-{saved_at_tag}_after-{after_tag}_before-{before_tag}.json"
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return str(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--after")
    ap.add_argument("--before")
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args()

    after_dt, before_dt = day_bounds_utc(args.after, args.before, require_after=True)
    config = load_config()
    result = {
        "after": iso_utc(after_dt),
        "before": iso_utc(before_dt),
        "generated_at": iso_utc(datetime.now(timezone.utc)),
        "lanes": {
            "slack": collect_slack_lane(config, after_dt, before_dt),
            "gmail": collect_gmail_lane(after_dt, before_dt),
            "whatsapp": collect_whatsapp_lane(after_dt, before_dt),
            "calendar": collect_calendar_lane(after_dt, before_dt),
            "meetings": collect_meetings(after_dt, before_dt),
        },
    }
    saved_to = save_run(result)
    result["saved_to"] = saved_to
    print(json.dumps(result, indent=2 if args.pretty else None, ensure_ascii=False))


if __name__ == "__main__":
    main()
