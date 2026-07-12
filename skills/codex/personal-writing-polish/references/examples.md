# Regression Examples

These examples define semantic and routing expectations. `Protected` items are test oracles, not optional suggestions.

## Proposition-equivalent anti-defensive rewrite

**Request:** Make the sentence more direct.

**Source:** “The change is not intended to alter inference results; it only reduces serialization overhead.”

**Protected:** inference results are unchanged; serialization overhead is reduced; no broader performance claim.

**Safe rewrite:** “The change reduces serialization overhead while leaving inference results unchanged.”

The two clauses retain the same propositions. Do not expand this into a claim about end-to-end latency or reliability.

## Necessary negation stays

**Request:** Remove defensive wording.

**Source:** “This observational analysis does not establish that treatment A caused the survival difference.”

**Protected:** observational design; no causal conclusion; treatment A; survival difference.

**Safe rewrite:** “Because the analysis is observational, it does not establish that treatment A caused the survival difference.”

The negation is the evidence boundary. A positive-sounding causal or associational substitute would change the claim unless the source supplies it.

## Voice calibration without invention

**Voice sample:** “先说结论：吞吐没有变化。真正的问题在数据加载。”

**Target:** “实验结果表明，在当前设置下，模型精度保持不变，而训练耗时由数据预处理阶段主导。”

**Protected:** current setting; accuracy unchanged; preprocessing dominates training time.

**Safe rewrite:** “先说结论：当前设置下，模型精度没有变化。训练耗时主要卡在数据预处理。”

The rewrite matches directness and cadence. It does not add a cause, metric, opinion, or personal experience.

## Cluster-based humanize

**Request:** Make this less AI-like.

**Source:** “It is important to note that the update represents a pivotal improvement. Moreover, it serves as a testament to the team's commitment. In conclusion, the command now exits with status 1 when validation fails.”

**Protected:** the update is claimed to be pivotal; it is claimed to reflect team commitment; the command exits with status 1 when validation fails. The excerpt does not establish whether the first two claims are supported or removable.

**Safe response:** “The excerpt does not provide support for the value and commitment claims, so I have preserved rather than silently removed them. Closest safe rewrite: ‘The update is a pivotal improvement that reflects the team's commitment. The command now exits with status 1 when validation fails.’”

The generic transitions can be removed, but the two substantive claims remain protected until the content owner marks them as unsupported and removable. The diagnosis still comes from the passage-level cluster, not a banned-word list.

## Unsupported praise is a content blocker

**Request:** Strengthen this paragraph.

**Source:** “The refactor creates a robust foundation for future scalability, reliability, and maintainability.”

**Protected:** the source claims that the refactor provides a robust foundation for future scalability, reliability, and maintainability; no supporting behavior or comparison appears in the excerpt.

**Safe response:** “The excerpt does not support these benefit claims, so I cannot safely strengthen or delete them. Closest semantic-preserving rewrite: ‘The refactor provides a robust foundation for future scalability, reliability, and maintainability.’ Ask the content owner whether the claims are supported or should be removed.”

Do not replace vague praise with new architectural benefits, downgrade it into a different claim, delete it silently, or invent a validation plan.

## Metrics, citations, Markdown, and LaTeX remain literal

**Request:** Polish for an academic report.

**Source:** “At 10% traffic, p99 decreased from 480 ms to 330 ms after 20 min; `error_rate=0.7%` [@lee2025]. We have not verified backfill behavior. The objective is $L = L_{task} + 0.1L_{aux}$.”

**Protected:** `10%`, `p99`, `480 ms`, `330 ms`, `20 min`, ``error_rate=0.7%``, `[@lee2025]`, the unknown backfill behavior, and `$L = L_{task} + 0.1L_{aux}$`.

**Safe rewrite:** “At 10% traffic, p99 decreased from 480 ms to 330 ms after 20 min, with `error_rate=0.7%` [@lee2025]. Backfill behavior remains unverified. The objective is $L = L_{task} + 0.1L_{aux}$.”

## Route substantive work before polishing

**Request:** “A improved, but B did not move. Explain why, design the next experiment, and make the answer polished.”

**Expected routing:** Do not use this skill to generate hypotheses or experiments. A research or analysis workflow owns that content. Once the explanation and experiment plan are supported and locked, this skill may polish their expression.

**Request:** “Decide whether we should accept this review comment and rewrite our reply.”

**Expected routing:** `personal-review-response` decides `accepted`, `rejected`, or `needs-clarification`; this skill may then polish the locked reply.

**Request:** “Draft a rebuttal to Reviewer 2 and make it less defensive.”

**Expected routing:** `awesome-rebuttal` owns venue constraints, strategy, and substantive response. This skill is only a final expression pass over an approved draft.
