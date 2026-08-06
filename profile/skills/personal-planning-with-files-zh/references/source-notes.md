# Source Notes

Checked: 2026-08-06.

- Othman Adi's original
  [`planning-with-files`](https://github.com/OthmanAdi/planning-with-files/blob/bc791694b83ef6a9f8f29cdb5adc4dbc66d3f2b6/skills/planning-with-files/SKILL.md)
  established file-backed recovery. The later v3.8.1 platform and its hooks,
  resolver, ledger, attestation, doctor, and stop gates are intentionally not
  adopted.
- Upstream issues #19, #106, #148, #178, #190, #191, #195, and #202 informed
  the need for useful checkpoints, per-task isolation, manual invocation, and
  a small lifecycle.
- Local history showed both successful fresh-task recovery and large,
  duplicated planning artifacts. The local design therefore uses two
  overwriteable current-state owners and no runtime machinery. Existing
  `progress.md` files remain readable legacy records but are not synchronized
  or created for new plans.
- The default project JOURNAL is a separate event-history owner. It does not
  become a second current-state or decision ledger.

No upstream script, hook, template, or substantial prose is bundled.
