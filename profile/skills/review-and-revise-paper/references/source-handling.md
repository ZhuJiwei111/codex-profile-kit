# Canonical source handling

## Discover the canonical paper

For LaTeX, find the real entrypoint and follow `\input`, `\include`, bibliography,
figure, and supplementary relationships only as far as needed for the requested
change. Prefer Makefiles, repository docs, and existing build scripts over
invented commands. Generated PDFs are evidence or outputs, not editable sources.

For Markdown, identify the file or ordered file set that actually produces the
paper. Check whether a generator owns it before editing. Treat frontmatter,
citations, math, embedded HTML, and linked figures as source semantics.

If several plausible entrypoints remain, ask the author. Do not silently select
an archived submission, an old draft, or a prior revision directory.

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
3. Require exactly one unambiguous match.
4. If it has drifted, do not approximate by line number or partial phrase.
   Rebuild and reapprove the package from live source.

For insertions, anchor both neighboring semantic blocks or a stable structural
marker. For tables, anchor the affected row/caption/label combination, not a
bare numeric cell that may occur elsewhere.

Use `apply_patch` for the exact approved edit. Do not reflow surrounding source,
run a rewriting formatter, or incorporate adjacent cleanup.

## Source-level verification

After application, verify only what the package changed:

- approved new text is present and the approved old text is absent where
  applicable;
- citations, labels, references, formulas, values, and formatting marks match
  the approved package;
- no unrelated hunk appeared in the affected files; and
- `git diff --check -- <affected paths>` passes.

Record checks in the ledger. Source verification is not render verification.

## Build and render policy

During proposal discussion and normal application, do not build the paper.
Build only when:

- the author explicitly asks to inspect visual effects;
- the change cannot be judged without rendering, such as float placement or a
  complex table/figure; or
- the workflow enters final freeze verification.

At freeze, use the project-owned environment and build path. Check errors,
undefined references/citations, relevant warnings, extracted text, page count,
and the pages affected by tables, figures, captions, or layout. Mark
`final_render_verified` only after fresh output is inspected.

PDF and DOCX may be compared or read, but this skill does not directly edit them.
For binary raster edits, use an image-editing workflow; for SVG or diagram source,
edit the canonical vector/code asset when separately authorized. The package
still records the intended visible change and approval.
