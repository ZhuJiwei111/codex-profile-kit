# Install Guide

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
It also validates personal-skill UI metadata, in-skill relative resource links,
and the aggregate 6,000-character personal description budget.

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
