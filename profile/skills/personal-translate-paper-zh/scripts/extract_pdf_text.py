#!/usr/bin/env python3
"""Extract a paper PDF into Markdown-ish text for translation.

The default engine uses PyMuPDF rich text dictionaries to preserve extractable
font styling, heading hints, superscripts, and paragraph reflow. It also renders
captioned figure and table regions to high-resolution PNGs so raster, vector,
composite figures, and complex tables can be linked from the extracted Markdown.
Plain-text extractors are retained only for
explicit diagnostics via --mode plain. The script does not perform OCR.
"""

from __future__ import annotations

import argparse
import html
import os
import re
import shutil
import statistics
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RichLine:
    text: str
    plain: str
    x0: float
    x1: float
    y0: float
    y1: float
    size: float
    boldish: bool


@dataclass
class VisualAsset:
    anchor_y: float
    markdown: str
    kind: str


def escape_markdown_text(text: str) -> str:
    text = html.unescape(text)
    text = text.replace("\u00ad", "")
    return text


def span_is_bold(span: dict) -> bool:
    font = str(span.get("font", "")).lower()
    flags = int(span.get("flags", 0))
    return bool(flags & 16) or "bold" in font or "black" in font or "semibold" in font


def span_is_italic(span: dict) -> bool:
    font = str(span.get("font", "")).lower()
    flags = int(span.get("flags", 0))
    return bool(flags & 2) or "italic" in font or "oblique" in font


def span_is_superscript(span: dict) -> bool:
    flags = int(span.get("flags", 0))
    return bool(flags & 1)


def style_span(text: str, span: dict) -> str:
    text = escape_markdown_text(text)
    if not text:
        return ""
    leading = re.match(r"^\s*", text).group(0)
    trailing = re.search(r"\s*$", text).group(0)
    core = text[len(leading) : len(text) - len(trailing) if trailing else len(text)]
    if not core:
        return text

    if span_is_superscript(span):
        core = f"<sup>{core}</sup>"
    if span_is_italic(span):
        core = f"*{core}*"
    if span_is_bold(span):
        core = f"**{core}**"
    return f"{leading}{core}{trailing}"


def join_span_texts(spans: list[dict]) -> tuple[str, str, float, bool]:
    parts: list[str] = []
    plain_parts: list[str] = []
    sizes: list[float] = []
    bold_flags: list[bool] = []
    previous_x1: float | None = None
    previous_size = 0.0

    for span in spans:
        raw = str(span.get("text", ""))
        if not raw:
            continue
        bbox = span.get("bbox", [0, 0, 0, 0])
        size = float(span.get("size", 0.0))
        gap = float(bbox[0]) - previous_x1 if previous_x1 is not None else 0.0
        if (
            parts
            and gap > max(previous_size, size) * 0.22
            and not parts[-1].endswith((" ", "\t"))
            and not raw.startswith((" ", "\t"))
        ):
            parts.append(" ")
            plain_parts.append(" ")
        parts.append(style_span(raw, span))
        plain_parts.append(escape_markdown_text(raw))
        sizes.append(size)
        bold_flags.append(span_is_bold(span))
        previous_x1 = float(bbox[2])
        previous_size = size

    text = "".join(parts)
    plain = "".join(plain_parts)
    median_size = statistics.median(sizes) if sizes else 0.0
    boldish = bool(bold_flags) and sum(bold_flags) / len(bold_flags) >= 0.5
    return text.strip(), re.sub(r"\s+", " ", plain).strip(), median_size, boldish


def line_from_pymupdf(line: dict) -> RichLine | None:
    spans = [span for span in line.get("spans", []) if str(span.get("text", "")).strip()]
    if not spans:
        return None
    text, plain, size, boldish = join_span_texts(spans)
    if not plain:
        return None
    bbox = line.get("bbox", [0, 0, 0, 0])
    return RichLine(
        text=text,
        plain=plain,
        x0=float(bbox[0]),
        x1=float(bbox[2]),
        y0=float(bbox[1]),
        y1=float(bbox[3]),
        size=size,
        boldish=boldish,
    )


def collect_body_size(pages: list[dict]) -> float:
    sizes: list[float] = []
    for page in pages:
        for block in page.get("blocks", []):
            if block.get("type") != 0:
                continue
            for line in block.get("lines", []):
                rich_line = line_from_pymupdf(line)
                if rich_line and len(rich_line.plain) > 25:
                    sizes.append(round(rich_line.size, 1))
    return statistics.median(sizes) if sizes else 10.0


def is_list_item(text: str) -> bool:
    return bool(re.match(r"^(\(?[0-9]+[.)]|[A-Za-z][.)]|[-*+•])\s+", text))


def is_heading_line(line: RichLine, body_size: float) -> bool:
    text = strip_markdown_styles(line.plain)
    if not text or len(text) > 120:
        return False
    if text.endswith((".", ",", ";", ":")) and not re.match(r"^\d+(\.\d+)*\s+", text):
        return False
    numbered = bool(re.match(r"^(\d+(\.\d+)*|[IVX]+)\s+[A-Z]", text))
    all_caps = len(text) <= 80 and text.upper() == text and re.search(r"[A-Z]", text)
    return line.size >= body_size + 1.8 or (line.boldish and (numbered or all_caps))


def strip_markdown_styles(text: str) -> str:
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"<sup>(.*?)</sup>", r"\1", text)
    return text.strip()


def heading_prefix(line: RichLine, body_size: float) -> str:
    if line.size >= body_size + 6:
        return "#"
    if line.size >= body_size + 3.5:
        return "##"
    return "###"


def should_join_lines(previous: RichLine, current: RichLine, body_size: float) -> bool:
    if is_heading_line(previous, body_size) or is_heading_line(current, body_size):
        return False
    if is_list_item(previous.plain) or is_list_item(current.plain):
        return False
    if previous.plain.endswith((".", "?", "!", ":", ";")) and current.x0 > previous.x0 + 8:
        return False
    line_gap = current.y0 - previous.y1
    line_height = max(previous.y1 - previous.y0, current.y1 - current.y0, 1.0)
    if line_gap > line_height * 0.9:
        return False
    if abs(current.x0 - previous.x0) > 24 and not previous.plain.endswith("-"):
        return False
    return True


def join_paragraph_line(previous: str, current: str) -> str:
    if previous.endswith("-") and current and current[0].islower():
        return previous[:-1] + current
    if previous.endswith((" ", "/", "-", "–")) or current.startswith((" ", "/", "-", "–")):
        return previous + current
    return previous + " " + current


def join_visual_line_text(previous: str, current: str) -> str:
    if not previous:
        return current
    if previous.endswith((" ", "/", "-", "–")) or current.startswith((" ", "/", "-", "–")):
        return previous + current
    return previous + " " + current


def same_visual_line(previous: RichLine, current: RichLine) -> bool:
    # Captions must never be merged horizontally with neighboring body text
    # from another column, even when their baselines coincide.
    if (
        is_figure_caption(previous.plain)
        or is_figure_caption(current.plain)
        or is_table_caption(previous.plain)
        or is_table_caption(current.plain)
    ):
        return False
    previous_center = (previous.y0 + previous.y1) / 2
    current_center = (current.y0 + current.y1) / 2
    line_height = max(previous.y1 - previous.y0, current.y1 - current.y0, 1.0)
    horizontal_gap = current.x0 - previous.x1
    return abs(previous_center - current_center) <= line_height * 0.45 and horizontal_gap < 80


def merge_visual_lines(lines: list[RichLine]) -> list[RichLine]:
    if not lines:
        return []
    sorted_lines = sorted(lines, key=lambda line: (line.y0, line.x0))
    merged: list[RichLine] = []

    for line in sorted_lines:
        if merged and same_visual_line(merged[-1], line):
            previous = merged[-1]
            merged[-1] = RichLine(
                text=join_visual_line_text(previous.text, line.text),
                plain=join_visual_line_text(previous.plain, line.plain),
                x0=min(previous.x0, line.x0),
                x1=max(previous.x1, line.x1),
                y0=min(previous.y0, line.y0),
                y1=max(previous.y1, line.y1),
                size=max(previous.size, line.size),
                boldish=previous.boldish and line.boldish,
            )
        else:
            merged.append(line)
    return merged


_FIGURE_CAPTION_RE = re.compile(
    r"^\s*(?:Figure|Fig\.)\s*(?:S?\d+[A-Za-z]?)\s*[:.]", re.IGNORECASE
)
_TABLE_CAPTION_RE = re.compile(
    r"^\s*(?:Table|Tab\.)\s*(?:S?\d+[A-Za-z]?)\s*[:.]", re.IGNORECASE
)


def is_figure_caption(text: str) -> bool:
    return bool(_FIGURE_CAPTION_RE.match(strip_markdown_styles(text)))


def is_table_caption(text: str) -> bool:
    return bool(_TABLE_CAPTION_RE.match(strip_markdown_styles(text)))


def caption_asset_id(text: str, kind: str, fallback_index: int) -> str:
    labels = r"Figure|Fig\." if kind == "figure" else r"Table|Tab\."
    match = re.match(
        rf"^\s*(?:{labels})\s*(S?\d+[A-Za-z]?)",
        strip_markdown_styles(text),
        re.IGNORECASE,
    )
    asset_id = match.group(1).lower() if match else str(fallback_index)
    return f"{int(asset_id):03d}" if asset_id.isdigit() else asset_id


def _rect_distance(a, b) -> tuple[float, float]:
    horizontal = max(a.x0 - b.x1, b.x0 - a.x1, 0.0)
    vertical = max(a.y0 - b.y1, b.y0 - a.y1, 0.0)
    return horizontal, vertical


def _figure_column_rect(caption: RichLine, page_rect, fitz):
    margin = 18.0
    page_width = page_rect.width
    if caption.x1 - caption.x0 >= page_width * 0.55:
        return fitz.Rect(margin, 0, page_rect.x1 - margin, page_rect.y1)
    midpoint = page_rect.x0 + page_width / 2
    # Permit a small overlap across the gutter. Figures and row labels often
    # extend beyond the exact half-page boundary even when the caption is
    # clearly assigned to one column.
    if (caption.x0 + caption.x1) / 2 < midpoint:
        return fitz.Rect(margin, 0, midpoint + 18, page_rect.y1)
    return fitz.Rect(midpoint - 18, 0, page_rect.x1 - margin, page_rect.y1)


def _collect_visual_rects(page, page_dict: dict, fitz) -> list:
    page_rect = page.rect
    rects = []
    for block in page_dict.get("blocks", []):
        if block.get("type") != 1 or not block.get("bbox"):
            continue
        rect = fitz.Rect(block["bbox"])
        if rect.width < 3 or rect.height < 3:
            continue
        if rect.get_area() >= page_rect.get_area() * 0.9:
            continue
        rects.append(rect)

    try:
        drawings = page.get_drawings()
    except Exception:  # noqa: BLE001 - image extraction should not break text extraction.
        drawings = []
    for drawing in drawings:
        raw_rect = drawing.get("rect")
        if raw_rect is None:
            continue
        rect = fitz.Rect(raw_rect)
        if max(rect.width, rect.height) < 3:
            continue
        if rect.get_area() >= page_rect.get_area() * 0.9:
            continue
        rects.append(rect)
    return rects


def _select_figure_crop(caption: RichLine, page_rect, visual_rects: list, fitz):
    column = _figure_column_rect(caption, page_rect, fitz)
    full_width_caption = caption.x1 - caption.x0 >= page_rect.width * 0.55
    max_height_ratio = 0.62 if full_width_caption else 0.39
    window_top = max(page_rect.y0 + 12, caption.y0 - page_rect.height * max_height_ratio)
    candidates = []
    for rect in visual_rects:
        if rect.y0 >= caption.y0 or rect.y1 <= window_top:
            continue
        clipped = rect & column
        if clipped.is_empty or clipped.width < 2 or clipped.height < 1:
            continue
        candidates.append(clipped)

    candidates.sort(key=lambda rect: (rect.y1, rect.get_area()), reverse=True)
    crop = candidates[0] if candidates else None
    if crop is not None:
        remaining = candidates[1:]
        changed = True
        while changed:
            changed = False
            kept = []
            for rect in remaining:
                horizontal, vertical = _rect_distance(crop, rect)
                if horizontal <= 28 and vertical <= 38:
                    crop = crop | rect
                    changed = True
                else:
                    kept.append(rect)
            remaining = kept

    fallback = crop is None or crop.width < 60 or crop.height < 35
    if fallback:
        crop = fitz.Rect(
            column.x0,
            max(window_top, caption.y0 - min(260, page_rect.height * 0.38)),
            column.x1,
            caption.y0 - 2,
        )
    else:
        # Tall qualitative panels often have a title drawn just above the main
        # image group. Preserve a little extra space only for these large
        # figures, avoiding unrelated body text around ordinary column plots.
        is_tall_panel = (
            max(crop.height, caption.y0 - crop.y0) > page_rect.height * 0.5
            and crop.y0 > page_rect.height * 0.15
        )
        top_y = (
            max(page_rect.y0 + 12, crop.y0 - 14)
            if is_tall_panel
            else max(window_top, crop.y0)
        )
        crop = fitz.Rect(
            max(column.x0, crop.x0 - 10),
            top_y,
            min(column.x1, crop.x1 + 10),
            min(caption.y0 - 2, max(crop.y1 + 8, caption.y0 - 16)),
        )

    crop = crop & page_rect
    return crop, fallback


def render_figure_assets(
    page,
    page_dict: dict,
    page_lines: list[RichLine],
    page_index: int,
    assets_dir: Path,
    markdown_path: Path,
    dpi: int,
    start_index: int,
    fitz,
) -> tuple[list[VisualAsset], int]:
    captions = [line for line in page_lines if is_figure_caption(line.plain)]
    if not captions:
        return [], start_index

    visual_rects = _collect_visual_rects(page, page_dict, fitz)
    assets: list[VisualAsset] = []
    figure_index = start_index
    assets_dir.mkdir(parents=True, exist_ok=True)

    for caption in captions:
        crop, fallback = _select_figure_crop(caption, page.rect, visual_rects, fitz)
        if crop.is_empty or crop.width < 20 or crop.height < 20:
            continue
        figure_id = caption_asset_id(caption.plain, "figure", figure_index)
        filename = f"figure-{figure_id}-page-{page_index:03d}.png"
        asset_path = assets_dir / filename
        matrix = fitz.Matrix(dpi / 72.0, dpi / 72.0)
        pixmap = page.get_pixmap(matrix=matrix, clip=crop, alpha=False)
        pixmap.save(asset_path)

        relative = Path(os.path.relpath(asset_path, markdown_path.parent)).as_posix()
        caption_plain = re.sub(r"\s+", " ", caption.plain).strip()
        alt = caption_plain[:120].replace("[", "(").replace("]", ")")
        marker = f"![{alt}]({relative})"
        if fallback:
            marker += "\n\n<!-- Auto-rendered fallback crop: verify this figure against the PDF. -->"
        # Figure captions belong below figures: insert the screenshot before
        # the first caption line in the intermediate Markdown.
        assets.append(VisualAsset(anchor_y=caption.y0, markdown=marker, kind="figure"))
        figure_index += 1

    return assets, figure_index


def collect_table_captions(page_dict: dict) -> list[RichLine]:
    captions: list[RichLine] = []
    for block in page_dict.get("blocks", []):
        if block.get("type") != 0:
            continue
        block_lines = []
        for raw_line in block.get("lines", []):
            rich_line = line_from_pymupdf(raw_line)
            if rich_line:
                block_lines.append(rich_line)
        if not block_lines or not is_table_caption(block_lines[0].plain):
            continue
        text = " ".join(line.text for line in block_lines)
        plain = " ".join(line.plain for line in block_lines)
        captions.append(
            RichLine(
                text=text,
                plain=plain,
                x0=min(line.x0 for line in block_lines),
                x1=max(line.x1 for line in block_lines),
                y0=min(line.y0 for line in block_lines),
                y1=max(line.y1 for line in block_lines),
                size=statistics.median(line.size for line in block_lines),
                boldish=all(line.boldish for line in block_lines),
            )
        )
    return sorted(captions, key=lambda line: (line.y0, line.x0))


def _table_rule_rects(page, lower: float, upper: float, fitz) -> list:
    rects = []
    for drawing in page.get_drawings():
        raw_rect = drawing.get("rect")
        if raw_rect is None:
            continue
        rect = fitz.Rect(raw_rect)
        if rect.y0 < lower or rect.y1 > upper or rect.y0 > page.rect.y1 - 70:
            continue
        if rect.width >= page.rect.width * 0.2 and rect.height <= 8:
            # MuPDF represents horizontal rules as zero-height rectangles;
            # inflate them slightly so rectangle unions remain non-empty.
            if rect.height < 1:
                rect = fitz.Rect(rect.x0, rect.y0 - 0.5, rect.x1, rect.y1 + 0.5)
            rects.append(rect)
    return rects


def _detected_table_rects(page, lower: float, upper: float, fitz) -> list:
    try:
        tables = page.find_tables().tables
    except Exception:  # noqa: BLE001 - fallback to ruled-line detection.
        tables = []
    rects = []
    for table in tables:
        rect = fitz.Rect(table.bbox)
        if rect.y0 >= lower - 3 and rect.y0 < upper and rect.y1 <= upper + 4:
            rects.append(rect)
    return rects


def _select_table_crop(page, caption: RichLine, upper: float, fitz):
    lower = caption.y1 + 0.5
    upper = min(upper, page.rect.y1 - 45)
    detected = _detected_table_rects(page, lower, upper, fitz)
    rules = _table_rule_rects(page, lower, upper, fitz)
    rects = detected + rules

    crop = None
    if rects:
        crop = rects[0]
        for rect in rects[1:]:
            crop = crop | rect

    fallback = (
        crop is None
        or crop.width < page.rect.width * 0.28
        or crop.height < 18
    )
    if fallback:
        crop = fitz.Rect(54, lower, page.rect.x1 - 54, upper)
    else:
        crop = fitz.Rect(
            max(42, crop.x0 - 8),
            max(lower, crop.y0 - 6),
            min(page.rect.x1 - 42, crop.x1 + 8),
            min(upper, crop.y1 + 8),
        )
    return crop & page.rect, fallback


def render_table_assets(
    page,
    page_dict: dict,
    page_index: int,
    assets_dir: Path,
    markdown_path: Path,
    dpi: int,
    start_index: int,
    fitz,
) -> tuple[list[VisualAsset], int]:
    captions = collect_table_captions(page_dict)
    if not captions:
        return [], start_index

    assets: list[VisualAsset] = []
    table_index = start_index
    assets_dir.mkdir(parents=True, exist_ok=True)

    for index, caption in enumerate(captions):
        next_caption_y = (
            captions[index + 1].y0 - 5
            if index + 1 < len(captions)
            else page.rect.y1 - 45
        )
        crop, fallback = _select_table_crop(page, caption, next_caption_y, fitz)
        if crop.is_empty or crop.width < 40 or crop.height < 18:
            continue

        table_id = caption_asset_id(caption.plain, "table", table_index)
        filename = f"table-{table_id}-page-{page_index:03d}.png"
        asset_path = assets_dir / filename
        matrix = fitz.Matrix(dpi / 72.0, dpi / 72.0)
        pixmap = page.get_pixmap(matrix=matrix, clip=crop, alpha=False)
        pixmap.save(asset_path)

        relative = Path(os.path.relpath(asset_path, markdown_path.parent)).as_posix()
        caption_plain = re.sub(r"\s+", " ", caption.plain).strip()
        alt = caption_plain[:120].replace("[", "(").replace("]", ")")
        marker = f"![{alt}]({relative})"
        if fallback:
            marker += "\n\n<!-- Auto-rendered fallback crop: verify this table against the PDF. -->"
        # Table captions belong above tables: insert the screenshot after the
        # final caption line in the intermediate Markdown.
        assets.append(VisualAsset(anchor_y=caption.y1 + 0.01, markdown=marker, kind="table"))
        table_index += 1

    return assets, table_index


def reflow_block_lines(
    lines: list[RichLine], body_size: float, assets: list[VisualAsset] | None = None
) -> list[str]:
    output: list[str] = []
    paragraph = ""
    previous_line: RichLine | None = None
    pending_assets = sorted(list(assets or []), key=lambda asset: asset.anchor_y)

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph.strip():
            output.append(re.sub(r"[ \t]+", " ", paragraph).strip())
        paragraph = ""

    for line in lines:
        while pending_assets and line.y0 >= pending_assets[0].anchor_y:
            flush_paragraph()
            output.append(pending_assets.pop(0).markdown)
            previous_line = None
        if is_heading_line(line, body_size):
            flush_paragraph()
            output.append(f"{heading_prefix(line, body_size)} {line.text}")
            previous_line = None
            continue
        if not paragraph:
            paragraph = line.text
        elif previous_line and should_join_lines(previous_line, line, body_size):
            paragraph = join_paragraph_line(paragraph, line.text)
        else:
            flush_paragraph()
            paragraph = line.text
        previous_line = line

    flush_paragraph()
    for asset in pending_assets:
        output.append(asset.markdown)
    return output


def _import_fitz():
    try:
        import fitz  # type: ignore

        return fitz
    except ImportError as exc:  # noqa: BLE001 - give an actionable install hint.
        raise RuntimeError(
            "PyMuPDF (module 'fitz') is not installed in the current Python "
            "environment. Install it into the current project environment, e.g.:\n"
            f"  {sys.executable} -m pip install PyMuPDF\n"
            "then rerun this script with that same interpreter."
        ) from exc


def extract_with_pymupdf_rich(
    pdf_path: Path,
    markdown_path: Path,
    assets_dir: Path | None = None,
    image_dpi: int = 400,
) -> str:
    fitz = _import_fitz()

    with fitz.open(pdf_path) as doc:
        pages = [page.get_text("dict", sort=True) for page in doc]
        body_size = collect_body_size(pages)
        lines: list[str] = [
            f"# Extracted Rich Markdown: {pdf_path.name}",
            "",
            "Extractor: PyMuPDF rich dict",
            "",
            "> This file is an intermediate rich extraction for translation. Review it against the PDF before translating.",
            "",
        ]
        figure_index = 1
        table_index = 1

        for page_index, (page, page_dict) in enumerate(zip(doc, pages), start=1):
            lines.extend([f"<!-- page {page_index} -->", ""])
            raw_page_lines: list[RichLine] = []
            for block in page_dict.get("blocks", []):
                if block.get("type") != 0:
                    continue
                for raw_line in block.get("lines", []):
                    rich_line = line_from_pymupdf(raw_line)
                    if rich_line:
                        raw_page_lines.append(rich_line)

            visual_assets: list[VisualAsset] = []
            if assets_dir is not None and raw_page_lines:
                figures, figure_index = render_figure_assets(
                    page=page,
                    page_dict=page_dict,
                    page_lines=raw_page_lines,
                    page_index=page_index,
                    assets_dir=assets_dir,
                    markdown_path=markdown_path,
                    dpi=image_dpi,
                    start_index=figure_index,
                    fitz=fitz,
                )
                tables, table_index = render_table_assets(
                    page=page,
                    page_dict=page_dict,
                    page_index=page_index,
                    assets_dir=assets_dir,
                    markdown_path=markdown_path,
                    dpi=image_dpi,
                    start_index=table_index,
                    fitz=fitz,
                )
                visual_assets = sorted(
                    figures + tables, key=lambda asset: asset.anchor_y
                )

            page_lines = merge_visual_lines(raw_page_lines)
            if page_lines:
                for paragraph in reflow_block_lines(page_lines, body_size, visual_assets):
                    lines.extend([paragraph, ""])
            else:
                lines.extend(["[no extractable text]", ""])

    return "\n".join(lines).rstrip() + "\n"


def extract_with_pymupdf_text(pdf_path: Path) -> list[str]:
    fitz = _import_fitz()

    pages = []
    with fitz.open(pdf_path) as doc:
        for page in doc:
            pages.append(page.get_text("text", sort=True))
    return pages


def extract_with_pypdf(pdf_path: Path) -> list[str]:
    from pypdf import PdfReader  # type: ignore

    reader = PdfReader(str(pdf_path))
    pages = []
    for page in reader.pages:
        try:
            pages.append(page.extract_text(extraction_mode="layout") or "")
        except TypeError:
            pages.append(page.extract_text() or "")
    return pages


def extract_with_pdfminer(pdf_path: Path) -> list[str]:
    from pdfminer.high_level import extract_text  # type: ignore

    text = extract_text(str(pdf_path))
    return text.split("\f")


def extract_with_pdftotext(pdf_path: Path) -> list[str]:
    if not shutil.which("pdftotext"):
        raise RuntimeError("pdftotext not found")

    completed = subprocess.run(
        ["pdftotext", "-layout", str(pdf_path), "-"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return completed.stdout.split("\f")


def extract_plain_pages(pdf_path: Path) -> tuple[str, list[str]]:
    extractors = [
        ("PyMuPDF plain text", extract_with_pymupdf_text),
        ("pypdf", extract_with_pypdf),
        ("pdfminer.six", extract_with_pdfminer),
        ("pdftotext", extract_with_pdftotext),
    ]
    failures = []
    for name, extractor in extractors:
        try:
            pages = extractor(pdf_path)
            if any(page.strip() for page in pages):
                return name, pages
            failures.append(f"{name}: extracted no text")
        except Exception as exc:  # noqa: BLE001 - report all extractor failures.
            failures.append(f"{name}: {exc}")
    raise RuntimeError("Could not extract text:\n" + "\n".join(failures))


def normalize_page(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"-\n(?=[a-z])", "", text)
    text = re.sub(r"(?<=[a-z,;:])\n(?=[a-z0-9(])", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def page_to_paragraphs(text: str) -> list[str]:
    text = normalize_page(text)
    if not text:
        return []
    blocks = re.split(r"\n\s*\n", text)
    paragraphs = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        if len(block) > 1800:
            pieces = re.split(
                r"(?<=[.!?])\s+(?=(?:[A-Z][a-z]|[0-9]+\.|[A-Z][A-Z ]{3,}))",
                block,
            )
            paragraphs.extend(piece.strip() for piece in pieces if piece.strip())
        else:
            paragraphs.append(block)
    return [re.sub(r"[ \t]+", " ", paragraph).strip() for paragraph in paragraphs]


def render_plain_markdown(pdf_path: Path, extractor_name: str, pages: list[str]) -> str:
    lines = [
        f"# Extracted Text: {pdf_path.name}",
        "",
        f"Extractor: {extractor_name}",
        "",
        "> This file is an explicit plain-text diagnostic extraction. Do not use it as the default translation source when rich extraction is available.",
        "",
    ]
    for index, page in enumerate(pages, start=1):
        paragraphs = page_to_paragraphs(page)
        lines.extend([f"<!-- page {index} -->", ""])
        if not paragraphs:
            lines.extend(["[no extractable text]", ""])
            continue
        for paragraph in paragraphs:
            lines.extend([paragraph, ""])
    return "\n".join(lines).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path, help="Path to the source PDF")
    parser.add_argument("--output", "-o", type=Path, help="Output Markdown path")
    parser.add_argument(
        "--mode",
        choices=("rich", "plain"),
        default="rich",
        help="Use PyMuPDF rich extraction by default; plain is an explicit diagnostic mode.",
    )
    parser.add_argument(
        "--images-dir",
        type=Path,
        help="Directory for rendered figure images (default: <pdf-stem>.assets beside the Markdown output).",
    )
    parser.add_argument(
        "--no-images",
        action="store_true",
        help="Do not render captioned figures/tables or insert Markdown image links.",
    )
    parser.add_argument(
        "--image-dpi",
        type=int,
        default=400,
        help="Rasterization DPI for figure crops (300-600; default: 400 for clear zooming)."
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    pdf_path = args.pdf.expanduser().resolve()
    if not pdf_path.exists():
        print(f"PDF not found: {pdf_path}", file=sys.stderr)
        return 2
    if pdf_path.suffix.lower() != ".pdf":
        print(f"Input is not a PDF: {pdf_path}", file=sys.stderr)
        return 2

    output_path = args.output
    if output_path is None:
        output_path = pdf_path.with_suffix(".extracted.md")
    else:
        output_path = output_path.expanduser().resolve()

    if args.image_dpi < 300 or args.image_dpi > 600:
        print("--image-dpi must be between 300 and 600", file=sys.stderr)
        return 2

    if args.mode == "rich":
        assets_dir = None
        if not args.no_images:
            if args.images_dir is None:
                assets_dir = output_path.parent / f"{pdf_path.stem}.assets"
            else:
                assets_dir = args.images_dir.expanduser().resolve()
        try:
            output = extract_with_pymupdf_rich(
                pdf_path=pdf_path,
                markdown_path=output_path,
                assets_dir=assets_dir,
                image_dpi=args.image_dpi,
            )
        except Exception as exc:  # noqa: BLE001 - report rich extraction failures clearly.
            print(f"Rich extraction failed: {exc}", file=sys.stderr)
            return 1
    else:
        extractor_name, pages = extract_plain_pages(pdf_path)
        output = render_plain_markdown(pdf_path, extractor_name, pages)

    output_path.write_text(output, encoding="utf-8")
    print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
