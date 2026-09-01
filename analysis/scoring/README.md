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

Recompute: `python3 ../scripts/agreement.py`.

## Headline numbers

- Canonical pair (rater-1 vs GPT-5.6 Sol): exact 68 %, within-1 97 %, Cohen's κ +0.49
  (unweighted) / **+0.64 (quadratic-weighted)**, Krippendorff's α +0.20.
- Reliable dimensions: D2 recency, D3 tool-factuality, D5 benchmark-factuality (κ ≈ 0.7).
- Weak dimensions needing sharper v2 anchors: D1 hardware-constraint (κ 0.15), D9
  internal-consistency (κ 0.14), D7 actionability, D8 security-model.
- Rater severity spread: 8.5 → 14.7 / 18 across the four raters on the same responses.

## Adjudicated ranking (non-anchor)

`perplexity` 18 · `mistral-large-3` 16 · `gpt-5` 14 · `grok-4` 14 · `kimi-instant` 12 ·
`gemini-3.1-pro` 12 · `qwen-3.7-plus` 12 · `meta-llama-4` 11 · `deepseek-expert` 9 ·
`deepseek-instant` 9 · `deepseek-instant-deepthink` 7 · `z-ai` 5. Anchor `claude-sonnet-5`: 15
(excluded from cross-response stats).

## Threats to validity (full list in the report)

1. **Dims 3 & 4 were not blind** for the rater-2 runs — an earlier version of `RATER-PACKET.md`
   leaked the list of real-but-post-cutoff tools. Fixed in the packet now; re-run for a clean
   D3/D4 if the paper needs it.
2. Rater severity varies ~3.6 / 18. `deepseek-chat` is near-uniform 2s (low information).
3. `grok-4` self-scored `grok-4`; `deepseek-chat` scored the DeepSeek responses.
4. `rater-1` is not design-independent (wrote the rubric).

## `RATER-PACKET.md`

The self-contained packet for a fresh, different LLM. Carries the rubric, scoring rules, response
order, output template. The rater must not see the capture `## Reviewer notes` and must not read
`analysis/verification/` before scoring (score from own web searches only).
