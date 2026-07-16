# Source Notes

Checked: 2026-07-11.

This skill uses upstream TDD material as design evidence. Local authorization,
user-change protection, proportionality, and workflow ownership take
precedence.

## Superpowers `test-driven-development`

- Release: [v6.1.1](https://github.com/obra/superpowers/releases/tag/v6.1.1)
- Annotated tag object: `c984ea2e7aeffdcc865784fd6c5e3ab75da0209a`
- Peeled release commit: `d884ae04edebef577e82ff7c4e143debd0bbec99`
- Pinned skill:
  <https://github.com/obra/superpowers/blob/d884ae04edebef577e82ff7c4e143debd0bbec99/skills/test-driven-development/SKILL.md>
- Pinned testing anti-patterns reference:
  <https://github.com/obra/superpowers/blob/d884ae04edebef577e82ff7c4e143debd0bbec99/skills/test-driven-development/testing-anti-patterns.md>
- License: MIT, Copyright (c) 2025 Jesse Vincent. See the
  [pinned license](https://github.com/obra/superpowers/blob/d884ae04edebef577e82ff7c4e143debd0bbec99/LICENSE).
- Audit note: upstream `main` matched this commit and these files on the check
  date. The local baseline remains pinned to v6.1.1 even if `main` later moves.
- Upstream file SHA-256:
  - `SKILL.md`: `b5b4717b8b761cce15a6cfe9022e33fd959e0894c0c39d72c9cb49c23486c10e`
  - `testing-anti-patterns.md`:
    `bde453bc258f06543987477c837939afaa774ea2acbd9f308d702fc452bc4283`

### Adopted

- Observe RED and confirm that it fails for the expected behavior reason.
- Use one small, clear check against real behavior.
- Implement the minimum behavior needed for GREEN, then rerun the focused
  check and directly related evidence.
- Refactor only while the relevant checks remain green.
- Avoid mock-only tests, test-only production APIs, and mocks created without
  understanding the dependency boundary.

### Adapted

- The upstream universal TDD rule became three risk-scaled evidence modes:
  `red_green`, `preserving_baseline`, and `alternate`.
- Whole-suite GREEN became the same focused check plus the cheapest directly
  coupled nearby checks; final breadth belongs to `personal-risk-verification`.
- Behavior-preserving task refactors use a pre-change passing baseline instead
  of an artificial RED.
- Configuration and generated artifacts are classified by behavioral effect
  and ownership instead of receiving a blanket exception.
- User or independently handed-off prior-stage implementation receives the
  strongest safe regression evidence without pretending that RED was observed.
  An exact, non-overlapping current-task Codex edit may be safely withdrawn to
  restore a real pre-change boundary.

### Rejected

- An exception-free iron law for every file type, risk level, and repository.
- Unconditional deletion of implementation written before a test.
- Unapproved or implicit reversion of user or prior-stage work merely to
  manufacture RED.
- Running the entire project suite during every small cycle.
- Expanding scope to fix every unrelated baseline failure.
- Treating a passing pre-change refactor baseline as a TDD violation.
- Copying the upstream long-form persuasion, rationalization tables, examples,
  or full testing anti-patterns reference into the local main file.

### Local Deviations

- Preserve user and independently handed-off prior-stage work and disclose
  missing RED evidence instead of staging a false historical failure. Their
  exact, recoverable rollback requires separate explicit user authorization;
  safely withdrawing an isolated current-task Codex edit remains part of the
  already authorized implementation workflow.
- Require separate authorization for installation, large environments, heavy
  resources, high-traffic downloads, and long-running checks.
- Route repository discovery, unexpected failure diagnosis, documentation
  synchronization, final verification, and Git finish work to their dedicated
  personal skills.
- Keep the cycle record conversational and non-persistent unless another
  approved workflow owns a durable record.

```yaml
skill_admission:
  skill: personal-test-first-changes
  acquisition_mode: created
  source_classification: hybrid
  provenance_status: complete
  admission_status: admitted
  portability_disposition: internalized
  safety_status: passed
  safety_review: "static_pass: Static review found no bundled executable; rollback of user or prior-stage work, installation, heavy checks, long jobs, and scope expansion remain prohibited or separately authorized."
  trigger_status: passed
  trigger_review: "static_pass: Bug-fix, feature, behavior-change, and refactor evidence routing was reviewed against diagnosis-only work, expected RED, final verification, and non-behavior changes."
  validation_status: passed
  validation:
    - "static_pass: Pinned upstream skill and anti-pattern reference, hashes, license, local adaptations, and authorization boundaries reviewed on 2026-07-16."
    - "static_pass: Targeted personal-skill admission validator fixtures passed on 2026-07-16."
  update_owner: "maintainer of personal-test-first-changes"
  update_rule: "Repeat provenance, safety, trigger, evidence-mode, and portability review before any source, RED/GREEN contract, trigger, or ownership change enters portable export."
  rollback_basis: "Remove the skill through personal-skill-hygiene and restore the reviewed tree from codex-profile-kit revision 3791645f59c0eeec497755bd7301be78b44efbea."
  unknowns_disposition: none
  unknowns: []
```
