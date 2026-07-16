# Discussion Packet Contracts

Use these structures as compact contracts, not mandatory forms. Keep only the
headings that help the current decision, write user-visible content in the
user's language, and link or cite evidence instead of copying large artifacts.

## Contents

- [Kickoff Brief](#kickoff-brief)
- [Evidence Packet](#evidence-packet)
- [Working Project Memo](#working-project-memo)
- [Restart Brief](#restart-brief)
- [Final Decision Memo](#final-decision-memo)

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

## Working Project Memo

Update the coordinator-owned project memo after each material round or
checkpoint. Prefer an unambiguous project decision-note convention; otherwise
write `.triad/<topic-slug>/working.md`. This is mutable recovery state, not proof
or execution authority.

```markdown
## Working Decision Memo

- Current question:
- Current outcome/status:
- Locked user decisions:
- Verified facts and cutoff:
- Decisive reasoning:
- Current best-supported options:
- Rejected options and why:
- Residual risks and unknowns:
- Superseded assumptions:
- Artifacts and paths:
- Reopen conditions:
- Next authority or action, if any:
```

If an older checkpoint is wrong, create a correction that names what changed
and why in the current memo. Do not keep forwarding a known-bad premise. Only the
current Codex coordinator writes this file; external participants return evidence.

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

## Final Decision Memo

Use `.triad/<topic-slug>/decision.md` or the established project convention when
the discussion stops, even if the result is a deferral. Curate verified state;
do not dump the transcript.

```markdown
## Decision Memo

- Question:
- Outcome/status: selected / deferred / needs evidence / reopened
- User decisions:
- Verified facts, sources, and evidence cutoff:
- Decisive reasoning:
- Rejected options and why:
- Residual risks and unknowns:
- Superseded assumptions:
- Artifacts and paths:
- Reopen conditions:
- Next authority or action, if any:
```

Keep the memo decision-focused. Planning may reference it but cannot rewrite it;
closeout and documentation workflows cannot rewrite it either. A failed write
makes persistence unsupported but does not by itself invalidate the in-thread
decision result.
