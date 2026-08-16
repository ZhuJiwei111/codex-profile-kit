# Current-Host Task Inventory

Use this reference only for the host where the calling Codex task is executing.
The procedure is the same on Windows, macOS, and Linux; only host-native path
and shell syntax may differ.

## Freeze The Host Scope

- Derive the current host identity from the calling task or a product surface
  that identifies it before returning task data.
- Use that same exact identity for every product query and mutation in the run.
- Treat an unknown host identity as a mutation blocker.
- Do not accept another host's ID, filesystem path, index content, or task list
  into this inventory. Manage another host from a task executing there.

## Safe Candidate Source

Prefer a product query that filters to the frozen host before results enter
context. When that surface is unavailable or incomplete, read only the current
host's own Codex metadata:

1. Resolve `CODEX_HOME` from the current process or current-host contract;
   otherwise use the current user's standard `~/.codex` directory.
2. Read `session_index.jsonl` explicitly as UTF-8 with an already-available
   host-native JSON parser. Project only task ID, title, and update time.
3. Read filenames under `archived_sessions/` only to identify archived task
   IDs.
4. Subtract archived IDs from index candidates. Treat the result as discovery,
   not as a mutation list.

Use `pwsh` on Windows and available POSIX-native tooling on macOS or Linux. Do
not install a parser merely for inventory. If safe parsing is unavailable,
report the evidence gap and stop before mutation. Never follow rollout/session
paths from the index or transfer the index to another host for processing.

## Product Reconciliation

- Avoid an unfiltered global task list while multiple hosts are connected.
- Project safe product metadata first and apply the exclusions in `SKILL.md`.
- Sort the remaining candidates by oldest substantive activity first and
  exact-read no more than the current run's bounded batch.
- Classify `No Codex thread found` once as index-only, stale, or unsupported;
  do not retry it as an archive operation.

After execution, verify only each actual archive target on the frozen host. Do
not re-read protected or main tasks merely to prove they were preserved. Do not
use an app-wide list or cross-host count as proof of archival.
