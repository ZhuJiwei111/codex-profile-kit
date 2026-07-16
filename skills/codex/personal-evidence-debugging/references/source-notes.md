# Source Notes

Checked: 2026-07-11.

This skill uses upstream systematic-debugging material as design evidence.
Local authorization, user-change protection, host boundaries, and specialist
workflow ownership take precedence.

## Superpowers `systematic-debugging`

- Release: [v6.1.1](https://github.com/obra/superpowers/releases/tag/v6.1.1)
- Annotated tag object: `c984ea2e7aeffdcc865784fd6c5e3ab75da0209a`
- Peeled release commit: `d884ae04edebef577e82ff7c4e143debd0bbec99`
- Pinned main skill:
  <https://github.com/obra/superpowers/blob/d884ae04edebef577e82ff7c4e143debd0bbec99/skills/systematic-debugging/SKILL.md>
- Pinned supporting material:
  - [root-cause-tracing.md](https://github.com/obra/superpowers/blob/d884ae04edebef577e82ff7c4e143debd0bbec99/skills/systematic-debugging/root-cause-tracing.md)
  - [defense-in-depth.md](https://github.com/obra/superpowers/blob/d884ae04edebef577e82ff7c4e143debd0bbec99/skills/systematic-debugging/defense-in-depth.md)
  - [condition-based-waiting.md](https://github.com/obra/superpowers/blob/d884ae04edebef577e82ff7c4e143debd0bbec99/skills/systematic-debugging/condition-based-waiting.md)
  - [condition-based-waiting-example.ts](https://github.com/obra/superpowers/blob/d884ae04edebef577e82ff7c4e143debd0bbec99/skills/systematic-debugging/condition-based-waiting-example.ts)
  - [find-polluter.sh](https://github.com/obra/superpowers/blob/d884ae04edebef577e82ff7c4e143debd0bbec99/skills/systematic-debugging/find-polluter.sh)
- License: MIT, Copyright (c) 2025 Jesse Vincent. See the
  [pinned license](https://github.com/obra/superpowers/blob/d884ae04edebef577e82ff7c4e143debd0bbec99/LICENSE).
- Audit note: upstream `main` matched the peeled v6.1.1 commit on the check
  date. The local baseline remains pinned to the release if `main` later moves.
- Relationship: v6.1.1 is the explicit design baseline. The local workflow and
  references are independently rewritten; no upstream script or long-form
  example is copied.

### Adopted

- Read the failure, reproduce it, and inspect recent relevant changes before a
  fix.
- Trace invalid data or state backward through component and call boundaries.
- Compare the broken path with the nearest trustworthy working implementation.
- Test one explicit hypothesis with a minimal discriminating experiment.
- Stop before a fourth independent failed fix and discuss architectural
  assumptions.
- Replace arbitrary sleeps with bounded condition-based waiting when the
  observable condition, rather than elapsed time, is the contract.

### Adapted

- The upstream four phases became a compact failure packet and five-stage
  evidence loop, followed by a separate fix handoff.
- Diagnosis and fix authorization are explicit and independent.
- Root-cause confidence is `confirmed`, `likely`, or `unknown`; inaccessible
  external causes are not overclaimed.
- Two no-new-information diagnostic cycles change tactic, while three actual
  independent failed fixes trigger architecture review.
- Fix implementation belongs to `personal-test-first-changes`, and final
  completion belongs to `personal-risk-verification`.
- Defense in depth is risk-based: each extra guard needs independent failure
  value and its own behavioral evidence.

### Rejected

- A mandatory full four-phase ceremony for every small technical issue.
- Treating three failed fixes as automatic proof that the architecture is
  wrong.
- Adding validation at every layer regardless of independent risk value.
- Printing complete environment variables, secrets, or sensitive inputs for
  diagnostic instrumentation.
- An absolute ban on bounded symptom handling when an external source cannot be
  observed.
- The project-specific TypeScript waiting example and `find-polluter.sh` as
  reusable local tools.
- Unbounded test execution, implicit package installation, or heavy reruns for
  diagnosis.
- Upstream persuasion tables, unsupported experience percentages, and
  long-form rationalization lists.

### Local Deviations

- Diagnosis-only work remains read-only with respect to task code and durable
  configuration; source instrumentation requires edit authority.
- Long jobs, GPU work, restarts, termination, monitoring, installation, and
  downloads retain their separate authorization boundaries.
- A failed verification does not silently authorize diagnosis, and debugging
  does not claim final completion.
- Durable guidance is routed only after a confirmed reusable cause and separate
  authorization.

```yaml
skill_admission:
  skill: personal-evidence-debugging
  acquisition_mode: created
  source_classification: hybrid
  provenance_status: complete
  admission_status: admitted
  portability_disposition: internalized
  safety_status: passed
  safety_review: "static_pass: Static review found no bundled executable; diagnosis is read-only by default and instrumentation, installation, long jobs, restarts, monitoring, and fixes retain separate authority."
  trigger_status: passed
  trigger_review: "static_pass: Unexpected failure investigation was reviewed against expected RED, status-only checks, test-first fixes, and final verification."
  validation_status: passed
  validation:
    - "static_pass: Pinned upstream release, supporting materials, license, independent rewrite, and local safety deviations reviewed on 2026-07-16."
    - "static_pass: Targeted personal-skill admission validator fixtures passed on 2026-07-16."
  update_owner: "maintainer of personal-evidence-debugging"
  update_rule: "Repeat provenance, safety, trigger, and portability review before any source, trigger, runtime surface, or ownership change enters portable export."
  rollback_basis: "Remove the skill through personal-skill-hygiene and restore the reviewed tree from codex-profile-kit revision 3791645f59c0eeec497755bd7301be78b44efbea."
  unknowns_disposition: none
  unknowns: []
```
