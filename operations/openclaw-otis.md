# OpenClaw on Otis

Otis uses OpenClaw for Telegram, Discord, Slack and scheduled work. Normal turns use `opencode-go/glm-5.3-flash` through the native OpenClaw runtime, with high thinking. T3 remains the owner of development threads; use the `t3-code` dispatch helper for cross-device visibility.

## GLM rollout, 16 September 2026

- OpenCode Go uses the same account on both Macs. Its API key stays in machine-local OpenCode auth and the OpenClaw credential store, never Git. OpenCode 1.18.31 is installed at `~/.opencode/bin/opencode` on both machines; its model defaults to GLM 5.3 Flash with `reasoningEffort: high`.
- OpenClaw's bundled `opencode-go` provider is enabled. Its GLM model entry explicitly records the official endpoint, capabilities and supported reasoning efforts because catalog discovery alone did not make the new model executable in 2026.9.4.
- Default chat, utility text, image understanding and PDF analysis use GLM. Subagents inherit their caller's model with high thinking. All agent cron jobs inherit the default. Automatic triage passes `opencode-go/glm-5.3-flash` with high thinking explicitly, from the 16 September 17:00 run onward; the triage instructions were rewritten in plain steps for it. T3 development model choices remain independent.
- Sol is a temporary automatic model fallback during the rollout. It does not automatically rescue a failed browser/tool call. Keep the fallback until real runs have been reviewed; Astra and Sol remain available for explicit recovery.
- Native OpenClaw loads `.agents/AGENTS.md` through `bootstrap-extra-files`, with workspace and cwd `/Users/otis` and `skipBootstrap: true`. This preserves the canonical file without copying or editing it.
- The bundled `document-extract` plugin is enabled (added to `plugins.allow`) since 16 September so GLM's `pdf` tool can read attachments; the first GLM triage run failed on PDFs without it. Media paths must stay under `/Users/otis`, not `/tmp`.
- Chrome uses OpenClaw's bundled browser plugin, profile `user`, driver `existing-session`, attach-only, targeting the existing default Chrome profile. Chrome's attach consent is required. The official app `cua_repl` was tested through generic MCP but browser calls failed without Codex turn metadata; that experimental mapping was removed. Codex-specific desktop/browser tools are not established GLM capabilities.
- Verification receipts and rollback configuration: `~/backups/openclaw-glm-20260915`. GLM executed shell and read-only collection across all nine intake/context lanes. High thinking was verified in request metadata and an API response with reasoning content. Existing triage checks: 72 passed.
- The frozen synthetic benchmark scored 50/80 with the original output wording, then 77/80 and 74/80 with an explicit serialization contract. Both revised runs got all decisions, reports, evidence and batch checks right. The repeat omitted reconciliation for an uncertain prepared write (kept pending, without proposing a duplicate write) and had five target mismatches. Sil chose to move triage to GLM anyway on 16 September, with clearer instructions and review of real runs. These are prompt-adaptation results, not a directly comparable model ranking. The first two attempts lacked instruction filenames and are excluded.
- Read-only rollout reviews are scheduled for 17 and 23 September at 18:00 Europe/Amsterdam. They must not remove the fallback or change models automatically.

The Codex-specific details below describe the retained fallback setup and earlier verification, not the normal GLM runtime.

## Shared configuration

- Canonical custom skills and instructions: `~/.agents`, GitHub `fulldotdev/agents`, branch `main`, on both Macs.
- Native discovery reads `~/.agents/skills` directly. Do not symlink the whole `.codex` or `.openclaw` directory. `.codex/AGENTS.md` links to `.agents/AGENTS.md`.
- T3 and the desktop use machine-local `~/.codex`. OpenClaw uses `appServer.homeScope: agent` and its prepared Codex OAuth profile, with `CODEX_HOME=~/.openclaw/agents/main/agent/codex-home`. This fixes the user-home error when creating scheduled jobs. `HOME` remains `/Users/otis`; credentials were not copied into the agent home.
- The agent home's `AGENTS.md` links to `~/.agents/AGENTS.md`, and its `plugins` directory links to the desktop-managed `~/.codex/plugins`. Shared skills are discovered natively. Its bundled marketplace wrapper is a real directory under the agent home with links to the official app's manifest and plugin directory.
- `appServer.args` supplies the agent-owned `marketplaces.openai-bundled.source` through Codex's supported `-c` option. This is necessary because, with cwd `/Users/otis`, Codex also discovers `~/.codex/config.toml` as project configuration and otherwise overwrites the agent's marketplace path. Do not remove the override without testing actual native tools in a new turn.
- OpenClaw: `~/.openclaw/openclaw.json`, service `ai.openclaw.gateway`, loopback port 18789. Secrets stay in machine-local credential files, outside Git.
- Retained OpenAI models: `openai/gpt-6-astra` and `openai/gpt-5.6-sol`, both with `agentRuntime.id: codex`. GLM uses `agentRuntime.id: openclaw`.
- Computer Use uses the official app-managed `unified-computer-use` plugin (`cua_repl`) on both Macs. OpenAI ships its executable and README inside `/Applications/ChatGPT.app/Contents/Resources/cua_node/lib/node_modules/@oai/cua-repl`; this is the app's native runtime, not a third-party driver. Both manual `node_repl` and obsolete disabled `computer-use` MCP entries have been removed; `codex mcp list` validates on both machines. The OpenClaw legacy readiness probe expects a direct `list_apps` MCP tool, so it is configured non-strict with `mcpServerName: cua_repl`; real browser and desktop tests remain necessary. App-use approvals from OpenClaw are routed to Sil's private Telegram chat via `approvals.plugin`.
- Native browser/Chrome and artifact plugins remain installed through Codex. Desktop app integrations still depend on local sessions and permissions; a native harness alone does not reproduce every hosted connector.
- Bundled OpenClaw skills are explicitly disabled via their `skills.entries` settings to avoid competing browser and service workflows. An empty `allowBundled` list did not disable them. Native Codex `cua_repl` provides UI control. Do not deny OpenClaw’s `computer` tool category indiscriminately: it also removes native Computer Use exposure. Shared custom skills and native Codex plugins remain available. Automatic skill rewriting and heartbeat jobs are disabled. OpenClaw's extra memory plugin is disabled (`plugins.slots.memory: none`, `memory-core.enabled: false`), including its dreaming behavior.
- OpenClaw workspace persona files `USER.md`, `SOUL.md` and `MEMORY.md` were archived at Sil's request. `skipBootstrap: true` prevents initial scaffold creation. Older task reports remain in `~/.openclaw/workspace/reports`; current canonical instruction loading is described above. Existing conversation history is preserved.

## Telegram messages

- `messages.queue.mode: steer` explicitly retains native Codex same-turn steering. There were no stored session queue overrides at verification.
- `messages.inbound.byChannel.telegram: 2000` bundles rapid text messages from the same sender/conversation after two seconds of silence. `messages.queue.debounceMsByChannel.telegram: 2000` also batches mid-turn steering before native `turn/steer`.
- Telegram streaming mode is `off`, with block streaming disabled, to avoid separate partial-answer messages. This does not disable native Codex same-turn steering.
- A running tool finishes before Codex consumes steering at its next model boundary. Messages arriving after a completed answer start subsequent work. Attachments and control commands can bypass initial text bundling. A runtime that cannot accept steering falls back to later execution.
- Reference: <https://docs.openclaw.ai/concepts/queue-steering> and <https://docs.openclaw.ai/concepts/messages>.

## State and scheduled work

- `tools.profile: full` and `tools.exec.mode: full` give the configured agent full host execution. Native turns verified `danger-full-access` and enabled networking. `codexPlugins.allow_all_plugins: true` and `allow_destructive_actions: true` permit the widest supported access to already accessible connected apps; they do not install or authenticate arbitrary apps. Sil remains the allowed Telegram sender; no channel was opened to other users.
- Chat-owned automation creation, manual execution and removal were verified through the native `automations` tool. This does not establish unrestricted scheduler administration: OpenClaw grants cross-session management to fresh authenticated Control UI administrators, not Telegram owner IDs. See <https://docs.openclaw.ai/automation/cron-jobs/managing-jobs>.
- A remaining limitation in OpenClaw 2026.9.4: the tested chat-created isolated cron stored a finite default tool cap. Its run had native Codex/Astra and filesystem access but lacked `cua_repl` and the native skills catalog. Requesting `toolsAllow: ["*"]` through the creator's automation tool did not broaden the stored cap. Do not claim that chat-created crons inherit all interactive native tools. The existing migrated operator jobs retain their original explicit full tool policies. No scheduler authority or OS lock checks were bypassed.

- Triage cursor and watchdog state: `~/.local/state/fulldev/work-triage`. Watchdog stdout/stderr logs live in its `logs` subdirectory. Existing pending batches and source cursors were transferred, not reset. Temporary output uses `~/.cache/fulldev/work-triage`; retired runtime paths must not be used.
- Two command automations: `~/.local/share/fulldev/automations`. The refund dedupe state is in `~/.local/state/fulldev/automations`; WhatsApp monitoring retains `.wacli/watchdog-state.json`.
- Video transcription: `~/.local/share/fulldev/video-venv/bin/python`.
- Historical job migration identifiers are in `~/backups/openclaw-migration-20260911/cron-map.json`. Use the authenticated administrator Automations page for the current inventory.
- `weekly-planning` maintains Notion only, Sunday at 10:00 Europe/Amsterdam, with one cleanup report delivered to Telegram Planning. Customer-update drafts, approvals and Monday sending are retired. `work-triage` retains one definition running daily at 07:00 and 17:00 Europe/Amsterdam.
- The retired Hermes runtime, history, compatibility symlink and dedicated backups were removed on 13 September at Sil's request. OpenClaw is the only supported runtime; there is no Hermes rollback. Customer Git history is retained separately where it was not present in the current checkout.

## Checks

```bash
openclaw health --json
openclaw gateway status --json
openclaw cron list --all --json
python3 ~/.agents/skills/work-triage/scripts/watchdog.py --check
python3 ~/.agents/skills/t3-code/scripts/t3_dispatch.py list
```

For Computer Use, run an OpenClaw native turn on a local test page, follow the instructions returned by `cua_repl`, and check typing, clicking and a screenshot in the existing Chrome default profile. Do not accept a tool listing as proof that app control works.

## Recovery

Use the retained OpenClaw configuration and state backups under `~/backups/openclaw-migration-20260911`. Preserve current Notion batches, send claims, receipts and source cursors when recovering. Reconcile uncertain deliveries before retrying any send. Old verification reports describe their dated state, not the current installation.

## Known limitation and verification history

Chrome extension control was verified while Otis was locked. Native desktop control works when unlocked; locked desktop control through T3/OpenClaw remains blocked (`cgWindowNotFound`). The native harness alone does not establish the trusted connected-device turn required for automatic unlock.

See [the 11 September verification report](references/openclaw-verification-2026-09-11.md) for test results, runtime versions, session IDs, and screenshots. Those results describe the tested sessions, not a guarantee for future sessions.
