# Codex Hookify Rules

此目录存放 Hookify 风格的 Markdown 规则，并由 Codex 原生 hook
`~/.codex/hooks/hookify_codex_runner.py` 执行。

规则文件示例：

```markdown
---
name: warn-dangerous-command
enabled: true
event: bash
action: warn
pattern: rm\s+-rf
---

检测到危险命令。请确认路径和删除范围。
```

支持的事件别名：

- `bash`: Codex `PreToolUse` / `PostToolUse` 中的 Bash 命令。
- `file`: Codex 文件编辑工具，例如 `Edit`、`Write`、`MultiEdit`、`apply_patch`。
- `prompt`: Codex `UserPromptSubmit`。
- `stop`: Codex `Stop`。
- `all`: 所有事件。

`action: block` 只会在 `PreToolUse` 中转成 Codex 的 deny 决策；其他事件只输出提醒。
