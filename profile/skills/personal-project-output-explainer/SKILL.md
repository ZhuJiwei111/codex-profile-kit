---
name: personal-project-output-explainer
description: Manual only. Use $personal-project-output-explainer to explain either an explicitly named existing output or the current task's existing evidence snapshot. Not for live status, ETA, diagnosis, new verification, documentation creation, review, or prose polishing.
---

# Personal Project Output Explainer

Translate existing Codex or project evidence into a reader-oriented explanation
without redoing the task or collecting a fresher status.

## Select The Entry

- Named output: explain the supplied or explicitly named response, result,
  artifact, table, evidence chain, or decision rationale.
- Current-task snapshot: when explicit invocation names no output, explain the
  goal, completed work, evidence chain, unresolved boundary, and next decision
  from the current task context.

Use only the named artifact and evidence already available in the task. A
bounded read of the named existing artifact is allowed when needed to see its
contents. Do not poll work, inspect live process state, rerun checks, diagnose a
failure, or start a new verification campaign.

If the named target is materially ambiguous, ask one focused question. Do not
enumerate tasks or infer another task from a similar title.

## Default Reader

Unless the user specifies another audience, write for an AI PhD student working
in AI for biology: strong in AI and machine learning, familiar with working
biology concepts, but new to this project's aliases, stages, unusual metrics,
and local assumptions.

Do not reteach standard AI concepts unless their project use is unusual. Explain
only the biological role, representation, proxy, or mechanistic limit needed to
interpret the result.

## Explain In This Order

Adapt the formatting, but preserve this reasoning order:

1. Practical meaning: state what the output means and why it matters now.
2. Terms: explain only project-local or cross-domain terms that block
   understanding.
3. Causal and evidence chain: connect relevant inputs, representations, model or
   pipeline roles, comparisons, metrics, observations, and decisions.
4. Supported and unsupported claims: separate reported claims, observed facts,
   inference, and unknowns.
5. Decision impact: explain what choice, concern, or next step follows within
   the existing evidence boundary.

For AI-for-biology evidence, make the bridge explicit when it carries the claim:
biological object or signal to representation, model role, comparison or
ablation, metric, and biological or engineering conclusion. Never equate a
proxy or model representation with the underlying biological mechanism.

## Preserve The Evidence Boundary

- Preserve exact identifiers, paths, modes, units, metrics, and technical terms.
- Attribute unverified statements to their source instead of promoting them to
  facts.
- Do not calculate readiness, coverage, remainder, or ETA from a value whose
  denominator or completion contract is unknown.
- Point out a visible logical jump or missing control only when it changes how
  the existing output should be read; label the observation as interpretation.
- Prefer a compact causal narrative over chronology, command dumps, or
  line-by-line paraphrase.

This skill produces explanation only. It does not change the source artifact,
the owning workflow's decision, or task state.

Read references/source-notes.md only when maintaining this skill.
