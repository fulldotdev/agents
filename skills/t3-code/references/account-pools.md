# T3 and the account pool

T3 on each machine connects to that machine's CLIProxyAPI pool on `127.0.0.1:8317`, described in [account-pool.md](../../../references/account-pool.md). Otis keeps working while MacBook is asleep. T3 Connect and SSH are separate from the provider proxy.

## Settings

- Provider environment and the "Account pool" usage source live in `~/.t3/userdata/settings.json`.
- Codex uses a Responses provider at `http://127.0.0.1:8317/v1` with `requires_openai_auth=true`, the local key in a sensitive provider environment variable.
- Claude uses `ANTHROPIC_BASE_URL` plus a sensitive `ANTHROPIC_CUSTOM_HEADERS` value with the local `x-api-key`. Keep Claude's native login for Chrome and connectors. Keep T3's embedded agent browser disabled.
- Model fallback is disabled. Session affinity lasts seven days of inactivity, held in memory, so bindings can change after a proxy restart.

## Threads

Use the Codex or Claude profile and choose a model; the proxy selects the account. Existing shadow homes share `~/.codex/sessions` and `~/.claude/projects`; changing those links breaks old conversations. Do not migrate a running thread's profile or home.

Before changing the routing mechanism, test account failover, native context recall, compaction, restart, and Chrome access with a real turn. Keep the T3 desktop app, CLI, and servers on the same tested versions across machines, on the chosen nightly channel.
