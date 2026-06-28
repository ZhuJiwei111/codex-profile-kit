# Codex Profile Kit

这是个人 Codex 配置的可迁移快照仓库。它只保存可同步、可审计的 profile
资产，不保存本机运行状态。

## 包含内容

- `rules/AGENTS.portable.md`：可迁移的 Codex 行为规则。
- `skills/`：非系统 Codex skills 和 `.agents/skills` 中的可迁移 skill。
- `hooks/`：native hook 脚本、Hookify 规则和 hook 文档。
- `templates/`：`hooks.json`、`config.toml`、目标机器本地信息模板。
- `scripts/sync.py`：从本机导出、校验、审计差异和安全应用的统一入口。

## 不包含内容

仓库不会保存 `auth.json`、session/history、SQLite state、attachments、cache、
plugin cache、memories、project trust、hook trusted hashes、conda 环境、数据集、
模型权重或 `*.tar.gz` 导出包。

## 常用命令

```bash
python3 scripts/sync.py audit
python3 scripts/sync.py export --dry-run
python3 scripts/sync.py export
python3 scripts/sync.py verify
python3 scripts/sync.py push --confirm
python3 scripts/sync.py apply
```

`apply` 默认只做 dry-run。要写回当前机器，必须显式使用 `--confirm`，并且脚本会
先把将覆盖的文件备份到 `~/codex-migration-archive/`。

## 同步原则

本机 active 配置是长期真源；这个仓库是可迁移快照。遇到 `AGENTS.md`、
`config.toml`、host facts、敏感路径或运行状态冲突时，先审计并让用户判断，不
做静默覆盖。
