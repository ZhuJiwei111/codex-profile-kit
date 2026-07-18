---
name: personal-risk-verification
description: Use as the single final evidence gate after task-owned local changes and before claiming completion, correctness, passing checks, or handoff readiness; not for intermediate testing, diagnosis, fixes, or Git actions.
---

# Personal Risk Verification

Make the final local completion judgment after the last relevant task-owned
change. Earlier tests, worker reports, reviews, and debugging results are
evidence inputs, not the final judgment.

The main process owns this gate. A delegated validator may gather evidence or
offer a non-authoritative recommendation, but it cannot decide task completion.

## Verify Proportionately

1. Re-read the requested outcome, acceptance criteria, scope, and applicable
   instructions.
2. Inspect the final task-owned diff, artifacts, and user-visible result while
   separating unrelated work.
3. Map each material completion claim to evidence that could fail if the claim
   were wrong. Reuse earlier evidence only when no later relevant change made
   it stale.
4. Run the smallest fresh, safe checks needed to close material gaps. Inspect
   meaningful output, exit status, collection scope, skips, warnings, and the
   actual resulting artifact or diff.
5. State checks not run and the consequence of each omission.

Scale evidence to risk. Documentation may need final readback, links or literal
consistency, and diff inspection. Code behavior may need the focused
reproduction or regression check plus directly coupled checks. A build claim
needs the build; a remote, product, deployment, PR, or publication claim needs
evidence from that owning surface. Do not let one evidence layer imply another.

Evidence is fresh only for the state it covered. Later overlapping source,
configuration, generated output, dependency, artifact, or documentation
changes invalidate the affected part. A local pass never proves remote CI,
deployment, publication, reviewer, or service state.

Detect false passes such as zero tests collected, swallowed failures, material
skips, stale cached output, truncated decisive output, or warnings that
contradict the claim. If an unexpected failure needs diagnosis or a missing
requirement needs implementation, stop this gate and return the gap to the
owning workflow.

## Give One Semantic Conclusion

Return exactly one of two meanings in clear natural language:

- the current evidence is sufficient for every material in-scope completion
  claim; or
- the current evidence is insufficient for at least one material claim.

Do not require a fixed status token, YAML record, matrix, or prescribed prose.
In any compact format, make the conclusion, supporting evidence, relevant
checks not run, and remaining risk easy to distinguish. When evidence is
insufficient, name the failed or missing requirement and the exact next owner,
decision, authority, or check needed.

Do not implement, diagnose, install dependencies, start heavy or long checks,
mutate external state, stage, commit, push, or publish from this gate. A later
Git or publication workflow may consume the unchanged positive conclusion and
its evidence identity.

See [source notes](references/source-notes.md) only when maintaining this
skill's provenance.
