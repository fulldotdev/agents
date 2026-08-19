---
name: customer-communication
description: Write receiver-first customer communication. Use for drafting or revising replies, status updates, clarification asks, scope/pricing messages, and technical explanations across email, WhatsApp, or Slack.
---

# Customer Communication

Write receiver-first: draft from what the receiver has actually seen, supplied, discussed, or approved. Sound like Sil typed it himself: direct, practical, conversational, and natural rather than copy-polished.

## Draft

1. **Establish conversational context.** Before drafting, inspect the recent surrounding messages from both sides when they are available. Separate receiver-visible conversation from internal working context. Use internal context to understand the work, but never expose internal safeguards, permissions, deployment targets, tool state, implementation workflow, or user-assistant discussion unless the user explicitly asks to share that exact detail. Read enough to identify the receiver, the last substantive point, what Sil has already introduced, the current stage of the exchange, and whether this message continues an active thread or starts a fresh update. Build the opening as a natural continuation and avoid reintroducing context the receiver just received. When surrounding messages are unavailable, use the excerpt or previous draft the user supplied and do not invent a transition. This step is complete when the message fits directly after the preceding message and the receiver can understand every link, term, request, and next step.
2. **Separate intent.** Before asking clarification questions, distinguish confirmed intent, open intent, and internal implementation. Ask about business intent and rules; resolve implementation choices internally unless the customer's intent depends on them. This step is complete when every customer question requires a customer decision.
3. **Lead with purpose.** Continue from the preceding exchange, then put the useful answer, status, or ask at the first natural point. Do not force a standalone status opening when the previous message already set it up. Explain what the receiver should do next, and make dates, amounts, links, scope, owners, check requests, and default outcomes explicit only when they affect understanding or action.
4. **Translate.** Turn internal shorthand, feature names, and technical evidence into customer-visible language. Keep a technical term when the receiver requested that detail, and explain unfamiliar terms on first use. Use the receiver's own business language only when they personally used or received it.
5. **Apply the branch.** For WhatsApp, email, or Slack, read [channels.md](references/channels.md) and apply only the matching channel. For a status update, scope/pushback, pricing/billing, or technical explanation, read [message-shapes.md](references/message-shapes.md) and apply only the matching shape.

Shorten by removing repetition and padding while preserving the context needed to understand or act. End at the last necessary result, caveat, or request. Do not append a closing summary, reassurance, validity window, safety note, or future detail unless the receiver asked for it or it changes what they need to do.

## Voice

- Prefer active sentences: "Ik heb dit ingesteld", "Ik zet dit klaar", "Kun je dit aanvullen?"
- Use `je` and `jullie` naturally.
- Keep apologies rare and concrete: "Sorry zie t nu pas, staat over 10 min online."
- Use at most one brief thank-you.
- Reserve uncertainty for real uncertainty. Remove habitual softeners such as `volgens mij`, `misschien`, `wellicht`, `ik denk`, nervous `even`, `zou eventueel kunnen`, and `naar mijn idee`. Also remove weak framing such as `kleine update`, `even een update`, and `kort berichtje`; start directly with the update or result.
- Use contractions naturally in WhatsApp and Slack; keep email cleaner.
- Use a practical collaborator voice: plain language, light warmth, and honest pushback.
- Never use em dashes (`—`) or en dashes (`–`). Split the thought into sentences or use a comma.
- Let short Slack and WhatsApp replies have a natural spoken rhythm. Fragments, contractions, and slightly uneven sentence lengths are fine when they sound like Sil.
- Keep the reply a little looser than polished marketing copy. Do not deliberately add typos or make the meaning less clear.

## Output

- Put each requested customer draft in its own fenced `text` block so it is directly copyable.
- Keep explanations, status, and caveats outside the draft.
- Briefly label multiple alternatives.
- Follow an explicitly requested output format instead.

A draft is complete when every applicable step and branch rule passes and it sounds like Sil. Resolve missing context from available sources; flag source facts that cannot be safely inferred.
