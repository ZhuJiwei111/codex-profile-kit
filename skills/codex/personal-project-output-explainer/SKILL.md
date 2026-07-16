---
name: personal-project-output-explainer
description: Manual only. Use $personal-project-output-explainer when the user explicitly wants an existing output or evidence chain decoded; default an unnamed target to the current Codex task, and do not use for ordinary status, diagnosis, docs, review, verification, or prose polishing.
---

# Personal Project Output Explainer

## Contract

Translate an existing Codex or project output into a reader-oriented
explanation. Make its terms, relationships, evidence boundary, and decision
impact understandable without redoing the original task.

- Run only after explicit `$personal-project-output-explainer` invocation. Keep
  implicit invocation disabled. The invocation itself is sufficient; it need
  not repeat the target when the current task default below is unambiguous.
- Decode a supplied response, result, artifact summary, evidence chain, or
  decision rationale. Ordinary status, summary, report, completion, or
  next-step wording alone is not a comprehension request.
- Keep source claims, verified facts, explainer interpretations, and unknowns
  distinct.
- Preserve exact identifiers, metrics, paths, modes, and technical terms while
  explaining their role and consequence.
- Follow an explicitly named audience, depth, or format over the defaults below.

## Resolve The Target

Use an explicitly supplied response, artifact, path, or evidence chain first.
Otherwise explain the most recent relevant Codex output in the current task.
When several current-task outputs are plausible and the choice changes the
explanation, ask one targeted question.

Do not enumerate tasks or infer another task from a similar title. Explaining a
different task requires an exact current-host reference or ID supplied by the
user and bounded read-only access. A project-wide evidence synthesis still
requires an explicit request; the current-task default does not authorize a
repository scan, live status collection, or new verification campaign.

## Default Reader

Assume an AI PhD student working in AI for biology:

- substantial AI and machine-learning knowledge;
- working biology knowledge without specialist depth in every subfield; and
- no prior knowledge of this project's aliases, custom modes, stages, unusual
  metrics, or local terminology.

Do not teach familiar AI terms from first principles unless their project use
is unusual. Explain biology to the depth needed for the current mechanism or
claim, not as a textbook survey. When cross-domain reasoning matters, connect
the biological object or signal to its representation, model role, comparison,
metric, and supported claim. Preserve the exact term after explaining it.

## Choose The Evidence Mode

### Decode Supplied Output

When the user supplies the output, use it as the primary source. Do not
automatically inspect the repository or re-run checks.

- Attribute unverified statements to the source: “这段输出表示……” rather than
  promoting them to observed facts.
- Explain a local term only from supported context. If its project meaning is
  ambiguous, state the likely reading and the unresolved ambiguity.
- When a project metric's denominator, unit, or completion contract is unknown,
  do not derive a remainder, coverage claim, or readiness judgment merely
  because its displayed value looks like a percentage.
- Perform a bounded read only when it can materially change the explanation and
  is already within the request's read-only scope.

### Synthesize Project Evidence

Use this mode only when the user explicitly wants to understand how several
stages, artifacts, experiments, or decisions fit together and the supplied
material is insufficient.

- Retrieve only evidence needed for the relevant chain, preferring exact
  reports, artifacts, decisions, and cutoffs over broad scans.
- Do not turn explanation into live status collection, diagnosis, test
  execution, review disposition, or a new verification campaign.
- Route missing evidence to its owner instead of smoothing over the gap.

## Build And Render A Reader Map

Before writing, identify these items implicitly; do not print them as a form:

- the source's core meaning;
- the terms, assumptions, or cross-domain links blocking comprehension;
- each important object's input, role, output, and consumer;
- the causal, data-flow, experimental, or stage relationship;
- what is reported, observed, inferred, unsupported, or unknown; and
- what the reader should care about now.

Render the explanation in layers when useful:

1. State in one or two sentences what the output means in practical terms.
2. Explain only the terms that block understanding, at first use.
3. Connect them through the relevant mechanism, flow, experiment, or stage chain.
4. State what the evidence supports and does not support.
5. End with the decision impact, current concern, or one natural next check.

Adapt the form rather than forcing headings:

- Explain one or two terms inline.
- Use a compact table when three or more exact mappings materially help, such as
  `term -> contextual meaning -> current consequence`.
- Use Mermaid only when a multi-component flow or stage sequence is materially
  clearer than prose.
- Explain what result-table numbers mean after the table.
- Do not repeat the source line by line unless it is short or the user requests
  annotation.
- Use analogies only as scaffolding; keep the exact relationship visible.

## Explain Terms And Audit Reasoning

For a decision-relevant term, explain only what is needed from:

- what it denotes in this project;
- its role in the pipeline, model, experiment, or decision;
- the reported state or value; and
- why that state matters.

For AI-for-biology work, make this bridge explicit when it carries the claim:

```text
biological object or signal
-> measured or processed representation
-> model input, target, or objective
-> comparison or ablation
-> metric
-> biological or engineering claim
```

Do not equate a proxy or modeled representation with the underlying biological
mechanism. Translate infrastructure names similarly: name the bottleneck,
failure mode, reliability property, or decision gate they affect.

Explain the source faithfully before performing a bounded epistemic audit:

- identify its conclusion and supporting comparison;
- point out a visible logical jump, missing control, ambiguous scope, or
  unsupported generalization when it changes how the output should be read;
- label any additional interpretation as the explainer's inference; and
- do not launch diagnosis, review, experiments, or a new final verdict.

For example, `normal > zero` may support that a model uses an input channel,
while `normal ~= shuffle` can still fail to show that correctly matched content
matters. Explain both the supported and unsupported claims.

## Explain Multi-Stage Work Causally

When several stages matter, replace chronology or command dumps with:

```text
original question
-> why prior evidence was insufficient
-> what changed
-> what was observed
-> what is now supported
-> what remains unresolved
-> why the next decision follows
```

Name important artifacts and evidence cutoffs, but include a stage only when it
changes the reader's understanding of the conclusion or its boundary.

## Route Adjacent Requests

- For an ordinary status or ETA request, leave this skill and use one bounded
  core read-only status check.
- `personal-evidence-debugging`: reproduction and root-cause work.
- `personal-review-response`: review-feedback disposition.
- `personal-risk-verification`: final completion verdict;
  `personal-branch-finish`: Git readiness or repository handoff.
- `personal-code-documentation`: substantial standalone architecture, API,
  onboarding, tutorial, or walkthrough artifacts. A small identified stale fact
  uses an ordinary scoped project-doc edit.
- `personal-writing-polish`: expression-only revision after facts are locked.
- Native task context and ordinary in-thread handoff own continuation; this skill
  does not persist session state.
- `personal-brainstorms` and manual-only `$personal-grilling`: unresolved
  design; manual-only `$personal-triad-discussion`: user-mediated GPT Pro
  deliberation.

Only after an explicit comprehension or decode request may an owning workflow
hand evidence or a verdict here for explanation. The handoff alone does not
trigger this skill. Do not change that owner's state, authority, or conclusion
while translating it.

## References

- Read [references/explanation-patterns.md](references/explanation-patterns.md)
  only when a complex explanation benefits from a concrete pattern.
- Read [references/source-notes.md](references/source-notes.md) only when
  auditing provenance or revising this skill.
