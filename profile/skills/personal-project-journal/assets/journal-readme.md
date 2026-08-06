# `.agent/` project audit journal

This journal is the human-readable history of durable project events in this
Git repository. It records what happened and why; it is not proof of current
state, an active task plan, or the binding decision owner.

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
- `routine`: ordinary durable maintenance or implementation.

Detail is proportional to importance. Completion alone is never a reason to
compress an important result to one line.

## What belongs here

Record repository changes, project-level decisions, confirmed root causes,
important blockers or costly failures, consequential external actions,
handoffs, and final outcomes. Ordinary explanation, browsing, repeated status,
and unchanged verification do not need an entry.

## Entry shape

```markdown
## YYYY-MM-DDTHH:MM:SS+08:00 · high|medium|routine · topic

Concise request and outcome summary.

- **改动**：include only when useful
- **证据**：include only evidence already gathered and worth retaining
- **影响 / 后续**：include only when consequential
```

Labels are optional. A routine entry can be one to three sentences. Do not fill
unused fields or run checks merely to complete an entry.

## Rules

1. Preserve the meaning of historical entries. Correct a material fact,
   decision, or conclusion with a new entry; spelling, punctuation, and
   meaning-preserving formatting may be fixed directly.
2. Do not record secrets, full internal addresses, personal data, raw large
   logs, or unsupported inference.
3. Record only Git and external state already observed before the journal edit;
   do not predict later commit or push results or create an entry solely for
   ordinary Git mechanics.
4. Keep journal files trackable, but never stage, commit, or push without
   matching authority.
5. When the normal append fails, leave the journal unchanged and report it
   instead of adding fallback write paths.
