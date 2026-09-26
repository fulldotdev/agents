---
name: agent-delegation
description: Use when delegating work to a subagent, another model, or another CLI. Explains how to pick the model, start it, brief it, and use its result.
---

# Agent delegation

## Models

- **Fable 5.1** (`claude-fable-5-1`): usually best at clean, mergeable code and refactors.
- **Astra** (`gpt-6-astra`): usually best at tool, browser and computer use, and at validating work end to end.
- **Opus 5** (`claude-opus-5`) and **Sol** (`gpt-5.6-sol`): same-provider subagents for exploration and clear implementation.
- Never use Sonnet as a subagent.
- Reasoning: medium for exploration and implementation, high for complex logic, security and review.

## Same provider

- Codex: call `spawn_agent` with `model: gpt-5.6-sol` and `reasoning_effort: medium`, and set `fork_turns` to `"none"` or a small number so the overrides apply. Use Astra high for reviews.
- Claude: use the Agent tool with `model: opus` for exploration and implementation, and the main model for reviews.

## Cross provider

Delegate over the CLI, in the background, from the current session. Start a T3 thread only when the user asks for one or will read and work in it themselves.

- Fable from Codex, to clean up a finished change, then verify it yourself:
  `claude -p --model claude-fable-5-1 --permission-mode acceptEdits "TASK"`
- Astra from Claude, for validating changes with shell tools, then review its findings:
  `codex exec --skip-git-repo-check -m gpt-6-astra -o /tmp/NAME.md "TASK"`
- Both CLIs go through the local account pool. "Out of usage" means every pooled account is exhausted; say so instead of switching models silently.

Run long jobs in the background.

## Brief and return

Give each subagent the goal, scope and paths, whether it may edit, and the expected output. Ask it to return findings with exact file paths, lines, commands or URLs, plus what it did not check, in under about 300 words unless more is needed. Never let two agents edit the same files at once.
