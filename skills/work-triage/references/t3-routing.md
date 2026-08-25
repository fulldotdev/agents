# T3 routing

Notion is the source of truth. T3 is an optional execution surface for small, bounded work with high confidence.

## Dispatch gate

Create or resume a T3 thread only when every condition is true:

1. A concrete, source-grounded Task exists or can be created without ambiguity.
2. The work has one deliverable in one known repository or workspace and fits one short cycle ending at review or preview.
3. The request, owning project, source, scope, and stopping boundary are clear.
4. The work is low-risk and reversible. It excludes release, deploy, merge, publish, payment, data deletion or migration, credential or security changes, external communication, and unresolved product, architecture, pricing, or scope decisions.
5. No stakeholder decision, clarification, or approval is needed before work starts.
6. The target thread is not running or waiting for approval or user input.

If a condition fails, stop at preparation. Preserve the source, update the Task and Timeline, prepare a native draft when useful, and record the exact missing decision. Research may prove the gate passes. Remaining uncertainty means it does not.

## Create or resume

- Create a thread only when an eligible Task has no owning T3 thread.
- Resume only when new actionable input belongs to the same Task and outcome, stays within its scope, and removes a blocker or gives concrete direction.
- New feedback, a Task status change, or an existing thread is not enough by itself.
- A Task may have one owning T3 thread. Use a separate Task for another stakeholder or independent outcome.

Update the Task and Timeline first. Check the thread index and live status before creating or resuming. Store the stable T3 environment, project, and thread locator in the Timeline.

### User-visible handoff

The dispatch prompt appears in Sil's existing thread. Write it for him, not as orchestration metadata.

Open with a natural sentence such as: `This is an automatic follow-up from heartbeat triage. Franziska added new feedback on the existing task, so I reopened this thread.` Then summarize what changed and what the agent will do in plain language. Put the Task and source links after the explanation. Include scope and safety limits without labels such as `Owning Task`, `New source`, `bounded feedback`, or `stopping boundary`.

End the prompt with these response requirements:

- The agent's first user-visible message says that heartbeat triage started the turn and why.
- The final reply opens with why the turn started automatically and what the agent did.
- The final reply explains the result and Sil's next action before mentioning files, commits, tests, IDs, or vendor internals.
- Technical detail appears only when it helps Sil review the work or act on a blocker.

The reader must understand the trigger, result, and next action without opening monday, Notion, or the code diff.

After a turn starts, record the dispatch and set the Task to Doing. A finished T3 turn does not prove the Task is Done; use the verification rule in `work-management`.

Triage ends after context updates, native drafts, appropriate Gmail archival, and T3 dispatch. T3 may implement, test, and prepare a preview within scope. Merge, release, publish, payment, destructive changes, and external communication still need approval.
