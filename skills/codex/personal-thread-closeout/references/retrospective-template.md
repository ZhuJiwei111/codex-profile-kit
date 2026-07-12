# Retrospective Template

Use this template only after the documentation value gate in `SKILL.md` passes.
Match the project's language and existing documentation conventions. Keep the
record compact and link to durable evidence instead of copying transcripts,
logs, or large diffs.

## Artifact Contract

Before writing, lock:

```yaml
retrospective:
  task_slug:
  task_outcome: completed | blocked | abandoned
  canonical_root:
  target_path:
  evidence_cutoff:
  documentation_reason:
  canonical_facts_updated: []
  protected_or_omitted_content: []
```

- Prefer an established retrospective, ADR, or postmortem location.
- Otherwise use `docs/retrospectives/<YYYY-MM-DD>-<task-slug>.md`.
- Select a short stable slug from the task objective, not from transient error
  text or sensitive content.
- Refuse an existing target or symlink. Do not overwrite an earlier record.
- Treat the retrospective as a historical evidence record. Correct a material
  error through a new clearly linked correction rather than silently rewriting
  the past.

## Markdown Shape

```markdown
# <Task title>

- Date: <YYYY-MM-DD>
- Outcome: <completed | blocked | abandoned>
- Evidence cutoff: <timestamp or final verified revision>
- Scope: <bounded task scope>

## Result

<What happened, without promotional language or a generic task summary.>

## Verified facts

- <fact and evidence anchor>

## Decisions

- <decision, reason, and material alternative rejected>

## Effective approaches

- <reusable method and the condition under which it worked>

## Failed attempts and learned boundaries

- <attempt, observed evidence, and what it ruled out>

## Documentation changes

- <canonical path and fact updated, or explicit skip reason>

## Remaining unknowns or resume conditions

- <unknown, blocker, owner, or exact discriminator>

## Candidate personal-workflow improvements

- <proposal only; no claim that AGENTS, skills, hooks, or profile-kit changed>

## Verification and repository state

- <checks, exit status, revision/diff identity, uncommitted state, and not-run items>
```

Omit empty sections when that improves clarity, except `Result`,
`Documentation changes`, and `Verification and repository state`, which make
the closeout boundary reproducible. Never turn an inference into a verified
fact merely to complete the template.

## Documentation Decision Examples

- A five-minute typo fix with no reusable lesson: `skip`.
- A failed attempt that only repeated a known error: `skip`.
- A failed migration that established a reusable recovery sequence:
  `create_retrospective`, and update troubleshooting docs when the recovery
  contract is verified.
- A new verified CLI default that made README text stale: `update_existing`.
- A consequential design decision plus a stale canonical description: `both`.
