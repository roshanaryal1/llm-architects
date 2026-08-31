# `analysis/consensus/` — cross-response synthesis (RQ1)

**Status: synthesis drafted (issue #10, PR).** The three artefacts exist; refine as `prompt-v2/v3`
(#8) and the rater scores (#9) land.

1. **[`consensus-matrix.md`](consensus-matrix.md)** — every one of the 39 decision axes: modal
   choice, count of the 10 non-anchor systems holding it, notable dissent. ~24 axes are unanimous.
2. **[`disagreements.md`](disagreements.md)** — the 8 axes with a genuine split (inference server #1,
   exact heavy model, per-task sandbox, task-queue backend, vector store, orchestration-framework
   layer, monitoring depth, cloud dependence) — each with the positions, the tradeoff, and what
   `reference-architecture.md` adjudicated. Plus 3 "non-disagreements" that resolve on inspection.
3. **[`reference-architecture.md`](reference-architecture.md)** — the merged design: every layer
   tagged `[consensus N/10]` or `[adjudicated]`, a layered diagram, the 32 GB resource budget, the
   security-boundary table, an 8-phase build order, and the "what NOT to build" union. This is the
   paper's synthesis section **and** the author's build brief.

The early-signal notes below are kept for provenance; the numbers above supersede them.

---

## Corpus: 13 responses from 11 systems — **data collection complete**

DeepSeek contributed 3 modes of one base model (DeepSeek-V4-Pro). `data/systems.csv` marks
`deepseek-expert` as the **canonical** DeepSeek answer.

- **Per-system claims below (RQ1 agreement, "how many models pick X")** count **11 systems**
  (10 non-anchor): the canonical column per system.
- **Per-response claims (RQ2 fabrication, RQ6 mode sensitivity)** use all **13 captures**.
- The 3 DeepSeek modes are a within-model finding of their own — see
  [`../deepseek-modes.md`](../deepseek-modes.md). Captures are never merged.

| slug | vendor / free tier | canonical | trust | sources | bucket |
|---|---|---|---|---|---|
| `claude-sonnet-5` | Anthropic (Claude Code, browsing) | ✔ (anchor) | HIGH — not blind | ~97 URLs | 1 |
| `mistral-large-3` | Mistral Le Chat (Large 3) | ✔ | HIGH | ~36 rated | 1 |
| `gpt-5` | OpenAI ChatGPT (GPT-5.6 Luna) | ✔ | HIGH | ~20 inline, 0 URLs | 1 |
| `perplexity` | Perplexity (Sonar) | ✔ | MED-HIGH | ~17 URLs | 1 |
| `kimi-instant` | Moonshot Kimi (Instant) | ✔ | MED-HIGH | search markers, 0 URLs | 2 |
| `deepseek-expert` | DeepSeek-V4-Pro (deep-reasoning mode) | ✔ | MED-HIGH | 0 | 2 |
| `gemini-3.1-pro` | Google Gemini | ✔ | MEDIUM | 0 | 2 |
| `qwen-3.7-plus` | Alibaba Qwen chat | ✔ | MEDIUM | 0 | 2 |
| `grok-4` | xAI Grok | ✔ | MEDIUM | 0 (M6 spec correct) | 2 |
| `z-ai` | Zhipu z.ai (GLM class) | ✔ | MEDIUM (→ MED-LOW) | 0 usable (search markers) | 2 |
| `meta-llama-4` | Meta AI / hosted Llama 4 | ✔ | LOW | **99 refs, ~60% junk** | 3 |
| `deepseek-instant` | DeepSeek-V4-Pro (fast mode) | mode-variant | LOW | 0 | 3 |
| `deepseek-instant-deepthink` | DeepSeek-V4-Pro (instant+DeepThink) | mode-variant | LOW | 0 | 3 |

"Bucket" = the 3-way recency/rigour split (see bottom). **Bucket 1: 4 · Bucket 2: 6 · Bucket 3: 3.**

---

## Early signal (from 13 responses — provisional, not a result)

> The `X/12` counts in this **early-signal** section are per-*response* (they include both
> non-canonical DeepSeek modes). The formal per-*system* tally (one canonical column per system,
> "of 11") is what `consensus-matrix.md` will produce — that is the number the paper reports for
> RQ1. Where the two differ it is because the DeepSeek fast modes echo `deepseek-expert`, so a
> per-system count is usually `per-response count − 0..2`. Several `X/11` figures below predate
> `grok-4` and are being refreshed in `consensus-matrix.md` (#10).

### Unanimous (11/11 systems; 13/13 responses)

- **MLX-family local inference** is the correct Apple-Silicon path (llama.cpp/Ollama as
  fallback/compat). Even the fabrication-heavy responses agree on this.
- **100 logical agents ≠ 100 model processes.** Agents are cheap YAML/SQLite definitions
  (role, tools, permissions, workspace, model tier); a bounded worker pool drains a task queue.
- **~1 concurrent large-model worker + 2–3 small-model workers.** Two large MoE models will not
  co-reside in 32 GB. Every response states this.
- **Coordinator/worker (supervisor) topology, explicitly NOT a swarm.**
- **The orchestrator is mostly your own code**, not a framework you live inside
  (CrewAI/AutoGen rejected by name in 10/12 "what NOT to install" lists).
- **SQLite** for the task queue + durable task state; requeue interrupted tasks on restart.
- **`launchd` KeepAlive + a watchdog + `caffeinate`/`pmset`** for 24/7; crash recovery from the
  persistent queue.
- **Tailscale only** for remote access — no public ports; small dashboard; emergency kill switch.
- **Dedicated non-admin macOS user** + tiered permissions (autonomous / notify-or-log / approve) +
  secrets never in the agent's filesystem + destructive-command blocklist + audit log.
- **Models hot on the internal SSD**; model library + papers + datasets + backups on the external.
- **Model swapping is worthwhile**; keep the hot model resident, load small models on demand.
- **Research = store-then-verify.** Every claim traces to a stored source snippet; a second pass
  verifies each claim against its source; a contradiction pass runs before synthesis; the final
  report is written only from the verified-claims table, not from parametric memory.
- **Context held to 16–32K locally** despite 256K model capability — repo-map + retrieval, not
  200K-token dumps.

### Strong majority

- **`sqlite-vec` is the plurality vector store (6/11):** Claude, Gemini, Kimi, Mistral, GPT-5, and
  Meta (as "the memo pattern") pick in-process SQLite vectors + BM25 hybrid. **ChromaDB 3/11**
  (Qwen, both DeepSeek fast modes). Perplexity → Qdrant embedded. Meta also names LanceDB embedded
  as the grow-into step. **8/11 explicitly avoid running a standalone vector-DB daemon initially.**
- **Coding harness:** **OpenHands-in-Docker** is the plurality primary/co-primary (Perplexity,
  Mistral, GPT-5, Meta, + Kimi/Qwen as secondary). **Aider** 5/11 (Qwen, both DeepSeek runs,
  Gemini, Kimi, Meta as the git-safe layer). **Claude Code** 2/11 (Claude, DeepSeek-Expert).
  GPT-5 and Meta both add an OpenCode/Qwen-Code interactive console.
- **Cloud is optional, not required (8/11):** local-first with a cloud-burst escape hatch for hard
  planning / final synthesis, gated by a token/cost budget; system stays useful at $0. Pure-local
  only in the two DeepSeek fast modes (and Qwen leans that way).
- **LiteLLM** as the model-router layer named by 4/11 (Kimi, Perplexity-optional, Meta, and
  implied by GPT-5's semaphore design); the rest use a small hand-written rule table.

### Genuine disagreement

| Axis | Positions |
|---|---|
| **Primary local model** | Qwen3-Coder-30B-A3B (Claude, Perplexity, DeepSeek-Expert, Kimi) · Qwen3.6-35B-A3B (GPT-5 primary, Mistral alt — GPT-5 rejects the 80B Qwen3-Coder-Next) · Qwen 27B dense / 35B-A3B (Grok) · dense 2024 32B (Qwen 3.7 Plus, Gemini) · **fabricated size/tag** ("Qwen3-Coder-Next 8B" — z-ai; fake tags — DeepSeek fast modes, Meta) |
| **Task queue backend** | SQLite-only (majority) · **Redis** (DeepSeek-Expert +Celery, z-ai, Meta-optional) |
| **Orchestration substrate** | Claude Agent SDK (Claude) · LangGraph (Perplexity, Mistral, Gemini) · Pydantic AI (GPT-5, with a written argument against LangGraph-as-core; Meta pairs it with LangGraph) · plain custom Python (Qwen, Kimi, Grok, z-ai, DeepSeek runs) |
| **Exec sandbox** | dedicated-user-only (Qwen, Grok via `sandbox-exec`) · user + `sandbox-exec` (z-ai) · user + Apple `container`/Colima (Claude) · user + Docker/OrbStack (DeepSeek-Expert [then forbids it], Perplexity, Mistral, GPT-5, Meta) · user + Lima VM + Seatbelt (DeepSeek-DeepThink, Gemini) |
| **Monitoring** | custom/minimal (most) · Grafana + Prometheus (DeepSeek-Expert, z-ai) |
| **Inference engine #1** | MLX + llama-swap (Claude) · Ollama-0.19-MLX (Kimi, Grok default) · mlx-lm server (Mistral, GPT-5) · llama.cpp server (Gemini) · **vLLM-MLX** (z-ai — first to make it the primary) |
| **Memory headroom** | keep 2–6 GB free (Claude, Perplexity, GPT-5, Mistral) · "oversubscribe to 32–34 GB, acceptable" (DeepSeek-DeepThink — outlier, likely bad advice) |
| **2026-edge tooling** | adopt it (Claude) · deliberately avoid, benchmark-first (Perplexity) · invent it (DeepSeek fast modes, Meta) |
| **M6 memory bandwidth** | **170 GB/s (correct)** — Claude, Mistral, Perplexity, GPT-5, Grok · **"~300+ GB/s" (wrong)** — Meta · not mentioned — Qwen, Gemini, Kimi, DeepSeek |

---

## Fabrication watch (RQ2)

| Response | Fabricated tools/models presented as real |
|---|---|
| `deepseek-instant` | `Rapid-MLX`, `DeepSeek Harness (DSH)` / `Local DSH`, `Gemma 4 26B`, `Qwen3.5/3.6/3.8` tags |
| `deepseek-instant-deepthink` | `Ornith-1.0-9B` / `ornith-claude-coder`, `Qwen3.5-35B-A3B` tag, `WhipDesk`, `Cloak`, `Helmrig`, `RemoteVibe`, `Lody`, `DiffResearch`, `LightAgent`, `Engram-Mem`, invented tok/s + SWE-bench numbers |
| `meta-llama-4` | `Rapid-MLX` (+ the same `raullenchai` Homebrew tap as `deepseek-instant`), `Gemma 4 12B`, `Qwen3.5-35B-A3B` (+ fake OpenRouter id), `OpenClaw` / `Claw Code` / `OpenClaw Gateway` / `Clawtrol` / `Hermes Agent` / `memo` (2 URLs) / `cplt` / `nono` / `agent-policy-engine` / `pi-search-hub` / `silicorism` / `TurboQuant K8V4` / `PFlash` — **each with a citation**; also `M6 ≈ 300+ GB/s` (wrong), and `[38]` mis-titles a real arXiv paper |
| `deepseek-expert` | none (real tools; only stale point-versions) |
| `qwen-3.7-plus` | none (stale but real) |
| `gemini-3.1-pro` | none (real tools; stale model + cloud-fallback names — recency, not fabrication) |
| `kimi-instant` | none (real tools; number inflation — "OpenCode 198k stars", "gpt-oss 98.3%" — and a stale cloud list) |
| `mistral-large-3` | none (~6 of ~36 "sources" are google.com/search URLs — evidence-quality, not fabrication) |
| `gpt-5` | none (~20 specific inline attributions, no resolvable URL list — evidence-quality, not fabrication) |
| `grok-4` | `rapid-mlx` (alt-list), `Gemma 4 31B` (alt-list), `GLM-4.7-Flash` (unverified) — minor, confined to alternatives; primary picks all real |
| `z-ai` | **`Qwen3-Coder-Next 8B`** — a fabricated *size* on a real model (it is an ~80B MoE) used as the load-bearing primary coding pick; + invented vLLM-MLX throughput numbers ("130-464 tok/s", "3.4x"). No invented tools/ecosystems. |
| `perplexity` | none (2 arXiv IDs unverified — evidence-quality, not fabrication) |
| `claude-sonnet-5` | none |

**9 of 13 responses fabricate nothing** (or only unverified point-versions in alt-lists, as
`grok-4` and `deepseek-expert` do). Real fabrication is concentrated in **DeepSeek's non-"expert"
free modes and Meta / Llama 4**; `z-ai` sits between — no invented tools, but its headline
model pick is a fabricated size (attribute corruption on a real 80B model).

**The strongest RQ2 result — cross-vendor confabulation of the same non-existent things:**

| Fabricated item | Appears in | Vendors |
|---|---|---|
| **`Rapid-MLX` / `rapid-mlx`** (+ the `raullenchai` Homebrew tap) | `deepseek-instant`, `meta-llama-4`, `grok-4` | DeepSeek, Meta, xAI (3) |
| **`Gemma 4`** (sizes given: 26B / 12B / 31B — unstable = confabulated) | `deepseek-instant`, `meta-llama-4`, `grok-4` | DeepSeek, Meta, xAI (3) |
| `Qwen3.5-35B-A3B` tag | `deepseek-instant-deepthink`, `meta-llama-4` | DeepSeek, Meta (2) |

Three independent vendors inventing the *same* fake tool (`Rapid-MLX`) and the *same* fake model
family (`Gemma 4`) is not random — it points to a shared training-data artefact or a shared
hallucination attractor around "the obvious next version". This is a paragraph, maybe a figure,
in the paper.

---

## The emerging headline: a 3-way recency/rigour split — and citations are not a proxy for it

| Bucket | Responses | Character |
|---|---|---|
| **1 — sourced/retrieval + current + M6-aware** | `claude-sonnet-5`, `mistral-large-3`, `perplexity`, `gpt-5` | Browsed or retrieval-assisted; engage the real M6 spec (170 GB/s, dual NE, 2026-08-25) and the current GLM-5.2 / Kimi K3 / DeepSeek V4 / Qwen3.6 frontier landscape; hedge every throughput number. |
| **2 — unsourced + partly behind** | `qwen-3.7-plus`, `gemini-3.1-pro`, `kimi-instant`, `deepseek-expert`, `grok-4`, `z-ai` | Real primary picks (mostly), but 0 (or unusable) sources. `qwen`/`gemini` are ~12–18 months behind on models and give no M6 detail; `kimi`/`deepseek-expert` are more current; `grok-4` gets the **M6 spec right (170 GB/s)** but drops 3 fabricated families into its alt-lists; `z-ai` is consensus-shaped with no invented tools but has **no M6 facts**, a **fabricated primary-model size**, internal inconsistencies, and relies on swap — the softest member of this bucket. |
| **3 — confident futurism (invents tools/models)** | `deepseek-instant`, `deepseek-instant-deepthink`, `meta-llama-4` | Recommend plausible-sounding but non-existent tools (`Rapid-MLX`, `DSH`, `Ornith-1.0-9B`, `OpenClaw`, `memo`, `Clawtrol`, …). |

Two cross-cuts that look like the actual paper contributions:

1. **Bucket-1 responses converge hardest on the architecture** (MLX + 1 large / 2–3 small workers +
   SQLite + sqlite-vec + OpenHands-in-Docker + Tailscale Serve + launchd + coordinator/worker),
   while buckets 2 and 3 scatter. "Grounded in current reality" appears to predict "agrees with
   the cross-model consensus".
2. **Citation count is not a proxy for citation quality — it can be anti-correlated.**
   `meta-llama-4` produces the largest reference apparatus in the corpus (99 numbered refs + a
   Sources list) and the least reliable one (~60% junk URLs, several propping up fabricated tools).
   A bucket-3 response can imitate bucket-1's *surface form*. Scoring "has a Sources section" as a
   proxy for "is grounded" would rank Meta above GPT-5 and near Claude — exactly backwards.
