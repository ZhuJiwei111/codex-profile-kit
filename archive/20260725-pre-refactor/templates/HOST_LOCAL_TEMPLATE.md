# Host Local Overlay Template

Copy this file to `~/.codex/HOST_LOCAL.md` on the target machine. Fill in only
facts that are true there, keep the file permission at `0600`, and never store
secrets in it.

## Read Policy

- Read this overlay only when host-dependent work requires it.
- Re-check dynamic facts such as tools, limits, storage, and devices when they
  affect the task.
- Record paths and commands, never credential values.

## Host

- Home directory:
- Primary work root:
- OS:
- Default shell:
- Non-interactive shell startup behavior:
- Timezone for user-facing timestamps:
- Useful tools confirmed with `command -v`:

## Python And Conda

- System Python path:
- System Python purpose:
- Conda root:
- Codex fallback environment name:
- Codex fallback environment prefix:
- Codex fallback Python version:
- Codex fallback invocation:
- Codex fallback package installer:
- Codex fallback role and write policy:
- Project environment root:
- Conda package cache:
- Preferred package manager:
- User-site Python visibility policy:

## Proxy And Network

- Are proxy variables set by default:
- Proxy enable command:
- Proxy disable command:
- Direct-network test command for large downloads:
- Notes for package indexes or GitHub access:

## Storage And GPU

- Storage paths to check before large artifacts:
- Storage check command:
- Current resource and cgroup check commands:
- GPU availability:
- CUDA home:
- CUDA version:
- Required GPU scoping convention:

## Local Install Decisions

- Which skills were installed:
- Were hooks enabled:
- Connectors re-authenticated:
- Date of last smoke test:

## Known Transient Tool And Source Limitations

- Tool, helper, or endpoint:
- Observed failure and date:
- Current bounded fallback:
- Conditions that justify retry:

## Remote Connection Contract

- Control-plane owner:
- Contract file to read before changing transport, proxy, launcher, or app-server startup:
