#!/usr/bin/env python3
"""Behavior tests for the read-only multiline coordination audit."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("audit_multiline.py")


class AuditMultilineTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = self.root / "project"
        self.repo.mkdir()
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Codex Test")
        self.git("config", "user.email", "codex-test@example.invalid")
        (self.repo / "README.md").write_text("baseline\n", encoding="utf-8")
        self.git("add", "README.md")
        self.git("commit", "-q", "-m", "baseline")
        self.base_oid = self.git("rev-parse", "HEAD").stdout.strip()

    def git(
        self,
        *args: str,
        cwd: Path | None = None,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["GIT_OPTIONAL_LOCKS"] = "0"
        return subprocess.run(
            ["git", "-C", str(cwd or self.repo), *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            check=check,
        )

    def add_worktree(self, line_id: str) -> tuple[Path, str]:
        branch = f"coord-test/{line_id}"
        path = self.root / ".codex-worktrees" / "project" / "coord-test" / "workers" / line_id
        path.parent.mkdir(parents=True, exist_ok=True)
        self.git("worktree", "add", "-q", "-b", branch, str(path), self.base_oid)
        return path, branch

    def add_integration_worktree(self) -> tuple[Path, str]:
        branch = "coord-test/integration"
        path = self.root / ".codex-worktrees" / "project" / "coord-test" / "integration"
        path.parent.mkdir(parents=True, exist_ok=True)
        self.git("worktree", "add", "-q", "-b", branch, str(path), self.base_oid)
        return path, branch

    def invoke(
        self,
        *,
        snapshot: dict[str, object] | None = None,
        check_mode: bool = False,
        project_root: Path | None = None,
    ) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
        command = [
            sys.executable,
            str(SCRIPT),
            str(project_root or self.repo),
            "--json",
        ]
        input_text = None
        if snapshot is not None:
            command.extend(["--snapshot", "-"])
            input_text = json.dumps(snapshot)
        if check_mode:
            command.append("--check")
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        # The auditor, not the test harness, owns its read-only Git environment.
        env.pop("GIT_OPTIONAL_LOCKS", None)
        result = subprocess.run(
            command,
            input=input_text,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            check=False,
        )
        report = json.loads(result.stdout) if result.stdout.strip() else {}
        return result, report

    def invoke_raw(
        self,
        snapshot_text: str,
        *,
        check_mode: bool = True,
    ) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
        command = [
            sys.executable,
            str(SCRIPT),
            str(self.repo),
            "--json",
            "--snapshot",
            "-",
        ]
        if check_mode:
            command.append("--check")
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env.pop("GIT_OPTIONAL_LOCKS", None)
        result = subprocess.run(
            command,
            input=snapshot_text,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            check=False,
        )
        report = json.loads(result.stdout) if result.stdout.strip() else {}
        return result, report

    def snapshot(self, *lines: dict[str, object]) -> dict[str, object]:
        return {
            "schema_version": 2,
            "coordination_id": "coord-test",
            "target_base_oid": self.base_oid,
            "phase": "executing",
            "lines": list(lines),
        }

    @staticmethod
    def grant_cleanup(
        snapshot: dict[str, object], line_id: str, path: Path
    ) -> None:
        snapshot["cleanup_grant"] = {
            "line_ids": [line_id],
            "worktree_paths": [str(path.resolve())],
        }

    def executing_line(
        self,
        line_id: str,
        path: Path,
        branch: str,
        *,
        depends_on: list[str] | None = None,
        write_set: list[str] | None = None,
        resource_claims: list[dict[str, str]] | None = None,
        bindings: list[dict[str, str]] | None = None,
        output_paths: list[str] | None = None,
        location_source: str = "user",
    ) -> dict[str, object]:
        return {
            "id": line_id,
            "phase": "executing",
            "worker_task_id": f"task-{line_id}",
            "worker_state": "working",
            "coordinator_decision": "pending",
            "depends_on": depends_on or [],
            "workspace": {
                "mode": "writer",
                "state": "dirty",
                "path": str(path),
                "branch": branch,
                "head_oid": self.git("rev-parse", "HEAD", cwd=path).stdout.strip(),
                "location_source": location_source,
                "ownership": "coordination",
            },
            "write_set": write_set or [f"src/{line_id}"],
            "resource_claims": resource_claims or [],
            "project_local_bindings": bindings or [],
            "output_paths": output_paths or [],
        }

    @staticmethod
    def finding_codes(report: dict[str, object]) -> set[str]:
        findings = report.get("findings", [])
        return {
            str(item.get("code"))
            for item in findings
            if isinstance(item, dict)
        }

    def repository_fingerprint(self) -> dict[str, object]:
        git_dir = Path(self.git("rev-parse", "--git-dir").stdout.strip())
        if not git_dir.is_absolute():
            git_dir = (self.repo / git_dir).resolve()
        index = git_dir / "index"
        cherry_pick_head = git_dir / "CHERRY_PICK_HEAD"
        return {
            "head": self.git("rev-parse", "HEAD").stdout,
            "refs": self.git("show-ref", check=False).stdout,
            "worktrees": self.git("worktree", "list", "--porcelain").stdout,
            "index_bytes": index.read_bytes() if index.exists() else None,
            "index_mtime_ns": index.stat().st_mtime_ns if index.exists() else None,
            "cherry_pick_head": (
                cherry_pick_head.read_bytes() if cherry_pick_head.exists() else None
            ),
        }

    def test_dirty_repo_without_snapshot_is_inventory_not_registry_risk(self) -> None:
        (self.repo / "README.md").write_text("dirty\n", encoding="utf-8")

        result, report = self.invoke()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(report["snapshot"]["provided"])
        messages = "\n".join(
            str(item.get("message")) for item in report.get("findings", [])
        )
        self.assertNotIn("registry", messages.lower())
        self.assertNotIn("not attached", messages.lower())

    def test_audit_from_linked_worktree_reports_primary_project_root(self) -> None:
        path, _ = self.add_worktree("line-a")

        result, report = self.invoke(project_root=path)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(report["repository"]["project_root"], str(self.repo.resolve()))

    def test_planned_line_may_omit_worker_and_workspace(self) -> None:
        line = {"id": "line-a", "phase": "planned", "depends_on": []}

        result, report = self.invoke(snapshot=self.snapshot(line), check_mode=True)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(report["summary"]["errors"], 0)

    def test_running_line_branch_mismatch_is_an_error(self) -> None:
        path, branch = self.add_worktree("line-a")
        line = self.executing_line("line-a", path, branch)
        line["workspace"]["branch"] = "wrong-branch"

        result, report = self.invoke(snapshot=self.snapshot(line), check_mode=True)

        self.assertEqual(result.returncode, 1)
        self.assertIn("workspace_branch_mismatch", self.finding_codes(report))

    def test_running_line_head_mismatch_is_an_error(self) -> None:
        path, branch = self.add_worktree("line-a")
        line = self.executing_line("line-a", path, branch)
        line["workspace"]["head_oid"] = "f" * 40

        result, report = self.invoke(snapshot=self.snapshot(line), check_mode=True)

        self.assertEqual(result.returncode, 1)
        self.assertIn("workspace_head_mismatch", self.finding_codes(report))

    def test_executing_line_requires_worker_and_workspace(self) -> None:
        line = {"id": "line-a", "phase": "executing", "depends_on": []}

        result, report = self.invoke(snapshot=self.snapshot(line), check_mode=True)

        self.assertEqual(result.returncode, 1)
        codes = self.finding_codes(report)
        self.assertIn("executing_worker_missing", codes)
        self.assertIn("executing_workspace_missing", codes)

    def test_executing_reader_can_bind_a_revision_without_a_worktree(self) -> None:
        line = {
            "id": "line-read",
            "phase": "executing",
            "worker_task_id": "task-line-read",
            "worker_state": "working",
            "coordinator_decision": "pending",
            "depends_on": [],
            "workspace": {
                "mode": "reader",
                "state": "clean",
                "revision_oid": self.base_oid,
            },
            "write_set": [],
            "resource_claims": [],
            "project_local_bindings": [],
            "output_paths": [],
        }

        result, report = self.invoke(snapshot=self.snapshot(line), check_mode=True)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(report["summary"]["errors"], 0)

    def test_duplicate_line_and_worker_task_ids_are_errors(self) -> None:
        path_a, branch_a = self.add_worktree("line-a")
        path_b, branch_b = self.add_worktree("line-b")
        line_a = self.executing_line("line-a", path_a, branch_a)
        line_b = self.executing_line("line-a", path_b, branch_b)
        line_b["worker_task_id"] = line_a["worker_task_id"]

        result, report = self.invoke(
            snapshot=self.snapshot(line_a, line_b), check_mode=True
        )

        self.assertEqual(result.returncode, 1)
        codes = self.finding_codes(report)
        self.assertIn("duplicate_line_id", codes)
        self.assertIn("duplicate_worker_task_id", codes)

    def test_dependency_cycle_is_an_error(self) -> None:
        lines = (
            {"id": "line-a", "phase": "planned", "depends_on": ["line-b"]},
            {"id": "line-b", "phase": "planned", "depends_on": ["line-a"]},
        )

        result, report = self.invoke(snapshot=self.snapshot(*lines), check_mode=True)

        self.assertEqual(result.returncode, 1)
        self.assertIn("dependency_cycle", self.finding_codes(report))

    def test_unknown_dependency_and_invalid_phase_are_errors(self) -> None:
        line = {"id": "line-a", "phase": "invented", "depends_on": ["missing"]}

        result, report = self.invoke(snapshot=self.snapshot(line), check_mode=True)

        self.assertEqual(result.returncode, 1)
        codes = self.finding_codes(report)
        self.assertIn("invalid_line_phase", codes)
        self.assertIn("unknown_dependency", codes)

    def test_invalid_worker_workspace_and_resource_states_are_errors(self) -> None:
        path, branch = self.add_worktree("line-a")
        line = self.executing_line(
            "line-a",
            path,
            branch,
            resource_claims=[{"id": "gpu:0", "mode": "maybe"}],
        )
        line["worker_state"] = "teleporting"
        line["workspace"]["state"] = "vanished"

        result, report = self.invoke(snapshot=self.snapshot(line), check_mode=True)

        self.assertEqual(result.returncode, 1)
        codes = self.finding_codes(report)
        self.assertIn("invalid_worker_state", codes)
        self.assertIn("invalid_workspace_state", codes)
        self.assertIn("invalid_resource_mode", codes)

    def test_workspace_path_must_be_an_actual_worktree(self) -> None:
        path, branch = self.add_worktree("line-a")
        line = self.executing_line("line-a", path, branch)
        line["workspace"]["path"] = str(self.root / "missing-worktree")

        result, report = self.invoke(snapshot=self.snapshot(line), check_mode=True)

        self.assertEqual(result.returncode, 1)
        self.assertIn("workspace_not_found", self.finding_codes(report))

    def test_two_active_writers_cannot_share_a_worktree(self) -> None:
        path, branch = self.add_worktree("shared")
        lines = (
            self.executing_line("line-a", path, branch),
            self.executing_line("line-b", path, branch),
        )

        result, report = self.invoke(snapshot=self.snapshot(*lines), check_mode=True)

        self.assertEqual(result.returncode, 1)
        self.assertIn("workspace_multiple_writers", self.finding_codes(report))

    def test_active_write_sets_and_exclusive_resources_cannot_overlap(self) -> None:
        path_a, branch_a = self.add_worktree("line-a")
        path_b, branch_b = self.add_worktree("line-b")
        lines = (
            self.executing_line(
                "line-a",
                path_a,
                branch_a,
                write_set=["src"],
                resource_claims=[{"id": "gpu:0", "mode": "exclusive"}],
            ),
            self.executing_line(
                "line-b",
                path_b,
                branch_b,
                write_set=["src/module.py"],
                resource_claims=[{"id": "gpu:0", "mode": "shared_read"}],
            ),
        )

        result, report = self.invoke(snapshot=self.snapshot(*lines), check_mode=True)

        self.assertEqual(result.returncode, 1)
        codes = self.finding_codes(report)
        self.assertIn("write_set_overlap", codes)
        self.assertIn("resource_claim_overlap", codes)

    def test_disjoint_writers_and_shared_read_resources_are_valid(self) -> None:
        path_a, branch_a = self.add_worktree("line-a")
        path_b, branch_b = self.add_worktree("line-b")
        lines = (
            self.executing_line(
                "line-a",
                path_a,
                branch_a,
                write_set=["src/a"],
                resource_claims=[{"id": "dataset:raw", "mode": "shared_read"}],
                output_paths=["artifacts/a"],
            ),
            self.executing_line(
                "line-b",
                path_b,
                branch_b,
                write_set=["src/ab"],
                resource_claims=[{"id": "dataset:raw", "mode": "shared_read"}],
                output_paths=["artifacts/b"],
            ),
        )

        result, report = self.invoke(snapshot=self.snapshot(*lines), check_mode=True)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(report["summary"]["errors"], 0)

    def test_output_paths_cannot_overlap(self) -> None:
        path_a, branch_a = self.add_worktree("line-a")
        path_b, branch_b = self.add_worktree("line-b")
        lines = (
            self.executing_line("line-a", path_a, branch_a, output_paths=["runs"]),
            self.executing_line(
                "line-b", path_b, branch_b, output_paths=["runs/line-b"]
            ),
        )

        result, report = self.invoke(snapshot=self.snapshot(*lines), check_mode=True)

        self.assertEqual(result.returncode, 1)
        self.assertIn("output_path_overlap", self.finding_codes(report))

    def test_unreachable_checkpoint_is_an_error(self) -> None:
        line = {
            "id": "line-a",
            "phase": "integrating",
            "depends_on": [],
            "checkpoint_oid": "f" * 40,
        }

        result, report = self.invoke(snapshot=self.snapshot(line), check_mode=True)

        self.assertEqual(result.returncode, 1)
        self.assertIn("checkpoint_unreachable", self.finding_codes(report))

    def test_oid_fields_require_full_immutable_object_ids(self) -> None:
        snapshot = self.snapshot(
            {"id": "line-a", "phase": "planned", "depends_on": []}
        )
        snapshot["target_base_oid"] = "main"

        result, report = self.invoke(snapshot=snapshot, check_mode=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("target_base_unreachable", self.finding_codes(report))

        snapshot["target_base_oid"] = "\0"
        result, report = self.invoke(snapshot=snapshot, check_mode=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("target_base_unreachable", self.finding_codes(report))

    def test_checkpoint_and_integration_mapping_are_branch_scoped(self) -> None:
        worker_path, worker_branch = self.add_worktree("line-a")
        integration_path, integration_branch = self.add_integration_worktree()
        (worker_path / "line-a.txt").write_text("worker result\n", encoding="utf-8")
        self.git("add", "line-a.txt", cwd=worker_path)
        self.git("commit", "-q", "-m", "worker checkpoint", cwd=worker_path)
        checkpoint = self.git("rev-parse", "HEAD", cwd=worker_path).stdout.strip()
        (integration_path / "integration.txt").write_text(
            "integration base\n", encoding="utf-8"
        )
        self.git("add", "integration.txt", cwd=integration_path)
        self.git("commit", "-q", "-m", "integration base", cwd=integration_path)
        integration_base = self.git(
            "rev-parse", "HEAD", cwd=integration_path
        ).stdout.strip()
        self.git("cherry-pick", checkpoint, cwd=integration_path)
        integrated = self.git("rev-parse", "HEAD", cwd=integration_path).stdout.strip()
        line = self.executing_line("line-a", worker_path, worker_branch)
        line.update(
            {
                "phase": "closed",
                "worker_state": "stopped",
                "coordinator_decision": "pass",
                "checkpoint_oid": checkpoint,
            }
        )
        line["workspace"]["head_oid"] = checkpoint
        line["workspace"]["state"] = "cleanup_candidate"
        snapshot = self.snapshot(line)
        snapshot["integration"] = {
            "workspace": {
                "path": str(integration_path),
                "branch": integration_branch,
                "head_oid": integrated,
                "location_source": "repo_sibling",
            },
            "records": [
                {
                    "line_id": "line-a",
                    "source_oid": checkpoint,
                    "integrated_oid": integrated,
                    "method": "cherry-pick",
                }
            ],
        }
        self.grant_cleanup(snapshot, "line-a", worker_path)

        result, report = self.invoke(snapshot=snapshot, check_mode=True)
        self.assertEqual(result.returncode, 0, result.stderr)

        snapshot["integration"]["records"][0]["integrated_oid"] = checkpoint
        result, report = self.invoke(snapshot=snapshot, check_mode=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("integrated_oid_not_on_branch", self.finding_codes(report))

        snapshot["integration"]["records"][0]["integrated_oid"] = integration_base
        result, report = self.invoke(snapshot=snapshot, check_mode=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("integration_patch_mismatch", self.finding_codes(report))

    def test_manual_conflict_resolution_requires_manual_method_and_preserved_source(
        self,
    ) -> None:
        (self.repo / "shared.txt").write_text(
            "coordinator_slot=unset\nworker_slot=unset\n",
            encoding="utf-8",
        )
        self.git("add", "shared.txt")
        self.git("commit", "-q", "-m", "shared baseline")
        self.base_oid = self.git("rev-parse", "HEAD").stdout.strip()

        worker_path, worker_branch = self.add_worktree("line-a")
        integration_path, integration_branch = self.add_integration_worktree()

        (worker_path / "shared.txt").write_text(
            "coordinator_slot=unset\nworker_slot=ready\n",
            encoding="utf-8",
        )
        self.git("add", "shared.txt", cwd=worker_path)
        self.git("commit", "-q", "-m", "worker checkpoint", cwd=worker_path)
        checkpoint = self.git("rev-parse", "HEAD", cwd=worker_path).stdout.strip()

        (integration_path / "shared.txt").write_text(
            "coordinator_slot=ready\nworker_slot=unset\n",
            encoding="utf-8",
        )
        self.git("add", "shared.txt", cwd=integration_path)
        self.git("commit", "-q", "-m", "integration fixture", cwd=integration_path)

        conflicted = self.git(
            "cherry-pick",
            checkpoint,
            cwd=integration_path,
            check=False,
        )
        self.assertNotEqual(conflicted.returncode, 0)
        self.assertIn("CONFLICT", conflicted.stdout + conflicted.stderr)
        (integration_path / "shared.txt").write_text(
            "coordinator_slot=ready\nworker_slot=ready\n",
            encoding="utf-8",
        )
        self.git("add", "shared.txt", cwd=integration_path)
        self.git(
            "-c",
            "core.editor=true",
            "cherry-pick",
            "--continue",
            cwd=integration_path,
        )
        integrated = self.git(
            "rev-parse", "HEAD", cwd=integration_path
        ).stdout.strip()

        line = self.executing_line("line-a", worker_path, worker_branch)
        line.update(
            {
                "phase": "closed",
                "worker_state": "stopped",
                "coordinator_decision": "pass",
                "checkpoint_oid": checkpoint,
                "preservation_ref": f"refs/heads/{worker_branch}",
            }
        )
        line["workspace"]["head_oid"] = checkpoint
        line["workspace"]["state"] = "cleanup_candidate"
        snapshot = self.snapshot(line)
        snapshot["integration"] = {
            "workspace": {
                "path": str(integration_path),
                "branch": integration_branch,
                "head_oid": integrated,
                "location_source": "repo_sibling",
            },
            "records": [
                {
                    "line_id": "line-a",
                    "source_oid": checkpoint,
                    "integrated_oid": integrated,
                    "method": "cherry-pick",
                }
            ],
        }
        self.grant_cleanup(snapshot, "line-a", worker_path)

        result, report = self.invoke(snapshot=snapshot, check_mode=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("integration_patch_mismatch", self.finding_codes(report))

        snapshot["integration"]["records"][0]["method"] = "manual"
        del line["preservation_ref"]
        result, report = self.invoke(snapshot=snapshot, check_mode=True)
        self.assertEqual(result.returncode, 1)
        codes = self.finding_codes(report)
        self.assertIn("integration_equivalence_unverified", codes)
        self.assertIn("cleanup_checkpoint_unpreserved", codes)

        line["preservation_ref"] = f"refs/heads/{worker_branch}"
        result, report = self.invoke(snapshot=snapshot, check_mode=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(report["summary"]["errors"], 0)
        self.assertIn(
            "integration_equivalence_unverified", self.finding_codes(report)
        )

    def test_checkpoint_must_belong_to_worker_branch_and_target_base(self) -> None:
        worker_path, worker_branch = self.add_worktree("line-a")
        orphan = self.root / "orphan"
        orphan.mkdir()
        self.git("init", "-q", "-b", "orphan", cwd=orphan)
        self.git("config", "user.name", "Codex Test", cwd=orphan)
        self.git("config", "user.email", "codex-test@example.invalid", cwd=orphan)
        (orphan / "orphan.txt").write_text("orphan\n", encoding="utf-8")
        self.git("add", "orphan.txt", cwd=orphan)
        self.git("commit", "-q", "-m", "orphan", cwd=orphan)
        orphan_oid = self.git("rev-parse", "HEAD", cwd=orphan).stdout.strip()
        self.git("fetch", "-q", str(orphan), orphan_oid)
        line = self.executing_line("line-a", worker_path, worker_branch)
        line["phase"] = "integrating"
        line["checkpoint_oid"] = orphan_oid

        result, report = self.invoke(snapshot=self.snapshot(line), check_mode=True)

        self.assertEqual(result.returncode, 1)
        codes = self.finding_codes(report)
        self.assertIn("checkpoint_not_on_worker_branch", codes)
        self.assertIn("checkpoint_not_based_on_target", codes)

    def test_immutable_ignored_project_data_symlink_is_valid(self) -> None:
        (self.repo / ".gitignore").write_text("/data/raw\n", encoding="utf-8")
        self.git("add", ".gitignore")
        self.git("commit", "-q", "-m", "ignore project data")
        self.base_oid = self.git("rev-parse", "HEAD").stdout.strip()
        source = self.repo / "data" / "raw"
        source.mkdir(parents=True)
        (source / "manifest.txt").write_text("v1\n", encoding="utf-8")
        path, branch = self.add_worktree("line-a")
        (path / "data").mkdir()
        (path / "data" / "raw").symlink_to(source, target_is_directory=True)
        binding = {
            "relative_path": "data/raw",
            "source_path": str(source),
            "mutability": "immutable",
            "binding": "symlink",
        }
        line = self.executing_line("line-a", path, branch, bindings=[binding])

        result, report = self.invoke(snapshot=self.snapshot(line), check_mode=True)

        self.assertEqual(result.returncode, 0, result.stderr)
        binding_codes = {
            code for code in self.finding_codes(report) if code.startswith("binding_")
        }
        self.assertEqual(binding_codes, set())
        self.assertTrue(
            any("immutable" in item.lower() for item in report["limitations"])
        )

    def test_invalid_binding_paths_and_targets_are_errors(self) -> None:
        source = self.repo / "shared-data"
        source.mkdir()
        path, branch = self.add_worktree("line-a")
        outside = self.root / "outside-data"
        outside.mkdir()
        bindings = [
            {
                "relative_path": "../escape",
                "source_path": str(source),
                "mutability": "immutable",
                "binding": "symlink",
            },
            {
                "relative_path": "external",
                "source_path": str(outside),
                "mutability": "immutable",
                "binding": "symlink",
            },
            {
                "relative_path": "missing",
                "source_path": str(self.repo / "not-there"),
                "mutability": "immutable",
                "binding": "symlink",
            },
            {
                "relative_path": "wrong-target",
                "source_path": str(source),
                "mutability": "immutable",
                "binding": "symlink",
            },
        ]
        (path / "external").symlink_to(outside, target_is_directory=True)
        (path / "missing").symlink_to(self.repo / "not-there")
        wrong = self.repo / "wrong-data"
        wrong.mkdir()
        (path / "wrong-target").symlink_to(wrong, target_is_directory=True)
        line = self.executing_line("line-a", path, branch, bindings=bindings)

        result, report = self.invoke(snapshot=self.snapshot(line), check_mode=True)

        self.assertEqual(result.returncode, 1)
        codes = self.finding_codes(report)
        self.assertIn("binding_relative_path_invalid", codes)
        self.assertIn("binding_source_outside_project", codes)
        self.assertIn("binding_source_missing", codes)
        self.assertIn("binding_target_mismatch", codes)

    def test_unignored_binding_is_an_error(self) -> None:
        source = self.repo / "shared-data"
        source.mkdir()
        path, branch = self.add_worktree("line-a")
        (path / "shared-data").symlink_to(source, target_is_directory=True)
        binding = {
            "relative_path": "shared-data",
            "source_path": str(source),
            "mutability": "immutable",
            "binding": "symlink",
        }
        line = self.executing_line("line-a", path, branch, bindings=[binding])

        result, report = self.invoke(snapshot=self.snapshot(line), check_mode=True)

        self.assertEqual(result.returncode, 1)
        self.assertIn("binding_not_ignored", self.finding_codes(report))

    def test_binding_must_not_shadow_a_tracked_project_path(self) -> None:
        tracked = self.repo / "data" / "schema.json"
        tracked.parent.mkdir()
        tracked.write_text("{}\n", encoding="utf-8")
        self.git("add", "data/schema.json")
        self.git("commit", "-q", "-m", "track schema")
        self.base_oid = self.git("rev-parse", "HEAD").stdout.strip()
        source = self.repo / "shared-schema.json"
        source.write_text("{}\n", encoding="utf-8")
        path, branch = self.add_worktree("line-a")
        binding = {
            "relative_path": "data/schema.json",
            "source_path": str(source),
            "mutability": "immutable",
            "binding": "symlink",
        }
        line = self.executing_line("line-a", path, branch, bindings=[binding])

        result, report = self.invoke(snapshot=self.snapshot(line), check_mode=True)

        self.assertEqual(result.returncode, 1)
        self.assertIn("binding_shadows_tracked_path", self.finding_codes(report))

    def test_binding_source_cannot_be_tracked_project_content(self) -> None:
        (self.repo / ".gitignore").write_text("/shared-readme\n", encoding="utf-8")
        self.git("add", ".gitignore")
        self.git("commit", "-q", "-m", "ignore binding destination")
        self.base_oid = self.git("rev-parse", "HEAD").stdout.strip()
        path, branch = self.add_worktree("line-a")
        (path / "shared-readme").symlink_to(self.repo / "README.md")
        binding = {
            "relative_path": "shared-readme",
            "source_path": str(self.repo / "README.md"),
            "mutability": "immutable",
            "binding": "symlink",
        }
        line = self.executing_line("line-a", path, branch, bindings=[binding])

        result, report = self.invoke(snapshot=self.snapshot(line), check_mode=True)

        self.assertEqual(result.returncode, 1)
        self.assertIn("binding_source_tracked", self.finding_codes(report))

    def test_mutable_binding_cannot_be_shared_by_active_writers(self) -> None:
        source = self.repo / "scratch-data"
        source.mkdir()
        path_a, branch_a = self.add_worktree("line-a")
        path_b, branch_b = self.add_worktree("line-b")
        bindings = []
        lines = []
        for line_id, path, branch in (
            ("line-a", path_a, branch_a),
            ("line-b", path_b, branch_b),
        ):
            relative = "scratch-data"
            (path / relative).symlink_to(source, target_is_directory=True)
            binding = {
                "relative_path": relative,
                "source_path": str(source),
                "mutability": "mutable",
                "binding": "symlink",
            }
            bindings.append(binding)
            lines.append(self.executing_line(line_id, path, branch, bindings=[binding]))

        result, report = self.invoke(snapshot=self.snapshot(*lines), check_mode=True)

        self.assertEqual(result.returncode, 1)
        self.assertIn("binding_shared_writable_target", self.finding_codes(report))

    def test_dirty_cleanup_candidate_is_rejected(self) -> None:
        path, branch = self.add_worktree("line-a")
        (path / "README.md").write_text("dirty cleanup\n", encoding="utf-8")
        line = self.executing_line("line-a", path, branch)
        line["phase"] = "closed"
        line["worker_state"] = "stopped"
        line["coordinator_decision"] = "pass"
        line["workspace"]["state"] = "cleanup_candidate"

        snapshot = self.snapshot(line)
        self.grant_cleanup(snapshot, "line-a", path)
        result, report = self.invoke(snapshot=snapshot, check_mode=True)

        self.assertEqual(result.returncode, 1)
        self.assertIn("cleanup_dirty_worktree", self.finding_codes(report))

    def test_clean_unpreserved_checkpoint_cannot_be_cleanup_candidate(self) -> None:
        path, branch = self.add_worktree("line-a")
        (path / "line-a.txt").write_text("result\n", encoding="utf-8")
        self.git("add", "line-a.txt", cwd=path)
        self.git("commit", "-q", "-m", "line result", cwd=path)
        checkpoint = self.git("rev-parse", "HEAD", cwd=path).stdout.strip()
        line = self.executing_line("line-a", path, branch)
        line["phase"] = "closed"
        line["worker_state"] = "stopped"
        line["coordinator_decision"] = "pass"
        line["checkpoint_oid"] = checkpoint
        line["workspace"]["head_oid"] = checkpoint
        line["workspace"]["state"] = "cleanup_candidate"

        snapshot = self.snapshot(line)
        self.grant_cleanup(snapshot, "line-a", path)
        result, report = self.invoke(snapshot=snapshot, check_mode=True)

        self.assertEqual(result.returncode, 1)
        self.assertIn("cleanup_checkpoint_unpreserved", self.finding_codes(report))

    def test_working_worker_cannot_be_a_cleanup_candidate(self) -> None:
        path, branch = self.add_worktree("line-a")
        (path / "line-a.txt").write_text("result\n", encoding="utf-8")
        self.git("add", "line-a.txt", cwd=path)
        self.git("commit", "-q", "-m", "line result", cwd=path)
        checkpoint = self.git("rev-parse", "HEAD", cwd=path).stdout.strip()
        line = self.executing_line("line-a", path, branch)
        line["phase"] = "closed"
        line["coordinator_decision"] = "pass"
        line["checkpoint_oid"] = checkpoint
        line["preservation_ref"] = f"refs/heads/{branch}"
        line["workspace"]["head_oid"] = checkpoint
        line["workspace"]["state"] = "cleanup_candidate"

        snapshot = self.snapshot(line)
        self.grant_cleanup(snapshot, "line-a", path)
        result, report = self.invoke(snapshot=snapshot, check_mode=True)

        self.assertEqual(result.returncode, 1)
        self.assertIn("cleanup_worker_active", self.finding_codes(report))

    def test_cleanup_candidate_requires_an_exact_grant(self) -> None:
        path, branch = self.add_worktree("line-a")
        line = self.executing_line("line-a", path, branch)
        line["phase"] = "closed"
        line["worker_state"] = "stopped"
        line["coordinator_decision"] = "pass"
        line["checkpoint_oid"] = self.base_oid
        line["preservation_ref"] = f"refs/heads/{branch}"
        line["workspace"]["state"] = "cleanup_candidate"

        result, report = self.invoke(snapshot=self.snapshot(line), check_mode=True)

        self.assertEqual(result.returncode, 1)
        self.assertIn("cleanup_not_granted", self.finding_codes(report))

    def test_primary_worktree_cannot_be_a_cleanup_candidate(self) -> None:
        line = {
            "id": "line-main",
            "phase": "closed",
            "worker_task_id": "task-main",
            "worker_state": "stopped",
            "coordinator_decision": "pass",
            "depends_on": [],
            "checkpoint_oid": self.base_oid,
            "preservation_ref": "refs/heads/main",
            "workspace": {
                "mode": "writer",
                "state": "cleanup_candidate",
                "path": str(self.repo),
                "branch": "main",
                "head_oid": self.base_oid,
                "location_source": "user",
                "ownership": "coordination",
            },
            "write_set": [],
            "resource_claims": [],
            "project_local_bindings": [],
            "output_paths": [],
        }
        snapshot = self.snapshot(line)
        self.grant_cleanup(snapshot, "line-main", self.repo)

        result, report = self.invoke(snapshot=snapshot, check_mode=True)

        self.assertEqual(result.returncode, 1)
        self.assertIn("cleanup_primary_worktree", self.finding_codes(report))

    def test_cleanup_rejects_interrupted_operation_and_active_dependent(self) -> None:
        path_a, branch_a = self.add_worktree("line-a")
        path_b, branch_b = self.add_worktree("line-b")
        git_dir = Path(self.git("rev-parse", "--git-dir", cwd=path_a).stdout.strip())
        if not git_dir.is_absolute():
            git_dir = (path_a / git_dir).resolve()
        (git_dir / "CHERRY_PICK_HEAD").write_text(
            self.base_oid + "\n", encoding="utf-8"
        )
        line_a = self.executing_line("line-a", path_a, branch_a)
        line_a["phase"] = "closed"
        line_a["worker_state"] = "stopped"
        line_a["coordinator_decision"] = "pass"
        line_a["checkpoint_oid"] = self.base_oid
        line_a["preservation_ref"] = f"refs/heads/{branch_a}"
        line_a["workspace"]["state"] = "cleanup_candidate"
        line_b = self.executing_line(
            "line-b", path_b, branch_b, depends_on=["line-a"]
        )
        snapshot = self.snapshot(line_a, line_b)
        self.grant_cleanup(snapshot, "line-a", path_a)

        result, report = self.invoke(snapshot=snapshot, check_mode=True)

        self.assertEqual(result.returncode, 1)
        codes = self.finding_codes(report)
        self.assertIn("cleanup_operation_in_progress", codes)
        self.assertIn("cleanup_active_dependent", codes)

    def test_coordination_and_line_ids_cannot_escape_layout(self) -> None:
        path, branch = self.add_worktree("line-a")
        line = self.executing_line(
            "../line-a", path, branch, location_source="repo_sibling"
        )
        snapshot = self.snapshot(line)
        snapshot["coordination_id"] = "../escape"

        result, report = self.invoke(snapshot=snapshot, check_mode=True)

        self.assertEqual(result.returncode, 1)
        codes = self.finding_codes(report)
        self.assertIn("coordination_id_invalid", codes)
        self.assertIn("line_id_invalid", codes)

    def test_repo_sibling_worker_layout_is_valid_and_drift_is_reported(self) -> None:
        path, branch = self.add_worktree("line-a")
        line = self.executing_line(
            "line-a", path, branch, location_source="repo_sibling"
        )

        result, report = self.invoke(snapshot=self.snapshot(line), check_mode=True)
        self.assertEqual(result.returncode, 0, result.stderr)

        line["workspace"]["path"] = str(self.repo)
        line["workspace"]["branch"] = "main"
        line["workspace"]["head_oid"] = self.git("rev-parse", "HEAD").stdout.strip()
        result, report = self.invoke(snapshot=self.snapshot(line), check_mode=True)

        self.assertEqual(result.returncode, 1)
        self.assertIn("workspace_layout_mismatch", self.finding_codes(report))

    def test_interrupted_cherry_pick_is_reported_without_repo_writes(self) -> None:
        git_dir = Path(self.git("rev-parse", "--git-dir").stdout.strip())
        if not git_dir.is_absolute():
            git_dir = (self.repo / git_dir).resolve()
        (git_dir / "CHERRY_PICK_HEAD").write_text(self.base_oid + "\n", encoding="utf-8")
        working_before = {
            path.relative_to(self.repo): path.read_bytes()
            for path in self.repo.rglob("*")
            if path.is_file() and ".git" not in path.parts
        }
        repository_before = self.repository_fingerprint()

        result, report = self.invoke()

        working_after = {
            path.relative_to(self.repo): path.read_bytes()
            for path in self.repo.rglob("*")
            if path.is_file() and ".git" not in path.parts
        }
        repository_after = self.repository_fingerprint()
        self.assertEqual(result.returncode, 0, result.stderr)
        current = next(
            item for item in report["worktrees"] if item["path"] == str(self.repo.resolve())
        )
        self.assertIn("cherry_pick", current["operations"])
        self.assertEqual(working_before, working_after)
        self.assertEqual(repository_before, repository_after)

    def test_audit_does_not_execute_repository_fsmonitor(self) -> None:
        sentinel = self.root / "fsmonitor-executed"
        hook = self.root / "fsmonitor-hook.sh"
        hook.write_text(
            f"#!/bin/sh\ntouch '{sentinel}'\nexit 0\n", encoding="utf-8"
        )
        hook.chmod(0o755)
        self.git("config", "core.fsmonitor", str(hook))

        result, _ = self.invoke()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(sentinel.exists())

    def test_malformed_snapshot_is_structured_and_does_not_echo_unknown_fields(self) -> None:
        result, report = self.invoke_raw("{not-json")

        self.assertEqual(result.returncode, 1)
        self.assertIn("snapshot_parse_error", self.finding_codes(report))

        snapshot = self.snapshot({"id": "line-a", "phase": "planned", "depends_on": []})
        snapshot["private_sentinel"] = "DO-NOT-ECHO"
        result, report = self.invoke(snapshot=snapshot, check_mode=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("DO-NOT-ECHO", result.stdout)


if __name__ == "__main__":
    unittest.main()
