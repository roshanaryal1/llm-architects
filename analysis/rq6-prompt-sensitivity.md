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
| perplexity | ✅ `perplexity-v2.md` | ✅ `perplexity-v3.md` (INCOMPLETE — no A–K) |
| gpt-5 | ✅ `gpt-5-v2.md` | ✅ `gpt-5-v3.md` |
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

| axis | v1 | v3 (preliminary — capture incomplete) |
|---|---|---|
| inference engine | Ollama-first, then MLX-native | **MLX-LM primary; Ollama/llama.cpp = fallback only** (matches v2) |
| primary local model | Qwen3-Coder-30B-A3B Q4 | **7B–14B-class** (even smaller than v2's 14–18B) |
| orchestration framework | LangGraph + SQLite | **custom small Python; no named framework** (matches v2) |
| deliverable A–K | delivered | **NOT delivered** — stopped to request more research |
| fabrication count | 0 | **0** (names no specific model tag) |

**perplexity summary:** v2 and v3 are both minimalist and near-identical; both drop LangGraph,
shrink the model, and put MLX-LM first. Because the v1→v2 shift (RFC framing, role wording gone)
and the v1→v3 shift (anti-anchoring steer gone) land in the *same place*, the driver for
Perplexity is **not** the "senior architect" role wording — it is section order / RFC framing, or
run-to-run variance. v3 also stopped early rather than deliver: removing the anti-popularity steer
did **not** make Perplexity name more products.

### gpt-5

| axis | v1 | v2 (RFC framing) | v3 (no anti-anchoring steer) |
|---|---|---|---|
| architecture shape | one inference lane, logical agents, coordinator/worker, SQLite state, evidence ledger, dedicated user, Tailscale | **=** | **=** |
| **primary inference engine** | **MLX-LM** primary | **→ llama.cpp server** primary (mlx_lm + Ollama *excluded*) | **→ Ollama** primary ("Do not build directly around MLX-LM. Do not make llama.cpp your application API") |
| orchestration substrate | Pydantic AI + custom scheduler | **→ LangGraph** + thin supervisor | **→ Prefect 3 + LangGraph** + thin supervisor (Prefect new) |
| coding executor | OpenHands (Docker) + Qwen Code | **→ mini-SWE-agent v2** (OpenHands demoted) | **→ OpenHands (Docker) + Aider + OpenCode** (back to OpenHands, adds two more) |
| primary model | Qwen3.6-35B-A3B Q4 (rejects 80B) | Qwen3.6-35B-A3B Q4_K_M (sourced) | **gpt-oss:20b + Qwen3.5-27B-Coding + Qwen3.6-35B-A3B + Nemotron 3.5 Lightning** |
| # models named | ~4 | **2** | **7** |
| sandbox | dedicated user + `capability://` + Docker | Colima VZ | **Docker Desktop** (which v2 put on its exclusion list) |
| new tools introduced | — | — | **Prefect 3, Nemotron 3.5 Lightning, Docker Desktop, MS Agent Framework, OpenClaw + Hermes (discussed at length)** |
| citations (RQ5) | ~20 inline attributions, 0 URLs → D6 1 | **~10 resolving primary URLs** → D6 2 | **0 — empty Sources section, no inline attributions** → D6 0 |
| fabrication | none (adj.) | none | none obvious; several unsourced numeric claims (dim 5 risk); Nemotron 3.5 Lightning / Qwen3.5-27B-Coding tags to web-verify |

**gpt-5 summary:** the model's **#1 inference engine is unstable under every framing** — MLX-LM,
llama.cpp, Ollama across v1/v2/v3. Architecture shape is rock-stable. The v3 ablation (anti-anchoring
/ anti-popularity steer removed) produced the **most product-heavy** answer (7 models vs 2), added
a whole orchestration layer (Prefect), softened the "don't adopt a young all-in-one daemon"
caution, picked a tool it had excluded one framing earlier (Docker Desktop), and **stopped citing
anything**. Strong support for the P3 hypothesis that the anti-anchoring / anti-popularity steer
does real work.

## Running findings (update as captures land)

1. **Framing moves products, not topology.** Both systems keep their entire architecture across
   all framings and change product picks. n = 2 systems, consistent with the paper's "converge on
   shape, diverge on products."
2. **The effect size is very different by model.** Perplexity's product picks barely move (and
   converge on minimalism regardless of *which* prompt change was made). GPT-5's move a lot —
   including its #1 inference engine changing in all three framings.
3. **The anti-anchoring / anti-popularity steer (v3 ablation) does real work — for GPT-5.**
   Removing it widened GPT-5's tool list (7 models vs 2), added Prefect + Nemotron + Docker
   Desktop, softened adoption caution, and collapsed its citations to zero. Perplexity showed no
   such widening (if anything it got more conservative). Preliminary: the steer's effect is
   model-dependent, largest on the model that is most eager to name products.
4. **Citation quality is framing-sensitive for GPT-5:** D6 = 1 (v1) → 2 (v2) → 0 (v3) on the same
   model, same task, same Sources-list request. Worth a sentence in RQ5.
5. *(fabrication-rate delta across framings — 0 confirmed so far across 4 captures; GPT-5 v3 has
   unsourced numbers + two tags to verify.)*
