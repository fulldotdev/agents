# Meeting summaries

Notion records and transcribes the meeting. Its [Meeting summary instructions](https://app.notion.com/p/3935979e268c8087beecd5ff5c1ebc10) produce only `Transcript available. Astra summary pending.` Keep that placeholder instruction as the default. The triage run creates the final summary.

## Read and write once

Read the complete source snapshot, which excludes Notion's summary. Use the transcript as evidence of what was said. Keep manual notes and preparation separate from spoken discussion. Use confirmed participant and company context to resolve names. Generate the summary and route supported follow-ups from this same reading.

Write in the meeting's main language. Start with `Meeting summary · YYYY-MM-DD`, using the generation date. Use a short heading for each topic and clear paragraphs or bullets. Keep all distinct topics, requirements, alternatives, decisions, conditions, unresolved questions and closing corrections. Remove filler and repetition. Preserve dates, amounts, versions and relevant examples. Keep proposals, tentative ownership, claimed delivery and confirmed acceptance distinct. Mark ambiguous wording instead of supplying a plausible meaning. Include a short source quote or link when an important qualification needs it; avoid repeated citations on every sentence.

Before saving, compare the draft with the source already in context. Check topic coverage, qualifications, speaker attribution, dates, amounts and later corrections. Aim for a useful reduction, without a fixed length target. A short meeting may not need much compression. Separate information learned from linked records from the meeting itself.

Save the summary Markdown to a local file, then run:

```bash
python3 ~/.agents/skills/work-triage/scripts/meeting_summary.py save PAGE_ID --file SUMMARY.md --source-fingerprint FINGERPRINT
```

Use `content_fingerprint` from the collected item, or `source_fingerprint` from the helper's `read` command. The save command checks the current source, replaces only the existing Summary tab and reads the result back. It does not expose the old summary to the model. If the source changed, read the refreshed source and revise the draft. Retry the meeting if saving or verification fails. Successful summary writes leave the source fingerprint unchanged.

## Reuse

For later context, read the saved meeting summary and relevant manual notes first. Open original passages when attribution, scope, price, approval, delivery, dates or uncertainty matter to a new action. Read the full transcript when the summary is absent, outdated or insufficient, and during the weekly source-to-Notion audit. A summary does not prove a topic was absent. Regenerate after source changes; editing only the generated summary is not new intake.
