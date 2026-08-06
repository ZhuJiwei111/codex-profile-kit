# `.agent/` project audit journal

This journal is the human-readable history of substantive work in this Git
repository. It records what happened and why; it is not proof of current state,
an active task plan, or the binding decision owner.

## Layout

- `JOURNAL.md` indexes monthly journals, newest month first.
- `journal/YYYY-MM.md` stores that month's entries, newest entry first.
- Existing project-specific journal layouts remain valid and are not migrated
  automatically.

## Importance

- `high`: authority, scope or contract changes, critical gates, root causes,
  costly pitfalls, external actions, handoffs, and final outcomes.
- `medium`: material implementation, diagnosis, phase progress, or changed
  risk.
- `routine`: ordinary substantive analysis, verification, or maintenance.

Detail is proportional to importance. Completion alone is never a reason to
compress an important result to one line.

## Entry template

```markdown
## YYYY-MM-DDTHH:MM:SS+08:00 · high|medium|routine · topic

- **目标**：request or purpose
- **结果**：outcome or decision
- **改动**：task changes, separating journal maintenance
- **验证 / 证据**：fresh checks or evidence anchors
- **决定 / 风险**：authority, supersession, caveat, or remaining risk
- **状态 / 后续**：observed state and concrete continuation
```

## Rules

1. Preserve historical entry bytes. Add a correction entry instead of silently
   rewriting an earlier fact.
2. Do not record secrets, full internal addresses, personal data, raw large
   logs, or unsupported inference.
3. Record only Git and external state already observed before the journal edit;
   do not predict later commit or push results.
4. Keep journal files trackable, but never stage, commit, or push without
   matching authority.
5. When a safe exact append is impossible, leave the journal unchanged and
   report the missing entry.
