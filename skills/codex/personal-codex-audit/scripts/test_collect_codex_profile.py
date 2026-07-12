#!/usr/bin/env python3
"""Regression tests for the safe Codex profile collector."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("collect_codex_profile.py")
SPEC = importlib.util.spec_from_file_location("collect_codex_profile", MODULE_PATH)
assert SPEC and SPEC.loader
COLLECTOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(COLLECTOR)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class CollectorTests(unittest.TestCase):
    def test_frontmatter_keeps_only_top_level_keys(self) -> None:
        text = """---
name: nested-rule
enabled: true
conditions:
  - field: tool_input.command
    operator: regex_match
    pattern: secret-nested-pattern
---
"""
        parsed = COLLECTOR.parse_frontmatter(text)
        self.assertEqual(set(parsed), {"name", "enabled", "conditions"})
        self.assertNotIn("secret-nested-pattern", json.dumps(parsed))

    def test_profile_separates_configured_hooks_from_unreferenced_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            write(
                home / ".codex" / "config.toml",
                """[features]
hooks = true
memories = true

[[skills.config]]
path = "~/.codex/skills/disabled/SKILL.md"
enabled = false

[hooks.state]
trusted_hash = "TRUST_HASH_SENTINEL"
""",
            )
            write(
                home / ".codex" / "hooks.json",
                json.dumps(
                    {
                        "hooks": {
                            "PreToolUse": [
                                {
                                    "matcher": "^Bash$",
                                    "hooks": [
                                        {
                                            "type": "command",
                                            "command": f'python3 "{home}/.codex/hooks/guard.py"',
                                        },
                                        {
                                            "type": "command",
                                            "command": f'python3 "{home}/.codex/hooks/runner.py"',
                                        },
                                    ],
                                },
                                {
                                    "matcher": "^apply_patch$",
                                    "hooks": [
                                        {
                                            "type": "command",
                                            "command": f'python3 "{home}/.codex/hooks/runner.py"',
                                        }
                                    ],
                                },
                            ]
                        }
                    }
                ),
            )
            write(home / ".codex" / "hooks" / "guard.py", '"""Guard."""\n')
            write(home / ".codex" / "hooks" / "runner.py", '"""Runner."""\n')
            write(home / ".codex" / "hooks" / "test_guard.py", "assert True\n")
            write(
                home / ".codex" / "hookify" / "nested.md",
                """---
name: nested
enabled: true
event: file
action: warn
conditions:
  - field: tool_input.command
    operator: regex_match
    pattern: NESTED_PATTERN_SENTINEL
---
""",
            )
            write(home / ".codex" / "memories" / "MEMORY.md", "MEMORY_SECRET_SENTINEL")
            write(home / ".codex" / "auth.json", "AUTH_SECRET_SENTINEL")

            profile = COLLECTOR.collect_profile(home)
            serialized = json.dumps(profile, sort_keys=True)

            self.assertEqual(profile["schema_version"], 3)
            self.assertEqual(profile["scope"]["memory_content"], "not-collected")
            self.assertEqual(profile["config"]["hooks_feature"], "explicitly-enabled")
            self.assertEqual(profile["config"]["memories_feature"], "explicitly-enabled")
            self.assertEqual(len(profile["config"]["skills_config"]), 1)
            self.assertFalse(profile["config"]["skills_config"][0]["enabled"])
            self.assertEqual(profile["counts"]["hook_registrations"], 3)
            self.assertEqual(profile["counts"]["registered_hook_files"], 2)
            self.assertEqual(profile["counts"]["unreferenced_hook_files"], 1)
            self.assertTrue(all(item["configured"] for item in profile["hooks"]["registrations"]))
            self.assertTrue(all(item["trust_state"] == "not-collected" for item in profile["hooks"]["registrations"]))
            self.assertTrue(all(item["individual_enabled_state"] == "not-collected" for item in profile["hooks"]["registrations"]))
            self.assertNotIn("command", profile["hooks"]["registrations"][0])
            self.assertNotIn("matcher", profile["hooks"]["registrations"][0])
            self.assertNotIn("TRUST_HASH_SENTINEL", serialized)
            self.assertNotIn("MEMORY_SECRET_SENTINEL", serialized)
            self.assertNotIn("AUTH_SECRET_SENTINEL", serialized)
            self.assertNotIn("NESTED_PATTERN_SENTINEL", serialized)
            self.assertNotIn("^Bash$", serialized)
            self.assertNotIn('python3 "', serialized)

    def test_mcp_inventory_projects_only_safe_public_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            write(
                home / ".codex" / "config.toml",
                '''[mcp_servers.openaiDeveloperDocs]
url = "https://developers.openai.com/mcp"
enabled = true

[mcp_servers.envAuth]
url = "https://mcp.example.com/service"
bearer_token_env_var = "BEARER_ENV_SECRET_SENTINEL"

[mcp_servers.headerAuth]
url = "https://headers.example.com/mcp"
http_headers = { Authorization = "HEADER_SECRET_SENTINEL" }

[mcp_servers.oauthAuth]
url = "https://oauth.example.com/mcp"
auth = { access_token = "OAUTH_SECRET_SENTINEL" }

[mcp_servers.unsafeUrl]
url = "https://URL_USER_SECRET_SENTINEL@example.com/mcp?token=URL_QUERY_SECRET_SENTINEL#URL_FRAGMENT_SECRET_SENTINEL"

[mcp_servers.localUrl]
url = "https://127.0.0.1/mcp"

[mcp_servers.unlistedPublic]
url = "https://mcp.example.com/service"

[mcp_servers.localProcess]
command = "COMMAND_SECRET_SENTINEL"
args = ["ARG_SECRET_SENTINEL"]
env = { TOKEN = "ENV_SECRET_SENTINEL" }
enabled = false
''',
            )

            profile = COLLECTOR.collect_profile(home)
            servers = {item["id"]: item for item in profile["config"]["mcp_servers"]}
            serialized = json.dumps(profile, sort_keys=True)

            self.assertEqual(profile["schema_version"], 3)
            self.assertEqual(profile["counts"]["mcp_servers"], 8)
            self.assertEqual(
                servers["openaiDeveloperDocs"],
                {
                    "id": "openaiDeveloperDocs",
                    "enabled": True,
                    "transport": "streamable-http",
                    "public_url": "https://developers.openai.com/mcp",
                    "auth_mechanism": "none",
                },
            )
            self.assertEqual(servers["envAuth"]["auth_mechanism"], "env-var-name")
            self.assertEqual(servers["headerAuth"]["auth_mechanism"], "headers")
            self.assertEqual(servers["oauthAuth"]["auth_mechanism"], "oauth-or-runtime")
            self.assertNotIn("public_url", servers["unsafeUrl"])
            self.assertNotIn("public_url", servers["localUrl"])
            self.assertNotIn("public_url", servers["unlistedPublic"])
            self.assertEqual(servers["localProcess"]["transport"], "stdio")
            self.assertEqual(servers["localProcess"]["auth_mechanism"], "not-collected")
            self.assertFalse(servers["localProcess"]["enabled"])

            for sentinel in (
                "BEARER_ENV_SECRET_SENTINEL",
                "HEADER_SECRET_SENTINEL",
                "OAUTH_SECRET_SENTINEL",
                "URL_USER_SECRET_SENTINEL",
                "URL_QUERY_SECRET_SENTINEL",
                "URL_FRAGMENT_SECRET_SENTINEL",
                "COMMAND_SECRET_SENTINEL",
                "ARG_SECRET_SENTINEL",
                "ENV_SECRET_SENTINEL",
            ):
                self.assertNotIn(sentinel, serialized)
            for forbidden_key in (
                "bearer_token_env_var",
                "http_headers",
                "env_http_headers",
                "command",
                "args",
                "env",
                "auth",
            ):
                self.assertNotIn(f'"{forbidden_key}":', serialized)

    def test_limited_toml_projection_keeps_mcp_secrets_out(self) -> None:
        projection = COLLECTOR.limited_toml_projection(
            '''[mcp_servers.docs]
url = "https://developers.openai.com/mcp"
enabled = true
bearer_token_env_var = "LIMITED_BEARER_SECRET_SENTINEL"
http_headers = { Authorization = "LIMITED_HEADER_SECRET_SENTINEL" }
command = "LIMITED_COMMAND_SECRET_SENTINEL"
args = ["LIMITED_ARG_SECRET_SENTINEL"]
'''
        )
        serialized = json.dumps(projection, sort_keys=True)

        self.assertEqual(
            projection["mcp_servers"],
            [
                {
                    "id": "docs",
                    "enabled": True,
                    "transport": "unknown",
                    "auth_mechanism": "headers",
                }
            ],
        )
        self.assertNotIn("LIMITED_BEARER_SECRET_SENTINEL", serialized)
        self.assertNotIn("LIMITED_HEADER_SECRET_SENTINEL", serialized)
        self.assertNotIn("LIMITED_COMMAND_SECRET_SENTINEL", serialized)
        self.assertNotIn("LIMITED_ARG_SECRET_SENTINEL", serialized)

    def test_feature_defaults_are_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            write(home / ".codex" / "config.toml", "[features]\n")
            profile = COLLECTOR.collect_profile(home)
            self.assertEqual(profile["config"]["hooks_feature"], "default-enabled")
            self.assertEqual(profile["config"]["memories_feature"], "default-disabled")

    def test_explicitly_disabled_features_are_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            write(
                home / ".codex" / "config.toml",
                "[features]\nhooks = false\nmemories = false\n",
            )
            profile = COLLECTOR.collect_profile(home)
            self.assertEqual(profile["config"]["hooks_feature"], "explicitly-disabled")
            self.assertEqual(profile["config"]["memories_feature"], "explicitly-disabled")

    def test_missing_referenced_hook_is_configured_but_not_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            write(
                home / ".codex" / "hooks.json",
                json.dumps(
                    {
                        "hooks": {
                            "PreToolUse": [
                                {
                                    "matcher": "Bash",
                                    "hooks": [
                                        {
                                            "type": "command",
                                            "command": f'python3 "{home}/.codex/hooks/missing.py"',
                                        }
                                    ],
                                }
                            ]
                        }
                    }
                ),
            )
            profile = COLLECTOR.collect_profile(home)
            registration = profile["hooks"]["registrations"][0]
            self.assertTrue(registration["configured"])
            self.assertFalse(registration["definition_exists"])
            self.assertEqual(profile["counts"]["registered_hook_files"], 0)

    def test_unsupported_inline_toml_is_marked_partial(self) -> None:
        if COLLECTOR.tomllib is not None:
            self.skipTest("limited parser is used only when tomllib is unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            write(
                home / ".codex" / "config.toml",
                """[[hooks.PreToolUse]]
matcher = "Bash"
[[hooks.PreToolUse.hooks]]
type = "command"
command = '''python3 ./guard.py'''
""",
            )
            profile = COLLECTOR.collect_profile(home)
            self.assertEqual(profile["config"]["parse_status"], "partial")

    def test_invalid_hooks_json_is_reported_without_crashing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            write(home / ".codex" / "hooks.json", "{not-json")
            profile = COLLECTOR.collect_profile(home)
            self.assertEqual(profile["hooks"]["sources"][0]["parse_status"], "invalid-json")
            self.assertEqual(profile["counts"]["hook_registrations"], 0)

    def test_symlinked_skills_obey_home_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside_tmp:
            home = Path(tmp)
            inside_target = home / "skill-sources" / "inside"
            outside_target = Path(outside_tmp) / "outside"
            sensitive_target = home / ".ssh" / "sensitive"
            write(
                inside_target / "SKILL.md",
                "---\nname: inside\ndescription: Safe linked skill.\n---\n",
            )
            write(
                outside_target / "SKILL.md",
                "---\nname: outside\ndescription: Must not be read.\n---\n",
            )
            write(
                sensitive_target / "SKILL.md",
                "---\nname: sensitive\ndescription: Sensitive target must not be read.\n---\n",
            )
            skill_root = home / ".codex" / "skills"
            skill_root.mkdir(parents=True)
            (skill_root / "inside").symlink_to(inside_target, target_is_directory=True)
            (skill_root / "outside").symlink_to(outside_target, target_is_directory=True)
            (skill_root / "sensitive").symlink_to(sensitive_target, target_is_directory=True)

            profile = COLLECTOR.collect_profile(home)
            skills = {item["folder"]: item for item in profile["skills"]}

            self.assertEqual(skills["inside"]["metadata_status"], "read")
            self.assertEqual(skills["inside"]["name"], "inside")
            self.assertEqual(skills["outside"]["metadata_status"], "not-read")
            self.assertEqual(skills["outside"]["target_scope"], "outside-home")
            self.assertEqual(skills["sensitive"]["metadata_status"], "not-read")
            self.assertEqual(skills["sensitive"]["target_scope"], "sensitive-excluded")
            self.assertNotIn("Must not be read", json.dumps(profile))
            self.assertNotIn("Sensitive target must not be read", json.dumps(profile))


if __name__ == "__main__":
    unittest.main()
