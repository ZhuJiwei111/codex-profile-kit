# Source Notes

Checked: 2026-07-16.

This skill is local-origin. It comes from the user's recurring difficulty
reading Codex outputs that contain project-local shorthand, professional terms,
cross-domain assumptions, and conclusions whose practical meaning is not
stated. No external skill text is copied, and no external derivative-license
claim is made.

## Contents

- [Local History](#local-history)
- [User-Origin Design Evidence](#user-origin-design-evidence)
- [Baseline Observations](#baseline-observations)
- [Adopted](#adopted)
- [Rejected Or Retired](#rejected-or-retired)
- [Local Deviations And Limits](#local-deviations-and-limits)

## Local History

- Initial profile-kit commit:
  `6574bce5f5ede8fb4566d0451ddcf613f7fdf8a5`
- Initial `SKILL.md` blob:
  `f85a492ca3fe670b9a2a006539315ba548310811`
- Initial `agents/openai.yaml` blob:
  `dcc5077f9136d4df92c6be3b86e65207bd54ccaf`
- Large advisor-style expansion commit:
  `ba76e83ace07c2595ab47c15f6066d661330f69e`
- Later writing-contract update:
  `c5370e8b0dd71577cd7dda93609b019316c2587d`
- Pre-rewrite `SKILL.md` blob:
  `a402b5bd5141a60217b2be9ad648cfea4c0658c1`
- Pre-rewrite `agents/openai.yaml` blob:
  `4df441fdcd0dc1bf5fda3104d1de9b3a2edd1ac8`

The initial version was a short reader-oriented explanation workflow. The later
expansion added useful evidence discipline and causal reporting, but fixed the
reader as an advisor-level technical audience and embedded a long,
project-specific AI-for-biology report example in the core skill.

## User-Origin Design Evidence

The accepted default reader is an AI PhD student working in AI for biology:
strong in AI and machine learning, familiar with basic biology, but not assumed
to have specialist depth in every biological subfield. The skill should not
teach common AI concepts from zero or treat biology as wholly unfamiliar.
Instead, it should explain the specific biological role, assumption, proxy, or
mechanistic limit needed to interpret the current result.

The accepted core job is comprehension, not generic reporting. The skill is
manual-only, decodes an explicitly named output first, and defaults an unnamed
target to the current Codex task. It synthesizes project evidence only when the
user explicitly requests that broader chain.

## Baseline Observations

Read-only probes against the pre-rewrite skill showed:

- a dense engineering-output request was translated successfully into plain
  meaning, local-term mappings, evidence gaps, and a defensible no-cutover
  decision; this core behavior is preserved;
- a live progress and ETA request was correctly recognized as outside
  comprehension and belongs to one bounded ordinary read-only status check;
- an under-evidenced CI error correctly routed to
  `personal-evidence-debugging` and refused to invent a root cause; and
- the metadata description was 74 characters long, while the profile UI budget
  requires 25-64 characters.

A focused pre-change contract check also confirmed that the advisor-level
reader, generic progress-update ownership, broad trigger, and missing
progressive-disclosure references were still present.

## Adopted

- Manual-only invocation, with no description-based implicit trigger.
- An unnamed explicit target defaults to the current task; other tasks require
  an exact user-supplied current-host reference.
- The unnamed mode produces a Current Task Snapshot covering the task goal,
  completed work, the decision-and-evidence chain, evidence cutoff, unresolved
  items, and why the next step follows. It does not silently substitute the
  most recent output as its target.
- A default AI-PhD/AI-for-biology reader profile with asymmetric domain depth.
- Layered explanation: practical meaning, necessary terms, relationships,
  evidence boundary, and decision impact.
- Supplied-output decoding without automatic repository inspection.
- Bounded evidence retrieval only for explicit multi-stage synthesis or a
  decision-changing ambiguity.
- Faithful source translation followed by a bounded epistemic audit.
- Exact separation of source claims, verified facts, explainer inferences, and
  unknowns.
- Just-in-time term explanation and explicit AI-to-biology representation links.
- Causal multi-stage synthesis instead of chronology or command dumps.

## Rejected Or Retired

- A fixed “PhD student reporting to an advisor” persona.
- Assuming every reader has advisor-level domain knowledge.
- Treating common status, summary, report, completion, handoff, or next-step
  wording as an explanation trigger by itself.
- Owning live status, ETA, diagnosis, review disposition, final verification,
  canonical documentation, persistence, or prose-only polishing.
- Automatic broad inspection before explaining supplied text.
- Printing the internal explanation map as a mandatory visible template.
- A long project-specific RNA/ATAC training example in the core skill.
- Explaining every term from first principles or leaving decision-critical
  biology assumptions implicit.
- Turning a visible reasoning gap into an unauthorized investigation or new
  verdict.
- Enumerating tasks or scanning a project merely because explicit invocation did
  not name an object.

## Local Deviations And Limits

- User-visible explanations default to Chinese under the global language rule;
  exact identifiers, metrics, paths, and established technical terms remain
  unchanged.
- An explicitly requested audience or format overrides the personal default.
- Core task handling and adjacent active workflows retain ownership of status,
  diagnosis, review, verification, Git readiness, docs, writing, continuation,
  design, and external deliberation. This skill does not claim them.
- No mechanical validator or reusable script is bundled. Metadata and link
  checks plus isolated engineering, AI-for-biology, multi-stage, missing-data,
  and adjacent-routing probes provide more proportionate evidence.

```yaml
skill_admission:
  skill: personal-project-output-explainer
  acquisition_mode: created
  source_classification: local-origin
  provenance_status: complete
  admission_status: admitted
  portability_disposition: internalized
  safety_status: passed
  safety_review: "static_pass: The instruction-only skill was reviewed; it performs bounded read-only explanation, does not grant implementation or external actions, and does not bundle scripts, hooks, credentials, persistence, or publication."
  trigger_status: passed
  trigger_review: "static_pass: Manual invocation, named-output decoding, unnamed Current Task Snapshot, live-status exclusion, and adjacent diagnosis/documentation routes were reviewed."
  validation_status: passed
  validation:
    - "static_pass: Local history, user-origin design evidence, metadata, and focused contract checks were reviewed on 2026-07-16."
    - "product_pass: A fresh bounded Current Task Snapshot forward probe preserved the goal, causal evidence cutoff, unresolved resource decision, and next action on 2026-07-16."
  update_owner: "maintainer of personal-project-output-explainer"
  update_rule: "Repeat provenance, safety, trigger, evidence-retrieval, audience, and portability review before the source, invocation modes, output contract, or adjacent owner boundaries change."
  rollback_basis: "Remove the skill through personal-skill-hygiene and restore the reviewed tree from codex-profile-kit revision 3791645f59c0eeec497755bd7301be78b44efbea."
  unknowns_disposition: none
  unknowns: []
```
