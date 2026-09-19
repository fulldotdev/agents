# T3 account pools

MacBook and Otis each run their own CLIProxyAPI service on `127.0.0.1:8317`. T3 connects to the proxy on the same machine. Otis keeps working while MacBook is asleep. T3 Connect and ordinary SSH are separate from the provider proxy.

## Accounts and selection

The Codex pool contains `sil@full.dev`, `sil+1@full.dev`, `sil+2@full.dev`, `sil+3@full.dev`, and `silveltman@gmail.com`. The Claude pool contains `sil@full.dev` and `silveltman@gmail.com`. Each machine has separately issued OAuth credentials. Shared subscription quotas still apply across both machines.

Use the Codex or Claude profile and choose a model. The proxy selects an account for a new conversation, then keeps that conversation on the selected account. It switches accounts when the selected account becomes unavailable. Model fallback is disabled. Session affinity is configured for seven days of inactivity, but bindings are held in memory and can change after a proxy restart.

## Local configuration

- Proxy executable: `~/.local/share/cliproxyapi/<version>/cli-proxy-api`.
- Proxy configuration: `~/.config/cliproxyapi/config.yaml` (JSON syntax, accepted as YAML).
- OAuth files: `~/.local/share/cliproxyapi/auth/`.
- LaunchAgent: `~/Library/LaunchAgents/com.fulldev.cliproxyapi.plist`.
- T3 provider environment and usage source: `~/.t3/userdata/settings.json`.

Keep keys and OAuth files local to each machine. The proxy listens only on loopback. Launchd restarts it after a crash. Otis Health checks local T3/proxy availability every fifteen minutes and reports persistent failures; it does not restart healthy agent sessions or prove live Connect relay connectivity.

## Native sessions and Chrome

T3 uses the native Codex and Claude drivers. Codex uses a Responses provider at `http://127.0.0.1:8317/v1`, with its local key supplied through a sensitive provider environment variable. Claude uses `ANTHROPIC_BASE_URL` plus a sensitive `ANTHROPIC_CUSTOM_HEADERS` value containing the local `x-api-key`.

Retain Claude's native account login for Chrome and connectors. Replacing it with `ANTHROPIC_AUTH_TOKEN` disables the required direct-login integration. Follow the browser skill for native Chrome pairing. Keep T3's embedded agent browser disabled.

The September 2026 cleanup consolidates profile references while retaining native session IDs, transcript content, and shared session directories. Existing shadow homes share `~/.codex/sessions` or `~/.claude/projects`; changing those links can break old conversations. Do not migrate a running thread's profile or home.

## Checks and maintenance

Check service availability, account authentication, quota responses, and an actual test turn separately. Successful OAuth does not establish that an account has available quota. T3's Account pool usage source reads quota windows through the local proxy management API.

Use fresh, independent OAuth logins when adding or repairing an account. Run logins sequentially. Codex callbacks use port 1455 and Claude callbacks use 54545. For Otis, forward that callback port over SSH while completing its login in MacBook Chrome. Finish the short-lived login promptly. Follow the browser skill for passwords and verification codes.

Keep the T3 desktop app, installed CLIs, running servers, and proxies on the same tested versions across machines. Preserve the chosen nightly channel. Weekly system hygiene checks installed and running versions and pending restarts. Test account failover, native context recall, compaction, restart, and Chrome access before changing the routing mechanism.
