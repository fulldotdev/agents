# Otis

Otis is the always-on Mac mini. It runs OpenClaw for Telegram, Discord and Slack, the scheduled agent jobs, the WhatsApp sync and the nightly contact sync. Shared skills live in `~/.agents`, synced through GitHub.

## OpenClaw

- Config `~/.openclaw/openclaw.json`, service `ai.openclaw.gateway`, loopback port 18789. Secrets stay in machine-local credential files.
- Default model `openai/gpt-6-astra` with high thinking, in the Codex runtime (`agentRuntime.id: codex`), including its desktop computer use, through OpenClaw's own Codex OAuth profiles and the existing subscriptions. The cron jobs use the same model. `opencode-go/glm-5.3-flash` in the native OpenClaw runtime remains the utility, image and PDF model. No automatic fallback.
- Plugins: telegram, discord, slack, openai, opencode-go, codex, browser, document-extract (PDF reading). Bundled OpenClaw skills are disabled one by one in `skills.entries`; memory plugin off.
- Browser: `browser.defaultProfile: "chrome"`, driver `extension`, through the OpenClaw Chrome extension, in Otis's existing Chrome profile signed into `sil@full.dev`. Agent-created tabs use the OpenClaw group. The built-in `user` profile is a separate Chrome MCP existing-session driver, not Codex's ChatGPT Chrome extension. Use the `chrome` profile. Connection details and recovery are in [Chrome setup](../skills/browser/references/chrome.md).
- Shared instructions come from `~/.agents/global/AGENTS.md` through the `bootstrap-extra-files` hook; the Codex runtime reads the same file through `codex-home/AGENTS.md`. No persona or memory files, the session-memory hook and memory flush are off. Skills come from `~/.agents/skills` directly.
- Media given to the pdf and image tools must be under `/Users/otis`, not `/tmp`.

## Scheduled work

| Job | Machine | When | Source / installer |
|---|---|---|---|
| work-triage (OpenClaw cron) | Otis | 07:00, 18:00 | `~/.agents/skills/work-triage/scripts/run.py`; Astra high; Telegram Triage |
| weekly-planning (OpenClaw cron) | Otis | Sunday 10:00 | `~/.agents/skills/weekly-planning/SKILL.md`; Astra high; Telegram Planning |
| system-hygiene (OpenClaw cron) | Otis | Sunday 09:00 | `~/.agents/skills/system-hygiene/SKILL.md`; Astra high; Telegram System |
| ai.openclaw.gateway | Otis | always | OpenClaw's own service installer and local config |
| com.t3tools.t3code.service | Otis | always | `t3 service install --base-dir ~/.t3`; runtime in `~/.t3/runtime/versions/` |
| com.fulldev.cliproxyapi | Both | always | local binary in `~/.local/share/cliproxyapi/`; [account pool setup](account-pool.md) |
| com.fulldev.wacli-sync | Otis | always | Homebrew `wacli sync --follow`; local LaunchAgent |
| dev.fulldev.contact-enrichment.google-google | Otis | daily 04:15 | `~/projects/contact-enrichment/sync-google-google.ts daily`; own project repo |
| com.fulldev.health | Both | at login, every 15 min | `~/.agents/skills/system-hygiene/scripts/health.py`; installer `install-health.py` in the same directory |
| com.fulldev.pool-routing | Both | at login, every 15 min | `~/.agents/skills/t3-code/scripts/pool-routing.py --apply`; installer `install-pool-routing.py` in the same directory |
| com.fulldev.otis-restart | Otis | first eligible day of each month, 05:00 | `~/.agents/global/scripts/otis-restart.py`; installer `install-otis-restart.sh` in the same directory |

Health runs locally on each Mac. MacBook submits only check booleans and a timestamp to Otis. Otis sends one combined report to Telegram System when a problem changes or recovers and starts a read-only T3 investigation for a persistent incident. See [health setup](health.md) for status, logs, installation and restricted SSH access.

Agent jobs are created with `openclaw cron add`; plain scripts run through launchd plists in `~/Library/LaunchAgents`. Give a one-off or temporary job a clear name and delete it when done.

System and vendor jobs are separate from Fulldev automation and should not be removed during routine cleanup. The MacBook has `com.google.GoogleUpdater.wake` hourly and `homebrew.mxcl.postgresql@15`. Otis has the Google updater; its Google Keystone jobs are disabled leftovers. OpenClaw's disabled heartbeat and skill-collection jobs are system-owned. There are no user crontabs. Fulldev recurring jobs use launchd or OpenClaw cron, and the combined health report is the source of truth for both Macs.

State lives under `~/.local/state/fulldev/`: `work-triage/` (batch, state, run receipts), `health/`, `pool-routing/`, `restart/`. Health and routing logs live in `~/Library/Logs/fulldev/`. Scratch files under `~/.cache/fulldev/`.

Google automation uses `gog`'s encrypted file keyring. `~/.local/bin/gog` loads its generated unlock key from the owner-only file `~/.config/gogcli/keyring-password` and runs the Homebrew binary. Keep `~/.local/bin` before Homebrew in shell and service PATHs; direct calls to `/opt/homebrew/bin/gog` omit the unlock key. OpenClaw's service environment and the contact-sync, health, and restart LaunchAgents use this path. The key and credentials stay local to Otis. Health and restart recovery check `gog auth list --check --json --no-input`; revoked Google authorization still requires consent.

The monthly restart is enabled. An unattended restart passed on 22 September at 22:04 after automatic login was re-saved in Users & Groups. Tailscale, OpenClaw, T3, the account proxy and WhatsApp sync returned without manual login. The installer `bash ~/.agents/global/scripts/install-otis-restart.sh` authorizes only `/sbin/shutdown -r now`, registers the 05:00 LaunchAgent, and attempts a restart after checking for active work. The recovery check reuses the existing health checks. State lives in `~/.local/state/fulldev/restart/`; logs in `~/Library/Logs/fulldev/otis-restart.log`.

## Telegram chats

Triage `-1003914987491`, System `-5094134988`, Sales `-5101802924`, Planning `-5475360719`, Sil privately `8491875812`.
