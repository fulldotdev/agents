# Meeting transcript analysis

Use this flow once for every new transcript revision marked `transcript_ready` by the Meetings collector.

Use a read-only local subagent when a long transcript would crowd the triage context. Give it the meeting ID and revision, linked records, and relevant source locators. Direct analysis is also fine. Do not route a meeting from the native Notion summary alone.

## Context

The analysis reads:

- the complete transcript from `GET v1/pages/{page_id}/markdown?include_transcript=true`;
- the current properties and body of linked Tasks and Projects;
- linked Company context when it affects ownership or routing;
- the full body of plausible active Tasks found from the transcript when relations are missing;
- a prior meeting, source message, or T3 thread only when the transcript relies on it or it can change the routing decision.

Keep lookup focused on the meeting's subjects. Do not scan broad mail, chat, repository, or company history.

## Result

Return the meeting ID and revision, material commitments, decisions, feedback and blockers with source locators, likely owning records, and routing recommendations. Keep speaker, ownership and scope uncertainty explicit; a possible commitment remains a candidate.

Triage applies `work-management`, performs writes, and decides whether the result meets the T3 dispatch gate. A delegated analyst only returns findings.

After routing, triage may update the Meeting `Summary` property with a concise index of the material outcome and what would justify opening the transcript. This helps later agents choose what to read; it is not evidence and does not replace the transcript.
