---
ledger_schema: review-and-revise-paper/v1
canonical_entrypoint: TODO
canonical_source_type: latex
target_venue: TODO
paper_language: en
interaction_language: zh-CN
build_policy: explicit_or_final_freeze
approval_policy: active_package_only
active_package: PKG-001
workflow_mode: one_shot
---

# Paper revision ledger

## 使用边界

- 每个文档有一个 canonical source；仅按作者明确要求建立新的修订目录。
- 默认先展示完整候选并获得作者批准；已有明确授权不重复询问。
- “确定”只批准当前 active package。
- 讨论阶段不构建 PDF；仅在明确视觉检查或 final freeze 时构建。
- Coverage inventory 只是覆盖目录，展开后必须由完整 package 替换。

## 文档角色与作者约定

- 当前对象：manuscript / Response（按实际保留）
- 送审对照与历史参考：未指定
- 授权同步目标：无
- 审阅顺序：按当前对象的阅读顺序；作者另有要求时在此记录
- 授权例外：无；若有，记录作者原话与精确范围，并将 approval_policy 改为 recorded_scope
- 完整前后英中对照：台账与回复中均展示；修改标注至少精确到句子

## Coverage inventory（可选）

当前 active package 已在下方展开；此处无未展开项。

## Active package

### PKG-001 — TODO

- 目标文件：`TODO`
- 完整原文锚点：`TODO（语义说明，不以行号作为唯一身份）`
- 关联修改与依赖：无；涉及多文件时列明各自完整锚点与修改块
- 修改动机：TODO
- reviewer / evidence 追溯：TODO
- workflow mode：`one_shot`
- 状态：`drafting`

#### 1. 原文英文

TODO。拟删除或替换内容使用
<span style="color:#c62828">红色</span>；未变内容保持黑色。

#### 2. 候选英文

TODO。新增或替换内容使用
<span style="color:#1565c0">蓝色</span>；未变内容保持黑色。

#### 3. 原文中文

TODO：忠实、完整翻译原文，并保持与英文相同的红色语义范围。

#### 4. 候选中文

TODO：忠实、完整翻译候选，并保持与英文相同的蓝色语义范围。

#### 5. 修改判断

- verdict：`TODO（必须修改 / 建议修改 / 不建议修改 / 作者选择 / 作者锁定风险）`
- direct evidence：TODO
- necessity：TODO
- consequence if unchanged：TODO
- claim boundary：TODO
- contribution preserved：TODO
- residual risk：TODO

#### 6. 作者决定

- 决定：`待决定`
- 批准范围：无
- 讨论记录：TODO

#### 7. 应用与验证记录

- application：`未应用`
- target paths：无
- source checks：未运行
- render checks：未运行
- remaining risk：TODO

## Completed packages

完成后将 package 保留在此处；不要复制出第二份完整条目。
暂缓项使用 deferred；作者决定不修改的条目使用 closed_without_change；
两者均不占用 active_package，保留完整条目及决定。
