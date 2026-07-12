---
name: ssh
description: Safely inspect and operate configured SSH hosts, especially the Mac mini alias `otis`. Use when the user asks to SSH into a machine, run remote commands, inspect or sync a remote repository, copy files over SSH, or verify remote state.
---

# SSH

Use aliases from `~/.ssh/config`; do not duplicate connection details in commands or this skill. `otis` is the Mac mini.

## Workflow

1. Start read-only. Confirm the host and target path before changing anything.
2. Run bounded, non-interactive commands: `ssh <host> '<command>'`.
3. Quote the remote command so local `$variables`, globs, and substitutions do not expand accidentally.
4. Keep secrets private. Never print private keys, tokens, full environment dumps, or unrelated SSH config.
5. Report the host, affected path, resulting state, and any retained backup.

## Remote Git

Before pulling, inspect:

```sh
ssh <host> 'cd "<repo>" && git status --short && git branch --show-current && git remote -v && git rev-parse --short HEAD'
```

Then:

1. If clean, use `git pull --ff-only` and verify status plus divergence from upstream.
2. If dirty, inspect the diff and untracked files. Do not pull over them.
3. Preserve useful remote changes in the canonical repository first when appropriate.
4. Stash remaining remote state with a dated, descriptive name and `-u`; never drop that stash automatically.
5. Pull with `--ff-only`, then verify both local and remote repositories are clean and synchronized.

For global agent updates, the canonical repository is local `~/.agents`; Otis uses `~/.agents`. Push the canonical changes before pulling them on Otis.

## File Transfer

Use `rsync` for directories or resumable transfers and `scp` for a simple file. Inspect source and destination first; avoid deletion flags unless the user explicitly requests mirroring.

## Safety

Ask before destructive, irreversible, privacy-sensitive, privileged, service-restarting, or machine-rebooting actions. A request to connect or inspect does not authorize broader remote changes.
