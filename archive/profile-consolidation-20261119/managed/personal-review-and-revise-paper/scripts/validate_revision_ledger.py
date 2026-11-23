#!/usr/bin/env python3
"""Mechanical validator for personal-review-and-revise-paper Markdown ledgers."""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


REQUIRED_FRONTMATTER = (
    "ledger_schema",
    "canonical_entrypoint",
    "canonical_source_type",
    "target_venue",
    "paper_language",
    "interaction_language",
    "build_policy",
    "approval_policy",
    "active_package",
    "workflow_mode",
)

REQUIRED_SECTIONS = (
    "原文英文",
    "候选英文",
    "原文中文",
    "候选中文",
    "作者决定",
    "应用与验证记录",
)
LEGACY_SECTIONS = REQUIRED_SECTIONS[:4] + ("修改判断",) + REQUIRED_SECTIONS[4:]
SCHEMA_SECTIONS = {
    "review-and-revise-paper/v1": LEGACY_SECTIONS,
    "review-and-revise-paper/v2": REQUIRED_SECTIONS,
}

VALID_STATUSES = {
    "drafting",
    "pending_author_decision",
    "approved",
    "applied_source_verified",
    "final_render_verified",
    "author_locked_risk",
    "deferred",
    "closed_without_change",
}
ACTIVE_STATUSES = {"drafting", "pending_author_decision", "approved"}
ALLOWED_COLORS = {"c62828", "1565c0"}
PACKAGE_RE = re.compile(r"^###\s+(PKG-\d{3,})\s+—\s+(.+?)\s*$", re.MULTILINE)
PACKAGE_HEADING_RE = re.compile(r"^###\s+PKG-[^\n]+$", re.MULTILINE)
SECTION_RE = re.compile(r"^####\s+(\d+)\.\s+(.+?)\s*$", re.MULTILINE)
STATUS_RE = re.compile(r"^-\s*状态[：:]\s*`([^`]+)`\s*$", re.MULTILINE)
RATIONALE_RE = re.compile(
    r"^> \*\*(?:修改|保留)理由(?:（[^）\n]+）)?[：:]\*\*[ \t]*(?P<body>[^\n]*)$",
    re.MULTILINE,
)


@dataclass(frozen=True)
class Package:
    package_id: str
    title: str
    body: str
    status: str | None


def parse_frontmatter(text: str) -> tuple[dict[str, str], str, list[str]]:
    errors: list[str] = []
    if not text.startswith("---\n"):
        return {}, text, ["ledger must start with YAML frontmatter"]
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}, text, ["frontmatter closing delimiter is missing"]
    raw = text[4:end]
    fields: dict[str, str] = {}
    for lineno, line in enumerate(raw.splitlines(), start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.match(r"^([a-z_]+):\s*(.*?)\s*$", line)
        if not match:
            errors.append(f"frontmatter line {lineno} is not a simple key/value field")
            continue
        key, value = match.groups()
        if key in fields:
            errors.append(f"frontmatter field is duplicated: {key}")
        fields[key] = value.strip('"\'')
    return fields, text[end + 5 :], errors


def parse_packages(body: str) -> tuple[list[Package], list[str]]:
    matches = list(PACKAGE_RE.finditer(body))
    errors: list[str] = []
    raw_headings = PACKAGE_HEADING_RE.findall(body)
    if len(raw_headings) != len(matches):
        errors.append("one or more PKG headings do not match '### PKG-NNN — title'")
    packages: list[Package] = []
    seen: set[str] = set()
    for index, match in enumerate(matches):
        package_id, title = match.groups()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        package_body = body[start:end]
        status_match = STATUS_RE.search(package_body)
        status = status_match.group(1) if status_match else None
        if package_id in seen:
            errors.append(f"duplicate package id: {package_id}")
        seen.add(package_id)
        packages.append(Package(package_id, title, package_body, status))
    return packages, errors


def split_sections(
    package: Package, required: tuple[str, ...]
) -> tuple[dict[str, str], list[str]]:
    matches = list(SECTION_RE.finditer(package.body))
    errors: list[str] = []
    names = [match.group(2).strip() for match in matches]
    numbers = [int(match.group(1)) for match in matches]
    if names != list(required) or numbers != list(range(1, len(required) + 1)):
        errors.append(
            f"{package.package_id} sections must be exactly: "
            + " | ".join(required)
        )
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        name = match.group(2).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(package.body)
        sections[name] = package.body[start:end].strip()
    return sections, errors


def meaningful(text: str) -> bool:
    stripped = re.sub(r"<[^>]+>", "", text).strip()
    return bool(stripped) and "TODO" not in stripped


def validate_text(text: str, source: str = "<memory>") -> list[str]:
    fields, body, errors = parse_frontmatter(text)
    for field in REQUIRED_FRONTMATTER:
        if not fields.get(field):
            errors.append(f"missing or empty frontmatter field: {field}")
        elif fields[field].strip().upper() == "TODO":
            errors.append(f"frontmatter field still contains TODO: {field}")

    schema = fields.get("ledger_schema")
    if schema is not None and schema not in SCHEMA_SECTIONS:
        errors.append("ledger_schema must be review-and-revise-paper/v1 or v2")
    required = SCHEMA_SECTIONS.get(schema, REQUIRED_SECTIONS)
    if fields.get("canonical_source_type") not in {None, "latex", "markdown"}:
        errors.append("canonical_source_type must be latex or markdown")
    if fields.get("build_policy") not in {None, "explicit_or_final_freeze"}:
        errors.append("build_policy must be explicit_or_final_freeze")
    if fields.get("approval_policy") not in {None, "active_package_only", "recorded_scope"}:
        errors.append("approval_policy must be active_package_only or recorded_scope")
    if fields.get("workflow_mode") not in {
        None,
        "one_shot",
        "serial_review",
        "apply_approved",
        "freeze_verify",
    }:
        errors.append("workflow_mode is invalid")

    packages, package_errors = parse_packages(body)
    errors.extend(package_errors)
    active: list[Package] = []

    for package in packages:
        if package.status not in VALID_STATUSES:
            errors.append(
                f"{package.package_id} has missing or invalid status: {package.status!r}"
            )
        elif package.status in ACTIVE_STATUSES:
            active.append(package)

        sections, section_errors = split_sections(package, required)
        errors.extend(section_errors)
        for section in required:
            if section not in sections or not sections[section].strip():
                errors.append(f"{package.package_id} section is empty: {section}")

        if package.status in {
            "pending_author_decision", "approved", "applied_source_verified",
            "final_render_verified",
        }:
            proposal_sections = required[:5] if schema == "review-and-revise-paper/v1" else required[:4]
            for section in proposal_sections:
                if not meaningful(sections.get(section, "")):
                    errors.append(f"{package.package_id} proposal is incomplete: {section}")

        rationales = [
            match
            for name in ("原文中文", "候选中文")
            for match in RATIONALE_RE.finditer(sections.get(name, ""))
        ]
        if schema == "review-and-revise-paper/v2" and package.status in {
            "pending_author_decision", "approved", "applied_source_verified",
            "final_render_verified", "closed_without_change", "author_locked_risk",
        }:
            if not rationales or any(not meaningful(m.group("body")) for m in rationales):
                errors.append(f"{package.package_id} lacks a complete reason note in the Chinese comparison")

        for original_name in ("原文英文", "原文中文"):
            if "color:#1565c0" in sections.get(original_name, ""):
                errors.append(f"{package.package_id} {original_name} contains proposed blue")
        for proposed_name in ("候选英文", "候选中文"):
            if "color:#c62828" in sections.get(proposed_name, ""):
                errors.append(f"{package.package_id} {proposed_name} contains original red")

        if package.status in {
            "approved", "applied_source_verified", "final_render_verified",
            "closed_without_change", "author_locked_risk",
        }:
            if not meaningful(sections.get("作者决定", "")) or "待决定" in sections.get(
                "作者决定", ""
            ):
                errors.append(f"{package.package_id} decided status lacks an author decision")
        if package.status in {"applied_source_verified", "final_render_verified"}:
            application = sections.get("应用与验证记录", "")
            if not meaningful(application) or "未应用" in application:
                errors.append(f"{package.package_id} applied status lacks an application record")
        if package.status == "final_render_verified":
            application = sections.get("应用与验证记录", "").lower()
            if "render" not in application and "构建" not in application:
                errors.append(f"{package.package_id} final status lacks render/build evidence")
        if package.status == "author_locked_risk":
            judgment = (
                sections.get("修改判断", "")
                if schema == "review-and-revise-paper/v1"
                else "\n".join(m.group(0) for m in rationales)
            )
            if "作者锁定风险" not in judgment:
                errors.append(f"{package.package_id} locked-risk status lacks matching verdict")

    if len(active) > 1:
        errors.append("more than one active package: " + ", ".join(p.package_id for p in active))

    active_field = fields.get("active_package")
    expected_active = active[0].package_id if len(active) == 1 else "none"
    if active_field and active_field != expected_active:
        errors.append(
            f"frontmatter active_package is {active_field!r}, expected {expected_active!r}"
        )

    opening_spans = len(re.findall(r"<span\b", text, flags=re.IGNORECASE))
    closing_spans = len(re.findall(r"</span>", text, flags=re.IGNORECASE))
    if opening_spans != closing_spans:
        errors.append(
            f"unbalanced span tags: {opening_spans} opening vs {closing_spans} closing"
        )
    for color in re.findall(r"color\s*:\s*#([0-9a-fA-F]{6})", text):
        if color.lower() not in ALLOWED_COLORS:
            errors.append(f"unsupported color #{color}; only red and blue are allowed")

    return [f"{source}: {error}" for error in errors]


def valid_fixture() -> str:
    sections = """
#### 1. 原文英文

The model has <span style="color:#c62828">strong transferability</span>.

#### 2. 候选英文

The model has <span style="color:#1565c0">higher MCC on the evaluated tasks</span>.

#### 3. 原文中文

该模型具有<span style="color:#c62828">很强的可迁移性</span>。

#### 4. 候选中文

该模型<span style="color:#1565c0">在所评估任务上取得更高 MCC</span>。

> **修改理由（本句，建议修改）：** Table 2 支持已评估任务上的 MCC 优势，原句会被理解为未经验证的普遍可迁移性；候选保留有证据支持的定量贡献。

#### 5. 作者决定

- 决定：`待决定`

#### 6. 应用与验证记录

- application：`未应用`
""".strip()
    return f"""---
ledger_schema: review-and-revise-paper/v2
canonical_entrypoint: paper.tex
canonical_source_type: latex
target_venue: Example Journal
paper_language: en
interaction_language: zh-CN
build_policy: explicit_or_final_freeze
approval_policy: active_package_only
active_package: PKG-001
workflow_mode: one_shot
---

# Ledger

### PKG-001 — Claim boundary

- 状态：`pending_author_decision`

{sections}
"""


def run_self_test() -> int:
    cases: list[tuple[str, str, bool]] = []
    valid = valid_fixture()
    package_block = valid[valid.index("### PKG-001") :]
    cases.append(("valid replacement", valid, True))
    reason = RATIONALE_RE.search(valid).group(0)
    cases.append(("missing local reason", valid.replace(reason, ""), False))
    cases.append((
        "reason only in English comparison",
        valid.replace(reason, "").replace("#### 2. 候选英文", reason + "\n\n#### 2. 候选英文"),
        False,
    ))
    # A note in the author-decision record cannot replace a Chinese comparison note.
    misplaced = valid.replace(reason, "").replace("- 决定：`待决定`", reason + "\n\n- 决定：`待决定`")
    cases.append(("reason only in decision record", misplaced, False))
    cases.append(("unfinished local reason", valid.replace(reason, '> **修改理由（本句，建议修改）：** TODO'), False))
    cases.append(("retention reason", valid.replace("修改理由", "保留理由"), True))
    cases.append(("stale section numbering", valid.replace("#### 5. 作者决定", "#### 6. 作者决定"), False))
    legacy = valid.replace("review-and-revise-paper/v2", "review-and-revise-paper/v1").replace(
        reason, "#### 5. 修改判断\n\n- verdict：`建议修改`\n- direct evidence：Table 2 支持已评估任务的定量优势。"
    ).replace("#### 5. 作者决定", "#### 6. 作者决定").replace("#### 6. 应用与验证记录", "#### 7. 应用与验证记录")
    cases.append(("legacy v1 remains valid", legacy, True))
    cases.append(("v2 rejects standalone judgment", legacy.replace("review-and-revise-paper/v1", "review-and-revise-paper/v2"), False))
    locked = valid.replace("pending_author_decision", "author_locked_risk").replace(
        "active_package: PKG-001", "active_package: none"
    ).replace("- 决定：`待决定`", "- 决定：`作者明确保留已知矛盾`\n- verdict：作者锁定风险")
    cases.append(("locked risk needs local verdict", locked, False))
    cases.append(("locked risk with local verdict", locked.replace("本句，建议修改", "本句，作者锁定风险"), True))
    insertion = valid.replace(
        'The model has <span style="color:#c62828">strong transferability</span>.',
        "*【原文在此处没有对应句子。】*",
    ).replace(
        'The model has <span style="color:#1565c0">higher MCC on the evaluated tasks</span>.',
        '<span style="color:#1565c0">We additionally report the held-out test MCC.</span>',
    )
    cases.append(("valid pure insertion", insertion, True))
    deletion = valid.replace(
        'The model has <span style="color:#1565c0">higher MCC on the evaluated tasks</span>.',
        "The model is evaluated on the reported tasks.",
    )
    cases.append(("valid deletion", deletion, True))
    table = valid.replace(
        'The model has <span style="color:#c62828">strong transferability</span>.',
        '| Model | Score |\n|---|---:|\n| SPACE | <span style="color:#c62828">\\textbf{0.80}</span> |',
    ).replace(
        'The model has <span style="color:#1565c0">higher MCC on the evaluated tasks</span>.',
        '| Model | Score |\n|---|---:|\n| SPACE | <span style="color:#1565c0">\\underline{0.80}</span> |',
    )
    cases.append(("valid table winner change", table, True))
    cases.append(("unclosed span", valid.replace("</span>", "", 1), False))
    cases.append(("green reference", valid.replace("#1565c0", "#2e7d32", 1), False))
    cases.append(
        (
            "blue in original",
            valid.replace("#c62828", "#1565c0", 1),
            False,
        )
    )
    cases.append(
        (
            "red in candidate",
            valid.replace("#1565c0", "#c62828", 1),
            False,
        )
    )
    duplicate = valid + "\n" + package_block
    cases.append(("duplicate package", duplicate, False))
    second_active = valid + "\n" + package_block.replace(
        "PKG-001", "PKG-002"
    ).replace(
        "pending_author_decision", "drafting"
    )
    cases.append(("multiple active packages", second_active, False))
    approved_without_decision = valid.replace(
        "pending_author_decision", "approved"
    )
    cases.append(("approved without decision", approved_without_decision, False))
    malformed_heading = valid.replace("### PKG-001 —", "### PKG-1 -", 1)
    cases.append(("malformed package heading", malformed_heading, False))

    deferred = valid.replace("pending_author_decision", "deferred").replace(
        "active_package: PKG-001", "active_package: none"
    )
    cases.append(("deferred package is inactive", deferred, True))
    next_package = package_block.replace("PKG-001", "PKG-002")
    cases.append((
        "deferred package alongside next proposal",
        deferred.replace("active_package: none", "active_package: PKG-002")
        + "\n" + next_package,
        True,
    ))
    cases.append((
        "deferred package cannot own active pointer",
        deferred.replace("active_package: none", "active_package: PKG-001"),
        False,
    ))
    closed = deferred.replace("deferred", "closed_without_change").replace(
        "- 决定：`待决定`", "- 决定：`作者确认保留原文`"
    ).replace("- application：`未应用`", "- application：`未应用（保留原文）`")
    cases.append(("author accepts no change", closed, True))
    cases.append((
        "no-change closure needs author decision",
        closed.replace("作者确认保留原文", "待决定"),
        False,
    ))
    cases.append((
        "recorded explicit scope policy",
        valid.replace("approval_policy: active_package_only", "approval_policy: recorded_scope"),
        True,
    ))
    incomplete = valid.replace(
        'The model has <span style="color:#1565c0">higher MCC on the evaluated tasks</span>.',
        "TODO",
    )
    cases.append(("pending proposal cannot contain unfinished candidate", incomplete, False))
    cases.append((
        "draft may contain unfinished candidate",
        incomplete.replace("pending_author_decision", "drafting"),
        True,
    ))

    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="review-ledger-selftest-") as tmp:
        base = Path(tmp)
        for index, (name, content, should_pass) in enumerate(cases, start=1):
            path = base / f"case-{index}.md"
            path.write_text(content, encoding="utf-8")
            passed = not validate_text(content, str(path))
            if passed != should_pass:
                failures.append(f"{name}: expected pass={should_pass}, got pass={passed}")
    if failures:
        for failure in failures:
            print(f"SELF-TEST FAIL: {failure}", file=sys.stderr)
        return 1
    print(f"SELF-TEST PASS: {len(cases)} cases")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if args.ledger is None:
        parser.error("ledger path is required unless --self-test is used")
    try:
        text = args.ledger.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        print(f"{args.ledger}: cannot read ledger: {exc}", file=sys.stderr)
        return 2
    errors = validate_text(text, str(args.ledger))
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"PASS: {args.ledger}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
