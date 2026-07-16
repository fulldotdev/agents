---
name: system-hygiene
description: "Keep Hermes-owned operating context, skill routing, cron jobs, and generated workspace clutter clean when there is concrete evidence."
---

# System Hygiene

Use this to keep the Hermes workspace clean, current, and low-noise. This is not a workflow-improvement review, broad infra audit, or treasure hunt for random findings.

Default stance: only act or report when the issue is concrete, evidenced, and likely to reduce routing risk, stale references, broken config, or obvious generated clutter.

## Scope

Inspect only the smallest useful set:

1. Live Hermes context files: `~/.hermes/SOUL.md`, project `.hermes.md`, `HERMES.md`, cwd `AGENTS.md`, cwd `CLAUDE.md`, cwd `.cursorrules`, and relevant `.cursor/rules/*.mdc`.
2. Hermes-owned skills: names, descriptions, folders, supporting files, and active path references under `~/.hermes/skills/` and the shared `~/.agents/skills/` source tree when it is being mirrored/imported.
3. Cron jobs: names, descriptions, payload skill names, schedules, scripts, workdirs, context chaining, and delivery targets.
4. Hermes config references: platform routing, toolsets, MCP names, gateway delivery targets, and paths that affect execution.
5. Generated clutter: Hermes-owned `tmp`, `.tmp`, `cache`, `.cache`, `artifacts`, generated output, obsolete backups, and failed-run leftovers under `~/.hermes/` or clearly Hermes-managed workspaces.

Use `agency-work` for triage, planning, delivery, and Notion-backed work itself.

## Worth Reporting

Report only:

1. A stale or broken reference that can affect routing or execution.
2. Duplicate or conflicting live instructions.
3. A skill/cron name, description, payload, or linked file that no longer matches behavior.
4. Hermes-generated clutter that is clearly obsolete, large, empty, or unreferenced.
5. A `hermes doctor`, gateway, cron, tool, or skill finding that requires a real decision or follow-up.
6. A cleanup action that was actually taken.

Suppress:

1. Rediscovered facts.
2. Tiny harmless files.
3. "Could maybe" findings.
4. Recommendations without a concrete action.
5. Style tweaks with no routing or correctness impact.
6. Daily memory/log/transcript observations.

If nothing passes the value filter, say so and stop.

## Safe Direct Actions

Direct cleanup is allowed only when all are true:

1. The target is Hermes-owned generated clutter.
2. It is not a log, transcript, session history, memory file, customer file, project source file, or active config file.
3. Evidence shows it is empty, obsolete, duplicated, failed-run residue, or superseded.
4. The action is low-risk and local.

Examples:

1. Empty generated temp/cache/artifact directories.
2. Failed-run leftovers with no live references.
3. Obsolete generated output under Hermes tmp/cache/artifact locations.
4. Old Hermes-generated backups clearly superseded by current files.
5. Duplicate disabled plugin/MCP caches when an active newer copy exists.

Recommend instead of doing when ownership, value, or risk is ambiguous.

## Never Touch

Never clean, trim, compress, rewrite, or delete:

1. Logs, transcripts, session history, or state databases.
2. Hermes memories or user profile data.
3. Customer/project source data, repos, app code, or client files.
4. Notion work/customer/project records.
5. Broad caches without clear age/reference evidence.

Do not change cron schedules, delivery targets, live config, skills, plugins, or MCP definitions unless the user explicitly asked for that specific change.

### External skills CLI safety

- `npx skills update --help` is not a safe help probe in the current Vercel Skills CLI: it executes an update. Use top-level `npx skills --help` for documented update flags, or inspect the upstream CLI docs/source. Treat `skills update` as a mutating command and check Git status afterward.

## Run Shape

1. Inspect only relevant files/config for the trigger.
2. Apply the value filter before reporting.
3. Do safe direct cleanup only when evidence is clear.
4. Keep recommendations rare and concrete.
5. Stop early when no useful hygiene issue is found.

Do not run a deep audit unless explicitly asked.
Do not run `hermes update`, alter profiles, or restart the gateway automatically; report when those need a real decision.

## Output

Return one concise numbered list. One item = one action, concrete recommendation, blocker, or failure.
Report only real actions/results. Do not mention internal checks, skipped items, backup creation, dedupe/verification passes, or "nothing changed" details unless the user explicitly asked for them.

Use prefixes:

- `Context:`
- `Skill:`
- `Cron:`
- `Config:`
- `Artifact:`
- `Cleanup:`
- `Doctor:`
- `Update:`
- `Blocked:`
- `Failed:`

Preferred shapes:

```md
1. Cleanup: `/path` removed empty generated directory.
2. Cron: `name` payload referenced stale skill name; recommend exact replacement.
3. Config: `gateway.home_channels` references removed Slack target; recommend exact replacement.
4. Artifact: `/path` 180MB/45d -> recommend delete; generated cache with no live reference.
```

If nothing passes the value filter, output exactly:

```md
1. Cleanup: no hygiene changes or cleanup candidates found.
```
