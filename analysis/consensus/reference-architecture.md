# Reference architecture

The merged design: every layer is either the **cross-model consensus** (with the /10 count) or an
**`[adjudicated]`** call resolving a split (reasoning in `disagreements.md`). This is the paper's
synthesis section and the build brief for the real system.

Target: Apple M6 Mac mini · 32 GB unified · ~170 GB/s · 512 GB internal + 1 TB external SSD ·
always-on · primarily local.

---

## 1. The stack

| Layer | Choice | Basis |
|---|---|---|
| **Inference engine** | `mlx-lm` server, fronted by **`llama-swap`** (request models by alias, TTL-unload idle) | MLX family `[consensus 10/10]`; server + swap layer `[adjudicated]` — Ollama-MLX is the acceptable simpler substitute |
| **Heavy model** (1 resident) | **Qwen3-Coder-30B-A3B** 4-bit MLX (MoE, ~3B active) — or **Qwen3.6-35B-A3B** 4-bit if it benchmarks better on the unit | `[adjudicated]` — plurality real pick (4/10); "~30–35B Qwen MoE" class `[consensus 7/10]` |
| **Small model** (1 resident) | **Qwen3-4B** (or 7–9B) 4-bit — routing, classification, extraction, summaries, cheap verification | `[consensus 10/10]` |
| **Coding fallback** | **Devstral Small 2 24B** 4-bit — kept tested, swapped in if the MoE stalls | named by 4+ |
| **Cloud burst** (optional, off by default) | one frontier API behind the router, `$/day` capped, `privacy_class`-gated | local-first + optional cloud `[consensus 7/10]` |
| **Orchestrator** | **thin custom Python supervisor** (asyncio) — owns queue, scheduler, resource governor, permissions, remote control | `[consensus 10/10]` "no single harness fits" |
| **Durable sub-graphs** | **LangGraph** *inside* the supervisor for the branchy research + coding flows only (not the outer loop) | `[adjudicated]` — plurality (5/10); `gpt-5`'s "framework ≠ operating system" argument |
| **Coding — autonomous** | **OpenHands** in a container sandbox (long-horizon unattended, worktree per task) | `[consensus 8/10]` |
| **Coding — interactive** | **Aider** (git-native, every change committed, transparent) | `[consensus 8/10]` |
| **Tool protocol** | **MCP** for filesystem / terminal / git / browser / research / documents | `[consensus]` |
| **Browser** | **Playwright** (headless, deterministic); GUI/computer-use only as a sandboxed last resort | `[consensus 10/10]` — "API > DOM > browser automation > GUI vision" |
| **Task queue** | **SQLite** (WAL), durable states `queued│leased│running│blocked│done│failed`, lease-timeout requeue | `[consensus 8/10]` — Redis only when multi-machine |
| **Model router** | **~80-line rule table**: task class + context size + budget + offline? → tier | `[consensus 10/10]`; LiteLLM optional if/when cloud is enabled |
| **Memory — base** | **filesystem Markdown** (`AGENTS.md`, `MEMORY.md`, per-project notes) + **SQLite** (tasks, decisions, runs, evidence, audit) + **FTS5** | `[consensus 10/10]` |
| **Memory — semantic** | **`sqlite-vec`** in the same DB file — added *only after* FTS5 retrieval starts missing things | `[adjudicated]` — plurality (5–6/10); Chroma acceptable if already known |
| **Memory — later** | **Graphiti** (temporal / "facts supersede each other") or Cognee/Mem0 — only on proven multi-hop / cross-project need | `[consensus 10/10]`; **no Neo4j / graph DB on day 1** `[consensus 10/10]` |
| **Research pipeline** | fixed stages: plan → discover (SearXNG **or** a managed API + OpenAlex/Semantic Scholar/arXiv/Crossref) → acquire (PyMuPDF; Marker/GROBID for structure) → extract `(claim, source, snippet, offsets)` → **independent verify** → **contradiction pass** → synthesize **from the verified-claims table only** → resolve DOIs | `[consensus 10/10]` |
| **Sandbox — base** | **dedicated non-admin macOS user** (`agent`) + workspace jail on the external SSD (symlink-resolved `startswith(allowed_root)`) | `[consensus 10/10]` |
| **Sandbox — per task** | **Colima** or **Apple `container`** (macOS 26) for OpenHands + untrusted code; **`sandbox-exec`** for one-off tool calls; default-deny egress + allowlist | `[adjudicated]` — avoids Docker Desktop; matches the anchor |
| **Secrets** | **macOS Keychain** (your account) + a broker that issues short-lived scoped tokens; **never** in the agent's filesystem/context/env | `[consensus 10/10]` |
| **Permissions** | explicit **autonomous / approval-required / never** tiers + destructive-command blocklist + **append-only audit log** (every tool call, model call, approval) | `[consensus 10/10]` |
| **Always-on** | **`launchd`** LaunchDaemon (`RunAtLoad` + `KeepAlive` + `ThrottleInterval`) for the supervisor + a **separate watchdog** LaunchDaemon (health-check → `kickstart -k`) | `[consensus 10/10]` |
| **Sleep** | **`caffeinate -dimsu`** wrapper + `pmset -a sleep 0 disablesleep 1` (desktop) | `[consensus 10/10]` |
| **Crash recovery** | durable SQLite queue survives reboot; startup sweep requeues expired-lease tasks; steps checkpoint to the task row so they **resume, not restart**; `launchd` restarts services | `[consensus 10/10]` |
| **Remote network** | **Tailscale** tailnet (WireGuard, no inbound ports); Tailscale SSH; ACLs limit the phone to the dashboard port + SSH | `[consensus 10/10]` |
| **Remote control plane** | small **FastAPI** service bound to the **tailnet IP only**, bearer-token auth: `POST /tasks`, `GET /queue`, `GET /runs/{id}/logs` (SSE), `POST /approvals/{id}`, `POST /stop`, `GET /status` + a mobile-first HTML dashboard | `[consensus 10/10]` |
| **Notifications** | **ntfy** (self-host or random topic) — approval-needed, done, budget-hit, crash; action buttons hit `/approvals/{id}` over the tailnet | `[consensus 10/10]` |
| **Monitoring** | structured JSONL logs + `/system/health` + ntfy alerts (Phase 1–7); **Grafana/Prometheus is a Phase-8 option**, not day 1 | `[adjudicated]` — 8/10 minimal |
| **Backups** | **restic** → external SSD + an offsite target (B2/S3, encrypted): memory, DBs, config, code. **Not** models (re-downloadable) | `[consensus]` |

---

## 2. Layered diagram

```text
Phone / Laptop
   │   Tailscale tailnet — WireGuard, no public ports
   ▼
FastAPI control plane (tailnet IP only) + HTML dashboard + ntfy push
   │        launchd KeepAlive │ separate watchdog (health → kickstart -k)
   ▼
Always-on Supervisor (thin custom Python / asyncio)
   loop: PAUSE? → sweep expired leases → schedule → observe → requeue/escalate
   owns: permissions · resource governor (RAM / tokens / $ / wall-clock) · audit log
   ▼
Task Queue (SQLite WAL)   states: queued│leased│running│blocked│done│failed
   │   bounded worker pool
   │      HEAVY ×1        LIGHT ×2–3        CLOUD ×N (off by default, $-capped)
   ▼
Agent layer  — 100+ definitions as data (role · tools · perms · model tier · objective)
   coordinator decomposes an objective → tasks → workers instantiate a definition per task
   durable sub-graphs (LangGraph) for research + coding flows
   ▼
Model Router (rule table: task class + ctx size + budget + offline? → tier)
   ├── local heavy   Qwen3-Coder-30B-A3B 4-bit  (via llama-swap → mlx-lm)
   ├── local light   Qwen3-4B 4-bit
   ├── local coder   Devstral Small 2 24B  (fallback)
   └── cloud         one frontier API  (optional, gated)
   ▼
Sandbox layer   user 'agent' (non-admin) · workspace jail on ext SSD · git worktree per task
                Colima / Apple container per risky exec · sandbox-exec for one-off calls
                default-deny egress + allowlist
   ▼
Tools (MCP)   Terminal · Filesystem · Git · Browser (Playwright) · Python ·
              Research (search + OpenAlex/S2/arXiv/Crossref + PyMuPDF/Marker/GROBID) · Documents
   ▼
Persistent memory (cross-cutting)
   filesystem Markdown  +  SQLite (tasks/decisions/runs/evidence/audit) + FTS5
   → sqlite-vec later → Graphiti only on proven multi-hop need
```

---

## 3. Resource budget (32 GB, planning estimates — not M6-measured)

| Component | Steady state (light) | Peak (heavy coding job) |
|---|---:|---:|
| macOS + services | ~7 GB | ~7 GB |
| Small model resident (Qwen3-4B) | ~3 GB | ~3 GB |
| Heavy model (Qwen3-Coder-30B-A3B 4-bit) | unloaded | ~18 GB |
| KV cache @ 32K ctx | — | ~3 GB |
| Supervisor + workers (Python) | ~2 GB | ~2 GB |
| SQLite + vec index | ~0.5 GB | ~0.5 GB |
| Headless browser | ~2.5 GB (when active) | evicted |
| Free / FS cache | ~15 GB | **~1 GB (tight)** |

**Rules the corpus is unanimous on:** 1 heavy inference request at a time · never two large models
co-resident · context ≤ 32K local (64K ceiling, 128K only with SSD-tiered KV) · model swapping is
worthwhile · keep 1 small model warm · memory **capacity** is the wall, then bandwidth, then the
single heavy slot.

`analysis/scripts/memory_budget.py` verdict for every response: heavy + small + browser **does not
co-reside** — the design must serialise, which is exactly what the worker pool + swap layer do.

---

## 4. Security boundaries (unanimous)

| Operation | Policy |
|---|---|
| Read/write inside the task workspace; run tests/linters/builds; local git branch/commit/worktree; local inference; allowlisted web GET | **autonomous** |
| `git push` / open PR / touch a shared remote; write outside the workspace; network to a non-allowlisted host; any credential/token request; cloud spend above cap; create agent definition past a cap | **approval** (pushed to phone with a diff/summary) |
| Read `~/.ssh`, Keychain, browser profiles, finance/tax dirs; `sudo`; disk utils; disable the audit log / watchdog / kill switch; `rm -rf` on real paths | **forbidden** — not reachable by the `agent` user by construction |

**Kill switch:** `agentctl stop` writes `~/agentlab/PAUSE` (checked every loop) + SIGKILLs the
worker process group; one tap from the phone; owned by your account.
**Runaway protection:** per-task + per-day token/$/wall-clock caps; max subagents/objective; loop
detector (same tool+args 3× → block); circuit breaker on repeated identical errors.

---

## 5. Build order (union of the roadmaps)

| Phase | Deliverable | Done when |
|---|---|---|
| **1** | dedicated `agent` user + external-SSD layout; `mlx-lm` + `llama-swap` + Qwen3-Coder-30B-A3B + Qwen3-4B; supervisor + SQLite queue; a worker that runs one shell task in a git worktree | `agentctl submit "write fn + pytest"` converges to a committed worktree |
| **2** | OpenHands (container) + Aider wired as the `coding` worker; `code-reviewer` gate; `git push` = approval | points at a real repo, iterates to green tests, stops at the push gate |
| **3** | research pipeline: SearXNG (or a managed API) + OpenAlex/S2/arXiv/Crossref + PyMuPDF/Marker; evidence DB (`sources`/`claims`/`claim_links`); independent verifier + contradiction pass | a question with a known literature contradiction → report surfaces both sides, every claim has a resolvable citation |
| **4** | memory: `memory/*.md` + frontmatter + `[[links]]`; per-project `.agentlab/memory/`; add `sqlite-vec` + hybrid recall **only when FTS5 misses** | session 2 recalls session 1's decisions without re-explaining |
| **5** | formalise `agents/*.md` (role/prompt/tools/perm_tier/model_tier); coordinator emits a task DAG; pool `heavy=1, light=2, cloud=4`; `create_agent_definition` capped; stopping conditions per objective | one objective needing code+research+docs fans into ~15–40 tasks, one coherent deliverable |
| **6** | `launchd` LaunchDaemon + watchdog + nightly "review & plan" job; `pmset` + `caffeinate`; lease-sweep on startup; `newsyslog` rotation | `killall python` mid-task → watchdog restarts ≤ 2 min, task resumes; `reboot` → back without login, queue drains |
| **7** | `tailscale up --ssh`; FastAPI control plane on the tailnet IP; dashboard + SSE logs + STOP; broker → ntfy with action buttons; Claude Code Remote Control (optional) | from cellular: submit a task, stream logs, approve a push, hit STOP, workers die in seconds |
| **8** | speculative decoding; prompt/KV caching per project; eval harness re-run on any model/prompt change; consider vLLM-MLX / oMLX; consider cloud-burst enablement; consider Grafana/Prometheus | measured tok/s + task success rate + $/day tracked; regressions caught before an overnight run |

Each phase is independently useful and independently reversible.

---

## 6. What NOT to build (union of the "do not install" lists)

Kubernetes / k3s / Nomad · standalone vector-DB **servers** (Milvus / Weaviate / Qdrant-server) ·
Neo4j / any graph DB on day 1 · CrewAI / AutoGen / AutoGPT / MetaGPT as the backbone ·
LangChain as core plumbing · Redis + Celery + RabbitMQ (SQLite is enough on one box) · PostgreSQL ·
Airflow / n8n / Zapier · Docker **Desktop** (use Colima / Apple `container`) · three inference
stacks at once (pick one server front) · a **70B+ dense** local model · the **80B Qwen3-Coder-Next**
(doesn't fit) · pixel-level GUI computer-use as the primary interface · ngrok / public reverse
proxy / exposed SSH · a trained model router (RouteLLM) · an opaque "memory product" as the source
of truth · "every trending agent framework simultaneously".

---

## 7. Where this differs from the anchor (`claude-sonnet-5`)

The anchor sits inside the modal choice on ~37 of 39 axes. The two exceptions, both explainable by
it answering from inside Claude Code:

- **Coding harness:** anchor = Claude Code + Goose; the merged design = **OpenHands + Aider** (the
  8/10 peer consensus, and both open-source / local-model-capable).
- **Orchestration substrate:** anchor = Claude Agent SDK; the merged design = **thin custom
  supervisor + LangGraph for sub-graphs** (the peer plurality).

Everything else — MLX, Qwen MoE, 1 heavy worker, SQLite queue, sqlite-vec, coordinator/worker,
dedicated user, Tailscale, launchd + watchdog, evidence-first research, defer the graph DB — the
anchor and the independent peers agree.
