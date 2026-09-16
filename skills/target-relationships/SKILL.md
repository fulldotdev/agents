---
name: target-relationships
description: Use when researching people around the user's target companies, preparing a daily networking list, or drafting a message for a verified contact opportunity.
---

# Target company relationships

Help the user meet relevant people at companies that could work with FullDev. Finding new people comes first. A recent post, event, or shared relationship gives a natural reason to reach out.

This is research and preparation only. Do not change Notion or Dex records, and do not send connection requests, messages, comments, or likes. The user does all outreach himself.

## Start

Run the collection script and read the file it names:

```bash
python3 ~/.agents/skills/target-relationships/scripts/collect.py
```

It contains the Companies with Status `Target` from Notion with their notes and website, the people already linked to those companies in Dex, the people listed in the past three weeks, and the user's DM examples. Then read the user's latest messages in the Telegram Sales chat (session `agent:main:telegram:group:-5101802924`) for feedback on earlier lists. Do not look this information up again. The rest is LinkedIn and web research.

## Who to pick

- The target companies and their notes define the audience and the possible collaboration. Keep no second company list in this skill or the automation prompt.
- An agency must demonstrably take on website or webshop projects, through design or implementation. Branding, flyers, or packaging alone is not enough. In-house developers are not required.
- Pick people involved in clients, partnerships, design, marketing, commerce, or development. Assess what FullDev could add. A similar stack or a growing agency does not prove a need to outsource. Consider in-house capacity and time zone when they affect the likely collaboration.
- Include someone outside a target company only with a proven connection, such as a collaboration or a relevant former role, and say what it is. Same industry or one shared LinkedIn connection is not enough.
- Use Dex, the Sales chat, and earlier suggestions in the collection file to recognize relationships, sent requests, and past suggestions. Being in Dex, a sent request, and an accepted connection are three different things. An earlier suggestion does not mean the user contacted them.
- Check the person's current role, profile, and reason to reach out. Read their recent posts, preferably from the past week. Spread the research across target companies. Repeat a person only with a new reason.

## Reason to reach out

Add a contact suggestion and a draft only when a relevant post, event, or confirmed shared partnership gives a reason. Write in the recipient's language, using `customer-communication` and the user's DM examples for tone. Keep it short, sincere, and specific. Do not copy typos or unsupported claims from the examples, add a generic pitch or a required closing question, or imply a relationship, familiarity, or need you have not verified. If the page is unreadable, say so and skip the draft. Reuse an introductory reason only with new context.

For browser work, use Chrome with the work profile from `environment`. Close the tabs you opened and leave existing tabs alone.

## Daily list

Write a compact numbered list in Dutch with ten well-supported items, researched across several target companies. Give fewer than ten when there are not enough verifiable findings, and say briefly what is missing.

New people first. For each item: name with a direct LinkedIn profile link, current role, company, and the specific relevance. Link any cited post directly with its date. For someone outside a target company, explain the connection. Put a contact suggestion and draft directly below that person when there is one.

Check every link and mark an unknown connection status as `onbekend`. No introduction or conclusion. With no useful findings, return exactly: `Vandaag geen nieuwe, goed onderbouwde ingangen gevonden.`
