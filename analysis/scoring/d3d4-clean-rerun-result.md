# Clean D3/D4 re-run — result

Date: 2026-09-01. Packet: `RATER-PACKET-D3D4.md` (names no tools; forbids reading
`analysis/verification/`; mandates live web verification; `UNRESOLVED → 1`).

Two raters run: **GPT-5.6 Sol** (ChatGPT, paid) and **Perplexity** (free).

## Headline

**The rater-packet leak did not materially change the canonical rater's D3/D4.**
GPT-5.6 Sol's clean run matched its contaminated #9 run on **11 of 13 responses**; the two
changes (`meta-llama-4` D4 1→2, `deepseek-instant-deepthink` D4 2→0) were both driven by specific
web findings, not by the absence of the leaked list. Sol web-verified independently in both
passes, so the contamination had little to bite on.

The second clean rater, **Perplexity, failed the task** and is discarded — it scored D3 = 0 for
seven responses by treating its own search misses as proof of nonexistence, the exact violation
`UNRESOLVED → 1` exists to prevent. See `d3d4-perplexity-2026-09-01.md`. It is a live
reproduction of the paper's §5 failure mode inside a rater.

## What GPT-5.6 Sol's clean run changed in the adjudicated scores

For D3/D4 specifically, the clean uncontaminated canonical-rater pass is now the best evidence,
and overrides the #9 adjudication on those two dimensions. Four cells move:

| response | dim | was | now | reason (Sol clean, web-verified) |
|---|---|:--:|:--:|---|
| `mistral-large-3` | D3 | 2 | **1** | `brew install goose` installs the wrong formula; the coding agent is `block-goose-cli`. |
| `kimi-instant` | D3 | 2 | **1** | `opencode config set model …` is not a documented OpenCode command. |
| `deepseek-expert` | D4 | 2 | **1** | future primary `Qwen3-Coder-70B` does not resolve (Qwen line is 30B-A3B / 480B / 80B Coder-Next); `DeepSeek-Coder-V3` has no authoritative card. |
| `deepseek-instant-deepthink` | D4 | 1 | **0** | upgrade plan describes `DeepSeek-V4` as a dense model needing 96–128 GB; real V4-Pro / V4-Flash are MoE (1.6T/49B-active; 284B/13B-active). Wrong load-bearing architecture premise. |

`meta-llama-4` D4: Sol clean scored 2 (all tags resolve, incl. `Qwen3-Coder-Next` 80B). Kept at
**1** in the adjudicated table because the response's *primary* model tag `Qwen3.5-35B-A3B` is
still `UNRESOLVED` in `analysis/verification/tool-model-register.md` (Perplexity also could not
resolve it; the likely reality is a mislabel of `Qwen3.6-35B-A3B`). Flagged for a tie-break if a
third clean rater is run.

## Revised adjudicated ranking (non-anchor, /18)

`perplexity` 18 · `mistral-large-3` 15 · `gpt-5` 14 · `grok-4` 14 · `gemini-3.1-pro` 12 ·
`qwen-3.7-plus` 12 · `kimi-instant` 11 · `meta-llama-4` 11 · `deepseek-instant` 9 ·
`deepseek-expert` 8 · `deepseek-instant-deepthink` 6 · `z-ai` 5. Anchor `claude-sonnet-5`: 15.

Movement vs the #9 table: `mistral` 16→15, `kimi` 12→11, `deepseek-expert` 9→8,
`deepseek-instant-deepthink` 7→6. **The band structure is unchanged** — top pair, a middle group,
and the DeepSeek-fast/`z-ai` tail. One notable local flip: `deepseek-instant` (9) now scores
*above* `deepseek-expert` (8), because the clean D4 check hit the "expert" mode's fabricated
future-model tags while the "instant" mode's picks all resolved. The DeepSeek mode effect (§9.2
of the paper) is real but not monotone across every dimension.

## New CLI/install-path errors surfaced (dim 3 = 1, not scored 0)

All real tools, wrong commands — worth listing for the paper's "actionability vs factuality"
point:

| response | bad command | correct form |
|---|---|---|
| `mistral-large-3` | `brew install goose` | `brew install block-goose-cli` |
| `kimi-instant` | `opencode config set model …` | `model` key in `opencode.json`, or `--model` |
| `qwen-3.7-plus` | `mlx.community download …`; `pip install mlx-lm[server]` | `mlx_lm.convert` / `hf download`; `mlx_lm.server` (no `[server]` extra) |
| `deepseek-expert` | `cd llama.cpp && make -j8` | CMake build (Metal on by default) |
| `gemini-3.1-pro` | `LLAMA_METAL=1 make -j` | CMake build |
| `z-ai` | `vllm-mlx-server --model …` | `vllm-mlx serve <model>` |
| `meta-llama-4` | `npm install -g opencode` | `npm install -g opencode-ai` |
| `deepseek-instant` | `brew install playwright` | `brew install playwright-cli` |
| `deepseek-instant-deepthink` | `pip install … sqlite3` | stdlib — no install |

## Register updates from this pass

Fold into `analysis/verification/tool-model-register.md`:

- **`vllm-mlx` → REAL** — `github.com/waybarrios/vllm-mlx`, CLI `vllm-mlx serve` (was `UNRESOLVED`
  / partly in §G).
- **`Qwen3-Coder-70B` → confirmed does NOT exist** — no Qwen card; a `deepseek-expert` future-pick
  fabrication (real Qwen line: 30B-A3B, 480B, 80B Coder-Next).
- **`Qwen3-Coder-32B` → confirmed does NOT exist** — `Qwen2.5-Coder-32B` is the real one; there is
  no Qwen3 32B Coder tag. A `z-ai` alt-list error.
- **`DeepSeek-Coder-V3` → UNRESOLVED** (no authoritative card).
- **`DeepSeek-V4` architecture** — V4-Pro is MoE 1.6T/49B-active; V4-Flash is MoE 284B/13B-active.
  `deepseek-instant-deepthink` calls V4 dense — a genuine defect (added to §E).
- **GLM-5.2 = 753B** per the official card (`mistral-large-3` said 744B — a minor size slip).

## Paper impact

- §11 threat softened: a clean uncontaminated re-run of the canonical rater-2 reproduced its
  contaminated D3/D4 on 11/13 responses; the leak's effect on the reported scores is negligible.
  The threat remains listed (the leak was real; one rater was demonstrably contaminatable in
  principle) but its severity is now bounded by evidence.
- §5 gains a one-line note: a second attempted clean rater (Perplexity) reproduced the
  training-cutoff / search-miss failure mode live.
- §10 ranking table updated to the revised adjudicated totals above.
- §9.2 gains the `deepseek-instant` > `deepseek-expert` local flip on the D4 dimension.
