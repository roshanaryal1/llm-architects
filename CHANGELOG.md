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

### Added — 2026-08-31 — response 7 (Gemini 3.1 Pro)
- Web-checked Gemini free tier: Pro-series left Google AI Studio's free tier 2026-04-01
  (free tier is now Flash-class); Pro access is paid or via the Gemini app. Recorded in the
  capture's `model_version_id`.
- `gemini-3.1-pro` — Google. Trust: MEDIUM. 0 sources. All named tools real (llama.cpp, Aider,
  PaperQA2, SearXNG, Crawl4AI, sqlite-vec, Lima, Mosh, Tailscale). Distinctive: only response to
  pick **llama.cpp as the primary engine** (not MLX); only one to name **PaperQA2** for
  citation-grounded research; agrees with Claude on **sqlite-vec** (vs the Chroma camp); runs
  **2 llama.cpp slots of one model** (`-np 2`) instead of 1-heavy+N-light. Weak points: 2024-era
  models (Qwen2.5-Coder-32B dense, R1-Distill-14B), stale cloud-fallback list ("Claude 3.5
  Sonnet" / "DeepSeek-V3"), no M6-specific facts.
- `memory_budget.py`: +`gemini` preset. `decisions-matrix.csv`: 39 axes × 11 columns (7 filled).

### Added — 2026-08-31 — CI fix + response 8 (Kimi Instant)
- **CI:** fixed the always-failing `markdownlint` job (issue #1, PR #2). `.markdownlint.json`
  disables cosmetic rules that verbatim captures trip; the job now lints authored prose only
  (`data/responses/**` and `analysis/findings/**` exempt). Deprecated actions bumped
  (checkout@v5, setup-node@v5, setup-python@v6). `validate` workflow green on `main`.
- Web-checked Kimi free tier: latest is **Kimi K3** (2.8T MoE, 1M ctx, weights 2026-07-27);
  interim K2.5/K2.6/K2.7-Code. Recorded in the capture's `model_version_id`.
- `kimi-instant` — Moonshot AI, free chat, Instant mode. Trust: MEDIUM-HIGH. Ran web searches
  (inline `cite web_search:N#M` markers — 0 resolvable URLs). All load-bearing tools real
  (Aider, OpenCode, OpenHands, Goose, LiteLLM, Firecrawl, Tavily, Perplexity Sonar, sqlite-vec,
  Cognee, Tailscale). Distinctive: **Ollama-0.19-MLX as the server**, **LiteLLM proxy** as a core
  router, **Firecrawl + Perplexity Sonar** managed research (free tiers) instead of self-hosted
  SearXNG, **sqlite-vec** camp (with Claude + Gemini). Weak: stale cloud fallback ("Claude 3.5
  Sonnet / GPT-4o"), inflated numbers ("OpenCode 198k stars", "gpt-oss 98.3%"), no M6 facts.
- `memory_budget.py`: +`kimi`, +`mistral`, +`mistral-two-resident` presets.
- `decisions-matrix.csv`: 39 axes × 12 columns (8 filled).

### Added — 2026-08-31 — response 9 (Mistral Large 3)
- Web-checked Mistral free tier: **Mistral Large 3** (675B total / 41B active, MoE, Apache-2.0,
  released 2025-12-02) is the 2026 flagship and the Le Chat free-tier model.
- `mistral-large-3` — converted from the raw `./Mistral.md` the user dropped at the repo root
  (wrapped as a proper capture, body byte-for-byte unchanged; root copy deleted). Trust: **HIGH** —
  the most rigorously-sourced response after the anchor: explicit Methodology / Limitations /
  Open Questions sections, ~36 credibility-rated sources with dates, engaged M6 specifics
  (170 GB/s, dual Neural Engine, 2 nm, ship dates), current 2026 frontier-model landscape
  (GLM-5.2 744B/40B-active, Kimi K3 2.8T, DeepSeek V4 — correctly ruled out for local), current
  tooling (mlx-lm 0.31.x, **oMLX SSD-tiered KV cache**, vllm-mlx, llama-swap v201, GPT-Researcher,
  Graphiti). Zero fabrications. Only response to raise SSD KV-cache spill and MLX
  RDMA-over-Thunderbolt clustering. Weakness: ~6 of ~36 "sources" are `google.com/search` URLs.
- `decisions-matrix.csv`: `mistral_large3` column filled (39 axes; 9 of 12 columns filled).

### Pending
- Responses: GPT-5, Grok 4, Llama 4.
- `prompts/prompt-v2.md` / `prompt-v3.md` paraphrases for prompt-sensitivity (RQ6).
- Second independent rater for the rubric; inter-rater agreement.
- `analysis/consensus/` synthesis once ≥ 6 responses are in.
