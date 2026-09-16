# Task timeline

A Task body is an append-only and possibly incomplete log of source events. It keeps the facts needed to understand the work without treating generated interpretation as evidence.

Social-post Tasks may keep editable Caption, Platform captions, Media and publication details before `## Timeline`; use `social-posts`. The Timeline itself remains append-only. Insert new events within that section, not into the editable post.

## Format

```md
## Timeline

*Append-only and possibly incomplete.*

### <native Notion @date> · [<channel>](<primary source>) · <short description>

- Direct requirements, decisions, constraints, owners, uncertainty, or verification.
```

Use a native Notion date in every heading. Link the channel to the main message, thread, meeting, document, PR, or file. The heading is the reference, so do not add a `Refs` section.

Append one event per source. Keep different sources in separate entries. Preserve exact names, filenames, IDs, branches, deadlines, decisions, safety constraints, verification claims, and useful uncertainty such as `draft`, `reported by the PR`, or `not yet tested`. Record changing facts as dated observations.

Keep the full message, transcript, or editable output at its original source. Put enough direct context in the Timeline to prevent a wrong future decision, but do not copy whole conversations or documents.

## Source references

When there is no URL that can open the source again, put the shortest reliable reference in the heading:

- `Telegram · chat <id> · topic <id> · message <id>`
- `Telegram · OpenClaw host <host> · chat <id> · message <id> · ingress event <id>`
- `Codex · host <reachable-host> · thread <uuid> · repo <owner/name> · checkout <branch-or-worktree>`
- `T3 Code · environment <name> · project <id> · thread <id>`
- `<channel> · <shortest reliable reference its tool can open>`

If no source URL or reliable reference exists, use `<channel> · source unavailable` and keep only the direct facts that were captured. A Task cannot cite itself as independent evidence.

## Corrections and generated content

Do not edit existing entries. Correct an error with a new event that identifies the old heading and its Notion block ID or URL. State what it replaces and what remains valid. Apply corrections before deriving the current state.

An authorized migration or repair may replace a known-bad pilot history with an accurate Timeline after the original evidence has been kept and checked.

Work out the current actions and completion conditions when reading. Do not store regenerated `Next`, `Done when`, inferred criteria, context summaries, or combined conclusions without a source.

For a work handoff, write a short current brief from the relevant source events: requested result, open decisions, allowed scope, and review limit. Put the brief and source references in the work prompt. Do not add it to the Task as a second current summary. Apply later corrections before relying on older entries.

Tiny reminders may have a short or empty body. Task titles name the work package or observable outcome, not every substep. Prefer English unless the work is clearly in Dutch. Preserve customer wording literally.
