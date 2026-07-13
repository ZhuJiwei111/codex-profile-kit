#!/usr/bin/env python3
"""Audit, export, verify, push, and apply a portable Codex profile kit."""

from __future__ import annotations

import argparse
import filecmp
import hashlib
import json
import os
import queue
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_HOME = Path.home()

MANAGED_DIRS = ("rules", "templates", "skills", "hooks", "agents")
MANAGED_FILES = ("INSTALL.md", "MIGRATION_MANIFEST.md", "CONNECTORS.md")
FORBIDDEN_NAMES = {
    "auth.json",
    "history.jsonl",
    "session_index.jsonl",
    "__pycache__",
}
FORBIDDEN_SUFFIXES = (".sqlite", ".sqlite-shm", ".sqlite-wal", ".pyc", ".tar.gz")
FORBIDDEN_PARTS = {
    "attachments",
    "cache",
    "memories",
    "sessions",
    "archived_sessions",
    ".tmp",
}
ALLOWED_SKILL_KEYS = {
    "allowed-tools",
    "description",
    "license",
    "metadata",
    "name",
}
PERSONAL_SKILL_DESCRIPTION_BUDGET = 6000
MANAGED_SKILL_DESCRIPTION_BUDGET = 6500
THIRD_PARTY_SKILL_LOCK_FILENAME = "THIRD_PARTY_SKILLS.lock.json"
REQUIRED_OPENAI_INTERFACE_KEYS = {
    "display_name",
    "short_description",
    "default_prompt",
}
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
PORTABLE_CODEX_SKILL_NAMES = {
    "awesome-rebuttal",
}
PORTABLE_CODEX_AGENT_SETTINGS = {
    "monitor": {
        "model": "gpt-5.6-luna",
        "model_reasoning_effort": "high",
        "sandbox_mode": "read-only",
    },
    "reviewer": {
        "model": "gpt-5.6-sol",
        "model_reasoning_effort": "high",
        "sandbox_mode": "read-only",
    },
}
PORTABLE_CODEX_AGENT_NAMES = set(PORTABLE_CODEX_AGENT_SETTINGS)
REQUIRED_CUSTOM_AGENT_KEYS = {
    "name",
    "description",
    "developer_instructions",
    "model",
    "model_reasoning_effort",
    "sandbox_mode",
}
ALLOWED_CUSTOM_AGENT_KEYS = REQUIRED_CUSTOM_AGENT_KEYS | {"nickname_candidates"}
ALLOWED_REASONING_EFFORTS = {
    "none",
    "minimal",
    "low",
    "medium",
    "high",
    "xhigh",
    "max",
    "ultra",
}
ALLOWED_AGENT_SANDBOX_MODES = {
    "read-only",
    "workspace-write",
    "danger-full-access",
}
RENAMED_CODEX_SKILLS = {
    "hookify-writing-rules": "personal-codex-hook-rules",
    "context-save-restore": "personal-context-save-restore",
    "code-simplifier": "personal-code-simplifier",
    "code-documentation": "personal-code-documentation",
}
HOST_LOCAL_AGENT_SECTIONS = {
    "Host Local Overlay",
    "Host Python And Conda",
    "Host Network, Storage, And Compute Resources",
    "Host Local Install Decisions",
}
HOST_LOCAL_AGENT_MARKERS = (
    "/root",
    "/opt/conda",
    "/usr/bin/zsh",
    "/usr/local/cuda",
    ".codex-shell-env",
    "proxy_off",
    "Ubuntu 22.04",
    "REMOTE_CONNECTION.md",
)
MANAGED_AGENTS_OVERLAY_START = "<!-- codex-remote-doc-pointer:start -->"
MANAGED_AGENTS_OVERLAY_END = "<!-- codex-remote-doc-pointer:end -->"
RETIRED_HOOK_TARGETS = (
    ".codex/hooks/.smart_commit_pending.json",
    ".codex/hooks/smart-commit.md",
    ".codex/hooks/smart_commit_stage.py",
    ".codex/hooks/test_smart_commit_stage.py",
    ".codex/hookify/warn-goal-long-job-monitoring.md",
    ".codex/hookify/warn-my-concern-discussion-mode.md",
    ".codex/hookify/warn-project-output-explainer-style-on-stop.md",
    ".codex/hookify/warn-useful-next-steps-on-stop.md",
)


HOST_LOCAL_TEMPLATE = """# Host Local Overlay Template

Copy this file to `~/.codex/HOST_LOCAL.md` on the target machine. Fill in only
facts that are true there, keep the file permission at `0600`, and never store
secrets in it.

## Read Policy

- Read this overlay only when host-dependent work requires it.
- Re-check dynamic facts such as tools, limits, storage, and devices when they
  affect the task.
- Record paths and commands, never credential values.

## Host

- Home directory:
- Primary work root:
- OS:
- Default shell:
- Non-interactive shell startup behavior:
- Timezone for user-facing timestamps:
- Useful tools confirmed with `command -v`:

## Python And Conda

- System Python path:
- System Python purpose:
- Conda root:
- Codex fallback environment name:
- Codex fallback environment prefix:
- Codex fallback Python version:
- Codex fallback invocation:
- Codex fallback package installer:
- Codex fallback role and write policy:
- Project environment root:
- Conda package cache:
- Preferred package manager:
- User-site Python visibility policy:

## Proxy And Network

- Are proxy variables set by default:
- Proxy enable command:
- Proxy disable command:
- Direct-network test command for large downloads:
- Notes for package indexes or GitHub access:

## Storage And GPU

- Storage paths to check before large artifacts:
- Storage check command:
- Current resource and cgroup check commands:
- GPU availability:
- CUDA home:
- CUDA version:
- Required GPU scoping convention:

## Local Install Decisions

- Which skills were installed:
- Were hooks enabled:
- Connectors re-authenticated:
- Date of last smoke test:

## Known Transient Tool And Source Limitations

- Tool, helper, or endpoint:
- Observed failure and date:
- Current bounded fallback:
- Conditions that justify retry:

## Remote Connection Contract

- Control-plane owner:
- Contract file to read before changing transport, proxy, launcher, or app-server startup:
"""


CONFIG_TEMPLATE = """sandbox_mode = "workspace-write"
personality = "friendly"
service_tier = "default"

[agents]
max_depth = 1

[plugins."github@openai-curated"]
enabled = true

# Intentional portable policy: explicitly enable this reviewed public,
# unauthenticated Docs MCP. This template is normative, not a field-for-field
# copy of a source host that may rely on the product default.
[mcp_servers.openaiDeveloperDocs]
url = "https://developers.openai.com/mcp"
enabled = true

[features]
hooks = true

[sandbox_workspace_write]
network_access = true
"""


CONNECTORS = """# Connector Reconnection Checklist

Do not copy connector auth state, OAuth tokens, cookies, app caches, or plugin
caches from the source machine.

## GitHub Plugin

- Install or enable the GitHub plugin on the target machine.
- Re-authenticate through the target Codex UI or CLI flow.
- Verify repository access with a low-risk metadata read before using PR or
  issue workflows.

## Other Connectors

- Reinstall connectors from trusted sources on the target machine.
- Re-authenticate interactively.
- Keep credentials out of `AGENTS.md`, skills, hooks, templates, and migration
  reports.

## Portable MCP Servers

- Review the public, secret-free MCP declarations in
  `templates/config.toml.template` and merge only the servers intended for the
  target host.
- The template is a normative portable policy rather than a field-for-field
  mirror of the source host. Its `enabled = true` explicitly enables the
  reviewed public Docs MCP even when the source host omitted that field and
  relied on the current product default.
- Recreate environment bindings or interactive authentication on the target
  machine; never copy credential values, authenticated headers, or runtime
  auth state.
- Verify each configured server with a low-risk capability or metadata read.

## Smoke Check

Ask Codex to summarize available connector capabilities without printing secret
values. If a connector fails, repair the target-machine installation rather than
copying old state.
"""


INSTALL = """# Install Guide

This flow is template-based. Inspect each step before enabling hooks on the
target machine.

## 1. Clone

```bash
git clone https://github.com/ZhuJiwei111/codex-profile-kit.git
cd codex-profile-kit
python3 scripts/sync.py verify
```

Verification rejects symbolic links inside managed profile assets so a copied
skill, hook, template, or custom agent cannot retain an out-of-profile target.
It also validates personal-skill UI metadata and source-note presence, in-skill
relative resource links, the aggregate 6,500-character managed-catalog
description budget, and the allowlist/content lock in
`THIRD_PARTY_SKILLS.lock.json` for portable third-party Codex skills.

## 2. Fill Host Facts

```bash
install -m 600 templates/HOST_LOCAL_TEMPLATE.md ~/.codex/HOST_LOCAL.md
```

Fill `~/.codex/HOST_LOCAL.md` with target-machine facts. Keep secrets out of it.

## 3. Install Portable Rules

Review `rules/AGENTS.portable.md`, then use it as the target machine's
`~/.codex/AGENTS.md`. On a machine with existing rules, merge only deliberate
machine-neutral instructions; keep all host facts in `~/.codex/HOST_LOCAL.md`.

`templates/config.toml.template` is a manual reference, not an apply target. It
deliberately leaves the parent model and reasoning effort session-dependent and
keeps `agents.max_depth = 1`; merge only settings you intend to own globally.

## 4. Dry-Run Apply

```bash
python3 scripts/sync.py apply
```

The default is dry-run. It reports changed portable assets and manual-review
areas without writing to active Codex configuration.

## 5. Apply After Review

```bash
python3 scripts/sync.py apply --confirm
```

The script backs up overwritten files under `~/codex-migration-archive/` before
copying portable skills, allowlisted custom agent profiles, hook scripts,
controlled global Markdown rules, and rendered `hooks.json`. Explicitly retired
hook files and renamed legacy skill directories are backed up before they are
removed. For containment safety, apply rejects symbolic-link path components
below the explicit target home instead of following them.

## 6. Verify Custom Agent Profiles

Review `agents/codex/*.toml` before applying them. On the target host, confirm
that each configured model exists and supports the selected reasoning effort.
Also verify the effective child sandbox when read-only enforcement matters:
live task overrides can supersede a custom file's `sandbox_mode`. Custom agents
may require a new Codex task before discovery changes are visible.

The profile was last fully verified against Codex CLI 0.144.1. For a patch
update, run the current focused loader and affected-surface smoke checks; do not
repeat the full audit solely because the patch number changed. Read
`skills/codex/personal-codex-audit/references/compatibility-policy.md` and
broaden verification when release notes or observed behavior change hooks,
custom agents, skill discovery, or another owned contract.

## 7. Review Hook Trust

Start Codex and run `/hooks`. Review the source, matcher, command, and current
hash for every changed definition, then trust only the definitions you accept.
Do not copy or edit `trusted_hash` entries manually; changed hooks remain
skipped until reviewed.

## 8. Reconnect Plugins And MCP Servers

Use `CONNECTORS.md` as the checklist. Re-authenticate connectors on the target
machine instead of copying connector state. Review the public MCP declarations
in `templates/config.toml.template`, merge only intended servers, and recreate
any target-host authentication through its normal mechanism.
"""


def run(cmd: list[str], cwd: Path = REPO_ROOT, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def rel(path: Path, root: Path = REPO_ROOT) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def copytree(src: Path, dst: Path) -> None:
    if src.is_symlink() or not src.is_dir():
        raise RuntimeError(f"copytree source must be a regular directory: {src}")
    if dst.is_symlink():
        raise RuntimeError(f"copytree destination must not be a symbolic link: {dst}")
    if dst.exists():
        if not dst.is_dir():
            raise RuntimeError(f"copytree destination must be a directory: {dst}")
        shutil.rmtree(dst)
    shutil.copytree(
        src,
        dst,
        symlinks=True,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def frontmatter_bounds(text: str) -> tuple[int, int] | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    return 4, end


def parse_frontmatter(text: str) -> dict[str, str]:
    bounds = frontmatter_bounds(text)
    if bounds is None:
        return {}
    start, end = bounds
    data: dict[str, str] = {}
    for line in text[start:end].splitlines():
        if line.startswith((" ", "\t")):
            continue
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("-") or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def sanitize_skill(skill_file: Path) -> None:
    text = skill_file.read_text(encoding="utf-8")
    bounds = frontmatter_bounds(text)
    if bounds is None:
        return
    start, end = bounds
    raw = text[start:end]
    kept = []
    for line in raw.splitlines():
        key = line.split(":", 1)[0].strip() if ":" in line else ""
        if key == "version":
            continue
        kept.append(line)
    sanitized = "---\n" + "\n".join(kept).rstrip() + "\n---" + text[end + 4 :]
    skill_file.write_text(sanitized, encoding="utf-8")


def is_portable_codex_skill(name: str) -> bool:
    return name.startswith("personal-") or name in PORTABLE_CODEX_SKILL_NAMES


_TOML_BASIC_ESCAPES = {
    '"': '"',
    "\\": "\\",
    "b": "\b",
    "t": "\t",
    "n": "\n",
    "f": "\f",
    "r": "\r",
}


def _decode_toml_escape(text: str, index: int) -> tuple[str, int]:
    """Decode one TOML 1.0 basic-string escape at ``index``."""
    if index + 1 >= len(text):
        raise ValueError("unterminated escape")
    marker = text[index + 1]
    if marker in _TOML_BASIC_ESCAPES:
        return _TOML_BASIC_ESCAPES[marker], index + 2
    if marker not in {"u", "U"}:
        raise ValueError(f"unsupported TOML escape \\{marker}")
    width = 4 if marker == "u" else 8
    start = index + 2
    end = start + width
    digits = text[start:end]
    if len(digits) != width or re.fullmatch(rf"[0-9A-Fa-f]{{{width}}}", digits) is None:
        raise ValueError(f"invalid TOML unicode escape \\{marker}{digits}")
    codepoint = int(digits, 16)
    if codepoint > 0x10FFFF or 0xD800 <= codepoint <= 0xDFFF:
        raise ValueError(f"invalid TOML unicode scalar U+{codepoint:04X}")
    return chr(codepoint), end


def _validate_toml_basic_character(character: str, *, multiline: bool) -> None:
    codepoint = ord(character)
    if character == "\n" and multiline:
        return
    if codepoint < 0x20 and character != "\t":
        raise ValueError(f"unescaped control character U+{codepoint:04X}")
    if codepoint == 0x7F:
        raise ValueError("unescaped control character U+007F")


def _parse_toml_basic_string_at(text: str, index: int = 0) -> tuple[str, int]:
    if index >= len(text) or text[index] != '"':
        raise ValueError("portable TOML strings must use basic-string quotes")
    decoded: list[str] = []
    index += 1
    while index < len(text):
        character = text[index]
        if character == '"':
            return "".join(decoded), index + 1
        if character == "\\":
            value, index = _decode_toml_escape(text, index)
            decoded.append(value)
            continue
        _validate_toml_basic_character(character, multiline=False)
        decoded.append(character)
        index += 1
    raise ValueError("unterminated TOML basic string")


def _parse_toml_basic_string(text: str) -> str:
    value, index = _parse_toml_basic_string_at(text)
    if text[index:].strip():
        raise ValueError("unexpected text after TOML basic string")
    return value


def _parse_toml_string_array(text: str) -> list[str]:
    if not text.startswith("["):
        raise ValueError("portable TOML arrays must start with '['")
    values: list[str] = []
    index = 1
    while True:
        while index < len(text) and text[index] in " \t":
            index += 1
        if index >= len(text):
            raise ValueError("unterminated portable TOML array")
        if text[index] == "]":
            index += 1
            if text[index:].strip():
                raise ValueError("unexpected text after portable TOML array")
            return values
        value, index = _parse_toml_basic_string_at(text, index)
        values.append(value)
        while index < len(text) and text[index] in " \t":
            index += 1
        if index >= len(text):
            raise ValueError("unterminated portable TOML array")
        if text[index] == "]":
            continue
        if text[index] != ",":
            raise ValueError("portable TOML array values must be comma-separated")
        index += 1
        while index < len(text) and text[index] in " \t":
            index += 1
        if index < len(text) and text[index] == "]":
            continue


def _parse_toml_multiline_basic_string(lines: list[str], index: int) -> tuple[str, int]:
    chunks: list[str] = []
    while index < len(lines):
        current = lines[index]
        index += 1
        if current == '"""':
            raw = "\n".join(chunks)
            decoded: list[str] = []
            cursor = 0
            while cursor < len(raw):
                character = raw[cursor]
                if character == "\\":
                    value, cursor = _decode_toml_escape(raw, cursor)
                    decoded.append(value)
                    continue
                _validate_toml_basic_character(character, multiline=True)
                decoded.append(character)
                cursor += 1
            return "".join(decoded), index
        if '"""' in current:
            raise ValueError("portable multiline strings require a standalone terminator")
        chunks.append(current)
    raise ValueError("unterminated multiline string")


def parse_custom_agent_toml(text: str, path: Path) -> dict[str, object]:
    """Parse a strict dependency-free subset that is always valid TOML 1.0."""
    data: dict[str, object] = {}
    text = text.replace("\r\n", "\n")
    if "\r" in text:
        raise ValueError("bare carriage return is not allowed in portable TOML")
    for character in text:
        codepoint = ord(character)
        if codepoint < 0x20 and character not in {"\n", "\t"}:
            raise ValueError(f"unescaped control character U+{codepoint:04X}")
        if codepoint == 0x7F:
            raise ValueError("unescaped control character U+007F")
    lines = text.split("\n")
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        index += 1
        if not line or line.startswith("#"):
            continue
        if line.startswith("["):
            raise ValueError("tables are not allowed in portable custom agents")
        match = re.fullmatch(r"([A-Za-z0-9_-]+)\s*=\s*(.*)", line)
        if match is None:
            raise ValueError(f"invalid assignment on line {index}")
        key, raw = match.groups()
        if key in data:
            raise ValueError(f"duplicate key {key}")

        if raw == '"""':
            value, index = _parse_toml_multiline_basic_string(lines, index)
            data[key] = value
            continue
        if raw.startswith('"""'):
            raise ValueError(
                f"portable multiline string for {key} must open on its own line"
            )
        if raw.startswith('"'):
            data[key] = _parse_toml_basic_string(raw)
            continue
        if raw.startswith("["):
            data[key] = _parse_toml_string_array(raw)
            continue
        raise ValueError(f"unsupported portable TOML value for {key}")
    return data


def load_custom_agent(path: Path) -> dict[str, object]:
    if path.is_symlink() or not path.is_file():
        raise SystemExit(f"custom agent must be a regular file: {path}")
    try:
        data = parse_custom_agent_toml(path.read_bytes().decode("utf-8"), path)
    except (OSError, UnicodeError, ValueError) as exc:
        raise SystemExit(f"invalid custom agent TOML: {path}: {exc}") from exc

    missing = REQUIRED_CUSTOM_AGENT_KEYS - set(data)
    if missing:
        raise SystemExit(f"missing custom agent keys in {path}: {sorted(missing)}")
    unexpected = set(data) - ALLOWED_CUSTOM_AGENT_KEYS
    if unexpected:
        raise SystemExit(f"unexpected keys in portable custom agent {path}: {sorted(unexpected)}")

    for key in REQUIRED_CUSTOM_AGENT_KEYS:
        value = data.get(key)
        if not isinstance(value, str) or not value.strip():
            raise SystemExit(f"custom agent key {key} must be a non-empty string: {path}")
    if data["name"] != path.stem:
        raise SystemExit(
            f"custom agent name/file mismatch: {data['name']} != {path.stem}: {path}"
        )
    expected_settings = PORTABLE_CODEX_AGENT_SETTINGS.get(path.stem)
    if expected_settings is not None:
        mismatches = {
            key: {"expected": expected, "observed": data.get(key)}
            for key, expected in expected_settings.items()
            if data.get(key) != expected
        }
        if mismatches:
            raise SystemExit(
                f"custom agent settings violate portable policy in {path}: {mismatches}"
            )
    effort = data["model_reasoning_effort"]
    if effort not in ALLOWED_REASONING_EFFORTS:
        raise SystemExit(f"unsupported model_reasoning_effort in {path}: {effort}")
    sandbox = data["sandbox_mode"]
    if sandbox not in ALLOWED_AGENT_SANDBOX_MODES:
        raise SystemExit(f"unsupported sandbox_mode in {path}: {sandbox}")
    nicknames = data.get("nickname_candidates")
    if nicknames is not None:
        if (
            not isinstance(nicknames, list)
            or not nicknames
            or any(not isinstance(item, str) or not item.strip() for item in nicknames)
        ):
            raise SystemExit(f"invalid nickname_candidates in {path}")
        normalized_nicknames = [item.strip() for item in nicknames]
        if len(set(normalized_nicknames)) != len(normalized_nicknames):
            raise SystemExit(f"duplicate nickname_candidates after trimming in {path}")
        if any(
            re.fullmatch(r"[A-Za-z0-9 _-]+", item) is None
            for item in normalized_nicknames
        ):
            raise SystemExit(f"invalid nickname_candidates characters in {path}")
        data["nickname_candidates"] = normalized_nicknames
    return data


def validate_custom_agents(root: Path) -> None:
    agent_root = root / "agents" / "codex"
    if not agent_root.is_dir() or agent_root.is_symlink():
        raise SystemExit(f"missing portable custom agent directory: {agent_root}")
    expected = {f"{name}.toml" for name in PORTABLE_CODEX_AGENT_NAMES}
    found = {path.name for path in agent_root.iterdir()}
    missing = expected - found
    if missing:
        raise SystemExit(f"missing portable custom agents: {sorted(missing)}")
    unexpected = found - expected
    if unexpected:
        raise SystemExit(
            f"unallowlisted portable custom agent entries: {sorted(unexpected)}"
        )
    for name in sorted(PORTABLE_CODEX_AGENT_NAMES):
        load_custom_agent(agent_root / f"{name}.toml")


def decode_codex_loader_message(line: str) -> dict[str, object]:
    try:
        message = json.loads(line)
    except json.JSONDecodeError as exc:
        raise SystemExit(
            f"Codex custom-agent loader returned non-JSON output: {line[:160]}"
        ) from exc
    if not isinstance(message, dict):
        raise SystemExit("Codex custom-agent loader returned a non-object message")
    return message


def run_codex_loader_protocol(
    codex: str, root: Path, environment: dict[str, str], timeout: float = 10.0
) -> tuple[int, list[dict[str, object]], str]:
    """Perform an interactive app-server handshake without starting a thread or turn."""
    process = subprocess.Popen(
        [codex, "app-server", "--stdio"],
        cwd=str(root),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        env=environment,
    )
    assert process.stdin is not None
    assert process.stdout is not None
    assert process.stderr is not None

    output: queue.Queue[object] = queue.Queue()
    output_done = object()
    stderr_chunks: list[str] = []

    def read_stdout() -> None:
        try:
            for line in process.stdout:
                output.put(line)
        finally:
            output.put(output_done)

    def read_stderr() -> None:
        stderr_chunks.append(process.stderr.read())

    stdout_thread = threading.Thread(target=read_stdout, daemon=True)
    stderr_thread = threading.Thread(target=read_stderr, daemon=True)
    stdout_thread.start()
    stderr_thread.start()

    messages: list[dict[str, object]] = []
    deadline = time.monotonic() + timeout

    def send(message: str) -> None:
        process.stdin.write(message + "\n")
        process.stdin.flush()

    def collect_until(request_id: int) -> dict[str, object] | None:
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return None
            try:
                item = output.get(timeout=remaining)
            except queue.Empty:
                return None
            if item is output_done:
                return None
            assert isinstance(item, str)
            if not item.strip():
                continue
            message = decode_codex_loader_message(item)
            messages.append(message)
            if message.get("id") == request_id:
                return message

    try:
        send(
            '{"id":1,"method":"initialize","params":{"clientInfo":'
            '{"name":"profile-sync","version":"1"},'
            '"capabilities":{"experimentalApi":true}}}'
        )
        initialize_response = collect_until(1)
        if initialize_response is not None and "result" in initialize_response:
            send('{"method":"initialized"}')
            send(
                '{"id":2,"method":"config/read","params":'
                '{"cwd":null,"includeLayers":true}}'
            )
            collect_until(2)
    finally:
        try:
            if not process.stdin.closed:
                process.stdin.close()
        except BrokenPipeError:
            pass
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=2)
        stdout_thread.join(timeout=2)
        stderr_thread.join(timeout=2)
        process.stdout.close()
        process.stderr.close()

    while True:
        try:
            item = output.get_nowait()
        except queue.Empty:
            break
        if item is output_done:
            continue
        assert isinstance(item, str)
        if item.strip():
            messages.append(decode_codex_loader_message(item))
    return process.returncode, messages, "".join(stderr_chunks)


def validate_codex_loader_messages(
    messages: list[dict[str, object]],
    stderr: str,
    expected_agent_paths: set[str],
    returncode: int,
) -> None:
    relevant_warnings: list[object] = []
    for message in messages:
        if message.get("method") != "configWarning":
            continue
        params = message.get("params")
        if not isinstance(params, dict):
            continue
        warning_path = params.get("path")
        combined = " ".join(
            str(params.get(key) or "") for key in ("summary", "details")
        )
        path_matches = False
        if isinstance(warning_path, str) and warning_path:
            path_matches = (
                str(Path(warning_path).resolve(strict=False)) in expected_agent_paths
            )
        text_matches = any(path in combined for path in expected_agent_paths)
        if path_matches or text_matches:
            relevant_warnings.append(params)
    malformed_stderr = any(
        marker in stderr.lower()
        for marker in (
            "malformed agent role",
            "failed to parse agent role",
            "toml parse error",
        )
    ) and any(path in stderr for path in expected_agent_paths)
    if relevant_warnings or malformed_stderr:
        details = (
            json.dumps(relevant_warnings, ensure_ascii=False)
            if relevant_warnings
            else stderr
        )
        raise SystemExit(f"Codex rejected a portable custom agent: {details}")
    if returncode:
        raise SystemExit(f"Codex custom-agent loader failed with exit {returncode}: {stderr}")

    rpc_errors = [message for message in messages if "error" in message]
    if rpc_errors:
        raise SystemExit(
            "Codex custom-agent loader JSON-RPC error: "
            + json.dumps(rpc_errors, ensure_ascii=False)
        )
    responses = {
        message.get("id"): message
        for message in messages
        if message.get("id") in {1, 2}
    }
    missing_success = [
        request_id
        for request_id in (1, 2)
        if request_id not in responses or "result" not in responses[request_id]
    ]
    if missing_success:
        raise SystemExit(
            "Codex custom-agent loader JSON-RPC responses are incomplete: "
            f"{missing_success}"
        )
    unexpected_execution = sorted(
        {
            str(message.get("method"))
            for message in messages
            if message.get("method") in {"thread/started", "turn/started"}
        }
    )
    if unexpected_execution:
        raise SystemExit(
            "Codex custom-agent loader unexpectedly started execution: "
            f"{unexpected_execution}"
        )


def validate_custom_agents_with_codex(root: Path) -> None:
    """Smoke-load portable roles through the installed Codex parser without a turn."""
    codex = shutil.which("codex")
    if codex is None:
        print("codex custom-agent loader check skipped: Codex CLI unavailable")
        return
    version = subprocess.run(
        [codex, "--version"],
        cwd=str(root),
        check=False,
        capture_output=True,
        text=True,
    )
    if version.returncode:
        raise SystemExit(version.stderr or version.stdout)

    with tempfile.TemporaryDirectory(
        prefix=f".{root.name}-agent-loader-", dir=root.parent
    ) as tmp:
        codex_home = Path(tmp) / "codex-home"
        shutil.copytree(root / "agents" / "codex", codex_home / "agents")
        expected_agent_paths = {
            str((codex_home / "agents" / f"{name}.toml").resolve())
            for name in PORTABLE_CODEX_AGENT_NAMES
        }
        environment = os.environ.copy()
        environment["CODEX_HOME"] = str(codex_home)
        returncode, messages, stderr = run_codex_loader_protocol(
            codex, root, environment
        )
        validate_codex_loader_messages(
            messages, stderr, expected_agent_paths, returncode
        )
    print(f"codex custom-agent loader ok: {version.stdout.strip()}")


def validate_export_custom_agent_sources(home: Path) -> None:
    agent_root = home / ".codex" / "agents"
    for name in sorted(PORTABLE_CODEX_AGENT_NAMES):
        path = agent_root / f"{name}.toml"
        if not path.exists() and not path.is_symlink():
            raise SystemExit(f"portable custom agent is unavailable in export source: {path}")
        load_custom_agent(path)


def export_custom_agents(codex: Path, root: Path) -> None:
    destination = root / "agents" / "codex"
    destination.mkdir(parents=True, exist_ok=True)
    for name in sorted(PORTABLE_CODEX_AGENT_NAMES):
        source = codex / "agents" / f"{name}.toml"
        load_custom_agent(source)
        shutil.copy2(source, destination / source.name)


def custom_agent_apply_pairs(root: Path, home: Path) -> list[tuple[Path, Path]]:
    source_root = root / "agents" / "codex"
    return [
        (source_root / f"{name}.toml", home / ".codex" / "agents" / f"{name}.toml")
        for name in sorted(PORTABLE_CODEX_AGENT_NAMES)
    ]


def validate_export_renamed_skill_sources(home: Path) -> None:
    skill_root = home / ".codex" / "skills"
    for successor_name in RENAMED_CODEX_SKILLS.values():
        successor = skill_root / successor_name
        if successor.is_symlink() or not successor.is_dir():
            raise SystemExit(
                f"renamed skill successor is unavailable in export source: {successor}"
            )
        skill_file = successor / "SKILL.md"
        if not skill_file.is_file():
            raise SystemExit(
                f"renamed skill successor is missing SKILL.md in export source: {successor}"
            )
        frontmatter = parse_frontmatter(skill_file.read_text(encoding="utf-8"))
        if frontmatter.get("name") != successor_name or not frontmatter.get("description"):
            raise SystemExit(
                f"renamed skill successor has invalid metadata in export source: {successor}"
            )


def strip_managed_agents_overlay(text: str) -> str:
    start_count = text.count(MANAGED_AGENTS_OVERLAY_START)
    end_count = text.count(MANAGED_AGENTS_OVERLAY_END)
    if start_count == 0 and end_count == 0:
        return text
    if start_count != 1 or end_count != 1:
        raise ValueError(
            "AGENTS.md contains a malformed managed AGENTS overlay: expected "
            "exactly one start marker and one end marker."
        )

    pattern = re.compile(
        rf"(?P<separator>\r?\n){re.escape(MANAGED_AGENTS_OVERLAY_START)}\r?\n"
        rf".*?\r?\n{re.escape(MANAGED_AGENTS_OVERLAY_END)}(?:\r?\n)?\Z",
        flags=re.DOTALL,
    )
    match = pattern.search(text)
    if match is None:
        raise ValueError(
            "AGENTS.md contains a malformed managed AGENTS overlay: the block "
            "must be line-delimited and form the final file suffix."
        )

    portable = text[: match.start()]
    if not portable.endswith(("\n", "\r")):
        portable += match.group("separator")
    return portable


def portable_agents(active_agents: Path) -> str:
    text = strip_managed_agents_overlay(active_agents.read_text(encoding="utf-8"))
    headings = {
        match.group(1).strip()
        for match in re.finditer(r"^## ([^#\n].*)$", text, flags=re.MULTILINE)
    }
    forbidden = sorted(headings & HOST_LOCAL_AGENT_SECTIONS)
    if forbidden:
        joined = ", ".join(forbidden)
        raise ValueError(
            f"AGENTS.md contains host-local sections: {joined}. "
            "Move those facts to ~/.codex/HOST_LOCAL.md before export."
        )
    leaked_markers = [marker for marker in HOST_LOCAL_AGENT_MARKERS if marker in text]
    if leaked_markers:
        joined = ", ".join(leaked_markers)
        raise ValueError(
            f"AGENTS.md contains host-local markers: {joined}. "
            "Move those facts to ~/.codex/HOST_LOCAL.md before export."
        )
    return text


def render_hooks_template(active_hooks_json: Path, home: Path) -> str:
    data = json.loads(active_hooks_json.read_text(encoding="utf-8"))
    home_text = str(home)

    def convert(value: object) -> object:
        if isinstance(value, dict):
            return {k: convert(v) for k, v in value.items()}
        if isinstance(value, list):
            return [convert(v) for v in value]
        if isinstance(value, str):
            value = value.replace(home_text, "{{HOME}}")
            value = re.sub(r"(^|\s)/usr/bin/python3(?=\s)", r"\1{{PYTHON3}}", value)
            value = re.sub(r"(^|\s)python3(?=\s)", r"\1{{PYTHON3}}", value)
            return value
        return value

    return json.dumps(convert(data), ensure_ascii=False, indent=2) + "\n"


def path_lexists(path: Path) -> bool:
    return os.path.lexists(os.fspath(path))


def remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def clear_managed_snapshot(root: Path) -> None:
    for relative in (*MANAGED_DIRS, *MANAGED_FILES):
        target = root / relative
        if path_lexists(target):
            remove_path(target)


def render_export_snapshot(root: Path, home: Path) -> None:
    """Render a complete managed snapshot into a disposable candidate root."""
    validate_export_renamed_skill_sources(home)
    validate_export_custom_agent_sources(home)
    codex = home / ".codex"
    agents = home / ".agents"
    clear_managed_snapshot(root)

    (root / "rules").mkdir(parents=True, exist_ok=True)
    write_text(root / "rules" / "AGENTS.portable.md", portable_agents(codex / "AGENTS.md"))

    (root / "templates").mkdir(parents=True, exist_ok=True)
    write_text(root / "templates" / "HOST_LOCAL_TEMPLATE.md", HOST_LOCAL_TEMPLATE)
    write_text(root / "templates" / "config.toml.template", CONFIG_TEMPLATE)
    write_text(root / "templates" / "hooks.json.template", render_hooks_template(codex / "hooks.json", home))

    skills_root = root / "skills"
    (skills_root / "codex").mkdir(parents=True, exist_ok=True)
    for skill_dir in sorted((codex / "skills").iterdir()):
        if not skill_dir.is_dir() or skill_dir.name.startswith("."):
            continue
        if not is_portable_codex_skill(skill_dir.name):
            continue
        dst = skills_root / "codex" / skill_dir.name
        copytree(skill_dir, dst)
        skill_file = dst / "SKILL.md"
        if skill_file.exists():
            sanitize_skill(skill_file)
    if (agents / "skills" / "find-skills").is_dir():
        copytree(agents / "skills" / "find-skills", skills_root / "agents" / "find-skills")

    export_custom_agents(codex, root)

    hooks_root = root / "hooks"
    (hooks_root / "scripts").mkdir(parents=True, exist_ok=True)
    (hooks_root / "rules").mkdir(parents=True, exist_ok=True)
    for path in sorted((codex / "hooks").glob("*.py")):
        shutil.copy2(path, hooks_root / "scripts" / path.name)
    for path in sorted((codex / "hookify").glob("*.md")):
        shutil.copy2(path, hooks_root / "rules" / path.name)

    write_text(root / "CONNECTORS.md", CONNECTORS)
    write_text(root / "INSTALL.md", INSTALL)
    write_text(root / "MIGRATION_MANIFEST.md", migration_manifest())


class ExportRollbackError(RuntimeError):
    """Raised when an export commit fails and automatic rollback is incomplete."""


def transactional_replace_managed_entries(
    replacements: list[tuple[Path, Path]], transaction_root: Path
) -> None:
    targets = [target.absolute() for _, target in replacements]
    if len(set(targets)) != len(targets):
        raise RuntimeError("export replacement plan contains duplicate targets")
    for index, target in enumerate(targets):
        for other in targets[index + 1 :]:
            if target in other.parents or other in target.parents:
                raise RuntimeError(
                    f"export replacement targets overlap: {target} and {other}"
                )
    for source, _ in replacements:
        if not path_lexists(source):
            raise RuntimeError(f"export replacement source is missing: {source}")

    rollback_root = transaction_root / "rollback"
    failed_new_root = transaction_root / "failed-new"
    journal: list[dict[str, object]] = []
    try:
        for index, (source, target) in enumerate(replacements):
            backup = rollback_root / f"{index:03d}-{target.name}"
            had_old = path_lexists(target)
            state: dict[str, object] = {
                "source": source,
                "target": target,
                "backup": backup,
                "had_old": had_old,
            }
            journal.append(state)
            target.parent.mkdir(parents=True, exist_ok=True)
            if had_old:
                backup.parent.mkdir(parents=True, exist_ok=True)
                os.replace(target, backup)
            os.replace(source, target)
    except BaseException as exc:
        rollback_errors: list[str] = []
        for index, state in reversed(list(enumerate(journal))):
            source = state["source"]
            target = state["target"]
            backup = state["backup"]
            assert isinstance(source, Path)
            assert isinstance(target, Path)
            assert isinstance(backup, Path)
            try:
                source_exists = path_lexists(source)
                target_exists = path_lexists(target)
                backup_exists = path_lexists(backup)
                if not source_exists:
                    if not target_exists:
                        raise RuntimeError(
                            "staged source and live target are both missing"
                        )
                    failed_new = failed_new_root / f"{index:03d}-{target.name}"
                    failed_new.parent.mkdir(parents=True, exist_ok=True)
                    os.replace(target, failed_new)
                    target_exists = False
                if state["had_old"]:
                    if backup_exists:
                        if target_exists:
                            raise RuntimeError(
                                "both original backup and live target exist during rollback"
                            )
                        target.parent.mkdir(parents=True, exist_ok=True)
                        os.replace(backup, target)
                    elif not target_exists:
                        raise RuntimeError(
                            "original target is missing without a rollback backup"
                        )
                else:
                    if backup_exists:
                        raise RuntimeError(
                            "unexpected rollback backup for originally absent target"
                        )
                    if target_exists:
                        raise RuntimeError(
                            "unexpected live target remains for originally absent target"
                        )
            except BaseException as rollback_exc:
                rollback_errors.append(f"{target}: {rollback_exc}")
        if rollback_errors:
            details = "; ".join(rollback_errors)
            raise ExportRollbackError(
                "export replacement failed and rollback is incomplete; "
                f"preserved transaction at {transaction_root}: {details}"
            ) from exc
        raise


def validate_archive_target(path: Path) -> None:
    if not path_lexists(path):
        return
    metadata = os.lstat(path)
    if not stat.S_ISREG(metadata.st_mode):
        raise RuntimeError(
            f"tarball target must be absent or a regular file: {path}"
        )


@contextmanager
def exclusive_export_lock(root: Path) -> Iterable[None]:
    try:
        import fcntl
    except ImportError as exc:
        raise RuntimeError(
            "safe concurrent export locking is unavailable on this platform"
        ) from exc
    canonical_root = root.resolve(strict=True)
    lock_parent = canonical_root.parent
    parent_metadata = os.lstat(lock_parent)
    if (
        not stat.S_ISDIR(parent_metadata.st_mode)
        or parent_metadata.st_uid != os.geteuid()
        or stat.S_IMODE(parent_metadata.st_mode) & 0o022
    ):
        raise RuntimeError(
            f"export lock parent must be a private owned directory: {lock_parent}"
        )
    lock_path = lock_parent / f".{canonical_root.name}.export.lock"
    no_follow = getattr(os, "O_NOFOLLOW", 0)
    if not no_follow:
        raise RuntimeError("safe no-follow export lock opening is unavailable")
    flags = os.O_RDWR | os.O_CREAT | no_follow | getattr(os, "O_CLOEXEC", 0)
    try:
        descriptor = os.open(lock_path, flags, 0o600)
    except OSError as exc:
        raise RuntimeError(f"could not open safe export lock: {lock_path}") from exc
    metadata = os.fstat(descriptor)
    if not stat.S_ISREG(metadata.st_mode) or metadata.st_uid != os.geteuid():
        os.close(descriptor)
        raise RuntimeError(f"export lock is not a regular owned file: {lock_path}")
    handle = os.fdopen(descriptor, "a+b")
    try:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError(
                f"another export is already active for profile root: {root}"
            ) from exc
        yield
    finally:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        finally:
            handle.close()


def export_to_locked(root: Path, home: Path, tarball: bool = False) -> None:
    transaction_root = Path(
        tempfile.mkdtemp(prefix=f".{root.name}-export-", dir=root.parent)
    )
    preserve_transaction = False
    archive: Path | None = None
    try:
        candidate = transaction_root / "candidate"
        shutil.copytree(
            root,
            candidate,
            symlinks=True,
            ignore=shutil.ignore_patterns(".git"),
        )
        render_export_snapshot(candidate, home)
        verify_repo(candidate)

        replacements = [
            (candidate / relative, root / relative)
            for relative in (*MANAGED_DIRS, *MANAGED_FILES)
        ]
        if tarball:
            archive = root.parent / (
                f"{root.name}-{datetime.now().strftime('%Y%m%d')}.tar.gz"
            )
            validate_archive_target(archive)
            staged_archive = transaction_root / archive.name
            with tarfile.open(staged_archive, "w:gz") as handle:
                handle.add(candidate, arcname=root.name, filter=tar_filter)
            replacements.append((staged_archive, archive))

        transactional_replace_managed_entries(replacements, transaction_root)
    except ExportRollbackError:
        preserve_transaction = True
        raise
    finally:
        if not preserve_transaction:
            shutil.rmtree(transaction_root, ignore_errors=True)
    if archive is not None:
        print(f"wrote {archive}")


def export_to(root: Path, home: Path, tarball: bool = False) -> None:
    root = root.absolute()
    home = home.expanduser().absolute()
    if root.is_symlink() or not root.is_dir():
        raise RuntimeError(f"profile root must be a regular directory: {root}")
    with exclusive_export_lock(root):
        export_to_locked(root, home, tarball=tarball)


def tar_filter(info: tarfile.TarInfo) -> tarfile.TarInfo | None:
    parts = Path(info.name).parts
    if any(part in FORBIDDEN_PARTS or part in FORBIDDEN_NAMES for part in parts):
        return None
    if info.name.endswith(FORBIDDEN_SUFFIXES):
        return None
    if ".git" in parts:
        return None
    return info


def migration_manifest() -> str:
    return """# Migration Manifest

Generated for a clean Codex profile kit.

## Included

- `rules/AGENTS.portable.md`: machine-neutral durable Codex behavior rules.
- `templates/HOST_LOCAL_TEMPLATE.md`: target-machine overlay template.
- `templates/hooks.json.template`: Codex hook wiring template with placeholders.
- `templates/config.toml.template`: minimal portable Codex config reference
  without a fixed parent model or reasoning effort, including reviewed public
  MCP endpoint declarations with no authentication state.
- `skills/codex/`: personal workflow skills plus explicitly allowlisted
  portable Codex skills from `~/.codex/skills`.
  Verification checks personal-skill UI metadata and source-note presence,
  relative resource links, and the aggregate 6,500-character managed-catalog
  description budget.
- `THIRD_PARTY_SKILLS.lock.json`: reviewed source/license state and exact
  content digests for allowlisted portable third-party Codex skills.
- `skills/agents/find-skills/`: portable agent skill discovery helper.
- `agents/codex/`: allowlisted custom Codex agent profiles from
  `~/.codex/agents`.
- `hooks/scripts/`: hook scripts and tests from `~/.codex/hooks`.
- `hooks/rules/`: controlled global Markdown rules from `~/.codex/hookify`.
- `CONNECTORS.md`: re-authentication and public MCP review checklist.
- `INSTALL.md`: target-machine install and smoke-test guide.

## Excluded

- Codex auth files, tokens, connector or MCP OAuth state, authenticated header
  values, cookies, passwords, and secrets.
- Session history, archived sessions, logs, attachments, and pasted files.
- SQLite databases, WAL/SHM files, state databases, and goal/history stores.
- Codex memories and rollout summaries.
- Plugin caches, app caches, marketplace temporary clones, and model caches.
- Project trust lists, hook trusted hashes, approval history, and local runtime
  state.
- Conda environments, package caches, datasets, model weights, project outputs,
  and machine-specific tool installations.
"""


@dataclass
class DiffSummary:
    only_left: list[str]
    only_right: list[str]
    different: list[str]


def file_map(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel_path = path.relative_to(root).as_posix()
        if rel_path.startswith(".git/"):
            continue
        result[rel_path] = sha256(path)
    return result


def diff_dirs(left: Path, right: Path) -> DiffSummary:
    left_map = file_map(left)
    right_map = file_map(right)
    return DiffSummary(
        only_left=sorted(set(left_map) - set(right_map)),
        only_right=sorted(set(right_map) - set(left_map)),
        different=sorted(k for k in set(left_map) & set(right_map) if left_map[k] != right_map[k]),
    )


def print_diff(summary: DiffSummary) -> None:
    for label, values in (
        ("only_export", summary.only_left),
        ("only_repo", summary.only_right),
        ("different", summary.different),
    ):
        print(f"{label}: {len(values)}")
        for value in values[:80]:
            print(f"  {value}")
        if len(values) > 80:
            print(f"  ... +{len(values) - 80} more")


def forbidden_path(path: Path) -> bool:
    parts = set(path.parts)
    if path.name in FORBIDDEN_NAMES:
        return True
    if any(part in FORBIDDEN_PARTS for part in parts):
        return True
    return path.name.endswith(FORBIDDEN_SUFFIXES)


def scan_forbidden(root: Path) -> list[str]:
    bad: list[str] = []
    for path in root.rglob("*"):
        if ".git" in path.parts:
            continue
        if forbidden_path(path):
            bad.append(rel(path, root))
    return sorted(bad)


def validate_managed_snapshot_paths(root: Path) -> None:
    bad: list[str] = []
    for relative in (*MANAGED_DIRS, *MANAGED_FILES):
        target = root / relative
        if target.is_symlink():
            bad.append(rel(target, root))
            continue
        if not target.is_dir():
            continue
        for path in target.rglob("*"):
            if path.is_symlink():
                bad.append(rel(path, root))
    if bad:
        raise SystemExit(
            "managed profile contains symbolic links:\n" + "\n".join(sorted(bad))
        )


def skill_tree_sha256(skill_dir: Path) -> str:
    """Hash one immutable skill snapshot by relative path and file content."""
    digest = hashlib.sha256()
    for path in sorted(skill_dir.rglob("*")):
        if path.is_symlink():
            raise SystemExit(f"third-party skill snapshot contains symlink: {path}")
        if not path.is_file():
            continue
        relative = path.relative_to(skill_dir).as_posix().encode("utf-8")
        digest.update(relative)
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def validate_personal_skill_source_notes(skill_dir: Path, root: Path) -> None:
    notes = skill_dir / "references" / "source-notes.md"
    if not notes.is_file() or notes.is_symlink():
        raise SystemExit(
            f"missing personal skill source-notes: {rel(skill_dir, root)}"
        )
    if not notes.read_text(encoding="utf-8").startswith("# Source Notes\n"):
        raise SystemExit(
            f"invalid personal skill source-notes heading: {rel(notes, root)}"
        )


def validate_third_party_skill_lock(root: Path) -> dict[str, dict[str, object]]:
    path = root / THIRD_PARTY_SKILL_LOCK_FILENAME
    if not path.is_file() or path.is_symlink():
        raise SystemExit(f"missing third-party skill lock: {path}")

    def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    try:
        data = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=unique_object,
        )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise SystemExit(f"invalid third-party skill lock: {path}: {exc}") from exc
    if not isinstance(data, dict) or set(data) != {"schema_version", "skills"}:
        raise SystemExit("invalid third-party skill lock top-level keys")
    if data["schema_version"] != 1 or not isinstance(data["skills"], list):
        raise SystemExit("invalid third-party skill lock schema")

    expected_entry_keys = {
        "name",
        "source_classification",
        "provenance_status",
        "admission_status",
        "portability_disposition",
        "source",
        "snapshot",
        "local_modifications",
        "provenance_gaps",
        "review_before_update",
    }
    expected_source_keys = {
        "repository",
        "requested_ref",
        "resolved_commit",
        "license",
        "checked",
    }
    expected_snapshot_keys = {
        "profile_revision",
        "profile_tree_oid",
        "hash_algorithm",
        "sha256",
    }
    entries: dict[str, dict[str, object]] = {}
    for raw_entry in data["skills"]:
        if not isinstance(raw_entry, dict) or set(raw_entry) != expected_entry_keys:
            raise SystemExit("invalid third-party skill lock entry keys")
        name = raw_entry["name"]
        if not isinstance(name, str) or re.fullmatch(r"[a-z0-9-]+", name) is None:
            raise SystemExit("invalid third-party skill lock name")
        if name in entries:
            raise SystemExit(f"duplicate third-party skill lock entry: {name}")

        source = raw_entry["source"]
        snapshot = raw_entry["snapshot"]
        if not isinstance(source, dict) or set(source) != expected_source_keys:
            raise SystemExit(f"invalid third-party skill lock source: {name}")
        if not isinstance(snapshot, dict) or set(snapshot) != expected_snapshot_keys:
            raise SystemExit(f"invalid third-party skill lock snapshot: {name}")
        repository = source["repository"]
        if not isinstance(repository, str) or re.fullmatch(
            r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\.git)?",
            repository,
        ) is None:
            raise SystemExit(f"invalid third-party skill repository: {name}")
        if not isinstance(source["requested_ref"], str) or not source["requested_ref"]:
            raise SystemExit(f"invalid third-party skill requested ref: {name}")
        resolved_commit = source["resolved_commit"]
        if resolved_commit is not None and (
            not isinstance(resolved_commit, str)
            or re.fullmatch(r"[0-9a-f]{40}", resolved_commit) is None
        ):
            raise SystemExit(f"invalid third-party skill resolved commit: {name}")
        if not isinstance(source["license"], str) or not source["license"].strip():
            raise SystemExit(f"invalid third-party skill license: {name}")
        try:
            datetime.strptime(source["checked"], "%Y-%m-%d")
        except (TypeError, ValueError) as exc:
            raise SystemExit(f"invalid third-party skill checked date: {name}") from exc

        source_classification = raw_entry["source_classification"]
        provenance_status = raw_entry["provenance_status"]
        admission_status = raw_entry["admission_status"]
        portability = raw_entry["portability_disposition"]
        if source_classification not in {
            "local-origin",
            "upstream-derived",
            "hybrid",
            "unresolved",
        }:
            raise SystemExit(f"invalid source_classification: {name}")
        if provenance_status not in {"complete", "partial", "missing", "conflicting"}:
            raise SystemExit(f"invalid provenance_status: {name}")
        if admission_status not in {"admitted", "legacy-exception"}:
            raise SystemExit(f"non-admitted third-party skill in portable lock: {name}")
        if portability != "vendor":
            raise SystemExit(f"invalid third-party portability disposition: {name}")
        if admission_status == "admitted" and provenance_status != "complete":
            raise SystemExit(f"admitted vendor provenance is incomplete: {name}")
        if provenance_status == "complete" and resolved_commit is None:
            raise SystemExit(f"complete vendor provenance lacks immutable commit: {name}")

        gaps = raw_entry["provenance_gaps"]
        if not isinstance(gaps, list) or not all(
            isinstance(item, str) and item.strip() for item in gaps
        ):
            raise SystemExit(f"invalid third-party provenance gaps: {name}")
        if (admission_status == "legacy-exception" or provenance_status != "complete") and not gaps:
            raise SystemExit(f"incomplete third-party provenance lacks gap: {name}")
        if raw_entry["local_modifications"] not in {"none", "present", "unknown"}:
            raise SystemExit(f"invalid third-party local modification state: {name}")
        if raw_entry["review_before_update"] is not True:
            raise SystemExit(f"third-party update review is not required: {name}")

        for key in ("profile_revision", "profile_tree_oid"):
            value = snapshot[key]
            if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{40}", value) is None:
                raise SystemExit(f"invalid third-party snapshot {key}: {name}")
        if snapshot["hash_algorithm"] != "sha256-path-content-v1":
            raise SystemExit(f"invalid third-party snapshot hash algorithm: {name}")
        expected_hash = snapshot["sha256"]
        if not isinstance(expected_hash, str) or re.fullmatch(r"[0-9a-f]{64}", expected_hash) is None:
            raise SystemExit(f"invalid third-party snapshot sha256: {name}")
        skill_dir = root / "skills" / "codex" / name
        if not skill_dir.is_dir() or skill_dir.is_symlink():
            raise SystemExit(f"allowlisted third-party skill is unavailable: {name}")
        if skill_tree_sha256(skill_dir) != expected_hash:
            raise SystemExit(f"third-party skill snapshot sha256 mismatch: {name}")
        entries[name] = raw_entry

    locked_names = set(entries)
    if locked_names != PORTABLE_CODEX_SKILL_NAMES:
        raise SystemExit(
            "third-party skill allowlist/lock mismatch: "
            f"allowlist={sorted(PORTABLE_CODEX_SKILL_NAMES)} "
            f"lock={sorted(locked_names)}"
        )
    skill_root = root / "skills" / "codex"
    managed_third_party = {
        item.name
        for item in skill_root.iterdir()
        if item.is_dir() and not item.name.startswith("personal-")
    }
    if managed_third_party != locked_names:
        raise SystemExit(
            "third-party skill directories/lock mismatch: "
            f"directories={sorted(managed_third_party)} "
            f"lock={sorted(locked_names)}"
        )
    return entries


def validate_skills(root: Path) -> None:
    skill_roots = [root / "skills" / "codex", root / "skills" / "agents"]
    personal_description_total = 0
    managed_description_total = 0
    for skill_root in skill_roots:
        if not skill_root.is_dir():
            continue
        for skill_dir in sorted(p for p in skill_root.iterdir() if p.is_dir()):
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.is_file():
                raise SystemExit(f"missing SKILL.md: {rel(skill_dir, root)}")
            text = skill_file.read_text(encoding="utf-8")
            fm = parse_frontmatter(text)
            if not fm.get("name") or not fm.get("description"):
                raise SystemExit(f"missing required frontmatter: {rel(skill_file, root)}")
            extra = set(fm) - ALLOWED_SKILL_KEYS
            if extra:
                raise SystemExit(f"unexpected frontmatter keys in {rel(skill_file, root)}: {sorted(extra)}")
            if fm["name"] != skill_dir.name:
                raise SystemExit(f"skill name/folder mismatch: {rel(skill_file, root)}")
            managed_description_total += len(fm["description"])
            if skill_dir.name.startswith("personal-"):
                personal_description_total += len(fm["description"])
                validate_personal_skill_openai_yaml(skill_dir, root)
            validate_skill_resource_links(skill_dir, root)
            if skill_dir.name.startswith("personal-"):
                validate_personal_skill_source_notes(skill_dir, root)
    if personal_description_total > PERSONAL_SKILL_DESCRIPTION_BUDGET:
        raise SystemExit(
            "personal skill description budget exceeded: "
            f"{personal_description_total} > {PERSONAL_SKILL_DESCRIPTION_BUDGET}"
        )
    if managed_description_total > MANAGED_SKILL_DESCRIPTION_BUDGET:
        raise SystemExit(
            "managed skill description budget exceeded: "
            f"{managed_description_total} > {MANAGED_SKILL_DESCRIPTION_BUDGET}"
        )


def parse_openai_interface(path: Path) -> dict[str, str]:
    """Parse the small, controlled interface mapping without a YAML dependency."""
    interface: dict[str, str] = {}
    in_interface = False
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if "\t" in raw_line:
            raise SystemExit(f"invalid tab indentation in {path}")
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if not raw_line.startswith(" "):
            in_interface = raw_line.strip() == "interface:"
            continue
        if not in_interface or not raw_line.startswith("  "):
            continue
        stripped = raw_line.strip()
        if ":" not in stripped:
            continue
        key, raw_value = stripped.split(":", 1)
        value = raw_value.strip()
        if value.startswith('"'):
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"invalid quoted value in {path}: {key}") from exc
            if not isinstance(parsed, str):
                raise SystemExit(f"non-string interface value in {path}: {key}")
            interface[key] = parsed
        elif value.startswith("'") and value.endswith("'"):
            interface[key] = value[1:-1].replace("''", "'")
        else:
            interface[key] = value
    return interface


def validate_personal_skill_openai_yaml(skill_dir: Path, root: Path) -> None:
    metadata = skill_dir / "agents" / "openai.yaml"
    if not metadata.is_file():
        raise SystemExit(f"missing agents/openai.yaml: {rel(skill_dir, root)}")
    interface = parse_openai_interface(metadata)
    missing = REQUIRED_OPENAI_INTERFACE_KEYS - set(interface)
    if missing:
        raise SystemExit(
            f"invalid agents/openai.yaml in {rel(skill_dir, root)}: "
            f"missing interface keys {sorted(missing)}"
        )
    if not interface["display_name"].strip():
        raise SystemExit(
            f"invalid agents/openai.yaml in {rel(skill_dir, root)}: empty display_name"
        )
    short_length = len(interface["short_description"])
    if not 25 <= short_length <= 64:
        raise SystemExit(
            f"invalid agents/openai.yaml in {rel(skill_dir, root)}: "
            f"short_description length {short_length} is outside 25..64"
        )
    invocation = f"${skill_dir.name}"
    if invocation not in interface["default_prompt"]:
        raise SystemExit(
            f"invalid agents/openai.yaml in {rel(skill_dir, root)}: "
            f"default_prompt must contain {invocation}"
        )


def validate_skill_resource_links(skill_dir: Path, root: Path) -> None:
    base = skill_dir.resolve()
    for markdown in sorted(skill_dir.rglob("*.md")):
        text = markdown.read_text(encoding="utf-8")
        for raw_target in MARKDOWN_LINK_RE.findall(text):
            target = raw_target.strip()
            if target.startswith("<") and target.endswith(">"):
                target = target[1:-1]
            target = target.split("#", 1)[0]
            if not target or target.startswith(("/", "#")):
                continue
            if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target):
                continue
            destination = (markdown.parent / target).resolve()
            try:
                destination.relative_to(base)
            except ValueError as exc:
                raise SystemExit(
                    f"skill resource link escapes skill root: "
                    f"{rel(markdown, root)} -> {raw_target}"
                ) from exc
            if not destination.exists():
                raise SystemExit(
                    f"missing skill resource: {rel(markdown, root)} -> {raw_target}"
                )


def validate_renamed_skills(root: Path) -> None:
    skill_root = root / "skills" / "codex"
    for legacy_name, successor_name in RENAMED_CODEX_SKILLS.items():
        legacy = skill_root / legacy_name
        successor = skill_root / successor_name
        if legacy.exists() or legacy.is_symlink():
            raise SystemExit(f"legacy renamed skill remains in profile: {rel(legacy, root)}")
        if not successor.is_dir() or successor.is_symlink():
            raise SystemExit(
                f"renamed skill successor is unavailable: {rel(successor, root)}"
            )


def validate_hookify(root: Path) -> None:
    count = 0
    for path in sorted((root / "hooks" / "rules").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        if "pattern" in fm:
            re.compile(fm["pattern"])
            count += 1
    print(f"hookify regex ok: {count}")


def validate_json(root: Path) -> None:
    template = root / "templates" / "hooks.json.template"
    text = template.read_text(encoding="utf-8")
    rendered = text.replace("{{HOME}}", "/tmp/codex-home").replace("{{PYTHON3}}", "python3")
    json.loads(rendered)


def validate_hooks(root: Path) -> None:
    scripts = sorted((root / "hooks" / "scripts").glob("*.py"))
    if scripts:
        cache = Path(tempfile.mkdtemp(prefix="codex-profile-pycache-"))
        try:
            result = run(["python3", "-X", f"pycache_prefix={cache}", "-m", "py_compile", *map(str, scripts)])
            if result.returncode:
                raise SystemExit(result.stderr or result.stdout)
        finally:
            shutil.rmtree(cache, ignore_errors=True)
    with tempfile.TemporaryDirectory(prefix="codex-profile-test-home-") as tmp_home:
        tmp_home_path = Path(tmp_home)
        rule_dst = tmp_home_path / ".codex" / "hookify"
        rule_dst.mkdir(parents=True)
        for rule in (root / "hooks" / "rules").glob("*.md"):
            shutil.copy2(rule, rule_dst / rule.name)
        env = os.environ.copy()
        env["HOME"] = str(tmp_home_path)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        for test_path in sorted((root / "hooks" / "scripts").glob("test_*.py")):
            result = run(["python3", str(test_path)], cwd=root, env=env)
            if result.returncode:
                raise SystemExit(result.stdout + result.stderr)


def validate_portable_config(root: Path) -> None:
    path = root / "templates" / "config.toml.template"
    if not path.is_file() or path.is_symlink():
        raise SystemExit(f"portable config template is unavailable: {path}")
    text = path.read_text(encoding="utf-8")
    if text != CONFIG_TEMPLATE:
        raise SystemExit("portable config template differs from the reviewed generator")
    required = (
        "[mcp_servers.openaiDeveloperDocs]",
        'url = "https://developers.openai.com/mcp"',
        "enabled = true",
    )
    missing = [item for item in required if item not in text]
    if missing:
        raise SystemExit(f"portable public MCP declaration is incomplete: {missing}")
    forbidden = (
        "bearer_token_env_var",
        "http_headers",
        "env_http_headers",
        "auth_status",
        "oauth",
        "token",
    )
    found = [item for item in forbidden if item in text.lower()]
    if found:
        raise SystemExit(f"portable config contains non-portable auth state: {found}")


def verify_repo(root: Path = REPO_ROOT) -> None:
    validate_managed_snapshot_paths(root)
    bad = scan_forbidden(root)
    if bad:
        raise SystemExit("forbidden paths:\n" + "\n".join(bad))
    validate_skills(root)
    validate_third_party_skill_lock(root)
    validate_renamed_skills(root)
    validate_custom_agents(root)
    validate_custom_agents_with_codex(root)
    validate_portable_config(root)
    validate_hookify(root)
    validate_json(root)
    validate_hooks(root)
    print("profile kit verification ok")


def export_dry_run(home: Path) -> DiffSummary:
    with tempfile.TemporaryDirectory(prefix="codex-profile-export-") as tmp:
        tmp_root = Path(tmp) / REPO_ROOT.name
        shutil.copytree(REPO_ROOT, tmp_root, ignore=shutil.ignore_patterns(".git"))
        export_to(tmp_root, home)
        return diff_dirs(tmp_root, REPO_ROOT)


def cmd_audit(args: argparse.Namespace) -> int:
    summary = export_dry_run(Path(args.home))
    print_diff(summary)
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    home = Path(args.home)
    if args.dry_run:
        print_diff(export_dry_run(home))
        return 0
    export_to(REPO_ROOT, home, tarball=args.tarball)
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    verify_repo(REPO_ROOT)
    return 0


def cmd_push(args: argparse.Namespace) -> int:
    export_to(REPO_ROOT, Path(args.home))
    verify_repo(REPO_ROOT)
    status = run(["git", "status", "--short"])
    print(status.stdout, end="")
    if not args.confirm:
        print("push skipped: rerun with --confirm to commit and push")
        return 0
    if not status.stdout.strip():
        print("nothing to commit")
        return 0
    run(["git", "add", "-A"], check_git_cwd())
    message = args.message or f"Sync Codex profile kit {datetime.now().strftime('%Y-%m-%d')}"
    commit = run(["git", "commit", "-m", message])
    if commit.returncode:
        raise SystemExit(commit.stdout + commit.stderr)
    push = run(["git", "push", "-u", "origin", "main"])
    if push.returncode:
        raise SystemExit(push.stdout + push.stderr)
    print(push.stdout, end="")
    return 0


def check_git_cwd() -> Path:
    return REPO_ROOT


def normalized_home(home: Path) -> Path:
    result = home.expanduser().absolute()
    if not result.is_dir():
        raise RuntimeError(f"target home must be an existing directory: {result}")
    return result


def safe_home_relative(
    path: Path,
    home: Path,
    *,
    label: str,
    expected_leaf: str | None = None,
) -> Path:
    """Validate a target path without following descendant symbolic links."""
    home = normalized_home(home)
    path = path.absolute()
    try:
        relative = path.relative_to(home)
    except ValueError as exc:
        raise RuntimeError(f"{label} escapes target home: {path}") from exc
    if not relative.parts:
        raise RuntimeError(f"{label} must be below target home: {path}")

    current = home
    for index, part in enumerate(relative.parts):
        current = current / part
        if not path_lexists(current):
            break
        metadata = os.lstat(current)
        if stat.S_ISLNK(metadata.st_mode):
            raise RuntimeError(f"{label} contains a symbolic link: {current}")
        is_leaf = index == len(relative.parts) - 1
        if not is_leaf and not stat.S_ISDIR(metadata.st_mode):
            raise RuntimeError(f"{label} parent is not a directory: {current}")
        if is_leaf and expected_leaf == "file" and not stat.S_ISREG(metadata.st_mode):
            raise RuntimeError(f"{label} is not a regular file: {current}")
        if is_leaf and expected_leaf == "dir" and not stat.S_ISDIR(metadata.st_mode):
            raise RuntimeError(f"{label} is not a regular directory: {current}")

    canonical_home = home.resolve(strict=True)
    canonical_path = path.resolve(strict=False)
    try:
        canonical_path.relative_to(canonical_home)
    except ValueError as exc:
        raise RuntimeError(f"{label} resolves outside target home: {path}") from exc
    return relative


def atomic_copy_regular_file(src: Path, dst: Path) -> None:
    source_metadata = os.lstat(src)
    if not stat.S_ISREG(source_metadata.st_mode):
        raise RuntimeError(f"copy source must be a regular file: {src}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    source_flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    source_fd = os.open(src, source_flags)
    temporary_fd = -1
    temporary_path: Path | None = None
    try:
        opened_metadata = os.fstat(source_fd)
        if not stat.S_ISREG(opened_metadata.st_mode):
            raise RuntimeError(f"copy source changed type while opening: {src}")
        temporary_fd, temporary_name = tempfile.mkstemp(
            prefix=f".{dst.name}.", dir=dst.parent
        )
        temporary_path = Path(temporary_name)
        with os.fdopen(source_fd, "rb") as source_handle:
            source_fd = -1
            with os.fdopen(temporary_fd, "wb") as destination_handle:
                temporary_fd = -1
                shutil.copyfileobj(source_handle, destination_handle)
        temporary_path.chmod(stat.S_IMODE(opened_metadata.st_mode))
        os.utime(
            temporary_path,
            ns=(opened_metadata.st_atime_ns, opened_metadata.st_mtime_ns),
            follow_symlinks=False,
        )
        os.replace(temporary_path, dst)
        temporary_path = None
    finally:
        if source_fd >= 0:
            os.close(source_fd)
        if temporary_fd >= 0:
            os.close(temporary_fd)
        if temporary_path is not None and path_lexists(temporary_path):
            temporary_path.unlink()


def atomic_write_text(dst: Path, text: str, mode: int = 0o600) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    temporary_fd, temporary_name = tempfile.mkstemp(
        prefix=f".{dst.name}.", dir=dst.parent
    )
    temporary_path: Path | None = Path(temporary_name)
    try:
        with os.fdopen(temporary_fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        assert temporary_path is not None
        temporary_path.chmod(mode)
        os.replace(temporary_path, dst)
        temporary_path = None
    finally:
        if temporary_path is not None and path_lexists(temporary_path):
            temporary_path.unlink()


def copy_file_with_backup(src: Path, dst: Path, backup_root: Path, home: Path) -> None:
    relative = safe_home_relative(
        dst, home, label="apply file destination", expected_leaf="file"
    )
    safe_home_relative(backup_root, home, label="apply backup root", expected_leaf="dir")
    if path_lexists(dst):
        backup = backup_root / relative
        safe_home_relative(
            backup, home, label="apply file backup", expected_leaf="file"
        )
        backup.parent.mkdir(parents=True, exist_ok=True)
        atomic_copy_regular_file(dst, backup)
    dst.parent.mkdir(parents=True, exist_ok=True)
    safe_home_relative(
        dst, home, label="apply file destination", expected_leaf="file"
    )
    atomic_copy_regular_file(src, dst)


def write_text_with_backup(
    text: str,
    dst: Path,
    backup_root: Path,
    home: Path,
    *,
    mode: int = 0o600,
) -> None:
    relative = safe_home_relative(
        dst, home, label="apply rendered destination", expected_leaf="file"
    )
    safe_home_relative(backup_root, home, label="apply backup root", expected_leaf="dir")
    if path_lexists(dst):
        backup = backup_root / relative
        safe_home_relative(
            backup, home, label="apply rendered backup", expected_leaf="file"
        )
        backup.parent.mkdir(parents=True, exist_ok=True)
        atomic_copy_regular_file(dst, backup)
    dst.parent.mkdir(parents=True, exist_ok=True)
    safe_home_relative(
        dst, home, label="apply rendered destination", expected_leaf="file"
    )
    atomic_write_text(dst, text, mode=mode)


def apply_pairs(home: Path) -> list[tuple[Path, Path]]:
    pairs: list[tuple[Path, Path]] = []
    for skill in (REPO_ROOT / "skills" / "codex").iterdir():
        if skill.is_dir():
            pairs.append((skill, home / ".codex" / "skills" / skill.name))
    for skill in (REPO_ROOT / "skills" / "agents").iterdir():
        if skill.is_dir():
            pairs.append((skill, home / ".agents" / "skills" / skill.name))
    pairs.extend(custom_agent_apply_pairs(REPO_ROOT, home))
    for path in (REPO_ROOT / "hooks" / "rules").glob("*.md"):
        pairs.append((path, home / ".codex" / "hookify" / path.name))
    for path in (REPO_ROOT / "hooks" / "scripts").glob("*.py"):
        pairs.append((path, home / ".codex" / "hooks" / path.name))
    return pairs


def validate_apply_plan(home: Path, pairs: list[tuple[Path, Path]], hooks_dst: Path) -> None:
    """Reject unsafe apply sources and targets before any target read or mutation."""
    home = normalized_home(home)
    planned_targets: list[Path] = []
    for src, dst in pairs:
        if src.is_symlink():
            raise RuntimeError(f"apply source must not be a symbolic link: {src}")
        if src.is_dir():
            expected_leaf = "dir"
        elif src.is_file():
            expected_leaf = "file"
        else:
            raise RuntimeError(f"apply source is unavailable: {src}")
        safe_home_relative(
            dst,
            home,
            label="apply destination",
            expected_leaf=expected_leaf,
        )
        planned_targets.append(dst.absolute())

    safe_home_relative(
        hooks_dst,
        home,
        label="rendered hooks destination",
        expected_leaf="file",
    )
    planned_targets.append(hooks_dst.absolute())
    for path in retired_hook_paths(home):
        safe_home_relative(
            path,
            home,
            label="retired hook destination",
            expected_leaf="file",
        )
        planned_targets.append(path.absolute())
    for legacy, successor in renamed_skill_paths(home):
        safe_home_relative(
            legacy,
            home,
            label="legacy renamed skill",
            expected_leaf="dir",
        )
        safe_home_relative(
            successor,
            home,
            label="renamed skill successor",
            expected_leaf="dir",
        )
        planned_targets.extend((legacy.absolute(), successor.absolute()))
    safe_home_relative(
        home / "codex-migration-archive",
        home,
        label="apply backup archive",
        expected_leaf="dir",
    )

    unique_targets = sorted(set(planned_targets), key=lambda item: (len(item.parts), str(item)))
    for index, target in enumerate(unique_targets):
        for other in unique_targets[index + 1 :]:
            if target in other.parents:
                raise RuntimeError(
                    f"apply destinations overlap unsafely: {target} and {other}"
                )


def retired_hook_paths(home: Path) -> list[Path]:
    return [home / relative for relative in RETIRED_HOOK_TARGETS]


def renamed_skill_paths(home: Path) -> list[tuple[Path, Path]]:
    skill_root = home / ".codex" / "skills"
    return [
        (skill_root / legacy, skill_root / successor)
        for legacy, successor in RENAMED_CODEX_SKILLS.items()
    ]


def pending_renamed_skills(home: Path) -> list[tuple[Path, Path]]:
    return [
        (legacy, successor)
        for legacy, successor in renamed_skill_paths(home)
        if legacy.exists() or legacy.is_symlink()
    ]


def backup_renamed_skills(
    pairs: list[tuple[Path, Path]], backup_root: Path, home: Path
) -> None:
    for legacy, _ in pairs:
        if legacy.is_symlink() or not legacy.is_dir():
            raise RuntimeError(f"legacy renamed skill is not a regular directory: {legacy}")
        try:
            relative = legacy.relative_to(home)
        except ValueError as exc:
            raise RuntimeError(f"legacy renamed skill escapes target home: {legacy}") from exc
        backup = backup_root / relative
        backup.parent.mkdir(parents=True, exist_ok=True)
        copytree(legacy, backup)


def retire_renamed_skills(pairs: list[tuple[Path, Path]]) -> None:
    retirable: list[Path] = []
    for legacy, successor in pairs:
        if not legacy.exists() and not legacy.is_symlink():
            continue
        if legacy.is_symlink() or not legacy.is_dir():
            raise RuntimeError(f"legacy renamed skill is not a regular directory: {legacy}")
        if successor.is_symlink() or not successor.is_dir():
            raise RuntimeError(f"renamed skill successor is unavailable: {successor}")
        source = REPO_ROOT / "skills" / "codex" / successor.name
        if not source.is_dir() or source.is_symlink():
            raise RuntimeError(f"verified profile successor is unavailable: {source}")
        summary = diff_dirs(source, successor)
        if summary.only_left or summary.only_right or summary.different:
            raise RuntimeError(f"installed successor does not match verified profile: {successor}")
        retirable.append(legacy)
    for legacy in retirable:
        shutil.rmtree(legacy)


def cmd_apply(args: argparse.Namespace) -> int:
    home = normalized_home(Path(args.home))
    verify_repo(REPO_ROOT)
    pairs = apply_pairs(home)
    hooks_dst = home / ".codex" / "hooks.json"
    validate_apply_plan(home, pairs, hooks_dst)
    renamed_pairs = pending_renamed_skills(home)
    changed: list[str] = []
    for src, dst in pairs:
        if not dst.exists() or (src.is_file() and sha256(src) != sha256(dst)):
            changed.append(f"{rel(src)} -> {dst}")
        elif src.is_dir():
            diff = filecmp.dircmp(src, dst)
            if diff.left_only or diff.right_only or diff.diff_files:
                changed.append(f"{rel(src)} -> {dst}")
    hooks_template = (REPO_ROOT / "templates" / "hooks.json.template").read_text(encoding="utf-8")
    rendered_hooks = hooks_template.replace("{{HOME}}", str(home)).replace("{{PYTHON3}}", "/usr/bin/python3")
    if not hooks_dst.exists() or hooks_dst.read_text(encoding="utf-8") != rendered_hooks:
        changed.append(f"templates/hooks.json.template -> {hooks_dst}")
    for path in retired_hook_paths(home):
        if path.exists():
            changed.append(f"retire {path}")
    for legacy, successor in renamed_pairs:
        changed.append(f"retire {legacy} after verified successor {successor}")

    print("manual review only: rules/AGENTS.portable.md and templates/config.toml.template")
    print(f"changed portable targets: {len(changed)}")
    for item in changed[:100]:
        print(f"  {item}")
    if len(changed) > 100:
        print(f"  ... +{len(changed) - 100} more")
    if not args.confirm:
        print("dry-run only: rerun with --confirm to apply")
        return 0

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    backup_root = home / "codex-migration-archive" / f"{stamp}-before-profile-kit-apply"
    safe_home_relative(
        backup_root,
        home,
        label="apply backup root",
        expected_leaf="dir",
    )
    backup_root.mkdir(parents=True, exist_ok=False)
    safe_home_relative(
        backup_root,
        home,
        label="apply backup root",
        expected_leaf="dir",
    )
    backup_renamed_skills(renamed_pairs, backup_root, home)
    for path in retired_hook_paths(home):
        if not path.exists():
            continue
        relative = safe_home_relative(
            path,
            home,
            label="retired hook destination",
            expected_leaf="file",
        )
        backup = backup_root / relative
        safe_home_relative(
            backup,
            home,
            label="retired hook backup",
            expected_leaf="file",
        )
        backup.parent.mkdir(parents=True, exist_ok=True)
        atomic_copy_regular_file(path, backup)
        path.unlink()
    for src, dst in pairs:
        if src.is_dir():
            if dst.exists():
                relative = safe_home_relative(
                    dst,
                    home,
                    label="apply directory destination",
                    expected_leaf="dir",
                )
                backup = backup_root / relative
                safe_home_relative(
                    backup,
                    home,
                    label="apply directory backup",
                    expected_leaf="dir",
                )
                backup.parent.mkdir(parents=True, exist_ok=True)
                copytree(dst, backup)
            copytree(src, dst)
        else:
            copy_file_with_backup(src, dst, backup_root, home)
    atomic_copy_regular_file(
        REPO_ROOT / "templates" / "hooks.json.template",
        backup_root / "rendered-hooks-template.txt",
    )
    write_text_with_backup(
        rendered_hooks,
        hooks_dst,
        backup_root,
        home,
        mode=0o600,
    )
    retire_renamed_skills(renamed_pairs)
    print(f"applied; backup: {backup_root}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", default=str(DEFAULT_HOME), help="active profile home")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("audit").set_defaults(func=cmd_audit)
    export = sub.add_parser("export")
    export.add_argument("--dry-run", action="store_true")
    export.add_argument("--tarball", action="store_true")
    export.set_defaults(func=cmd_export)
    sub.add_parser("verify").set_defaults(func=cmd_verify)
    push = sub.add_parser("push")
    push.add_argument("--confirm", action="store_true")
    push.add_argument("-m", "--message")
    push.set_defaults(func=cmd_push)
    apply = sub.add_parser("apply")
    apply.add_argument("--confirm", action="store_true")
    apply.set_defaults(func=cmd_apply)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
