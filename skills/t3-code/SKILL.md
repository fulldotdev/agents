---
name: t3-code
description: "Use when inspecting, creating, resuming, or settling T3 agent threads on Otis, or installing, updating, linking, or troubleshooting the Otis T3 service and T3 Connect."
---

# T3 Code on Otis

Otis runs the T3 server and provider processes. T3 Connect shows managed threads on the signed-in MacBook and mobile clients but does not start work. OpenClaw starts work through the local helper below.

Use a T3 thread when work must be visible across devices. T3 does not import a standalone provider resume such as `codex exec resume`.

Read [references/setup.md](references/setup.md) only for installing, updating, linking, or troubleshooting the service or T3 Connect.

## Dispatch

Use the helper instead of raw HTTP requests or bearer tokens:

```bash
python3 ~/.agents/skills/t3-code/scripts/t3_dispatch.py list

python3 ~/.agents/skills/t3-code/scripts/t3_dispatch.py status \
  --thread-id <thread-id>

python3 ~/.agents/skills/t3-code/scripts/t3_dispatch.py create \
  --project-id <project-id> \
  --title "Task title" \
  --branch <actual-checkout-branch> \
  --prompt "Read <Task URL> and complete the authorized work within the user's stated scope."

python3 ~/.agents/skills/t3-code/scripts/t3_dispatch.py resume \
  --thread-id <thread-id> \
  --prompt "Read <Task URL> and <new source>. Continue the authorized work within the user's stated scope."
```

The helper creates the thread, then starts its first turn. It also supports settle and unsettle. Defaults are `gpt-6-astra`, high reasoning, and full access. Override with `T3_DEFAULT_MODEL`, `T3_DEFAULT_REASONING_EFFORT`, `--model`, `--reasoning-effort`, or `--runtime-mode`.

## Before and after

Use `list` or `status` to see the current state and pending requests. Do not start a turn on a running thread. Pass an approval or answer the user gave through T3's response mechanism; otherwise leave the request pending. A stopped, ready, or settled thread can be resumed when the work is approved.

Pass the checkout's current Git branch as `--branch`. Resolve a detached HEAD first. The prompt gives context and limits, not development instructions.

After starting, confirm the thread exists and its state. For a tracked Task, save the T3 reference and checkout information through `work-management`. T3 stores model and session metadata itself.

For automatic triage, `work-triage` and its [t3-routing.md](../work-triage/references/t3-routing.md) decide whether work may start. This skill adds no permission of its own.
