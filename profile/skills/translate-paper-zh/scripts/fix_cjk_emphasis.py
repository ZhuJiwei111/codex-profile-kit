#!/usr/bin/env python3
"""Fix Markdown emphasis that fails to render because a *paired* emphasis
span begins or ends with punctuation on its inner side.

Root cause (verified against markdown-it, the parser used by
markdown-preview-enhanced)
--------------------------------------------------------------------------
CommonMark's flanking-delimiter rule cares about *punctuation*, not CJK
letters. A paired emphasis span is only rejected when its content begins or
ends with a *punctuation* character:

- Content ends with punctuation, e.g. ``**快速模式（Fast Mode，MTP）**``
  (ends with full-width ``）``) -> closing ``**`` is not right-flanking ->
  the whole span renders literally with visible asterisks.
- Content starts with punctuation, e.g. ``**（备注）说明**`` -> opening ``**``
  is not left-flanking.

Content that starts/ends with a CJK *letter* (e.g. ``**快速模式**``) renders
fine and needs no fix.

Fix
---
For each *paired* emphasis span, insert an invisible zero-width space
``U+200B`` on the INNER side of any delimiter whose adjacent content
character is punctuation:

- ``**（备注）说明**``       -> ``**​（备注）说明**``      (opening inner ZWSP)
- ``**快速模式（MTP）**``    -> ``**快速模式（MTP）​**``   (closing inner ZWSP)

The ZWSP counts as an ordinary character to the parser, restoring the
flanking condition, while staying invisible and virtually copy-safe.

Why paired matching
-------------------
Only balanced ``**...**`` / ``*...*`` spans are touched. Isolated asterisks
used as footnote markers or table notes (e.g. ``* 表示复现结果`` or a line
starting with ``*（说明...``) are NOT paired emphasis and are left untouched,
avoiding false positives. List markers (``* item``) and thematic breaks
(``***``) are likewise never matched.

The transform is idempotent: a delimiter already carrying an inner ZWSP does
not match again.

Usage
-----
    python fix_cjk_emphasis.py paper.zh.md            # fix in place
    python fix_cjk_emphasis.py paper.zh.md --check     # report only, exit 1 if issues
    python fix_cjk_emphasis.py paper.zh.md -o out.md   # write to a different file
"""

from __future__ import annotations

import argparse
import re
import sys

ZWSP = "\u200b"

# Punctuation that triggers the flanking failure when it sits on the inner
# side of an emphasis delimiter (ASCII + CJK/full-width/general punctuation).
_PUNCT_CLASS = (
    r"!-/:-@\[-`{-~"          # ASCII punctuation
    r"\u2000-\u206f"          # General Punctuation (… — ‘’ “”)
    r"\u3000-\u303f"          # CJK Symbols and Punctuation （、。「」）
    r"\uff00-\uffef"          # Halfwidth and Fullwidth Forms （（）！？：，）
)
_PUNCT = re.compile("[" + _PUNCT_CLASS + "]")

# Paired emphasis spans. Bold first (``**...**``), then italic (``*...*``).
# Content is non-greedy and may not contain the delimiter run itself.
# We match on a per-line basis (DOTALL off) since emphasis does not span
# blank-line-separated blocks in practice for this workflow.
_BOLD = re.compile(r"(?<!\*)\*\*(?!\*)(.+?)(?<!\*)\*\*(?!\*)")
_ITALIC = re.compile(r"(?<![\*\w])\*(?!\*)([^*\n]+?)\*(?!\*)")


def _fix_span(inner: str) -> tuple[str, int]:
    """Add inner ZWSP to a span's content where it starts/ends with punct."""
    n = 0
    if inner and _PUNCT.match(inner[0]) and not inner.startswith(ZWSP):
        inner = ZWSP + inner
        n += 1
    if inner and _PUNCT.match(inner[-1]) and not inner.endswith(ZWSP):
        inner = inner + ZWSP
        n += 1
    return inner, n


def fix_text(text: str) -> tuple[str, int]:
    total = 0

    def _bold_sub(m: "re.Match[str]") -> str:
        nonlocal total
        inner, n = _fix_span(m.group(1))
        total += n
        return "**" + inner + "**"

    def _italic_sub(m: "re.Match[str]") -> str:
        nonlocal total
        inner, n = _fix_span(m.group(1))
        total += n
        return "*" + inner + "*"

    text = _BOLD.sub(_bold_sub, text)
    text = _ITALIC.sub(_italic_sub, text)
    return text, total


def count_issues(text: str) -> int:
    """Count paired spans still starting/ending with punctuation, no ZWSP."""
    n = 0
    for pat in (_BOLD, _ITALIC):
        for m in pat.finditer(text):
            inner = m.group(1)
            if inner and _PUNCT.match(inner[0]) and not inner.startswith(ZWSP):
                n += 1
            if inner and _PUNCT.match(inner[-1]) and not inner.endswith(ZWSP):
                n += 1
    return n


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Insert U+200B on the inner side of paired Markdown "
        "emphasis delimiters whose content starts/ends with punctuation, so "
        "bold/italic renders in markdown-it / markdown-preview-enhanced."
    )
    parser.add_argument("path", help="Markdown file to fix (usually *.zh.md).")
    parser.add_argument(
        "-o", "--output", help="Write result here instead of editing in place."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report remaining issues without modifying the file. Exit code 1 "
        "if any issue is found.",
    )
    args = parser.parse_args(argv)

    try:
        with open(args.path, encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        print(f"error: cannot read {args.path}: {exc}", file=sys.stderr)
        return 2

    if args.check:
        n = count_issues(text)
        if n:
            print(
                f"{args.path}: {n} paired emphasis span(s) start/end with "
                "punctuation without an inner ZWSP"
            )
            return 1
        print(f"{args.path}: OK (no punctuation-adjacent emphasis issues)")
        return 0

    fixed, n = fix_text(text)
    out_path = args.output or args.path
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(fixed)

    remaining = count_issues(fixed)
    print(f"inserted {n} ZWSP; remaining issues: {remaining}; wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
