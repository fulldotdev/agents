# Task body

Use a short current Brief and dated Updates. The Brief helps a person or agent understand the work without rebuilding its history. Updates preserve the evidence. Either may be incomplete: read the new source and current record before changing anything. T3 and triage use this same format.

## Format

```md
## Brief

Show review stars only after five published reviews. Apply the rule to product cards and product pages, as requested in [Slack feedback](https://example.com/feedback).

The existing widget stays in use. Whether historical imported reviews count is still unanswered.

## Updates

### 23 September 2026 · [Slack](https://example.com/feedback) · Review threshold

The customer requested a minimum of five published reviews. They asked whether imported reviews count; no answer was recorded.
```

Write the Brief from supported sources: the current agreed outcome, requirements, constraints, and unresolved questions. Link the evidence. Keep a request or proposal explicitly unconfirmed until a source confirms it. Put actual task status, ownership, dates, and Sprint in properties. Omit empty sections and a Brief that would merely repeat the title. A tiny reminder may have an empty body.

Update the Brief when the agreement changes. Preserve details that still apply. Never invent next steps, acceptance criteria, owners, or commitments to fill the format. Put project-wide context in the Project and link it instead of copying it into every Task.

## Updates and corrections

Append only meaningful new requirements, feedback, decisions, progress, delivery, blockers, or verification. Use the event's date, newest entry last, and a source link. Preserve exact names, IDs, filenames, branches, deadlines, amounts, qualifications, and uncertainty. Keep incoming requirements distinct from implementation evidence. The full conversation stays at its source.

Without a URL, use a reference a tool can reopen, such as `T3 Code · thread <id>` or `Telegram · chat <id> · message <id>`. If unavailable, state that. Use a native Notion date mention when supported.

Before appending, check whether T3, triage, or the user already saved the same fact. A stored source link alone does not prove its contents were handled. Compare meaning and dates, including later replies and corrections. Preserve old entries; correct a mistake with a new entry naming what it replaces, and update the Brief to the corrected facts.

Keep an existing `Timeline` as the Updates section rather than renaming it or creating a second log. Add a Brief to an existing Task only when the active work benefits from it, after checking the sources. Never rewrite the backlog just to apply this format.

Social-post Tasks keep their editable Caption, Platform captions, Media, and Publication sections as `social-posts` describes. Preserve those sections and their existing Timeline. Add a Brief only for work context those sections do not already cover.

## Files and writing

Use `Resources` for named reusable files and links, following `work-management`. In an Update, link the relevant resource and explain what it establishes. Show an image or video in the body when seeing it there helps understand the requirement or evidence; reuse the same saved original instead of uploading a second copy. Preserve existing body attachments.

Use `ntn` and the Notion Markdown API. Read the current body immediately before editing, then use targeted `update_content` changes to the Brief and the end of Updates or Timeline. Preserve other sections and concurrent edits. Read back the changed body and properties. An API success response alone does not verify the saved content.

Task titles name the work package or outcome. Pick one language per Task: English or the customer's language. Keep customer wording literal.
