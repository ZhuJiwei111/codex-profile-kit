# Source Notes

## Fixed Source

- Checked: 2026-07-11
- Project: `OthmanAdi/planning-with-files`
- Release: [`v3.4.0`](https://github.com/OthmanAdi/planning-with-files/releases/tag/v3.4.0)
- Fixed commit: [`d71b3be47b62fe49d60fb2ede800e1907ebea3d9`](https://github.com/OthmanAdi/planning-with-files/tree/d71b3be47b62fe49d60fb2ede800e1907ebea3d9)
- English skill: [`skills/planning-with-files/SKILL.md`](https://github.com/OthmanAdi/planning-with-files/blob/d71b3be47b62fe49d60fb2ede800e1907ebea3d9/skills/planning-with-files/SKILL.md)
- Simplified Chinese skill: [`skills/planning-with-files-zh/SKILL.md`](https://github.com/OthmanAdi/planning-with-files/blob/d71b3be47b62fe49d60fb2ede800e1907ebea3d9/skills/planning-with-files-zh/SKILL.md)
- License: [MIT, Copyright (c) 2026 Ahmad Adi](https://github.com/OthmanAdi/planning-with-files/blob/d71b3be47b62fe49d60fb2ede800e1907ebea3d9/LICENSE)

Relevant upstream failure evidence remains:

- [One-shot sessions hijacked by unrelated plans, issue #195](https://github.com/OthmanAdi/planning-with-files/issues/195)
- [Unfinished plans forced to continue, issue #178](https://github.com/OthmanAdi/planning-with-files/issues/178)
- [Hooks activated before plan review, issue #190](https://github.com/OthmanAdi/planning-with-files/issues/190)

## Adopted Principles

- Keep goals, durable evidence, and current progress distinct.
- Treat disk state as resumable memory, not current proof or authority.
- Reconcile restored state with the current workspace before action.
- Keep external material sourced and keep attachment explicit.
- Preserve compact restart questions and clear handoff state.

## Rejected Upstream Mechanics

- Automatic triggers based on complexity, tool calls, or elapsed work.
- Hook injection, forced continuation, session-database catch-up, or latest-plan
  guessing.
- Autonomous loops, broad attestation, and copied upstream scripts or templates.

The local skill has no planning hooks. Explicit selection and a semantic opt-out
prevent unrelated plan attachment at the source.

## Local Design

The following contract is local and is not represented as upstream behavior:

- One concise project-root `task_plan.md` and no root findings/progress.
- Ordered serial phase trios with exactly one active phase.
- Root ownership limited to global goal, scope, acceptance, phase order, pointer,
  and overall status.
- Phase-local goal, evidence, progress, checks, and handoff.
- One canonical coordinator writer; executors return handoffs only.
- Explicit draft activation, approval-bound phase switch, correction, archive,
  and successor decisions without claiming cross-file atomicity.
- Root-anchored no-follow validation, exact phase and namespace ownership, and
  a final sequential identity/hash recheck.
- Simple exact-file snapshots for confirmed non-sensitive content, redacted
  incident records for sensitive correction, and append-only correction notes,
  without a generation, frozen-trust, packet, lineage, or persistent
  transaction model.
- A standard-library read-only validator that checks root/phase identity,
  serial state, path and symlink safety, source hashes, and concurrent reads.

This revision deliberately replaces the earlier local repo/task hierarchy,
generation rollover, initialization selector, frozen-record trust, and staging
transaction design. Those were local experiments, not upstream requirements.

No upstream template, script, or substantial prose is copied. Source concepts
are re-expressed under the local Codex authorization model; the fixed source and
license remain recorded for audit.
