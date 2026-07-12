---
name: wacli
description: Use the locally installed wacli tool to authenticate, sync, inspect, search, or send third-party WhatsApp messages and files. Trigger only for explicit WhatsApp history/tool requests or requests to contact someone else; normal active WhatsApp conversations use the gateway.
---

# wacli

1. Inspect `wacli --version`, `wacli --help`, and the relevant `wacli <command> --help`. Use `https://wacli.sh` for current documentation.
2. Select the requested named account/store explicitly when multiple accounts exist.
3. For read-only inspection, prefer `--read-only --json`; scope searches to the smallest relevant chat and window.
4. Run authentication, sync, history backfill, downloads, or local-store mutations only when the user requested them. Backfill is best-effort and may require the primary phone online.
5. Before sending, require an exact recipient and message/file. Confirm both immediately before executing any third-party send.

Do not use wacli for the user’s normal active chat. Do not expose private message history, account data, or local store contents beyond the requested scope.
