---
name: translate-paper-zh
description: Manual only. Use only when the user explicitly invokes $translate-paper-zh to translate an English academic paper PDF or extracted paper text into paragraph-aligned English-Chinese Markdown with locally rendered figures and tables.
---

# Translate Paper ZH

## Purpose

Convert an English academic paper PDF into a bilingual Markdown translation with paragraph-level alignment and consistently rendered high-resolution screenshots for all figures and tables.

Use local PyMuPDF rich-text extraction plus local page-region screenshot rendering by default. Treat screenshots—not reconstructed Markdown tables or raw embedded bitmap extraction—as the canonical visual representation. Do not use MinerU, cloud parsing APIs, or OCR services unless the user explicitly requests them.

Default outputs:

- Intermediate extraction: `input-name.extracted.md`
- Figure assets: `input-name.assets/figure-NNN-page-NNN.png`
- Table assets: `input-name.assets/table-NNN-page-NNN.png`
- Final translation: `input-name.zh.md` in the same directory as the source PDF

## Workflow

1. Locate the paper PDF the user named. If multiple PDFs match or the target is unclear, ask the user to choose.
2. Resolve this loaded skill's directory and use the current project-owned Python interpreter. Ensure PyMuPDF is available in that interpreter; install it only when the applicable host package policy authorizes installation:

   ```bash
   python3 -m pip install PyMuPDF
   ```

   Skip installation when the dependency is already present.
3. Extract rich Markdown, captioned figures, and captioned tables with the bundled script:

   ```bash
   python3 /resolved/skill/directory/scripts/extract_pdf_text.py \
     paper.pdf --output paper.extracted.md
   ```

   The default rich path uses font spans, coordinates, and line geometry to preserve extractable **bold**, *italic*, superscripts, heading hints, and paragraph reflow. It detects `Figure`/`Fig.` and `Table`/`Tab.` captions and renders both visual types from PDF page regions at **400 DPI by default**. Save PNG files under `paper.assets/`. Insert figure screenshots before figure captions and table screenshots after table captions, matching academic layout conventions. Page-region rendering preserves raster, vector, composite, and complex tabular content consistently. Never use less than 300 DPI for normal translation deliverables.
4. Inspect `paper.extracted.md` and `paper.assets/` before translating. Check paragraph reflow, two-column order, missing pages, headers/footers, equations, OCR artifacts, hyphenation, figure/table placement, crop boundaries, image legibility, and caption association. Treat `<!-- Auto-rendered fallback crop: verify this figure against the PDF. -->` and `<!-- Auto-rendered fallback crop: verify this table against the PDF. -->` as mandatory manual-review markers.
5. If rich extraction fails, stop and report the failure. Do not silently fall back to plain text. If the PDF is scanned or extraction quality is too poor, stop and report that OCR or a better source file is needed.
6. Translate section by section into `paper.zh.md`, preserving section order, paragraph order, visual asset order, and relative asset paths. Copy each English source paragraph from the reviewed extraction instead of regenerating it from memory; preserve all citations and technical clauses. Apply one canonical placement rule throughout:
   - Figure: high-resolution screenshot → English caption blockquote → Chinese caption.
   - Table: English caption blockquote → Chinese caption → high-resolution screenshot.
   Do not add a Markdown reconstruction of a table by default. Add machine-readable table data only when the user explicitly requests it, place it after the screenshot, and verify every cell against the screenshot.
7. Run the bundled CJK-emphasis normalizer on the finished `paper.zh.md` (see "Bold/italic rendering with punctuation"). It is idempotent, so re-running after edits is safe.
8. Run the bundled translation validator in strict mode. Treat every error as a blocker and manually review every warning:

   ```bash
   python3 /resolved/skill/directory/scripts/validate_translation.py \
     paper.extracted.md paper.zh.md --strict
   ```

9. Run the final checks below before reporting completion.

To disable image rendering for text-only diagnostics, pass `--no-images`. To choose a different asset directory or rasterization resolution, use `--images-dir <dir>` and `--image-dpi <300-600>`. Use **400 DPI by default**. Increase to **450-600 DPI** for dense qualitative panels, screenshots, plots with small legends, or figures whose text is not crisp at 150-200% zoom. Do not lower below 300 DPI to reduce file size; preserve readability instead. Keep the image workflow enabled for normal translations.

## Output Contract

Use this format for ordinary body paragraphs:

```markdown
## 中文章节标题

> English source paragraph with original **bold**, *italic*, citations such as [12], URLs such as https://example.com, and `$I_{src}$`.

完整的中文翻译段落，保留 **加粗**、*斜体*、https://example.com 和 `$I_{src}$`，但不要保留英文原文中的引用标记。
```

Follow these rules strictly:

- Translate paragraph by paragraph, not sentence by sentence.
- Merge PDF-wrapped lines into coherent source paragraphs before translating.
- Put each English source paragraph immediately before its complete Chinese translation.
- Put English source paragraphs in Markdown blockquotes (`>`). Do not blockquote Chinese translation paragraphs.
- Preserve the original English paragraph's extractable formatting as much as possible, including **bold**, *italic*, inline code, code blocks, lists, equations, figure/table captions, footnotes, and table structure.
- Preserve the Chinese translation's corresponding Markdown formatting as much as possible.
- Preserve every valid figure's placement and relative asset path; do not blockquote image lines.
- Keep each figure image immediately before its caption. Put the English caption in a blockquote and its complete Chinese translation directly below it.
- Preserve every table screenshot and relative path. Put the English table caption in a blockquote, the Chinese caption directly below it, and the screenshot immediately after the caption pair.
- Keep exactly one canonical screenshot per numbered figure/table unless the source itself splits the item across pages. Do not duplicate a visual using both an extracted bitmap and a page screenshot.
- Translate image alt text when useful, but never alter the path inside `(paper.assets/...)`.
- Do not summarize, omit, simplify, or paraphrase away technical detail.
- Use accurate, natural academic Chinese and keep terminology stable.

## Source Fidelity and Paragraph Completeness

- Treat each English blockquote as a source transcript, not a rewritten explanation. Copy it from the reviewed extraction and compare it against the PDF when extraction is noisy.
- Preserve every citation, parenthetical qualification, cross-reference, numerical condition, and technical clause in English blockquotes. Remove citations only from the Chinese translation.
- Never shorten an English paragraph to improve readability. Repair PDF line wrapping and obvious extraction artifacts without deleting content.
- Compare paragraph endings against the PDF. Page and column breaks commonly cause the last sentences of a paragraph to disappear or attach to another block.
- When a source paragraph crosses a page boundary, reconstruct the complete English paragraph first, then translate the complete paragraph. Do not translate only the first page fragment.
- Maintain one-to-one alignment at paragraph level. If several short list items form one semantic block, preserve all items and their order rather than summarizing them.
- After each section, compare its English blockquote count, citation count, and final sentence against the reviewed extraction. A citation deficit or a substantially shorter matched paragraph requires manual review.
- Treat `validate_translation.py --strict` warnings about source fidelity or missing citations as completion blockers unless comparison with the PDF proves them to be extraction false positives; document any intentional exception.

### Bold/italic rendering with punctuation (important)

CommonMark's flanking-delimiter rule (as implemented by `markdown-it`, used by `markdown-preview-enhanced`) rejects a *paired* emphasis span when its content **starts or ends with a punctuation character** — including full-width CJK punctuation such as `）`, `，`, `。`. The whole span then renders literally with visible asterisks. This was verified with markdown-it.

- FAILS: `**快速模式（Fast Mode，MTP）**并行` — content ends with `）` (punctuation) → literal `**`.
- FAILS: `**（备注）说明**` — content starts with `（`.
- Renders fine: `**快速模式**并行` — content starts/ends with a CJK *letter*, so no fix is needed. Adjacency to a CJK *letter* is NOT the problem; adjacency of *punctuation on the inner side of the delimiter* is.

Fix: insert a zero-width space `U+200B` on the **inner** side of the offending delimiter, between the delimiter and the punctuation:

- `**（备注）说明**`    → `**​（备注）说明**`    (ZWSP right after the opening `**`)
- `**快速模式（MTP）**` → `**快速模式（MTP）​**` (ZWSP right before the closing `**`)

The ZWSP is invisible, does not affect layout, and is virtually copy-safe.

Do not hand-edit this. After finishing the `.zh.md`, run the bundled normalizer. It only touches *paired* `**...**` / `*...*` spans whose content starts/ends with punctuation, inserting an inner `U+200B` (idempotent, safe to re-run). It deliberately leaves isolated asterisks alone — e.g. footnote markers like `* 表示复现结果` or a line starting with `*（说明…` — as well as list markers (`* item`) and thematic breaks (`***`), so it will not create false positives:

```bash
# Fix in place
python3 /resolved/skill/directory/scripts/fix_cjk_emphasis.py \
  paper.zh.md

# Or just check (exit code 1 if any issue remains)
python3 /resolved/skill/directory/scripts/fix_cjk_emphasis.py \
  paper.zh.md --check
```

## Rich Extraction Expectations

- Use the bundled script's default `--mode rich` path for PDFs.
- Expect the intermediate file to contain page markers, inferred Markdown headings, reflowed paragraphs, and span-level formatting such as `**bold**`, `*italic*`, and `<sup>...</sup>` when the PDF exposes that information.
- Do not preserve PDF visual line breaks inside ordinary prose paragraphs. Reflow wrapped lines into complete paragraphs before translation.
- Keep list items, headings, standalone equations, captions, and table-like blocks separated when the extraction makes them identifiable.
- If rich extraction fails or produces no meaningful text, stop and tell the user that OCR, a better source file, or a different extraction strategy is needed.
- Do not install or call MinerU by default for this skill. Use local rich extraction first; only discuss MinerU if the user explicitly asks for it.

## Unified Figure and Table Screenshot Policy

- Render every numbered figure and table from its PDF page region. Do not use embedded-image extraction for figures and page screenshots for tables as two different quality paths; use the same screenshot renderer, DPI policy, color mode, PNG format, and crop-review process for both.
- Use 400 DPI by default and enforce a 300 DPI minimum. Raise dense, small-font, screenshot-heavy, or multi-panel visuals to 450–600 DPI.
- Name assets deterministically from source caption numbers: `figure-NNN-page-NNN.png` and `table-NNN-page-NNN.png`. Keep them in one paper-specific `.assets` directory beside the Markdown output.
- Preserve source ordering and maintain one-to-one mapping among caption number, screenshot filename, and Markdown reference.
- Apply academic caption placement consistently:
  - Figures: screenshot above caption.
  - Tables: caption above screenshot.
- Separate screenshot and caption with exactly one blank line. Do not allow unrelated prose, another visual, a heading, or a page marker between a screenshot and its caption group.

## Figure Handling

- Render captioned figures from the PDF page region rather than relying only on embedded image objects. This preserves vector plots, diagrams assembled from many small image blocks, and mixed raster/vector figures.
- Insert the Markdown image link immediately before the detected `Figure`/`Fig.` caption in the intermediate extraction and preserve that location in the final translation.
- Verify every rendered crop against the source PDF. Check that the crop contains the whole figure, excludes unrelated body text, and remains crisp when zoomed to 150-200% in Markdown preview.
- Check output pixel dimensions as a secondary guardrail: target roughly 2400 px or more for a full-width figure at 400 DPI and 1200 px or more for a half-column figure. If labels remain blurry at 200% zoom, increase DPI regardless of pixel count.
- Treat fallback-crop comments as unresolved review items. Correct or replace a bad crop before declaring the translation complete; never silently keep a misleading figure.
- Inspect ordinary crops too: titles, legends, row labels, or panels can extend slightly beyond the detected vector/image bounds even without a fallback marker. Re-render the affected page region manually when any edge is clipped.
- Apply manual crop corrections only after the final automatic extraction pass, because rerunning the extractor overwrites deterministic asset filenames.
- Account for papers that use unusual caption labels or place captions away from figures. Compare the number and ordering of source figures against Markdown image links. Report any figure that cannot be reliably extracted or associated.
- Keep text appearing inside figures unchanged; do not invent translations inside rasterized images. Translate the extractable figure caption below the image.
- Do not duplicate the same figure through both a page crop and a separately extracted embedded image.

## Table Handling

- Detect `Table`/`Tab.` captions and render the associated table region as `table-NNN-page-NNN.png` at the same high DPI used for figures.
- Preserve every substantive table as a complete screenshot. Do not add assistant-authored summaries, selected-value notes, approximate-number recaps, method lists, or explanations such as “无法可靠重建为网格” after the screenshot. The paper's own surrounding prose already provides interpretation. Add a table summary only when the user explicitly asks for analysis, and keep that analysis outside the paragraph-aligned translation deliverable.
- Prefer the screenshot as the fidelity source when merged cells, multi-row headers, mathematical notation, underlines/bold rankings, or scattered PDF columns make Markdown reconstruction unreliable.
- Do not reconstruct a Markdown table by default. The screenshot is the canonical table representation. Only add a machine-readable Markdown table when explicitly requested, verify all values against the screenshot, and place it below the screenshot.
- Place the English table caption first as a blockquote, the Chinese caption next, and the screenshot immediately below.
- Inspect every table screenshot for complete headers, first/last rows, footnotes, rules, and column edges. A crop is invalid if any header, legend, note, or row is clipped.
- Enforce at least 300 DPI and use 400 DPI by default. Raise dense, full-page, or small-font tables to 450-600 DPI when needed.
- Treat table fallback-crop comments as unresolved. Compare the crop against the source page and manually correct it before completion.
- Compare source table numbers against output assets and captions. Missing or duplicated table numbers are completion blockers.

## Title, Byline, and Biography

- At the top of the final `.zh.md`, output only the Chinese translation of the paper title as the Markdown title.
- Do not include the English title blockquote.
- Omit author names, affiliations, emails, contribution notes, correspondence notes, funding footnotes attached to the byline, and biography sections.
- Do not translate biography content. If a paper has a `Biography`, `Biographies`, `Author Biography`, or similar section, skip that section entirely.
- Continue translating the actual paper content such as abstract, keywords, introduction, method, experiments, appendix, figure captions, and table captions when extractable.

## Citations, URLs, and References

- Keep citation markers exactly in English source paragraphs, because they are part of the original paragraph.
- Remove citation markers from Chinese translation paragraphs. This includes forms such as `[1]`, `[12, 15]`, `(Smith et al., 2024)`, `Smith et al. (2024)`, `\cite{...}`, and superscript-style citation markers when they are clearly citations.
- Do not invent citations in Chinese translations.
- Keep URLs unchanged and untranslated wherever they appear in body text, captions, footnotes, or tables.
- Omit the references/bibliography section from the final `.zh.md` by default. Stop before sections titled `References`, `Bibliography`, `Works Cited`, or equivalent. Include references only if the user explicitly asks.

## Math and Technical Notation

- Convert variables and equations to Markdown math environments where appropriate.
- Use inline math such as `$I_{src}$`, `$V$`, and `$P \sim \pi_\theta(\cdot \mid I_{src}, V)$`.
- Use display math for standalone equations:

  ```markdown
  $$
  P \sim \pi_\theta(\cdot \mid I_{src}, V)
  $$
  ```

- Reconstruct obvious math notation from extraction artifacts when the intended notation is clear.
- Do not leave plain-text variables such as `Isrc` when the intended formula is clearly `$I_{src}$`.
- Keep code, dataset names, benchmark names, product names, model names, library names, and file names unchanged unless there is a standard Chinese rendering.

## Extraction Cleanup

- Remove repeated page headers, footers, page numbers, and running titles when they interrupt paragraphs.
- Repair obvious line-break hyphenation.
- Rejoin ordinary prose lines that were split only because of PDF layout.
- Keep equations and code blocks separate from prose.
- Watch especially for two-column papers where extraction may interleave columns or move captions into body paragraphs.
- Preserve all tables as high-resolution screenshots and translate only the paper's own nearby natural-language explanations. Do not add a duplicate Markdown grid unless the user explicitly requests machine-readable data.
- Never insert assistant-authored table recaps, extraction excuses, approximate values, invented grids, or selected-value notes into the translation.
- Preserve non-extractable text visually inside the rendered figure. Do not invent a transcription or translation; mention unreadable figure text only when it affects comprehension.
- Use `[原文不清]` only when the source cannot be confidently recovered.
- Ask the user before making broad cleanup choices that could change meaning.

## Long Papers

For long PDFs:

1. Extract the whole text first.
2. Translate into the same output file section by section.
3. Keep an internal terminology list and apply it consistently.
4. Periodically compare headings and paragraph counts against the extracted text.
5. If the context window is too small to finish in one pass, save the partial `.zh.md`, report the completed range, and continue from the next section when resumed.

## Final Check

Before saying the task is complete:

- Confirm the final `.zh.md` exists.
- Confirm the title area contains only the Chinese title.
- Confirm author metadata and biography sections are omitted.
- Confirm major source sections appear in the output, except references/bibliography.
- Confirm English source paragraphs are blockquoted and Chinese translation paragraphs are not.
- Compare a sample from every major section against the PDF, including the first and last sentence, citations, numbers, formulas, and cross-references.
- Confirm the final Markdown contains no U+FFFD replacement characters or unexplained Unicode control characters.
- Search for extraction markers such as `[unreadable]`, `[missing]`, and `[原文不清]`; report any that remain.
- Spot-check that Chinese translation paragraphs do not contain citation markers.
- Spot-check that URLs remain unchanged and untranslated.
- Spot-check that obvious formulas use Markdown math notation.
- Compare source `Figure`/`Fig.` captions against Markdown image links; report unmatched or missing figures.
- Compare source `Table`/`Tab.` numbers against table screenshots and bilingual captions; missing, duplicated, or mismatched tables are blockers.
- Confirm every referenced asset exists and every link is relative and valid. Enforce the canonical adjacency sequences exactly: `figure screenshot → English caption → Chinese caption` and `English table caption → Chinese caption → table screenshot`.
- Confirm figures and tables were rendered through the same page-region screenshot path at 300 DPI or higher; spot-check fine labels at 200% zoom and rerender unclear assets at 450-600 DPI.
- Confirm full-width and half-column screenshots satisfy the approximate 400-DPI pixel-width guardrails (2400 px and 1200 px respectively), unless the source PDF itself has lower native raster resolution.
- Confirm no fallback-crop review comment remains unresolved.
- For every optional Markdown table, compare all cells and column order against its screenshot; a screenshot does not excuse incorrect transcribed values.
- Confirm the CJK-emphasis normalizer reports no remaining issues (`fix_cjk_emphasis.py paper.zh.md --check` exits 0); otherwise bold/italic will not render in `markdown-preview-enhanced`.
- Confirm `validate_translation.py paper.extracted.md paper.zh.md --strict` exits 0, or document each manually verified false-positive warning before delivery.
- Give the user the absolute paths to the Markdown file and its `.assets` directory.
