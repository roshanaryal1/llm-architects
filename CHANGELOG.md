# Changelog

All notable changes to the corpus and analysis. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/). Dates are ISO-8601.

## [Unreleased]

### Added — 2026-08-31 — repository bootstrap
- Enterprise repo scaffolding: `README`, `CONTRIBUTING`, `CODE_OF_CONDUCT`, `CITATION.cff`,
  dual licensing (MIT code / CC-BY-4.0 data), `.gitignore`, `.editorconfig`, `.markdownlint.json`,
  `Makefile`, GitHub issue/PR templates, `validate.yml` CI.
- `prompts/prompt-v1.md` — canonical study instrument, frozen.
- `docs/`: `methodology.md`, `rubric.md`, `comparison-axes.md`, `glossary.md`, `paper-options.md`.
- `analysis/scripts/`: `memory_budget.py` (32 GB fit estimator), `validate_matrix.py` (CSV lint).
- `data/decisions-matrix.csv` — 39 decision axes, 10 planned model columns.
- `data/schema/decisions-matrix.schema.md`.

### Added — 2026-08-31 — responses 1–4 captured
- `claude-sonnet-5` — Anthropic, browsing ON, ~97 sources. Trust: HIGH (but not a blind peer;
  used as consensus anchor). MoE-first (Qwen3-Coder-30B-A3B + gpt-oss-20b), `llama-swap`,
  `sqlite-vec`, Apple `container` sandbox, optional cloud < $30/mo.
- `qwen-3.7-plus` — Alibaba, no sources. Trust: MEDIUM. Honest 2024-era snapshot
  (Qwen2.5 dense 32B, Aider+OpenHands, ChromaDB, Telegram, no containers). Strong process
  agreement with Claude; stale model picks; no M6-specifics.
- `deepseek-instant` — DeepSeek fast mode, no sources. Trust: LOW. Fabricated stack:
  "Rapid-MLX", "DeepSeek Harness (DSH)", "Gemma 4 26B", "Qwen3.5/3.6/3.8" version numbers.
  Internal contradiction (Ollama forbidden in J, installed in Phase 4).
- `deepseek-expert` — DeepSeek deep mode, no sources. Trust: MEDIUM-HIGH. Realistic stack
  (Claude Code + custom orchestrator, Redis+Celery, Grafana+Prometheus, Docker+seatbelt).
  Point-versions lag (Opus 4.5 / Gemini 2.5 Pro / RTX 4090). Internal contradiction on Docker
  (recommended in A/H, forbidden in J).

### Added — 2026-08-31 — responses 5–6 + free-model identification
- Web-searched the current free-tier default model per provider (Aug 2026):
  DeepSeek free chat = **DeepSeek-V4-Pro** (GA 2026-04-24, 284B MoE / 13B active, 1M ctx);
  Perplexity free = **Sonar** (Llama-based, auto model-selection);
  Qwen free chat ≈ **Qwen3.7** (flagship **Qwen3.8-Max** GA 2026-08-03).
  Updated `qwen-3.7-plus.md` and both DeepSeek `model_version_id` fields accordingly.
- `perplexity` — Perplexity free tier. Trust: MEDIUM-HIGH. Only non-Claude response to cite
  sources (~17 real URLs). Most security-thorough response; explicitly refuses to fake M6
  throughput numbers; LangGraph + OpenHands + Ollama→MLX + Qwen3-Coder-30B-A3B + Qdrant(embedded)
  + Tailscale Serve; deliberately conservative (avoids 2026-edge tooling).
- `deepseek-instant-deepthink` — DeepSeek-V4-Pro free chat, DeepThink mode. Trust: LOW.
  Highest fabrication count in the corpus: `Ornith-1.0-9B`, `Qwen3.5-35B-A3B` (tag), `WhipDesk`,
  `Cloak`, `Helmrig`, `DiffResearch`, `LightAgent`, `Engram-Mem`, plus invented benchmark numbers.
  Also uniquely advises memory **oversubscription** ("~32–34 GB … slight oversubscription acceptable").
- `memory_budget.py`: added `perplexity` and `deepseek-deepthink` presets.
- `decisions-matrix.csv`: now 39 axes × 11 model columns (6 filled: claude, qwen37plus,
  deepseek_instant, deepseek_expert, deepseek_deepthink, perplexity).

### Pending
- Responses: GPT-5, Gemini 3 Pro, Grok 4, Mistral Large 3, Llama 4.
- `prompts/prompt-v2.md` / `prompt-v3.md` paraphrases for prompt-sensitivity (RQ6).
- Second independent rater for the rubric; inter-rater agreement.
- `analysis/consensus/` synthesis once ≥ 6 responses are in.
