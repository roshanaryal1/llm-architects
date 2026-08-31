# Consensus matrix (RQ1)

Per decision axis: the **modal choice**, the count of **independent non-anchor systems** holding it
(out of **10** — `claude-sonnet-5` is the anchor and excluded; DeepSeek counted once via its
canonical `deepseek-expert`; the two non-canonical DeepSeek modes are excluded here and used only
in RQ2/RQ6), and the notable dissent.

Derived from `../../data/decisions-matrix.csv` (39 axes × 13 columns) + each capture's
`## Reviewer notes`. "Anchor agrees" is noted separately because Claude is not a blind peer.

**Legend:** 🟢 unanimous or near-unanimous (9–10/10) · 🟡 majority (6–8/10) · 🟠 plurality (4–5/10, no majority) · 🔴 genuine split (see `disagreements.md`).

---

## Inference & models

| # | Axis | Modal choice | Count /10 | Anchor | Notable dissent |
|---|------|--------------|:---------:|:------:|-----------------|
| 🟢 | `inference_engine` (family) | **MLX-family** on Apple Silicon; llama.cpp/Ollama as fallback/compat | 10 | ✔ | none — the only fully unanimous tool choice |
| 🔴 | `inference_engine` (which server is #1) | *no majority* — `mlx-lm` server direct (2), Ollama-MLX (2), vLLM-MLX (2), llama.cpp-first (1), "Ollama→MLX" (1), "MLX+llama.cpp both" (2) | — | MLX + `llama-swap` | see `disagreements.md` |
| 🟡 | `heavy_local_model` (class) | **~30–35B Qwen MoE, ~3B active, 4-bit** (Qwen3-Coder-30B-A3B or Qwen3.6-35B-A3B) | 7 | ✔ (Qwen3-Coder-30B-A3B) | dense 2024 32B (`qwen-3.7-plus`, `gemini` = 2, the "behind" pair); fabricated size (`meta`, `z-ai` = 2) |
| 🟠 | `heavy_local_model` (exact) | **Qwen3-Coder-30B-A3B** specifically | 4 | ✔ | Qwen3.6-35B-A3B (`gpt-5` primary, `mistral` alt, `grok` alt) |
| 🟢 | `resident_light_model` | **one small 4–9B model** for classification / routing / summaries | 10 | ✔ | size ranges 0.8B–14B; `kimi` swaps rather than keeping one resident |
| 🟢 | `num_models_resident` | **1 large-model worker + 1 small**, ever | 9 | ✔ | `z-ai` §B diagram shows 3 co-resident (contradicts its own text); `deepseek-deepthink` (mode-variant, excluded) says 3 |
| 🟢 | `model_swapping_recommended` | **yes** — keep one daily driver warm, swap the rest on demand | 10 | ✔ | none |
| 🟢 | `concurrency_heavy` | **1** concurrent large-model request/worker | 10 | ✔ | `grok`/`z-ai` write "1–3" but their own budgets resolve to 1 |
| 🟢 | `concurrency_light` | **2–4** concurrent small-model / tool workers | 10 | ✔ | none |
| 🟡 | `cloud_dependence` | **local-first + optional cloud burst** for hardest planning / synthesis / citation-verify, budget-capped; $0 baseline | 7 | ✔ | pure-local, no cloud LLM (`qwen`, `z-ai`; the two DeepSeek fast modes lean this way) |
| 🟡 | `model_router` | **hand-written rule table** by task-type (+ context size + budget + load) | 10 | ✔ | 4 add **LiteLLM** as the proxy (`kimi`, `meta`, `z-ai`, `perplexity`-optional); a trained router (RouteLLM) rejected by all |

## Orchestration & agents

| # | Axis | Modal choice | Count /10 | Anchor | Notable dissent |
|---|------|--------------|:---------:|:------:|-----------------|
| 🟢 | `orchestration_stance` | **thin custom orchestrator**, not a heavyweight framework ("no single harness meets all requirements") | 10 | ✔ | none |
| 🟢 | `build_vs_adopt` | **build the supervisor / scheduler yourself**; adopt the execution pieces + MCP | 10 | ✔ | none |
| 🟠 | `orchestration_framework` (durable-state layer under your code) | **LangGraph** for the durable multi-step graphs | 5 | ✖ (Agent SDK) | Pydantic AI (`gpt-5` w/ a written argument against LangGraph-as-core; `meta` pairs both); plain custom / no framework (`qwen`, `kimi`, `z-ai`, partly `grok`, `deepseek-expert`) |
| 🟢 | `topology` | **hierarchical coordinator/worker** (supervisor → planner → specialists); explicitly **not a swarm** | 10 | ✔ | none |
| 🟢 | `dynamic_agents` | **agents = data** (YAML/JSON/SQLite rows: role, prompt, tools, permissions, model tier); coordinator instantiates one per task + can generate new definitions at runtime; state persists between activations | 10 | ✔ | none |
| 🟢 | `task_queue` | — see split below — | — | ✔ (SQLite) | — |
| 🟡 | `task_queue` (backend) | **SQLite** (durable, single-file, crash-visible) | 8 | ✔ | **Redis (+Celery)** — `deepseek-expert`, `z-ai` (the two that also want Grafana+Prometheus); `meta` optional |
| 🟡 | `coding_agent` (autonomous) | **OpenHands in a Docker sandbox** for long-horizon unattended work | 8 | ✖ (Claude Code) | `deepseek-expert` picks Claude Code; `z-ai` picks Devstral+custom tools |
| 🟡 | `coding_agent` (interactive) | **Aider** for git-native / transparent edits | 8 | ✔ | `perplexity` uses only OpenHands; `gpt-5`/`meta` add an OpenCode/Qwen-Code console |
| 🟢 | `coding_agent` (Claude Code as *the* core) | **rejected** — proprietary / cloud, "optional accelerator only" | 8 | anchor uses it | `deepseek-expert` also picks it |

## Research

| # | Axis | Modal choice | Count /10 | Anchor | Notable dissent |
|---|------|--------------|:---------:|:------:|-----------------|
| 🟢 | `research_arch` | **fixed pipeline**: plan → discover (web + academic APIs + PDF) → extract claims → verify each → contradiction pass → synthesize **from the verified-claims table only** → report | 10 | ✔ | off-the-shelf loop named by some (`GPT-Researcher` — `grok`, `perplexity`-alt; `PaperQA2` — `gemini`; `STORM`/`Open Deep Research` — `mistral`); the rest hand-roll it |
| 🟢 | `anti_hallucination` | **model never cites from memory**; every claim → stored source snippet + `verification_status`; independent verifier re-checks; contradiction pass; DOI resolve against Crossref/OpenAlex | 10 | ✔ | strength varies — `deepseek-instant-deepthink` (excluded) states no explicit rules |
| 🟢 | web-search tool | **at least one** of SearXNG (self-host) / Exa / Firecrawl / Tavily / Brave / Perplexity-Sonar | 10 | ✔ (SearXNG) | self-host (`claude`, `perplexity`-fallback, `mistral`-option) vs managed API (`kimi`, `gpt-5`, `z-ai`, `grok`, `meta`) |
| 🟢 | academic-discovery | **OpenAlex + Semantic Scholar + arXiv (+ Crossref)** APIs | 10 | ✔ | none |
| 🟢 | PDF → structured text | **PyMuPDF** first; **Marker** / **GROBID** / **Docling** for structure | 10 | ✔ | none |

## Memory

| # | Axis | Modal choice | Count /10 | Anchor | Notable dissent |
|---|------|--------------|:---------:|:------:|-----------------|
| 🟢 | `memory_start` | **filesystem (Markdown) + SQLite** | 10 | ✔ | none |
| 🟠 | `vector_db` | **`sqlite-vec`** (in-process, no daemon) | 5–6 | ✔ | **ChromaDB** (`qwen`, `z-ai` = 2; + the DeepSeek fast modes, excluded); **Qdrant embedded** (`perplexity`); LanceDB as grow-into (`meta`); "defer entirely" (`grok`, `deepseek-expert`) |
| 🟢 | standalone vector-DB **daemon** on day 1 | **avoid** | 8 | ✔ | none material |
| 🟢 | `memory_later` | add a **hybrid vector + graph** layer (Mem0 / Cognee / **Graphiti**) **only** when multi-hop / temporal / cross-project recall becomes a real pain | 10 | ✔ | Graphiti named for "facts supersede each other" by `claude` + `mistral` |
| 🟢 | `knowledge_graph` on day 1 | **no** — Neo4j / heavy graph DB deferred | 10 | ✔ | none — Neo4j is on 6+ "do not install" lists |
| 🟢 | memory tiers | **episodic + semantic + procedural (+ working)** as distinct stores | 9 | ✔ | naming varies; `z-ai` adds Redis as the "working" tier |

## Ops, security, remote

| # | Axis | Modal choice | Count /10 | Anchor | Notable dissent |
|---|------|--------------|:---------:|:------:|-----------------|
| 🟢 | `sandbox_isolation` (base) | **dedicated non-admin macOS user** + workspace/path jail (symlink-resolved) | 10 | ✔ | none |
| 🔴 | `sandbox_isolation` (per-task container) | *split* — Docker/OrbStack (5), `sandbox-exec`/Seatbelt (3), Apple `container`/Colima (anchor), Lima VM (2) | — | Apple `container`/Colima | see `disagreements.md` |
| 🟢 | secrets | **never in the agent's filesystem/context**; Keychain or a broker, injected per-tool | 10 | ✔ | `meta`/`nono`-style fd-injection (unverified tool) — same principle |
| 🟢 | permission model | **explicit autonomous / approval-required / never** tiers + a destructive-command blocklist + an append-only audit log | 10 | ✔ | wording varies; the autonomous-vs-approval line is remarkably consistent (read+test+workspace-edit+local-git = auto; push/install/outside-workspace/credentials/spend = approve) |
| 🟢 | `remote_network` | **Tailscale only** — no public ports, no router port-forward | 10 | ✔ | WireGuard as the manual fallback; Funnel/Cloudflare-Tunnel for the dashboard rejected by 4+ |
| 🟢 | `remote_control_plane` | **small FastAPI/Streamlit dashboard bound to the tailnet IP** + push notifications (ntfy / Pushover / Telegram) + emergency STOP + approval queue | 10 | ✔ | `z-ai` adds a Caddy reverse proxy (unique); `claude` adds Claude Code Remote Control (unique) |
| 🟢 | `always_on_supervision` | **`launchd`** (`RunAtLoad` + `KeepAlive`) + a **separate watchdog** process | 10 | ✔ | `meta` notes `kickstart -k` not `bootout` |
| 🟢 | `sleep_prevention` | **`caffeinate`** (+ `pmset` / Energy settings) | 10 | ✔ | `gpt-5` — queue-aware keep-awake (sleep when idle) |
| 🟢 | `crash_recovery` | **durable SQLite queue survives crash/reboot**; on startup requeue/resume tasks stuck "running" (lease timeout → INTERRUPTED); checkpoint task state so it resumes not restarts | 10 | ✔ | none |
| 🟡 | monitoring | **custom / minimal** (structured JSON logs) | 8 | ✔ | **Grafana + Prometheus** — `deepseek-expert`, `z-ai` |

## Storage

| # | Axis | Modal choice | Count /10 | Anchor | Notable dissent |
|---|------|--------------|:---------:|:------:|-----------------|
| 🟢 | `storage_internal` (512 GB) | OS + **hot/active model(s)** + SQLite DBs + active repos + logs; keep ~100–150 GB free | 10 | ✔ | none |
| 🟢 | `storage_external` (1 TB) | full **model library** + git repos + research papers/PDFs + datasets + embeddings + backups + disposable task workspaces; APFS | 10 | ✔ | `z-ai` assumes a 3rd 2 TB HDD not in the spec |
| 🟢 | hot model / live DB on the external SSD | **no** — latency + dropout risk | 9 | ✔ | none material |

## Bottleneck (analysis, not a choice)

| # | Axis | Consensus | Count /10 |
|---|------|-----------|:---------:|
| 🟢 | `biggest_bottleneck` | **memory** — capacity first, then bandwidth (→ tok/s), then the single heavy slot (→ queue latency); KV-cache growth is the silent one | 10 |

---

## Summary counts

- **Fully unanimous (10/10 or 9/10):** ~24 of 39 axes — MLX family, 1-heavy-worker, model swapping, custom thin orchestrator, coordinator/worker topology, agents-as-data, fixed research pipeline, never-cite-from-memory, filesystem+SQLite memory, defer the knowledge graph, dedicated non-admin user, Tailscale-only, FastAPI dashboard + STOP, launchd + watchdog, caffeinate, durable-queue crash recovery, internal-hot / external-cold storage split, memory-is-the-bottleneck.
- **Majority (6–8/10):** SQLite task queue (8), OpenHands+Aider coding (8 each), optional-cloud (7), minimal monitoring (8), ~30–35B Qwen MoE class (7).
- **Plurality / no majority (4–5/10):** the specific inference server, the exact heavy model, the orchestration-framework layer, `sqlite-vec` vs Chroma.
- **Genuine split (see `disagreements.md`):** inference server #1, per-task sandbox tech, task-queue backend, monitoring depth.

The anchor (`claude-sonnet-5`) sits inside the modal choice on **every** axis except two: it uses Claude Code (proprietary) where the peers converge on OpenHands+Aider, and it uses its own Agent SDK where the peers split between LangGraph and plain custom. Both are explainable by it being an Anthropic product answering from inside Claude Code.
