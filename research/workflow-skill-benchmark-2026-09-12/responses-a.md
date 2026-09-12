# Snapshot A decisions

Simulation only. These are proposed actions, not performed service operations. For external record writes, prepare a durable intent, verify readback, then resolve it before acknowledging the source. Routine context writes remain quiet. Report delivery is marked only after verified delivery evidence. Fixture IDs stand in for URLs where the fixture supplies no literal URL.

## 01

Records/source: No record or file changes. The verified 09:10 reply answers e01 and all completion checks pass.
Execution/messaging: No task, draft, follow-up, or outgoing message.
Queue/report: Acknowledge e01 as `no_action`, citing the verified sent reply and absence of missing context. No report; `NO_REPLY`.
Missing information: None.

## 02

Records/source: Reuse T02. Append e02 as a dated source event describing design approval and its durable PDF reference. Add https://drive.google.com/file/d/fixture02/view to P02 Files without uploading another copy. Correct only D02's phone number; preserve other contact fields. Keep contact ownership in Dex and the unchanged project scope intact.
Execution/messaging: Do not infer completion from “already built”; T02 remains Doing without verified outcome completion. No duplicate task or automatic new execution.
Queue/report: Verify the Timeline, Files link, and phone correction before acknowledging e02 as handled. These are quiet context updates; `NO_REPLY`.
Missing information: No routing ambiguity; Dex operating skill is absent from this snapshot.

## 03

Records/source: Append e03a and e03b as separate T03 Timeline events using each original pulse URL. Identify customer copy as the dependency and customer as its owner. Keep executable remaining work visible through the recorded source facts. Preserve T03 Doing; no Due reminder without agreement.
Execution/messaging: Continue accepted executable work under the existing delivery commitment. Do not duplicate monday tickets into Notion or mark the entire package Waiting. No automatic thread dispatch can be selected from the supplied evidence.
Queue/report: Verify both events and acknowledge each as handled. Quiet record updates; `NO_REPLY`.
Missing information: Exact repository/thread needed only for a concrete execution handoff.

## 04

Records/source: Route e04 to T04b using the quoted original and verified Fayn store/repository. Append its actual feedback as a dated source event. Leave T04a and Teveo untouched; the collector summary and matching title do not establish ownership.
Execution/messaging: T04b remains Doing. Do not resume either running thread or create another owner. R04b is the relevant owner for subsequent execution coordination.
Queue/report: Verify T04b's stored feedback, acknowledge e04 as handled, and stay silent because only context was updated.
Missing information: None for routing. Running-thread status prevents automatic feedback dispatch now.

## 05

Records/source: Preserve T05-old Done. Create a separate booking integration Task under P05, Area Delivery, Todo, current Sprint, with Due empty. Append original e05 and Sil's acceptance as separate source events; relate the earlier launch where useful without reopening it.
Execution/messaging: Sil's accepted implementation covers starting that work. Prepare its execution handoff from accepted scope and sources; select the actual repository, checkout, and owning thread before dispatch. Do not guess those identifiers or send a customer message.
Queue/report: Verify creation and acknowledge its record action. Report the new Task. Keep any unresolved execution action pending rather than claiming dispatch.
Missing information: Repository/checkout and execution target are absent from this fixture.

## 06

Records/source: Append e06 to T06's Timeline with the cancellation and superseding T06b locator. Set T06 Todo → Canceled and clear both Sprint and Due in the final write. Preserve history and T06b.
Execution/messaging: Stop treating T06 as executable. No deletion, duplicate work, or customer message.
Queue/report: Verify Canceled status and empty Sprint/Due, resolve the cancellation intent, and acknowledge e06. Report `Task canceled: T06 - Todo → Canceled`.
Missing information: None; use fixture IDs instead of inventing native URLs.

## 07

Records/source: Keep e07 as an unconfirmed proposal in its source. Create no Task, agreed price, Due date, or accepted scope from the unsent agent draft.
Execution/messaging: Replace the saved inaccurate draft with one grounded reply, preserving any valid human wording: “Welke ERP-software gebruiken jullie, en wat moet de koppeling precies doen? Met die informatie kan ik beoordelen wat er nodig is en wat het kost.” Save one matching Gmail draft if this is a Gmail thread; never send it. Do not promise €900 or next week.
Queue/report: Verify the corrected draft, record a material draft update, acknowledge e07, and report the draft for review.
Missing information: Source channel/draft location must be confirmed for Gmail storage.

## 08

Records/source: No changes; all routing is already complete.
Execution/messaging: Preserve G08 exactly, including Sil's manual edits. Do not recreate, overwrite, or send it.
Queue/report: Reconcile the existing draft receipt and persisted report against verified delivery. Mark that report reported if needed, without recording a new draft outcome. Acknowledge e08 as handled after confirming no outstanding intent. Return `NO_REPLY`.
Missing information: None.

## 09

Records/source: Do not infer e09a's meaning or store imagined requirements. Keep its attachment and quoted-original issue unresolved. e09b needs no record change because its question is fully answered and context is complete.
Execution/messaging: No execution or reply based on e09a. No duplicate Gmail draft for e09b.
Queue/report: Retry e09a with the precise missing evidence: readable attachment and recoverable quoted original, or other evidence establishing its relevance and meaning. Acknowledge e09b as `no_action`. Complete successful independent lanes while retaining e09a's payload. First failure does not meet escalation threshold; `NO_REPLY`.
Missing information: Readable original material and quotation context for e09a.

## 10

Records/source: Append e10 to T10's Timeline before execution, preserving the exact customer feedback and source locator.
Execution/messaging: Resume/wake R10 under the automatic feedback gate. Give it the verified repository/branch, corrected current brief, expected result, and review-preview boundary. Ask it to implement, validate, and prepare a review preview using development conventions. No release or external message. Preserve R10 as the sole owner.
Queue/report: Prepare the dispatch intent before calling, confirm R10's resumed state, resolve with its receipt, and acknowledge e10 when routing and dispatch are verified. Report `T3 continued: R10`.
Missing information: None affecting the dispatch decision; actual branch/native locator must come from verified execution context.

## 11

Records/source: Append e11's proposal to T11's Timeline, explicitly retaining its unaccepted scope and unresolved expected result. Keep T11 Done and the Project Paused. Do not rewrite the project agreement or invent a delivery Task because the Project lacks executable work.
Execution/messaging: Do not revive settled R11 or start another thread. A customer calling this small does not authorize implementation. No new Gmail draft is required by the supplied proposal alone.
Queue/report: Verify durable proposal context, acknowledge e11 as handled, and stay silent; `NO_REPLY`.
Missing information: Accepted scope, expected result, and explicit Sil authorization are required before revisiting the settled thread.

## 12

Records/source: Route to weekly-planning reconciliation using the original Planning reply. Preserve the helper's drafts, review versions, approvals, and receipts in the Project body. The quote of v1 cannot approve changed text B in v2.
Execution/messaging: Keep update 2's revised text unapproved and unsent. Request fresh approval of update 2 in the current v2 review; do not claim B was approved. Create neither a second Gmail draft nor a separate Notion approval Task.
Queue/report: Let the weekly helper own approval/send state. Triage can acknowledge its routing decision but must not encode the approval in triage cursors or pending queue. No separate triage outcome report.
Missing information: Fresh approval of exact current text B and destination.

## 13

Records/source: Reuse the verified existing T13. Resolve I13 with T13's receipt and native URL; do not create another Task. Reopen older e13-old from the durable ledger and inspect its source before deciding, even though refreshed context omitted it.
Execution/messaging: No repeated creation. Continue processing completed Gmail and independent pending work.
Queue/report: Acknowledge I13's event after reconciliation. Report the undelivered creation as item 9, `Task created: T13`; leave it unmarked until delivery is verified. Retain Slack's checkpoint and missing pages. Keep e13-old unfinished if its evidence is unavailable. One failed collection alone warrants no escalation.
Missing information: e13-old's decision evidence and remaining Slack pages. T13's native URL is asserted but not literally provided.

## 14

Records/source: Append verified quote acceptance e14 and Q14 locator to S14, then mark its completed sales outcome Done. Create a separate Delivery Task under P14, Todo, current Sprint, Due empty, with exact accepted scope, amounts, and source evidence. Change P14 Discovery → Planned. Keep its accurate agreed scope and weekly helper section intact; no copied sales history or next steps on S14.
Execution/messaging: No additional scope/price negotiation or automatic new T3 thread from customer acceptance alone without established implementation-start authorization.
Queue/report: Verify and report S14 done, delivery Task created, and P14 status changed. Acknowledge after resolving all writes.
Missing information: S14's previous status for its transition; no routing blocker. Moneybird operating skill is absent from this snapshot.

## 15

Records/source: Append e15 as a correction event identifying B15's old heading and block ID. State that Tuesday replaces Friday as the delivery deadline and that other valid facts remain. Set Due to the source-supported Tuesday. Keep Doing and preserve B15 unchanged. Do not manually edit the generated Summary or project scope.
Execution/messaging: Derive subsequent work and handoffs using the correction, not the stale summary. No separate work item or outgoing message.
Queue/report: Verify the new event and corrected Due, resolve the quiet update, acknowledge e15 as handled, and return `NO_REPLY`.
Missing information: Exact calendar date if the source locator cannot disambiguate which Tuesday; do not invent one.

## 16

Records/source: Preserve verified C16 rescheduling and its event URL. Reconcile/resolve the Calendar action receipt without moving it again. Retain Slack's incomplete checkpoint and unresolved work.
Execution/messaging: No repeat Calendar write. Sil must reconnect the affected Slack workspace's expired authorization. Do not repeat the watchdog's runtime warning.
Queue/report: Record the verified Calendar action and new actionable Slack failure. Continue numbering: `4. Calendar rescheduled: C16 - Monday 14:00 → Tuesday 10:00`; `5. Slack collection blocked: reconnect the affected workspace to renew expired authorization.` Link C16 using the supplied event URL. Mark these reported only after verified delivery.
Missing information: Actual workspace name and event URL are not printed in the fixture; use fixture references without inventing them.
