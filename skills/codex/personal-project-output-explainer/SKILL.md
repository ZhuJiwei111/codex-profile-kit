---
name: personal-project-output-explainer
description: Use when explaining or summarizing project plans, diagnostic findings, handoff notes, artifact status, preprocessing or training pipeline outputs, research/engineering decisions, project status updates, implementation completion reports, progress summaries, next-step recommendations, or stage decisions; especially when the user asks “如何理解”, “解释一下”, “辅助决策”, “给不熟悉项目的人讲”, “总结一下”, “汇报”, “现在状态”, “下一步”, “怎么决策”, “完成了什么”, “交接”, or otherwise wants a project answer made clear for someone who partially knows the project but lacks current context.
---

# Personal Project Output Explainer

Use this skill to explain or summarize project-related answers in a way that helps a reader with partial project knowledge understand what matters and decide what to do next.

## Default Audience

Assume the reader knows the broad project exists, but does not know the current thread state, artifact names, pipeline stage, or why the output matters.

## Use When

Use this style for project plans, decision recommendations, completion reports,
status updates, handoff notes, artifact or pipeline result explanations, and
progress summaries. Common trigger phrases include “总结一下”, “汇报”, “现在状态”,
“下一步”, “怎么决策”, “完成了什么”, “交接”, “结果意味着什么”, “如何理解”,
“解释一下”, and “辅助决策”.

## Response Style

- Prefer Chinese. Keep necessary artifact names, field names, commands, metrics, and filenames in English/code style, and define them on first use.
- Use free-flowing paragraphs instead of a rigid template. Do not force fixed section headings unless they improve scanning.
- Use dynamic detail: be concise when the context was already explained or the reply is just a close-out; go detailed when the user asks for a detailed introduction; otherwise aim for medium detail, roughly 4-8 useful paragraphs for non-trivial project answers.
- Start with one short sentence or paragraph that says what the output is essentially about.
- Then explain the minimum background needed to understand the output.
- Translate metrics, artifact states, and pipeline steps into concrete consequences.
- Separate facts, risks, judgments, and decisions in the prose.
- When decisions are involved, list the realistic options and their costs, then give one lightweight recommendation if the evidence supports it.
- End by stating what decision or next action this explanation supports.

## Progress Updates

For commentary updates while work is in progress, keep this style compressed to
at most two sentences: say the current stage, the essential progress or risk,
and the immediate next step. Do not expand into full background, options, or
decision analysis unless the user asks.

## Exceptions

Do not force this style onto tiny direct answers, simple command output, code review findings, low-level debugging, CI error localization, or long-job real-time status checks. In those cases, follow the more specific task or skill format.

If the user explicitly asks for “简洁”, “只给命令”, “只给结论”, or another format, honor that format and compress the explanation.
