---
name: personal-evidence-debugging
description: Diagnose an unexpected failure, hang, flake, or failed fix before another speculative change. Excludes expected test-first RED and routine completion checks.
---

# Personal Evidence Debugging

Find the cause with the smallest observation that can change the diagnosis.

- Pin down expected versus observed behavior and use the narrowest practical
  reproduction. Separate the target failure from setup, fixtures, and an
  unrelated baseline failure.
- Inspect the first causally useful anomaly and the affected boundary. When
  the mechanism is already visible, explain it and check the direct fix; a
  formal hypothesis sequence adds nothing.
- Otherwise choose one hypothesis, predict an observable result, and run a
  bounded check that distinguishes it from the alternatives.
- After a failed fix, revise the causal model or inspected boundary before
  making another change. There is no fixed retry count or automatic demand to
  redesign the architecture.

With fix authority, make the smallest supported correction and rerun the same
reproduction. Add a regression test when a repeatable behavior and an existing
harness justify one; retain no one-off diagnostic program without a real owner.
For a difficult reproduction, choose the cheapest useful signal: an existing
test, CLI or request fixture, captured trace replay, or old/new comparison.
For a regression with known good and bad revisions, a bounded bisection can
narrow the cause. Performance work needs a baseline at the affected operation;
measure the same workload after the change. Read code to find the right probe
when needed; no runnable reproduction is a prerequisite for useful inspection.
If direct reproduction is unavailable, work from the available evidence and
state the confidence limit. Ask for access or captured material only when it
blocks the next useful check.

For flakes and hangs, inspect relevant ordering, resources, timing, and shared
state rather than adding blind sleeps, retries, or fallbacks.

Report the cause as confirmed, likely, or unknown, with the evidence and any
remaining uncertainty. A diagnosis request does not authorize a restart,
relaunch, monitoring, or unrelated fix.

Read `references/source-notes.md` only when maintaining provenance.
