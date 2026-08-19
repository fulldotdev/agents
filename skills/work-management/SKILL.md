---
name: work-management
description: "Manage the Notion-backed work system. Use whenever Tasks, Projects, Customers, Sprints, Someday, triage, weekly planning, statuses, priorities, or work coordination with Productive or Moneybird are involved."
---

# Work Management

This skill owns work-system semantics. Live Notion owns current records and schema.

Read the matching workflow reference before acting:

- Broad Gmail, Slack, WhatsApp, calendar, meeting, Codex, or Notion intake: [triage.md](references/triage.md)
- Weekly review, Productive reconciliation, system review, or Sprint planning: [planning.md](references/planning.md)
- Exact Notion property names, option names, relations, IDs, or write validation: [notion-schema.md](references/notion-schema.md)
- Productive or Moneybird actions coordinated with agency records: [commercial-coordination.md](references/commercial-coordination.md)
- Configuring or regenerating the Notion AI Task Summary: [summary-prompt.md](references/summary-prompt.md)
- Normal Task, Project, or Customer management and direct Notion updates: use this main skill plus the relevant domain skill.

Load multiple references only when the request genuinely crosses workflows.

## Model

- **Task**: a compact, executable work package, usually spanning hours to a few days and normally less than one week. It may contain several tightly related actions when they serve the same stakeholder and concrete outcome or deliverable. Its Timeline preserves the direct events needed to derive the current action and completion conditions at read time.
- **Project**: a bounded multi-work-item or multi-week outcome with a clear completion point, usually comprising multiple independently managed Tasks.
- **Customer**: stable account context. Use a lowercase domain/repo-style handle and add a fitting page emoji when creating one.
- **Sprint**: Monday-Sunday commitment containing every Task Sil has explicitly committed to work on substantially that week. Prefer completion within the week, but allow an externally delivered result just after Sunday when substantive execution is deliberately scheduled in the current Sprint. Apply no numeric capacity limit.
- **Goal**: an accepted desired outcome or durable personal/business result. Use Goal status `Backlog` when the outcome is real but has no active horizon or execution plan; move it to `3 maanden`, `1 jaar`, or another horizon only when consciously activated.
- **Someday**: non-executable maybe-later idea, vague exploration, or possible action that is not yet an accepted outcome.
- **Source**: message, email, meeting, file, link, attachment, quote, decision, blocker, requirement, or other evidence. A Source provides context; executable work requires a routed outcome.
- **Document**: a findable authored work product or external-document index entry, such as copy, a brief, scope, spec, research note, draft, or designed asset. Mutable content belongs in the Document page or its `Source URL`; link it to Tasks, Projects, and Companies instead of embedding it in a Task body.

Tasks may link directly to a Customer. One Customer may own multiple Projects when the commercial or delivery scopes have independent outcomes or completion points. Keep several actions in one Task when they belong to the same stakeholder, concrete outcome or deliverable, and short execution window. Split work when the stakeholder changes, an outcome can be completed independently, or it has its own blocker, approval, or deliverable. Use a Project when one broader outcome needs multiple Tasks or is likely to span more than about one week.

Projects own the shared outcome, scope, commercials, cross-Task decisions, and delivery history. Tasks own one compact work package and its source-grounded execution evidence; derive acceptance conditions at read time from direct Timeline events and live sources rather than maintaining an inferred criteria section. Do not turn Tasks into indefinite operational buckets; recurring work needs a bounded period or result.

## Area

Use Area to describe where a Task belongs. Choose the single Area that owns its primary outcome:

- **Delivery**: do work for customers, including implementation, support, coordination, QA, communication, and customer-specific operations.
- **Sales**: qualify a lead, define scope, prepare an offer, or win a commitment.
- **Growth**: grow Full.dev through marketing, positioning, partnerships, internal products, reusable assets, open-source work, or demand generation.
- **Admin**: operate the business or work system, including finance, legal, tooling, and internal coordination.
- **Personal**: non-business work.

Choose Area from the primary outcome, not merely from the linked Customer or Project. Work intended to win new or expanded business is Sales; other work done for a customer is Delivery.

## Routing

1. Read the target item's full properties, Markdown body, and relevant source context before deciding or writing.
2. Route to an existing active Task, Project or Customer context, a new Task, a new Project plus first Task, Someday, or no action.
3. Reuse an active Task only when the incoming work belongs to the same stakeholder, concrete outcome or deliverable, and short execution window.
4. Add tightly related calls, preparation, follow-up, blockers, preferences, and source files to that Task instead of creating action-level duplicates. Put mutable authored work products such as copy, briefs, scopes, specs, research, drafts, and designed assets in `Documents`; link them to the Task and append only source-grounded document update events to the Task Timeline.
5. Split a separate Task when the stakeholder changes or the work has an independently completable outcome, deliverable, blocker, or approval. Group related Tasks in a Project when the broader outcome has multiple work items or is likely to span more than about one week.
6. Treat Tasks completed before today as closure records. Create a related follow-up Task only when genuinely new execution actually arrives; do not keep or create dormant Tasks for hypothetical future requests.
7. Create a Task for Sil only when Sil owns a concrete action, decision, deliverable, or follow-up. Work owned by another person belongs in Project or source context until Sil receives an executable responsibility.
8. Use `Waiting` while a concrete dependency prevents execution. When it clears, choose `Todo` or `Doing` from whether execution has started; apply no automatic transition.
9. Preserve source trace through relations and compact, reopenable references.

Routing is complete when every actionable source has one owning record, every non-action has a deliberate destination, and every write retains its source trace.

## Status

- **Todo**: accepted and executable, but not started. A Sprint relation expresses weekly commitment; Todo without a Sprint remains unscheduled.
- **Doing**: execution has started and remains unfinished, including between work sessions.
- **Waiting**: a concrete person, dependency, decision, timing condition, customer, vendor, approval, or review prevents execution.
- **Done**: completed and verified; customer work uses the evidence gates in `customer-work`.
- **Canceled**: duplicate, superseded, moved to Someday, no longer executable, or explicitly dropped.

Treat the Status property as the sole source of truth. Timeline entries record direct status evidence but do not restate status as a body field or derive it from age, Sprint membership, missing information, or activity. Apply no limit to Todo, Doing, or Sprint size. Keep started unfinished work in Doing unless a concrete dependency makes it Waiting.

Before changing Status, append the direct event, decision, blocker, verification, reopening, or cancellation source that supports the transition. `Done` is terminal unless Sil or a newer source explicitly reopens the same deliverable; new work after completion normally becomes a related Task. For `Canceled`, remove obsolete Sprint and Due properties. Removing or ignoring an item within a combined Task changes only that combined Task; preserve any standalone Task unless the user explicitly cancels it.

Use due dates for real deadlines and follow-up dates.

## Project status

- **Discovery**: active sales, scoping, and proposal period before delivery commitment.
- **Planned**: delivery is approved or committed but has not started.
- **In Progress**: delivery has started.
- **Paused**: a deliberate project-level hold.
- **Completed**: the agreed Project outcome is delivered.
- **Canceled**: the Project is explicitly stopped.

Move Discovery to Planned when a concrete delivery commitment or approval exists.

## Documents

Use `Documents` for mutable authored work products and for indexing external documents that must be findable. The database is hybrid: keep Notion-native work in the Document body; for Google Docs, Drive, Figma, or another canonical external file, keep the Document body minimal and set `Source URL` to the canonical location. Never duplicate an external document merely to make it searchable.

Keep the schema minimal:

- `Name`
- bidirectional `Tasks`, `Projects`, and `Companies` relations
- optional `Source URL`
- automatic `Created` and `Edited`

A Task relation exposes the document title without fetching the body. Store full copy, evolving requirements, long research, designs, and attached assets in the Document, not in the Task. The Task Timeline records only direct document lifecycle events such as creation, a meaningful update, review, approval, publication, or archival. Each event links the exact Document or external source and summarizes the direct delta in one or two compact bullets. Do not copy the complete Document content into the Timeline, treat a mutable Document body as historical proof for earlier states, or use the Task as the source for its own Document claims.

When a mutable artifact is currently embedded in a Task, create and relate a Document, preserve its content and files there, verify the relation and artifacts, and only then replace the Task content with a compact Timeline event. Preserve Task properties and never hand-edit the AI Summary.

## Timeline bodies

A Task body is an incomplete, append-only source log. Capture durable requirements, decisions, approvals, deadlines, scope, blockers, technical facts, files, verification, and corrections in the event where they became known. Preserve source titles, filenames, IDs, links, and quotes literally. Absence from the Timeline is never evidence that something did not happen.

Use this body:

```md
## Timeline

*Append-only and possibly incomplete.*

### <native Notion @date> — [<channel>](<primary source>) — <short description>

- Rich, direct source context.
- Explicit decisions, constraints, owners, uncertainty, and evidence that may affect future execution.
```

Use a native Notion date mention in every entry heading. Link the channel name to the primary message, thread, meeting, document, PR, or file. Keep the description short and concrete. The heading is the reference: do not repeat it in a separate `Refs` line. When context comes from multiple sources, append separate source entries rather than a combined synthesis.

When no reopenable URL exists, keep the channel unlinked and place its stable locator in the heading:

- `Telegram · chat <id> · topic <id> · message <id>`; omit unavailable segments.
- `Telegram · Hermes host <host> · profile <profile> · session <session-id> · message <id>` when only the captured Hermes conversation is reopenable.
- `Codex · host <reachable-host> · thread <uuid> · repo <owner/name> · checkout <branch-or-worktree>`; a bare thread ID or local hostname without a reachable host mapping is insufficient across machines.
- For another system, use `<channel> · <smallest stable locator that a resolver can reopen>`.

Examples:

```md
### <native Notion @date> — [Slack](https://workspace.slack.com/archives/<channel>/<message>) — Categoriebeheer afgestemd
### <native Notion @date> — Telegram · chat <id> · topic <id> · message <id> — AI-toegang gevraagd
### <native Notion @date> — Telegram · Hermes host otis · profile default · session <session-id> · message <id> — AI-toegang gevraagd
### <native Notion @date> — Codex · host otis · thread <uuid> · repo owner/metispro · checkout <branch> — Implementatie gevalideerd
```

If neither a URL nor stable locator exists, write `<channel> · source unavailable` in the heading and preserve only the direct facts actually captured. Never replace the original source with a different channel merely to obtain a clickable link.

Append one self-contained entry per source event and keep Timeline entries in ascending source-event chronology. When one source event is split across consecutive messages or files, preserve their source order as separate entries unless one durable link resolves the complete event. Include enough direct context to prevent a future AI from making a materially wrong decision, while keeping provenance local to that entry. Preserve exact names, channels, owners, branches, deadlines, decisions, safety constraints, verification claims, and uncertainty such as `concept`, `reported by the PR`, or `not yet tested`. Phrase volatile facts as dated observations. A Task must never cite itself as independent evidence for its own claims.

In normal operation, existing entries are immutable. Append corrections that quote the exact superseded heading and include its Notion block ID or block URL when available; same-date descriptions alone are not unique enough. State which claims are replaced and which remain valid. When reading, process all correction and supersession entries before deriving current claims, even when the superseded entry appears earlier. During an explicit migration or repair where the user authorizes rewriting, replace the pilot history with one clean source-faithful Timeline and remove correction scaffolding rather than preserving known-bad entries. Do not persist regenerated `Next`, `Done when`, current-state summaries, inferred criteria, or uncited synthesis. Derive those at read time from the Timeline and live sources. The `Summary` property is AI-generated: never edit it manually or treat it as evidence. If it is stale or misleading, tell the user to regenerate it with the configured Notion AI prompt.

Tiny reminders may have a light or empty body. Write compact titles that name the work package or observable outcome, not every substep. Prefer English titles unless the work is clearly conducted in Dutch; then use Dutch. Preserve customer language literally.

Project bodies remain flexible. Use relevant sections such as `## Outcome`, `## Current state`, `## Open loops`, and `## Commercials`.

## Domain ownership

- `moneybird` owns estimates, invoices, recurring billing, open balances, and finance safety; Rabobank owns observed bank receipts. Do not duplicate passive monitoring in Notion when the native system already surfaces it reliably. Create a Task only for an explicit action, decision, exception, approval, or cross-system follow-up that the native system does not own.
- `productive-io` owns hours evidence and time-entry writes.
- `monday-com` owns individual customer execution tickets. Do not copy those tickets into Notion. A bounded weekly Notion Task may still represent Sil's personal Fayn or TEVEO delivery commitment across monday tickets; monday remains the execution-detail source.
- `trackler-nl` owns its read-only coaching context.
- `customer-work` owns scoped customer execution, customer-visible QA, preview, approval, release, and handoff.
- `customer-communication` owns customer-facing messages and their output format.

## Approval and completion

Obtain explicit approval before sending customer or vendor messages, publishing customer work or Moneybird documents, changing unclear finance data, deleting records or data, scanning broad private sources, restructuring databases or templates, or changing automation schedules.

Complete an in-scope change after proportional verification through tests, builds, browser checks, API readback, screenshots, document validation, or source confirmation. Append the durable result, verification evidence, decisions, and useful links as a source-grounded Timeline event, then update canonical properties.

When updating both a Task body and properties, write the body first and the canonical properties last, then read the page back. Workspace automations or Markdown page updates may reapply Sprint or Due defaults; for `Canceled` Tasks, explicitly clear Sprint and Due in the final property write and verify both are empty.

Use a concise numbered list for operational reports, multiple actions, decisions, blockers, or approval questions. Use `customer-communication` formatting for customer drafts.
