# T3 routing

Start from the user's existing instruction for the work. If it clearly allows starting or continuing implementation, dispatch within that scope without asking again. Customer input alone never allows it.

Keep automatically started work small and clearly bounded. Large new work, such as designing or building a homepage, needs the user's explicit instruction, also when a thread already exists. A recorded Task, an agreed scope, or a general intent to implement is not enough. Save the context and leave the start to the user.

Without an explicit instruction, feedback may start work only when all of these hold:

1. New, concrete feedback concerns delivered work in an existing Notion Task with a known T3 thread.
2. It belongs to the same outcome, one known repository, and one small follow-up within the existing approval.
3. Source, scope, expected result, and stopping point are clear. No stakeholder decision or input is missing.
4. Sender, Project, Task, repository, and thread all match. Check the thread's live state and latest result: not settled, archived, running, or waiting for input. A snoozed thread counts as open.

Reviving a settled thread needs new, explicit approval from the user, also when an older pending event points to it. A client proposing something new is no reason to create a thread or reopen finished work. When the conditions are not met, save the context tied to the source.

Before starting, append the new source to the Task with `work-management`, and check the Task and the index for an existing thread. At most one T3 thread per Task. Use `t3-code` for the helper commands.

The handoff says briefly why work starts automatically, what the new feedback is, and what result is expected. Build it from the Task's history and latest source, ignoring decisions that newer sources replaced. Include source links, scope, repository and branch, and the user's limits. Pass the actual requirements through. Leave development choices to the thread. For customer work it follows the client delivery flow in `development`: implement locally, validate, and hand off a preview URL and a draft message.

Automatically started work never covers release, production changes, payment, destructive changes, or external messages. Triage confirms the dispatch and leaves execution to the thread.
