---
name: t3-code
description: "Operate T3-managed agent threads on Otis: inspect, create, resume, settle, and expose them through T3 Connect. Use for T3 thread dispatch or the rare Otis T3 service/Connect issue."
license: MIT
---

# T3 Code on Otis

Otis runs the authoritative T3 server and provider processes. T3 Connect makes its managed threads visible on the signed-in MacBook and mobile clients; it does not itself start work. OpenClaw starts work through the authenticated local dispatch helper.

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
  --branch <actual-checkout-branch> \
  --prompt "Read <Task URL>. Use development and complete the authorized work, including its agreed review or release boundary."

python3 ~/.agents/skills/t3-code/scripts/t3_dispatch.py resume \
  --thread-id <thread-id> \
  --prompt "Read <Task URL> and <new source>. Use development and complete the authorized work, including its agreed review or release boundary."
```

The helper creates a thread before starting its first turn, supports settle/unsettle operations, and defaults to `gpt-6-astra`, high reasoning, and full access. Override these with `T3_DEFAULT_MODEL`, `T3_DEFAULT_REASONING_EFFORT`, `--model`, `--reasoning-effort`, or `--runtime-mode` when a task needs different settings.

## Triage integration

For automatic triage, use `work-triage` and its [dispatch gate](../work-triage/references/t3-routing.md); that reference owns source updates, authorization, and handoff requirements. This tool skill grants no additional start permission.

Use the compact T3 index or `status` to check live state and pending requests. Do not duplicate a running turn. When Sil has supplied a pending approval or answer, pass it through T3's supported response mechanism and continue the authorized work; otherwise preserve the pending request. A stopped, ready, or settled thread may be resumed directly when the requested work is authorized.

For implementation handoffs, tell the executing agent to use `development`. Inspect Git in the target checkout and pass its current branch through the required `--branch` argument. Resolve a detached HEAD before creating a thread; do not invent a branch.

After dispatch, confirm the expected thread and its state. On a tracked Task, preserve its T3 locator and relevant checkout information through `work-management`; native T3 already owns model and session metadata. Triage stops after dispatch; implementation and verification belong to the executing agent.
