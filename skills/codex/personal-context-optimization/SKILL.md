---
name: personal-context-optimization
description: Use when context, tool output, retrieval noise, repeated re-reading, or subtask context mixing is slowing work down or increasing token cost without improving quality.
---

# Personal Context Optimization

Reduce noise before compressing signal. Context quality matters more than raw
context size.

## Priority Order

1. Scope retrieval: search exact paths, symbols, commands, and docs.
2. Mask resolved verbose tool output after key facts are captured.
3. Compact old turns with `personal-context-compression` when state must survive.
4. Partition only when there are at least three independent subtasks or one
   context cannot hold the useful evidence.

## Guardrails

- Measure the dominant source of context first: tool output, docs, history, or
  mixed subtasks.
- Never hide recent error output during active debugging.
- Preserve retrievability: keep path, command, or reference ID for elided output.
- Do not optimize prompts by adding more process text.
- If an optimization does not reduce re-reading or improve focus, remove it.

## Signals

Use this when you see repeated re-reading, irrelevant retrieval, lost decisions,
large duplicate outputs, or subagents carrying unrelated context.
