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

## ppt-master local documentation links

- Upstream: `https://github.com/hugohe3/ppt-master`
- Owner: unmanaged standalone installation; no checkout or upstream revision
  metadata was available for the reviewed local snapshot.
- Patch: `ppt-master-local-doc-links.patch`
- Reviewed: 2026-10-25

This two-file patch repairs the installed three-kind template documentation by
linking to bundled workflows and the entrypoint's kind/segment model. Current
upstream documentation uses four kinds and is not a compatible replacement for
that snapshot. The patch changes references only; it does not update the skill
implementation or enroll the external installation in profile sync.

Before applying to an unmanaged installation, back up the two named files and
run `git apply --check` from that skill directory against this patch. Apply it
only when the reviewed preimage matches. Re-review after any upstream update;
an unknown base revision is not permission to overwrite another installation.
