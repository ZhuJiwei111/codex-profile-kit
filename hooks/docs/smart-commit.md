---
name: smart-commit
description: Adapted Codex native hook that records files touched by file-edit tools and stages them only after explicit acceptance.
category: git
event: PostToolUse, UserPromptSubmit
matcher: "^(Edit|Write|MultiEdit|apply_patch)$; acceptance prompt"
language: python
version: 1.1.0-codex
source: https://github.com/davepoon/buildwithclaude/blob/main/plugins/all-hooks/hooks/smart-commit.md
---

# smart-commit

Codex 适配版分两步工作：

1. 文件编辑工具成功后，只记录本次工具明确触及的仓库内文件，作为待验收暂存列表。
2. 用户之后明确说“验收通过”“可以暂存”“可以 add”或“stage”等确认语时，才暂存待验收列表里的文件。

安全边界：

- 不运行 `git commit`。
- 不运行 `git add .`。
- 不处理 hook payload 中没有明确出现的文件。
- 不处理当前 Git 仓库之外的路径。
- 不在文件刚编辑完成时自动暂存。
- 如果待暂存文件跨多个仓库且当前提示词无法确定目标仓库，则不会暂存。

实际执行脚本：

```text
{{HOME}}/.codex/hooks/smart_commit_stage.py
```

默认 pending 状态文件：

```text
{{HOME}}/.codex/hooks/.smart_commit_pending.json
```
