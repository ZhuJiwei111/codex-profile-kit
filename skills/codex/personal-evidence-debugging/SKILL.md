---
name: personal-evidence-debugging
description: Use for an unexpected local failure, wrong-reason test failure, flake, hang, or failed fix attempt before making another speculative change. Not for an expected test RED, an ordinary status check, or final verification.
---

# Personal Evidence Debugging

Trace an unexpected failure to the strongest supported causal explanation before
another change. Use the smallest investigation that resolves the uncertainty.

## Respect The Requested Scope

A diagnosis request permits bounded inspection and ephemeral probes, not a
durable fix. An existing fix or build request includes the bounded diagnosis and
cause-backed correction needed inside its authorized implementation scope.

An expected RED that fails for the intended behavior reason remains with
personal-test-first-changes. Use this skill when the failure is unexpected,
fails for the wrong reason, flakes, hangs, or persists after a fix.

## Fast Path

For a reproducible local failure:

1. State expected versus observed behavior.
2. Reproduce with the narrowest useful command and distinguish the target
   failure from setup, fixture, dependency, or unrelated baseline failure.
3. Identify the first causally useful failure, not merely the final log line.
4. State one hypothesis, its predicted observation, and what would falsify it.
5. Run one bounded discriminating check.

If direct evidence already exposes the mechanism, do not manufacture extra
hypothesis cycles. Under fix authority, apply only the smallest cause-backed
change and rerun the same discriminating check.

## Expand Only When Needed

For flakes, hangs, deep call chains, state pollution, repeated failed fixes, or
multi-component boundaries, also inspect only the relevant:

- environment, inputs, recent changes, and boundary state;
- nearest trustworthy working path and its material differences;
- producer of the first invalid value or state; and
- timing, ordering, shared-state, resource, or external variables that can
  change between runs.

Read references/investigation-techniques.md for these advanced cases.

Test one causal model at a time. If repeated cause-backed fixes or repeated
checks produce no new discriminating evidence, stop recombining the same model.
Summarize what each hypothesis predicted and observed, then choose a materially
different layer, boundary, or causal model before another product edit. There is
no fixed attempt count.

## Label The Conclusion

- confirmed: a specific mechanism explains the symptom and a discriminating
  observation or intervention changes the result as predicted.
- likely: it is the strongest supported explanation, but an inaccessible,
  timing, hardware, or external boundary prevents confirmation.
- unknown: the evidence establishes only correlation, symptom location, or
  competing explanations.

Do not claim inaccessible third-party internals as confirmed. A failed
cause-backed fix is new evidence, not permission to add another speculative
patch.

## Report

For diagnosis-only work, report the mechanism, confidence label, evidence,
unknowns, and smallest useful next action, then stop. For an authorized fix,
report the change and the before-and-after discriminating evidence.

Do not expose secrets or complete credential-bearing environment data. A failed
long job does not authorize polling, restart, repair, or relaunch. Final task
completion remains with personal-risk-verification.

Read references/source-notes.md only when maintaining provenance or revising
this skill.
