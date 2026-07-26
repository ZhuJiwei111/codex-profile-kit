# Codex Profile Kit

这是个人 Codex 配置的机器无关权威源。永久流向只有：

```text
portable Git working tree → current host CODEX_HOME
```

active profile 不是反向导出源。

## 管理范围

- `profile/`：按目标相对路径保存 `AGENTS.md`、人工 memory、两个 hooks 和
  personal skills。
- `profile-manifest.toml`：列出受管 file/tree 和经过审阅的精确退役
  file/tree；除这些退役项外，相邻的外部 skill、plugin cache 和未列出文件不受
  影响。
- `personal.config.toml`：只投影脚本内显式允许的配置叶子键。
- `profile/hooks.json`：以占位符保存机器无关 wiring；同步时把运行
  `profile_sync.py` 的同一个 Python 绝对路径渲染到活动定义。
- `external-overlays/`：记录经审阅的第三方 skill 本地补丁与精确上游 revision；
  不由 profile sync 自动安装或部署。
- `archive/`：保留本次重构前的旧实现，不部署到 active profile。

仓库不管理 `HOST_LOCAL.md`、连接合同、credentials、auth/session/history、
trust、cache、plugin 安装或认证、MCP、sandbox、TUI、项目配置和其他未列出的
`config.toml` 键。

## 使用

需要 Python 3.11+、当前 Codex CLI，以及 `HOST_LOCAL.md` 中记录的
`codex-tools` 环境。先把该主机的准确解释器设为 `PROFILE_PYTHON`，并在同一轮
`preview/check/apply` 中保持不变：

```bash
PROFILE_PYTHON=/absolute/path/from/HOST_LOCAL
"$PROFILE_PYTHON" scripts/profile_sync.py preview
"$PROFILE_PYTHON" scripts/profile_sync.py check
"$PROFILE_PYTHON" scripts/profile_sync.py apply
```

- `preview`：显示解析后的官方 `$CODEX_HOME`、hook runtime 和精确
  add/change/delete，存在 drift 仍返回 0。
- `check`：完全一致才返回 0。
- `apply`：重新计算 diff；有变更时建立
  `${CODEX_HOME}.profile-sync-backups/<timestamp>/`，逐 leaf 原子替换，配置最后
  通过 `config/batchWrite` 写入，随后检查；失败时尽力恢复本批已改目标。调用
  `apply` 本身就是本机部署授权。
- manifest 中的精确退役项会显示为 `DELETE`，并与普通变更一样先进入上述备份；
  仓库中普通文件或 skill 的缺失不会触发删除。

脚本不提供 target override、active→repo export、Git、JSON 输出、备份清理或永久
远程 fan-out。备份不会自动删除。

## 修改与 Git

直接修改 portable 源。新变更在部署前：

1. 运行聚焦检查和 `preview`；
2. 审阅精确 diff；
3. 精确 stage task-owned paths，并创建 factual local commit；
4. 从该 commit 执行 `apply` 和 `check`。

只有用户明确要求“提交/同步到 GitHub”时才 non-force push；工具不会自动创建 PR。
从 GitHub 更新时，先检查本地状态并取得一个明确、无冲突的 portable revision，再
执行 preview/apply。

## 验证

```bash
PYTHONDONTWRITEBYTECODE=1 \
  "$PROFILE_PYTHON" \
  -m unittest discover -s tests -p 'test_*.py'
```

Hook definition 改变后，现有 task 仍可能使用启动时加载的旧 definition。先部署新
definition 和 runner，在 fresh task 中通过 `/hooks` 审阅 trust 并做 dispatch
检查，再删除仍被旧 task 使用的 runner。Profile sync 不复制或修改 trust state。
