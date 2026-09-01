# `analysis/scoring/`

Rubric scoring for RQ1–RQ6. One file per rater; **independent scores only** — never edit another
rater's file.

## Status: issue #9 COMPLETE (2026-09-01)

Four raters scored all 13 responses on the 9-dimension rubric.

| file | rater | role |
|---|---|---|
| `rater-agreement-2026-09-01.md` | — | **the report**: agreement stats, adjudication of all 37 gaps, adjudicated final scores, threats to validity |
| `scores-adjudicated-2026-09-01.csv` | — | the reportable score table |
| `gpt-5.6-sol-2026-09-01.md` + `scores-gpt-5.6-sol-2026-09-01.csv` | GPT-5.6 Sol (ChatGPT, paid) | **canonical rater-2** |
| `grok-4-rater-2026-09-01.md` + `scores-grok-4-2026-09-01.csv` | Grok 4 | variance check |
| `deepseek-chat-rater-2026-09-01.md` + `scores-deepseek-chat-2026-09-01.csv` | DeepSeek chat run | variance check (low-information — near-uniform 2s) |
| `scores-rater-1-2026-09-01.csv` | rater-1 (this repo, from capture reviewer notes) | first rater |
| `RATER-PACKET-D3D4.md` + `d3d4-gpt-5.6-sol-2026-09-01.md` (+ csv) | GPT-5.6 Sol | **clean D3/D4 re-run** — used to override the contaminated #9 D3/D4 |
| `d3d4-perplexity-2026-09-01.md` (+ csv) | Perplexity | clean D3/D4 attempt — **discarded** (violated `UNRESOLVED → 1`) |
| `d3d4-clean-rerun-result.md` | — | the D3/D4 re-run verdict + the four cell changes |

Recompute: `python3 ../scripts/agreement.py`.

## Headline numbers

- Canonical pair (rater-1 vs GPT-5.6 Sol): exact 68 %, within-1 97 %, Cohen's κ +0.49
  (unweighted) / **+0.64 (quadratic-weighted)**, Krippendorff's α +0.20.
- Reliable dimensions: D2 recency, D3 tool-factuality, D5 benchmark-factuality (κ ≈ 0.7).
- Weak dimensions needing sharper v2 anchors: D1 hardware-constraint (κ 0.15), D9
  internal-consistency (κ 0.14), D7 actionability, D8 security-model.
- Rater severity spread: 8.5 → 14.7 / 18 across the four raters on the same responses.

## Adjudicated ranking (non-anchor) — after the clean D3/D4 re-run (2026-09-01)

`perplexity` 18 · `mistral-large-3` 15 · `gpt-5` 14 · `grok-4` 14 · `gemini-3.1-pro` 12 ·
`qwen-3.7-plus` 12 · `kimi-instant` 11 · `meta-llama-4` 11 · `deepseek-instant` 9 ·
`deepseek-expert` 8 · `deepseek-instant-deepthink` 6 · `z-ai` 5. Anchor `claude-sonnet-5`: 15
(excluded from cross-response stats).

## Clean D3/D4 re-run (2026-09-01)

`RATER-PACKET-D3D4.md` — dims 3 & 4 only, no leaked list, mandatory web verification. Files:
`d3d4-gpt-5.6-sol-2026-09-01.md` (+ csv), `d3d4-perplexity-2026-09-01.md` (+ csv, **discarded**
— violated `UNRESOLVED → 1`), `d3d4-clean-rerun-result.md` (the verdict).

**Result:** the canonical rater's clean D3/D4 matched its contaminated #9 pass on 11/13
responses. The leak's effect on the reported scores is small. Four cells moved on new web
findings: `mistral` D3 2→1, `kimi` D3 2→1, `deepseek-expert` D4 2→1, `deepseek-instant-deepthink`
D4 1→0.

## Threats to validity (full list in the report)

1. **Dims 3 & 4 were not blind** for the #9 rater-2 runs — an earlier `RATER-PACKET.md` leaked
   the real-but-post-cutoff tool list. **Bounded by the clean re-run above**: the canonical
   rater's uncontaminated D3/D4 reproduced its contaminated pass on 11/13 responses, so the
   leak's effect on the table is small. The threat is still listed (the leak was real) but its
   severity is now measured, not assumed.
2. Rater severity varies ~3.6 / 18. `deepseek-chat` is near-uniform 2s (low information).
3. `grok-4` self-scored `grok-4`; `deepseek-chat` scored the DeepSeek responses.
4. `rater-1` is not design-independent (wrote the rubric).

## `RATER-PACKET.md`

The self-contained packet for a fresh, different LLM. Carries the rubric, scoring rules, response
order, output template. The rater must not see the capture `## Reviewer notes` and must not read
`analysis/verification/` before scoring (score from own web searches only).
