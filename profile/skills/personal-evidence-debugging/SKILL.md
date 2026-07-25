---
name: personal-evidence-debugging
description: Use for an unexpected local failure, wrong-reason check failure, flake, hang, or failed fix attempt before making another speculative change; not for an expected RED, ordinary status, or final verification.
---

# Personal Evidence Debugging

Find the strongest supported causal explanation with the smallest useful
investigation.

1. Reproduce with the narrowest command and separate target behavior from
   setup, fixture, dependency, or unrelated baseline failure.
2. Locate the first causally useful anomaly, not merely the final log line.
3. State one hypothesis, its predicted observation, and a falsifier.
4. Run one bounded check that distinguishes that hypothesis.
5. If evidence supports it and fix authority exists, make the smallest
   cause-backed correction and rerun the same reproduction.

If direct evidence already exposes the mechanism, skip extra hypothesis
ceremony. A failed fix is new evidence: change the causal model or inspected
boundary instead of stacking a fallback, wrapper, or another guess.

For flakes and hangs, inspect only relevant timing, ordering, shared state,
resources, environment, and nearest trustworthy working path. There is no
fixed attempt count.

Label the conclusion `confirmed`, `likely`, or `unknown` in ordinary prose.
Diagnosis alone does not authorize a fix, restart, relaunch, or ongoing
monitoring. Report the mechanism, evidence, uncertainty, and smallest useful
next action.

Read `references/source-notes.md` only when maintaining provenance.
