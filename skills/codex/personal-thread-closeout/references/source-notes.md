# Source Notes

Checked: 2026-07-13

## Provenance Decision

- Classification: local-origin personal workflow.
- Primary source: the user's recurring need to review a finished Codex task,
  preserve durable lessons, update project documentation only when worthwhile,
  and archive the exact target without losing the closeout audit trail.
- This skill is not derived from an external retrospective or thread-management
  skill. No upstream text, script, or runtime package is copied.

## User-Locked Design Decisions

The design conversation fixed these requirements:

- explicit `$personal-thread-closeout` invocation is required;
- a separate controller task must receive one explicit target reference or ID;
- the target must differ from the controller and remain on the current host;
- Codex decides whether the target task is terminal from available evidence;
- persistent writes are limited to the target task's project;
- personal `AGENTS.md`, `HOST_LOCAL.md`, skills, hooks, and profile-kit receive
  proposals only;
- documentation is conditional, so short tasks and failures without new
  knowledge may be archived without a new document;
- when documentation is valuable, prefer an existing project convention and
  otherwise use a unique `docs/retrospectives/<date>-<task-slug>.md` record;
- archive must use the exact target ID as the final state-changing action; the
  controller stays active and reports the result.

## Local Profile Evidence

The following profile-kit revision was the fixed collaboration baseline during
the initial design:

- Revision: `1958e80b1af61cc5437d95e844a95eaf55aadef8`
- `rules/AGENTS.portable.md`: Git blob
  `e20fa56361bee15b1187bb377fb50170ae722ffa`
- `skills/codex/personal-risk-verification/SKILL.md`: Git blob
  `5aa8ccb9932f590a8e606678ebd8cdc231ffc663`
- `skills/codex/personal-docs-sync-light/SKILL.md`: Git blob
  `4a097917cdce2adf3cc4f35b2cacb658f5057fa8`
- `skills/codex/personal-branch-finish/SKILL.md`: Git blob
  `80ed3fa4cac6160f0ef95b1870b1bd05e5dfb0d8`

These sources define authorization, final verification, canonical-doc updates,
and Git finish boundaries. They are design evidence, not bundled runtime
dependencies.

## Live Self-Archive RED

On 2026-07-13 the first live invocation ran inside target thread
`019f4c1c-909a-76e2-8d17-01ffe75eb184` (`优化个人配置`). The workflow correctly
assessed the task as ready and chose `documentation: skip` because its design,
sources, and material lessons were already preserved in canonical skill
references. It then attempted to archive its own calling thread.

Observed result:

- the target became archived;
- the closeout turn status became `interrupted`;
- no final `closeout_result` or direct archive confirmation was recorded in the
  target turn; and
- an external controller later unarchived the target and could then read the
  interrupted turn by exact ID.

This is direct evidence that self-archive cannot satisfy the result contract.
The local design therefore requires an external controller and an explicit,
different target ID.

## Codex App Capability Evidence

The current Codex App tool surface checked on 2026-07-13 exposes native thread
read and archive actions. An archived target may be unavailable to thread reads
until it is unarchived. At runtime:

- require the target reference or ID in the controller invocation;
- read the target by exact ID before archive and page only as far as needed;
- never omit the target ID or replace it with the controller ID;
- treat the archive tool result as the only direct evidence that archive
  occurred; and
- keep the controller alive to report that result.

These capabilities are environment-owned and may change independently of the
portable skill. Their contracts do not authorize raw transcript access,
cross-host management, or treating archive as proof of task completion.

## Rejected Designs

- implicit invocation at every task ending;
- self-archive or omission of the target thread ID;
- archiving merely because the user typed the skill name;
- title-only search or broad thread enumeration to choose a target;
- mandatory documentation for short or non-informative failed tasks;
- one cumulative global lessons file shared by unrelated projects;
- automatic personal-skill, AGENTS, hook, or profile-kit self-modification;
- automatic stage, commit, push, PR, merge, worker control, or job control; and
- claiming archive success when the native action was not observed.
