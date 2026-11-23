# Native hook maintenance

Use hooks only for narrow mechanical prohibitions. Before changing one, inspect
the active client protocol, canonical tool/event name, definition and handler.
Use current official documentation or the installed release schema; a historical
test is not current dispatch evidence. Treat PreToolUse as a guardrail, not a
complete security boundary.

Check one matching, one nonmatching and one adjacent-tool payload using the
existing harness. Keep stdout empty or valid event-specific JSON and diagnostics
on stderr. Never change stored trust decisions. Changed unmanaged definitions
need native /hooks review; retain a runner loaded by an active task until a fresh
task verifies the new definition. Report actual dispatch coverage and remaining
limitations rather than assuming a matching function proves runtime adoption.
