#!/usr/bin/env python3
"""Audit, export, verify, and apply a portable Codex profile kit."""

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


@dataclass(frozen=True)
class ReviewedPersonalSkillLegacySnapshot:
    """Compatibility lock plus distinct historical rollback source."""

    rollback_revision: str
    rollback_tree: str
    allowed_content_sha256: str


REVIEWED_PERSONAL_SKILL_LEGACY_SNAPSHOTS = {
    "personal-branch-finish": ReviewedPersonalSkillLegacySnapshot(
        rollback_revision="3791645f59c0eeec497755bd7301be78b44efbea",
        rollback_tree="ff0d3a66a8fd6962fa2050cd02a982a7fd03cff2",
        allowed_content_sha256=(
            "5fa82d29aa715da87df96253f2738073343ba0ee8a9af6c45aafd6cebbaead14"
        ),
    ),
    "personal-code-documentation": ReviewedPersonalSkillLegacySnapshot(
        rollback_revision="3791645f59c0eeec497755bd7301be78b44efbea",
        rollback_tree="074ebe5e1fe21df47535ea0a88a1e74bd357f5ae",
        allowed_content_sha256=(
            "65bc263c0733718fd50f10d2381e28945c584d042d7f69266e87381c95dc8e59"
        ),
    ),
    "personal-risk-verification": ReviewedPersonalSkillLegacySnapshot(
        rollback_revision="3791645f59c0eeec497755bd7301be78b44efbea",
        rollback_tree="943a87d8ac2d9cd229d25cee8d596d85e07bcfae",
        allowed_content_sha256=(
            "17b5368dcb7ef3e0553693858f0096f1ee7c48e38102670876b9ae9237e03dc2"
        ),
    ),
    "personal-writing-polish": ReviewedPersonalSkillLegacySnapshot(
        rollback_revision="3791645f59c0eeec497755bd7301be78b44efbea",
        rollback_tree="6dc2b073b17a9f90c809bf69aa7a09840558f403",
        allowed_content_sha256=(
            "534aa32b5273dcb8948f1cafb8b63b60f1dcd7a7c3d99e5917781fb21989857e"
        ),
    ),
}
PERSONAL_SKILL_ADMISSION_EVIDENCE_PREFIXES = (
    "static_pass: ",
    "runtime_pass: ",
    "product_pass: ",
)
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


@dataclass(frozen=True)
class RetiredCodexSkill:
    """Reviewed retirement policy for one historical Codex skill identity."""

    hash_algorithm: str
    digests: tuple[str, ...]
    replacement: str
    replacement_skills: tuple[str, ...] = ()
    active_contract_markers: tuple[str, ...] = ()
    replacement_contract_markers: tuple[str, ...] = ()
    replacement_provenance_markers: tuple[str, ...] = ()


RETIRED_CODEX_SKILLS = {
    "context-save-restore": RetiredCodexSkill(
        hash_algorithm="sha256-path-content-v1",
        digests=(
            "79a94c43f613d8c8fd8fb078b3fcb87aaaf4de6c1b6b0c9d357ad5a8323b429b",
        ),
        replacement=(
            "current-host exact-task bounded reads; use "
            "personal-planning-with-files-zh only for explicit durable state"
        ),
        replacement_skills=("personal-planning-with-files-zh",),
        active_contract_markers=(
            "for continuation on the current host",
            "exact task id",
            "bounded evidence request",
        ),
    ),
    "personal-context-compression": RetiredCodexSkill(
        hash_algorithm="sha256-path-content-v1",
        digests=(
            "d97d4095802982300cd7a4f102a3094208d7654a5a71bfb86074a7fd86f2b3c7",
            "3444c65483bf122b70440741b7c113f42b249dc6dca2affb402da0c3d6cfb5cc",
        ),
        replacement=(
            "ordinary compact handoff; use exact-task reads, "
            "personal-planning-with-files-zh, or a Triad memo only when applicable"
        ),
        replacement_skills=(
            "personal-planning-with-files-zh",
            "personal-triad-discussion",
        ),
        active_contract_markers=(
            "keep context bounded",
            "handoffs",
            "state evidence boundaries",
        ),
    ),
    "personal-context-optimization": RetiredCodexSkill(
        hash_algorithm="sha256-path-content-v1",
        digests=(
            "060a7de6a56d0be89f24ad8beb0037e9f552637f9917285e646e2c4ed85f2010",
            "1e19d268044d4d95695385c8e73076474ed717a17093fd4de94ed12cf494f92d",
        ),
        replacement="AGENTS targeted retrieval plus a bounded evidence executor",
        replacement_skills=("personal-subagent-boundaries",),
        active_contract_markers=(
            "keep context bounded",
            "prefer targeted inspection",
            "bounded evidence request",
        ),
        replacement_contract_markers=("bounded substantive read",),
    ),
    "personal-context-save-restore": RetiredCodexSkill(
        hash_algorithm="sha256-path-content-v1",
        digests=(
            "6ea5c7b02b56863ef1b570c5f0c5a623559388f10f3414a2af6f606b354fb420",
            "a5ec4a2e6adcb614247cb5193c2328637483e44803ccb28eb89005e640c285cb",
        ),
        replacement=(
            "current-host exact-task bounded reads; use "
            "personal-planning-with-files-zh only for explicit durable state"
        ),
        replacement_skills=("personal-planning-with-files-zh",),
        active_contract_markers=(
            "for continuation on the current host",
            "exact task id",
            "bounded evidence request",
        ),
    ),
    "personal-docs-sync-light": RetiredCodexSkill(
        hash_algorithm="sha256-path-content-v1",
        digests=(
            "36c32775022ea3590690ea533ed798f2732a9953f3bd12df4c0216341f58ea70",
            "d724aa2b0afdff7f4cb5f2a671a64328c9fcca1ec18011dde395ef0a0c54d9ea",
            "52089bce134700c1a4d891afeca4e282b39bcdf642ab177e5650bae6da6bb430",
        ),
        replacement="personal-code-documentation mode sync_existing",
        replacement_skills=("personal-code-documentation",),
        replacement_contract_markers=(
            "sync_existing",
        ),
        replacement_provenance_markers=(
            "personal-docs-sync-light",
            "36c32775022ea3590690ea533ed798f2732a9953f3bd12df4c0216341f58ea70",
            "d724aa2b0afdff7f4cb5f2a671a64328c9fcca1ec18011dde395ef0a0c54d9ea",
            "52089bce134700c1a4d891afeca4e282b39bcdf642ab177e5650bae6da6bb430",
        ),
    ),
    "personal-long-job-status": RetiredCodexSkill(
        hash_algorithm="sha256-path-content-v1",
        digests=(
            "ce9c278b5c6967ee94d10024917a0cd5cf90943c65c28bb1a5be3bc8ab315f8a",
            "7e1dd49c8defb5bc4f33b61e259176e38e372f4c584865b12af9ea37fa0859d8",
        ),
        replacement=(
            "ordinary bounded one-shot status; active monitoring uses "
            "personal-subagent-boundaries/references/monitoring.md"
        ),
        replacement_skills=("personal-subagent-boundaries",),
        active_contract_markers=(
            "ordinary status or eta request is one bounded read-only one-shot check",
            "active monitoring requires explicit observation authority",
        ),
        replacement_contract_markers=(
            "active monitoring",
            "references/monitoring.md",
        ),
    ),
    "personal-repo-intake": RetiredCodexSkill(
        hash_algorithm="sha256-path-content-v1",
        digests=(
            "84ec07eb713d208c98ab5497f4a5a4741a724a59b208f4acf406dc4fa05c6809",
            "944b137f2733088ff2aa17ea35740afe19dad3538d9a3cc4505bc714461c3153",
            "9fd34a5f80de9c3994ecaa455993c4e4f92f7bb15f7a0a2712865e25ba03a298",
        ),
        replacement="AGENTS bounded repository preflight",
        active_contract_markers=(
            "before broad repository edits",
            "dirty state",
            "verification path",
        ),
    ),
}

RENAMED_CODEX_SKILLS = {
    "hookify-writing-rules": "personal-codex-hook-rules",
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
    ".codex/hookify/warn-gpu-task-without-device-scope.md",
    ".codex/hookify/warn-long-running-direct-launch.md",
    ".codex/hookify/warn-long-running-monitoring.md",
    ".codex/hookify/warn-package-manager-install.md",
    ".codex/hookify/warn-sensitive-file-edits.md",
    ".codex/hookify/warn-sensitive-path-command.md",
)
# Reviewed from Git revision 24b4ef88e6545b018c94bb18b3bf260ed87bdcca.
REVIEWED_RETIRED_HOOK_TARGET_SHA256 = {
    ".codex/hookify/warn-gpu-task-without-device-scope.md": (
        "866364be7890d90faf08533c2e9e40fc9074bf9905980ea972fec1b2c8587438"
    ),
    ".codex/hookify/warn-long-running-direct-launch.md": (
        "ce09d5abef36adb88f84e8b2a5f3c742b31889f48f7e28f8e20b4b46e9c5a1c0"
    ),
    ".codex/hookify/warn-long-running-monitoring.md": (
        "6e159a09e3efcc899431f18abff11217f6b03ff5b3f0f1f9d338ac0d5072c8e1"
    ),
    ".codex/hookify/warn-package-manager-install.md": (
        "56023e289b942e979497b8ee55f081968082bbe8ff5acf5fbd4a79a27f5cbb66"
    ),
    ".codex/hookify/warn-sensitive-file-edits.md": (
        "5e3d5e228106f51174f2cb4633c6809ae20cc29510d4c80be3d82ce142ffdcb8"
    ),
    ".codex/hookify/warn-sensitive-path-command.md": (
        "b7cf3fd950692784ec773f6e780eac9e4dce9648559bce247218c67ba8b2b726"
    ),
}
REVIEWED_HOOK_SNAPSHOT_SHA256 = {
    "hooks/rules/README.md": "4642a0f45229b8edb18b8b01710c3091b664a7d94f2c47ead48d5fc7ac541929",
    "hooks/rules/block-base-conda-install.md": "590c70f67a75443791e9039f0537478586e630b6fbe863f2e9116c3636f19309",
    "hooks/rules/block-sensitive-file-edits.md": "653e4e0331261cd30c48cf0312cbd6db269b35adfdd6fa778ba49eea50a201eb",
    "hooks/rules/block-sensitive-path-command.md": "58b413968c5842065c817557724f38e2dd55ea95b1d2f0720bc53f96d848bd87",
    "hooks/scripts/direct_download_guard.py": "1c3799338a241ad0cc48563e08688bc9f4668b8f17d157e24a48330982f819db",
    "hooks/scripts/hookify_codex_runner.py": "615ebcad5ff5c68096a34eaaae15857d12e70aee1a313a1c2f9aab8bbcb85275",
    "hooks/scripts/test_direct_download_guard.py": "e98a6bd8ac39830b33cac97384a79028ce95c08dc8a3566f976deb28534d052f",
    "hooks/scripts/test_hookify_codex_runner.py": "4e1b953f415742f0610ef4714d5852aa6160701fa17449584cc8e78735c11188",
    "hooks/scripts/test_hooks_configuration.py": "3708f3d3ba3e86a4ba299eaf15d3e75907369736b90330ba9bcf0d49112f82cc",
    "templates/hooks.json.template": "f1834239a0ecc009f6da652d645ebc0505186f33c346676f6dfc23269e23995f",
}


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


REMOTE_CONNECTION_EXAMPLE = """# Remote Connection Contract — Portable Example

This is a reviewed, static, manual-only schema. Copy it outside the profile
repository before filling it. Never commit host values or credential material.
Unresolved placeholders are not executable. Profile export regenerates this
example from `scripts/sync.py`; export, audit, verify, and apply never read,
copy, create, overwrite, back up, or delete the active connection contract.

## Scope And Ownership

- Scope: current execution host only
- Control-plane owner: `{{CONTROL_PLANE_OWNER_ROLE}}`
- Runtime owner: `{{RUNTIME_OWNER_ROLE}}`
- Change authority: `{{EXPLICIT_USER_CONTROLLED_WORKFLOW}}`
- Active contract location: `{{HOST_LOCAL_CONTRACT_LOCATION}}`
- Required access mode: `{{RESTRICTIVE_LOCAL_ACCESS_MODE}}`

Record ownership boundaries before any transport, proxy, launcher, or
app-server change. A portable profile snapshot must not replace an externally
managed connection contract.

## Stable Entrypoints

- Codex launcher: `{{CODEX_ENTRYPOINT}}`
- Transport entrypoint: `{{TRANSPORT_ENTRYPOINT}}`
- Proxy or direct wrapper: `{{NETWORK_WRAPPER_OR_NONE}}`
- App-server startup owner: `{{APP_SERVER_STARTUP_OWNER}}`
- Managed runtime category: `{{RUNTIME_CATEGORY}}`
- Repository work-root category: `{{WORK_ROOT_CATEGORY}}`

Entrypoints must describe user-invoked interfaces, not embedded credentials or
an assumed shell mutation.

## Network Routes

| Route | Purpose | Endpoint category | Authentication category | Direct/proxy policy | Owner |
| --- | --- | --- | --- | --- | --- |
| `{{ROUTE_ID}}` | `{{PURPOSE}}` | `{{ENDPOINT_CATEGORY}}` | `{{AUTH_CATEGORY}}` | `{{ROUTE_POLICY}}` | `{{OWNER_ROLE}}` |

- Small direct-access preflight: `{{LOW_TRAFFIC_PREFLIGHT}}`
- Escalation entrypoint after a direct failure: `{{USER_CONTROLLED_FALLBACK}}`
- Revocation or disable path: `{{REVOCATION_WORKFLOW}}`

Store only route categories and reviewed entrypoints here. Keep tokens,
passwords, cookies, keys, authenticated URLs, and secret environment values in
their dedicated credential mechanisms.

## Health Verification

- Low-risk connectivity check: `{{CONNECTIVITY_CHECK}}`
- Launcher or service status check: `{{STATUS_CHECK}}`
- Expected healthy signal: `{{HEALTHY_SIGNAL}}`
- Expected failure classification: `{{FAILURE_CLASSIFICATION}}`
- Maximum bounded check duration: `{{CHECK_DURATION}}`

Verification must be non-destructive and small enough to distinguish transport,
authentication, proxy, launcher, and service failures without exposing secret
values.

## Logs And Diagnosis

- Primary log category or location: `{{PRIMARY_LOG_REFERENCE}}`
- Secondary diagnostic source: `{{SECONDARY_DIAGNOSTIC_REFERENCE}}`
- Redaction boundary: `{{REDACTION_RULE}}`
- Bounded inspection command: `{{BOUNDED_LOG_CHECK}}`
- Dynamic facts to re-check: `{{DYNAMIC_FACTS}}`

Do not copy whole logs into durable profile artifacts. Record only the evidence
needed to locate and classify a failure.

## Recovery And Rollback

- Last-known-good reference: `{{LAST_KNOWN_GOOD_REFERENCE}}`
- Backup location category: `{{BACKUP_LOCATION_CATEGORY}}`
- Rollback owner: `{{ROLLBACK_OWNER_ROLE}}`
- Stop condition: `{{STOP_CONDITION}}`
- Restore sequence: `{{RESTORE_SEQUENCE}}`
- Post-restore verification: `{{POST_RESTORE_CHECK}}`

Rollback must preserve the external control-plane owner's contract and stop for
new authority when recovery would touch credentials, broaden access, or replace
an unowned launcher or service.

## Known Limitations

- Unsupported route or environment: `{{UNSUPPORTED_CASE}}`
- External dependency: `{{EXTERNAL_DEPENDENCY}}`
- User action required: `{{USER_ACTION}}`
- Evidence gap: `{{UNVERIFIED_ASSUMPTION}}`

## Verification Record

- Last verified: `{{DATE_AND_TIME_ZONE}}`
- Runtime or client version category: `{{VERSION_REFERENCE}}`
- Verified by: `{{VERIFIER_ROLE}}`
- Evidence boundary: `{{WHAT_WAS_AND_WAS_NOT_TESTED}}`
- Re-check trigger: `{{CHANGE_OR_EXPIRY_TRIGGER}}`
- Re-check command: `{{LOW_RISK_RECHECK}}`
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
    if name in RETIRED_CODEX_SKILLS:
        return False
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
    codex = home / ".codex"
    preflight_retired_skills(home, codex / "skills")
    validate_export_renamed_skill_sources(home)
    validate_export_custom_agent_sources(home)
    agents = home / ".agents"
    clear_managed_snapshot(root)

    (root / "rules").mkdir(parents=True, exist_ok=True)
    write_text(root / "rules" / "AGENTS.portable.md", portable_agents(codex / "AGENTS.md"))

    (root / "templates").mkdir(parents=True, exist_ok=True)
    write_text(root / "templates" / "HOST_LOCAL_TEMPLATE.md", HOST_LOCAL_TEMPLATE)
    write_text(
        root / "templates" / "REMOTE_CONNECTION_EXAMPLE.md",
        REMOTE_CONNECTION_EXAMPLE,
    )
    write_text(root / "templates" / "config.toml.template", CONFIG_TEMPLATE)
    write_text(root / "templates" / "hooks.json.template", render_hooks_template(codex / "hooks.json", home))

    skills_root = root / "skills"
    (skills_root / "codex").mkdir(parents=True, exist_ok=True)
    for skill_dir in sorted((codex / "skills").iterdir()):
        if not skill_dir.is_dir() or skill_dir.name.startswith("."):
            continue
        if not is_portable_codex_skill(skill_dir.name):
            continue
        if skill_dir.name.startswith("personal-"):
            validate_personal_skill_openai_yaml(skill_dir, home)
            validate_personal_skill_source_notes(skill_dir, home)
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
    retired_hook_sources = {home / relative for relative in RETIRED_HOOK_TARGETS}
    for path in sorted((codex / "hooks").glob("*.py")):
        if path in retired_hook_sources:
            continue
        shutil.copy2(path, hooks_root / "scripts" / path.name)
    for path in sorted((codex / "hookify").glob("*.md")):
        if path in retired_hook_sources:
            continue
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
- `templates/REMOTE_CONNECTION_EXAMPLE.md`: reviewed static, manual-only remote
  connection example; it is never populated from the active host contract.
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
- `hooks/scripts/`: reviewed hook scripts and tests from `~/.codex/hooks`;
  export filters retired targets and verifies the pinned snapshot before code
  execution.
- `hooks/rules/`: reviewed controlled global Markdown rules from
  `~/.codex/hookify`, limited to the pinned portable inventory.
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
    """sha256-path-content-v1 over sorted regular-file paths and content hashes."""
    digest = hashlib.sha256()
    for path in sorted(skill_dir.rglob("*")):
        if path.is_symlink():
            raise SystemExit(f"skill snapshot contains symlink: {path}")
        try:
            info = path.stat(follow_symlinks=False)
        except OSError as exc:
            raise SystemExit(
                f"skill snapshot entry cannot be inspected: {path}"
            ) from exc
        if stat.S_ISDIR(info.st_mode):
            continue
        if not stat.S_ISREG(info.st_mode):
            raise SystemExit(
                f"skill snapshot contains non-regular entry: {path}"
            )
        relative = path.relative_to(skill_dir).as_posix().encode("utf-8")
        digest.update(relative)
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


@dataclass(frozen=True)
class RetiredSkillSnapshot:
    identity: str
    path: Path
    digest: str
    policy: RetiredCodexSkill


def validate_retired_skill_registry() -> None:
    seen_digests: set[str] = set()
    for identity, policy in RETIRED_CODEX_SKILLS.items():
        if policy.hash_algorithm != "sha256-path-content-v1":
            raise SystemExit(f"unsupported retired skill hash algorithm: {identity}")
        if not policy.digests:
            raise SystemExit(f"retired skill has no reviewed digests: {identity}")
        for digest in policy.digests:
            if re.fullmatch(r"[0-9a-f]{64}", digest) is None:
                raise SystemExit(f"invalid retired skill digest: {identity}: {digest}")
            if digest in seen_digests:
                raise SystemExit(f"duplicate retired skill digest: {digest}")
            seen_digests.add(digest)
        if not policy.replacement.strip():
            raise SystemExit(f"retired skill has no replacement contract: {identity}")


def _normalized_contract_text(text: str) -> str:
    return " ".join(text.casefold().split())


def replacement_live_contract_text(source: Path, skill_file: Path) -> str:
    """Read the SKILL contract and its linked Markdown references only."""

    pending = [skill_file]
    visited: set[Path] = set()
    chunks: list[str] = []
    while pending:
        path = pending.pop()
        resolved = path.resolve()
        if resolved in visited:
            continue
        try:
            resolved.relative_to(source.resolve())
        except ValueError as exc:
            raise RuntimeError(
                f"retired skill replacement contract link escapes skill root: {path}"
            ) from exc
        if path.name == "source-notes.md" or path.suffix.lower() != ".md":
            continue
        if path.is_symlink() or not path.is_file():
            raise RuntimeError(
                f"retired skill replacement contract reference is unavailable: {path}"
            )
        text = path.read_text(encoding="utf-8")
        visited.add(resolved)
        chunks.append(text)
        for raw_target in MARKDOWN_LINK_RE.findall(text):
            target = raw_target.strip()
            if target.startswith("<") and target.endswith(">"):
                target = target[1:-1]
            target = target.split("#", 1)[0]
            if not target or target.startswith(("/", "#")):
                continue
            if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target):
                continue
            destination = path.parent / target
            if destination.suffix.lower() == ".md":
                pending.append(destination)
    return "\n".join(chunks)


def validate_retired_replacement_sources(
    skill_root: Path,
    policies: Iterable[RetiredCodexSkill],
) -> None:
    """Verify every replacement exists and contains its reviewed contract."""

    unique_policies = tuple(dict.fromkeys(policies))
    for policy in unique_policies:
        replacement_text: list[str] = []
        provenance_text: list[str] = []
        for name in policy.replacement_skills:
            if name in RETIRED_CODEX_SKILLS:
                raise RuntimeError(
                    f"retired skill replacement points at another tombstone: {name}"
                )
            source = skill_root / name
            if source.is_symlink() or not source.is_dir():
                raise RuntimeError(
                    f"retired skill replacement prerequisite is unavailable: {source}"
                )
            skill_file = source / "SKILL.md"
            if not skill_file.is_file() or skill_file.is_symlink():
                raise RuntimeError(
                    f"retired skill replacement prerequisite lacks SKILL.md: {source}"
                )
            frontmatter = parse_frontmatter(skill_file.read_text(encoding="utf-8"))
            if frontmatter.get("name") != name or not frontmatter.get("description"):
                raise RuntimeError(
                    f"retired skill replacement prerequisite has invalid metadata: {source}"
                )
            for path in sorted(source.rglob("*")):
                if path.is_symlink():
                    raise RuntimeError(
                        f"retired skill replacement prerequisite contains a symlink: {path}"
                    )
            replacement_text.append(
                replacement_live_contract_text(source, skill_file)
            )
            notes = source / "references" / "source-notes.md"
            if notes.is_file() and not notes.is_symlink():
                provenance_text.append(notes.read_text(encoding="utf-8"))

        normalized = _normalized_contract_text("\n".join(replacement_text))
        missing = [
            marker
            for marker in policy.replacement_contract_markers
            if _normalized_contract_text(marker) not in normalized
        ]
        if missing:
            raise RuntimeError(
                "retired skill replacement contract prerequisite is pending migration: "
                + ", ".join(missing)
            )
        normalized_provenance = _normalized_contract_text(
            "\n".join(provenance_text)
        )
        missing_provenance = [
            marker
            for marker in policy.replacement_provenance_markers
            if _normalized_contract_text(marker) not in normalized_provenance
        ]
        if missing_provenance:
            raise RuntimeError(
                "retired skill replacement provenance prerequisite is incomplete: "
                + ", ".join(missing_provenance)
            )


def validate_active_retirement_contract(
    home: Path,
    snapshots: Iterable[RetiredSkillSnapshot],
) -> None:
    snapshots = tuple(snapshots)
    markers = sorted(
        {
            marker
            for snapshot in snapshots
            for marker in snapshot.policy.active_contract_markers
        }
    )
    if not markers:
        return
    agents = home / ".codex" / "AGENTS.md"
    try:
        safe_home_relative(
            agents,
            home,
            label="active AGENTS retirement prerequisite",
            expected_leaf="file",
        )
    except RuntimeError as exc:
        raise RuntimeError(
            f"pending migration: active AGENTS contract prerequisite is unsafe: {agents}"
        ) from exc
    if agents.is_symlink() or not agents.is_file():
        raise RuntimeError(
            f"pending migration: active AGENTS contract prerequisite is unavailable: {agents}"
        )
    normalized = _normalized_contract_text(agents.read_text(encoding="utf-8"))
    missing = [
        marker
        for marker in markers
        if _normalized_contract_text(marker) not in normalized
    ]
    if missing:
        raise RuntimeError(
            "pending migration: active AGENTS contract prerequisite is incomplete: "
            + ", ".join(missing)
        )


def preflight_retired_skills(
    home: Path,
    replacement_skill_root: Path,
) -> list[RetiredSkillSnapshot]:
    """Inspect every tombstoned identity before any profile mutation."""

    home = normalized_home(home)
    skill_root = home / ".codex" / "skills"
    snapshots: list[RetiredSkillSnapshot] = []
    errors: list[str] = []
    for identity, policy in sorted(RETIRED_CODEX_SKILLS.items()):
        path = skill_root / identity
        if not path_lexists(path):
            continue
        try:
            safe_home_relative(
                path,
                home,
                label="retired skill destination",
                expected_leaf="dir",
            )
            if path.is_symlink() or not path.is_dir():
                raise RuntimeError("not a regular directory")
            digest = skill_tree_sha256(path)
        except (RuntimeError, SystemExit) as exc:
            errors.append(f"{identity}: unsafe retired skill: {exc}")
            continue
        if digest not in policy.digests:
            errors.append(
                f"{identity}: retired skill conflict/divergence; unreviewed digest {digest}"
            )
            continue
        snapshots.append(
            RetiredSkillSnapshot(
                identity=identity,
                path=path,
                digest=digest,
                policy=policy,
            )
        )
    if errors:
        raise RuntimeError("retired skill preflight failed:\n" + "\n".join(errors))

    policies = [snapshot.policy for snapshot in snapshots]
    validate_retired_replacement_sources(replacement_skill_root, policies)
    validate_active_retirement_contract(home, snapshots)
    return snapshots


def validate_personal_skill_identity_paths(
    skill_dir: Path,
    root: Path,
) -> tuple[Path, Path]:
    if skill_dir.is_symlink():
        raise SystemExit(
            f"personal skill directory must not be a symbolic link: {rel(skill_dir, root)}"
        )
    if not skill_dir.is_dir():
        raise SystemExit(
            f"personal skill path must be a regular directory: {rel(skill_dir, root)}"
        )

    skill_file = skill_dir / "SKILL.md"
    if skill_file.is_symlink():
        raise SystemExit(
            f"personal SKILL.md must not be a symbolic link: {rel(skill_file, root)}"
        )
    if not skill_file.is_file():
        raise SystemExit(
            f"personal SKILL.md must be a regular file: {rel(skill_file, root)}"
        )

    agents_dir = skill_dir / "agents"
    if agents_dir.is_symlink():
        raise SystemExit(
            f"personal agents directory must not be a symbolic link: {rel(agents_dir, root)}"
        )
    if not agents_dir.is_dir():
        raise SystemExit(
            f"personal agents path must be a regular directory: {rel(agents_dir, root)}"
        )

    metadata = agents_dir / "openai.yaml"
    if metadata.is_symlink():
        raise SystemExit(
            "personal agents/openai.yaml must not be a symbolic link: "
            f"{rel(metadata, root)}"
        )
    if not metadata.is_file():
        raise SystemExit(
            "personal agents/openai.yaml must be a regular file: "
            f"{rel(metadata, root)}"
        )
    return skill_file, metadata


def validate_personal_skill_source_notes(skill_dir: Path, root: Path) -> None:
    validate_personal_skill_identity_paths(skill_dir, root)
    references_dir = skill_dir / "references"
    if references_dir.is_symlink():
        raise SystemExit(
            "personal references directory must not be a symbolic link: "
            f"{rel(references_dir, root)}"
        )
    if not references_dir.is_dir():
        raise SystemExit(
            "personal references path must be a regular directory: "
            f"{rel(references_dir, root)}"
        )
    notes = references_dir / "source-notes.md"
    if not notes.is_file() or notes.is_symlink():
        raise SystemExit(
            f"missing personal skill source-notes: {rel(skill_dir, root)}"
        )
    text = notes.read_text(encoding="utf-8")
    if not text.startswith("# Source Notes\n"):
        raise SystemExit(
            f"invalid personal skill source-notes heading: {rel(notes, root)}"
        )

    admission = parse_personal_skill_admission(text, notes)
    skill_name = admission["skill"]
    if skill_name != skill_dir.name:
        raise SystemExit(
            "personal skill admission identity mismatch: "
            f"{rel(notes, root)} records {skill_name!r}, expected {skill_dir.name!r}"
        )

    acquisition_mode = admission["acquisition_mode"]
    if acquisition_mode not in {"created", "installed"}:
        raise SystemExit(
            f"invalid personal skill admission acquisition_mode in {rel(notes, root)}: "
            f"{acquisition_mode!r}"
        )
    source_classification = admission["source_classification"]
    if source_classification not in {
        "local-origin",
        "upstream-derived",
        "hybrid",
        "unresolved",
    }:
        raise SystemExit(
            "invalid personal skill admission source_classification in "
            f"{rel(notes, root)}: {source_classification!r}"
        )
    provenance_status = admission["provenance_status"]
    if provenance_status not in {"complete", "partial", "missing", "conflicting"}:
        raise SystemExit(
            f"invalid personal skill admission provenance_status in {rel(notes, root)}: "
            f"{provenance_status!r}"
        )

    admission_status = admission["admission_status"]
    if admission_status not in {"admitted", "legacy-exception"}:
        raise SystemExit(
            f"non-portable personal skill admission_status in {rel(notes, root)}: "
            f"{admission_status!r}"
        )
    portability = admission["portability_disposition"]
    if portability not in {"vendor", "internalized"}:
        raise SystemExit(
            "non-portable personal skill admission portability_disposition in "
            f"{rel(notes, root)}: {portability!r}"
        )

    for status_field in ("safety_status", "trigger_status", "validation_status"):
        if admission[status_field] != "passed":
            raise SystemExit(
                f"personal skill admission {status_field} must be passed in "
                f"{rel(notes, root)}"
            )
    evidence_fields = {
        "safety_review": [admission["safety_review"]],
        "trigger_review": [admission["trigger_review"]],
        "validation": admission["validation"],
    }
    for evidence_field, evidence_items in evidence_fields.items():
        if not all(
            isinstance(item, str)
            and item.startswith(PERSONAL_SKILL_ADMISSION_EVIDENCE_PREFIXES)
            for item in evidence_items
        ):
            raise SystemExit(
                "passed personal skill admission evidence requires a controlled pass prefix in "
                f"{evidence_field}: {rel(notes, root)}"
            )
    unknowns = admission["unknowns"]
    unknowns_disposition = admission["unknowns_disposition"]
    if unknowns_disposition not in {
        "none",
        "bounded-nonmaterial",
        "provenance-gap",
    }:
        raise SystemExit(
            "invalid personal skill admission unknowns_disposition in "
            f"{rel(notes, root)}: {unknowns_disposition!r}"
        )

    if source_classification == "unresolved":
        raise SystemExit(
            "portable personal skill admission cannot use unresolved source classification in "
            f"{rel(notes, root)}"
        )
    if admission_status == "admitted":
        if provenance_status != "complete":
            raise SystemExit(
                "admitted personal skill requires complete provenance in "
                f"{rel(notes, root)}"
            )
        expected_disposition = "bounded-nonmaterial" if unknowns else "none"
        if unknowns_disposition != expected_disposition:
            raise SystemExit(
                "admitted personal skill unknowns/disposition mismatch in "
                f"{rel(notes, root)}: expected {expected_disposition!r}"
            )
    if admission_status == "legacy-exception":
        if provenance_status != "partial":
            raise SystemExit(
                "legacy-exception personal skill requires partial provenance in "
                f"{rel(notes, root)}"
            )
        if unknowns_disposition != "provenance-gap":
            raise SystemExit(
                "legacy-exception personal skill requires provenance-gap disposition in "
                f"{rel(notes, root)}"
            )
        if not unknowns:
            raise SystemExit(
                "legacy-exception personal skill must record its provenance gap in "
                f"{rel(notes, root)}"
            )
        update_rule = _normalized_contract_text(admission["update_rule"])
        if "re-admission" not in update_rule or not re.search(
            r"\b(?:no update|updates? (?:are )?blocked)\b", update_rule
        ):
            raise SystemExit(
                "legacy-exception personal skill must block updates pending re-admission in "
                f"{rel(notes, root)}"
            )
        rollback_basis = admission["rollback_basis"]
        rollback_normalized = rollback_basis.casefold()
        revisions = re.findall(
            r"\brevision\s+`?([0-9a-f]{40})`?(?![0-9a-f])",
            rollback_normalized,
        )
        trees = re.findall(
            r"\btree\s+`?([0-9a-f]{40})`?(?![0-9a-f])",
            rollback_normalized,
        )
        if "exact" not in rollback_normalized:
            raise SystemExit(
                "legacy-exception personal skill requires exact revision and tree rollback basis in "
                f"{rel(notes, root)}"
            )
        reviewed_snapshot = REVIEWED_PERSONAL_SKILL_LEGACY_SNAPSHOTS.get(
            skill_dir.name
        )
        if (
            len(revisions) != 1
            or len(trees) != 1
            or reviewed_snapshot is None
            or reviewed_snapshot.rollback_revision != revisions[0]
            or reviewed_snapshot.rollback_tree != trees[0]
        ):
            raise SystemExit(
                "legacy-exception personal skill requires its reviewed legacy snapshot binding in "
                f"{rel(notes, root)}"
            )
        actual_content_sha256 = skill_tree_sha256(skill_dir)
        if actual_content_sha256 != reviewed_snapshot.allowed_content_sha256:
            raise SystemExit(
                "legacy-exception personal skill violates its reviewed legacy content lock in "
                f"{rel(skill_dir, root)}: expected "
                f"{reviewed_snapshot.allowed_content_sha256}, observed "
                f"{actual_content_sha256}"
            )


PERSONAL_SKILL_ADMISSION_FIELDS = {
    "skill",
    "acquisition_mode",
    "source_classification",
    "provenance_status",
    "admission_status",
    "portability_disposition",
    "safety_status",
    "safety_review",
    "trigger_status",
    "trigger_review",
    "validation_status",
    "validation",
    "update_owner",
    "update_rule",
    "rollback_basis",
    "unknowns_disposition",
    "unknowns",
}
PERSONAL_SKILL_ADMISSION_LIST_FIELDS = {"validation", "unknowns"}


def _parse_controlled_yaml_scalar(raw_value: str, path: Path, field: str) -> str:
    value = raw_value.strip()
    if not value:
        raise SystemExit(f"empty {field} in {path}")
    if value.startswith('"'):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"invalid quoted {field} in {path}") from exc
        if not isinstance(parsed, str):
            raise SystemExit(f"non-string {field} in {path}")
        return parsed
    if value.startswith("'"):
        if len(value) < 2 or not value.endswith("'"):
            raise SystemExit(f"invalid quoted {field} in {path}")
        return value[1:-1].replace("''", "'")
    if value in {"null", "Null", "NULL", "~", "{}"} or value.startswith("["):
        raise SystemExit(f"unsupported scalar {field} in {path}")
    return value


def parse_personal_skill_admission(text: str, path: Path) -> dict[str, object]:
    """Parse one deliberately small YAML admission mapping embedded in Markdown."""

    lines = text.splitlines()
    starts = [index for index, line in enumerate(lines) if line == "skill_admission:"]
    if len(starts) != 1:
        raise SystemExit(
            f"personal skill source-notes must contain exactly one admission record: {path}"
        )

    result: dict[str, object] = {}
    current_list: str | None = None
    for raw_line in lines[starts[0] + 1 :]:
        if "\t" in raw_line:
            raise SystemExit(f"invalid tab indentation in personal skill admission: {path}")
        if not raw_line.strip():
            continue
        if not raw_line.startswith("  "):
            break
        if raw_line.startswith("    - "):
            if current_list is None:
                raise SystemExit(f"unexpected admission list item in {path}")
            item = _parse_controlled_yaml_scalar(
                raw_line[6:], path, f"{current_list} item"
            )
            cast_list = result[current_list]
            if not isinstance(cast_list, list):
                raise SystemExit(f"invalid admission list in {path}: {current_list}")
            cast_list.append(item)
            continue
        if raw_line.startswith("   "):
            raise SystemExit(f"invalid admission indentation in {path}: {raw_line!r}")

        stripped = raw_line[2:]
        if ":" not in stripped:
            raise SystemExit(f"invalid personal skill admission field in {path}")
        field, raw_value = stripped.split(":", 1)
        field = field.strip()
        if field not in PERSONAL_SKILL_ADMISSION_FIELDS:
            raise SystemExit(f"unexpected personal skill admission field in {path}: {field}")
        if field in result:
            raise SystemExit(f"duplicate personal skill admission field in {path}: {field}")
        if field in PERSONAL_SKILL_ADMISSION_LIST_FIELDS:
            value = raw_value.strip()
            if value not in {"", "[]"}:
                raise SystemExit(f"personal skill admission {field} must be a list in {path}")
            result[field] = []
            current_list = field
        else:
            result[field] = _parse_controlled_yaml_scalar(raw_value, path, field)
            current_list = None

    missing = PERSONAL_SKILL_ADMISSION_FIELDS - set(result)
    if missing:
        raise SystemExit(
            f"personal skill admission is missing fields in {path}: {sorted(missing)}"
        )
    for field in PERSONAL_SKILL_ADMISSION_FIELDS - PERSONAL_SKILL_ADMISSION_LIST_FIELDS:
        value = result[field]
        if not isinstance(value, str) or not value.strip():
            raise SystemExit(f"personal skill admission {field} must be non-empty in {path}")
    validation = result["validation"]
    if not isinstance(validation, list) or not validation:
        raise SystemExit(f"personal skill admission validation must be non-empty in {path}")
    return result


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
            if skill_dir.name in RETIRED_CODEX_SKILLS:
                raise SystemExit(
                    f"retired skill identity remains in profile: {rel(skill_dir, root)}"
                )
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


def parse_openai_metadata(path: Path) -> dict[str, dict[str, object]]:
    """Parse the controlled interface and policy mappings without PyYAML."""

    sections: dict[str, dict[str, object]] = {"interface": {}, "policy": {}}
    current_section: str | None = None
    seen_sections: set[str] = set()
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if "\t" in raw_line:
            raise SystemExit(f"invalid tab indentation in {path}")
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if not raw_line.startswith(" "):
            stripped = raw_line.strip()
            section = stripped[:-1] if stripped.endswith(":") else ""
            if section in sections:
                if section in seen_sections:
                    raise SystemExit(f"duplicate {section} mapping in {path}")
                seen_sections.add(section)
                current_section = section
            else:
                current_section = None
            continue
        if current_section is None or not raw_line.startswith("  "):
            continue
        if raw_line.startswith("   "):
            continue
        stripped = raw_line.strip()
        if ":" not in stripped:
            continue
        key, raw_value = stripped.split(":", 1)
        key = key.strip()
        section_values = sections[current_section]
        if key in section_values:
            raise SystemExit(f"duplicate {current_section} value in {path}: {key}")
        value = raw_value.strip()
        if value.startswith('"'):
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"invalid quoted value in {path}: {key}") from exc
            if not isinstance(parsed, str):
                raise SystemExit(
                    f"non-string {current_section} value in {path}: {key}"
                )
            section_values[key] = parsed
        elif value.startswith("'") and value.endswith("'"):
            section_values[key] = value[1:-1].replace("''", "'")
        elif value in {"true", "false"}:
            section_values[key] = value == "true"
        else:
            section_values[key] = value
    return sections


def parse_openai_interface(path: Path) -> dict[str, str]:
    """Return the string-valued interface mapping from controlled metadata."""

    interface = parse_openai_metadata(path)["interface"]
    for key, value in interface.items():
        if not isinstance(value, str):
            raise SystemExit(f"non-string interface value in {path}: {key}")
    return interface  # type: ignore[return-value]


def validate_personal_skill_openai_yaml(skill_dir: Path, root: Path) -> None:
    skill_file, metadata = validate_personal_skill_identity_paths(skill_dir, root)
    parsed_metadata = parse_openai_metadata(metadata)
    interface_values = parsed_metadata["interface"]
    for key, value in interface_values.items():
        if not isinstance(value, str):
            raise SystemExit(
                f"invalid agents/openai.yaml in {rel(skill_dir, root)}: "
                f"non-string interface value {key}"
            )
    interface: dict[str, str] = interface_values  # type: ignore[assignment]
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

    policy = parsed_metadata["policy"]
    if "allow_implicit_invocation" not in policy:
        raise SystemExit(
            f"invalid agents/openai.yaml in {rel(skill_dir, root)}: "
            "missing required policy.allow_implicit_invocation"
        )
    implicit_policy = policy["allow_implicit_invocation"]
    if not isinstance(implicit_policy, bool):
        raise SystemExit(
            f"invalid agents/openai.yaml in {rel(skill_dir, root)}: "
            "policy.allow_implicit_invocation must be true or false"
        )
    description = _normalized_contract_text(
        parse_frontmatter(skill_file.read_text(encoding="utf-8")).get(
            "description", ""
        )
    )
    manual_only_markers = (
        "manual only",
        "only when the user explicitly invokes",
        "only when the user explicitly requests",
        "use only for explicitly requested",
    )
    if implicit_policy and any(marker in description for marker in manual_only_markers):
        raise SystemExit(
            f"invalid agents/openai.yaml in {rel(skill_dir, root)}: "
            "manual-only skill requires policy.allow_implicit_invocation: false"
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


def validate_reviewed_hook_snapshot(root: Path) -> None:
    """Reject exported hook code before compiling or executing candidate tests."""

    expected = set(REVIEWED_HOOK_SNAPSHOT_SHA256)
    observed: set[str] = set()
    for relative_dir in ("hooks/scripts", "hooks/rules"):
        directory = root / relative_dir
        if directory.is_symlink() or not directory.is_dir():
            raise SystemExit(
                f"reviewed hook snapshot directory is unavailable: {directory}"
            )
        for path in sorted(directory.iterdir()):
            relative = rel(path, root)
            if path.is_symlink() or not path.is_file():
                raise SystemExit(
                    f"reviewed hook snapshot contains a non-regular entry: {relative}"
                )
            observed.add(relative)

    template = root / "templates" / "hooks.json.template"
    if template.is_symlink() or not template.is_file():
        raise SystemExit(
            f"reviewed hook snapshot template is unavailable: {template}"
        )
    observed.add(rel(template, root))

    missing = sorted(expected - observed)
    extra = sorted(observed - expected)
    if missing or extra:
        details = []
        if missing:
            details.append("missing=" + ",".join(missing))
        if extra:
            details.append("extra=" + ",".join(extra))
        raise SystemExit(
            "reviewed hook snapshot inventory mismatch: " + "; ".join(details)
        )

    changed = [
        relative
        for relative, expected_digest in REVIEWED_HOOK_SNAPSHOT_SHA256.items()
        if sha256(root / relative) != expected_digest
    ]
    if changed:
        raise SystemExit(
            "reviewed hook snapshot digest mismatch: " + ", ".join(sorted(changed))
        )


def validate_hooks(root: Path) -> None:
    validate_reviewed_hook_snapshot(root)
    scripts_root = root / "hooks" / "scripts"
    scripts = sorted(scripts_root.glob("*.py"))
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
        count_script = (
            "import pathlib, sys, unittest; "
            "suite = unittest.defaultTestLoader.discover("
            "str(pathlib.Path(sys.argv[1])), pattern='test_*.py'); "
            "print(suite.countTestCases())"
        )
        count = run(["python3", "-c", count_script, str(scripts_root)], cwd=root, env=env)
        if count.returncode:
            raise SystemExit(count.stdout + count.stderr)
        try:
            test_count = int(count.stdout.strip())
        except ValueError as exc:
            raise SystemExit(
                f"hook test discovery returned an invalid count: {count.stdout!r}"
            ) from exc
        if test_count == 0:
            raise SystemExit("hook validation found zero tests")
        result = run(
            [
                "python3",
                "-m",
                "unittest",
                "discover",
                "-s",
                str(scripts_root),
                "-p",
                "test_*.py",
            ],
            cwd=root,
            env=env,
        )
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


def validate_remote_connection_example(root: Path) -> None:
    path = root / "templates" / "REMOTE_CONNECTION_EXAMPLE.md"
    if not path.is_file() or path.is_symlink():
        raise SystemExit(f"static remote connection example is unavailable: {path}")
    if path.read_text(encoding="utf-8") != REMOTE_CONNECTION_EXAMPLE:
        raise SystemExit(
            "remote connection example differs from the reviewed static generator"
        )


def verify_repo(root: Path = REPO_ROOT) -> None:
    validate_retired_skill_registry()
    validate_managed_snapshot_paths(root)
    bad = scan_forbidden(root)
    if bad:
        raise SystemExit("forbidden paths:\n" + "\n".join(bad))
    validate_skills(root)
    validate_retired_replacement_sources(
        root / "skills" / "codex",
        RETIRED_CODEX_SKILLS.values(),
    )
    validate_third_party_skill_lock(root)
    validate_renamed_skills(root)
    validate_custom_agents(root)
    validate_custom_agents_with_codex(root)
    validate_remote_connection_example(root)
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
    raise SystemExit(
        "legacy sync.py push is disabled and fails closed; use "
        "audit -> export -> inspect -> personal-risk-verification -> github:yeet"
    )


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


def validate_reviewed_retired_hook_targets(home: Path) -> None:
    """Fail closed when a reviewed retired Hookify target drifted."""

    home = normalized_home(home)
    retired_targets = set(RETIRED_HOOK_TARGETS)
    for relative, approved_digest in sorted(
        REVIEWED_RETIRED_HOOK_TARGET_SHA256.items()
    ):
        if relative not in retired_targets:
            raise RuntimeError(
                f"reviewed retired hook is not registered for retirement: {relative}"
            )
        if re.fullmatch(r"[0-9a-f]{64}", approved_digest) is None:
            raise RuntimeError(
                f"reviewed retired hook has an invalid digest: {relative}"
            )
        target = home / relative
        safe_home_relative(
            target,
            home,
            label="reviewed retired hook target",
            expected_leaf="file",
        )
        if not path_lexists(target):
            continue
        observed_digest = sha256(target)
        if observed_digest != approved_digest:
            raise RuntimeError(
                f"unreviewed retired hook digest: {relative}: {observed_digest}"
            )


def validate_apply_plan(
    home: Path,
    pairs: list[tuple[Path, Path]],
    hooks_dst: Path,
) -> list[RetiredSkillSnapshot]:
    """Reject unsafe apply sources and targets before any target read or mutation."""
    home = normalized_home(home)
    validate_reviewed_retired_hook_targets(home)
    retired_snapshots = preflight_retired_skills(
        home,
        REPO_ROOT / "skills" / "codex",
    )
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
    for snapshot in retired_snapshots:
        planned_targets.append(snapshot.path.absolute())
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
    return retired_snapshots


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


def create_unique_apply_backup_root(home: Path) -> Path:
    archive_root = home / "codex-migration-archive"
    safe_home_relative(
        archive_root,
        home,
        label="apply backup archive",
        expected_leaf="dir",
    )
    archive_root.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    base_name = f"{stamp}-before-profile-kit-apply"
    for index in range(10_000):
        suffix = "" if index == 0 else f"-{index}"
        candidate = archive_root / f"{base_name}{suffix}"
        if path_lexists(candidate):
            continue
        safe_home_relative(
            candidate,
            home,
            label="apply backup root",
            expected_leaf="dir",
        )
        try:
            candidate.mkdir(exist_ok=False)
        except FileExistsError:
            continue
        return candidate
    raise RuntimeError("could not allocate a unique apply backup directory")


def backup_retired_skills(
    snapshots: Iterable[RetiredSkillSnapshot],
    backup_root: Path,
    home: Path,
) -> None:
    for snapshot in snapshots:
        relative = safe_home_relative(
            snapshot.path,
            home,
            label="retired skill destination",
            expected_leaf="dir",
        )
        backup = backup_root / relative
        safe_home_relative(
            backup,
            home,
            label="retired skill backup",
            expected_leaf="dir",
        )
        backup.parent.mkdir(parents=True, exist_ok=True)
        copytree(snapshot.path, backup)
        archived_digest = skill_tree_sha256(backup)
        if archived_digest != snapshot.digest:
            raise RuntimeError(
                f"retired skill archive digest mismatch: {snapshot.identity}"
            )


def write_retired_skill_archive_manifest(
    snapshots: Iterable[RetiredSkillSnapshot],
    backup_root: Path,
    home: Path,
) -> None:
    entries = []
    for snapshot in snapshots:
        original = safe_home_relative(
            snapshot.path,
            home,
            label="retired skill destination",
            expected_leaf="dir",
        ).as_posix()
        entries.append(
            {
                "identity": snapshot.identity,
                "hash_algorithm": snapshot.policy.hash_algorithm,
                "digest": snapshot.digest,
                "original_path": original,
                "archive_path": original,
                "replacement": snapshot.policy.replacement,
            }
        )
    manifest = {
        "schema_version": 1,
        "retired_skills": entries,
        "restore_guidance": [
            (
                "Restore only while using a profile-kit revision that does not "
                "contain the corresponding retirement tombstone."
            ),
            "Require the original destination path to be absent before restore.",
            (
                "Recompute sha256-path-content-v1 for the archived directory and "
                "require the recorded digest before restore."
            ),
        ],
    }
    manifest_path = backup_root / "retired-skills-manifest.json"
    safe_home_relative(
        manifest_path,
        home,
        label="retired skill archive manifest",
        expected_leaf="file",
    )
    atomic_write_text(
        manifest_path,
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        mode=0o600,
    )


def retire_reviewed_skills(snapshots: Iterable[RetiredSkillSnapshot], home: Path) -> None:
    skill_root = home / ".codex" / "skills"
    retirable: list[Path] = []
    for snapshot in snapshots:
        safe_home_relative(
            snapshot.path,
            home,
            label="retired skill destination",
            expected_leaf="dir",
        )
        if skill_tree_sha256(snapshot.path) != snapshot.digest:
            raise RuntimeError(
                f"retired skill changed after preflight: {snapshot.identity}"
            )
        for replacement_name in snapshot.policy.replacement_skills:
            installed = skill_root / replacement_name
            source = REPO_ROOT / "skills" / "codex" / replacement_name
            if installed.is_symlink() or not installed.is_dir():
                raise RuntimeError(
                    f"installed retirement replacement is unavailable: {installed}"
                )
            summary = diff_dirs(source, installed)
            if summary.only_left or summary.only_right or summary.different:
                raise RuntimeError(
                    f"installed retirement replacement differs from profile: {installed}"
                )
        retirable.append(snapshot.path)
    for path in retirable:
        shutil.rmtree(path)


def cmd_apply(args: argparse.Namespace) -> int:
    home = normalized_home(Path(args.home))
    verify_repo(REPO_ROOT)
    pairs = apply_pairs(home)
    hooks_dst = home / ".codex" / "hooks.json"
    retired_snapshots = validate_apply_plan(home, pairs, hooks_dst)
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
    for snapshot in retired_snapshots:
        changed.append(
            f"retire {snapshot.path} after archived digest {snapshot.digest}"
        )

    print("manual review only: rules/AGENTS.portable.md and templates/config.toml.template")
    print(f"changed portable targets: {len(changed)}")
    for item in changed[:100]:
        print(f"  {item}")
    if len(changed) > 100:
        print(f"  ... +{len(changed) - 100} more")
    if not args.confirm:
        print("dry-run only: rerun with --confirm to apply")
        return 0

    backup_root = create_unique_apply_backup_root(home)
    backup_retired_skills(retired_snapshots, backup_root, home)
    write_retired_skill_archive_manifest(retired_snapshots, backup_root, home)
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
    retire_reviewed_skills(retired_snapshots, home)
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
    push = sub.add_parser(
        "push",
        help="legacy compatibility command; always exits nonzero",
    )
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
