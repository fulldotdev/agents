---
name: work-triage
description: Runs inbound work triage across Gmail, Slack, WhatsApp, calendar, meetings, and Notion capture buckets using live work-management metadata.
---

# Work Triage

Incoming lane only. Always apply `work-management`: Projects = durable buckets. Tasks = small execution items. Sources = Meetings/Gmail/Slack/WhatsApp/Calendar.

## Order

1. Collect lanes.
2. Fetch live Notion metadata for relevant databases.
3. Match/create Project first.
4. Match/create Task only for concrete action.
5. Update Project for scope/agreement/customer/project-state.
6. Move non-executable to Someday.
7. Report real changes only.

## Metadata

For Notion: prefer stable `NOTION_API_KEY`; else active connector/MCP. Always read schema metadata before relying on fields. Bodies via markdown/body API or equivalent.

Known collection IDs are hints only. Prefer current database by name + schema. Use live database/property descriptions, relation targets, and status/select options for schema semantics. Use this skill for collection strategy, matching, write safety, and reporting.

## Lanes

Use available tools: API, CLI, MCP, app connector. Do not assume same integrations in Codex/OpenClaw/cron/desktop.

Default cron window: caller should pass `after`/`before`. If missing: Gmail inbox mode, Notion open work, no time-window claims for comms. Max 200 items/lane unless caller says otherwise. Partial lane failure: continue, report failed lane, do not pretend full triage ran.

### Notion Tasks: Execution Inventory

Fetch current Tasks using live status names.
- Include open statuses; exclude closed statuses.
- Also fetch recently edited closed Tasks for dedupe/closure/no-reopen.
- Sort by Edited/last edited desc if possible.
- Capture url/id, all props, important relations, dates, assignee, and status.
- Read body if changing or matching.
- Existing projectless customer/delivery Task: resolve/create smallest durable Project, link Task, then report.

### Notion Projects: Durable Context

Fetch current active/open Projects using live status names.
- Do not use closed Projects as ordinary match candidates.
- Fetch closed Project only through exact relation/search/history need.
- Capture url/id, all props, relations, target/date, and status.
- Read body only for likely match, relation, or update.
- New execution/admin/follow-up Task must have Project relation when customer/delivery related.

### Meetings: Source Material

Fetch meeting pages created/edited in window.
- Filter by Created or Edited inside cron window when available.
- Capture url/id, title, edited time, relations, calendar/source URL if any.
- Read body + transcript/summary. Long transcript: summary + action-relevant passages first.
- Convert decisions/commitments/actions to Project update or concrete Task.
- Meeting page is not work bucket.

### Gmail: Inbox/Thread Context

Fetch configured accounts/mailboxes.
- Modes: inbox mode = `in:inbox`; window mode = `after:YYYY/MM/DD before:YYYY/MM/DD`; custom query if caller provides one.
- Per thread: full messages, labels, from/to/cc/bcc, date, subject, plain text, attachments, thread id/link.
- Track: in-window, in inbox, unread, archived, Sil replied.
- Attachments: filename, MIME, size, saved path/source URL.
- Keep in inbox if concrete ask, scheduling, approval, unanswered customer/vendor, reply-needed.
- Archive only clearly safe + no reply needed.

### Slack: Mentions/DMs/Threads

Fetch window context.
- Fetch `from:me`, explicit user mentions, DMs/MPIMs in window.
- Sent: include surrounding history + thread replies.
- Mentions: require explicit user mention if possible; broad name matches are noise.
- DMs: include nearby history + replies.
- Capture team, channel id/name/type, ts, sender id/name, text, permalink, files, thread, surrounding, Sil participation.
- Input only unless user asks to send.

### WhatsApp: Inbound Chats/Media

Fetch window messages.
- Require `after`/`before`; if absent, skip and report missing window.
- Group by chat.
- Capture chat name/id, msg id, sender, timestamp, text/display/snippet, message/media kind.
- Media: type, display text, saved paths/source refs.
- Preserve chronological order.
- Input only unless user asks to send.

### Calendar: Prep/Follow-up Signals

Fetch events in window per account.
- Require `after`/`before`; if absent, skip and report missing window.
- Capture id, iCalUID, title, description, location, status, type, link, start/end, created/updated, organizer, creator, attendees, source calendar.
- Use for prep, follow-up, customer/project context, meeting links.
- Create Task only for concrete prep/follow-up.

## Cron Contract

- Inputs: `after`, `before`, optional lane/account/customer/project filters.
- Window is half-open when tool supports it: `after <= item < before`.
- Required lanes for full cron triage: Notion Tasks, Notion Projects, Gmail. Other lanes best-effort unless caller requires them.
- On auth/tool failure: continue other lanes; report `Failed: lane - reason`; do not write changes based on missing required lane.
- Before any write: re-read target page properties/body.
- After write: verify status/relation/body changed or report failure.
- If any required write fails, report blocker; do not claim task/project handled.
- Output: one numbered list; include writes, archives, failed lanes, blockers. No internal run paths.

## Matching/Writes

- Dedupe before write: source, Project, Task, fact, link, status.
- Match Project first. Create compact Project if real work lacks one.
- Link Project to Customer when identifiable.
- Do not create Task if concrete action already exists.
- Once an item is understood, route out of triage status using live status options.
- Strong source evidence may close concrete work only when safe and allowed.
- Real schema names only. No hallucinated fields.
- Read body before interpreting/changing. Never blind append.
- Do not paste full transcripts, duplicate Project scope in Tasks, overwrite execution/review top sections, or edit autogenerated summary fields.

## Body Placement

- Project body: durable outcome, scope/agreements, current context, delivery notes, source links, main refs. Loose structure; do not force sections.
- Task body: work-triage/work-management additions are compact dated trace/context. Do not overwrite work-execution top sections.
- Prefer mentions, links, dates, people, concise trace over copied transcripts.

## Safety

- Gmail: never archive reply-needed threads.
- Gmail: archive only safe, no reply needed, currently inbox.
- Slack/WhatsApp: never send/hide/archive unless explicit.
- Never send Gmail/Slack/WhatsApp replies unless explicit.

## Report

- One concise numbered list.
- Include only net-new writes, real status changes, new refs, action-relevant facts.
- Suppress rediscovered facts/already-archived sources.
- Nothing changed -> say so.

## Examples

- Customer email adds scope -> update Project, create Task only for concrete next action.
- Vague captured idea -> Someday, not Task.
