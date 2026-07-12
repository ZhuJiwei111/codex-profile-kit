---
name: personal-skill-hygiene
description: Use when a specific Codex skill, plugin, or hook needs pre-activation admission, provenance or portability review, or a lifecycle decision to enable, disable, archive, restore, rename, remove, or replace it, especially for newly created or externally installed skills.
---

# Personal Skill Hygiene

## Contract

Own pre-activation admission and lifecycle decisions for one concrete Codex
skill, plugin, or hook. Keep observations, recommendations, and approved
mutations distinct.

- Start read-only unless the user explicitly requests a lifecycle change.
- Confirm the target, host, desired outcome, and authorization boundary.
- Treat `.system/skill-creator` and `.system/skill-installer` as product-owned
  authoring and transport engines, not as local admission verdicts.
- Prefer a recoverable state transition over immediate deletion.
- Preserve unrelated configuration and user changes.
- Report exact paths and evidence without exposing sensitive values.

## Route Before Acting

Read [references/lifecycle-routing.md](references/lifecycle-routing.md) before
choosing an owner. Route authoring, installation, hook design, and full-profile
work to their specialist skills instead of duplicating those workflows here.

For a newly created or externally installed skill, read
[the admission contract](references/skill-admission.md) and
[the provenance contract](references/provenance-contract.md) before activation
or portable adoption. This skill owns the admission decision; `skill-creator`
and `skill-installer` still own the actual authoring and installation mechanics.

Keep this skill as the primary owner only when the central question is the
target's lifecycle state or its safest lifecycle disposition. For a mixed
request, separate the lifecycle decision from the specialist implementation.

## Admission Workflow

1. Lock one candidate, its acquisition mode, intended activation scope, and
   whether the request authorizes review, authoring, installation, activation,
   or portable adoption.
2. Keep external candidates outside active discovery until the applicable
   source, instruction, script, dependency, trigger, and rollback checks pass.
   Popularity, a curated label, or successful download is not trust evidence.
3. Let `skill-creator` author or revise local content and let
   `skill-installer` acquire the exact approved source. Do not fork, overwrite,
   or export `.system` skills.
4. Apply the four admission dimensions in the admission contract. Preserve
   unknown or conflicting evidence instead of manufacturing an `admitted`
   result.
5. Use risk-scaled static checks, script tests, and positive, negative, and
   adjacent-trigger probes. Installation alone never authorizes dependencies,
   hooks, MCP configuration, credentials, publication, or external actions.
6. Assign one admission result and portability disposition. Activate or export
   only the admitted surface; keep deferred candidates quarantined or outside
   discovery with an exact resume condition.
7. Record update ownership and rollback evidence. A modified vendor must be
   reclassified or internalized rather than silently updated as upstream code.

## Lifecycle Workflow

1. Lock one target or a tightly related replacement pair. If the request covers
   the whole reusable profile, route it to `personal-codex-audit`.
2. Inspect only the evidence needed for the target. Use
   [references/targeted-audit.md](references/targeted-audit.md) for state
   definitions, artifact-specific checks, and evidence boundaries.
3. Distinguish `exists`, `discoverable/registered`, `configured`, `enabled`,
   `trusted`, `cached`, and `archived`. Do not infer one state from another.
4. Assign one disposition: `keep`, `update-via-specialist`, `disable`,
   `archive`, `restore`, `rename`, `remove`, `replace`, or
   `needs-clarification`. If a disposition's required evidence is unknown, use
   `needs-clarification` and state any conditional next disposition separately.
5. Explain the evidence, purpose, collaboration impact, rollback path, and
   residual risk before any destructive or broad state change.
6. Apply only the authorized transition. Prefer `disable -> archive -> confirm
   replacement -> remove/cache cleanup` when those stages apply.
7. Validate the resulting state with the narrowest reliable check. Use
   [references/skill-testing-levels.md](references/skill-testing-levels.md)
   when content, triggering, safety discipline, or destructive behavior is at
   issue.
8. Report the actual change, validation result, retained recovery path, and any
   state that remains unknown or user-controlled.

## Hard Boundaries

- Do not create or rewrite skill content here; route that work to
  `skill-creator` after the lifecycle decision is settled.
- Do not edit, copy, or vendor `.system` skills into the personal profile.
- Do not author hooks here or treat this skill as a generic configuration
  editor.
- Do not edit `.system` skills, credentials, auth/session files, private keys,
  `.netrc`, or hook trust hashes.
- Do not treat a cache directory as proof of installation, enablement, trust,
  or ownership.
- Do not remove a sole or non-reconstructible copy. Archive first when the
  recovery source is not independently verified.
- Do not split a workflow merely because a skill is long. Split only when
  triggers, owners, or resources have genuinely separable boundaries.
- Do not use deletion as a substitute for an official disable, uninstall, or
  trust-review mechanism.
- Do not treat stars, install counts, repository ownership, a curated label, or
  successful installation as proof of safety, trigger quality, or admission.
- Do not mark an unassessed, deferred, or rejected candidate active or portable.
- Do not stage, commit, push, publish, or contact external services unless the
  user separately authorizes that action.

## References

- [references/lifecycle-routing.md](references/lifecycle-routing.md): choose
  the primary skill or product owner.
- [references/skill-admission.md](references/skill-admission.md): admit,
  defer, reject, activate, internalize, or keep one candidate host-only.
- [references/provenance-contract.md](references/provenance-contract.md):
  classify and record external, local, hybrid, and unresolved evidence.
- [references/targeted-audit.md](references/targeted-audit.md): inspect and
  classify one target without turning the task into a profile-wide audit.
- [references/skill-testing-levels.md](references/skill-testing-levels.md):
  scale validation to trigger, discipline, and destructive-action risk.
- [references/source-notes.md](references/source-notes.md): upstream evidence,
  pinned versions, adopted ideas, rejected assumptions, and local deviations.
