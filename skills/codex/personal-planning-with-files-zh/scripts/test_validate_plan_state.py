#!/usr/bin/env python3
"""Focused tests for the serial-phase planning-state validator."""

from __future__ import annotations

import importlib.util
import io
import json
import os
from pathlib import Path
from contextlib import redirect_stdout
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock


SCRIPT = Path(__file__).with_name("validate_plan_state.py")


def load_validator_module():
    spec = importlib.util.spec_from_file_location("validate_plan_state", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ValidatorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repo"
        self.root.mkdir()

    def frontmatter(self, fields: list[str], body: str = "body\n") -> str:
        return "---\n" + "\n".join(fields) + "\n---\n\n" + body

    def write_project(
        self,
        *,
        plan_status: str = "draft",
        phases: tuple[str, ...] = ("phase-01", "phase-02"),
        active_phase: str | None = None,
        phase_statuses: dict[str, str] | None = None,
        root_extra: tuple[str, ...] = (),
    ) -> None:
        if phase_statuses is None:
            if plan_status == "closed":
                phase_statuses = {phase: "closed" for phase in phases}
            elif plan_status == "active":
                selected = active_phase or phases[0]
                active_index = phases.index(selected)
                phase_statuses = {
                    phase: "closed" if index < active_index else "active" if phase == selected else "draft"
                    for index, phase in enumerate(phases)
                }
                active_phase = selected
            else:
                phase_statuses = {phase: "draft" for phase in phases}

        root_fields = [
            "planning_owner: personal-planning-with-files-zh",
            "schema_version: 2",
            "plan_kind: project",
            "plan_role: root",
            "plan_id: project-roadmap",
            f"plan_status: {plan_status}",
            f"canonical_root: {self.root}",
            "phases: [" + ", ".join(phases) + "]",
        ]
        if active_phase is not None:
            root_fields.append(f"active_phase: {active_phase}")
        root_fields.extend(root_extra)
        (self.root / "task_plan.md").write_text(self.frontmatter(root_fields), encoding="utf-8")

        for phase in phases:
            record = self.root / ".planning" / "plans" / phase
            record.mkdir(parents=True)
            common = [
                "planning_owner: personal-planning-with-files-zh",
                "schema_version: 2",
                "plan_kind: phase",
                "plan_id: project-roadmap",
                f"phase_id: {phase}",
            ]
            task = common + [
                "plan_role: task_plan",
                f"phase_status: {phase_statuses[phase]}",
                f"canonical_root: {self.root}",
            ]
            findings = common + ["plan_role: findings", "evidence_cutoff: unverified"]
            progress = common + ["plan_role: progress"]
            for name, fields in (
                ("task_plan.md", task),
                ("findings.md", findings),
                ("progress.md", progress),
            ):
                (record / name).write_text(self.frontmatter(fields), encoding="utf-8")

    def run_validator(
        self,
        *,
        operation: str = "inspect",
        record: Path | None = None,
    ) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
        command = [
            sys.executable,
            str(SCRIPT),
            "--canonical-root",
            str(self.root),
            "--operation",
            operation,
            "--json",
        ]
        if record is not None:
            command.extend(["--record", str(record)])
        completed = subprocess.run(command, text=True, capture_output=True, check=False)
        payload = json.loads(completed.stdout)
        return completed, payload

    def issue_codes(self, payload: dict[str, object]) -> set[str]:
        return {str(issue["code"]) for issue in payload["issues"]}  # type: ignore[index]

    def test_help_lists_operations(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--help"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        for operation in ("inspect", "init", "resume", "correct", "archive", "successor"):
            self.assertIn(operation, completed.stdout)

    def test_empty_project_is_initializable_only_for_init(self) -> None:
        completed, payload = self.run_validator(operation="init")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(payload["status"], "initializable")

        completed, payload = self.run_validator(operation="inspect")
        self.assertEqual(completed.returncode, 1)
        self.assertIn("missing_root_plan", self.issue_codes(payload))

    def test_init_rejects_symlinked_root_task_plan(self) -> None:
        outside = Path(self.temp.name) / "outside-task-plan.md"
        outside.write_text("outside\n", encoding="utf-8")
        (self.root / "task_plan.md").symlink_to(outside)
        completed, payload = self.run_validator(operation="init")
        self.assertEqual(completed.returncode, 1)
        self.assertIn("unsafe_managed_path", self.issue_codes(payload))

    def test_root_anchor_rejects_parent_swap_to_symlink_during_open(self) -> None:
        module = load_validator_module()
        anchor = Path(self.temp.name) / "anchor"
        project = anchor / "project"
        project.mkdir(parents=True)
        moved_anchor = Path(self.temp.name) / "anchor-real"
        real_open = os.open
        swapped = False
        opened = None

        def open_then_swap(path, flags, *args, **kwargs):
            nonlocal swapped
            descriptor = real_open(path, flags, *args, **kwargs)
            if path == "anchor" and kwargs.get("dir_fd") is not None and not swapped:
                anchor.rename(moved_anchor)
                anchor.symlink_to(moved_anchor, target_is_directory=True)
                swapped = True
            return descriptor

        with mock.patch.object(module.os, "open", side_effect=open_then_swap) as mocked_open:
            supported_dir_fd = set(module.os.supports_dir_fd) | {mocked_open}
            with mock.patch.object(module.os, "supports_dir_fd", supported_dir_fd):
                try:
                    with self.assertRaises(module.InvocationError):
                        opened = module.RootAccess(project)
                finally:
                    if opened is not None:
                        opened.close()

    def test_init_rejects_symlinked_planning_directory(self) -> None:
        outside = Path(self.temp.name) / "outside-planning"
        outside.mkdir()
        (self.root / ".planning").symlink_to(outside, target_is_directory=True)
        completed, payload = self.run_validator(operation="init")
        self.assertEqual(completed.returncode, 1)
        self.assertIn("unsafe_managed_path", self.issue_codes(payload))

    def test_init_rejects_symlinked_managed_namespaces(self) -> None:
        for namespace in ("plans", "snapshots", "archive"):
            with self.subTest(namespace=namespace):
                planning = self.root / ".planning"
                planning.mkdir()
                outside = Path(self.temp.name) / f"outside-{namespace}"
                outside.mkdir()
                (planning / namespace).symlink_to(outside, target_is_directory=True)
                completed, payload = self.run_validator(operation="init")
                (planning / namespace).unlink()
                planning.rmdir()
                self.assertEqual(completed.returncode, 1)
                self.assertIn("unsafe_managed_path", self.issue_codes(payload))

    def test_archive_postflight_is_initializable_with_safe_history(self) -> None:
        archive = self.root / ".planning/archive/project-roadmap"
        snapshots = self.root / ".planning/snapshots/correction-01"
        archive.mkdir(parents=True)
        snapshots.mkdir(parents=True)
        (archive / "ARCHIVE.md").write_text("manifest\n", encoding="utf-8")
        (archive / "evidence.txt").write_text("evidence\n", encoding="utf-8")
        (snapshots / "CORRECTION.md").write_text("redacted\n", encoding="utf-8")
        completed, payload = self.run_validator(operation="init")
        self.assertEqual(completed.returncode, 0, (completed.stderr, payload))
        self.assertEqual(payload["status"], "initializable")

    def test_archive_allows_packet_domain_evidence_name(self) -> None:
        archive = self.root / ".planning/archive/project-roadmap"
        archive.mkdir(parents=True)
        (archive / "packet-loss-analysis.csv").write_text("loss,0\n", encoding="utf-8")
        completed, payload = self.run_validator(operation="init")
        self.assertEqual(completed.returncode, 0, (completed.stderr, payload))
        self.assertEqual(payload["status"], "initializable")

    def test_snapshots_allow_code_generation_domain_evidence_name(self) -> None:
        snapshot = self.root / ".planning/snapshots/correction-01"
        snapshot.mkdir(parents=True)
        (snapshot / "code-generation-benchmark.md").write_text("benchmark\n", encoding="utf-8")
        completed, payload = self.run_validator(operation="init")
        self.assertEqual(completed.returncode, 0, (completed.stderr, payload))
        self.assertEqual(payload["status"], "initializable")

    def test_archive_allows_plain_generation_evidence_directory(self) -> None:
        evidence = self.root / ".planning/archive/project-roadmap/evidence/generation"
        evidence.mkdir(parents=True)
        (evidence / "summary.md").write_text("summary\n", encoding="utf-8")
        completed, payload = self.run_validator(operation="init")
        self.assertEqual(completed.returncode, 0, (completed.stderr, payload))
        self.assertEqual(payload["status"], "initializable")

    def test_archive_evidence_hardlink_is_rejected(self) -> None:
        archive = self.root / ".planning/archive/project-roadmap"
        archive.mkdir(parents=True)
        outside = Path(self.temp.name) / "outside-evidence.txt"
        outside.write_text("evidence\n", encoding="utf-8")
        os.link(outside, archive / "evidence.txt")
        completed, payload = self.run_validator(operation="init")
        self.assertEqual(completed.returncode, 1)
        self.assertIn("unsafe_managed_path", self.issue_codes(payload))

    def test_init_rejects_symlink_inside_historical_namespaces(self) -> None:
        for namespace in ("snapshots", "archive"):
            with self.subTest(namespace=namespace):
                evidence = self.root / ".planning" / namespace / "record"
                evidence.mkdir(parents=True)
                outside = Path(self.temp.name) / f"outside-{namespace}.txt"
                outside.write_text("outside\n", encoding="utf-8")
                (evidence / "linked.txt").symlink_to(outside)
                completed, payload = self.run_validator(operation="init")
                (evidence / "linked.txt").unlink()
                evidence.rmdir()
                (self.root / ".planning" / namespace).rmdir()
                (self.root / ".planning").rmdir()
                self.assertEqual(completed.returncode, 1)
                self.assertIn("unsafe_managed_path", self.issue_codes(payload))

    def test_nested_historical_legacy_names_are_rejected(self) -> None:
        cases = (
            ("archive", "_repo", True),
            ("archive", "PACKET.md", False),
            ("archive", "generation-001", True),
            ("archive", "generation-history", True),
            ("archive", "g000001", True),
            ("archive", "g0042-migration", True),
            ("snapshots", "TRANSACTION.md", False),
            ("snapshots", "transactions", True),
            ("snapshots", ".staging", True),
        )
        for namespace, name, is_directory in cases:
            with self.subTest(namespace=namespace, name=name):
                record = self.root / ".planning" / namespace / "record"
                record.mkdir(parents=True)
                legacy = record / name
                if is_directory:
                    legacy.mkdir()
                else:
                    legacy.write_text("legacy\n", encoding="utf-8")
                completed, payload = self.run_validator(operation="init")
                shutil.rmtree(self.root / ".planning")
                self.assertEqual(completed.returncode, 1)
                self.assertIn("legacy_state_forbidden", self.issue_codes(payload))

    def test_valid_draft_project(self) -> None:
        self.write_project()
        before = {
            path: path.read_bytes()
            for path in self.root.rglob("*.md")
        }
        completed, payload = self.run_validator()
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(payload["status"], "valid")
        self.assertEqual(payload["plan_status"], "draft")
        self.assertIsNone(payload["active_phase"])
        self.assertEqual(before, {path: path.read_bytes() for path in self.root.rglob("*.md")})

    def test_root_task_plan_hardlink_is_rejected(self) -> None:
        self.write_project()
        os.link(self.root / "task_plan.md", Path(self.temp.name) / "outside-task-plan.md")
        completed, payload = self.run_validator()
        self.assertEqual(completed.returncode, 1)
        self.assertIn("unsafe_managed_path", self.issue_codes(payload))

    def test_valid_active_serial_project(self) -> None:
        self.write_project(plan_status="active", active_phase="phase-02")
        completed, payload = self.run_validator(operation="resume")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(payload["active_phase"], "phase-02")
        self.assertEqual(payload["phase_statuses"], {"phase-01": "closed", "phase-02": "active"})

    def test_valid_closed_project_for_archive_and_successor(self) -> None:
        self.write_project(plan_status="closed")
        for operation in ("archive", "successor"):
            completed, payload = self.run_validator(operation=operation)
            self.assertEqual(completed.returncode, 0, (operation, completed.stderr, payload))
            self.assertEqual(payload["status"], "valid")

    def test_closed_project_cannot_resume(self) -> None:
        self.write_project(plan_status="closed")
        completed, payload = self.run_validator(operation="resume")
        self.assertEqual(completed.returncode, 1)
        self.assertIn("operation_not_allowed", self.issue_codes(payload))

    def test_active_project_cannot_archive_or_initialize(self) -> None:
        self.write_project(plan_status="active")
        for operation in ("archive", "successor", "init"):
            completed, payload = self.run_validator(operation=operation)
            self.assertEqual(completed.returncode, 1)
            self.assertIn("operation_not_allowed", self.issue_codes(payload))

    def test_root_findings_or_progress_is_duplicate_truth(self) -> None:
        self.write_project()
        for name in ("findings.md", "progress.md"):
            (self.root / name).write_text("duplicate\n", encoding="utf-8")
        completed, payload = self.run_validator()
        self.assertEqual(completed.returncode, 1)
        self.assertIn("duplicate_root_truth", self.issue_codes(payload))

    def test_missing_phase_trio_is_invalid(self) -> None:
        self.write_project()
        (self.root / ".planning/plans/phase-01/findings.md").unlink()
        completed, payload = self.run_validator()
        self.assertEqual(completed.returncode, 1)
        self.assertIn("incomplete_phase_trio", self.issue_codes(payload))

    def test_phase_directory_must_contain_exactly_the_trio(self) -> None:
        self.write_project()
        (self.root / ".planning/plans/phase-01/notes.md").write_text("extra\n", encoding="utf-8")
        completed, payload = self.run_validator()
        self.assertEqual(completed.returncode, 1)
        self.assertIn("unexpected_phase_entry", self.issue_codes(payload))

    def test_unlisted_phase_directory_is_invalid(self) -> None:
        self.write_project()
        extra = self.root / ".planning/plans/phase-extra"
        extra.mkdir()
        completed, payload = self.run_validator()
        self.assertEqual(completed.returncode, 1)
        self.assertIn("unlisted_phase", self.issue_codes(payload))

    def test_active_pointer_must_resolve(self) -> None:
        self.write_project(
            plan_status="active",
            active_phase="phase-missing",
            phase_statuses={"phase-01": "draft", "phase-02": "draft"},
        )
        completed, payload = self.run_validator()
        self.assertEqual(completed.returncode, 1)
        self.assertIn("invalid_active_phase", self.issue_codes(payload))

    def test_exactly_one_phase_may_be_active(self) -> None:
        self.write_project(
            plan_status="active",
            active_phase="phase-01",
            phase_statuses={"phase-01": "active", "phase-02": "active"},
        )
        completed, payload = self.run_validator()
        self.assertEqual(completed.returncode, 1)
        self.assertIn("multiple_active_phases", self.issue_codes(payload))

    def test_serial_order_requires_closed_before_and_draft_after(self) -> None:
        self.write_project(
            plan_status="active",
            active_phase="phase-02",
            phase_statuses={"phase-01": "draft", "phase-02": "active"},
        )
        completed, payload = self.run_validator()
        self.assertEqual(completed.returncode, 1)
        self.assertIn("invalid_serial_state", self.issue_codes(payload))

    def test_legacy_lineage_packet_and_generation_fields_are_forbidden(self) -> None:
        self.write_project(root_extra=(
            "generation: 3",
            "root_plan_id: old-root",
            "initialized_from: packet:old-context",
        ))
        completed, payload = self.run_validator()
        self.assertEqual(completed.returncode, 1)
        self.assertIn("legacy_field_forbidden", self.issue_codes(payload))

    def test_legacy_staging_state_is_forbidden(self) -> None:
        self.write_project()
        staging = self.root / ".planning/plans/phase-01/.staging"
        staging.mkdir()
        completed, payload = self.run_validator()
        self.assertEqual(completed.returncode, 1)
        self.assertIn("legacy_state_forbidden", self.issue_codes(payload))

    def test_planning_top_level_rejects_repo_and_old_packet_generation_state(self) -> None:
        self.write_project()
        planning = self.root / ".planning"
        (planning / "_repo").mkdir()
        (planning / "PACKET.md").write_text("legacy\n", encoding="utf-8")
        (planning / "generation-001").mkdir()
        completed, payload = self.run_validator()
        self.assertEqual(completed.returncode, 1)
        self.assertIn("legacy_state_forbidden", self.issue_codes(payload))

    def test_planning_top_level_allows_only_owned_namespaces(self) -> None:
        self.write_project()
        (self.root / ".planning/notes.md").write_text("extra\n", encoding="utf-8")
        completed, payload = self.run_validator()
        self.assertEqual(completed.returncode, 1)
        self.assertIn("unexpected_planning_entry", self.issue_codes(payload))

    def test_canonical_root_mismatch_is_invalid(self) -> None:
        self.write_project()
        task = self.root / "task_plan.md"
        task.write_text(task.read_text().replace(str(self.root), str(self.root / "moved")), encoding="utf-8")
        completed, payload = self.run_validator()
        self.assertEqual(completed.returncode, 1)
        self.assertIn("canonical_root_mismatch", self.issue_codes(payload))

    def test_symlinked_managed_file_is_invalid(self) -> None:
        self.write_project()
        target = self.root / "outside.md"
        target.write_text("outside\n", encoding="utf-8")
        findings = self.root / ".planning/plans/phase-01/findings.md"
        findings.unlink()
        findings.symlink_to(target)
        completed, payload = self.run_validator()
        self.assertEqual(completed.returncode, 1)
        self.assertIn("unsafe_managed_path", self.issue_codes(payload))

    def test_symlinked_phase_directory_is_invalid(self) -> None:
        self.write_project()
        phase = self.root / ".planning/plans/phase-01"
        for child in phase.iterdir():
            child.unlink()
        phase.rmdir()
        outside = Path(self.temp.name) / "outside-phase"
        outside.mkdir()
        phase.symlink_to(outside, target_is_directory=True)
        completed, payload = self.run_validator()
        self.assertEqual(completed.returncode, 1)
        self.assertIn("unsafe_managed_path", self.issue_codes(payload))

    def test_draft_and_closed_must_omit_active_phase_even_when_null(self) -> None:
        for status in ("draft", "closed"):
            with self.subTest(status=status):
                self.write_project(plan_status=status, root_extra=("active_phase: null",))
                completed, payload = self.run_validator()
                for path in sorted(self.root.rglob("*"), reverse=True):
                    if path.is_file():
                        path.unlink()
                    elif path.is_dir():
                        path.rmdir()
                self.assertEqual(completed.returncode, 1)
                self.assertIn("unexpected_active_phase_field", self.issue_codes(payload))

    def test_record_must_be_root_or_listed_phase(self) -> None:
        self.write_project()
        completed, payload = self.run_validator(record=self.root / "elsewhere")
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(payload["status"], "invocation_error")

    def test_selected_phase_still_validates_whole_project(self) -> None:
        self.write_project()
        (self.root / "findings.md").write_text("duplicate\n", encoding="utf-8")
        completed, payload = self.run_validator(record=self.root / ".planning/plans/phase-01")
        self.assertEqual(completed.returncode, 1)
        self.assertIn("duplicate_root_truth", self.issue_codes(payload))

    def test_stable_reader_detects_concurrent_change(self) -> None:
        module = load_validator_module()
        path = self.root / "state.md"
        path.write_text("state\n", encoding="utf-8")
        real = os.stat(path)
        before = SimpleNamespace(
            st_dev=real.st_dev,
            st_ino=real.st_ino,
            st_size=real.st_size,
            st_mtime_ns=real.st_mtime_ns,
            st_mode=real.st_mode,
            st_nlink=real.st_nlink,
        )
        after = SimpleNamespace(
            st_dev=real.st_dev,
            st_ino=real.st_ino,
            st_size=real.st_size + 1,
            st_mtime_ns=real.st_mtime_ns + 1,
            st_mode=real.st_mode,
            st_nlink=real.st_nlink,
        )
        secure_root = module.RootAccess(self.root)
        self.addCleanup(secure_root.close)
        with mock.patch.object(module.os, "fstat", side_effect=[before, after]):
            with self.assertRaises(module.ConcurrentReadError):
                secure_root.read_stable_text(Path("state.md"))

    def test_root_anchored_reader_detects_atomic_file_replacement(self) -> None:
        module = load_validator_module()
        path = self.root / "state.md"
        replacement = self.root / "replacement.md"
        path.write_text("original\n", encoding="utf-8")
        replacement.write_text("replacement\n", encoding="utf-8")
        real_read = os.read
        swapped = False

        def read_then_replace(descriptor: int, size: int) -> bytes:
            nonlocal swapped
            data = real_read(descriptor, size)
            if data and not swapped:
                os.replace(replacement, path)
                swapped = True
            return data

        secure_root = module.RootAccess(self.root)
        self.addCleanup(secure_root.close)
        with mock.patch.object(module.os, "read", side_effect=read_then_replace):
            with self.assertRaises(module.ConcurrentReadError):
                secure_root.read_stable_text(Path("state.md"))

    def test_final_recheck_detects_replacement_after_controlled_read(self) -> None:
        module = load_validator_module()
        path = self.root / "state.md"
        replacement = self.root / "replacement.md"
        path.write_text("original\n", encoding="utf-8")
        replacement.write_text("replacement\n", encoding="utf-8")
        secure_root = module.RootAccess(self.root)
        self.addCleanup(secure_root.close)
        secure_root.read_stable_text(Path("state.md"))
        os.replace(replacement, path)
        with self.assertRaises(module.ConcurrentReadError):
            secure_root.final_recheck()

    def test_final_recheck_treats_deleted_tracked_directory_as_concurrent(self) -> None:
        module = load_validator_module()
        tracked = self.root / "tracked"
        tracked.mkdir()
        secure_root = module.RootAccess(self.root)
        self.addCleanup(secure_root.close)
        secure_root.list_directory(Path("tracked"))
        tracked.rmdir()
        with self.assertRaises(module.ConcurrentReadError):
            secure_root.final_recheck()

    def test_validator_emits_json_when_tracked_directory_disappears(self) -> None:
        module = load_validator_module()
        self.write_project()
        ephemeral = self.root / "ephemeral"
        ephemeral.mkdir()
        original_final_recheck = module.RootAccess.final_recheck

        def delete_before_final_recheck(access) -> None:
            access.list_directory(Path("ephemeral"))
            ephemeral.rmdir()
            original_final_recheck(access)

        output = io.StringIO()
        with mock.patch.object(module.RootAccess, "final_recheck", delete_before_final_recheck):
            with redirect_stdout(output):
                exit_code = module.main(
                    [
                        "--canonical-root",
                        str(self.root),
                        "--operation",
                        "inspect",
                        "--json",
                    ]
                )
        payload = json.loads(output.getvalue())
        self.assertEqual(exit_code, 1)
        self.assertEqual(payload["status"], "invalid")
        self.assertIn("concurrent_change", self.issue_codes(payload))


if __name__ == "__main__":
    unittest.main()
