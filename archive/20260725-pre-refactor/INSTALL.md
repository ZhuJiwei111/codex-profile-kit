# Install Guide

建议直接让 Codex 在本仓库中执行迁移。Codex 应保留无关改动，并在 Git 整合或
apply preview 出现歧义时停下确认。

## 1. 获取或更新仓库

新主机：

```bash
git clone https://github.com/ZhuJiwei111/codex-profile-kit.git
cd codex-profile-kit
python3 scripts/sync.py verify
```

已有 clone：让 Codex 检查分支、dirty state 和 remote 后，安全整合选定的上游
revision。`sync.py` 本身不执行 pull、commit 或 push。

## 2. 保留本机状态

`templates/HOST_LOCAL_TEMPLATE.md` 只用于创建或整理本机
`~/.codex/HOST_LOCAL.md`；`templates/config.toml.template` 只是手工参考。不要从
源主机复制 auth、connector/MCP session、trust hash 或其他 runtime state。

## 3. 应用 active profile

```bash
python3 scripts/sync.py apply
python3 scripts/sync.py apply --confirm
python3 scripts/sync.py audit
```

第一条只预览当时的候选目标。确认仓库 revision 和 active profile 未发生变化后，
紧接着执行 `--confirm`；它会重新计算目标、在
`~/codex-migration-archive/` 创建完整备份，并事务安装 portable AGENTS、所有仓库
内 `personal-*` skills 和原生 hooks。最后的 audit 应为 zero drift。

confirmed apply 也会备份并清理 manifest 中列出的精确退役项。其他非 personal
skills、host-only personal additions 和未受管文件保持不变。符号链接目标会
fail closed；事务失败则恢复原内容。

一次性 Hookify 退役有一个时序边界：若当前 task 已加载将被删除的旧 hook command，
先完成所有其他工具操作，再执行 confirmed apply；最终 post-audit 交给加载新 wiring
的 fresh bounded worker/task。不要把临时兼容 shim 留作最终配置。

## 4. 完成本机步骤

- 仅在确有需要时手工协调 `templates/config.toml.template` 中的设置。
- 按 [CONNECTORS.md](CONNECTORS.md) 在目标机重新认证。
- 在 `/hooks` 中检查新的 hook definition，并只信任接受的 hash。
- 如 skill 或 hook discovery 尚未刷新，新建一个 Codex task 再验证。

Python 要求为 3.11+。若系统 `python3` 不满足，让 Codex读取
`~/.codex/HOST_LOCAL.md` 并使用其中记录的 fallback；无需把该路径写入 portable
配置。
