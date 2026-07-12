# Source Notes

Checked: 2026-07-12.

This skill is local-origin and is based on the user's recurring project need to
keep one-time data conversion and repair logic out of maintained runtime code.
Available Git history and a bounded exact-phrase search did not establish an
external textual source. No external text is copied, and no derivative-license
claim is made.

## Contents

- [Local History](#local-history)
- [User-Origin Design Evidence](#user-origin-design-evidence)
- [Official Codex Evidence](#official-codex-evidence)
- [Baseline Observations](#baseline-observations)
- [Adopted](#adopted)
- [Adapted](#adapted)
- [Rejected](#rejected)
- [Local Deviations](#local-deviations)

## Local History

- Initial profile-kit commit:
  `6574bce5f5ede8fb4566d0451ddcf613f7fdf8a5`
- Initial `SKILL.md` blob:
  `b27d4d794ead5487be54d01a507c1a0954099749`
- Initial `agents/openai.yaml` blob:
  `34ecb3fbcea26af7aac2a0787e9c09fae7824568`

The files still matched those initial blobs before this revision. The initial
skill already preferred temporary helpers over permanent branches and compared
direct transformation with regeneration. It did not fully separate steady-state
behavior from historical transition, task-owned roles from path names, or
traceable retention from throwaway cleanup.

## User-Origin Design Evidence

The primary motivating pattern is a generator whose future shard default must
change while already generated data must be reorganized once. Adding a
permanent reshard module to the generator makes a local transition look like an
ongoing supported feature. The accepted design instead uses:

- the smallest maintained configuration or behavior change for future data;
- a temporary converter for existing data;
- separate verification for the new steady state and the historical migration;
- retention or cleanup based on provenance and audit value.

The user also approved a placement rule with one project/worktree-level `tmp/`
root, task-scoped subdirectories, an independently managed monorepo-subproject
exception, and output-adjacent staging when atomic publication or large storage
requires it.

## Official Codex Evidence

- [Build skills](https://learn.chatgpt.com/docs/build-skills) documents explicit
  and implicit skill invocation, description-based matching, progressive
  disclosure, optional references and scripts, and the recommendation to keep
  one skill focused on one job and prefer instructions unless deterministic
  tooling is required.
- [Customization overview: Skills](https://learn.chatgpt.com/docs/customization/overview#skills)
  describes skills as reusable workflows whose metadata is visible first and
  whose instructions, references, and scripts load only when needed.

On the check date, the Codex manual helper failed because its HEAD request to
the official manual endpoint returned HTTP 403. The configured OpenAI Docs MCP
then successfully fetched the official pages above. These pages are current
product documentation rather than commit-pinned source and should be rechecked
when Codex skill discovery or metadata behavior changes.

Official documentation supports the skill structure and trigger design. It
does not prescribe a project temporary-artifact lifecycle; that policy remains
local.

## Baseline Observations

Read-only forward probes against the initial skill showed:

- a simple count with an explicit no-file requirement correctly stayed a direct
  command;
- cleanup pressure correctly preserved an unknown-provenance file and avoided
  a directory-wide delete, relying partly on global instructions;
- a synthetic large JSONL merge preserved inputs and proposed staging, but it
  selected a root and invented newline, empty-record, and full-pass validation
  rules before the task contract established them.

No real dataset, large artifact, deletion, or long-running job was used in
those probes.

## Adopted

- Split future steady-state behavior from one-time historical transition.
- Default an explicitly one-off transition with no ongoing-support evidence to
  a temporary helper.
- Require positive evidence before adding a permanent migration module, flag,
  branch, parameter, or API.
- Use a hybrid of minimal durable change and temporary conversion when future
  defaults and existing artifacts both need work.
- Use one owning project/worktree `tmp/` root with task-scoped subdirectories.
- Separate canonical inputs, formal deliverables, helpers, evidence, staging,
  caches, sensitive intermediates, and unknown-provenance files.
- Derive validation from the actual transformation contract and risk.

## Adapted

- Narrow implicit triggering from generic statistics and audits to situations
  where one-off work might otherwise become permanent code.
- Keep the core split and execution gate in `SKILL.md`; move the selection,
  placement, role, transformation, and promotion matrices into one on-demand
  reference.
- Preserve useful small helpers without equating preservation with Git tracking.
- Allow output-adjacent staging for large or atomically published deliverables
  while keeping helper code and lightweight evidence in the task `tmp/` folder.

## Rejected

- Creating a helper for every one-line statistic or read-only check.
- Adding transition logic to a normal runtime path merely because that path is
  convenient to edit.
- Treating every possible future reuse as evidence for a permanent feature.
- Treating all `tmp/` contents as disposable or all helpers as worth retaining.
- Scattering helpers through source directories or silently editing
  `.gitignore` to hide them.
- Generic cache cleanup, project-wide `tmp/` deletion, or ownership inferred
  from path alone.
- Invented format invariants or unconditional high-cost validation passes.
- A bundled generic transformation or cleanup script; task contracts are too
  heterogeneous for that to be safe.

## Local Deviations

- Global `AGENTS.md` remains the owner of installation, resource, long-job,
  destructive, sensitive-data, Git, and user-change protection boundaries.
- Domain workflows retain the semantics and acceptance contract of debugging,
  documentation, code cleanup, tests, and generated artifacts. This skill owns
  the durable-versus-temporary split and task-owned helper lifecycle.
- A formal deliverable is not temporary merely because a temporary helper
  created it.
- Large shared immutable data and cross-worktree bindings belong to
  `personal-multiline-coordination` rather than this skill.
- No mechanical validator or reusable script is bundled. Validation uses the
  profile's skill validators plus isolated behavioral scenarios.
