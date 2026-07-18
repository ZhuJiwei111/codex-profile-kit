---
name: personal-planning-with-files-zh
description: Manual only. Use $personal-planning-with-files-zh to create, select, resume, update, close, or succeed a durable plan stored in the current local project, including projects with multiple independent plans.
---

# Personal Planning With Files Zh

Persist an explicitly requested plan inside the current project. Write
user-visible planning content in Chinese unless an external convention requires
otherwise. Keep implicit invocation disabled; use the built-in plan for ordinary
multi-step work.

## Store Independent Plans

Use one directory per plan and allow several plans to coexist:

```text
<project-root>/.planning/plans/<YYYYMMDD>-<slug>/
├── task_plan.md
├── findings.md
└── progress.md
```

Use the local date and a unique lowercase kebab-case slug. Do not create a root
coordinator file, nested plan, symlink, path escape, or duplicate source of
truth.

Keep each file narrow:

- `task_plan.md`: plan ID, `active` or `closed` status, goal, scope, non-goals,
  success criteria, one current phase, ordered phases, next action, and an
  optional predecessor plan ID.
- `findings.md`: verified facts and sources, decisions, assumptions, unknowns,
  invalidated evidence, and evidence cutoff.
- `progress.md`: completed work, current activity, checks and results,
  blockers, handoff state, and latest update time.

An active plan has exactly one current phase. Earlier phases are complete and
later phases are pending. A closed plan has no current phase. Do not create
parallel current phases or store detailed execution logs in `task_plan.md`.

## Select Or Restore Locally

Resolve the canonical root of the current project. Restore only from that
root's `.planning/plans/` on this machine; do not search other projects, hosts,
tasks, chats, memories, archives, or global state.

1. Honor an exact plan ID supplied by the user.
2. Otherwise inspect only enough metadata from local plan directories to find
   candidates relevant to the current request.
3. If exactly one candidate is plausible, select it automatically and report
   its ID, goal, status, and current phase.
4. If several candidates are plausible, show their IDs and distinguishing goal
   or phase, recommend the closest match, and ask the user to choose.
5. If none exists, create one only when the request authorizes a new
   file-backed plan; otherwise report that no matching plan was found.

Read `task_plan.md` first, then the selected plan's `findings.md` and
`progress.md`. Reconcile them with the current project state before relying on
old evidence. Mark stale or contradicted findings as invalidated rather than
silently treating them as current facts.

Do not auto-adopt unrelated or legacy planning files.

## Update Automatically

An explicit create, resume, or manage request authorizes scoped updates to the
selected plan's three files. Once selected, update them automatically after a
material change; do not request approval for each routine planning write.

- Update `findings.md` when evidence, a decision, an assumption, or an unknown
  materially changes.
- Update `progress.md` after meaningful work, validation, a blocker, or a
  handoff—not after every tool call.
- Update `task_plan.md` when scope or success criteria are approved, the current
  phase changes, the next action changes materially, or the plan closes.

Read back changed files and keep their claims consistent. Preserve unrelated
user edits and stop if another writer or an unresolved overlap makes a safe
update impossible.

Planning files are memory, not authority or proof. The surrounding request
still controls implementation, tests, long jobs, Git, publication, external
actions, and destructive work. A status-only request remains read-only unless
it explicitly asks to update planning state.

## Advance, Close, Or Continue

- Advance the current phase only after its completion evidence is recorded.
  Mark it complete and the next ordered phase current in the same coordinated
  update, then verify that only one current phase remains.
- Close a plan when its success criteria are satisfied or the user explicitly
  ends or defers it. Record the outcome and remaining risk in `progress.md`, set
  status to `closed`, clear the current phase, and preserve the files in place.
- Never reopen a closed plan. Continued work requires a new active successor
  directory with a new `<YYYYMMDD>-<slug>` ID. Record the predecessor ID and
  carry forward only still-relevant decisions and revalidated evidence.
- Do not mutate the predecessor while creating or operating the successor.

At handoff, report the selected plan path, status, current phase, fresh evidence
cutoff, completed checks, blockers, and exact next action.

## Resource

Read [source-notes.md](references/source-notes.md) only for provenance or
maintenance.
