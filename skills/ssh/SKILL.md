---
name: ssh
description: Use when work must run on a configured SSH host, especially Otis, including remote commands, repository inspection or sync, file transfer, and remote-state verification.
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

Use `git pull --ff-only` when compatible with the actual state. Preserve dirty and untracked work; do not stash, overwrite, or switch branches merely to make a pull succeed. Reconcile useful changes through GitHub as the task requires, then verify the intended commits reached the target checkout.

For global agent updates, the canonical repository is local `~/.agents`; Otis uses `~/.agents`. Push the canonical changes before pulling them on Otis.

## File Transfer

Use `rsync` for directories or resumable transfers and `scp` for a simple file. Inspect source and destination first; avoid deletion flags unless the user explicitly requests mirroring.

## Safety

A request to connect or inspect does not authorize broader remote changes. Apply the user's existing authorization and approval boundaries; do not ask again for an action already covered by the request.
