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

### Pending
- Responses: GPT-5, Gemini 3 Pro, Grok 4, Mistral Large 3, Llama 4, one deep-research agent.
- `prompts/prompt-v2.md` / `prompt-v3.md` paraphrases for prompt-sensitivity (RQ6).
- Second independent rater for the rubric; inter-rater agreement.
- `analysis/consensus/` synthesis once ≥ 6 responses are in.
