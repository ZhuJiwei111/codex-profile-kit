# Explanation Patterns

Use these examples as reasoning patterns, not mandatory templates. Preserve the
actual source's terms and evidence rather than copying the examples' structure
or conclusions.

## Contents

- [Choose A Shape](#choose-a-shape)
- [Decode A Dense Engineering Output](#decode-a-dense-engineering-output)
- [Bridge AI And Biology](#bridge-ai-and-biology)
- [Explain A Multi-Stage Evidence Chain](#explain-a-multi-stage-evidence-chain)
- [Handle Ambiguous Local Terms](#handle-ambiguous-local-terms)

## Choose A Shape

Use prose when the reader needs one conclusion and one or two definitions. Use
a mapping table when several exact terms must remain visible. Use a flow only
when understanding depends on three or more connected stages or objects.

Avoid a glossary detached from the source. Define a term at the point where its
role becomes necessary, then connect it to the conclusion.

## Decode A Dense Engineering Output

Source:

> Index migration completed; dual-read remains enabled; backfill watermark is
> 97.3%; 42 orphaned rows are quarantined; cutover is blocked because the new
> path has p99 480 ms against a 350 ms SLO.

Useful explanation shape:

1. Lead with the decision: the new path is not ready to replace the old path.
2. Map only the blocking terms:

| Source term | Contextual meaning | Consequence |
| --- | --- | --- |
| `dual-read` | Old and new read paths are both still participating for comparison or fallback | The old path is still part of the safety boundary |
| backfill watermark | Reported progress marker for historical-data migration; confirm its exact project definition | Some historical coverage may remain incomplete |
| quarantined rows | Records held outside the normal path because they failed a relationship or validity rule | Their user or data impact still needs classification |
| `p99` versus SLO | Tail latency is 480 ms while the accepted threshold is 350 ms | The explicit performance gate fails |
| cutover blocked | The production-switch gate has not passed | Do not retire the old path yet |

3. Separate explicit facts from gaps. The source reports a failed performance
gate. It does not, by itself, establish result equivalence, error rate, the
meaning of the remaining 2.7%, or the business impact of quarantined records.

Do not assert that a project-local watermark is percentage completion unless
the source or project contract defines it that way.

## Bridge AI And Biology

Suppose a model receives an embedding derived from a regulatory signal and an
evaluation compares:

- `normal`: correctly matched signal embedding;
- `zero`: the signal channel replaced with zeros; and
- `shuffle`: non-zero embeddings assigned to the wrong samples.

Explain the bridge:

```text
biological regulatory signal
-> processed embedding used as a model input
-> zero tests whether the channel contributes anything
-> shuffle tests whether sample-specific correspondence matters
-> retrieval or prediction metric measures downstream behavior
```

Interpretation:

- `normal > zero` supports that the model benefits from the presence of the
  channel.
- `normal > shuffle` would support that correctly matched biological content
  matters.
- `normal ~= shuffle` weakens the stronger claim. It may indicate reliance on
  a non-zero prior, source signature, or other channel-level property rather
  than the intended sample-specific regulatory information.

Do not replace this with a broad claim that the model learned the biological
mechanism. The ablation tests information use at the modeled representation
level; mechanistic interpretation needs stronger evidence.

## Explain A Multi-Stage Evidence Chain

Chronology alone:

> Cleaned the data, changed the objective, ran 50k steps, added an ablation,
> and decided not to scale training.

Reader-oriented chain:

1. The project needed to determine whether poor evaluation came from noisy
   inputs or from an objective that did not reward the intended correspondence.
2. Data cleaning removed a known confounder but did not produce the expected
   separation, so input quality was not a sufficient explanation.
3. The revised objective improved the target metric, but a `shuffle` control
   remained close to the normal condition.
4. The evidence therefore supports channel use but not correct correspondence.
5. Longer training would amplify an unresolved shortcut, so the next useful
   step is a discriminating control or objective change rather than scale.

Keep only stages that change the causal interpretation or the next decision.

## Handle Ambiguous Local Terms

If an output says “`strict-clean` passed, so release is safe” and the project
does not define `strict-clean`, explain the boundary:

- the source reports that a named gate passed;
- the gate's covered checks, exclusions, environment, and evidence cutoff are
  unknown; and
- release safety does not follow until that gate is shown to own every required
  release condition.

Do not manufacture a plausible definition from the name. A bounded read of the
gate definition may be appropriate only when it can materially settle the
interpretation and the request allows it.
