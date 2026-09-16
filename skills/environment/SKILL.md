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
- Use the work Chrome profile signed into `sil@full.dev`: the `sil@full.dev` profile on MacBook and `Your Chrome` on Otis. Cookies and app sessions are separate on each machine. Check sign-in on the machine you are using.
- MacBook's `sil+1@full.dev`, `sil+2@full.dev` and `silveltman@gmail.com` profiles are for Sil's separate account workflows; use them only when requested. The `sil+…` names identify separate app sessions, not separate Google accounts.
- On Otis, OpenClaw uses browser profile `chrome` (extension) by default. Do not select `user` (remote-debugging attach) for routine work; it can require interactive approval again. See [Otis operations](../../operations/openclaw-otis.md).
- On MacBook, Apple Passwords handles passwords and passkeys; keep Chrome password saving and automatic sign-in disabled.
- When Sil asks to access a site, saved Chrome credentials and password-manager autofill may be used to sign in. Never reveal, copy, export, or change saved credentials, and never enter 2FA codes.

## Shared skills and instructions

- Manage shared custom skills in `~/.agents` on MacBook and sync to Otis through GitHub. Codex, Claude, OpenCode, OpenClaw, and Cursor all read `~/.agents/skills` directly. There is no global AGENTS.md. Keep project instructions in their repository. Keep credentials, plugins, and machine configuration local.
- Do not edit installed skills unless Sil explicitly asks. Local changes can block updates or be overwritten.
- Write custom skills and references in the plain style defined by `user-communication`. Start descriptions with `Use when` or `Always use when`. Remove generic advice and repetition. Put detailed procedures in references and reusable commands in scripts when that makes the skill easier to use.

## Automations on Otis

- Recurring agent jobs are OpenClaw cron jobs (`openclaw cron add`); plain scripts run through launchd plists in `~/Library/LaunchAgents`. `~/.agents/operations/openclaw-otis.md` lists what runs.
- Give a one-off or temporary job a clear name. Put its purpose and end date in the message, and delete it once the work is done. `system-hygiene` reports finished or expired jobs left behind.
