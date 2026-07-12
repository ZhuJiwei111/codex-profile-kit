# Hook Testing

## Test Sequence

For a behavior change, preserve this order:

1. Record `codex --version` and the active hook source.
2. Add the smallest payload fixture that demonstrates the intended match or
   regression.
3. Run it and confirm that it fails for the intended reason.
4. Make the minimal implementation or rule change.
5. Re-run the focused test, then the nearby hook suite.
6. Exercise a match, a non-match, and an adjacent-rule conflict.
7. Inspect the final hook definition and trust state.

Use synthetic payloads. Do not copy commands, paths, environment values, or
transcripts that contain credentials.

## Local Suite

```bash
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s "$CODEX_HOME/hooks" -p 'test_*.py' -v
python3 -m json.tool "$CODEX_HOME/hooks.json" >/dev/null
```

The suite should cover rule parsing, exact event classification, native command
input, warning JSON, deny JSON, block precedence, malformed input, and active
configuration wiring.

## Read-Only Payload Smokes

This warning fixture evaluates the adapter without executing the embedded Bash
command:

```bash
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
printf '%s\n' '{"session_id":"test-session","transcript_path":null,"cwd":"/tmp","hook_event_name":"PreToolUse","model":"test-model","permission_mode":"default","turn_id":"test-turn","tool_name":"Bash","tool_use_id":"test-call","tool_input":{"command":"pip install demo-package"}}' \
  | python3 "$CODEX_HOME/hooks/hookify_codex_runner.py" --event PreToolUse \
  | python3 -m json.tool
```

Use a harmless non-matching command and assert empty stdout:

```bash
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
test -z "$(printf '%s\n' '{"session_id":"test-session","transcript_path":null,"cwd":"/tmp","hook_event_name":"PreToolUse","model":"test-model","permission_mode":"default","turn_id":"test-turn","tool_name":"Bash","tool_use_id":"test-call","tool_input":{"command":"printf safe"}}' \
  | python3 "$CODEX_HOME/hooks/hookify_codex_runner.py" --event PreToolUse)"
```

For a block rule, feed a synthetic payload that matches only a test rule in an
isolated temporary rule directory or use the unit-test harness. Never aim a
destructive command at the real shell merely to test a hook.

## Output Checks

For every matching payload, verify:

- stdout contains exactly one JSON object
- `hookSpecificOutput.hookEventName` matches the event
- a warning uses `additionalContext`
- a block uses `permissionDecision: "deny"` and a reason
- diagnostics appear only on stderr
- no secret or raw authenticated value is present

Exit `0` and empty stdout are valid for a non-match.

## Definition And Trust Checks

Changing a handler command, matcher, event, timeout, or registered hook source
changes the hook definition. After tests pass:

1. Do not edit a persisted trust hash.
2. Tell the user exactly which definition changed.
3. Ask the user to inspect and trust it through `/hooks`.
4. Do not claim the hook is active until that review is complete.

Changing only a dynamically loaded Markdown rule does not change `hooks.json`,
but still test the rule and report its enabled state.

## Skill Routing Probes

Use these scenarios when validating the skill itself:

| Prompt | Expected owner |
| --- | --- |
| Create and payload-test a focused PreToolUse guard | `personal-codex-hook-rules` |
| Audit the whole reusable profile, including hooks | `personal-codex-audit` |
| Decide whether to install, disable, or archive a hook skill | `personal-skill-hygiene` |
| Add a durable response-writing preference | AGENTS.md or a writing skill, not a hook |
| Diagnose an unexpected hook test failure | `personal-evidence-debugging`, using this protocol reference as needed |
