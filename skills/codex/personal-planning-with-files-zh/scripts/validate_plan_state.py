#!/usr/bin/env python3
"""Validate one managed planning record without modifying project state."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import errno
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
from typing import Any, BinaryIO, Iterable


OWNER = "personal-planning-with-files-zh"
TRIO = ("task_plan.md", "findings.md", "progress.md")
ROLE_BY_FILE = {
    "task_plan.md": "task_plan",
    "findings.md": "findings",
    "progress.md": "progress",
}
PLAN_ID_PATTERN = r"[a-z0-9][a-z0-9-]{2,63}"
PLAN_ID_RE = re.compile(rf"{PLAN_ID_PATTERN}\Z")
HASH_RE = re.compile(r"[0-9a-f]{64}\Z")
KEY_RE = re.compile(r"[A-Za-z0-9_.-]+\Z")
HISTORY_NAME_RE = re.compile(r"g([0-9]{4})-[0-9]{8}-[a-z0-9][a-z0-9-]{0,63}\Z")
CORRECTION_NAME_RE = re.compile(r"c[0-9]{4}-[0-9]{8}-[a-z0-9][a-z0-9-]{0,63}\.md\Z")
RFC3339_UTC_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?Z\Z")
INITIALIZED_FROM_RE = re.compile(
    rf"(?:archive:{PLAN_ID_PATTERN}#(?:original|c[0-9]{{4}})|"
    rf"snapshot:{PLAN_ID_PATTERN}@g[0-9]{{4}}(?:#c[0-9]{{4}})?|"
    rf"plan:{PLAN_ID_PATTERN}@g[0-9]{{4}}|"
    r"packet:[A-Za-z0-9._-]{3,128})\Z"
)
VALID_PLAN_STATUS = {"draft", "active", "closed"}
VALID_CLOSURE_STATUS = {"complete", "cancelled", "suspended", "superseded"}
VALID_RECORD_TRUST = {"valid", "corrected", "invalidated", "redacted"}
VALID_TRANSACTION_OPERATIONS = {"generation-rollover", "generation-correction"}
VALID_TRANSACTION_PHASES = {"staged", "snapshot-published", "active-published", "verified"}


class FrontmatterError(ValueError):
    """Raised when a managed Markdown frontmatter block is unsupported."""


class InvocationError(ValueError):
    """Raised when the validator cannot inspect the requested environment."""


class ConcurrentReadError(RuntimeError):
    """Raised when a file changes while its validation snapshot is read."""


class UnsafeFileError(ValueError):
    """Raised when a no-follow read does not resolve to one regular file."""


@dataclass(frozen=True)
class Issue:
    code: str
    category: str
    message: str


@dataclass(frozen=True)
class DocumentSnapshot:
    metadata: dict[str, Any]
    digest: str
    stamp: tuple[int, int, int, int, int, int]


@dataclass(frozen=True)
class TrioReadResult:
    status: str
    metadata: dict[str, dict[str, Any]]
    hashes: dict[str, str]
    stamps: tuple[tuple[Path, tuple[int, int, int, int, int, int]], ...]


def stamp_from_stat(value: os.stat_result) -> tuple[int, int, int, int, int, int]:
    return (
        value.st_dev,
        value.st_ino,
        value.st_mode,
        value.st_size,
        value.st_mtime_ns,
        value.st_ctime_ns,
    )


def open_regular_nofollow(path: Path) -> tuple[BinaryIO, tuple[int, int, int, int, int, int]]:
    before = os.lstat(path)
    if not stat.S_ISREG(before.st_mode):
        raise UnsafeFileError("path is not a regular file")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        if exc.errno == errno.ELOOP:
            raise UnsafeFileError("path became a symlink during validation") from exc
        raise
    handle = os.fdopen(descriptor, "rb")
    opened = os.fstat(handle.fileno())
    if not stat.S_ISREG(opened.st_mode):
        handle.close()
        raise UnsafeFileError("path is not a regular file")
    before_stamp = stamp_from_stat(before)
    opened_stamp = stamp_from_stat(opened)
    if before_stamp != opened_stamp:
        handle.close()
        raise ConcurrentReadError("path changed while it was opened")
    return handle, opened_stamp


def read_frontmatter_lines(handle: BinaryIO, digest: Any | None = None) -> list[str]:
    encoded_lines: list[bytes] = []
    total = 0
    closed = False
    for index in range(1, 131):
        line = handle.readline(65537)
        if digest is not None:
            digest.update(line)
        total += len(line)
        if not line:
            raise FrontmatterError("missing closing frontmatter delimiter")
        if total > 65536:
            raise FrontmatterError("frontmatter exceeds the bounded parser limit")
        stripped = line.rstrip(b"\r\n")
        if index == 1:
            if stripped != b"---":
                raise FrontmatterError("missing opening frontmatter delimiter")
            continue
        if stripped == b"---":
            closed = True
            break
        encoded_lines.append(stripped)
    if not closed:
        raise FrontmatterError("frontmatter exceeds the bounded parser limit")
    try:
        return [line.decode("utf-8") for line in encoded_lines]
    except UnicodeDecodeError as exc:
        raise FrontmatterError("frontmatter is not valid UTF-8") from exc


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        raise FrontmatterError("empty scalar values are unsupported; omit optional keys")
    if value.startswith('"'):
        try:
            decoded = json.loads(value)
        except json.JSONDecodeError as exc:
            raise FrontmatterError(f"invalid double-quoted scalar: {exc.msg}") from exc
        if not isinstance(decoded, str):
            raise FrontmatterError("quoted frontmatter scalars must be strings")
        return decoded
    if value.startswith("'"):
        if len(value) < 2 or not value.endswith("'"):
            raise FrontmatterError("invalid single-quoted scalar")
        return value[1:-1].replace("''", "'")
    if HASH_RE.fullmatch(value):
        return value
    if re.fullmatch(r"-?[0-9]+", value):
        return int(value)
    if value in {"true", "false"}:
        return value == "true"
    if value in {"null", "~"}:
        return None
    if value[0] in "[{|>&*!":
        raise FrontmatterError("collections, block scalars, tags, anchors, and aliases are unsupported")
    return value


def parse_frontmatter_lines(lines: list[str]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    nested_key: str | None = None
    for line in lines:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith(" "):
            if not line.startswith("  ") or line.startswith("   ") or nested_key is None:
                raise FrontmatterError("only one two-space-indented mapping level is supported")
            nested_line = line[2:]
            if ":" not in nested_line:
                raise FrontmatterError("invalid nested mapping entry")
            key, raw_value = nested_line.split(":", 1)
            key = key.strip()
            if not KEY_RE.fullmatch(key):
                raise FrontmatterError(f"unsupported nested key: {key!r}")
            mapping = result[nested_key]
            if key in mapping:
                raise FrontmatterError(f"duplicate nested key: {key}")
            mapping[key] = parse_scalar(raw_value)
            continue

        nested_key = None
        if ":" not in line:
            raise FrontmatterError("invalid top-level mapping entry")
        key, raw_value = line.split(":", 1)
        key = key.strip()
        if not KEY_RE.fullmatch(key):
            raise FrontmatterError(f"unsupported key: {key!r}")
        if key in result:
            raise FrontmatterError(f"duplicate key: {key}")
        if raw_value.strip():
            result[key] = parse_scalar(raw_value)
        else:
            result[key] = {}
            nested_key = key
    return result


def verify_unchanged_path(path: Path, stamp: tuple[int, int, int, int, int, int]) -> None:
    try:
        current = stamp_from_stat(os.lstat(path))
    except OSError as exc:
        raise ConcurrentReadError("path changed or disappeared during validation") from exc
    if current != stamp:
        raise ConcurrentReadError("path changed during validation")


def parse_frontmatter(path: Path) -> dict[str, Any]:
    handle, before = open_regular_nofollow(path)
    try:
        with handle:
            lines = read_frontmatter_lines(handle)
            after = stamp_from_stat(os.fstat(handle.fileno()))
    finally:
        if not handle.closed:
            handle.close()
    if before != after:
        raise ConcurrentReadError("frontmatter changed during validation")
    verify_unchanged_path(path, before)
    return parse_frontmatter_lines(lines)


def read_hashed_frontmatter(path: Path) -> DocumentSnapshot:
    handle, before = open_regular_nofollow(path)
    digest = hashlib.sha256()
    try:
        with handle:
            lines = read_frontmatter_lines(handle, digest)
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
            after = stamp_from_stat(os.fstat(handle.fileno()))
    finally:
        if not handle.closed:
            handle.close()
    if before != after:
        raise ConcurrentReadError("file changed during validation")
    verify_unchanged_path(path, before)
    return DocumentSnapshot(
        metadata=parse_frontmatter_lines(lines),
        digest=digest.hexdigest(),
        stamp=before,
    )


def lexical_absolute(path: Path) -> Path:
    return Path(os.path.abspath(os.fspath(path)))


def path_has_symlink(path: Path, root: Path) -> bool:
    """Check lexical components from root to path without following them."""
    try:
        relative = path.relative_to(root)
    except ValueError:
        return path.is_symlink()
    current = root
    if current.is_symlink():
        return True
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            return True
    return False


def is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


class PlanValidator:
    def __init__(
        self,
        canonical_root: Path,
        record: Path,
        *,
        check_lineage: bool,
        for_initialization: bool,
    ) -> None:
        self.root_input = lexical_absolute(canonical_root)
        self.record_input = lexical_absolute(record)
        try:
            self.root = self.root_input.resolve(strict=True)
        except (OSError, RuntimeError) as exc:
            raise InvocationError(f"canonical root is not accessible: {self.root_input}") from exc
        if not self.root.is_dir():
            raise InvocationError(f"canonical root is not a directory: {self.root_input}")
        try:
            self.record = self.record_input.resolve(strict=True)
        except (OSError, RuntimeError) as exc:
            raise InvocationError(f"record is not accessible: {self.record_input}") from exc
        if not self.record.is_dir():
            raise InvocationError(f"record is not a directory: {self.record_input}")

        self.check_lineage = check_lineage
        self.for_initialization = for_initialization
        self.issues: list[Issue] = []
        self.needs_rebind = False
        self.record_type = self.infer_record_type()
        self.metadata: dict[str, dict[str, Any]] = {}
        self.control_metadata: dict[str, Any] = {}
        self.source_hashes: dict[str, str] = {}
        self.file_stamps: dict[str, tuple[Path, tuple[int, int, int, int, int, int]]] = {}

    def add_issue(self, code: str, category: str, message: str) -> None:
        issue = Issue(code=code, category=category, message=message)
        if issue not in self.issues:
            self.issues.append(issue)

    def infer_record_type(self) -> str:
        if self.record == self.root:
            return "active-repo"

        plans_base = self.root / ".planning" / "plans"
        try:
            relative = self.record.relative_to(plans_base)
        except ValueError:
            relative = None
        if relative is not None:
            if len(relative.parts) == 1:
                return "active-task"
            if len(relative.parts) == 3 and relative.parts[1] == ".staging":
                return "staging"
            if len(relative.parts) == 3 and relative.parts[1] == "history":
                return "generation-snapshot"

        repo_sidecar = self.root / ".planning" / "_repo"
        try:
            relative = self.record.relative_to(repo_sidecar)
        except ValueError:
            relative = None
        if relative is not None and len(relative.parts) == 2:
            if relative.parts[0] == ".staging":
                return "staging"
            if relative.parts[0] == "history":
                return "generation-snapshot"

        archive_base = self.root / ".planning" / "archive"
        try:
            relative = self.record.relative_to(archive_base)
        except ValueError:
            relative = None
        if relative is not None and len(relative.parts) == 2 and relative.parts[0] in {"plans", "repo"}:
            return "terminal-archive"
        return "unknown"

    def validate(self) -> dict[str, Any]:
        self.validate_paths()
        if is_within(self.record, self.root):
            self.load_trio()
            self.validate_trio()
            self.validate_control()
            self.validate_location()
            self.validate_staging()
            self.validate_history_surface()
            if self.check_lineage:
                self.validate_lineage()
            self.validate_snapshot_stability()
        if self.for_initialization and self.record_type not in {"terminal-archive", "generation-snapshot"}:
            self.add_issue(
                "initialization_requires_frozen_record",
                "invalid",
                "Initialization eligibility can be checked only for a terminal archive or generation snapshot.",
            )
        status = self.compute_status()
        hash_binding_scope = self.compute_hash_binding_scope()
        task = self.metadata.get("task_plan.md", {})
        return {
            "schema_version": 1,
            "status": status,
            "record_type": self.record_type,
            "inspection_root": str(self.root),
            "recorded_canonical_root": task.get("canonical_root"),
            "record": str(self.record),
            "plan_id": task.get("plan_id"),
            "generation": task.get("generation"),
            "record_trust": self.control_metadata.get("record_trust"),
            "transaction_phase": self.control_metadata.get("phase"),
            "needs_rebind": self.needs_rebind,
            "hash_binding_scope": hash_binding_scope,
            "source_hashes": self.source_hashes,
            "issues": [asdict(issue) for issue in self.issues],
        }

    def validate_paths(self) -> None:
        if self.root_input != self.root:
            self.add_issue(
                "canonical_root_argument_not_realpath",
                "invalid",
                "The supplied canonical root is not its resolved absolute path.",
            )
        if not is_within(self.record, self.root):
            self.add_issue(
                "record_outside_root",
                "invalid",
                "The selected record resolves outside the canonical root.",
            )
            return
        if path_has_symlink(self.record_input, self.root_input):
            self.add_issue(
                "symlink_not_allowed",
                "invalid",
                "The selected record path contains a symlink component.",
            )

    def load_trio(self) -> None:
        for filename in TRIO:
            path = self.record / filename
            if not path.exists():
                self.add_issue("missing_file", "invalid", f"Required planning file is missing: {filename}.")
                continue
            if path.is_symlink():
                self.add_issue("symlink_not_allowed", "invalid", f"Planning file is a symlink: {filename}.")
                continue
            if not path.is_file():
                self.add_issue("not_regular_file", "invalid", f"Planning path is not a regular file: {filename}.")
                continue
            try:
                snapshot = read_hashed_frontmatter(path)
                self.metadata[filename] = snapshot.metadata
                self.source_hashes[filename] = snapshot.digest
                self.file_stamps[filename] = (path, snapshot.stamp)
            except ConcurrentReadError as exc:
                self.add_issue("record_changed_during_validation", "stale", f"Unstable {filename}: {exc}.")
            except UnsafeFileError as exc:
                self.add_issue("symlink_not_allowed", "invalid", f"Unsafe {filename}: {exc}.")
            except FrontmatterError as exc:
                self.add_issue("invalid_frontmatter", "invalid", f"Invalid {filename} frontmatter: {exc}.")

    def require_equal(self, metadata: dict[str, Any], key: str, expected: Any, filename: str) -> None:
        if metadata.get(key) != expected:
            self.add_issue(
                "metadata_mismatch",
                "invalid",
                f"{filename} has an invalid {key!r} value.",
            )

    def validate_trio(self) -> None:
        task = self.metadata.get("task_plan.md")
        if task is None:
            return
        required = {
            "planning_owner",
            "schema_version",
            "plan_kind",
            "plan_id",
            "plan_role",
            "plan_status",
            "generation",
            "canonical_root",
            "evidence_cutoff",
        }
        for key in sorted(required - set(task)):
            self.add_issue("missing_metadata", "invalid", f"task_plan.md is missing required key: {key}.")

        self.require_equal(task, "planning_owner", OWNER, "task_plan.md")
        self.require_equal(task, "schema_version", 1, "task_plan.md")
        self.require_equal(task, "plan_role", "task_plan", "task_plan.md")

        plan_id = task.get("plan_id")
        if not isinstance(plan_id, str) or not PLAN_ID_RE.fullmatch(plan_id):
            self.add_issue("invalid_plan_id", "invalid", "plan_id must be a 3-64 character lowercase safe identifier.")
        kind = task.get("plan_kind")
        if kind not in {"repo", "task"}:
            self.add_issue("invalid_plan_kind", "invalid", "plan_kind must be 'repo' or 'task'.")
        generation = task.get("generation")
        if not isinstance(generation, int) or isinstance(generation, bool) or generation < 1:
            self.add_issue("invalid_generation", "invalid", "generation must be a positive integer.")
        status = task.get("plan_status")
        if status not in VALID_PLAN_STATUS:
            self.add_issue("invalid_plan_status", "invalid", "plan_status is not supported.")
        closure = task.get("closure_status")
        if status == "closed":
            if closure not in VALID_CLOSURE_STATUS:
                self.add_issue("invalid_closure_status", "invalid", "A closed plan requires a valid closure_status.")
        elif closure is not None:
            self.add_issue("invalid_closure_status", "invalid", "Only a closed plan may define closure_status.")

        evidence_cutoff = task.get("evidence_cutoff")
        if not isinstance(evidence_cutoff, str) or not evidence_cutoff.strip():
            self.add_issue("invalid_evidence_cutoff", "invalid", "evidence_cutoff must be a non-empty scalar string.")

        for field in ("root_plan_id", "parent_plan_id", "predecessor_plan_id"):
            if field not in task:
                continue
            value = task[field]
            if not isinstance(value, str) or not PLAN_ID_RE.fullmatch(value):
                self.add_issue("invalid_lineage_field", "invalid", f"{field} must contain one valid plan_id.")

        initialized_from = task.get("initialized_from")
        if initialized_from is not None and (
            not isinstance(initialized_from, str) or not INITIALIZED_FROM_RE.fullmatch(initialized_from)
        ):
            self.add_issue(
                "invalid_initialized_from",
                "invalid",
                "initialized_from must use an exact archive, snapshot, plan-generation, or packet selector.",
            )

        if kind == "repo" and any(field in task for field in ("root_plan_id", "parent_plan_id")):
            self.add_issue("invalid_repo_lineage", "invalid", "A repo plan cannot define root_plan_id or parent_plan_id.")

        root_value = task.get("canonical_root")
        if not isinstance(root_value, str) or not Path(root_value).is_absolute():
            self.add_issue("invalid_canonical_root", "invalid", "canonical_root must be an absolute path.")
        elif str(lexical_absolute(Path(root_value))) != root_value:
            self.add_issue("invalid_canonical_root", "invalid", "canonical_root must be lexically normalized.")
        elif root_value != str(self.root):
            if self.record_type in {"active-task", "active-repo", "staging"}:
                self.needs_rebind = True
                self.add_issue(
                    "canonical_root_mismatch",
                    "stale",
                    "Active planning metadata does not match the selected canonical root.",
                )
            else:
                self.add_issue(
                    "historical_root_mismatch",
                    "info",
                    "Frozen provenance records a different historical canonical root.",
                )

        for filename, expected_role in ROLE_BY_FILE.items():
            metadata = self.metadata.get(filename)
            if metadata is None:
                continue
            self.require_equal(metadata, "planning_owner", OWNER, filename)
            self.require_equal(metadata, "schema_version", 1, filename)
            self.require_equal(metadata, "plan_role", expected_role, filename)
            if metadata.get("plan_id") != plan_id:
                self.add_issue("plan_id_mismatch", "invalid", f"{filename} does not match the canonical plan_id.")
            if metadata.get("generation") != generation:
                self.add_issue("generation_mismatch", "invalid", f"{filename} does not match the canonical generation.")

    def validate_location(self) -> None:
        if self.record_type == "unknown":
            self.add_issue("invalid_record_location", "invalid", "The selected directory is not a canonical managed record path.")
            return
        task = self.metadata.get("task_plan.md")
        if task is None or not isinstance(task.get("plan_id"), str):
            return
        plan_id = task["plan_id"]
        kind = task.get("plan_kind")
        if self.record_type == "active-repo":
            if kind != "repo" or self.record != self.root:
                self.add_issue("invalid_record_location", "invalid", "A repo plan must use the canonical project root.")
        elif self.record_type == "active-task":
            expected = lexical_absolute(self.root / ".planning" / "plans" / plan_id)
            if kind != "task" or self.record != expected:
                self.add_issue("invalid_record_location", "invalid", "A task plan is not at its canonical plan-id path.")
        elif self.record_type == "terminal-archive":
            branch = "repo" if kind == "repo" else "plans"
            expected = lexical_absolute(self.root / ".planning" / "archive" / branch / plan_id)
            if kind not in {"repo", "task"} or self.record != expected:
                self.add_issue("invalid_record_location", "invalid", "The archive is not at its canonical terminal path.")
        elif self.record_type == "generation-snapshot":
            base = (
                self.root / ".planning" / "_repo" / "history"
                if kind == "repo"
                else self.root / ".planning" / "plans" / plan_id / "history"
            )
            match = HISTORY_NAME_RE.fullmatch(self.record.name)
            generation = task.get("generation")
            if (
                kind not in {"repo", "task"}
                or self.record.parent != lexical_absolute(base)
                or match is None
                or not isinstance(generation, int)
                or int(match.group(1)) != generation
            ):
                self.add_issue("invalid_record_location", "invalid", "The snapshot is outside its plan-local history.")
        elif self.record_type == "staging":
            expected = (
                self.root / ".planning" / "_repo" / ".staging" / self.record.name
                if kind == "repo"
                else self.root / ".planning" / "plans" / plan_id / ".staging" / self.record.name
            )
            txid = self.control_metadata.get("txid")
            if (
                kind not in {"repo", "task"}
                or self.record != lexical_absolute(expected)
                or not isinstance(txid, str)
                or txid != self.record.name
            ):
                self.add_issue("invalid_record_location", "invalid", "A staging record is not at its exact plan-local transaction path.")

    def validate_control(self) -> None:
        control_name = {
            "terminal-archive": "ARCHIVE.md",
            "generation-snapshot": "SNAPSHOT.md",
            "staging": "TRANSACTION.md",
        }.get(self.record_type)
        if control_name is None:
            return
        control_path = self.record / control_name
        issue_code = "invalid_transaction_control" if control_name == "TRANSACTION.md" else "invalid_control"
        if control_path.is_symlink() or not control_path.is_file():
            self.add_issue(issue_code, "invalid", f"Record control is not one regular non-symlink file: {control_name}.")
            return
        try:
            control_snapshot = read_hashed_frontmatter(control_path)
            control = control_snapshot.metadata
        except (FrontmatterError, ConcurrentReadError, UnsafeFileError) as exc:
            self.add_issue(issue_code, "invalid", f"Invalid {control_name} frontmatter: {exc}.")
            return
        self.file_stamps[control_name] = (control_path, control_snapshot.stamp)
        self.control_metadata = control

        if control_name == "TRANSACTION.md":
            self.validate_transaction(control)
            return

        expected_type = "terminal-archive" if control_name == "ARCHIVE.md" else "generation-snapshot"
        if control.get("record_type") != expected_type:
            self.add_issue("invalid_control", "invalid", f"{control_name} has the wrong record_type.")
        trust = control.get("record_trust")
        if trust not in VALID_RECORD_TRUST:
            self.add_issue("invalid_record_trust", "invalid", f"{control_name} has an invalid record_trust.")
        task = self.metadata.get("task_plan.md", {})
        if control.get("plan_id") != task.get("plan_id"):
            self.add_issue("control_identity_mismatch", "invalid", f"{control_name} plan_id does not match the frozen trio.")
        if control.get("generation") != task.get("generation"):
            self.add_issue("control_identity_mismatch", "invalid", f"{control_name} generation does not match the frozen trio.")

        if control_name == "ARCHIVE.md" and task.get("plan_status") != "closed":
            self.add_issue("archive_not_closed", "invalid", "A terminal archive must contain a closed plan.")
        if control_name == "SNAPSHOT.md":
            generation = task.get("generation")
            target_generation = control.get("target_generation")
            created_at = control.get("created_at")
            if (
                not isinstance(generation, int)
                or not isinstance(target_generation, int)
                or isinstance(target_generation, bool)
                or target_generation != generation + 1
                or not isinstance(created_at, str)
                or RFC3339_UTC_RE.fullmatch(created_at) is None
            ):
                self.add_issue(
                    "missing_snapshot_metadata",
                    "invalid",
                    "SNAPSHOT.md requires target_generation = generation + 1 and a UTC created_at value.",
                )

        expected_hashes = control.get("source_hashes")
        if not isinstance(expected_hashes, dict):
            self.add_issue("missing_source_hashes", "invalid", f"{control_name} lacks source_hashes.")
        else:
            for filename in TRIO:
                expected = expected_hashes.get(filename)
                actual = self.source_hashes.get(filename)
                if not isinstance(expected, str) or not HASH_RE.fullmatch(expected):
                    self.add_issue("invalid_source_hash", "invalid", f"{control_name} has an invalid hash for {filename}.")
                elif actual is not None and expected != actual:
                    self.add_issue("hash_mismatch", "invalid", f"Frozen body hash does not match {control_name}: {filename}.")

        corrections = self.record / "corrections"
        correction_files: list[Path] = []
        if corrections.exists():
            if corrections.is_symlink() or not corrections.is_dir():
                self.add_issue("invalid_corrections", "invalid", "corrections is not a regular directory.")
            else:
                for path in sorted(corrections.iterdir()):
                    if path.is_symlink() or not path.is_file() or CORRECTION_NAME_RE.fullmatch(path.name) is None:
                        self.add_issue("invalid_correction_record", "invalid", "A correction entry is not a canonical regular file.")
                        continue
                    correction_files.append(path)
        if trust in {"corrected", "invalidated", "redacted"} and not correction_files:
            self.add_issue("missing_correction", "invalid", "Non-valid record trust requires a correction record.")
        if trust == "valid" and correction_files:
            self.add_issue(
                "unapplied_correction",
                "incomplete",
                "Correction files exist while the frozen control still declares record_trust: valid.",
            )

        if self.for_initialization:
            if trust == "invalidated":
                self.add_issue("initialization_blocked", "invalid", "An invalidated frozen record cannot initialize active state.")
            elif trust == "redacted":
                self.add_issue("initialization_requires_review", "stale", "A redacted record requires explicit completeness review.")

    def validate_transaction(self, control: dict[str, Any]) -> None:
        required = {
            "planning_owner",
            "schema_version",
            "record_type",
            "operation",
            "txid",
            "plan_kind",
            "plan_id",
            "source_generation",
            "target_generation",
            "canonical_root",
            "phase",
            "seed_digest",
            "source_record",
            "history_record",
            "source_hashes",
        }
        for key in sorted(required - set(control)):
            self.add_issue("invalid_transaction_control", "invalid", f"TRANSACTION.md is missing required key: {key}.")

        task = self.metadata.get("task_plan.md", {})
        expected_pairs = {
            "planning_owner": OWNER,
            "schema_version": 1,
            "record_type": "plan-transaction",
            "plan_kind": task.get("plan_kind"),
            "plan_id": task.get("plan_id"),
            "canonical_root": str(self.root),
        }
        for key, expected in expected_pairs.items():
            if control.get(key) != expected:
                self.add_issue("invalid_transaction_control", "invalid", f"TRANSACTION.md has an invalid {key!r} value.")

        operation = control.get("operation")
        if operation not in VALID_TRANSACTION_OPERATIONS:
            self.add_issue("invalid_transaction_control", "invalid", "TRANSACTION.md has an unsupported operation.")
        txid = control.get("txid")
        if not isinstance(txid, str) or PLAN_ID_RE.fullmatch(txid) is None:
            self.add_issue("invalid_transaction_control", "invalid", "TRANSACTION.md has an invalid txid.")
        phase = control.get("phase")
        if phase not in VALID_TRANSACTION_PHASES:
            self.add_issue("invalid_transaction_control", "invalid", "TRANSACTION.md has an unsupported phase.")
        seed_digest = control.get("seed_digest")
        if not isinstance(seed_digest, str) or HASH_RE.fullmatch(seed_digest) is None:
            self.add_issue("invalid_transaction_control", "invalid", "TRANSACTION.md has an invalid seed_digest.")

        source_generation = control.get("source_generation")
        target_generation = control.get("target_generation")
        if (
            not isinstance(source_generation, int)
            or isinstance(source_generation, bool)
            or not isinstance(target_generation, int)
            or isinstance(target_generation, bool)
            or source_generation < 1
            or target_generation != source_generation + 1
            or task.get("generation") != target_generation
        ):
            self.add_issue(
                "invalid_transaction_generation",
                "invalid",
                "The staged trio must be exactly one generation after the transaction source.",
            )

        plan_id = task.get("plan_id")
        kind = task.get("plan_kind")
        expected_source = (
            self.root if kind == "repo" else self.root / ".planning" / "plans" / str(plan_id)
        )
        expected_history_base = (
            self.root / ".planning" / "_repo" / "history"
            if kind == "repo"
            else expected_source / "history"
        )
        source_record = self.parse_control_path(control.get("source_record"), "source_record")
        history_record = self.parse_control_path(control.get("history_record"), "history_record")
        if source_record is not None and source_record != lexical_absolute(expected_source):
            self.add_issue("invalid_transaction_path", "invalid", "source_record is not the canonical active record.")
        history_match = HISTORY_NAME_RE.fullmatch(history_record.name) if history_record is not None else None
        if (
            history_record is not None
            and (
                history_record.parent != lexical_absolute(expected_history_base)
                or history_match is None
                or not isinstance(source_generation, int)
                or int(history_match.group(1)) != source_generation
            )
        ):
            self.add_issue("invalid_transaction_path", "invalid", "history_record is not the exact plan-local source-generation path.")

        expected_hashes = self.validate_hash_mapping(control.get("source_hashes"), "TRANSACTION.md")
        if source_record is None or expected_hashes is None or not source_record.is_dir():
            self.add_issue("transaction_source_unavailable", "incomplete", "The transaction source record is unavailable.")
            return

        source_state = self.read_transaction_trio(source_record)
        source_ok = self.accept_transaction_trio("source", source_state)
        history_surface = self.transaction_trio_surface(history_record)
        history_state = self.read_transaction_trio(history_record) if history_surface == "complete" else None
        history_ok = history_state is not None and self.accept_transaction_trio("history", history_state)
        if phase in {"staged", "snapshot-published"}:
            if source_ok and (
                source_state.hashes != expected_hashes
                or not self.transaction_identity_matches(source_state.metadata, control, source_generation)
            ):
                self.add_issue("transaction_source_mismatch", "invalid", "The live source no longer matches transaction source_hashes.")
        if phase == "staged" and history_record is not None and history_record.exists():
            if history_surface == "partial":
                self.add_issue("transaction_history_incomplete", "incomplete", "The history target contains a partial transaction record.")
            elif history_surface == "unsafe":
                self.add_issue("transaction_history_collision", "invalid", "The history target crosses an unsafe filesystem boundary.")
            elif history_ok and history_state is not None and history_state.hashes != expected_hashes:
                self.add_issue("transaction_history_collision", "invalid", "The history target already contains different or partial state.")
            elif history_ok:
                self.add_issue("transaction_phase_mismatch", "incomplete", "History already exists while TRANSACTION.md still declares phase: staged.")
        if phase in {"snapshot-published", "active-published", "verified"}:
            if history_surface in {"absent", "partial"}:
                self.add_issue("transaction_snapshot_incomplete", "incomplete", "The published history does not match transaction source_hashes.")
            elif (
                history_surface == "unsafe"
                or (
                    history_ok
                    and history_state is not None
                    and (
                        history_state.hashes != expected_hashes
                        or not self.transaction_identity_matches(history_state.metadata, control, source_generation)
                    )
                )
            ):
                self.add_issue("transaction_snapshot_collision", "invalid", "The published history conflicts with transaction source state.")
            elif history_ok and history_record is not None:
                self.validate_transaction_snapshot_control(history_record, control, expected_hashes)
        if phase in {"active-published", "verified"}:
            if source_ok and (
                source_state.hashes != self.source_hashes
                or not self.transaction_identity_matches(source_state.metadata, control, target_generation)
            ):
                self.add_issue("transaction_target_mismatch", "incomplete", "The active record does not match the staged target trio.")

    def transaction_trio_surface(self, record: Path | None) -> str:
        if record is None or not record.exists():
            return "absent"
        if record.is_symlink() or path_has_symlink(record, self.root) or not record.is_dir():
            return "unsafe"
        required = [record / filename for filename in TRIO]
        if any(path.is_symlink() or not path.is_file() for path in required):
            return "partial"
        return "complete"

    def validate_transaction_snapshot_control(
        self,
        history_record: Path,
        transaction: dict[str, Any],
        expected_hashes: dict[str, str],
    ) -> None:
        path = history_record / "SNAPSHOT.md"
        if path.is_symlink() or not path.is_file():
            self.add_issue("transaction_snapshot_incomplete", "incomplete", "The published history lacks a regular SNAPSHOT.md.")
            return
        try:
            snapshot = read_hashed_frontmatter(path)
        except (FrontmatterError, ConcurrentReadError, UnsafeFileError) as exc:
            self.add_issue("transaction_snapshot_control_invalid", "invalid", f"SNAPSHOT.md cannot control the transaction history: {exc}.")
            return
        self.file_stamps["history:SNAPSHOT.md"] = (path, snapshot.stamp)
        control = snapshot.metadata
        source_generation = transaction.get("source_generation")
        target_generation = transaction.get("target_generation")
        if (
            control.get("record_type") != "generation-snapshot"
            or control.get("record_trust") != "valid"
            or control.get("plan_id") != transaction.get("plan_id")
            or control.get("generation") != source_generation
            or control.get("target_generation") != target_generation
            or not isinstance(control.get("created_at"), str)
            or RFC3339_UTC_RE.fullmatch(control["created_at"]) is None
            or control.get("source_hashes") != expected_hashes
        ):
            self.add_issue("transaction_snapshot_control_invalid", "invalid", "SNAPSHOT.md metadata does not match the approved transaction.")

    def transaction_identity_matches(
        self,
        metadata: dict[str, dict[str, Any]],
        control: dict[str, Any],
        generation: Any,
    ) -> bool:
        task = metadata.get("task_plan.md", {})
        if (
            task.get("planning_owner") != OWNER
            or task.get("plan_id") != control.get("plan_id")
            or task.get("plan_kind") != control.get("plan_kind")
            or task.get("generation") != generation
        ):
            return False
        return all(
            metadata.get(filename, {}).get("plan_id") == control.get("plan_id")
            and metadata.get(filename, {}).get("generation") == generation
            and metadata.get(filename, {}).get("plan_role") == ROLE_BY_FILE[filename]
            for filename in TRIO
        )

    def parse_control_path(self, value: Any, field: str) -> Path | None:
        if not isinstance(value, str) or not Path(value).is_absolute():
            self.add_issue("invalid_transaction_path", "invalid", f"{field} must be an absolute normalized path.")
            return None
        path = lexical_absolute(Path(value))
        if str(path) != value or not is_within(path, self.root) or path_has_symlink(path, self.root):
            self.add_issue("invalid_transaction_path", "invalid", f"{field} escapes or crosses a symlink boundary.")
            return None
        return path

    def validate_hash_mapping(self, value: Any, label: str) -> dict[str, str] | None:
        if not isinstance(value, dict):
            self.add_issue("missing_source_hashes", "invalid", f"{label} lacks source_hashes.")
            return None
        result: dict[str, str] = {}
        for filename in TRIO:
            item = value.get(filename)
            if not isinstance(item, str) or HASH_RE.fullmatch(item) is None:
                self.add_issue("invalid_source_hash", "invalid", f"{label} has an invalid hash for {filename}.")
                continue
            result[filename] = item
        return result if len(result) == len(TRIO) else None

    def accept_transaction_trio(self, label: str, result: TrioReadResult) -> bool:
        if result.status == "ok":
            for path, stamp_value in result.stamps:
                self.file_stamps[f"transaction-{label}:{path.name}"] = (path, stamp_value)
            return True
        if result.status == "changed":
            self.add_issue("transaction_state_changed", "stale", f"The transaction {label} changed during validation.")
        elif result.status == "missing":
            self.add_issue("transaction_state_incomplete", "incomplete", f"The transaction {label} trio is missing or partial.")
        else:
            self.add_issue("transaction_state_invalid", "invalid", f"The transaction {label} trio is malformed or unsafe.")
        return False

    def read_transaction_trio(self, record: Path | None) -> TrioReadResult:
        surface = self.transaction_trio_surface(record)
        if surface in {"absent", "partial"}:
            return TrioReadResult("missing", {}, {}, ())
        if surface == "unsafe" or record is None:
            return TrioReadResult("unsafe", {}, {}, ())
        metadata: dict[str, dict[str, Any]] = {}
        hashes: dict[str, str] = {}
        snapshots: list[tuple[Path, tuple[int, int, int, int, int, int]]] = []
        try:
            for filename in TRIO:
                snapshot = read_hashed_frontmatter(record / filename)
                metadata[filename] = snapshot.metadata
                hashes[filename] = snapshot.digest
                snapshots.append((record / filename, snapshot.stamp))
            for path, stamp_value in snapshots:
                verify_unchanged_path(path, stamp_value)
        except FrontmatterError:
            return TrioReadResult("malformed", {}, {}, ())
        except UnsafeFileError:
            return TrioReadResult("unsafe", {}, {}, ())
        except (ConcurrentReadError, FileNotFoundError):
            return TrioReadResult("changed", {}, {}, ())
        return TrioReadResult("ok", metadata, hashes, tuple(snapshots))

    def validate_staging(self) -> None:
        if self.record_type not in {"active-task", "active-repo"}:
            return
        staging = (
            self.record / ".staging"
            if self.record_type == "active-task"
            else self.root / ".planning" / "_repo" / ".staging"
        )
        if not staging.exists():
            return
        if staging.is_symlink() or path_has_symlink(staging, self.root) or not staging.is_dir():
            self.add_issue("invalid_staging", "invalid", "The staging path is not a regular directory.")
            return
        if any(staging.iterdir()):
            self.add_issue("unfinished_transaction", "incomplete", "An unresolved plan-local staging transaction exists.")

    def validate_history_surface(self) -> None:
        if self.record_type not in {"active-task", "active-repo"}:
            return
        history = (
            self.record / "history"
            if self.record_type == "active-task"
            else self.root / ".planning" / "_repo" / "history"
        )
        if not history.exists():
            return
        if history.is_symlink() or path_has_symlink(history, self.root) or not history.is_dir():
            self.add_issue("invalid_history", "invalid", "The plan-local history path is not one safe directory.")
            return
        for entry in sorted(history.iterdir()):
            match = HISTORY_NAME_RE.fullmatch(entry.name)
            if entry.is_symlink() or not entry.is_dir() or match is None:
                self.add_issue("invalid_history_record", "invalid", "A plan-local history entry is not canonical.")
                continue
            required = [entry / name for name in (*TRIO, "SNAPSHOT.md")]
            if any(path.is_symlink() or not path.is_file() for path in required):
                self.add_issue("partial_history_record", "incomplete", f"History record is partial: {entry.name}.")

    def validate_snapshot_stability(self) -> None:
        for filename, (path, stamp_value) in self.file_stamps.items():
            try:
                verify_unchanged_path(path, stamp_value)
            except ConcurrentReadError as exc:
                self.add_issue("record_changed_during_validation", "stale", f"Unstable {filename}: {exc}.")

    def candidate_task_plans(self) -> Iterable[tuple[Path, bool]]:
        root_task = self.root / "task_plan.md"
        if not root_task.is_symlink() and root_task.is_file():
            yield root_task, True

        plans_dir = self.root / ".planning" / "plans"
        if self.safe_lineage_directory(plans_dir):
            for child in sorted(plans_dir.iterdir()):
                task = child / "task_plan.md"
                if child.is_symlink() or not child.is_dir() or path_has_symlink(child, self.root):
                    self.add_issue("lineage_scope_unsafe", "invalid", "A task-plan lineage path is unsafe.")
                    continue
                if task.is_symlink() or not task.is_file():
                    self.add_issue("lineage_record_invalid", "stale", "A managed task-plan directory lacks one regular task_plan.md.")
                    continue
                yield task, True

        for branch in ("plans", "repo"):
            archive_dir = self.root / ".planning" / "archive" / branch
            if self.safe_lineage_directory(archive_dir):
                for child in sorted(archive_dir.iterdir()):
                    task = child / "task_plan.md"
                    if child.is_symlink() or not child.is_dir() or path_has_symlink(child, self.root):
                        self.add_issue("lineage_scope_unsafe", "invalid", "An archive lineage path is unsafe.")
                        continue
                    if task.is_symlink() or not task.is_file():
                        self.add_issue("lineage_record_invalid", "stale", "A managed archive lacks one regular task_plan.md.")
                        continue
                    yield task, False

    def safe_lineage_directory(self, path: Path) -> bool:
        if path.is_symlink() or path_has_symlink(path, self.root):
            self.add_issue("lineage_scope_unsafe", "invalid", "A lineage namespace crosses a symlink boundary.")
            return False
        if not path.exists():
            return False
        if not path.is_dir():
            self.add_issue("lineage_scope_unsafe", "invalid", "A lineage namespace is not a directory.")
            return False
        try:
            resolved = path.resolve(strict=True)
        except (OSError, RuntimeError):
            self.add_issue("lineage_scope_unsafe", "invalid", "A lineage namespace cannot be resolved safely.")
            return False
        if not is_within(resolved, self.root):
            self.add_issue("lineage_scope_unsafe", "invalid", "A lineage namespace resolves outside the canonical root.")
            return False
        return True

    def validate_lineage(self) -> None:
        selected = self.metadata.get("task_plan.md")
        if selected is None or not isinstance(selected.get("plan_id"), str):
            return

        records: dict[str, list[tuple[dict[str, Any], bool, Path]]] = {}
        archive_controls: dict[str, dict[str, Any]] = {}
        for task_path, active in self.candidate_task_plans():
            root_candidate = task_path == self.root / "task_plan.md"
            try:
                metadata = parse_frontmatter(task_path)
            except (FrontmatterError, ConcurrentReadError, UnsafeFileError):
                if root_candidate:
                    # A repository may own an unrelated root task_plan.md.
                    # Only planning-owner metadata opts it into this lineage.
                    continue
                self.add_issue("lineage_record_unreadable", "stale", "A lineage candidate has unreadable frontmatter.")
                continue
            if metadata.get("planning_owner") != OWNER:
                if root_candidate:
                    continue
                self.add_issue("lineage_record_unmanaged", "stale", "A managed-namespace lineage record lacks planning ownership metadata.")
                continue
            plan_id = metadata.get("plan_id")
            if not isinstance(plan_id, str) or PLAN_ID_RE.fullmatch(plan_id) is None:
                self.add_issue("lineage_record_invalid", "stale", "A managed lineage candidate lacks a valid plan_id.")
                continue
            generation = metadata.get("generation")
            if (
                metadata.get("plan_kind") not in {"repo", "task"}
                or metadata.get("plan_status") not in VALID_PLAN_STATUS
                or not isinstance(generation, int)
                or isinstance(generation, bool)
                or generation < 1
            ):
                self.add_issue("lineage_record_invalid", "stale", f"Managed lineage identity is malformed: {plan_id}.")
                continue
            if not self.lineage_trio_is_consistent(task_path, metadata):
                continue
            if not active:
                archive_control = self.read_lineage_archive_control(task_path.parent, metadata)
                if archive_control is None:
                    continue
                archive_controls[plan_id] = archive_control
            malformed_lineage = any(
                field in metadata
                and (not isinstance(metadata[field], str) or PLAN_ID_RE.fullmatch(metadata[field]) is None)
                for field in ("root_plan_id", "parent_plan_id", "predecessor_plan_id")
            )
            if malformed_lineage:
                self.add_issue("lineage_record_invalid", "stale", f"Managed lineage metadata is malformed: {plan_id}.")
            records.setdefault(plan_id, []).append((metadata, active, task_path))

        for plan_id, entries in records.items():
            if len(entries) > 1:
                self.add_issue("duplicate_plan_id", "invalid", f"plan_id appears in multiple live or terminal records: {plan_id}.")

        selected_id = selected["plan_id"]
        for field in ("root_plan_id", "parent_plan_id", "predecessor_plan_id"):
            if selected.get(field) == selected_id:
                self.add_issue("lineage_self_link", "invalid", f"{field} cannot reference the current plan.")

        def one_record(plan_id: str) -> tuple[dict[str, Any], bool, Path] | None:
            entries = records.get(plan_id, [])
            return entries[0] if len(entries) == 1 else None

        root_id = selected.get("root_plan_id")
        if isinstance(root_id, str):
            target = one_record(root_id)
            if target is None:
                self.add_issue("lineage_unresolved", "stale", "root_plan_id is not uniquely visible in the canonical root.")
            elif not target[1] or target[0].get("plan_kind") != "repo" or target[0].get("plan_status") == "closed":
                self.add_issue("inactive_root_plan", "stale", "root_plan_id does not reference one active repo plan.")

        parent_id = selected.get("parent_plan_id")
        if isinstance(parent_id, str):
            target = one_record(parent_id)
            if target is None:
                self.add_issue("lineage_unresolved", "stale", "parent_plan_id is not uniquely visible in the canonical root.")
            elif not target[1] or target[0].get("plan_kind") != "task" or target[0].get("plan_status") == "closed":
                self.add_issue("inactive_parent_plan", "stale", "parent_plan_id does not reference one active task plan.")

        predecessor_id = selected.get("predecessor_plan_id")
        if isinstance(predecessor_id, str) and one_record(predecessor_id) is None:
            self.add_issue("lineage_unresolved", "stale", "predecessor_plan_id is not uniquely visible in the canonical root.")

        initialized_from = selected.get("initialized_from")
        if isinstance(initialized_from, str) and INITIALIZED_FROM_RE.fullmatch(initialized_from):
            if initialized_from.startswith("archive:"):
                remainder = initialized_from.removeprefix("archive:")
                source_id, selector = remainder.split("#", 1)
                target = one_record(source_id)
                if target is None or target[1]:
                    self.add_issue("lineage_unresolved", "stale", "initialized_from archive is not uniquely visible.")
                else:
                    trust = archive_controls.get(source_id, {}).get("record_trust")
                    if trust == "invalidated":
                        self.add_issue("lineage_source_invalidated", "invalid", "initialized_from cannot use an invalidated archive.")
                    elif trust == "redacted":
                        self.add_issue("lineage_source_requires_review", "stale", "initialized_from redacted archive requires completeness review.")
                    elif selector == "original" and trust != "valid":
                        self.add_issue("lineage_unresolved", "stale", "The original archive selector does not include its active correction chain.")
                    elif selector.startswith("c"):
                        corrections = target[2].parent / "corrections"
                        matches = [] if not self.safe_lineage_directory(corrections) else list(corrections.glob(f"{selector}-*.md"))
                        canonical = any(
                            path.is_file()
                            and not path.is_symlink()
                            and CORRECTION_NAME_RE.fullmatch(path.name) is not None
                            for path in matches
                        )
                        if trust != "corrected" or not canonical:
                            self.add_issue("lineage_unresolved", "stale", "initialized_from correction is not controlled or visible.")
            elif initialized_from.startswith("plan:"):
                remainder = initialized_from.removeprefix("plan:")
                source_id, generation_selector = remainder.split("@g", 1)
                target = one_record(source_id)
                if target is None or target[0].get("generation") != int(generation_selector):
                    self.add_issue("lineage_unresolved", "stale", "initialized_from plan generation is not visible.")
            elif initialized_from.startswith("snapshot:"):
                remainder = initialized_from.removeprefix("snapshot:")
                source_and_generation, separator, correction_selector = remainder.partition("#")
                source_id, generation_selector = source_and_generation.split("@g", 1)
                selector_status = self.snapshot_selector_status(
                    source_id,
                    int(generation_selector),
                    correction_selector if separator else None,
                    records,
                )
                if selector_status == "missing":
                    self.add_issue("lineage_unresolved", "stale", "initialized_from snapshot is not visible.")
                elif selector_status == "invalid":
                    self.add_issue("lineage_control_invalid", "stale", "initialized_from snapshot control is incomplete or inconsistent.")
                elif selector_status == "invalidated":
                    self.add_issue("lineage_source_invalidated", "invalid", "initialized_from cannot use an invalidated snapshot.")
                elif selector_status == "review":
                    self.add_issue("lineage_source_requires_review", "stale", "initialized_from snapshot requires its correction or completeness review.")

        for field in ("parent_plan_id", "predecessor_plan_id"):
            chain: list[str] = []
            current_id: str | None = selected_id
            while current_id is not None:
                if current_id in chain:
                    self.add_issue("lineage_cycle", "invalid", f"{field} contains a cycle reachable from the selected plan.")
                    break
                chain.append(current_id)
                current = one_record(current_id)
                if current is None:
                    break
                next_id = current[0].get(field)
                current_id = next_id if isinstance(next_id, str) else None

        selected_terminal = selected.get("plan_status") == "closed" or self.record_type == "terminal-archive"
        if selected_terminal:
            for plan_id, entries in records.items():
                for metadata, active, _ in entries:
                    if not active or metadata.get("plan_status") == "closed":
                        continue
                    if metadata.get("parent_plan_id") == selected_id or metadata.get("root_plan_id") == selected_id:
                        self.add_issue("active_child_of_terminal", "invalid", f"Active child still references terminal plan: {plan_id}.")

    def lineage_trio_is_consistent(self, task_path: Path, task: dict[str, Any]) -> bool:
        for filename in ("findings.md", "progress.md"):
            path = task_path.parent / filename
            if path.is_symlink() or path_has_symlink(path, self.root) or not path.is_file():
                self.add_issue("lineage_record_invalid", "stale", "A managed lineage candidate has a partial or unsafe trio.")
                return False
            try:
                metadata = parse_frontmatter(path)
            except (FrontmatterError, ConcurrentReadError, UnsafeFileError):
                self.add_issue("lineage_record_invalid", "stale", "A managed lineage candidate has unreadable trio metadata.")
                return False
            if (
                metadata.get("planning_owner") != OWNER
                or metadata.get("schema_version") != 1
                or metadata.get("plan_id") != task.get("plan_id")
                or metadata.get("generation") != task.get("generation")
                or metadata.get("plan_role") != ROLE_BY_FILE[filename]
            ):
                self.add_issue("lineage_record_invalid", "stale", "A managed lineage candidate has inconsistent trio metadata.")
                return False
        return True

    def read_lineage_archive_control(self, archive: Path, task: dict[str, Any]) -> dict[str, Any] | None:
        path = archive / "ARCHIVE.md"
        if path.is_symlink() or path_has_symlink(path, self.root) or not path.is_file():
            self.add_issue("lineage_control_invalid", "stale", "A terminal lineage record lacks a safe ARCHIVE.md.")
            return None
        try:
            control = parse_frontmatter(path)
        except (FrontmatterError, ConcurrentReadError, UnsafeFileError):
            self.add_issue("lineage_control_invalid", "stale", "A terminal lineage record has unreadable ARCHIVE.md metadata.")
            return None
        hashes = control.get("source_hashes")
        hashes_valid = isinstance(hashes, dict) and all(
            isinstance(hashes.get(filename), str) and HASH_RE.fullmatch(hashes[filename]) is not None
            for filename in TRIO
        )
        if (
            control.get("record_type") != "terminal-archive"
            or control.get("record_trust") not in VALID_RECORD_TRUST
            or control.get("plan_id") != task.get("plan_id")
            or control.get("generation") != task.get("generation")
            or task.get("plan_status") != "closed"
            or not hashes_valid
        ):
            self.add_issue("lineage_control_invalid", "stale", "ARCHIVE.md does not control the terminal lineage record.")
            return None
        return control

    def snapshot_selector_status(
        self,
        plan_id: str,
        generation: int,
        correction_selector: str | None,
        records: dict[str, list[tuple[dict[str, Any], bool, Path]]],
    ) -> str:
        entries = records.get(plan_id, [])
        bases: list[Path] = []
        for metadata, active, task_path in entries:
            if metadata.get("plan_kind") == "repo":
                if active:
                    bases.append(self.root / ".planning" / "_repo" / "history")
                else:
                    bases.append(task_path.parent / "history")
            else:
                bases.append(task_path.parent / "history")
        prefix = f"g{generation:04d}-"
        candidates: list[Path] = []
        for base in bases:
            if not self.safe_lineage_directory(base):
                continue
            for child in base.iterdir():
                match = HISTORY_NAME_RE.fullmatch(child.name)
                if (
                    child.is_symlink()
                    or not child.is_dir()
                    or match is None
                    or not child.name.startswith(prefix)
                ):
                    continue
                required = [child / filename for filename in (*TRIO, "SNAPSHOT.md")]
                if any(path.is_symlink() or not path.is_file() for path in required):
                    continue
                candidates.append(child)
        if not candidates:
            return "missing"
        if len(candidates) != 1:
            return "invalid"

        child = candidates[0]
        control = child / "SNAPSHOT.md"
        try:
            metadata = parse_frontmatter(control)
        except (FrontmatterError, ConcurrentReadError, UnsafeFileError):
            return "invalid"
        hashes = metadata.get("source_hashes")
        hashes_valid = isinstance(hashes, dict) and all(
            isinstance(hashes.get(filename), str) and HASH_RE.fullmatch(hashes[filename]) is not None
            for filename in TRIO
        )
        trust = metadata.get("record_trust")
        if (
            metadata.get("record_type") != "generation-snapshot"
            or trust not in VALID_RECORD_TRUST
            or metadata.get("plan_id") != plan_id
            or metadata.get("generation") != generation
            or metadata.get("target_generation") != generation + 1
            or not isinstance(metadata.get("created_at"), str)
            or RFC3339_UTC_RE.fullmatch(metadata["created_at"]) is None
            or not hashes_valid
        ):
            return "invalid"
        if trust == "invalidated":
            return "invalidated"
        if trust == "redacted":
            return "review"
        if trust == "valid":
            return "valid" if correction_selector is None else "invalid"
        if correction_selector is None:
            return "review"

        corrections = child / "corrections"
        if not self.safe_lineage_directory(corrections):
            return "invalid"
        matches = list(corrections.glob(f"{correction_selector}-*.md"))
        if any(
            path.is_file()
            and not path.is_symlink()
            and CORRECTION_NAME_RE.fullmatch(path.name) is not None
            for path in matches
        ):
            return "valid"
        return "invalid"

    def compute_status(self) -> str:
        categories = {issue.category for issue in self.issues}
        if "invalid" in categories:
            return "invalid"
        if "incomplete" in categories:
            return "incomplete"
        if "stale" in categories:
            return "stale"
        return "valid"

    def compute_hash_binding_scope(self) -> str:
        if set(self.source_hashes) != set(TRIO):
            return "none"
        blocking = [issue for issue in self.issues if issue.category != "info"]
        if not blocking:
            return "standard"
        if (
            self.needs_rebind
            and len(blocking) == 1
            and blocking[0].code == "canonical_root_mismatch"
        ):
            return "rebind-preview-only"
        return "none"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read-only validator for one managed file-backed planning record.",
    )
    parser.add_argument("--canonical-root", required=True, type=Path, help="Resolved project or worktree root.")
    parser.add_argument("--record", required=True, type=Path, help="Explicit planning record directory to validate.")
    parser.add_argument("--check-lineage", action="store_true", help="Check bounded local plan-id relationships.")
    parser.add_argument(
        "--for-initialization",
        action="store_true",
        help="Require a frozen record to be eligible for initialization.",
    )
    parser.add_argument("--json", action="store_true", dest="json_output", help="Emit machine-readable JSON.")
    return parser


def print_result(result: dict[str, Any], *, json_output: bool) -> None:
    if json_output:
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    print(f"status: {result['status']}")
    print(f"record_type: {result['record_type']}")
    print(f"record: {result['record']}")
    if result.get("plan_id") is not None:
        print(f"plan_id: {result['plan_id']}")
    if result.get("generation") is not None:
        print(f"generation: {result['generation']}")
    if result.get("record_trust") is not None:
        print(f"record_trust: {result['record_trust']}")
    if result.get("transaction_phase") is not None:
        print(f"transaction_phase: {result['transaction_phase']}")
    print(f"needs_rebind: {str(result['needs_rebind']).lower()}")
    print(f"hash_binding_scope: {result['hash_binding_scope']}")
    for issue in result["issues"]:
        print(f"- [{issue['category']}] {issue['code']}: {issue['message']}")


def print_invocation_error(message: str, *, json_output: bool) -> None:
    if json_output:
        print(
            json.dumps(
                {
                    "schema_version": 1,
                    "status": "invocation_error",
                    "error": "invocation_error",
                    "message": message,
                },
                indent=2,
                sort_keys=True,
            )
        )
    else:
        print(f"error: {message}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        validator = PlanValidator(
            args.canonical_root,
            args.record,
            check_lineage=args.check_lineage,
            for_initialization=args.for_initialization,
        )
        result = validator.validate()
    except (InvocationError, OSError) as exc:
        print_invocation_error(str(exc), json_output=args.json_output)
        return 2
    print_result(result, json_output=args.json_output)
    return 0 if result["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
