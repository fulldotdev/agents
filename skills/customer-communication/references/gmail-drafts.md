# Gmail drafts

Local workflow knowledge belongs here, outside the vendor-managed `gog` skill. Read `gog` for authentication and operation safeguards. Syntax below was checked against installed gog v0.37.0 help on 7 September 2026. Recheck help when the installed version differs.

## Prepare and preserve the conversation

Inspect the latest thread and existing drafts before creating a reply. If a matching draft already exists, read and update that draft, preserving Sil's edits. If the customer has already received an answer, do not create another reply for the same question. Select the account explicitly.

```bash
gog --readonly --gmail-no-send --account user@example.com --no-input gmail thread get THREAD_ID --sanitize-content --json --wrap-untrusted
gog --readonly --gmail-no-send --account user@example.com --no-input gmail drafts list --all --json
gog --readonly --gmail-no-send --account user@example.com --no-input gmail drafts get DRAFT_ID --json --wrap-untrusted
```

Use a plain UTF-8 body file with actual newlines. `--body` does not turn literal `\n` into newlines. Draft replies require an explicit subject. Use the Gmail message ID of the specific message being answered for stable reply headers. `--thread-id` instead uses the thread's latest message, which may have changed or may be a draft. Select recipients from the current conversation; `--reply-all` is appropriate only when all original recipients should receive the reply.

After authorization to save the draft, preview the exact mutation with `--dry-run`, then run it without that flag:

```bash
gog --gmail-no-send --account user@example.com --no-input --dry-run gmail drafts create --to recipient@example.com --subject 'Re: Existing subject' --reply-to-message-id MESSAGE_ID --body-file /absolute/path/reply.txt --json
gog --gmail-no-send --account user@example.com --no-input --dry-run gmail drafts update DRAFT_ID --subject 'Re: Existing subject' --body-file /absolute/path/reply.txt --json
```

Updating preserves reply headers by default; do not use `--clear-reply-context` for a reply. Omitting `--attach` preserves existing attachments. `--attach` replaces them. Inspect recipient fields after update rather than assuming omission preserves every field. `--quote` is optional when useful; do not append duplicate signatures or quoted history manually.

## IDs, readback, and links

Keep the returned draft object's `id` (sometimes exposed as `draftId`) for draft CLI/API operations. Its `message.id` is a Gmail message ID, and `message.threadId` identifies the conversation. They are different identifiers. Update/get expects the draft ID, never the message or thread ID. Read the result of `drafts get` after each write and verify account, recipients, subject, body, attachments, and reply thread. Use the refreshed message ID for a draft link because replacing draft content may replace its message.

For conversation links, use the CLI's account-aware output:

```bash
gog --readonly --account user@example.com --no-input gmail url THREAD_ID --json
```

For a draft, use `https://mail.google.com/mail/u/ACCOUNT_INDEX/#drafts/MESSAGE_ID` with its current `message.id`. The numeric browser account index must be observed in the machine's default Chrome profile; do not assume `/u/0/` or substitute an email address into `/u/`. The CLI account and browser account order are separate. Verify a direct draft link in the correct mailbox before calling it validated. If browser validation is unavailable, provide the CLI-generated conversation link and say the draft was verified through readback, without claiming the browser link was checked.

If a write returns an ambiguous result, read the thread and drafts again before retrying creation. A draft is not a sent message; authorization to prepare one does not authorize sending it.
