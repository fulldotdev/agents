---
name: work-triage
description: "Runs inbound work triage across Gmail, Slack, WhatsApp, calendar, meetings, and Notion capture buckets using live work-management metadata."
---

# Work Triage

1. Collect incoming lane context through sub-agents:
Start one sub-agent per lane:
- WhatsApp messages
- Meeting notes
- Slack DMs, mentions, and threads
- Calendar events for sil@full.dev
- Calendar events for silveltman@gmail.com
- Emails for sil@full.dev
- Emails for silveltman@gmail.com

Each sub-agent must return findings in a clean, context-efficient format while preserving all relevant content. Split by topic and/or chat. Always include references per item.

2. Collect current Notion context:
- Active customers with status Prospect or Active, or edited in the last week
- Active projects with status Discovery, Planned, In Progress, or edited in the last week
- Active tasks with status Todo, Doing, Waiting, or edited in the last week

3. Match incoming information against existing Notion data:
Process relevant incoming lane context into Notion. Use current Notion context to decide the best destination. Prefer updating existing items over creating new ones when there is a reasonable match. Use Notion properties where possible, and store incoming lane context in page bodies.

4. Process lanes accordingly:
- Meetings: suffix the title with a brief meeting description and fill relation properties
- Email: archive emails that have no remaining value or whose value is clearly captured in Notion. Never archive emails that still need action. Draft extremely concise, direct, and simple replies when clearly needed
- Slack: draft extremely concise, direct, and simple replies when clearly needed
- Calendar: create meetings when they were clearly forgotten or missed
- WhatsApp: archive chats that are clearly paused or finished for now and do not need a reply

5. Report via teleframe:
- Use one concise numbered list
- One numbered item = one concrete action, change, or blocker
- Format: `Type: [name](link) info`
- Use compact type prefixes, e.g. Customer:, Project:, Task:, Archive:, Draft:, Failed:, Blocked:
- If nothing changed, say so
