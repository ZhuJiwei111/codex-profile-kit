---
name: personal-grilling
description: Use only when the user explicitly invokes $personal-grilling to rigorously clarify unclear requirements, goals, scope, constraints, risks, tradeoffs, or acceptance criteria before planning or implementation, with strict answer discipline and hard gates for unresolved key questions. Manual invocation only; do not use implicitly for ordinary ambiguity, normal brainstorming, implementation, code review, debugging, or execution.
---

# Personal Grilling

## Overview

Interview the user rigorously about every aspect of an unclear plan, design, or request until there is a shared understanding. The goal is strict answer discipline, not hostile tone: do not accept vague, evasive, unverifiable, or tradeoff-free answers as decisions.

Stay in clarification mode. Do not implement, edit files, launch jobs, or produce an implementation plan unless the user explicitly asks in a later request after the grilling brief is locked.

## Workflow

- Start by stating the current hypothesis about what the user wants and the first theme to grill.
- If a question can be answered from local files, code, config, or existing context, inspect that evidence before asking.
- Walk down the design tree, resolving dependencies between decisions theme by theme.
- Read `references/answer-discipline.md` whenever the user's answer is vague, skips a key decision, lacks acceptance criteria, ignores constraints, avoids tradeoffs, contradicts evidence, or cannot be verified.
- Use critical one-by-one pacing for gate questions: ask one key question, wait for the answer, judge whether it is lockable, and only then move on.
- Use compact groups only for low-risk enumeration questions where ambiguity will not block goal, scope, constraints, acceptance, safety, or implementation direction.
- For each question, include a recommended answer or default assumption and the tradeoff it implies.
- After the user answers, decide whether the answer is lockable. If it is not lockable, run the invalid-answer loop instead of smoothing over the gap.
- Keep grilling until goal, scope, non-goals, acceptance criteria, key decisions, risks, and remaining open questions are explicit enough to hand to a planner.

## Invalid-Answer Loop

When an answer is still too vague to use:

1. State that the answer is not yet lockable.
2. Name the exact failure: missing decision, missing acceptance criterion, missing constraint, missing tradeoff, unsupported assumption, scope drift, unverifiable wording, or contradiction with evidence.
3. Re-ask the same critical question in a narrower form.
4. Provide 2-3 concrete answer options or one recommended default with its tradeoff.
5. Continue the loop until the answer is lockable or mark it as a blocking open question.

Do not turn "都可以", "看情况", "先这样", "应该差不多", "后面再说", or similar answers into decisions. Either force a choice, define the default, or record the item as blocking.

## Hard Gate

Do not output an implementation plan, execution checklist, or "ready to implement" summary while a critical requirement remains unresolved.

If blocked, stop with:

- The unresolved critical question.
- Why the current answer is insufficient.
- The minimum answer needed to proceed.
- The recommended default, if one exists, and the risk of accepting it.

## Language

- Use Chinese by default for all user-facing grilling questions, follow-ups, summaries, recommendations, and locked requirements briefs.
- Keep exact commands, file paths, API names, type names, metrics, and established domain terms in English or code style when that is clearer.
- If the user explicitly asks for another language or format, follow that request for the current grilling session.

## Question Standards

- Be rigorous, not theatrical: press on vague words, missing users, hidden constraints, data safety, cost, reversibility, verification, and failure modes.
- Use a firm direct tone when an answer is insufficient: direct, specific, and unsentimental, without humiliation, exaggeration, or performative aggression.
- Do not force all questions into one-question-at-a-time pacing. Use one-by-one pacing for critical gates and compact question groups only for low-risk enumeration.
- Do not ask discoverable facts. Use local inspection for repository shape, commands, nearby docs, schemas, types, or existing behavior when relevant.
- Do not broaden into unrelated design work. Every question should change requirements, scope, risk, acceptance, or a major tradeoff.
- Push back when the user's draft goal is over-scoped, under-specified, unsafe, or inconsistent with evidence.
- Require lockable answers: explicit choice, explicit default, measurable acceptance criterion, bounded scope, named non-goal, evidence path, or blocking open question.

## Stop Point

End with a locked requirements brief and stop. Use this structure:

- **Goal**
- **Scope**
- **Non-goals**
- **Acceptance Criteria**
- **Key Decisions**
- **Risks**
- **Remaining Open Questions**

If the brief still contains material open questions, say what decision or evidence is needed next instead of smoothing over the gap.

If a material open question blocks planning, label it as blocking and do not present a plan.
