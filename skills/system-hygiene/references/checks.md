# Periodic checks

1. **Skills and instructions.** Check duplicate responsibilities, contradictions, stale commands, broken links and missing required dependencies. Keep shared conventions in `~/.agents`, project instructions in their repositories, and development execution details out of triage. Judge distinct triggers before proposing consolidation. Vendor skills use their supported update path; do not rewrite them locally.

2. **Files and storage.** Measure free space and meaningful growth. Inspect large temporary files, downloads, trash, caches and old backups. Explain each deletion candidate's purpose and recoverability. Library also holds settings and app data: never treat the whole directory as a cache. Distinguish logical folder size from reclaimable space, especially with APFS clones and hard links.

3. **Projects.** Look for abandoned generated output, temporary copies and obsolete checkouts. Read Git status, worktree ownership and relevant process use. Preserve uncommitted files and unique commits; a Git bundle can retain unique history when removal is separately authorized. pnpm already shares package data: inspect store versions and unused packages rather than proposing generic deduplication. `.dev` can contain source and review work, not just disposable output.

4. **Previews and processes.** Identify local servers, editor processes and tunnels that appear abandoned. Match each to its project, output path and current owner before recommending shutdown. Open files, process arguments and listeners are evidence; a `dist` or cache directory may power a daily-used preview. Never stop it during inspection.

5. **Automations.** Read schedules and recent run/delivery status for expired one-offs, duplicates, stale disabled jobs and actionable failures. A successful run does not establish delivery. Do not rerun jobs, inspect business decisions in depth, or rebuild a workflow as routine maintenance. Respect previously deferred investigations. Some system-owned jobs cannot be removed through the ordinary CLI; do not bypass that restriction.

6. **CLI tooling.** Compare actual command resolution, installed versions and required dependencies across Macs. Detect stale shims and competing installations. Different Node versions or machine-specific tools are not defects without consequences. Use each machine's existing manager; credentials and machine configuration remain local.

7. **Sync and Git.** Compare shared skills/instruction commits across Macs and identify uncommitted or unpushed work that may be forgotten. Distinguish intentional divergence and active work. Inspect before suggesting sync; never switch branches, merge or push as part of the audit. A push to a connected Shopify branch can change a remote theme.

8. **Apps, plugins and models.** Monthly, inspect duplicate or superseded installations and large downloads/models. Check actual workflow references and active use before proposing removal. No usage timestamp is not proof an app is unused. List concrete savings and how removal affects work; an admin-password requirement is a user action, not permission to bypass macOS.
