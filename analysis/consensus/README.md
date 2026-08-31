# `analysis/consensus/` — cross-response synthesis (RQ1)

**Status: not started.** Formal synthesis begins once the remaining ~5 responses are in
(currently 6: claude-sonnet-5, qwen-3.7-plus, deepseek-instant, deepseek-expert,
deepseek-instant-deepthink, perplexity).

## What goes here

1. **`consensus-matrix.md`** — for each axis in `data/decisions-matrix.csv`: the modal choice, the
   count of *independent* responses holding it (Claude excluded from the count — it is the anchor,
   not a blind peer), and a note on the spread.
2. **`disagreements.md`** — the axes where responses genuinely conflict, with the competing
   positions and the tradeoff. These are the interesting part of the paper.
3. **`reference-architecture.md`** — one merged design: majority position per axis, every
   non-consensus call explicitly labelled `[adjudicated]` with reasoning. This is the paper's
   synthesis section and the author's build brief.

## Early signal (from 6 responses — provisional, not a result)

**Unanimous (6/6):**

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
  DeepSeek-Instant + DeepSeek-DeepThink name fabricated variants of the same idea). Only
  Qwen 3.7 Plus picks a **dense 32B**.
- Context held to **16–32K** locally despite 256K capability (Claude, Perplexity, DeepSeek-Expert).
- Research = **evidence-first pipeline, model never cites from memory, mandatory contradiction
  pass** (Claude, Qwen, both DeepSeek runs, Perplexity — 5/6).

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
- **Sources:** Claude ~97, Perplexity ~17, everyone else **0**.

**Fabrication watch (RQ2):**

| Response | Fabricated tools/models presented as real |
|---|---|
| deepseek-instant | `Rapid-MLX`, `DeepSeek Harness (DSH)` / `Local DSH`, `Gemma 4 26B`, `Qwen3.5/3.6/3.8` tags |
| deepseek-instant-deepthink | `Ornith-1.0-9B` / `ornith-claude-coder`, `Qwen3.5-35B-A3B` tag, `WhipDesk`, `Cloak`, `Helmrig`, `RemoteVibe`, `Lody`, `DiffResearch`, `LightAgent`, `Engram-Mem`, invented tok/s + SWE-bench numbers |
| deepseek-expert | none (real tools; only stale point-versions) |
| qwen-3.7-plus | none (stale but real) |
| perplexity | none (2 arXiv IDs unverified — evidence-quality, not fabrication) |
| claude-sonnet-5 | none |

Pattern so far: **the fabrication is concentrated in DeepSeek's non-"expert" free modes**, not
across vendors — a within-provider mode effect worth calling out in the paper.
