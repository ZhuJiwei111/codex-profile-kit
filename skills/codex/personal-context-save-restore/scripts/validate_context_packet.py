#!/usr/bin/env python3
"""Validate one explicit immutable context packet without modifying state."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import stat
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


OWNER = "personal-context-save-restore"
RECORD_TYPE = "context-packet"
SCHEMA_VERSION = 1
PACKET_ID_RE = re.compile(r"ctx-\d{8}t\d{6}z-[a-z0-9][a-z0-9-]{0,63}")
DERIVED_FROM_RE = re.compile(
    r"packet:(ctx-\d{8}t\d{6}z-[a-z0-9][a-z0-9-]{0,63})"
    r"@sha256:([0-9a-f]{64})"
)
SHA256_RE = re.compile(r"[0-9a-f]{64}")
SOURCE_REVISION_RE = re.compile(r"git:[0-9a-f]{7,64}")
DERIVATION_REASONS = {"correction", "rebind", "refresh"}
REQUIRED_FIELDS = {
    "context_owner",
    "schema_version",
    "record_type",
    "packet_id",
    "created_at",
    "canonical_root",
    "evidence_cutoff",
}
OPTIONAL_FIELDS = {
    "source_revision",
    "valid_until",
    "tags",
    "derived_from",
    "derivation_reason",
}
REQUIRED_HEADINGS = (
    "Goal and constraints",
    "Verified snapshot state",
    "Artifacts",
    "Decisions and provenance",
    "Evidence and verification",
    "Unknowns, risks, and blockers",
    "Proposed next actions",
)
STATUS_EXIT = {
    "valid": 0,
    "stale": 1,
    "invalid": 1,
    "invocation_error": 2,
}


def issue(code: str, message: str, severity: str) -> dict[str, str]:
    return {"code": code, "message": message, "severity": severity}


def base_result(packet: Path) -> dict[str, Any]:
    return {
        "status": "valid",
        "packet": str(packet),
        "packet_id": None,
        "sha256": None,
        "canonical_root": None,
        "evidence_cutoff": None,
        "valid_until": None,
        "derived_from": None,
        "issues": [],
    }


def invocation_error(packet: Path, code: str, message: str) -> dict[str, Any]:
    result = base_result(packet)
    result["status"] = "invocation_error"
    result["issues"] = [issue(code, message, "invocation_error")]
    return result


def finalize(result: dict[str, Any]) -> dict[str, Any]:
    severities = {item["severity"] for item in result["issues"]}
    if "invalid" in severities:
        result["status"] = "invalid"
    elif "stale" in severities:
        result["status"] = "stale"
    else:
        result["status"] = "valid"
    return result


def parse_scalar(raw: str) -> Any:
    value = raw.strip()
    if not value:
        raise ValueError("empty value")
    if value[0] in {'"', "'"}:
        parsed = ast.literal_eval(value)
        if not isinstance(parsed, str):
            raise ValueError("quoted value must be a string")
        return parsed
    if value.startswith("["):
        return json.loads(value)
    if value.isdigit():
        return int(value)
    return value


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("packet must start with YAML frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("frontmatter has no closing delimiter") from exc

    fields: dict[str, Any] = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        if line[:1].isspace() or ":" not in line:
            raise ValueError("frontmatter must use flat key-value fields")
        key, raw = line.split(":", 1)
        key = key.strip()
        if not re.fullmatch(r"[a-z][a-z0-9_]*", key):
            raise ValueError("frontmatter contains an invalid key")
        if key in fields:
            raise ValueError("frontmatter contains a duplicate key")
        fields[key] = parse_scalar(raw)
    return fields, "\n".join(lines[end + 1 :])


def parse_utc(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.endswith("Z"):
        return None
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return None
    if parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        return None
    return parsed


def stable_read(path: Path) -> tuple[bytes, os.stat_result] | None:
    before = path.stat(follow_symlinks=False)
    data = path.read_bytes()
    after = path.stat(follow_symlinks=False)
    signature_before = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
    signature_after = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
    if signature_before != signature_after:
        return None
    return data, after


def validate_packet(
    *,
    canonical_root: Path | str,
    packet: Path | str,
    expected_sha256: str | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    packet_path = Path(packet)
    root_path = Path(canonical_root)

    if not root_path.is_absolute():
        return invocation_error(packet_path, "root_not_absolute", "Canonical root must be absolute.")
    try:
        resolved_root = root_path.resolve(strict=True)
    except OSError:
        return invocation_error(packet_path, "root_unavailable", "Canonical root is unavailable.")
    if not resolved_root.is_dir():
        return invocation_error(packet_path, "root_not_directory", "Canonical root is not a directory.")

    if not packet_path.is_absolute():
        return invocation_error(packet_path, "packet_not_absolute", "Packet path must be absolute.")
    if packet_path.is_symlink():
        return invocation_error(packet_path, "packet_symlink", "Packet must not be a symlink.")
    try:
        metadata = packet_path.lstat()
    except OSError:
        return invocation_error(packet_path, "packet_unavailable", "Packet is unavailable.")
    if not stat.S_ISREG(metadata.st_mode):
        return invocation_error(packet_path, "packet_not_regular", "Packet must be a regular file.")
    try:
        resolved_packet = packet_path.resolve(strict=True)
    except OSError:
        return invocation_error(packet_path, "packet_unavailable", "Packet cannot be resolved.")
    if resolved_packet != packet_path:
        return invocation_error(
            packet_path,
            "packet_symlink_component",
            "Packet path must not traverse symlink components or aliases.",
        )
    expected_parent = resolved_root / ".codex" / "context"
    if packet_path.parent != expected_parent:
        return invocation_error(
            packet_path,
            "packet_path_escape",
            "Packet must be a direct child of the canonical context directory.",
        )

    if expected_sha256 is not None and not SHA256_RE.fullmatch(expected_sha256):
        return invocation_error(
            packet_path,
            "invalid_expected_sha256",
            "Expected SHA-256 must contain 64 lowercase hexadecimal characters.",
        )

    try:
        stable = stable_read(packet_path)
    except OSError:
        return invocation_error(packet_path, "packet_read_failed", "Packet could not be read.")
    if stable is None:
        return invocation_error(packet_path, "packet_changed_during_read", "Packet changed during validation.")
    data, _ = stable
    result = base_result(packet_path)
    digest = hashlib.sha256(data).hexdigest()
    result["sha256"] = digest
    if expected_sha256 is not None and digest != expected_sha256:
        result["issues"].append(
            issue("sha256_mismatch", "Packet SHA-256 differs from the expected snapshot.", "stale")
        )

    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        result["issues"].append(issue("invalid_utf8", "Packet must be UTF-8 text.", "invalid"))
        return finalize(result)
    try:
        fields, body = parse_frontmatter(text)
    except (SyntaxError, ValueError):
        result["issues"].append(
            issue("malformed_frontmatter", "Packet frontmatter is malformed.", "invalid")
        )
        return finalize(result)

    unknown = set(fields) - REQUIRED_FIELDS - OPTIONAL_FIELDS
    missing = REQUIRED_FIELDS - set(fields)
    if unknown:
        result["issues"].append(
            issue("unknown_frontmatter_fields", "Packet frontmatter has unsupported fields.", "invalid")
        )
    if missing:
        result["issues"].append(
            issue("missing_frontmatter_fields", "Packet frontmatter is missing required fields.", "invalid")
        )

    if fields.get("context_owner") != OWNER:
        result["issues"].append(issue("invalid_owner", "Packet owner is invalid.", "invalid"))
    if fields.get("schema_version") != SCHEMA_VERSION:
        result["issues"].append(
            issue("unsupported_schema", "Packet schema version is unsupported.", "invalid")
        )
    if fields.get("record_type") != RECORD_TYPE:
        result["issues"].append(
            issue("invalid_record_type", "Packet record type is invalid.", "invalid")
        )

    packet_id = fields.get("packet_id")
    if not isinstance(packet_id, str) or not PACKET_ID_RE.fullmatch(packet_id):
        result["issues"].append(issue("invalid_packet_id", "Packet ID is invalid.", "invalid"))
    else:
        result["packet_id"] = packet_id
        if packet_path.name != f"{packet_id}.md":
            result["issues"].append(
                issue("filename_mismatch", "Packet filename does not match its packet ID.", "invalid")
            )

    created_at = parse_utc(fields.get("created_at"))
    evidence_cutoff = parse_utc(fields.get("evidence_cutoff"))
    if created_at is None:
        result["issues"].append(
            issue("invalid_created_at", "created_at must be an RFC 3339 UTC timestamp.", "invalid")
        )
    if evidence_cutoff is None:
        result["issues"].append(
            issue(
                "invalid_evidence_cutoff",
                "evidence_cutoff must be an RFC 3339 UTC timestamp.",
                "invalid",
            )
        )
    else:
        result["evidence_cutoff"] = fields.get("evidence_cutoff")
    if created_at is not None and evidence_cutoff is not None and evidence_cutoff > created_at:
        result["issues"].append(
            issue("cutoff_after_creation", "Evidence cutoff cannot follow packet creation.", "invalid")
        )

    packet_root = fields.get("canonical_root")
    if not isinstance(packet_root, str) or not Path(packet_root).is_absolute():
        result["issues"].append(
            issue("invalid_canonical_root", "Packet canonical root must be absolute.", "invalid")
        )
    elif os.path.normpath(packet_root) != packet_root:
        result["issues"].append(
            issue("unnormalized_canonical_root", "Packet canonical root must be normalized.", "invalid")
        )
    else:
        result["canonical_root"] = packet_root
        if packet_root != str(resolved_root):
            result["issues"].append(
                issue("needs_rebind", "Packet canonical root differs from the current root.", "stale")
            )

    valid_until_value = fields.get("valid_until")
    if valid_until_value is not None:
        valid_until = parse_utc(valid_until_value)
        if valid_until is None:
            result["issues"].append(
                issue("invalid_valid_until", "valid_until must be an RFC 3339 UTC timestamp.", "invalid")
            )
        else:
            result["valid_until"] = valid_until_value
            reference_now = now or datetime.now(timezone.utc)
            if reference_now.tzinfo is None:
                reference_now = reference_now.replace(tzinfo=timezone.utc)
            if valid_until < reference_now.astimezone(timezone.utc):
                result["issues"].append(
                    issue(
                        "valid_until_elapsed",
                        "Packet validity horizon elapsed; dynamic facts require revalidation.",
                        "stale",
                    )
                )
            if created_at is not None and valid_until < created_at:
                result["issues"].append(
                    issue("valid_until_before_creation", "valid_until precedes packet creation.", "invalid")
                )

    source_revision = fields.get("source_revision")
    if source_revision is not None and (
        not isinstance(source_revision, str) or not SOURCE_REVISION_RE.fullmatch(source_revision)
    ):
        result["issues"].append(
            issue("invalid_source_revision", "source_revision must identify a Git commit.", "invalid")
        )

    tags = fields.get("tags")
    if tags is not None and (
        not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags)
    ):
        result["issues"].append(issue("invalid_tags", "tags must be a string list.", "invalid"))

    derived_from = fields.get("derived_from")
    derivation_reason = fields.get("derivation_reason")
    if (derived_from is None) != (derivation_reason is None):
        result["issues"].append(
            issue(
                "incomplete_derivation",
                "Derived packets require both source identity and derivation reason.",
                "invalid",
            )
        )
    elif derived_from is not None:
        result["derived_from"] = derived_from
        match = DERIVED_FROM_RE.fullmatch(derived_from) if isinstance(derived_from, str) else None
        if match is None or match.group(1) == packet_id:
            result["issues"].append(
                issue("invalid_derived_from", "Derived packet source identity is invalid.", "invalid")
            )
        if derivation_reason not in DERIVATION_REASONS:
            result["issues"].append(
                issue("invalid_derivation_reason", "Packet derivation reason is invalid.", "invalid")
            )

    for heading in REQUIRED_HEADINGS:
        if re.search(rf"(?m)^## {re.escape(heading)}\s*$", body) is None:
            result["issues"].append(
                issue("missing_body_heading", "Packet body is missing a required section.", "invalid")
            )
            break

    return finalize(result)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--canonical-root", required=True, type=Path)
    parser.add_argument("--packet", required=True, type=Path)
    parser.add_argument("--expected-sha256")
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = validate_packet(
        canonical_root=args.canonical_root,
        packet=args.packet,
        expected_sha256=args.expected_sha256,
    )
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"status: {result['status']}")
        print(f"packet: {result['packet']}")
        if result["packet_id"]:
            print(f"packet_id: {result['packet_id']}")
        if result["sha256"]:
            print(f"sha256: {result['sha256']}")
        for item in result["issues"]:
            print(f"{item['severity']}: {item['code']}: {item['message']}")
    return STATUS_EXIT[result["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
