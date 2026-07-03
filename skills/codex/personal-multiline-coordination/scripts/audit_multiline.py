#!/usr/bin/env python3
"""Read-only audit for project-local multiline coordination state."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


LINE_CARD_REQUIRED = {
    "id",
    "objective",
    "cwd",
    "branch",
    "owner",
    "scope",
    "exclusive_files",
    "handoff_path",
    "stop_condition",
    "verification",
}

ACTIVE_STATUSES = {"active", "waiting_intake", "pass", "needs-more-evidence", "finish_candidate"}


def run_git(args: list[str], cwd: Path) -> tuple[int, str, str]:
    proc = subprocess.run(
        ["git", "-C", str(cwd), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def resolve_root(path: Path) -> tuple[Path, str | None]:
    code, out, err = run_git(["rev-parse", "--show-toplevel"], path)
    if code == 0 and out:
        return Path(out).resolve(), None
    return path.resolve(), err or "not a git repository"


def current_branch(path: Path) -> str | None:
    code, out, _ = run_git(["branch", "--show-current"], path)
    if code == 0 and out:
        return out
    code, out, _ = run_git(["rev-parse", "--short", "HEAD"], path)
    if code == 0 and out:
        return f"detached:{out}"
    return None


def dirty_count(path: Path) -> int | None:
    code, out, _ = run_git(["status", "--short"], path)
    if code != 0:
        return None
    return 0 if not out else len(out.splitlines())


def parse_worktree_porcelain(text: str) -> list[dict[str, Any]]:
    worktrees: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            if current:
                worktrees.append(current)
                current = None
            continue
        if line.startswith("worktree "):
            if current:
                worktrees.append(current)
            current = {"path": line[len("worktree ") :]}
        elif current is not None:
            if " " in line:
                key, value = line.split(" ", 1)
                current[key] = value
            else:
                current[line] = True
    if current:
        worktrees.append(current)
    return worktrees


def list_worktrees(root: Path) -> list[dict[str, Any]]:
    code, out, _ = run_git(["worktree", "list", "--porcelain"], root)
    if code != 0 or not out:
        return []
    result = []
    for wt in parse_worktree_porcelain(out):
        path = Path(str(wt.get("path", ""))).resolve()
        branch = str(wt.get("branch", "")).removeprefix("refs/heads/") or current_branch(path)
        result.append(
            {
                "path": str(path),
                "branch": branch,
                "head": wt.get("HEAD"),
                "detached": bool(wt.get("detached")),
                "bare": bool(wt.get("bare")),
                "exists": path.exists(),
                "dirty_count": dirty_count(path) if path.exists() else None,
            }
        )
    return result


def load_registry(root: Path) -> tuple[dict[str, Any] | None, str | None]:
    registry_path = root / ".codex" / "multiline" / "registry.json"
    if not registry_path.exists():
        return None, None
    try:
        data = json.loads(registry_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - report parse failures without mutating.
        return None, f"{type(exc).__name__}: {exc}"
    if not isinstance(data, dict):
        return None, "registry root is not a JSON object"
    return data, None


def normalize_lines(registry: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not registry:
        return []
    raw = registry.get("lines", [])
    if isinstance(raw, list):
        return [line for line in raw if isinstance(line, dict)]
    if isinstance(raw, dict):
        lines = []
        for key, value in raw.items():
            if isinstance(value, dict):
                line = dict(value)
                line.setdefault("id", key)
                lines.append(line)
        return lines
    return []


def path_matches(candidate: str | None, known_paths: set[str]) -> bool:
    if not candidate:
        return False
    try:
        return str(Path(candidate).resolve()) in known_paths
    except OSError:
        return False


def analyze(root: Path) -> dict[str, Any]:
    project_root, root_warning = resolve_root(root)
    registry, registry_error = load_registry(project_root)
    lines = normalize_lines(registry)
    worktrees = list_worktrees(project_root)
    worktree_paths = {wt["path"] for wt in worktrees}
    registry_dir = project_root / ".codex" / "multiline"
    findings: list[dict[str, str]] = []

    if root_warning:
        findings.append({"severity": "warning", "message": f"Project root is not a git root: {root_warning}"})
    if registry_error:
        findings.append({"severity": "error", "message": f"Cannot parse registry.json: {registry_error}"})
    if registry is None and registry_error is None:
        findings.append({"severity": "info", "message": "No .codex/multiline/registry.json found."})

    seen_ids: set[str] = set()
    for line in lines:
        line_id = str(line.get("id", "<missing-id>"))
        status = str(line.get("status", ""))
        if line_id in seen_ids:
            findings.append({"severity": "error", "message": f"Duplicate line id: {line_id}"})
        seen_ids.add(line_id)

        if status in {"proposed", "active"}:
            missing = sorted(k for k in LINE_CARD_REQUIRED if not line.get(k))
            if missing:
                findings.append(
                    {
                        "severity": "warning",
                        "message": f"Line {line_id} is {status} but missing Line Card fields: {', '.join(missing)}",
                    }
                )

        cwd = line.get("cwd")
        if status in ACTIVE_STATUSES and not path_matches(str(cwd) if cwd else None, worktree_paths):
            findings.append(
                {
                    "severity": "warning",
                    "message": f"Line {line_id} status {status} has cwd not found in git worktree list: {cwd}",
                }
            )

        branch = line.get("branch")
        if cwd and branch and path_matches(str(cwd), worktree_paths):
            resolved = str(Path(str(cwd)).resolve())
            actual = next((wt.get("branch") for wt in worktrees if wt["path"] == resolved), None)
            if actual and str(branch) != str(actual):
                findings.append(
                    {
                        "severity": "warning",
                        "message": f"Line {line_id} branch mismatch: registry={branch}, worktree={actual}",
                    }
                )

        handoff = line.get("handoff_path")
        if status in {"waiting_intake", "pass", "finish_candidate"} and handoff:
            if not Path(str(handoff)).exists():
                findings.append(
                    {
                        "severity": "warning",
                        "message": f"Line {line_id} expects handoff but path does not exist: {handoff}",
                    }
                )

    active_registry_cwds = {
        str(Path(str(line["cwd"])).resolve())
        for line in lines
        if line.get("cwd") and str(line.get("status", "")) in ACTIVE_STATUSES
    }
    for wt in worktrees:
        if wt["path"] not in active_registry_cwds and wt.get("dirty_count"):
            findings.append(
                {
                    "severity": "info",
                    "message": f"Dirty worktree is not attached to an active registry line: {wt['path']} ({wt['dirty_count']} changed entries)",
                }
            )

    return {
        "audit_version": 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "project_root": str(project_root),
        "registry": {
            "dir": str(registry_dir),
            "json_path": str(registry_dir / "registry.json"),
            "md_path": str(registry_dir / "registry.md"),
            "json_exists": (registry_dir / "registry.json").exists(),
            "md_exists": (registry_dir / "registry.md").exists(),
            "schema_version": registry.get("schema_version") if registry else None,
            "line_count": len(lines),
        },
        "worktrees": worktrees,
        "lines": [
            {
                "id": line.get("id"),
                "status": line.get("status"),
                "cwd": line.get("cwd"),
                "branch": line.get("branch"),
                "owner": line.get("owner"),
                "handoff_path": line.get("handoff_path"),
            }
            for line in lines
        ],
        "findings": findings,
    }


def print_text(report: dict[str, Any]) -> None:
    print(f"Multiline audit: {report['project_root']}")
    print(f"Registry: {report['registry']['json_path']} exists={report['registry']['json_exists']}")
    print(f"Registry summary: lines={report['registry']['line_count']} md_exists={report['registry']['md_exists']}")
    print("")
    print("Worktrees:")
    if not report["worktrees"]:
        print("- none detected")
    for wt in report["worktrees"]:
        dirty = wt["dirty_count"]
        dirty_text = "unknown" if dirty is None else str(dirty)
        print(f"- {wt['path']} branch={wt.get('branch')} dirty_count={dirty_text}")
    print("")
    print("Lines:")
    if not report["lines"]:
        print("- none registered")
    for line in report["lines"]:
        print(f"- {line.get('id')} status={line.get('status')} cwd={line.get('cwd')} branch={line.get('branch')}")
    print("")
    print("Findings:")
    if not report["findings"]:
        print("- no findings")
    for finding in report["findings"]:
        print(f"- [{finding['severity']}] {finding['message']}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Read-only audit for multiline coordination registry and worktrees.")
    parser.add_argument("project_root", nargs="?", default=os.getcwd(), help="Project root or any path inside the project.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    args = parser.parse_args(argv)

    report = analyze(Path(args.project_root))
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_text(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
