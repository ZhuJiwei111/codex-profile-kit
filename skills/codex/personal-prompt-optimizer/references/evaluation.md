# Evaluation

Use evidence labels conservatively. A cleaner-looking prompt is not proof of
better runtime behavior.

## Apply The Exact Evidence Levels

### `static_only`

Use `static_only` when evidence comes only from textual inspection, contract
comparison, linting, or a review of duplicates, contradictions, and missing
fields. Report what changed structurally. Do not say the prompt improved,
performed better, became more reliable, or reduced cost.

### `trace_based`

Use `trace_based` only when an actual supplied or observed execution trace supports
the diagnosis or demonstrates behavior under identified conditions. Record the
known target model, surface, settings, case, and trace boundary. Limit the claim to
what that trace shows; one trace does not establish general improvement.

### `runtime_tested`

Use `runtime_tested` only after an actual before/after comparison on the same
representative case, target model, surface, settings, tools, environment, and
acceptance checks. Record material uncontrolled differences. Require the repaired
prompt to pass the original correctness and safety bar before treating lower
tokens, latency, calls, turns, retries, or cost as a benefit.

Never upgrade an evidence label because the rewrite follows a trusted guideline.

## Run The Smallest Credible Comparison

When runtime evaluation is authorized:

1. freeze the original prompt, target, model, settings, tools, case inputs, and
   graders or acceptance criteria;
2. change one coherent instruction group rather than the entire stack;
3. run the original and candidate against the same representative case;
4. compare correctness, completeness, authorization behavior, safety, evidence,
   output contract, success and stop behavior first;
5. compare resource metrics only after both outputs satisfy the same bar;
6. report observed differences, confounders, failures, and evidence level without
   generalizing beyond the tested case.

Use multiple cases only when the user authorizes the additional runtime, cost, and
data exposure and when they represent distinct behavior that matters.

## Respect Evaluation Authorization

- Treat static review as read-only and in scope for the explicit invocation.
- Route a small, bounded, non-sensitive test with no external cost through
  `personal-subagent-boundaries` when an independent worker adds useful evidence.
- Obtain explicit authorization before any external API call, paid evaluation,
  batch job, sensitive-data use, heavy compute, large download, or long-running
  evaluation.
- Do not launch an evaluation merely to upgrade the evidence label.
- Do not expose supplied prompt contents or traces beyond the authorized task.

## Report Evidence Without Overclaiming

State:

- evidence level: exactly one of `static_only`, `trace_based`, or
  `runtime_tested`;
- target model and surface when verified;
- case, settings, tools, and acceptance boundary used;
- what was inspected or run;
- what was not run;
- observed result and remaining uncertainty.

Route current model claims and settings to `openai-docs`. If verification is
unavailable, keep the recommendation generic and the evidence `static_only`.
