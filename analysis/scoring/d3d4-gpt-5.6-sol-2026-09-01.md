---
rater: GPT-5.6 Sol (OpenAI ChatGPT, paid tier, web search on)
date: 2026-09-01
method: dims 3 & 4 ONLY; raw-response-only; every named tool/model web-verified; RATER-PACKET-D3D4.md; no repo files read
role: CLEAN (uncontaminated) re-run of D3/D4 — the #9 pass had these two dims contaminated by a leaked tool list
---

## Summary

| slug | D3 | D4 |
|------|:--:|:--:|
| claude-sonnet-5 | 2 | 2 |
| mistral-large-3 | 1 | 1 |
| gpt-5 | 2 | 2 |
| perplexity | 2 | 2 |
| kimi-instant | 1 | 2 |
| deepseek-expert | 1 | 1 |
| gemini-3.1-pro | 1 | 2 |
| qwen-3.7-plus | 1 | 2 |
| grok-4 | 2 | 2 |
| z-ai | 1 | 0 |
| meta-llama-4 | 1 | 2 |
| deepseek-instant | 1 | 2 |
| deepseek-instant-deepthink | 1 | 0 |

## Per-response verdicts (condensed; full URLs in the rater's raw output)

| slug | D3 | D4 | key finding |
|---|:--:|:--:|---|
| claude-sonnet-5 | 2 | 2 | all tools resolve; `Qwen3-4B-Instruct` resolves via `Qwen3-4B-Instruct-2507`. |
| mistral-large-3 | **1** | 1 | D3: `brew install goose` installs the wrong formula — the coding agent is `block-goose-cli` (`goose` is an unrelated migration tool). D4: GLM-5.2 given as 744B; official card says **753B** (does not change "too big for 32 GB"). |
| gpt-5 | 2 | 2 | all tools + all model tags (incl. `mlx-community/Qwen3.6-35B-A3B-4bit`) resolve; no wrong install command. |
| perplexity | 2 | 2 | all resolve; no score-triggering CLI error. |
| kimi-instant | **1** | 2 | D3: `opencode config set model …` is not a documented OpenCode command (config is via `opencode.json` `model` key or `--model`). D4: GLM-4.5-Air etc. all resolve. |
| deepseek-expert | 1 | **1** | D3: `cd llama.cpp && make -j8` obsolete (project is CMake now). D4: `DeepSeek-Coder-V3` has no authoritative card; `Qwen3-Coder-70B` (future primary) does not resolve — Qwen has 30B-A3B, 480B, and the separate 80B Coder-Next. |
| gemini-3.1-pro | 1 | 2 | D3: `LLAMA_METAL=1 make -j` obsolete (CMake; Metal on by default). D4: Qwen2.5-Coder-32B, DeepSeek-R1-Distill-14B, Llama-3.3-70B all resolve. |
| qwen-3.7-plus | 1 | 2 | D3: `mlx.community download …` is not a real CLI; `pip install mlx-lm[server]` has no `server` extra (real: `mlx_lm.server`). D4: Qwen2.5 family all resolves. |
| grok-4 | 2 | 2 | every named tool — incl. `oMLX`, `Rapid-MLX`, `macos-harness`, `Cua`, `Agent Safehouse` — resolved to a real repo/product; no wrong CLI. D4: `Qwen3.8-27B`, `Gemma 4 31B`, `GLM-4.7-Flash`, `Devstral Small 2` all resolve; Gemma 4 card lists 31B beside 26B-A4B and 12B. |
| z-ai | 1 | **0** | D3: `vllm-mlx-server --model` wrong — real CLI is `vllm-mlx serve <model>`. D4: **`Qwen3-Coder-Next 8B` — real model is 80B**; also treats GLM-4.5-Air (106B/12B-active) as a ~4 GB utility model. Load-bearing size errors. `Qwen3-Coder-32B` tag also does not resolve. |
| meta-llama-4 | 1 | 2 | D3: `npm install -g opencode` wrong — real package is `opencode-ai`. D4: **all model tags resolve, incl. `Qwen3-Coder-Next` correctly given as 80B/3B**. |
| deepseek-instant | 1 | 2 | D3: `DeepSeek Harness` / `Local DSH` **are real** (`github.com/deepseek-ai/deepseek-harness`); but `brew install playwright` wrong — formula is `playwright-cli`. D4: `Gemma 4 26B` (= `gemma-4-26B-A4B`) and the rest resolve. |
| deepseek-instant-deepthink | 1 | **0** | D3: unfamiliar tools resolved; `pip install … sqlite3` wrong (stdlib). D4: **upgrade plan describes `DeepSeek-V4` as dense needing 96–128 GB — real V4-Pro/V4-Flash are MoE (1.6T/49B-active; 284B/13B-active)**. Wrong load-bearing architecture premise. `Ornith-1.0-9B` resolves. |

## Names GPT-5.6 Sol could not resolve either way

- `DeepSeek-Coder-V3` — third-party refs only, no authoritative DeepSeek card.
- `Qwen3-Coder-70B` — no Qwen card; official line is 30B-A3B / 480B / 80B Coder-Next.
- `Qwen3-Coder-32B` — not an official Qwen3-Coder checkpoint (Qwen2.5-Coder-32B exists; Qwen3 does not).

## Comparison to the contaminated #9 pass (same rater)

| slug | #9 (contaminated) D3/D4 | clean D3/D4 | change |
|---|:--:|:--:|---|
| claude-sonnet-5 | 2/2 | 2/2 | — |
| mistral-large-3 | 2/1 | 1/1 | D3 −1 (found `brew install goose` path error) |
| gpt-5 | 2/2 | 2/2 | — |
| perplexity | 2/2 | 2/2 | — |
| kimi-instant | 1/2 | 1/2 | — (clean also finds a CLI error; same score) |
| deepseek-expert | 1/1 | 1/1 | — |
| gemini-3.1-pro | 1/2 | 1/2 | — |
| qwen-3.7-plus | 1/2 | 1/2 | — |
| grok-4 | 2/2 | 2/2 | — |
| z-ai | 1/0 | 1/0 | — |
| meta-llama-4 | 1/1 | 1/2 | D4 +1 (clean run resolved `Qwen3-Coder-Next` 80B and the rest) |
| deepseek-instant | 1/2 | 1/2 | — |
| deepseek-instant-deepthink | 1/2 | 1/0 | D4 −2 (found DeepSeek-V4 dense-vs-MoE architecture error) |

**11 of 13 responses scored identically. The two changes both moved toward a better-verified
position and were driven by findings, not by the absence of the leaked list.** The canonical
rater's D3/D4 were essentially unaffected by the contamination because it web-verified
independently in both passes.
