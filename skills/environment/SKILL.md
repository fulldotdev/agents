---
name: environment
description: Always use when running commands, using the browser or computer, signing in to sites, or working with files, projects, machines (MacBook, Otis), shared skills or agent configuration.
---

# Environment

## Machines

- We work on Sil's personal MacBook and on a remote always-on Mac mini named Otis.
- On MacBook, you can SSH into Otis with `ssh -A otis`.
- Keep projects in `~/projects`. Align projects and T3 Code's project lists on both machines when creating, moving, or explicitly syncing a project. Sync project contents through GitHub.

## Tools and browser

- Prefer CLIs and other direct tools when available; use the browser or computer when needed.
- Always use the machine's Chrome default profile for browser tasks.
- When Sil asks to access a site, saved Chrome credentials and password-manager autofill may be used to sign in. Never reveal, copy, export, or change saved credentials, and never enter 2FA codes.

## Shared skills and instructions

- Manage shared custom skills in `~/.agents` on the MacBook; sync to Otis through GitHub. Every agent (Codex, Claude, OpenCode, OpenClaw, Cursor) reads `~/.agents/skills` directly; there is no global AGENTS.md. Keep project instructions in their repository and credentials, plugins, and machine configuration local.
- Do not edit installed skills unless Sil explicitly asks. Local changes can block updates or be overwritten.
- Keep custom skills concise. Remove generic guidance, duplication, and detail that belongs in references or scripts.

## Automations on Otis

- Recurring agent jobs are OpenClaw cron jobs (`openclaw cron add`); plain scripts run through launchd plists in `~/Library/LaunchAgents`. `~/.agents/operations/openclaw-otis.md` lists what runs.
- A one-off or temporary job gets a clear name with its purpose and end date in the message, and is deleted as soon as it has done its work. Do not leave finished or expired jobs behind; `system-hygiene` reports any that remain.
