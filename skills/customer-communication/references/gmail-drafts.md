# Gmail drafts

Keep our draft workflow here so updates to the installed `gog` skill do not overwrite it. Read `gog` for sign-in and tool rules. The commands below were checked against gog v0.37.0 help on 7 September 2026. Recheck help if the installed version differs.

## Prepare and preserve the conversation

Inspect the latest thread and existing drafts before creating a reply. If a matching draft already exists, read and update that draft, preserving Sil's edits. If the customer has already received an answer, do not create another reply for the same question. Select the account explicitly.

```bash
gog --readonly --gmail-no-send --account user@example.com --no-input gmail thread get THREAD_ID --sanitize-content --json --wrap-untrusted
gog --readonly --gmail-no-send --account user@example.com --no-input gmail drafts list --all --json
gog --readonly --gmail-no-send --account user@example.com --no-input gmail drafts get DRAFT_ID --json --wrap-untrusted
```

Use a plain UTF-8 body file with actual newlines. `--body` does not turn literal `\n` into newlines. Set the subject explicitly.

Use the Gmail message ID of the message being answered to keep the reply attached to it. `--thread-id` uses the latest message instead, which may have changed or may be a draft. Select recipients from the current conversation. Use `--reply-all` only when all original recipients should receive the reply.

Create or update the authorized draft directly. Use `--dry-run` if you need to check the command first:

```bash
gog --gmail-no-send --account user@example.com --no-input gmail drafts create --to recipient@example.com --subject 'Re: Existing subject' --reply-to-message-id MESSAGE_ID --body-file /absolute/path/reply.txt --json
gog --gmail-no-send --account user@example.com --no-input gmail drafts update DRAFT_ID --subject 'Re: Existing subject' --body-file /absolute/path/reply.txt --json
```

Updating preserves reply headers by default. Do not use `--clear-reply-context` for a reply. Omitting `--attach` keeps existing attachments; supplying it replaces them. Check recipients after an update rather than assuming omitted fields stayed unchanged. Use `--quote` when helpful. Do not add duplicate signatures or quoted history manually.

## IDs, checks, and links

Use the returned draft `id` (sometimes `draftId`) for draft get and update calls. `message.id` identifies the Gmail message; `message.threadId` identifies the conversation. These IDs are not interchangeable.

After each write, use `drafts get` to check the account, recipients, subject, body, attachments, and reply thread. Use the current message ID in the draft link because updating a draft may replace its message.

For conversation links, use the CLI's account-aware output:

```bash
gog --readonly --account user@example.com --no-input gmail url THREAD_ID --json
```

For a draft, use `https://mail.google.com/mail/u/ACCOUNT_INDEX/#drafts/MESSAGE_ID` with its current `message.id`. Check the numeric account index in the work Chrome profile on the machine you are using, following `environment`. Do not assume `/u/0/` or put an email address after `/u/`. The CLI account does not determine the browser's account order.

Open the draft link in the correct mailbox before reporting it as checked. If browser access is unavailable, give the CLI-generated conversation link and state that you checked the draft through the CLI.

If a write returns an ambiguous result, read the thread and drafts again before retrying creation. A draft is not a sent message; authorization to prepare one does not authorize sending it.
