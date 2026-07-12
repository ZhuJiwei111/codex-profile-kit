#!/usr/bin/env python3
"""Focused tests for portable profile synchronization."""

from __future__ import annotations

import importlib.util
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
        docs_sync = (
            SYNC.REPO_ROOT
            / "skills/codex/personal-docs-sync-light/references/source-notes.md"
        ).read_text(encoding="utf-8")
        repo_intake = (
            SYNC.REPO_ROOT
            / "skills/codex/personal-repo-intake/references/source-notes.md"
        ).read_text(encoding="utf-8")
        code_docs = (
            SYNC.REPO_ROOT
            / "skills/codex/personal-code-documentation/references/source-notes.md"
        ).read_text(encoding="utf-8")
        subagent = (
            SYNC.REPO_ROOT
            / "skills/codex/personal-subagent-boundaries/references/source-notes.md"
        ).read_text(encoding="utf-8")

        self.assertIn("901fb94c0fb9ffc8cb2d8275d99622475f77f401", docs_sync)
        self.assertIn("upstream-derived", docs_sync)
        self.assertNotIn("ChrisWiles", docs_sync)
        self.assertIn("hybrid", repo_intake.lower())
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
        repo_intake = (
            skill_root / "personal-repo-intake/references/source-notes.md"
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
        self.assertIn("mutable, unpinned `main`", repo_intake)
        self.assertIn("not provenance evidence", repo_intake)

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

    def test_manual_only_skill_routes_require_explicit_invocation(self) -> None:
        skill_root = SYNC.REPO_ROOT / "skills" / "codex"
        grilling_meta = (
            skill_root / "personal-grilling/agents/openai.yaml"
        ).read_text(encoding="utf-8")
        status_meta = (
            skill_root / "personal-long-job-status/agents/openai.yaml"
        ).read_text(encoding="utf-8")
        triad_meta = (
            skill_root / "personal-triad-discussion/agents/openai.yaml"
        ).read_text(encoding="utf-8")
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

        for metadata in (grilling_meta, status_meta, triad_meta):
            self.assertIn("allow_implicit_invocation: false", metadata)
        self.assertIn("$personal-grilling", multiline_routing)
        self.assertIn("$personal-long-job-status", multiline_routing)
        self.assertIn("$personal-grilling", worktree_integration)
        self.assertIn("$personal-long-job-status", debugging)
        self.assertIn("$personal-long-job-status", branch_finish)
        self.assertIn("$personal-long-job-status", output_explainer)
        self.assertIn("$personal-triad-discussion", output_explainer)
        self.assertIn("ordinary", debugging.lower())
        self.assertIn("ordinary", branch_finish.lower())

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
            skill_root / "personal-docs-sync-light/SKILL.md",
            skill_root / "personal-context-save-restore/SKILL.md",
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

    def test_context_packet_writes_use_the_final_verification_gate(self) -> None:
        context_skill = (
            SYNC.REPO_ROOT
            / "skills/codex/personal-context-save-restore/SKILL.md"
        ).read_text(encoding="utf-8")

        self.assertIn("personal-risk-verification", context_skill)
        self.assertRegex(
            " ".join(context_skill.split()).lower(),
            r"(?:packet|write).{0,160}personal-risk-verification",
        )

    def test_portable_mcp_enablement_is_documented_as_normalization(self) -> None:
        template = SYNC.CONFIG_TEMPLATE.lower()
        connectors = SYNC.CONNECTORS.lower()

        self.assertIn("intentional portable", template)
        self.assertIn("normative", connectors)
        self.assertIn("enabled = true", template)


class PortableSkillTests(unittest.TestCase):
    def test_every_personal_skill_has_source_notes(self) -> None:
        root = SYNC.REPO_ROOT / "skills" / "codex"
        personal = sorted(path for path in root.glob("personal-*") if path.is_dir())

        self.assertEqual(len(personal), 25)
        for skill in personal:
            with self.subTest(skill=skill.name):
                source = skill / "references" / "source-notes.md"
                self.assertTrue(source.is_file(), source)
                self.assertIn("source", source.read_text(encoding="utf-8").lower())

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

    def test_renamed_context_skill_replaces_legacy_allowlist_entry(self) -> None:
        self.assertTrue(SYNC.is_portable_codex_skill("personal-context-save-restore"))
        self.assertFalse(SYNC.is_portable_codex_skill("context-save-restore"))

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

            with mock.patch.object(
                SYNC,
                "PERSONAL_SKILL_DESCRIPTION_BUDGET",
                8,
                create=True,
            ):
                with self.assertRaisesRegex(SystemExit, "description budget"):
                    SYNC.validate_skills(root)


class CustomAgentProfileTests(unittest.TestCase):
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
        effort: str = "low",
        sandbox: str = "read-only",
    ) -> Path:
        path = root / "agents" / "codex" / f"{name}.toml"
        path.parent.mkdir(parents=True, exist_ok=True)
        model = "gpt-5.6-sol" if name == "reviewer" else "gpt-5.6-terra"
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
                        'model = "gpt-5.6-terra"',
                        'model_reasoning_effort = "low"',
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
            for name, effort in (("monitor", "low"), ("reviewer", "high"), ("local-only", "medium")):
                path = source_root / f"{name}.toml"
                path.parent.mkdir(parents=True, exist_ok=True)
                model = "gpt-5.6-sol" if name == "reviewer" else "gpt-5.6-terra"
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
        self.assertIn(
            (
                home / ".codex/skills/context-save-restore",
                home / ".codex/skills/personal-context-save-restore",
            ),
            pairs,
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
            legacy = home / ".codex/skills/context-save-restore"
            successor = home / ".codex/skills/personal-context-save-restore"
            legacy.mkdir(parents=True)
            (legacy / "SKILL.md").write_text("legacy\n", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "successor"):
                SYNC.retire_renamed_skills([(legacy, successor)])

            self.assertTrue(legacy.is_dir())

    def test_verified_successor_retires_legacy_after_backup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "target-home"
            backup_root = home / "migration-archive" / "before-apply"
            legacy = home / ".codex/skills/context-save-restore"
            successor = home / ".codex/skills/personal-context-save-restore"
            source = SYNC.REPO_ROOT / "skills/codex/personal-context-save-restore"
            legacy.mkdir(parents=True)
            (legacy / "SKILL.md").write_text("legacy\n", encoding="utf-8")
            SYNC.copytree(source, successor)
            pairs = [(legacy, successor)]

            SYNC.backup_renamed_skills(pairs, backup_root, home)
            SYNC.retire_renamed_skills(pairs)

            self.assertFalse(legacy.exists())
            self.assertTrue(successor.is_dir())
            backup = backup_root / ".codex/skills/context-save-restore/SKILL.md"
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
