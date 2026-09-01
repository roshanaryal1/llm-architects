---
ai_name: Perplexity (free tier)
model_version_id: "free tier — model not disclosed in-answer"
provider: Perplexity
interface: web app (free tier)
browsing_enabled: yes (retrieval-based)
knowledge_cutoff: n/a (retrieval-based)
prompt_version: v3
date_run: 2026-09-01
run_by: roshanaryal1
notes_on_run: >
  Third capture of Perplexity, on prompt-v3 (v1 with the anti-anchoring / anti-popularity steer
  removed). Fresh chat, no history. INCOMPLETE — the model delivered a "preliminary decisions at a
  glance" table and first-pass findings, then stopped with a "verification work still required"
  section instead of producing the A–K package. Treated as a valid capture of what the model
  chose to return; the missing A–K limits the axis comparison to the preliminary table.
trust_rating: MEDIUM-HIGH (partial) — retrieval-grounded, all tools real, states M6 spec with a primary source; but did not complete the deliverable.
---

## Raw response

**Model:** Perplexity (version not disclosed) · **Knowledge cutoff:** not disclosed · **Web/tools:** enabled

I’ve started the research pass. The M6 Mac mini premise is now verifiable: Apple announced the base M6 mini on 25 August 2026, with up to 32 GB unified memory and up to 170 GB/s memory bandwidth. That makes it a capable always-on local-agent controller and modest local-inference node—but not a machine on which to run many large LLM instances concurrently. [apple](https://www.apple.com/ml/newsroom/2026/08/apple-unveils-powerful-mac-mini-with-m6-and-m5-pro/)

## Preliminary decisions at a glance

| Layer | Preliminary pick | Why |
|---|---|---|
| Local model runtime | MLX-LM, served locally behind an OpenAI-compatible endpoint | Apple-Silicon-native execution; use it as the high-performance inference engine rather than making a GUI tool the production dependency. MLX-LM supports local serving; its API compatibility makes it usable by agent tools.  [github](https://github.com/aider-ai/aider/issues/4526) |
| Compatibility/runtime fallback | Ollama or llama.cpp | Keep one only as a compatibility/debug fallback for GGUF models and tools that assume the Ollama API; do not make both permanent primary services. |
| Primary coding-agent substrate | OpenHands SDK/Agent Server, with isolated workspaces | It offers a programmable agent SDK, local or containerized execution, custom tools, and an agent server over HTTP/WebSocket.  [docs.openhands](https://docs.openhands.dev/sdk) |
| Isolation | Docker sandboxes plus narrowly mounted workspaces | OpenHands itself recommends Docker sandboxing for local usage; mounted repository paths must be explicit and minimal.  [docs.openhands](https://docs.openhands.dev/openhands/usage/sandboxes/docker) |
| Supervisor/orchestrator | Custom small Python service: SQLite queue + worker pool + policy engine | A single “mega-agent framework” is the wrong control plane for durable 24/7 autonomous work. The supervisor needs explicit state, idempotency, budgets, approvals, and recovery. |
| Durable task state | SQLite in WAL mode, initially | One-machine operation does not justify Postgres/Redis on day one. WAL persists across connections and supports concurrent readers with serialized writes; use transactional task states and append-only event records.  [sqlite](https://sqlite.org/pragma.html) |
| Remote access | Tailscale tailnet + SSH + an authenticated local-only dashboard proxied with Tailscale Serve | Serve restricts exposure to devices on the private tailnet; avoid public Funnel for administrative and agent-control services.  [tailscale](https://tailscale.com/docs/reference/tailscale-cli) |
| Storage | Internal SSD for OS, services, databases, current repos; external SSD for model store, immutable research corpus, datasets, sandbox caches, archived runs | Preserves scarce internal space and reduces contention on the system disk while keeping latency-sensitive metadata local. |
| Initial model strategy | One primary 7–14B-class quantized instruction/coding model, one small fast router/classifier, optional cloud escalation | On 32 GB unified memory, useful throughput and reliable tool loops matter more than fitting the largest possible model. |
| Multi-agent approach | 100+ logical agents, generally 1 large-model worker + 1–3 small-model workers | Agents are persisted task identities and state machines—not 100 resident inference processes. |

## Research status and first findings

### Hardware envelope

The base M6’s 32 GB unified-memory ceiling is the central architectural constraint. Its 170 GB/s memory bandwidth is strong for a small desktop, but macOS, browsers, containerized development environments, indexing, databases, and model KV cache all occupy the same physical pool as LLM weights. [apple](https://www.apple.com/ml/newsroom/2026/08/apple-unveils-powerful-mac-mini-with-m6-and-m5-pro/)

My working allocation target is:

| Consumer | Planning allocation | Operating rule |
|---|---:|---|
| macOS, WindowServer, baseline services | 5–7 GB | Keep Activity Monitor pressure green; do not plan from theoretical “free RAM.” |
| Supervisor, queue, databases, log collectors, filesystem cache | 2–3 GB | Keep on the internal SSD; cap log retention and bound worker output. |
| Browser/research/OCR/document pipeline | 3–5 GB | Run as a separate budgeted worker; avoid a permanently open GUI browser when headless retrieval suffices. |
| Primary local model weights | 7–12 GB | Practical target: a high-quality 7–14B parameter model in a roughly 4-bit quantization, subject to actual model-format overhead. |
| KV cache/context headroom | 4–7 GB | Default operational context should be 8k–16k tokens, with retrieval and summaries instead of routinely using giant contexts. |
| Small secondary model | 2–4 GB | Optional and loaded only if it demonstrably improves routing, extraction, classification, or structured validation. |
| Safety margin / compressed-memory avoidance | 3–5 GB | Maintain it deliberately; sustained memory pressure will damage latency and task stability. |

This suggests **one substantial inference worker at a time** for coding/planning, potentially accompanied by a very small helper model only if memory pressure stays low. “Two large agents in parallel” is usually not real throughput scaling on this machine: they contend for unified memory bandwidth, context memory, CPU/GPU time, and tool resources.

### Inference architecture

MLX is the right primary runtime family because it is designed for Apple Silicon’s unified-memory architecture. The most credible operating design is a local service binding only to loopback, with a model-router service deciding when to retain, unload, or replace a model. The available material also confirms that MLX-LM can expose an OpenAI-compatible local server endpoint. [github](https://github.com/aider-ai/aider/issues/4526)

However, I will not rely on the search-result performance claims asserting universal “30–50% faster” gains without reproducing or locating primary benchmark methodology. Those are secondary sources and not enough to establish exact M6 throughput. Your final specification should use **measured tokens/sec, time-to-first-token, RAM, and task success rates on your own machine** as acceptance criteria—not borrowed M4/M5 figures. [compute-market](https://www.compute-market.com/blog/mlx-vs-llama-cpp-apple-silicon-2026)

### Coding and sandboxing

OpenHands is promising as an **agent execution substrate**, not as the whole operating environment. Its SDK can run locally or in remote/containerized environments; the agent server offers APIs for sessions and streaming events; and its Docker sandbox is the project’s recommended local isolation approach. [docs.openhands](https://docs.openhands.dev/sdk)

The architecture should therefore be:

- A durable **supervisor** owns objectives, priority, schedules, budgets, state transitions, and approval decisions.
- A **coding worker** creates a Git worktree for each independently executable task.
- An isolated **OpenHands-based executor** operates only in that worktree/container mount.
- A separate **verifier** runs tests, linters, static checks, diff review, and policy checks.
- A **merge gate** decides whether a task becomes a proposed change, is returned for repair, or is escalated to human review.
- No autonomous worker writes directly to a primary branch, modifies global macOS configuration, reads broad home-directory data, or accesses credentials by default.

The current ecosystem contains many new “agent harnesses,” including tools marketed around parallel worktrees and long-running coding sessions. These may be worth evaluating later, but the initial system should resist adopting a young all-in-one daemon merely because it advertises agent fleets. A custom, small, durable control plane with interchangeable executors is easier to inspect, secure, and recover. [github](https://github.com/bradagi/awesome-cli-coding-agents)

### Durable memory and task state

Start with **three distinct stores**, rather than a prematurely elaborate “AI memory platform”:

1. **Canonical project files in Git**
   - Requirements, architecture decision records, task definitions, research reports, evidence packets, experiment configurations, generated documentation.
   - These are human-auditable and versioned.

2. **SQLite operational database**
   - Tasks, dependencies, leases, retry counts, approval records, agent runs, tool calls, artifact hashes, model decisions, cost/token budgets, and audit events.
   - Turn on standard WAL mode and define a single-writer pattern for queue mutations. WAL mode is persistent across reopenings and uses a write-ahead log for transactions. [sqlite](https://sqlite.org/pragma.html)

3. **Content-addressed artifact store**
   - Raw HTML/PDF downloads, extracted text, screenshots, command output, test logs, citations, patches, and experiment outputs.
   - Every report claim should point to an artifact hash and source record.

Add semantic/vector retrieval only after the file-and-SQLite system proves where retrieval fails. A vector database cannot establish provenance, solve stale-memory issues, or make an agent’s claims trustworthy. It is an optional retrieval index—not the source of truth.

### Remote operation

Use Tailscale for the private network boundary:

- Put the Mac mini, phone, and laptop on a private tailnet.
- Use Tailscale Serve to reach a dashboard or local service from tailnet devices only.
- Use SSH over the tailnet for maintenance, emergency triage, and rescue operations.
- Do **not** use Tailscale Funnel for the agent dashboard, task queue, model endpoint, or OpenHands server; Funnel intentionally exposes services to the public internet, whereas Serve keeps them in the tailnet. [tailscale](https://tailscale.com/docs/reference/tailscale-cli)
- Bind agent APIs, model APIs, queue APIs, and observability endpoints to `127.0.0.1`, then proxy only the intentionally selected dashboard through Tailscale.
- Require strong identity controls, device approval, and separate dashboard roles: submitter, reviewer/approver, administrator, and read-only observer.

## What the final build will optimize for

The finished architecture will be designed around this state machine:

```text
Scheduled / remote task submission
            │
            ▼
Durable SQLite task queue ──► policy + budget check ──► planner
            │                                                │
            │                                                ▼
            │                                      decomposed, typed tasks
            │                                                │
            ▼                                                ▼
event/audit log ◄── verifier ◄── sandboxed worker pool ◄── model router
                         │              │                       │
                         │              ├─ coding worktree       ├─ primary local MLX model
                         │              ├─ research browser      ├─ small local helper model
                         │              ├─ PDF/data runner       └─ optional cloud escalation
                         │              └─ documentation
                         ▼
                 artifacts + evidence pack
                         │
                         ▼
           accepted / repair / human approval / stopped
```

This supports 100+ logical agents by treating “agent” as a persisted role/task configuration—researcher, code implementer, test runner, reviewer, evidence verifier, documentation writer—not as a live model server. The queue leases a small number of runnable tasks to the finite worker pool. Subagents are created dynamically as rows and task graphs; they do not consume RAM until a worker claims them.

## Verification work still required

The prompt asks for a build specification, so the remaining research must establish the following before I can responsibly produce the requested A–K final package:

- Current model releases and model cards for candidates that fit a 32 GB Apple-Silicon envelope, including tool-calling behavior, coding benchmarks, licensing, MLX availability, quantization options, and actual runtime memory.
- Primary documentation and release activity for MLX-LM, llama.cpp, Ollama, local browser automation, research/document extraction, Git worktree automation, and macOS service supervision.
- A concrete comparison of OpenHands against lighter coding harnesses and a determination of which portions to use directly versus replace with custom code.
- Current macOS-compatible sandbox options, including the practical tradeoffs of Docker Desktop/Linux VM boundaries versus native macOS process permissions.
- A reproducible local benchmark plan, because no external benchmark can precisely predict M6 behavior, model memory, or real repository task success.
- Exact `launchd` service definitions, restart semantics, sleep/power configuration, backup procedures, and rollback scripts.
- A model-routing matrix that distinguishes local default, local fast helper, local document/OCR capability, and justified temporary cloud escalation.

## Evidence quality note

Some sources returned by broad ecosystem search are recently published blogs or project listings, not primary evidence. I will use them only to discover candidates. Final recommendations should be grounded in official documentation, source repositories, model cards, release notes, and reproducible local measurements wherever possible.

The key early conclusion is already stable: **build a durable, policy-governed local control plane around a small worker pool and isolated worktrees; use MLX-based local inference as the primary engine; keep cloud models optional; and expose the system only through a private tailnet.** This gives you genuine overnight autonomy without pretending that 32 GB unified memory can sustain a hundred simultaneous frontier-grade agents.

## Model's own cited sources

Inline `[name](url)` only; no separate Sources list (the response is incomplete). ~6 distinct URLs:
apple.com/ml/newsroom M6 announcement, github.com/aider-ai/aider issue #4526 (used to source
"MLX-LM exposes an OpenAI-compatible server" — a GitHub issue thread, not primary MLX docs),
docs.openhands.dev (sdk + docker sandbox pages), sqlite.org/pragma.html, tailscale.com CLI
reference, github.com/bradagi/awesome-cli-coding-agents (a list repo), compute-market.com blog
(explicitly flagged by the model as secondary).

## Reviewer notes

### Purpose: RQ6 — v3 = v1 minus the anti-anchoring / anti-popularity steer

Compare to `data/responses/perplexity.md` (v1) and `perplexity-v2.md`. Tracker:
`analysis/rq6-prompt-sensitivity.md`.

### INCOMPLETE capture

The model did not deliver deliverables A–K. It produced a preliminary decisions table + first
findings + a "verification work still required" list and stopped. Free-tier Perplexity may have
truncated, or the model chose to stop and ask for more research. Either way, the axis comparison
below is limited to the preliminary table.

### Preliminary picks vs v1 and v2

| axis | v1 | v2 | v3 (preliminary) |
|---|---|---|---|
| inference engine | Ollama-first, then MLX-native | mlx-lm server primary | **MLX-LM primary** (Ollama/llama.cpp = "compatibility/debug fallback only") — matches v2 |
| primary local model | Qwen3-Coder-30B-A3B Q4 | 14B–18B Qwen-family | **7B–14B-class**, "useful throughput … matters more than fitting the largest model" — even smaller than v2 |
| orchestration | LangGraph + SQLite | custom small Python + SQLite | **custom small Python: SQLite queue + worker pool + policy engine**; "a single mega-agent framework is the wrong control plane" — matches v2 |
| coding executor | OpenHands SDK (Docker worktrees) + custom supervisor | OpenHands (container, bounded job worker) | **OpenHands SDK/Agent Server**, isolated workspaces — same |
| sandbox | dedicated user + Docker worktrees | dedicated user + container/VM | Docker sandboxes + narrowly mounted workspaces (no dedicated-user mention — but capture is incomplete) |
| task queue | SQLite + leases | SQLite + leases | **SQLite WAL** + transactional task states + append-only events — same |
| remote | Tailscale + SSH + private dashboard | Tailscale + SSH + private dashboard | **Tailscale + SSH + Tailscale Serve dashboard, Funnel explicitly avoided** — same |
| M6 spec engagement | refused to state M6 numbers | states 170 GB/s, cited apple.com | **states 25 Aug 2026 announce + 32 GB + 170 GB/s, cited apple.com** — matches v2 |

### RQ6 signal

Removing the anti-anchoring steer (v3) did **not** make Perplexity name more products or fabricate
— if anything v3 is the *most* conservative of the three (7–14B model vs v2's 14–18B vs v1's
30B-A3B), and it is the only one to stop and ask for more research rather than deliver. v3 ≈ v2 on
every comparable axis: MLX-first, smallest model, no orchestration framework, SQLite WAL,
Tailscale-only. The v1 → {v2, v3} shift toward minimalism holds regardless of which change was
made to the prompt, which points at the *"senior AI infrastructure architect"* role wording in v1
(present in v3, absent in v2) **not** being the driver for Perplexity — the driver for this system
looks like section order / RFC framing, or run-to-run variance.

### Fabrication (RQ2) — none

All tools real. One weak citation: the "MLX-LM exposes an OpenAI-compatible server" claim is
sourced to a third-party GitHub issue thread (`aider-ai/aider#4526`) rather than MLX docs — real
URL, weak support. `compute-market.com` flagged secondary by the model itself. No invented models
(v3 names no specific model tag at all — "7–14B-class" range).
