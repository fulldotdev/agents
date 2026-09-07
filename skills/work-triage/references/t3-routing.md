# T3 routing

Notion is the source of truth. T3 is an optional execution surface for small, bounded work with high confidence.

## Create or resume threads

Create or resume a T3 thread only when every condition is true:

1. A concrete, source-grounded Task exists or can be created without ambiguity.
2. The work has one deliverable in one known repository or workspace and fits one short cycle ending at review or preview.
3. The request, owning project, source, scope, and stopping boundary are clear.
4. No stakeholder decision, clarification, or approval is needed before work starts.

Update the Task and Timeline first. Check the thread index and live status before creating or resuming. Store the stable T3 environment, project, and thread locator in the Timeline.

### User-visible handoff

The dispatch prompt appears in Sil's existing thread. Write it for him, not as orchestration metadata.

Open with a natural sentence such as: `This is an automatic follow-up from heartbeat triage. A customer added new feedback to the existing task, so I reopened this thread.` Then summarize what changed and what the agent will do in plain language. Put references and links after the explanation. Include scope and safety limits without internal orchestration labels.

Make sure the final reply in the thread briefly explains why this has been started automatically, instruct the thread to include this brief intro. The reader must understand the trigger, result, and next action without opening linked sources, task records, or technical artifacts.

T3 may implement, test, and prepare a preview within scope. Merge, release, publish, payment, destructive changes, and external communication still need approval.

You run from Otis; when providing the user with preview urls always use tailscale hosted urls.
