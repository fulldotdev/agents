---
name: t3-code
description: "Use when inspecting, creating, resuming, or settling T3 agent threads on Otis, or installing, updating, linking, or troubleshooting the Otis T3 service and T3 Connect."
license: MIT
---

# T3 Code on Otis

Otis runs the authoritative T3 server and provider processes. T3 Connect makes managed threads visible on the signed-in MacBook and mobile clients. It does not start work. OpenClaw starts work through the authenticated local helper.

Use T3-managed threads when work must be visible across devices. T3 does not automatically import a standalone provider resume such as `codex exec resume`.

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
  --prompt "Read <Task URL> and complete the authorized work within Sil's stated scope."

python3 ~/.agents/skills/t3-code/scripts/t3_dispatch.py resume \
  --thread-id <thread-id> \
  --prompt "Read <Task URL> and <new source>. Continue the authorized work within Sil's stated scope."
```

The helper creates a thread before starting its first turn. It supports settle and unsettle operations and defaults to `gpt-6-astra`, high reasoning, and full access. When a task needs different settings, override them with `T3_DEFAULT_MODEL`, `T3_DEFAULT_REASONING_EFFORT`, `--model`, `--reasoning-effort`, or `--runtime-mode`.

## Triage integration

For automatic triage, use `work-triage` and its [conditions for starting work](../work-triage/references/t3-routing.md). That reference defines source updates, authorization, and handoff requirements. This tool skill grants no additional permission to start work.

Use the compact T3 index or `status` to check the current state and pending requests. Do not duplicate a running turn. When Sil has supplied a requested approval or answer, pass it through T3's supported response mechanism and continue the authorized work. Otherwise, leave the request pending. A stopped, ready, or settled thread may be resumed directly when the requested work is authorized.

The executing thread selects its own applicable skills. Dispatch prompts carry the task context and authorization, not development instructions. Inspect Git in the target checkout and pass its current branch through the required `--branch` argument. Resolve a detached HEAD before creating a thread. Do not invent a branch.

After starting work, confirm the expected thread and its state. For a tracked Task, save its T3 reference and relevant checkout information through `work-management`. T3 already stores model and session metadata. Triage stops after starting the thread. The executing agent handles implementation and verification.
