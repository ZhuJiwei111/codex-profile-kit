#!/usr/bin/env python3
"""Tests for the read-only planning-state validator."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).with_name("validate_plan_state.py")


def load_validator_module():
    spec = importlib.util.spec_from_file_location("planning_state_validator_under_test", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_validator_module()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ValidatorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.base = Path(self.tempdir.name)
        self.root = self.base / "repo"
        self.root.mkdir()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def task_record(self, plan_id: str = "task-one") -> Path:
        return self.root / ".planning" / "plans" / plan_id

    def write_trio(
        self,
        record: Path,
        *,
        plan_id: str = "task-one",
        kind: str = "task",
        status: str = "active",
        generation: int = 1,
        canonical_root: Path | None = None,
        closure_status: str | None = None,
        root_plan_id: str | None = None,
        parent_plan_id: str | None = None,
        predecessor_plan_id: str | None = None,
        missing: str | None = None,
        findings_generation: int | None = None,
    ) -> None:
        record.mkdir(parents=True, exist_ok=True)
        root_value = canonical_root if canonical_root is not None else self.root
        task_lines = [
            "---",
            "planning_owner: personal-planning-with-files-zh",
            "schema_version: 1",
            f"plan_kind: {kind}",
            f"plan_id: {plan_id}",
            "plan_role: task_plan",
            f"plan_status: {status}",
            f"generation: {generation}",
            f"canonical_root: {root_value}",
            "evidence_cutoff: unverified",
        ]
        if closure_status is not None:
            task_lines.append(f"closure_status: {closure_status}")
        if root_plan_id is not None:
            task_lines.append(f"root_plan_id: {root_plan_id}")
        if parent_plan_id is not None:
            task_lines.append(f"parent_plan_id: {parent_plan_id}")
        if predecessor_plan_id is not None:
            task_lines.append(f"predecessor_plan_id: {predecessor_plan_id}")
        task_lines.extend(["---", "", "# Task Plan", ""])
        if missing != "task_plan.md":
            (record / "task_plan.md").write_text("\n".join(task_lines))

        for filename, role in (("findings.md", "findings"), ("progress.md", "progress")):
            if missing == filename:
                continue
            role_generation = findings_generation if role == "findings" and findings_generation is not None else generation
            text = "\n".join(
                [
                    "---",
                    "planning_owner: personal-planning-with-files-zh",
                    "schema_version: 1",
                    f"plan_id: {plan_id}",
                    f"plan_role: {role}",
                    f"generation: {role_generation}",
                    "---",
                    "",
                    f"# {role.title()}",
                    "",
                ]
            )
            (record / filename).write_text(text)

    def write_control(
        self,
        record: Path,
        name: str,
        *,
        trust: str,
        hashes: dict[str, str],
        include_snapshot_fields: bool = True,
        plan_id: str = "task-one",
        generation: int = 1,
    ) -> None:
        lines = [
            "---",
            f"record_type: {'terminal-archive' if name == 'ARCHIVE.md' else 'generation-snapshot'}",
            f"record_trust: {trust}",
            f"plan_id: {plan_id}",
            f"generation: {generation}",
        ]
        if name == "SNAPSHOT.md" and include_snapshot_fields:
            lines.extend([f"target_generation: {generation + 1}", "created_at: 2026-07-11T00:00:00Z"])
        lines.append("source_hashes:")
        lines.extend(f"  {key}: {value}" for key, value in hashes.items())
        lines.extend(["---", "", f"# {name}", ""])
        (record / name).write_text("\n".join(lines))

    def write_transaction(
        self,
        staging: Path,
        source: Path,
        *,
        txid: str = "tx-0001",
        history: Path | None = None,
    ) -> None:
        target_history = history or source / "history" / "g0001-20260711-phase-one"
        hashes = self.trio_hashes(source)
        lines = [
            "---",
            "planning_owner: personal-planning-with-files-zh",
            "schema_version: 1",
            "record_type: plan-transaction",
            "operation: generation-rollover",
            f"txid: {txid}",
            "plan_kind: task",
            "plan_id: task-one",
            "source_generation: 1",
            "target_generation: 2",
            f"canonical_root: {self.root}",
            "phase: staged",
            f"seed_digest: {'0' * 64}",
            f"source_record: {source}",
            f"history_record: {target_history}",
            "source_hashes:",
        ]
        lines.extend(f"  {key}: {value}" for key, value in hashes.items())
        lines.extend(["---", "", "# Transaction", ""])
        (staging / "TRANSACTION.md").write_text("\n".join(lines))

    def trio_hashes(self, record: Path) -> dict[str, str]:
        return {name: sha256(record / name) for name in ("task_plan.md", "findings.md", "progress.md")}

    def run_validator(
        self,
        record: Path,
        *,
        root: Path | None = None,
        check_lineage: bool = False,
        for_initialization: bool = False,
    ) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
        command = [
            sys.executable,
            str(SCRIPT),
            "--canonical-root",
            str(root or self.root),
            "--record",
            str(record),
            "--json",
        ]
        if check_lineage:
            command.append("--check-lineage")
        if for_initialization:
            command.append("--for-initialization")
        completed = subprocess.run(command, text=True, capture_output=True, check=False)
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError:
            payload = {}
        return completed, payload

    def assert_issue(self, payload: dict[str, object], code: str) -> None:
        issues = payload.get("issues", [])
        self.assertIn(code, {item["code"] for item in issues})

    def test_help(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--help"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("--canonical-root", completed.stdout)
        self.assertIn("--record", completed.stdout)

    def test_valid_task_plan_is_read_only(self) -> None:
        record = self.task_record()
        self.write_trio(record)
        before = {
            path.relative_to(self.root): (path.read_bytes(), path.stat().st_mtime_ns)
            for path in self.root.rglob("*")
            if path.is_file()
        }
        completed, payload = self.run_validator(record)
        after = {
            path.relative_to(self.root): (path.read_bytes(), path.stat().st_mtime_ns)
            for path in self.root.rglob("*")
            if path.is_file()
        }
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(payload["status"], "valid")
        self.assertFalse(payload["needs_rebind"])
        self.assertEqual(payload["hash_binding_scope"], "standard")
        self.assertEqual(payload["inspection_root"], str(self.root))
        self.assertEqual(payload["recorded_canonical_root"], str(self.root))
        self.assertEqual(set(payload["source_hashes"]), {"task_plan.md", "findings.md", "progress.md"})
        self.assertEqual(before, after)

    def test_valid_repo_plan(self) -> None:
        self.write_trio(self.root, plan_id="repo-main", kind="repo")
        completed, payload = self.run_validator(self.root)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(payload["record_type"], "active-repo")

    def test_repo_plan_ignores_unmanaged_control_filenames(self) -> None:
        self.write_trio(self.root, plan_id="repo-main", kind="repo")
        (self.root / "ARCHIVE.md").write_text("# Project-owned archive notes\n")
        completed, payload = self.run_validator(self.root)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(payload["record_type"], "active-repo")

    def test_partial_trio_is_invalid(self) -> None:
        record = self.task_record()
        self.write_trio(record, missing="progress.md")
        completed, payload = self.run_validator(record)
        self.assertEqual(completed.returncode, 1)
        self.assertEqual(payload["status"], "invalid")
        self.assert_issue(payload, "missing_file")

    def test_generation_mismatch_is_invalid(self) -> None:
        record = self.task_record()
        self.write_trio(record, findings_generation=2)
        completed, payload = self.run_validator(record)
        self.assertEqual(completed.returncode, 1)
        self.assert_issue(payload, "generation_mismatch")

    def test_canonical_root_mismatch_needs_rebind(self) -> None:
        record = self.task_record()
        self.write_trio(record, canonical_root=self.base / "old-repo")
        completed, payload = self.run_validator(record)
        self.assertEqual(completed.returncode, 1)
        self.assertEqual(payload["status"], "stale")
        self.assertTrue(payload["needs_rebind"])
        self.assertEqual(payload["hash_binding_scope"], "rebind-preview-only")
        self.assert_issue(payload, "canonical_root_mismatch")

    def test_incomplete_rebind_has_no_hash_binding_scope(self) -> None:
        record = self.task_record()
        self.write_trio(record, canonical_root=self.base / "old-repo")
        staging = record / ".staging" / "tx-0001"
        staging.mkdir(parents=True)
        (staging / "TRANSACTION.md").write_text("unfinished\n")
        completed, payload = self.run_validator(record)
        self.assertEqual(completed.returncode, 1)
        self.assertEqual(payload["status"], "incomplete")
        self.assertTrue(payload["needs_rebind"])
        self.assertEqual(payload["hash_binding_scope"], "none")

    def test_symlinked_file_is_invalid(self) -> None:
        record = self.task_record()
        self.write_trio(record)
        progress = record / "progress.md"
        target = record / "progress-real.md"
        progress.rename(target)
        progress.symlink_to(target.name)
        completed, payload = self.run_validator(record)
        self.assertEqual(completed.returncode, 1)
        self.assert_issue(payload, "symlink_not_allowed")

    def test_path_escape_is_invalid(self) -> None:
        outside = self.base / "outside"
        self.write_trio(outside)
        completed, payload = self.run_validator(outside)
        self.assertEqual(completed.returncode, 1)
        self.assert_issue(payload, "record_outside_root")

    def test_invalid_lifecycle_combination(self) -> None:
        record = self.task_record()
        self.write_trio(record, status="active", closure_status="complete")
        completed, payload = self.run_validator(record)
        self.assertEqual(completed.returncode, 1)
        self.assert_issue(payload, "invalid_closure_status")

    def test_unfinished_staging_is_incomplete(self) -> None:
        record = self.task_record()
        self.write_trio(record)
        staging = record / ".staging" / "tx-1"
        staging.mkdir(parents=True)
        (staging / "TRANSACTION.md").write_text("unfinished\n")
        completed, payload = self.run_validator(record)
        self.assertEqual(completed.returncode, 1)
        self.assertEqual(payload["status"], "incomplete")
        self.assert_issue(payload, "unfinished_transaction")

    def test_valid_staging_transaction(self) -> None:
        source = self.task_record()
        self.write_trio(source)
        staging = source / ".staging" / "tx-0001"
        self.write_trio(staging, generation=2)
        self.write_transaction(staging, source)
        completed, payload = self.run_validator(staging)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(payload["record_type"], "staging")

    def test_snapshot_published_requires_valid_snapshot_control(self) -> None:
        source = self.task_record()
        self.write_trio(source)
        history = source / "history" / "g0001-20260711-phase-one"
        self.write_trio(history)
        (history / "SNAPSHOT.md").write_text("not frontmatter\n")
        staging = source / ".staging" / "tx-0001"
        self.write_trio(staging, generation=2)
        self.write_transaction(staging, source, history=history)
        transaction = staging / "TRANSACTION.md"
        transaction.write_text(transaction.read_text().replace("phase: staged", "phase: snapshot-published"))
        completed, payload = self.run_validator(staging)
        self.assertEqual(completed.returncode, 1)
        self.assert_issue(payload, "transaction_snapshot_control_invalid")

    def test_valid_snapshot_published_transaction(self) -> None:
        source = self.task_record()
        self.write_trio(source)
        history = source / "history" / "g0001-20260711-phase-one"
        self.write_trio(history)
        self.write_control(history, "SNAPSHOT.md", trust="valid", hashes=self.trio_hashes(history))
        staging = source / ".staging" / "tx-0001"
        self.write_trio(staging, generation=2)
        self.write_transaction(staging, source, history=history)
        transaction = staging / "TRANSACTION.md"
        transaction.write_text(transaction.read_text().replace("phase: staged", "phase: snapshot-published"))
        completed, payload = self.run_validator(staging)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(payload["transaction_phase"], "snapshot-published")

    def test_staging_wrong_location_is_invalid(self) -> None:
        source = self.task_record()
        self.write_trio(source)
        staging = self.root / "misc" / ".staging" / "tx-0001"
        self.write_trio(staging, generation=2)
        self.write_transaction(staging, source)
        completed, payload = self.run_validator(staging)
        self.assertEqual(completed.returncode, 1)
        self.assert_issue(payload, "invalid_record_location")

    def test_transaction_control_symlink_is_invalid(self) -> None:
        source = self.task_record()
        self.write_trio(source)
        staging = source / ".staging" / "tx-0001"
        self.write_trio(staging, generation=2)
        target = staging / "TRANSACTION.real.md"
        target.write_text("---\nrecord_type: plan-transaction\n---\n")
        (staging / "TRANSACTION.md").symlink_to(target.name)
        completed, payload = self.run_validator(staging)
        self.assertEqual(completed.returncode, 1)
        self.assert_issue(payload, "invalid_transaction_control")

    def test_partial_history_is_incomplete(self) -> None:
        record = self.task_record()
        self.write_trio(record)
        partial = record / "history" / "g0001-20260711-phase-one"
        partial.mkdir(parents=True)
        (partial / "task_plan.md").write_text("partial\n")
        completed, payload = self.run_validator(record)
        self.assertEqual(completed.returncode, 1)
        self.assertEqual(payload["status"], "incomplete")
        self.assert_issue(payload, "partial_history_record")

    def test_staged_partial_history_is_incomplete_not_collision(self) -> None:
        source = self.task_record()
        self.write_trio(source)
        history = source / "history" / "g0001-20260711-phase-one"
        history.mkdir(parents=True)
        (history / "task_plan.md").write_text("partial\n")
        staging = source / ".staging" / "tx-0001"
        self.write_trio(staging, generation=2)
        self.write_transaction(staging, source, history=history)
        completed, payload = self.run_validator(staging)
        self.assertEqual(completed.returncode, 1)
        self.assertEqual(payload["status"], "incomplete")
        self.assert_issue(payload, "transaction_history_incomplete")
        self.assertNotIn("transaction_history_collision", {item["code"] for item in payload["issues"]})

    def test_invalidated_archive_blocks_initialization(self) -> None:
        record = self.root / ".planning" / "archive" / "plans" / "task-one"
        self.write_trio(record, status="closed", closure_status="complete")
        self.write_control(record, "ARCHIVE.md", trust="invalidated", hashes=self.trio_hashes(record))
        corrections = record / "corrections"
        corrections.mkdir()
        (corrections / "c0001-20260711-invalid.md").write_text("# Correction\n")
        completed, payload = self.run_validator(record, for_initialization=True)
        self.assertEqual(completed.returncode, 1)
        self.assert_issue(payload, "initialization_blocked")

    def test_valid_archive_can_be_validated(self) -> None:
        record = self.root / ".planning" / "archive" / "plans" / "task-one"
        self.write_trio(record, status="closed", closure_status="complete")
        self.write_control(record, "ARCHIVE.md", trust="valid", hashes=self.trio_hashes(record))
        completed, payload = self.run_validator(record)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(payload["record_type"], "terminal-archive")

    def test_terminal_archive_requires_closed_plan(self) -> None:
        record = self.root / ".planning" / "archive" / "plans" / "task-one"
        self.write_trio(record, status="active")
        self.write_control(record, "ARCHIVE.md", trust="valid", hashes=self.trio_hashes(record))
        completed, payload = self.run_validator(record)
        self.assertEqual(completed.returncode, 1)
        self.assert_issue(payload, "archive_not_closed")

    def test_valid_trust_with_correction_is_incomplete(self) -> None:
        record = self.root / ".planning" / "archive" / "plans" / "task-one"
        self.write_trio(record, status="closed", closure_status="complete")
        self.write_control(record, "ARCHIVE.md", trust="valid", hashes=self.trio_hashes(record))
        corrections = record / "corrections"
        corrections.mkdir()
        (corrections / "c0001-20260711-pending.md").write_text("# Pending correction\n")
        completed, payload = self.run_validator(record)
        self.assertEqual(completed.returncode, 1)
        self.assertEqual(payload["status"], "incomplete")
        self.assert_issue(payload, "unapplied_correction")

    def test_snapshot_hash_mismatch_is_invalid(self) -> None:
        record = self.task_record() / "history" / "g0001-phase"
        self.write_trio(record)
        hashes = self.trio_hashes(record)
        hashes["progress.md"] = "0" * 64
        self.write_control(record, "SNAPSHOT.md", trust="valid", hashes=hashes)
        completed, payload = self.run_validator(record)
        self.assertEqual(completed.returncode, 1)
        self.assert_issue(payload, "hash_mismatch")

    def test_snapshot_requires_transition_metadata(self) -> None:
        record = self.task_record() / "history" / "g0001-20260711-phase-one"
        self.write_trio(record)
        self.write_control(
            record,
            "SNAPSHOT.md",
            trust="valid",
            hashes=self.trio_hashes(record),
            include_snapshot_fields=False,
        )
        completed, payload = self.run_validator(record)
        self.assertEqual(completed.returncode, 1)
        self.assert_issue(payload, "missing_snapshot_metadata")

    def test_initialization_requires_frozen_record(self) -> None:
        record = self.task_record()
        self.write_trio(record)
        completed, payload = self.run_validator(record, for_initialization=True)
        self.assertEqual(completed.returncode, 1)
        self.assert_issue(payload, "initialization_requires_frozen_record")

    def test_self_parent_is_invalid(self) -> None:
        record = self.task_record()
        self.write_trio(record, parent_plan_id="task-one")
        completed, payload = self.run_validator(record, check_lineage=True)
        self.assertEqual(completed.returncode, 1)
        self.assert_issue(payload, "lineage_self_link")

    def test_parent_cycle_is_invalid(self) -> None:
        record_a = self.task_record("task-a")
        record_b = self.task_record("task-b")
        self.write_trio(record_a, plan_id="task-a", parent_plan_id="task-b")
        self.write_trio(record_b, plan_id="task-b", parent_plan_id="task-a")
        completed, payload = self.run_validator(record_a, check_lineage=True)
        self.assertEqual(completed.returncode, 1)
        self.assert_issue(payload, "lineage_cycle")

    def test_predecessor_cycle_is_invalid(self) -> None:
        record_a = self.task_record("task-a")
        record_b = self.task_record("task-b")
        self.write_trio(record_a, plan_id="task-a", predecessor_plan_id="task-b")
        self.write_trio(record_b, plan_id="task-b", predecessor_plan_id="task-a")
        completed, payload = self.run_validator(record_a, check_lineage=True)
        self.assertEqual(completed.returncode, 1)
        self.assert_issue(payload, "lineage_cycle")

    def test_dangling_parent_is_stale(self) -> None:
        record = self.task_record()
        self.write_trio(record, parent_plan_id="missing-parent")
        completed, payload = self.run_validator(record, check_lineage=True)
        self.assertEqual(completed.returncode, 1)
        self.assertEqual(payload["status"], "stale")
        self.assert_issue(payload, "lineage_unresolved")

    def test_unmanaged_root_task_plan_is_ignored_in_lineage(self) -> None:
        record = self.task_record()
        self.write_trio(record)
        (self.root / "task_plan.md").write_text("# User-owned project notes\n")
        completed, payload = self.run_validator(record, check_lineage=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(payload["status"], "valid")
        self.assertNotIn(
            "lineage_record_unreadable",
            {item["code"] for item in payload["issues"]},
        )

    def test_managed_lineage_candidate_without_plan_id_is_stale(self) -> None:
        record = self.task_record()
        self.write_trio(record)
        broken = self.task_record("broken")
        broken.mkdir(parents=True)
        (broken / "task_plan.md").write_text(
            "---\nplanning_owner: personal-planning-with-files-zh\nschema_version: 1\n---\n"
        )
        completed, payload = self.run_validator(record, check_lineage=True)
        self.assertEqual(completed.returncode, 1)
        self.assert_issue(payload, "lineage_record_invalid")

    def test_lineage_scan_does_not_follow_planning_symlink(self) -> None:
        self.write_trio(self.root, plan_id="repo-main", kind="repo")
        outside = self.base / "outside-planning"
        external_record = outside / "plans" / "external"
        self.write_trio(external_record, plan_id="repo-main")
        (self.root / ".planning").symlink_to(outside, target_is_directory=True)
        completed, payload = self.run_validator(self.root, check_lineage=True)
        self.assertEqual(completed.returncode, 1)
        self.assert_issue(payload, "lineage_scope_unsafe")
        self.assertNotIn("duplicate_plan_id", {item["code"] for item in payload["issues"]})

    def test_non_string_lineage_field_is_invalid(self) -> None:
        record = self.task_record()
        self.write_trio(record)
        task = record / "task_plan.md"
        task.write_text(task.read_text().replace("evidence_cutoff: unverified", "evidence_cutoff: unverified\nparent_plan_id: 123"))
        completed, payload = self.run_validator(record, check_lineage=True)
        self.assertEqual(completed.returncode, 1)
        self.assert_issue(payload, "invalid_lineage_field")

    def test_missing_initialized_snapshot_is_stale(self) -> None:
        record = self.task_record()
        self.write_trio(record)
        task = record / "task_plan.md"
        task.write_text(
            task.read_text().replace(
                "evidence_cutoff: unverified",
                "evidence_cutoff: unverified\ninitialized_from: snapshot:task-source@g0009",
            )
        )
        completed, payload = self.run_validator(record, check_lineage=True)
        self.assertEqual(completed.returncode, 1)
        self.assertEqual(payload["status"], "stale")
        self.assert_issue(payload, "lineage_unresolved")

    def test_exact_initialized_snapshot_is_visible(self) -> None:
        source = self.task_record("task-source")
        self.write_trio(source, plan_id="task-source", generation=2)
        snapshot = source / "history" / "g0001-20260711-phase-one"
        self.write_trio(snapshot, plan_id="task-source", generation=1)
        self.write_control(
            snapshot,
            "SNAPSHOT.md",
            trust="valid",
            hashes=self.trio_hashes(snapshot),
            plan_id="task-source",
            generation=1,
        )
        record = self.task_record()
        self.write_trio(record)
        task = record / "task_plan.md"
        task.write_text(
            task.read_text().replace(
                "evidence_cutoff: unverified",
                "evidence_cutoff: unverified\ninitialized_from: snapshot:task-source@g0001",
            )
        )
        completed, payload = self.run_validator(record, check_lineage=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(payload["status"], "valid")

    def test_initialized_snapshot_cannot_use_invalidated_control(self) -> None:
        source = self.task_record("task-source")
        self.write_trio(source, plan_id="task-source", generation=2)
        snapshot = source / "history" / "g0001-20260711-phase-one"
        self.write_trio(snapshot, plan_id="task-source", generation=1)
        self.write_control(
            snapshot,
            "SNAPSHOT.md",
            trust="invalidated",
            hashes=self.trio_hashes(snapshot),
            plan_id="task-source",
            generation=1,
        )
        corrections = snapshot / "corrections"
        corrections.mkdir()
        (corrections / "c0001-20260711-invalid.md").write_text("# Invalidated\n")
        record = self.task_record()
        self.write_trio(record)
        task = record / "task_plan.md"
        task.write_text(
            task.read_text().replace(
                "evidence_cutoff: unverified",
                "evidence_cutoff: unverified\ninitialized_from: snapshot:task-source@g0001",
            )
        )
        completed, payload = self.run_validator(record, check_lineage=True)
        self.assertEqual(completed.returncode, 1)
        self.assert_issue(payload, "lineage_source_invalidated")

    def test_initialized_corrected_snapshot_names_correction(self) -> None:
        source = self.task_record("task-source")
        self.write_trio(source, plan_id="task-source", generation=2)
        snapshot = source / "history" / "g0001-20260711-phase-one"
        self.write_trio(snapshot, plan_id="task-source", generation=1)
        self.write_control(
            snapshot,
            "SNAPSHOT.md",
            trust="corrected",
            hashes=self.trio_hashes(snapshot),
            plan_id="task-source",
            generation=1,
        )
        corrections = snapshot / "corrections"
        corrections.mkdir()
        (corrections / "c0001-20260711-fix.md").write_text("# Correction\n")
        record = self.task_record()
        self.write_trio(record)
        task = record / "task_plan.md"
        task.write_text(
            task.read_text().replace(
                "evidence_cutoff: unverified",
                "evidence_cutoff: unverified\ninitialized_from: snapshot:task-source@g0001#c0001",
            )
        )
        completed, payload = self.run_validator(record, check_lineage=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_partial_managed_root_plan_cannot_satisfy_lineage(self) -> None:
        record = self.task_record()
        self.write_trio(record, root_plan_id="repo-main")
        self.write_trio(self.root, plan_id="repo-main", kind="repo")
        (self.root / "findings.md").unlink()
        completed, payload = self.run_validator(record, check_lineage=True)
        self.assertEqual(completed.returncode, 1)
        self.assert_issue(payload, "lineage_record_invalid")
        self.assert_issue(payload, "lineage_unresolved")

    def test_initialized_archive_requires_archive_control(self) -> None:
        archive = self.root / ".planning" / "archive" / "plans" / "task-old"
        self.write_trio(archive, plan_id="task-old", status="closed", closure_status="complete")
        record = self.task_record()
        self.write_trio(record)
        task = record / "task_plan.md"
        task.write_text(
            task.read_text().replace(
                "evidence_cutoff: unverified",
                "evidence_cutoff: unverified\ninitialized_from: archive:task-old#original",
            )
        )
        completed, payload = self.run_validator(record, check_lineage=True)
        self.assertEqual(completed.returncode, 1)
        self.assert_issue(payload, "lineage_control_invalid")
        self.assert_issue(payload, "lineage_unresolved")

    def test_initialized_original_archive_with_control_is_visible(self) -> None:
        archive = self.root / ".planning" / "archive" / "plans" / "task-old"
        self.write_trio(archive, plan_id="task-old", status="closed", closure_status="complete")
        self.write_control(
            archive,
            "ARCHIVE.md",
            trust="valid",
            hashes=self.trio_hashes(archive),
            plan_id="task-old",
        )
        record = self.task_record()
        self.write_trio(record)
        task = record / "task_plan.md"
        task.write_text(
            task.read_text().replace(
                "evidence_cutoff: unverified",
                "evidence_cutoff: unverified\ninitialized_from: archive:task-old#original",
            )
        )
        completed, payload = self.run_validator(record, check_lineage=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_empty_mapping_evidence_cutoff_is_invalid(self) -> None:
        record = self.task_record()
        self.write_trio(record)
        task = record / "task_plan.md"
        task.write_text(task.read_text().replace("evidence_cutoff: unverified", "evidence_cutoff:"))
        completed, payload = self.run_validator(record)
        self.assertEqual(completed.returncode, 1)
        self.assert_issue(payload, "invalid_evidence_cutoff")

    def test_symlink_loop_is_structured_invocation_error(self) -> None:
        loop_a = self.base / "loop-a"
        loop_b = self.base / "loop-b"
        loop_a.symlink_to(loop_b)
        loop_b.symlink_to(loop_a)
        completed, payload = self.run_validator(loop_a, root=loop_a)
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(payload.get("status"), "invocation_error")
        self.assertEqual(payload.get("error"), "invocation_error")

    def test_hashed_frontmatter_detects_concurrent_change(self) -> None:
        record = self.task_record()
        self.write_trio(record)
        path = record / "task_plan.md"
        real_fstat = os.fstat
        call_count = 0

        def mutate_before_second_fstat(fd):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                path.write_text(path.read_text().replace("plan_status: active", "plan_status: draft"))
            return real_fstat(fd)

        with mock.patch.object(VALIDATOR.os, "fstat", side_effect=mutate_before_second_fstat):
            with self.assertRaises(VALIDATOR.ConcurrentReadError):
                VALIDATOR.read_hashed_frontmatter(path)

    def test_hashed_frontmatter_detects_atomic_replacement(self) -> None:
        record = self.task_record()
        self.write_trio(record)
        path = record / "task_plan.md"
        replacement = record / "replacement.md"
        replacement.write_text(path.read_text().replace("plan_status: active", "plan_status: draft"))
        real_lstat = os.lstat
        path_lstat_calls = 0

        def replace_before_final_lstat(value):
            nonlocal path_lstat_calls
            if Path(value) == path:
                path_lstat_calls += 1
                if path_lstat_calls == 2:
                    os.replace(replacement, path)
            return real_lstat(value)

        with mock.patch.object(VALIDATOR.os, "lstat", side_effect=replace_before_final_lstat):
            with self.assertRaises(VALIDATOR.ConcurrentReadError):
                VALIDATOR.read_hashed_frontmatter(path)

    def test_transaction_source_is_rechecked_before_result(self) -> None:
        source = self.task_record()
        self.write_trio(source)
        staging = source / ".staging" / "tx-0001"
        self.write_trio(staging, generation=2)
        self.write_transaction(staging, source)
        real_verify = VALIDATOR.verify_unchanged_path
        staged_task_checks = 0

        def mutate_source_before_final_checks(path, stamp):
            nonlocal staged_task_checks
            if path == staging / "task_plan.md":
                staged_task_checks += 1
                if staged_task_checks == 2:
                    progress = source / "progress.md"
                    progress.write_text(progress.read_text() + "changed after transaction read\n")
            return real_verify(path, stamp)

        validator = VALIDATOR.PlanValidator(
            self.root,
            staging,
            check_lineage=False,
            for_initialization=False,
        )
        with mock.patch.object(VALIDATOR, "verify_unchanged_path", side_effect=mutate_source_before_final_checks):
            payload = validator.validate()
        self.assertEqual(payload["status"], "stale")
        self.assertEqual(payload["hash_binding_scope"], "none")
        self.assert_issue(payload, "record_changed_during_validation")


if __name__ == "__main__":
    unittest.main()
