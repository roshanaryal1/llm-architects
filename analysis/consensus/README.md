# `analysis/consensus/` — cross-response synthesis (RQ1)

**Status: not started.** Formal synthesis begins once the remaining ~1 response is in
(currently 10: claude-sonnet-5, qwen-3.7-plus, deepseek-instant, deepseek-expert,
deepseek-instant-deepthink, perplexity, gemini-3.1-pro, kimi-instant, mistral-large-3, gpt-5).
Only Grok 4 (#6) and Llama 4 (#7) remain.

## What goes here

1. **`consensus-matrix.md`** — for each axis in `data/decisions-matrix.csv`: the modal choice, the
   count of *independent* responses holding it (Claude excluded from the count — it is the anchor,
   not a blind peer), and a note on the spread.
2. **`disagreements.md`** — the axes where responses genuinely conflict, with the competing
   positions and the tradeoff. These are the interesting part of the paper.
3. **`reference-architecture.md`** — one merged design: majority position per axis, every
   non-consensus call explicitly labelled `[adjudicated]` with reasoning. This is the paper's
   synthesis section and the author's build brief.

## Early signal (from 10 responses — provisional, not a result)

**Unanimous (10/10):**

- MLX-family local inference (Ollama/MLX; llama.cpp as fallback/diagnostic).
- 100+ logical agents = stored definitions/job-specs + task queue + small worker pool + model
  router; **~1 heavy inference slot**; dynamic agents by cloning a template.
- Coordinator/worker (supervisor) topology, explicitly **not swarm**.
- Custom thin orchestrator/supervisor — **not** CrewAI / AutoGen as the backbone.
- **SQLite** for task state + queue (no Redis except DeepSeek-Expert).
- `launchd` KeepAlive + separate watchdog + `pmset`/`caffeinate`; crash recovery by re-queuing
  from a persistent queue.
- **Tailscale-only** remote (no public ports) + a small dashboard + emergency kill switch.
- Dedicated **non-admin macOS user** + tiered permissions (autonomous / notify / approve) +
  Keychain secrets + egress allowlist + runaway limits (tokens/time/iterations).
- Models on internal SSD (load speed); library + papers + archives + backups on external SSD.
- Model **swapping is worthwhile**; keep the heavy model unloaded when idle.
- "Do not install" overlap: Kubernetes, standalone vector DB servers, PostgreSQL, Neo4j-early,
  AutoGen/CrewAI, LangChain-as-core (5–6 of 6 lists).

**Strong majority:**

- Heavy model = **Qwen3-Coder-30B-A3B** MoE (Claude, DeepSeek-Expert, Perplexity explicitly;
  DeepSeek-Instant + DeepSeek-DeepThink name fabricated variants of the same idea). **Qwen 3.7
  Plus and Gemini 3.1 Pro both pick a dense 2024-era 32B** (Qwen2.5-Coder-32B) instead — the
  two responses with the oldest model knowledge.
- Context held to **16–32K** locally despite 256K capability (Claude, Perplexity, DeepSeek-Expert,
  Gemini).
- Research = **evidence-first / citation-grounded** (Claude, Qwen, both DeepSeek runs, Perplexity
  build a custom evidence pipeline; Gemini delegates it to **PaperQA2** off-the-shelf — 6/7).
- **`sqlite-vec` is now the plurality vector store (5/10):** Claude, Gemini, Kimi, Mistral, GPT-5
  all pick it (in-process, no daemon, "explicitly not Chroma"); Qwen + both DeepSeek runs pick
  ChromaDB (3/10); Perplexity picks Qdrant embedded; Mistral adds Mem0 as the later step.
  **6/10 explicitly avoid running a standalone vector-DB daemon.**
- **Coding harness:** **OpenHands** is now the plurality (Perplexity, Mistral, GPT-5, + Kimi/Qwen
  as secondary = 4-6/10, always in a Docker sandbox); **Aider** 5/10 (Qwen, both DeepSeek runs,
  Gemini, Kimi); **Claude Code** 2/10 (Claude, DeepSeek-Expert). GPT-5 uniquely adds **Qwen Code**
  as the interactive console.
- **Orchestration substrate splits 4 ways:** Claude Agent SDK (Claude) · **LangGraph** (Perplexity,
  Mistral, Gemini) · **Pydantic AI** (GPT-5, with a dedicated argument against LangGraph-as-core) ·
  plain custom Python (Qwen, Kimi, DeepSeek runs). All 10 agree the orchestrator is mostly
  **your own code**, not a framework.
- **Managed research APIs vs self-host:** Kimi (Firecrawl + Perplexity Sonar), GPT-5 (Exa Search +
  Contents), Perplexity (paid-API fallback) lean on hosted research; Claude + Qwen + DeepSeek-Expert
  + Mistral build a custom evidence pipeline; Gemini uses PaperQA2. **All 10** agree "store
  retrieved content before synthesis; verify every citation; run a contradiction pass".
- **M6-aware vs generic:** 4/10 engage the actual M6 spec (170 GB/s, dual NE, 2026-08-25 ship
  date) — Claude, Mistral, Perplexity, GPT-5 — and all 4 are also the sourced/current responses.

**Genuine disagreement:**

- **Task queue:** SQLite-only (5/6) vs **Redis + Celery** (DeepSeek-Expert).
- **Vector store:** `sqlite-vec` (Claude) vs **ChromaDB** (Qwen, both DeepSeek runs) vs
  **Qdrant embedded** (Perplexity).
- **Orchestration substrate:** Claude Agent SDK (Claude) vs **LangGraph** (Perplexity, and
  DeepSeek-Expert forbids it) vs Smolagents/"LightAgent" (DeepSeek-DeepThink) vs plain custom
  (Qwen).
- **Coding harness:** Claude Code (Claude, DeepSeek-Expert) vs **OpenHands SDK** (Perplexity, and
  Qwen as secondary) vs **Aider** (Qwen primary, both DeepSeek runs).
- **Exec sandbox:** dedicated-user-only (Qwen) vs user + Apple `container`/Colima (Claude) vs
  user + **Docker** (DeepSeek-Expert [then forbids it], Perplexity) vs user + **Lima VM** +
  Seatbelt (DeepSeek-DeepThink).
- **Cloud:** pure-local (Qwen, both DeepSeek runs) vs optional cloud for hard tasks
  (Claude, DeepSeek-Expert, Perplexity).
- **Monitoring:** custom/minimal (most) vs **Grafana + Prometheus** (DeepSeek-Expert).
- **2026-edge tooling:** adopt (Claude) vs deliberately avoid, benchmark-first (Perplexity) vs
  invent it (both DeepSeek runs).
- **Memory headroom:** keep 4–6 GB free (Perplexity, Claude) vs **oversubscribe to 32–34 GB**,
  "acceptable" (DeepSeek-DeepThink — outlier, likely bad advice).
- **Primary local model:** **Qwen3-Coder-30B-A3B** (Claude, Perplexity, DeepSeek-Expert, Kimi) vs
  **Qwen3.6-35B-A3B** (Mistral alt, GPT-5 primary — GPT-5 explicitly rejects the 80B Qwen3-Coder-Next
  as "wrong machine") vs dense 2024 32B (Qwen 3.7 Plus, Gemini) vs fabricated tags (DeepSeek non-expert).
- **Sources:** Claude ~97, Mistral ~36 (rated), Perplexity ~17; GPT-5 / Kimi / Gemini give
  inline attributions but 0 resolvable URLs; Qwen + all 3 DeepSeek runs give **0**.

**Fabrication watch (RQ2):**

| Response | Fabricated tools/models presented as real |
|---|---|
| deepseek-instant | `Rapid-MLX`, `DeepSeek Harness (DSH)` / `Local DSH`, `Gemma 4 26B`, `Qwen3.5/3.6/3.8` tags |
| deepseek-instant-deepthink | `Ornith-1.0-9B` / `ornith-claude-coder`, `Qwen3.5-35B-A3B` tag, `WhipDesk`, `Cloak`, `Helmrig`, `RemoteVibe`, `Lody`, `DiffResearch`, `LightAgent`, `Engram-Mem`, invented tok/s + SWE-bench numbers |
| deepseek-expert | none (real tools; only stale point-versions) |
| qwen-3.7-plus | none (stale but real) |
| gemini-3.1-pro | none (real tools; stale model + cloud-fallback names — recency, not fabrication) |
| kimi-instant | none (real tools; number inflation — "OpenCode 198k stars", "gpt-oss 98.3%" — and a stale cloud list) |
| mistral-large-3 | none (~6 of ~36 "sources" are google.com/search URLs — evidence-quality, not fabrication) |
| gpt-5 | none (~20 specific inline attributions, no resolvable URL list — evidence-quality, not fabrication) |
| perplexity | none (2 arXiv IDs unverified — evidence-quality, not fabrication) |
| claude-sonnet-5 | none |

Pattern so far: **the fabrication is concentrated in DeepSeek's non-"expert" free modes**, not
across vendors — a within-provider mode effect worth calling out in the paper. **8 of 10 responses
fabricate nothing.** The more interesting axis is a 3-way recency/rigour split:

1. **Sourced + current + M6-aware (4/10)** — `claude-sonnet-5`, `mistral-large-3`, `perplexity`,
   `gpt-5` (browsed or retrieval-assisted; engage 170 GB/s + ship dates + the current
   GLM-5.2 / Kimi K3 / DeepSeek V4 / Qwen3.6 frontier landscape; hedge every throughput number).
   Of these, only Claude and Perplexity give a resolvable URL list; Mistral gives a rated one;
   GPT-5 gives inline attributions only.
2. **Unsourced + ~12-18 months behind (3/10)** — `qwen-3.7-plus`, `gemini-3.1-pro`, `kimi-instant`
   (real tools, but 2024-era models and/or `Claude 3.5 Sonnet` as the cloud fallback; no M6 facts).
3. **Confident futurism (2/10)** — `deepseek-instant`, `deepseek-instant-deepthink`
   (invent plausible-sounding 2026 tools/models — Rapid-MLX, DSH, Ornith-1.0-9B, WhipDesk …).
   `deepseek-expert` (same base model, "expert" mode) escapes this into bucket 2.

Emerging cross-cut: the 4 responses in bucket 1 also **converge hardest on the architecture**
(MLX + 1 large + 1 small worker + SQLite + sqlite-vec + OpenHands-in-Docker + Tailscale + launchd),
while buckets 2 and 3 diverge more — worth testing whether "grounded in current reality" predicts
"agrees with the consensus".
