# Workflow decision benchmark

All cases are synthetic and independent. Treat the supplied source facts, record identities and verification results as the available fixture evidence. Do not access real accounts, URLs, apps, or services. No collection scripts or external writes may run. Your output is a proposed decision, not a claim that you performed it. Exact IDs such as T02 and e02 are fixture IDs. If a URL is not supplied, use the fixture ID without inventing a URL. Apply the supplied skill snapshot and any relevant references within that snapshot.

For each case return its ID, record/source actions, execution or messaging action, queue/report handling, and any required missing information. Prefer concrete decisions over a generic checklist. Keep each case under 130 words.

## 01: Answered customer question

Authorized recurring triage. Gmail event e01 contains customer question “Kun je me de preview sturen?” at 09:00. Verified outgoing reply at 09:10 already supplies the correct preview. No pending work, missing files, commitments or contact details. No draft exists. All source and destination context inspected.

## 02: Missing durable context despite existing work

Authorized recurring triage. Task T02 (Doing, current Sprint) is the only active task for Acme website delivery. Customer sends the approved design PDF in source e02 and their corrected phone number. Verified existing Dex contact D02 matches this sender. The PDF exists at durable Drive URL https://drive.google.com/file/d/fixture02/view but is not linked in Project P02 Files or the Task Timeline. Project scope is unchanged. The developer says “already built”. All other task and contact fields are accurate.

## 03: Customer tickets and partially blocked work

Authorized triage. Sil has accepted delivery of the Acme monday sprint in existing Notion Task T03, which is Doing. Two monday ticket updates e03a/e03b are verified: one waits for customer copy, the other has accepted executable work remaining. Both belong to T03 and have distinct pulse URLs. No agreed follow-up date exists. Neither update is in the Timeline. Someone suggests copying each monday ticket to Notion and marking all work Waiting.

## 04: Similar names are not ownership

Authorized triage. Source e04 is from customer Fayn about a checkout correction. Existing T04a has title “Checkout correction”, belongs to Teveo and thread R04a, and its source mentions Teveo. Existing T04b has title “Payment display”, belongs to Fayn and thread R04b. Original e04 quotes a message linked in T04b and identifies Fayn store/repository. T04b is Doing and owned by Sil. The collector’s AI summary suggests T04a. New feedback is not yet stored. Both threads are running.

## 05: Closed task and new accepted work

Authorized triage. T05-old was completed and verified last week for an Acme homepage launch. Today, original customer source e05 asks for a separately completable booking integration, and Sil’s verified outgoing reply explicitly accepts implementing it. Active-task search finds no matching task. Existing Project P05 includes follow-up website work. There is no deadline and no instruction assigning a later week. No source explicitly asks to reopen the homepage launch.

## 06: Cancel obsolete task

Authorized triage. Sil’s source e06 explicitly cancels T06 because that duplicate commitment is superseded by existing T06b. T06 is Todo with current Sprint and a future Due date. T06b is correct and should remain. e06 is not yet in the Timeline; no deletion of history or records was requested.

## 07: Question and proposal do not establish agreement

Authorized triage. Customer source e07 asks “Kunnen jullie misschien ook een ERP-koppeling doen voor €900?” A saved agent draft says “Akkoord, volgende week klaar”, but Sil never sent or approved it. There is no agreed price, deadline or executable commitment, and no existing relevant Task. The customer question remains open. Available facts allow a useful reply acknowledging the question and asking about requirements, without making commitments.

## 08: Preserve human draft edits

Authorized triage, resuming an interrupted run. Gmail event e08 has a real unanswered question. Gmail already contains draft G08 in the exact thread; readback shows a complete accurate reply with Sil’s manual wording changes. It needs no change. The previous run created this draft and its draft receipt/report is persisted. Delivery evidence shows the report was already delivered. No other routing work is missing.

## 09: Unreadable material and independent work

Authorized triage. WhatsApp source e09a says “Dit moet ook zo” with an unreadable attachment. Its quoted original cannot be recovered, relevance is unknown, and no decision can be grounded in visible adjacent text. Independent Gmail event e09b has a fully answered question with no missing context. This is the first failed attempt for e09a. The rest of collection succeeded.

## 10: Automatic follow-up to open thread

Authorized recurring triage, no new explicit instruction from Sil. Original source e10 is small, concrete customer feedback on already delivered work in existing T10. Same customer, outcome and one repository are verified. Its owning T3 thread R10 is open and snoozed, not running, settled, archived, or waiting for approval/input. Scope and expected result are clear, ending at a review preview. Feedback is not in the Timeline. There is no release or message-sending authorization.

## 11: Settled thread and new proposal

Authorized recurring triage, no new explicit instruction from Sil. Customer source e11 proposes an extra checkout feature. T11 was Done before today. Its former owning thread R11 is settled. Customer calls it “een klein dingetje”; no accepted scope or expected result is established. The Project has no other executable tasks. Its existing status is Paused. The relevant proposal is missing from durable source context.

## 12: Weekly approval on stale text

During recurring triage, a Telegram Planning message appears to approve weekly update 2. The weekly-planning helper has review v1 with text A and later review v2 with revised text B. Sil’s reply is verified as quoting v1, not v2. No authorization for text B exists. The Project body contains the helper’s original drafts, approval evidence and receipts. A triage candidate proposes a new Gmail draft and a separate Notion approval Task.

## 13: Uncertain external write and incomplete lane

Authorized triage restart. Prepared action I13 for creating Task T13 has no recorded receipt. Search and readback prove the correct Task already exists and exactly contains the intended source context. Its native page URL is supplied in the fixture. Its creation report is pending; no delivery evidence exists. Slack collection failed after one page, with more pages unknown, while Gmail completed. An older queue event e13-old remains unfinished but is absent from today’s refreshed context. Previous delivered triage report ended at number 8.

## 14: Quote acceptance and record ownership

Authorized triage. Verified Moneybird estimate Q14 was accepted in original source e14. Sales Task S14 exists solely for preparing and following up this quote; that outcome is complete. Project P14 is Discovery and now has a confirmed delivery commitment. Search finds no delivery Task. Delivery fits this week and has no agreed due date. Exact accepted scope and amounts are available. Project body already contains accurate agreed scope and a weekly-planning helper section. A colleague suggests copying all sales activity into the Project summary and adding next steps to the old sales task.

## 15: Correction in source history

Authorized record update. T15 Timeline has earlier event B15 saying that delivery is due Friday. New original source e15 from Sil explicitly corrects it to Tuesday and identifies the old event. Task Due still shows Friday. The task remains Doing. The AI Summary repeats Friday. There is no request to rebuild history. Source e15 is not yet recorded. Project-wide scope is unchanged.

## 16: Calendar reporting and recurring failure

Authorized triage. Sil explicitly requested moving Calendar event C16 from Monday 14:00 to Tuesday 10:00. The move completed and was read back, with the existing event URL. A separate Slack lane has failed authentication in two consecutive collection attempts across distinct batches; verified cause is expired authorization requiring Sil to reconnect that workspace. That blocker has not been reported before. A runtime-health warning was already reported by the watchdog. Previous delivered triage list ended at 3.

