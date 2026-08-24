# Otis T3 Setup

Use this reference only for T3 installation, service, Connect, visibility, or split-server problems.

## Current architecture

- Otis uses the official headless T3 service with `~/.t3` as its state directory.
- T3 Connect exposes that environment to desktop and mobile clients signed into the same account.
- Exactly one server process may own `~/.t3`. Running the Otis desktop backend beside the service can create a second port, conflicting state, and duplicate relay tunnels.

## Update and service

Keep the Otis server channel/version aligned with the client:

```bash
npm view t3@nightly version
npm install -g --allow-scripts=node-pty,msgpackr-extract t3@nightly
t3 service install   # first setup only
t3 service update
t3 service status
```

The macOS service is normally `~/Library/LaunchAgents/com.t3tools.t3code.service.plist` and listens locally on port 3773.

## T3 Connect

Link or relink Otis with:

```bash
t3 connect link --base-dir "$HOME/.t3" --headless
t3 service update
t3 connect status --base-dir "$HOME/.t3" --json
```

Healthy status has `desired`, `authenticated`, and `linked` all true. Authorization codes and bearer credentials are ephemeral secrets and do not belong in logs or work records.

If a remote thread is visible on mobile but not desktop, select the Otis or All Environments filter and open/add the existing remote project under Otis. That registers the remote path; it does not clone it to the MacBook.

## Single-server check

When thread state diverges or duplicate projects appear, inspect listeners and processes:

```bash
lsof -nP -iTCP:3773 -sTCP:LISTEN
lsof -nP -iTCP:3774 -sTCP:LISTEN
ps aux | egrep '[T]3 Code|[t]3 serve|cloudflared'
```

For the remote-first Otis setup, retain the official service and stop the competing Otis desktop backend. Restart/reconnect clients after restoring one server.

Primary upstream references are `docs/user/remote-access.md`, `docs/user/updating.md`, `docs/user/background-service.md`, and `docs/internals/t3-connect.md` in the T3 Code repository.

