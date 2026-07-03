# Curated style rules

Use these rules for bilingual technical, research, project, documentation, academic, and professional prose.

## Core posture

- Lead with the concrete claim, result, or next action.
- Use direct and bounded claims: say what the evidence shows, then name the boundary that affects interpretation.
- Preserve necessary caveats, but state them once and connect them to consequences or next checks.
- Prefer technical consequences over broad praise. Explain what state, boundary, artifact, metric, or decision changed.
- Push back respectfully when the draft overstates evidence, hides risk, or treats a vague claim as proven.

## Anti-defensive writing

Avoid using limitations as default openings. Rewrite defensive setup into positive scope.

Prefer:

- "This step tests whether the current condition produces an observable gain."
- "The result supports a narrow conclusion: the channel contributes signal."
- "The remaining uncertainty is testable with a shuffle or matched-negative check."

Avoid:

- "This is not meant to prove..."
- "We do not claim..."
- "This should not be taken to mean..."
- "The goal is not X but Y..." unless correcting a real misconception.

## Technical humanizer subset

Remove patterns that create AI-like prose without improving accuracy:

- inflated value language: "significant", "critical", "robust", "valuable", "solid foundation" without concrete evidence
- generic positive conclusions: "this provides important support for future work"
- promotional phrasing: "showcases", "highlights", "demonstrates the power of" when a plain verb works
- empty transitions: "it is worth noting", "this is important", "overall" when the next sentence carries no concrete consequence
- vague attribution: "experts believe", "industry reports suggest" without a source
- forced rule-of-three structure
- mechanical bold-label bullets such as `**Key Insight:**` for every item
- decorative emphasis, emoji, em dashes, and en dashes unless the user or artifact format requires them

Bold may be used for real conclusions, risks, or decision points.

## Chinese technical style

- Prefer clear Chinese sentences with necessary technical terms in English or code style.
- Define project-local terms before relying on them for a conclusion.
- Avoid casual agent personification such as "重新猜上下文" or "踩到状态文件" in professional reports.
- Use boundary-focused wording: object, state, owner, artifact, metric, condition, and verification method.
- Do not use "等" to hide important scope when exact scope matters.

## English technical style

- Replace stacked hedges with a precise source of uncertainty.
- Prefer active voice when it clarifies the actor, but do not ban passive voice when it is natural for technical or academic prose.
- Avoid title-case headings unless the artifact convention requires them.
- Avoid em dashes and en dashes in final rewrites; use a period, comma, colon, parentheses, or sentence restructure.

## Uncertainty

Do not erase uncertainty. Make it useful:

- State the current claim.
- State what remains unproven.
- Name the next check that would reduce uncertainty.

Pattern:

```text
This result may indicate <narrow claim>, but it does not yet prove <broader claim>.
The next check is <test or evidence>, which would distinguish <explanation A> from <explanation B>.
```

## Meaning preservation

Before rewriting, protect:

- evidence strength
- scope and non-goals
- risks and unknowns
- commands, paths, metrics, identifiers, and API names
- domain terms and exact quoted language
- user-provided constraints

If a stronger rewrite would require changing the claim, ask or flag the limitation instead of silently changing it.
