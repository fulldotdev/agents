# Meeting transcript analysis

Do this once for each new transcript revision marked `transcript_ready` by the Meetings collector.

A read-only local subagent may do the analysis when a long transcript would crowd the triage context. Give it the meeting ID and revision, the linked records, and the relevant source references. Direct analysis is fine too. Never place meeting context from the Notion summary alone.

## Context

Read:

- the full transcript from `GET v1/pages/{page_id}/markdown?include_transcript=true`;
- the properties and body of linked Tasks and Projects;
- linked Company context when it changes where the meeting belongs;
- the full body of plausible active Tasks found from the transcript when relations are missing;
- a prior meeting, source message, or T3 thread only when the transcript depends on it or it changes where the context belongs.

Stay on the meeting's subjects. Do not scan broad mail, chat, repository, or company history.

## Result

Return the meeting ID and revision with the commitments, decisions, feedback, and blockers that affect the work, each with source references, likely records, and where it should go. Say when you are unsure about speakers, ownership, or scope. A possible commitment is not a confirmed one.

Triage then applies `work-management`, does the writes, and decides whether T3 work may start. A delegated analyst returns findings only.

Meeting summaries live in Notion's meeting-notes block. Do not add a separate Summary property.
