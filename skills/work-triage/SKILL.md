---
name: work-triage
description: "Use when processing recurring intake from Gmail, Slack, WhatsApp, Calendar, meetings, T3 Code, and Notion into saved context, started work, or draft replies."
---

# Work triage

The runner collects new items into one batch file. For each item: find where it belongs, add missing context, draft a reply when needed, then report. Use `work-management` for all Notion work. Keep triage to intake and routing. When access or a tool fails, retry the item and report the blocker; leave installations, browser repairs, and other tooling work to a separate request.

Read [t3-routing.md](references/t3-routing.md) before starting or continuing a T3 thread.

For a requested quality review, read [assess-quality.md](references/assess-quality.md). Keep that review separate from recurring intake.

## The batch file

Read the batch file named in the prompt once. It contains:

- `items`: new source items since the last run, including the user's outgoing messages and recently settled T3 threads. Outgoing messages can confirm agreements, delivery, or changed plans. Gmail items are thread headers only, so read the thread before deciding. WhatsApp and Slack items include the text. Meeting items contain names, relations, readiness, revision, and source references; fetch the meeting record as described below.
- `retry`: items an earlier run could not finish, with the reason.
- `index`: all open Tasks, Tasks closed today, Projects, Companies, and open T3 threads, with codes, statuses, and URLs. Use it to find the right record.
- `lanes_failed`: sources that could not be collected, with the number of consecutive failures.
- `triage_chat_changed`: when true, first read the user's recent messages in the Triage chat (session `agent:main:telegram:group:-1003914987491`). They can correct earlier triage decisions.

Read more of a source when you need it:

```bash
python3 ~/.agents/skills/work-triage/scripts/collect.py source gmail --thread-id ID --account ACCOUNT [--download]
python3 ~/.agents/skills/work-triage/scripts/collect.py source t3_threads --thread-id ID
python3 ~/.agents/skills/work-triage/scripts/collect.py source slack --query TEXT
```

Use `wacli` for more WhatsApp history, `gog` for Gmail and Calendar, and `ntn` for Notion pages. Collector output is YAML by default; pass `--format json` before parsing it as JSON. Check a command's help after a syntax error instead of trying guessed variants.

## Per item

Handle messages from the same person about the same topic together. Check three things:

1. **What does the source say?** Read the new exchange, including the user's replies. For Gmail read the thread; for Slack read the containing thread; for WhatsApp read the conversation around the new exchange. Expand backwards when a reply, quote, changed agreement, ownership, or completion depends on earlier context. Read the full relevant conversation when that context cannot be resolved. A header or excerpt alone is not enough to decide an actionable item. Open attachments that matter. Transcribe voice messages. If you cannot read something you need, retry the item and say what is missing.
2. **Which record owns it?** Find the Company, Project, Task, or T3 thread in the index. A sender can represent several companies. Match the message's website, product, and topic with the destination; the sender alone is not enough. If nothing matches, search Notion before concluding there is no record. Retry unresolved ownership rather than guessing.
3. **What is already there?** Read the record's Brief, Updates or existing Timeline, and Resources, plus the parent Project's Resources. Compare dated source events with the latest replies and delivery evidence. A stored status or old blocker is not proof of the current situation. Add only context that is missing, including when another agent already recorded this source.

Then take every action that applies. One item may need several.

- **Nothing new.** Move on when the record already has the context or the item needs no tracking: small talk, an FYI, a notification, a question the user already answered.
- **Add context to Notion.** Put a new requirement, feedback, decision, agreement, deadline, file, or link in the Task body or the right Project or Company body. Create a Task, Project, or Company only when `work-management` says so. Resolve people and company relationships through `work-management`.
- **Update status.** After adding context, check the recorded dependency and completion condition. When a requested reply or document arrives, clear that dependency and apply the supported status through `work-management`.
- **Draft a reply.** For a human email with a real open question. Read the thread again right before writing, and skip it if the user already replied. Create or update one Gmail draft with `customer-communication` and `gog`. Keep the user's edits. No placeholders. Never send.
- **Start work.** Start or continue a T3 thread only when `t3-routing.md` allows it. Tell the thread the required outcome and where the context is, not how to develop it.
- **Archive.** Archive a Gmail thread when nothing remains for the user: no reply, decision, payment, or follow-up. A thread with an unsent draft stays in the inbox. Use `gog gmail archive THREAD_ID --thread` with the account.
- **Calendar.** Create, move, or cancel an event only when a source supports it.
- **Cannot finish now.** Add a retry line as described below.

## Attachments

An attachment matters when it can change where work belongs, its scope or price, approval, execution, or completion. View images, transcribe audio, watch only the needed parts of video, and extract text from documents.

- Downloads are scratch files under `~/.cache/fulldev/work-triage/`, not `/tmp`, because the PDF and image tools reject files there. WhatsApp media is already on disk at the path in the item.
- Inspect the original. Make a smaller copy or selected frames only when a tool needs them, and do not rely on a preview for details you cannot read in it.
- When a file defines a requirement, decision, acceptance condition, blocker, or proof of completion, add the full-resolution original or a permanent URL to the right `Resources`, and explain the evidence in the Task update. Other media stays at its source.
- Retry the item when a needed file cannot be read. Mentioning a PDF, CSV, image, or video in an update is not the same as inspecting it. A missing duplicate does not block an outcome that other evidence supports.

## Meetings

Read the meeting page and its complete summary and manual notes first, using `ntn` and `GET v1/pages/{page_id}/markdown`. Check `truncated` and `unknown_block_ids` and fetch any missing content. An index entry or truncated body excerpt is not the summary. Keep every topic, including tentative requests, disagreement, delivery claims, and unanswered questions. Use the meeting date and source wording; let the triage model decide what affects tracked work.

- Read [meeting-summary.md](references/meeting-summary.md) when creating or assessing the factual summary instruction. Until summaries produced with that instruction have been checked against representative full transcripts, use full transcripts for commitment extraction. A generic short recap or action list does not meet it. For older or incomplete summaries, read the full transcript through `GET v1/pages/{page_id}/markdown?include_transcript=true`. A summary cannot prove that something was absent from the meeting.
- Open transcript passages when a speaker, company, scope, date, dependency, contradiction, or tentative commitment is unclear. Verify transcript evidence before recording approval, price or scope acceptance, or completion. Read the full transcript when the needed passage cannot be located or the summary misses discussion coverage. If unavailable, preserve uncertainty and retry the affected item.
- Read linked Tasks and Projects, and plausible active Tasks when relations are missing. Compare facts already recorded by T3 or another triage run before appending. An old Timeline or the words "Full transcript: read" do not establish completeness.
- Route supported commitments, decisions, feedback, and blockers through `work-management`. Leave the summary in Notion's meeting-notes block, without a separate Summary property. Keep the original transcript for verification.

## Report

Return one numbered list in English, starting at the number in the prompt. One line per outcome, in these formats:

```text
12. Task created: [Title](notion-url) · Project or Company
13. Task done: [Title](notion-url) · Doing → Done
14. Task reopened: [Title](notion-url) · Done → Todo · reason
15. Task canceled: [Title](notion-url) · Todo → Canceled
16. Project created: [Name](notion-url) · Company
17. Project: [Name](notion-url) · Planned → In Progress
18. Draft: [Subject or recipient](gmail-url)
19. T3 started: [Title](t3-url)
20. T3 continued: [Title](t3-url)
21. Calendar: [Title](event-url) · Thu 16:00 → Fri 10:00
22. Source failing: Slack, 3 runs. Action: sign in again in Chrome on Otis.
23. Heads-up: Google security alert for info@example.nl · check if the login was you
```

- A Company follows the Project formats. Report a draft when it is new or meaningfully updated.
- Put the link on the title. No IDs or host names.
- End a line with a reason of at most ten words only when the user must act: a deadline, a decision, something not sent.
- `Heads-up` is only for a security alert or an outage the user must act on today and that has no record. Anything else becomes a Task or is dropped.
- Report a failing source after two or more consecutive failed runs. For browser problems, use the access failures in `browser`'s [chrome.md](../browser/references/chrome.md).
- Report nothing else: no routine messages, context appends, archived mail, or no-action decisions.

Items you could not finish go after the list, one line each:

```
RETRY: gmail:1a0a938e523b9652 attachment could not be read; check the PDF
```

Copy the exact `ref` from the batch. Use one line per item, including for several blocked messages from the same source. Keep an unresolved retry until its source was read and handled, or the user explicitly excludes it. The runner returns these with your note in the next run. With nothing to report or retry, return exactly `NO_REPLY`.
