---
name: t3-code
description: "Operate T3-managed agent threads on Otis: inspect, create, resume, settle, and expose them through T3 Connect. Use for T3 thread dispatch or the rare Otis T3 service/Connect issue."
license: MIT
metadata:
  hermes:
    tags: [T3-Code, T3-Connect, Remote-Agents, Automation]
    related_skills: [codex, work-management, work-triage]
---

# T3 Code on Otis

Otis runs the authoritative T3 server and provider processes. T3 Connect makes its managed threads visible on the signed-in MacBook and mobile clients; it does not itself start work. Hermes starts work through the authenticated local dispatch helper.

Use T3-managed threads when cross-device visibility matters. A standalone provider resume, such as `codex exec resume`, is not automatically imported into T3.

Read [references/setup.md](references/setup.md) only when installing, updating, linking, or troubleshooting the Otis service or T3 Connect.

## Dispatch

Use the helper instead of building HTTP requests or handling bearer tokens:

```bash
python3 ~/.agents/skills/t3-code/scripts/t3_dispatch.py list

python3 ~/.agents/skills/t3-code/scripts/t3_dispatch.py status \
  --thread-id <thread-id>

python3 ~/.agents/skills/t3-code/scripts/t3_dispatch.py create \
  --project-id <project-id> \
  --title "Task title" \
  --prompt "Read <Task URL> and continue to the review/preview boundary."

python3 ~/.agents/skills/t3-code/scripts/t3_dispatch.py resume \
  --thread-id <thread-id> \
  --prompt "See <new source> and the updated Task <Task URL>. Continue within scope and stop at review/preview."
```

The helper creates a thread before starting its first turn, supports settle/unsettle operations, and defaults to `gpt-5.6-sol`, high reasoning, and full access. Override these with `T3_DEFAULT_MODEL`, `T3_DEFAULT_REASONING_EFFORT`, `--model`, `--reasoning-effort`, or `--runtime-mode` when a task needs different settings.

## Triage integration

Notion is the work source of truth; T3 is an optional execution surface. For automated triage, load `work-triage` and apply its automatic-dispatch gate. A Task may have at most one owning T3 thread; most Tasks do not need one.

Before dispatch:

1. Update the owning Task with the exact new source.
2. Use the compact T3 index or `status` to check `sessionStatus`, `latestTurnState`, pending approvals, and pending user input.
3. Create only when an eligible Task has no thread. Resume only for actionable input that belongs to the same eligible Task, outcome, and small low-risk scope.
4. Start a turn only when the thread is not already running or waiting for approval/input.

The presence of a Task, new feedback, or an existing thread does not by itself authorize an automated turn. When the gate does not pass, triage prepares the work and reports it for Sil instead.

A stopped, ready, or settled thread may be resumed directly. Store the T3 environment, project ID, thread ID, repository path, branch, provider/model, and provider session ID when available as a source-grounded Task Timeline event. Do not store credentials.

Automated prompts follow the user-visible handoff rules in `work-triage/references/t3-routing.md`. They say in normal language that heartbeat triage started the turn, what new event caused it, and what work will continue. Task links, source links, scope, and safety limits come afterward.

The agent's first user-visible message identifies the automatic trigger. Its final reply opens with the reason the turn started and what the agent did, then states the result and Sil's next action. Do not lead with files, commits, test counts, IDs, or vendor internals.

External communication, release, payment, and ambiguous irreversible actions remain approval-gated.

After dispatch, confirm the expected thread exists and surface completed, running, failed, approval-needed, or user-input-needed state. Verify filesystem or git results only when the owning execution workflow calls for that verification; triage itself stops after dispatch.
