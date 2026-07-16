# Source Notes

Checked: 2026-07-12.

This skill uses upstream completion-verification material as design evidence.
Local authorization, user-change protection, risk proportionality, bounded
context, and specialist workflow ownership take precedence. The available
history does not prove that the initial local text was copied from upstream.

## Superpowers `verification-before-completion`

- Release: [v6.1.1](https://github.com/obra/superpowers/releases/tag/v6.1.1)
- Annotated tag object: `c984ea2e7aeffdcc865784fd6c5e3ab75da0209a`
- Peeled release commit: `d884ae04edebef577e82ff7c4e143debd0bbec99`
- Pinned skill:
  <https://github.com/obra/superpowers/blob/d884ae04edebef577e82ff7c4e143debd0bbec99/skills/verification-before-completion/SKILL.md>
- Upstream skill Git blob: `2f14076e59e6ce5cd6f88007421a85f0bd772520`
- Upstream skill SHA-256:
  `ea52d15aabaf72bc6b558efe2c126f161b53961090ddcd712000273bfe8c7b6c`
- License: MIT, Copyright (c) 2025 Jesse Vincent. See the
  [pinned license](https://github.com/obra/superpowers/blob/d884ae04edebef577e82ff7c4e143debd0bbec99/LICENSE).
- License Git blob: `abf0390320aa14406af7a520b9b0739fdda9bf08`
- Audit note: upstream `main` matched the peeled v6.1.1 commit and pinned skill
  blob on the check date. The local baseline remains pinned to v6.1.1 if
  `main` later moves.

Related design evidence:

- Superpowers
  [`writing-skills`](https://github.com/obra/superpowers/blob/d884ae04edebef577e82ff7c4e143debd0bbec99/skills/writing-skills/SKILL.md),
  Git blob `6d3ded6e62ffdaaed7a84b52bc53f66e00e548be`, supplies the
  discipline-skill pressure-testing method.
- Superpowers
  [`systematic-debugging`](https://github.com/obra/superpowers/blob/d884ae04edebef577e82ff7c4e143debd0bbec99/skills/systematic-debugging/SKILL.md),
  Git blob `b0eca38b3cf9523ea86c9211e96949c8e69d1d1c`, separates
  debugging from final verification.

## Local History

- Initial local commit: `6574bce5f5ede8fb4566d0451ddcf613f7fdf8a5`
- Initial `SKILL.md` blob: `a3cd48e7a755af32d8566cd89a1784f555d2993f`
- Initial `agents/openai.yaml` blob:
  `ca751b422284d79cadbd389387ebb98cf16685c2`

The initialization commit also contained a separate route from the old generic
`code-simplifier` to upstream `verification-before-completion`. That supports a
conceptual relationship but does not establish direct textual derivation of
the 26-line local skill.

## Adopted

- Require fresh evidence before a completion, correctness, passing, or
  readiness claim.
- Map each claim to evidence that directly proves it instead of extrapolating
  from an unrelated check.
- Run the relevant check, read its semantic result and exit status, and report
  the actual outcome when it fails.
- Review requirements separately from test results.
- Inspect delegated work and its evidence rather than accepting a worker's
  success summary as the final decision.

## Adapted

- Replace “run in this message” with evidence that applies after the last
  relevant change to the claimed surface.
- Reuse still-applicable evidence and rerun only checks invalidated by later
  relevant changes.
- Replace unconditional full-command language with risk-proportionate direct
  checks and explicit coverage gaps.
- Check bounded meaningful output, exit status, failure counts, and wrapper or
  pipeline semantics without forcing unbounded logs into context.
- Use a binary `supported | not_supported` verdict instead of relying on
  rhetoric or implicit satisfaction language.
- Treat final verification as a consumer of implementation, review,
  debugging, and documentation evidence rather than a replacement for those
  workflows.

## Rejected

- Punitive wording that equates incomplete verification with lying or threatens
  the agent.
- Triggering a full completion gate for every positive statement, delegation,
  intermediate pass, or move between implementation steps.
- Unconditional full-suite execution after unrelated changes.
- Reverting and restoring task or user code inside the completion gate to
  manufacture a regression RED.
- Treating a lint pass as build evidence, a worker report as completion
  evidence, or a local pass as proof of remote state.
- Mixing commit, push, PR creation, remote CI reruns, or review-thread mutation
  into local completion verification.
- Copying upstream persuasion tables, emoji examples, unsupported experience
  claims, or long rationalization lists into the local skill.

## Local Deviations

- Preserve unrelated user and prior-stage changes and scope the completion
  claim to task-owned work.
- Keep long-running checks, installation, network use, GPU resources,
  destructive work, and external mutation behind their existing authorization
  boundaries.
- A failed verification does not authorize diagnosis or another fix; route it
  to `personal-evidence-debugging` when that work is in scope.
- Documentation synchronization, test-first implementation, review handling,
  project explanation, and Git finish work retain their dedicated owners.
- Keep the completion record conversational and non-persistent unless another
  approved workflow owns a durable handoff.
- Render evidence-state boundaries in Chinese for user-visible reports while
  retaining stable English values only at machine-readable or external
  convention boundaries.
