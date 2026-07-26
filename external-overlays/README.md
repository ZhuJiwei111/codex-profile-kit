# External Skill Overlays

These patches preserve deliberate local adaptations to externally maintained
skills without making `profile_sync.py` install or partially manage their
upstream trees.

## awesome-rebuttal

- Upstream: `https://github.com/xiongqi123123/awesome-rebuttal`
- Base revision: `3434455fb2460b85793b4e3082bd28bf86ff7323`
- Patch: `awesome-rebuttal.patch`
- Reviewed: 2026-07-26

Recovery requires an independently reviewed checkout of the exact base
revision. From that checkout:

```bash
git apply --check <profile-repo>/external-overlays/awesome-rebuttal.patch
git apply <profile-repo>/external-overlays/awesome-rebuttal.patch
```

The patch makes invocation manual-only, preserves explicit Git and questionnaire
authority, and fixes capability paths. Re-review the upstream diff and update
the recorded base revision before rebasing the overlay.
