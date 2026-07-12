# Source Notes

## Contents

- [Origin](#origin)
- [Inspected Upstream Files](#inspected-upstream-files)
- [Adopted](#adopted)
- [Adapted For Personal Codex](#adapted-for-personal-codex)
- [Rejected](#rejected)
- [Codex Runtime Boundary](#codex-runtime-boundary)
- [Evaluator Decision](#evaluator-decision)
- [Local Departures](#local-departures)

## Origin

- Upstream: `muratcankoylan/Agent-Skills-for-Context-Engineering`,
  `skills/context-compression`.
- Origin assessment: high-confidence condensed derivative based on shared
  wording, summary structure, probes, anti-patterns, and the user's provenance
  context; the local Git history contains no original attribution.
- Pinned repository HEAD:
  `c2b9a19107d263f965def4e8f7d1cd0d0fee1a59`.
- Stable release: `v2.3.0`
  (`61f38ffc0ff3ae83adcf2fe011f3b751105add6d`).
- Upstream skill metadata: version `1.3.0`.
- Most recent semantic target change:
  `cbc2c978133d882acfa02f51d72d7092911bbd83`.
- Checked: `2026-07-11`.
- License: MIT, Copyright (c) 2025 Context Engineering Agent Skills
  Contributors.
- Local profile-kit baseline: `6574bce`.
- No upstream script, test, reference body, or substantial prose is vendored
  into the personal skill.

## Inspected Upstream Files

- [Context Compression `SKILL.md`](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/blob/c2b9a19107d263f965def4e8f7d1cd0d0fee1a59/skills/context-compression/SKILL.md)
- [Evaluation Framework](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/blob/c2b9a19107d263f965def4e8f7d1cd0d0fee1a59/skills/context-compression/references/evaluation-framework.md)
- [`compression_evaluator.py`](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/blob/c2b9a19107d263f965def4e8f7d1cd0d0fee1a59/skills/context-compression/scripts/compression_evaluator.py)
- [MIT License](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/blob/c2b9a19107d263f965def4e8f7d1cd0d0fee1a59/LICENSE)

## Adopted

- Optimize for tokens per completed task rather than tokens per individual
  request.
- Produce a structured continuation summary centered on current progress,
  constraints, decisions, artifacts, failures, risks, and next actions.
- Preserve an artifact trail and exact decision-critical identifiers.
- Protect early user constraints from disappearing during repeated summaries.
- Check recall, artifact location, decision rationale, and continuation quality
  before treating a summary as usable.

## Adapted For Personal Codex

- Replace blind anchored merge with incremental processing that emits one
  self-contained current snapshot and invalidates superseded state.
- Replace heuristic quality scores with evidence anchors, provenance labels,
  evidence cutoffs, and independent forward probes.
- Treat schemas, API shapes, and code as external authorities that should be
  cited or reloaded rather than copied wholesale or paraphrased as canonical.
- Treat a compression result as a non-persistent candidate payload. The
  explicit save/restore workflow owns durable packets and restoration.
- Let planning supply bounded source state for a candidate rollover seed;
  planning retains lineage, preview, approval, archive, and write ownership.
- Preserve an existing long-job handoff only with its evidence cutoff; do not
  poll or recompute current status.

## Rejected

- Fixed token counts, message counts, context percentages, compression ratios,
  or benchmark scores as universal triggers or acceptance criteria.
- Automatic compaction, truncation, sliding windows, masking, or rewriting of
  prior Codex history from this prose skill.
- Raw secret preservation, partial token reproduction, or credential-bearing
  commands in continuation summaries.
- Treating a summary as proof, authorization, durable state, or an authoritative
  schema.
- Default file writes, persistent state, plan rollover, process polling, or
  root-cause diagnosis.
- Importing the upstream evaluator, tests, or evaluation reference as runtime
  dependencies.

## Codex Runtime Boundary

- Local runtime at review time: `codex-cli 0.144.1`.
- Local feature state: `remote_compaction_v2` is stable and enabled.
- Tagged Codex source: `rust-v0.144.1`, commit
  `44918ea10c0f99151c6710411b4322c2f5c96bea`.
- The tagged [compact prompt](https://github.com/openai/codex/blob/44918ea10c0f99151c6710411b4322c2f5c96bea/codex-rs/prompts/templates/compact/prompt.md)
  asks for a concise handoff containing progress, decisions, constraints, next
  steps, and critical references.
- The OpenAI Codex repository is licensed under
  [Apache-2.0](https://github.com/openai/codex/blob/44918ea10c0f99151c6710411b4322c2f5c96bea/LICENSE).
- [OpenAI's Codex agent-loop description](https://openai.com/index/unrolling-the-codex-agent-loop/)
  states that Codex automatically uses native compaction after its runtime
  threshold is exceeded.
- [OpenAI's Responses API environment description](https://openai.com/index/equip-responses-api-computer-environment/)
  describes compaction as a native platform mechanism that returns a compacted
  context representation.
- The Codex manual helper failed on `2026-07-11` because the official manual
  endpoint returned HTTP 403; the pinned source and official pages above were
  used as the bounded fallback.

## Evaluator Decision

Do not import the upstream evaluator. It is demonstration code whose dimensions
reuse length, suffix, and lexical-overlap heuristics; parts of the supplied
compressed context are not used consistently, and the tests do not establish
end-to-end summary fidelity. A deterministic score would create false precision
for this judgment-heavy workflow.

Use frontmatter and resource validation plus independent forward probes for
secret handling, stale evidence, artifact classification, decision retention,
and continuation quality.

## Local Departures

- This skill emits only an in-message continuation snapshot from currently
  visible evidence.
- It does not invoke or configure native compaction, write a durable packet,
  mutate planning state, poll jobs, or execute next actions.
- It prefers the shortest self-contained snapshot that preserves evidence and
  authority boundaries; it records no fixed compression target.
