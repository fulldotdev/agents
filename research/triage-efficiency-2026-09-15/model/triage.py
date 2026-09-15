#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def load_cases():
    path = Path(__file__).parent / ".data" / "evidence.json"
    return json.loads(path.read_text())["cases"]


def main():
    parser = argparse.ArgumentParser(description="Read synthetic triage evidence")
    sub = parser.add_subparsers(dest="command", required=True)
    show = sub.add_parser("show")
    show.add_argument("--event", required=True)
    context = sub.add_parser("context")
    group = context.add_mutually_exclusive_group(required=True)
    group.add_argument("--case")
    group.add_argument("--query")
    args = parser.parse_args()
    cases = load_cases()

    if args.command == "show":
        matches = [case for case in cases if case["queue_event"] == args.event]
        payload = [{"case_id": c["case_id"], "queue_event": c["queue_event"], "topic": c["topic"], "source": c["source"]} for c in matches]
        marker = f"RETRIEVAL event={args.event} matches={len(payload)}"
    elif args.case:
        matches = [case for case in cases if case["case_id"] == args.case]
        payload = [{"case_id": c["case_id"], "destinations": c["destinations"], "context": c["context"]} for c in matches]
        marker = f"RETRIEVAL case={args.case} matches={len(payload)}"
    else:
        needle = args.query.casefold()
        matches = [case for case in cases if needle in json.dumps(case).casefold()]
        payload = matches
        marker = f"RETRIEVAL query={args.query!r} matches={len(payload)}"

    print(marker)
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
