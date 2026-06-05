# AGENTS.md

## General
- Ask before destructive, irreversible, or privacy-sensitive actions
- When you do not have permission, always tell the user, no sloppy gueswork

## Communication
- Be extremely concise, sacrifice grammar for the sake of concision
- Be critical and concrete; push back
- When sharing a list, prefer a numbered list. Especially when needing feedback from user
- Customer drafts: extremely concise, certain and direct

## Tools
- Use notion when user references tasks, projects, customers, someday, goals, insights, meetings
- Use Moneybird when user references quotes, invoices

## Development
- Pull latest when new session.
- Work on branch `preview`; merge to `main` when tested/publish-ready.
- On teveo/fayn Shopify projects, push directly to main, user publishes via Shopify CLI.
- Verify through dev server; when done, give url(s) or snapshot(s).

## Shared dev server
- Default to one shared tmux dev server per project.
- Session name = project folder, e.g. `plantsome`.
- Port lives in `.env.local` as `DEV_PORT`; tmux only keeps server alive.
- Before starting dev, check `http://localhost:$DEV_PORT`; if healthy, reuse it.
- If `DEV_PORT` missing, choose one unused stable port and save it to `.env.local`.
- If unhealthy and no tmux session exists, start:
  `mkdir -p .dev && tmux new -ds <project-folder> 'cd <project-path> && npm run dev 2>&1 | tee -a .dev/dev.log'`
- If unhealthy but tmux exists, inspect logs instead of starting a second server.
- Logs: `tail -f .dev/dev.log`; attach: `tmux attach -t <project-folder>`.
- Stop tmux only when explicitly asked.
