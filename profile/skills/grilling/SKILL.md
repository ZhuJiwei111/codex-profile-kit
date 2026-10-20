---
name: grilling
description: Stress-test a plan or design when the user asks for an interview, grilling, or consequential requirement clarification.
---

Ask one material decision at a time, with a concrete recommendation and a small
set of real alternatives. Resolve prerequisite choices before downstream ones.
Explore discoverable facts directly rather than asking the user; use a bounded
worker only when delegation is authorized and useful.

Wait for the user's explicit answer. Preserve settled choices and do not reopen
them without new evidence. Prefer concrete examples to abstract questions the
user cannot meaningfully answer. Stop once no open choice could materially
change the outcome, scope, or acceptance; do not explore a hypothetical tree to
exhaustion. Summarize the agreed design, evidence, and remaining assumptions.

For multi-turn continuity, reuse the existing plan or decision owner. Bind a
short answer to the complete option shown. Reread settled decisions after
compaction or handoff. If the user requests a durable record and none exists,
keep one compact task-owned note with scope, settled choices and their evidence,
open questions, and the next material decision. Do not create another ledger
beside an existing owner.

If the request also includes glossary or ADR maintenance, use
`../domain-modeling/SKILL.md` for that document scope; an interview by itself
does not create domain documents.

This interview alone does not authorize implementation, new files, or external
actions. Respect authority already given for a next step.

Read `references/source-notes.md` only when maintaining provenance.
