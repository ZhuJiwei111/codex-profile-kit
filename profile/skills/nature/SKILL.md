---
name: nature
description: Manual router for the portable Nature research and academic-writing suite. Use only when the user explicitly invokes $nature and wants Codex to select the smallest appropriate Nature workflow without knowing each child skill name.
---

# Nature Skill Router

Route one explicit `$nature` request to the smallest useful set of installed
Nature skills. The router does not authorize unrelated external writes,
credential changes, downloads, messages, or persistent jobs.

## Routing workflow

1. Classify the requested outcome before loading a child skill.
2. Select one primary child skill and add another only when the task genuinely
   spans distinct workflows.
3. Announce the selected child skill or skills and why they apply.
4. Read every selected child `SKILL.md` completely before taking task actions.
   Resolve child paths under `~/.codex/skills/<folder>/SKILL.md`.
5. Follow the selected instructions faithfully. Ask only when a missing choice
   materially changes correctness, safety, cost, or output.
6. Load `nature-shared` only when a selected child explicitly requires one of
   its references. Never route a user request directly to `nature-shared`.

## Child selection

- `nature-academic-search`: literature discovery, citation metrics, influential
  citer analysis, MeSH strategies, or reference-file management.
- `nature-citation`: claim-level Nature/CNS citations and reference exports.
- `nature-data`: Data Availability, repository planning, dataset citations, or
  FAIR metadata.
- `nature-downloader`: lawful full-text, supporting-information, CNKI, OA, or
  publisher retrieval.
- `nature-experiment-log`: structured Obsidian experimental records.
- `nature-figure`: manuscript plots, multi-panel figures, graphical abstracts,
  or scientific schematics.
- `nature-literature-pipeline`: recurring or end-to-end discovery, scoring,
  reading, delivery, and archival pipelines.
- `nature-paper-card`: fixed-format, evidence-led deep reading of one paper.
- `nature-paper-to-patent`: Chinese patent disclosures and paper-to-patent work.
- `nature-paper2ppt`: Chinese paper presentations or journal-club PPTX files.
- `nature-polishing`: academic prose polishing, translation, restructuring, and
  manuscript LaTeX layout repair.
- `researchwrite`: proposal-first scientific writing in compose, revise, or
  hybrid mode.
- `nature-reader`: full-paper bilingual, figure-aware reading and translation.
- `nature-ref-verifier`: field-by-field verification of supplied references.
- `nature-response`: reviewer responses, rebuttals, revision cover letters, and
  red-marked revision packages.
- `nature-reviewer`: pre-submission mock peer review.
- `nature-statistics`: statistical reporting, methods, legends, assumptions,
  sample sizes, and reviewer statistics concerns.
- `nature-writing`: manuscript sections and initial-submission materials built
  from author-provided evidence.

## Overlap rules

- Use `nature-writing` to create substantive manuscript content; use
  `nature-polishing` when content already exists and the main need is language,
  structure, translation, or LaTeX presentation.
- Use `nature-reader` for full bilingual reading; use `nature-paper-card` for a
  structured analytical card.
- Use `nature-reviewer` before submission; use `nature-response` after receiving
  reviewer or editor comments.
- Use `nature-academic-search` to discover literature; use `nature-citation` to
  attach sources to claims; use `nature-ref-verifier` to audit an existing
  bibliography.
- Combine `nature-statistics`, `nature-data`, or `nature-figure` with a writing
  workflow only when those evidence surfaces are in scope.

Do not load all child skills preemptively.
