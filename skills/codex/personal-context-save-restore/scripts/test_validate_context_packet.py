#!/usr/bin/env python3
"""Focused tests for the read-only context packet validator."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).with_name("validate_context_packet.py")
SPEC = importlib.util.spec_from_file_location("validate_context_packet", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Could not load {SCRIPT}")
VALIDATOR = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = VALIDATOR
SPEC.loader.exec_module(VALIDATOR)

NOW = datetime(2026, 7, 11, 12, 0, tzinfo=timezone.utc)
PACKET_ID = "ctx-20260711t115800z-profile-audit"
HEADINGS = (
    "Goal and constraints",
    "Verified snapshot state",
    "Artifacts",
    "Decisions and provenance",
    "Evidence and verification",
    "Unknowns, risks, and blockers",
    "Proposed next actions",
)


class ContextPacketValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name).resolve()
        self.context_dir = self.root / ".codex" / "context"
        self.context_dir.mkdir(parents=True)

    def packet_text(
        self,
        *,
        packet_id: str = PACKET_ID,
        canonical_root: Path | None = None,
        valid_until: str | None = None,
        tags: list[str] | None = None,
        derived_from: str | None = None,
        derivation_reason: str | None = None,
    ) -> str:
        root = canonical_root or self.root
        fields = [
            "---",
            'context_owner: "personal-context-save-restore"',
            "schema_version: 1",
            'record_type: "context-packet"',
            f'packet_id: "{packet_id}"',
            'created_at: "2026-07-11T11:58:00Z"',
            f'canonical_root: "{root}"',
            'evidence_cutoff: "2026-07-11T11:57:00Z"',
        ]
        if valid_until is not None:
            fields.append(f'valid_until: "{valid_until}"')
        if tags is not None:
            fields.append(f"tags: {json.dumps(tags)}")
        if derived_from is not None:
            fields.append(f'derived_from: "{derived_from}"')
        if derivation_reason is not None:
            fields.append(f'derivation_reason: "{derivation_reason}"')
        fields.extend(("---", "", "# Context Packet", ""))
        for heading in HEADINGS:
            fields.extend((f"## {heading}", "", "- Test fixture.", ""))
        return "\n".join(fields)

    def write_packet(
        self,
        *,
        filename: str | None = None,
        text: str | None = None,
        **kwargs: object,
    ) -> Path:
        path = self.context_dir / (filename or f"{PACKET_ID}.md")
        path.write_text(text or self.packet_text(**kwargs), encoding="utf-8")
        return path

    def validate(
        self,
        packet: Path,
        *,
        canonical_root: Path | None = None,
        expected_sha256: str | None = None,
    ) -> dict[str, object]:
        return VALIDATOR.validate_packet(
            canonical_root=canonical_root or self.root,
            packet=packet,
            expected_sha256=expected_sha256,
            now=NOW,
        )

    @staticmethod
    def issue_codes(result: dict[str, object]) -> set[str]:
        return {issue["code"] for issue in result["issues"]}

    def test_valid_packet_reports_stable_sha256(self) -> None:
        result = self.validate(self.write_packet())

        self.assertEqual(result["status"], "valid")
        self.assertEqual(result["packet_id"], PACKET_ID)
        self.assertRegex(result["sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual(result["issues"], [])

    def test_validation_does_not_modify_packet_bytes_or_metadata(self) -> None:
        packet = self.write_packet()
        before_bytes = packet.read_bytes()
        before_stat = packet.stat()

        self.validate(packet)

        after_stat = packet.stat()
        self.assertEqual(packet.read_bytes(), before_bytes)
        self.assertEqual(after_stat.st_size, before_stat.st_size)
        self.assertEqual(after_stat.st_mtime_ns, before_stat.st_mtime_ns)

    def test_root_mismatch_requires_rebind(self) -> None:
        old_root = self.root / "moved-from"
        old_root.mkdir()
        packet = self.write_packet(canonical_root=old_root)

        result = self.validate(packet)

        self.assertEqual(result["status"], "stale")
        self.assertIn("needs_rebind", self.issue_codes(result))

    def test_expired_valid_until_marks_facts_stale(self) -> None:
        packet = self.write_packet(valid_until="2026-07-11T11:59:59Z")

        result = self.validate(packet)

        self.assertEqual(result["status"], "stale")
        self.assertIn("valid_until_elapsed", self.issue_codes(result))

    def test_expected_hash_mismatch_is_stale(self) -> None:
        result = self.validate(self.write_packet(), expected_sha256="0" * 64)

        self.assertEqual(result["status"], "stale")
        self.assertIn("sha256_mismatch", self.issue_codes(result))

    def test_inline_string_tags_are_supported(self) -> None:
        packet = self.write_packet(tags=["handoff", "profile-audit"])

        self.assertEqual(self.validate(packet)["status"], "valid")

    def test_derived_packet_requires_well_formed_source_identity(self) -> None:
        source_packet_id = "ctx-20260711t110000z-profile-audit"
        packet = self.write_packet(
            derived_from=f"packet:{source_packet_id}@sha256:{'a' * 64}",
            derivation_reason="correction",
        )

        self.assertEqual(self.validate(packet)["status"], "valid")

        malformed = self.write_packet(
            filename="ctx-20260711t115801z-malformed-derived.md",
            text=self.packet_text(
                packet_id="ctx-20260711t115801z-malformed-derived",
                derived_from="packet:unknown@sha256:nope",
                derivation_reason="correction",
            ),
        )
        result = self.validate(malformed)
        self.assertEqual(result["status"], "invalid")
        self.assertIn("invalid_derived_from", self.issue_codes(result))

    def test_filename_must_match_packet_id(self) -> None:
        packet = self.write_packet(filename="ctx-20260711t115900z-other.md")

        result = self.validate(packet)

        self.assertEqual(result["status"], "invalid")
        self.assertIn("filename_mismatch", self.issue_codes(result))

    def test_malformed_frontmatter_is_invalid(self) -> None:
        packet = self.write_packet(text="---\npacket_id: broken\n")

        result = self.validate(packet)

        self.assertEqual(result["status"], "invalid")
        self.assertIn("malformed_frontmatter", self.issue_codes(result))

    def test_symlink_packet_is_rejected_without_reading_target(self) -> None:
        target = self.root / "target.md"
        target.write_text(self.packet_text(), encoding="utf-8")
        packet = self.context_dir / f"{PACKET_ID}.md"
        packet.symlink_to(target)

        result = self.validate(packet)

        self.assertEqual(result["status"], "invocation_error")
        self.assertIn("packet_symlink", self.issue_codes(result))

    def test_packet_outside_context_directory_is_rejected(self) -> None:
        packet = self.root / f"{PACKET_ID}.md"
        packet.write_text(self.packet_text(), encoding="utf-8")

        result = self.validate(packet)

        self.assertEqual(result["status"], "invocation_error")
        self.assertIn("packet_path_escape", self.issue_codes(result))

    def test_cli_json_uses_documented_exit_codes(self) -> None:
        packet = self.write_packet()

        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--canonical-root",
                str(self.root),
                "--packet",
                str(packet),
                "--json",
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout)["status"], "valid")


if __name__ == "__main__":
    unittest.main()
