# 本地 DS 独立审查原始最终回复

基于修改前的 SKILL.md 资料包及 manifest/AGENTS/HOST_LOCAL 模板；不包含全部参考文件、脚本或活动配置。原生最终回复从 handoff 表行开始，前段未出现在该最终字段中；不能充作完整逐项实现审计。无权限拒绝。下文原样保留，不据此自动采纳。

| `handoff` | 保留 | 17 行；`handoff:10` 明确“不关闭、不归档”，与 `task-archive` 边界清楚 | 不改；可加一句“研究项目交接优先复用 `personal-research-project`，这里只产出交接文档” |

结论：这 8 项没有需要合并的。`multiline` 的问题是范围蔓延，不是存在必要；`subagent` 与它按“交互所有权”分流是正确的。`task-archive`、`temporary-work`、`handoff` 分别对应产品历史、临时目录、未完成交接，不能合成一个“生命周期”大杂烩。

## 三、工程系列

不建议大合并。16 个 skill 看起来多，但大多是 15–60 行、manual-only、触发条件和产物都不同；合并会造出一个带模式的大 router，反而增加选择和审批成本。逐组判断：

| 组 | 技能 | 结论 | 依据 |
|---|---|---|---|
| 入口 | `ask-matt` | 保留 | manual router；`ask-matt:43-44` 已声明表内名称不是 slash command |
| 收敛 | `grilling`、`wayfinder`、`to-spec`、`to-tickets` | 全部保留 | 分别对应“压力测试决策”“大型不确定路线”“写规格”“拆票据”，产物不同 |
| 设计 | `codebase-design`、`domain-modeling`、`improve-codebase-architecture` | 全部保留 | `tdd:29` 和 `improve:8` 依赖 `codebase-design`；`domain-modeling` 管术语/ADR，`improve` 管评估 |
| 实现 | `implement`、`tdd`、`prototype` | 保留 | `implement` 是授权内实现；`tdd` 是测试优先模式；`prototype` 是一次性验证 |
| 审查 | `code-review`、`triage`、`personal-code-simplifier`、`personal-code-documentation`、`personal-evidence-debugging` | 保留 | 输入分别是 diff、issue/PR、明确清理范围、文档契约、异常证据；没有可安全合并的重叠 |
| 人工步骤 | `wizard`、`to-questionnaire` | 保留 | 产物分别是 bash 脚本和 Markdown 问卷 |
| 初始化 | `setup-matt-pocock-skills` | 可归档（条件） | 唯一职责是初始 tracker/glossary/ADR 配置；`domain-modeling:13-16` 已要求复用现有 owner，`code-review:18-19` 明确缺 tracker 配置不阻塞。若不再频繁开新仓库，这个 skill 没有独立价值 |

需要修的两处小缺陷：

1. `tdd:29` 写“use the `/codebase-design` skill”。Codex 不注册 slash command，`ask-matt:43-44` 也明确说表内名称不是 slash command。改为 `codebase-design` 或相对路径。
2. `personal-code-simplifier` 可以保留，但如果要进一步减面，可把它的规则并入 `implement` 的“behavior-preserving cleanup”段；当前不建议，因为它对“不改 prompt/模板/用户字符串”的约束有价值。

若归档 `setup-matt-pocock-skills`，唯一依赖是 `ask-matt:40` 的表行，删掉即可；没有其他 skill 引用它。

## 四、research / teach / researchwrite

| 技能 | 结论 | 依据与依赖 | 动作 |
|---|---|---|---|
| `research` | 保留 | 17 行；唯一“保存的引用研究笔记”轻量入口；`description` 已排除普通问答和快速文档搜索 | 不改 |
| `teach` | 条件保留，否则可归档 | 139 行，外加 `MISSION-FORMAT.md`、`RESOURCES-FORMAT.md`、`LEARNING-RECORD-FORMAT.md` 等 companion files；只有 `ask-matt:37` 引用；多会话学习工作区是特定需求 | 若保留，`description` 加 “Manual only”，并核实三个格式文件存在；若归档，删 `ask-matt:37` |
| `researchwrite` | 留待第 3 技能合并/归档，本轮不迁移 | 150 行 + 20 个 references；`41-61` 的 `state.json`、`00_scope.md`…`05_style_guide.md` 是第二套项目状态；`100-147` 的 QA/评分 pipeline 与项目记录、ARS academic-paper、nature-writing 重叠 | 本轮不动；第 3 技能设计时决定“只保留开题/研究计划模式并复用 project-journal”，或归档 |

`researchwrite` 的关键冲突不是“它写得不好”，而是它自建 `state.json` 和 `qa_logs/`，与 `AGENTS.md:124-127`“不要另建 file-backed plan”以及 `personal-research-project:23`“不新建独立 plan 状态体系”直接冲突。若保留，至少删掉 `state.json` 和评分状态，把项目事实交给 `personal-project-journal`。

## 五、ARS 是否适合默认处理全部研究请求

不适合。三条直接依据：

1. ARS 自己的 `description` 已经限定：“Ordinary paper translation, prose edits, figures, or mock review use their focused skills”（`academic-research-suite/SKILL.md:3-7`）。
2. ARS 自己的范围段更明确：“General literature discovery belongs to `nature-academic-search`; manuscript drafting, polishing, mock review and reviewer replies have focused `nature-*` entries”（同文件 `28-35`）。
3. `AGENTS.md:89-95` 却写“Default scientific research, literature review, academic writing, manuscript review, and experiment-planning requests to ARS”。这与 ARS 自己的分工相反，也会让轻量请求进入一个需要“先读 manifest、再选 workflow”的重型 suite（ARS:37-45）。

建议把 `AGENTS.md:89-95` 改成“显式优先 + 结果分流”，而不是新增一个 router 文件：

| 请求 | 默认 owner |
|---|---|
| 明确点名 `$skill`、`ars-*` 或现有工作流 | 该 skill，直接服从 |
| 系统综述、meta-analysis、研究问题收敛（socratic）、研究方案/可复现实验设计 | ARS，且只读一个 workflow |
| 一般文献发现、检索、文献管理 | `nature-academic-search` |
| 稿件起草/章节 | `nature-writing` |
| 开题/研究计划 | `researchwrite`（若保留）或 ARS proposal mode，第 3 技能再统一 |
| 润色/学术翻译 | `nature-polishing` / `personal-translate-paper-zh` |
| 模拟审稿 | `nature-reviewer`（第 4 技能前） |
| 审稿回复 | `nature-response` |
| 绘图 | `nature-figure`（第 5 技能前） |
| 引用支撑 / 参考文献审计 | `nature-citation` / `nature-ref-verifier` |
| 端到端论文 | `paper-spine`，仅显式请求 |

另外两个与 ARS 相关的真实问题：

- **可移植性缺口**：ARS 不在 `profile-manifest.toml` 的 `trees` 中（`8-63`），但 `AGENTS.md:90` 把它设为默认。若 ARS 不是由其他插件安装，`profile-sync.py apply` 不会部署它，新主机上的默认路由会指向不存在的 skill。要么把 `skills/academic-research-suite` 加进 manifest，要么明确它是 unmanaged external skill 并取消默认。
- **中文变体冲突**：`ARS:326` 默认 Traditional Chinese，`AGENTS.md:154` 只说“Use Chinese”。用户当前用简体中文；建议统一为简体，或让 ARS 跟随 `AGENTS.md` 的用户语言，而不是自己定繁简。

## 六、Nature 整套是否仍需保留

保留核心，但不把“手动启用”理解为“必须全部自动注册/默认”。`personal-nature` 是 manual router（`personal-nature:3`），只有显式 `$personal-nature` 才路由；子技能仍会按各自 description 被自动选中。整套保留的理由：

- `nature-shared` 是共享依赖，`nature-reader:67` 和 `nature-paper2ppt:52` 直接引用 `../nature-shared/core/terminology-ledger.md`，不能先归档。
- 第 3/4/5 技能会重做写作、润色、审稿、绘图；现有 `nature-writing`、`nature-polishing`、`nature-reviewer`、`nature-figure` 是重要输入材料，现在归档会迫使后续重新收集。
- 没有使用日志，不能判断哪些子技能真的不用；只能按职责判断。

条件归档候选，按优先级：

| 技能 | 判断 | 依据 |
|---|---|---|
| `nature-literature-pipeline` | 优先可归档 | 113 行；`55-59` 指示设置每日 cron、投递 Feishu/Telegram；与 `AGENTS.md:19-21`“本地工作不授权外部消息”和“持久任务需授权”冲突；只被 `personal-nature:37`、`nature-paper-card:153` 引用。若仍用 Hermes cron，则保留并补授权门 |
| `nature-experiment-log` | 合并候选，暂缓 | `nature-experiment-log:3,18-21` 已声明不维护 JOURNAL/TODO；它只做原始实验材料到 YAML 记录，和 `personal-project-journal` 的实验卡有重叠但边界清楚。等 journal 的模板覆盖 Obsidian 后再归档 |
| `nature-paper-to-patent` | 保留（条件） | 独立交付物，无其他技能依赖；只有不再做专利时归档 |
| `nature-paper2ppt` | 保留（条件） | 同上；组会/答辩 PPT 是独立交付物 |
| `nature-data` | 保留 | Data Availability/FAIR 是独立写作面，和 `nature-statistics` 不重叠 |

核心保留集：`nature-academic-search`、`nature-citation`、`nature-ref-verifier`、`nature-downloader`、`nature-reader`、`nature-paper-card`、`nature-writing`、`nature-polishing`、`nature-response`、`nature-reviewer`、`nature-figure`、`nature-statistics`、`nature-shared`、`personal-nature`。

三处重叠只需在 description 里写清 owner，不必现在合并：

- `nature-academic-search` 的 `citation-verification` 是快速核对；逐字段多源审计归 `nature-ref-verifier`（`nature-ref-verifier:22-55`）。
- `nature-citation` 是 Nature/CNS 期刊范围内的 claim-to-source 支撑；一般发现归 `nature-academic-search`（`nature-citation:20-23`）。
- `nature-reader` 与 `personal-translate-paper-zh` 已在 `nature-reader:20-25` 分流：前者是 source-mapped reader，后者是段落对齐双语翻译。

`nature-ref-verifier:55` 还有一处授权冲突：它说超过 20 条就“拆给并行子代理”，但没有加“仅在用户授权委派时”。应改为“若委派已授权”，与 `AGENTS.md:111-115`、`subagent:22-23` 一致。

## 七、翻译 skill

`personal-translate-paper-zh` 必须保留，本轮不动。它是 manual-only（`personal-translate-paper-zh:3`），有完整的 PDF 提取、图表截图、段落对齐、CJK 强调修复和 strict validator 契约；用户明确说常用。后续技能应把它作为“PDF 双语翻译”的唯一 owner 引用，而不是复制或替换。`personal-nature:48,64-66` 和 `nature-reader:20-25` 已经把这条边界写对了。

## 八、HOST_LOCAL 模板是否混入动态状态

是。模板本身是空 schema，没有写入具体值；但 schema 把若干动态/派生状态放进了“主机事实”，违反了 `AGENTS.md:3-6` 的“host facts 放 HOST_LOCAL、task state 放任务/仓库”和“已有事实不重复维护”。

| 行 | 字段 | 性质 | 判断 |
|---|---|---|---|
| `11` | Updated at | 维护元数据 | 偏好；若无人维护会误导，建议改 “Last reviewed” 或删除 |
| `12-16` | OS/架构/host ID/CODEX_HOME/profile repo | 持久事实 | 保留 |
| `20-24` | Python/conda/环境策略/standing install authority | 持久策略 | 保留 |
| `30` | Hook runtime interpreter | 持久配置投影 | 保留，但注明 `hooks.json` 是权威 |
| `31` | 不可修改的 runtime/plugin-cache 路径 | 持久策略 | 保留 |
| `32` | Fresh-task hook trust status and verification date | **动态产品状态** | 删除。`personal-codex-hook-rules:18` 明确“never edit persisted trust state”；trust 状态由 `/hooks` 拥有，复制到 HOST_LOCAL 会产生第二权威并很快过期 |
| `36-38` | 存储/CPU/GPU/可用性约束 | 半持久容量/策略 | 保留；容量变化时更新，不作为实时监控 |
| `45-47` | Proxy/SSH 别名/endpoint facts | 持久事实 | 保留别名和端点 |
| `47` | last bounded probe | **瞬态观测** | 删除或移到任务记录。探测结果不是主机事实，且会过期 |
| `48` | Saved project roots by host ID or project label | **动态注册表** | 删除，改为指针：连接目标归 `proj/.local/connections.json`（`personal-tencent-remote-execution:13`） |
| `52-54` | 本地安装/部署约定、需审批路径/服务 | 持久策略 | 保留。手动启用 Nature 这类“决定”放这里 |
| `59-61` | 0600/ACL 策略 | 持久策略 | 保留策略 |
| `61` | 记录“实际使用的 ACL 验证命令” | 一次性审计产物 | 删除或移到 setup 记录 |

具体可执行修改：

1. 在模板开头加一句：“本文件只记录无法从原生配置发现的持久主机事实和常设策略；运行状态、trust 决定、探测结果、项目注册表不复制到这里，指向其 owner。”
2. 删除 `HOST_LOCAL.template.md:32`。
3. 把 `:47` 的 “last bounded probe” 删掉，只保留别名/端点。
4. 把 `:48` 改成“连接/项目注册表：`proj/.local/connections.json`（或项目登记）”。
5. 删除 `:61` 的命令记录，只保留 0600/ACL 要求。
6. `:11` 改为“Last reviewed”或去掉；不要让一个过期日期看起来像权威。

区分：手动启用/信任某个扩展是**决定**，可留在 `Host-Specific Decisions`；当前 trust 状态是**运行时状态**，不复制。

## 九、真实缺陷清单

按影响排序；这些是建议修的不一致，不是风格偏好。

1. **ARS 默认路由过宽且自相矛盾**：`AGENTS.md:89-95` vs `academic-research-suite/SKILL.md:3-7,28-35`。收窄为“ARS 只做系统综述/元分析/RQ 收敛/研究方案，其他走聚焦 skill”。
2. **ARS 与 paper-spine 未纳入 manifest，却被默认/引用**：`profile-manifest.toml:8-63` 没有二者；`AGENTS.md:90` 默认 ARS，`academic-research-suite/SKILL.md:34` 把 PaperSpine 称为显式替代。若不由其他插件管理，这是部署缺口。
3. **HOST_LOCAL 动态字段**：`HOST_LOCAL.template.md:32,47,48,61`，见第八节。
4. **硬编码主机路径**：
   - `AGENTS.md:4` 写 `~/.codex/HOST_LOCAL.md`，应改为 `$CODEX_HOME/HOST_LOCAL.md`；`profile-sync:30-32` 和模板 `:15` 已使用 CODEX_HOME。
   - `personal-nature:19` 写 `~/.codex/skills/<folder>/SKILL.md`，应解析 `$CODEX_HOME`。
   - `personal-review-and-revise-paper:195` 写 `/usr/bin/python3`，应使用项目解释器或 `python3`。
   - `paper-spine:159-171` 写 `$env:USERPROFILE\.claude\skills\...` / `.codex`，并强制 `sandbox_permissions: require_escalated`；这与“低审批负担”冲突。它属于第 3 技能范围，本轮不迁移，但应确认是否属于 portable profile。
5. **第二套项目/资源状态**：
   - `researchwrite:41-61` 的 `state.json` 与 `personal-project-journal` 冲突。
   - `multiline:102-125` 的 GPU/ETA/资源表与 `tencent:38-52` 冲突。
   - `nature-experiment-log:18-21` 与 journal 的实验卡有重叠（边界已写，暂可接受）。
6. **SHA-256 冲突**：`AGENTS.md:49-53` 禁止 routine 计算/记录摘要；`nature-downloader:329` 的 manifest 明确写 `SHA-256`。要么在 AGENTS 加“外部工具自身格式要求的 digest 除外”，要么从 downloader manifest 去掉。
7. **中文变体冲突**：`AGENTS.md:154` 未定繁简；`ARS:326` 默认繁体。建议统一为简体或“跟随用户”。
8. **profile-sync 路径措辞**：`personal-profile-sync:16-17` 的 `profile/skills/<name>` 与 manifest 的 `skills/<name>` 不一致；若仓库确有外层 `profile/` 目录则不是缺陷，需核实。
9. **`tdd:29` 的 `/codebase-design` 斜杠写法**：Codex 不注册 slash command，改为普通名称。
10. **`nature-ref-verifier:55` 无条件建议并行子代理**：加“仅在委派已授权时”。
11. **`nature-literature-pipeline:55-59` 指示设置 cron/Feishu 投递**：若保留，必须加“需用户明确授权外部投递/持久任务”，与 `AGENTS.md:19-21` 一致。
12. **ARS 版本三处重复**：`academic-research-suite/SKILL.md:8-10,22-25` 要求 `VERSION`、SKILL metadata、`manifest.json` 三处一致；这是维护点，不是当前错误，但 profile-sync 应把版本校验纳入 check。

**证据缺口，不是缺陷**：bundle 缺少所有 `references/`、`scripts/`、`hooks.json`。`writing-for-agents:13-14`、`teach:10-18`、`codebase-design:116-118`、`prototype:18-19`、`tdd:18`、`wizard:10`、`ask-matt:49`、`task-archive:117,197`、`profile-sync:28-38` 都依赖 companion files；需在安装树中核实，不能据 bundle 判断它们坏了。建议检查命令：

```bash
for d in materials/skills/*/; do
  [ -f "$d/SKILL.md" ] || echo "missing SKILL.md: $d"
done
# 再按各 SKILL.md 内引用的 references/ scripts/ static/ 逐项核对安装树
```

## 十、偏好而非缺陷

以下可以保留，不必为了“精简”改动：

- `AGENTS.md:173-179` 每条回答末尾的 `下一步建议：`。它增加固定样板，但与“避免装饰性强调”有张力；这是用户偏好，不是缺陷。若嫌啰嗦，可改为“仅在有明确后续动作时输出”。
- `task-archive` 的 24 小时/15 天表、50 条上限，`nature-downloader` 的大量状态码和确认门：这些是风险驱动，不是过度工程化。
- 保留 Nature 整套带来的维护成本：在第 3/4/5 技能完成前，这是有意的取舍。
- `AGENTS.md:118-123` 的 `gpt-5.6-terra` / `gpt-5.6-luna`：若 profile 只在固定主机/账号使用，是偏好；若要跨主机移植，则是真实缺陷，应移到 HOST_LOCAL 或模型路由配置。
- manual-only 标记和 `ask-matt` 的两层路由：成本低，不必合并。

## 十一、需要用户决定的事项

只列真正会改变行为的；其余按推荐默认执行。

1. **ARS 默认范围**：推荐“收窄为系统综述/元分析/RQ 收敛/研究方案 + 显式 ARS”，其余走 `nature-*`/`researchwrite`。若坚持“所有研究请求默认 ARS”，则必须接受与 ARS 自身 scope 的冲突，并补 manifest。
2. **ARS/paper-spine 的归属**：推荐 ARS 加入 manifest（若仍作默认）；paper-spine 若不在用，标为 unmanaged 或从第 3 技能中淘汰。需确认它们是否由其他插件安装。
3. **researchwrite**：推荐第 3 技能时“只保留开题/研究计划模式，删 state.json/评分，复用 project-journal”；若开题报告不是常见需求，直接归档。
4. **teach**：推荐仅在有真实多会话学习需求时保留，否则归档并删 `ask-matt:37`。
5. **Nature 尾部**：推荐先归档 `nature-literature-pipeline`（若不再用 Hermes cron/Feishu）；`nature-experiment-log` 等 journal 模板覆盖后再定；`paper-to-patent`/`paper2ppt`/`data` 按实际交付确认。
6. **中文变体**：推荐简体（跟随用户），而不是 ARS 的繁体默认。
7. **`setup-matt-pocock-skills`**：推荐若不再频繁初始化新仓库就归档；否则保留。

## 十二、建议执行顺序

1. 改 `AGENTS.md:89-95` 的 ARS 默认路由；同时决定 `AGENTS.md:154` 的简繁。
2. 决定 ARS/paper-spine 是否进 manifest；更新 `profile-manifest.toml` 和 `personal-profile-sync:16-17` 的路径措辞。
3. 清理 `HOST_LOCAL.template.md` 的动态字段（`:32,47,48,61`）。
4. 修硬编码路径：`AGENTS.md:4`、`personal-nature:19`、`personal-review-and-revise-paper:195`；paper-spine 留给第 3 技能。
5. 把 `multiline:102-125` 改为指向 `tencent`/`research-project` 的短指针。
6. 处理 `researchwrite` 的 `state.json`（并入 project-journal 或随第 3 技能归档）。
7. 条件归档：`nature-literature-pipeline`、`setup-matt-pocock-skills`、`teach`；每次同步更新 `personal-nature` 子列表和 `ask-matt` 表。
8. 第 3/4/5 技能设计前，不动 `nature-writing`、`nature-polishing`、`nature-reviewer`、`nature-figure`、`personal-review-and-revise-paper`、`personal-translate-paper-zh`。

下一步建议：先按推荐收窄 `AGENTS.md:89-95` 的 ARS 默认路由，并确认 ARS/paper-spine 是否纳入 `profile-manifest.toml`；这是后续归档和合并的前提。