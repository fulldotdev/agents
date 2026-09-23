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

## Checking limits

Check usage limits in T3 Code’s Account pool view. Its usage source reads each machine’s local CLIProxyAPI pool.

## Local setup

- Service: launchd `com.fulldev.cliproxyapi`, loopback `127.0.0.1:8317`, binary `~/.local/share/cliproxyapi/<version>/cli-proxy-api`, config `~/.config/cliproxyapi/config.yaml`, management key `~/.config/cliproxyapi/management.key`, OAuth files `~/.local/share/cliproxyapi/auth/`.
- Log: `~/Library/Logs/CLIProxyAPI/service.log`. Read it first for any model error from T3 or a CLI.
- Claude CLI: `ANTHROPIC_BASE_URL` and `ANTHROPIC_CUSTOM_HEADERS` (x-api-key) in `~/.claude/settings.json`. Keep the native Claude login; `ANTHROPIC_AUTH_TOKEN` would break Chrome and connectors.
- Codex CLI: `model_provider = "pool"` in `~/.codex/config.toml`, with `requires_openai_auth = true` so Chrome and computer use keep the ChatGPT session.
- T3: provider settings in `~/.t3/userdata/settings.json`; see the t3-code skill.
- Adding or repairing an account: fresh OAuth login through the proxy, one at a time. Codex callbacks use port 1455, Claude 54545. For Otis, forward the port over SSH and finish the login in MacBook Chrome. A successful login does not prove available quota; check limits separately.
- Keys, OAuth files, and config stay on their machine. Otis Health checks the proxy every fifteen minutes.
