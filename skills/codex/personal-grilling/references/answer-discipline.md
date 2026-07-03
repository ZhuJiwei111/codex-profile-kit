# Answer Discipline Failure Taxonomy

Use this reference when a grilling answer is too vague, evasive, broad, optimistic, or unverifiable to lock.

## Operating Rule

Do not convert ambiguity into a decision. A lockable answer must contain at least one of:

- an explicit choice
- an explicit default
- a measurable acceptance criterion
- a bounded scope or named non-goal
- a concrete constraint
- a named tradeoff
- an evidence path or verification method
- a blocking open question

When the answer is not lockable, say so directly, name the failure, and re-ask the narrowest version of the same question.

## Failure Types

### Vague Preference

Detect when the user says variants of "都可以", "看情况", "随便", "先这样", "应该差不多", or gives only a general preference.

- Point out: "这个回答还不能锁定，因为它没有选择默认行为。"
- Re-ask: "在没有更多信息时，默认采用 A 还是 B？"
- Block when: the default affects cost, safety, correctness, user-visible behavior, or reversibility.

### Skipped Decision

Detect when the answer responds to background context but not the actual choice.

- Point out: "你解释了原因，但没有回答要选哪条路。"
- Re-ask: "当前版本锁定为 A、B，还是明确延期？"
- Block when: implementation shape, ownership, scope, or acceptance depends on the decision.

### Missing Acceptance Criteria

Detect when the user states a goal but not how success will be judged.

- Point out: "这个目标还无法验收，因为没有判定完成的标准。"
- Re-ask: "什么具体结果出现时，我们可以说这件事完成了？"
- Block when: completion, verification, handoff, or user-visible success would otherwise be subjective.

### Missing Constraint

Detect when the answer ignores cost, time, data safety, compatibility, environment, reversibility, or resource limits.

- Point out: "这个回答跳过了约束，后面容易做出不可接受的实现。"
- Re-ask: "这里最硬的约束是什么：时间、风险、兼容、成本、数据安全，还是可逆性？"
- Block when: the work may install software, alter global state, run long jobs, touch credentials, spend resources, or mutate shared artifacts.

### No Tradeoff

Detect when the user wants all benefits without selecting what to sacrifice.

- Point out: "这里还没有取舍；这些目标不能同时最大化。"
- Re-ask: "如果只能优先一个，优先速度、质量、可维护性、安全性，还是最小改动？"
- Block when: implementation choices conflict or the result could be optimized in incompatible directions.

### No Evidence

Detect when the answer asserts a fact that should be verified but gives no source, path, command, test, metric, or observable signal.

- Point out: "这个判断还没有证据入口。"
- Re-ask: "我们用哪个文件、命令、测试、指标或人工检查来确认它？"
- Block when: the assertion drives scope, risk, correctness, or go/no-go.

### Scope Drift

Detect when the answer expands the work beyond the original theme or adds adjacent goals without naming non-goals.

- Point out: "这个回答把范围扩大了，但没有说哪些不做。"
- Re-ask: "本轮明确做什么，明确不做什么？"
- Block when: the expanded scope changes files, ownership, cost, acceptance, or timeline.

### Contradiction With Evidence

Detect when local files, code, logs, config, prior answers, or current constraints contradict the answer.

- Point out: "这个回答和已有证据冲突。冲突点是 X。"
- Re-ask: "我们以哪个为准：用户新决定、仓库现状、已有计划，还是需要先查证？"
- Block when: proceeding would risk wrong edits, stale assumptions, or unsafe operations.

### Unverifiable Wording

Detect terms like "更好", "更优雅", "更稳定", "足够", "简单一点", "不要太复杂" without a measurable or observable meaning.

- Point out: "这个词还不能执行，因为不同人会给出不同解释。"
- Re-ask: "这里的 '更好' 具体表现为哪个可观察结果？"
- Block when: design, implementation, or review could pass or fail depending on interpretation.

### Risk Not Acknowledged

Detect when the answer chooses an option but does not acknowledge the obvious downside, reversibility, failure mode, or mitigation.

- Point out: "这个选择可以成立，但风险没有被确认。"
- Re-ask: "你接受的主要风险是什么？失败时怎么回退或止损？"
- Block when: the risk affects data safety, cost, long-running jobs, user-visible behavior, credentials, or irreversible changes.

## Blocking Open Questions

Mark a question as blocking when:

- the answer controls whether work is safe or in scope
- no reasonable default is safe
- the user refuses or cannot yet choose
- local evidence is insufficient and cannot be discovered cheaply
- proceeding would require inventing requirements

Use this format:

```markdown
Blocking question: <question>
Why blocked: <specific missing decision or evidence>
Minimum answer needed: <choice/default/evidence/acceptance criterion>
Recommended default: <default or "none">
Risk if assumed: <risk>
```

## Non-Blocking Defaults

Use a recommended default only when:

- the default is reversible
- the blast radius is small
- the user has already expressed a compatible preference
- the default is stated explicitly in the locked brief
- the risk is recorded

Even then, do not silently assume. Say: "我建议默认 X，因为 Y；代价是 Z。"
