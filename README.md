# Codex Profile Kit

这是个人 Codex 配置的可迁移快照仓库。它只保存可同步、可审计的 profile
资产，不保存本机运行状态。

## 包含内容

- `rules/AGENTS.portable.md`：可迁移的 Codex 行为规则。
- `skills/`：非系统 Codex skills 和 `.agents/skills` 中的可迁移 skill。
- `agents/codex/`：经过明确 allowlist 的 custom Codex agent 执行配置。
- `hooks/`：native hook 脚本、受控的全局 Markdown 规则和对应测试。
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
先把将覆盖的文件备份到 `~/codex-migration-archive/`。apply 在读取或写入目标前
会拒绝 `--home` 之下的符号链接路径组件，避免沿链接越界覆盖；如果使用这种目录
共享方式，需要先改成真实目录并人工核对。`verify` 也会拒绝受管 snapshot 内的
符号链接，防止把跨目录引用迁移到目标 profile。

`export` 先在同一文件系统的临时候选副本中完成生成和 `verify`，随后只事务替换
受管入口。验证失败或正常替换异常时，live snapshot 保持不变或自动回滚；这不等
同于断电级多路径原子性。同一 live root 的并发 export 会通过进程锁 fail fast，
不会交错写入混合 snapshot。

Custom agent profile 会同步到 `~/.codex/agents/`。具体模型和 reasoning effort
属于执行配置，不代表主进程的固定档位；在目标主机应用前必须重新核对当前模型
目录和支持的 reasoning levels。Custom file 中的 `sandbox_mode` 也只是请求值，
当前任务的 live runtime override 可能覆盖它；安全关键的 read-only worker 必须
核对有效 sandbox。portable `config.toml` 模板不会固定主进程模型或 reasoning，
并保留 `agents.max_depth = 1` 的非递归委派默认值。

## 同步原则

本机 active 配置是长期真源；这个仓库是可迁移快照。遇到 `AGENTS.md`、
`config.toml`、host facts、敏感路径或运行状态冲突时，先审计并让用户判断，不
做静默覆盖。

Windows 控制平面可以在 active `~/.codex/AGENTS.md` 末尾追加一个由
`codex-remote-doc-pointer` markers 限定的受管远程运维指针。`export` 和
`audit` 只在该块成对、唯一且位于文件末尾时将其从 portable 视图中剥离；它们
不会修改 active 文件。无 marker、marker 损坏或位置错误的 host-local 指针仍会
被拒绝。`apply` 对 AGENTS 继续保持 manual review，不自动覆盖该文件。
