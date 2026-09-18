---
name: work-triage
description: "Use when processing recurring intake from Gmail, Slack, WhatsApp, Calendar, meetings, T3 Code, and Notion into saved context, started work, or draft replies."
---

# Work triage

The runner collects new items into one batch file. For each item: find where it belongs, add missing context, draft a reply when needed, then report. Use `work-management` for all Notion work.

Read [t3-routing.md](references/t3-routing.md) before starting or continuing a T3 thread.

## The batch file

Read the batch file named in the prompt once. It contains:

- `items`: new source items since the last run. Gmail items are thread headers only, so read the thread before deciding. WhatsApp and Slack items include the text. The user's own messages are not items, but you see them when you read the thread.
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

Use `wacli` for more WhatsApp history, `gog` for Gmail and Calendar, and `ntn` for Notion pages.

## Per item

Handle messages from the same person about the same topic together. Check three things:

1. **What does the source say?** Read the whole thread or chat, including the user's replies. Open attachments that matter. Transcribe voice messages. If you cannot read something you need, retry the item and say what is missing.
2. **Which record owns it?** Find the Company, Project, Task, or T3 thread in the index. Match on sender and topic, not on a similar name. If nothing matches, search Notion before concluding there is no record.
3. **What is already there?** Read the record's body, Timeline, and Resources, plus the parent Project's Resources. The Task may not have this message yet.

Then take every action that applies. One item may need several.

- **Nothing new.** Move on when the record already has the context or the item needs no tracking: small talk, an FYI, a notification, a question the user already answered.
- **Add context to Notion.** Put a new requirement, feedback, decision, agreement, deadline, file, or link in the Task Timeline or the right Project or Company body. Create a Task, Project, or Company only when `work-management` says so. Send contact details to Dex through `dex-skill`.
- **Draft a reply.** For a human email with a real open question. Read the thread again right before writing, and skip it if the user already replied. Create or update one Gmail draft with `customer-communication` and `gog`. Keep the user's edits. No placeholders. Never send.
- **Start work.** Start or continue a T3 thread only when `t3-routing.md` allows it. Tell the thread the required outcome and where the context is, not how to develop it.
- **Archive.** Archive a Gmail thread when nothing remains for the user: no reply, decision, payment, or follow-up. A thread with an unsent draft stays in the inbox. Use `gog gmail archive THREAD_ID --thread` with the account.
- **Calendar.** Create, move, or cancel an event only when a source supports it.
- **Cannot finish now.** Add a retry line as described below.

## Attachments

An attachment matters when it can change where work belongs, its scope or price, approval, execution, or completion. View images, transcribe audio, watch only the needed parts of video, and extract text from documents.

- Downloads are scratch files under `~/.cache/fulldev/work-triage/`, not `/tmp`, because the PDF and image tools reject files there. WhatsApp media is already on disk at the path in the item.
- Inspect the original. Make a smaller copy or selected frames only when a tool needs them, and do not rely on a preview for details you cannot read in it.
- When a file defines a requirement, decision, acceptance condition, blocker, or proof of completion, add the full-resolution original or a permanent URL to the right `Resources`, and reference the source in the Task Timeline. Other media stays at its source.
- Retry the item when a needed file cannot be read. A missing duplicate does not block an outcome that other evidence supports.

## Meetings

Analyze each new transcript revision marked `transcript_ready` once. Read the full transcript from `GET v1/pages/{page_id}/markdown?include_transcript=true`, never the Notion summary alone. A read-only subagent may do this for a long transcript.

- Also read the linked Tasks and Projects, the linked Company when it changes where the meeting belongs, and plausible active Tasks when relations are missing. Read an earlier meeting, message, or T3 thread only when the transcript depends on it.
- Take out the commitments, decisions, feedback, and blockers that affect work, each with its source and the record it belongs to. A possible commitment is not a confirmed one. Say when speakers, ownership, or scope are unclear.
- Then route them like any other item. The summary stays in Notion's meeting-notes block, without a separate Summary property.

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

The runner returns these with your note in the next run. With nothing to report or retry, return exactly `NO_REPLY`.
