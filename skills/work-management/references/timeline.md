# Task timeline

A Task body is an append-only, possibly incomplete log of source events. It keeps the facts needed to understand the work, without treating generated interpretation as evidence.

Social-post Tasks may keep an editable Caption, Platform captions, Media, and Publication section above `## Timeline`; see `social-posts`. The Timeline itself stays append-only. New events go inside that section, not into the editable post.

## Format

```md
## Timeline

*Append-only and possibly incomplete.*

### <native Notion @date> · [<channel>](<primary source>) · <short description>

- Direct requirements, decisions, constraints, owners, uncertainty, or verification.
```

Every heading has a native Notion date. Link the channel to the main message, thread, meeting, document, PR, or file. The heading is the reference, so there is no `Refs` section.

One event per source, and different sources in separate entries. Keep exact names, filenames, IDs, branches, deadlines, decisions, safety constraints, verification claims, and useful uncertainty such as `draft`, `reported by the PR`, or `not yet tested`. Record changing facts as dated observations.

The full message, transcript, or editable output stays at its source. Put enough direct context in the Timeline to prevent a wrong decision later, but do not copy whole conversations or documents.

## Source references

When no URL can reopen the source, put the shortest reliable reference in the heading:

- `Telegram · chat <id> · topic <id> · message <id>`
- `Telegram · OpenClaw host <host> · chat <id> · message <id> · ingress event <id>`
- `Codex · host <reachable-host> · thread <uuid> · repo <owner/name> · checkout <branch-or-worktree>`
- `T3 Code · environment <name> · project <id> · thread <id>`
- `<channel> · <shortest reliable reference its tool can open>`

With no URL or reliable reference, use `<channel> · source unavailable` and keep only the direct facts. A Task cannot cite itself as evidence.

## Corrections and generated content

Do not edit existing entries. Correct an error with a new event that names the old heading and its Notion block ID or URL, says what it replaces, and what still holds. Apply corrections before working out the current state.

An approved migration or repair may replace a known-bad history with an accurate Timeline once the original evidence is kept and checked.

Work out current actions and completion conditions when reading. Do not store regenerated `Next`, `Done when`, inferred criteria, context summaries, or conclusions without a source.

For a handoff, write a short brief from the relevant events: the requested result, open decisions, allowed scope, and review limit. Put it in the work prompt with source references, not in the Task as a second summary. Apply later corrections before relying on older entries.

Tiny reminders may have a short or empty body. Task titles name the work package or the observable outcome, not every substep. Prefer English unless the work is clearly in Dutch. Keep customer wording literal.
