# Source Notes

Checked: 2026-07-18.

This is a local-origin workflow shaped by recurring Codex App task, Git
worktree, long-job, and recovery use. No external workflow text or executable
is bundled.

Key local preferences are a main-process control plane, one immutable worktree
per persistent writer, minimal in-conversation line state, event-driven intake,
and preservation-first recovery. Active monitoring is explicit only, uses a
dedicated App task requesting `gpt-5.6-luna` with low reasoning, and has no
silent executor or model fallback. The main process chooses cadence; without a
better basis it uses `20 -> 40 -> 60 -> 60 ...` minutes. Observer read-only
behavior is a semantic boundary, and observer liveness failure closes the
monitoring path rather than transferring recurring polling to the controller.
