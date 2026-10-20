# Matt Pocock Skills

- Upstream: `https://github.com/mattpocock/skills`
- Version: `v1.2.3`
- Imported: 2026-08-08
- License: MIT; see [LICENSE](./LICENSE).

The portable profile vendors the 25 promoted skills listed by the upstream
`.claude-plugin/plugin.json` at this version. They are stored as independent
managed trees under `profile/skills/` so `profile_sync.py` can deploy them to
Codex without installing the upstream Claude plugin or the experimental
`in-progress` and `misc` buckets.

The imported workflow content is retained from upstream. The local Codex policy
for `diagnosing-bugs` is explicit-only as of 2026-10-20;
`personal-evidence-debugging` remains the automatic diagnosis entry. Local profile rules,
including explicit authority for Git commits, external writes, credentials,
heavy work, and repository changes, continue to take precedence over workflow
steps suggested by a vendored skill.

Upstream user-invoked skills retain the Claude-oriented
`disable-model-invocation` frontmatter key, which Codex's strict
`quick_validate.py` does not accept. Their Codex policy is carried by the
co-located `agents/openai.yaml`; the repository contract test verifies that
every such skill sets `allow_implicit_invocation: false`.

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

建议下一批归档 `resolving-merge-conflicts` 并同步修订 `ask-matt` 引用。
其余内容暂不整包升级：本机没有上游假设的 Skill tool，且新增整规格并行实现、
PR 和复盘流程不属于本次精简目标。保留 `tdd`、`codebase-design`、
`domain-modeling`、`writing-for-agents` 的专用价值；普通任务不必套用完整编排。
本批仅把 `diagnosing-bugs` 改为手动，未替换上游工作流或导入新技能。
