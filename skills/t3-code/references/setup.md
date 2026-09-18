# Otis T3 setup

Use this only for installation, service, Connect, visibility, or split-server problems.

## Architecture

- Otis runs the official headless T3 service with `~/.t3` as its state directory.
- T3 Connect exposes that environment to desktop and mobile clients on the same account.
- Exactly one server process may own `~/.t3`. Running the Otis desktop backend next to the service creates a second port, conflicting state, and duplicate relay tunnels.

## Update and service

Keep the Otis server channel and version in line with the client:

```bash
npm view t3@nightly version
npm install -g --allow-scripts=node-pty,msgpackr-extract t3@nightly
t3 service install   # first setup only
t3 service update
t3 service status
```

The macOS service is `~/Library/LaunchAgents/com.t3tools.t3code.service.plist` and listens locally on port 3773.

## T3 Connect

Link or relink Otis:

```bash
t3 connect link --base-dir "$HOME/.t3" --headless
t3 service update
t3 connect status --base-dir "$HOME/.t3" --json
```

Healthy means `desired`, `authenticated`, and `linked` are all true. Authorization codes and bearer credentials are temporary secrets. Keep them out of logs and work records.

If a remote thread shows on mobile but not on desktop, pick the Otis or All Environments filter, then open or add the remote project under Otis. That registers the remote path without cloning to MacBook.

## Browser choice

Keep `enableAgentBrowserAccess: false` in each environment's `~/.t3/userdata/settings.json`. It disables agent access to T3's embedded browser and its injected routing instructions. Native Chrome integrations remain available. Provider sessions already running can retain their earlier tools until restarted. Follow [environment's Chrome setup](../../environment/references/chrome.md) for Codex and Claude; do not disable the whole T3 MCP server or modify the installed app.

## Single-server check

When thread state diverges or projects appear twice, look at listeners and processes:

```bash
lsof -nP -iTCP:3773 -sTCP:LISTEN
lsof -nP -iTCP:3774 -sTCP:LISTEN
ps aux | egrep '[T]3 Code|[t]3 serve|cloudflared'
```

Keep the official service and stop the competing desktop backend. Restart or reconnect clients afterwards.

Upstream references: `docs/user/remote-access.md`, `docs/user/updating.md`, `docs/user/background-service.md`, and `docs/internals/t3-connect.md` in the T3 Code repository.
