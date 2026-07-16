---
name: customer-communication
description: Draft and refine customer-facing messages in direct, practical communication style. Use when drafting, writing, reviewing, shortening, or adapting customer communication, especially replies, project updates, scope/pricing notes, technical explanations, and status updates.
---

# Customer Communication

## Core Style

Write direct, practical, human, and certain. Lead with the useful answer, status, or ask. Skip padding.

Default tone:

- Clear over polished.
- Friendly without being soft.
- Practical over explanatory.
- Specific about dates, money, links, scope, and next steps.
- Honest when scope, timing, or assumptions are off.
- Be concise only after the receiver has enough context. Remove repetition and padding, not information they need to understand the message or act on it.

## Receiver Context First

Write from the receiver's knowledge, not from the internal conversation that produced the draft.

Before drafting:

1. Identify who will receive the message and what they have actually seen, supplied, discussed, or approved.
2. Treat everything else as new information. Assume no project knowledge unless the conversation provides direct evidence that the receiver has it.
3. Introduce the purpose before details: what this is, why they are receiving it, and what they should do.
4. Translate internal shorthand, feature names, technical terms, and team language into plain customer language. If a term must remain, explain it the first time.
5. Preserve useful context when shortening. A shorter draft is worse when it forces the receiver to guess what a link, request, document, environment, or next step means.

When the receiver's prior context is unknown, use the clearest plain-language explanation and assume they know nothing about the work so far.

Before drafting clarification questions for a customer, separate:

- Confirmed intent: what the customer already made clear.
- Open intent: what the customer still needs to decide or clarify.
- Internal implementation: technical choices we should not push back to the customer unless their intent depends on it.

Ask customers about intent and business rules, not implementation mechanics. For example: ask whether a group should be fixed or self-manageable, not whether it should be a tag, metafield, segment, or API rule.

Use a receiver's own words for business concepts only when they personally used or received those words. Do not assume terminology from an internal discussion is shared customer context. If their wording is unknown, use plain language and briefly explain the concept.

Avoid filler and softeners such as: "volgens mij", "misschien", "wellicht", "ik denk", "even" as a nervous habit, "zou eventueel kunnen", "naar mijn idee". Use uncertainty only when it is real.

## Output Format

- Present a requested customer draft in a fenced `text` code block so it is directly copyable.
- Keep any explanation, status, or caveat outside the code block.
- When providing multiple drafts, label them briefly and give each its own code block.
- Follow a different format only when the user explicitly requests one.

## Channel Rules

WhatsApp:

- Ultra-short and conversational.
- Use fragments when natural: "Staat online", "is gefixt", "kan ik fixen", "begin volgende week".
- Use Dutch shorthand when it fits Sil: "ff", "t", "idd", "sws", "isgoed", "rdy".
- Emojis are allowed but sparse: ✅, 👍🏻, 👌🏻, 💪🏻.
- Put the action/status first, then a customer-usable link or detail.
- If saying "preview", include the preview URL in the same message.
- Do not mention internal validation or implementation terms such as build, typecheck, commit, branch, merge, schema, or overflow unless the customer explicitly asked for technical detail. Translate to customer-visible language such as "alles mobiel en desktop nagelopen".

Email:

- Use a simple greeting: "Hey Naam", "Hi Naam", or "Hoi Naam".
- First paragraph states why the mail exists.
- Explain what any preview, document, request, or decision is before giving its link or details.
- Use short headings or bullet lists for pricing, scope, work done, problem/solution, or next steps.
- Include explicit numbers and dates.
- Close with the concrete ask or default: "Laat me weten...", "Hoor graag of dat klopt", "Mocht ik voor [datum] niks horen, dan..."
- Signature can be "[~ Sil Veltman](https://full.dev/contact)" when appropriate.

Slack:

- Match the workspace language. Dutch or English are both fine; code-switch only if the thread already does.
- Keep updates operational: version/status first, then bullets, then owner/check request.
- Use direct pings only when needed.
- For shared customer channels, be concise and factual: "fixed in 2.18.2 ✅", "on it", "preview is now pushed as 2.18.0 ✅".

## Common Structures

Status update:

1. State result: "Staat online ✅" / "Is gefixt" / "Preview staat klaar".
2. Add the relevant link when there is anything to view, especially for previews.
3. Mention one caveat only if it matters.
4. Ask for check only when needed.

Scope or pushback:

1. Acknowledge what exists or what was asked.
2. Say the hard part plainly.
3. Explain the practical implication.
4. Suggest a call, decision, or smaller first step.

Example shape:
"Ik kan hier wel bij helpen, maar dit is niet zo simpel als [their framing]. [Their work/input] is waardevol, maar [real constraint]. Ik stel voor om [next step]."

Pricing or billing:

1. State the change or recommendation.
2. Give the numbers.
3. Explain the practical reason in one short paragraph.
4. Say what happens by default if they do not respond.

Technical explanation:

1. "Het probleem" in plain customer language.
2. Concrete example.
3. "De oplossing".
4. What the customer should do or check.

## Language Details

- Prefer active sentences: "Ik heb dit ingesteld", "Ik zet dit klaar", "Kun je dit aanvullen?"
- Use "je/jullie" naturally.
- Keep apologies rare and concrete: "Sorry zie t nu pas, staat over 10 min online."
- Do not over-thank. "Thanks!" or "Dankjewel voor het doorgeven" is enough.
- For customer-facing Dutch, contractions are fine in WhatsApp/Slack; keep email a bit cleaner.
- Do not make messages corporate, legalistic, or overly warm.

## Draft Checklist

- Is the first line immediately useful?
- Could this receiver understand the message without access to our internal discussion?
- Are unfamiliar links, terms, documents, and requests introduced in plain language?
- Are dates, amounts, links, and owner/check requests explicit?
- Is there a clear next step or default outcome?
- Has only repetition or padding been removed, while useful context remains?
- Does it sound like Sil, not like a generic account manager?
