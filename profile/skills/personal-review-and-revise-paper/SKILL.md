---
name: personal-review-and-revise-paper
description: Review and revise a LaTeX or Markdown manuscript or reviewer response through exact bilingual before/after proposals, author discussion, and scoped application. Use for single edits or serial revision; preserve the author's argument and chosen source.
---

# Personal Review And Revise Paper

Use one declared canonical source per document and one revision ledger for the
active review scope. The default lifecycle is:

`canonical paper -> exact ledger proposal -> author discussion -> explicit approval -> in-place edit`

The ledger is writable during discussion; canonical edits follow approval.
Create a new revision directory only when the author explicitly requests it,
then designate that source as canonical and retain the submission as a baseline.

## Operating contract

- Treat the live canonical source as the application authority. A submitted
  baseline answers what reviewers read; evidence determines scientific validity.
- Use Git and exact source anchors for protection; do not require a clean
  worktree and do not create automatic backup copies.
- Keep at most one active package. Size it by a complete argument and its
  dependent prose, captions, tables, or Methods, rather than sentence count.
- Default to approval of the exact displayed package. "确定" approves that
  package; "进入下一包" authorizes review, not its application. Honor explicit
  user overrides and already-granted scope instead of imposing a second approval
  gate. Record any broader editing authority before using it.
- Replace a pending proposal when the author refines it. Do not append stale
  variants, duplicate full entries, or retain an inventory placeholder after
  expanding it.
- Preserve unrelated working-tree changes. Git and external actions need their
  own authority. Response edits need an explicit Response-editing request;
  approval of a Response does not by itself approve manuscript changes.
- Keep user-facing discussion and the ledger in Chinese by default. Preserve
  manuscript text, code, paths, citations, formulas, identifiers, and technical
  terms in their source language.

## Select the workflow

Infer one workflow from the explicit request:

- **Single edit**: prepare, discuss, and optionally apply one package, then stop.
- **Serial review**: follow the author's order; otherwise use manuscript reading
  order or reviewer-comment order. After closing one package, display the next
  automatically without asking whether to continue.
- **Apply approved**: apply the single package already marked `approved` after
  rechecking its source anchor.
- **Freeze verification**: build and inspect the final paper only after all
  intended packages are closed or the author explicitly requests rendering.

Do not add slash commands or silently switch a single edit into a full-paper
review.

Read `references/workflow-context.md` when resuming another task, reviewing a
Response, planning a whole revision, or using author-authorized parallel work.

## 1. Ground in live project state

Before proposing text:

1. Find the repository root and read applicable instructions.
2. Inspect Git status without cleaning it. Identify the user's existing changes
   and the exact surface this invocation may write.
3. Resolve the canonical `.tex` entrypoint or Markdown document from live
   files, include/import relationships, build configuration, and user input.
4. Locate an existing revision ledger. If none exists, use
   `assets/revision-ledger-template.md` as the source for an `apply_patch`
   creation in the project's established docs area. If no destination
   convention is discoverable, ask for the location and recommend
   `docs/paper_revision/REVISION_LEDGER.md`.
5. Record the required configuration using the template. Keep document roles,
   author overrides, review order, and authorized synchronization targets in the
   ledger's scope section; preserve existing compatible ledgers.

Carry forward explicit author decisions from historical tasks, then verify
their target against live source. Historical scientific claims require evidence.

Read `references/source-handling.md` before resolving multi-file LaTeX, applying
an approved package, handling a dirty worktree, or running final verification.

## 2. Build one exact proposal

Read the target source and the minimum evidence needed to judge the requested
change. Trace claims to the paper's data, code-observed facts, verified result
artifacts, citations, or reviewer concern as applicable.

Choose a semantic package:

- Keep a paragraph's result, interpretation, and supported contribution together
  when they form one argument, even if this touches several files.
- Do not split a tiny caption change from the paragraph or table whose meaning
  it controls.
- Do not combine unrelated improvements merely to reduce approval turns.
- Split when the author can decide each part independently. Merge pending parts
  when separation repeats context or temporarily removes part of the argument.
  Supplement details may be grouped more broadly when the author permits it.

Reuse the matching inventory ID, or assign the next stable `PKG-NNN` ID. Replace
its inventory placeholder with the complete package. Set it to `drafting`, then
populate the full original/proposed English and Chinese views, judgment, and
pending decision record. Change it to `pending_author_decision` only when every
required section is complete.

Read `references/ledger-format.md` before writing or revising a package. Copy
the exact package shape from `assets/revision-ledger-template.md`; do not invent
a shorter summary format.

## 3. Judge without defensive drift

Apply `references/revision-judgment.md` to each package; read it once and revisit
when the scientific decision changes. State:

- the verdict;
- the direct evidence and claim boundary;
- why the change is necessary or unnecessary;
- the concrete consequence of leaving the source unchanged; and
- which contribution remains intact.

Keep strong claims that the evidence supports. Do not add caveats for imagined
objections, convert the paper into a rebuttal log, or volunteer weak negative
findings unrelated to the requested decision.

## 4. Discuss before editing the paper

Update the ledger, then show the author in the reply itself:

- the package ID and target location;
- the recommended verdict;
- complete current and proposed English, and faithful complete Chinese versions,
  grouped by paragraph when useful for comparison;
- exact table/figure changes using the ledger's adaptive display rules; and
- a clickable link to the full bilingual package.

Use sentence-level change marking or finer; unchanged sentences stay unmarked.
A ledger link complements the comparison rather than replacing it. On the
first proposal, provide the usable wording rather than requiring a separate
outline-approval turn unless the author asks to discuss structure first.

Apply annotations and partial approvals only to the selected content. A request
to reconsider wording produces a replacement candidate; it does not approve
unseen wording. If the author approves just paragraph 2, apply only that exact
paragraph and leave the others intact. Update English, Chinese, and the concise
decision record together. Follow explicit scope overrides as recorded above.

Under the default approval policy, wait for the author before canonical edits.
Close author-accepted no-change decisions as `closed_without_change`; use
`deferred` when the author postpones a package. See the status rules in
`references/ledger-format.md` before changing or resuming either state.

## 5. Apply one approved package

When the active package is approved within the recorded authority:

1. Record the approved scope and set the package to `approved`.
2. Re-read the target file and compare the complete approved original anchor
   with the live source. Ignore line numbers as identity.
3. If the anchor is absent, duplicated, or changed, stop its application. Restore
   it to `pending_author_decision`, explain the drift, and rebuild from live source.
   If the exact approved edit is already present, verify and record it instead
   of applying it twice.
4. If the anchor matches exactly once, use `apply_patch` to change only the
   approved surface in the canonical paper.
5. Run the smallest source-level check that distinguishes success: exact text,
   numeric/citation/cross-reference checks where relevant, and
   `git diff --check` scoped to the affected paths.
6. Record target paths, applied content, checks, and residual risk. Once all
   approved targets pass and all package decisions are resolved, set status to
   `applied_source_verified` and top-level `active_package: none`. For partial
   approvals or interrupted application, preserve the remaining scope and use
   the state rules in `references/ledger-format.md` and `references/source-handling.md`.

Do not re-polish approved text during application. Use one focused verification
pass; do not repeat equivalent checks or reread the whole paper per package.
Compile only under the build policy in `references/source-handling.md`.

## 6. Continue or freeze

- In single-edit mode, stop after the application record.
- In serial-review mode, immediately expand the next semantic package and make
  it the sole active package. Honor deferred items and the author's chosen order.
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
markup only. A passing result does not certify author authority, translation
fidelity, scientific correctness, citation validity, or claim strength.
