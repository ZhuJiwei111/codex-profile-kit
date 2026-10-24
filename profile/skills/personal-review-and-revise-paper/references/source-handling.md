# Canonical source handling

## Discover the canonical paper

For LaTeX, find the real entrypoint and follow `\input`, `\include`, bibliography,
figure, and supplementary relationships only as far as needed for the requested
change. Prefer Makefiles, repository docs, and existing build scripts over
invented commands. Generated PDFs are evidence or outputs, not editable sources.

For Markdown, identify the file or ordered file set that actually produces the
paper. Check whether a generator owns it before editing. Treat frontmatter,
citations, math, embedded HTML, and linked figures as source semantics.

If several plausible entrypoints remain, use the author's declared target or
ask when unresolved. An explicit request to establish a new revision directory
authorizes that destination; preserve the submitted source as the baseline and
designate one current editable source. Do not create additional candidate or
backup trees automatically.

## Work safely in Git

Inspect repository root, branch, status, and the exact affected paths. A dirty
worktree is allowed. Preserve unrelated edits and stop if another task owns an
overlapping source surface.

Do not require a commit, create a branch, stage, commit, push, or make backup
copies merely to apply a package. Git is the recovery surface; the ledger is the
decision record.

## Use a complete source anchor

The original English/source block in an approved package is the apply
precondition. Before editing:

1. Re-read the target file from disk.
2. Search for the complete original block, including meaningful LaTeX markup.
   Remove only the ledger's comparison spans when recovering the anchor. For
   rendered table views or multi-file packages, record each exact source block
   once in the anchor metadata so display transformations do not destroy it.
3. Require exactly one unambiguous match.
4. If it has drifted, do not approximate by line number or partial phrase.
   Rebuild the package from live source and obtain the decision required by the
   recorded approval policy. If the old block is absent because the complete
   approved replacement is already at the target, verify the applied scope and
   record completion instead of inserting it again.

For insertions, anchor both neighboring semantic blocks or a stable structural
marker. For tables, anchor the affected row/caption/label combination, not a
bare numeric cell that may occur elsewhere.

Use `apply_patch` for the exact approved edit. Do not reflow surrounding source,
run a rewriting formatter, or incorporate adjacent cleanup.

For multi-file application, check all anchors before the first edit. If only
some approved targets were written before a failure, record them explicitly and
keep the package `approved` with the remaining targets pending. Resume only the
missing edits; do not call the whole package applied or open the next one yet.

When the author requests manuscript revision highlighting, reuse the project's
existing markup at sentence-level or finer. Leave unchanged sentences unmarked.
Ledger red/blue comparison colors do not automatically authorize TeX highlights.

## Source-level verification

After application, verify only what the package changed:

- approved new text is present and the approved old text is absent where
  applicable;
- citations, labels, references, formulas, values, and formatting marks match
  the approved package;
- this application introduced no unrelated changes relative to the live source
  read before editing (existing dirty hunks are not this package's changes); and
- `git diff --check -- <affected paths>` passes.

Record checks in the ledger. For authorized bilingual/TeX synchronization,
verify that every declared target carries the same approved meaning, numbers,
citations, and tables. Source verification is not render verification.

## Build and render policy

During proposal discussion and normal application, do not build the paper.
Build only when:

- the author explicitly asks to inspect visual effects;
- the workflow enters final freeze verification.

If a visual change cannot be judged at source level, explain the needed preview
and obtain rendering authority. An explicit no-build instruction remains in
force until the author changes it; do not infer permission from package closure.

At freeze, use the project-owned environment and build path. Check errors,
undefined references/citations, relevant warnings, extracted text, page count,
and the pages affected by tables, figures, captions, or layout. Mark
`final_render_verified` only after fresh output is inspected.

PDF and DOCX may be compared or read, but this skill does not directly edit them.
For binary raster edits, use an image-editing workflow; for SVG or diagram source,
edit the canonical vector/code asset when separately authorized. The package
still records the intended visible change and approval.
