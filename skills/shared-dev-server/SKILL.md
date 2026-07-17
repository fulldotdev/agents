---
name: shared-dev-server
description: Start, reuse, inspect, keep, or stop one tmux-backed local dev server per project. Use when asked to run dev, start a local server, inspect a dev-server URL or logs, reuse an existing project server, or clean up managed dev servers.
---

# Shared Dev Server

Use the bundled `scripts/dev-server.sh` for lifecycle operations. Run it from the project directory; do not copy it into the project or change `package.json`.

## Commands

```bash
<skill-path>/scripts/dev-server.sh start
<skill-path>/scripts/dev-server.sh status
<skill-path>/scripts/dev-server.sh logs
<skill-path>/scripts/dev-server.sh logs --follow
<skill-path>/scripts/dev-server.sh keep
<skill-path>/scripts/dev-server.sh stop
<skill-path>/scripts/dev-server.sh list
```

## Rules

1. Use the project folder name as the tmux session name.
2. Store the selected port only in the untracked `.dev/server.env`; never add it to `.env.local` or `package.json`.
3. Run the existing package script with the framework's normal port argument. For pnpm this is `pnpm run dev --port <port>`; npm needs `npm run dev -- --port <port>`.
4. Reuse a server only when its recorded project directory matches and its URL responds.
5. Let `start` renew the default four-hour lease. Run `keep` only when the user explicitly asks for the server to remain running indefinitely.
6. If startup fails, let the helper stop the session it created and report the retained log.
7. Stop only the matching managed tmux session. Broader process cleanup requires an explicit user request and target inspection.

Return the verified local URL and lease state.
