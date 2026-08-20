---
name: wacli
description: Use wacli on the Otis Mac mini to authenticate, sync, inspect, search, or send third-party WhatsApp messages and files. Trigger for explicit WhatsApp history/tool requests, recent-reply reads, or requests to contact someone else; normal active WhatsApp conversations use the gateway.
---

# wacli

1. Run wacli where its authoritative store lives on Otis. When already running on Otis, use the local CLI and store directly. From another machine, use the configured SSH alias `otis`.
2. Inspect the relevant `wacli <command> --help` on Otis before unfamiliar operations. Use `https://wacli.sh` only when current documentation is needed.
3. For reads, searches, message context, and recent replies, use bounded non-interactive commands with `--read-only --json`, scoped to the smallest relevant chat and time window. `work-triage` should normally use its collector rather than operating wacli manually.
4. When a requested recent reply has not reached the store, run one bounded `wacli sync --once` on Otis, then repeat the scoped read. Authentication, history backfill, downloads, and broader store mutations require an explicit request.
5. Select the requested named account/store explicitly when multiple accounts exist.
6. Before sending, require an exact recipient and message/file. Confirm both immediately before executing any third-party send.

For WhatsApp reads covered by this skill, do not switch to Computer Use, browser control, Chrome, or WhatsApp Web. If Otis or its wacli store is unavailable, report that boundary instead of changing surfaces.

Do not use wacli for the user’s normal active chat. Do not expose private message history, account data, or store contents beyond the requested scope.
