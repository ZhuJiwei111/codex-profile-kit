# Nature Skills

- Upstream: `https://github.com/yuan1z0825/nature-skills`
- Revision: `703c150ec6b3d7885dc93aa0232a6b7fdd6686ed`
- Imported: 2026-08-08
- License: Apache-2.0; see [LICENSE](./LICENSE). Individual imported trees may
  retain additional bundled license notices.

The portable profile vendors the 18 `nature-*` child skills installed from this
revision plus upstream `nature-proposal-writer`, which is installed under
`profile/skills/researchwrite/` to match its `name: researchwrite` frontmatter.
The local `$personal-nature` router is maintained separately under
`profile/skills/personal-nature/`.

The imported snapshot was matched against the local installation using every
skill's Git tree hash recorded in `~/.agents/.skill-lock.json`. Local
post-install integration changes are retained: six skill frontmatters normalize
version and author fields under `metadata`, and every child has Codex
`agents/openai.yaml` metadata with `allow_implicit_invocation: false`. Portable
profile contract metadata adds missing display names and short descriptions.

The child skills include executable Python, MJS, and shell helpers. Some routes
can access literature services, institution-authorized browser sessions,
credential configuration, OpenRouter image generation, or recurring delivery.
They remain explicit-only, and the portable profile's authority, credential,
networking, external-write, and persistent-job rules take precedence.

To update the snapshot, inspect a new exact upstream revision, compare it with
the retained local integration changes, replace the complete imported trees,
reapply only reviewed integration metadata, update this record and license if
needed, then run the repository contract tests and profile preview.

## 上游复核与本地适配：2026-10-20

完整 vendored 基线仍为上述 revision；对上游
`c8599197e7d2a22c2a091bbf8c14efcb3625cfa0` 的 19 个 child/proposal
入口逐一比较，更新 16 个更短、更明确的触发描述；三个语义未变的描述
保持原样，避免纯格式改动。详细取舍见
[逐项复核记录](../skill-review-20261020.toml)。

选择性适配 reader 的节选/问答范围、citation 的 Nature/CNS 适用边界、
researchwrite 的 proposal 定位、figure 的现有后端与显式 provider 选择、
reviewer 的按需多视角输出。保留已有脚本、静态参考和全部 explicit-only 策略；
未宣称完整升级到各 child 最新版或运行时已验证。共享依赖仍按原树保留。

不启用 SessionStart 自动更新，不隐式安装依赖或注册外部 MCP/provider，
不把巡检、浏览器授权或定期投递当成内容请求的默认步骤。官方产物工具仍负责
其原生文档/演示生命周期，专门的论文叙事、证据和版式指导不应取代工具契约。
