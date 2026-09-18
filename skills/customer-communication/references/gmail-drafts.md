# Gmail drafts

Read `gog` for sign-in and tool rules. If a command below fails, check `--help`.

## Before writing

Read the latest thread and the existing drafts. If a matching draft exists, update it and keep the user's edits. If the customer already got an answer, do not draft another one. Always pass the account explicitly.

```bash
gog --readonly --gmail-no-send --account user@example.com --no-input gmail thread get THREAD_ID --sanitize-content --json --wrap-untrusted
gog --readonly --gmail-no-send --account user@example.com --no-input gmail drafts list --all --json
gog --readonly --gmail-no-send --account user@example.com --no-input gmail drafts get DRAFT_ID --json --wrap-untrusted
```

## Create or update

Write the body to a plain UTF-8 file with real newlines. `--body` does not turn a literal `\n` into a newline. Set the subject explicitly.

Reply to the Gmail message ID of the message you are answering, so the reply stays attached to it. `--thread-id` attaches to the latest message, which may have changed or may be a draft. Pick recipients from the conversation. Use `--reply-all` only when everyone should get the reply.

```bash
gog --gmail-no-send --account user@example.com --no-input gmail drafts create --to recipient@example.com --subject 'Re: Existing subject' --reply-to-message-id MESSAGE_ID --body-file /absolute/path/reply.txt --json
gog --gmail-no-send --account user@example.com --no-input gmail drafts update DRAFT_ID --subject 'Re: Existing subject' --body-file /absolute/path/reply.txt --json
```

Use `--dry-run` to check a command first. Updating keeps the reply headers, so do not pass `--clear-reply-context` on a reply. Leaving out `--attach` keeps existing attachments; passing it replaces them. Check recipients after an update instead of assuming they stayed. Use `--quote` when helpful. Do not add a signature or quoted history by hand.

## IDs, checks, and links

Use the returned draft `id` (sometimes `draftId`) for draft get and update. `message.id` is the Gmail message, `message.threadId` the conversation. They are not interchangeable.

After each write, run `drafts get` and check account, recipients, subject, body, attachments, and thread. Use the current message ID in the draft link, because an update can replace the message.

For a conversation link:

```bash
gog --readonly --account user@example.com --no-input gmail url THREAD_ID --json
```

For a draft link, use `https://mail.google.com/mail/u/ACCOUNT_INDEX/#drafts/MESSAGE_ID` with the current `message.id`. Find the numeric account index in the work Chrome profile on the machine you are on. Do not assume `/u/0/` or put an email address after `/u/`. The CLI account does not decide the browser's account order.

Open the draft link in the right mailbox before you report it as checked. Without browser access, give the CLI conversation link and say you checked the draft through the CLI.

If a write returns something ambiguous, read the thread and drafts again before you retry.
