---
name: customer-communication
description: Use when drafting or revising customer-facing email, WhatsApp, or Slack messages, including replies, status updates, clarification questions, scope or pricing messages, and technical explanations.
---

# Customer Communication

Add customer-specific judgment and delivery rules to prose already governed by `unslop`. Draft from what the receiver has actually seen, supplied, discussed, or approved.

## Draft

1. **Establish receiver-visible context.** Inspect the recent messages from both sides when available. Identify the receiver, the last substantive point, what Sil has already introduced, and whether this continues an active exchange or starts a fresh update. Do not reintroduce context the receiver just received. When only an excerpt or previous draft is available, use it without inventing a transition.
2. **Separate business intent from implementation.** Distinguish confirmed intent, open intent, and internal implementation. Ask the customer only about business decisions or rules. Resolve implementation choices internally unless their intent depends on them.
3. **Make the customer action clear.** Continue from the exchange, then give the answer, status, or ask at the first natural point. Include dates, amounts, links, scope, owners, check requests, and default outcomes only when they affect what the receiver understands or does next.
4. **Translate internal context.** Turn internal shorthand, feature names, and technical evidence into customer-visible language. Keep technical detail when the receiver requested it. Use the receiver's business language only when they personally used or received it.
5. **Apply the relevant branch.** For WhatsApp, email, or Slack, read [channels.md](references/channels.md) and apply only that channel. For a status update, scope or pushback, pricing or billing, or technical explanation, read [message-shapes.md](references/message-shapes.md) and apply only that shape.

## Customer boundaries

- Sound like Sil as a practical collaborator. Use `je` and `jullie` naturally, with light warmth and honest pushback.
- Tie apologies to a concrete lapse or customer impact. Use at most one brief thank-you.
- Never expose internal safeguards, permissions, deployment targets, tool state, implementation workflow, or user-assistant discussion unless the user explicitly asks to share that exact detail.
- Do not invent prior agreement, approval, customer-visible facts, or a transition unsupported by the available conversation.
- End after the last customer-relevant result, caveat, or request. Do not add internal safety notes, workflow details, or future deadlines that require no customer action.

## Output

- Put each requested customer draft in its own fenced `text` block so it is directly copyable.
- Keep explanations, status, and caveats outside the draft.
- Briefly label multiple alternatives.
- Follow an explicitly requested output format instead.

A draft is complete when every applicable customer rule passes and it sounds like Sil. Resolve missing context from available sources and flag customer-visible facts that cannot be safely inferred.
