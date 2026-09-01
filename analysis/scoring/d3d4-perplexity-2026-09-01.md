---
rater: Perplexity (free, web search)
date: 2026-09-01
method: dims 3 & 4 ONLY; RATER-PACKET-D3D4.md
role: CLEAN re-run attempt — DISCARDED as a rater (protocol violation, see below). Retained as a data point.
---

## Why this run is discarded

The packet rule is explicit: **"your searches find nothing either way → UNRESOLVED → this scores
the dimension 1, never 0."** This rater instead scored D3 = 0 whenever *its own searches* failed
to surface a project, calling that "a positively unsupported / non-found named tool
recommendation."

Its own "names I could not resolve" list contains: `rapid-mlx`, `OpenClaw`, `Clawtrol`, `nono`,
`cplt`, `agent-policy-engine`, `WhipDesk`, `Ornith-1.0-9B`, `DeepSeek Harness`, `Local DSH`,
`Gemma 4 31B`, `Gemma 4 12B`, `GLM-4.7-Flash`, `LightAgent`, `DiffResearch`. **Every one of the
first thirteen is confirmed real** in `analysis/verification/tool-model-register.md` and was
resolved without difficulty by GPT-5.6 Sol on the same task. The last two remain genuinely
unresolved but should still have scored 1, not 0.

This is a live reproduction, inside a rater, of the exact failure mode this study documents in
§5 of the paper: **treating "not found by my search" as "does not exist" penalises real,
current tooling.** It belongs in the paper as an anecdote, not in the adjudicated scores.

## Scores as delivered (NOT used)

| slug | D3 | D4 |
|------|:--:|:--:|
| claude-sonnet-5 | 1 | 1 |
| mistral-large-3 | 1 | 1 |
| gpt-5 | 1 | 1 |
| perplexity | 1 | 1 |
| kimi-instant | 1 | 1 |
| deepseek-expert | 0 | 1 |
| gemini-3.1-pro | 1 | 2 |
| qwen-3.7-plus | 0 | 2 |
| grok-4 | 0 | 0 |
| z-ai | 0 | 0 |
| meta-llama-4 | 0 | 0 |
| deepseek-instant | 0 | 0 |
| deepseek-instant-deepthink | 0 | 0 |

It also applied a blanket D3 = 1 ceiling to responses it *did* verify ("unresolved
command/version details" on claude, gpt-5, perplexity itself), so even its non-zero scores are
not rubric-faithful (a wrong CLI is D3 = 1; "I didn't check the version" is not).

## The one useful signal

The D4 = 0 calls for `z-ai` (Qwen3-Coder-Next 8-vs-80B) and its instinct that
`deepseek-instant-deepthink` / `meta-llama-4` model layers are shaky are *directionally*
consistent with GPT-5.6 Sol and rater-1 — but arrived at by the wrong method.
