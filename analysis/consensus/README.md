# `analysis/consensus/` — cross-response synthesis (RQ1)

**Status: not started.** Build this once ≥ 6 responses are captured (currently 4).

## What goes here

1. **`consensus-matrix.md`** — for each axis in `data/decisions-matrix.csv`: the modal choice, the
   count of *independent* responses holding it (Claude excluded from the count — it is the anchor,
   not a blind peer), and a note on the spread.
2. **`disagreements.md`** — the axes where responses genuinely conflict, with the competing
   positions and the tradeoff. These are the interesting part of the paper.
3. **`reference-architecture.md`** — one merged design: majority position per axis, every
   non-consensus call explicitly labelled `[adjudicated]` with reasoning. This is the paper's
   synthesis section and the author's build brief.

## Early signal (from 4 responses — provisional, not a result)

**Strong agreement so far:**

- MLX-family local inference (llama.cpp as fallback).
- 100+ logical agents = stored definitions + task queue + small worker pool + model router;
  ~1 heavy inference slot; dynamic agent creation by cloning a template.
- Custom thin orchestrator — **not** CrewAI / AutoGen / LangGraph as the backbone.
- SQLite for state; filesystem for docs; vector store deferred or embedded (not a standalone DB
  on day one — though 3 of 4 said Chroma, Claude said sqlite-vec).
- `launchd` KeepAlive + a separate watchdog + `caffeinate`/`pmset`; crash recovery by re-queuing
  from a persistent queue.
- Tailscale-only remote (no public ports) + a small FastAPI/Flask dashboard + `ntfy`/Pushover +
  emergency kill switch.
- Dedicated non-admin macOS user + tiered permissions (autonomous / notify / approve) + secrets
  in Keychain or age/gpg + `pfctl` egress allowlist + runaway limits (tokens/time/iterations).
- Models on the internal SSD; model library + papers + archives + backups on the external SSD.
- "Do not install": AutoGPT/CrewAI/AutoGen, LangChain-as-core, Kubernetes, standalone vector DBs,
  PostgreSQL, Airflow/n8n (appears on 3–4 of the 4 "what NOT to install" lists).

**Genuine disagreement so far:**

- **Model architecture:** MoE 30B (Claude, DeepSeek-Instant) vs dense 32B (Qwen 3.7 Plus) vs
  dense 14B verifier (DeepSeek-Expert).
- **Task queue:** SQLite-only (Claude, Qwen, DeepSeek-Instant) vs Redis + Celery (DeepSeek-Expert).
- **Vector store:** `sqlite-vec` (Claude) vs ChromaDB (the other three).
- **Exec sandbox:** dedicated-user-only (Qwen) vs user + Apple `container`/Colima (Claude) vs
  user + Docker + seatbelt (DeepSeek-Expert, which then forbids Docker elsewhere).
- **Cloud:** pure-local (Qwen, DeepSeek-Instant) vs optional cloud for hard tasks
  (Claude, DeepSeek-Expert).
- **Monitoring:** custom/minimal (Claude, Qwen) vs Grafana + Prometheus (DeepSeek-Expert).
- **Sources:** Claude ~97, everyone else 0.

**Fabrication watch (RQ2):** DeepSeek-Instant invents `Rapid-MLX`, `DeepSeek Harness (DSH)`,
`Gemma 4 26B`, and `Qwen3.5/3.6/3.8` version numbers. No other response fabricates tools.
