# Source Notes

Checked: 2026-07-19.

## Sources

- [Superpowers `brainstorming` v6.1.1](https://github.com/obra/superpowers/blob/v6.1.1/skills/brainstorming/SKILL.md),
  commit `d884ae04edebef577e82ff7c4e143debd0bbec99`, MIT, Copyright
  (c) 2025 Jesse Vincent: scope decomposition, component boundaries, inline
  design review, and selective visual assistance.
- Local portable `AGENTS.md`: authorization, discussion signals, ask-first
  boundaries, simple-task handling, and Chinese user output.
- Local `personal-grilling`: explicit-only semantic coverage gate and
  confirmation owner.
- User feedback from tasks `019f6f4d-ed8f-7661-a773-9a48e901df56` and
  `019f7484-3ca3-7dd2-9800-eb31185baafe` on 2026-07-19: decisions that were
  verbally locked were later compressed or forgotten; stable IDs, explicit
  replacement chains, and a persistent recovery ledger prevented recurrence.

## Local Preferences

- Run implicitly only for consequential design or concern work; bypass simple,
  explicit, low-risk edits.
- Recommend first, ask only decision-changing questions, and do not invent
  alternatives when one path clearly fits.
- Preserve the original request's authorization instead of adding a generic
  design approval gate.
- Keep brainstorming as the design-synthesis owner and grilling as the
  explicit-only coverage owner.
- Use the built-in plan by default and create no persistent design artifact
  for a simple task. For long-lived, multi-round, cross-session, recovery, or
  handoff work, maintain one scoped canonical decision record; this records
  discussion state and does not grant implementation authority.
- Preserve stable decision IDs, explicit replacement chains, and exact
  task-owned semantics across synthesis rather than relying on conversational
  memory or a lossy final summary.

No upstream script, asset, or substantial prose is copied.
