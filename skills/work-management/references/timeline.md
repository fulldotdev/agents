# Task timeline

A Task body is an append-only, possibly incomplete log of source events. It keeps the facts needed to understand the work, without treating generated interpretation as evidence.

Social-post Tasks may keep an editable Caption, Platform captions, Media, and Publication section above `## Timeline`; see `social-posts`. The Timeline itself stays append-only. New events go inside that section, not into the editable post.

## Format

```md
## Timeline

### <native Notion @date> · [<channel>](<source link>) · <short description>

- Requirements, decisions, constraints, owners, uncertainty, or verification from this source.
```

The Timeline is a dated log of what each source added. One entry per source, newest last. Link the channel to the message, thread, meeting, document, PR, or file. Without a URL, write the shortest reference a tool can reopen, such as `T3 Code · thread <id>` or `Telegram · chat <id> · message <id>`. With nothing to point to, write `source unavailable`.

Keep exact names, IDs, filenames, branches, deadlines, and decisions, and mark uncertainty such as `draft` or `not yet tested`. Write enough to prevent a wrong decision later. The full message or document stays at its source.

## Corrections

Do not edit old entries. Correct a mistake with a new entry that names the old one and says what it replaces. When reading, apply corrections and newer entries before working out the current state.

Store only what a source said. Do not store generated `Next` steps, `Done when` criteria, or summaries; work those out when reading. A handoff brief goes in the work prompt, not in the Task.

Task titles name the work package or the outcome, not every substep. Prefer English unless the work is clearly in Dutch. Keep customer wording literal. A tiny reminder may have an empty body.
