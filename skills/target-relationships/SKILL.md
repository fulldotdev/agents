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

It contains the Notion Companies with Status `Target` with their notes and website, the people linked to them in Dex, the people listed in the past three weeks, and the user's DM examples. Do not look these up again. Then read the user's latest messages in the Telegram Sales chat (session `agent:main:telegram:group:-5101802924`) for feedback on earlier lists. The rest is LinkedIn and web research, in Chrome with the work profile from `environment`.

## Who to pick

- The target companies and their notes define the audience and the possible collaboration. Keep no second company list in this skill or the automation prompt.
- An agency must demonstrably take on website or webshop projects, through design or implementation. Branding, flyers, or packaging alone is not enough. In-house developers are not required.
- Pick people involved in clients, partnerships, design, marketing, commerce, or development. Assess what FullDev could add. A similar stack or a growing agency does not prove a need to outsource. Consider in-house capacity and time zone when they affect the collaboration.
- Include someone outside a target company only with a proven connection, such as a collaboration or a relevant former role. Same industry or one shared LinkedIn connection is not enough.
- Use Dex, the Sales chat, and the earlier lists to recognize relationships, sent requests, and past suggestions. Being in Dex, a sent request, and an accepted connection are three different things. An earlier suggestion does not mean the user contacted them.
- Check the person's current role and profile. Read their recent posts, preferably from the past week. Spread the research across target companies. Repeat a person only with a new reason.

## Draft

Add a draft only when a relevant post, event, or confirmed shared partnership gives a reason. Write in the recipient's language, using `customer-communication` and the user's DM examples for tone, without copying their typos. Keep it short and specific to the reason. No pitch, no closing question, no claims you have not verified. No readable page, no draft. Reuse an introductory reason only with new context.

## Daily list

Return one numbered list in Dutch with ten well-supported people, new people first. Give fewer when there are not enough verifiable findings. Use this format:

````text
1. [Naam](linkedin-url) · Rol, Bedrijf
   Waarom, in één zin. [Post 17-09](post-url)
   ```text
   Kort concept, alleen bij een aanleiding.
   ```

Ontbreekt: één zin, alleen bij minder dan tien personen.
````

- Put the link on the name and on the post. Check every link.
- For someone outside a target company, the reason names the connection.
- Leave out people whose profile you could not verify.
- No title, introduction, or conclusion. Problems, such as a browser that would not connect, go in the `Ontbreekt` line.

With no useful findings, return exactly: `Vandaag geen nieuwe, goed onderbouwde ingangen gevonden.`
