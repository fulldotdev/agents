---
name: t3-code
description: "Use when managing T3 projects or threads, checking Codex or Claude account-pool limits, or installing, updating, linking, or troubleshooting the Otis T3 service and T3 Connect."
---

# T3 Code on Otis

Otis runs the T3 server. Start a T3 thread only when the user asks for one, through the helper below. Delegation without that request goes over the CLI, see `agent-delegation`.

Read [references/setup.md](references/setup.md) when adding, renaming, syncing, or removing projects, or working on the service or T3 Connect.

Read [references/account-pools.md](references/account-pools.md) for how T3 connects to the account pool. The pool itself, its accounts, and usage limits are in [account-pool.md](../../global/references/account-pool.md).

For remaining quota and reset times, use `python3 ~/.agents/skills/t3-code/scripts/pool-usage.py`. Add `--provider claude` or `--provider codex` to narrow the read, and `--json` for structured output. Read the account-pool reference for remote checks and interpretation. Use the API by default; open the dashboard for a requested visual check.

## Dispatch

Use one thread per PR. A Task may have several threads over time; reuse the thread for follow-up work on the same PR.

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

Threads run on the project checkout under `~/projects`. Pass the checkout's current Git branch as `--branch`. Resolve a detached HEAD first. The prompt gives context and limits, not development instructions.

After starting, confirm the thread exists and its state. For a tracked Task, save the T3 reference and checkout information through `work-management`. T3 stores model and session metadata itself.

Triage does not start or continue threads. Starting work needs the user's instruction; this skill adds no permission of its own.
