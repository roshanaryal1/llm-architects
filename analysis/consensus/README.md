# `analysis/consensus/` — cross-response synthesis (RQ1)

**Status: early-signal only.** The three real artefacts below are not written yet; build them once
Grok 4 (#6) lands (11 of ~12 responses captured):

1. **`consensus-matrix.md`** — per axis in `data/decisions-matrix.csv`: the modal choice, the count
   of *independent* responses holding it (`claude-sonnet-5` excluded — it is the anchor, not a
   blind peer), and a note on the spread.
2. **`disagreements.md`** — the axes where responses genuinely conflict, with the competing
   positions and the tradeoff. The interesting part of the paper.
3. **`reference-architecture.md`** — one merged design; every non-consensus call labelled
   `[adjudicated]` with reasoning. The paper's synthesis section and the author's build brief.

---

## Corpus: 11 responses from 9 systems

DeepSeek contributed 3 modes of one base model (DeepSeek-V4-Pro). `data/systems.csv` marks
`deepseek-expert` as the **canonical** DeepSeek answer.

- **Per-system claims below (RQ1 agreement, "how many models pick X")** count **9 systems**
  (8 non-anchor): the canonical column per system.
- **Per-response claims (RQ2 fabrication, RQ6 mode sensitivity)** use all **11 captures**.
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
| `meta-llama-4` | Meta AI / hosted Llama 4 | ✔ | LOW | **99 refs, ~60% junk** | 3 |
| `deepseek-instant` | DeepSeek-V4-Pro (fast mode) | mode-variant | LOW | 0 | 3 |
| `deepseek-instant-deepthink` | DeepSeek-V4-Pro (instant+DeepThink) | mode-variant | LOW | 0 | 3 |

"Bucket" = the emerging 3-way recency/rigour split (see bottom).

---

## Early signal (from 11 responses — provisional, not a result)

> The `X/11` counts in this **early-signal** section are per-*response* (they include both
> non-canonical DeepSeek modes). The formal per-*system* tally (one canonical column per system,
> "of 9") is what `consensus-matrix.md` will produce — that is the number the paper reports for
> RQ1. Where the two differ it is because the DeepSeek fast modes echo `deepseek-expert`, so a
> per-system count is usually `per-response count − 0..2`.

### Unanimous (9/9 systems; 11/11 responses)

- **MLX-family local inference** is the correct Apple-Silicon path (llama.cpp/Ollama as
  fallback/compat). Even the fabrication-heavy responses agree on this.
- **100 logical agents ≠ 100 model processes.** Agents are cheap YAML/SQLite definitions
  (role, tools, permissions, workspace, model tier); a bounded worker pool drains a task queue.
- **~1 concurrent large-model worker + 2–3 small-model workers.** Two large MoE models will not
  co-reside in 32 GB. Every response states this.
- **Coordinator/worker (supervisor) topology, explicitly NOT a swarm.**
- **The orchestrator is mostly your own code**, not a framework you live inside
  (CrewAI/AutoGen rejected by name in 9/11 "what NOT to install" lists).
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
| **Primary local model** | Qwen3-Coder-30B-A3B (Claude, Perplexity, DeepSeek-Expert, Kimi) · Qwen3.6-35B-A3B (GPT-5 primary, Mistral alt — GPT-5 rejects the 80B Qwen3-Coder-Next) · dense 2024 32B (Qwen 3.7 Plus, Gemini) · fabricated tags (DeepSeek fast modes, Meta) |
| **Task queue backend** | SQLite-only (8/11) · Redis + Celery (DeepSeek-Expert) · Redis+SQLite fallback (Meta, optional) |
| **Orchestration substrate** | Claude Agent SDK (Claude) · LangGraph (Perplexity, Mistral, Gemini) · Pydantic AI (GPT-5, with a written argument against LangGraph-as-core; Meta pairs it with LangGraph) · plain custom Python (Qwen, Kimi, DeepSeek runs) |
| **Exec sandbox** | dedicated-user-only (Qwen) · user + Apple `container`/Colima (Claude) · user + Docker/OrbStack (DeepSeek-Expert [then forbids it], Perplexity, Mistral, GPT-5, Meta) · user + Lima VM + Seatbelt (DeepSeek-DeepThink, Gemini) |
| **Monitoring** | custom/minimal (most) · Grafana + Prometheus (DeepSeek-Expert) |
| **Memory headroom** | keep 2–6 GB free (Claude, Perplexity, GPT-5, Mistral) · "oversubscribe to 32–34 GB, acceptable" (DeepSeek-DeepThink — outlier, likely bad advice) |
| **2026-edge tooling** | adopt it (Claude) · deliberately avoid, benchmark-first (Perplexity) · invent it (DeepSeek fast modes, Meta) |
| **M6 memory bandwidth** | **170 GB/s (correct)** — Claude, Mistral, Perplexity, GPT-5 · **"~300+ GB/s" (wrong)** — Meta · not mentioned — the rest |

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
| `perplexity` | none (2 arXiv IDs unverified — evidence-quality, not fabrication) |
| `claude-sonnet-5` | none |

**8 of 11 responses fabricate nothing.** The fabrication is concentrated in **DeepSeek's non-"expert"
free modes and Meta / Llama 4** — a within-/cross-vendor mode effect, not a spread. Notably,
**`Rapid-MLX` + the `raullenchai` Homebrew tap + `Gemma 4`** appear in *both* `deepseek-instant`
and `meta-llama-4` — a shared hallucination attractor worth a paragraph in the paper.

---

## The emerging headline: a 3-way recency/rigour split — and citations are not a proxy for it

| Bucket | Responses | Character |
|---|---|---|
| **1 — sourced/retrieval + current + M6-aware** | `claude-sonnet-5`, `mistral-large-3`, `perplexity`, `gpt-5` | Browsed or retrieval-assisted; engage the real M6 spec (170 GB/s, dual NE, 2026-08-25) and the current GLM-5.2 / Kimi K3 / DeepSeek V4 / Qwen3.6 frontier landscape; hedge every throughput number. |
| **2 — unsourced + ~12–18 months behind** | `qwen-3.7-plus`, `gemini-3.1-pro`, `kimi-instant`, `deepseek-expert` | Real tools, but 2024-era models and/or `Claude 3.5 Sonnet` as the cloud fallback; little or no M6-specific detail. |
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
