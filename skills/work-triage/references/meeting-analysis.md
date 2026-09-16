# Meeting transcript analysis

Use this process once for each new transcript revision marked `transcript_ready` by the Meetings collector.

You may use a read-only local subagent when a long transcript would crowd the triage context. Give it the meeting ID and revision, linked records, and relevant source references. Direct analysis is also fine. Never place meeting context from the Notion summary alone.

## Context

The analysis reads:

- the complete transcript from `GET v1/pages/{page_id}/markdown?include_transcript=true`;
- the current properties and body of linked Tasks and Projects;
- linked Company context when it changes where the meeting belongs;
- the full body of plausible active Tasks found from the transcript when relations are missing;
- a prior meeting, source message, or T3 thread only when the transcript relies on it or it can change where the context belongs.

Keep lookup focused on the meeting's subjects. Do not scan broad mail, chat, repository, or company history.

## Result

Return the meeting ID and revision. Include commitments, decisions, feedback, and blockers that affect the work, with source references, likely records, and recommendations for where they belong. State uncertainty about speakers, ownership, and scope. Do not treat a possible commitment as confirmed.

Triage applies `work-management`, performs writes, and decides whether the result meets the conditions for starting T3 work. A delegated analyst returns findings only.

Meeting summaries live in Notion's meeting-notes block. Do not recreate a separate Summary property.
