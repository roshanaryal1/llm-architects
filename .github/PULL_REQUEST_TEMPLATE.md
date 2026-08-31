<!-- Delete the sections that don't apply. -->

## Type

- [ ] New model response
- [ ] Rubric scoring (new rater)
- [ ] Consensus / analysis
- [ ] Docs / tooling
- [ ] Correction to an existing capture (append-only; raw response untouched)

## Summary

<!-- One or two sentences. Which model, or which analysis. -->

## New model response checklist

- [ ] Ran **only** the text between the START/END markers of `prompts/prompt-v1.md`
- [ ] `data/responses/<slug>.md` created from `_TEMPLATE.md`
- [ ] `## Raw response` is **verbatim** — no typo fixes, no reflowed tables, no trimming
- [ ] Front-matter complete: model, version, provider, interface, browsing, cutoff,
      prompt_version, date_run, run_by, notes_on_run, `trust_rating` (+ one-line reason)
- [ ] `## Model's own cited sources` filled (or `NONE`)
- [ ] `## Reviewer notes` covers: recency (RQ4), hallucinations (RQ2, list each with severity),
      32 GB fit (RQ3 — paste `memory_budget.py` verdict), internal consistency (RQ6),
      agreements + divergences vs existing responses
- [ ] Column added to `data/decisions-matrix.csv`, fabrications flagged in-cell
- [ ] `CHANGELOG.md` updated
- [ ] `make check` passes locally

## Scoring PR checklist

- [ ] New file `analysis/scoring/<rater>-<YYYY-MM-DD>.md` (did **not** edit another rater's file)
- [ ] Scored every response independently against `docs/rubric.md`, 0/1/2 per dimension
- [ ] One-line justification per dimension, quoting the response text

## Notes for the reviewer
