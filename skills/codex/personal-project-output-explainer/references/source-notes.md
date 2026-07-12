# Source Notes

Checked: 2026-07-12.

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

The accepted core job is comprehension, not generic reporting. The skill
decodes a supplied output by default and, when explicitly requested, synthesizes
multi-stage evidence for a reader who did not follow the work. It may be
selected without the skill name only when the user explicitly signals a need to
understand or decode existing output, evidence, or a decision.

## Baseline Observations

Read-only probes against the pre-rewrite skill showed:

- a dense engineering-output request was translated successfully into plain
  meaning, local-term mappings, evidence gaps, and a defensible no-cutover
  decision; this core behavior is preserved;
- a live progress and ETA request was correctly recognized as outside
  comprehension; its former `personal-long-job-status` route is now retired, so
  an unnamed request leaves specialist workflows and uses one bounded ordinary
  read-only status check, while only explicit `$personal-long-job-status`
  invocation enters that skill;
- an under-evidenced CI error correctly routed to
  `personal-evidence-debugging` and refused to invent a root cause; and
- the metadata description was 74 characters long, while the profile UI budget
  requires 25-64 characters.

A focused pre-change contract check also confirmed that the advisor-level
reader, generic progress-update ownership, broad trigger, and missing
progressive-disclosure references were still present.

## Adopted

- Narrow implicit triggering for explicit comprehension signals.
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

## Local Deviations And Limits

- User-visible explanations default to Chinese under the global language rule;
  exact identifiers, metrics, paths, and established technical terms remain
  unchanged.
- An explicitly requested audience or format overrides the personal default.
- Adjacent workflows retain ownership of status, diagnosis, review,
  verification, Git readiness, docs, writing, persistence, design, and external
  deliberation. This skill does not claim those responsibilities.
- No mechanical validator or reusable script is bundled. Metadata and link
  checks plus isolated engineering, AI-for-biology, multi-stage, missing-data,
  and adjacent-routing probes provide more proportionate evidence.
