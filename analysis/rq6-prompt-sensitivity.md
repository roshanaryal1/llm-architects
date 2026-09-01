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

| system | v2 | v3 | confound |
|---|:--:|:--:|---|
| perplexity | ✅ `perplexity-v2.md` | ✅ `perplexity-v3.md` (INCOMPLETE) | — |
| gpt-5 | ✅ `gpt-5-v2.md` | ✅ `gpt-5-v3.md` | — |
| qwen-3.7-plus | ✅ `qwen-3.7-plus-v2.md` | ✅ `qwen-3.7-plus-v3.md` | **v1 did not browse; v2/v3 did.** v2↔v3 is the clean pair. |
| z-ai | ✅ `z-ai-v2.md` | ✅ `z-ai-v3.md` | **v1 = different model (GLM-4.x) + broken browse; v2/v3 = GLM-5.2, no browse.** v2↔v3 is the clean pair (but v2/v3 self-report different cutoffs). |
| gemini-3.1-pro | ✅ `gemini-3.1-pro-v2.md` | ✅ `gemini-3.1-pro-v3.md` | **NO Gemini pair holds the model fixed** — v2 self-reports "Gemini 2.5 Pro"/2026, v3 self-reports "Gemini 1.5 Pro"/Jan-2025. v1↔v2 (both browsing-off, both ~2.5-Pro-era) is the least-confounded pair and showed near-zero movement. |

**All 5 systems captured (v2 + v3 each). RQ6 data collection complete.**

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

### qwen-3.7-plus (clean pair = v2 vs v3, both browsed)

| axis | v2 (RFC framing) | v3 (no anti-anchoring steer) |
|---|---|---|
| architecture shape | coordinator/worker, 1 heavy + small, SQLite queue, dedicated user, launchd, Tailscale | **=** |
| inference engine | MLX via Ollama | **→ MLX + llama.cpp** (Ollama = fallback) |
| orchestration | OpenHands + LangGraph | **→ LangGraph** (OpenHands = "heavier alternative, cloud-scale") |
| coding agent | OpenHands + Aider | **→ Aider + Safehouse** (Safehouse = named macOS sandbox tool, new) |
| research | Firecrawl/Jina, custom | **→ GPT-Researcher + Firecrawl** (named product) |
| memory | SQLite + LanceDB | **→ SQLite + LanceDB + NetworkX** (adds graph layer) |
| sandbox | dedicated user + Lima VM | **→ dedicated user + Safehouse** |
| # named products | ~9 | **~14** |
| sources | 10 URLs | **15 URLs** |
| M6 engagement | "32GB M6" framing, no GB/s | **states "~170 GB/s"** (sourced to a community guide) |

**qwen summary:** v3 (steer removed) is **more product-heavy** — ~14 named tools vs ~9, adds
Safehouse + OpenClaw + GPT-Researcher + NetworkX + Gradio, 15 sources vs 10. Matches the GPT-5
direction. (v1 excluded from the phrasing analysis — it didn't browse.)

### z-ai (clean pair = v2 vs v3, both GLM-5.2, both no-browse)

| axis | v2 (RFC framing) | v3 (no anti-anchoring steer) |
|---|---|---|
| architecture shape | coordinator/worker, logical agents as DB rows, 1 heavy + small, launchd, Tailscale, dedicated user | **=** |
| primary model | Qwen3-30B-A3B 4-bit (MoE, ~16 GB) | **→ Qwen 2.5/3.0 14B 4-bit** (~8-14 GB) — *more conservative* |
| task queue | SQLite WAL | **→ Redis + RQ** (Redis was on v2's exclusion list) |
| vector store | LanceDB | **→ ChromaDB** (v2 preferred LanceDB over Chroma) |
| sandbox | `sandbox-exec` profiles + `pf` egress allowlist | **→ Docker Desktop** (v2's backup, "heavier") |
| research | GPT-Researcher + PaperQA2 (named) | **→ SearXNG + Playwright + PyMuPDF, custom** (no named product) |
| # sources | ~45 real URLs | **7 real URLs** |
| RAM math | "21 GB resident, coder swapped" | "Total 32.0 GB, zero-swap" (sums to exactly 32) |

**z-ai summary:** v3 (steer removed) is **LESS product-heavy and more conservative** — opposite
of GPT-5 and Qwen. Drops to a 14B primary, reverts to Redis/ChromaDB/Docker (all three on v2's
own exclusion list), no named research product, 7 sources vs 45. Possible run-to-run noise
(v2/v3 self-report different cutoffs). Architecture shape unchanged. (v1 excluded — different
model + broken browse.)

## Running findings (update as captures land)

1. **Framing moves products, not topology.** n = 4 systems. Every capture keeps its entire
   architecture (coordinator/worker, logical agents as data, one heavy + small model, SQLite
   state, dedicated user, launchd, Tailscale) across every framing. Only product picks move.
   Direct support for the paper's "converge on shape, diverge on products".
2. **Effect size is strongly model-dependent.** Perplexity barely moves (and converges on
   minimalism regardless of which prompt change is made). GPT-5 moves a lot — its #1 inference
   engine is *different in all three framings* (MLX-LM / llama.cpp / Ollama). Qwen and z-ai move
   a moderate amount.
3. **The v3 ablation (anti-anchoring / anti-popularity steer removed) is not monotone.** GPT-5
   and Qwen both name **more** products with the steer gone (GPT-5: 7 models vs 2, adds Prefect +
   Nemotron + Docker Desktop; Qwen: ~14 vs ~9, adds Safehouse + GPT-Researcher + NetworkX).
   **z-ai goes the other way** — fewer products, more conservative, reverts to tools on its own
   exclusion list. So the steer does real work, but the sign of its effect depends on the model:
   it suppresses product-naming in the eager namers (GPT-5, Qwen) and does something different in
   GLM-5.2.
4. **Citation behaviour is framing-sensitive.** GPT-5: D6 1 (v1, attributions/0 URLs) → 2 (v2,
   ~10 primary URLs) → **0 (v3, empty Sources section)**. z-ai: ~45 URLs (v2) → 7 (v3). Qwen:
   10 (v2) → 15 (v3). No consistent direction — but all four systems' citation *apparatus* shifts
   with phrasing on the same identical Sources-list request. Worth a sentence in RQ5.
5. **Fabrication: still 0 confirmed across 8 prompt-v2/v3 captures.** Names to web-verify:
   GPT-5 v3 (`Nemotron 3.5 Lightning`, `Qwen3.5-27B-Coding-NVFP4`), Qwen v3 (`Safehouse` — appears
   real, `tessl.io` blog). GPT-5 v3 has several unsourced numeric claims (dim-5 risk).
6. **Two confounds limit the analysis:** Qwen didn't browse for v1; z-ai used a different model +
   broken browsing for v1. For both, only the v2↔v3 pair is a clean phrasing comparison. This
   also means the corpus accidentally contains a small **browsing on/off** signal for Qwen (v1
   off, v2/v3 on) and a **model-upgrade** signal for z-ai — both worth a line in the paper.

7. **The free tiers are not reproducible instruments across runs.** Two of the five systems
   served a *different underlying model* between paraphrase runs: **z-ai** self-reported cutoff
   "~mid-2025" (v2) vs "Late 2024" (v3) for the same "GLM-5.2" label; **Gemini** self-reported
   "Gemini 2.5 Pro" / "2026" (v2) vs **"Gemini 1.5 Pro" / "January 2025"** (v3) — a materially
   older model. No Gemini pair holds the model fixed. This is itself a paper finding (a
   threat-to-validity that generalises: *"the same free chat product is not a stable model
   across sessions"*), and it means the clean phrasing comparison exists only for **GPT-5** and
   **Perplexity** (both held their model identity across all three framings).

8. **Gemini and Perplexity are the low-sensitivity end.** Gemini v1↔v2 (the only Gemini pair
   where both runs are browsing-off and ~2.5-Pro-era) is *nearly the same response* — identical
   primary model, inference engine, orchestration, coding agent, vector store, and (stale) cloud
   fallback. Perplexity's product picks barely move. GPT-5 is the high-sensitivity extreme (#1
   inference engine differs in all three framings). Qwen and z-ai are mid, but confounded.

9. **RQ2 note — one fabricated-*context* hallucination:** Gemini v3 closed by asking the operator
   about prioritising work on "your existing projects like **safeRoute and RentMate**" — project
   names not in the prompt, invented by the model. Distinct from inventing a tool/model; logged
   for RQ2 as a hallucinated-context item.

## What the RQ6 data supports for the paper

- **Primary result:** across 5 systems × 3 framings, **every response keeps its architecture and
  only changes products.** This is the strongest single-sentence support for the paper's
  headline ("converge on shape, diverge on products") — and it holds under two different kinds of
  prompt perturbation (full paraphrase, and a targeted anti-anchoring-steer ablation).
- **Secondary result:** the anti-anchoring / anti-popularity steer *does* measurably change the
  product list — but the **sign is model-dependent** (suppresses product-naming in GPT-5 and
  Qwen; the opposite in GLM-5.2). Reportable as: "the steer is not inert, but it does not have a
  uniform effect."
- **Threat-to-validity result:** free chat tiers are not reproducible instruments — 2/5 systems
  served a different model between runs. The paper's methods section must say the v2/v3 runs are
  a *snapshot pair*, not a controlled A/B, for z-ai and Gemini.
- **Not supported:** any claim that phrasing changes the *fabrication rate* (0 confirmed
  fabrications across all 10 v2/v3 captures) or the *architecture*.
