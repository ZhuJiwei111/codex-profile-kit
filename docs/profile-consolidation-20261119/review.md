# 2026-11-19 个人 profile 整理

本轮按用户授权修改并精确部署，不含 Git 提交/推送，不介入另一个交互会话的 dev 整理。普通安装 skills 从 65 项减为 47 项：37 项 manifest 管理，10 项外部维护。系统与插件技能另计。

## 归档与恢复

以下受管源码完整移至 `../../archive/profile-consolidation-20261119/managed/`，manifest 标为退休并移除活动安装：

- `ask-matt`
- `handoff`
- `implement`
- `improve-codebase-architecture`
- `personal-code-documentation`
- `personal-code-simplifier`
- `personal-codex-hook-rules`
- `personal-review-and-revise-paper`
- `researchwrite`
- `setup-matt-pocock-skills`
- `teach`
- `to-questionnaire`
- `to-spec`
- `to-tickets`
- `triage`
- `wayfinder`
- `wizard`

PaperSpine 完整移至 `../../archive/profile-consolidation-20261119/external/paper-spine/`。恢复受管项时，先恢复 source，撤销精确 retired entry 并加入 trees，再 preview/apply/check 对应 --path；外部项独立审阅后恢复，不混入 manifest。

架构评估与行为保持简化规则吸收入 codebase-design；必要交接由 multiline-coordination 维护；hook 维护规程归 writing-for-agents 的按需 reference。旧论文修订资料保留给第三 skill 设计。

## 保留和优化

- multiline/subagent/task-archive/temporary-work 分别维护交互会话、有界 worker、产品聊天归档、任务临时文件；不合成生命周期大工具。
- profile-sync 新增 repeatable --path，仅选 manifest 精确条目，排除配置和插件，允许已审阅未提交源码。复用原锁、备份、漂移检查与回滚。完整 release 仍需已提交版本和独立 Git 授权。
- AGENTS 收窄 ARS 默认路由，移除过时子代理模型 ID，强调讨论充分与最终答复自洽。personal.config 的模型值对齐已有本机 gpt-6.2-sol；本轮未全量投影配置。
- HOST_LOCAL 与模板移除旧连接探测、实时容量、历史 trust 验收等快照，保留路径/常设策略，修复 CLI 路径；本机文件保持0600。
- 翻译保留原双语、图表与质量要求，增加局部请求、提取复用和结构校验不替代语义检查。
- code-review、codebase-design、domain-modeling、grilling、personal-evidence-debugging、prototype、tdd 及 research 保留。tdd 的设计引用改为真实相对链接。
- Nature 整套已为手动调用，暂保留；修复 ref-verifier 自动委派与 literature-pipeline 的定时/外部投递边界。Nature shared 仍被多个子技能使用，不孤立删除。
- ARS 保留系统综述、元分析、RQ与显式流程能力，外部 overlay 修正强制 Nature 路由、PaperSpine 已退役引用与默认繁体。未更新上游、脚本或内部工作流。
- paper-writing/paper-polish 留给第三 skill；frontier/omniscientist/paper-review 等留给第四 skill；cvpr/framework/research-figure 留给第五 skill。此次不合并。

## Hooks 与插件

当前 CLI experimental schema 仍提供 deprecated autoResolutionMs，不能据当前工具签名缺字段就宣称已退役。守卫修复 null 误拦截，保留非空计时器拦截；定义和信任状态未改。测试覆盖 null、无字段、0与正数，及相邻工具。未冒称已在新会话验证实际 dispatch。

Zotero、Presentations、Spreadsheets 官方卸载成功，随后官方清单及 cache 检查确认不再安装。移除 spreadsheets 同时移除其 excel-live-control 能力。Plugin Management 与 Work Pets 被官方接口403拒绝：Installed-by-default plugins cannot be uninstalled；保持原状，不绕过限制。

## 独立审查与验证

本地 tclaude DS 只读审查，supervisor作业20261119064050-8557930d2a94，255.01秒完成，事件已ack。报告与回执见同目录。采用其ARS/HOST_LOCAL/授权边界等可核实发现；不采纳“工程入口各有名称就应全部保留”。Nature自动触发、profile目录路径冲突等判断与实际配置不符；下载器现有格式的摘要字段属于已有格式例外，不据此另改下载实现。

41项profile/hook/plugin-sync测试通过；本次修改skill格式检查通过。已核对选中源/活动原始一致，精确部署后check无差异；没有全仓apply。备份：
- ~/.codex.profile-sync-backups/20261119T064606.387754Z
- ~/.codex.profile-sync-backups/20261119T064737.883767Z

尚需未来真实新任务验证 hook 分发与新路由选择。没有自动派发验证任务、创建值守或修改另一个执行会话。

## 后续确认：四项 Nature 能力退出

用户确认专利、PPT、实验笔记、定期文献推送没有实际用途。归档并移除安装 nature-paper-to-patent、nature-paper2ppt、nature-experiment-log、nature-literature-pipeline；清除其在保留技能路由、README和共享能力说明中的引用。完整源码仍在本记录上列归档目录。普通安装skills现为43项，其中33项受管。9项profile契约检查通过，精确部署check无差异。未操作既有定时任务或服务，归档skill不代表取消外部运行任务。
