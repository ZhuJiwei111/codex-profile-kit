# Source Notes

## Provenance Decision

- Classification: hybrid
- Inputs: the user's repository-intake work experience, user-identified
  RigorPilot conceptual influence, and a local redesign for Codex instruction,
  worktree, authorization, and repository-safety contracts.
- Evidence boundary: direct textual derivation from RigorPilot is not
  established. The hybrid label records multiple design inputs, not copied
  wording or a proven source lineage.
- Checked: 2026-07-12

## RigorPilot `repo-intake-and-plan`

- User-supplied possible source:
  <https://github.com/camillanapoles/skill_RigorPilot-Skills/blob/main/skills/repo-intake-and-plan/SKILL.md>
- Canonical upstream: <https://github.com/lllllllama/RigorPilot-Skills>
- Audited repository head:
  `56bc41c40beabc42f5628f06bb2634a5196071f5`
- Skill content pinned at:
  <https://github.com/lllllllama/RigorPilot-Skills/blob/d4ce1a3ee7ff9e72e236b0f7ef72567d819f82d9/skills/repo-intake-and-plan/SKILL.md>
- Skill last-change commit:
  `d4ce1a3ee7ff9e72e236b0f7ef72567d819f82d9`
- Initial skill commit: `4deb5252e2ca0521c249a71d1b035d764968eaa9`
- Checked: 2026-07-11
- License: MIT, Copyright (c) 2026 Chengkun Rao. See the
  [upstream license](https://github.com/lllllllama/RigorPilot-Skills/blob/56bc41c40beabc42f5628f06bb2634a5196071f5/LICENSE).
- Relationship: conceptual influence identified by the user and combined with
  personal work experience and local Codex/AGENTS redesign. Chronology and
  broad role are consistent with that influence, but direct textual derivation
  remains unproven.

### Adopted

- Explicit positive and negative triggers, inputs, outputs, and phase limits.
- Direct project evidence before filename-based inference.
- Explicit ambiguity instead of overcommitting to a guessed command.
- Separation of discovery from installation, asset acquisition, execution, and
  high-risk patching.
- A smallest-sufficient handoff to the next workflow.

### Adapted

- README-first reproduction intake became repository-wide, task-relevant
  evidence collection across instructions, documentation, manifests, CI, and
  scripts.
- The reproduction recommendation became an ephemeral intake contract, not a
  plan.
- Inference, evaluation, and training categories became generic verification
  candidates with explicit evidence status, source, environment owner, and
  side-effect or authorization notes.

### Rejected

- Mandatory README-first scanning and fixed file or directory lists.
- Deep-learning-specific command categories and checkpoint assumptions.
- The `scan_repo.py` and `extract_commands.py` heuristic scanners.
- Planning, environment setup, downloads, or command execution inside intake.
- Helper-tier or orchestrator-only invocation restrictions.

### Local Deviations

- Trigger only on a decision-relevant unknown, not repository unfamiliarity.
- Resolve Git worktree ownership, applicable instruction scope, dirty overlap,
  edit ownership, and verification ownership.
- Preserve user changes and hand execution, debugging, planning, coordination,
  and final verification to their dedicated workflows.

## OpenAI Codex Instructions

- Source: <https://learn.chatgpt.com/docs/agent-configuration/agents-md>
- Checked: 2026-07-11
- Adopted: rely on Codex's root-to-current-directory instruction chain and
  inspect an additional root-to-target chain only when the task target lies
  outside the currently applicable path.
- Local deviation: repository intake does not reimplement global instruction
  discovery or recursively enumerate all instruction files.

## Superpowers Baseline

- Source: <https://github.com/obra/superpowers/tree/v6.1.1/skills>
- Checked: 2026-07-11
- Finding: v6.1.1 has no directly corresponding repository-intake skill and was
  not used as the content source for this workflow.
