# Task timeline

A Task body is an append-only, possibly incomplete log of source events. It keeps the facts needed to understand the work without storing generated interpretation as evidence.

## Format

```md
## Timeline

*Append-only and possibly incomplete.*

### <native Notion @date> — [<channel>](<primary source>) — <short description>

- Direct requirements, decisions, constraints, owners, uncertainty, or verification.
```

Use a native Notion date in every heading. Link the channel to the main message, thread, meeting, document, PR, or file. The heading is the reference, so do not add a `Refs` section.

Append one event per source. Keep different sources in separate entries instead of combining them. Preserve exact names, filenames, IDs, branches, deadlines, decisions, safety constraints, verification claims, and useful uncertainty such as `concept`, `reported by the PR`, or `not yet tested`. Write changing facts as dated observations.

Keep the full message, transcript, or mutable artifact at its canonical source. Put enough direct context in the Timeline to prevent a wrong future decision, but do not copy whole conversations or documents.

## Stable locators

When a reopenable URL is unavailable, put the smallest stable locator in the heading:

- `Telegram · chat <id> · topic <id> · message <id>`
- `Telegram · Hermes host <host> · profile <profile> · session <session-id> · message <id>`
- `Codex · host <reachable-host> · thread <uuid> · repo <owner/name> · checkout <branch-or-worktree>`
- `T3 Code · environment <name> · project <id> · thread <id>`
- `<channel> · <smallest stable locator its resolver can reopen>`

If no source URL or stable locator exists, use `<channel> · source unavailable` and preserve only the direct facts actually captured. A Task cannot cite itself as independent evidence.

## Corrections and generated content

Do not edit existing entries. Correct an error with a new event that identifies the old heading and its Notion block ID or URL. State what it replaces and what remains valid. Apply corrections before deriving the current state.

An authorized migration or repair may replace a known-bad pilot history with a clean, source-faithful Timeline after the underlying evidence is preserved and verified.

Derive current actions and completion conditions when reading. Do not store regenerated `Next`, `Done when`, inferred criteria, context summaries, or uncited synthesis. Notion generates the `Summary` property. Never edit it manually or treat it as evidence.

Tiny reminders may have a short or empty body. Task titles name the work package or observable outcome, not every substep. Prefer English unless the work is clearly in Dutch. Preserve customer wording literally.
