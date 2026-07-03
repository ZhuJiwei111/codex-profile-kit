---
name: personal-writing-polish
description: Polish user-visible technical, research, project, documentation, academic, or professional prose when the user asks to revise, rewrite, humanize, remove AI-like wording, remove defensive writing, strengthen expression, make text more natural, or make writing more direct while preserving evidence boundaries. Use for explicit writing-polish requests; do not replace task-specific explanation, code documentation, rebuttal, or project-output skills when the user is asking for substantive analysis rather than prose revision.
---

# Personal Writing Polish

## Overview

Use this skill as a prose editor, not as a substantive analyst. It combines anti-defensive writing and selected humanizer patterns for bilingual technical work: direct claims, concrete consequences, natural rhythm, and preserved evidence boundaries.

## Trigger Boundary

Use this skill when the user explicitly asks to:

- polish, revise, rewrite, strengthen, or tighten text
- remove defensive writing, caveats, hedging, AI-like phrasing, or promotional language
- make a draft more natural, human, direct, professional, concise, or readable
- improve Chinese technical summaries, English documents, academic prose, README prose, reports, explanations, or professional writing

Do not use this skill merely because the assistant is producing an ordinary answer. For project explanations, summaries, diagnostic reports, or handoffs where the user needs analysis, use the relevant task skill first, then apply these rules only if the user asks for prose polish.

## Workflow

1. Identify the target language, audience, artifact type, and whether the user wants a draft only or file edits.
2. Preserve meaning before style. Read enough surrounding context to avoid changing claims, evidence strength, terminology, metrics, paths, commands, risks, or unresolved questions.
3. Read `references/style-rules.md` for the editing rules.
4. Read `references/examples.md` when examples would clarify the rewrite direction or when the user asks for examples.
5. Read `references/source-notes.md` when citing or comparing the original external skills.
6. Produce a compact audit and rewrite by default.

## Default Output

Use `Compact Audit + Rewrite` unless the user asks for a different format:

```markdown
Audit:
- <2-4 concrete prose issues>

Rewrite:
<complete revised text>
```

Keep the audit brief. Do not perform a line-by-line style trial unless the user asks for detailed editing notes.

## Authority

Default to draft-first. If the user provides a file path, show the audit and rewritten draft first unless they explicitly ask to edit the file. When editing files, change only the requested text surface and inspect the diff.

## Hard Boundaries

- Evidence first: do not strengthen claims beyond the available evidence.
- Keep necessary scope, safety, legal, ethical, methodological, and technical limits.
- Do not delete risk, uncertainty, or unknowns; turn them into evidence boundaries or next checks.
- Do not rewrite commands, paths, metrics, identifiers, exact reviewer wording, API names, or domain terms unless the user explicitly asks.
- Do not force personality into technical, legal, reference, or research text.
- Do not convert this skill into a generic humanizer pass for every answer.
