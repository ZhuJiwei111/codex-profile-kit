---
name: personal-project-journal
description: Maintain project experiment, research-stage and maintenance cards, the unified TODO, grouped GLOSSARY, and consequential JOURNAL events. Use when project work changes these records or their ownership; do not create records for routine discussion, isolated lookups, or unchanged checks.
---

# 个人项目记录

唯一维护项目卡片、TODO、GLOSSARY、JOURNAL 的字段、状态、模板和记录操作。项目如何启动、拆分职责及选择公共实现归 [个人研究项目启动与协作](../personal-research-project/SKILL.md)，不在这里再维护一套组织流程。

## 选择事实归属

| 内容 | 维护位置 |
|---|---|
| 实验目的、授权、当前交付事实、主要结果与判断 | 实验卡 |
| 跨实验的阶段问题、证据与方向判断 | S 阶段卡（可沿用已有专题页） |
| 独立服务或维护对象的用途、入口、依赖与交付 | M 维护卡 |
| 具体参数、逐格证据、细粒度执行状态 | 原生配置、产物与作业记录 |
| 持续动作、具体执行人及安排 | .agent/TODO.md |
| 跨材料术语、符号与别名 | .agent/GLOSSARY.md |
| 重要变化、原因、教训及历史依据 | .agent/JOURNAL.md |
| 项目特有规则或全项目综合判断 | 已有项目文档 |

建卡、更新、失败、订正或收口时读 [卡片](references/cards.md)。更新项目待办、术语或事件时读 [项目记录](references/project-records.md)。保存共享材料时遵循 [写入](references/writing.md)。只读当前任务所需参考，不每次加载全部材料。

## 授权与已有位置

先找实际权威位置、项目约定与相关近期记录；同步只读副本不是写入源。新项目按本规范按需建立，既有项目不因采用本 skill 自动迁移、回填或改变跟踪策略。

记录按已有记录维护或执行授权更新；记录权限与实验执行权限分别判断。沿用已有记录，缺少时可在已有写入授权范围内按需初始化，不另设审批。讨论、审阅、诊断等只读任务不写记录；已授权执行中的诊断与修复沿用该任务授权。记录维护不扩大卡片、TODO、GLOSSARY 或日志的写入范围，也不授权实验、Git、发布或外部消息。

旧任务如果明确沿已有计划或特殊记录继续，先尊重其当前事实属主，不新建同步副本，不迁移或删除它来满足新布局。新的个人研究工作不再创建独立 planning 状态体系。

## 写什么、何时写

在范围、授权、负责人、交付、阻塞、证据、结论或交接发生实质变化时更新相应所有者。不要把每条命令、重复验证和模型轮询抄成事件；不把记录保存当作原授权内执行前置。

可恢复工作的入口在开始时留下，细粒度进度仍读实际执行记录。完成待办先确认交付已保存，再移除行动；卡片主表来自同一汇总并校验，不能手写另一套数字。

重要判断要能追到来源；分清实测、引用与推断。历史事实保留原意，重大纠正带日期说明。保存、验证、提交、发布与实际运行分别报告，不预测未来动作。若记录无法安全写入，说明具体缺口与属主，不另造台账。

只完成一次性工作且有重要影响时记 JOURNAL；普通解释留在会话即可。是否已完成与是否归档是两件事。
