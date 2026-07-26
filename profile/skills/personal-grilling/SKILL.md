---
name: personal-grilling
description: Manual only. Use only when the user explicitly invokes $personal-grilling for exhaustive, multi-round requirement clarification that resolves one material decision at a time, persists current decisions across turns, and stops for explicit closure before any implementation.
---

# Personal Grilling

Pressure-test a consequential requirement before planning or implementation.
Run only after explicit invocation.

## Establish Scope And Memory

State the question being clarified, existing locks, material non-goals, evidence
cutoff, and the fact that implementation is outside this workflow.

Use the user's named plan or decision file when one exists. Otherwise, before
the first material question, create one exact task-owned Markdown record and
report its path. Invocation authorizes only this continuity record, not product
or project implementation.

Keep the record as compact current state:

- scope, existing locks, and non-goals;
- observed facts with evidence anchors and cutoff;
- material decisions or open branches with stable IDs and status
  `proposed`, `locked`, `superseded`, `deferred`, or `open`;
- the exact user answer or evidence that supports each state;
- only consequential dependencies, assumptions, risks, or acceptance effects;
  and
- the next material question.

Separate facts, Codex recommendations, and user-owned decisions. A later
explicit answer may supersede an earlier lock; preserve only the shortest link
needed to understand that replacement. Do not keep a transcript.

## Resolve One Decision Per Turn

1. Select the unresolved parent decision with the largest effect on safety,
   scope, acceptance, or rework.
2. Investigate discoverable facts with bounded read-only checks instead of
   asking the user to supply them.
3. When real options are known, give Codex's recommendation and two or three
   materially different options. Use an open question only when the option
   space is genuinely unknown, and provide examples or candidate hypotheses.
4. Ask exactly one material decision. Do not bundle dependent subquestions.
5. Wait for the explicit answer without a timeout or automatic default. Bind a
   concise answer such as `1` to the complete option that was presented.
6. Update the record first, check direct conflicts and affected branches, then
   report only the delta and ask the next question.

On `continue`, compaction recovery, or handoff, reread the record rather than
reconstructing decisions from recent chat.

## Close

When no material branch is visibly open, read
`references/coverage-model.md` and perform one silent, risk-scaled gap scan.
Open only a gap that could change the result.

Then give a short settled/open/assumption summary and ask separately whether
grilling is complete. On confirmation, update the record and stop. Do not
combine closure with authorization to plan or implement.

Do not create a PRD, spec, ADR, tickets, tracker, evaluation platform, or
downstream workflow. Read `references/source-notes.md` only when maintaining
provenance.
