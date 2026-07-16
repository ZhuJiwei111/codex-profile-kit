# Source Notes

Checked: 2026-07-12

This skill is a local semantic-preserving editing workflow informed by two upstream skills. Upstream snapshots are design evidence, not runtime dependencies. No substantial upstream passage is copied into the local instructions.

## Local history

- The prior local version first appeared in profile-kit commit `c5370e8b0dd71577cd7dda93609b019316c2587d`.
- Prior tracked blobs:
  - `SKILL.md`: `4dec97f70d2ab740b8082da7d0f7566c1f1c4490`
  - `agents/openai.yaml`: `02ac428b2bcef7c9a653f8de572cfd06b19a32e8`
  - `references/examples.md`: `8cc8c098ac761f39b28b7e195b1730be1611b553`
  - `references/source-notes.md`: `38ba31470eac6f991e31204ba082e46f5561d113`
  - `references/style-rules.md`: `b600db274278c6462185dfbaf80925932c65de0a`
- Git history retains the removed `style-rules.md`; the replacement reference is `editing-lenses.md`.

## Humanizer

- Repository: <https://github.com/blader/humanizer>
- Fixed commit: `1b48564898e999219882660237fde01bf4843a0f`
- Release observed at that commit: v2.8.2
- Tree: `299241e3698ecdfe6ba5633da3f407349cff25d6`
- `SKILL.md` blob: `f6d973be6d1b283f9622b19397cbe4cbbc3d3cf9`
- Source: <https://github.com/blader/humanizer/blob/1b48564898e999219882660237fde01bf4843a0f/SKILL.md>
- License: MIT, Copyright 2025 Siqi Chen. <https://github.com/blader/humanizer/blob/1b48564898e999219882660237fde01bf4843a0f/LICENSE>

Adopted:

- evaluate prose patterns in contextual clusters rather than by isolated words;
- calibrate observable voice features from a supplied sample;
- keep false-positive awareness when reviewing punctuation, passives, headings, lists, and hedges;
- distinguish natural prose editing from generic cleanup.

Rejected:

- AI-detector, authorship, or “undetectable” claims;
- hard bans on dashes, curly quotes, passive voice, title capitalization, or three-part lists;
- a mandatory draft-audit-final ceremony or fixed paragraph counts;
- invented personality, opinions, first-person experience, tangents, or supporting detail;
- examples that improve style by changing stance or fabricating facts.

The upstream skill attributes some pattern material to Wikipedia-related guidance. That underlying provenance and licensing were not independently audited here, so this local skill retains only generalized editorial concepts and does not reproduce that material.

## Anti-Defensive Writing

- Repository: <https://github.com/Kiterlin/anti-defensive-writing>
- Fixed commit: `088df470b2871a66315698cd55b6a9fd0301d918`
- Tree: `83c2d4e0dd01fd387e8cfa033b4e0b09b31d68f0`
- `SKILL.md` blob: `2a5f19a08d5bb310338a7c46867e7234089a4438`
- Source: <https://github.com/Kiterlin/anti-defensive-writing/blob/088df470b2871a66315698cd55b6a9fd0301d918/SKILL.md>
- License: MIT, Copyright 2026 Kiterlin. <https://github.com/Kiterlin/anti-defensive-writing/blob/088df470b2871a66315698cd55b6a9fd0301d918/LICENSE>

Adopted:

- classify whether a negative or caveat is a necessary boundary, contrast, or removable rhetorical defense;
- prefer direct positive scope when it expresses exactly the same supported proposition;
- preserve limitations that carry methodological, safety, or factual meaning.

Rejected:

- converting “not X” into an attractive “Y” without independent support for Y;
- treating all hedging or negation as weakness;
- deleting uncertainty to make a claim sound confident.

Local deviation: every anti-defensive rewrite passes a proposition-equivalence gate. Truth conditions, evidence modality, causal strength, and scope must remain unchanged.

## Local design decisions

- The entry gate requires both locked text and explicit transformation intent, including natural-language intent.
- Default output is rewrite-only. Audits, alternatives, and rationales are opt-in except when a semantic conflict must be disclosed.
- Semantic preservation governs every lens; stylistic fluency never authorizes new content.
- Missing support in a supplied excerpt triggers a visible evidence-conflict flag, not silent deletion or weakening of the source claim.
- Content-owning skills run first for explanations, documentation, review decisions, rebuttals, and research analysis.
- No upstream installation, detector integration, or mechanical validator is required at runtime.

```yaml
skill_admission:
  skill: personal-writing-polish
  acquisition_mode: created
  source_classification: hybrid
  provenance_status: partial
  admission_status: legacy-exception
  portability_disposition: internalized
  safety_status: passed
  safety_review: "static_pass: Static review found an instruction-and-reference-only skill; edits require locked text and transformation intent, preserve propositions and evidence, and bundle no detector, installation, or external mutation."
  trigger_status: passed
  trigger_review: "static_pass: Expression-only rewriting was reviewed against analysis, new content, review disposition, rebuttal strategy, documentation ownership, and bare read-only review requests."
  validation_status: passed
  validation:
    - "static_pass: Pinned upstream commits, trees, blobs, licenses, local history, and the declared underlying-source gap reviewed on 2026-07-16."
    - "static_pass: Targeted personal-skill admission validator fixtures passed on 2026-07-16."
  update_owner: "maintainer of personal-writing-polish"
  update_rule: "No update is authorized; any content, source, trigger, executable, or metadata change requires a fresh re-admission before portable export."
  rollback_basis: "The pre-batch rollback source is exact codex-profile-kit revision 3791645f59c0eeec497755bd7301be78b44efbea and exact tree 6dc2b073b17a9f90c809bf69aa7a09840558f403; the current compatibility-only allowed content is separately locked by the validator's reviewed sha256-path-content-v1 full-tree digest."
  unknowns_disposition: provenance-gap
  unknowns:
    - "Humanizer's attributed Wikipedia-related pattern provenance and licensing were not independently audited; only generalized editorial concepts are retained."
```
