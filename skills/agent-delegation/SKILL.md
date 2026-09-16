---
name: agent-delegation
description: Use when a task needs extensive reading of code, logs, documents, or tool output, independent research in parallel, or a second model to clean up or verify code.
---

# Agent delegation

Keep the main thread for requirements, decisions, edits that need the whole conversation, and the final answer. Delegate work whose raw output will not be needed again.

## When to delegate

- Reading or searching likely to exceed about 30k tokens: mapping code paths, logs, long docs, large CLI or API output.
- Independent questions that can run in parallel.
- Cleanup or verification by a model with different strengths.

Read a known file or make a single lookup directly. Keep customer-facing judgment and closely linked steps in the main thread when a handoff would lose context. Each subagent starts with about 25k to 30k tokens of setup.

## Models

For OpenClaw operations, use native `sessions_spawn` with the caller's inherited model (normally GLM) and high thinking. Switch models through a CLI only when Sil explicitly asks. The choices below apply to development work in T3, Codex, or Claude.

- **Fable 5.1** (`claude-fable-5-1`): usually best at clean, mergeable code and refactors.
- **Astra** (`gpt-6-astra`): usually best at tool, browser and computer use, and at validating work end to end.
- **Opus 5** (`claude-opus-5`) and **Sol** (`gpt-5.6-sol`): same-provider subagents for exploration and clear implementation.
- Never use Sonnet as a subagent.
- Reasoning: medium for exploration and implementation, high for complex logic, security and review.

## Same provider

- Codex: call `spawn_agent` with `model: gpt-5.6-sol` and `reasoning_effort: medium`, and set `fork_turns` to `"none"` or a small number so the overrides apply. Use Astra high for reviews.
- Claude: use the Agent tool with `model: opus` for exploration and implementation, and the main model for reviews.

## Cross provider

- Fable from Codex, to clean up a finished change, then verify it yourself:
  `claude -p --model claude-fable-5-1 --permission-mode acceptEdits "TASK"`
- Astra from Claude, for validating changes with shell tools, then review its findings:
  `codex exec --skip-git-repo-check -m gpt-6-astra -o /tmp/NAME.md "TASK"`
- Headless `codex exec` has no browser or computer use. For those checks, ask Sil to run them in a T3 Codex thread.

Run long jobs in the background. If `codex exec` hits a usage limit, retry with `CODEX_HOME=~/.codex-t3/codex-1`, then `~/.codex-t3/codex-2`, then `~/.codex-t3/codex-5` (other accounts). If a CLI is still not logged in or out of usage, say so instead of switching models silently.

## Brief and return

Give each subagent the goal, scope, paths, permission to edit or read only, and expected output. Ask for findings with exact paths, lines, commands or URLs, plus anything it did not check. Aim for under 300 words unless more detail is needed. Never let two agents edit the same files at once. Check key claims before acting on them.
