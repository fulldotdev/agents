# Browser access failures

Follow the work-profile selection in the `environment` skill. On Otis, OpenClaw normally uses the `chrome` extension connection. Check `openclaw browser status --json` and `openclaw browser extension status --json`; a failing extension connection is not a reason to enable Remote Debugging or switch to `user`.

For `Target identities are unavailable`, a Chrome Web Store tab prevented tab enumeration during setup. Close it if it belongs to the current task, then retry; preserve the user's tabs.

If a task explicitly uses remote-debugging attach, recommend enabling Chrome Remote Debugging only after verifying that its switch is disabled on the target machine. `browser_consent_required`, `consumer_profile_endpoint_requires_grant`, or an approval popup that cannot be found or accessed mean connection approval is blocked, not that Remote Debugging is disabled. Report the exact approval/access blocker and target machine; if the popup is inaccessible or the remedy is unknown, say so rather than inventing a fix.
