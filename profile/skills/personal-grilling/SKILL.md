---
name: personal-grilling
description: Manual core for pressure-testing plans and decisions. Use on explicit personal-grilling requests, or read as a reference within an already-authorized clarification workflow. Ordinary discussion does not trigger formal grilling.
---

# Personal Grilling

Standalone use stays in conversation. For requested documented discussion, read
`../personal-grill-with-docs/SKILL.md`. Reading this core does not expand authority.

## Question Loop

1. Establish scope, non-goals, and existing decisions. Reuse settled answers.
2. Investigate discoverable facts with bounded read-only checks. Distinguish
   observations, recommendations, assumptions, and user-owned decisions.
   Delegate only with user or applicable repository authority.
3. Resolve the highest-impact unresolved parent decision first. Recommend an
   option and offer two or three materially different choices when known;
   use an open question when the option space is unknown.
4. Keep each round easy to answer. Bundle independent simple choices when useful;
   wait for parent answers before dependent questions. Neither exactly one
   question nor every open question is a fixed requirement.
5. Wait for explicit user-owned choices. Silence and timeouts never choose a
   default. Bind concise answers to the complete options actually presented.
   Continue useful independent work within existing authority while waiting.
6. Reconcile answers with prior decisions and affected branches. Later explicit
   answers may supersede earlier decisions; retain enough context to explain
   the replacement. Report the delta rather than repeating the discussion.

## Finish

When material questions appear resolved, read `references/coverage-model.md`
for one silent gap scan. Ask only about gaps that could change the result;
do not exhaust imaginary branches or turn the lenses into a checklist.

Summarize conclusions, remaining assumptions or deferred choices, and the next
concrete action. No separate closure confirmation is required. Discussion does
not itself authorize implementation; reuse existing implementation authority
when it covers the next action, without another permission gate.

Do not create files, specs, ADRs, tickets, or downstream workflows by default.
The caller owns authorized persistence. Read `references/source-notes.md` only
when maintaining provenance.
