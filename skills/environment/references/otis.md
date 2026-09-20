# Otis

Otis is the always-on Mac mini. It runs OpenClaw for Telegram, Discord and Slack, the scheduled agent jobs, the WhatsApp sync and the nightly contact sync. Shared skills live in `~/.agents`, synced through GitHub.

## OpenClaw

- Config `~/.openclaw/openclaw.json`, service `ai.openclaw.gateway`, loopback port 18789. Secrets stay in machine-local credential files.
- Default model `opencode-go/glm-5.3-flash` with high thinking, in the native OpenClaw runtime. Also used for subagents, images and PDFs. No automatic fallback.
- Astra and Sol stay available for explicit use, through the Codex runtime (`agentRuntime.id: codex`), because Codex brings the good desktop computer use. The four OpenAI auth profiles stay as backups.
- Plugins: telegram, discord, slack, openai, opencode-go, codex, browser, document-extract (PDF reading). Bundled OpenClaw skills are disabled one by one in `skills.entries`; memory plugin off.
- Browser: `browser.defaultProfile: "chrome"`, driver `extension`, through the OpenClaw Chrome extension, in Otis's existing Chrome profile signed into `sil@full.dev`. Agent-created tabs use the OpenClaw group. The built-in `user` profile is a separate Chrome MCP existing-session driver, not Codex's ChatGPT Chrome extension. Use the `chrome` profile. Connection details and recovery are in [Chrome setup](../skills/browser/references/chrome.md).
- No AGENTS.md or persona files. Agents read `~/.agents/skills` directly.
- Media given to the pdf and image tools must be under `/Users/otis`, not `/tmp`.

## Scheduled work

| Job | When | Runs |
|---|---|---|
| work-triage (OpenClaw cron) | 07:00, 12:00, 17:00 | `~/.agents/skills/work-triage/scripts/run.py`, report to Telegram Triage |
| target-relationships (OpenClaw cron) | daily 08:00 | agent turn, list to Telegram Sales |
| weekly-planning (OpenClaw cron) | Sunday 10:00 | agent turn, report to Telegram Planning |
| system-hygiene (OpenClaw cron) | Sunday 09:00 | agent turn, report to Telegram System |
| com.fulldev.wacli-sync (launchd) | always | `wacli sync --follow` |
| dev.fulldev.contact-enrichment.dex-google (launchd) | daily 04:15 | `~/projects/contact-enrichment/sync-dex-google.ts daily` |
| com.fulldev.otis-health (launchd) | every 15 min | `~/.agents/skills/system-hygiene/scripts/otis-health.py`, one message to Telegram System when something breaks or recovers |
| com.fulldev.pool-usage (launchd) | daily 08:03 | `~/.agents/skills/environment/scripts/pool-usage.py --telegram`, quota left per pooled account to Telegram System |

Agent jobs are created with `openclaw cron add`; plain scripts run through launchd plists in `~/Library/LaunchAgents`. Give a one-off or temporary job a clear name and delete it when done.

State lives under `~/.local/state/fulldev/`: `work-triage/` (batch, state, run receipts), `health/`. Scratch files under `~/.cache/fulldev/`.

## Telegram chats

Triage `-1003914987491`, System `-5094134988`, Sales `-5101802924`, Planning `-5475360719`, Sil privately `8491875812`.
