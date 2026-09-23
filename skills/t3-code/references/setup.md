# T3 setup

Use this for project setup, installation, service, Connect, visibility, or split-server problems.

## Projects

Use the exact GitHub repository name as the T3 project name, without the owner prefix. New checkouts go in `~/projects/<repo-name>`. Check each machine's `origin` and T3 workspace path against the intended repository, then verify that MacBook and Otis have matching registrations. Existing paths can stay when threads or tools depend on them.

Keep Project grouping on so each repository appears once with MacBook and Otis as environments. Accept `owner/repo` as T3’s combined label. Verify one project in the command palette and both environments in the new-chat selector.

GitHub transfers committed work through pushes and fetches or pulls. It does not sync uncommitted files, ignored files, or the branch checked out on the other machine. Report those separately from broken project links. Compare patches before calling divergent commits unique; cherry-picked changes can have different commit IDs.

When a repository moves or is renamed, update its existing T3 record so its threads stay attached. Before removing a project, check archived threads as well as visible ones. The shell/list response can omit archived threads; an empty list does not prove the project has no history.

## Architecture

- Otis runs the official headless T3 service with `~/.t3` as its state directory.
- T3 Connect exposes that environment to desktop and mobile clients on the same account.
- Exactly one server process may own `~/.t3`. Running the Otis desktop backend next to the service creates a second port, conflicting state, and duplicate relay tunnels.

## Update and service

Keep the Otis server channel and version in line with the client:

```bash
npm view t3@nightly version
t3 update <tested-version> --channel nightly --base-dir "$HOME/.t3" --yes
t3 service status
```

Use `t3 service install --base-dir "$HOME/.t3"` for first setup or to refresh an existing service after a package-manager update. Check for active turns before restarting. The macOS service is `~/Library/LaunchAgents/com.t3tools.t3code.service.plist` and listens locally on port 3773. Update the MacBook desktop app separately to the same tested version; compare the running server with the installed CLI after restarting.

## T3 Connect

Link or relink Otis:

```bash
t3 connect link --base-dir "$HOME/.t3" --headless
t3 service restart
t3 connect status --base-dir "$HOME/.t3" --json
```

The saved Connect configuration should have `desired`, `authenticated`, and `linked` all true. Confirm live connectivity by opening the Otis environment from another device. The saved status alone does not prove the relay is connected. Authorization codes and bearer credentials are temporary secrets. Keep them out of logs and work records.

If a remote thread shows on mobile but not on desktop, pick the Otis or All Environments filter, then open or add the remote project under Otis. That registers the remote path without cloning to MacBook.

## Browser choice

Use T3's embedded browser for local and preview checks that need no login. Use the user's Chrome profile for signed-in sites and Shopify previews, following [Chrome setup](../../browser/references/chrome.md).

Enable **Agent browser access** in Settings → Integrations for the owning environment. This controls `enableAgentBrowserAccess` in `~/.t3/userdata/settings.json`; T3 omits values equal to its defaults. Use the settings UI while T3 is running so cached settings do not overwrite a file edit. Check project overrides. Existing provider sessions may need a new session to receive the tools.

## Single-server check

When thread state diverges or projects appear twice, look at listeners and processes:

```bash
lsof -nP -iTCP:3773 -sTCP:LISTEN
lsof -nP -iTCP:3774 -sTCP:LISTEN
ps aux | egrep '[T]3 Code|[t]3 serve|cloudflared'
```

Keep the official service and stop the competing desktop backend. Restart or reconnect clients afterwards.

Upstream references: `docs/user/remote-access.md`, `docs/user/updating.md`, `docs/user/background-service.md`, and `docs/internals/t3-connect.md` in the T3 Code repository.
