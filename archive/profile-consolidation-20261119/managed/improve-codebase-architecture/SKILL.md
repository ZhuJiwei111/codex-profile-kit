---
name: improve-codebase-architecture
description: Manual only. Find concrete module-boundary improvements in a named area or observed codebase pain point.
---

# Improve Codebase Architecture

Read the installed `../codebase-design/SKILL.md` for useful module and seam
concepts, then inspect the repository's existing domain language and decisions.
Use familiar project terms rather than forcing a new vocabulary.

Start with the user's named area or an observed change hotspot. Inspect the
flow and relevant consumers; expand only when that could change the diagnosis.
Use bounded independent exploration when delegation is authorized and helpful,
not as a mandatory first step.

Recommend a small number of concrete opportunities. For each, show the actual
friction, proposed boundary, effect on consumers and tests, and the cost or
trade-off. Prefer changes with a present consumer or demonstrated repetition.
A familiar code smell or hypothetical future extension is insufficient.

Default to an inline assessment. Create an HTML or other durable report only
when requested, following the repository's report process. A user-selected
opportunity can lead to further design; assessment alone does not authorize
refactoring, compulsory grilling, new files, branches, or publication.
