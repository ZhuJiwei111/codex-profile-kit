---
name: personal-repo-intake
description: Use only when a local repository's root or worktree, applicable instructions, relevant dirty state, edit surface, or verification command is genuinely unclear.
---

# Personal Repo Intake

Resolve only repository uncertainties that would change where or how scoped
work can safely begin. This skill is read-only, bounded, and ephemeral.

## Trigger Gate

Use this skill only when at least one of these is genuinely unclear:

- the task-owned repository root, worktree, workspace, or canonical `cwd`;
- the project instructions that apply to the target path;
- whether existing user changes overlap the likely edit surface;
- whether the task should change source, generated output, or another owner;
- the task-relevant verification command, harness, or environment owner.

Skip it when those facts are already known and fresh. First exposure to a
repository is not enough by itself. When a failure is already known and its
repository boundary is clear, go directly to debugging; if that boundary is
unclear, resolve only the missing intake facts before handing off. Also skip
this skill for final verification, Git finish work, or a simple explicit
low-risk edit whose work boundary is already clear.

Skipping this skill does not waive applicable instructions or global
repository-safety checks.

## Owned Intake Result

Return a compact result in the conversation; do not persist it as project
state:

```yaml
canonical_root:
task_cwd_or_worktree:
applicable_instructions:
repo_state: clean | dirty_nonoverlap | dirty_overlap | not_git | unknown
edit_surface:
generated_or_owned_by:
verification_candidates:
  - command_or_target:
    purpose:
    source_path:
    evidence_status: explicit | inferred | conflicted | unknown
    environment_owner:
    effects_or_authorization:
blocking_unknowns:
next_owner:
intake_status: ready | ready_with_nonoverlap | needs_user_decision
```

- `canonical_root` is the task-owned Git worktree top level or an unambiguous
  non-Git workspace, not a Git common directory or another checkout.
- `dirty_nonoverlap` does not block later work. Treat untracked files as user
  work too.
- The result records facts and uncertainty; it does not broaden authorization,
  create a plan, or become durable context state.

## Bounded Workflow

1. Reuse exact paths, handoffs, and still-fresh session facts. Do not rediscover
   known state.
2. Resolve root or worktree ownership only if unclear. Start with `pwd` and the
   Git top level; inspect Git directory, common directory, submodule, symlink,
   or linked-worktree details only when they affect ownership.
3. Use the already applicable instruction chain. If the target lies outside
   that path, inspect only the root-to-target chain needed for that target; do
   not scan every `AGENTS.md` in the repository.
4. Classify existing changes against the candidate edit surface. Read only the
   minimal relevant diff when overlap is possible. Never clean, revert, or
   overwrite user work to simplify intake.
5. Identify the edit owner from precise project evidence such as paths,
   symbols, manifests, generators, scripts, or CI configuration. Do not treat
   directory names as a universal generated-file blacklist.
6. Identify task-relevant verification candidates and their environment or
   side-effect requirements. Do not run tests, builds, installers, generators,
   downloads, environment creation, or other substantive project commands.
7. Stop as soon as the intake result is sufficient for the next workflow.

## Evidence Discipline

- Prefer exact project evidence over filename guesses. Compare applicable
  instructions, documentation, manifests, CI, and scripts when relevant.
- Mark a candidate `explicit` only when a project artifact states the exact
  command or target. Mark assembled or guessed candidates `inferred`.
- Use `conflicted` when relevant sources disagree; preserve the conflict rather
  than choosing silently. Use `unknown` when evidence remains insufficient.
- A documented command is evidence, not execution authority or proof that the
  command is current, safe, cheap, or available in the active environment.
- Do not reproduce credential-bearing commands or values. Redact sensitive
  material and report only the source path and configuration category.

## Stop And Route

- `ready`: decision-changing uncertainties are resolved; hand off.
- `ready_with_nonoverlap`: unrelated user changes exist; record the protected
  boundary and hand off.
- `needs_user_decision`: root or owner remains genuinely ambiguous, overlapping
  work cannot be preserved safely, or environment choices materially change
  behavior or cost. Ask one decision-changing question.
- If a discovery command fails unexpectedly, record its command, `cwd`, exit
  status, and compact error evidence. Do not turn intake into debugging.

Route design to `personal-brainstorms`, durable plans to
`personal-planning-with-files-zh`, executable behavior checks to
`personal-test-first-changes`, known failures to `personal-evidence-debugging`,
and retrieval bloat to `personal-context-optimization`. Route worker contracts
to `personal-subagent-boundaries`, multi-worktree coordination to
`personal-multiline-coordination`, final evidence to
`personal-risk-verification`, and Git readiness to `personal-branch-finish`.
A coordinator may pass this result to workers; workers should not rescan unless
a relevant fact is stale or contradicted.

See [source notes](references/source-notes.md) for external design evidence and
local deviations.
