---
name: personal-thread-closeout
description: Manual only. Use from a separate controller task to assess and archive one exact current-host Codex task, an exact ID list, or an explicitly requested sweep of one exact current-host project; preserve worthwhile project knowledge and archive each ready task last.
---

# Personal Thread Closeout

Close only explicitly selected tasks from a different controller task. Keep the
controller alive to report results and never archive the controller itself.

This workflow may assess readiness, let Codex preserve useful knowledge inside
the target project, verify that write, and archive the exact target. It does not
authorize implementation, Git, publication, profile changes, worker/job control,
or continuation of the target's work.

## Select Exact Current-Host Targets

Accept one exact task ID, an ordered list of exact IDs, or an explicit sweep of
one exact project on the current host. Resolve supplied IDs exactly without
title guessing. Do not enumerate tasks for single-ID or list requests.

For a project sweep, require the user to name the exact project and explicitly
request the sweep. Use a native bounded list surface to filter current-host and
exact-project metadata before reading task content. Do not impose an automatic
age threshold, item limit, title match, or cross-host search. If the surface
cannot enforce that boundary, stop the sweep without reading or archiving
candidates.

Process an exact list or sweep sequentially. De-duplicate exact IDs by first
occurrence. A target-local blocker leaves that task open and does not block a
later independent target. A shared task-list, host-identity, or exact-ID action
failure stops later mutations while preserving earlier results.

Never read raw transcript, session, history, memory, authentication, credential,
or other runtime files. Use native task reads and only enough completed turns
and project evidence to assess the target.

## Assess Readiness Semantically

Read the exact target's identity, title, status, reported `cwd`, requested
outcome, final evidence, repository handoff, and remaining ownership. A task is
ready to archive only when current evidence makes all of these clear:

- the work is completed, explicitly abandoned, or genuinely blocked with a
  reproducible resume condition; it is not active or unclear;
- no unresolved user decision, worker, job, external operation, or unreported
  repository state still depends on the task as sole owner;
- completed task-owned local changes have a fresh positive semantic conclusion
  from `personal-risk-verification` covering their final state; and
- uncommitted changes, checks not run, remaining risk, external state, and the
  next owner are reported honestly.

Do not require a fixed verdict token or closeout state record. Tests passing, a
worker recommendation, or a clean diff alone does not establish completion. If
evidence is insufficient, report what is missing and leave the target open.

An approved detached job may survive only when its ownership and reproducible
handoff no longer depend on the target task.

## Let Codex Decide What Merits Preservation

Codex decides whether the target contains verified, non-obvious knowledge that
will help future project work. Preserve only material value such as a changed
contract, consequential decision and constraint, recurring recovery method,
useful failed attempt, or unresolved risk with a reproducible resume condition.

Skip project writes for obvious results, transient status, duplicates,
unsupported inference, or failures that established nothing reusable. Skipping
is an ordinary judgment, not a missing closeout stage.

Prefer a small update to the project's existing canonical document. Do not
create a retrospective template or new document by default. Keep facts,
decisions, lessons, inferences, failures, and unknowns distinguishable; never
copy secrets, raw task transcripts, long logs, or sensitive intermediates.

Resolve the project root and document owner from target evidence. If either is
unclear, do not write. Substantial new architecture, API, onboarding, or
tutorial documentation belongs to `personal-code-documentation`; personal
profile improvements remain proposals for a separate workflow.

After any preservation write, read back the changed section, inspect the final
diff, run the narrow relevant documentation checks, and obtain a fresh positive
semantic conclusion from `personal-risk-verification`. If that evidence is
insufficient, leave the target open.

## Archive Last

Before archival, prepare the result containing the exact ID and title, outcome,
readiness evidence or blocker, preservation paths or skip reason, verification
and repository state, remaining risk, and next owner.

Then invoke the native archive action for that exact ID. Archive is that
target's final mutation. The native result is the only evidence that archival
occurred. A missing, denied, mismatched, or failed result means the task remains
unarchived.
After archival, do not edit its project, restart its work, or mutate the target.

Return one compact result per exact ID and a short batch summary when useful.

See [source notes](references/source-notes.md) only when maintaining this
skill's provenance or product assumptions.
