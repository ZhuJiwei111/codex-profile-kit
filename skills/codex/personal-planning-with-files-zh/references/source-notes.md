# Source Notes

Checked: 2026-07-18.

## Source

- [`OthmanAdi/planning-with-files` v3.4.0](https://github.com/OthmanAdi/planning-with-files/releases/tag/v3.4.0),
  commit [`d71b3be47b62fe49d60fb2ede800e1907ebea3d9`](https://github.com/OthmanAdi/planning-with-files/tree/d71b3be47b62fe49d60fb2ede800e1907ebea3d9),
  including the [Simplified Chinese skill](https://github.com/OthmanAdi/planning-with-files/blob/d71b3be47b62fe49d60fb2ede800e1907ebea3d9/skills/planning-with-files-zh/SKILL.md),
  MIT, Copyright (c) 2026 Ahmad Adi.
- Relevant upstream failure reports: [unrelated plan attachment
  #195](https://github.com/OthmanAdi/planning-with-files/issues/195),
  [forced unfinished-plan continuation
  #178](https://github.com/OthmanAdi/planning-with-files/issues/178), and
  [hooks before plan review
  #190](https://github.com/OthmanAdi/planning-with-files/issues/190).

## Adopted Principles

- Keep the plan, durable evidence, and current progress separate.
- Treat disk state as resumable memory rather than current proof or authority.
- Reconcile restored state with the current workspace before acting.

## Local Preferences

- Invoke manually and restore only from the current project on the current
  machine.
- Store multiple independent plans at
  `.planning/plans/<YYYYMMDD>-<slug>/`, each with exactly `task_plan.md`,
  `findings.md`, and `progress.md`.
- Select one plausible candidate automatically and ask when several candidates
  remain plausible.
- Use only plan lifecycle states `active` and `closed`, with exactly one current
  phase in an active plan.
- Let Codex maintain the selected files automatically after material changes.
- Never reopen a closed plan; continue through a new successor.
- Exclude hooks, validators, transaction state, global latest-plan guessing,
  archive protocols, and forced continuation.

No upstream script, template, or substantial prose is copied.
