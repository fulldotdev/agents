---
name: wacli
description: Use when an explicit request needs wacli on Otis to authenticate, sync, inspect, search, or send third-party WhatsApp messages and files, including history searches and reading recent replies. Normal active WhatsApp conversations use the gateway.
---

# wacli

- Run wacli on Otis, where its store lives. From another machine, go through `ssh otis`.
- Docs: [wacli.sh](https://wacli.sh).
- For reads, searches, and recent replies, use bounded non-interactive commands with `--read-only --json`, limited to the smallest relevant chat and time window. `work-triage` uses its own collector instead of running wacli by hand.
- If a recent reply is not in the store yet, run one `wacli sync --once` on Otis and read again. Authentication, history backfill, downloads, and other store changes need an explicit request.
- When there are several accounts, name the account or store explicitly.
- Send only when the user has approved that exact recipient and message or file. If any of those is unclear, confirm first.

Stay on wacli for WhatsApp reads. Do not switch to computer use, the browser, or WhatsApp Web. If Otis or the store is unavailable, report that.

Do not use wacli for the user's own active chat.
