---
name: personal-context-optimization
description: Use when current-session retrieval, tool output, or mixed evidence causes repeated reads or lost signal; not for compaction or persistence.
---

# Personal Context Optimization

This is a Codex-session workflow, not an inference-runtime optimizer. Optimize
the next retrieval, tool call, or evidence grouping in the current session.
Keep signal retrievable. Do not claim to erase, mask, or rewrite conversation
items that have already been emitted.

## Trigger Gate

Use this skill when at least one condition is present:

- repeated full reads or duplicate tool output are replacing targeted lookup;
- the next retrieval is likely to return substantially more than the current
  decision needs;
- independent evidence domains are being mixed and causing omissions,
  contradictions, or repeated reconstruction;
- a relevant fact was found but cannot be relocated reliably.

Do not trigger only to chase token savings, for an ordinary bounded inspection,
a small direct task, or context that is merely long. Route unclear repository
boundaries to `personal-repo-intake`. Route pressure from accumulated
conversation history to `personal-context-compression`.

## Owned Scope

This skill owns:

- just-in-time retrieval within the current session;
- shaping future tool output at its source;
- retaining minimal facts with reproducible evidence anchors;
- logical evidence partitioning when mixed domains reduce accuracy.

It does not own repository intake, history compaction, cross-session
persistence, agent creation, temporary artifact lifecycle, root-cause
debugging, inference-runtime prefix caching, or token-budget telemetry.

## Workflow

1. Classify the dominant friction once: retrieval scope, output volume,
   repeated reads, evidence mixing, or accumulated history. If accumulated
   history is the problem, stop and hand off to `personal-context-compression`.
2. Before the next retrieval, state the evidence contract:
   - the exact question;
   - the source to inspect;
   - the query, fields, range, or output ceiling;
   - the condition for stopping or expanding.
3. Shape output at the source:
   - prefer exact paths, symbols, identifiers, or reference IDs;
   - filter, aggregate, page, sample, or request a bounded line range;
   - expand progressively only when the bounded result is insufficient.
4. Capture the minimum usable fact and a reproducible anchor, as applicable:
   - file path plus symbol, nearby stable text, or line range;
   - command, `cwd`, exit status, and relevant output span;
   - document URL or reference ID plus version, date, or section;
   - query or filter plus the evidence cutoff.
5. Do not reread an entire resolved output merely because it remains in the
   conversation. Retrieve from the saved anchor if the fact must be checked
   again.
6. Partition by evidence dependency, not task count. Use logical sections first.
   Consider isolated agent context only when evidence sets are genuinely
   independent and mixing them is already harmful.
7. Keep the strategy only if the next action becomes narrower, the evidence can
   be reproduced, or repeated reading stops. Otherwise stop adding optimization
   process.

## Failure Evidence

During an unresolved failure, preserve the command, `cwd`, exit status, first
failing condition, exact error with its local neighborhood, and unresolved
hypotheses, with secrets redacted. Do not replace causal evidence with a
conclusory summary.

`personal-evidence-debugging` owns root-cause investigation. This skill may
narrow retrieval but must not hide or discard unresolved failure evidence.

## Collaboration Boundaries

- `personal-repo-intake`: determine repository root, applicable instructions,
  dirty state, edit surface, and verification path.
- `personal-context-compression`: produce a compact continuation when
  accumulated history is the limiting factor.
- The explicit context save/restore workflow: persist or resume state across
  sessions; this skill does not write durable packets.
- `personal-subagent-boundaries`: decide whether to create or delegate to an
  isolated agent and define its context contract.
- `personal-temporary-work`: own helpers or artifact transformations created to
  filter or aggregate evidence.
- `personal-evidence-debugging`: diagnose unexpected failures and preserve the
  causal chain.

## Maintenance Reference

Read [source notes](references/source-notes.md) only when auditing or updating
this skill.
