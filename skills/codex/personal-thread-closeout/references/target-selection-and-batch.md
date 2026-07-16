# Target Selection And Batch Contract

Use this reference for an explicit target list or explicit project sweep. A
single exact target uses the same per-target contract with a one-item batch.

## Exact Target Lists

Resolve each user-supplied reference to one exact current-host task ID. Reject an
ambiguous title, missing target, controller ID, or cross-host target. Preserve
input order and deduplicate after exact resolution:

```text
[A, B, A, C] -> [A, B, C]
```

The first occurrence supplies order and user-facing label. A later duplicate
does not create another assessment, documentation write, or archive attempt.

## Explicit Project Sweep

Project enumeration is allowed only when the user explicitly requests a sweep
and supplies an exact project identity. Before listing, identify the current
host. If the tool returns multiple hosts, discard non-current-host records before
their content enters context.

Use the target project's exact product identity when available. Otherwise use a
canonical project root only when task metadata exposes it reliably. Similar
titles, parent directories, repository names, or controller cwd are not enough.

Compute the default cutoff in the user's current timezone:

```text
cutoff = start of current local day - 15 calendar days
eligible when last_activity < cutoff
```

Thus a task at the cutoff is not eligible. Require a reliable last-activity
timestamp for every candidate. Filter exact project and current host, exclude
the controller, sort ascending by last activity with exact ID as deterministic
tie-breaker, and select the first 10.

Fail closed before mutation when current host, project identity, timestamps,
filtering, or ordering cannot be established. An empty eligible set is a valid
no-op result, not permission to broaden the project or cutoff.

## Sequential Processing

Process one target completely before the next:

```text
read -> assess -> optional docs -> verify -> prepare result -> archive
```

Archive is the last mutation for that target. Do not defer all archive calls to
the end of the batch.

Classify failures:

- **Target-local:** missing evidence, unclear outcome, active work, unavailable
  target project root, documentation failure, verification failure, or one
  target archive failure. Record it and continue.
- **Shared infrastructure:** current host cannot be identified, exact-ID reads or
  archives are unavailable globally, project selector is unreliable, or the
  controller cannot preserve batch results. Stop later mutation.

A shared failure does not erase prior target results. Never roll back an archive
or project document merely to make the batch look atomic.

## Result Schema

```yaml
closeout_batch:
  mode: explicit_targets | project_sweep
  controller_thread:
    id:
  project:
    identity:
    host:
    cutoff:
    selection_limit: 10
  normalized_target_ids: []
  duplicates_ignored: []
  results:
    - target_thread:
        id:
        title:
        host:
        cwd:
        observed_status:
      readiness: ready | not_ready
      task_outcome: completed | blocked | abandoned | unclear
      experience:
        summary:
        verified_facts: []
        reusable_lessons: []
        informative_failed_attempts: []
        remaining_unknowns: []
      documentation:
        decision: update_existing | create_retrospective | both | skip
        reason:
        changed_paths: []
      verification:
        verdict: supported | not_required | not_supported
        checks: []
        not_run: []
      repository_state:
      remaining_risks: []
      candidate_profile_improvements: []
      archive: performed | not_performed
      archive_evidence:
      next_owner:
  shared_failure:
  first_unprocessed_target:
  skipped_without_mutation: []
```

Omit project cutoff fields for an explicit list when they do not apply. Keep an
entry for every normalized target processed before a shared stop. Do not claim
archive success without the exact native tool result.
