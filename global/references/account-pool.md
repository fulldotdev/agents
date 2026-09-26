# Account pool

Codex and Claude requests from T3, the terminal CLIs, and `codex exec` or `claude -p` go through a local CLIProxyAPI account pool on each machine. OpenClaw on Otis uses its own Codex auth profiles instead. The proxy picks an account per conversation, keeps that conversation on it, and switches when the account runs out. "Out of usage" means every pooled account is exhausted; say so instead of switching models silently.

## Accounts

| Name | Account | Plan |
|---|---|---|
| Codex | sil@full.dev | Pro |
| Codex 0 | silveltman@gmail.com | Pro-lite |
| Codex 1, 2, 3 | sil+1, sil+2, sil+3@full.dev | Pro-lite |
| Claude | sil@full.dev | Max |
| Claude 0 | silveltman@gmail.com | Max |

Use these names in reports. Each machine holds its own OAuth files; subscription quotas are shared across machines. Claude has a Fable-scoped weekly window besides the all-models weekly window, and the Fable window blocks first.

## Routing

Both machines use unique account priorities to drain accounts in a fixed order:

- Codex: Codex (500), Codex 0 (400), Codex 1 (300), Codex 2 (200), Codex 3 (100).
- Claude: Claude 0 (200), Claude (100).

The configured strategy is `fill-first` on both machines. Priorities determine the fixed account order. Session affinity keeps existing conversations on their account until it becomes unavailable. A recovered higher-priority account is eligible for new conversations again. Priorities are fixed, not automatically reordered after resets.

Change priorities through `PATCH /v0/management/auth-files/fields` with `{"name":"<auth filename>","priority":500}`. This persists the setting without replacing the selector or restarting the proxy. Check persisted priorities and real requests after changes. Previous priority settings are stored locally in `~/.config/cliproxyapi/routing-backups/` on each machine.

Set the strategy through `PUT /v0/management/routing/strategy` with `{"value":"fill-first"}` and verify it with GET on the same path. A strategy change replaces the selector and can rebind existing conversations; no service restart is needed.

## Checking limits

Read usage through the local CLIProxyAPI management API with the [pool usage helper](../../skills/t3-code/scripts/pool-usage.py):

```bash
python3 ~/.agents/skills/t3-code/scripts/pool-usage.py
python3 ~/.agents/skills/t3-code/scripts/pool-usage.py --provider claude --json
```

For Otis, run the same helper there. From MacBook, this reads Otis without copying credentials or requiring an installed copy of the helper:

```bash
ssh -A otis 'python3 - --json' < ~/.agents/skills/t3-code/scripts/pool-usage.py
```

The helper lists accounts with `GET /v0/management/auth-files`, then sends provider usage GET requests through `POST /v0/management/api-call` with `auth_index` and the literal `Bearer $TOKEN$` placeholder. The proxy supplies OAuth credentials. Output contains account identity, remaining percentages, reset timestamps and errors only. It neither changes routing nor consumes reset credits.

Use T3 Code's Account pool view when the user asks for a visual check or a comparison with T3. Read API timestamps as authoritative instants and display them in Europe/Amsterdam; T3's displayed minute can differ. Compare the same account and window, and refresh stale dashboard values before diagnosing a percentage mismatch. The same subscription shown on both machines is one quota, not two.

Codex windows are identified by `limit_window_seconds`; `primary_window` can be the weekly limit. Claude reports used percentages in `utilization` and `limits[].percent`; remaining is `100 - used`. Include the model-specific `weekly_scoped` windows, especially Fable, with their own reset times. A free five-hour window or remaining all-models quota does not make an exhausted Fable window usable. Missing usage is unknown, not zero or full. Report per-account API failures without silently trying another account or machine.

## Local setup

- Service: launchd `com.fulldev.cliproxyapi`, loopback `127.0.0.1:8317`, binary `~/.local/share/cliproxyapi/<version>/cli-proxy-api`, config `~/.config/cliproxyapi/config.yaml`, management key `~/.config/cliproxyapi/management.key`, OAuth files `~/.local/share/cliproxyapi/auth/`.
- Log: `~/Library/Logs/CLIProxyAPI/service.log`. Read it first for any model error from T3 or a CLI.
- Claude CLI: `ANTHROPIC_BASE_URL` and `ANTHROPIC_CUSTOM_HEADERS` (x-api-key) in `~/.claude/settings.json`. Keep the native Claude login; `ANTHROPIC_AUTH_TOKEN` would break Chrome and connectors.
- Codex CLI: `model_provider = "pool"` in `~/.codex/config.toml`, with `requires_openai_auth = true` so Chrome and computer use keep the ChatGPT session.
- T3: provider settings in `~/.t3/userdata/settings.json`; see the t3-code skill.
- Adding or repairing an account: fresh OAuth login through the proxy, one at a time. Codex callbacks use port 1455, Claude 54545. For Otis, forward the port over SSH and finish the login in MacBook Chrome. A successful login does not prove available quota; check limits separately.
- Keys, OAuth files, and config stay on their machine. Otis Health checks the proxy every fifteen minutes.
