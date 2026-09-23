# Writing skills

Custom skills and `~/.agents/global/AGENTS.md` follow its plain style, plus these rules.

- The description starts with `Use when` or `Always use when` and holds only the trigger.
- Say what to do, with a direct verb. Keep a "do not" sentence only when it names a mistake that happened and the positive rule does not prevent it. Remove it when the mistake stops recurring.
- Say each rule once. Style, permission, and evidence rules live in `~/.agents/global/AGENTS.md`, browser rules in `browser`. Do not restate them in a skill.
- Where the output format matters, show a filled-in template instead of describing it. Links sit on the name or title.
- Leave out background the agent does not act on: how a system came to be, schedules that live in the cron, notes to whoever edits the skill, and rules for a one-off migration.
- Leave out what a current model already does by default.
- Use a list when items are parallel, such as statuses or formats. Use sentences for reasoning.
- Keep exact names, IDs, commands, thresholds, and permission boundaries.
- Long procedures go in a reference, reusable commands in a script. A reference that is always needed belongs in the skill body.
- Say "the user", not a name. No em dashes.
