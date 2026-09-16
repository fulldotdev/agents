# Browser access failures

On Otis, OpenClaw uses the `chrome` extension connection. Check `openclaw browser status --json` and `openclaw browser extension status --json`. A failing extension connection is no reason to switch to another profile or enable Chrome Remote Debugging.

`Target identities are unavailable` means a Chrome Web Store tab blocked tab enumeration during setup. Close it if it belongs to this task, then retry. Leave the user's tabs alone.

`browser_consent_required`, `consumer_profile_endpoint_requires_grant`, or an approval popup you cannot find means connection approval is blocked. Report the exact blocker and the machine. If the fix is unknown, say so instead of inventing one.
