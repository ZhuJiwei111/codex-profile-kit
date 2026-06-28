# Install Guide

This flow is template-based. Inspect each step before enabling hooks on the
target machine.

## 1. Clone

```bash
git clone https://github.com/ZhuJiwei111/codex-profile-kit.git
cd codex-profile-kit
python3 scripts/sync.py verify
```

## 2. Fill Host Facts

```bash
cp templates/HOST_LOCAL_TEMPLATE.md HOST_LOCAL.md
```

Fill `HOST_LOCAL.md` with target-machine facts. Keep secrets out of it.

## 3. Install Portable Rules

Review `rules/AGENTS.portable.md`, then merge it into the target
`~/.codex/AGENTS.md`. Add only true target-machine facts from `HOST_LOCAL.md`.

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
copying portable skills, hooks, Hookify rules, hook docs, and rendered
`hooks.json`.

## 6. Reconnect Plugins

Use `CONNECTORS.md` as the checklist. Re-authenticate connectors on the target
machine instead of copying connector state.
