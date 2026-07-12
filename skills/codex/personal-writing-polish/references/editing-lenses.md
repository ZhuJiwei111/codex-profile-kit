# Editing Lenses

Use this reference after the entry gate and semantic fingerprint in `SKILL.md`. Select the smallest set of lenses that satisfies the request. These are contextual editing heuristics, not token-level bans.

## Selection Order

1. Apply explicit user, venue, project, and artifact requirements.
2. Preserve the semantic fingerprint and protected literal elements.
3. Select only the requested or clearly necessary lenses.
4. Prefer a smaller safe change over a more elegant semantic change.
5. Run the semantic-delta review after all lenses have been applied.

## Artifact Modes

### Technical-neutral

Prefer explicit actors, concrete operations, stable terminology, short causal chains, and locally useful caveats. Preserve code-shaped tokens exactly. Do not add broad benefit claims to make implementation prose sound important.

### Academic-calibrated

Preserve epistemic modality, study scope, baselines, metrics, statistical wording, limitations, citations, and distinctions among observation, association, mechanism, and causality. Remove ceremony only when it carries no methodological function.

### Project or professional-direct

Lead with the decision, state, consequence, or required action. Keep ownership, dates, blockers, and unknowns explicit. Replace vague assurances with existing evidence, but do not manufacture evidence or commitments.

### Personal-expressive

Use only when the user asks for it or provides an authorized voice sample. Match observable features such as sentence length, directness, register, transition density, and preferred terminology. Do not infer or invent personality, history, emotion, or opinion.

## Lenses

### Clarity

- Replace vague referents with their existing antecedents.
- Put the actual actor and action near each other when the source identifies them.
- Turn abstract nominalizations into verbs when truth conditions stay fixed.
- State an existing consequence directly instead of surrounding it with importance language.
- Keep necessary definitions and domain terms; simplicity is not terminological erasure.

### Anti-defensive

Classify a sentence before changing it:

- **Necessary boundary:** safety limit, non-goal, exception, uncertainty, failed condition, or scope exclusion. Preserve it.
- **Contrastive claim:** a negation distinguishes this result from a plausible alternative. Preserve the distinction.
- **Rhetorical defense:** the sentence anticipates criticism but contributes no unique proposition. It may be removed.
- **Indirect positive scope:** a negative construction expresses a supported positive proposition. Rewrite only if the propositions are equivalent under the same evidence.

The equivalence gate is strict. “This does not prove X” cannot become “This proves Y” unless the source separately supports Y. “We did not evaluate long-term safety” cannot become a claim about short-term safety. When equivalence is uncertain, retain the negation.

### Humanize

Look for clusters across a passage rather than isolated tokens. Useful clusters include:

- **Importance or promotion:** repeated “crucial,” “landmark,” “pivotal,” “underscores,” or broad impact language without an existing concrete consequence. Treat a benefit or value judgment as a protected claim unless the content owner confirms that it is removable; absence of support in an excerpt is a reason to flag it, not silently delete it.
- **Vague attribution or speculative fill:** “experts believe,” unnamed consensus, unsupported causal bridges, or plausible-sounding context added only for smoothness.
- **Chat residue and signposting:** greetings, meta promises, recap labels, generic conclusions, or “let us explore” language that does not belong to the artifact.
- **Mechanical structure:** repeated paragraph templates, uniform sentence length, excessive mirrored contrasts, or headings that fragment a short argument.
- **Defensive framing:** stacked caveats, pre-emptive reassurance, or repeated statements of what the work is not.
- **Rhythm or voice mismatch:** abrupt register shifts, monotonous cadence, excessive connective phrases, or vocabulary absent from the authorized sample.
- **Diff-anchored writing:** prose organized around “we added/changed” when readers need the resulting behavior, state, or decision.
- **Chinese translation stiffness:** repeated “进行…的,” unnecessary “值得注意的是,” English clause order carried into Chinese, redundant subjects, or literal connective stacking.

Do not claim that a rewrite is “undetectable,” proves human authorship, or defeats an AI detector. Natural prose is an editorial outcome, not a provenance test.

### Voice match

Extract only observable, reusable traits from the authorized sample:

- language and register;
- typical sentence and paragraph length;
- directness and hedge density;
- preferred transitions and punctuation;
- terminology, pronoun use, and heading style;
- tolerance for fragments, parentheticals, or rhetorical questions.

Apply those traits to the locked content. Do not copy distinctive phrases unnecessarily, and do not add anecdotes, beliefs, humor, emotions, or first-person claims absent from the target.

### Compress

Use only when requested or allowed. Remove repeated propositions, empty setup, and redundant summaries. Do not compress away qualifications, evidence boundaries, operational details, or information needed by the target audience.

### Artifact fit

Preserve established structure when it carries a contract: abstract sections, API field descriptions, issue templates, reviewer numbering, changelog conventions, or handoff fields. Improve local phrasing without silently redesigning the artifact.

## False Positives

None of the following is a defect by itself:

- one em dash or other dash;
- passive voice where the actor is unknown, irrelevant, or intentionally omitted;
- Title Case required by an artifact;
- a list of three real items;
- curly quotation marks;
- formal or domain-specific vocabulary;
- an “as of” date needed for temporal scope;
- a necessary negation, limitation, or hedge;
- repeated terminology needed for precision.

Change these only when the passage-level context shows a real clarity, voice, or artifact-fit problem. Under `expression_only`, keep scope-bearing clauses and qualifications attached to the proposition they govern; do not reorder material propositions.

## Bilingual Checks

For Chinese, prefer natural information order and explicit logical relations without forcing English punctuation or nominal style. Preserve English identifiers and established technical terms when translation would reduce precision.

For English, do not erase calibrated modality merely to sound decisive. Preserve the conventions of the target research or technical community and the user's chosen variety of English.

In either language, user-provided style guides and target-venue rules override these defaults unless they conflict with semantic preservation; surface that conflict instead of guessing.
