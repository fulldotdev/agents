---
name: customer-communication
description: Write receiver-first customer communication. Use for drafting or revising replies, status updates, clarification asks, scope/pricing messages, and technical explanations across email, WhatsApp, or Slack.
---

# Customer Communication

Write receiver-first: draft from what the receiver has actually seen, supplied, discussed, or approved. Sound direct, practical, human, and certain.

## Draft

1. **Establish context.** Identify the receiver and the direct evidence of what they already know. Treat everything else as new information. When their prior context is unknown, assume no project knowledge and explain the work in plain language. This step is complete when the receiver can understand every link, term, document, request, and next step without the internal discussion.
2. **Separate intent.** Before asking clarification questions, distinguish confirmed intent, open intent, and internal implementation. Ask about business intent and rules; resolve implementation choices internally unless the customer's intent depends on them. This step is complete when every customer question requires a customer decision.
3. **Lead with purpose.** Put the useful answer, status, or ask first. Then explain what the message concerns, why it matters, and what the receiver should do. Make dates, amounts, links, scope, owners, check requests, and default outcomes explicit.
4. **Translate.** Turn internal shorthand, feature names, and technical evidence into customer-visible language. Keep a technical term when the receiver requested that detail, and explain unfamiliar terms on first use. Use the receiver's own business language only when they personally used or received it.
5. **Apply the branch.** For WhatsApp, email, or Slack, read [channels.md](references/channels.md) and apply only the matching channel. For a status update, scope/pushback, pricing/billing, or technical explanation, read [message-shapes.md](references/message-shapes.md) and apply only the matching shape.

Shorten by removing repetition and padding while preserving the context needed to understand or act.

## Voice

- Prefer active sentences: "Ik heb dit ingesteld", "Ik zet dit klaar", "Kun je dit aanvullen?"
- Use `je` and `jullie` naturally.
- Keep apologies rare and concrete: "Sorry zie t nu pas, staat over 10 min online."
- Use at most one brief thank-you.
- Reserve uncertainty for real uncertainty. Remove habitual softeners such as `volgens mij`, `misschien`, `wellicht`, `ik denk`, nervous `even`, `zou eventueel kunnen`, and `naar mijn idee`.
- Use contractions naturally in WhatsApp and Slack; keep email cleaner.
- Use a practical collaborator voice: plain language, light warmth, and honest pushback.

## Output

- Put each requested customer draft in its own fenced `text` block so it is directly copyable.
- Keep explanations, status, and caveats outside the draft.
- Briefly label multiple alternatives.
- Follow an explicitly requested output format instead.

A draft is complete when every applicable step and branch rule passes and it sounds like Sil. Resolve missing context from available sources; flag source facts that cannot be safely inferred.
