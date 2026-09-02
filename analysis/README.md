# `analysis/`

Everything derived from the raw corpus.

```
analysis/
├── findings/     Long-form per-response research notes (deeper than the capture file's
│                 "Reviewer notes"). Currently: claude-sonnet-5-findings.md (the sourced baseline,
│                 21 sections, ~97 URLs — used as the recency/factuality reference for the others).
├── scoring/      One file per rubric rater: <rater>-<YYYY-MM-DD>.md. Independent scores only —
│                 never overwrite another rater's file. Inter-rater agreement (Cohen's κ /
│                 Krippendorff's α) is computed across these. [awaiting rater 2]
├── consensus/    Cross-response synthesis (RQ1): the modal choice per axis, disagreement map,
│                 and the merged reference architecture. Built once ≥ 6 responses are in.
└── scripts/      Reproducible checks (stdlib Python, MIT):
    ├── memory_budget.py    32 GB fit estimator; run against each response's co-resident set.
    └── validate_matrix.py  CSV linter used by `make validate` / CI.
```

## Workflow

1. New capture lands in `data/responses/` + a matrix column.
2. Rater(s) score it against `docs/rubric.md` → `analysis/scoring/`.
3. Deep-dive notes (optional, for high-interest responses) → `analysis/findings/`.
4. When ≥ 6 responses: (re)build `analysis/consensus/`.
5. `analysis/consensus/` → `paper/draft-v1.md` (the write-up).

## Scripts quick ref

```bash
python3 analysis/scripts/memory_budget.py --preset claude
python3 analysis/scripts/memory_budget.py --preset deepseek-expert
python3 analysis/scripts/memory_budget.py --weights 18 3 --ctx 32000 --browser
python3 analysis/scripts/validate_matrix.py data/decisions-matrix.csv
```
