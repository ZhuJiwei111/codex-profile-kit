# Examples

Use these examples to calibrate the user's preferred style.

## Direct and bounded

Input:

> 这不是为了证明这个方案一定更好，只是从一个有限角度说明它可能有帮助。

Rewrite:

> 这一步检验当前条件下这个方案是否带来可观测收益。它不能证明方案普遍更优，但能决定下一阶段是否值得继续投入。

Why:

- Leads with the test being performed.
- Keeps the evidence boundary.
- Connects the boundary to the next decision.

## Boundary focus

Input:

> 这个改动显著提升了整体工作流的清晰度、稳定性和可维护性，为后续工作奠定了坚实基础。

Rewrite:

> 这个改动让多线协作的状态边界更清楚：每条线有明确的 worktree、owner、handoff 和 intake 状态。下一次多 worktree 任务可以用它验证是否减少上下文恢复和协调错误。

Why:

- Replaces broad praise with concrete state boundaries.
- Names the verification condition.
- Avoids casual personification.

## Judgment plain

Input:

> 这个结果比较复杂。部分指标改善，部分指标没有变化，因此后续还需要进一步分析。

Rewrite:

> 这个结果不能简单判为通过。指标改善集中在 A，B 基本没有变化，所以它支持“局部有效”，还不支持“整体方案成立”。下一步应先查 B 为什么没有响应。

Why:

- Gives judgment without drama.
- Separates supported and unsupported claims.
- Ends with the next check.

## Uncertainty with next test

Input:

> 这个结果可能说明模型用到了这个通道，但目前还不能完全证明机制成立。

Rewrite:

> 这个结果可能说明模型用到了这个通道，但目前还不能完全证明机制成立。下一步需要加入 shuffle 或匹配难例，检查模型是否依赖正确样本上的信息，而不是只依赖通道本身的存在。

Why:

- Keeps the cautious tone.
- Adds the next test that can resolve the uncertainty.

## English anti-defensive

Input:

> We do not claim that this model is superior in every situation.

Rewrite:

> The model is most useful when the task requires interpretable comparisons across cases.

Why:

- Converts a defensive non-claim into positive scope.

## English technical humanizer

Input:

> This change is a crucial enhancement that significantly improves robustness, maintainability, and long-term scalability.

Rewrite:

> This change reduces one failure mode: the worker state and handoff state now come from the same registry. The next multi-worktree task can show whether that reduces coordination errors.

Why:

- Replaces inflated value language with a concrete consequence and verification path.
