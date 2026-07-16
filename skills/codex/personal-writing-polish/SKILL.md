---
name: personal-writing-polish
description: Use only for explicit polishing, rewriting, humanizing, voice matching, or removal of defensive/AI-like phrasing from supplied or locked text while preserving claims and evidence; not for analysis, new content, review disposition, rebuttal strategy, or documentation ownership.
---

# Personal Writing Polish

## Purpose

Act as a semantic-preserving expression editor. Improve how locked content is written without taking ownership of its facts, reasoning, evidence, decisions, or document contract.

This is a transformation layer, not a content-generation workflow. The skill may change wording and rhythm; it may change ordering or compress content only when the edit contract authorizes that freedom. It must not silently change what the text claims or how strongly the evidence supports it.

## Entry Gate

Use this skill only when both conditions hold:

1. The user supplied or identified text whose substantive content is already available or locked.
2. The user explicitly wants polishing, rewriting, humanizing, voice matching, tightening, or removal of defensive or AI-like phrasing. Natural-language intent is sufficient; the user need not name the skill.

Route out when the request primarily asks for analysis, an explanation, new prose from an undeveloped idea, research diagnosis, experiment design, review disposition, rebuttal strategy, or documentation ownership. Use the content-owning skill first. For a mixed request, complete and lock the facts, evidence, and structure there, then apply this editing layer.

For this workflow, “locked” means that the content owner has settled the claims, evidence boundaries, decisions, and required structure for the editing pass. It does not mean that this skill has independently verified them. Content produced earlier in the same turn may be treated as locked only when no unresolved choice would materially change it; otherwise return to the content owner or ask for the missing decision.

Do not invoke this skill merely because an ordinary answer could sound better. Global writing conventions belong to `AGENTS.md`.

## Establish the Edit Contract

Infer a compact contract from the request and surrounding artifact. Ask only when an unresolved choice would materially alter the output.

```yaml
target:
output_mode: rewrite_only | audit_only | audit_and_rewrite | file_edit
language:
audience:
artifact:
requested_lenses: []
semantic_freedom: expression_only | structure_allowed | compression_allowed
format_constraints: []
voice_sample:
protected_elements: []
```

Defaults:

- A pasted passage plus “polish” or “rewrite” means `rewrite_only` and `expression_only`.
- Preserve the source language unless the user requests translation or bilingual output.
- Treat venue, project, template, and user style requirements as binding.
- Use a voice sample only when the user supplied or explicitly authorized it.
- `expression_only` permits wording, syntax, punctuation, and local rhythm changes, but not reordering material propositions or changing the attachment of scope, conditions, or qualifications. `structure_allowed` permits sentence or paragraph reordering while the semantic fingerprint remains binding.

Read [editing-lenses.md](references/editing-lenses.md) to select and apply lenses. Read [examples.md](references/examples.md) for regression cases or ambiguous boundaries. Read [source-notes.md](references/source-notes.md) only for provenance or upstream comparison.

## Build a Semantic Fingerprint

Before rewriting, identify the protected meaning and literal tokens. Preserve:

- facts, claims, stance, and the distinction between observation, inference, hypothesis, and recommendation;
- evidence modality and causal strength;
- scope, conditions, exceptions, negations, non-goals, uncertainties, and unknowns;
- metrics, units, statistics, quantities, dates, and time windows;
- quotations, citations, footnotes, links, and attribution boundaries;
- code, commands, paths, APIs, identifiers, LaTeX, tables, and domain terms;
- actions, decisions, obligations, deadlines, and exact reviewer or stakeholder wording;
- venue, template, word-count, page-count, and formatting constraints.

Do not invent facts, sources, experiments, explanations, next steps, causal links, judgments of adequacy or value, personal experience, opinions, or personality. If available evidence does not support an attractive source claim, flag the evidence conflict. Do not silently remove, weaken, or replace that claim merely because its support is absent from the supplied excerpt. Remove it only when the content owner explicitly marks it as unsupported and removable, or when it is demonstrably non-propositional repetition under the locked contract.

## Apply Editing Lenses

Choose only the lenses needed by the request:

- **Clarity:** make actors, actions, referents, and consequences explicit using existing content.
- **Anti-defensive:** classify the function of each caveat or negation. Rewrite it positively only when the new proposition is logically equivalent and equally supported; otherwise preserve it.
- **Humanize:** address contextual clusters of mechanical prose instead of enforcing word blacklists or detector-oriented tricks.
- **Voice match:** calibrate observable features of an authorized sample without inventing biography, attitude, or opinions.
- **Compress:** remove true repetition only when compression is requested or clearly allowed.
- **Artifact fit:** match the established conventions of the target academic, technical, project, or professional artifact.

Patterns are evidence for editorial judgment, not automatic violations. A passive sentence, dash, hedge, formal term, title style, or three-item list may be exactly right.

## Review the Semantic Delta

Compare the rewrite against the fingerprint before returning or editing:

1. Each material claim has the same truth conditions.
2. Evidence and causal strength are unchanged.
3. Scope, uncertainty, necessary negation, and non-goals remain intact.
4. Protected literal elements and format constraints are preserved.
5. No unsupported content was introduced through smoother wording.

When a requested style change conflicts with semantic preservation, state the conflict briefly and provide the closest safe rewrite. Never make the substantive change silently.

## Output and Edit Authority

- Return only the rewritten text by default.
- Return an audit only when requested; return both audit and rewrite only when requested.
- Provide alternatives or a change rationale only when requested or when a semantic conflict must be surfaced.
- A bare file path, “review,” or “suggest” request is read-only. Edit a file only when the user explicitly asks to change it.
- For authorized file edits, touch only the requested prose surface, preserve surrounding structure, inspect the diff, and use `personal-risk-verification` after the last relevant edit.

## Collaboration Boundaries

- `personal-project-output-explainer`, `personal-code-documentation` (including
  `sync_existing`), and `personal-review-response` own their substantive
  content before this skill edits expression.
- `awesome-rebuttal` always owns live submission rules, reviewer strategy, and rebuttal content; this skill may polish only a locked draft.
- This skill grants no Git, publication, external-message, or broader file-edit authority.
