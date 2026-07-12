# Source Notes

## Origin

- Upstream: `muratcankoylan/Agent-Skills-for-Context-Engineering`,
  `skills/context-optimization`.
- Origin assessment: high-confidence direct derivative based on the user's
  provenance information and the local rule structure; the local Git history
  contains no original attribution.
- Pinned repository commit:
  `c2b9a19107d263f965def4e8f7d1cd0d0fee1a59`.
- Stable release context: `v2.3.0`
  (`61f38ffc0ff3ae83adcf2fe011f3b751105add6d`).
- Upstream skill metadata: version `2.1.0`, last updated `2026-05-15`.
- Checked: `2026-07-11`.
- License: MIT, Copyright (c) 2025 Context Engineering Agent Skills
  Contributors.
- No upstream script or substantial prose is vendored into the personal skill.

## Inspected Upstream Files

- [Context Optimization `SKILL.md`](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/blob/c2b9a19107d263f965def4e8f7d1cd0d0fee1a59/skills/context-optimization/SKILL.md)
- [Optimization Techniques Reference](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/blob/c2b9a19107d263f965def4e8f7d1cd0d0fee1a59/skills/context-optimization/references/optimization_techniques.md)
- [`compaction.py`](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/blob/c2b9a19107d263f965def4e8f7d1cd0d0fee1a59/skills/context-optimization/scripts/compaction.py)
- [MIT License](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/blob/c2b9a19107d263f965def4e8f7d1cd0d0fee1a59/LICENSE)

## Adopted

- Treat context quality as more important than raw token reduction.
- Trigger optimization in response to observed pressure rather than applying it
  periodically or universally.
- Scope retrieval narrowly and expand progressively.
- Preserve retrievability through evidence anchors.
- Preserve active debugging errors and their causal context.
- Consider evidence independence and coordination cost before partitioning.
- Stop using an optimization when it has no observable benefit.

## Adapted For Personal Codex

- Replace runtime observation masking with source-side shaping of future tool
  output, compact fact capture, and a rule against rereading resolved bulk.
- Replace numeric token, latency, cache, and quality metrics with observable
  session outcomes: narrower retrieval, reproducible evidence, and less
  repeated reading.
- Let this skill identify a possible need for context isolation; route agent
  creation and delegation policy to `personal-subagent-boundaries`.
- Route actual conversation compaction to `personal-context-compression`.
- Route durable cross-session state to the explicit save/restore workflow.

## Rejected

- Claiming that a Codex skill can delete, rewrite, or mask previously emitted
  conversation items.
- Treating three or more subtasks as a hard partitioning threshold.
- Universal 70%, 80%, or 90% context-utilization triggers.
- KV-cache or prefix-layout changes as actions available to a current Codex
  session workflow.
- Cache-hit, token-category, latency, cost, or quality telemetry that the skill
  cannot obtain reliably.
- Importing the upstream demonstration `compaction.py` or its in-memory
  `ObservationStore` as a validator or runtime dependency.
- Owning compression, persistence, temporary artifact lifecycle, or root-cause
  diagnosis in this skill.

## Corroborating Sources

These sources validate the local capability boundaries; they are not the
origin of this skill.

- [OpenAI: Unrolling the Codex agent loop](https://openai.com/index/unrolling-the-codex-agent-loop/)
  explains that tool results are appended to the conversation and that
  compaction is handled by the agent harness.
- [OpenAI: Equipping the Responses API with a computer environment](https://openai.com/index/equip-responses-api-computer-environment/)
  supports keeping bulky intermediate data in the environment and returning
  bounded results or references.
- [OpenAI: Conversation state](https://developers.openai.com/api/docs/guides/conversation-state)
  documents compaction as an API or runtime mechanism rather than a prose-skill
  mutation of prior turns.
- [Anthropic: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
  supports just-in-time retrieval, progressive disclosure, high-fidelity
  compaction, and isolated context for suitable independent work.
- [Anthropic: How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
  supports treating agent isolation as a task-dependent tradeoff rather than a
  fixed subtask-count rule.

## Local Departures

- Target runtime at review time: `codex-cli 0.144.1`.
- This skill optimizes only future retrieval, future tool output, and active
  evidence grouping in the current session.
- It records no fixed numeric budget because the required category-level
  telemetry is not exposed to the skill.
- It adds no script, hook, persistent observation store, or automatic monitor.
