# OpenClaw on Otis

Otis uses OpenClaw for Telegram, Discord, Slack and scheduled work. Native Codex owns model turns and its own tools through the official `@openclaw/codex` runtime. T3 remains the owner of development threads; use the `t3-code` dispatch helper for cross-device visibility.

## Shared configuration

- Canonical custom skills and instructions: `~/.agents`, GitHub `fulldotdev/agents`, branch `main`, on both Macs.
- Native discovery reads `~/.agents/skills` directly. Do not symlink the whole `.codex` or `.openclaw` directory. `.codex/AGENTS.md` links to `.agents/AGENTS.md`.
- Codex configuration, login, native plugins and MCPs remain machine-local in `~/.codex`. OpenClaw uses Codex's user home through `appServer.homeScope: user`.
- OpenClaw: `~/.openclaw/openclaw.json`, service `ai.openclaw.gateway`, loopback port 18789. Secrets stay in machine-local credential files, outside Git.
- Agent model: `openai/gpt-6-astra` with `agentRuntime.id: codex`. Do not replace this with only a Codex model provider, which would change the harness.
- Computer Use uses the official app-managed `unified-computer-use` plugin (`cua_repl`) on both Macs. OpenAI ships its executable and README inside `/Applications/ChatGPT.app/Contents/Resources/cua_node/lib/node_modules/@oai/cua-repl`; this is the app's native runtime, not a third-party driver. Both manual `node_repl` and obsolete disabled `computer-use` MCP entries have been removed; `codex mcp list` validates on both machines. The OpenClaw legacy readiness probe expects a direct `list_apps` MCP tool, so it is configured non-strict with `mcpServerName: cua_repl`; real browser and desktop tests remain necessary. App-use approvals from OpenClaw are routed to Sil's private Telegram chat via `approvals.plugin`.
- Native browser/Chrome and artifact plugins remain installed through Codex. Desktop app integrations still depend on local sessions and permissions; a native harness alone does not reproduce every hosted connector.
- Bundled OpenClaw skills are explicitly disabled via their `skills.entries` settings to avoid competing browser and service workflows. An empty `allowBundled` list did not disable them. Native Codex `cua_repl` provides UI control. Do not deny OpenClaw’s `computer` tool category indiscriminately: it also removes native Computer Use exposure. Shared custom skills and native Codex plugins remain available. Automatic skill rewriting and heartbeat jobs are disabled. OpenClaw's extra memory plugin is disabled (`plugins.slots.memory: none`, `memory-core.enabled: false`), including its dreaming behavior.
- OpenClaw workspace persona files `USER.md`, `SOUL.md` and `MEMORY.md` were archived outside the workspace at Sil's request. `skipBootstrap: true` prevents initial scaffold creation. The workspace contains task reports; canonical instructions remain `.agents/AGENTS.md`, discovered through native Codex. Existing conversation history is preserved.

## Telegram messages

- `messages.queue.mode: steer` explicitly retains native Codex same-turn steering. There were no stored session queue overrides at verification.
- `messages.inbound.byChannel.telegram: 2000` bundles rapid text messages from the same sender/conversation after two seconds of silence. `messages.queue.debounceMsByChannel.telegram: 2000` also batches mid-turn steering before native `turn/steer`.
- Telegram streaming mode is `off`, with block streaming disabled, to avoid separate partial-answer messages. This does not disable native Codex same-turn steering.
- A running tool finishes before Codex consumes steering at its next model boundary. Messages arriving after a completed answer start subsequent work. Attachments and control commands can bypass initial text bundling. A runtime that cannot accept steering falls back to later execution.
- Reference: <https://docs.openclaw.ai/concepts/queue-steering> and <https://docs.openclaw.ai/concepts/messages>.

## State and scheduled work

- Triage cursor and watchdog state: `~/.local/state/fulldev/work-triage`. Existing pending batches and source cursors were transferred, not reset. Old absolute temporary-artifact paths remain readable under `.hermes`; new temporary output uses `~/.cache/fulldev/work-triage`.
- Two command automations: `~/.local/share/fulldev/automations`. The refund dedupe state is in `~/.local/state/fulldev/automations`; WhatsApp monitoring retains `.wacli/watchdog-state.json`.
- Video transcription: `~/.local/share/fulldev/video-venv/bin/python`, independent of Hermes.
- Eight migrated jobs retain schedules and Telegram destinations. Cron timezone is Europe/Amsterdam. Their old/new identifiers are in `~/backups/openclaw-migration-20260911/cron-map.json`.
- Weekplanning reads original Telegram ingress in `.openclaw/state/openclaw.sqlite` and historical Hermes evidence. Edited approvals replace earlier evidence. Missing or pruned evidence blocks sending; ask for fresh approval. Source cursors remain independent across rollback.
- Hermes is archived at `~/archives/hermes-20260911/runtime`; `.hermes` is a compatibility symlink preserving historical paths required by approval evidence and old task artifacts. Its launcher and gateway plist are archived alongside it, and the service remains unloaded and disabled. Conversations, cron outputs and memory remain available as retained history, outside OpenClaw's prompt. History is not represented as a resumed native Codex or T3 thread.

## Checks

```bash
openclaw health --json
openclaw gateway status --json
openclaw cron list --all --json
python3 ~/.agents/skills/work-triage/scripts/watchdog.py --check
python3 ~/.agents/skills/t3-code/scripts/t3_dispatch.py list
```

For Computer Use, run an OpenClaw native turn on a local test page, follow the instructions returned by `cua_repl`, and check typing, clicking and a screenshot in the existing Chrome default profile. Do not accept a tool listing as proof that app control works.

## Rollback

The verified pre-migration backup is `~/backups/openclaw-migration-20260911`, including the original service plists, configuration and consistent SQLite backups. The large `.hermes/state.db` backup is stored as `state.db.gz`; its decompressed SHA-256 was verified. Decompress it before SQLite inspection or restoration. Keep both runtimes' state and histories.

1. Unload `com.fulldev.work-triage-watchdog` and stop OpenClaw with `openclaw gateway stop`. Disable its launchd service before enabling Hermes. Never run both channel listeners or schedulers together.
2. Copy the latest canonical triage state back into `.hermes/state/work-triage` as well as retaining the canonical copy. Keep the migrated approval helper: set `WEEKLY_PLANNING_RUNTIME=hermes` and `WORK_TRIAGE_RUNTIME=hermes` in the restored Hermes gateway environment. It continues to verify both histories and accepts new Hermes feedback.
3. Restore the backed-up Hermes gateway/watchdog plists and their original credentials, enable `ai.hermes.gateway`, and bootstrap it. Set `WORK_TRIAGE_RUNTIME=hermes` in the watchdog environment. Do not reset Notion batches, send claims, receipts or source cursors.
4. Hermes cron prompts still contain their original `[SILENT]` behavior. Restore that token in the two shared workflow references (`weekly-planning/references/sunday.md`, `work-triage/references/processing.md`) for Hermes operation; keep native-history verification and independent state paths.
5. Verify Hermes channel connectivity, exactly eight expected enabled jobs and triage processing before reloading the watchdog. Reconcile the current week before any customer send; uncertain deliveries require inspection, never an automatic retry.

## Known limitation and verification history

Chrome extension control was verified while Otis was locked. Native desktop control works when unlocked; locked desktop control through T3/OpenClaw remains blocked (`cgWindowNotFound`). The native harness alone does not establish the trusted connected-device turn required for automatic unlock.

See [the 11 September verification report](references/openclaw-verification-2026-09-11.md) for test results, runtime versions, session IDs, and screenshots. Those results describe the tested sessions, not a guarantee for future sessions.
