# Codex Profile Kit

这是个人 Codex 配置的机器无关快照。仓库只管理边界明确、可审计的 profile
资产；主机事实、认证信息和运行状态留在目标机器。

## 同步范围

`export`、`audit` 和 `apply` 只管理以下 active profile 资产：

- `rules/AGENTS.portable.md`：完整的机器无关 `~/.codex/AGENTS.md`。
- `skills/codex/personal-*`：个人 Codex workflow skills。
- `hooks/`：脚本、受控 Markdown 规则、测试和 wiring 的显式 inventory。
- `agents/codex/`：显式 inventory 中的 custom Codex agent profiles。

`templates/`、`INSTALL.md` 和 `CONNECTORS.md` 是迁移参考，不是 active 配置的
逐字段镜像。仓库不会导出或应用 `~/.agents/skills`，也不会管理任何不以
`personal-` 开头的 Codex skill。目标机已有的这些 skill 会被保留，并排除在 drift
判断之外。

仓库不保存 `HOST_LOCAL.md`、`config.toml`、连接器或 MCP 认证、`auth.json`、
session/history、SQLite state、attachments、cache、memories、project trust、hook
trusted hashes、环境、数据集、模型权重或导出压缩包。

## 入站同步

`scripts/sync.py` 需要 Python 3.11+。下文的 `python3` 只是 Codex 已解析出的
interpreter 占位符；若默认 Python 低于 3.11，Codex 应读取
`~/.codex/HOST_LOCAL.md` 并使用其中记录的 fallback，用户通常无需手工寻找环境。

通常直接让 Codex 在本仓库中完成同步：先检查当前分支和未提交改动，再 `fetch`
并按仓库策略整合选定的上游 revision；随后连续运行：

```bash
python3 scripts/sync.py apply
python3 scripts/sync.py apply --confirm
python3 scripts/sync.py audit
```

第一条 dry-run 给出当时 repo/profile candidate 的 exact target list；CLI 不会保存
或绑定这份结果。Codex 必须确认 repo/profile candidate identity 未变并紧接着运行
`--confirm`，后者会重新计算目标。确认后的 apply 会先在
`~/codex-migration-archive/` 下建立带时间戳的整文件备份，再事务替换受管资产；
其中 `~/.codex/AGENTS.md` 会由 portable 文件完整替换，而不是局部合并。最后的
audit 应报告 zero drift。Git 整合由 Codex 或用户显式完成；`sync.py` 不会隐式
pull、commit 或 push。

`HOST_LOCAL.md`、`config.toml`、连接器、认证和其他 runtime state 始终由目标机
手工维护。参见 [INSTALL.md](INSTALL.md) 和 [CONNECTORS.md](CONNECTORS.md)。

## 出站同步

标准链是 `audit` → 一次 mutating `export`（内部构造并验证 candidate）→ 审阅
exact Git diff：

```bash
python3 scripts/sync.py audit
python3 scripts/sync.py export
```

Codex 随后按 export 报告的精确受管路径检查 `git diff`。可选的只读
`export --dry-run` 只比较 invocation 当时的状态；它不会成为后续 export 的持久或
绑定 plan，后续 export 仍会重新构造并验证 candidate。验证或替换失败会保留原状态
或回滚。暂存、提交和发布需要另行明确授权。兼容命令 `sync.py push` 始终 fail
closed，不执行发布。

## 安全边界

代码会拒绝已知敏感路径、文件类型和符号链接，并检查受管 inventory 与相对资源
引用；它不提供通用的内容级秘密扫描。内容级秘密由 outbound 后的 exact Git diff
review 负责。apply 拒绝沿 `--home` 下的符号链接路径写入，覆盖前保留整文件备份，
并在事务失败时回滚。这些保证不等同于断电级多路径原子性。

Hook 仍需审阅源码、wiring 和目标机 trust；custom agent 的模型、reasoning effort
和有效 sandbox 也需在目标机核对。`templates/config.toml.template` 只是手工参考，
不会固定主进程模型或自动改写目标机配置。
