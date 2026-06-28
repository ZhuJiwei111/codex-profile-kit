---
name: personal-evidence-debugging
description: Use when a test, command, app behavior, build, import, training job, or script fails unexpectedly, flakes, hangs, or repeats the same failure during local diagnosis.
---

# Personal Evidence Debugging

Debug from concrete evidence. Do not patch from vibes.

## Loop

1. Capture the exact failing command, symptom, traceback, log line, or observed
   behavior.
2. Form one active hypothesis and inspect the smallest relevant surface.
3. Change one thing at a time.
4. Re-run the narrowest check that can confirm or reject the hypothesis.
5. If the same failure repeats twice, change tactic: inspect a different layer,
   reduce the case, check environment/config, or ask for missing context.

## Guardrails

- Prefer reproducing the failure before editing code.
- If reproduction is expensive, find a cheaper proxy such as a unit test, import
  check, parser check, dry run, or focused log read.
- Preserve useful error text in the final summary, but do not dump long logs.
- Never hide a failed verification command.
- After repeated failures, summarize the lesson and record durable guidance only
  in the narrowest correct scope: project `AGENTS.md` for repo-specific rules,
  global `AGENTS.md` only for server-wide behavior and only when requested or
  clearly in scope.
