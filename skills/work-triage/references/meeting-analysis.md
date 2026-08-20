# Meeting transcript analysis

Use this flow once for every new transcript revision marked `transcript_ready` by the Meetings collector.

## Isolation

Keep the full transcript out of the continuing heartbeat conversation. Delegate one read-only local analysis per meeting. Pass the meeting page ID, title, transcript revision, linked Company, Project, and Task IDs, plus plausible T3 thread locators from the compact index. The delegated analysis fetches its own source material and returns only its findings.

If delegation is unavailable, perform the same work in a separate focused context. Do not route a meeting from the native Notion summary alone.

## Context

The analysis reads:

- the complete transcript from `GET v1/pages/{page_id}/markdown?include_transcript=true`;
- the current properties and body of linked Tasks and Projects;
- linked Company context when it affects ownership or routing;
- the full body of plausible active Tasks found from the transcript when relations are missing;
- a prior meeting, source message, or T3 thread only when the transcript relies on it or it can change the routing decision.

Keep lookup focused on the meeting's subjects. Do not scan broad mail, chat, repository, or company history.

## Result

Return a compact source-grounded assessment with:

- the meeting ID and transcript revision;
- explicit Sil-owned commitments, decisions, customer feedback, blockers, deadlines, external commitments, and context-only facts;
- a short evidence quote or transcript locator for every material finding;
- the likely existing Task or Project, when supported;
- uncertainty about the speaker, owner, scope, or intended outcome;
- a one- or two-sentence candidate for the Meeting `Summary` property;
- a routing recommendation, without writing records, dispatching T3, or preparing external communication.

Separate explicit statements from interpretation. A possible commitment stays a candidate when speaker identity or ownership is unclear. The parent heartbeat applies `work-management`, performs writes, and decides whether the result meets the T3 dispatch gate.

After routing, the parent may update the existing Meeting `Summary` property with the candidate. Keep it to two sentences and make it useful as a routing index: name the meeting's material outcome and say what would justify opening the transcript. This property helps later agents choose what to read; it is not evidence and does not replace the transcript.
