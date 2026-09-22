# Assess triage quality

Use the strongest available model for a requested review. Check its availability and report the model used; an unattended triage run does not trigger a review or a model switch.

1. Choose an explicit period, normally the last seven days. Collect Gmail, Slack, WhatsApp, Calendar, meeting transcripts, and T3 activity for that period through `collect.py source` with `--after`, `--before`, and `--format json`. Include outgoing messages and pass `--include-settled --include-archived` for T3. Use the source collectors directly, not `run.py`, so live intake bookmarks and retries stay unchanged. Report unavailable sources and incomplete retrieval.
2. Read the original threads, relevant attachments, and full meeting transcripts. Follow older context only where needed to understand an agreement, delivery, or correction. Group messages about the same outcome.
3. Compare each meaningful commitment, change, decision, blocker, and delivery with its owning Notion record, Resources, and linked client ticket. Read the actual destination even if it was not edited during the review period. Check prior records and T3 evidence before calling something missing.
4. Report what landed correctly and a numbered list of concrete misses or mistakes, with source and destination links and the smallest useful correction. Distinguish missing work, wrong ownership, stale status, unsupported commitments, duplicate context, and unread evidence. Separate collector failures from model judgment and tool failures. State the coverage; do not claim a percentage from an incomplete sample.
5. Keep the review read-only unless corrections are requested. Answer in chat. Use existing run receipts and token usage when cost matters; add no score database, dashboard, or recurring audit job.
