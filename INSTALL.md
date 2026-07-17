# Install Guide

For routine migration, ask Codex to execute this guide in the repository. Codex
should preserve unrelated work and stop if Git integration or the apply preview
needs a decision.

`scripts/sync.py` requires Python 3.11 or newer. In the commands below,
`python3` is a placeholder for the interpreter resolved by Codex. If the default
is older, Codex should read `~/.codex/HOST_LOCAL.md` and use its documented
fallback; the user normally does not need to locate an environment manually.

## 1. Get The Snapshot

For a new clone:

```bash
git clone https://github.com/ZhuJiwei111/codex-profile-kit.git
cd codex-profile-kit
python3 scripts/sync.py verify
```

For an existing clone, have Codex inspect the branch and dirty state, fetch the
remote, and integrate the selected upstream revision according to the current
branch policy. The synchronization script does not pull, commit, or push Git
history.

## 2. Keep Host State Local

Use `templates/HOST_LOCAL_TEMPLATE.md` only as a starting point for
`~/.codex/HOST_LOCAL.md`; preserve existing host facts and keep secrets out.
Treat `templates/config.toml.template` as a manual reference. Do not copy auth,
connector, MCP session, trust, or other runtime state from the source machine.

## 3. Preview, Apply, And Audit

```bash
python3 scripts/sync.py apply
python3 scripts/sync.py apply --confirm
python3 scripts/sync.py audit
```

The first command is a dry-run that reports the exact target list for the
repo/profile candidate at that moment; the CLI does not persist or bind that
result to `--confirm`. Codex must confirm that the repo/profile candidate
identity is unchanged and run `--confirm` immediately afterward; confirmation
recalculates the targets. Confirmed apply creates a timestamped backup under
`~/codex-migration-archive/`, then transactionally installs the managed payload.
It backs up and replaces the complete `~/.codex/AGENTS.md`, installs only
`personal-*` Codex skills, and applies the explicit hook and custom-agent
inventories. Existing non-personal Codex skills and `~/.agents/skills` remain
untouched and do not count as drift. The final audit should report zero drift.

Apply rejects symbolic-link path components below the target home and rolls
back a failed managed replacement. Review the preview before confirmation;
path containment does not make an unintended overwrite acceptable.

## 4. Finish Host-Local Setup

- Reconcile only the intended settings from `templates/config.toml.template`.
- Follow `CONNECTORS.md` and re-authenticate on the target machine.
- Review each applied custom agent's model, reasoning effort, and effective
  sandbox for this host.
- Run `/hooks`, inspect changed definitions, and trust only accepted hashes.

Some discovery or hook changes may require a new Codex task before they become
visible.
