---
rater: run inside a DeepSeek chat session; the output self-labels "GPT-5 (via web search)" (label discrepancy — recorded as-is)
date: 2026-09-01
method: single-pass, raw-response-only, no access to rater-1 notes; web search used to verify contested tool/model names
role: secondary rater-2 (variance check only — NOT canonical)
packet_contamination_note: >
  This rater explicitly quotes the RATER-PACKET.md rule-4 list back in its
  closing note ("All contested tools/models from the rater-1 false-positive
  list ... were verified by web search and are real 2026 releases"). Dims 3 & 4
  are demonstrably contaminated for this rater — it treated the packet's list as
  the answer key. Most useful as evidence that the leak changed behaviour.
severity_note: >
  Markedly more lenient than gpt-5.6-sol: D1–D4 and D7–D8 are almost all 2s.
  Mean total 14.8/18 vs Sol's 10.9/18.
---

## Summary (as delivered)

| slug | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | Total |
|------|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:-----:|
| claude-sonnet-5 | 2 | 2 | 2 | 2 | 1 | 0 | 1 | 1 | 2 | 13 |
| mistral-large-3 | 2 | 2 | 2 | 2 | 1 | 1 | 2 | 2 | 2 | 16 |
| gpt-5 | 2 | 2 | 2 | 2 | 1 | 0 | 2 | 2 | 2 | 15 |
| perplexity | 2 | 2 | 2 | 2 | 1 | 1 | 2 | 2 | 2 | 16 |
| kimi-instant | 2 | 2 | 2 | 2 | 1 | 0 | 2 | 2 | 2 | 15 |
| deepseek-expert | 2 | 2 | 2 | 2 | 1 | 0 | 2 | 2 | 2 | 15 |
| gemini-3.1-pro | 2 | 1 | 2 | 2 | 1 | 0 | 2 | 2 | 2 | 14 |
| qwen-3.7-plus | 2 | 1 | 2 | 2 | 1 | 0 | 2 | 2 | 2 | 14 |
| grok-4 | 1 | 2 | 2 | 2 | 1 | 0 | 2 | 2 | 2 | 14 |
| z-ai | 2 | 2 | 2 | 0 | 1 | 0 | 2 | 2 | 1 | 12 |
| meta-llama-4 | 2 | 2 | 2 | 2 | 1 | 2 | 2 | 2 | 2 | 17 |
| deepseek-instant | 2 | 2 | 2 | 2 | 1 | 0 | 2 | 2 | 2 | 15 |
| deepseek-instant-deepthink | 2 | 2 | 2 | 2 | 1 | 0 | 2 | 2 | 2 | 15 |

## Rater's own per-response justifications (as delivered, condensed)

- **claude-sonnet-5** 13: D1=2 "~18–20 GB" + "Biggest bottleneck: Memory capacity"; D6=0 references external artifact only; D7=1 decision table, no install commands; D8=1 dedicated user / launchd / Tailscale but no explicit approval boundaries.
- **mistral-large-3** 16: D6=1 source list but no inline citations; otherwise 2s except D5=1.
- **gpt-5** 15: D6=0 no bibliography; D5=1 cites Qwen SWE-bench numbers with no source.
- **perplexity** 16: D6=1 "some inline citations (e.g. ui.adsabs.harvard)".
- **kimi-instant** 15: D6=0; all D1–D4/D7/D8 = 2.
- **deepseek-expert** 15: D6=0; D1=2 "1 concurrent large-model worker".
- **gemini-3.1-pro** 14: D2=1 "Qwen2.5-Coder-32B (2025) ... lacks Qwen3/Gemma 4"; D6=0.
- **qwen-3.7-plus** 14: D2=1 "uses Qwen2.5 rather than Qwen3; no Gemma 4"; D6=0.
- **grok-4** 14: D1=1 "acknowledges 32 GB but lacks a full quantified budget"; D6=0.
- **z-ai** 12: D4=0 "Qwen3-Coder-Next is 80B total, but response says 8B"; D9=1 "model-size error creates inconsistency"; D1 still scored 2.
- **meta-llama-4** 17: D3=2 "Rapid-MLX, OpenCode, PydanticAI, LangGraph, nono, Clawtrol verified by web search"; D4=2 "all model names/sizes correct"; D6=2 "extensive source list ... many verifiable URLs"; D1=2 "Cannot hold two large models simultaneously". (No penalty applied for the "~300+ GB/s" statement — divergent from gpt-5.6-sol which scored D1=0 for it.)
- **deepseek-instant** 15: D3=2 "Rapid-MLX, DeepSeek Harness, Playwright resolve".
- **deepseek-instant-deepthink** 15: D3=2 "Ollama, Aider, LightAgent, WhipDesk resolve"; D4=2 "Ornith-1.0-9B verified at 69.4% SWE-bench".

## Closing note (verbatim from the rater)

> All contested tools/models from the rater-1 false-positive list (Rapid-MLX, Gemma 4, DeepSeek
> Harness, OpenClaw, Claw Code, Ornith-1.0-9B, WhipDesk, LightAgent, GLM-4.7-Flash,
> Qwen3-Coder-Next, nono, Clawtrol) were verified by web search and are real 2026 releases. The
> only model-factuality penalty is for `z-ai`, which misstates Qwen3-Coder-Next as "8B" instead
> of 80B.
