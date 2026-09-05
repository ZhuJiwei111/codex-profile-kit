---
name: diagnosing-bugs
description: Investigate complex regressions, intermittent failures, or bugs that remain unexplained after a focused evidence check. Also use when explicitly invoked. Ordinary errors and directly explained failures belong to personal-evidence-debugging.
---

# Diagnosing Bugs

Use the phases that distinguish the remaining causes. Existing logs, source,
or a focused check may already establish the mechanism; proceed to the next
useful action without rebuilding evidence or completing every phase. For
ordinary failures, use `personal-evidence-debugging` instead of this workflow.
Diagnosis alone does not authorize fixes, instrumentation writes, heavy
resource use, or external actions.

When exploring the codebase, read `CONTEXT.md` (if it exists) to get a clear mental model of the relevant modules, and check ADRs in the area you're touching.

## Redact

This skill has you show commands, outputs and captured artifacts. **Redact every secret first** — write `<REDACTED>` in its place. Build loops against env vars, so the credential stays in the environment rather than in what you show. Captured artifacts carry auth headers: quote only the lines that carry the signal.

If the redacted output is not enough to diagnose the bug, say so and ask the user.

## Phase 1 — Build a feedback loop

Prefer a focused signal for the reported symptom. Reuse an existing check;
build a new loop only when it can resolve uncertainty or verify a correction.

### Ways to construct one — try them in roughly this order

1. **Failing test** at whatever seam reaches the bug — unit, integration, e2e.
2. **Curl / HTTP script** against a running dev server.
3. **CLI invocation** with a fixture input, diffing stdout against a known-good snapshot.
4. **Headless browser script** (Playwright / Puppeteer) — drives the UI, asserts on DOM/console/network.
5. **Replay a captured trace.** Save a real network request / payload / event log to disk; replay it through the code path in isolation.
6. **Throwaway harness.** Spin up a minimal subset of the system (one service, mocked deps) that exercises the bug code path with a single function call.
7. **Property / fuzz loop.** For input-dependent failures, use bounded generated inputs that exercise the suspected pattern.
8. **Bisection harness.** If the bug appeared between two known states (commit, dataset, version), automate "boot at state X, check, repeat" so you can `git bisect run` it.
9. **Differential loop.** Run the same input through old-version vs new-version (or two configs) and diff outputs.
10. **HITL bash script.** Last resort. If a human must click, drive _them_ with `scripts/hitl-loop.template.sh` so the loop is still structured. Captured output feeds back to you.

### Tighten the loop

Treat the loop as a product. Once you have _a_ loop, **tighten** it:

- Can I make it faster? (Cache setup, skip unrelated init, narrow the test scope.)
- Can I make the signal sharper? (Assert on the specific symptom, not "didn't crash".)
- Can I make it more deterministic? (Pin time, seed RNG, isolate filesystem, freeze network.)

### Non-deterministic bugs

Use bounded repetitions or targeted timing probes within the authorized
resource budget. Record the observed failure rate and uncertainty; rare
failures can still provide useful evidence. Increase load only when it can
distinguish a supported hypothesis and the resource use is authorized.

### When you genuinely cannot build a loop

Use available source and redacted artifacts to form a provisional explanation
and identify a distinguishing check. State what remains unverified. Ask for
missing access, a captured artifact, or instrumentation authority only when
the next useful action depends on it; continue independent authorized analysis.

### Assess the signal

A useful loop exercises the reported symptom and can distinguish failure from
success. Report the command and consequential result when run, including any
limits on reproducibility. Source inspection and hypothesis formation can
precede a runnable loop; neither alone proves the fix.

## Phase 2 — Reproduce + minimise

When a loop is available, run it and inspect whether it captures the symptom.

Confirm:

- [ ] The loop produces the failure mode the **user** described — not a different failure that happens to be nearby. Wrong bug = wrong fix.
- [ ] Reproducibility or the observed failure rate is recorded, including uncertainty for intermittent failures.
- [ ] You have captured the exact symptom (error message, wrong output, slow timing) so later phases can verify the fix actually addresses it.

### Minimise

Once it's red, shrink the repro to the **smallest scenario that still goes red**. Cut inputs, callers, config, data, and steps **one at a time**, re-running the loop after each cut — keep only what's load-bearing for the failure.

Why bother: a minimal repro shrinks the hypothesis space in Phase 3 (fewer moving parts left to suspect) and becomes the clean regression test in Phase 5.

Stop minimising when the remaining example is sufficient to distinguish the
cause and verify a correction. Reuse an already adequate reproduction.

## Phase 3 — Hypothesise

Start with the strongest evidence-backed hypothesis. Add competing hypotheses
only when plausible alternatives change the next check; no fixed count is
required. Revise the explanation when observations contradict it.

Each hypothesis must be **falsifiable**: state the prediction it makes.

> Format: "If <X> is the cause, then <changing Y> will make the bug disappear / <changing Z> will make it worse."

If you cannot state the prediction, the hypothesis is a vibe — discard or sharpen it.

Explain the working hypothesis and distinguishing check when useful. Continue
authorized checks without an extra approval checkpoint; unresolved user-owned
choices still require an explicit answer before dependent work.

## Phase 4 — Instrument

Each probe must map to a specific prediction from Phase 3. **Change one variable at a time.**

Tool preference:

1. **Debugger / REPL inspection** if the env supports it. One breakpoint beats ten logs.
2. **Targeted logs** at the boundaries that distinguish hypotheses.
3. Never "log everything and grep".

**Tag every debug log** with a unique prefix, e.g. `[DEBUG-a4f2]`. Cleanup at the end becomes a single grep. Untagged logs survive; tagged logs die.

**Perf branch.** For performance regressions, logs are usually wrong. Instead: establish a baseline measurement (timing harness, `performance.now()`, profiler, query plan), then bisect. Measure first, fix second.

## Phase 5 — Fix + regression test

When a fix is authorized, prefer a regression test before the fix if a useful
test seam exists and the test adds meaningful protection. Reuse an existing
focused check for a reversible, low-impact correction when that is sufficient.

A correct seam is one where the test exercises the **real bug pattern** as it occurs at the call site. If the only available seam is too shallow (single-caller test when the bug needs multiple callers, unit test that can't replicate the chain that triggered the bug), a regression test there gives false confidence.

If no suitable automated seam exists, report the verification limitation and
use the strongest practical check. This alone does not establish an
architectural defect or authorize a refactor.

When adding a regression test is warranted and a correct seam exists:

1. Turn the minimised repro into a failing test at that seam.
2. Watch it fail.
3. Apply the fix.
4. Watch it pass.
5. Re-run the Phase 1 feedback loop against the original (un-minimised) scenario.

## Phase 6 — Cleanup + post-mortem

For an implemented fix, run the appropriate original check and any added
regression test. Reuse that result at closeout; broaden or repeat checks only
for new changes, failures, or unresolved concerns. For diagnosis-only work,
report the supported cause, uncertainty, and smallest next action.

Remove only task-created temporary instrumentation and artifacts. Report the
mechanism, changed paths, and meaningful verification limits. Recommend an
architectural follow-up only when the evidence warrants it; implementation,
Git actions, and external publication require their matching authority.
