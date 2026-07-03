# Registry Contract

Use project-local state under `.codex/multiline/`:

- `.codex/multiline/registry.json`: machine-readable source of truth.
- `.codex/multiline/registry.md`: human-readable coordinator summary.

Only the coordinator may write these files. Workers write line-local handoffs and wait for coordinator intake.

## Minimal JSON Shape

```json
{
  "schema_version": 1,
  "project": "project-name",
  "updated_at": "2026-07-03T00:00:00Z",
  "coordinator": "thread or user-owned coordinator",
  "lines": [
    {
      "id": "line-a",
      "status": "active",
      "objective": "Bounded outcome for this line",
      "cwd": "/absolute/canonical/worktree",
      "branch": "feature/branch",
      "owner": "worker thread or human owner",
      "scope": ["paths or behavior owned by this line"],
      "exclusive_files": ["paths this line may edit"],
      "readonly_inputs": ["paths this line may inspect but not mutate"],
      "handoff_path": "/absolute/path/to/line-local/handoff.md",
      "stop_condition": "pass | no-go | needs-more-evidence | blocked",
      "verification": ["commands or evidence expected before pass"],
      "decision": "current coordinator decision",
      "risks": ["known risk"],
      "updated_at": "2026-07-03T00:00:00Z"
    }
  ],
  "checkpoints": [],
  "decision_records": [],
  "recovery_queue": []
}
```

Support `lines` as either a list or an object keyed by line id when reading old or hand-written registries. When writing new registries, prefer a list.

## Required Line Card Fields

Before a line becomes `active`, record:

- `id`
- `objective`
- `cwd`
- `branch`
- `owner`
- `scope`
- `exclusive_files`
- `handoff_path`
- `stop_condition`
- `verification`

If any required field is missing, keep the line in `proposed` and ask for or derive the missing fact before launching work.

## Markdown Summary

Keep `registry.md` short and coordinator-readable:

- Current coordinator decision.
- Active lines and their gates.
- Waiting intake lines.
- Finish candidates.
- Blocked/no-go lines.
- Recovery queue highlights.
- Next safe action.

Do not duplicate long logs, secrets, raw model outputs, or large artifact listings. Link to paths instead.
