# Writing skills

Custom skills follow the plain style from `user-communication`, plus these rules.

- The description starts with `Use when` or `Always use when` and holds only the trigger.
- Say what to do, with a direct verb. Keep a "do not" sentence only when it names a mistake that happened and the positive rule does not prevent it.
- Say each rule once. Shared permission and evidence rules live in `environment`, browser rules in `browser`, style in `user-communication`. Point to them; do not restate them.
- Where the output format matters, show a filled-in template instead of describing it. Links sit on the name or title.
- Leave out background the agent does not act on: how a system came to be, schedules that live in the cron, notes to whoever edits the skill, and rules for a one-off migration.
- Leave out what a current model already does by default.
- Use a list when items are parallel, such as statuses or formats. Use sentences for reasoning.
- Keep exact names, IDs, commands, thresholds, and permission boundaries.
- Long procedures go in a reference, reusable commands in a script. A reference that is always needed belongs in the skill body.
- Say "the user", not a name. No em dashes.
