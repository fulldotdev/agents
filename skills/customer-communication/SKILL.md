---
name: customer-communication
description: Use when drafting or revising customer emails, WhatsApp messages, or Slack messages in Sil's voice.
---

# Customer communication

## Read the conversation

Write as Sil continuing the conversation. Read the latest relevant messages from both sides and Sil's corrections. Find the open question, what the customer knows, and what Sil has agreed or done. Check whether the latest sent reply already answers the question. A draft or someone else's request does not prove agreement.

Base the message on the conversation with its recipients, including relevant threads and meetings they attended. Internal discussion with the agent helps prepare the work but does not automatically belong in the update. Raise a new topic only when Sil asks or it helps answer the recipient's question. Introduce it as new.

## Write the message

Give the answer or result first, with enough explanation to make it useful. Follow the plain style in `user-communication` and match the conversation's language and familiarity. In Dutch, use `ik`, `je`, and `jullie`. A short acknowledgment or fitting emoji can add warmth. Choose greetings, thanks, lists, and sign-offs to fit the exchange. Do not copy typos or force informality.

For unclear scope, explain what is included, what is missing, and what that means for the customer. Then explain any extra work or decision. For a problem, separate confirmed facts from possible causes and offer a useful next step within the authorized work.

Resolve implementation choices internally. Include technical detail when the recipient needs it to decide, use, or review something. Keep the agent's internal checks and permission rules out of the message.

Use confirmed amounts and scope. Use `commercial-scoping` when these need calculation or reconciliation. Never invent agreement, completion, availability, prices, deadlines, or consequences of silence. Include a verified link when the customer needs to review or use something. Ask a follow-up only for an open point. Stop after the last useful result, caveat, or request.

Read [examples.md](references/examples.md) for tone or sensitive replies about scope, problems, or pricing. The examples explain writing choices; their facts do not apply to other customers.

## Deliver the draft

Put each draft in its own fenced `text` block unless Sil requests another format. Give one version unless alternatives are requested. Keep internal notes and missing facts outside the block. A draft with unresolved factual placeholders is not ready to send. Use an existing or requested sign-off when appropriate, and avoid duplicate email signatures.

For requested Gmail drafts or drafts authorized by triage, use `gog` and [gmail-drafts.md](references/gmail-drafts.md) directly. A chat-only writing request stays in chat. Saving a draft does not authorize sending.
