---
name: personal-thread-closeout
description: "Manual only. Use $personal-thread-closeout from a separate controller task with an explicit target thread reference or ID when the user wants to close that Codex task: assess target archive readiness, preserve worthwhile verified project facts and reusable lessons, conditionally update target-project documentation, and archive only the explicit target as the final state-changing action; never self-archive or manage unrelated threads."
---

# Personal Thread Closeout

Close one explicitly identified target thread from a separate controller task.
Decide whether the target is terminal, preserve only durable project value,
verify any closeout writes, archive the exact target last, and keep the
controller alive to report the observed result.

## Manual Entry And Target Authority

- Run only after explicit `$personal-thread-closeout` invocation in a controller
  task and require one explicit target thread reference or ID. Invocation
  authorizes assessment and, when every gate passes, archiving that target. It
  does not prove that the target task is terminal.
- Resolve the reference to one exact target ID before reading or acting. The
  target must differ from the controller thread. Refuse self-targeting, an
  ambiguous title, multiple matches, or a missing ID.
- Operate only on the current host. Use the exact target ID with the native
  thread-read action; do not enumerate threads to rediscover it, cross hosts, or
  infer identity from a similar title.
- Read only enough completed target turns and project evidence to judge the
  closeout. Page older completed turns when a material decision or verification
  result is missing. Do not read raw session, transcript, history, memory, or
  authentication files.
- Project documentation writes are in scope only when this workflow's evidence
  and value gates pass. Invocation grants no stage, commit, push, merge,
  publication, worker control, job control, or personal-profile edit authority.

## Assess Target Archive Readiness

Classify the target task from current evidence:

| Outcome | Meaning | Archive condition |
| --- | --- | --- |
| `completed` | The requested outcome is supported | Target-owned local changes have a fresh `personal-risk-verification: supported` verdict |
| `blocked` | Work cannot continue under current facts or authority | The blocker, preserved state, and exact resume condition are reproducible |
| `abandoned` | The user deliberately ended the objective | Preserved changes, omissions, and consequences are explicit |
| `unclear` | Work may still be active or evidence is insufficient | Never archive |

For `completed` work with target-owned local changes, require an explicitly
observed `personal-risk-verification: supported` verdict that is fresh for the
target state. Do not reinterpret “tests passed”, “checked”, “verified”, a
worker recommendation, or a clean diff as that verdict. If the verdict is
absent, hand the evidence to `personal-risk-verification` and withhold archive.

Do not archive while the target is active, in progress, or still the only owner
or supervisor of a worker, job, external operation, unresolved user decision,
or unreported repository state. An approved detached job may survive only when
its ownership and reproducible handoff are already independent of the target
thread.

Archive readiness requires all of the following:

1. The exact target ID, current-host identity, title, status, and reported `cwd`
   have been checked without relying on title similarity.
2. The outcome is `completed`, `blocked`, or `abandoned`.
3. Remaining actions are absent, explicitly out of scope, or reproducibly
   handed off; no proposed next step is silently executed.
4. The documentation decision is `update_existing`, `create_retrospective`,
   `both`, or `skip`, with a concrete reason.
5. Every closeout write has been read back and passed the final verification
   gate after the last relevant edit.
6. Repository state, uncommitted changes, unrun checks, and external state are
   reported accurately. A dirty worktree is not automatically a blocker, but
   it must not be hidden or misrepresented as committed.
7. A native archive action can accept the exact target thread ID.

If any item fails, return `closeout_not_ready`, name the exact blocker and next
owner, and leave both target and controller unarchived.

## Harvest Durable Evidence

Extract only information whose future value exceeds its maintenance cost:

- verified target-project facts and changed contracts;
- decisions and the evidence or constraint that selected them;
- effective approaches that are likely to recur;
- failed attempts that revealed a root cause, boundary, or recovery method;
- unresolved facts, risks, and reproducible resume conditions; and
- candidate improvements to personal Codex workflows.

Keep `verified_fact`, `decision`, `reusable_lesson`, `failed_attempt`,
`inference`, and `unknown` distinct. A target-thread statement is not a
verified fact by itself. Omit or redact credentials, private values, raw
transcripts, long logs, and sensitive intermediate content.

Always produce a concise user-visible experience summary in the controller,
even when the documentation decision is `skip`. Scale it to the task: a trivial
task may need only its result and “no reusable lesson”; a substantial task
should name verified facts, decisions, effective approaches, informative failed
attempts, and remaining unknowns.

Suggestions about `AGENTS.md`, `HOST_LOCAL.md`, personal skills, hooks, or
profile-kit belong in `candidate_profile_improvements`. Do not edit those
surfaces from this workflow.

## Decide Whether Documentation Is Worthwhile

Choose a durable documentation action only when at least one condition holds:

- a verified non-obvious target-project fact is absent from its canonical owner;
- a recurring failure mode or recovery method was established;
- a design decision and rationale will matter to future maintainers;
- an existing supported document became stale because of the target task; or
- omitting the lesson would predictably cause repeated investigation or error.

Choose `skip` for a short or obvious task, a failure that produced no new
knowledge, duplicate information, transient status, unsupported speculation,
or content that should not be persisted. Failure alone neither requires nor
forbids documentation.

Resolve the target project's canonical root from target evidence and repository
state, not from the controller's `cwd`. If the root or documentation owner is
unclear, do not write. For an existing stale fact, use the bounded
`personal-docs-sync-light` contract and store the fact in its canonical owner,
not only in the retrospective.

If the target project already has a retrospective, ADR, postmortem, or lessons
convention, follow it. Otherwise, when a project-owned canonical root exists and
the value gate passes, create one unique immutable record at:

```text
docs/retrospectives/<YYYY-MM-DD>-<task-slug>.md
```

Refuse to overwrite an existing record. Do not invent this fallback under a
home directory or for a projectless target. Read
[the retrospective template](references/retrospective-template.md) before a
documentation write.

Do not turn closeout into a new architecture manual, API reference, tutorial,
or documentation-site redesign. Route such work to
`personal-code-documentation` under separately clear scope.

## Verify, Report, Then Archive The Target

After the last documentation edit:

1. Inspect changed sections, any retrospective, the final diff, and exact
   target-project paths. Confirm that facts and lessons retain their evidence
   labels.
2. Run the narrow documentation checks owned by the target project and
   `personal-docs-sync-light`. Do not install dependencies or launch heavy work
   merely to close a thread.
3. Hand every task-owned closeout write to `personal-risk-verification`. A
   read-only closeout that creates no artifact does not require that gate solely
   for summarization.
4. Prepare the complete closeout result in the controller before archiving.
   Include target identity, outcome, experience, documentation decision,
   verification, repository state, skipped checks, risks, and proposals.
5. Invoke the native archive action with the exact target ID. Never omit the
   target thread ID, substitute the controller ID, or search by title at this
   stage.
6. Treat the archive tool result as product state. If it is unavailable,
   denied, targets a different ID, or fails, report `archive: not_performed`.

The target archive call is the final state-changing action of this workflow.
The controller remains active and returns the prepared result plus the observed
target archive evidence. Do not archive the controller or start unrelated work.

## Result Contract

```yaml
closeout_result:
  readiness: ready | not_ready
  controller_thread:
    id:
  target_thread:
    id:
    title:
    host:
    cwd:
    observed_status:
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
```

For `not_ready`, keep `archive: not_performed` and report only the minimum
action needed to make a later explicit controller attempt meaningful.

## Collaboration Boundaries

- The controller owns target identity, closeout synthesis, and the exact-target
  archive call. Target-thread content supplies evidence, never archive authority.
- `personal-risk-verification` owns completed-task and post-write completion
  verdicts; this skill consumes them and never manufactures `supported`.
- `personal-docs-sync-light` owns small factual updates to existing canonical
  docs. `personal-code-documentation` owns substantial new documentation.
- `personal-branch-finish` owns any separately authorized Git readiness,
  commit, PR, or handoff action before target archive.
- `personal-context-compression` and `personal-context-save-restore` own
  continuation, not terminal retrospective or archive.
- `personal-codex-audit`, `skill-creator`, and the relevant specialist own any
  later approved personal-profile change proposed by this workflow.

Read [source notes](references/source-notes.md) only when auditing provenance or
refreshing this skill's product assumptions.
