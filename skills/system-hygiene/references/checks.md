# Periodic checks

1. **Skills and instructions.** Check for duplicate responsibilities, contradictions, stale commands, broken links, and missing required dependencies. Keep shared conventions in `~/.agents`, project instructions in their repositories, and development execution details out of triage. Compare distinct triggers before proposing consolidation. Update vendor skills through their supported path. Do not rewrite them locally.

2. **Files and storage.** Measure free space and meaningful growth. Inspect large temporary files, downloads, trash, caches, and old backups. Explain each deletion candidate's purpose and recoverability. Library also holds settings and app data, so never treat the whole directory as a cache. Distinguish logical folder size from reclaimable space, especially with APFS clones and hard links.

3. **Projects.** Look for abandoned generated output, temporary copies, and obsolete checkouts. Read Git status, worktree ownership, and relevant process use. Preserve uncommitted files and unique commits. A Git bundle can retain unique history when removal is separately authorized. pnpm already shares package data, so inspect store versions and unused packages instead of proposing generic deduplication. `.dev` can contain source and review work, not only disposable output.

4. **Previews and processes.** Identify local servers, editor processes, and tunnels that appear abandoned. Match each one to its project, output path, and current owner before recommending shutdown. Open files, process arguments, and listeners are evidence. A `dist` or cache directory may power a preview used every day. Never stop it during inspection.

5. **Automations.** Compare `openclaw cron list` and the launchd plists on Otis with `~/.agents/operations/openclaw-otis.md`. Flag one-off or temporary jobs that have run or expired, duplicates, disabled leftovers, and jobs with recent failures. Propose deleting them. A successful run does not prove delivery. Do not rerun jobs, inspect business decisions in depth, or rebuild a workflow as routine maintenance. Respect previously deferred investigations. Some system-owned jobs cannot be removed through the ordinary CLI. Do not bypass that restriction.

6. **CLI tooling.** Compare actual command resolution, installed versions, and required dependencies across Macs. Detect stale shims and competing installations. Different Node versions or machine-specific tools are not defects unless they cause a problem. Use each machine's existing manager. Credentials and machine configuration remain local.

7. **Sync and Git.** Compare shared skill and instruction commits across Macs. Identify uncommitted or unpushed work that may be forgotten. Distinguish intentional divergence from active work. Inspect before suggesting a sync. Never switch branches, merge, or push as part of the audit. A push to a connected Shopify branch can change a remote theme.

8. **Apps, plugins, and models.** Each month, inspect duplicate or superseded installations and large downloads or models. Check actual workflow references and active use before proposing removal. A missing usage timestamp does not prove that an app is unused. State the concrete savings and how removal would affect work. An admin-password requirement calls for user action and does not permit bypassing macOS.
