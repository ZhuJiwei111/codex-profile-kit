#!/usr/bin/env python3
"""Validate a bilingual paper translation against its rich extraction.

Checks structural completeness, source-blockquote fidelity, citations, visual
assets, table/figure numbering, Unicode corruption, and suspicious summaries.
The validator is conservative: errors always fail; warnings fail with --strict.
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path


CITATION_PATTERNS = (
    re.compile(r"\[[0-9]+(?:\s*[,;–-]\s*[0-9]+)*\]"),
    re.compile(r"\([A-Z][A-Za-z-]+ et al\.,? \d{4}[a-z]?(?:;[^)]*)?\)"),
    re.compile(r"\b[A-Z][A-Za-z-]+ et al\. \(\d{4}[a-z]?\)"),
    re.compile(r"\\cite\{[^}]+\}"),
)
ASSET_RE = re.compile(r"!\[[^]]*\]\(([^)]+)\)")
FIGURE_LINK_RE = re.compile(r"(?:^|/)figure-(\d+)-page-\d+\.png$", re.I)
TABLE_LINK_RE = re.compile(r"(?:^|/)table-(\d+)-page-\d+\.png$", re.I)
SOURCE_FIGURE_RE = re.compile(r"^(?:Figure|Fig\.)\s*(\d+)\s*[:.]", re.I)
SOURCE_TABLE_RE = re.compile(r"^(?:Table|Tab\.)\s*(\d+)\s*[:.]", re.I)
FINAL_FIGURE_RE = re.compile(r"^>\s*(?:Figure|Fig\.)\s*(\d+)\s*[:.]", re.I)
FINAL_TABLE_RE = re.compile(r"^>\s*(?:Table|Tab\.)\s*(\d+)\s*[:.]", re.I)
FINAL_ZH_FIGURE_RE = re.compile(r"^图\s*(\d+)\s*[：:]")
FINAL_ZH_TABLE_RE = re.compile(r"^表\s*(\d+)\s*[：:]")
SUMMARY_RE = re.compile(r"(?:列结构分散|无法可靠重建|保留关键(?:数值|结论)|此处保留关键)")


@dataclass
class Finding:
    level: str
    message: str


def strip_markdown(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[*_`$]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", strip_markdown(text).lower())


def citation_count(text: str) -> int:
    return sum(len(pattern.findall(text)) for pattern in CITATION_PATTERNS)


def source_blocks(text: str) -> list[str]:
    text = re.split(
        r"^#{1,3}\s+\**(?:References|Bibliography)\b",
        text,
        maxsplit=1,
        flags=re.I | re.M,
    )[0]
    blocks = []
    for block in re.split(r"\n\s*\n", text):
        block = block.replace("\n", " ").strip()
        if len(block) < 80 or block.startswith(("#", "<!--", "![", "> This", "Extractor:")):
            continue
        if len(tokens(block)) >= 12:
            blocks.append(block)
    return blocks


def best_source_match(quote: str, blocks: list[str]) -> tuple[float, str]:
    q_tokens = set(tokens(quote))
    best_score = 0.0
    best_block = ""
    for block in blocks:
        b_tokens = set(tokens(block))
        score = len(q_tokens & b_tokens) / max(1, len(q_tokens | b_tokens))
        if score > best_score:
            best_score = score
            best_block = block
    return best_score, best_block


def numbered_set(pattern: re.Pattern[str], lines: list[str]) -> set[int]:
    values = set()
    for line in lines:
        match = pattern.match(strip_markdown(line))
        if match:
            values.add(int(match.group(1)))
    return values


def next_nonempty_index(lines: list[str], start: int) -> int | None:
    for index in range(start, len(lines)):
        if lines[index].strip():
            return index
    return None


def asset_number(line: str, pattern: re.Pattern[str]) -> int | None:
    match = ASSET_RE.search(line)
    if not match:
        return None
    number = pattern.search(match.group(1))
    return int(number.group(1)) if number else None


def validate_visual_placement(source_lines: list[str], final_lines: list[str]) -> list[Finding]:
    findings: list[Finding] = []
    source_errors = []
    final_errors = []
    duplicate_markdown_tables = []

    # Intermediate extraction: figure screenshot -> English caption;
    # English table caption -> table screenshot.
    for index, line in enumerate(source_lines):
        figure_number = asset_number(line, FIGURE_LINK_RE)
        if figure_number is not None:
            caption_index = next_nonempty_index(source_lines, index + 1)
            caption = source_lines[caption_index] if caption_index is not None else ""
            match = SOURCE_FIGURE_RE.match(strip_markdown(caption))
            if not match or int(match.group(1)) != figure_number:
                source_errors.append(("figure", figure_number, index + 1))
        table_match = SOURCE_TABLE_RE.match(strip_markdown(line))
        if table_match:
            table_number = int(table_match.group(1))
            asset_index = next_nonempty_index(source_lines, index + 1)
            asset_line = source_lines[asset_index] if asset_index is not None else ""
            if asset_number(asset_line, TABLE_LINK_RE) != table_number:
                source_errors.append(("table", table_number, index + 1))

    # Final bilingual Markdown:
    # figure screenshot -> English caption -> Chinese caption;
    # English table caption -> Chinese caption -> table screenshot.
    for index, line in enumerate(final_lines):
        figure_number = asset_number(line, FIGURE_LINK_RE)
        if figure_number is not None:
            en_index = next_nonempty_index(final_lines, index + 1)
            zh_index = next_nonempty_index(final_lines, en_index + 1) if en_index is not None else None
            en_line = final_lines[en_index] if en_index is not None else ""
            zh_line = final_lines[zh_index] if zh_index is not None else ""
            en_match = FINAL_FIGURE_RE.match(strip_markdown(en_line))
            zh_match = FINAL_ZH_FIGURE_RE.match(strip_markdown(zh_line))
            if (
                not en_match
                or int(en_match.group(1)) != figure_number
                or not zh_match
                or int(zh_match.group(1)) != figure_number
            ):
                final_errors.append(("figure", figure_number, index + 1))

        table_match = FINAL_TABLE_RE.match(strip_markdown(line))
        if table_match:
            table_number = int(table_match.group(1))
            zh_index = next_nonempty_index(final_lines, index + 1)
            asset_index = next_nonempty_index(final_lines, zh_index + 1) if zh_index is not None else None
            zh_line = final_lines[zh_index] if zh_index is not None else ""
            asset_line = final_lines[asset_index] if asset_index is not None else ""
            zh_match = FINAL_ZH_TABLE_RE.match(strip_markdown(zh_line))
            if (
                not zh_match
                or int(zh_match.group(1)) != table_number
                or asset_number(asset_line, TABLE_LINK_RE) != table_number
            ):
                final_errors.append(("table", table_number, index + 1))
            else:
                grid_index = next_nonempty_index(final_lines, asset_index + 1)
                if grid_index is not None and final_lines[grid_index].lstrip().startswith("|"):
                    duplicate_markdown_tables.append((table_number, grid_index + 1))

    if source_errors:
        findings.append(Finding("ERROR", f"提取稿图表与 caption 邻接/顺序错误：{source_errors[:20]}"))
    if final_errors:
        findings.append(Finding("ERROR", f"译稿图表与双语 caption 邻接/顺序错误：{final_errors[:20]}"))
    if duplicate_markdown_tables:
        findings.append(
            Finding(
                "WARN",
                "截图后存在重复 Markdown 表格；仅在用户明确要求机器可读数据时保留："
                f"{duplicate_markdown_tables[:20]}",
            )
        )
    return findings


def validate(source_path: Path, final_path: Path) -> list[Finding]:
    findings: list[Finding] = []
    source = source_path.read_text(encoding="utf-8")
    final = final_path.read_text(encoding="utf-8")
    source_lines = source.splitlines()
    final_lines = final.splitlines()

    if "\ufffd" in final:
        findings.append(Finding("ERROR", f"译稿包含 {final.count(chr(0xFFFD))} 个 U+FFFD 替换字符"))

    unexpected_controls = []
    for index, char in enumerate(final):
        if unicodedata.category(char) == "Cf" and char != "\u200b":
            unexpected_controls.append((index, f"U+{ord(char):04X}"))
    if unexpected_controls:
        findings.append(Finding("ERROR", f"译稿包含异常格式控制字符：{unexpected_controls[:5]}"))

    h1 = [line for line in final_lines if line.startswith("# ")]
    if len(h1) != 1:
        findings.append(Finding("ERROR", f"译稿应恰有一个 H1 标题，当前为 {len(h1)} 个"))
    if re.search(r"^#{1,6}\s+(?:References|Bibliography|参考文献)\b", final, re.I | re.M):
        findings.append(Finding("ERROR", "译稿包含默认应省略的参考文献章节"))

    source_figures = numbered_set(SOURCE_FIGURE_RE, source_lines)
    source_tables = numbered_set(SOURCE_TABLE_RE, source_lines)
    for match in ASSET_RE.finditer(source):
        figure_match = FIGURE_LINK_RE.search(match.group(1))
        table_match = TABLE_LINK_RE.search(match.group(1))
        if figure_match:
            source_figures.add(int(figure_match.group(1)))
        if table_match:
            source_tables.add(int(table_match.group(1)))
    final_figures = numbered_set(FINAL_FIGURE_RE, final_lines)
    final_tables = numbered_set(FINAL_TABLE_RE, final_lines)

    linked_figures: set[int] = set()
    linked_tables: set[int] = set()
    missing_assets = []
    duplicate_assets = []
    seen_paths: set[str] = set()
    for match in ASSET_RE.finditer(final):
        relative = match.group(1)
        asset = (final_path.parent / relative).resolve()
        if not asset.exists():
            missing_assets.append(relative)
        if relative in seen_paths:
            duplicate_assets.append(relative)
        seen_paths.add(relative)
        figure_match = FIGURE_LINK_RE.search(relative)
        table_match = TABLE_LINK_RE.search(relative)
        if figure_match:
            linked_figures.add(int(figure_match.group(1)))
        if table_match:
            linked_tables.add(int(table_match.group(1)))

    if missing_assets:
        findings.append(Finding("ERROR", f"缺失视觉资源：{missing_assets[:10]}"))
    if duplicate_assets:
        findings.append(Finding("WARN", f"重复引用视觉资源：{duplicate_assets[:10]}"))

    for label, expected, captions, linked in (
        ("图", source_figures, final_figures, linked_figures),
        ("表", source_tables, final_tables, linked_tables),
    ):
        if expected != captions:
            findings.append(Finding("ERROR", f"{label}题编号不一致：原文={sorted(expected)}，译稿={sorted(captions)}"))
        if expected != linked:
            findings.append(Finding("ERROR", f"{label}资源编号不一致：原文={sorted(expected)}，资源={sorted(linked)}"))

    findings.extend(validate_visual_placement(source_lines, final_lines))

    blocks = source_blocks(source)
    quotes = [(index + 1, line[2:].strip()) for index, line in enumerate(final_lines) if line.startswith("> ")]
    low_fidelity = []
    missing_citations = []
    for line_number, quote in quotes:
        if len(tokens(quote)) < 15 or SOURCE_FIGURE_RE.match(strip_markdown(quote)) or SOURCE_TABLE_RE.match(strip_markdown(quote)):
            continue
        score, block = best_source_match(quote, blocks)
        if not block:
            continue
        quote_tokens = tokens(quote)
        block_tokens = tokens(block)
        recall = len(set(quote_tokens) & set(block_tokens)) / max(1, len(set(block_tokens)))
        if score >= 0.35 and recall < 0.68 and len(block_tokens) > len(quote_tokens) * 1.25:
            low_fidelity.append((line_number, round(recall, 2), quote[:70]))
        source_citations = citation_count(block)
        quote_citations = citation_count(quote)
        if score >= 0.45 and source_citations > quote_citations:
            missing_citations.append((line_number, source_citations, quote_citations))

    if low_fidelity:
        findings.append(Finding("WARN", f"英文引用块可能被删减/改写：{low_fidelity[:12]}"))
    if missing_citations:
        findings.append(Finding("WARN", f"英文引用块疑似遗漏原文引用：{missing_citations[:12]}"))

    chinese_citations = []
    in_code = False
    for index, line in enumerate(final_lines, start=1):
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code or not line.strip() or line.startswith((">", "#", "!", "|")):
            continue
        line_without_math = re.sub(r"\$[^$]+\$", "", line)
        if citation_count(line_without_math):
            chinese_citations.append(index)
    if chinese_citations:
        findings.append(Finding("WARN", f"中文段落疑似残留引用标记，行号：{chinese_citations[:20]}"))

    summaries = [
        (index + 1, line[:90])
        for index, line in enumerate(final_lines)
        if SUMMARY_RE.search(line)
    ]
    if summaries:
        findings.append(
            Finding(
                "ERROR",
                "发现不应出现在段落对齐译稿中的助手表格概括/提取说明："
                f"{summaries[:12]}",
            )
        )

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Rich extracted Markdown")
    parser.add_argument("translation", type=Path, help="Final bilingual Markdown")
    parser.add_argument("--strict", action="store_true", help="Fail on warnings as well as errors")
    args = parser.parse_args()

    for path in (args.source, args.translation):
        if not path.exists():
            print(f"ERROR: file not found: {path}", file=sys.stderr)
            return 2

    findings = validate(args.source.resolve(), args.translation.resolve())
    if not findings:
        print("OK: no structural or fidelity issues found")
        return 0

    for finding in findings:
        print(f"{finding.level}: {finding.message}")
    errors = any(finding.level == "ERROR" for finding in findings)
    warnings = any(finding.level == "WARN" for finding in findings)
    return 1 if errors or (args.strict and warnings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
