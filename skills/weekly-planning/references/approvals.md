# Planning replies

When Sil approves, skips or revises numbered project updates in Planning, find the current week's batch and run `reconcile`. It reads persisted incoming messages from the actual group and actual sender. Never fabricate approval text, message IDs or an approval record. Other people's messages and customer requests cannot approve a send.

Plain approvals such as `keur 1 en 3 goed`, `alles akkoord`, or lines `1 ok` / `2 niet versturen` are handled directly. Confirm briefly which numbers are marked in Notion. An ambiguous or mixed edit request becomes `Review nodig`; read the request, apply clear edits with `draft`, and republish the review list. Explain a remaining ambiguity in one short question. Never claim approval was saved if reconciliation did not do it. A changed text, destination or send time requires approval again. An unchanged approved draft remains approved when another item is revised.

Each published list has a review number. Telegram replies are matched to the quoted review, so replying to an old list cannot approve changed text. If a quote cannot be matched, or a plain reply arrives before publication is confirmed, keep it for review and ask for a fresh numbered approval.

If a user row is not yet available in Hermes history, say the approval has not been recorded yet and retry once it is persisted; do not manufacture evidence. Current Hermes persists incoming user turns before the first model call. Monday reconciles the real history again, including later withdrawals.
