# `analysis/consensus/` — cross-response synthesis (RQ1)

**Status: synthesis drafted (issue #10).** Refine as `prompt-v2/v3` (#8) and the rater scores (#9)
land.

1. **[`consensus-matrix.md`](consensus-matrix.md)** — the decision axes with, for each, the
   modal/plurality choice, the count of the 10 non-anchor systems holding it, and a
   spread/interpretation note.
2. **[`disagreements.md`](disagreements.md)** — the ~10 axes with a genuine split (primary model,
   inference server, orchestration substrate, coding executor, vector store, sandbox depth,
   task-queue backend, cloud escalation, memory-residency policy, monitoring stack) — each with the
   positions, the tradeoff, and the engineering implication. Plus what the split pattern means for
   the paper.
3. **[`reference-architecture.md`](reference-architecture.md)** — the merged design in 17 sections:
   9 design principles, a topology diagram, per-subsystem picks tagged `[adjudicated]` where the
   corpus splits, a 32 GB resource-budget table, a `[adjudicated]` decisions ledger, a
   "what NOT to build initially" list, and a 12-step first-implementation order. The paper's
   synthesis section **and** the author's build brief.

> A fuller alternative draft of these three files (grouped-by-category matrix with a 🟢🟡🟠🔴
> legend, an 8-phase build order with test/rollback per phase) exists in git history at
> `61b658f` / `d94e211` / `8227151` — cherry-pick from it if useful.

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
  fallback/compat). Even the lowest-rigour responses agree on this.
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
| **Primary local model** | Qwen3-Coder-30B-A3B (Claude, Perplexity, DeepSeek-Expert, Kimi) · Qwen3.6-35B-A3B (GPT-5 primary, Mistral alt — GPT-5 correctly rejects the 80B Qwen3-Coder-Next as too big for 32 GB) · Qwen 27B dense / 35B-A3B (Grok) · dense 2024 32B (Qwen 3.7 Plus, Gemini) · **genuine size error** ("Qwen3-Coder-Next 8B" — z-ai; real model is 80B MoE) · `Qwen3.5-*` tags unverified (DeepSeek fast modes, Meta) |
| **Task queue backend** | SQLite-only (majority) · **Redis** (DeepSeek-Expert +Celery, z-ai, Meta-optional) |
| **Orchestration substrate** | Claude Agent SDK (Claude) · LangGraph (Perplexity, Mistral, Gemini) · Pydantic AI (GPT-5, with a written argument against LangGraph-as-core; Meta pairs it with LangGraph) · plain custom Python (Qwen, Kimi, Grok, z-ai, DeepSeek runs) |
| **Exec sandbox** | dedicated-user-only (Qwen, Grok via `sandbox-exec`) · user + `sandbox-exec` (z-ai) · user + Apple `container`/Colima (Claude) · user + Docker/OrbStack (DeepSeek-Expert [then forbids it], Perplexity, Mistral, GPT-5, Meta) · user + Lima VM + Seatbelt (DeepSeek-DeepThink, Gemini) |
| **Monitoring** | custom/minimal (most) · Grafana + Prometheus (DeepSeek-Expert, z-ai) |
| **Inference engine #1** | MLX + llama-swap (Claude) · Ollama-0.19-MLX (Kimi, Grok default) · mlx-lm server (Mistral, GPT-5) · llama.cpp server (Gemini) · **vLLM-MLX** (z-ai — first to make it the primary) |
| **Memory headroom** | keep 2–6 GB free (Claude, Perplexity, GPT-5, Mistral) · "oversubscribe to 32–34 GB, acceptable" (DeepSeek-DeepThink — outlier, likely bad advice) |
| **2026-edge tooling** | adopt it (Claude) · deliberately avoid, benchmark-first (Perplexity) · name lots of it (DeepSeek fast modes, Meta — **all real, post-anchor-cutoff releases**) |
| **M6 memory bandwidth** | **170 GB/s (correct)** — Claude, Mistral, Perplexity, GPT-5, Grok · **"~300+ GB/s" (wrong)** — Meta only · not mentioned — Qwen, Gemini, Kimi, DeepSeek, z-ai |

---

## Fabrication watch (RQ2) — RETRACTED AND REBUILT 2026-09-01

> **The original version of this section was wrong.** The anchor rater (Claude Sonnet, ~Jan 2026
> knowledge cutoff) flagged 14 tools/models across the corpus as fabricated. On web verification
> (see `analysis/verification/tool-model-register.md`), **zero were confirmed fabricated** and at
> least 12 are **real products/model releases dated Feb–Aug 2026** — after the anchor's cutoff.
> "Cross-vendor shared hallucination of `Rapid-MLX` / `Gemma 4`" is **withdrawn**: both are real
> (`raullenchai/Rapid-MLX`, renamed from vLLM-MLX Mar 2026; Gemma 4 released 2026-04-02 with both
> 26B-A4B MoE and 31B dense variants).

### The real RQ2 finding

**An LLM used as a systems-architecture rater, with a fixed training cutoff, systematically
misclassifies real post-cutoff tools and models as hallucinations.** 14 anchor "fabrication"
flags → 0 confirmed fabricated, ≥12 real-but-post-cutoff, remainder unresolved. The false
positives cluster exactly on the responses that were *most* current (DeepSeek fast modes, Meta),
which the anchor's own recency limits made it least able to verify.

| "Fabrication" flagged by the anchor | Verdict | Evidence (2026) |
|---|---|---|
| `Rapid-MLX` (deepseek-instant, meta-llama-4, grok-4) | **REAL** | `github.com/raullenchai/Rapid-MLX`, ex vLLM-MLX, renamed Mar 2026 |
| `Gemma 4` 26B / 31B / 12B (deepseek-instant, meta-llama-4, grok-4) | **REAL** | Released 2026-04-02; 26B-A4B MoE + 31B dense + 12B unified all real variants |
| `DeepSeek Harness` / `DSH` (deepseek-instant) | **REAL** | `github.com/deepseek-ai/deepseek-harness`, open-sourced 2026-08-13, MIT |
| `OpenClaw` (meta-llama-4) | **REAL** | Steinberger; ex Warelay → Moltbot → OpenClaw; has a Wikipedia page |
| `Claw Code` (z-ai, meta-llama-4) | **REAL** | Clean-room Claude Code rewrite after the 2026-03-31 source-map leak; ~72k stars |
| `Clawtrol` (meta-llama-4) | **REAL** | `github.com/wolverin0/clawtrol` — agent kanban dashboard |
| `Ornith-1.0-9B` (deepseek-instant-deepthink) | **REAL** | `huggingface.co/deepreinforce-ai/Ornith-1.0-9B`; Ollama `ornith:9b` |
| `WhipDesk` (deepseek-instant-deepthink) | **REAL** | `github.com/BinaryBananaLLC/WhipDesk` — phone control of coding agents |
| `LightAgent` (deepseek-instant-deepthink) | **REAL** | `github.com/wanxingai/LightAgent`; arXiv 2509.09292 |
| `nono` (meta-llama-4) | **REAL** | Landlock/Seatbelt sandbox tool, file + network isolation |
| `GLM-4.7-Flash` (grok-4) | **REAL** | Zhipu, 2026-01-19, 30B-A3B MoE — grok's label is spec-accurate |
| `Qwen3-Coder-Next` (referenced by gpt-5, z-ai) | **REAL, 80B MoE** | `huggingface.co/Qwen/Qwen3-Coder-Next` — gpt-5 right to reject it; z-ai wrong to call it 8B |
| `Helmrig`, `Cloak`, `DiffResearch`, `cplt`, `memo`, `agent-policy-engine`, `pi-search-hub` | **UNRESOLVED** | No web evidence found either way — **not** counted as fabrication |

### Genuine defects that survive verification (these stay in the analysis)

| Response | Defect | Type |
|---|---|---|
| `z-ai` | `Qwen3-Coder-Next` given as "8B ~5 GB" — real is 80B MoE; it is the load-bearing primary coding pick | model size error |
| `z-ai` | same model quoted at 5 GB and 14 GB; 3-instance co-resident diagram vs on-demand prose; "fits with swapping" | internal inconsistency + hardware slip |
| `grok-4` | none beyond 0 sources — got the full M6 spec incl 170 GB/s right; alt-list picks all real | (no surviving factual defect) |
| `deepseek-expert` | recommends Docker in A/H, forbids it in J; dashboard binds `0.0.0.0` vs "no public exposure" | internal contradiction |
| `deepseek-instant` | recommends Ollama in Phase 4, forbids it in J | internal contradiction |
| `deepseek-instant-deepthink` | 256K context vs 1–2 GB KV budget; advocates 32–34 GB always-loaded (memory oversubscription) | hardware violation |
| `meta-llama-4` | 99 numbered refs; ~60% junk GitHub commit/PR/issue/`SKILL.md` URLs; same tool given multiple repo URLs; `[38]` mis-titles a real arXiv paper | citation quality (verifiable independent of recency) |
| `kimi-instant` | number inflation ("OpenCode 198k stars", "gpt-oss 98.3%"); stale cloud list | recency / rigour |
| `gemini-3.1-pro`, `qwen-3.7-plus` | ~12–18 months behind on models; stale cloud-fallback names; no M6 detail | recency (RQ4) |

---

## The recency/rigour split — recomputed against the adjudicated rubric scores (2026-09-01)

> The original 3-way split put `deepseek-instant`, `deepseek-instant-deepthink` and `meta-llama-4`
> in a "confident futurism / invents tools" bucket. Web verification killed that premise. The
> buckets below are now backed by the **adjudicated 9-dimension rubric scores** from the
> four-rater pass (issue #9 — see `analysis/scoring/rater-agreement-2026-09-01.md`), not by
> rater judgement of "fabrication".
>
> **Adjudicated totals (/18, non-anchor; after the clean D3/D4 re-run 2026-09-01):**
> perplexity 18 · mistral-large-3 15 · gpt-5 14 · grok-4 14 · gemini-3.1-pro 12 ·
> qwen-3.7-plus 12 · kimi-instant 11 · meta-llama-4 11 · deepseek-instant 9 ·
> deepseek-expert 8 · deepseek-instant-deepthink 6 · z-ai 5.
> Anchor `claude-sonnet-5`: 15 (excluded from cross-response stats).
> Inter-rater: exact 68 %, within-1 97 %, Cohen's κ_w +0.64, Krippendorff's α +0.20.
> **D6 citation-quality is the cleanest separator** — the top 4 score 2/2/2/0, everyone else 0.

| Bucket (adjudicated) | Responses | Character |
|---|---|---|
| **1 — sourced-or-consensus + current + M6-aware** (adj. 14–18) | `perplexity` (18), `mistral-large-3` (15), `gpt-5` (14), `grok-4` (14) — plus anchor `claude-sonnet-5` (15) | Engage the real M6 spec (170 GB/s, dual NE, 2026-08-25); hedge throughput; picks all real and current. `perplexity`/`mistral` also cite (D6 = 2); `gpt-5`/`grok-4` are held a step down by 0 usable source URLs. |
| **2 — current, real picks, 0 usable sources, model-recency lag or a spec slip** (adj. 11–12) | `gemini-3.1-pro` (12), `qwen-3.7-plus` (12), `kimi-instant` (11), `meta-llama-4` (11) | D6 = 0. `qwen`/`gemini` carry a ~12–18-month model lag and no M6 engagement; `kimi` a wrong CLI + number inflation; `meta` the ~60 % junk-URL apparatus and the M6 "300+ GB/s" bandwidth error. |
| **3 — real internal defects** (adj. ≤ 9) | `deepseek-instant` (9), `deepseek-expert` (8), `deepseek-instant-deepthink` (6), `z-ai` (5) | Not "confident futurism" — the tools are real. They score low for **verifiable** reasons: `deepseek-expert` / `deepseek-instant` each recommend a tool their own "do not install" list forbids (D9 = 0), and `deepseek-expert` additionally names a non-existent future model `Qwen3-Coder-70B` (D4 = 1); `deepseek-instant-deepthink` advocates 32–34 GB oversubscription (D1 = 0) and mislabels DeepSeek-V4 as dense (D4 = 0); `z-ai` has a load-bearing model-size error (Qwen3-Coder-Next 8B vs 80B; GLM-4.5-Air ~4 GB vs 106B/12B) and a 5-vs-14 GB self-contradiction (D1/D4/D9 = 0). |

Cross-cuts that still look like paper contributions:

1. **Bucket-1 responses converge hardest on the architecture** (MLX + 1 large / 2–3 small workers +
   SQLite + sqlite-vec + OpenHands-in-Docker + Tailscale Serve + launchd + coordinator/worker),
   while buckets 2 and 3 scatter. Being sourced *and* internally consistent predicts agreement
   with the cross-model consensus — being merely *current* does not.
2. **Citation count is not a proxy for citation quality — it can be anti-correlated.**
   `meta-llama-4` produces the largest reference apparatus in the corpus (99 numbered refs + a
   Sources list) and the least reliable one (~60% junk URLs). Independent of recency: the URLs
   don't resolve or don't support the claim. Scoring "has a Sources section" as a proxy for "is
   grounded" would rank Meta above GPT-5 — backwards.
3. **RQ2 itself:** LLM-as-rater cutoff bias produces false-positive hallucination flags,
   concentrated on the most up-to-date responses. Ground truth =
   `analysis/verification/tool-model-register.md`.
