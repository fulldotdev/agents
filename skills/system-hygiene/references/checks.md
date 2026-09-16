1. **Skills and instructions.** Check the custom skills in `~/.agents/skills` against these rules and propose fixes for what drifted:
   - The description starts with `Use when` or `Always use when` and contains only the trigger, not body rules.
   - Sentences use everyday words and direct verbs, one job per sentence, no em dashes, and say "the user", not a name.
   - Each rule appears once. The shared permission and evidence rules live only in `environment`. A tool skill does not restate them, and two skills do not describe the same responsibility.
   - No text about retired systems or old workflows, no dated provenance that the agent does not need, and nothing a current model already knows or does by default.
   - Links between skills and references resolve, commands still match the installed tools, and no `__pycache__`, empty folders, or stray files sit inside a skill.
   Installed skills update through their own path, not local edits. Shared conventions belong in `~/.agents`, project instructions in their repositories.

2. **Files and storage.** Measure free space and meaningful growth. Look at large temporary files, downloads, trash, caches, and old backups. For each deletion candidate, say what it is for and whether it can be recovered. Library holds settings and app data, so never treat it as a cache. Separate logical folder size from reclaimable space, especially with APFS clones and hard links.

3. **Projects.** Look for abandoned generated output, temporary copies, and stale checkouts. Read Git status, worktree ownership, and process use. Keep uncommitted files and unique commits. A Git bundle can keep unique history when removal is approved separately. pnpm already shares package data, so look at store versions and unused packages instead of proposing deduplication. `.dev` can hold source and review work, not only disposable output.

4. **Previews and processes.** Find local servers, editor processes, and tunnels that look abandoned. Match each to its project, output path, and owner before proposing a shutdown. Open files, process arguments, and listeners are evidence. A `dist` or cache directory may power a preview used daily. Never stop it during inspection.

5. **Automations.** Compare `openclaw cron list` and the launchd plists on Otis with `~/.agents/operations/openclaw-otis.md`. Flag one-off jobs that ran or expired, duplicates, disabled leftovers, and jobs with recent failures, and propose deleting them. A successful run does not prove delivery. Do not rerun jobs, dig into business decisions, or rebuild a workflow as maintenance. Respect deferred investigations. Some system-owned jobs cannot be removed through the CLI; do not work around that.

6. **CLI tooling.** Compare command resolution, installed versions, and dependencies across both Macs. Look for stale shims and competing installs. Different Node versions or machine-specific tools are fine unless they cause a problem. Use each machine's own package manager. Credentials and machine config stay local.

7. **Sync and Git.** Compare shared skill and instruction commits across both Macs. Find uncommitted or unpushed work that may be forgotten. Tell intentional divergence apart from active work, and look before suggesting a sync. Never switch branches, merge, or push during the audit. A push to a connected Shopify branch can change a live theme.

8. **Apps, plugins, and models.** Monthly, look for duplicate or superseded installs and large downloads or models. Check real workflow references and use before proposing removal. A missing usage timestamp does not prove an app is unused. State the saving and the effect on work. An admin-password prompt means the user must act; do not bypass macOS.
