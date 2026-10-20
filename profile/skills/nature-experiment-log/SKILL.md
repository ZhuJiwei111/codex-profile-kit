---
name: nature-experiment-log
description: "将用户指定的实验图片、转录或原始笔记整理成带 YAML 的实验记录，可沿用 Obsidian vault；不承担仓库 JOURNAL、任务状态或通用日志维护。"
license: MIT
metadata:
  version: "1.0.0"
  author: "十五 (JL Lab)"
  hermes:
    tags: [research, experiment, logging, feishu, obsidian, automation]
    related_skills: [nature-literature-pipeline, feishu-cli-integration]
---

# Experiment Record

把用户提供的实验原始材料整理成可追溯记录。先沿用用户指定的
vault、目录、字段和实验编号；没有约定时，在已授权的目标中使用
最小记录：实验目的、日期、实际操作、条件、观察、原始材料位置与疑问。
保留原始观察与后续解释的区别，不把估计值写成实测值。

仓库阶段事件由 `personal-project-journal` 维护；活动任务由既有 TODO
或计划维护。本技能只处理原始实验材料及其结构化记录，不重复这些所有者。
普通讨论、上传一张图片或一次代码实验不触发另建实验日志。

## 按需采用实验室格式

用户需要材料实验或 Obsidian/Dataview 格式时，选择与实际实验匹配的
`references/example-log.md`、`references/example-electrochemical.md` 或
`references/example-thermal-stability.md`；不要把设备、样品批次或材料
体系字段强加到机器学习实验。模板和编号示例是可选约定。

只在请求包含相应索引时使用 `templates/`，不初始化整套 vault。
附件沿用已有路径或复制到已授权的位置；不擅自移动、删除原始材料。
模糊的样品号、条件和单位标为待确认；只询问影响记录含义的缺口。

## 外部来源

本地材料不需要飞书或 bot。仅在用户明确要求从飞书取材料、当前已有
对应连接或工具且授权范围明确时读取指定来源；不要扫描整个群、配置
凭据或自行安装连接。语音输入使用已有转录或可用的转录能力，不假设
存在 `vision_analyze` 或其他宿主专用 API。

写后核对关键数值、单位、附件引用和缺口标记，报告实际保存的位置。
