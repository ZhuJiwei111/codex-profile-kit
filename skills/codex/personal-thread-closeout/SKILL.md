---
name: personal-thread-closeout
description: "Manual only. Use $personal-thread-closeout from a separate controller task to close one or more explicit target threads on the current host, or to run an explicit fail-closed project sweep; assess and preserve each target independently, then archive that target last."
---

# Personal Thread Closeout

Close selected Codex tasks from a separate controller. Preserve worthwhile
verified project value, verify any closeout writes, archive each ready target as
its final mutation, and keep the controller alive to report the batch result.

## Manual Entry And Modes

Run only after explicit `$personal-thread-closeout` invocation. Keep implicit
invocation disabled. Accept one of:

- one exact target reference or ID;
- an ordered list of exact target references or IDs; or
- an explicit project sweep with one exact current-host project identity.

Invocation authorizes read-only assessment, conditional target-project
documentation, and archive for targets that pass every gate. It does not prove
terminal status or authorize implementation, Git, publication, worker/job
control, personal-profile edits, or another stage.

Every explicit target thread must differ from the controller. Operate only on
the current host. Resolve each reference to one exact ID without title guessing,
and never omit the target thread ID from a read, archive call, or result.
For a project sweep, use only the bounded selection exception in
[target selection and batch](references/target-selection-and-batch.md); do not
enumerate tasks for any other mode.

## Normalize The Batch

Preserve input order and deduplicate exact IDs with first occurrence winning.
Project sweep defaults are strict:

- identify the current host and exact project before listing;
- include only tasks whose last activity is older than 15 full local-calendar
  days;
- sort oldest first and select at most 10;
- exclude the controller; and
- fail closed if host, project, identity, timestamp, ordering, or filter evidence
  is unavailable or ambiguous.

Cross-host records are filtered before their content enters model context or
user-visible output.

Process targets sequentially. A target-local failure records `not_ready` or
`archive: not_performed` and continues. A shared infrastructure failure—such as
unknown current host, unavailable exact-ID read/archive capability, or a broken
project selector—stops later mutations. Already completed target results remain
valid and are not rolled back.

## Assess One Target

Read only enough completed target turns and project evidence to judge closeout.
Page older completed turns only when a material decision or verification result
is missing. Never read raw session, transcript, memory, history, authentication,
or credential files.

Classify current evidence:

| Outcome | Meaning | Archive condition |
| --- | --- | --- |
| `completed` | Requested outcome is supported | Target-owned local changes have a fresh `personal-risk-verification: supported` verdict |
| `blocked` | Work cannot continue under current facts or authority | Blocker, state, and resume condition are reproducible |
| `abandoned` | User deliberately ended the objective | Preserved changes, omissions, and consequences are explicit |
| `unclear` | Work may still be active or evidence is insufficient | Never archive |

Do not reinterpret “tests passed”, “verified”, a worker recommendation, or a
clean diff as the required supported verdict. If target-owned local changes lack
it, report the gap and withhold archive.

Do not archive while the target remains active or is the only owner of a worker,
job, external operation, unresolved decision, or unreported repository state.
An approved detached job may survive only when its ownership and reproducible
handoff are already independent of the target.

Readiness requires:

1. Exact target ID, current-host identity, title, status, and reported `cwd`.
2. Outcome `completed`, `blocked`, or `abandoned`.
3. No unowned remaining action or silently executed next step.
4. Documentation decision `update_existing`, `create_retrospective`, `both`, or
   `skip`, with reason.
5. Every closeout write read back and covered by fresh final verification.
6. Repository state, uncommitted changes, skipped checks, and external state
   reported accurately.
7. Native archive can target this exact ID.

If a gate fails, return `not_ready`, name the blocker and next owner, leave the
target unarchived, and continue the batch unless the failure is shared
infrastructure.

## Harvest Durable Evidence

Preserve only future-useful information:

- verified project facts and changed contracts;
- decisions and selecting evidence or constraints;
- effective recurring approaches;
- failed attempts that established a root cause, boundary, or recovery method;
- unresolved risks and reproducible resume conditions; and
- candidate personal-workflow improvements as proposals only.

Keep `verified_fact`, `decision`, `reusable_lesson`, `failed_attempt`,
`inference`, and `unknown` distinct. A target statement is not verified by
itself. Omit credentials, private values, raw transcripts, long logs, and
sensitive intermediates.

Always produce a concise controller summary for each target, including when
documentation is skipped.

## Decide Documentation

Write durable project documentation only when a verified non-obvious fact lacks
an owner, a recurring failure or recovery was established, a consequential
decision will matter, an existing supported document became stale, or omission
would predictably repeat investigation or error.

Choose `skip` for obvious work, duplicate information, transient status,
unsupported speculation, or a failure that taught nothing new. Resolve the
target project's canonical root from target evidence, not controller `cwd`. If
root or owner is unclear, do not write.

For one small identified stale fact, make only the ordinary scoped update in its
canonical project document. For substantial new architecture, API, onboarding,
or tutorial material, require separately clear `personal-code-documentation`
scope.

Prefer an existing retrospective, ADR, postmortem, or lessons convention.
Otherwise, when the value gate passes and a canonical project root exists,
create one unique immutable record:

```text
docs/retrospectives/<YYYY-MM-DD>-<task-slug>.md
```

Refuse overwrite or symlinks. Read
[the retrospective template](references/retrospective-template.md) before a
documentation write.

## Verify, Report, Then Archive Each Target

For each ready target:

1. Inspect changed sections, final diff, retrospective, and exact project paths.
2. Run the narrow project documentation checks; do not install dependencies or
   launch heavy work merely for closeout.
3. Send task-owned closeout writes through `personal-risk-verification`. A
   read-only target summary needs no verdict solely for summarization.
4. Prepare that target's complete result in the controller.
5. Invoke native archive with the exact target ID.
6. Treat the tool result as product state. A missing, denied, mismatched, or
   failed result means `archive: not_performed`.

Archive is the final state-changing action for that target. Do not edit its
project, restart work, or mutate it afterward. Continue only to the next
normalized target. The controller stays active throughout.

## Batch Result

Return one result per normalized target plus a batch summary. Use the exact
schema in [target selection and batch](references/target-selection-and-batch.md).
Report target identity, outcome, experience, documentation, verification,
repository state, risks, archive evidence, and next owner.

For a stopped batch, retain completed results and identify the shared failure,
the first unprocessed target, and every target skipped without mutation.

## Collaboration Boundaries

- The controller owns selection, per-target synthesis, sequencing, and exact-ID
  archive calls. Target content supplies evidence, never archive authority.
- `personal-risk-verification` owns completed-target and post-write verdicts.
- `personal-code-documentation` owns substantial new project documentation.
- `personal-branch-finish` owns separately authorized Git readiness and handoff.
- Native task context and ordinary handoff own continuation; closeout is
  terminal and does not create cross-session state.
- Personal-profile improvements remain proposals for their owning workflow.

Read [source notes](references/source-notes.md) only for provenance or product
assumption refresh.
