# Source Notes

Checked: 2026-07-13.

This skill combines pinned upstream interview discipline, two local historical
revisions, the accepted behavior of adjacent personal skills, and the user's
reported working experience. Upstream sources are design evidence, not runtime
dependencies and not text to copy mechanically.

## Contents

- [Sources](#sources)
- [Adopted](#adopted)
- [Deliberately Rejected](#deliberately-rejected)
- [Local History And Regression Analysis](#local-history-and-regression-analysis)
- [User-Locked Local Decisions](#user-locked-local-decisions)
- [License Notice](#license-notice)

## Sources

| Source | Pin or status | License/status | Role |
| --- | --- | --- | --- |
| [`grill-me`](https://github.com/mattpocock/skills/blob/d574778f94cf620fcc8ce741584093bc650a61d3/skills/productivity/grill-me/SKILL.md) | v1.1.0 annotated tag object `eabea89380927aadb93abf6e290a19334d249292`; commit `d574778f94cf620fcc8ce741584093bc650a61d3` | MIT, Copyright (c) 2026 Matt Pocock | Manual entry point |
| [`grilling`](https://github.com/mattpocock/skills/blob/d574778f94cf620fcc8ce741584093bc650a61d3/skills/productivity/grilling/SKILL.md) | v1.1.0 at the same commit | MIT | Decision-tree walk, one-at-a-time questions, facts versus decisions, and confirmation gate |
| [Current upstream repository](https://github.com/mattpocock/skills) | `main` observed by `git ls-remote` at `391a2701dd948f94f56a39f7533f8eea9a859c87` on 2026-07-13 | MIT | Current README still describes resolving every decision-tree branch; `grill-me` is a thin manual wrapper over `grilling` |
| [v1.1.0 release](https://github.com/mattpocock/skills/releases/tag/v1.1.0) | Released 2026-07-08 | Verified GitHub release | Evidence for explicit confirmation and the facts-versus-decisions split |
| Local pre-refactor `personal-grilling` | profile-kit commit `c5370e8b0dd71577cd7dda93609b019316c2587d` | Personal work | Explicit design-tree walk and required coverage of goal, scope, non-goals, acceptance, decisions, and risks |
| Local prior refactor | profile-kit commit `6057e9d64a633534f28b7c2e50cc907b4b1a3d4c` | Personal work | Manual-only metadata, one-question pacing, assumptions, source notes, and downstream authorization handoff |
| Current `personal-brainstorms` and adjacent personal workflows | Active profile checked 2026-07-13 | Personal profile system | Design ownership, evidence boundaries, risk verification, source provenance, context, authorization, and handoff contracts |
| User working experience | Explicit feedback and sequential decisions on 2026-07-13 | Personal experience, not an external authority | Reported false negatives: the agent often stopped after one easy question and required the user to surface source, compatibility, portability, smoke, rollback, and cross-skill concerns |

The current upstream `grill-me` file is intentionally small. The reusable
behavior lives in `grilling`; the local skill keeps one Codex-native manual
entry point instead of reproducing that two-skill wrapper structure.

## Adopted

- Manual invocation and a hard no-implementation gate during grilling.
- Walk the decision tree and resolve user-owned decisions one at a time.
- Research discoverable facts instead of asking the user for them.
- Keep decisions user-owned and wait for explicit answers.
- Provide a recommendation with the material tradeoff.
- Use no numeric question limit.
- Require explicit shared-understanding confirmation before handoff.
- Restore the old local revision's explicit coverage duty.
- Add a universal core, task-type packs, dependency propagation, sourced leaf
  statuses, material risk dispositions, and three closure passes.
- Treat the user's solution as a hypothesis and test smaller alternatives,
  second-order effects, and failure conditions.
- Accept concise exact choices without inventing a rationale requirement.

## Deliberately Rejected

- Hostile, theatrical, or performative interpretations of “relentless.”
- Asking every imaginable question regardless of materiality.
- Treating a finite checklist as formal proof of semantic completeness.
- Automatically writing domain docs or adopting `grill-with-docs` behavior.
- Reading unrelated repositories, tasks, sessions, memories, hosts, or secrets.
- Persisting a ledger without the trigger and authority of the owning context or
  planning workflow.
- Allowing a preauthorized implementation request to skip coverage
  confirmation.
- Requiring verbose rationales for unambiguous option choices.
- Enacting, staging, committing, publishing, or pushing a plan from inside this
  skill.

## Local History And Regression Analysis

The `c5370e8` revision explicitly required walking the design tree until the
goal, scope, non-goals, acceptance criteria, decisions, risks, and open questions
were ready for a planner. The `6057e9d` revision improved question admission,
facts-versus-decisions, confirmation, and composition, but its lead objective
became “the fewest questions needed.” Combined with a strict admission gate and
the lightweight posture of `personal-brainstorms`, that created a false-negative
bias: the skill filtered a small candidate set rather than proving that the
candidate set covered the problem.

The current design keeps the later revision's useful controls but reverses the
order:

1. discover and classify coverage;
2. investigate facts;
3. ask only unresolved material user decisions;
4. propagate consequences;
5. prove closure through coverage, consistency, adversarial review, and user
   confirmation.

## User-Locked Local Decisions

- Default to coverage-first hard grilling with no session question cap.
- Use a universal core plus dynamic task-type packs.
- Allow only explicit user deferral for material items.
- Require coverage, consistency, and adversarial closure passes.
- Make grilling an independent gate when paired with brainstorming.
- Show concise per-answer deltas and a full ledger before closure.
- Challenge the proposed solution while leaving final material decisions with
  the user.
- Keep exactly one material decision per turn.
- Work one material theme at a time and open every new theme with one neutral
  open-ended question before recommendations or options.
- Give every question no timeout; silence and elapsed UI time never resolve,
  defer, or confirm it.
- Require explicit coverage confirmation even after preauthorization.
- Investigate decision-changing facts proactively and boundedly.
- Require an explicit disposition for every material residual risk.
- Let a short option answer close only the current leaf and propagate its
  consequences.
- Record a source type for every leaf.
- Accept the bounded residual risk that semantic completeness cannot be
  formally proven.
- Keep brainstorming as the sole design-synthesis owner; grilling returns only
  its sourced ledger and closure status.

Post-implementation forward probes added explicit branches for profile
bootstrap/self-update trust roots, deletion/rename/tombstone propagation,
prediction-time information boundaries and feature lineage, independent
experimental units and pseudoreplication, plus a complete-but-proportionate
ledger rule for simple tasks. Follow-up review added explicit multi-writer
conflict semantics and evaluation-selection/multiplicity boundaries. These are
local regression findings, not claims that the upstream sources name those
domains.

## License Notice

MIT License

Copyright (c) 2026 Matt Pocock

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the “Software”), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
