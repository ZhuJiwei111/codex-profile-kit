# Serial Phase Transitions

Read this reference before activating a draft, switching phases, closing the
project, or recovering an interrupted edit.

## Activation

Activation changes an approved root plan from `draft` to `active` and activates
the first ordered phase. Before writing, show the root and first-phase content,
controlled-file hashes, exact status edits, and current writer. After writing,
validate that:

- the root points to the first phase;
- exactly that phase is active;
- every later phase remains draft; and
- no root findings/progress or unlisted phase state exists.

Do not activate a draft whose global acceptance, phase order, or first-phase
acceptance is still unresolved.

## Phase Switch

A switch is one approval-bound state transition, not three independent
approvals and not a claim of filesystem-level cross-file atomicity:

```text
old active phase -> closed
root active_phase -> next ordered phase
next ordered phase -> active
```

Prepare the switch only when the current phase's acceptance and handoff are
supported. Show:

- current and next phase IDs;
- current root and both phase `task_plan.md` hashes;
- phase acceptance evidence and skipped checks;
- information inherited by the next phase;
- the exact three status/pointer changes; and
- recovery content if the write is interrupted.

Approval binds all three changes. Do not close the old phase without updating
the pointer and activating the next one, or activate the next phase while the
old one remains active.

After the edit, run the validator against the root or next phase. It must show
all earlier phases closed, exactly the pointer target active, and all later
phases draft. Then read back the old handoff and new phase acceptance.

## Closing The Project

The final phase closes only after its acceptance and verification are recorded.
Project closure then removes `active_phase`, sets the root to `closed`, and
requires every phase to be closed. Closure does not archive files and does not
authorize a successor.

Lifecycle never runs backward: do not change an `active` or `closed` root or
phase to `draft`. While still draft, content may be revised under approval. If
an active or closed plan needs a change to its goal, scope, global acceptance,
phase order, or the validity of a closed phase, record the consequence, close
the source when appropriate, and create a separately approved successor.

If remaining work is intentionally abandoned, record the consequence and user
decision in the final phase before closing. Do not encode cancelled, suspended,
or blocked as lifecycle values.

## Interrupted Edit Recovery

There is no persistent staging transaction or phase registry. If an edit stops
between writes:

1. Run the validator and inspect only the root plus the two affected phase plans.
2. Compare them with the approval-bound hashes and shown transition.
3. If the intended final state is fully determined and source ownership is
   unchanged, finish or roll back the exact approved switch.
4. If content changed, another writer acted, or the approved state is unclear,
   stop and request a refreshed decision.

Recovery restores one valid serial state; it does not authorize a different
phase order, correction, implementation action, or archive.

## Handoff Between Phases

Keep the old phase's detailed history in its trio. The next phase receives only
the decisions, verified evidence, artifacts, constraints, and open risks it
needs. Link to large evidence instead of copying it. The root receives no
detailed rollup beyond the active pointer and concise overall status.
