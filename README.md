# Codex Profile Kit

这是个人 Codex 配置的机器无关快照，目标是在另一台主机上让 Codex 快速恢复同一套
个性化工作方式，而不是复制整台机器的运行状态。

## 管理边界

仓库只同步：

- `rules/AGENTS.portable.md` → 完整的 `~/.codex/AGENTS.md`
- `skills/codex/personal-*` → 个人 workflow skills
- `hooks/scripts/` 与 `templates/hooks.json.template` → 原生 Codex hook 实现、测试和 wiring

仓库明确不管理非 `personal-*` skills（例如 `awesome-rebuttal`）、custom agent
profiles、`HOST_LOCAL.md`、`config.toml`、认证/连接器状态、session/history、trust
hash、cache、memories、环境、数据集或模型权重。目标机已有的非 personal skills 和
其他未受管内容会保留，也不算 drift。

## 四个动作

`scripts/sync.py` 需要 Python 3.11+；通常直接让 Codex 选择项目或
`HOST_LOCAL.md` 中记录的可用解释器。

```bash
python3 scripts/sync.py audit
python3 scripts/sync.py export --dry-run
python3 scripts/sync.py export
python3 scripts/sync.py apply
python3 scripts/sync.py apply --confirm
python3 scripts/sync.py audit
```

- `audit`：只读比较当前仓库与本机 active profile。
- `export`：把本机当前存在的受管配置保守地 overlay 到本地仓库；不会执行 Git
  操作，也不会因本机缺失而删除 repo-only personal skill 或 hook script。
- “同步到 GitHub”：`export` 后验证并审阅精确 diff，再按明确授权提交/推送。
- “从 GitHub 同步”：先让 Codex 安全更新本地仓库到选定 revision，再运行 apply
  dry-run、带备份的 confirmed apply 和 post-audit。仅 pull 仓库不等于更新本机
  Codex 配置。

dry-run 只描述当次状态；`--confirm` 会重新计算目标。confirmed apply 在
`~/codex-migration-archive/` 建立时间戳备份后事务替换受管内容，失败时回滚。
`templates/hooks.json.template` 始终由仓库维护，export 不会从本机已渲染的
`~/.codex/hooks.json` 反向生成它。因此，仓库有意保留而本机尚未 apply 的条目会继续
出现在 inbound audit 中。

## 退役与保留

本次 profile 明确退役 `personal-review-response`、旧 `monitor.toml` /
`reviewer.toml` custom agents，以及 Hookify Markdown adapter。confirmed apply 会先
备份再清理这些精确路径；普通“仓库中不存在”不会被解释为删除其他本机 skill。
该清理可重复执行，且不会触碰同目录中的未受管文件。

## 安全说明

同步会拒绝受管路径中的符号链接、特殊文件和已知敏感/runtime 文件名，并验证
skill 资源链接和显式 hook inventory；它不替代对最终 Git diff 的秘密检查。
`hooks.json` 定义变更后，必须由用户在 `/hooks` 中检查并信任新的精确 hash。

详细迁移步骤见 [INSTALL.md](INSTALL.md)，边界清单见
[MIGRATION_MANIFEST.md](MIGRATION_MANIFEST.md)。
