---
name: work-triage
description: Runs inbound work triage across Gmail, Slack, WhatsApp, calendar, meetings, and Notion capture buckets using live work-management metadata.
---

# Work Triage

Incoming lane only. Always apply `work-management`: Projects = durable buckets. Tasks = small execution items. Sources = Meetings/Gmail/Slack/WhatsApp/Calendar.

## Order

1. Collect lanes.
2. Fetch live Notion metadata for relevant databases.
3. Match Customer first when identifiable.
4. Create Project only when the work is durable/project-shaped.
5. Match/create Task only for concrete action.
6. Link every customer-related Task directly to Customer, and to Project only when project context is warranted.
7. Move non-executable to Someday.
8. Report real changes only.

## Metadata

For Notion: prefer official `ntn` CLI with local login; use `NOTION_API_TOKEN` only for headless runs. Always read schema metadata before relying on fields. Bodies via markdown/body API or equivalent.

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
- Existing customer/delivery Task without direct Customer: fill the direct Customer relation when identifiable, even if Project is already linked. Create/link Project only when the Task belongs to a durable project, retainer, sprint, delivery scope, or multi-step work package.

### Notion Projects: Durable Context

Fetch current active/open Projects using live status names.
- Do not use closed Projects as ordinary match candidates.
- Fetch closed Project only through exact relation/search/history need.
- Capture url/id, all props, relations, target/date, and status.
- Read body only for likely match, relation, or update.
- New customer-related execution/admin/follow-up Task must link directly to Customer when identifiable. Project is optional and only for durable project context.
- Create Project only for durable context: scoped delivery, retainer/sprint, proposal/contract package, recurring work, multi-task effort, repository/site/app context, or customer work that needs ongoing project state.

### Meetings: Source Material

Fetch meeting pages created/edited in window.
- Filter by Created or Edited inside cron window when available.
- Capture url/id, title, edited time, relations, calendar/source URL if any.
- Read body + transcript/summary. Long transcript: summary + action-relevant passages first.
- Suffix vague/default meeting note titles with useful context when the source clearly supports it, preferably customer/project + topic; preserve the existing title/date/time instead of replacing it unless the title is empty or unusable.
- Fill Meeting note relation fields whenever identifiable from title/body/calendar/source context: Customer(s), Project(s), and concrete Task(s). Prefer existing related pages; create Customers/Projects/Tasks only under the normal triage rules below.
- Convert decisions/commitments/actions to Customer update, Project update, or concrete Task based on scope.
- Meeting page is not work bucket.

### Gmail: Inbox/Thread Context

Fetch configured accounts/mailboxes.
- Account meaning:
  - `sil@full.dev` = zakelijke mailbox.
  - `silveltman@gmail.com` = persoonlijke mailbox.
- `sil@smallgiants.nl` is forwarded/centralized into `sil@full.dev`; do not check it as a separate Gmail account by default.
- Use labels on `sil@full.dev` when available to distinguish source/context, e.g. `Account/Full.dev`, `Account/Smallgiants`.
- Always check these two Gmail accounts unless caller explicitly narrows scope:
  - `sil@full.dev`
  - `silveltman@gmail.com`
- Use `sil@smallgiants.nl` Gmail OAuth/API only as fallback/verification when forwarding/labels look broken or caller explicitly requests it.
- If one account auth/token fails, continue the other account and report the failed account by email address.
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
- WhatsApp is special: sync actionable messages and needed media refs/paths into Notion, because not every agent/runtime has WhatsApp access.
- Require `after`/`before`; if absent, skip and report missing window.
- If `wacli doctor` reports the default store locked by an active `wacli sync --follow --download-media`, do not stop it and do not start another sync/backfill against that store. Use read-only `chats list` / `messages list/search/show/context` and local store paths when possible; report blocked only if the needed data is unavailable.
- For window triage, use `wacli messages list --after <date> --before <date> --json`; do not call `wacli messages search ""` because empty queries fail.
- Use `wacli messages context --chat <jid> --id <msgid> --json` for nearby context when a message looks actionable.
- Group by chat.
- Capture chat name/id, msg id, sender, timestamp, text/display/snippet, message/media kind.
- Media: first capture metadata from the message and prefer the already-downloaded local file (`LocalPath`/`DownloadedAt` in wacli JSON, or `local_path`/`downloaded_at` in `wacli.db`; usually under `<store>/media/...`) when sync is running with `--download-media`. If the message is synced but the local path is missing and the file is needed, use `wacli --read-only media download --chat <jid> --id <msgid> --output <dir> --json` with an explicit output path; otherwise wait for/background sync. Do not stop `sync --follow --download-media` for triage media.
- Preserve chronological order.
- Input only unless user asks to send.

### Calendar: Prep/Follow-up Signals

Fetch events in window per configured account/calendar.
- Require `after`/`before`; if absent, skip and report missing window.
- Default account setup:
  - Use `sil@full.dev` as the zakelijke Calendar OAuth account.
  - `gog calendar events --account sil@full.dev ...` only returns the primary `sil@full.dev` calendar.
  - Fetch `sil@full.dev` and the visible shared `sil@smallgiants.nl` calendar as separate calendar IDs under the same `sil@full.dev` account.
  - Use `silveltman@gmail.com` for personal calendar.
  - Do not check `sil@smallgiants.nl` as a separate Calendar OAuth account by default; use it only as fallback/verification when the shared calendar is missing or unreadable.
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
- Output: one compact numbered list; include writes, archives, drafts, failed lanes, blockers. No internal run paths.

## Matching/Writes

- Dedupe before write: source, Customer, Project, Task, fact, link, status.
- Match Customer first for every customer-related source. `Task.Customer` is the operational source of truth for customer work filters.
- For Meeting notes, also update the Meeting page itself when possible: suffix the existing title with logical context and fill Customer, Project, and Task relation fields with matched/created pages. Do not invent relations when evidence is weak.
- Do not create a Project purely to give a Task a Customer.
- Link Task directly to Customer whenever identifiable, regardless of whether Project is also linked.
- Create compact Project only when the item is project-shaped or needs durable project context.
- Link Project to Customer when the Project itself carries customer context, but do not rely on Project.Customer as a substitute for Task.Customer.
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
- Never draft when the source message still needs a human reply decision, missing context, or triage judgement first.
- Drafts may be prepared for Email and Slack only when the needed answer is clear, low-risk, and useful for Sil to review/send.

## Report

- One concise numbered list.
- One numbered item = one concrete action/change/blocker. Do not bundle multiple Gmail archives, drafts, Notion writes, status changes, or blockers into one item.
- General format: `Type: [name](link) info`.
- Use compact type prefixes. Common examples: `Customer:`, `Project:`, `Task:`, `Archive:`, `Draft:`, `Failed:`, `Blocked:`, etc.
- For linked items, use exact source/page URL and a compact name variant. Put the action/info after the link.
- Archived Gmail: one archived thread/message per item. Format exactly: `Archive: [short subject or sender](mail link)`.
- Drafted Email/Slack message: one draft per item. Format `Draft: [short subject/customer/channel](draft link) info` when link exists; otherwise `Draft: name - info`.
- Include only net-new writes, real status changes, new refs, archives, drafts, execution artifacts, failed lanes, blockers.
- Suppress rediscovered facts/already-archived sources.
- Nothing changed -> say so.

## Examples

- Customer email adds standalone action -> create/update Task linked directly to Customer; do not create Project just for the relation.
- Customer email adds durable scope -> update/create Project, create Task only for concrete next action.
- Vague captured idea -> Someday, not Task.
