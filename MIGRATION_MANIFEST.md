# Migration Manifest

## Managed Payload

- `rules/AGENTS.portable.md`: 完整替换 `~/.codex/AGENTS.md`。
- `skills/codex/personal-*`: 仅个人 Codex workflow skills。
- `hooks/scripts/`: 原生 hook handlers 及其行为测试。
- `templates/hooks.json.template`: 仓库拥有的 wiring，apply 时渲染为
  `~/.codex/hooks.json`；export 不从 active 文件反向生成它。

目标机上的非 personal Codex skills、host-only personal additions 和其他未受管
文件会保留并排除在 drift 之外。

## Explicit Retirements

confirmed apply 会先备份、再删除以下精确 active-profile 路径；重复执行是 no-op：

- `.codex/skills/personal-review-response`
- `.codex/skills/personal-context-compression`
- `.codex/skills/personal-context-optimization`
- `.codex/skills/personal-context-save-restore`
- `.codex/skills/personal-docs-sync-light`
- `.codex/skills/personal-long-job-status`
- `.codex/skills/personal-repo-intake`
- `.codex/agents/monitor.toml`
- `.codex/agents/reviewer.toml`
- `.codex/hookify/README.md`
- `.codex/hookify/block-base-conda-install.md`
- `.codex/hookify/block-sensitive-file-edits.md`
- `.codex/hookify/block-sensitive-path-command.md`
- `.codex/hooks/hookify_codex_runner.py`
- `.codex/hooks/test_hookify_codex_runner.py`

该列表不是通用 tombstone 机制；仓库中普通文件或 skill 的缺失不会触发本机删除。
若当前 task 已缓存将被退役的 hook command，应把 confirmed apply 放在该 task 的
工具阶段末尾，并由 fresh bounded executor 完成最终 zero-drift audit。

## Repository References

- `templates/HOST_LOCAL_TEMPLATE.md`: host-local facts 起点。
- `templates/REMOTE_CONNECTION_EXAMPLE.md`: 不含凭据的连接示例。
- `templates/config.toml.template`: 不自动应用的配置参考。
- `INSTALL.md`: 仓库更新、preview、confirmed apply 和 post-audit 流程。
- `CONNECTORS.md`: 目标机重新连接清单。

## Host-Local Or Excluded

- `HOST_LOCAL.md`、`config.toml`、custom agent profiles、连接约定、认证、tokens、
  cookies、connector/MCP session 和 hook trust state。
- session/history、logs、attachments、SQLite、goals、memories、plugin/app cache、
  marketplace clone 和 project trust。
- 环境、package cache、数据集、模型权重、项目输出和机器专用工具。
