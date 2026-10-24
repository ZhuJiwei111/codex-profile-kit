# Revision ledger format

## Single source of state

Use one repository-local Markdown ledger. Its frontmatter owns stable project
configuration and identifies the sole active package; its body owns proposals,
author decisions, applications, and verification records. Record document roles,
review order, explicit authority overrides, and synchronization targets in its
scope section. Keep one canonical source per document; additional author-requested
presentation formats follow that source and contain no independent decisions.

Default `approval_policy` is `active_package_only`. When the author explicitly
grants broader editing discretion, use `recorded_scope` and quote the authority
with its exact document/section bounds in the scope section. A validator cannot
determine whether that authorization is real; the agent must verify it.

Use the template in `../assets/revision-ledger-template.md`. Keep exactly one
meaning in one place: a fully expanded package replaces its coverage-inventory
placeholder, and an updated candidate replaces its superseded candidate.

## Required package shape

Each package uses `### PKG-NNN — title` and these seven headings in order:

1. `原文英文`
2. `候选英文`
3. `原文中文`
4. `候选中文`
5. `修改判断`
6. `作者决定`
7. `应用与验证记录`

Package metadata before section 1 records the target file and semantic anchor,
motivation, reviewer/evidence provenance, status, and workflow mode. Do not use
line numbers as the only anchor because edits move them.

For a multi-part package, label the same target blocks consistently within each
of the four language/version sections. A Response package also includes the
complete reviewer comment and Chinese translation in metadata; it is context,
not text to silently rewrite. Do not migrate an existing compatible ledger just
to rename headings or reorder records during ordinary discussion.

## Color contract

- Original English and Chinese: wrap only deleted or replaced material in
  `<span style="color:#c62828">...</span>`.
- Proposed English and Chinese: wrap only added or replacement material in
  `<span style="color:#1565c0">...</span>`.
- Keep unchanged text black by leaving it outside spans.
- Mark changed sentences or smaller meaningful spans, never an entire paragraph
  merely because one sentence changed. Keep this resolution in manuscript
  highlights too when those highlights are separately requested.
- Do not use green reference text. This workflow has two versions only:
  original and proposed.
- Keep HTML spans outside fenced code blocks so the Markdown renderer can show
  color.
- Preserve complete citations, formulas, references, punctuation, and context
  in both full semantic units.

For a pure insertion, state that no corresponding original text exists, then
show the complete insertion in blue. For a pure deletion, show the complete
affected original in red and enough black context in the proposal to make the
deletion location unambiguous.

Chinese text must be a faithful, complete rendering of the corresponding
English semantic unit, not a summary. Preserve exact technical terms when
translation would make verification harder. The colored meaning boundaries in
English and Chinese must correspond.

Do not add a separate fenced `diff`, sentence-by-sentence change list, or prose
summary that duplicates the red/blue comparison.

## Tables

Use adaptive exact display:

- Entirely new table: show the complete proposed matrix.
- Existing small table: show the complete original and proposed table.
- Existing large table: show every affected row in full, every changed cell,
  caption/header/footnote/structure changes, and every changed bold, underline,
  or winner mark. Unchanged rows outside the affected surface need not repeat.
- In affected rows, retain unchanged cells in black; color only changed cells or
  formatting tokens.
- Never replace concrete cells with phrases such as "新增某行" or "更新若干数值".

Numeric matrices appear once because numbers are language-neutral. In the
Chinese sections, translate every caption, header, footnote, label, and prose
statement, then point to the exact numeric matrix already displayed rather than
copying it mechanically.

Use the same complete before/after bilingual comparison in the user reply;
paragraph-paired ordering is fine there. Repeat full numeric matrices in both
languages if the author explicitly requests standalone bilingual tables.

## Figures, citations, and cross-references

For a figure package, record the original and proposed caption, affected panel,
asset path, visible change, manuscript interpretation, and whether a rendered
preview is required. For bibliography changes, show the complete affected entry
and explain the citation-level consequence; do not produce noisy field-by-field
diffs when the entry is simply new.

Treat labels, `\ref`/`\cref`, citations, table numbering, and winner formatting
as semantic content when they change what a reader sees.

## Status transitions

The normal application path is:

`drafting -> pending_author_decision -> approved -> applied_source_verified -> final_render_verified`

- `deferred`: the author postpones an unclosed proposal. Preserve its candidate,
  evidence gaps, and reason in place, then clear the active pointer. To resume,
  recheck live source and return it to `drafting` or `pending_author_decision`.
  Do not inherit approval for refreshed wording.
- `closed_without_change`: the author accepts leaving the source unchanged or
  rejects the proposal. Record the decision and `application: 未应用（保留原文）`.
  This closes the package without inventing a successful source edit. Keep the
  discussed proposal for traceability, clearly identified as not applied.

`author_locked_risk` is a terminal exception for a verified contradiction the
author explicitly chooses not to change. It must describe the unresolved risk
and must never say the issue passed consistency verification.

Only `drafting`, `pending_author_decision`, or `approved` may be the top-level
active package. At most one package may have one of these statuses.

`author_locked_risk` records an explicit unresolved decision, not a routine
no-change outcome. An applied package reopened for new wording receives a new
linked ID; preserve its original approval and application history. A partial
approval applies only the approved blocks. Record whether rejected blocks are
closed or deferred; keep the parent open if part of its decision remains pending.

## Updating a proposal

When the author requests different wording:

1. Rebuild the candidate and faithful Chinese translation in the same package.
2. Recompute the red/blue spans from the original to the new candidate.
3. Replace the previous candidate rather than appending another full variant.
4. Add one concise decision note explaining what changed.
5. Keep the package `pending_author_decision` until the new exact candidate is
   approved within the recorded author authority.
