# Codex Profile Kit

这是个人 Codex 配置的可迁移快照仓库。它只保存可同步、可审计的 profile
资产，不保存本机运行状态。

## 包含内容

- `rules/AGENTS.portable.md`：可迁移的 Codex 行为规则。
- `skills/`：非系统 Codex skills 和 `.agents/skills` 中的可迁移 skill。
- `THIRD_PARTY_SKILLS.lock.json`：allowlist 第三方 Codex skill 的来源状态和
  精确内容摘要锁。
- `agents/codex/`：经过明确 allowlist 的 custom Codex agent 执行配置。
- `hooks/`：native hook 脚本、受控的全局 Markdown 规则和对应测试。
- `templates/`：`hooks.json`、`config.toml`、目标机器本地信息模板，以及只供
  人工审阅的静态 `REMOTE_CONNECTION_EXAMPLE.md`。
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
python3 scripts/sync.py apply
```

标准 outbound 发布路由是：`audit` → `export` → `inspect` →
`personal-risk-verification` → `github:yeet` handoff/draft pull request。也就是先
审计 active profile 与快照差异，生成候选快照并检查精确路径，再验证候选未变且
适合交接；最后由 `github:yeet` 独占发布流程。legacy `sync.py push` 只保留解析兼容，
始终 fail closed，不会执行导出、状态检查、暂存、提交或发布。

`apply` 默认只做 dry-run。要写回当前机器，必须显式使用 `--confirm`，并且脚本会
先把将覆盖的文件备份到 `~/codex-migration-archive/`。apply 在读取或写入目标前
会拒绝 `--home` 之下的符号链接路径组件，避免沿链接越界覆盖；如果使用这种目录
共享方式，需要先改成真实目录并人工核对。`verify` 也会拒绝受管 snapshot 内的
符号链接，防止把跨目录引用迁移到目标 profile；同时验证 personal skill 的 UI
metadata 与 source-notes、所有受管 skill 的相对资源链接，以及 managed catalog
descriptions 合计不超过 6,500 字符。allowlist 第三方 skill 还必须与
`THIRD_PARTY_SKILLS.lock.json` 的身份和完整内容摘要精确闭合；缺项、额外项或
内容漂移都会 fail closed。personal UI metadata 合同不扩展到 vendor skill。

`export` 先在同一文件系统的临时候选副本中完成生成和 `verify`，随后只事务替换
受管入口。验证失败或正常替换异常时，live snapshot 保持不变或自动回滚；这不等
同于断电级多路径原子性。同一 live root 的并发 export 会通过进程锁 fail fast，
不会交错写入混合 snapshot。

Hook 是受审阅的安全边界，不只依赖候选自带测试。`verify` 会在编译或执行候选 hook
代码前，先用 `scripts/sync.py` 中固定的 inventory 和 SHA-256 摘要核对脚本、规则、
测试及 wiring template；旧 active hook 不能用“旧代码 + 旧测试”自证通过。修改 hook
时应通过 hook-rule workflow 同时审阅 active 文件、portable snapshot、测试和摘要，
然后再运行 export；不要为通过导出而单独刷新摘要。

Custom agent profile 会同步到 `~/.codex/agents/`。具体模型和 reasoning effort
属于执行配置，不代表主进程的固定档位；在目标主机应用前必须重新核对当前模型
目录和支持的 reasoning levels。Custom file 中的 `sandbox_mode` 也只是请求值，
当前任务的 live runtime override 可能覆盖它；安全关键的 read-only worker 必须
核对有效 sandbox。portable `config.toml` 模板不会固定主进程模型或 reasoning，
并保留 `agents.max_depth = 1` 的非递归委派默认值。

## 同步原则

本机 active 配置是长期真源；这个仓库是可迁移快照。Hook 的受审阅摘要门禁是该
原则下的安全例外：active 变化仍需与 portable contract 一起审阅后才能导出。遇到
`AGENTS.md`、`config.toml`、host facts、敏感路径或运行状态冲突时，先审计并让
用户判断，不做静默覆盖。

当前路由固定为 portable `AGENTS.md` → active `HOST_LOCAL.md` 中的主机指针 →
active connection contract；portable `AGENTS.md` 不生成也不推荐连接 marker。
`codex-remote-doc-pointer` 仅保留为 `legacy compatibility`：`export` 和 `audit`
只在旧 marker 块成对、唯一且位于 active `AGENTS.md` 文件末尾时将其从 portable
视图中剥离，并且绝不生成该块或修改 active 文件。无 marker 的旧连接指针、损坏
marker 或位置错误的 marker 仍会被拒绝。`apply` 对 AGENTS 继续保持 manual
review，不自动覆盖该文件。
`templates/REMOTE_CONNECTION_EXAMPLE.md` 是仓库内唯一受审阅的静态连接示例；
它是 manual-only 的通用 schema，不含真实主机值或凭据。`export` 不读取 active
connection contract，`audit`、`verify` 和 `apply` 也不会备份、创建、覆盖或删除
该 active 文件。
