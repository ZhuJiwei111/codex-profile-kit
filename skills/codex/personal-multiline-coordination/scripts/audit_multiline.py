#!/usr/bin/env python3
"""Read-only reconciliation audit for multiline worker/worktree coordination."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
from typing import Any, Iterable


AUDIT_VERSION = 2
SNAPSHOT_VERSION = 2
LINE_PHASES = {
    "planned",
    "ready",
    "executing",
    "waiting_intake",
    "integrating",
    "verified",
    "closed",
    "blocked",
    "cancelled",
}
ACTIVE_LINE_PHASES = {"executing", "waiting_intake", "integrating"}
WORKER_STATES = {
    "queued",
    "working",
    "waiting",
    "reported",
    "stopped",
    "failed",
    "unavailable",
}
COORDINATOR_DECISIONS = {
    "pending",
    "pass",
    "no-go",
    "needs-more-evidence",
    "blocked",
}
WORKSPACE_STATES = {
    "prepared",
    "clean",
    "dirty",
    "handed_off",
    "cleanup_candidate",
    "preserved",
}
WORKSPACE_MODES = {"writer", "reader"}
LOCATION_SOURCES = {
    "user",
    "repo_instructions",
    "app_native",
    "host_local",
    "repo_sibling",
}
RESOURCE_MODES = {"exclusive", "shared_read"}
INTEGRATION_METHODS = {"cherry-pick", "merge", "rebase", "squash", "manual"}
WORKSPACE_OWNERS = {"coordination", "external"}
MAX_LINES = 1000
SAFE_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
SNAPSHOT_PHASES = {
    "designing",
    "ready",
    "executing",
    "integrating",
    "verifying",
    "closed",
    "blocked",
}


def git_environment() -> dict[str, str]:
    env = os.environ.copy()
    env["GIT_OPTIONAL_LOCKS"] = "0"
    env.setdefault("LC_ALL", "C.UTF-8")
    return env


def git_command(cwd: Path, args: list[str]) -> list[str]:
    return [
        "git",
        "-C",
        str(cwd),
        "-c",
        "core.fsmonitor=false",
        "-c",
        "core.untrackedCache=false",
        "-c",
        "core.hooksPath=/dev/null",
        *args,
    ]


def run_git(args: list[str], cwd: Path) -> tuple[int, str, str]:
    try:
        process = subprocess.run(
            git_command(cwd, args),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=git_environment(),
            check=False,
            timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired, UnicodeError, ValueError) as exc:
        return 124, "", f"{type(exc).__name__}: {exc}"
    return process.returncode, process.stdout.rstrip("\n"), process.stderr.rstrip("\n")


def within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def resolve_git_path(raw: str, cwd: Path) -> Path:
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = cwd / candidate
    return candidate.resolve()


def resolve_project_root(path: Path) -> tuple[Path | None, str | None]:
    code, output, error = run_git(["rev-parse", "--show-toplevel"], path)
    if code or not output:
        return None, error or "not a Git worktree"
    return Path(output).resolve(), None


def parse_worktree_porcelain(text: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for raw_line in text.splitlines():
        if not raw_line:
            if current is not None:
                records.append(current)
                current = None
            continue
        if raw_line.startswith("worktree "):
            if current is not None:
                records.append(current)
            current = {"path": raw_line[len("worktree ") :]}
            continue
        if current is None:
            continue
        key, separator, value = raw_line.partition(" ")
        current[key] = value if separator else True
    if current is not None:
        records.append(current)
    return records


def worktree_git_dir(path: Path) -> Path | None:
    code, output, _ = run_git(["rev-parse", "--git-dir"], path)
    if code or not output:
        return None
    return resolve_git_path(output, path)


def worktree_operations(path: Path) -> list[str]:
    git_dir = worktree_git_dir(path)
    if git_dir is None:
        return []
    markers = {
        "merge": git_dir / "MERGE_HEAD",
        "cherry_pick": git_dir / "CHERRY_PICK_HEAD",
        "revert": git_dir / "REVERT_HEAD",
        "bisect": git_dir / "BISECT_LOG",
    }
    operations = [name for name, marker in markers.items() if marker.exists()]
    if (git_dir / "rebase-merge").exists() or (git_dir / "rebase-apply").exists():
        operations.append("rebase")
    return sorted(operations)


def worktree_status(path: Path) -> dict[str, int | None]:
    code, output, _ = run_git(["status", "--porcelain=v1", "--untracked-files=normal"], path)
    if code:
        return {"dirty_count": None, "staged_count": None, "unstaged_count": None, "untracked_count": None}
    lines = output.splitlines() if output else []
    staged = 0
    unstaged = 0
    untracked = 0
    for line in lines:
        status = line[:2]
        if status == "??":
            untracked += 1
            continue
        if len(status) >= 1 and status[0] not in {" ", "?"}:
            staged += 1
        if len(status) >= 2 and status[1] not in {" ", "?"}:
            unstaged += 1
    return {
        "dirty_count": len(lines),
        "staged_count": staged,
        "unstaged_count": unstaged,
        "untracked_count": untracked,
    }


def list_worktrees(root: Path) -> tuple[list[dict[str, Any]], str | None]:
    code, output, error = run_git(["-c", "core.quotePath=false", "worktree", "list", "--porcelain"], root)
    if code:
        return [], error or "git worktree list failed"
    worktrees: list[dict[str, Any]] = []
    for raw in parse_worktree_porcelain(output):
        raw_path = str(raw.get("path", ""))
        if not raw_path or raw_path.startswith('"'):
            continue
        path = Path(raw_path).resolve()
        branch_value = str(raw.get("branch", ""))
        branch = branch_value.removeprefix("refs/heads/") or None
        status = worktree_status(path) if path.exists() else {
            "dirty_count": None,
            "staged_count": None,
            "unstaged_count": None,
            "untracked_count": None,
        }
        worktrees.append(
            {
                "path": str(path),
                "branch": branch,
                "head_oid": raw.get("HEAD"),
                "detached": bool(raw.get("detached")),
                "bare": bool(raw.get("bare")),
                "locked": "locked" in raw,
                "lock_reason": raw.get("locked") if isinstance(raw.get("locked"), str) else None,
                "prunable": "prunable" in raw,
                "prune_reason": raw.get("prunable") if isinstance(raw.get("prunable"), str) else None,
                "exists": path.exists(),
                "operations": worktree_operations(path) if path.exists() else [],
                **status,
            }
        )
    return worktrees, None


class Findings:
    def __init__(self) -> None:
        self.items: list[dict[str, Any]] = []

    def add(
        self,
        severity: str,
        code: str,
        message: str,
        *,
        line_ids: Iterable[str] | None = None,
        path: str | None = None,
    ) -> None:
        finding: dict[str, Any] = {
            "severity": severity,
            "code": code,
            "message": message,
        }
        if line_ids:
            finding["line_ids"] = sorted(set(line_ids))
        if path:
            finding["path"] = path
        self.items.append(finding)


def load_snapshot(source: str | None) -> tuple[dict[str, Any] | None, str | None]:
    if source is None:
        return None, None
    try:
        if source == "-":
            text = sys.stdin.read()
        else:
            text = Path(source).read_text(encoding="utf-8")
        data = json.loads(text)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return None, f"{type(exc).__name__}: {exc}"
    if not isinstance(data, dict):
        return None, "snapshot root must be a JSON object"
    return data, None


def commit_exists(root: Path, oid: Any) -> bool:
    if not isinstance(oid, str) or not oid:
        return False
    code, resolved, _ = run_git(["rev-parse", "--verify", f"{oid}^{{commit}}"], root)
    return code == 0 and resolved == oid


def commit_patch_id(root: Path, oid: str) -> str | None:
    try:
        show = subprocess.run(
            git_command(root, [
                "show",
                "--format=",
                "--no-ext-diff",
                "--no-textconv",
                "--binary",
                oid,
            ]),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=git_environment(),
            check=False,
            timeout=20,
        )
        if show.returncode:
            return None
        patch_id = subprocess.run(
            git_command(root, ["patch-id", "--stable"]),
            input=show.stdout,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=git_environment(),
            check=False,
            timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired, UnicodeError, ValueError):
        return None
    if patch_id.returncode or not patch_id.stdout.strip():
        return None
    return patch_id.stdout.split()[0]


def valid_identifier(value: Any) -> bool:
    return (
        isinstance(value, str)
        and value not in {".", ".."}
        and SAFE_IDENTIFIER.fullmatch(value) is not None
    )


def is_ancestor(root: Path, ancestor: str, descendant: str) -> bool:
    code, _, _ = run_git(["merge-base", "--is-ancestor", ancestor, descendant], root)
    return code == 0


def valid_relative_path(value: Any) -> str | None:
    if not isinstance(value, str) or not value or "\\" in value:
        return None
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        return None
    return path.as_posix()


def paths_overlap(first: str, second: str) -> bool:
    first_parts = PurePosixPath(first).parts
    second_parts = PurePosixPath(second).parts
    shortest = min(len(first_parts), len(second_parts))
    return first_parts[:shortest] == second_parts[:shortest]


def projected_line(line: dict[str, Any]) -> dict[str, Any]:
    workspace = line.get("workspace")
    workspace_projection = None
    if isinstance(workspace, dict):
        workspace_projection = {
            "mode": workspace.get("mode"),
            "state": workspace.get("state"),
            "revision_oid": workspace.get("revision_oid"),
            "path": workspace.get("path"),
            "branch": workspace.get("branch"),
            "head_oid": workspace.get("head_oid"),
            "location_source": workspace.get("location_source"),
        }
    return {
        "id": line.get("id"),
        "phase": line.get("phase"),
        "worker_task_id": line.get("worker_task_id"),
        "worker_state": line.get("worker_state"),
        "coordinator_decision": line.get("coordinator_decision"),
        "depends_on": line.get("depends_on") if isinstance(line.get("depends_on"), list) else [],
        "checkpoint_oid": line.get("checkpoint_oid"),
        "workspace": workspace_projection,
    }


def expected_layout(root: Path, coordination_id: str) -> Path:
    return root.parent / ".codex-worktrees" / root.name / coordination_id


def validate_workspace(
    *,
    workspace: dict[str, Any],
    line_id: str,
    coordination_id: str,
    project_root: Path,
    actual_by_path: dict[str, dict[str, Any]],
    findings: Findings,
) -> tuple[Path | None, dict[str, Any] | None]:
    mode = workspace.get("mode")
    if mode not in WORKSPACE_MODES:
        findings.add("error", "invalid_workspace_mode", f"Line {line_id} has an invalid workspace mode.", line_ids=[line_id])
    state = workspace.get("state")
    if state not in WORKSPACE_STATES:
        findings.add("error", "invalid_workspace_state", f"Line {line_id} has an invalid workspace state.", line_ids=[line_id])
    location_source = workspace.get("location_source")
    ownership = workspace.get("ownership")
    if mode == "writer" and ownership not in WORKSPACE_OWNERS:
        findings.add("error", "invalid_workspace_ownership", f"Line {line_id} has invalid or missing workspace ownership.", line_ids=[line_id])
    if mode == "writer" and location_source not in LOCATION_SOURCES:
        findings.add("error", "invalid_location_source", f"Line {line_id} has an invalid worktree location source.", line_ids=[line_id])
    elif mode == "reader" and location_source is not None and location_source not in LOCATION_SOURCES:
        findings.add("error", "invalid_location_source", f"Line {line_id} has an invalid worktree location source.", line_ids=[line_id])
    raw_path = workspace.get("path")
    if mode == "reader" and not raw_path:
        revision = workspace.get("revision_oid")
        if not commit_exists(project_root, revision):
            findings.add("error", "reader_revision_unreachable", f"Line {line_id} reader revision is not a reachable commit.", line_ids=[line_id])
        return None, None
    if not isinstance(raw_path, str) or not raw_path:
        findings.add("error", "workspace_path_missing", f"Line {line_id} has no workspace path.", line_ids=[line_id])
        return None, None
    try:
        path = Path(raw_path).resolve()
    except (OSError, ValueError):
        findings.add("error", "workspace_path_invalid", f"Line {line_id} workspace path cannot be resolved.", line_ids=[line_id])
        return None, None
    actual = actual_by_path.get(str(path))
    if actual is None:
        findings.add("error", "workspace_not_found", f"Line {line_id} workspace is not in git worktree inventory.", line_ids=[line_id], path=str(path))
    else:
        expected_branch = workspace.get("branch")
        if expected_branch != actual.get("branch"):
            findings.add("error", "workspace_branch_mismatch", f"Line {line_id} workspace branch differs from Git.", line_ids=[line_id], path=str(path))
        expected_head = workspace.get("head_oid")
        if expected_head != actual.get("head_oid"):
            findings.add("error", "workspace_head_mismatch", f"Line {line_id} workspace HEAD differs from Git.", line_ids=[line_id], path=str(path))
    if location_source == "repo_sibling":
        expected = expected_layout(project_root, coordination_id) / "workers" / line_id
        if path != expected.resolve():
            findings.add("error", "workspace_layout_mismatch", f"Line {line_id} does not use the declared repo-sibling worker layout.", line_ids=[line_id], path=str(path))
    return path, actual


def validate_binding(
    *,
    binding: dict[str, Any],
    line_id: str,
    workspace_path: Path | None,
    project_root: Path,
    findings: Findings,
) -> tuple[str | None, str | None]:
    relative = valid_relative_path(binding.get("relative_path"))
    if relative is None:
        findings.add("error", "binding_relative_path_invalid", f"Line {line_id} has an unsafe project-local binding path.", line_ids=[line_id])
    binding_type = binding.get("binding")
    if binding_type != "symlink":
        findings.add("error", "binding_type_invalid", f"Line {line_id} project-local binding must declare symlink.", line_ids=[line_id])
    mutability = binding.get("mutability")
    if mutability not in {"immutable", "mutable"}:
        findings.add("error", "binding_mutability_invalid", f"Line {line_id} project-local binding has invalid mutability.", line_ids=[line_id])
    raw_source = binding.get("source_path")
    source: Path | None = None
    if not isinstance(raw_source, str) or not raw_source or not Path(raw_source).is_absolute():
        findings.add("error", "binding_source_invalid", f"Line {line_id} project-local binding needs an absolute source path.", line_ids=[line_id])
    else:
        try:
            source = Path(raw_source).resolve()
        except (OSError, ValueError):
            findings.add("error", "binding_source_invalid", f"Line {line_id} project-local binding source cannot be resolved.", line_ids=[line_id])
            source = None
        if source is None:
            return None, str(mutability) if isinstance(mutability, str) else None
        if not within(source, project_root):
            findings.add("error", "binding_source_outside_project", f"Line {line_id} binding source is outside the project root.", line_ids=[line_id], path=str(source))
        if not source.exists():
            findings.add("error", "binding_source_missing", f"Line {line_id} binding source does not exist.", line_ids=[line_id], path=str(source))
        if source == project_root or within(source, project_root / ".git"):
            findings.add("error", "binding_source_reserved", f"Line {line_id} binding source is a reserved repository path.", line_ids=[line_id], path=str(source))
        elif within(source, project_root):
            source_relative = source.relative_to(project_root).as_posix()
            tracked_code, tracked_output, _ = run_git(["ls-files", "--", source_relative], project_root)
            if tracked_code == 0 and tracked_output:
                findings.add("error", "binding_source_tracked", f"Line {line_id} binding source contains Git-tracked project content.", line_ids=[line_id], path=str(source))
    if workspace_path is None or relative is None:
        return (str(source) if source else None), str(mutability) if isinstance(mutability, str) else None
    destination = workspace_path / relative
    tracked_code, _, _ = run_git(["ls-files", "--error-unmatch", "--", relative], workspace_path)
    if tracked_code == 0:
        findings.add("error", "binding_shadows_tracked_path", f"Line {line_id} binding would shadow a tracked path.", line_ids=[line_id], path=str(destination))
    ignored_code, _, _ = run_git(["check-ignore", "-q", "--", relative], workspace_path)
    if ignored_code != 0:
        findings.add("error", "binding_not_ignored", f"Line {line_id} binding destination is not ignored by Git.", line_ids=[line_id], path=str(destination))
    if not destination.is_symlink():
        findings.add("error", "binding_symlink_missing", f"Line {line_id} binding destination is not a symlink.", line_ids=[line_id], path=str(destination))
    elif source is not None and destination.resolve() != source:
        findings.add("error", "binding_target_mismatch", f"Line {line_id} binding target differs from its declaration.", line_ids=[line_id], path=str(destination))
    if mutability == "mutable":
        findings.add("error", "binding_mutable_symlink", f"Line {line_id} declares a shared symlink for mutable project data.", line_ids=[line_id], path=str(destination))
    return (str(source) if source else None), str(mutability) if isinstance(mutability, str) else None


def validate_snapshot(
    snapshot: dict[str, Any],
    *,
    project_root: Path,
    worktrees: list[dict[str, Any]],
    findings: Findings,
) -> list[dict[str, Any]]:
    if snapshot.get("schema_version") != SNAPSHOT_VERSION:
        findings.add("error", "snapshot_schema_unsupported", f"Snapshot schema_version must be {SNAPSHOT_VERSION}.")
    coordination_id = snapshot.get("coordination_id")
    if not valid_identifier(coordination_id):
        findings.add("error", "coordination_id_invalid", "Snapshot needs a safe coordination_id path component.")
        coordination_id = "<invalid>"
    if snapshot.get("phase") not in SNAPSHOT_PHASES:
        findings.add("error", "invalid_snapshot_phase", "Snapshot has an invalid coordination phase.")
    target_base = snapshot.get("target_base_oid")
    target_base_valid = commit_exists(project_root, target_base)
    if not target_base_valid:
        findings.add("error", "target_base_unreachable", "Snapshot target_base_oid is not a reachable commit.")
    cleanup_grant = snapshot.get("cleanup_grant")
    granted_cleanup_lines: set[str] = set()
    granted_cleanup_paths: set[str] = set()
    if cleanup_grant is not None:
        if not isinstance(cleanup_grant, dict):
            findings.add("error", "cleanup_grant_invalid", "cleanup_grant must be an object.")
        else:
            raw_grant_lines = cleanup_grant.get("line_ids", [])
            raw_grant_paths = cleanup_grant.get("worktree_paths", [])
            if not isinstance(raw_grant_lines, list) or any(not isinstance(item, str) for item in raw_grant_lines):
                findings.add("error", "cleanup_grant_invalid", "cleanup_grant line_ids must be an array of strings.")
            else:
                granted_cleanup_lines = set(raw_grant_lines)
            if not isinstance(raw_grant_paths, list) or any(not isinstance(item, str) for item in raw_grant_paths):
                findings.add("error", "cleanup_grant_invalid", "cleanup_grant worktree_paths must be an array of absolute paths.")
            else:
                for raw_grant_path in raw_grant_paths:
                    try:
                        grant_path = Path(raw_grant_path)
                        if not grant_path.is_absolute():
                            raise ValueError("cleanup path is not absolute")
                        granted_cleanup_paths.add(str(grant_path.resolve()))
                    except (OSError, ValueError):
                        findings.add("error", "cleanup_grant_invalid", "cleanup_grant contains an invalid worktree path.")
    raw_lines = snapshot.get("lines")
    if not isinstance(raw_lines, list):
        findings.add("error", "lines_invalid", "Snapshot lines must be a JSON array.")
        raw_lines = []
    if len(raw_lines) > MAX_LINES:
        findings.add("error", "line_limit_exceeded", f"Snapshot contains more than {MAX_LINES} lines.")
        raw_lines = raw_lines[:MAX_LINES]
    lines = [line for line in raw_lines if isinstance(line, dict)]
    if len(lines) != len(raw_lines):
        findings.add("error", "line_entry_invalid", "Every snapshot line must be a JSON object.")

    actual_by_path = {item["path"]: item for item in worktrees}
    ids = [line.get("id") for line in lines if isinstance(line.get("id"), str) and line.get("id")]
    for line_id, count in Counter(ids).items():
        if count > 1:
            findings.add("error", "duplicate_line_id", f"Line id {line_id} appears more than once.", line_ids=[line_id])
    worker_ids = [line.get("worker_task_id") for line in lines if isinstance(line.get("worker_task_id"), str) and line.get("worker_task_id")]
    for worker_id, count in Counter(worker_ids).items():
        if count > 1:
            findings.add("error", "duplicate_worker_task_id", "A Desktop worker task is assigned to more than one line.")

    line_by_id = {str(line.get("id")): line for line in lines if isinstance(line.get("id"), str) and line.get("id")}
    dependencies: dict[str, list[str]] = {}
    active_writers: list[tuple[str, Path, dict[str, Any]]] = []
    active_write_sets: list[tuple[str, str]] = []
    active_outputs: list[tuple[str, str]] = []
    resource_owners: dict[str, list[tuple[str, str]]] = defaultdict(list)
    mutable_sources: dict[str, list[str]] = defaultdict(list)
    checkpoints: dict[str, str] = {}
    cleanup_candidates: list[tuple[str, dict[str, Any], Path | None, dict[str, Any] | None]] = []

    for line in lines:
        line_id_value = line.get("id")
        if not isinstance(line_id_value, str) or not line_id_value:
            findings.add("error", "line_id_missing", "A snapshot line has no non-empty id.")
            continue
        line_id = line_id_value
        if not valid_identifier(line_id):
            findings.add("error", "line_id_invalid", f"Line {line_id} id is not a safe path component.", line_ids=[line_id])
        phase = line.get("phase")
        if phase not in LINE_PHASES:
            findings.add("error", "invalid_line_phase", f"Line {line_id} has an invalid phase.", line_ids=[line_id])
        worker_state = line.get("worker_state")
        if worker_state is not None and worker_state not in WORKER_STATES:
            findings.add("error", "invalid_worker_state", f"Line {line_id} has an invalid worker state.", line_ids=[line_id])
        decision = line.get("coordinator_decision")
        if decision is not None and decision not in COORDINATOR_DECISIONS:
            findings.add("error", "invalid_coordinator_decision", f"Line {line_id} has an invalid coordinator decision.", line_ids=[line_id])
        if phase == "executing" and not line.get("worker_task_id"):
            findings.add("error", "executing_worker_missing", f"Executing line {line_id} has no Desktop worker task id.", line_ids=[line_id])
        workspace = line.get("workspace")
        if phase == "executing" and not isinstance(workspace, dict):
            findings.add("error", "executing_workspace_missing", f"Executing line {line_id} has no workspace declaration.", line_ids=[line_id])

        raw_dependencies = line.get("depends_on", [])
        if not isinstance(raw_dependencies, list) or any(not isinstance(item, str) for item in raw_dependencies):
            findings.add("error", "dependencies_invalid", f"Line {line_id} dependencies must be string ids.", line_ids=[line_id])
            dependencies[line_id] = []
        else:
            dependencies[line_id] = list(raw_dependencies)

        workspace_path: Path | None = None
        workspace_actual: dict[str, Any] | None = None
        if isinstance(workspace, dict):
            workspace_path, workspace_actual = validate_workspace(
                workspace=workspace,
                line_id=line_id,
                coordination_id=coordination_id,
                project_root=project_root,
                actual_by_path=actual_by_path,
                findings=findings,
            )
            if phase in ACTIVE_LINE_PHASES and workspace.get("mode") == "writer" and workspace_path is not None:
                active_writers.append((line_id, workspace_path, workspace))

        for field, collector, code in (
            ("write_set", active_write_sets, "write_set_path_invalid"),
            ("output_paths", active_outputs, "output_path_invalid"),
        ):
            raw_paths = line.get(field, [])
            if not isinstance(raw_paths, list):
                findings.add("error", code, f"Line {line_id} {field} must be an array.", line_ids=[line_id])
                continue
            for raw_path in raw_paths:
                normalized = valid_relative_path(raw_path)
                if normalized is None:
                    findings.add("error", code, f"Line {line_id} has an unsafe {field} entry.", line_ids=[line_id])
                elif phase in ACTIVE_LINE_PHASES:
                    collector.append((line_id, normalized))

        raw_claims = line.get("resource_claims", [])
        if not isinstance(raw_claims, list):
            findings.add("error", "resource_claims_invalid", f"Line {line_id} resource_claims must be an array.", line_ids=[line_id])
        else:
            for claim in raw_claims:
                if not isinstance(claim, dict) or not isinstance(claim.get("id"), str) or not claim.get("id"):
                    findings.add("error", "resource_claim_invalid", f"Line {line_id} has an invalid resource claim.", line_ids=[line_id])
                    continue
                mode = claim.get("mode")
                if mode not in RESOURCE_MODES:
                    findings.add("error", "invalid_resource_mode", f"Line {line_id} has an invalid resource claim mode.", line_ids=[line_id])
                elif phase in ACTIVE_LINE_PHASES:
                    resource_owners[str(claim["id"])].append((line_id, str(mode)))

        bindings = line.get("project_local_bindings", [])
        if not isinstance(bindings, list):
            findings.add("error", "bindings_invalid", f"Line {line_id} project_local_bindings must be an array.", line_ids=[line_id])
        else:
            for binding in bindings:
                if not isinstance(binding, dict):
                    findings.add("error", "binding_invalid", f"Line {line_id} has a non-object binding.", line_ids=[line_id])
                    continue
                source, mutability = validate_binding(
                    binding=binding,
                    line_id=line_id,
                    workspace_path=workspace_path,
                    project_root=project_root,
                    findings=findings,
                )
                if phase in ACTIVE_LINE_PHASES and source and mutability == "mutable":
                    mutable_sources[source].append(line_id)

        checkpoint = line.get("checkpoint_oid")
        if checkpoint is not None:
            if not commit_exists(project_root, checkpoint):
                findings.add("error", "checkpoint_unreachable", f"Line {line_id} checkpoint is not a reachable commit.", line_ids=[line_id])
            else:
                checkpoint_string = str(checkpoint)
                checkpoints[line_id] = checkpoint_string
                worker_head = workspace_actual.get("head_oid") if workspace_actual else None
                if isinstance(worker_head, str) and worker_head and not is_ancestor(project_root, checkpoint_string, worker_head):
                    findings.add("error", "checkpoint_not_on_worker_branch", f"Line {line_id} checkpoint is not contained by its worker branch.", line_ids=[line_id])
                if target_base_valid and not is_ancestor(project_root, str(target_base), checkpoint_string):
                    findings.add("error", "checkpoint_not_based_on_target", f"Line {line_id} checkpoint does not descend from target_base_oid.", line_ids=[line_id])

        if isinstance(workspace, dict) and workspace.get("state") == "cleanup_candidate":
            cleanup_candidates.append((line_id, line, workspace_path, workspace_actual))
            if workspace_actual is None or workspace_actual.get("dirty_count") != 0:
                findings.add("error", "cleanup_dirty_worktree", f"Line {line_id} cleanup candidate is not a clean worktree.", line_ids=[line_id], path=str(workspace_path) if workspace_path else None)
            if workspace_actual and workspace_actual.get("operations"):
                findings.add("error", "cleanup_operation_in_progress", f"Line {line_id} cleanup candidate has an interrupted Git operation.", line_ids=[line_id], path=str(workspace_path) if workspace_path else None)
            if phase != "closed":
                findings.add("error", "cleanup_line_not_closed", f"Line {line_id} cleanup candidate is not closed.", line_ids=[line_id])
            if line.get("worker_state") not in {"reported", "stopped"}:
                findings.add("error", "cleanup_worker_active", f"Line {line_id} cleanup candidate still has an active or unknown worker state.", line_ids=[line_id])
            if workspace.get("ownership") != "coordination":
                findings.add("error", "cleanup_not_owned", f"Line {line_id} cleanup candidate is not coordination-owned.", line_ids=[line_id])
            if workspace_path == project_root:
                findings.add("error", "cleanup_primary_worktree", f"Line {line_id} attempts to clean up the primary project worktree.", line_ids=[line_id], path=str(project_root))
            if line_id not in granted_cleanup_lines or workspace_path is None or str(workspace_path) not in granted_cleanup_paths:
                findings.add("error", "cleanup_not_granted", f"Line {line_id} cleanup candidate is not covered by an exact cleanup grant.", line_ids=[line_id], path=str(workspace_path) if workspace_path else None)

    known_ids = set(line_by_id)
    for line_id, required in dependencies.items():
        for dependency in required:
            if dependency not in known_ids:
                findings.add("error", "unknown_dependency", f"Line {line_id} references an unknown dependency.", line_ids=[line_id])

    indegree = {line_id: 0 for line_id in known_ids}
    dependents: dict[str, list[str]] = defaultdict(list)
    for line_id, required in dependencies.items():
        for dependency in required:
            if dependency in known_ids:
                indegree[line_id] += 1
                dependents[dependency].append(line_id)
    ready = [line_id for line_id, degree in indegree.items() if degree == 0]
    visited = 0
    while ready:
        line_id = ready.pop()
        visited += 1
        for dependent in dependents.get(line_id, []):
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                ready.append(dependent)
    if visited != len(known_ids):
        findings.add("error", "dependency_cycle", "Line dependencies contain a cycle.", line_ids=[line_id for line_id, degree in indegree.items() if degree > 0])

    active_phases_by_id = {
        str(line.get("id")): line.get("phase")
        for line in lines
        if isinstance(line.get("id"), str)
    }
    for candidate_id, _, _, _ in cleanup_candidates:
        active_dependents = [
            dependent
            for dependent in dependents.get(candidate_id, [])
            if active_phases_by_id.get(dependent) in ACTIVE_LINE_PHASES
        ]
        if active_dependents:
            findings.add("error", "cleanup_active_dependent", f"Line {candidate_id} still has active dependent lines.", line_ids=[candidate_id, *active_dependents])

    workspace_owners: dict[str, list[str]] = defaultdict(list)
    for line_id, path, _ in active_writers:
        workspace_owners[str(path)].append(line_id)
    for path, owners in workspace_owners.items():
        if len(owners) > 1:
            findings.add("error", "workspace_multiple_writers", "An active worktree is assigned to more than one writer line.", line_ids=owners, path=path)

    for collector, code, message in (
        (active_write_sets, "write_set_overlap", "Active writer lines have overlapping write sets."),
        (active_outputs, "output_path_overlap", "Active lines have overlapping output paths."),
    ):
        for index, (first_line, first_path) in enumerate(collector):
            for second_line, second_path in collector[index + 1 :]:
                if first_line != second_line and paths_overlap(first_path, second_path):
                    findings.add("error", code, message, line_ids=[first_line, second_line])

    for owners in resource_owners.values():
        if len(owners) > 1 and any(mode == "exclusive" for _, mode in owners):
            findings.add("error", "resource_claim_overlap", "Active lines have conflicting resource claims.", line_ids=[line_id for line_id, _ in owners])
    for source, owners in mutable_sources.items():
        if len(set(owners)) > 1:
            findings.add("error", "binding_shared_writable_target", "Active writer lines share a mutable project-data target.", line_ids=owners, path=source)

    valid_integrated_sources: set[str] = set()
    integration_workspace_path: Path | None = None
    integration = snapshot.get("integration")
    if integration is not None and not isinstance(integration, dict):
        findings.add("error", "integration_invalid", "Snapshot integration must be an object.")
    elif isinstance(integration, dict):
        integration_workspace = integration.get("workspace")
        integration_branch: str | None = None
        integration_head: str | None = None
        if not isinstance(integration_workspace, dict):
            findings.add("error", "integration_workspace_missing", "Integration records require an integration workspace.")
        else:
            raw_path = integration_workspace.get("path")
            try:
                path = Path(raw_path).resolve() if isinstance(raw_path, str) and raw_path else None
            except (OSError, ValueError):
                path = None
                findings.add("error", "integration_workspace_path_invalid", "Integration workspace path cannot be resolved.")
            integration_workspace_path = path
            actual = actual_by_path.get(str(path)) if path else None
            if actual is None:
                findings.add("error", "integration_workspace_not_found", "Integration workspace is not in git worktree inventory.", path=str(path) if path else None)
            else:
                integration_branch = integration_workspace.get("branch") if isinstance(integration_workspace.get("branch"), str) else None
                integration_head = actual.get("head_oid") if isinstance(actual.get("head_oid"), str) else None
                if integration_branch != actual.get("branch"):
                    findings.add("error", "integration_branch_mismatch", "Integration workspace branch differs from Git.", path=str(path))
                if integration_workspace.get("head_oid") != actual.get("head_oid"):
                    findings.add("error", "integration_head_mismatch", "Integration workspace HEAD differs from Git.", path=str(path))
            if integration_workspace.get("location_source") == "repo_sibling" and path is not None:
                expected = expected_layout(project_root, coordination_id) / "integration"
                if path != expected.resolve():
                    findings.add("error", "integration_layout_mismatch", "Integration workspace does not use the declared repo-sibling layout.", path=str(path))
        records = integration.get("records", [])
        if not isinstance(records, list):
            findings.add("error", "integration_records_invalid", "Integration records must be an array.")
            records = []
        for record in records:
            if not isinstance(record, dict):
                findings.add("error", "integration_record_invalid", "An integration record is not an object.")
                continue
            line_id = record.get("line_id")
            source_oid = record.get("source_oid")
            integrated_oid = record.get("integrated_oid")
            method = record.get("method")
            record_valid = True
            if not isinstance(line_id, str) or line_id not in line_by_id:
                findings.add("error", "integration_line_unknown", "An integration record references an unknown line.")
                record_valid = False
            if method not in INTEGRATION_METHODS:
                findings.add("error", "integration_method_invalid", "An integration record has an invalid method.", line_ids=[line_id] if isinstance(line_id, str) else None)
                record_valid = False
            if not commit_exists(project_root, source_oid):
                findings.add("error", "integration_source_unreachable", "An integration source OID is not a reachable commit.", line_ids=[line_id] if isinstance(line_id, str) else None)
                record_valid = False
            if not commit_exists(project_root, integrated_oid):
                findings.add("error", "integrated_oid_unreachable", "An integrated OID is not a reachable commit.", line_ids=[line_id] if isinstance(line_id, str) else None)
                record_valid = False
            if isinstance(line_id, str) and line_id in line_by_id:
                if line_id not in checkpoints:
                    findings.add("error", "integration_checkpoint_missing", f"Line {line_id} has an integration record but no valid checkpoint.", line_ids=[line_id])
                    record_valid = False
                elif source_oid != checkpoints[line_id]:
                    findings.add("error", "integration_source_mismatch", f"Line {line_id} integration source differs from its checkpoint.", line_ids=[line_id])
                    record_valid = False
            if isinstance(integrated_oid, str) and integration_head and commit_exists(project_root, integrated_oid):
                if not is_ancestor(project_root, integrated_oid, integration_head):
                    findings.add("error", "integrated_oid_not_on_branch", "An integrated OID is not contained by the integration branch.", line_ids=[line_id] if isinstance(line_id, str) else None)
                    record_valid = False
            if record_valid and isinstance(source_oid, str) and isinstance(integrated_oid, str):
                if method in {"cherry-pick", "rebase"}:
                    source_patch = commit_patch_id(project_root, source_oid)
                    integrated_patch = commit_patch_id(project_root, integrated_oid)
                    if source_patch is None or integrated_patch is None:
                        findings.add("error", "integration_patch_unverifiable", "A patch-preserving integration record could not be verified.", line_ids=[line_id] if isinstance(line_id, str) else None)
                        record_valid = False
                    elif source_patch != integrated_patch:
                        findings.add("error", "integration_patch_mismatch", "Integrated commit patch differs from the declared source checkpoint.", line_ids=[line_id] if isinstance(line_id, str) else None)
                        record_valid = False
                elif method == "merge":
                    if not is_ancestor(project_root, source_oid, integrated_oid):
                        findings.add("error", "integration_merge_missing_source", "Merge integration does not contain the declared source checkpoint.", line_ids=[line_id] if isinstance(line_id, str) else None)
                        record_valid = False
                else:
                    findings.add("warning", "integration_equivalence_unverified", "Squash or manual integration cannot prove source equivalence mechanically; preserve the source checkpoint separately.", line_ids=[line_id] if isinstance(line_id, str) else None)
                    record_valid = False
            if record_valid and isinstance(source_oid, str):
                valid_integrated_sources.add(source_oid)

    default_integration_path = expected_layout(project_root, coordination_id) / "integration"
    for line_id, _, workspace_path, _ in cleanup_candidates:
        if workspace_path is not None and (
            workspace_path == integration_workspace_path
            or workspace_path == default_integration_path.resolve()
        ):
            findings.add("error", "cleanup_integration_worktree", f"Line {line_id} attempts to clean up the coordinator integration worktree as a worker line.", line_ids=[line_id], path=str(workspace_path))

    for line in lines:
        workspace = line.get("workspace")
        if not isinstance(workspace, dict) or workspace.get("state") != "cleanup_candidate":
            continue
        line_id = line.get("id")
        checkpoint = line.get("checkpoint_oid")
        decision = line.get("coordinator_decision")
        preserved = False
        if isinstance(checkpoint, str) and checkpoint in valid_integrated_sources:
            preserved = True
        preservation_ref = line.get("preservation_ref")
        if isinstance(checkpoint, str) and isinstance(preservation_ref, str) and preservation_ref:
            format_code, _, _ = run_git(["check-ref-format", preservation_ref], project_root)
            if preservation_ref.startswith("refs/") and format_code == 0:
                code, _, _ = run_git(["show-ref", "--verify", "--quiet", preservation_ref], project_root)
                if code == 0 and is_ancestor(project_root, checkpoint, preservation_ref):
                    preserved = True
            else:
                findings.add("error", "cleanup_preservation_ref_invalid", f"Line {line_id} preservation_ref is not a full Git ref.", line_ids=[str(line_id)])
        if not isinstance(checkpoint, str) or not checkpoint:
            findings.add("error", "cleanup_checkpoint_missing", f"Line {line_id} cleanup candidate has no checkpoint.", line_ids=[str(line_id)])
        elif not preserved:
            findings.add("error", "cleanup_checkpoint_unpreserved", f"Line {line_id} checkpoint is not integrated or preserved by a declared ref.", line_ids=[str(line_id)])
        if decision not in {"pass", "no-go"}:
            findings.add("error", "cleanup_decision_missing", f"Line {line_id} cleanup candidate lacks a terminal coordinator decision.", line_ids=[str(line_id)])

    return [projected_line(line) for line in lines]


def analyze(project_path: Path, snapshot_source: str | None) -> tuple[dict[str, Any], bool]:
    findings = Findings()
    project_root, root_error = resolve_project_root(project_path)
    snapshot_provided = snapshot_source is not None
    snapshot, snapshot_error = load_snapshot(snapshot_source)
    fatal_repository_error = project_root is None
    if project_root is None:
        findings.add("error", "repository_not_found", "The supplied path is not inside a readable Git worktree.")
        project_root = project_path.resolve()
        worktrees: list[dict[str, Any]] = []
        common_dir = None
    else:
        worktrees, worktree_error = list_worktrees(project_root)
        if worktree_error:
            findings.add("error", "worktree_inventory_failed", "Git worktree inventory could not be read.")
        inspected_root = project_root
        primary = next(
            (
                Path(item["path"])
                for item in worktrees
                if not item.get("bare") and item.get("path")
            ),
            inspected_root,
        )
        project_root = primary.resolve()
        common_code, common_output, _ = run_git(["rev-parse", "--git-common-dir"], inspected_root)
        common_dir = str(resolve_git_path(common_output, inspected_root)) if common_code == 0 and common_output else None
    if root_error and fatal_repository_error:
        # Keep raw Git diagnostics out of the JSON report; callers only need the category.
        pass
    if snapshot_error:
        findings.add("error", "snapshot_parse_error", "The coordination snapshot could not be parsed as a JSON object.")
    projected_lines: list[dict[str, Any]] = []
    if snapshot is not None and not fatal_repository_error:
        projected_lines = validate_snapshot(
            snapshot,
            project_root=project_root,
            worktrees=worktrees,
            findings=findings,
        )
    counts = Counter(item["severity"] for item in findings.items)
    report = {
        "audit_version": AUDIT_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "repository": {
            "project_root": str(project_root),
            "git_common_dir": common_dir,
        },
        "snapshot": {
            "provided": snapshot_provided,
            "source": "stdin" if snapshot_source == "-" else ("file" if snapshot_source else None),
            "schema_version": snapshot.get("schema_version") if isinstance(snapshot, dict) else None,
            "coordination_id": snapshot.get("coordination_id") if isinstance(snapshot, dict) else None,
            "phase": snapshot.get("phase") if isinstance(snapshot, dict) else None,
            "line_count": len(snapshot.get("lines", [])) if isinstance(snapshot, dict) and isinstance(snapshot.get("lines"), list) else 0,
        },
        "worktrees": worktrees,
        "lines": projected_lines,
        "findings": findings.items,
        "summary": {
            "errors": counts.get("error", 0),
            "warnings": counts.get("warning", 0),
            "info": counts.get("info", 0),
        },
        "limitations": [
            "Desktop worker existence, host identity, authorization, and live task state are not queried by this local audit.",
            "An immutable project-local binding is a coordination declaration; this audit checks Git tracking, ignore state, source location, and symlink target, not process-level write prevention.",
        ],
    }
    return report, fatal_repository_error


def print_text(report: dict[str, Any]) -> None:
    print(f"Multiline coordination audit v{report['audit_version']}: {report['repository']['project_root']}")
    snapshot = report["snapshot"]
    print(f"Snapshot: provided={snapshot['provided']} coordination_id={snapshot['coordination_id']} lines={snapshot['line_count']}")
    print("Worktrees:")
    if not report["worktrees"]:
        print("- none")
    for worktree in report["worktrees"]:
        print(
            f"- {worktree['path']} branch={worktree['branch']} "
            f"dirty={worktree['dirty_count']} operations={','.join(worktree['operations']) or '-'}"
        )
    print("Lines:")
    if not report["lines"]:
        print("- none")
    for line in report["lines"]:
        workspace = line.get("workspace") or {}
        print(f"- {line.get('id')} phase={line.get('phase')} decision={line.get('coordinator_decision')} cwd={workspace.get('path')}")
    print("Findings:")
    if not report["findings"]:
        print("- none")
    for finding in report["findings"]:
        print(f"- [{finding['severity']}] {finding['code']}: {finding['message']}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Read-only reconciliation audit for multiline worker/worktree coordination.")
    parser.add_argument("project_root", nargs="?", default=os.getcwd(), help="Project root or a path inside its primary worktree.")
    parser.add_argument("--snapshot", metavar="FILE", help="Optional schema-v2 coordinator snapshot; use - for stdin.")
    parser.add_argument("--json", action="store_true", help="Emit the stable JSON report.")
    parser.add_argument("--check", action="store_true", help="Exit 1 when the report contains an error finding.")
    args = parser.parse_args(argv)
    report, fatal_repository_error = analyze(Path(args.project_root), args.snapshot)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_text(report)
    if fatal_repository_error:
        return 2
    if args.check and report["summary"]["errors"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
