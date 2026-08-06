---
name: wacli
description: Use wacli on the SSH host `otis` to authenticate, sync, inspect, search, or send third-party WhatsApp messages and files. Trigger for explicit WhatsApp history/tool requests, requests to read a recent reply, or requests to contact someone else; normal active WhatsApp conversations use the gateway.
---

# wacli

1. Run wacli on the Mac mini through the configured SSH alias `otis`. Do not use the local wacli store as the WhatsApp source.
2. Inspect the remote CLI before use: `ssh otis 'wacli --version && wacli --help'`, followed by the relevant `wacli <command> --help` on Otis. Use `https://wacli.sh` only when current documentation is needed.
3. For reads, searches, message context, and recent replies, use bounded non-interactive commands shaped like `ssh otis 'wacli ... --read-only --json'`. Scope every command to the smallest relevant chat and time window.
4. When the user asks to read a new or recent reply and Otis has not received it yet, run a bounded `wacli sync --once` on Otis, then repeat the scoped read. Run authentication, history backfill, downloads, or broader local-store mutations only when explicitly requested.
5. Select the requested named account/store explicitly when multiple accounts exist.
6. Before sending, require an exact recipient and message/file. Confirm both immediately before executing any third-party send from Otis.

For WhatsApp reads covered by this skill, do not switch to Computer Use, browser control, Chrome, or WhatsApp Web. If Otis or its wacli store is unavailable, report that boundary instead of changing surfaces.

Do not use wacli for the user’s normal active chat. Do not expose private message history, account data, or store contents beyond the requested scope.
