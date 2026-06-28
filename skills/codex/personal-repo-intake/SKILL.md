---
name: personal-repo-intake
description: Use when starting work in an unfamiliar or uncertain local repository, before broad inspection or edits, especially when current directory, git state, project layout, commands, or generated directories are unclear.
---

# Personal Repo Intake

Keep repository discovery bounded. Learn enough to act, then stop exploring.

## Intake

1. Run `pwd`.
2. If inside a repo, run `git status --short`.
3. Discover files with capped `rg --files` or `fd`.
4. Read only relevant local instructions, manifests, scripts, and tests.

## Boundaries

- Prefer targeted `rg` over recursive browsing.
- Cap output with exact paths, globs, `sed`, `head`, `tail`, or tool-native
  limits.
- Exclude heavy/generated paths early: `.git`, `.venv`, `node_modules`, `data`,
  `datasets`, `outputs`, `results`, `checkpoints`, `wandb`, `runs`, `logs`,
  `conda_envs`, and `conda_pkgs`.
- Stop once the edit surface, commands, and verification surface are clear.
- Never revert unrelated user changes.

## Common Mistakes

| Mistake | Correction |
| --- | --- |
| Reading many files before knowing the path | Search exact names, commands, or symbols |
| Ignoring dirty state | Check git status before edits |
| Treating generated files as source | Exclude them unless directly relevant |
