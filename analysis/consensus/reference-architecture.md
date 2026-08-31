# Reference architecture

**Purpose:** a build-ready synthesis of the 10 independent non-anchor system recommendations. This document deliberately separates **consensus constraints** from `[adjudicated]` implementation choices.

## 1. Design principles

1. **Local-first:** the system remains useful with no paid cloud LLM.
2. **Memory is the primary constraint:** design for 32 GB unified memory, not for an abstract model maximum.
3. **One heavy inference slot:** do not co-reside two large models.
4. **100 logical agents, bounded physical workers:** agent definitions are cheap; workers are scarce.
5. **Durable state:** process memory is never the source of truth for task progress.
6. **Evidence before synthesis:** research output is generated only from verified evidence.
7. **Least privilege:** agents run as a dedicated non-admin user; stronger isolation is applied to untrusted execution.
8. **Private remote access:** no public model endpoint; remote control goes through the private tailnet.
9. **Replaceable components:** inference servers, coding executors and optional frameworks sit behind narrow interfaces.

## 2. System topology

```text
                         ┌─────────────────────────┐
                         │   Private remote UI/API  │
                         │   FastAPI + dashboard    │
                         └────────────┬────────────┘
                                      │ Tailscale
                                      ▼
┌────────────────────────────────────────────────────────────────┐
│                        SUPERVISOR                               │
│  policy → planner → scheduler → leases → recovery → audit     │
└──────────────┬──────────────────────────┬──────────────────────┘
               │                          │
               ▼                          ▼
       ┌───────────────┐          ┌─────────────────┐
       │ SQLite WAL    │          │ Model router    │
       │ tasks/leases/ │          │ type + quality  │
       │ events/audit  │          │ + memory/load   │
       └───────────────┘          └────────┬────────┘
                                          │
                         ┌────────────────┴────────────────┐
                         ▼                                 ▼
                ┌────────────────┐                 ┌──────────────┐
                │ Heavy worker   │                 │ Light pool   │
                │ 1 slot         │                 │ 2–3 workers  │
                └───────┬────────┘                 └──────┬───────┘
                        │                                  │
                        ▼                                  ▼
                ┌────────────────┐                 ┌──────────────┐
                │ Local inference│                 │ classifiers/ │
                │ MLX-family     │                 │ summaries/IO │
                └────────────────┘                 └──────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Coding / research   │
              │ executors           │
              │ Aider/OpenHands/etc │
              └──────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Evidence + artifacts │
              │ SQLite/filesystem    │
              └──────────────────────┘
```

This is a **coordinator/worker architecture, not a swarm**. A task may create many logical specialist definitions, but only a bounded number of physical workers execute at once.

## 3. Model and inference layer

### [adjudicated] Heavy model

Start with a **Qwen3-Coder-30B-A3B-class 4-bit MoE** as the benchmark baseline. The corpus gives this family the strongest direct support, while newer Qwen3.6-35B-A3B is a credible alternative. Do not encode the model name as permanent truth: benchmark candidate checkpoints on the actual M6 for quality, memory footprint, prompt processing and sustained generation.

### [adjudicated] Inference runtime

Use an **MLX-family serving adapter**, initially favouring `mlx-lm` or the best validated MLX server available at build time. Keep llama.cpp and Ollama as compatibility/fallback implementations behind the adapter. Do not make the supervisor depend directly on one server API.

### Residency policy

- One large model resident at a time.
- One small helper may remain resident if measured memory headroom is safe.
- Additional models load on demand.
- Model swapping is task-policy-driven, not per trivial task.
- Keep a hard RAM safety floor and monitor unified-memory pressure.

### Resource budget (32 GB — planning estimates, not M6-measured)

Drawn from the published MLX benchmarks the sourced responses cite (M4/M5 hardware, extrapolated).
`analysis/scripts/memory_budget.py` reproduces these per response.

| Component | Steady state (light work) | Peak (heavy coding job) |
|---|---:|---:|
| macOS + services | ~7 GB | ~7 GB |
| Small model resident (Qwen3-4B 4-bit) | ~3 GB | ~3 GB |
| Heavy model (Qwen3-Coder-30B-A3B 4-bit) | unloaded | ~18 GB |
| KV cache @ 32K context | — | ~3 GB |
| Supervisor + workers (Python) | ~2 GB | ~2 GB |
| SQLite + FTS/vec index | ~0.5 GB | ~0.5 GB |
| Headless browser | ~2.5 GB (when active) | evicted |
| Free / filesystem cache | ~15 GB | **~1 GB — the tight case** |

`memory_budget.py` verdict for **every** captured response: heavy model + small model + browser
**cannot co-reside** in 32 GB. The design must serialise inference — which the 1-heavy-worker
semaphore + the swap manager do. Context above ~32K needs SSD-tiered KV (only `mistral-large-3`
raised this) or it OOMs. The one response that keeps 3 models loaded relies on swap and is the
outlier the corpus rejects.

### [adjudicated] Router

Use a small deterministic policy table first:

| Task class | Default route |
|---|---|
| classification / simple extraction | light model |
| ordinary coding | heavy model + coding executor |
| research retrieval / parsing | tool-only where possible; light model for extraction |
| deep reasoning / synthesis | heavy model |
| verification | light model first, heavy model when ambiguity is high |
| cloud escalation | only after policy gate |

Train a learned router only after enough task telemetry exists to justify it.

## 4. Agent model

An **agent is a durable logical definition**, not a running model process. Store:

- `agent_id`
- role
- objective
- model preference
- tool allowlist
- workspace
- memory scope
- permission tier
- context/token budget
- max steps
- state

The supervisor can create specialist definitions dynamically and enqueue tasks against them. Physical concurrency remains bounded by worker and model semaphores.

## 5. Orchestration

### [adjudicated] Supervisor

Build a small Python supervisor around `asyncio`, SQLite and explicit state transitions. Use a framework such as LangGraph or PydanticAI only inside workflows where its durability/state semantics provide measurable value.

The supervisor owns:

- task decomposition
- priority
- leases
- model routing
- concurrency limits
- approvals
- retries
- checkpointing
- recovery
- audit events

This keeps the architecture portable if an agent framework changes or disappears.

## 6. Coding execution

### [adjudicated] Two execution modes

**Interactive/git-safe:** Aider or OpenCode.

**Autonomous/untrusted:** OpenHands inside a stronger sandbox, with per-task worktrees.

Claude Code may be used as an optional accelerator where available, but it is not a required architectural dependency.

Every autonomous coding task follows:

```text
plan → branch/worktree → edit → test → inspect diff → fix →
repeat boundedly → commit → report → optional PR/review
```

Destructive operations require an approval policy regardless of model confidence.

## 7. Research subsystem

Research is a deterministic evidence pipeline:

```text
query
  ↓
discover sources
  ↓
filter primary/high-quality sources
  ↓
retrieve and store source material
  ↓
extract claims + evidence excerpts
  ↓
verify each claim against its source
  ↓
run contradiction detection
  ↓
assign verification/confidence status
  ↓
synthesize only from verified evidence
  ↓
validate citations
```

The evidence ledger is the source of truth. A generated claim without a supporting evidence record is `UNVERIFIED`, not silently accepted.

## 8. Memory

### Day one

**SQLite + filesystem.** SQLite stores structured state, claims, evidence, tasks, leases and metadata. Markdown/JSON artifacts remain human-readable and versionable.

### [adjudicated] Semantic retrieval

Start with **sqlite-vec (embedded)** plus BM25/FTS. Do not deploy a standalone Qdrant/Chroma/Milvus/Weaviate service initially.

### [adjudicated] Growth path

Add a richer embedded vector layer only when retrieval tests show SQLite/FTS/vec is inadequate. Add a knowledge graph only after measured workloads demonstrate a multi-hop, temporal or entity-relationship need. The corpus does not justify Neo4j on day one.

## 9. Queue and recovery

### [adjudicated] Queue

Use a **SQLite WAL-backed task queue**. A task has at least:

`queued → leased → running → succeeded | failed | interrupted | cancelled`

Leases expire. On supervisor restart, stale `running` tasks become `interrupted` and are requeued according to retry policy.

Tasks should be idempotent where possible. Destructive actions must never be replayed blindly after recovery.

Redis is a future scaling option, not a day-one dependency.

## 10. Security and sandboxing

Run the system under a **dedicated non-admin macOS account**. Use separate workspaces per project/task and strict filesystem permissions.

### Capability tiers

- **Autonomous:** safe local edits, tests, retrieval and non-destructive tooling.
- **Notify/log:** actions with meaningful side effects; execute and record notification where policy permits.
- **Approve:** network-sensitive, publication, account, deletion or infrastructure changes.
- **Never:** credential extraction, privilege escalation, destructive host operations, arbitrary public exposure.

### [adjudicated] Strong sandbox

Use Docker/OrbStack or an equivalent isolated runtime for untrusted autonomous code when the workload warrants it. Do not require containers for every ordinary task because 32 GB makes unnecessary virtualization overhead costly.

Secrets live in Keychain/environment injection outside the agent workspace; never write credentials into agent files.

## 11. Remote control

### [adjudicated] Network

Use **Tailscale only** for routine remote access. Bind the dashboard/API to the tailnet interface or loopback-proxied path. Do not expose Ollama/MLX/llama.cpp endpoints directly to the Internet.

### Control plane

A small FastAPI service should expose:

- system health
- queue status
- task submission/status
- worker/model status
- logs
- approvals
- emergency stop

The emergency-stop endpoint should stop new work and request orderly cancellation of active tasks before any stronger kill operation.

## 12. Always-on operation

Use:

- `launchd` `RunAtLoad` + `KeepAlive`
- a separate watchdog/heartbeat
- structured rotating logs
- `caffeinate`/appropriate `pmset` policy while work is queued
- startup recovery from SQLite

Prefer queue-aware sleep prevention: when the queue is empty for a configured period, normal sleep can resume. When work is pending, the machine stays awake on AC power.

## 13. Storage layout

### Internal 512 GB SSD

Keep latency-sensitive state here:

- macOS and applications
- Python/runtime environments
- supervisor and inference binaries
- SQLite databases/WAL
- active repositories/worktrees
- active cache
- **[adjudicated] hot model weights** when practical

Maintain a substantial free-space reserve; do not fill the internal disk simply because capacity exists.

### External 1 TB SSD

Use for:

- full model library
- research corpus and PDFs
- datasets
- archived repositories
- experiment artifacts
- long-term logs
- backup sets
- cold model weights

The external SSD is storage, **not itself a backup strategy**; important state should have an additional backup destination.

## 14. Cloud escalation policy

Cloud is an optional second opinion/escape hatch.

Escalate only when:

1. local confidence is below threshold, or
2. the task is explicitly marked frontier/hard, and
3. privacy classification permits it, and
4. the budget allows it, and
5. the user/task policy permits external processing.

Redact sensitive data before escalation. The system must remain operational if the cloud provider is unavailable.

## 15. What not to build initially

- Kubernetes/K3s
- multiple concurrent large inference servers
- a standalone vector-DB cluster
- Neo4j or another heavy graph database
- Redis/Celery before SQLite is measured as insufficient
- a swarm of persistent LLM processes
- public model endpoints
- GUI/computer-use as the primary control path
- a mega-stack containing every agent framework
- a learned router before telemetry exists
- a 70B+/80B dense model merely because it is larger

## 16. Non-consensus decisions ledger

| Decision | Status | Why |
|---|---|---|
| Heavy model checkpoint | **[adjudicated]** | Start from Qwen3-Coder-30B-A3B class; benchmark newer 35B-A3B candidate. |
| Inference server | **[adjudicated]** | MLX-family adapter; validate mlx-lm/Ollama/llama.cpp alternatives on real hardware. |
| Orchestration framework | **[adjudicated]** | Custom supervisor owns architecture; frameworks are subordinate components. |
| Coding executor | **[adjudicated]** | Aider/OpenCode interactive; OpenHands for autonomous sandboxed work. |
| Vector implementation | **[adjudicated]** | sqlite-vec + FTS initially; migrate only on measured retrieval need. |
| Sandbox depth | **[adjudicated]** | Dedicated user for ordinary work; stronger container/VM isolation for untrusted code. |
| Queue backend | **[adjudicated]** | SQLite WAL first; Redis only after scale evidence. |
| Cloud | **[adjudicated]** | Optional, privacy/budget/confidence gated. |
| Monitoring | **[adjudicated]** | Native metrics + structured logs first; Prometheus/Grafana later if needed. |

## 17. First implementation order

1. SQLite schema for tasks, leases, events, agents and approvals.
2. Supervisor event loop and durable recovery.
3. Model adapter + one heavy model + one light model.
4. Concurrency semaphores: heavy=1, light=2–3.
5. Model swap manager with RAM/headroom policy.
6. Aider/OpenHands executor adapters.
7. Research evidence ledger + verification pipeline.
8. Dedicated-user permissions and task workspaces.
9. launchd + watchdog + queue-aware `caffeinate`.
10. Tailscale-only FastAPI dashboard and emergency stop.
11. sqlite-vec/FTS retrieval.
12. Benchmark and tune before adding frameworks, Redis, graph memory or cloud escalation.

The architecture is intentionally **boring at the control-plane level and sophisticated at the policy/evidence level**. That is the central engineering lesson of the corpus.