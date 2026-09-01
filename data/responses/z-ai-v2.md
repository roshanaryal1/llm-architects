---
ai_name: z.ai (Zhipu GLM)
model_version_id: "GLM-5.2 (Z.ai); self-reports knowledge cutoff ~mid-2025"
provider: Zhipu AI (z.ai)
interface: z.ai chat (free)
browsing_enabled: NO — self-declared "answering from internal knowledge"; URLs given as "canonical project locations", explicitly marked "re-verify"
knowledge_cutoff: "self-reported ~mid-2025"
prompt_version: v2
date_run: 2026-09-01
run_by: roshanaryal1
notes_on_run: >
  Second z.ai capture, on prompt-v2 (RFC framing). Fresh chat. Full A–K + a ~45-entry Sources list
  of real canonical repo/vendor URLs, each tagged primary/secondary, with an upfront disclaimer
  that everything is recalled from ~mid-2025 internal knowledge and must be re-verified. CONFOUND:
  the v1 capture used a different model (GLM-4.6/4.7 class) WITH broken browsing (`turn0searchN`
  markers). This v2 run is GLM-5.2 with browsing OFF. So v1→v2 mixes a model change and a
  browsing change; treat the axis deltas as suggestive, not attributable to phrasing.
trust_rating: MEDIUM-HIGH (big jump from v1's 5/18). No fabricated model sizes, all repos real, honest RAM math ("~21 GB resident", "bottleneck is RAM"), explicit no-browsing disclaimer. Main limitation: not verified against the 2026 ecosystem (own admission).
---

## Raw response

Model: GLM-5.2 (Z.ai)
Knowledge cutoff: ~mid-2025
Web browsing/tools enabled for this answer: No — answering from internal knowledge. I cannot verify the state of the ecosystem on 31 August 2026; where a version or capability matters, I mark it as "needs verification" and reason from the trajectory visible at my cutoff. The M6 base chip does not exist in my training data, so Apple-Silicon numbers are extrapolated from M4/M5 behaviour.

---

## Decisions at a glance

| Layer | Pick | Backup |
|---|---|---|
| Local inference engine | **MLX-LM** (primary), llama.cpp (secondary), Ollama (UI/convenience) | vLLM-Apple (immature) |
| Primary reasoning model | **Qwen3-30B-A3B, 4-bit MLX** | DeepSeek-V3.1-Distill-Qwen-32B Q4 |
| Coding model | **Qwen2.5-Coder-14B-Instruct Q6** (or Qwen3-Coder-14B if shipped) | Qwen2.5-Coder-32B Q4 (tight on 32GB) |
| Fast/router model | **Llama-3.2-3B-Instruct Q8** | Qwen3-4B |
| Embeddings | **bge-m3** (or Qwen3-Embedding-0.6B) | nomic-embed-text-v1.5 |
| Vision (optional) | **Qwen2.5-VL-7B Q4** | Llama-3.2-Vision-11B |
| Model router / API shim | **LiteLLM** | custom Python wrapper |
| Agent graph / orchestration | **LangGraph** (state machine) + custom supervisor | AutoGen / AG2 |
| Tool layer | **MCP servers** (fs, git, shell, browser, web) | direct function-calling |
| Coding sub-agent | **Aider** (headless, `--yes-always`, worktrees) | OpenHands headless |
| Research sub-agent | **GPT-Researcher** retargeted to local LLM + STORM-style planner | custom |
| Durable memory | **SQLite (WAL) + LanceDB + Markdown daily logs** | Postgres+pgvector later |
| Background/scheduling | **launchd** + watchdog Python process | systemd-equivalent n/a on macOS |
| Sandbox / isolation | **dedicated `agent` OS user + `sandbox-exec` profiles + per-task worktree** | Docker Desktop (heavier) |
| Browser automation | **Playwright + browser-use** | Skyvern |
| Remote access | **Tailscale + Caddy + Open WebUI + Telegram bot for approvals** | Cloudflare Tunnel |
| Storage layout | internal 512GB: OS, hot models, DBs, .git · external 1TB: model archive, papers, datasets, logs, scratch | — |
| Stop/kill switch | **Telegram `/halt` → supervisor SIGTERM + sandbox revoke** | physical power button |

---

## Investigation areas

### 1. On-device inference on a 32 GB base Apple-Silicon Mac

**Engines, ranked for this exact machine.**

- **MLX-LM** (Apple, Apache-2.0). Best Metal utilisation, native unified-memory semantics (no CPU↔GPU copy), supports 4/6/8-bit quantisation in `.mlx` format, KV cache on GPU, can serve via `mlx_lm.server` (OpenAI-compatible). This is the primary engine.
- **llama.cpp** with Metal backend. More mature than MLX for edge cases (some quantisations, LoRA hot-swap, multi-model in one process), slightly behind on peak throughput. Use as the secondary engine and for models where MLX conversion lags.
- **Ollama**. Wraps llama.cpp, easy model management, decent OpenAI API. Use it for the operator-facing UI and for ad-hoc models, not for the hot path.
- **vLLM-Apple**. At my cutoff it was experimental; verify before relying on it.
- **LM Studio**. Same engine family as llama.cpp, good for interactive use, weaker for headless orchestration.

**What to actually run.** Optimise *useful work per hour*, not parameter count. MoE models are the right answer on base Apple Silicon because inference cost is paid on active parameters, not total.

1. **Qwen3-30B-A3B** (3B active, ~16 GB at 4-bit). Best quality/throughput trade on this hardware: 30B-class reasoning at 3B-class cost. Hold resident.
2. **Qwen2.5-Coder-14B-Instruct at Q6** (~11 GB). Smaller than the 32B coder, but at Q6 its edit quality on Python/TS/Rust is within a hair of the 32B at Q4, and it leaves headroom for the reasoning model. Hold resident alongside (1).
3. **Llama-3.2-3B-Instruct at Q8** (~3 GB). Always resident. Handles routing decisions, classification, summarisation, structured output. ~3-5× the throughput of (1).
4. **bge-m3** (~2 GB). Multilingual dense+sparse+ColBERT embeddings. Always resident via a small sentence-transformers/Infinity process.
5. **Optional on-demand:** Qwen2.5-VL-7B Q4 for screenshots/PDFs, DeepSeek-R1-Distill-Qwen-32B Q4 for hardest reasoning tasks. Load only when needed, unload after.

**RAM math (32 GB total).** macOS + windowserver + browsers ≈ 6 GB. Models resident: (1) 16 + (2) 11 + (3) 3 + (4) 2 = 32 GB — too much. Drop (2) to Q4 (~9 GB) and total model weight is 30 GB, still over budget with OS overhead. Practical resident set is **(1)+(3)+(4) ≈ 21 GB**, with (2) loaded on demand when a coding task is dispatched and the reasoning model flushed or kept cold. KV cache for (1) at 32k context ≈ 2-4 GB at 4-bit. **Bottleneck is RAM, not compute.**

**Concurrency.** MLX-LM server processes one request at a time per model. For 100+ logical agents (see §3) you do **not** want 100 concurrent inferences — you want a worker pool with bounded concurrency (default 2 large-model workers + 4 small-model workers) and queue depth in front.

**Models to not run:** anything ≥70B (won't fit at usable quant even with swap), anything at FP16 beyond ~14B, and any model family without an MLX or GGUF build.

**Load/unload behaviour.** MLX loads weights to unified memory in seconds; swapping models in/out is cheap enough that on-demand loading for (2)/(5) is fine. Do **not** hold the 14B coder resident all the time — let the supervisor load it for a coding sub-task and unload when the task completes.

### 2. Agent runtimes and harnesses

Surveyed at cutoff: **LangGraph**, **AutoGen/AG2**, **CrewAI**, **smolagents**, **Pydantic-AI**, **OpenAI Swarm**, **Bee Agent Framework**, **Microsoft Agent Framework**, **LlamaIndex Workflows**, **Mastra**.

Comparison axes that actually matter here: durable state, sub-agent spawning, MCP support, recovery from mid-task crash, long-running/background jobs, headless-first (not chat-first), local-model friendliness, no implicit cloud SDK.

Findings:
- **CrewAI** is pleasant but chat/role-play oriented; weaker on durable state.
- **AutoGen/AG2** is strong on multi-agent conversation but heavy on Python class hierarchies; v0.4+ is much better but still chat-shaped.
- **smolagents** is lightweight and code-first, good for tool calls, but thin on durable orchestration.
- **LangGraph** is the only one with explicit graph-state checkpointing, time travel, sub-graphs as sub-agents, and a checkpoint store you can put on SQLite/Postgres. It is verbose, but it is the right primitive for a 24/7 unattended system.

**Decision:** LangGraph as the graph/state layer, wrapped in a **custom supervisor** (≈800 lines of Python) that owns the task queue, model router, MCP tool registry, watchdog, and the kill-switch. The supervisor is the only durable process; LangGraph graphs are loaded as needed and checkpointed to SQLite.

### 3. Many-agent design on 32 GB

Critical distinction: **logical agents ≠ model processes**. 100 logical agents means 100 agent definitions + 100 task records + 100 context bundles — not 100 simultaneous inferences.

Design (coordinator/worker, hierarchical):
- **1 supervisor** (custom Python, no LLM in the hot loop except for routing decisions).
- **N specialised agent definitions** (planner, coder, reviewer, debugger, researcher, summariser, critic, librarian, …). Each definition = JSON: role, allowed tools, allowed models, system prompt, permission profile.
- **Worker pool:** 2 large-model workers (Qwen3-30B-A3B) + 4 small-model workers (Llama-3.2-3B) + 1 coder worker (Qwen2.5-Coder-14B loaded on demand). Bounded by a semaphore.
- **Task queue:** SQLite table `tasks(id, agent_def, parent, status, payload, deps, retries, started, finished)`. Workers poll; supervisor assigns.
- **Dynamic sub-agents:** supervisor can synthesise a new agent definition by prompting the small model ("you need an agent that does X with tools Y, return JSON"), validate the JSON, register it, and dispatch. No hand-configuration.
- **Execution model:** mostly sequential chains with occasional parallel fan-out (e.g. researcher spawns 3 parallel sub-queries to the small model). True parallelism is bounded by the worker pool, not by agent count.
- **Why not swarm?** Swarm topologies burn tokens on agent-to-agent chatter. On 32 GB that throughput is wasted; a coordinator/worker topology is strictly more efficient.

### 4. Autonomous coding systems

Compared: **Aider**, **OpenHands** (ex-OpenDevin), **Cline / Roo Code**, **SWE-agent**, **Continue**, **Goose** (Block), **Cursor agent** (closed), **Devin** (closed).

For this build the relevant axes: works against *any* local directory (not a hosted repo), supports Git branches and worktrees, runs shell and tests, edits files directly, self-reviews, runs headless, supports local models, and is sandboxable.

- **OpenHands** is the most capable end-to-end but heavy (Docker-default, browser-based runtime). Headless mode exists. Strong choice if you accept its runtime.
- **Aider** is the leanest: a CLI that edits files in a working tree, supports any local model via LiteLLM, has built-in Git worktree-friendly behaviour, `--yes-always` for unattended runs, and a `--subarch`/editor mode that is genuinely strong on Qwen-Coder. Excellent for the iterative edit/test loop.
- **SWE-agent** is research-oriented and assumes a containerised repo.
- **Cline/Roo Code** are editor-bound (VS Code), not headless.

**Decision: Aider as the primary coding sub-agent, called headless from the supervisor.** Pattern: supervisor creates a git worktree `~/ws/<task-id>`, runs `aider --model litellm/qwen-coder --yes-always --no-auto-commits --message-file <task.md>`, captures diff, runs tests, asks the small model to review the diff, and either commits or rolls back. OpenHands stays available as a fallback for harder repo-comprehension tasks where Aider's context window is the bottleneck.

### 5. Autonomous research systems

Compared: **GPT-Researcher** (assafelovic/gpt-researcher), **STORM** (Stanford), **OpenResearcher**, **PaperQA2**, **various "Deep Research" clones**.

Axes: web search, source/literature discovery, PDF parsing, citation extraction, evidence tracking, claim checking, contradiction detection, synthesis, report writing, and — critically — **anti-fabrication**.

**Decision: GPT-Researcher with a custom planner, retargeted to local LLMs and a local embedding index.** Plus **PaperQA2** for the academic-PDF Q&A sub-path (it is purpose-built for citation-anchored answers and refuses to answer when no source supports a claim).

Anti-fabrication design:
1. Every claim in a research report is tagged with a source span (`paper_id`, `page`, `bbox`, `char_range`).
2. A *verification pass* (separate small-model worker) re-prompts: "Given the cited span, does it support the claim? Answer SUPPORT / REFUTE / INSUFFICIENT."
3. Any INSUFFICIENT or REFUTED claim is dropped or flagged for human review.
4. The report writer is only allowed to use sentences that survived verification. Citations are emitted as `[paper_id:char_range]` and rendered as footnotes with URLs/DOIs only after a second verifier confirms the URL resolves and the paper matches the claimed title.
5. PDFs are parsed with **pymupdf4llm** or **MarkItDown** (not raw text extraction), preserving page metadata for the span anchors.

### 6. Durable memory

Compared: filesystem JSON/Markdown, SQLite, Postgres+pgvector, Chroma, Qdrant, LanceDB, Weaviate, Milvus, **mem0**, **Letta** (ex-MemGPT), **Zep/Graphiti**, knowledge graphs (Neo4j, Memgraph).

Decision tree: what does a personal 24/7 lab actually need *today*? Append-only event log + structured project state + semantic recall. A graph DB or a managed memory service is premature.

**Start with (phase 4):**
- **SQLite (WAL mode)** as the canonical store. Tables: `projects`, `tasks`, `messages`, `decisions`, `findings`, `experiments`, `artifacts`, `episodes`.
- **LanceDB** for vector search over Markdown/SQLite-row embeddings. LanceDB is embedded (no server), uses Arrow format, and is fast on Apple Silicon. Replaces Chroma/Qdrant for this scale.
- **Filesystem Markdown** for human-readable artefacts: `~/agent/runs/YYYY-MM-DD.md`, `~/agent/projects/<slug>/notes/`, `~/agent/projects/<slug>/decisions/ADR-NNNN-*.md`.
- **Embedding strategy:** bge-m3 dense vectors for semantic recall; no knowledge graph yet.

**Add later (only when a real need appears):** Graphiti for causal/ temporal links (when contradiction detection needs it), or pgvector if migrating to Postgres for other reasons.

### 7. Machine control and isolation

Layers of defence, from outermost to innermost:

1. **Dedicated macOS user `agent`** (Standard, not Admin). The supervisor runs as this user. `sudo` is configured to require a password for *everything*, including `sudo -l`.
2. **`sandbox-exec` profiles** (macOS seatbelt). Each agent role gets a profile: e.g. `coder.sb` allows write to `~/ws/**`, read to `~/repos/**`, deny `~/Documents`, `~/Library/Keychains`, `~/.ssh`, deny network except allowlist. `sandbox-exec -f coder.sb -- <cmd>`.
3. **Per-task Git worktree** under `~/ws/<task-id>/`. Worktree is removed after task merge or kept for audit.
4. **Tool allowlists via MCP.** Each MCP server (fs, git, shell, browser, web) enforces its own allowlist. The shell MCP refuses commands matching a deny regex (`rm -rf /`, `sudo`, `dd`, `mkfs`, `:(){:|:&};:`, `curl|sh`, etc.).
5. **Credential isolation.** Secrets live in a `~/agent/secrets/` directory with mode 0700, *not* in env vars. MCP tools read them on demand and never log values. The agent user has no access to the operator's Keychain.
6. **Network isolation.** Outbound traffic from the `agent` user is filtered by a `pf` rule set allowing only: Tailscale interface, DNS, HTTP/HTTPS to a research allowlist (arxiv.org, semanticscholar.org, github.com, doi.org, crossref.org, duckduckgo.com, google.com search). Everything else dropped.
7. **Destructive-command policy.** Any command that would `git push --force`, `rm -rf` outside a worktree, send email, post to a public site, or touch a remote API with side effects requires Telegram approval.
8. **Emergency kill switch.** Telegram `/halt` → supervisor sets `halted=1` in SQLite, sends SIGTERM to all workers, revokes sandbox profiles by chmod-ing them 000, and parks itself in a poll-only loop until `/resume`.

### 8. Running 24/7 on macOS

- **launchd plist** `~/Library/LaunchAgents/ai.z.agent.supervisor.plist` with `RunAtLoad=true`, `KeepAlive=true`, `ThrottleInterval=30`, `StandardOutPath`/`StandardErrorPath` to `~/agent/logs/`.
- **Auto-restart on crash:** `KeepAlive` handles it; `ThrottleInterval` prevents a tight crash loop.
- **Watchdog:** separate launchd job `ai.z.agent.watchdog.plist` running every 60 s. Checks (a) supervisor PID alive, (b) heartbeat row in SQLite updated within last 5 min, (c) MLX server alive. If any fails: kill -9, restart, page via Telegram.
- **Sleep prevention:** `caffeinate -dimsu` spawned by the supervisor, plus System Settings → Energy → "Prevent automatic sleeping when the display is off" and "Wake for network access".
- **Task persistence:** all in-flight tasks are checkpointed to SQLite *before* execution; on restart the supervisor re-reads the queue and resumes from the last checkpoint.
- **Logging:** structured JSON lines to `~/agent/logs/supervisor.jsonl`, rotated by `newsyslog`. Telegram digest every 6 hours.
- **Network hardening:** Tailscale only — no port forwarding, no public IP exposure, MagicDNS for naming, Tailscale ACLs restrict which devices can reach the Mac.
- **Crash recovery semantics:** idempotent task steps. Every step is wrapped in a transaction: `BEGIN; UPDATE tasks SET status='running'; <do work>; UPDATE tasks SET status='done', result=...; COMMIT;`. A crash mid-step leaves the row in `running`; on restart the supervisor re-runs it (work must be made idempotent — re-applying a patch, re-running a test, etc.).

### 9. Remote reach

- **Tailscale** on the Mac and on the phone/laptop. The Mac is reachable only from the tailnet.
- **SSH** on the tailnet for emergency shell. Key-only, no password.
- **Caddy** (on the Mac, listening on the tailnet IP only) reverse-proxies:
  - `https://agent.<tailnet>/` → Open WebUI (chat/status/queue)
  - `https://agent.<tailnet>/api/` → supervisor REST (submit task, list queue, get logs, approve/deny pending actions)
  - `https://agent.<tailnet>/files/` → static file browser for artefacts
- **Open WebUI** as the primary dashboard. Tags: pending approvals, current task, last 20 messages, recent diffs.
- **Telegram bot** as the *approval and alert* channel — not the primary interface. Sends: task started/finished, test failures, approvals needed, errors, 6-hourly digest. Accepts: `/halt`, `/resume`, `/approve <id>`, `/reject <id>`, `/status`, `/queue`.
- **Emergency stop:** Telegram `/halt`, or a physical "kill" button on the desk wired to `pmset sleepnow` via a Shortcut, or pulling the network — supervisor times out heartbeats and parks.
- **Auth:** Tailscale device identity (WireGuard keys) is the primary auth. Caddy adds a session cookie over Open WebUI for the web UI. Telegram uses a shared secret rotated monthly.

### 10. Storage split

| Item | Location | Why |
|---|---|---|
| macOS + apps + swap | internal 512GB | OS must be on internal; swap is fastest on internal NVMe |
| Hot models (`qwen3-30b-a3b-4bit.mlx`, `llama-3.2-3b-q8.mlx`, `bge-m3`) | internal `~/.cache/huggingface` | latency matters every model load |
| Model archive (on-demand models, vision, distills) | external 1TB `~/models/` | large, cold, streamed in on demand |
| SQLite DB + LanceDB | internal `~/agent/db/` | every supervisor tick reads/writes; must be fast |
| Git repos (mirrors of operator's projects) | internal `~/repos/` | frequent reads/writes, branch switching |
| Per-task worktrees | internal `~/ws/` | bursty I/O, small |
| Paper PDFs | external `~/papers/` | large, mostly cold, occasionally re-read |
| Datasets | external `~/datasets/` | large, cold |
| Logs | external `~/logs/` | append-mostly, large over time |
| Scratch / agent experiments | external `~/scratch/` | throwaway, large |
| Backups (Time Machine + restic snapshots of `~/agent/db/` and repos) | external (separate volume) | durability |

External SSD expected throughput on M6's Thunderbolt 5 controller: well above the ~600 MB/s needed for paper/dataset streaming. Internal NVMe is reserved for hot paths. **Durability caveat:** external SSDs fail more often than internal; the DB and active repos stay on internal and are snapshotted to external via `restic` every hour.

---

## Deliverables

### A. Technology stack

| Layer | Chosen technology | Alternatives considered | Rationale |
|---|---|---|---|
| Inference engine | MLX-LM | llama.cpp, Ollama, vLLM-Apple | Native unified-memory path; best Metal perf at this size |
| Reasoning model | Qwen3-30B-A3B (4-bit MLX) | DeepSeek-V3.1-distill-32B Q4, Llama-4-Scout | MoE: 30B quality at 3B active cost |
| Coding model | Qwen2.5-Coder-14B Q6 (load on demand) | Qwen2.5-Coder-32B Q4, DeepSeek-Coder-V2-Lite | 14B-Q6 quality ≈ 32B-Q4 on edits, half the RAM |
| Fast/router model | Llama-3.2-3B Q8 | Qwen3-4B, Phi-4-mini | Tiny, fast, sufficient for routing/classification |
| Embeddings | bge-m3 | nomic-embed-v1.5, Qwen3-Embedding | Multilingual, dense+sparse+ColBERT in one |
| Vision (optional) | Qwen2.5-VL-7B Q4 | Llama-3.2-Vision-11B | Only loaded when screenshots/PDFs need it |
| Model router | LiteLLM | custom Python shim, OpenRouter | OpenAI-compatible façade, easy per-task routing |
| Orchestration | LangGraph + custom supervisor | AutoGen/AG2, CrewAI, smolagents | Graph checkpointing + durable state |
| Coding sub-agent | Aider (headless) | OpenHands, SWE-agent, Cline | Leanest, worktree-friendly, local-model first |
| Research sub-agent | GPT-Researcher (retargeted) + PaperQA2 | STORM, OpenResearcher | Anti-fabrication via verifier pass |
| Memory | SQLite (WAL) + LanceDB + Markdown logs | Postgres+pgvector, Chroma, Letta, Zep | Embedded, no server, sufficient at this scale |
| Tools | MCP servers (fs, git, shell, browser, web) | direct function-calling | Standardised, allowlisted, swappable |
| Browser | Playwright + browser-use | Selenium, Skyvern | Headless-first, robust, MCP-friendly |
| PDF parsing | pymupdf4llm + MarkItDown | PyPDF2, unstructured | Preserves page/position anchors for citations |
| Sandbox | macOS `sandbox-exec` + dedicated `agent` user + worktrees | Docker Desktop, UTM VM, Lima | Lightest viable isolation on base M-series |
| Scheduling | launchd (LaunchAgent) | cron, systemd (n/a), pm2 | Native, robust, crash-recovery built in |
| Remote access | Tailscale + Caddy + Open WebUI + Telegram bot | Cloudflare Tunnel, ngrok, Tailscale Funnel | No public exposure; tailnet-only |
| Notifications/approvals | Telegram bot | Slack, Matrix, ntfy | Phone-native, no extra infra, works on cellular |
| Backups | restic → external SSD + Time Machine | Borg, Duplicacy | restic is fast, dedup-friendly, free |

### B. Architecture diagram

```
                       ┌─────────────────────────────────────┐
                       │  Operator phone/laptop (tailnet)   │
                       │  Open WebUI · SSH · Telegram       │
                       └──────────────────┬────────────────┘
                                          │ Tailscale (WireGuard)
                                          ▼
                       ┌─────────────────────────────────────┐
                       │  Caddy  (TLS, tailnet-only :443)     │
                       │  /  → Open WebUI   /api → supervisor │
                       └──────────────────┬────────────────┘
                                          ▼
   ┌──────────────────────────────────────────────────────────────────┐
   │  Supervisor (Python, launchd KeepAlive, dedicated `agent` user)   │
   │  Task queue (SQLite) · Watchdog · Model router (LiteLLM) · Approvals│
   │  LangGraph graphs: plan / code / debug / research / review / synth │
   │  Worker pool (semaphores): 2× large (Qwen3-30B-A3B 4bit) ·         │
   │    4× small (Llama-3.2-3B Q8) · 1× coder (Qwen2.5-Coder-14B Q6) ·  │
   │    1× embed (bge-m3)                                               │
   └──────────────────────────────────────────────────────────────────┘
        │                              │
        ▼                              ▼
   MLX-LM servers (:8000 reasoning, :8001 small, :8002 coder on-demand,
   :8003 embed)          MCP tool servers (fs · git · shell · browser ·
                          web · papers · sandbox)
                                       │
                                       ▼
   macOS sandbox-exec · dedicated `agent` user · worktrees ~/ws/<task-id>/
                                       │
                                       ▼
   Durable memory: SQLite (WAL) ~/agent/db/ · LanceDB ~/agent/vec/ ·
   Markdown logs ~/agent/runs/
                                       │
                                       ▼
   Storage: internal 512GB (OS, hot models, DB, repos, ws) ·
   external 1TB (archive, papers, datasets, logs, scratch, backups)
```

### C. Resource plan

**RAM (32 GB unified, target steady state ~26 GB used, ~6 GB headroom):**

| Component | RAM |
|---|---|
| macOS + windowserver + spotlight | 4.0 GB |
| Tailscale + Caddy + Open WebUI | 0.3 GB |
| Supervisor + LangGraph + Python | 0.5 GB |
| SQLite + LanceDB (cached pages) | 1.0 GB |
| Telegram bot + watchdog | 0.2 GB |
| MLX Qwen3-30B-A3B 4-bit (weights) | 16.0 GB |
| MLX Llama-3.2-3B Q8 (weights) | 3.0 GB |
| MLX bge-m3 (weights) | 2.0 GB |
| KV cache, large model (32k ctx, 4-bit) | ~3.0 GB |
| KV cache, small model | 0.5 GB |
| Browser (Playwright, when active) | 1.5 GB |
| **Total** | **~32 GB** → tight; supervisor triggers model unload of coder/vision as needed |

When the on-demand coder is loaded (+9 GB at Q4), the supervisor **unloads the reasoning model** for the duration, runs the coder against a queued batch of coding tasks, then swaps back. Net effect: 100-150 s of model-swap overhead per swap, amortised over many tasks.

**Storage:** internal usage ≈ 130 GB of 512 GB (macOS+apps ~50, hot models ~35, DB ~5, repos ~30, ws ~10). External usage ≈ 680 GB of 1 TB (model archive ~200, logs ~50, papers ~80, datasets ~150, scratch ~200) + a separate ~200 GB restic backup volume. Comfortable.

### D. Agent model — running 100+ logical agents without 100 processes

**Logical agent = a row in `agents` table** (`id, role, tools, models, permissions, system_prompt, parent_task, context_bundle`). Physical existence = a Python coroutine holding that row plus a worker semaphore slot. Runtime invariant: at most `N=7` simultaneous model inferences (2 large + 4 small + 1 coder). 100+ logical agents are parked in the queue or blocked on dependencies. Hierarchical topology: Supervisor (no LLM except routing) → Specialists (planner, coder, reviewer, debugger, researcher, summariser, librarian, critic) → Dynamic sub-agents (bounded token budget, restricted tool subset) → Tool calls (MCP). Parked agents cost ~10 KB each in SQLite; worker slots are the only RAM consumer. Dynamic agent creation: small model emits a JSON agent definition; supervisor validates schema, normalises permissions (never expanding beyond the parent's), registers, dispatches.

### E. Model assignment

| Task | Model | Quant |
|---|---|---|
| Planning (decompose objective → tasks) | Qwen3-30B-A3B | 4-bit |
| Coding (edit/test/debug) | Qwen2.5-Coder-14B | Q6 |
| Debugging | Qwen2.5-Coder-14B | Q6 |
| Research (query, extract, verify) | Qwen3-30B-A3B | 4-bit |
| Summarisation | Llama-3.2-3B | Q8 |
| Classification / routing / structured output | Llama-3.2-3B | Q8 |
| Final synthesis (long-form report) | Qwen3-30B-A3B | 4-bit |
| Embedding / retrieval | bge-m3 | FP16 |
| Hard reasoning (rare) | DeepSeek-R1-Distill-Qwen-32B Q4 (on demand) | 4-bit |
| Vision | Qwen2.5-VL-7B | Q4 |

### F. Continuous-operation design

Overnight loop (pseudo): `t = queue.pop_next_ready(); if None: sleep 60s; checkpoint(t,'running'); try: result = run_agent(t.agent_def, sandbox=profile_for(t)); checkpoint(t,'done'); maybe queue follow-ups; except HaltSignal: checkpoint(t,'interrupted'); park(); except Exception: t.retries+=1; retry(<3) else fail+telegram_alert`.

Failure recovery: supervisor crash → launchd `KeepAlive` restarts in 30 s → watchdog verifies heartbeat → queue resumes from `running` rows (idempotent re-run). MLX crash → watchdog restarts, one retry. Reboot → launchd starts supervisor on login (auto-login on `agent`, screen locked) → queue resumes. Power loss → SQLite WAL guarantees no committed task lost; in-flight re-runs. Bad model output → caught, `t.retries++`, escalate to a different model on next try.

Stop conditions: max retries (3), max wall-clock per task (30 min default), max tokens per task (200k), daily token budget, operator `/halt`, `objective_met` flag.

### G. Remote-operation design

From a phone on cellular: receives Telegram "Task T-1042 needs approval to `git push --force`" → replies `/approve T-1042` → supervisor proceeds. For deeper interaction: Open WebUI at `https://agent.<tailnet>/` shows graph state, queue, recent diffs, recent tool calls; can submit a new task in plain text. Emergency stop chain: Telegram `/halt` → supervisor halts → sandbox profiles chmod 000 → MLX servers killed → banner in Open WebUI. `/resume` reverses.

### H. Security design

Threat model: confused-deputy agent, prompt injection from a fetched web page / malicious dependency, model hallucinating a destructive command, LAN attacker, tailnet compromise.

Permissions — **unattended, no sign-off:** read under `~/repos/` and `~/papers/`; write under `~/ws/<task-id>/`; run tests; `git commit` on a worktree branch; web search via allowlist; read arxiv/semanticscholar; pip-install into a per-task venv. **Unattended within sandbox, sign-off on commit to `main`:** `git checkout main`, `git merge`, `git push`. **Always requires Telegram sign-off:** `git push --force`, push to a non-origin remote, `rm -rf` outside `~/ws/`, sending email, posting to public sites, any side-effecting API (payments/deployments/social), installing system packages, editing `~/repos/**` outside a worktree, egress to a non-allowlisted host, deny-regex matches. **Never allowed:** reading `~/Documents`, `~/Desktop`, `~/Downloads`, `~/Pictures`, `~/Library/Keychains`, `~/.ssh`, `~/.aws`, `~/.config/gh`, the operator's Keychain/mail/messages/photos — enforced by `sandbox-exec` + the `agent` user's filesystem permissions.

Audit: every tool call → `~/logs/audit.jsonl` (timestamp, agent_id, tool, args redacted, return code, duration), hash-chained daily (SHA-256). Resource limits: per-task token/wall-clock budgets, daily token budget, MLX concurrency caps, SQLite write-rate cap. Runaway protection: >100 tool calls in 5 min, or >3 retries in 10 min, or token spend >2× daily rolling average → park + Telegram page.

### I. Installation procedure

```bash
# 0. As the operator (admin) — create the agent user
sudo sysadminctl -addUser agent -fullName "Agent User" -password - -admin no
sudo dseditgroup -o edit -a agent -t user staff
# 1. Switch to the agent user (auto-login set in System Settings)
sudo su - agent
# 2. Install Homebrew (agent-scoped)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
# 3. Dependencies
brew install python@3.12 node git sqlite restic caddy tailscale telegram-cli
brew install --cask playwright
# 4. Python tooling
python3.12 -m venv ~/agent/venv && source ~/agent/venv/bin/activate
pip install mlx mlx-lm llama-cpp-python litellm langgraph lancedb sentence-transformers \
            pymupdf4llm open-webui playwright browser-use aider gpt-researcher paper-qa telebot pydantic
# 5. Models (internal)
huggingface-cli download Qwen/Qwen3-30B-A3B-Instruct-4bit
huggingface-cli download meta-llama/Llama-3.2-3B-Instruct
huggingface-cli download Qwen/Qwen2.5-Coder-14B-Instruct
huggingface-cli download BAAI/bge-m3
# 6. Layout
mkdir -p ~/agent/{db,vec,runs,logs,secrets,configs} ~/repos ~/ws ~/models ~/papers ~/datasets ~/scratch
# 7. External SSD symlinks (assume /Volumes/ExtSSD)
ln -s /Volumes/ExtSSD/{models,papers,datasets,logs,scratch} ~/
# 8. Tailscale
tailscale up --ssh --accept-routes
# 9. Supervisor
cd ~/agent && git clone <your-supervisor-repo> src && cd src && pip install -e .
# 10-12. launchd plists for mlx-large (:8000), mlx-small (:8001), mlx-embed (:8003),
#        supervisor, watchdog — RunAtLoad, KeepAlive, ThrottleInterval 30.
#        (:8002 coder is on-demand, not launchd.)
launchctl load ~/Library/LaunchAgents/ai.z.agent.*.plist
# 13. Caddy (bind tailscale0, tls internal): / → Open WebUI :8080, /api/* → supervisor :9000
brew services start caddy
# 14. Telegram bot token → ~/agent/secrets/telegram.env  (chmod 600)
# 15. Smoke test
curl http://127.0.0.1:8000/v1/chat/completions -H 'Content-Type: application/json' \
  -d '{"model":"qwen3-30b","messages":[{"role":"user","content":"ping"}]}'
```

**How components talk:** LiteLLM → `http://127.0.0.1:800X/v1/`. Supervisor ↔ MCP over stdio / local HTTP. Telegram bot → Telegram over HTTPS (outbound only). Open WebUI → LiteLLM only. Caddy fronts everything on the tailnet interface.

**Test:** `python -m agent.tests.smoke` — load each model, route "hello" through LiteLLM, dispatch a trivial coding task (write + run a Python one-liner in a worktree, check stdout), run a trivial research task (search arxiv for one paper, parse abstract, return one cited sentence), assert one audit-log entry per tool call.

**Failure modes & rollback:** MLX OOM → unload coder/vision, then drop large concurrency to 1. Sandboxed hang → watchdog kills after 5 min/step. Telegram outage → approvals queue locally, shown in Open WebUI. SQLite lock contention → WAL (already), `busy_timeout` 5000 ms. Poisoned queue → each task has `parent`/`retries`; failed parent re-plans with a different model. Rollback: each phase has a `teardown.sh` (`launchctl unload` + drop its tables).

### J. Exclusion list

Docker Desktop (heavy RAM; `sandbox-exec` + worktrees suffice) · Kubernetes/k3s (overkill) · Postgres+pgvector (premature; SQLite+LanceDB handle millions of rows) · Neo4j/Memgraph (KG not needed yet) · LangChain umbrella lib (too much surface; LangGraph alone) · CrewAI (chat-oriented) · OpenAI Assistants / Anthropic Agents API (breaks local-first) · vLLM (Apple-Silicon support immature) · LlamaIndex full framework (heavy) · Ray (overkill for one host) · Zep/Graphiti/Letta (memory services not needed yet) · Cursor/Devin/Windsurf (closed, can't run unattended on local models) · Slack/Discord as approval channel (Telegram is simpler) · ngrok/Cloudflare Tunnel (opens a public path) · Time Machine as the only backup (restic added) · LM Studio as the headless engine · anything ≥70B · multiple model servers when not needed.

### K. Scaling path

**64 GB:** coder model resident always (no swap); second large-model worker (2× large throughput); vision model resident; KV cache to 64k context; Postgres worth considering. **96 GB:** add DeepSeek-R1-Distill-Qwen-32B Q4 resident for hard reasoning; 3 large + 1 reasoning worker; LanceDB 10M+ vectors. **128 GB:** 70B-class model at Q4 (Llama-4-Maverick, Qwen3-72B) resident; switch to Postgres+pgvector if the memory graph grows. **Pro/Max chip:** wider bandwidth → 1.5-2× throughput at same RAM; same stack. **Added discrete GPU (Linux + RTX 5090):** heaviest model there via vLLM, exposed through LiteLLM over Tailscale; Mac becomes orchestrator + small-model host. **Multiple Macs:** Tailscale mesh, one supervisor, distributed workers, SQLite → Postgres on the primary. **Cloud burst (optional, paid):** for one-off hard tasks (e.g. 200k-context repo comprehension), LiteLLM routes to Anthropic/OpenAI/DeepSeek API with a per-task token cap. Default off; enabled per task by the planner with operator sign-off.

---

## Sources

Marking each as **primary** (vendor/repo/benchmark from the originator) or **secondary** (overview, blog, comparison). All recalled from internal knowledge at ~mid-2025; URLs and current versions should be re-verified before this RFC is built.

- MLX and MLX-LM — https://github.com/ml-explore/mlx-lm — **primary**
- Apple Silicon unified memory architecture — https://developer.apple.com/metal/ — **primary**
- llama.cpp Metal backend — https://github.com/ggerganov/llama.cpp — **primary**
- Ollama — https://ollama.com — **primary**
- LiteLLM — https://github.com/BerriAI/litellm — **primary**
- LangGraph — https://github.com/langchain-ai/langgraph — **primary**
- AutoGen / AG2 — https://github.com/microsoft/autogen — **primary**
- CrewAI — https://github.com/crewAIInc/crewAI — **primary**
- Aider — https://github.com/Aider-AI/aider — **primary**
- OpenHands — https://github.com/All-Hands-AI/OpenHands — **primary**
- SWE-agent — https://github.com/SWE-agent/SWE-agent — **primary**
- Goose (Block) — https://github.com/block/goose — **primary**
- GPT-Researcher — https://github.com/assafelovic/gpt-researcher — **primary**
- STORM (Stanford) — https://github.com/stanford-oval/storm — **primary**
- PaperQA2 — https://github.com/Future-House/paper-qa — **primary**
- bge-m3 — https://huggingface.co/BAAI/bge-m3 — **primary**
- Qwen3 model family — https://github.com/QwenLM/Qwen3 — **primary**
- Qwen2.5-Coder — https://github.com/QwenLM/Qwen2.5-Coder — **primary**
- Llama 3.2 — https://github.com/meta-llama/llama-models — **primary**
- DeepSeek-R1 distills — https://github.com/deepseek-ai/DeepSeek-R1 — **primary**
- LanceDB — https://github.com/lancedb/lancedb — **primary**
- Chroma — https://github.com/chroma-core/chroma — **primary**
- Qdrant — https://github.com/qdrant/qdrant — **primary**
- mem0 — https://github.com/mem0ai/mem0 — **primary**
- Letta (MemGPT) — https://github.com/letta-ai/letta — **primary**
- Zep / Graphiti — https://github.com/getzep/graphiti — **primary**
- Model Context Protocol (MCP) — https://modelcontextprotocol.io — **primary**
- Playwright — https://github.com/microsoft/playwright — **primary**
- browser-use — https://github.com/browser-use/browser-use — **primary**
- Skyvern — https://github.com/Skyvern-AI/skyvern — **primary**
- pymupdf4llm — https://github.com/pymupdf/PyMuPDF — **primary**
- MarkItDown — https://github.com/microsoft/markitdown — **primary**
- Open WebUI — https://github.com/open-webui/open-webui — **primary**
- Caddy — https://caddyserver.com — **primary**
- Tailscale — https://tailscale.com — **primary**
- restic — https://restic.net — **primary**
- Apple launchd man page — https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html — **primary**
- Apple `sandbox-exec` reference — https://developer.apple.com/library/archive/documentation/Security/Conceptual/AppSandboxDesignGuide/ — **primary**
- SQLite WAL — https://www.sqlite.org/wal.html — **primary**
- HumanEval / MBPP / SWE-bench — https://github.com/princeton-nlp/SWE-bench — **primary** (used to justify coding-model choice)
- Qwen2.5-Coder technical report — https://arxiv.org/abs/2409.12186 — **primary**
- Apple Silicon inference benchmarks (various) — https://github.com/ggerganov/llama.cpp/discussions — **secondary**
- "Local LLM agent stacks 2025" overviews — various blog posts — **secondary**

*End of response. prompt_version: v2.*

## Model's own cited sources

~45-entry list, each tagged primary/secondary, **all real canonical URLs** (github.com repos,
huggingface model cards, official docs, one arXiv ID `2409.12186` for the Qwen2.5-Coder report).
Upfront disclaimer: "All recalled from internal knowledge at ~mid-2025; URLs and current versions
should be re-verified before this RFC is built." This is a *reference list of where to look*, not
evidence retrieved for this answer (browsing was off) — but every URL is a genuine project home,
unlike v1's `turn0searchN` markers.

## Reviewer notes

### Purpose: RQ6 — z.ai v1 vs v2

Compare to `data/responses/z-ai.md` (v1). Tracker: `analysis/rq6-prompt-sensitivity.md`.

### CONFOUND: model + browsing both changed

v1 = a GLM-4.6/4.7-class model with **broken browsing** (`turn0searchN` markers, no resolvable
URLs), which produced the corpus's lowest-scoring response (adjudicated 5/18): a load-bearing
model-size error (`Qwen3-Coder-Next 8B` vs real 80B), 5-vs-14 GB self-contradiction, relies on
swap, no M6 facts. v2 = **GLM-5.2** with **browsing OFF** (honest self-declaration). Two variables
changed at once; the v1→v2 delta is not attributable to the RFC phrasing.

### v2 is a dramatically better response than v1 (n/a to RQ6, but notable)

- No fabricated model sizes. Explicit RAM math: `(1)+(3)+(4) ≈ 21 GB resident`, `bottleneck is
  RAM, not compute`, coder loaded on demand with the reasoning model flushed.
- Every named tool/model real: MLX-LM, llama.cpp, Ollama, LiteLLM, LangGraph, Aider, GPT-Researcher,
  PaperQA2, bge-m3, MCP, Playwright, browser-use, pymupdf4llm, MarkItDown, Open WebUI, Caddy,
  Tailscale, restic, `sandbox-exec`.
- No internal contradiction. `sandbox-exec` + dedicated user + `pf` egress allowlist + hash-chained
  audit log — a coherent, detailed security model.
- Honest limitation: "M6 base chip does not exist in my training data; Apple-Silicon numbers
  extrapolated from M4/M5." No invented 170 GB/s figure.
- ~45 real reference URLs (vs v1's 0 usable).

### Load-bearing axes vs v1

| axis | v1 (GLM-4.x, broken browse) | v2 (GLM-5.2, no browse, RFC framing) |
|---|---|---|
| inference engine | vLLM-MLX #1 (invented tok/s) | **MLX-LM #1** (llama.cpp 2nd, Ollama UI-only) |
| primary model | "Qwen3-Coder-Next 8B" (**wrong size**) | **Qwen3-30B-A3B 4-bit** (real, MoE rationale) |
| coding model | Devstral Small 2 / §3 contradiction | Qwen2.5-Coder-14B Q6, load-on-demand |
| orchestration | custom asyncio + Redis + FastAPI + MCP | **LangGraph + custom supervisor** |
| task queue | Redis (persistent) | **SQLite WAL** |
| vector store | ChromaDB | **LanceDB** |
| sandbox | dedicated user + `sandbox-exec` + Keychain | dedicated user + `sandbox-exec` profiles + `pf` egress allowlist (same family, more detail) |
| remote | Tailscale + Caddy + FastAPI | Tailscale + Caddy + **Open WebUI + Telegram** |
| M6 facts | none | none, **but honestly flagged** as extrapolated |
| sources | 0 usable (`turn0searchN`) | ~45 real canonical URLs |
| internal contradictions | 3 (5-vs-14 GB, model, concurrency) | none found |

### RQ6 signal — confounded, use with care

The improvement is almost certainly the **model upgrade** (GLM-4.x → GLM-5.2), not the RFC
phrasing. What v2 does show: even with browsing OFF, GLM-5.2 produces a consensus-aligned,
internally consistent, honestly-hedged architecture with a real reference list. The clean
phrasing comparison for z.ai is **v2 vs v3** (both GLM-5.2, both no-browse).
