# Health on both Macs

Run local checks on both machines with one shared script. MacBook submits its latest result to Otis. Otis combines both results and reports changes in Telegram System. The [job inventory](otis.md#scheduled-work) lists schedules and source locations.

## Checks and status

Both Macs check the local account proxy, the routing receipt and free disk space. Routing must report `ok: true`, `apply: true`, and a run within 45 minutes. After MacBook wakes from a gap longer than 45 minutes, give routing 15 minutes to catch up. Warn below 10 GiB or 5% free disk space. Backup setup and iCloud sync are intentionally excluded.

Otis also checks OpenClaw, T3 and its saved Connect configuration, WhatsApp, Google access, contact sync, work-triage, weekly-planning and system-hygiene. A configured T3 connection is not proof of live relay connectivity. Agent jobs get a 45-minute completion grace; contact sync gets one hour. Disabled jobs are skipped. OpenClaw's existing automatic gateway restart remains enabled. Other checks only observe.

Read without starting jobs, sending messages or creating threads:

```bash
python3 -B ~/.agents/skills/system-hygiene/scripts/health.py --machine macbook --collect
ssh -A otis 'python3 -B ~/.agents/skills/system-hygiene/scripts/health.py --machine otis --collect'
ssh -A otis 'python3 -B ~/.agents/skills/system-hygiene/scripts/health.py --status'
```

Machine-local files under `~/.local/state/fulldev/health/`:

| File | Purpose |
|---|---|
| `local.json` | Last local check on either Mac |
| `macbook.json` | Last accepted MacBook report on Otis, with receipt time |
| `report.json` | Combined checks and incident references on Otis |
| `state.json` | Check state, incident IDs, last delivered alert and pending delivery |
| `install-backups/` | Previous Otis health LaunchAgent |

Logs are in `~/Library/Logs/fulldev/health.log`. `launchctl print gui/$(id -u)/com.fulldev.health` shows the schedule, process and last exit status. Exit 2 means a detected problem or a failed status/report delivery; exit 1 means the script failed. The shared code lives in `skills/system-hygiene/scripts/health.py` and `health-checks.py`. The monthly Otis restart imports the same service checks.

MacBook status older than 45 minutes is unknown, never healthy. An offline transition alone sends no alert and does not resolve an existing incident. MacBook keeps its last local result and submits a fresh result on the next run. Otis can continue checking itself when MacBook is offline. A total Otis outage cannot report itself.

## Delivery and incident threads

Only Otis sends combined alerts to Telegram System. Save the delivered fingerprint only after the send command succeeds. Retry failed delivery on the next run, using the latest combined state. Use `--machine otis --run --notify-now` for an authorized one-off combined report.

A problem needs two distinct observations at least 15 minutes apart before an investigation thread is started. Repeated reads of one MacBook receipt do not count. Start at most one thread per health run. Keep one thread for the duration of an incident; save its ID before creating it and check for an existing turn before retrying. A fresh passing check closes the incident locally. A recurrence after recovery is a new incident. Keep the last incident per machine/check, rather than an unbounded event history.

Create threads in Otis's `agents` T3 project with Astra high and approval-required mode. The first turn is explicitly read-only: inspect the current evidence, explain the cause, propose a next step, then stop. It must not change settings, restart services, send messages or start recurring work. The user handles follow-up in that thread. Failed T3 creation is saved as `thread_error` and retried; Telegram reporting continues independently. The link uses T3 Connect and requires the user's existing T3 login.

## Restricted status submission

MacBook's dedicated key is `~/.ssh/id_ed25519_health`. Its SSH config is `~/.config/fulldev/health-ssh.conf`. It uses the verified Otis host key, no agent, no forwarding and a short timeout. It works unattended without exposing the general SSH key.

Otis's `authorized_keys` entry uses `restrict` and a forced `health.py --receive` command. Only the original command `health-submit` is accepted. The receiver accepts at most 8 KiB within 10 seconds, fixed MacBook check names, boolean results and a recent timestamp. It refuses older or conflicting receipts. It cannot accept shell commands, paths, diagnostic prose or credentials. The key grants no shell, PTY, port forwarding or access from Otis to MacBook.

## Installation

Pull the reviewed `agents` commit on both Macs first. Keep credentials and machine configuration outside Git.

On MacBook, create the dedicated key and config before enabling its job:

```bash
python3 -B ~/.agents/skills/system-hygiene/scripts/install-health.py --machine macbook --configure-only
```

Copy only its `.pub` file to Otis through the existing administration connection. On Otis, authorize it and select the existing T3 project:

```bash
python3 -B ~/.agents/skills/system-hygiene/scripts/install-health.py \
  --machine otis --project-id 10963dc2-a788-4eb9-8415-f42942a64f9a \
  --public-key /path/to/macbook-health.pub --configure-only
```

Then run the installer without `--configure-only` on each machine. Otis remembers its project ID in `~/.config/fulldev/health.json`. The installer replaces `com.fulldev.otis-health` with `com.fulldev.health` and saves the old plist. It refuses to unload a currently running health task. Both jobs run at login and every 15 minutes; routing keeps its own independent job.

Verify a MacBook submission, a fresh combined report, launchd exit statuses and the continued routing jobs. Exercise receiver rejection, stale/offline reporting, delivery retry and thread deduplication with isolated temporary state before deployment. Send one combined activation report after verifying both machines.
