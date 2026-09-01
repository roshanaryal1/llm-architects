# RQ6 — prompt-sensitivity (v1 vs v2 vs v3)

**Question:** how much does the *phrasing* of the instrument move a model's answer, holding the
model and the task fixed?

**Design:** re-run a ≥ 5-system subset on two controlled variants of `prompt-v1.md`:

- **v2** (`prompts/prompt-v2.md`) — full paraphrase: "respond to this technical RFC" framing
  instead of "act as a senior AI infrastructure architect", sections reshuffled, every sentence
  reworded. Same substance.
- **v3** (`prompts/prompt-v3.md`) — v1 minus the anti-anchoring / anti-popularity steer
  ("Do NOT assume that any particular existing product … is the correct answer", "Do not
  recommend tools because they are popular", "Look beyond … Reddit or YouTube", "not brand
  popularity"). Everything else byte-identical to v1.

Each `(system, version)` pair is a **fresh chat, no history**. Captures:
`data/responses/<slug>-v2.md` / `<slug>-v3.md` with `prompt_version` front-matter. This file is
the axis-by-axis delta tracker; the paper's §9 (RQ6) reports from it.

## Subset

Target: 2 top-tier, 2 mid, 1 low (from the adjudicated ranking). Chosen: **perplexity, gpt-5,
gemini-3.1-pro, qwen-3.7-plus, z-ai** (adjust if a run is unavailable).

## Progress

| system | v2 | v3 |
|---|:--:|:--:|
| perplexity | ✅ captured `perplexity-v2.md` | ⬜ pending |
| gpt-5 | ⬜ running (slow) | ⬜ pending |
| gemini-3.1-pro | ⬜ pending | ⬜ pending |
| qwen-3.7-plus | ⬜ pending | ⬜ pending |
| z-ai | ⬜ pending | ⬜ pending |

## Delta table — load-bearing axes

`=` unchanged vs that system's v1 capture · `→` changed (value after the arrow) · `NF` = new
fabrication introduced · `−F` = a v1 fabrication dropped.

### perplexity

| axis | v1 | v2 | v3 |
|---|---|---|---|
| architecture shape | coordinator/worker, 1 heavy + small, SQLite state, Tailscale, dedicated user, evidence-first research | **=** | — |
| inference engine | Ollama-first, then MLX-native | **→ `mlx-lm` server primary; Ollama = compat adapter only** | — |
| primary local model | Qwen3-Coder-30B-A3B Q4 | **→ 14B–18B Qwen-family 4-bit; explicitly rejects 27–32B as always-on primary** | — |
| orchestration framework | LangGraph + SQLite | **→ custom small Python + SQLite; no named framework** | — |
| coding executor | OpenHands (Docker worktrees) + custom supervisor | **=** | — |
| vector store | Qdrant (embedded) | **→ SQLite FTS5 first; add Qdrant only after measured need** | — |
| task queue | SQLite + leases | **=** | — |
| sandbox | dedicated non-admin user + Docker worktrees | **= (dedicated non-admin `ailab` user + container/VM)** | — |
| remote | Tailscale + SSH + private dashboard | **=** | — |
| 24/7 | launchd + KeepAlive + watchdog | **=** | — |
| cloud posture | optional, LiteLLM budget caps, $0-usable | **= (optional, approval-gated, $0-usable; LiteLLM not named)** | — |
| M6 spec engagement | refused to state M6 numbers | **→ states 170 GB/s + core layout, cited to apple.com; still refuses throughput SLOs** | — |
| fabrication count | 0 (2 future-dated arXiv IDs unverified) | **0** (1 future-dated arXiv ID `2511.05502` unverified) | — |
| citations | ~17 real URLs, mostly primary, a few aggregator | ~14 real URLs, mostly primary, 2 secondary | — |

**perplexity v1→v2 summary:** architecture **identical**; **4 implementation axes shifted, all
toward minimalism** (MLX-first, smaller model, no named orchestration framework, deferred vector
store) + slightly more M6 engagement. Zero fabrication in either framing.

## Running findings (update as captures land)

1. **Framing moves products, not topology** (n = 1 so far). Perplexity's RFC-framed answer kept
   the whole architecture and changed four product choices, every one toward a smaller / less
   branded stack. Preliminary support for: the "senior architect" role framing nudges toward
   naming specific products; a neutral "RFC" framing nudges toward the minimal defensible stack.
2. *(v3 / anti-anchoring ablation — pending)*
3. *(fabrication-rate delta across framings — pending; perplexity contributes 0/0 so far)*
