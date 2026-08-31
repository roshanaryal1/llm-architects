# Disagreements (RQ1)

The axes where the corpus genuinely splits — no majority, or a substantive minority with a real
argument. For each: the competing positions, who holds them, the actual tradeoff, and what
`reference-architecture.md` adjudicated. Counts are of the **10 non-anchor systems**.

---

## 1. Which inference server is #1

**Everyone agrees on the MLX family. Nobody agrees on the server.**

| Position | Systems | Argument |
|---|---|---|
| `mlx-lm` server, direct | `mistral`, `gpt-5` | Apple-native, OpenAI-compatible + tool calling + continuous batching, WWDC-endorsed; smallest dependency surface; "MLX-LM server security is minimal — put it behind Tailscale, never expose it" (`gpt-5`) |
| Ollama 0.19+ (MLX backend) | `kimi`, `grok` (default) | Easiest lifecycle + model management + OpenAI API; "now MLX-fast on Mac"; the practical default for someone who wants to start today |
| `vLLM-MLX` | `meta`, `z-ai` (#1 pick) | Continuous batching + paged KV cache → higher aggregate throughput under concurrent agent load; Anthropic-API-compatible variants exist. **Caveat:** `meta`'s throughput numbers ("130–464 tok/s", "3.4×") are unattributed; `z-ai`'s are invented |
| llama.cpp server, first | `gemini` | Lowest RAM overhead vs "Python-heavy runners"; `-np` slot prompt-caching; GGUF ecosystem breadth |
| "Ollama to start, benchmark MLX later" | `perplexity` | Explicitly defers the decision to a two-hour benchmark on the real M6 |
| MLX **and** llama.cpp, both installed | `qwen`, `deepseek-expert` | MLX for the hot path, llama.cpp for long-tail model formats |
| + `llama-swap` in front | `claude` (anchor), `mistral` | Request "the coding model" / "the small model" by alias; TTL-unload idle models |
| + `oMLX` | `mistral` | SSD-tiered KV cache so 128K+ contexts spill to the external SSD instead of OOM — **the only response to raise this** |

**Tradeoff:** `mlx-lm`/Ollama = simplest, single-user-fast, weak concurrency. `vLLM-MLX` = best under concurrent load, youngest/least-proven, some responses inflate its numbers. `llama.cpp` = most compatible, slowest decode.

**Adjudicated:** `mlx-lm` server (unanimous family + the two most-sourced non-anchor picks) fronted
by `llama-swap` (the swap layer 3 responses want). Ollama-MLX is the acceptable simpler substitute.
`vLLM-MLX` and `oMLX` are Phase-8 upgrades once you measure real concurrent demand and real KV
pressure — not day-1 picks, and not on the strength of the unverified throughput claims.

---

## 2. Exact heavy local model

**7/10 land in the "~30–35B Qwen MoE, ~3B active, 4-bit" family. The exact model splits, and 4/10 are wrong.**

| Position | Systems | Note |
|---|---|---|
| Qwen3-Coder-30B-A3B (real MoE) | `deepseek-expert`, `perplexity`, `kimi`, `mistral` (+ anchor) | The plurality real pick; ~17–22 GB at 4-bit, 256K capable, MoE keeps decode fast |
| Qwen3.6-35B-A3B (real MoE) | `gpt-5` (primary), `mistral` (alt), `grok` (alt) | Near-equivalent; `gpt-5` explicitly **rejects the 80B Qwen3-Coder-Next** ("wrong machine", ~40 GB) — `meta` agrees on the 80B |
| Dense 2024 32B (Qwen2.5-Coder-32B) | `qwen-3.7-plus`, `gemini` | The two responses with the oldest model knowledge; a dense 32B is far slower per token on 170 GB/s than a 3B-active MoE |
| Fabricated | `meta` (`Qwen3.5-35B-A3B` + fake OpenRouter id), `z-ai` (`Qwen3-Coder-Next 8B` — a real 80B model given a fake 8B size) | Attribute corruption on real model names |
| Devstral Small 2 (24B) | named as a coding option by `grok`, `mistral`, `z-ai`, `gpt-5`-adjacent | Only local coder with a hard SWE-bench number; the safe fallback |

**Tradeoff:** MoE (30–35B / ~3B active) = "reasoning of a big model at the speed of a small one",
fits with context headroom. Dense 32B = simpler, proven, ~3–4× slower per token here. 80B = doesn't
fit. 8–14B dense = fast but weaker on multi-file work.

**Adjudicated:** **Qwen3-Coder-30B-A3B 4-bit** (plurality real pick), or **Qwen3.6-35B-A3B 4-bit**
if it has the better MLX build at install time — pick by measured tok/s + KV headroom on the unit.
Keep **Devstral Small 2 24B** as the tested fallback. Not a dense 2024 32B; not the 80B.

---

## 3. Per-task execution sandbox

**Dedicated non-admin user + workspace jail is unanimous. The container/VM layer on top is not.**

| Position | Systems | Argument |
|---|---|---|
| Docker / OrbStack container per task | `deepseek-expert`, `perplexity`, `mistral`, `gpt-5`, `meta` | "OpenHands officially recommends its Docker sandbox"; non-root + read-only mounts + egress filter + timeout; OrbStack for macOS perf. **`deepseek-expert` then lists "Docker for Mac" under *do not install* — an internal contradiction** |
| `sandbox-exec` / Seatbelt profiles | `gemini`, `grok`, `z-ai` | Native macOS, no VM overhead, per-binary rules; lighter for non-container tool calls |
| Apple `container` (macOS 26) / Colima | `claude` (anchor) | Per-workload lightweight VM, native, avoids Docker Desktop licensing; Colima as the safe fallback |
| Lima VM | `deepseek-instant-deepthink` (mode-variant), `gemini` (mention) | Full Linux VM isolation, heavier |
| kernel-capability sandboxes (`cplt`, `nono`) | `meta`, `z-ai` (mention) | fd-injection secrets, seccomp-BPF — **`cplt`/`nono` are unverified/likely fabricated** |

**Tradeoff:** container = strongest isolation for untrusted generated code + what OpenHands expects,
but Docker Desktop has licensing/overhead and shares the host kernel. `sandbox-exec` = zero
overhead, native, but coarser and macOS-only. Apple `container` = VM-per-workload without Docker
Desktop, but young.

**Adjudicated:** dedicated non-admin user + workspace jail (unanimous) **+ Colima or Apple
`container`** for the OpenHands coding sandbox and any untrusted-code execution (avoids Docker
Desktop; matches the anchor) **+ `sandbox-exec`** as a light wrapper for one-off tool calls that
don't need a container. Default-deny egress with an allowlist regardless of which one.

---

## 4. Task-queue backend

| Position | Systems | Argument |
|---|---|---|
| SQLite (single file, WAL) | `claude`, `qwen`, `perplexity`, `gemini`, `kimi`, `mistral`, `gpt-5`, `grok` (8/10) | Zero daemon, survives reboot, crash-visible states, one backup target; "one box does not justify Redis" |
| Redis (+ Celery) | `deepseek-expert`, `z-ai` (+ `meta` optional) | In-memory speed, native priorities/retries, "durable" with persistence; both these responses also want Grafana + Prometheus — a heavier-infra worldview |

**Tradeoff:** Redis buys throughput + mature priority/retry semantics at the cost of another daemon,
another failure mode, another thing to back up — on a single 32 GB box where the queue is never the
bottleneck (the single heavy inference slot is).

**Adjudicated:** **SQLite** (8/10). Revisit Redis only when you go multi-machine (a shared queue
across a Mac orchestrator + a GPU inference host) — which several responses flag as exactly the
64 GB+/GPU-server upgrade trigger.

---

## 5. Vector store (when you add one)

| Position | Systems | Argument |
|---|---|---|
| `sqlite-vec` (in-process) | `claude`, `gemini`, `kimi`, `mistral`, `gpt-5` (+ `meta` "memo pattern") = 5–6/10 | No daemon, ~4 ms queries, lives in the DB file you already back up; `gpt-5` flags it "pre-v1, API may change" |
| ChromaDB | `qwen`, `z-ai` (+ DeepSeek fast modes) = 2–3/10 | Popular, simple Python, "good enough for a start" |
| Qdrant embedded | `perplexity` | Local binary, advanced filtering, "a sensible later step without deploying a server" |
| LanceDB embedded | `meta` (grow-into) | Embedded columnar, no service |
| defer entirely | `grok`, `deepseek-expert` | "FTS5 first; add a vector layer only when lexical search fails" |

**Tradeoff:** all are embedded/local; the real question is whether to add the dependency at all
before lexical/FTS search demonstrably breaks. `sqlite-vec` adds the least; Chroma/Qdrant/LanceDB
add a package + a second index to manage.

**Adjudicated:** **`sqlite-vec`** (plurality), added **only after** SQLite FTS5 retrieval starts
missing things. Chroma is an acceptable substitute if you already know it. Migrate to Qdrant/LanceDB
only past ~1 M chunks (the trigger several responses name).

---

## 6. Orchestration-framework layer under the custom supervisor

| Position | Systems | Argument |
|---|---|---|
| LangGraph (for the durable multi-step graphs) | `perplexity`, `gemini`, `mistral`, `grok`, `meta` = 5/10 | Directed graph + conditional edges + durable checkpoints + human-in-the-loop; "maps to audit trails and rollback points" |
| Pydantic AI (type-safe agent loop) | `gpt-5` (with a dedicated section *against* LangGraph-as-core), `meta` (pairs both) | FastAPI-style ergonomics, structured output, MCP/A2A, subagent toolsets; "a graph framework alone is not your operating system" |
| plain custom Python (no framework) | `qwen`, `kimi`, `z-ai`, partly `grok`, `deepseek-expert` | "Heavy frameworks add latency + token overhead + cloud assumptions"; asyncio + a queue is enough |
| Claude Agent SDK | `claude` (anchor only) | Reuses the Claude Code agent loop + permissions + subagents + per-subagent model routing |

**Tradeoff:** LangGraph = real durable-execution + observability for free, but it is an abstraction
to learn and it is not the whole control plane. Pydantic AI = lighter, type-safe, still young.
Plain custom = maximum control, you write the checkpointing/retry/HITL yourself.

**Adjudicated:** a **thin custom Python supervisor owns the top-level loop** (queue, scheduling,
permissions, resource governor, remote control — the things no framework covers). Add **LangGraph**
(the plurality) *inside* it for the durable, branchy research and coding sub-graphs only — not as
the outer loop. `gpt-5`'s argument stands: the framework is a node executor, not the operating
system.

---

## 7. Monitoring depth

| Position | Systems |
|---|---|
| custom / minimal — structured JSON logs + a health endpoint | 8/10 |
| Grafana + Prometheus | `deepseek-expert`, `z-ai` |

**Tradeoff:** Grafana/Prometheus = real dashboards + alerting + historical trends, at the cost of
two more services on a 32 GB box for a single-operator system.

**Adjudicated:** **structured logs + the FastAPI `/system/health` endpoint + ntfy alerts** for
Phase 1–7. Grafana/Prometheus is a legitimate **Phase 8** add once you have weeks of logs and want
trend analysis — not before.

---

## 8. Cloud dependence

| Position | Systems | Argument |
|---|---|---|
| local-first + optional cloud burst | `claude`, `deepseek-expert`, `perplexity`, `mistral`, `gpt-5`, `grok`, `kimi` = 7/10 | Escalate to a frontier API only for the hardest planning / final synthesis / citation-verification, gated by a $/day budget; "don't be ideological about 100% local" (`gpt-5`) |
| pure local, no cloud LLM | `qwen`, `z-ai` (+ DeepSeek fast modes lean this way) | Privacy + $0 + offline resilience; cloud only for web search |

**Tradeoff:** the 30–35B local class still trails frontier models on hard multi-file reasoning and
on citation discipline — the two places a mistake costs hours. But every cloud call is data leaving
the box and a recurring cost.

**Adjudicated:** **local-first, cloud-optional** (7/10). Wire the escape hatch (one frontier model
behind the router, budget-capped, `privacy_class`-gated per `gpt-5`), leave it **off by default**,
turn it on per-objective for the hardest steps. The system must be fully useful with it off.

---

## Non-disagreements worth noting

These looked like splits but resolve on inspection:

- **"1–3 concurrent large workers"** (`grok`, `z-ai`) vs **"1"** (everyone else) — `grok`/`z-ai`'s
  own memory budgets only fit **1**; `z-ai` even admits "fits with swapping". Not a real split.
- **Docker on the "do not install" list** (`deepseek-expert`, `z-ai`, `kimi`) vs **Docker for the
  sandbox** (`perplexity`, `mistral`, `gpt-5`, `meta`) — the "avoid" lists mean **Docker Desktop**
  (licensing/overhead); the "use" recommendations are satisfied by Colima/OrbStack. Same position,
  different words.
- **self-hosted vs managed web search** — a cost/privacy preference, not an architecture
  disagreement; all 10 agree on "store retrieved content, verify every citation".
