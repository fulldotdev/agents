# OpenClaw on Otis

Otis uses OpenClaw for Telegram, Discord, Slack and scheduled work. Native Codex owns model turns and its own tools through the official `@openclaw/codex` runtime. T3 remains the owner of development threads; use the `t3-code` dispatch helper for cross-device visibility.

## Shared configuration

- Canonical custom skills and instructions: `~/.agents`, GitHub `fulldotdev/agents`, branch `main`, on both Macs.
- Native discovery reads `~/.agents/skills` directly. Do not symlink the whole `.codex` or `.openclaw` directory. `.codex/AGENTS.md` links to `.agents/AGENTS.md`.
- Codex configuration, login, native plugins and MCPs remain machine-local in `~/.codex`. OpenClaw uses Codex's user home through `appServer.homeScope: user`.
- OpenClaw: `~/.openclaw/openclaw.json`, service `ai.openclaw.gateway`, loopback port 18789. Secrets stay in machine-local credential files, outside Git.
- Agent model: `openai/gpt-6-astra` with `agentRuntime.id: codex`. Do not replace this with only a Codex model provider, which would change the harness.
- Computer Use uses the native plugin through `node_repl` and its wrapper. The OpenClaw legacy readiness probe expects a direct `list_apps` MCP tool, so it is configured non-strict with `mcpServerName: node_repl`; a successful real desktop test remains necessary. Chrome currently requires approval in the Otis desktop app.
- Native browser/Chrome and artifact plugins remain installed through Codex. Desktop app integrations still depend on local sessions and permissions; a native harness alone does not reproduce every hosted connector.
- Bundled OpenClaw skills are disabled to avoid competing browser and service workflows. Shared custom skills and native Codex plugins remain available. Automatic skill rewriting, dreaming and heartbeat jobs are disabled.

## State and scheduled work

- Triage cursor and watchdog state: `~/.local/state/fulldev/work-triage`. Existing pending batches and source cursors were transferred, not reset. Old absolute temporary-artifact paths remain readable under `.hermes`; new temporary output uses `~/.cache/fulldev/work-triage`.
- Two command automations: `~/.local/share/fulldev/automations`. The refund dedupe state is in `~/.local/state/fulldev/automations`; WhatsApp monitoring retains `.wacli/watchdog-state.json`.
- Video transcription: `~/.local/share/fulldev/video-venv/bin/python`, independent of Hermes.
- Eight migrated jobs retain schedules and Telegram destinations. Cron timezone is Europe/Amsterdam. Their old/new identifiers are in `~/backups/openclaw-migration-20260911/cron-map.json`.
- Weekplanning reads original Telegram ingress in `.openclaw/state/openclaw.sqlite` and historical Hermes evidence. Edited approvals replace earlier evidence. Missing or pruned evidence blocks sending; ask for fresh approval. Source cursors remain independent across rollback.
- Hermes conversations, cron outputs and memory remain in `.hermes` as retained history. OpenClaw workspace contains copied memory/personality files. History is not represented as a resumed native Codex or T3 thread.

## Checks

```bash
openclaw health --json
openclaw gateway status --json
openclaw cron list --all --json
python3 ~/.agents/skills/work-triage/scripts/watchdog.py --check
python3 ~/.agents/skills/t3-code/scripts/t3_dispatch.py list
```

For Computer Use, run an OpenClaw native turn on a local test page, follow the installed computer-use skill, and check typing, clicking and a screenshot in the existing Chrome default profile. Do not accept a tool listing as proof that app control works.

## Rollback

The verified pre-migration backup is `~/backups/openclaw-migration-20260911`, including the original service plists, configuration and consistent SQLite backups. The large `.hermes/state.db` backup is stored as `state.db.gz`; its decompressed SHA-256 was verified. Decompress it before SQLite inspection or restoration. Keep both runtimes' state and histories.

1. Unload `com.fulldev.work-triage-watchdog` and stop OpenClaw with `openclaw gateway stop`. Disable its launchd service before enabling Hermes. Never run both channel listeners or schedulers together.
2. Copy the latest canonical triage state back into `.hermes/state/work-triage` as well as retaining the canonical copy. Keep the migrated approval helper: set `WEEKLY_PLANNING_RUNTIME=hermes` and `WORK_TRIAGE_RUNTIME=hermes` in the restored Hermes gateway environment. It continues to verify both histories and accepts new Hermes feedback.
3. Restore the backed-up Hermes gateway/watchdog plists and their original credentials, enable `ai.hermes.gateway`, and bootstrap it. Set `WORK_TRIAGE_RUNTIME=hermes` in the watchdog environment. Do not reset Notion batches, send claims, receipts or source cursors.
4. Hermes cron prompts still contain their original `[SILENT]` behavior. Restore that token in the two shared workflow references (`weekly-planning/references/sunday.md`, `work-triage/references/processing.md`) for Hermes operation; keep native-history verification and independent state paths.
5. Verify Hermes channel connectivity, exactly eight expected enabled jobs and triage processing before reloading the watchdog. Reconcile the current week before any customer send; uncertain deliveries require inspection, never an automatic retry.

## Migration verification, 11 September 2026

- 54 weekplanning and 60 triage tests passed, with independent Astra review.
- Native Codex turns reported `agentHarnessId: codex` and executed native terminal and `node_repl` tools.
- A silent native cron test completed with `NO_REPLY`; its one-shot job was removed automatically.
- The migrated WhatsApp watchdog completed with exit 0 and no output or message.
- All three channels reconnected after a managed gateway restart. Eight jobs retained their next-run times; the triage watchdog passed with existing pending/deferred state preserved.
- T3's authenticated helper still listed its 57 threads. The independent transcription environment imported faster-whisper 1.2.1.
- Still open: native Computer Use app control. The actual Chrome test returned “Computer Use was not approved to use Google Chrome.” Grant Chrome access in the desktop app on Otis, then rerun the local fixture test. No app-control success is claimed from `list_apps` alone.
- MacBook's older duplicate `.codex/skills/social-posts` was archived under `~/backups/openclaw-migration-20260911`; canonical `.agents/skills/social-posts` remains.
