#!/usr/bin/env python3
"""Collect a bounded, read-only inventory of the current Codex profile."""

from __future__ import annotations

import argparse
import ast
import ipaddress
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

try:
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # Python 3.10 on the current host.
    tomllib = None


SCHEMA_VERSION = 3
MAX_TEXT_BYTES = 64 * 1024
MAX_DOC_BYTES = 8 * 1024

EXCLUDED_PATH_COMPONENTS = {
    ".git",
    ".gnupg",
    ".ssh",
    "archived_sessions",
    "attachments",
    "cache",
    "logs",
    "memories",
    "sessions",
    "__pycache__",
}

SENSITIVE_NAMES = {
    ".netrc",
    "auth.json",
    "history.jsonl",
    "session_index.jsonl",
}

SCRIPT_SUFFIXES = ("py", "sh", "js", "mjs", "ts", "rb", "pl")
COMMAND_FILE_RE = re.compile(
    r"(?P<path>(?:~?/|\.\.?/)?[A-Za-z0-9_./${}()\-]+\."
    rf"(?:{'|'.join(SCRIPT_SUFFIXES)}))"
)
MCP_ID_RE = re.compile(r"[A-Za-z0-9_.-]{1,128}\Z")
MCP_HEADER_FIELDS = {"http_headers", "env_http_headers", "headers"}
MCP_ENV_AUTH_FIELDS = {"bearer_token_env_var"}
MCP_RUNTIME_AUTH_FIELDS = {"auth", "authentication", "authorization", "oauth"}
ALLOWLISTED_PUBLIC_MCP_URLS = {
    "https://developers.openai.com/mcp",
}


def read_limited(path: Path, max_bytes: int = MAX_TEXT_BYTES) -> str:
    with path.open("rb") as handle:
        data = handle.read(max_bytes)
    return data.decode("utf-8", errors="replace")


def parse_frontmatter(text: str) -> dict[str, str]:
    """Parse only unindented scalar keys from a Markdown frontmatter block."""
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    raw = text[4:end]
    data: dict[str, str] = {}
    for line in raw.splitlines():
        if not line or line[0].isspace():
            continue
        stripped = line.strip()
        if stripped.startswith(("#", "-")) or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        value = value.strip().strip('"').strip("'")
        data[key.strip()] = value
    return data


def parse_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered == "true":
            return True
        if lowered == "false":
            return False
    return None


def safe_mcp_id(raw: Any) -> str:
    value = raw if isinstance(raw, str) else str(raw)
    if MCP_ID_RE.fullmatch(value):
        return value
    return "redacted-invalid-id"


def safe_public_https_url(raw: Any) -> str | None:
    """Return only a reviewed public endpoint with no auth-bearing URL parts."""
    if not isinstance(raw, str):
        return None
    value = raw.strip()
    if not value or any(char.isspace() or ord(char) < 32 for char in value):
        return None
    try:
        parsed = urlsplit(value)
        host = parsed.hostname
        _ = parsed.port
    except ValueError:
        return None
    if parsed.scheme.lower() != "https" or not host:
        return None
    if parsed.username is not None or parsed.password is not None:
        return None
    if parsed.query or parsed.fragment:
        return None

    lowered_host = host.rstrip(".").lower()
    if lowered_host in {"localhost", "localhost.localdomain"}:
        return None
    if lowered_host.endswith((".localhost", ".local", ".internal")):
        return None
    try:
        address = ipaddress.ip_address(lowered_host)
    except ValueError:
        if "." not in lowered_host:
            return None
    else:
        if not address.is_global:
            return None
    return value if value in ALLOWLISTED_PUBLIC_MCP_URLS else None


def mcp_auth_mechanism(keys: set[str], *, has_url: bool) -> str:
    lowered = {key.lower() for key in keys}
    if any(key in MCP_RUNTIME_AUTH_FIELDS or key.startswith("oauth") for key in lowered):
        return "oauth-or-runtime"
    if lowered & MCP_HEADER_FIELDS:
        return "headers"
    if lowered & MCP_ENV_AUTH_FIELDS:
        return "env-var-name"
    if has_url and "env" not in lowered:
        return "none"
    return "not-collected"


def project_mcp_server(server_id: Any, raw: Any) -> dict[str, Any]:
    data = raw if isinstance(raw, dict) else {}
    present = data.get("_present_keys")
    keys = set(present) if isinstance(present, set) else {str(key) for key in data}
    url_candidate = data.get("url")
    has_url = isinstance(url_candidate, str) and bool(url_candidate.strip())
    has_command = "command" in keys
    if has_url and not has_command:
        transport = "streamable-http"
    elif has_command and not has_url:
        transport = "stdio"
    else:
        transport = "unknown"

    projected: dict[str, Any] = {
        "id": safe_mcp_id(server_id),
        "enabled": parse_bool(data.get("enabled")),
        "transport": transport,
        "auth_mechanism": mcp_auth_mechanism(keys, has_url=has_url),
    }
    public_url = safe_public_https_url(url_candidate)
    if public_url is not None and projected["auth_mechanism"] == "none":
        projected["public_url"] = public_url
    return projected


def parse_mcp_table_path(section: str) -> tuple[str, str | None] | None:
    prefix = "mcp_servers."
    if not section.startswith(prefix):
        return None
    tail = section[len(prefix) :].strip()
    if not tail:
        return None
    if tail[0] in {'"', "'"}:
        try:
            value = ast.literal_eval(tail)
        except (SyntaxError, ValueError):
            return None
        return (str(value), None) if isinstance(value, str) else None
    server_id, separator, nested = tail.partition(".")
    if not MCP_ID_RE.fullmatch(server_id):
        return None
    return server_id, nested if separator else None


def first_heading(text: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip() or None
    return None


def module_doc_summary(text: str) -> str | None:
    try:
        module = ast.parse(text)
    except SyntaxError:
        return None
    doc = ast.get_docstring(module)
    if not doc:
        return None
    first_line = " ".join(doc.strip().splitlines()).strip()
    if len(first_line) > 240:
        first_line = first_line[:237].rstrip() + "..."
    return first_line or None


def is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve(strict=False))
        return True
    except ValueError:
        return False


def is_sensitive_path(path: Path) -> bool:
    lowered_parts = {part.lower() for part in path.parts}
    if path.name.lower() in SENSITIVE_NAMES:
        return True
    if path.suffix.lower().startswith(".sqlite"):
        return True
    return bool(lowered_parts & EXCLUDED_PATH_COMPONENTS)


def rel(path: Path, home: Path) -> str:
    try:
        return str(path.relative_to(home))
    except ValueError:
        return str(path)


def collect_agents(home: Path) -> dict[str, Any]:
    agents_path = home / ".codex" / "AGENTS.md"
    result: dict[str, Any] = {
        "path": rel(agents_path, home),
        "exists": agents_path.is_file() and not agents_path.is_symlink(),
        "headings": [],
    }
    if not result["exists"]:
        return result
    text = read_limited(agents_path)
    headings = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            headings.append({"level": level, "title": stripped[level:].strip()})
    result["headings"] = headings
    return result


def collect_skills(home: Path) -> list[dict[str, Any]]:
    roots = [
        ("codex", home / ".codex" / "skills"),
        ("agents", home / ".agents" / "skills"),
    ]
    skills: list[dict[str, Any]] = []
    for source, root in roots:
        if not root.is_dir():
            continue
        for skill_dir in sorted(root.iterdir()):
            is_link = skill_dir.is_symlink()
            if skill_dir.name.startswith(".") or not (skill_dir.is_dir() or is_link):
                continue
            skill_file = skill_dir / "SKILL.md"
            entry: dict[str, Any] = {
                "source": source,
                "path": rel(skill_file, home),
                "folder": skill_dir.name,
                "symlink": is_link or skill_file.is_symlink(),
                "target_scope": "within-home",
                "metadata_status": "not-read",
                "name": "",
                "description": "",
            }

            resolved = skill_file.resolve(strict=False)
            if entry["symlink"] and not is_within(resolved, home):
                entry["target_scope"] = "outside-home"
                skills.append(entry)
                continue
            if is_sensitive_path(resolved):
                entry["target_scope"] = "sensitive-excluded"
                skills.append(entry)
                continue
            if not resolved.is_file():
                entry["metadata_status"] = "missing"
                skills.append(entry)
                continue

            text = read_limited(resolved)
            fm = parse_frontmatter(text)
            entry.update(
                {
                    "metadata_status": "read",
                    "name": fm.get("name", ""),
                    "description": fm.get("description", ""),
                }
            )
            skills.append(entry)
    return skills


def collect_hookify(home: Path) -> list[dict[str, Any]]:
    root = home / ".codex" / "hookify"
    rules: list[dict[str, Any]] = []
    if not root.is_dir():
        return rules
    for path in sorted(root.glob("*.md")):
        if path.is_symlink() or path.name == "README.md":
            continue
        text = read_limited(path)
        fm = parse_frontmatter(text)
        rules.append(
            {
                "path": rel(path, home),
                "name": fm.get("name", path.stem),
                "declared_enabled": parse_bool(fm.get("enabled")),
                "event": fm.get("event", ""),
                "action": fm.get("action", ""),
                "frontmatter_keys": sorted(fm),
                "top_level_pattern_present": "pattern" in fm,
                "top_level_pattern_length": len(fm.get("pattern", "")),
                "heading": first_heading(text),
            }
        )
    return rules


def strip_toml_comment(value: str) -> str:
    quote = ""
    escaped = False
    for index, char in enumerate(value):
        if escaped:
            escaped = False
            continue
        if char == "\\" and quote == '"':
            escaped = True
            continue
        if quote:
            if char == quote:
                quote = ""
            continue
        if char in {'"', "'"}:
            quote = char
        elif char == "#":
            return value[:index].rstrip()
    return value.strip()


def parse_toml_scalar(raw: str) -> Any:
    value = strip_toml_comment(raw).strip()
    parsed_bool = parse_bool(value)
    if parsed_bool is not None:
        return parsed_bool
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        try:
            return ast.literal_eval(value)
        except (SyntaxError, ValueError):
            return value[1:-1]
    return value


def limited_toml_projection(text: str) -> dict[str, Any]:
    """Parse only allowlisted config sections on Python versions without tomllib."""
    features: dict[str, Any] = {}
    skills_config: list[dict[str, Any]] = []
    hook_groups: list[dict[str, Any]] = []
    section = ""
    current_skill: dict[str, Any] | None = None
    current_group: dict[str, Any] | None = None
    current_handler: dict[str, Any] | None = None
    mcp_builders: dict[str, dict[str, Any]] = {}
    current_mcp_id: str | None = None
    current_mcp_nested: str | None = None
    parse_status = "ok"

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        array_match = re.fullmatch(r"\[\[([^\]]+)\]\]", line)
        table_match = re.fullmatch(r"\[([^\]]+)\]", line)
        if array_match:
            section = array_match.group(1)
            current_skill = None
            current_handler = None
            current_mcp_id = None
            current_mcp_nested = None
            if section == "skills.config":
                current_skill = {}
                skills_config.append(current_skill)
                current_group = None
            elif section.startswith("hooks.") and not section.startswith("hooks.state"):
                parts = section.split(".")
                if len(parts) == 2:
                    current_group = {
                        "event": parts[1],
                        "matcher_present": False,
                        "matcher": None,
                        "handlers": [],
                    }
                    hook_groups.append(current_group)
                elif len(parts) == 3 and parts[2] == "hooks":
                    candidates = [item for item in hook_groups if item["event"] == parts[1]]
                    current_group = candidates[-1] if candidates else None
                    if current_group is not None:
                        current_handler = {}
                        current_group["handlers"].append(current_handler)
                else:
                    parse_status = "partial"
            else:
                current_group = None
            continue
        if table_match:
            section = table_match.group(1)
            mcp_path = parse_mcp_table_path(section)
            if mcp_path is not None:
                current_mcp_id, current_mcp_nested = mcp_path
                builder = mcp_builders.setdefault(
                    current_mcp_id,
                    {"_present_keys": set()},
                )
                if current_mcp_nested:
                    root = current_mcp_nested.split(".", 1)[0]
                    builder["_present_keys"].add(root)
                    if root not in MCP_HEADER_FIELDS | MCP_RUNTIME_AUTH_FIELDS | {"env"}:
                        parse_status = "partial"
                current_skill = None
                current_group = None
                current_handler = None
                continue
            current_mcp_id = None
            current_mcp_nested = None
            if (section == "hooks" or section.startswith("hooks.")) and not section.startswith("hooks.state"):
                parse_status = "partial"
            current_skill = None
            current_group = None
            current_handler = None
            continue
        if "=" not in line:
            if (
                section in {"features", "skills.config"}
                or section.startswith("hooks.")
                or section.startswith("mcp_servers.")
            ):
                parse_status = "partial"
            continue
        key, raw_value = [part.strip() for part in line.split("=", 1)]
        if current_mcp_id is not None:
            builder = mcp_builders[current_mcp_id]
            if current_mcp_nested is not None:
                continue
            builder["_present_keys"].add(key)
            if key == "url":
                builder["url"] = parse_toml_scalar(raw_value)
            elif key == "enabled":
                builder["enabled"] = parse_toml_scalar(raw_value)
            continue
        if raw_value.startswith(('"""', "'''")):
            parse_status = "partial"
            continue
        value = parse_toml_scalar(raw_value)
        if section == "features" and key in {"hooks", "memories"}:
            features[key] = value
        elif section == "skills.config" and current_skill is not None and key in {"path", "enabled"}:
            current_skill[key] = value
        elif current_handler is not None and key in {"type", "command"}:
            current_handler[key] = value
        elif current_group is not None and key == "matcher":
            current_group["matcher_present"] = True
            current_group["matcher"] = value

    return {
        "features": features,
        "skills_config": skills_config,
        "hook_groups": hook_groups,
        "mcp_servers": [
            project_mcp_server(server_id, builder)
            for server_id, builder in mcp_builders.items()
        ],
        "parser": "limited-safe-projection",
        "parse_status": parse_status,
    }


def tomllib_projection(text: str) -> dict[str, Any]:
    assert tomllib is not None
    data = tomllib.loads(text)
    features = data.get("features", {}) if isinstance(data.get("features"), dict) else {}
    skills_table = data.get("skills", {}) if isinstance(data.get("skills"), dict) else {}
    raw_skills = skills_table.get("config", [])
    skills_config = raw_skills if isinstance(raw_skills, list) else []
    raw_mcp = data.get("mcp_servers", {})
    mcp_table = raw_mcp if isinstance(raw_mcp, dict) else {}
    hook_groups: list[dict[str, Any]] = []
    hooks = data.get("hooks", {}) if isinstance(data.get("hooks"), dict) else {}
    for event, raw_groups in hooks.items():
        if event == "state" or not isinstance(raw_groups, list):
            continue
        for raw_group in raw_groups:
            if not isinstance(raw_group, dict):
                continue
            handlers = raw_group.get("hooks", [])
            hook_groups.append(
                {
                    "event": str(event),
                    "matcher_present": "matcher" in raw_group,
                    "matcher": raw_group.get("matcher"),
                    "handlers": handlers if isinstance(handlers, list) else [],
                }
            )
    return {
        "features": features,
        "skills_config": skills_config,
        "hook_groups": hook_groups,
        "mcp_servers": [
            project_mcp_server(server_id, raw_server)
            for server_id, raw_server in mcp_table.items()
        ],
        "parser": "tomllib",
        "parse_status": "ok",
    }


def feature_state(value: Any, *, default_enabled: bool) -> str:
    parsed = parse_bool(value)
    if parsed is True:
        return "explicitly-enabled"
    if parsed is False:
        return "explicitly-disabled"
    return "default-enabled" if default_enabled else "default-disabled"


def project_config_path(raw: Any, home: Path) -> dict[str, Any]:
    if not isinstance(raw, str) or not raw:
        return {"path": "", "scope": "unknown"}
    if raw == "~":
        path = home
    elif raw.startswith("~/"):
        path = home / raw[2:]
    else:
        path = Path(raw)
    if not path.is_absolute():
        return {"path": raw, "scope": "relative-config"}
    if is_within(path, home):
        return {"path": rel(path, home), "scope": "home"}
    return {"path": path.name, "scope": "outside-home"}


def collect_config(home: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    path = home / ".codex" / "config.toml"
    public: dict[str, Any] = {
        "path": rel(path, home),
        "exists": path.is_file() and not path.is_symlink(),
        "parser": "none",
        "parse_status": "not-present",
        "hooks_feature": "default-enabled",
        "memories_feature": "default-disabled",
        "skills_config": [],
        "mcp_servers": [],
        "hook_state": "not-collected",
    }
    if not public["exists"]:
        return public, []

    text = read_limited(path)
    try:
        projection = tomllib_projection(text) if tomllib is not None else limited_toml_projection(text)
    except Exception:
        projection = {
            "features": {},
            "skills_config": [],
            "hook_groups": [],
            "mcp_servers": [],
            "parser": "tomllib" if tomllib is not None else "limited-safe-projection",
            "parse_status": "invalid-or-unsupported",
        }

    features = projection["features"]
    public.update(
        {
            "parser": projection["parser"],
            "parse_status": projection["parse_status"],
            "hooks_feature": feature_state(features.get("hooks"), default_enabled=True),
            "memories_feature": feature_state(features.get("memories"), default_enabled=False),
            "skills_config": [],
            "mcp_servers": projection["mcp_servers"],
        }
    )
    for item in projection["skills_config"]:
        if not isinstance(item, dict):
            continue
        projected = project_config_path(item.get("path"), home)
        projected["enabled"] = parse_bool(item.get("enabled"))
        public["skills_config"].append(projected)
    return public, projection["hook_groups"]


def collect_json_hook_groups(home: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    path = home / ".codex" / "hooks.json"
    if not path.is_file() or path.is_symlink():
        return [], []
    source = {
        "path": rel(path, home),
        "format": "json",
        "parse_status": "ok",
        "registration_count": 0,
    }
    try:
        data = json.loads(read_limited(path))
    except (json.JSONDecodeError, OSError):
        source["parse_status"] = "invalid-json"
        return [source], []
    hooks = data.get("hooks", {}) if isinstance(data, dict) else {}
    groups: list[dict[str, Any]] = []
    if isinstance(hooks, dict):
        for event, raw_groups in hooks.items():
            if not isinstance(raw_groups, list):
                continue
            for raw_group in raw_groups:
                if not isinstance(raw_group, dict):
                    continue
                handlers = raw_group.get("hooks", [])
                groups.append(
                    {
                        "source": rel(path, home),
                        "event": str(event),
                        "matcher_present": "matcher" in raw_group,
                        "matcher": raw_group.get("matcher"),
                        "handlers": handlers if isinstance(handlers, list) else [],
                    }
                )
    source["registration_count"] = sum(len(group["handlers"]) for group in groups)
    return [source], groups


def project_command_file(token: str, home: Path) -> tuple[dict[str, Any], Path | None]:
    if "$" in token or "$(" in token:
        return {"name": Path(token).name, "scope": "dynamic", "exists": None}, None
    if token.startswith("~/"):
        path = home / token[2:]
    else:
        path = Path(token)
    if not path.is_absolute():
        return {"name": path.name, "path": token, "scope": "runtime-relative", "exists": None}, None
    if not is_within(path, home):
        return {"name": path.name, "scope": "outside-home", "exists": None}, None
    resolved = path.resolve(strict=False)
    if is_sensitive_path(resolved):
        return {"name": path.name, "scope": "sensitive-excluded", "exists": None}, None
    return {
        "name": path.name,
        "path": rel(path, home),
        "scope": "home",
        "exists": path.is_file(),
    }, path


def extract_command_files(command: Any, home: Path) -> tuple[list[dict[str, Any]], list[Path]]:
    if not isinstance(command, str):
        return [], []
    projected: list[dict[str, Any]] = []
    local_paths: list[Path] = []
    seen: set[str] = set()
    for match in COMMAND_FILE_RE.finditer(command):
        token = match.group("path")
        if token in seen:
            continue
        seen.add(token)
        item, local_path = project_command_file(token, home)
        projected.append(item)
        if local_path is not None:
            local_paths.append(local_path)
    return projected, local_paths


def hook_file_metadata(path: Path, home: Path) -> dict[str, Any]:
    item: dict[str, Any] = {
        "path": rel(path, home),
        "name": path.name,
        "suffix": path.suffix,
        "description": "",
    }
    if path.suffix == ".md":
        text = read_limited(path)
        fm = parse_frontmatter(text)
        item["description"] = fm.get("description", "") or first_heading(text) or ""
    elif path.suffix == ".py":
        item["description"] = module_doc_summary(read_limited(path, MAX_DOC_BYTES)) or ""
    return item


def collect_hooks(
    home: Path,
    config: dict[str, Any],
    inline_groups: list[dict[str, Any]],
) -> dict[str, Any]:
    sources, json_groups = collect_json_hook_groups(home)
    groups = list(json_groups)
    if inline_groups:
        config_source = {
            "path": config["path"],
            "format": "inline-toml",
            "parse_status": config["parse_status"],
            "registration_count": sum(len(group.get("handlers", [])) for group in inline_groups),
        }
        sources.append(config_source)
        for group in inline_groups:
            copied = dict(group)
            copied["source"] = config["path"]
            groups.append(copied)

    registrations: list[dict[str, Any]] = []
    registered_paths: set[Path] = set()
    for group in groups:
        matcher = group.get("matcher")
        matcher_length = len(matcher) if isinstance(matcher, str) else 0
        for handler in group.get("handlers", []):
            if not isinstance(handler, dict):
                continue
            files, local_paths = extract_command_files(handler.get("command"), home)
            registered_paths.update(path.resolve(strict=False) for path in local_paths)
            existence_values = [item.get("exists") for item in files]
            if existence_values and all(value is True for value in existence_values):
                definition_exists: bool | None = True
            elif any(value is False for value in existence_values):
                definition_exists = False
            else:
                definition_exists = None
            registrations.append(
                {
                    "source": group.get("source", config["path"]),
                    "event": group.get("event", ""),
                    "matcher_present": bool(group.get("matcher_present")),
                    "matcher_length": matcher_length,
                    "handler_type": handler.get("type", "unknown"),
                    "command_present": isinstance(handler.get("command"), str),
                    "referenced_files": files,
                    "definition_exists": definition_exists,
                    "configured": True,
                    "global_feature_state": config["hooks_feature"],
                    "individual_enabled_state": "not-collected",
                    "trust_state": "not-collected",
                    "trust_check": "/hooks",
                }
            )

    root = home / ".codex" / "hooks"
    registered_files: list[dict[str, Any]] = []
    unreferenced_files: list[dict[str, Any]] = []
    if root.is_dir():
        for path in sorted(root.iterdir()):
            if not path.is_file() or path.is_symlink() or is_sensitive_path(path):
                continue
            metadata = hook_file_metadata(path, home)
            if path.resolve(strict=False) in registered_paths:
                registered_files.append(metadata)
            else:
                unreferenced_files.append(metadata)

    hookify_rules = collect_hookify(home)
    runner_registered = any(item["name"] == "hookify_codex_runner.py" for item in registered_files)
    for rule in hookify_rules:
        rule["runner_registered"] = runner_registered

    return {
        "feature_state": config["hooks_feature"],
        "sources": sources,
        "registrations": registrations,
        "registered_files": registered_files,
        "unreferenced_files": unreferenced_files,
        "hookify_rules": hookify_rules,
        "individual_enabled_state": "not-collected",
        "trust_state": "not-collected",
        "trust_check": "/hooks",
        "plugin_hooks": "not-collected",
        "managed_hooks": "not-collected",
    }


def collect_profile(home: Path) -> dict[str, Any]:
    home = home.expanduser().resolve()
    agents = collect_agents(home)
    skills = collect_skills(home)
    config, inline_groups = collect_config(home)
    hooks = collect_hooks(home, config, inline_groups)
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "home": str(home),
        "read_only": True,
        "scope": {
            "host": "current",
            "memory_content": "not-collected",
            "threads": "not-collected",
            "sessions": "not-collected",
        },
        "agents": agents,
        "skills": skills,
        "config": config,
        "hooks": hooks,
        "counts": {
            "agents_headings": len(agents["headings"]),
            "skills": len(skills),
            "hookify_rules": len(hooks["hookify_rules"]),
            "hook_registrations": len(hooks["registrations"]),
            "registered_hook_files": len(hooks["registered_files"]),
            "unreferenced_hook_files": len(hooks["unreferenced_files"]),
            "mcp_servers": len(config["mcp_servers"]),
        },
        "excluded_by_default": sorted(SENSITIVE_NAMES | EXCLUDED_PATH_COMPONENTS),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Collect a bounded, read-only Codex profile inventory as JSON."
    )
    parser.add_argument("--home", default=str(Path.home()), help="Current-host profile home")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    args = parser.parse_args()

    profile = collect_profile(Path(args.home))
    indent = 2 if args.pretty else None
    print(json.dumps(profile, ensure_ascii=False, indent=indent, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
