# Nature Skills

- Upstream: `https://github.com/yuan1z0825/nature-skills`
- Revision: `703c150ec6b3d7885dc93aa0232a6b7fdd6686ed`
- Imported: 2026-08-08
- License: Apache-2.0; see [LICENSE](./LICENSE). Individual imported trees may
  retain additional bundled license notices.

The portable profile vendors the 18 `nature-*` child skills installed from this
revision plus upstream `nature-proposal-writer`, which is installed under
`profile/skills/researchwrite/` to match its `name: researchwrite` frontmatter.
The local `$nature` router is maintained separately under
`profile/skills/nature/`.

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

## 上游核对：2026-10-20

当前安装基线不变。核对上游 HEAD
`c8599197e7d2a22c2a091bbf8c14efcb3625cfa0` 的 README 及四个入口：
`nature-reader`、`nature-polishing`、`nature-figure`、`nature-paper2ppt`。

- `nature-reader` 入口版本为 2.1.1，允许按用户指定范围回答或生成节选，
  不再将普通单篇论文问题强制扩展为完整双语 reader；这是值得优先吸收的修正。
- polishing、figure、paper2ppt 的触发描述更短、更清晰；
  polishing 明确区分已有文字润色与新章节/论证重建。
- figure 仍是有独立价值的科学绘图工作流；PPT 和双语阅读仍各有产物契约，
  不能仅因与官方文档/PPT 工具相邻就删除。共享包应随实际调用者保留。
- 上游支持选择性安装；其可选 SessionStart 自动更新与本仓库固定版本和
  本地适配所有权不兼容，本轮不启用。

本次只核对上述入口与安装建议，未审阅全量脚本/引用/资产差异，
因此不声称整套已审查或可直接升级。下次优先比较 reader 及其 shared 依赖，
保留所有 explicit-only policy，再决定定向更新；无需全量新增 skills。

来源：[上游 README](https://github.com/Yuan1z0825/nature-skills)、
[reader 入口](https://github.com/Yuan1z0825/nature-skills/blob/c8599197e7d2a22c2a091bbf8c14efcb3625cfa0/skills/nature-reader/SKILL.md)。
