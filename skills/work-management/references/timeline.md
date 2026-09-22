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

Use `ntn` and the Notion Markdown API for body changes. Append to the Timeline with a targeted `update_content` operation against its freshly read ending, with a blank line before the new heading. Avoid replacing the whole page to add an event. Read back the changed section and any changed properties. An API success response alone does not verify the saved content.

Keep exact names, IDs, filenames, branches, deadlines, and decisions, and mark uncertainty such as `draft` or `not yet tested`. Write enough to prevent a wrong decision later. The full message or document stays at its source.

## Corrections

Do not edit old entries. Correct a mistake with a new entry that names the old one and says what it replaces. When reading, apply corrections and newer entries before working out the current state.

Store only what a source said. Do not store generated `Next` steps, `Done when` criteria, or summaries; work those out when reading. A handoff brief goes in the work prompt, not in the Task.

Task titles name the work package or the outcome, not every substep. Pick one language per Task: English, or the customer's language. Keep customer wording literal. A tiny reminder may have an empty body.
