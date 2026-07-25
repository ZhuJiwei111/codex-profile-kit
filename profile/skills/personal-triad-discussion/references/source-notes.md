# Source Notes

Checked: 2026-07-25.

- This local workflow comes from repeated user-mediated GPT Pro discussions in
  which independent framing plus Codex's project evidence changed an important
  decision.
- Local failures included missing kickoff context, relays that replayed the
  entire project, role drift, forgotten locks, and two topic files growing into
  competing sources of truth.
- The current design therefore distinguishes kickoff from continuing-chat
  relays and owns one overwriteable `.triad/<topic-slug>.md`.
- External-model debate research supports viewpoint diversity only
  conditionally; it does not make another model authoritative or justify
  indefinite rounds.

No external chat control, model slug, script, or protocol machinery is bundled.
