# Matt Pocock Skills

- Upstream: `https://github.com/mattpocock/skills`
- Version: `v1.2.3`
- Imported: 2026-08-08
- License: MIT; see [LICENSE](./LICENSE).

The portable profile retains 24 of the promoted skills listed by the upstream
`.claude-plugin/plugin.json` at this version; `resolving-merge-conflicts` is
archived under `archive/20261020-skill-cleanup/`. They are stored as independent
managed trees under `profile/skills/` so `profile_sync.py` can deploy them to
Codex without installing the upstream Claude plugin or the experimental
`in-progress` and `misc` buckets.

The pinned baseline is retained with reviewed Codex/local adapters. Current
routing, authority, verification and glossary-owner changes are recorded per
skill in [the 2026-10-20 review](../skill-review-20261020.toml). These are not a
claim that the complete v1.3.1 package or its executable helpers was installed.
Existing licenses and supporting reference files remain in place.

Invocation policy is owned by `agents/openai.yaml`. Claude-only
`disable-model-invocation` and `argument-hint` frontmatter keys have been removed;
manual skills remain `allow_implicit_invocation: false`. Local Git, external
write, credential and resource authority continues to govern every workflow.

To update them, review a new exact upstream tag, replace the complete promoted
set from that tag, update this version record and license if needed, then run
the repository contract tests and profile preview before committing.

## 上游核对：2026-10-20

本机仍固定 `v1.2.3`；最新已发布版本为
[`v1.3.1`](https://github.com/mattpocock/skills/releases/tag/v1.3.1)，
对应 commit `24fe0ef7737efae15c87225755e9f6f5965e4888`。
上游移除了 `resolving-merge-conflicts`，认为模型无需专用流程即可处理；
将术语文件约定从 `CONTEXT.md` 改为 `GLOSSARY.md`；
以明确的 Skill tool 调用替换 slash 指令；新增 `implement-spec`、`pr`、`retro`。

`resolving-merge-conflicts` 已归档，`ask-matt` 已移除该引用并缩为按需路由。
其余内容不整包升级：新增整规格并行实现、PR 和复盘流程不属于本次精简目标；
已选择性吸收适用的入口更新，清理原有固定编排和宿主假设。保留 `tdd`、`codebase-design`、
`domain-modeling`、`writing-for-agents` 的专用价值；普通任务不必套用完整编排。
`diagnosing-bugs` 保持手动；完整逐项取舍和社区问题依据见上述 review。
