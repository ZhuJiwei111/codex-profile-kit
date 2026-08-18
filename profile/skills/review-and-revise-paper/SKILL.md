---
name: review-and-revise-paper
description: Discuss, approve, and apply precise revisions to a canonical LaTeX or Markdown paper through a bilingual Markdown ledger, without creating a parallel revised manuscript.
---

# Review And Revise Paper

Use one canonical paper source and one repository-local Markdown ledger. The
fixed lifecycle is:

`canonical paper -> exact ledger proposal -> author discussion -> explicit approval -> in-place edit`

The ledger is writable during discussion. The paper is not. Never create a
`revision-clean`, candidate-paper, or other parallel manuscript tree.

## Operating contract

- Treat the live canonical paper as the only manuscript authority.
- Use Git and exact source anchors for protection; do not require a clean
  worktree and do not create automatic backup copies.
- Keep at most one active package. A package covers one semantic unit, or
  related prose, caption, table, and figure changes that answer one scientific
  question.
- Require an exact proposal and an explicit author decision before every paper
  mutation, including when the user says "直接修改". The word "确定" approves
  only the active package currently displayed.
- Replace a pending proposal when the author refines it. Do not append stale
  variants, duplicate full entries, or retain an inventory placeholder after
  expanding it.
- Preserve unrelated working-tree changes. Do not stage, commit, push, submit,
  or edit reviewer correspondence unless separately authorized.
- Keep user-facing discussion and the ledger in Chinese by default. Preserve
  manuscript text, code, paths, citations, formulas, identifiers, and technical
  terms in their source language.

## Select the workflow

Infer one workflow from the explicit request:

- **Single edit**: prepare, discuss, and optionally apply one package, then stop.
- **Serial review**: review the paper in reading order; after applying one
  approved package, expand the next package automatically.
- **Apply approved**: apply the single package already marked `approved` after
  rechecking its source anchor.
- **Freeze verification**: build and inspect the final paper only after all
  intended packages are closed or the author explicitly requests rendering.

Do not add slash commands or silently switch a single edit into a full-paper
review.

## 1. Ground in live project state

Before proposing text:

1. Find the repository root and read applicable instructions.
2. Inspect Git status without cleaning it. Identify the user's existing changes
   and the exact surface this invocation may write.
3. Resolve the canonical `.tex` entrypoint or Markdown manuscript from live
   files, include/import relationships, build configuration, and user input.
4. Locate an existing revision ledger. If none exists, use
   `assets/revision-ledger-template.md` as the source for an `apply_patch`
   creation in the project's established docs area. If no destination
   convention is discoverable, ask for the location and recommend
   `docs/paper_revision/REVISION_LEDGER.md`.
5. Record the canonical entrypoint, source type, venue, language, build policy,
   approval policy, workflow mode, and active package in the ledger frontmatter.

Historical tasks, reviewer responses, task boards, and old drafts may explain
motivation. They never override the live canonical source or verified evidence.

Read `references/source-handling.md` before resolving multi-file LaTeX, applying
an approved package, handling a dirty worktree, or running final verification.

## 2. Build one exact proposal

Read the target source and the minimum evidence needed to judge the requested
change. Trace claims to the paper's data, code-observed facts, verified result
artifacts, citations, or reviewer concern as applicable.

Choose a semantic package:

- Combine nearby changes only when they share one scientific decision.
- Do not split a tiny caption change from the paragraph or table whose meaning
  it controls.
- Do not combine unrelated improvements merely to reduce approval turns.

Assign the next stable `PKG-NNN` ID. Replace any matching coverage-inventory
placeholder with the complete package. Set it to `drafting`, then populate the
full original/proposed English and Chinese views, judgment, and pending decision
record. Change it to `pending_author_decision` only when every required section
is complete.

Read `references/ledger-format.md` before writing or revising a package. Copy
the exact package shape from `assets/revision-ledger-template.md`; do not invent
a shorter summary format.

## 3. Judge without defensive drift

Read `references/revision-judgment.md` for every new package. State:

- the verdict;
- the direct evidence and claim boundary;
- why the change is necessary or unnecessary;
- the concrete consequence of leaving the source unchanged; and
- which contribution remains intact.

Keep strong claims that the evidence supports. Do not add caveats for imagined
objections, convert the paper into a rebuttal log, or volunteer weak negative
findings unrelated to the requested decision.

## 4. Discuss before editing the paper

Update only the ledger, then show the author:

- the package ID and target location;
- the recommended verdict;
- the exact candidate wording or table/figure change; and
- a clickable link to the full bilingual package.

Wait for an explicit decision. Apply annotations and partial approvals only to
the selected content. If wording changes, replace the blue candidate and its
Chinese counterpart in the same package; keep only a concise decision note
about superseded wording.

Do not edit the manuscript while the package is `drafting` or
`pending_author_decision`.

## 5. Apply one approved package

When the author explicitly approves the active package:

1. Record the approved scope and set the package to `approved`.
2. Re-read the target file and compare the complete approved original anchor
   with the live source. Ignore line numbers as identity.
3. If the anchor is absent, duplicated, or changed, stop. Restore the package to
   `pending_author_decision`, explain the drift, and rebuild it from live source.
4. If the anchor matches exactly once, use `apply_patch` to change only the
   approved surface in the canonical paper.
5. Run the smallest source-level check that distinguishes success: exact text,
   numeric/citation/cross-reference checks where relevant, and
   `git diff --check` scoped to the affected paths.
6. Record target paths, applied content, checks, and residual risk. Set status to
   `applied_source_verified` and set top-level `active_package: none`.

Do not re-polish approved text during application. Do not compile during normal
discussion or source application.

## 6. Continue or freeze

- In single-edit mode, stop after the application record.
- In serial-review mode, immediately expand the next semantic package without
  editing it and make that package the sole active package.
- In freeze-verification mode, discover and run the project-owned build. Inspect
  logs, extracted text, references, relevant tables/figures, and rendered pages.
  Update successfully rendered packages to `final_render_verified`; keep any
  author-accepted unresolved contradiction as `author_locked_risk`.

PDF and DOCX may be read or verified but are not canonical editable sources.
Binary figure changes may be recorded and approved here, but use the applicable
image/vector workflow for the actual asset edit.

## Ledger validation

Run the mechanical validator after creating or structurally changing a ledger:

```bash
/usr/bin/python3 <skill-dir>/scripts/validate_revision_ledger.py /absolute/path/to/REVISION_LEDGER.md
```

Run its bundled tests after changing the validator:

```bash
/usr/bin/python3 <skill-dir>/scripts/validate_revision_ledger.py --self-test
```

Resolve `<skill-dir>` as the directory containing this `SKILL.md`.

The validator checks structure, status, duplicate/active packages, and color
markup only. A passing result does not certify translation fidelity, scientific
correctness, citation validity, or claim strength.
