#!/usr/bin/env python3
"""Focused tests for portable profile synchronization."""

from __future__ import annotations

import argparse
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


sys.dont_write_bytecode = True

SYNC_PATH = Path(__file__).with_name("sync.py")
SPEC = importlib.util.spec_from_file_location("profile_sync", SYNC_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Could not load {SYNC_PATH}")
SYNC = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = SYNC
SPEC.loader.exec_module(SYNC)


RETIRED_PERSONAL_SKILLS = frozenset(
    {
        "personal-context-compression",
        "personal-context-optimization",
        "personal-context-save-restore",
        "personal-docs-sync-light",
        "personal-long-job-status",
        "personal-repo-intake",
    }
)

# Reproducible with sync.skill_tree_sha256 (sha256-path-content-v1). Sources are
# the exact Git snapshots named below plus one reviewed legacy migration archive
# snapshot. Duplicate archive copies were intentionally collapsed.
REVIEWED_RETIRED_SKILL_DIGESTS = {
    "context-save-restore": (
        # Reviewed legacy migration archive snapshot.
        "79a94c43f613d8c8fd8fb078b3fcb87aaaf4de6c1b6b0c9d357ad5a8323b429b",
    ),
    "personal-context-compression": (
        # git:6574bce5f5ede8fb4566d0451ddcf613f7fdf8a5
        "d97d4095802982300cd7a4f102a3094208d7654a5a71bfb86074a7fd86f2b3c7",
        # git:6057e9d64a633534f28b7c2e50cc907b4b1a3d4c
        "3444c65483bf122b70440741b7c113f42b249dc6dca2affb402da0c3d6cfb5cc",
    ),
    "personal-context-optimization": (
        # git:6574bce5f5ede8fb4566d0451ddcf613f7fdf8a5
        "060a7de6a56d0be89f24ad8beb0037e9f552637f9917285e646e2c4ed85f2010",
        # git:6057e9d64a633534f28b7c2e50cc907b4b1a3d4c
        "1e19d268044d4d95695385c8e73076474ed717a17093fd4de94ed12cf494f92d",
    ),
    "personal-context-save-restore": (
        # git:6057e9d64a633534f28b7c2e50cc907b4b1a3d4c
        "6ea5c7b02b56863ef1b570c5f0c5a623559388f10f3414a2af6f606b354fb420",
        # git:1958e80b1af61cc5437d95e844a95eaf55aadef8
        "a5ec4a2e6adcb614247cb5193c2328637483e44803ccb28eb89005e640c285cb",
    ),
    "personal-docs-sync-light": (
        # git:6574bce5f5ede8fb4566d0451ddcf613f7fdf8a5
        "36c32775022ea3590690ea533ed798f2732a9953f3bd12df4c0216341f58ea70",
        # git:6057e9d64a633534f28b7c2e50cc907b4b1a3d4c
        "d724aa2b0afdff7f4cb5f2a671a64328c9fcca1ec18011dde395ef0a0c54d9ea",
        # git:1958e80b1af61cc5437d95e844a95eaf55aadef8
        "52089bce134700c1a4d891afeca4e282b39bcdf642ab177e5650bae6da6bb430",
    ),
    "personal-long-job-status": (
        # git:6574bce5f5ede8fb4566d0451ddcf613f7fdf8a5
        "ce9c278b5c6967ee94d10024917a0cd5cf90943c65c28bb1a5be3bc8ab315f8a",
        # git:6057e9d64a633534f28b7c2e50cc907b4b1a3d4c
        "7e1dd49c8defb5bc4f33b61e259176e38e372f4c584865b12af9ea37fa0859d8",
    ),
    "personal-repo-intake": (
        # git:6574bce5f5ede8fb4566d0451ddcf613f7fdf8a5
        "84ec07eb713d208c98ab5497f4a5a4741a724a59b208f4acf406dc4fa05c6809",
        # git:6057e9d64a633534f28b7c2e50cc907b4b1a3d4c
        "944b137f2733088ff2aa17ea35740afe19dad3538d9a3cc4505bc714461c3153",
        # git:1958e80b1af61cc5437d95e844a95eaf55aadef8
        "9fd34a5f80de9c3994ecaa455993c4e4f92f7bb15f7a0a2712865e25ba03a298",
    ),
}

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


class PortableAgentsTests(unittest.TestCase):
    def write_agents(self, text: str) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        path = Path(temp_dir.name) / "AGENTS.md"
        path.write_text(text, encoding="utf-8")
        return path

    def test_machine_neutral_agents_are_exported_verbatim(self) -> None:
        text = """# Portable Codex Instructions

## Workflow

- Preserve user changes.

## Host-Dependent Work

- Read `~/.codex/HOST_LOCAL.md` when host facts matter.
"""
        path = self.write_agents(text)

        self.assertEqual(SYNC.portable_agents(path), text)

    def test_host_local_fact_sections_are_rejected(self) -> None:
        text = """# Portable Codex Instructions

## Workflow

- Preserve user changes.

## Host Local Overlay

- Home directory: `/root`.
"""
        path = self.write_agents(text)

        with self.assertRaisesRegex(ValueError, "Host Local Overlay"):
            SYNC.portable_agents(path)

    def test_current_host_literals_are_rejected(self) -> None:
        text = """# Portable Codex Instructions

## Host-Dependent Work

- The home directory is `/root`.
"""
        path = self.write_agents(text)

        with self.assertRaisesRegex(ValueError, "/root"):
            SYNC.portable_agents(path)

    def test_control_plane_remote_pointer_suffix_is_stripped(self) -> None:
        portable = """# Portable Codex Instructions

## Workflow

- Preserve user changes.
"""
        active = portable + """
<!-- codex-remote-doc-pointer:start -->
- Read `~/.codex/REMOTE_CONNECTION.md` before connection maintenance.
<!-- codex-remote-doc-pointer:end -->
"""
        path = self.write_agents(active)
        original = path.read_bytes()

        self.assertEqual(SYNC.portable_agents(path), portable)
        self.assertEqual(path.read_bytes(), original)

    def test_unmarked_remote_pointer_is_rejected(self) -> None:
        text = """# Portable Codex Instructions

## Host-Dependent Work

- Read `~/.codex/REMOTE_CONNECTION.md` before connection maintenance.
"""
        path = self.write_agents(text)

        with self.assertRaisesRegex(ValueError, "REMOTE_CONNECTION.md"):
            SYNC.portable_agents(path)

    def test_malformed_control_plane_overlay_is_rejected(self) -> None:
        malformed = (
            """# Portable Codex Instructions

<!-- codex-remote-doc-pointer:start -->
- Managed pointer.
""",
            """# Portable Codex Instructions

<!-- codex-remote-doc-pointer:end -->
""",
            """# Portable Codex Instructions

<!-- codex-remote-doc-pointer:start -->
- Managed pointer.
<!-- codex-remote-doc-pointer:end -->

## Workflow

- Content after the overlay.
""",
            """# Portable Codex Instructions

<!-- codex-remote-doc-pointer:start -->
- First managed pointer.
<!-- codex-remote-doc-pointer:end -->

<!-- codex-remote-doc-pointer:start -->
- Second managed pointer.
<!-- codex-remote-doc-pointer:end -->
""",
        )

        for text in malformed:
            with self.subTest(text=text):
                path = self.write_agents(text)
                with self.assertRaisesRegex(ValueError, "managed AGENTS overlay"):
                    SYNC.portable_agents(path)

    def test_portable_agents_keep_only_durable_routing_contracts(self) -> None:
        agents = (SYNC.REPO_ROOT / "rules/AGENTS.portable.md").read_text(
            encoding="utf-8"
        )
        normalized = " ".join(agents.split()).lower()

        self.assertNotIn("codex-remote-doc-pointer", normalized)
        self.assertNotIn("remote_connection.md", normalized)
        for detailed_protocol in (
            "records a cadence rationale",
            "monitoring reports use chinese event names",
            "put traceable helpers under the relevant project's `tmp/` directory",
        ):
            self.assertFalse(
                detailed_protocol in normalized,
                f"detailed protocol remains in portable AGENTS: {detailed_protocol}",
            )

        self.assertIsNotNone(
            re.search(
                r"(?:user-input|user input).{0,180}(?:no|without|never).{0,40}"
                r"(?:timer|deadline|timeout)",
                normalized,
            ),
            "portable AGENTS lacks the no-timeout user-input contract",
        )
        self.assertIsNotNone(
            re.search(
                r"silence.{0,60}(?:never|not).{0,30}(?:consent|approval)",
                normalized,
            ),
            "portable AGENTS does not say silence is never consent",
        )

        for direct_help_term in (
            "user-controlled",
            "sudo",
            "exact bounded action",
            "prolonged workaround",
        ):
            self.assertTrue(
                direct_help_term in normalized,
                f"portable AGENTS lacks direct-help term: {direct_help_term}",
            )

        for control_plane_term in (
            "scope",
            "decisions",
            "contracts",
            "intake",
            "synthesis",
            "final verdict",
            "substantive reading",
            "critical path",
        ):
            self.assertTrue(
                control_plane_term in normalized,
                f"portable AGENTS lacks control-plane term: {control_plane_term}",
            )
        self.assertIsNotNone(
            re.search(
                r"(?:no qualified executor|executor is unavailable).{0,120}"
                r"(?:wait|reclaim|local degradation)",
                normalized,
            ),
            "portable AGENTS lacks the no-executor fallback contract",
        )
        self.assertIsNotNone(
            re.search(r"(?:never|do not).{0,40}silent", normalized),
            "portable AGENTS lacks the no-silent-degradation contract",
        )

        self.assertIsNotNone(
            re.search(r"(?:1[–-]3|one to three).{0,30}sentences", normalized),
            "portable AGENTS lacks the result-aware response length",
        )
        self.assertTrue(
            "outcome-specific" in normalized,
            "portable AGENTS lacks outcome-specific next-action routing",
        )
        self.assertIsNotNone(
            re.search(r"terminal.{0,100}(?:no next action|omit|none)", normalized),
            "portable AGENTS lacks the terminal-state next-action rule",
        )
        self.assertIsNotNone(
            re.search(
                r"new authority.{0,100}exact (?:approval|permission)", normalized
            ),
            "portable AGENTS lacks the exact new-authority request rule",
        )


class RemoteConnectionContractTests(unittest.TestCase):
    def test_remote_connection_example_is_one_reviewed_static_asset(self) -> None:
        asset = SYNC.REPO_ROOT / "templates/REMOTE_CONNECTION_EXAMPLE.md"

        self.assertTrue(asset.is_file())
        self.assertFalse(asset.is_symlink())
        self.assertEqual(asset.read_text(encoding="utf-8"), SYNC.REMOTE_CONNECTION_EXAMPLE)

    def test_remote_example_is_a_generic_manual_contract_schema(self) -> None:
        example = SYNC.REMOTE_CONNECTION_EXAMPLE

        for heading in (
            "## Scope And Ownership",
            "## Stable Entrypoints",
            "## Network Routes",
            "## Health Verification",
            "## Logs And Diagnosis",
            "## Recovery And Rollback",
            "## Known Limitations",
            "## Verification Record",
        ):
            self.assertIn(heading, example)
        for boundary in (
            "current execution host only",
            "manual-only",
            "Never commit host values or credential material",
            "Unresolved placeholders are not executable",
        ):
            self.assertIn(boundary, example)
        self.assertNotIn("<WINDOWS_HOST>", example)

    def test_readme_routes_remote_contract_through_host_local_only(self) -> None:
        readme = " ".join((SYNC.REPO_ROOT / "README.md").read_text(
            encoding="utf-8"
        ).split()).lower()

        self.assertIn("legacy compatibility", readme)
        self.assertIn("host_local.md", readme)
        self.assertNotIn("可以在 active `~/.codex/agents.md` 末尾追加", readme)

    def test_export_uses_static_example_without_reading_active_remote(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "profile"
            home = base / "home"
            codex = home / ".codex"
            root.mkdir()
            for directory in (
                codex / "skills",
                codex / "hooks",
                codex / "hookify",
                home / ".agents" / "skills",
            ):
                directory.mkdir(parents=True, exist_ok=True)
            (codex / "AGENTS.md").write_text(
                "# Portable Codex Instructions\n", encoding="utf-8"
            )
            (codex / "hooks.json").write_text("{}\n", encoding="utf-8")
            # A directory makes any accidental read_text() of the active contract fail.
            (codex / "REMOTE_CONNECTION.md").mkdir()

            with mock.patch.object(SYNC, "validate_export_renamed_skill_sources"):
                with mock.patch.object(SYNC, "validate_export_custom_agent_sources"):
                    with mock.patch.object(SYNC, "export_custom_agents"):
                        SYNC.render_export_snapshot(root, home)

            exported = root / "templates/REMOTE_CONNECTION_EXAMPLE.md"
            self.assertTrue(exported.is_file())
            self.assertEqual(
                exported.read_text(encoding="utf-8"),
                SYNC.REMOTE_CONNECTION_EXAMPLE,
            )

    def test_confirmed_apply_does_not_touch_active_remote(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            remote = home / ".codex" / "REMOTE_CONNECTION.md"
            remote.parent.mkdir(parents=True)
            remote.write_text("control-plane-owned\n", encoding="utf-8")
            args = argparse.Namespace(home=str(home), confirm=True)

            with mock.patch.object(SYNC, "verify_repo"):
                with mock.patch.object(SYNC, "apply_pairs", return_value=[]):
                    with mock.patch.object(SYNC, "retired_hook_paths", return_value=[]):
                        with mock.patch.object(SYNC, "renamed_skill_paths", return_value=[]):
                            with mock.patch.object(
                                SYNC, "pending_renamed_skills", return_value=[]
                            ):
                                self.assertEqual(SYNC.cmd_apply(args), 0)

            self.assertEqual(remote.read_text(encoding="utf-8"), "control-plane-owned\n")
            archived = list(
                (home / "codex-migration-archive").glob(
                    "**/.codex/REMOTE_CONNECTION.md"
                )
            )
            self.assertEqual(archived, [])


class PythonEnvironmentPolicyTests(unittest.TestCase):
    def test_portable_agents_use_explicit_environment_decision_order(self) -> None:
        agents = (SYNC.REPO_ROOT / "rules" / "AGENTS.portable.md").read_text(
            encoding="utf-8"
        )
        normalized = " ".join(agents.split())

        self.assertNotIn(
            "Prefer non-interactive commands and `python3`",
            normalized,
        )
        self.assertIn("host-documented Codex fallback environment", normalized)
        self.assertIn("Reserve the system Python", normalized)
        self.assertIn("standing authorized", normalized)

    def test_host_template_records_the_fallback_environment_contract(self) -> None:
        template = (
            SYNC.REPO_ROOT / "templates" / "HOST_LOCAL_TEMPLATE.md"
        ).read_text(encoding="utf-8")

        self.assertEqual(SYNC.HOST_LOCAL_TEMPLATE, template)
        self.assertIn("- System Python purpose:", template)
        self.assertIn("- Codex fallback environment prefix:", template)
        self.assertIn("- Codex fallback Python version:", template)
        self.assertIn("- Codex fallback invocation:", template)
        self.assertIn("- Codex fallback package installer:", template)
        self.assertIn("- Codex fallback role and write policy:", template)


class WholeProfileContractTests(unittest.TestCase):
    def test_legacy_push_fails_closed_before_export_or_git(self) -> None:
        completed = subprocess.CompletedProcess(
            args=["git", "status", "--short"],
            returncode=0,
            stdout="",
            stderr="",
        )
        with mock.patch.object(SYNC, "export_to") as export:
            with mock.patch.object(SYNC, "verify_repo") as verify:
                with mock.patch.object(SYNC, "run", return_value=completed) as run:
                    for confirm in (False, True):
                        with self.subTest(confirm=confirm):
                            args = argparse.Namespace(
                                home="/unused",
                                confirm=confirm,
                                message="unused",
                            )
                            with self.assertRaisesRegex(
                                SystemExit,
                                r"audit.*export.*personal-risk-verification.*github:yeet",
                            ):
                                SYNC.cmd_push(args)

        export.assert_not_called()
        verify.assert_not_called()
        run.assert_not_called()

    def test_goal_mode_requires_an_explicit_request(self) -> None:
        agents = (SYNC.REPO_ROOT / "rules" / "AGENTS.portable.md").read_text(
            encoding="utf-8"
        )
        normalized = " ".join(agents.split())

        self.assertIn(
            "Use Goal mode only when the user or system explicitly requests it",
            normalized,
        )
        self.assertIn("Ordinary multi-step work uses normal plan tracking", normalized)
        self.assertNotIn(
            "Use goal mode for bounded implementation, verification, handoff",
            normalized,
        )

    def test_portable_agents_reuse_same_task_deterministic_failures(self) -> None:
        agents = (SYNC.REPO_ROOT / "rules" / "AGENTS.portable.md").read_text(
            encoding="utf-8"
        )
        normalized = " ".join(agents.split())

        self.assertIn(
            "Within one task, reuse a confirmed deterministic source or tool failure",
            normalized,
        )
        self.assertIn("helper version", normalized)

    def test_host_template_records_transient_source_failures(self) -> None:
        template = (
            SYNC.REPO_ROOT / "templates" / "HOST_LOCAL_TEMPLATE.md"
        ).read_text(encoding="utf-8")

        self.assertIn("## Known Transient Tool And Source Limitations", template)
        self.assertIn("- Observed failure and date:", template)
        self.assertIn("- Conditions that justify retry:", template)

    def test_portable_config_contains_only_the_public_docs_mcp(self) -> None:
        template = SYNC.CONFIG_TEMPLATE

        self.assertIn("[mcp_servers.openaiDeveloperDocs]", template)
        self.assertIn('url = "https://developers.openai.com/mcp"', template)
        self.assertIn("enabled = true", template)
        for forbidden in (
            "bearer_token_env_var",
            "http_headers",
            "env_http_headers",
            "auth_status",
            "oauth",
            "token",
        ):
            self.assertNotIn(forbidden, template.lower())

        self.assertIn("## Portable MCP Servers", SYNC.CONNECTORS)
        self.assertIn("templates/config.toml.template", SYNC.CONNECTORS)

    def test_portable_config_validator_rejects_auth_state(self) -> None:
        dangerous = SYNC.CONFIG_TEMPLATE + 'bearer_token_env_var = "MCP_SECRET"\n'
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "templates" / "config.toml.template"
            path.parent.mkdir(parents=True)
            path.write_text(dangerous, encoding="utf-8")
            with mock.patch.object(SYNC, "CONFIG_TEMPLATE", dangerous):
                with self.assertRaisesRegex(SystemExit, "non-portable auth state"):
                    SYNC.validate_portable_config(root)

    def test_worker_outcome_contract_is_consistent(self) -> None:
        subagent = (
            SYNC.REPO_ROOT
            / "skills/codex/personal-subagent-boundaries/SKILL.md"
        ).read_text(encoding="utf-8")
        multiline = (
            SYNC.REPO_ROOT
            / "skills/codex/personal-multiline-coordination/references/contracts.md"
        ).read_text(encoding="utf-8")
        multiline_main = (
            SYNC.REPO_ROOT
            / "skills/codex/personal-multiline-coordination/SKILL.md"
        ).read_text(encoding="utf-8")

        canonical = "accept | reject | needs-more-evidence"
        self.assertIn(canonical, subagent)
        self.assertIn("decision: accept | reject | needs-more-evidence", subagent)
        self.assertIn(canonical, multiline)
        self.assertIn("`accept`, `reject`,\n  or `needs-more-evidence`", multiline_main)
        self.assertNotIn("needs_more_evidence", subagent + multiline)
        self.assertNotIn("follow_up", subagent)
        self.assertNotRegex(
            multiline,
            r"recommended_outcome[^\n]*(?:rework|blocked)",
        )

    def test_worker_roles_keep_recommendation_and_verdict_ownership_separate(self) -> None:
        executor = (
            SYNC.REPO_ROOT / "skills/codex/personal-subagent-boundaries/SKILL.md"
        ).read_text(encoding="utf-8").lower()
        reviewer = (SYNC.REPO_ROOT / "agents/codex/reviewer.toml").read_text(
            encoding="utf-8"
        ).lower()
        monitor = (SYNC.REPO_ROOT / "agents/codex/monitor.toml").read_text(
            encoding="utf-8"
        ).lower()
        agents = " ".join(
            (SYNC.REPO_ROOT / "rules/AGENTS.portable.md")
            .read_text(encoding="utf-8")
            .split()
        ).lower()

        self.assertIn("recommended_outcome", executor)
        for observer in (reviewer, monitor):
            self.assertIn("evidence", observer)
            self.assertIsNotNone(
                re.search(r"uncertaint|unknown|ambigu", observer),
                "observer contract lacks uncertainty reporting",
            )
            self.assertNotIn("recommended outcome", observer)
            self.assertIsNotNone(
                re.search(r"(?:do not|never).{0,100}authoritative", observer),
                "observer contract lacks the authoritative-verdict boundary",
            )
        self.assertIsNotNone(
            re.search(
                r"(?:main process|coordinator).{0,180}authoritative.{0,80}verdict",
                agents,
            ),
            "portable AGENTS lacks main-process verdict ownership",
        )

    def test_ordinary_status_is_one_bounded_read_not_monitoring(self) -> None:
        agents = " ".join(
            (SYNC.REPO_ROOT / "rules/AGENTS.portable.md")
            .read_text(encoding="utf-8")
            .split()
        ).lower()

        self.assertIsNotNone(
            re.search(
                r"ordinary.{0,100}(?:status|eta).{0,120}"
                r"(?:one-shot|one bounded|single bounded).{0,80}read",
                agents,
            ),
            "portable AGENTS lacks ordinary one-shot status routing",
        )
        self.assertIsNotNone(
            re.search(
                r"(?:status|eta).{0,180}(?:not monitoring|"
                r"does not authorize monitoring|without (?:a )?monitor)",
                agents,
            ),
            "portable AGENTS does not separate one-shot status from monitoring",
        )

    def test_continuation_is_current_host_exact_task_and_packet_free(self) -> None:
        agents = " ".join(
            (SYNC.REPO_ROOT / "rules/AGENTS.portable.md")
            .read_text(encoding="utf-8")
            .split()
        ).lower()

        self.assertIsNotNone(
            re.search(
                r"current[- ]host.{0,120}exact (?:task|thread).{0,120}bounded",
                agents,
            ),
            "portable AGENTS lacks current-host exact-task continuation",
        )
        self.assertIsNotNone(
            re.search(
                r"continuation.{0,140}(?:no packet|without (?:a )?packet|"
                r"do not create.{0,30}packet)",
                agents,
            ),
            "portable AGENTS lacks packet-free bounded continuation",
        )

    def test_publish_and_branch_finish_routes_are_outcome_exclusive(self) -> None:
        branch = (
            SYNC.REPO_ROOT / "skills/codex/personal-branch-finish/SKILL.md"
        ).read_text(encoding="utf-8")
        audit = (
            SYNC.REPO_ROOT
            / "skills/codex/personal-codex-audit/references/sync-policy.md"
        ).read_text(encoding="utf-8")
        normalized = " ".join((branch + "\n" + audit).split()).lower()

        self.assertTrue("yeet" in normalized, "publish routing does not name yeet")
        self.assertIsNotNone(
            re.search(r"yeet.{0,120}(?:publish|push|draft pr)", normalized),
            "yeet is not bound to the publication outcome",
        )
        self.assertIsNotNone(
            re.search(
                r"personal-branch-finish.{0,160}(?:readiness|handoff|preservation)",
                normalized,
            ),
            "branch-finish is not bound to readiness/handoff",
        )
        self.assertIsNotNone(
            re.search(
                r"(?:outcome-exclusive|mutually exclusive|do not run both|choose one)",
                normalized,
            ),
            "publish and branch-finish routes are not outcome-exclusive",
        )
        self.assertIsNotNone(
            re.search(
                r"(?:do not|never).{0,80}(?:install|enable).{0,120}"
                r"(?:publish|publication|push|yeet)",
                normalized,
            ),
            "publication routing lacks the no-auto-install boundary",
        )

    def test_final_gate_uses_ordered_evidence_layers(self) -> None:
        verification = " ".join(
            (
                SYNC.REPO_ROOT
                / "skills/codex/personal-risk-verification/SKILL.md"
            )
            .read_text(encoding="utf-8")
            .split()
        ).lower()

        structure = verification.find("structure")
        static = verification.find("static", structure)
        semantic = verification.find("semantic scenario", static)
        runtime = verification.find("runtime", semantic)
        product_smoke = verification.find("product smoke", runtime)
        self.assertGreaterEqual(structure, 0)
        self.assertGreater(static, structure)
        self.assertGreater(semantic, static)
        self.assertIn("independent", verification[static:runtime])
        self.assertGreater(runtime, semantic)
        self.assertIn("selective", verification[semantic:product_smoke])
        self.assertGreater(product_smoke, runtime)

    def test_branch_finish_has_no_legacy_registry_contract(self) -> None:
        branch_finish = (
            SYNC.REPO_ROOT / "skills/codex/personal-branch-finish/SKILL.md"
        ).read_text(encoding="utf-8")

        self.assertNotIn("finish_candidate", branch_finish)
        self.assertNotIn("registry-prune", branch_finish)
        self.assertNotIn("registry state", branch_finish)
        self.assertIn("coordinator_decision", branch_finish)
        self.assertIn(
            "coordinator_decision: pending | pass | no-go | needs-more-evidence | blocked",
            branch_finish,
        )
        self.assertIn("line_records:", branch_finish)
        self.assertIn("integration_head_oid:", branch_finish)
        self.assertIn("source_checkpoint_oid", branch_finish)
        self.assertIn("integration record's `source_oid`", branch_finish)
        self.assertIn("handoff-only for Git mutations", branch_finish)
        self.assertNotIn("unless its line contract explicitly", branch_finish)

    def test_corrected_provenance_is_machine_neutral(self) -> None:
        code_docs = (
            SYNC.REPO_ROOT
            / "skills/codex/personal-code-documentation/references/source-notes.md"
        ).read_text(encoding="utf-8")
        subagent = (
            SYNC.REPO_ROOT
            / "skills/codex/personal-subagent-boundaries/references/source-notes.md"
        ).read_text(encoding="utf-8")

        self.assertIn("901fb94c0fb9ffc8cb2d8275d99622475f77f401", code_docs)
        self.assertIn("upstream-derived", code_docs)
        self.assertNotIn("ChrisWiles", code_docs)
        self.assertIn("Classification: hybrid", subagent)
        self.assertNotIn("/root/", code_docs)
        self.assertNotIn("668a5bcf22a71948d2375caf4c2b5a7d2eb09d2c", code_docs)

    def test_final_source_provenance_is_reproducible(self) -> None:
        skill_root = SYNC.REPO_ROOT / "skills" / "codex"
        multiline = (
            skill_root
            / "personal-multiline-coordination/references/source-notes.md"
        ).read_text(encoding="utf-8")
        brainstorms = (
            skill_root / "personal-brainstorms/references/source-notes.md"
        ).read_text(encoding="utf-8")
        hygiene = (
            skill_root / "personal-skill-hygiene/references/source-notes.md"
        ).read_text(encoding="utf-8")
        hook_rules = (
            skill_root / "personal-codex-hook-rules/references/source-notes.md"
        ).read_text(encoding="utf-8")

        self.assertIn("5ad41a7157352724ac51ad24f87949e3e23cc694", multiline)
        self.assertIn("`method: manual`", multiline)
        self.assertIn("`preservation_ref`", multiline)
        for notes in (brainstorms, hygiene):
            self.assertIn("profile-kit revision", notes)
            self.assertRegex(notes, r"SHA-256 `[0-9a-f]{64}`")
            self.assertIn("not exported", notes)
        self.assertIn("hooks/scripts/hookify_codex_runner.py", hook_rules)
        self.assertIn("hooks/scripts/test_hookify_codex_runner.py", hook_rules)
        self.assertIn("Git blob", hook_rules)

    def test_audit_skill_records_change_triggered_compatibility(self) -> None:
        policy = (
            SYNC.REPO_ROOT
            / "skills/codex/personal-codex-audit/references/compatibility-policy.md"
        ).read_text(encoding="utf-8")

        self.assertIn("0.144.1", policy)
        self.assertIn("patch", policy.lower())
        self.assertIn("contract", policy.lower())
        self.assertIn("focused", policy.lower())

    def test_monitor_observer_never_executes_contingencies(self) -> None:
        agents = (
            SYNC.REPO_ROOT / "rules" / "AGENTS.portable.md"
        ).read_text(encoding="utf-8")
        subagent_monitoring = (
            SYNC.REPO_ROOT
            / "skills/codex/personal-subagent-boundaries/references/monitoring.md"
        ).read_text(encoding="utf-8")
        multiline = (
            SYNC.REPO_ROOT
            / "skills/codex/personal-multiline-coordination/SKILL.md"
        ).read_text(encoding="utf-8")
        grants = (
            SYNC.REPO_ROOT
            / "skills/codex/personal-multiline-coordination/references/resource-grants.md"
        ).read_text(encoding="utf-8")

        self.assertIn("must not stop, repair, restart", agents)
        self.assertIn(
            "does not authorize the monitoring observer to execute them",
            subagent_monitoring,
        )
        self.assertNotIn("unless an exact contingency was preauthorized", multiline)
        self.assertNotIn("It may execute an exact contingency", grants)
        normalized = " ".join((multiline + "\n" + grants).split()).lower()
        self.assertIn("even when an exact contingency was preauthorized", normalized)
        self.assertRegex(
            normalized,
            r"supervisor or coordinator .{0,80}(?:execute|act)",
        )

    def test_portable_agents_route_owned_protocols_without_losing_fallbacks(self) -> None:
        skill_root = SYNC.REPO_ROOT / "skills" / "codex"
        agents = " ".join(
            (SYNC.REPO_ROOT / "rules/AGENTS.portable.md")
            .read_text(encoding="utf-8")
            .split()
        ).lower()
        subagent = " ".join(
            (skill_root / "personal-subagent-boundaries/SKILL.md")
            .read_text(encoding="utf-8")
            .split()
        ).lower()
        monitoring = " ".join(
            (skill_root / "personal-subagent-boundaries/references/monitoring.md")
            .read_text(encoding="utf-8")
            .split()
        ).lower()
        risk = " ".join(
            (skill_root / "personal-risk-verification/SKILL.md")
            .read_text(encoding="utf-8")
            .split()
        ).lower()

        for fallback in (
            "authoritative task verdict",
            "does not authorize monitoring",
            "must not stop, repair, restart",
            "`supported` verdict",
        ):
            with self.subTest(global_fallback=fallback):
                self.assertIn(fallback, agents)
        for owner in (
            "personal-subagent-boundaries",
            "personal-multiline-coordination",
            "personal-risk-verification",
        ):
            with self.subTest(global_route=owner):
                self.assertIn(owner, agents)

        for moved_detail in (
            "recommended_outcome",
            "configured_unverified",
            "product-confirmed",
            "exactly one runtime-verified read-only monitor",
        ):
            with self.subTest(global_exclusion=moved_detail):
                self.assertNotIn(moved_detail, agents)

        for delegation_contract in (
            "recommended_outcome",
            "wait for or reclaim",
            "explicit local degradation",
            "sole recurring read-only observer",
            "`已配置但未验证`",
            "`仅提示约束`",
            "`运行时已验证`",
        ):
            with self.subTest(delegation_owner=delegation_contract):
                self.assertIn(delegation_contract, subagent)
        self.assertIn("cadence rationale", monitoring)
        for verification_contract in (
            "structure_static",
            "semantic_scenarios",
            "runtime_product_smoke",
        ):
            with self.subTest(verification_owner=verification_contract):
                self.assertIn(verification_contract, risk)
        for user_facing_state in (
            "`已配置`",
            "`已配置但未验证`",
            "`仅提示约束`",
            "`运行时已验证`",
            "`产品内已确认`",
            "`未运行`",
            "`未知`",
        ):
            with self.subTest(verification_state=user_facing_state):
                self.assertIn(user_facing_state, risk)

    def test_monitor_cadence_keeps_dynamic_primary_with_numeric_fallback(self) -> None:
        monitoring = (
            SYNC.REPO_ROOT
            / "skills/codex/personal-subagent-boundaries/references/monitoring.md"
        ).read_text(encoding="utf-8")

        self.assertIn("Do not encode one global numerical interval", monitoring)
        self.assertIn("non-binding sanity checks", monitoring)
        for cadence in (
            "30-60 minutes",
            "45-60 minutes",
            "90-120 minutes",
            "2-4 hours",
        ):
            self.assertIn(cadence, monitoring)
        self.assertIn(
            "job-specific signals justify a different cadence",
            monitoring,
        )

    def test_profile_sync_allows_confirmed_public_or_private_remote(self) -> None:
        policy = (
            SYNC.REPO_ROOT
            / "skills/codex/personal-codex-audit/references/sync-policy.md"
        ).read_text(encoding="utf-8")

        self.assertIn("Visibility may be public or private", policy)
        self.assertIn(
            "Do not change repository visibility without separate explicit authority",
            policy,
        )
        self.assertIn("authorization to publish the isolated diff", policy)
        self.assertNotIn("Confirmed private remote", policy)

    def test_profile_sync_has_a_routine_directional_fast_path(self) -> None:
        skill_root = (
            SYNC.REPO_ROOT / "skills/codex/personal-codex-audit"
        )
        skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        policy = (skill_root / "references/sync-policy.md").read_text(
            encoding="utf-8"
        )
        combined = " ".join((skill + "\n" + policy).split()).lower()

        self.assertIn("routine directional sync", combined)
        self.assertIn("do not run the whole-profile collector", combined)
        self.assertIn("host connection contract", combined)
        self.assertIn("one verification pass per unchanged state", combined)
        self.assertIn("resume at the first incomplete stage", combined)
        self.assertIn("reuse still-valid evidence", combined)
        self.assertIn("pythondontwritebytecode=1", combined)
        self.assertIn("__pycache__", combined)
        self.assertIn("does not reopen semantic review", combined)
        self.assertIn("visible checkpoint after preflight", combined)
        self.assertIn("report the blocker before another attempt", combined)
        self.assertIn(
            "do not call `sync.py push --confirm` after a completed export",
            combined,
        )

    def test_legacy_push_policy_is_fail_closed_compatibility_only(self) -> None:
        audit_root = SYNC.REPO_ROOT / "skills/codex/personal-codex-audit"
        policy = (audit_root / "references/sync-policy.md").read_text(
            encoding="utf-8"
        )
        source_notes = (audit_root / "references/source-notes.md").read_text(
            encoding="utf-8"
        )
        normalized = " ".join((policy + "\n" + source_notes).split()).lower()

        self.assertIn("fail-closed compatibility only", normalized)
        self.assertIn(
            "before export, status inspection, staging, commit, or push",
            normalized,
        )
        self.assertIn("personal-risk-verification", normalized)
        self.assertIn("github:yeet", normalized)
        self.assertNotIn("that script untouched", normalized)

    def test_directional_sync_intent_authorizes_the_bounded_handoff_chain(self) -> None:
        skill_root = (
            SYNC.REPO_ROOT / "skills/codex/personal-codex-audit"
        )
        skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        policy = (skill_root / "references/sync-policy.md").read_text(
            encoding="utf-8"
        )
        metadata = (skill_root / "agents/openai.yaml").read_text(
            encoding="utf-8"
        )
        combined = " ".join((skill + "\n" + policy).split()).lower()

        self.assertIn(
            "audit, export, final local verification, and a bounded publication handoff",
            combined,
        )
        self.assertIn("personal-risk-verification: supported", combined)
        self.assertIn("github:yeet", combined)
        self.assertIn(
            "exclusively performs branch setup, staging, commit, push, and draft pull-request creation",
            combined,
        )
        self.assertIn("fetch, non-conflicting integration, and confirmed apply", combined)
        self.assertIn("do not ask again at each internal stage", combined)
        normalized_metadata = " ".join(metadata.split()).lower()
        self.assertIn("supported candidate", normalized_metadata)
        self.assertIn("hand the full commit/push/pr flow to $github:yeet", normalized_metadata)

    def test_outbound_sync_hands_commit_and_publication_to_yeet(self) -> None:
        skill_root = (
            SYNC.REPO_ROOT / "skills/codex/personal-codex-audit"
        )
        skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        policy = (skill_root / "references/sync-policy.md").read_text(
            encoding="utf-8"
        )
        combined = " ".join((skill + "\n" + policy).split()).lower()

        self.assertIn("profile executor must not stage, commit, or push", combined)
        self.assertIn("hand the complete publication flow to `github:yeet`", combined)
        self.assertIn(
            "owns branch setup, staging, commit, push, and draft pull-request creation",
            combined,
        )
        self.assertIn("dependency_install_authorized: false", combined)
        self.assertIn(
            "missing publication helpers do not authorize installation",
            combined,
        )

    def test_profile_sync_escalates_material_risk_instead_of_all_syncs(self) -> None:
        policy = (
            SYNC.REPO_ROOT
            / "skills/codex/personal-codex-audit/references/sync-policy.md"
        ).read_text(encoding="utf-8")
        normalized = " ".join(policy.split()).lower()

        for trigger in (
            "new, removed, or renamed managed asset",
            "unrelated or ambiguous worktree state",
            "merge conflict",
            "repository visibility change",
            "sync tooling",
        ):
            self.assertIn(trigger, normalized)
        self.assertIn("existing admitted portable targets", normalized)

    def test_readme_uses_the_verified_yeet_outbound_publish_route(self) -> None:
        readme = (SYNC.REPO_ROOT / "README.md").read_text(encoding="utf-8")
        normalized = " ".join(readme.split()).lower()

        self.assertFalse(
            "python3 scripts/sync.py push --confirm" in normalized,
            "README still recommends the all-in-one push command",
        )
        for step in (
            "audit",
            "export",
            "inspect",
            "personal-risk-verification",
            "github:yeet",
            "draft pull request",
        ):
            self.assertTrue(step in normalized, f"README lacks outbound step: {step}")
        for forbidden in ("exact-path commit", "git commit", "git push"):
            self.assertNotIn(
                forbidden,
                normalized,
                f"README still recommends direct publication step: {forbidden}",
            )

    def test_manual_only_skill_routes_require_explicit_invocation(self) -> None:
        skill_root = SYNC.REPO_ROOT / "skills" / "codex"
        metadata_paths = (
            skill_root / "personal-grilling/agents/openai.yaml",
            skill_root / "personal-triad-discussion/agents/openai.yaml",
            skill_root / "personal-prompt-optimizer/agents/openai.yaml",
        )
        multiline_routing = (
            skill_root / "personal-multiline-coordination/references/routing.md"
        ).read_text(encoding="utf-8")
        worktree_integration = (
            skill_root
            / "personal-multiline-coordination/references/worktree-integration.md"
        ).read_text(encoding="utf-8")
        debugging = (
            skill_root / "personal-evidence-debugging/SKILL.md"
        ).read_text(encoding="utf-8")
        branch_finish = (
            skill_root / "personal-branch-finish/SKILL.md"
        ).read_text(encoding="utf-8")
        output_explainer = (
            skill_root / "personal-project-output-explainer/SKILL.md"
        ).read_text(encoding="utf-8")

        for metadata_path in metadata_paths:
            with self.subTest(metadata=metadata_path):
                self.assertTrue(
                    metadata_path.is_file(),
                    f"missing manual-only metadata: {metadata_path}",
                )
                metadata = metadata_path.read_text(encoding="utf-8")
                self.assertIn("allow_implicit_invocation: false", metadata)
        self.assertIn("$personal-grilling", multiline_routing)
        self.assertIn("$personal-grilling", worktree_integration)
        self.assertIn("$personal-triad-discussion", output_explainer)
        self.assertFalse(
            "personal-long-job-status"
            in multiline_routing + debugging + branch_finish + output_explainer,
            "live routing still references retired personal-long-job-status",
        )
        self.assertIn("ordinary", debugging.lower())
        self.assertIn("ordinary", branch_finish.lower())

    def test_grilling_requires_sourced_three_pass_coverage_closure(self) -> None:
        skill_root = SYNC.REPO_ROOT / "skills" / "codex" / "personal-grilling"
        skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        coverage_path = skill_root / "references" / "coverage-model.md"
        normalized = " ".join(skill.split()).lower()

        self.assertNotIn("fewest questions needed", normalized)
        self.assertTrue(coverage_path.is_file())
        coverage = " ".join(coverage_path.read_text(encoding="utf-8").split()).lower()
        for phrase in (
            "coverage pass",
            "consistency pass",
            "adversarial pass",
            "explicit coverage confirmation",
        ):
            self.assertIn(phrase, normalized)
        for phrase in (
            "universal core",
            "task-type packs",
            "source_type",
            "risk_disposition",
            "bootstrap",
            "tombstone",
            "concurrent writers",
            "prediction-time information boundary",
            "pseudoreplication",
            "evaluation-selection boundary",
            "multiplicity",
        ):
            with self.subTest(coverage_phrase=phrase):
                self.assertIn(phrase, coverage)
        self.assertIn("proportionate ledger", normalized)

    def test_grilling_guides_open_questions_and_recovers_from_uncertainty(self) -> None:
        skill_root = SYNC.REPO_ROOT / "skills" / "codex" / "personal-grilling"
        skill = " ".join(
            (skill_root / "SKILL.md").read_text(encoding="utf-8").split()
        ).lower()
        discipline = " ".join(
            (skill_root / "references/answer-discipline.md")
            .read_text(encoding="utf-8")
            .split()
        ).lower()

        for phrase in (
            "guided open-ended question",
            "non-exhaustive reference angles",
            "minimum-effort response",
            "uncertainty or asks for reference",
        ):
            with self.subTest(skill_phrase=phrase):
                self.assertIn(phrase, skill)
        self.assertIn("do not ask another open question by default", discipline)
        self.assertIn("## worked examples", discipline)
        for example in (
            "guided opening without solution anchoring",
            "uncertainty switches to concrete help",
            "free-form expertise remains valid",
        ):
            with self.subTest(example=example):
                self.assertIn(example, discipline)

    def test_brainstorms_yields_to_grilling_coverage_when_paired(self) -> None:
        brainstorms = (
            SYNC.REPO_ROOT / "skills/codex/personal-brainstorms/SKILL.md"
        ).read_text(encoding="utf-8")
        normalized = " ".join(brainstorms.split()).lower()

        self.assertIn("grilling coverage gate", normalized)
        self.assertIn("does not apply while `personal-grilling` is active", normalized)
        self.assertIn("reopen", normalized)

    def test_thread_closeout_requires_an_external_controller(self) -> None:
        skill_root = SYNC.REPO_ROOT / "skills" / "codex"
        closeout = (
            skill_root / "personal-thread-closeout/SKILL.md"
        ).read_text(encoding="utf-8")
        metadata = (
            skill_root / "personal-thread-closeout/agents/openai.yaml"
        ).read_text(encoding="utf-8")
        notes = (
            skill_root / "personal-thread-closeout/references/source-notes.md"
        ).read_text(encoding="utf-8")
        normalized = " ".join(closeout.split()).lower()

        self.assertIn("allow_implicit_invocation: false", metadata)
        self.assertIn("target thread", metadata.lower())
        self.assertIn("explicit target thread", normalized)
        self.assertIn("must differ from the controller", normalized)
        self.assertIn("never omit the target thread id", normalized)
        self.assertNotIn("archiving the calling thread", normalized)
        self.assertNotIn("omit `threadid`", normalized)
        self.assertIn("interrupted", notes)
        self.assertIn("external controller", notes.lower())

    def test_thread_closeout_manual_batch_contract_is_complete(self) -> None:
        skill_root = (
            SYNC.REPO_ROOT / "skills" / "codex" / "personal-thread-closeout"
        )
        skill = " ".join(
            (skill_root / "SKILL.md").read_text(encoding="utf-8").split()
        ).lower()
        metadata = " ".join(
            (skill_root / "agents/openai.yaml")
            .read_text(encoding="utf-8")
            .split()
        ).lower()
        batch = " ".join(
            (skill_root / "references/target-selection-and-batch.md")
            .read_text(encoding="utf-8")
            .split()
        ).lower()

        self.assertIn("allow_implicit_invocation: false", metadata)
        self.assertIn(
            "ordered list of exact target references or ids",
            skill,
        )
        self.assertIn(
            "preserve input order and deduplicate after exact resolution",
            batch,
        )
        self.assertIn("first occurrence supplies order", batch)
        self.assertIn(
            "discard non-current-host records before their content enters context",
            batch,
        )
        self.assertIn(
            "cutoff = start of current local day - 15 calendar days",
            batch,
        )
        self.assertIn("eligible when last_activity < cutoff", batch)
        self.assertIn("a task at the cutoff is not eligible", batch)
        self.assertIn(
            "sort ascending by last activity with exact id as deterministic tie-breaker",
            batch,
        )
        self.assertIn("select the first 10", batch)
        self.assertIn("exclude the controller", batch)
        self.assertIn("target-local", batch)
        self.assertIn("record it and continue", batch)
        self.assertIn("shared infrastructure", batch)
        self.assertIn("stop later mutation", batch)
        self.assertIn("archive is the last mutation for that target", batch)
        self.assertIn("do not defer all archive calls to the end of the batch", batch)

    def test_cross_session_coordination_does_not_imply_file_planning(self) -> None:
        skill_root = SYNC.REPO_ROOT / "skills" / "codex"
        multiline = (
            skill_root / "personal-multiline-coordination/SKILL.md"
        ).read_text(encoding="utf-8")
        routing = (
            skill_root / "personal-multiline-coordination/references/routing.md"
        ).read_text(encoding="utf-8")
        combined = " ".join((multiline + "\n" + routing).split()).lower()

        self.assertNotIn("for cross-session work, promote", combined)
        self.assertNotIn("when a coordination run must cross sessions, ask", combined)
        self.assertRegex(
            combined,
            r"(?:alone does not|does not by itself) authorize",
        )
        self.assertIn("explicit file-backed planning", combined)

    def test_output_explainer_routes_require_comprehension_intent(self) -> None:
        skill_root = SYNC.REPO_ROOT / "skills" / "codex"
        files = (
            skill_root / "personal-branch-finish/SKILL.md",
            skill_root / "personal-code-documentation/SKILL.md",
            skill_root / "personal-triad-discussion/SKILL.md",
        )
        combined = "\n".join(path.read_text(encoding="utf-8") for path in files)
        normalized = " ".join(combined.split()).lower()

        self.assertNotIn("ordinary completion or project explanations", normalized)
        self.assertNotIn(
            "explains project status, evidence, decisions, and next steps",
            normalized,
        )
        self.assertNotIn("reader-oriented status and decision explanations", normalized)
        self.assertNotIn("separate audience-facing report", normalized)
        for path in files:
            text = path.read_text(encoding="utf-8").lower()
            self.assertTrue("compreh" in text or "decode" in text, path)

    def test_portable_mcp_enablement_is_documented_as_normalization(self) -> None:
        template = SYNC.CONFIG_TEMPLATE.lower()
        connectors = SYNC.CONNECTORS.lower()

        self.assertIn("intentional portable", template)
        self.assertIn("normative", connectors)
        self.assertIn("enabled = true", template)

    def test_new_skills_route_through_the_admission_contract(self) -> None:
        agents = (
            SYNC.REPO_ROOT / "rules/AGENTS.portable.md"
        ).read_text(encoding="utf-8")
        hygiene = (
            SYNC.REPO_ROOT / "skills/codex/personal-skill-hygiene/SKILL.md"
        ).read_text(encoding="utf-8")
        normalized_agents = " ".join(agents.split()).lower()
        normalized_hygiene = " ".join(hygiene.split()).lower()

        self.assertIn(
            "before activating a newly created or externally installed skill, "
            "apply the skill-admission contract owned by "
            "`personal-skill-hygiene`",
            normalized_agents,
        )
        self.assertIn("skill-admission.md", normalized_hygiene)
        self.assertIn("provenance-contract.md", normalized_hygiene)
        for detail in (
            "source_classification",
            "primary_sources",
            "admission_status",
            "portability_disposition",
            "identity -> provenance",
        ):
            self.assertNotIn(detail, normalized_agents)

    def test_profile_audit_tracks_skill_admission_dimensions(self) -> None:
        skill_root = SYNC.REPO_ROOT / "skills/codex"
        audit = (
            skill_root / "personal-codex-audit/SKILL.md"
        ).read_text(encoding="utf-8")
        state = (
            skill_root
            / "personal-codex-audit/references/profile-state-model.md"
        ).read_text(encoding="utf-8")
        source_policy = (
            skill_root / "personal-codex-audit/references/source-policy.md"
        ).read_text(encoding="utf-8")
        combined = " ".join((audit + state + source_policy).split()).lower()

        for dimension in (
            "source_classification",
            "provenance_status",
            "admission_status",
            "portability_disposition",
        ):
            self.assertIn(dimension, combined)
        self.assertIn("third_party_skills.lock.json", combined)

    def test_generated_docs_describe_skill_admission_validation(self) -> None:
        install = (SYNC.REPO_ROOT / "INSTALL.md").read_text(encoding="utf-8")
        manifest = (
            SYNC.REPO_ROOT / "MIGRATION_MANIFEST.md"
        ).read_text(encoding="utf-8")
        readme = (SYNC.REPO_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertEqual(install, SYNC.INSTALL)
        self.assertEqual(manifest, SYNC.migration_manifest())
        for document in (install, manifest, readme):
            normalized = document.lower()
            self.assertIn("third_party_skills.lock.json", normalized)
            self.assertIn("managed", normalized)
            self.assertIn("6,500", normalized)


class PortableSkillTests(unittest.TestCase):
    def test_every_personal_skill_has_source_notes(self) -> None:
        root = SYNC.REPO_ROOT / "skills" / "codex"
        personal = sorted(path for path in root.glob("personal-*") if path.is_dir())

        self.assertEqual(len(personal), 21)
        self.assertIn("personal-thread-closeout", {skill.name for skill in personal})
        for skill in personal:
            with self.subTest(skill=skill.name):
                source = skill / "references" / "source-notes.md"
                self.assertTrue(source.is_file(), source)
                self.assertIn("source", source.read_text(encoding="utf-8").lower())

    def test_prompt_optimizer_contract_is_manual_and_bounded(self) -> None:
        skill_root = (
            SYNC.REPO_ROOT / "skills" / "codex" / "personal-prompt-optimizer"
        )
        self.assertTrue(
            skill_root.is_dir(),
            f"missing formal skill directory: {skill_root}",
        )

        reference_paths = tuple(
            skill_root / "references" / name
            for name in (
                "repair-patterns.md",
                "handoff-patterns.md",
                "evaluation.md",
                "source-notes.md",
            )
        )
        required_paths = (
            skill_root / "SKILL.md",
            skill_root / "agents" / "openai.yaml",
            *reference_paths,
        )
        for path in required_paths:
            with self.subTest(path=path):
                self.assertTrue(path.is_file(), f"missing prompt optimizer resource: {path}")

        skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        metadata = (skill_root / "agents" / "openai.yaml").read_text(
            encoding="utf-8"
        )
        references = "\n".join(
            path.read_text(encoding="utf-8") for path in reference_paths
        )
        source_notes = (
            skill_root / "references" / "source-notes.md"
        ).read_text(encoding="utf-8")
        frontmatter = SYNC.parse_frontmatter(skill)
        description = frontmatter["description"].lower()
        normalized_skill = " ".join(skill.split()).lower()
        combined = " ".join((skill + "\n" + references).split()).lower()
        emit_section = normalized_skill.partition("## emit the result")[2].partition(
            "## apply owner routing"
        )[0]

        self.assertEqual(frontmatter["name"], "personal-prompt-optimizer")
        self.assertIn("$personal-prompt-optimizer", description)
        self.assertRegex(description, r"(?:use|invoke).{0,80}explicit")
        self.assertIn("allow_implicit_invocation: false", metadata)
        self.assertNotIn("allow_implicit_invocation: true", metadata)
        for mode in ("repair mode", "handoff mode"):
            self.assertIn(mode, combined)
        for evidence_level in ("static_only", "trace_based", "runtime_tested"):
            self.assertIn(evidence_level, combined)
        self.assertRegex(combined, r"exactly one.{0,120}canonical")
        self.assertRegex(combined, r"prompt alone.{0,120}```text")
        self.assertRegex(
            combined,
            r"read-only.{0,160}(?:do not|never).{0,80}write files",
        )
        self.assertRegex(combined, r"do not.{0,100}memory.{0,40}memo.{0,40}state")
        for owner in (
            "personal-brainstorms",
            "personal-grilling",
            "personal-writing-polish",
            "personal-triad-discussion",
            "personal-project-output-explainer",
            "personal-subagent-boundaries",
            "openai-docs",
            "skill-creator",
        ):
            self.assertIn(owner, combined)
        self.assertIn("owner routing", combined)

        for manual_owner in (
            "$personal-grilling",
            "$personal-triad-discussion",
            "$personal-project-output-explainer",
        ):
            with self.subTest(manual_owner=manual_owner):
                self.assertIn(manual_owner, combined)
                self.assertRegex(
                    combined,
                    rf"(?:do not|never|cannot).{{0,100}}{re.escape(manual_owner)}"
                    r".{0,120}implicit",
                )
        self.assertRegex(
            combined,
            r"(?:tell|prompt|ask).{0,80}user.{0,100}explicit"
            r".{0,80}(?:separate|another)",
        )

        self.assertRegex(
            normalized_skill,
            r"(?:before|prior to).{0,80}(?:selecting|choosing).{0,40}mode",
        )
        self.assertRegex(
            normalized_skill,
            r"neither.{0,100}supplied prompt.{0,160}bounded side-task discussion"
            r".{0,160}(?:do not|must not|never).{0,80}(?:handoff|generate|invent)",
        )
        for gate_signal in ("outcome or target", "current authorization boundary"):
            self.assertIn(gate_signal, normalized_skill)
        self.assertRegex(
            normalized_skill,
            r"ask (?:at most )?one.{0,80}materially changing.{0,80}targeted question",
        )
        self.assertRegex(
            normalized_skill,
            r"(?:forbids|prohibits|declines).{0,80}questions?"
            r".{0,160}(?:explicit )?placeholders",
        )
        self.assertRegex(
            normalized_skill,
            r"(?:list|state).{0,80}missing.{0,80}(?:outside|before|after)"
            r".{0,40}(?:prompt )?block",
        )
        self.assertRegex(normalized_skill, r"(?:do not|never).{0,40}guess")

        self.assertRegex(emit_section, r"(?:default|normally).{0,80}```text")
        self.assertRegex(
            emit_section,
            r"(?:more backticks|longer.{0,40}fence).{0,120}"
            r"(?:longest|maximum).{0,80}backtick run",
        )
        self.assertRegex(
            emit_section,
            r"(?:preserve|keep).{0,80}(?:inner|internal)"
            r".{0,80}(?:literal|unchanged)",
        )

        self.assertNotIn("briefly state only the necessary rationale", emit_section)
        self.assertIn("evaluation.md", emit_section)
        for report_field in (
            "target/surface",
            "case/settings/tools/acceptance boundary",
            "observed result",
            "remaining uncertainty",
        ):
            self.assertIn(report_field, emit_section)
        self.assertRegex(
            emit_section,
            r"(?:only|include).{0,80}applicable.{0,80}(?:known|available)",
        )
        self.assertRegex(emit_section, r"(?:mark|label|state).{0,40}unknown")

        self.assertRegex(
            source_notes,
            r"(?m)^- skill: personal-prompt-optimizer$",
        )
        self.assertRegex(
            source_notes,
            r"(?m)^- checked(?:_at)?: 2026-07-16$",
        )

        self.assertIn("any material unresolved branch", combined)
        self.assertIn("decision owner", combined)
        self.assertRegex(
            combined,
            r"each branch.{0,80}(?:execution )?consequence",
        )
        self.assertIn("stop/ask condition", combined)
        for prohibited_source in (
            "adjacent authority",
            "similar behavior",
            "unapproved conservative fallback",
        ):
            self.assertIn(prohibited_source, combined)
        self.assertRegex(
            combined,
            r"(?:do not|never).{0,100}(?:infer|derive|grant|authorize)"
            r".{0,100}unconfirmed branch",
        )

    def test_prompt_optimizer_has_a_complete_admission_record(self) -> None:
        source_notes = (
            SYNC.REPO_ROOT
            / "skills/codex/personal-prompt-optimizer/references/source-notes.md"
        ).read_text(encoding="utf-8")
        normalized = " ".join(source_notes.split()).lower()

        self.assertIn("skill_admission:", source_notes)
        for field, value in (
            ("skill", "personal-prompt-optimizer"),
            ("acquisition_mode", "created"),
            ("source_classification", "hybrid"),
            ("provenance_status", "complete"),
            ("admission_status", "admitted"),
            ("portability_disposition", "internalized"),
        ):
            with self.subTest(field=field):
                self.assertRegex(
                    source_notes,
                    rf"(?m)^  {field}: {re.escape(value)}$",
                )
        for field in (
            "safety_review",
            "trigger_review",
            "validation",
            "update_owner",
            "update_rule",
            "rollback_basis",
            "unknowns",
        ):
            self.assertRegex(source_notes, rf"(?m)^  {field}:")
        for evidence in (
            "quick_validate",
            "profile tests",
            "zero drift",
            "product-confirmed",
            "fresh side-conversation",
            "explicit discovery",
            "manual handoff mode",
            "downstream prompt effectiveness is not runtime_tested",
            "negative no-invocation product smoke was not rerun",
        ):
            self.assertIn(evidence, normalized)
        self.assertNotIn("/root/", source_notes)

    def test_managed_profile_rejects_descendant_symbolic_links(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "profile"
            outside = Path(tmp) / "outside.txt"
            link = root / "skills" / "codex" / "sample" / "external"
            outside.write_text("outside\n", encoding="utf-8")
            link.parent.mkdir(parents=True)
            link.symlink_to(outside)

            with self.assertRaisesRegex(SystemExit, "symbolic links"):
                SYNC.validate_managed_snapshot_paths(root)

    def test_renamed_hook_skill_replaces_legacy_allowlist_entry(self) -> None:
        self.assertTrue(SYNC.is_portable_codex_skill("personal-codex-hook-rules"))
        self.assertFalse(SYNC.is_portable_codex_skill("hookify-writing-rules"))

    def test_retired_context_skill_identities_are_not_portable(self) -> None:
        self.assertFalse(SYNC.is_portable_codex_skill("personal-context-save-restore"))
        self.assertFalse(SYNC.is_portable_codex_skill("context-save-restore"))
        self.assertIn("context-save-restore", SYNC.RETIRED_CODEX_SKILLS)

    def test_renamed_code_simplifier_replaces_legacy_allowlist_entry(self) -> None:
        self.assertTrue(SYNC.is_portable_codex_skill("personal-code-simplifier"))
        self.assertFalse(SYNC.is_portable_codex_skill("code-simplifier"))

    def test_renamed_code_documentation_replaces_legacy_allowlist_entry(self) -> None:
        self.assertTrue(SYNC.is_portable_codex_skill("personal-code-documentation"))
        self.assertFalse(SYNC.is_portable_codex_skill("code-documentation"))

    def test_personal_skill_ui_metadata_is_validated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / "skills" / "codex" / "personal-sample"
            (skill / "agents").mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\nname: personal-sample\n"
                "description: Use for one focused sample workflow.\n---\n",
                encoding="utf-8",
            )
            (skill / "agents" / "openai.yaml").write_text(
                "display_name: Sample\n"
                "short_description: This flat legacy metadata must fail validation\n"
                "default_prompt: Use sample.\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(SystemExit, "openai.yaml"):
                SYNC.validate_skills(root)

    def test_personal_skill_resource_links_are_validated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / "skills" / "codex" / "personal-sample"
            (skill / "agents").mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\nname: personal-sample\n"
                "description: Use for one focused sample workflow.\n---\n\n"
                "Read [missing](references/missing.md).\n",
                encoding="utf-8",
            )
            (skill / "agents" / "openai.yaml").write_text(
                "interface:\n"
                "  display_name: \"Personal Sample\"\n"
                "  short_description: \"Validate one focused sample workflow\"\n"
                "  default_prompt: \"Use $personal-sample for this sample.\"\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(SystemExit, "missing skill resource"):
                SYNC.validate_skills(root)

    def test_personal_skill_requires_source_notes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / "skills" / "codex" / "personal-sample"
            (skill / "agents").mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\nname: personal-sample\n"
                "description: Use for one focused sample workflow.\n---\n",
                encoding="utf-8",
            )
            (skill / "agents" / "openai.yaml").write_text(
                "interface:\n"
                "  display_name: \"Personal Sample\"\n"
                "  short_description: \"Validate one focused sample workflow\"\n"
                "  default_prompt: \"Use $personal-sample for this sample.\"\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(SystemExit, "source-notes"):
                SYNC.validate_skills(root)

    def test_personal_catalog_description_budget_is_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / "skills" / "codex" / "personal-sample"
            (skill / "agents").mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\nname: personal-sample\n"
                "description: Use for one focused sample workflow.\n---\n",
                encoding="utf-8",
            )
            (skill / "agents" / "openai.yaml").write_text(
                "interface:\n"
                "  display_name: \"Personal Sample\"\n"
                "  short_description: \"Validate one focused sample workflow\"\n"
                "  default_prompt: \"Use $personal-sample for this sample.\"\n",
                encoding="utf-8",
            )
            (skill / "references").mkdir()
            (skill / "references" / "source-notes.md").write_text(
                "# Source Notes\n",
                encoding="utf-8",
            )

            with mock.patch.object(
                SYNC,
                "PERSONAL_SKILL_DESCRIPTION_BUDGET",
                8,
                create=True,
            ):
                with self.assertRaisesRegex(SystemExit, "description budget"):
                    SYNC.validate_skills(root)

    def test_managed_catalog_budget_includes_non_personal_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            vendor = root / "skills" / "codex" / "vendor-sample"
            agent = root / "skills" / "agents" / "agent-sample"
            vendor.mkdir(parents=True)
            agent.mkdir(parents=True)
            (vendor / "SKILL.md").write_text(
                "---\nname: vendor-sample\n"
                "description: This vendor description consumes catalog context.\n"
                "---\n",
                encoding="utf-8",
            )
            (agent / "SKILL.md").write_text(
                "---\nname: agent-sample\n"
                "description: This agent description also consumes catalog context.\n"
                "---\n",
                encoding="utf-8",
            )

            with mock.patch.object(
                SYNC,
                "MANAGED_SKILL_DESCRIPTION_BUDGET",
                70,
                create=True,
            ):
                with self.assertRaisesRegex(
                    SystemExit,
                    "managed skill description budget",
                ):
                    SYNC.validate_skills(root)

    def test_portable_third_party_lock_matches_allowlist(self) -> None:
        entries = SYNC.validate_third_party_skill_lock(SYNC.REPO_ROOT)
        self.assertEqual(set(entries), SYNC.PORTABLE_CODEX_SKILL_NAMES)

    def test_portable_third_party_lock_rejects_allowlist_drift(self) -> None:
        with mock.patch.object(
            SYNC,
            "PORTABLE_CODEX_SKILL_NAMES",
            {"different-vendor"},
        ):
            with self.assertRaisesRegex(SystemExit, "allowlist"):
                SYNC.validate_third_party_skill_lock(SYNC.REPO_ROOT)

    def test_portable_third_party_lock_rejects_snapshot_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "profile"
            shutil.copytree(
                SYNC.REPO_ROOT / "skills/codex/awesome-rebuttal",
                root / "skills/codex/awesome-rebuttal",
            )
            shutil.copy2(
                SYNC.REPO_ROOT / "THIRD_PARTY_SKILLS.lock.json",
                root / "THIRD_PARTY_SKILLS.lock.json",
            )
            skill = root / "skills/codex/awesome-rebuttal/SKILL.md"
            skill.write_text(
                skill.read_text(encoding="utf-8") + "\nchanged\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(SystemExit, "snapshot sha256"):
                SYNC.validate_third_party_skill_lock(root)

    def test_portable_third_party_lock_rejects_duplicate_json_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "profile"
            root.mkdir()
            source = (
                SYNC.REPO_ROOT / "THIRD_PARTY_SKILLS.lock.json"
            ).read_text(encoding="utf-8")
            duplicate = source.replace(
                '"schema_version": 1,',
                '"schema_version": 1,\n  "schema_version": 1,',
                1,
            )
            (root / "THIRD_PARTY_SKILLS.lock.json").write_text(
                duplicate,
                encoding="utf-8",
            )

            with self.assertRaisesRegex(SystemExit, "duplicate JSON key"):
                SYNC.validate_third_party_skill_lock(root)

    def test_portable_third_party_lock_rejects_extra_skill_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "profile"
            shutil.copytree(
                SYNC.REPO_ROOT / "skills/codex/awesome-rebuttal",
                root / "skills/codex/awesome-rebuttal",
            )
            shutil.copy2(
                SYNC.REPO_ROOT / "THIRD_PARTY_SKILLS.lock.json",
                root / "THIRD_PARTY_SKILLS.lock.json",
            )
            extra = root / "skills/codex/extra-vendor"
            extra.mkdir()
            (extra / "SKILL.md").write_text(
                "---\nname: extra-vendor\n"
                "description: Unlocked third-party skill.\n---\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(SystemExit, "directories/lock mismatch"):
                SYNC.validate_third_party_skill_lock(root)


class CustomAgentProfileTests(unittest.TestCase):
    def test_monitor_profile_pins_luna_high(self) -> None:
        self.assertEqual(
            SYNC.PORTABLE_CODEX_AGENT_SETTINGS["monitor"],
            {
                "model": "gpt-5.6-luna",
                "model_reasoning_effort": "high",
                "sandbox_mode": "read-only",
            },
        )

    def test_portable_config_keeps_parent_model_session_dependent(self) -> None:
        self.assertNotRegex(SYNC.CONFIG_TEMPLATE, r"(?m)^model\s*=")
        self.assertNotRegex(SYNC.CONFIG_TEMPLATE, r"(?m)^model_reasoning_effort\s*=")
        self.assertIn("[agents]\nmax_depth = 1\n", SYNC.CONFIG_TEMPLATE)

    def write_profile(
        self,
        root: Path,
        name: str,
        *,
        declared_name: str | None = None,
        effort: str | None = None,
        sandbox: str = "read-only",
    ) -> Path:
        path = root / "agents" / "codex" / f"{name}.toml"
        path.parent.mkdir(parents=True, exist_ok=True)
        settings = SYNC.PORTABLE_CODEX_AGENT_SETTINGS[name]
        model = settings["model"]
        effort = effort or settings["model_reasoning_effort"]
        path.write_text(
            "\n".join(
                [
                    f'name = "{declared_name or name}"',
                    f'description = "Portable {name} agent."',
                    f'model = "{model}"',
                    f'model_reasoning_effort = "{effort}"',
                    f'sandbox_mode = "{sandbox}"',
                    'developer_instructions = "Stay within the assigned role."',
                    "",
                ]
            ),
            encoding="utf-8",
        )
        return path

    def test_valid_portable_custom_agents_are_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_profile(root, "monitor")
            self.write_profile(root, "reviewer", effort="high")

            SYNC.validate_custom_agents(root)

    def test_custom_agent_name_must_match_filename(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_profile(root, "monitor", declared_name="other")
            self.write_profile(root, "reviewer", effort="high")

            with self.assertRaisesRegex(SystemExit, "name/file mismatch"):
                SYNC.validate_custom_agents(root)

    def test_custom_agent_reasoning_effort_must_be_supported_value(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_profile(root, "monitor", effort="fastest")
            self.write_profile(root, "reviewer", effort="high")

            with self.assertRaisesRegex(SystemExit, "model_reasoning_effort"):
                SYNC.validate_custom_agents(root)

    def test_custom_agent_role_settings_must_match_portable_policy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_profile(root, "monitor", sandbox="workspace-write")
            self.write_profile(root, "reviewer", effort="medium")

            with self.assertRaisesRegex(SystemExit, "portable policy"):
                SYNC.validate_custom_agents(root)

    def test_portable_custom_agent_rejects_unreviewed_config_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            monitor = self.write_profile(root, "monitor")
            self.write_profile(root, "reviewer", effort="high")
            monitor.write_text(
                monitor.read_text(encoding="utf-8") + 'api_key = "<REDACTED>"\n',
                encoding="utf-8",
            )

            with self.assertRaisesRegex(SystemExit, "unexpected keys"):
                SYNC.validate_custom_agents(root)

    def test_portable_custom_agent_rejects_non_toml_escape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            monitor = self.write_profile(root, "monitor")
            self.write_profile(root, "reviewer", effort="high")
            monitor.write_text(
                monitor.read_text(encoding="utf-8").replace(
                    'description = "Portable monitor agent."',
                    'description = "bad\\/escape"',
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(SystemExit, "invalid custom agent TOML"):
                SYNC.validate_custom_agents(root)

    def test_portable_custom_agent_accepts_escaped_backslash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            monitor = self.write_profile(root, "monitor")
            self.write_profile(root, "reviewer", effort="high")
            monitor.write_text(
                monitor.read_text(encoding="utf-8").replace(
                    'description = "Portable monitor agent."',
                    'description = "valid\\\\q"',
                ),
                encoding="utf-8",
            )

            SYNC.validate_custom_agents(root)

    def test_portable_custom_agent_rejects_raw_control_character(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            monitor = self.write_profile(root, "monitor")
            self.write_profile(root, "reviewer", effort="high")
            monitor.write_bytes(
                monitor.read_bytes().replace(
                    b'developer_instructions = "Stay within the assigned role."',
                    (
                        b'developer_instructions = """\n'
                        b"Stay\x0bwithin the assigned role.\n"
                        b'"""'
                    ),
                )
            )

            with self.assertRaisesRegex(SystemExit, "control character"):
                SYNC.validate_custom_agents(root)

    def test_portable_custom_agent_rejects_bare_carriage_return(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            monitor = self.write_profile(root, "monitor")
            self.write_profile(root, "reviewer", effort="high")
            monitor.write_bytes(
                monitor.read_bytes().replace(
                    b"Portable monitor agent.",
                    b"Portable\rmonitor agent.",
                )
            )

            with self.assertRaisesRegex(SystemExit, "carriage return"):
                SYNC.validate_custom_agents(root)

    def test_portable_custom_agent_rejects_invalid_nicknames(self) -> None:
        invalid_lists = (
            '["Alpha", " Alpha "]',
            '["A/B"]',
        )
        for nickname_list in invalid_lists:
            with self.subTest(nickname_list=nickname_list):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    monitor = self.write_profile(root, "monitor")
                    self.write_profile(root, "reviewer", effort="high")
                    monitor.write_text(
                        monitor.read_text(encoding="utf-8")
                        + f"nickname_candidates = {nickname_list}\n",
                        encoding="utf-8",
                    )

                    with self.assertRaisesRegex(SystemExit, "nickname_candidates"):
                        SYNC.validate_custom_agents(root)

    def test_portable_custom_agent_normalizes_valid_nicknames(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            monitor = self.write_profile(root, "monitor")
            self.write_profile(root, "reviewer", effort="high")
            monitor.write_text(
                monitor.read_text(encoding="utf-8")
                + 'nickname_candidates = [" Alpha ", "Beta-2"]\n',
                encoding="utf-8",
            )

            loaded = SYNC.load_custom_agent(monitor)

            self.assertEqual(loaded["nickname_candidates"], ["Alpha", "Beta-2"])

    def test_portable_custom_agent_directory_rejects_extra_children(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_profile(root, "monitor")
            self.write_profile(root, "reviewer", effort="high")
            extra = root / "agents" / "codex" / "nested" / "child.toml"
            extra.parent.mkdir()
            extra.write_text(
                "\n".join(
                    [
                        'name = "child"',
                        'description = "Nested unreviewed role."',
                        'developer_instructions = "Do nothing."',
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(SystemExit, "unallowlisted portable custom agent"):
                SYNC.validate_custom_agents(root)

    def test_current_codex_loader_agrees_on_invalid_toml_escape(self) -> None:
        codex = shutil.which("codex")
        if codex is None:
            self.skipTest("Codex CLI is unavailable")

        with tempfile.TemporaryDirectory(
            prefix="codex-agent-loader-", dir=Path.home()
        ) as tmp:
            root = Path(tmp)
            profile = self.write_profile(root, "monitor")
            self.write_profile(root, "reviewer", effort="high")
            profile.write_text(
                profile.read_text(encoding="utf-8").replace(
                    'description = "Portable monitor agent."',
                    'description = "bad\\/escape"',
                ),
                encoding="utf-8",
            )

            with self.assertRaises(SystemExit) as raised:
                SYNC.validate_custom_agents_with_codex(root)
            native_error = str(raised.exception)
            self.assertIn("monitor.toml", native_error)
            self.assertIn("failed to parse agent role file", native_error.lower())
            with self.assertRaisesRegex(SystemExit, "invalid custom agent TOML"):
                SYNC.load_custom_agent(profile)

    def test_current_codex_loader_accepts_valid_portable_profiles(self) -> None:
        codex = shutil.which("codex")
        if codex is None:
            self.skipTest("Codex CLI is unavailable")

        with tempfile.TemporaryDirectory(
            prefix="codex-agent-loader-valid-", dir=Path.home()
        ) as tmp:
            root = Path(tmp)
            self.write_profile(root, "monitor")
            self.write_profile(root, "reviewer", effort="high")

            SYNC.validate_custom_agents(root)
            SYNC.validate_custom_agents_with_codex(root)

    def test_codex_loader_requires_successful_initialize_and_config_read(self) -> None:
        with self.assertRaisesRegex(SystemExit, "JSON-RPC"):
            SYNC.validate_codex_loader_messages(
                [
                    {"id": 1, "result": {}},
                    {
                        "id": 2,
                        "error": {"code": -32603, "message": "failed"},
                    },
                ],
                "",
                set(),
                0,
            )

    def test_codex_loader_ignores_unrelated_warning_after_success(self) -> None:
        SYNC.validate_codex_loader_messages(
            [
                {
                    "method": "configWarning",
                    "params": {
                        "path": "/tmp/unrelated-config.toml",
                        "summary": "Ignoring malformed agent role definition",
                        "details": "failed to parse agent role file from another layer",
                    },
                },
                {"id": 1, "result": {}},
                {"id": 2, "result": {}},
            ],
            "",
            {"/tmp/codex-home/agents/monitor.toml"},
            0,
        )

    def test_export_requires_every_allowlisted_custom_agent_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            source_root = home / ".codex" / "agents"
            source_root.mkdir(parents=True)
            (source_root / "monitor.toml").write_text(
                "\n".join(
                    [
                        'name = "monitor"',
                        'description = "monitor"',
                        'model = "gpt-5.6-luna"',
                        'model_reasoning_effort = "high"',
                        'sandbox_mode = "read-only"',
                        'developer_instructions = "Bounded role."',
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(SystemExit, "reviewer"):
                SYNC.validate_export_custom_agent_sources(home)

    def test_export_custom_agents_copies_only_allowlisted_profiles(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            codex = base / "home" / ".codex"
            export_root = base / "profile"
            source_root = codex / "agents"
            for name, model, effort in (
                ("monitor", "gpt-5.6-luna", "high"),
                ("reviewer", "gpt-5.6-sol", "high"),
                ("local-only", "gpt-5.6-terra", "medium"),
            ):
                path = source_root / f"{name}.toml"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    "\n".join(
                        [
                            f'name = "{name}"',
                            f'description = "{name}"',
                            f'model = "{model}"',
                            f'model_reasoning_effort = "{effort}"',
                            'sandbox_mode = "read-only"',
                            'developer_instructions = "Bounded role."',
                            "",
                        ]
                    ),
                    encoding="utf-8",
                )

            SYNC.export_custom_agents(codex, export_root)

            exported = sorted(
                path.name for path in (export_root / "agents" / "codex").glob("*.toml")
            )
            self.assertEqual(exported, ["monitor.toml", "reviewer.toml"])

    def test_custom_agent_apply_pairs_target_codex_agent_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "profile"
            home = Path(tmp) / "home"
            monitor = self.write_profile(root, "monitor")
            reviewer = self.write_profile(root, "reviewer", effort="high")

            pairs = SYNC.custom_agent_apply_pairs(root, home)

            self.assertEqual(
                pairs,
                [
                    (monitor, home / ".codex" / "agents" / "monitor.toml"),
                    (reviewer, home / ".codex" / "agents" / "reviewer.toml"),
                ],
            )


class RetiredSkillLifecycleTests(unittest.TestCase):
    def write_valid_personal_skill(self, root: Path, name: str) -> Path:
        skill = root / "skills" / "codex" / name
        (skill / "agents").mkdir(parents=True)
        (skill / "references").mkdir()
        (skill / "SKILL.md").write_text(
            f"---\nname: {name}\n"
            "description: Use for one focused retired workflow fixture.\n---\n",
            encoding="utf-8",
        )
        (skill / "agents" / "openai.yaml").write_text(
            "interface:\n"
            "  display_name: \"Retired Fixture\"\n"
            "  short_description: \"Exercise one retired skill identity\"\n"
            f"  default_prompt: \"Use ${name} for this fixture.\"\n",
            encoding="utf-8",
        )
        (skill / "references" / "source-notes.md").write_text(
            "# Source Notes\n", encoding="utf-8"
        )
        return skill

    def run_confirmed_apply(
        self,
        home: Path,
        digest_by_name: dict[str, str],
    ) -> tuple[BaseException | None, Path]:
        source = home.parent / "new-guard.py"
        destination = home / ".codex" / "hooks" / "sentinel.py"
        source.write_text("new\n", encoding="utf-8")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text("old\n", encoding="utf-8")
        args = argparse.Namespace(home=str(home), confirm=True)

        def fake_skill_digest(path: Path) -> str:
            return digest_by_name.get(path.name, "f" * 64)

        error: BaseException | None = None
        with mock.patch.object(SYNC, "verify_repo"):
            with mock.patch.object(
                SYNC, "apply_pairs", return_value=[(source, destination)]
            ):
                with mock.patch.object(SYNC, "retired_hook_paths", return_value=[]):
                    with mock.patch.object(SYNC, "renamed_skill_paths", return_value=[]):
                        with mock.patch.object(
                            SYNC, "pending_renamed_skills", return_value=[]
                        ):
                            with mock.patch.object(
                                SYNC,
                                "skill_tree_sha256",
                                side_effect=fake_skill_digest,
                            ):
                                try:
                                    SYNC.cmd_apply(args)
                                except (RuntimeError, SystemExit) as exc:
                                    error = exc
        return error, destination

    def test_registry_contains_all_reviewed_identities_and_digests(self) -> None:
        registry = getattr(SYNC, "RETIRED_CODEX_SKILLS", {})

        self.assertEqual(set(registry), set(REVIEWED_RETIRED_SKILL_DIGESTS))
        self.assertEqual(
            sum(len(values) for values in REVIEWED_RETIRED_SKILL_DIGESTS.values()),
            15,
        )
        for identity, digests in REVIEWED_RETIRED_SKILL_DIGESTS.items():
            with self.subTest(identity=identity):
                entry = repr(registry[identity])
                self.assertIn("sha256-path-content-v1", entry)
                for digest in digests:
                    self.assertIn(digest, entry)

    def test_legacy_context_identity_is_a_tombstone_not_a_rename(self) -> None:
        self.assertNotIn("context-save-restore", SYNC.RENAMED_CODEX_SKILLS)
        self.assertIn("context-save-restore", SYNC.RETIRED_CODEX_SKILLS)

    def test_verify_rejects_a_retired_skill_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_valid_personal_skill(root, "personal-context-compression")

            with self.assertRaisesRegex(SystemExit, "retired"):
                SYNC.validate_skills(root)

    def test_export_filter_never_resurrects_retired_personal_skills(self) -> None:
        for name in sorted(RETIRED_PERSONAL_SKILLS):
            with self.subTest(name=name):
                self.assertFalse(SYNC.is_portable_codex_skill(name))

    def test_export_filter_omits_retired_hook_sources(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "profile"
            home = base / "home"
            codex = home / ".codex"
            root.mkdir()
            for directory in (
                codex / "skills",
                codex / "hooks",
                codex / "hookify",
                home / ".agents" / "skills",
            ):
                directory.mkdir(parents=True, exist_ok=True)
            (codex / "AGENTS.md").write_text(
                "# Portable Codex Instructions\n", encoding="utf-8"
            )
            (codex / "hooks.json").write_text("{}\n", encoding="utf-8")
            (codex / "hooks" / "smart_commit_stage.py").write_text(
                "retired\n", encoding="utf-8"
            )
            (codex / "hooks" / "live_guard.py").write_text(
                "live\n", encoding="utf-8"
            )
            (codex / "hookify" / "warn-package-manager-install.md").write_text(
                "retired\n", encoding="utf-8"
            )
            (codex / "hookify" / "live-rule.md").write_text(
                "live\n", encoding="utf-8"
            )

            with mock.patch.object(SYNC, "validate_export_renamed_skill_sources"):
                with mock.patch.object(SYNC, "validate_export_custom_agent_sources"):
                    with mock.patch.object(SYNC, "export_custom_agents"):
                        SYNC.render_export_snapshot(root, home)

            self.assertTrue((root / "hooks/scripts/live_guard.py").is_file())
            self.assertTrue((root / "hooks/rules/live-rule.md").is_file())
            self.assertFalse((root / "hooks/scripts/smart_commit_stage.py").exists())
            self.assertFalse(
                (root / "hooks/rules/warn-package-manager-install.md").exists()
            )

    def test_replacement_contract_cannot_come_only_from_source_notes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_root = Path(tmp)
            replacement_root = skill_root / "skills" / "codex"
            replacement = self.write_valid_personal_skill(
                skill_root, "personal-replacement"
            )
            (replacement / "references/source-notes.md").write_text(
                "# Source Notes\n\nlive replacement contract marker\n",
                encoding="utf-8",
            )
            policy = SYNC.RetiredCodexSkill(
                hash_algorithm="sha256-path-content-v1",
                digests=("a" * 64,),
                replacement="fixture replacement",
                replacement_skills=("personal-replacement",),
                replacement_contract_markers=(
                    "live replacement contract marker",
                ),
            )

            with self.assertRaisesRegex(RuntimeError, "pending migration"):
                SYNC.validate_retired_replacement_sources(
                    replacement_root, [policy]
                )

    def test_retired_skill_hash_rejects_fifo_entries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "retired-skill"
            skill.mkdir()
            (skill / "SKILL.md").write_text("retired\n", encoding="utf-8")
            os.mkfifo(skill / "runtime.pipe")

            with self.assertRaisesRegex(SystemExit, "regular"):
                SYNC.skill_tree_sha256(skill)

    def test_apply_conflict_preflight_makes_zero_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            skills = home / ".codex" / "skills"
            for name in (
                "personal-context-compression",
                "personal-context-optimization",
            ):
                skill = skills / name
                skill.mkdir(parents=True)
                (skill / "SKILL.md").write_text(name + "\n", encoding="utf-8")
            agents = home / ".codex" / "AGENTS.md"
            agents.write_text(
                (SYNC.REPO_ROOT / "rules/AGENTS.portable.md").read_text(
                    encoding="utf-8"
                ),
                encoding="utf-8",
            )
            for replacement in (
                "personal-planning-with-files-zh",
                "personal-triad-discussion",
            ):
                shutil.copytree(
                    SYNC.REPO_ROOT / "skills" / "codex" / replacement,
                    skills / replacement,
                )

            error, destination = self.run_confirmed_apply(
                home,
                {
                    "personal-context-compression": (
                        REVIEWED_RETIRED_SKILL_DIGESTS[
                            "personal-context-compression"
                        ][-1]
                    ),
                    "personal-context-optimization": "f" * 64,
                },
            )

            self.assertEqual(destination.read_text(encoding="utf-8"), "old\n")
            self.assertFalse((home / "codex-migration-archive").exists())
            self.assertIsNotNone(error)
            self.assertRegex(str(error).lower(), r"(?:conflict|diverg|retired)")

    def test_missing_active_contract_blocks_retirement_before_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            retired = home / ".codex" / "skills" / "personal-context-optimization"
            retired.mkdir(parents=True)
            (retired / "SKILL.md").write_text("retired\n", encoding="utf-8")
            (home / ".codex" / "AGENTS.md").write_text(
                "# Incomplete active contract\n", encoding="utf-8"
            )

            error, destination = self.run_confirmed_apply(
                home,
                {
                    "personal-context-optimization": (
                        REVIEWED_RETIRED_SKILL_DIGESTS[
                            "personal-context-optimization"
                        ][-1]
                    )
                },
            )

            self.assertEqual(destination.read_text(encoding="utf-8"), "old\n")
            self.assertFalse((home / "codex-migration-archive").exists())
            self.assertIsNotNone(error)
            self.assertRegex(
                str(error).lower(), r"(?:contract|prerequisite|pending migration)"
            )

    def test_personal_catalog_has_twenty_one_live_skills(self) -> None:
        root = SYNC.REPO_ROOT / "skills" / "codex"
        personal = {path.name for path in root.glob("personal-*") if path.is_dir()}

        self.assertEqual(len(personal), 21)
        self.assertIn("personal-prompt-optimizer", personal)
        self.assertEqual(personal & RETIRED_PERSONAL_SKILLS, set())

    def test_docs_sync_contract_is_merged_into_code_documentation(self) -> None:
        replacement = SYNC.REPO_ROOT / "skills/codex/personal-code-documentation"
        skill = (replacement / "SKILL.md").read_text(encoding="utf-8")
        metadata = (replacement / "agents/openai.yaml").read_text(encoding="utf-8")
        notes = (replacement / "references/source-notes.md").read_text(
            encoding="utf-8"
        )
        normalized = " ".join(skill.split()).lower()
        frontmatter = SYNC.parse_frontmatter(skill)

        self.assertIn("sync_existing", frontmatter["description"])
        self.assertIn("sync_existing", metadata)
        self.assertIn("sync_existing", normalized)
        for trigger in ("cli", "api", "config", "install", "workflow", "stale"):
            self.assertIn(trigger, normalized)
        for bounded_change in ("small", "literal", "link", "example", "snippet"):
            self.assertIn(bounded_change, normalized)
        for exclusion in ("architecture", "explanation", "status", "polish"):
            self.assertIn(exclusion, normalized)
        self.assertIn("personal-docs-sync-light", notes)
        for digest in REVIEWED_RETIRED_SKILL_DIGESTS["personal-docs-sync-light"]:
            self.assertIn(digest, notes)
        registry_entry = repr(SYNC.RETIRED_CODEX_SKILLS["personal-docs-sync-light"])
        self.assertIn("personal-code-documentation", registry_entry)
        self.assertIn("sync_existing", registry_entry)

    def test_retired_references_are_only_historical_or_test_evidence(self) -> None:
        canonical_registry = SYNC.REPO_ROOT / "scripts" / "sync.py"
        sync_test = Path(__file__).resolve()
        live: list[str] = []
        allowed_suffixes = {".json", ".md", ".py", ".toml", ".yaml", ".yml"}
        identities = set(REVIEWED_RETIRED_SKILL_DIGESTS)

        for path in SYNC.REPO_ROOT.rglob("*"):
            if (
                not path.is_file()
                or path.suffix.lower() not in allowed_suffixes
                or ".git" in path.parts
                or path in {canonical_registry, sync_test}
            ):
                continue
            text = path.read_text(encoding="utf-8")
            matched = sorted(identity for identity in identities if identity in text)
            if not matched:
                continue
            if path.name == "source-notes.md" or "archive" in path.parts:
                continue
            live.append(f"{path.relative_to(SYNC.REPO_ROOT)}: {', '.join(matched)}")

        self.assertFalse(
            live,
            "live stale references remain:\n" + "\n".join(live[:20]),
        )


class RenamedSkillLifecycleTests(unittest.TestCase):
    def test_export_rejects_concurrent_writer_before_rendering(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "profile"
            home = Path(tmp) / "source-home"
            root.mkdir()
            home.mkdir()
            sentinel = root / "README.md"
            sentinel.write_text("preserve me\n", encoding="utf-8")

            with SYNC.exclusive_export_lock(root):
                with self.assertRaisesRegex(RuntimeError, "already active"):
                    SYNC.export_to(root, home)

            self.assertEqual(sentinel.read_text(encoding="utf-8"), "preserve me\n")

    def test_export_lock_rejects_symbolic_link_without_following_it(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "profile"
            outside = base / "outside.txt"
            root.mkdir()
            outside.write_text("outside\n", encoding="utf-8")
            lock_path = base / ".profile.export.lock"
            lock_path.symlink_to(outside)

            with self.assertRaisesRegex(RuntimeError, "safe export lock"):
                with SYNC.exclusive_export_lock(root):
                    self.fail("symbolic-link lock must not be acquired")

            self.assertEqual(outside.read_text(encoding="utf-8"), "outside\n")

    def test_export_tarball_rejects_existing_directory_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "profile"
            home = base / "source-home"
            root.mkdir()
            home.mkdir()
            archive = root.parent / (
                f"{root.name}-{SYNC.datetime.now().strftime('%Y%m%d')}.tar.gz"
            )
            archive.mkdir()
            sentinel = archive / "keep.txt"
            sentinel.write_text("preserve me\n", encoding="utf-8")

            with mock.patch.object(SYNC, "render_export_snapshot"):
                with mock.patch.object(SYNC, "verify_repo"):
                    with self.assertRaisesRegex(RuntimeError, "regular file"):
                        SYNC.export_to(root, home, tarball=True)

            self.assertEqual(sentinel.read_text(encoding="utf-8"), "preserve me\n")

    def test_export_replacement_failure_rolls_back_every_managed_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "profile"
            candidate = base / "transaction" / "candidate"
            transaction_root = base / "transaction"
            first_target = root / "rules"
            second_target = root / "INSTALL.md"
            first_source = candidate / "rules"
            second_source = candidate / "INSTALL.md"
            first_target.mkdir(parents=True)
            (first_target / "old.txt").write_text("old rules\n", encoding="utf-8")
            second_target.write_text("old install\n", encoding="utf-8")
            first_source.mkdir(parents=True)
            (first_source / "new.txt").write_text("new rules\n", encoding="utf-8")
            second_source.write_text("new install\n", encoding="utf-8")

            real_replace = SYNC.os.replace
            call_count = 0

            def fail_during_second_install(source: Path, destination: Path) -> None:
                nonlocal call_count
                call_count += 1
                if call_count == 4:
                    raise OSError("injected replacement failure")
                real_replace(source, destination)

            with mock.patch.object(
                SYNC.os, "replace", side_effect=fail_during_second_install
            ):
                with self.assertRaisesRegex(OSError, "injected replacement failure"):
                    SYNC.transactional_replace_managed_entries(
                        [
                            (first_source, first_target),
                            (second_source, second_target),
                        ],
                        transaction_root,
                    )

            self.assertEqual(
                (first_target / "old.txt").read_text(encoding="utf-8"),
                "old rules\n",
            )
            self.assertFalse((first_target / "new.txt").exists())
            self.assertEqual(second_target.read_text(encoding="utf-8"), "old install\n")

    def test_export_interrupt_rolls_back_every_managed_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "profile"
            candidate = base / "transaction" / "candidate"
            transaction_root = base / "transaction"
            first_target = root / "rules"
            second_target = root / "INSTALL.md"
            first_source = candidate / "rules"
            second_source = candidate / "INSTALL.md"
            first_target.mkdir(parents=True)
            (first_target / "old.txt").write_text("old rules\n", encoding="utf-8")
            second_target.write_text("old install\n", encoding="utf-8")
            first_source.mkdir(parents=True)
            (first_source / "new.txt").write_text("new rules\n", encoding="utf-8")
            second_source.write_text("new install\n", encoding="utf-8")

            real_replace = SYNC.os.replace
            call_count = 0

            def interrupt_during_second_install(source: Path, destination: Path) -> None:
                nonlocal call_count
                call_count += 1
                if call_count == 4:
                    raise KeyboardInterrupt("injected interrupt")
                real_replace(source, destination)

            with mock.patch.object(
                SYNC.os, "replace", side_effect=interrupt_during_second_install
            ):
                with self.assertRaises(KeyboardInterrupt):
                    SYNC.transactional_replace_managed_entries(
                        [
                            (first_source, first_target),
                            (second_source, second_target),
                        ],
                        transaction_root,
                    )

            self.assertEqual(
                (first_target / "old.txt").read_text(encoding="utf-8"),
                "old rules\n",
            )
            self.assertFalse((first_target / "new.txt").exists())
            self.assertEqual(second_target.read_text(encoding="utf-8"), "old install\n")

    def test_export_interrupt_after_replace_rolls_back_from_filesystem_state(self) -> None:
        for interrupt_call in (3, 4):
            with self.subTest(interrupt_call=interrupt_call):
                with tempfile.TemporaryDirectory() as tmp:
                    base = Path(tmp)
                    root = base / "profile"
                    candidate = base / "transaction" / "candidate"
                    transaction_root = base / "transaction"
                    first_target = root / "rules"
                    second_target = root / "INSTALL.md"
                    first_source = candidate / "rules"
                    second_source = candidate / "INSTALL.md"
                    first_target.mkdir(parents=True)
                    (first_target / "old.txt").write_text(
                        "old rules\n", encoding="utf-8"
                    )
                    second_target.write_text("old install\n", encoding="utf-8")
                    first_source.mkdir(parents=True)
                    (first_source / "new.txt").write_text(
                        "new rules\n", encoding="utf-8"
                    )
                    second_source.write_text("new install\n", encoding="utf-8")

                    real_replace = SYNC.os.replace
                    call_count = 0

                    def interrupt_after_replace(
                        source: Path, destination: Path
                    ) -> None:
                        nonlocal call_count
                        call_count += 1
                        real_replace(source, destination)
                        if call_count == interrupt_call:
                            raise KeyboardInterrupt("injected post-replace interrupt")

                    with mock.patch.object(
                        SYNC.os, "replace", side_effect=interrupt_after_replace
                    ):
                        with self.assertRaises(KeyboardInterrupt):
                            SYNC.transactional_replace_managed_entries(
                                [
                                    (first_source, first_target),
                                    (second_source, second_target),
                                ],
                                transaction_root,
                            )

                    self.assertEqual(
                        (first_target / "old.txt").read_text(encoding="utf-8"),
                        "old rules\n",
                    )
                    self.assertFalse((first_target / "new.txt").exists())
                    self.assertEqual(
                        second_target.read_text(encoding="utf-8"),
                        "old install\n",
                    )

    def test_export_validation_failure_preserves_existing_managed_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "profile"
            home = base / "source-home"
            codex = home / ".codex"

            for successor_name in SYNC.RENAMED_CODEX_SKILLS.values():
                successor = codex / "skills" / successor_name
                successor.mkdir(parents=True)
                (successor / "SKILL.md").write_text(
                    f"---\nname: {successor_name}\ndescription: test skill\n---\n",
                    encoding="utf-8",
                )

            for name, settings in SYNC.PORTABLE_CODEX_AGENT_SETTINGS.items():
                profile = codex / "agents" / f"{name}.toml"
                profile.parent.mkdir(parents=True, exist_ok=True)
                profile.write_text(
                    "\n".join(
                        [
                            f'name = "{name}"',
                            f'description = "Portable {name} agent."',
                            f'model = "{settings["model"]}"',
                            (
                                "model_reasoning_effort = "
                                f'"{settings["model_reasoning_effort"]}"'
                            ),
                            f'sandbox_mode = "{settings["sandbox_mode"]}"',
                            'developer_instructions = "Bounded role."',
                            "",
                        ]
                    ),
                    encoding="utf-8",
                )

            (codex / "AGENTS.md").write_text(
                "# Portable Codex Instructions\n\n## Host Local Overlay\n\n- bad\n",
                encoding="utf-8",
            )
            (codex / "hooks.json").write_text("{}\n", encoding="utf-8")

            sentinel = root / "skills" / "codex" / "user-dirty.txt"
            sentinel.parent.mkdir(parents=True)
            sentinel.write_text("preserve me\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "Host Local Overlay"):
                SYNC.export_to(root, home)

            self.assertEqual(sentinel.read_text(encoding="utf-8"), "preserve me\n")

    def test_export_missing_successor_preserves_existing_profile(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            home = root / "source-home"
            source_skills = home / ".codex/skills"
            for successor_name in SYNC.RENAMED_CODEX_SKILLS.values():
                if successor_name == "personal-code-simplifier":
                    continue
                successor = source_skills / successor_name
                successor.mkdir(parents=True)
                (successor / "SKILL.md").write_text(
                    f"---\nname: {successor_name}\ndescription: test skill\n---\n",
                    encoding="utf-8",
                )
            legacy = source_skills / "code-simplifier"
            legacy.mkdir(parents=True)
            (legacy / "SKILL.md").write_text("legacy\n", encoding="utf-8")

            profile = root / "profile"
            sentinel = profile / "skills/codex/personal-code-simplifier/SKILL.md"
            sentinel.parent.mkdir(parents=True)
            sentinel.write_text("keep successor\n", encoding="utf-8")

            with self.assertRaisesRegex(SystemExit, "personal-code-simplifier"):
                SYNC.export_to(profile, home)

            self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep successor\n")

    def test_renamed_skill_paths_are_scoped_to_target_home(self) -> None:
        home = Path("/tmp/profile-home")

        pairs = SYNC.renamed_skill_paths(home)

        self.assertTrue(pairs)
        self.assertTrue(
            all(old.is_relative_to(home) and new.is_relative_to(home) for old, new in pairs)
        )
        self.assertNotIn(
            home / ".codex/skills/context-save-restore",
            {legacy for legacy, _ in pairs},
        )
        self.assertIn(
            (
                home / ".codex/skills/code-simplifier",
                home / ".codex/skills/personal-code-simplifier",
            ),
            pairs,
        )
        self.assertIn(
            (
                home / ".codex/skills/code-documentation",
                home / ".codex/skills/personal-code-documentation",
            ),
            pairs,
        )

    def test_missing_successor_never_retires_legacy_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "target-home"
            legacy = home / ".codex/skills/code-simplifier"
            successor = home / ".codex/skills/personal-code-simplifier"
            legacy.mkdir(parents=True)
            (legacy / "SKILL.md").write_text("legacy\n", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "successor"):
                SYNC.retire_renamed_skills([(legacy, successor)])

            self.assertTrue(legacy.is_dir())

    def test_verified_successor_retires_legacy_after_backup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "target-home"
            backup_root = home / "migration-archive" / "before-apply"
            legacy = home / ".codex/skills/code-simplifier"
            successor = home / ".codex/skills/personal-code-simplifier"
            source = SYNC.REPO_ROOT / "skills/codex/personal-code-simplifier"
            legacy.mkdir(parents=True)
            (legacy / "SKILL.md").write_text("legacy\n", encoding="utf-8")
            SYNC.copytree(source, successor)
            pairs = [(legacy, successor)]

            SYNC.backup_renamed_skills(pairs, backup_root, home)
            SYNC.retire_renamed_skills(pairs)

            self.assertFalse(legacy.exists())
            self.assertTrue(successor.is_dir())
            backup = backup_root / ".codex/skills/code-simplifier/SKILL.md"
            self.assertEqual(backup.read_text(encoding="utf-8"), "legacy\n")

    def test_confirmed_apply_backs_up_and_retires_legacy_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "target-home"
            legacy = home / ".codex/skills/code-simplifier"
            legacy.mkdir(parents=True)
            (legacy / "SKILL.md").write_text("legacy\n", encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    str(SYNC_PATH),
                    "--home",
                    str(home),
                    "apply",
                    "--confirm",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertFalse(legacy.exists())
            successor = home / ".codex/skills/personal-code-simplifier"
            self.assertTrue(successor.is_dir())
            summary = SYNC.diff_dirs(
                SYNC.REPO_ROOT / "skills/codex/personal-code-simplifier",
                successor,
            )
            self.assertEqual(summary.only_left, [])
            self.assertEqual(summary.only_right, [])
            self.assertEqual(summary.different, [])
            backups = list(
                (home / "codex-migration-archive").glob(
                    "*-before-profile-kit-apply/.codex/skills/"
                    "code-simplifier/SKILL.md"
                )
            )
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), "legacy\n")


class HookLifecycleTests(unittest.TestCase):
    def test_reviewed_retired_hook_registry_matches_git_baseline(self) -> None:
        registry = getattr(SYNC, "REVIEWED_RETIRED_HOOK_TARGET_SHA256", {})

        self.assertEqual(registry, REVIEWED_RETIRED_HOOK_TARGET_SHA256)
        self.assertLessEqual(set(registry), set(SYNC.RETIRED_HOOK_TARGETS))

    def test_drifted_reviewed_retired_hook_blocks_apply_before_backup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            target = (
                home
                / ".codex/hookify/warn-gpu-task-without-device-scope.md"
            )
            target.parent.mkdir(parents=True)
            target.write_text("unreviewed target-host drift\n", encoding="utf-8")
            args = argparse.Namespace(home=str(home), confirm=True)

            with mock.patch.object(SYNC, "verify_repo"):
                with mock.patch.object(SYNC, "apply_pairs", return_value=[]):
                    with self.assertRaisesRegex(
                        RuntimeError,
                        "unreviewed retired hook digest",
                    ):
                        SYNC.cmd_apply(args)

            self.assertEqual(
                target.read_text(encoding="utf-8"),
                "unreviewed target-host drift\n",
            )
            self.assertFalse((home / "codex-migration-archive").exists())

    def test_reviewed_retired_hook_rejects_symlink_and_non_regular_state(self) -> None:
        relative = Path(
            ".codex/hookify/warn-gpu-task-without-device-scope.md"
        )
        for state in ("symlink", "directory"):
            with self.subTest(state=state):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    home = root / "home"
                    target = home / relative
                    target.parent.mkdir(parents=True)
                    if state == "symlink":
                        outside = root / "outside.md"
                        outside.write_text("reviewed bytes unavailable\n", encoding="utf-8")
                        target.symlink_to(outside)
                    else:
                        target.mkdir()

                    with self.assertRaisesRegex(
                        RuntimeError,
                        r"(?:symbolic link|regular file)",
                    ):
                        SYNC.validate_apply_plan(
                            home,
                            [],
                            home / ".codex/hooks.json",
                        )
                    self.assertFalse((home / "codex-migration-archive").exists())

    def test_exact_reviewed_retired_hook_uses_backup_and_retire_flow(self) -> None:
        relative = ".codex/hookify/warn-gpu-task-without-device-scope.md"
        reviewed_bytes = b"reviewed retired hook fixture\n"
        reviewed_digest = SYNC.hashlib.sha256(reviewed_bytes).hexdigest()
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            target = home / relative
            target.parent.mkdir(parents=True)
            target.write_bytes(reviewed_bytes)
            args = argparse.Namespace(home=str(home), confirm=True)

            with mock.patch.object(
                SYNC,
                "REVIEWED_RETIRED_HOOK_TARGET_SHA256",
                {relative: reviewed_digest},
                create=True,
            ):
                with mock.patch.object(SYNC, "verify_repo"):
                    with mock.patch.object(SYNC, "apply_pairs", return_value=[]):
                        self.assertEqual(SYNC.cmd_apply(args), 0)

            self.assertFalse(target.exists())
            backups = list(
                (home / "codex-migration-archive").glob(
                    f"*-before-profile-kit-apply/{relative}"
                )
            )
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_bytes(), reviewed_bytes)

    def test_hook_validation_rejects_unreviewed_candidate_before_execution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(SYNC.REPO_ROOT / "hooks", root / "hooks")
            (root / "templates").mkdir()
            shutil.copy2(
                SYNC.REPO_ROOT / "templates/hooks.json.template",
                root / "templates/hooks.json.template",
            )
            guard = root / "hooks/scripts/direct_download_guard.py"
            guard.write_text(
                guard.read_text(encoding="utf-8").replace(
                    '"additionalContext": context,',
                    '"permissionDecision": "deny",',
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(SystemExit, "reviewed hook snapshot"):
                SYNC.validate_hooks(root)

    def test_hook_validation_rejects_an_empty_test_suite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            scripts = root / "hooks" / "scripts"
            scripts.mkdir(parents=True)
            (scripts / "test_empty.py").write_text(
                "#!/usr/bin/env python3\n\"\"\"No tests are defined.\"\"\"\n",
                encoding="utf-8",
            )

            with mock.patch.object(SYNC, "validate_reviewed_hook_snapshot"):
                with self.assertRaisesRegex(SystemExit, r"(?:zero|no) tests"):
                    SYNC.validate_hooks(root)

    def test_file_backup_uses_explicit_target_home(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            home = root / "target-home"
            source = root / "source.py"
            destination = home / ".codex" / "hooks" / "guard.py"
            backup_root = home / "archive" / "before-apply"
            source.write_text("new\n", encoding="utf-8")
            destination.parent.mkdir(parents=True)
            destination.write_text("old\n", encoding="utf-8")

            SYNC.copy_file_with_backup(source, destination, backup_root, home)

            self.assertEqual(destination.read_text(encoding="utf-8"), "new\n")
            backup = backup_root / ".codex" / "hooks" / "guard.py"
            self.assertEqual(backup.read_text(encoding="utf-8"), "old\n")

    def test_file_backup_rejects_symlink_destination_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            home = root / "target-home"
            source = root / "source.py"
            destination = home / ".codex" / "hooks" / "guard.py"
            backup_root = home / "archive" / "before-apply"
            outside = root / "outside.py"
            source.write_text("new\n", encoding="utf-8")
            outside.write_text("outside\n", encoding="utf-8")
            destination.parent.mkdir(parents=True)
            destination.symlink_to(outside)

            with self.assertRaisesRegex(RuntimeError, "symbolic link"):
                SYNC.copy_file_with_backup(source, destination, backup_root, home)

            self.assertEqual(outside.read_text(encoding="utf-8"), "outside\n")
            self.assertTrue(destination.is_symlink())

    def test_file_backup_rejects_symlink_parent_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            home = root / "target-home"
            source = root / "source.py"
            outside_dir = root / "outside-hooks"
            linked_parent = home / ".codex" / "hooks"
            destination = linked_parent / "guard.py"
            backup_root = home / "archive" / "before-apply"
            source.write_text("new\n", encoding="utf-8")
            outside_dir.mkdir()
            outside_file = outside_dir / "guard.py"
            outside_file.write_text("outside\n", encoding="utf-8")
            linked_parent.parent.mkdir(parents=True)
            linked_parent.symlink_to(outside_dir, target_is_directory=True)

            with self.assertRaisesRegex(RuntimeError, "symbolic link"):
                SYNC.copy_file_with_backup(source, destination, backup_root, home)

            self.assertEqual(outside_file.read_text(encoding="utf-8"), "outside\n")

    def test_apply_preflight_rejects_later_symlink_before_any_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            home = root / "target-home"
            source_one = root / "source-one.py"
            source_two = root / "source-two.py"
            destination_one = home / ".codex" / "hooks" / "one.py"
            destination_two = home / ".codex" / "agents" / "two.toml"
            outside_agents = root / "outside-agents"
            source_one.write_text("new one\n", encoding="utf-8")
            source_two.write_text("new two\n", encoding="utf-8")
            destination_one.parent.mkdir(parents=True)
            destination_one.write_text("old one\n", encoding="utf-8")
            outside_agents.mkdir()
            destination_two.parent.parent.mkdir(parents=True, exist_ok=True)
            destination_two.parent.symlink_to(outside_agents, target_is_directory=True)

            with self.assertRaisesRegex(RuntimeError, "symbolic link"):
                SYNC.validate_apply_plan(
                    home,
                    [
                        (source_one, destination_one),
                        (source_two, destination_two),
                    ],
                    home / ".codex" / "hooks.json",
                )

            self.assertEqual(destination_one.read_text(encoding="utf-8"), "old one\n")
            self.assertFalse((home / "codex-migration-archive").exists())

    def test_apply_preflight_rejects_symlink_backup_archive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            home = root / "target-home"
            source = root / "source.py"
            destination = home / ".codex" / "hooks" / "guard.py"
            outside_archive = root / "outside-archive"
            source.write_text("new\n", encoding="utf-8")
            destination.parent.mkdir(parents=True)
            outside_archive.mkdir()
            (home / "codex-migration-archive").symlink_to(
                outside_archive, target_is_directory=True
            )

            with self.assertRaisesRegex(RuntimeError, "symbolic link"):
                SYNC.validate_apply_plan(
                    home,
                    [(source, destination)],
                    home / ".codex" / "hooks.json",
                )

    def test_retired_hook_paths_are_scoped_to_target_home(self) -> None:
        home = Path("/tmp/profile-home")

        paths = SYNC.retired_hook_paths(home)

        self.assertTrue(paths)
        self.assertTrue(all(path.is_relative_to(home) for path in paths))
        self.assertIn(home / ".codex/hooks/smart_commit_stage.py", paths)
        self.assertIn(
            home / ".codex/hookify/warn-useful-next-steps-on-stop.md",
            paths,
        )

    def test_portable_apply_pairs_do_not_include_smart_commit(self) -> None:
        pairs = SYNC.apply_pairs(Path("/tmp/profile-home"))

        names = {src.name for src, _ in pairs}
        self.assertNotIn("smart_commit_stage.py", names)
        self.assertNotIn("test_smart_commit_stage.py", names)
        self.assertNotIn("smart-commit.md", names)


if __name__ == "__main__":
    unittest.main()
