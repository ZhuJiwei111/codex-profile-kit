#!/usr/bin/env python3
"""Read-only validator for one project-root serial-phase planning record."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
from typing import Any


OWNER = "personal-planning-with-files-zh"
SCHEMA_VERSION = 2
TRIO = ("task_plan.md", "findings.md", "progress.md")
PLANNING_NAMESPACES = ("plans", "snapshots", "archive")
OPERATIONS = ("inspect", "init", "resume", "correct", "archive", "successor")
STATUSES = {"draft", "active", "closed"}
ID_RE = re.compile(r"[a-z0-9][a-z0-9-]{2,63}\Z")
LEGACY_FIELDS = {
    "generation",
    "root_plan_id",
    "parent_plan_id",
    "predecessor_plan_id",
    "initialized_from",
    "record_trust",
    "closure_status",
}


class InvocationError(RuntimeError):
    """The requested root or record cannot be inspected safely."""


class UnsafeManagedPath(RuntimeError):
    """A managed path crossed a symlink or a non-directory component."""


class ConcurrentReadError(RuntimeError):
    """A managed path changed during a bounded inspection."""


class FrontmatterError(RuntimeError):
    """A controlled file has invalid frontmatter."""


@dataclass(frozen=True)
class Issue:
    code: str
    message: str
    path: str | None = None


PathSignature = tuple[int, int, int, int, int, int]
IdentitySignature = tuple[int, int, int]
DirectoryChain = tuple[tuple[tuple[str, ...], IdentitySignature], ...]


@dataclass(frozen=True)
class DirectorySnapshot:
    relative: tuple[str, ...]
    chain: DirectoryChain
    signature: PathSignature
    entries: tuple[tuple[str, PathSignature], ...]


@dataclass(frozen=True)
class ControlledRead:
    relative: tuple[str, ...]
    digest: str
    signature: PathSignature
    chain: DirectoryChain


def _path_signature(info: os.stat_result | Any) -> PathSignature:
    return (
        info.st_dev,
        info.st_ino,
        info.st_mode,
        info.st_size,
        info.st_mtime_ns,
        info.st_nlink,
    )


def _identity_signature(info: os.stat_result | Any) -> IdentitySignature:
    return (info.st_dev, info.st_ino, info.st_mode)


class RootAccess:
    """Root-anchored, no-follow access to every managed planning path."""

    def __init__(self, root: Path) -> None:
        if not root.is_absolute():
            raise InvocationError("canonical root must be absolute")
        if root.anchor != "/":
            raise InvocationError("canonical root must use the filesystem / anchor")
        root_parts = tuple(root.parts[1:])
        if any(part in {"", ".", ".."} or "/" in part or "\x00" in part for part in root_parts):
            raise InvocationError("canonical root contains an unsafe path component")

        if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
            raise InvocationError("platform lacks required no-follow directory access")
        if os.open not in os.supports_dir_fd or os.stat not in os.supports_dir_fd:
            raise InvocationError("platform lacks required root-anchored dir_fd access")
        if os.stat not in os.supports_follow_symlinks:
            raise InvocationError("platform lacks required no-follow stat access")

        self.root = root
        self._dir_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
        if hasattr(os, "O_CLOEXEC"):
            self._dir_flags |= os.O_CLOEXEC
        self._file_flags = os.O_RDONLY | os.O_NOFOLLOW
        if hasattr(os, "O_CLOEXEC"):
            self._file_flags |= os.O_CLOEXEC

        try:
            self._root_fd, self._anchor_chain = self._open_anchor_chain(root_parts)
        except (OSError, UnsafeManagedPath) as exc:
            raise InvocationError(f"cannot open canonical root without following links: {root}") from exc
        self._root_parts = root_parts
        root_info = os.fstat(self._root_fd)
        if not stat.S_ISDIR(root_info.st_mode):
            os.close(self._root_fd)
            raise InvocationError(f"canonical root is not a directory: {root}")
        self._root_signature = _path_signature(root_info)
        self._root_identity = _identity_signature(root_info)
        self._controlled_reads: dict[tuple[str, ...], ControlledRead] = {}
        self._directory_snapshots: dict[tuple[str, ...], DirectorySnapshot] = {}
        self._absent_paths: set[tuple[str, ...]] = set()
        self._closed = False
        try:
            self._verify_root_identity()
        except ConcurrentReadError as exc:
            self.close()
            raise InvocationError(str(exc)) from exc

    def _open_anchor_chain(self, parts: tuple[str, ...]) -> tuple[int, DirectoryChain]:
        """Open an absolute directory one component at a time from `/`."""

        descriptor = os.open("/", self._dir_flags)
        root_info = os.fstat(descriptor)
        if not stat.S_ISDIR(root_info.st_mode):
            os.close(descriptor)
            raise UnsafeManagedPath("filesystem anchor is not a real directory")
        chain: list[tuple[tuple[str, ...], IdentitySignature]] = [
            ((), _identity_signature(root_info))
        ]
        prefix: list[str] = []
        try:
            for part in parts:
                try:
                    child = os.open(part, self._dir_flags, dir_fd=descriptor)
                except OSError as exc:
                    raise UnsafeManagedPath(
                        f"absolute root component cannot be opened without following links: "
                        f"/{'/'.join(prefix + [part])}"
                    ) from exc
                os.close(descriptor)
                descriptor = child
                info = os.fstat(descriptor)
                if not stat.S_ISDIR(info.st_mode):
                    raise UnsafeManagedPath(
                        f"absolute root component is not a real directory: "
                        f"/{'/'.join(prefix + [part])}"
                    )
                prefix.append(part)
                chain.append((tuple(prefix), _identity_signature(info)))
            return descriptor, tuple(chain)
        except Exception:
            os.close(descriptor)
            raise

    def close(self) -> None:
        if not self._closed:
            os.close(self._root_fd)
            self._closed = True

    def _parts(self, relative: Path | str) -> tuple[str, ...]:
        path = Path(relative)
        if path.is_absolute():
            raise UnsafeManagedPath("managed paths must be relative to the canonical root")
        parts = tuple(part for part in path.parts if part != ".")
        if any(part in {"", ".", ".."} or "/" in part or "\x00" in part for part in parts):
            raise UnsafeManagedPath("managed path contains an unsafe component")
        return parts

    def _display(self, parts: tuple[str, ...]) -> str:
        return str(self.root.joinpath(*parts))

    def _verify_root_identity(self) -> None:
        try:
            descriptor, chain = self._open_anchor_chain(self._root_parts)
        except (OSError, UnsafeManagedPath) as exc:
            raise ConcurrentReadError("canonical root identity changed during inspection") from exc
        try:
            if chain != self._anchor_chain or _identity_signature(os.fstat(descriptor)) != self._root_identity:
                raise ConcurrentReadError("canonical root identity changed during inspection")
        finally:
            os.close(descriptor)

    def _open_directory(self, parts: tuple[str, ...]) -> tuple[int, DirectoryChain]:
        descriptor = os.dup(self._root_fd)
        chain: list[tuple[tuple[str, ...], IdentitySignature]] = [((), self._root_identity)]
        prefix: list[str] = []
        try:
            for part in parts:
                try:
                    child = os.open(part, self._dir_flags, dir_fd=descriptor)
                except FileNotFoundError:
                    raise
                except OSError as exc:
                    raise UnsafeManagedPath(
                        f"managed directory cannot be opened without following links: "
                        f"{self._display(tuple(prefix + [part]))}"
                    ) from exc
                os.close(descriptor)
                descriptor = child
                info = os.fstat(descriptor)
                if not stat.S_ISDIR(info.st_mode):
                    raise UnsafeManagedPath(
                        f"managed directory component is not a real directory: "
                        f"{self._display(tuple(prefix + [part]))}"
                    )
                prefix.append(part)
                chain.append((tuple(prefix), _identity_signature(info)))
            return descriptor, tuple(chain)
        except Exception:
            os.close(descriptor)
            raise

    def _verify_chain(self, expected: DirectoryChain) -> None:
        try:
            descriptor, anchor_chain = self._open_anchor_chain(self._root_parts)
        except (OSError, UnsafeManagedPath) as exc:
            raise ConcurrentReadError("canonical root identity changed during inspection") from exc
        try:
            if anchor_chain != self._anchor_chain:
                raise ConcurrentReadError("canonical root anchor chain changed during inspection")
            if not expected or expected[0][0] != ():
                raise ConcurrentReadError("invalid managed directory identity chain")
            if _identity_signature(os.fstat(descriptor)) != expected[0][1]:
                raise ConcurrentReadError("canonical root identity changed during inspection")
            for parts, signature in expected[1:]:
                part = parts[-1]
                try:
                    child = os.open(part, self._dir_flags, dir_fd=descriptor)
                except OSError as exc:
                    raise ConcurrentReadError(
                        f"managed directory identity changed: {self._display(parts)}"
                    ) from exc
                os.close(descriptor)
                descriptor = child
                if _identity_signature(os.fstat(descriptor)) != signature:
                    raise ConcurrentReadError(
                        f"managed directory identity changed: {self._display(parts)}"
                    )
        finally:
            os.close(descriptor)

    def lstat(self, relative: Path | str, *, track_absence: bool = False) -> PathSignature | None:
        parts = self._parts(relative)
        if not parts:
            return self._root_signature
        try:
            parent, chain = self._open_directory(parts[:-1])
        except FileNotFoundError:
            if track_absence:
                self._absent_paths.add(parts)
            return None
        try:
            try:
                first = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
            except FileNotFoundError:
                self._verify_chain(chain)
                if track_absence:
                    self._absent_paths.add(parts)
                return None
            except OSError as exc:
                raise UnsafeManagedPath(
                    f"cannot inspect managed path safely: {self._display(parts)}"
                ) from exc
            first_signature = _path_signature(first)
        finally:
            os.close(parent)
        self._verify_chain(chain)

        try:
            parent, second_chain = self._open_directory(parts[:-1])
        except FileNotFoundError as exc:
            raise ConcurrentReadError(
                f"managed path parent changed during inspection: {self._display(parts)}"
            ) from exc
        try:
            try:
                second = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
            except FileNotFoundError as exc:
                raise ConcurrentReadError(
                    f"managed path changed during inspection: {self._display(parts)}"
                ) from exc
            except OSError as exc:
                raise UnsafeManagedPath(
                    f"cannot re-inspect managed path safely: {self._display(parts)}"
                ) from exc
            second_signature = _path_signature(second)
        finally:
            os.close(parent)
        self._verify_chain(second_chain)
        if chain != second_chain or first_signature != second_signature:
            raise ConcurrentReadError(
                f"managed path identity changed during inspection: {self._display(parts)}"
            )
        return second_signature

    def _directory_snapshot_once(self, parts: tuple[str, ...]) -> DirectorySnapshot:
        try:
            descriptor, chain = self._open_directory(parts)
        except FileNotFoundError as exc:
            raise ConcurrentReadError(
                f"managed directory disappeared during inspection: {self._display(parts)}"
            ) from exc
        try:
            before_info = os.fstat(descriptor)
            before = _path_signature(before_info)
            try:
                names = sorted(os.listdir(descriptor))
                entries = tuple(
                    (name, _path_signature(os.stat(name, dir_fd=descriptor, follow_symlinks=False)))
                    for name in names
                )
            except (FileNotFoundError, NotADirectoryError) as exc:
                raise ConcurrentReadError(
                    f"managed directory changed while listing: {self._display(parts)}"
                ) from exc
            except OSError as exc:
                raise UnsafeManagedPath(
                    f"cannot inspect managed directory safely: {self._display(parts)}"
                ) from exc
            after = _path_signature(os.fstat(descriptor))
        finally:
            os.close(descriptor)
        if before != after or _identity_signature(before_info) != chain[-1][1]:
            raise ConcurrentReadError(
                f"managed directory changed while listing: {self._display(parts)}"
            )
        self._verify_chain(chain)
        return DirectorySnapshot(parts, chain, before, entries)

    def list_directory(self, relative: Path | str, *, track: bool = True) -> dict[str, PathSignature]:
        parts = self._parts(relative)
        first = self._directory_snapshot_once(parts)
        second = self._directory_snapshot_once(parts)
        if first != second:
            raise ConcurrentReadError(
                f"managed directory identity changed during inspection: {self._display(parts)}"
            )
        if track:
            self._directory_snapshots[parts] = second
        return dict(second.entries)

    def _read_once(self, parts: tuple[str, ...]) -> tuple[bytes, ControlledRead]:
        if not parts:
            raise UnsafeManagedPath("a controlled file path cannot name the project root")
        try:
            parent, chain = self._open_directory(parts[:-1])
        except FileNotFoundError as exc:
            raise UnsafeManagedPath(
                f"controlled file parent is missing: {self._display(parts)}"
            ) from exc
        try:
            try:
                descriptor = os.open(parts[-1], self._file_flags, dir_fd=parent)
            except OSError as exc:
                raise UnsafeManagedPath(
                    f"cannot open controlled file without following links: {self._display(parts)}"
                ) from exc
        finally:
            os.close(parent)

        try:
            before = os.fstat(descriptor)
            if not stat.S_ISREG(before.st_mode):
                raise UnsafeManagedPath(
                    f"controlled path is not a regular file: {self._display(parts)}"
                )
            if before.st_nlink != 1:
                raise UnsafeManagedPath(
                    f"controlled file must have exactly one hard link: {self._display(parts)}"
                )
            chunks: list[bytes] = []
            try:
                while True:
                    chunk = os.read(descriptor, 1024 * 1024)
                    if not chunk:
                        break
                    chunks.append(chunk)
            except OSError as exc:
                raise UnsafeManagedPath(
                    f"cannot read controlled file safely: {self._display(parts)}"
                ) from exc
            after = os.fstat(descriptor)
            if _path_signature(before) != _path_signature(after):
                raise ConcurrentReadError(
                    f"controlled file changed while reading: {self._display(parts)}"
                )
            data = b"".join(chunks)
        finally:
            os.close(descriptor)

        self._verify_chain(chain)
        current = self.lstat(Path(*parts))
        signature = _path_signature(after)
        if current != signature:
            raise ConcurrentReadError(
                f"controlled file identity changed after reading: {self._display(parts)}"
            )
        record = ControlledRead(parts, hashlib.sha256(data).hexdigest(), signature, chain)
        return data, record

    def read_stable_text(self, relative: Path | str, *, track: bool = True) -> tuple[str, str]:
        parts = self._parts(relative)
        data, record = self._read_once(parts)
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise UnsafeManagedPath(
                f"controlled file is not UTF-8: {self._display(parts)}"
            ) from exc
        if track:
            self._controlled_reads[parts] = record
        return text, record.digest

    def final_recheck(self) -> None:
        """Recheck the bounded evidence set before emitting a result.

        This is a sequential identity/hash recheck, not a claim that multiple
        files were captured atomically.
        """

        for parts, expected in tuple(self._directory_snapshots.items()):
            current = self._directory_snapshot_once(parts)
            if current != expected:
                raise ConcurrentReadError(
                    f"managed namespace changed before result: {self._display(parts)}"
                )
        for parts in tuple(self._absent_paths):
            if self.lstat(Path(*parts), track_absence=False) is not None:
                raise ConcurrentReadError(
                    f"previously absent managed path appeared before result: {self._display(parts)}"
                )
        for parts, expected in tuple(self._controlled_reads.items()):
            _, current = self._read_once(parts)
            if current != expected:
                raise ConcurrentReadError(
                    f"controlled file changed before result: {self._display(parts)}"
                )


def _scalar(value: str) -> Any:
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        body = value[1:-1].strip()
        if not body:
            return []
        return [_scalar(part) for part in body.split(",")]
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    if re.fullmatch(r"-?[0-9]+", value):
        return int(value)
    if value in {"null", "~"}:
        return None
    return value


def parse_frontmatter(text: str, path: Path) -> dict[str, Any]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise FrontmatterError(f"missing opening frontmatter delimiter: {path}")
    try:
        end = next(index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration as exc:
        raise FrontmatterError(f"missing closing frontmatter delimiter: {path}") from exc

    metadata: dict[str, Any] = {}
    for line_number, line in enumerate(lines[1:end], start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[:1].isspace() or ":" not in line:
            raise FrontmatterError(f"unsupported frontmatter at {path}:{line_number}")
        key, raw_value = line.split(":", 1)
        key = key.strip()
        if not re.fullmatch(r"[a-z][a-z0-9_]*", key):
            raise FrontmatterError(f"invalid frontmatter key at {path}:{line_number}")
        if key in metadata:
            raise FrontmatterError(f"duplicate frontmatter key {key!r} at {path}:{line_number}")
        metadata[key] = _scalar(raw_value)
    return metadata


def _legacy_name(name: str) -> bool:
    lowered = name.lower()
    exact = {
        "_repo",
        ".staging",
        "transaction.md",
        "transactions",
        "packet.md",
        "generation-history",
    }
    return (
        lowered in exact
        or re.fullmatch(r"generation-[0-9]+", lowered) is not None
        or re.fullmatch(r"g[0-9]{4,}(?:-[a-z0-9][a-z0-9._-]*)?", lowered) is not None
    )


class Validator:
    def __init__(self, canonical_root: Path, operation: str, record: Path | None) -> None:
        self.access = RootAccess(canonical_root)
        self.root = canonical_root
        self.operation = operation
        self.record_input = record
        self.issues: list[Issue] = []
        self.hashes: dict[str, str] = {}
        self.root_metadata: dict[str, Any] = {}
        self.phase_metadata: dict[str, dict[str, dict[str, Any]]] = {}
        self.phase_statuses: dict[str, str] = {}
        self._finalized = False

    def close(self) -> None:
        self.access.close()

    def issue(self, code: str, message: str, path: Path | None = None) -> None:
        rendered = None
        if path is not None:
            try:
                rendered = str(path.relative_to(self.root))
            except ValueError:
                rendered = str(path)
        self.issues.append(Issue(code, message, rendered))

    def _full(self, relative: Path | str) -> Path:
        return self.root / Path(relative)

    def safe_lstat(self, relative: Path | str, *, track_absence: bool = False) -> PathSignature | None:
        try:
            return self.access.lstat(relative, track_absence=track_absence)
        except UnsafeManagedPath as exc:
            self.issue("unsafe_managed_path", str(exc), self._full(relative))
        except ConcurrentReadError as exc:
            self.issue("concurrent_change", str(exc), self._full(relative))
        return None

    def safe_list_directory(self, relative: Path | str) -> dict[str, PathSignature] | None:
        try:
            return self.access.list_directory(relative)
        except (UnsafeManagedPath, FileNotFoundError) as exc:
            self.issue("unsafe_managed_path", str(exc), self._full(relative))
        except ConcurrentReadError as exc:
            self.issue("concurrent_change", str(exc), self._full(relative))
        return None

    def read_metadata(self, relative: Path) -> dict[str, Any] | None:
        path = self._full(relative)
        try:
            text, digest = self.access.read_stable_text(relative)
            metadata = parse_frontmatter(text, path)
        except ConcurrentReadError as exc:
            self.issue("concurrent_change", str(exc), path)
            return None
        except UnsafeManagedPath as exc:
            self.issue("unsafe_managed_path", str(exc), path)
            return None
        except FrontmatterError as exc:
            self.issue("invalid_controlled_file", str(exc), path)
            return None
        self.hashes[relative.as_posix()] = digest
        return metadata

    def validate_fields(
        self,
        metadata: dict[str, Any],
        path: Path,
        *,
        required: set[str],
        allowed: set[str],
    ) -> None:
        for field in sorted(required - metadata.keys()):
            self.issue("missing_field", f"missing required field: {field}", path)
        for field in sorted(metadata.keys() - allowed):
            code = "legacy_field_forbidden" if field in LEGACY_FIELDS else "unexpected_field"
            self.issue(code, f"field is not part of the serial-phase contract: {field}", path)

    def validate_common(self, metadata: dict[str, Any], path: Path) -> None:
        if metadata.get("planning_owner") != OWNER:
            self.issue("invalid_owner", f"planning_owner must be {OWNER}", path)
        if metadata.get("schema_version") != SCHEMA_VERSION:
            self.issue("invalid_schema", f"schema_version must be {SCHEMA_VERSION}", path)
        plan_id = metadata.get("plan_id")
        if not isinstance(plan_id, str) or not ID_RE.fullmatch(plan_id):
            self.issue("invalid_plan_id", "plan_id must use 3-64 lowercase letters, digits, or hyphens", path)

    def validate_root(self, relative: Path) -> list[str]:
        path = self._full(relative)
        metadata = self.read_metadata(relative)
        if metadata is None:
            return []
        self.root_metadata = metadata
        required = {
            "planning_owner",
            "schema_version",
            "plan_kind",
            "plan_role",
            "plan_id",
            "plan_status",
            "canonical_root",
            "phases",
        }
        allowed = required | {"active_phase"}
        self.validate_fields(metadata, path, required=required, allowed=allowed)
        self.validate_common(metadata, path)
        if metadata.get("plan_kind") != "project" or metadata.get("plan_role") != "root":
            self.issue("invalid_root_role", "root task_plan.md must be plan_kind: project and plan_role: root", path)
        if metadata.get("canonical_root") != str(self.root):
            self.issue("canonical_root_mismatch", "recorded canonical_root does not match the inspected root", path)
        if metadata.get("plan_status") not in STATUSES:
            self.issue("invalid_plan_status", "plan_status must be draft, active, or closed", path)

        phases = metadata.get("phases")
        if not isinstance(phases, list) or not phases:
            self.issue("invalid_phase_order", "phases must be one non-empty ordered list", path)
            return []
        if any(not isinstance(phase, str) or not ID_RE.fullmatch(phase) for phase in phases):
            self.issue("invalid_phase_id", "every phase id must use 3-64 lowercase letters, digits, or hyphens", path)
            return []
        if len(set(phases)) != len(phases):
            self.issue("duplicate_phase_id", "the ordered phase list must not contain duplicates", path)
        return phases

    def validate_phase_file(
        self,
        relative: Path,
        phase_id: str,
        expected_role: str,
    ) -> dict[str, Any] | None:
        path = self._full(relative)
        metadata = self.read_metadata(relative)
        if metadata is None:
            return None
        common = {"planning_owner", "schema_version", "plan_kind", "plan_id", "phase_id", "plan_role"}
        allowed = set(common)
        required = set(common)
        if expected_role == "task_plan":
            allowed |= {"phase_status", "canonical_root"}
            required |= {"phase_status", "canonical_root"}
        elif expected_role == "findings":
            allowed.add("evidence_cutoff")
            required.add("evidence_cutoff")
        self.validate_fields(metadata, path, required=required, allowed=allowed)
        self.validate_common(metadata, path)
        if metadata.get("plan_kind") != "phase":
            self.issue("invalid_phase_kind", "phase files must use plan_kind: phase", path)
        if metadata.get("plan_role") != expected_role:
            self.issue("invalid_phase_role", f"plan_role must be {expected_role}", path)
        if metadata.get("phase_id") != phase_id:
            self.issue("phase_identity_mismatch", "phase_id must match its directory", path)
        if metadata.get("plan_id") != self.root_metadata.get("plan_id"):
            self.issue("plan_identity_mismatch", "phase plan_id must match the root plan", path)
        if expected_role == "task_plan":
            status_value = metadata.get("phase_status")
            if status_value not in STATUSES:
                self.issue("invalid_phase_status", "phase_status must be draft, active, or closed", path)
            if metadata.get("canonical_root") != str(self.root):
                self.issue("canonical_root_mismatch", "phase canonical_root must match the root", path)
        return metadata

    def validate_phase(self, phase_id: str, relative: Path) -> None:
        entries = self.safe_list_directory(relative)
        if entries is None:
            return
        names = set(entries)
        for name in sorted(names - set(TRIO)):
            code = "legacy_state_forbidden" if _legacy_name(name) else "unexpected_phase_entry"
            self.issue(code, f"phase directories may contain only the managed trio: {name}", self._full(relative / name))
            if stat.S_ISLNK(entries[name][2]):
                self.issue("unsafe_managed_path", "managed phase directories must not contain symlinks", self._full(relative / name))
        for name in TRIO:
            signature = entries.get(name)
            path = self._full(relative / name)
            if signature is None or not stat.S_ISREG(signature[2]):
                if signature is not None:
                    detail = "must not be a symlink" if stat.S_ISLNK(signature[2]) else "must be a real regular file"
                    self.issue("unsafe_managed_path", f"phase file {detail}: {name}", path)
                self.issue("incomplete_phase_trio", f"phase must contain one regular {name}", path)

        metadata_by_role: dict[str, dict[str, Any]] = {}
        for filename, role in zip(TRIO, ("task_plan", "findings", "progress")):
            signature = entries.get(filename)
            if signature is not None and stat.S_ISREG(signature[2]):
                metadata = self.validate_phase_file(relative / filename, phase_id, role)
                if metadata is not None:
                    metadata_by_role[role] = metadata
        self.phase_metadata[phase_id] = metadata_by_role
        task = metadata_by_role.get("task_plan", {})
        status_value = task.get("phase_status")
        if isinstance(status_value, str):
            self.phase_statuses[phase_id] = status_value

    def scan_safe_tree(self, relative: Path) -> None:
        entries = self.safe_list_directory(relative)
        if entries is None:
            return
        for name, signature in entries.items():
            path = relative / name
            mode = signature[2]
            if _legacy_name(name):
                self.issue(
                    "legacy_state_forbidden",
                    f"legacy planning state is forbidden in managed history: {name}",
                    self._full(path),
                )
            if stat.S_ISLNK(mode):
                self.issue("unsafe_managed_path", "managed history must not contain symlinks", self._full(path))
            elif stat.S_ISDIR(mode):
                self.scan_safe_tree(path)
            elif stat.S_ISREG(mode):
                if signature[5] != 1:
                    self.issue(
                        "unsafe_managed_path",
                        "managed history files must have exactly one hard link",
                        self._full(path),
                    )
            else:
                self.issue("unsafe_managed_path", "managed history may contain only real directories and regular files", self._full(path))

    def validate_namespace(self, phases: list[str] | None) -> None:
        planning = Path(".planning")
        planning_signature = self.safe_lstat(planning, track_absence=phases is None)
        if planning_signature is None:
            if phases is not None:
                for phase in phases:
                    self.issue("missing_phase_record", f"listed phase record is missing: {phase}", self._full(planning / "plans" / phase))
            return
        if not stat.S_ISDIR(planning_signature[2]):
            self.issue("unsafe_managed_path", ".planning must be one real directory", self._full(planning))
            return

        top_entries = self.safe_list_directory(planning)
        if top_entries is None:
            return
        for name in sorted(set(top_entries) - set(PLANNING_NAMESPACES)):
            code = "legacy_state_forbidden" if _legacy_name(name) else "unexpected_planning_entry"
            self.issue(code, f".planning may contain only plans, snapshots, and archive: {name}", self._full(planning / name))
            if stat.S_ISLNK(top_entries[name][2]):
                self.issue("unsafe_managed_path", "managed planning state must not contain symlinks", self._full(planning / name))

        for namespace in ("snapshots", "archive"):
            signature = top_entries.get(namespace)
            relative = planning / namespace
            if signature is None:
                continue
            if not stat.S_ISDIR(signature[2]):
                self.issue("unsafe_managed_path", f".planning/{namespace} must be one real directory", self._full(relative))
                continue
            self.scan_safe_tree(relative)

        plans = planning / "plans"
        plans_signature = top_entries.get("plans")
        if plans_signature is None:
            self.safe_lstat(plans, track_absence=phases is None)
            if phases is not None:
                for phase in phases:
                    self.issue("missing_phase_record", f"listed phase record is missing: {phase}", self._full(plans / phase))
            return
        if not stat.S_ISDIR(plans_signature[2]):
            self.issue("unsafe_managed_path", ".planning/plans must be one real directory", self._full(plans))
            return

        plan_entries = self.safe_list_directory(plans)
        if plan_entries is None:
            return
        if phases is None:
            if plan_entries:
                self.issue("orphan_active_plan_state", "active plan records exist without a root task_plan.md", self._full(plans))
            self.scan_safe_tree(plans)
            return

        visible: set[str] = set()
        for name, signature in plan_entries.items():
            path = plans / name
            if not stat.S_ISDIR(signature[2]):
                self.issue("unsafe_managed_path", "plans may contain only real phase directories", self._full(path))
                continue
            visible.add(name)
            if name not in phases:
                self.issue("unlisted_phase", "phase directory is absent from the root phase order", self._full(path))

        for phase in phases:
            record = plans / phase
            if phase not in visible:
                self.issue("missing_phase_record", f"listed phase record is missing: {phase}", self._full(record))
                continue
            self.validate_phase(phase, record)

    def validate_serial_state(self, phases: list[str]) -> None:
        plan_status = self.root_metadata.get("plan_status")
        active_pointer = self.root_metadata.get("active_phase")
        active_field_present = "active_phase" in self.root_metadata
        active_phases = [phase for phase in phases if self.phase_statuses.get(phase) == "active"]
        if len(active_phases) > 1:
            self.issue("multiple_active_phases", "only one phase may be active")

        if plan_status == "draft":
            if active_field_present:
                self.issue("unexpected_active_phase_field", "a draft project must omit active_phase entirely")
            if active_pointer is not None or active_phases:
                self.issue("invalid_active_phase", "a draft project cannot have an active phase")
            if any(self.phase_statuses.get(phase) != "draft" for phase in phases):
                self.issue("invalid_serial_state", "every phase must remain draft while the project is draft")
            return

        if plan_status == "closed":
            if active_field_present:
                self.issue("unexpected_active_phase_field", "a closed project must omit active_phase entirely")
            if active_pointer is not None or active_phases:
                self.issue("invalid_active_phase", "a closed project cannot have an active phase")
            if any(self.phase_statuses.get(phase) != "closed" for phase in phases):
                self.issue("invalid_serial_state", "every phase must be closed before the project closes")
            return

        if plan_status != "active":
            return
        if not isinstance(active_pointer, str) or active_pointer not in phases:
            self.issue("invalid_active_phase", "an active project must point to one listed phase")
            return
        if active_phases != [active_pointer]:
            self.issue("invalid_active_phase", "active_phase must name the only active phase")
        active_index = phases.index(active_pointer)
        expected = {
            phase: "closed" if index < active_index else "active" if index == active_index else "draft"
            for index, phase in enumerate(phases)
        }
        if any(self.phase_statuses.get(phase) != status_value for phase, status_value in expected.items()):
            self.issue("invalid_serial_state", "phases before active_phase must be closed and later phases draft")

    def validate_operation(self) -> None:
        status_value = self.root_metadata.get("plan_status")
        permitted = {
            "inspect": STATUSES,
            "init": {"draft"},
            "resume": {"draft", "active"},
            "correct": STATUSES,
            "archive": {"closed"},
            "successor": {"closed"},
        }[self.operation]
        if status_value not in permitted:
            self.issue("operation_not_allowed", f"operation {self.operation} is not allowed for plan_status {status_value}")

    def validate_record_selector(self, phases: list[str]) -> str:
        if self.record_input is None:
            return str(self.root)
        if not self.record_input.is_absolute():
            raise InvocationError("record must be an absolute path")
        selected = self.record_input
        allowed = {self.root, *(self.root / ".planning" / "plans" / phase for phase in phases)}
        if selected not in allowed:
            raise InvocationError("record must be the canonical root or one listed phase directory")
        if selected == self.root:
            return str(selected)
        relative = selected.relative_to(self.root)
        try:
            signature = self.access.lstat(relative)
        except (UnsafeManagedPath, ConcurrentReadError) as exc:
            raise InvocationError("record must not cross symlinks or changed path identities") from exc
        if signature is None or not stat.S_ISDIR(signature[2]):
            raise InvocationError("selected record does not exist as one real directory")
        return str(selected)

    def finalize_evidence(self) -> None:
        if self._finalized:
            return
        self._finalized = True
        try:
            self.access.final_recheck()
        except UnsafeManagedPath as exc:
            self.issue("unsafe_managed_path", str(exc))
        except ConcurrentReadError as exc:
            self.issue("concurrent_change", str(exc))

    def result(self) -> tuple[int, dict[str, Any]]:
        for relative in (Path("findings.md"), Path("progress.md")):
            signature = self.safe_lstat(relative)
            if signature is not None:
                if stat.S_ISLNK(signature[2]):
                    self.issue("unsafe_managed_path", "forbidden root detail path must not be a symlink", self._full(relative))
                self.issue("duplicate_root_truth", "root findings/progress are forbidden; phase trios own detail", self._full(relative))

        root_relative = Path("task_plan.md")
        root_signature = self.safe_lstat(root_relative, track_absence=True)
        if root_signature is None:
            self.validate_namespace(None)
            if self.operation != "init":
                self.issue("missing_root_plan", "project root task_plan.md is required", self._full(root_relative))
            self.finalize_evidence()
            if self.operation == "init" and not self.issues:
                return 0, self.payload(str(self.root), status="initializable")
            return 1, self.payload(str(self.root))
        if not stat.S_ISREG(root_signature[2]):
            self.issue("unsafe_managed_path", "project root task_plan.md must be one real regular file", self._full(root_relative))
            self.validate_namespace(None)
            self.finalize_evidence()
            return 1, self.payload(str(self.root))

        phases = self.validate_root(root_relative)
        self.validate_namespace(phases)
        self.validate_serial_state(phases)
        self.validate_operation()
        selected = self.validate_record_selector(phases)
        self.finalize_evidence()
        payload = self.payload(selected)
        return (1 if self.issues else 0), payload

    def payload(self, selected: str, *, status: str | None = None) -> dict[str, Any]:
        return {
            "status": "invalid" if self.issues else status or "valid",
            "operation": self.operation,
            "canonical_root": str(self.root),
            "selected_record": selected,
            "plan_id": self.root_metadata.get("plan_id"),
            "plan_status": self.root_metadata.get("plan_status"),
            "active_phase": self.root_metadata.get("active_phase"),
            "phase_statuses": self.phase_statuses,
            "source_hashes": self.hashes,
            "issues": [asdict(issue) for issue in self.issues],
        }


def invocation_payload(operation: str, canonical_root: Path, message: str) -> dict[str, Any]:
    return {
        "status": "invocation_error",
        "operation": operation,
        "canonical_root": str(canonical_root),
        "selected_record": None,
        "plan_id": None,
        "plan_status": None,
        "active_phase": None,
        "phase_statuses": {},
        "source_hashes": {},
        "issues": [{"code": "invocation_error", "message": message, "path": None}],
    }


def render_text(payload: dict[str, Any]) -> str:
    lines = [
        f"status: {payload['status']}",
        f"operation: {payload['operation']}",
        f"canonical_root: {payload['canonical_root']}",
        f"plan_id: {payload['plan_id']}",
        f"plan_status: {payload['plan_status']}",
        f"active_phase: {payload['active_phase']}",
    ]
    for issue in payload["issues"]:
        suffix = f" ({issue['path']})" if issue.get("path") else ""
        lines.append(f"- {issue['code']}: {issue['message']}{suffix}")
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read-only validator for project-root serial-phase planning state."
    )
    parser.add_argument("--canonical-root", required=True, type=Path, help="Resolved project root.")
    parser.add_argument(
        "--operation",
        choices=OPERATIONS,
        default="inspect",
        help="Validate eligibility for inspect, init, resume, correct, archive, or successor.",
    )
    parser.add_argument("--record", type=Path, help="Optional root or listed phase directory.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    validator: Validator | None = None
    try:
        validator = Validator(args.canonical_root, args.operation, args.record)
        exit_code, payload = validator.result()
    except InvocationError as exc:
        exit_code = 2
        payload = invocation_payload(args.operation, args.canonical_root, str(exc))
    finally:
        if validator is not None:
            validator.close()
    output = json.dumps(payload, indent=2, sort_keys=True) if args.json else render_text(payload)
    print(output)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
