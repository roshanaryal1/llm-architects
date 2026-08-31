# `analysis/scoring/`

One file per rubric rater: `<rater-slug>-<YYYY-MM-DD>.md`. **Independent scores only** — never
edit another rater's file. Inter-rater agreement (Cohen's κ / Krippendorff's α) is computed across
these; see `../scripts/agreement.py` (to be added).

- `RATER-PACKET.md` — the self-contained packet to hand a fresh, *different* LLM (issue #9). It
  carries the 9-dimension rubric, the scoring rules, the response order, and the output template.
  The rater must **not** see the `## Reviewer notes` in the capture files (rater-1's opinions).
- `rater-1-*.md` — rater-1's scores, to be extracted from the `## Reviewer notes` blocks into the
  same table format for comparison. [pending]
