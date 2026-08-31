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

### Added — 2026-08-31 — response 10 (GPT-5.6 Luna) — closes #5
- Web-checked ChatGPT free tier: default since **2026-08-06** is **GPT-5.6 Luna** (smallest of
  the GPT-5.6 family: Luna / Terra / Sol). Recorded in the capture's `model_version_id`.
- `gpt-5` — OpenAI ChatGPT free tier. Trust: **HIGH** — rivals `mistral-large-3` and `perplexity`,
  close to the anchor. 87-section architecture review; every named tool real, current and
  correctly described (Pydantic AI durable-execution integrations, OpenHands headless
  auto-approval, Exa Agent beta, Letta MemFS, Mem0 2026 benchmark caveats, sqlite-vec pre-v1,
  Tailnet Lock). Engaged M6 specifics (170 GB/s, dual NE, ship date). Strong epistemic discipline
  ("benchmarks as capability indicators not throughput"); zero fabrications. Distinctive:
  **Pydantic AI** orchestration substrate (dedicated section arguing against LangGraph-as-core);
  **Qwen3.6-35B-A3B** primary (rejects the 80B Qwen3-Coder-Next); **Qwen Code** interactive
  console; **Exa Search + Contents**; **`capability://` filesystem broker**; **`privacy_class`
  per-task data routing**; **queue-aware keep-awake**. Weakness: ~20 inline factual attributions
  but no resolvable Sources list.
- `memory_budget.py`: +`gpt5` preset (Qwen3.6-35B-A3B 4-bit + Qwen3.5-4B both resident → ~4 GB over).
- `decisions-matrix.csv`: `gpt5` column filled (39 axes; 10 of 12 columns).

### Added — 2026-08-31 — response 11 (Meta / Llama 4) — closes #7
- `meta-llama-4` — converted from the raw `./data/responses/meta.md` the user dropped (wrapped as
  a proper capture, body byte-for-byte unchanged; renamed to the slug convention). Meta AI /
  hosted Llama 4; exact variant + host not disclosed. Trust: **LOW**.
- **The most-cited response in the corpus (99 numbered refs + a Sources list) and the lowest
  citation quality.** ~60% of citations are junk `github.com/<user>/<repo>/commit|pull|issues|SKILL.md`
  URLs cited as authoritative; several "support" fabricated tools. Recycles the fabricated
  **`Rapid-MLX`** (+ the same `raullenchai` Homebrew tap `deepseek-instant` invented) and
  **`Gemma 4`**; invents a fake `Qwen3.5-35B-A3B` OpenRouter id; invents an entire
  **`OpenClaw` / `Claw Code` / `Clawtrol` / `memo` / `cplt` / `nono`** ecosystem; **gets M6
  bandwidth wrong** ("~300+ GB/s"; actual is 170); mis-titles a real arXiv paper. The architecture
  *shape* lands on consensus (MLX + 1 large / 2-3 small workers + SQLite WAL + LiteLLM +
  PydanticAI/LangGraph + launchd + Tailscale Serve + coordinator/worker) but every load-bearing
  product pick is fabricated.
- `memory_budget.py`: +`meta` preset (35B-A3B + Qwen2.5-Coder-7B both resident → ~7 GB over).
- `decisions-matrix.csv`: `llama4` column filled (39 axes; **11 of 12 columns** — only `grok4` left).

### Added — 2026-08-31 — response 12 (Grok 4) — closes #6 — **data collection complete**
- `grok-4` — xAI Grok, free tier. Trust: **MEDIUM**. Engaged the real M6 spec **correctly**
  (170 GB/s, 2s+4P+6E core layout) — unlike `meta-llama-4` which got bandwidth wrong. Primary
  picks (Qwen 27B/35B-A3B, Devstral, OpenHands + Aider, custom supervisor + LangGraph, sqlite-vec,
  Tailscale, launchd + watchdog) are all real and match the cross-model consensus almost exactly.
  But **0 sources**, and it casually names three fabricated model families in its *alternatives*
  lists: **`rapid-mlx`** (the 3rd response across 3 vendors — DeepSeek, Meta, xAI — to name
  Rapid-MLX), **`Gemma 4 31B`** (the 3rd response to invent "Gemma 4", each giving a different
  size: 26B / 12B / 31B — the confabulation signature), and **`GLM-4.7-Flash`** (unverified point
  release). Bucket 2.
- `data/systems.csv`: `grok-4` marked canonical (the only xAI capture).
- `memory_budget.py`: +`grok` preset. `decisions-matrix.csv`: **39 axes × 12 columns — ALL FILLED**
  (validator: 0 warnings).

### Added — 2026-08-31 — response 13 (z.ai / Zhipu GLM) — bonus system
- `z-ai` — Zhipu z.ai free chat (GLM class). Response 13 / **system 11**. Trust: **MEDIUM**
  (leaning MEDIUM-LOW). Architecture shape fully consensus-aligned and **no invented tool
  ecosystem** (unlike `meta-llama-4` / `deepseek-instant`), but: **0 usable sources**
  (`【turn0searchN】` markers only); **no M6-specific facts**; its load-bearing primary pick is a
  **fabricated size — `Qwen3-Coder-Next 8B`** when the real model is an ~80B MoE (`gpt-5` and
  `meta-llama-4` both name it at 80B); internal inconsistencies (5 GB vs 14 GB for the same model;
  Qwen3-Coder-Next vs Devstral as "the" coding stack; swap-strategy vs a 3-instance concurrent
  diagram); relies on swap ("Fits within 32GB RAM with swapping"); assumes a 3rd drive (2 TB HDD)
  not in the spec. Distinctive: **vLLM-MLX as the #1 primary engine** (first response to do so —
  the tool is real, the "130-464 tok/s" numbers are not); **Caddy** reverse proxy (unique);
  **Redis** for both task queue and working memory; recommends its own GLM-4.5-Air. Bucket 2.
- `data/systems.csv`: `z-ai` appended, canonical. `memory_budget.py`: +`zai` preset.
- `decisions-matrix.csv`: `z_ai` column added — **39 axes × 13 columns, all filled**.

### Milestone: data collection (13 responses / 11 systems)
- 11 systems (10 non-anchor): Anthropic, Mistral, OpenAI, Perplexity, Moonshot, Google, Alibaba,
  Meta, DeepSeek (3 modes), xAI, Zhipu.
- Next: #10 (`consensus-matrix.md` / `disagreements.md` / `reference-architecture.md` — critical
  path), #9 (2nd rater — required for paper), #8 (`prompt-v2/v3`, optional), #11 (paper draft),
  #12–#14 / #17 follow-up probes (optional).
- `prompts/prompt-v2.md` / `prompt-v3.md` paraphrases for prompt-sensitivity (RQ6).
- Second independent rater for the rubric; inter-rater agreement.
- `analysis/consensus/` synthesis once ≥ 6 responses are in.
