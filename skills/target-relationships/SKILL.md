---
name: target-relationships
description: Use when researching people around Sil's target companies, preparing a daily networking list, or drafting a message for a verified contact opportunity. Sil handles all outreach himself.
---

# Target company relationships

Help Sil meet relevant people at companies that could work with FullDev. Prioritize finding new people. Recent posts, events, and shared relationships can provide a natural reason to reach out.

## Start

First run the collection script and read the file it names:

```bash
python3 ~/.agents/skills/target-relationships/scripts/collect.py
```

It contains Companies with Status `Target` from Notion, including their notes and website. It also contains people already linked to those companies in Dex, people included in a list during the past three weeks, and Sil's DM examples. Then read Sil's latest messages in the Telegram Sales chat (session `agent:main:telegram:group:-5101802924`) for feedback on earlier lists. Do not look up this collected information again. The remaining work is LinkedIn and web research.

## Selection and context

- The target companies and their notes define the audience and possible collaboration. Do not maintain a second company list in this skill or the automation prompt.
- Agencies must demonstrably take on website or webshop projects through design or implementation. Branding, flyers, or packaging alone are insufficient. In-house developers are not required.
- Choose people involved in clients, partnerships, design, marketing, commerce, or development. Assess what FullDev could add. A similar technical stack or a growing agency does not prove a need to outsource. Consider in-house development capacity and time zone when they affect the likely collaboration.
- Include someone outside a target company only when there is a proven connection, such as a collaboration or relevant former role. State that connection. Working in the same industry or sharing one LinkedIn connection is insufficient.
- Use Dex contacts, the Sales chat, and earlier suggestions in the collection file to recognize relationships, sent requests, and previous suggestions. Presence in Dex, a sent request, and an accepted connection are separate facts. A previous suggestion does not prove contact.
- Verify the person's current role, profile, and contact opportunity. Review relevant personal posts, preferably from the past week. Spread the research across target companies. Repeat a person only when there is a new reason.

## Reason to reach out

Add a contact suggestion and draft only when a relevant post, event, or confirmed shared partnership gives a reason to reach out. Write in the recipient's language, using `customer-communication` and Sil's collected DM examples for tone. Keep it short, sincere, and specific. Do not copy typos or unsupported claims from the examples, add a generic pitch or required closing question, or imply an unverified relationship, familiarity, or need. If the page is unreadable, report that and omit the draft. Reuse an introductory reason only when there is new context.

This work is research and preparation only. Do not change Notion or Dex records. Do not send connection requests, messages, comments, or likes. Sil chooses and performs the outreach. For browser work, use Chrome according to the global browser rules. Close the research tabs you opened and preserve existing tabs.

## Daily list

Write a compact numbered list in Dutch with ten well-supported items. Research several target companies. Give fewer than ten if there are not enough verifiable findings, and briefly state what is missing.

Put new people first. For each item, give the person's name with a direct LinkedIn profile link, current role, company, and specific relevance. Link directly to any cited post and include its date. For someone outside a target company, explain the connection. Put any suitable contact suggestion and draft message directly below that person.

Verify every link and mark an unknown connection status as `onbekend`. Omit a general introduction and conclusion. If there are no useful findings, return exactly: `Vandaag geen nieuwe, goed onderbouwde ingangen gevonden.`
