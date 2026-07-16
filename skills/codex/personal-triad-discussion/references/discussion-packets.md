# Discussion Packet Contracts

Use these structures as compact contracts, not mandatory forms. Keep only the
headings that help the current decision, write user-visible content in the
user's language, and link or cite evidence instead of copying large artifacts.

## Contents

- [Kickoff Brief](#kickoff-brief)
- [Low-Bandwidth Round](#low-bandwidth-round)
- [Evidence Packet](#evidence-packet)
- [Working Project Memo](#working-project-memo)
- [Continuity Restart](#continuity-restart)
- [Blank Restart](#blank-restart)
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

## Low-Bandwidth Round

Start the discussion with exactly these five lines:

```text
Discussion goal: <decision or bottleneck>
Current state: <verified state and material unknown>
Role split: <GPT Pro, Codex control plane, and any evidence worker>
This round: <one concrete discussion action>
When you need to intervene: <now, at a named decision, or not yet>
```

For every later user-visible round, use exactly one status label:

- `无需你操作`
- `需要你转发`
- `需要你决定`
- `需要你授权`
- `需要你操作`

When action is requested, include the exact action, reason, impact, and success
signal. Use this compact shape and omit fields that carry no information:

```markdown
<exactly one status label>

本轮小结：
关键变化：
Codex 当前判断：

请求：
- exact action:
- reason:
- impact:
- success signal:

发送给 GPT Pro：
<one complete directly relayable message, when another round has value>
```

After a GPT Pro reply, classify verified facts, Project context, inference, and
unknowns; update the working memo; delegate substantial read-only evidence work
when needed; summarize the key change and Codex judgment; and prepare the next
relay. Do not ask the user to say `continue`.

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

## Continuity Restart

Use when opening a new chat in the same ChatGPT Project while preserving the
minimum verified state needed for safe continuation.

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
and remind GPT Pro that Project memory may contain superseded material and
cannot guarantee isolation.

## Blank Restart

Use only when the user wants an independent restart without an explicit
handoff. Ask the user to open a new chat. Do not send the working memo, do not
send verified state, and do not send old conclusions. Provide only a neutral new
kickoff that states the question and desired independent role without prior
answers.

Project memory cannot guarantee isolation, so a Blank Restart cannot prove that
the new GPT Pro chat has no earlier Project context. Disclose this limitation;
do not compensate by adding old state to the kickoff.

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
