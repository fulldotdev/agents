---
name: monday-com
description: Use when reading Teveo or fayn monday.com boards for ticket context, or making a ticket update the user explicitly requested.
---

# monday.com

monday holds the Teveo and fayn tickets, updates, statuses, and sprint groups. `work-management` does the planning and Notion writes. Return ticket facts with pulse URLs or IDs so it can use them.

## Boards and access

- Teveo: `https://teveo-bunch.monday.com/boards/1853861128`
- fayn: `https://teveo-bunch.monday.com/boards/1780576681`

Use Chrome with the work profile from `environment`. Do not use the monday API.

## Reading

For a focused question, read the ticket's updates, links, attachments, and row fields. For a sprint, backlog, release, or capacity review, read every ticket in scope and check its name, group, Priority, and Expected hours, including fields that look blank. Compare what you covered with the full group. A hidden column or a closed ticket dialog does not prove a field is empty.

Keep exact pulse URLs or IDs and version names. Read every relevant ticket or say what blocked you. Do not guess board fields from urgency, comments, colors, or order. If "current sprint" could mean either customer, check both boards.

Read Slack when a ticket links a thread or the user asks. Keep its permalink and say which facts come from Slack.

## Changes

Default to reading. Change a ticket only when the user asked for that change and the ticket is clear. Stay within the request, check the result, and return the ticket link.

Download an attachment only when the preview is not enough, keep it in a temporary path, and never alter it.

Report what you found with sources, what you covered, and any gaps.
