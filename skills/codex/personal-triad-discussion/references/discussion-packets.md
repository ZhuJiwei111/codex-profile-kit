# Discussion Packet Contracts

Use these structures as compact contracts, not mandatory forms. Keep only the
headings that help the current decision, write user-visible content in the
user's language, and link or cite evidence instead of copying large artifacts.

## Contents

- [Kickoff Brief](#kickoff-brief)
- [Evidence Packet](#evidence-packet)
- [Decision Checkpoint](#decision-checkpoint)
- [Restart Brief](#restart-brief)
- [Final Decision Synthesis](#final-decision-synthesis)

## Kickoff Brief

Use once when initializing the GPT Pro chat. Keep the framing neutral enough to
obtain an independent first pass.

```markdown
# Consultation Brief

## Decision To Examine
- What decision, bottleneck, or project premise needs reconsideration?
- What would a useful result enable?

## Why Now
- What changed, failed, stalled, or became uncertain?

## Verified Facts
- Fact:
  Evidence or source:
  Evidence cutoff:

## User Decisions And Constraints
- Locked goal or preference:
- Hard constraint:
- Explicit non-goal:

## Current Hypotheses
- Hypothesis:
  Why it is plausible:
  What would falsify it:

## Material Unknowns
- Unknown:
  Decision impact:

## First-Round Request
- Independently reframe the problem.
- Identify hidden assumptions and competing explanations.
- Propose alternatives before evaluating an existing preferred answer.
- Separate verified facts, Project-derived context, interpretation, and unknowns.
- Name only evidence that could materially change the decision.

## Evidence And Action Boundary
- Available evidence:
- Evidence not inspected:
- Actions not authorized by this consultation:
```

Do not paste a preferred Codex solution into the first brief unless the user
specifically wants a review rather than an independent reframe. If Project
memory may already contain a preferred solution, tell GPT Pro not to treat it as
the default or as verified evidence.

## Evidence Packet

Use this contract when local inspection or delegated work returns facts for the
discussion. Compress raw material before relay.

```markdown
## Evidence Packet

- Question answered:
- Observed facts:
- Source paths, artifact identities, or commands:
- Evidence cutoff:
- Interpretation supported:
- Competing interpretation still possible:
- Not inspected or not run:
- Decision impact:
```

Never turn a worker's recommendation into the coordinator's verdict. Preserve
exact error text, paths, versions, metrics, and commands only when they are
decision-relevant; otherwise link to the source or provide a bounded excerpt.

## Decision Checkpoint

Create only after a material state change. A checkpoint is an in-thread recovery
and decision aid, not proof and not execution authority.

```markdown
## Decision Checkpoint

- Current question:
- Locked user decisions:
- Verified facts and cutoff:
- Current best-supported options:
- Material disagreement:
- Invalidated or rejected assumptions:
- Unknowns that could change the decision:
- Next targeted question or evidence task:
```

If an older checkpoint is wrong, create a correction that names what changed
and why. Do not silently rewrite history or keep forwarding a known-bad premise.

## Restart Brief

Use when opening a clean GPT Pro chat in the same ChatGPT Project.

```markdown
# Restart Brief

## Purpose Of The Restart
- Context length, false premise, role confusion, or another concrete reason.

## Current Verified State
- Decision question:
- Locked user decisions:
- Verified facts and evidence cutoff:
- Remaining options:

## Do Not Inherit
- Rejected assumption:
- Superseded conclusion:
- Missing evidence previously mistaken for fact:

## Open Disagreement
- Claim:
- Why it matters:
- Cheapest discriminator:

## Requested Role And Response
- Reframer, challenger, domain expert, alternative generator, or synthesizer.
- Exact question for this round.
```

Do not replay the full transcript. Include only state needed to continue safely,
and remind GPT Pro that Project memory may contain superseded material.

## Final Decision Synthesis

Use when the discussion stops, even if the result is a deferral rather than a
consensus.

```markdown
## Decision Synthesis

- Outcome: selected / deferred / needs evidence / reopened
- Selected option or remaining decision:
- Decisive evidence and cutoff:
- Strongest unresolved disagreement:
- Rejected alternatives and reasons:
- Unverified items and residual risk:
- Next discriminator or separately authorized workflow:
```

Keep the synthesis decision-focused. Use a separate explanation or planning
workflow when the user needs a broad report or an executable plan.
