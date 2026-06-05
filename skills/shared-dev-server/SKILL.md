---
name: shared-dev-server
description: "Use when starting, reusing, debugging, or stopping local dev servers in repo workspaces."
---

# Shared Dev Server

Use one shared tmux dev server per project.

## Rules

1. Session name = project folder.
2. Store the port in `.env.local` as `DEV_PORT`.
3. tmux only keeps the server alive; `.env.local` is the source of truth for the port.
4. Before starting: check `http://localhost:$DEV_PORT`. If healthy, reuse it.
5. If `DEV_PORT` is missing: choose one unused stable port and save it to `.env.local`.
6. If unhealthy and no tmux session exists, start one:
   `mkdir -p .dev && tmux new -ds <project-folder> 'cd <project-path> && npm run dev 2>&1 | tee -a .dev/dev.log'`
7. If unhealthy but tmux exists, inspect logs instead of starting a second server.
8. Logs: `tail -f .dev/dev.log`; attach: `tmux attach -t <project-folder>`.
9. Stop tmux only when explicitly asked.

## Done

Return the local URL and any verification snapshot/result the user needs.
