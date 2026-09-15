# Triage Media

Attachments are source context when their contents can change routing, scope, pricing, approval, execution, or completion.

Inspect relevant files according to type: images and screenshots visually, audio through transcription or audio analysis, video through bounded video analysis, and documents through text extraction. Use filenames, MIME types, source context, and the original source ID or link when deciding relevance.

Collector downloads are scratch files under `~/.cache/fulldev/work-triage/` by default (`WORK_TRIAGE_TEMP_DIR` can override it), with a reusable per-account/thread Gmail attachment cache. Each focused Gmail read still refreshes the source; gog reuses files by message/attachment index and expected size. WhatsApp uses its existing exact message media paths. These caches are not durable references. Reuse an available extraction within a run for the same unchanged file. Inspect the original when practical; create a smaller derivative or selected frames when needed by the analysis tool. Analysis derivatives never replace the original, and small previews cannot establish unreadable detail.

When media directly defines a requirement, decision, acceptance condition, blocker, handoff, or completion evidence, preserve the full-resolution original and add it or its durable canonical URL to the owning Company, Project or Task `Resources` property, following `work-management` ownership rules. Retain the original source locator in the Task Timeline when the file is task evidence. Incidental media stays at its reopenable Gmail, Slack, WhatsApp, meeting, or file source.

Report a blocker when material media cannot be inspected or preserved well enough for the pending decision. An unavailable redundant attachment does not block an otherwise evidenced outcome.
