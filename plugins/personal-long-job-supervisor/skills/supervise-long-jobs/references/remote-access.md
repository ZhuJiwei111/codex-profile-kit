# SSH remote access

The managed plugin source owns both controller and remote code. Deploy its
`scripts/` directory to a persistent remote path; Python 3.9+ and SSH are enough.
Check the executing runtime’s `release_version` in capabilities (older versions may omit it). A running worker keeps its deployed version until completion. No daemon,
watchdog, scheduled task, or model relay is installed.

## One connection owner

Project `.local/connections.json` owns current SSH target aliases, default target,
and runtime locations; `.local/ssh_config` owns SSH transport. Keep `.local/`
private and ignored by Git. Example (replace paths from the actual project):

```json
{
  "default_target": "main",
  "targets": {"main": {"ssh_alias": "project-main"}},
  "supervisor": {
    "python": "/absolute/python3",
    "entry": "/shared/tools/supervisor/scripts/remote.py",
    "state_root": "/shared/project/.local/supervisor-state"
  }
}
```

For shared container pools, `.local/connections.json` and `ssh_config` are
symlinks to host-private shared files. The shared JSON owns `targets`,
`default_target` and common `supervisor.python`/`supervisor.entry` settings.
The adjacent `.local/project.json` stores only project-specific settings such
as `worktree`, optional `target_worktrees`, and `supervisor.state_root`.
The controller reads targets and the default exclusively from the shared file;
project supervisor settings override shared runtime settings only when needed.
Changing the shared default affects new calls in every project; existing job
locators retain their original target and state root. Combined configurations
without a project.json remain supported.

Automated `.local/supervisor/jobs/<job-id>.json` locators hold only the selected
connection target and shared state path. The plugin controller's `remote_jobs/`
index points to the project. Neither stores duplicated status or SSH credentials.
Native remote `jobs/<job-id>/` owns registration, worker/target identities, logs,
events, acknowledgments and result. Multiple nodes may use the same state root.

## Launch and consume

Run these commands with the controller's absolute Python and installed plugin:

```text
<python> <plugin>/scripts/remote.py --project <project> capabilities
<python> <plugin>/scripts/remote.py --project <project> [--target <target>] start --name <name> --cwd <remote-cwd> -- <remote-executable> <args>...
<python> <plugin>/scripts/remote.py --project <project> status <job-id>
<python> <plugin>/scripts/remote.py --project <project> wait <job-id> [<job-id>...]
<python> <plugin>/scripts/remote.py --project <project> ack <job-id> <event-id>
```

`start --stage-path <remote-path>` uses the same task-owned snapshot interface as
local jobs; stage events persist on the execution host across SSH disconnects.

Start validates the selected target, then reserves the ID locally before sending SSH. On an uncertain response,
inspect the reported ID or repeat the same start with `--request-id <job-id>`
and identical inputs. Reservation is atomic: repeat calls never launch again;
a reservation without a confirmed worker reports uncertainty. Diagnose that
reservation before explicitly authorizing another job. Changed inputs under the
same ID are rejected. Cleaned request IDs cannot be replayed.

MCP `wait_any` groups local and remote registrations by their execution target.
The SSH wait uses the native store in bounded requests and preserves interruption
tokens across requests. Cancelling a wait closes only its SSH transport; events
and worker execution remain intact. SSH failure is an observation error, never
proof of target failure or permission to restart it.

## Reconnect and shared-disk recovery

Default target changes affect new starts only. Existing locators keep their target.
When the connection owner exits a target, remove its live connection registration
and precise SSH trust entry; connection removal does not require proof of platform
release. Preserve existing job locators and their original target/state_root.
Reading old records uses the recovery routes below; discarding native run records
with `clean --released-host` still requires confirmed release and evidence handoff.
Do not keep dead SSH routes for historical results. Shared job records contain execution identity, not SSH
credentials. A new container's matching PID is never treated as the old process.

```text
<python> <plugin>/scripts/remote.py --project <project> --via <current-target> status <job-id>
<python> <plugin>/scripts/remote.py --project <project> --target <current-target> recover
```

`recover` rebuilds disposable local locators from the configured shared state root.
Existing locators whose targets remain registered are preserved. Missing or released
routes are rebuilt through the selected target only for a matching execution host
or an existing terminal result. Other nonterminal jobs are returned as `unresolved`;
run recovery through their actual execution target to restore those routes. If that
container was released and the local locator is missing, explicit `--via <current-target>
status <job-id>` reads the configured shared records without creating a locator or
authorizing cleanup. Recovery
never silently binds all active jobs to one node.

Terminal results and original event IDs remain readable from shared storage.

When the owner has explicitly confirmed that the original execution instance was
released, preserve required research evidence outside the disposable job directory,
then discard its runtime records through a current shared-disk target:

```text
<python> <plugin>/scripts/remote.py --project <project> --target <current-target> clean <job-id> --released-host
```

This flag is the caller's confirmation of release and evidence handoff, not a
deduction from SSH failure or removal of a connection entry. It accepts only a
different remote execution instance, does not inspect or signal its old PID, and
does not invent a completed/failed result. It removes the job directory and local
locators, retaining only the existing request replay guard. Artifacts outside the
job directory remain untouched. Ordinary `clean` retains its normal terminal and
acknowledgment checks; no bulk or automatic cleanup is added.

Without a result, a foreign execution identity returns `execution_host_unverified`
and does not append an error event or inspect a local PID. Waiting requires the
actual execution target; an unverified member does not prevent other verified
members in a multi-job wait from delivering events. Recovery restores observation; resuming scientific work
from a checkpoint belongs to its authorized task owner. Local jobs keep their
native PID/start identity behavior even if the controller hostname changes. Linux
boot and PID-namespace identity checks remain active for both local and remote jobs.

Remote events use atomic directory locking on shared storage. Locks cover only
read/modify/write operations, never execution or SSH waits. An abandoned lock is
reported; it is not stolen by age. Inspect its owner and confirm no active writer
before removing exactly that abandoned lock. Validate the filesystem primitive
on the actual deployment; one-node tests are not a cross-node guarantee.

A monitor/lock failure does not stop the worker from waiting for its target.
Diagnostics go to its existing log; a terminal result is saved independently of
the event lock. A still-pending monitor error is retained in that same result
record so reconciliation can publish it without a separate ledger. Once the lock is usable, inspection can reconcile the terminal
event. Monitor sampling happens outside the event lock; only its sole owning
worker updates monitor states, while event IDs and acknowledgments merge under
the shared lock. No additional observer or automatic lock stealing is involved.
