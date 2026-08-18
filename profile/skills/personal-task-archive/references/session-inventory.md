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

## Complete Metadata Source

Use the first available source that is both host-local and complete:

1. Prefer a product query that applies the frozen host filter before returning
   data, exposes source or parent metadata, and pages to exhaustion.
2. Otherwise initialize a local app-server on the current execution host and
   page `thread/list` with `archived=false`, `useStateDbOnly=true`, a bounded
   page size, every supported source kind, and each returned cursor until no
   cursor remains. Project only task ID, title, update time, status, source or
   parent metadata, and hard-protection signals. Do not request turns.
3. If neither source is available, use the current host's metadata index only
   as incomplete discovery:

   1. Resolve `CODEX_HOME` from the current process or current-host contract;
      otherwise use the current user's standard `~/.codex` directory.
   2. Read `session_index.jsonl` explicitly as UTF-8 with an already-available
   host-native JSON parser. Project only task ID, title, and update time.
   3. Read filenames under `archived_sessions/` only to identify archived task
   IDs.
   4. Subtract archived IDs from index candidates.

The index fallback cannot establish a raw main-task/subAgent split because its
safe projection lacks source and parent metadata. Report that split as unknown,
identify the fallback as incomplete, and require exact product reads to confirm
host identity and every protection signal before any candidate can become an
automatic archive.

Use `pwsh` on Windows and available POSIX-native tooling on macOS or Linux. Do
not install a parser merely for inventory. If safe parsing is unavailable,
report the evidence gap and stop before mutation. Never follow rollout/session
paths from the index or transfer the index to another host for processing.

An app-wide list that accepts only a global limit, mixes hosts, or omits
delegated children is a navigation surface. Do not filter it after retrieval
and present the remainder as a complete current-host inventory. A full page,
an unexhausted cursor, missing host identity, or missing source metadata is an
explicit completeness gap rather than evidence that no more subAgents exist.

## Product Reconciliation

- Avoid an unfiltered global task list while multiple hosts are connected.
- Record the raw unarchived main-task and subAgent totals before applying the
  exclusions in `SKILL.md`; keep total, protected, eligible, read, and
  deferred counts distinct.
- Sort the remaining candidates by oldest substantive activity first and
  exact-read no more than the current run's bounded batch.
- Classify `No Codex thread found` once as index-only, stale, or unsupported;
  do not retry it as an archive operation.

After execution, verify only each actual archive target on the frozen host. Do
not re-read protected or main tasks merely to prove they were preserved. Do not
use an app-wide list or cross-host count as proof of archival.
