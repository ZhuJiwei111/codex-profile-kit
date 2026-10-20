# External Skill Overlays

These patches preserve deliberate local adaptations to externally maintained
skills without making `profile_sync.py` install or partially manage their
upstream trees.

## awesome-rebuttal

- Upstream: `https://github.com/xiongqi123123/awesome-rebuttal`
- Base revision: `3434455fb2460b85793b4e3082bd28bf86ff7323`
- Patch: `awesome-rebuttal.patch`
- Reviewed: 2026-07-26

Recovery requires an independently reviewed checkout of the exact base
revision. From that checkout:

```bash
git apply --check <profile-repo>/external-overlays/awesome-rebuttal.patch
git apply <profile-repo>/external-overlays/awesome-rebuttal.patch
```

The patch makes invocation manual-only, preserves explicit Git and questionnaire
authority, and fixes capability paths. Re-review the upstream diff and update
the recorded base revision before rebasing the overlay.

## 本机 skill 路由精简（2026-10-20）

`skill-routing-20261020.patch` 仅修改两个外部 skill 的入口：
`paper-spine` 改为手动调用，
`academic-research-suite`（本机适配包 0.1.22，ARS 3.19.0）收窄自动路由；显式 ARS 请求保留其原有子工作流。
`clarify-before-action` 已退役，由 manifest 精确移除，不再保留补丁。
这些完整 skill 树不由 profile sync 管理；补丁不安装依赖、不替换脚本、
不启用 hook。更新后须先核对补丁上下文，不能对新版本盲目重放。

从本机 `~/.codex/skills` 检查补丁用 `git apply --check <补丁绝对路径>`；
获授权后用 `git apply <补丁绝对路径>`，恢复用 `git apply -R <补丁绝对路径>`。
不要在 profile 仓库根运行。受管调试已统一为 personal-evidence-debugging。

旧 `hatch-pet` 保存于 `archive/20261020-skill-cleanup/hatch-pet/`，
manifest 将其列为精确退役项；恢复时先撤销该 retirement，再独立审阅旧技能。

### 其他上游判断：2026-10-20

- ARS 的真正更新源是
  [academic-research-skills-codex](https://github.com/Imbad0202/academic-research-skills-codex)，
  而非把 Claude 版本直接覆盖到本机。2026-10-16 发布的 3.23.1
  相比本机适配包 0.1.22（ARS 3.19.0）增加 sr-screener，并修复 CSV 导入；
  上游仍明确不声称已验证 Codex 模型效果。保留为系统综述、元分析和实验方案入口，
  后续单独比较升级；本批收窄自动路由，不引入新流程、provider 或模型配置。
- PaperSpine 的来源由本机 updater 中的
  `WUBING2023/PaperSpine` URL 取证确认；无法从本机目录确定完整包版本。
  [当前上游](https://github.com/WUBING2023/PaperSpine)
  已转向 PaperSpine5、v0.4.0-alpha.3 完整平台套件、Web 工作台和运行时，
  含调用时自动更新。它属于产品迁移，不能当作旧 skill 的原地文本更新；
  本批保留旧文件并改为手动，不运行旧 updater 或新安装器。
- 本机 `personal-*` 的 source-notes 是设计来源记录；
  这些已重写为本地工作流，不与其引用的社区仓库保持逐文件同步。
  更新判断应保留实际改错经验和当前授权边界，不用新上游覆盖本地契约。
