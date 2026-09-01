---
ai_name: Gemini 3.1 Pro
model_version_id: "self-reports 'Gemini 2.5 Pro'; cutoff self-reported '2026'"
provider: Google
interface: Gemini app / AI Studio (free)
browsing_enabled: NO — self-declared "Answered explicitly from internal technical knowledge base"
knowledge_cutoff: "self-reported 2026"
prompt_version: v2
date_run: 2026-09-01
run_by: roshanaryal1
notes_on_run: >
  Second Gemini capture, on prompt-v2 (RFC framing). Fresh chat. Full A–K. Browsing OFF (same as
  v1). Self-reports "Gemini 2.5 Pro" — the v3 run self-reported "Gemini 1.5 Pro", so the free
  tier served different underlying models across the two runs (see z-ai for a similar issue).
  ~5 sources given as project names only (no URLs).
trust_rating: MEDIUM — all tools/models real, coherent, quantified RAM budget; but 0 resolving citations, stale cloud fallback (Claude 3.5 Sonnet — same as v1), no M6-specific facts.
---

## Raw response

**Model:** Gemini 2.5 Pro | **Knowledge Cutoff:** 2026 | **Web Browsing/Tools:** Disabled (Answered explicitly from internal technical knowledge base)

---

## Decisions at a Glance

| Component / Layer | Chosen Technology | Key Alternative Considered | Primary Rationale |
| --- | --- | --- | --- |
| **Local Inference Engine** | `llama.cpp` (`llama-server`) / `mlx-lm` | Ollama, vLLM | Native Apple Silicon Metal acceleration, minimal overhead, custom KV cache quantization (Q4_0 KV). |
| **Primary Code/Reasoning LLM** | Qwen2.5-Coder-32B-Instruct (Q4_K_M) | DeepSeek-Coder-V2-Lite, Llama-3.3-70B | Highest code generation benchmark score fitting within 20 GB VRAM allocation. |
| **Fast Routine/Routing LLM** | Qwen2.5-7B-Instruct (Q4_K_M) | Llama-3.1-8B-Instruct | ~4.5 GB memory footprint, ultra-fast generation for summarization, tool routing, and classification. |
| **Cloud Fallback LLM (Optional)** | Anthropic Claude 3.5 Sonnet API | OpenAI o3-mini | High reasoning and long-context architecture capability when local verification retries hit threshold. |
| **Agent Orchestrator** | Custom Async State Engine (`LangGraph` core + `LiteLLM`) | AutoGen, CrewAI, Agentkit | Minimal background overhead; precise event-driven state control for 100+ logical agents on 32 GB RAM. |
| **Autonomous Coding Harness** | Aider CLI (Headless runner mode) | OpenHands, Claude Code CLI | Proven git worktree integration, low memory footprint, strict multi-file edit tracking, robust local model support. |
| **Autonomous Research System** | Custom Async Pipeline (`Playwright` + `sqlite-vec` + `pypdf`) | Perplexity API, AutoGPT | Deterministic citation verification, zero hallucinated sources, local offline vector indexing of downloaded PDFs. |
| **Durable Memory Layer** | SQLite (`sqlite-vec` extension + WAL mode) | ChromaDB, Qdrant, PostgreSQL | Single file database, zero background daemon RAM consumption, native fast hybrid BM25 + vector search. |
| **Execution Sandboxing** | macOS Sandbox (`sandbox-exec`) + OrbStack / Docker | macOS Virtual Machines (UTM) | Avoids 4–8 GB hypervisor memory tax while enforcing strict directory boundary and system privilege isolation. |
| **Process Supervisor / 24/7** | macOS Native `launchd` + `caffeinate` | PM2, Systemd, Supervisord | Native macOS system daemon management; self-healing process restarts and hardware sleep inhibition. |
| **Remote Control & Alerting** | Tailscale + Telegram Bot API (Async Webhook) | SSH Tunneling, Ngrok, Cloudflare | Zero public inbound ports, encrypted WireGuard peer-to-peer mesh connectivity, mobile push notifications & kill-switch. |

---

## 1. On-Device Inference

On Apple Silicon M6 with 32 GB of unified memory, macOS system processes reserve approximately 6–8 GB of RAM. This leaves a reliable operating ceiling of 24–26 GB for model weights, key-value (KV) caches, and dynamic context allocation.

### Local Engines: `llama.cpp` vs. `mlx-lm` vs. Ollama

* **`llama.cpp` (`llama-server`):** Selected as the primary engine. Offers Metal execution, precise memory allocation, support for standard GGUF quantizations, and low overhead. Crucially, `llama.cpp` supports FP16/Q8_0/Q4_0 KV cache quantization, saving 40–60% of context memory overhead.
* **`mlx-lm`:** Exceptional token output speed on Apple Silicon using native MLX arrays. However, memory management during concurrent multi-context batching is less tightly capped than `llama.cpp` standard GGUF servers.
* **Ollama:** Excellent developer UX, but adds an extra API abstraction layer and background memory footprint that is unnecessary in a constrained, headless continuous build environment.

### Model Selection & Quantization Strategy

* **Primary Workhorse Model (Coding, Complex Planning, Debugging):** `Qwen2.5-Coder-32B-Instruct` (Quantized at `Q4_K_M`).
* *Weight Footprint:* ~19.8 GB.
* *Context Capacity:* Configured to 16,384 tokens with Q4_0 KV cache (~1.8 GB). Total VRAM allocation: ~21.6 GB.
* *Performance:* Exceptional instruction-following, multi-file code editing, and tool execution benchmark performance matching larger open-weights models.

* **Lightweight Worker Model (Routing, Summarization, Log Analysis, Classification):** `Qwen2.5-7B-Instruct` (Quantized at `Q4_K_M`).
* *Weight Footprint:* ~4.5 GB.
* *Context Capacity:* 8,192 tokens (~0.6 GB).
* *Execution Strategy:* Hot-swapped on-demand via `llama-server` model swapping or kept resident alongside Qwen2.5-Coder only when using dynamic time-slicing (unloading 32B model to disk when bulk sub-agent processing occurs).

---

## 2. Agent Runtimes and Harnesses

A multi-agent autonomous system needs long-running execution loops, state persistence, tool sandboxing, sub-agent delegation, and graceful error handling.

### Evaluation of Frameworks

* **OpenHands (formerly OpenDevin) / AutoGen / CrewAI:** Heavy reliance on complex abstractions, high background memory footprints, and difficult state serializations over extended autonomous periods.
* **LangGraph Core (Python `asyncio` base):** Chosen as the state management backbone. Represents agent workflows as directed acyclic or cyclic graphs. Agent states are serialized into SQLite directly at every step node, enabling exact state recovery if the daemon or machine reboots.
* **Aider (Headless Driver):** Chosen for file-level coding tasks. Aider manages git tree context, automatically generates unified diffs, runs test suites, and reverts failed edits deterministically.

---

## 3. Many-Agent Design on Small Hardware

Running 100 concurrent LLM process instances on a 32 GB unified memory machine will trigger severe system swapping and out-of-memory (OOM) kernel panics. The architecture must decouple **Logical Agents** from **Model Inference Workers**.

```
[ 100+ Logical Agent State Nodes (SQLite / Async Event Loop) ]
                                |
                   (Task Queue & Priority Router)
                                |
             [ Concurrency Semaphore: Max 1 Heavy / 2 Light ]
                                |
                 [ Local llama.cpp Inference Engine ]
```

### Decoupled Execution Architecture

* **Logical Agent:** A lightweight JSON/Python dictionary containing context history, memory pointers, status flags (`IDLE`, `QUEUED`, `RUNNING`, `WAITING_INPUT`), and assigned system prompts. 100 logical agents consume less than 50 MB of system RAM.
* **Worker Pool Concurrency:** A global `asyncio.Semaphore(1)` enforces that only **one** heavy inference query (32B model) runs on the GPU at any single instant. A secondary priority queue buffers requests from agents.
* **Topology:** Coordinator-Worker hierarchy. A persistent *Supervisor Agent* breaks complex goals into task items inside SQLite. *Worker Agents* are dynamically instantiated as state machines, pull tasks, request LLM inference time through the queue semaphore, execute external tool commands, record output, and terminate.

---

## 4. Autonomous Coding Systems

Autonomous coding requires reliable file editing, dependency isolation, execution loop handling, and automated git management.

### Coding Harness Strategy

* **Repository Comprehension:** Uses `ctags` combined with `tree-sitter` parsing to extract structural AST symbols without loading entire repositories into LLM context windows.
* **Git Worktrees:** Every task assigned to an agent executes inside an isolated Git Worktree (`git worktree add -b task-xyz ./worktrees/task-xyz`). This prevents sub-agents from overwriting the main branch or stepping on each other's changes.
* **Self-Correction Loop:**
1. Agent generates code edit.
2. Harness applies diff to worktree.
3. Harness executes configured test runner (`pytest`, `npm test`, etc.).
4. If failure occurs, compiler/test stdout error traces are fed back into the agent context for up to 3 automated retry attempts.
5. On pass, agent creates git commit; on persistent failure, worktree is stashed and escalated to human approval queue.

---

## 5. Autonomous Research Systems

Autonomous research requires finding external evidence, parsing complex PDFs, checking claims, and synthesizing reports without inventing citations.

### Anti-Hallucination Pipeline

```
[ Query ] -> [ Web/ArXiv Search API ] -> [ Fetch Raw HTML/PDF ]
                                                 |
                                     [ Unstructured Text Extract ]
                                                 |
                                     [ Vector Store Indexing ]
                                                 |
                                 [ Chunk Rerank + Strict Citation Extraction ]
                                                 |
                                     [ Synthesizer (Local 32B) ]
```

* **Document Processing:** Local PDF parsing using `pdfplumber` and `pypdf` to extract raw text, tables, and section metadata.
* **Evidence & Claim Mapping:** Extracted chunks are stored in SQLite (`sqlite-vec`). The synthesizer model is prompted with strict grounding: *Every assertion must explicitly cite exact document metadata `[DocID: Page]` present in context. If context is insufficient, explicit negative response is enforced.*
* **Contradiction Check Node:** A verification step compares synthesized statements against raw retrieved passages using a dual-pass evaluation prompt to confirm source fidelity before generating final Markdown outputs.

---

## 6. Durable Memory

An autonomous system operating 24/7 needs persistent storage across system reboots.

### SQLite + `sqlite-vec` Architecture

* **Short-Term Memory (Episodic):** Last N conversation turns and step observations stored directly in agent state tables.
* **Long-Term Memory (Semantic):** Text snippets embedded using a fast local embedding model (`bge-small-en-v1.5`, ~130 MB memory footprint running via `onnxruntime` or `mlx`). Embedded vectors are saved in SQLite tables with the `sqlite-vec` extension enabled.
* **Hybrid Search:** Combines SQLite `FTS5` full-text BM25 keyword search with `sqlite-vec` cosine similarity scores using Reciprocal Rank Fusion (RRF). This avoids running standalone vector database daemons (like Qdrant or Milvus) that constantly consume background memory.

---

## 7. Machine Control and Isolation

Autonomous agents executing arbitrary shell commands present system security risks. Absolute security boundaries are required.

### Multi-Layered Security Boundary

* **Dedicated macOS User Account:** System runs under a non-administrator macOS user account named `ai-worker`. This account has no access to primary user credentials, keychains, desktop folders, or personal documents.
* **macOS Sandbox (`sandbox-exec`):** Agent commands execute wrapped in custom `.sb` profiles limiting filesystem access exclusively to target project workspace directories and preventing execution of dangerous binary utilities (`sudo`, `diskutil`, `dscl`).
* **Network Isolation:** Outbound web scraping tools are restricted via internal proxy to HTTPS (ports 443/80). Local network access to local home routers or non-essential loopback interfaces is restricted via macOS Application Firewall settings.

---

## 8. Running 24/7

To maintain continuous operational status, the workstation must automatically survive panics, power blips, model crashes, and system sleep states.

### Process Supervision & macOS Integration

* **Power Management:** Executed via system service: `caffeinate -dimsu` running continuously to prevent macOS display sleep, system sleep, or idle disk spindown.
* **Daemon Management:** Managed by native macOS `launchd` service files installed in `/Library/LaunchDaemons/com.autonomous.aiworkstation.plist`.
* `KeepAlive: true` ensures instant process restart upon unhandled runtime termination.
* `ThrottleInterval: 10` prevents crash loop thrashing.

* **State Recovery:** On startup, the supervisor daemon reads SQLite task tables, identifies any task marked `IN_PROGRESS` prior to shutdown, reverts the affected worktree, and re-queues the task with a `REBOOT_RECOVERY` flag.

---

## 9. Remote Reach

Operators must monitor system status, issue commands, and approve high-risk actions remotely from an iPhone or mobile device safely.

### Tailscale + Secure Telegram Operator Bot

* **Network Transport:** Tailscale mesh VPN creates an encrypted, peer-to-peer overlay network. Zero open inbound router ports.
* **Interaction Layer:** A lightweight asynchronous Telegram Bot daemon listening via long-polling or webhooks over Tailscale.
* **Capabilities:**
* *Notifications:* Sends structured status summaries, job completions, and errors directly to the operator's phone.
* *Approvals:* Interactive inline buttons (`[Approve Task]` / `[Reject]`) for operations exceeding privilege thresholds (e.g., git push to main, network outbound API calls).
* *Emergency Stop:* Instant command (`/kill`) triggers a hardware shutdown of active sub-agent child shell processes via `SIGTERM`/`SIGKILL` cascades.

---

## 10. Storage Split

Proper drive partition and allocation prevent OS drive saturation and maximize overall I/O performance.

```
[ 512 GB Internal NVMe SSD ]
├── / (macOS System & Core Applications)
├── /Users/ai-worker/daemon/ (Orchestrator code & Python virtualenvs)
└── /Users/ai-worker/db/ (SQLite State DB & FTS Vector Indexes)

[ 1 TB External USB4/Thunderbolt SSD ]
├── /Volumes/ExternalSSD/models/ (GGUF Weights: Qwen 32B, 7B, Embeddings)
├── /Volumes/ExternalSSD/workspaces/ (Active Git Worktrees & Repositories)
├── /Volumes/ExternalSSD/datasets/ (Scraped PDFs, Literature & Raw HTML caches)
└── /Volumes/ExternalSSD/logs/ (System Logs & Comprehensive Audit Trails)
```

---

## Deliverable A: Technology Stack Table

| Layer | Chosen Technology | Alternatives Considered | Rationale |
| --- | --- | --- | --- |
| **Hardware / OS** | Apple Mac mini M6 (32GB / 512GB + 1TB) | Mac Studio M2 Max, Intel NUC | High unified memory bandwidth (~150-200 GB/s) at low idle power draw (~5W). |
| **Local LLM Engine** | `llama.cpp` (`llama-server`) | Ollama, vLLM, MLX Server | Superior control over GGUF quantization, Metal optimization, and KV cache quant. |
| **Primary Code Model** | Qwen2.5-Coder-32B-Instruct (Q4_K_M) | DeepSeek-Coder-V2-Lite, Llama-3.1-70B | Fits within 21.6 GB VRAM budget while offering top-tier code synthesis. |
| **Fast Utility Model** | Qwen2.5-7B-Instruct (Q4_K_M) | Llama-3.1-8B, Mistral-7B | Sub-second latency for lightweight text tasks with low memory consumption. |
| **Orchestration** | Custom `asyncio` + `LangGraph` | AutoGen, CrewAI | Direct control over agent execution loops without heavy dependency bloat. |
| **Coding Engine** | Aider (Headless CLI Driver) | OpenHands, Custom Shell Scripting | Built-in tree-sitter indexing, git diff handling, and automated test loops. |
| **Vector Indexing** | SQLite (`sqlite-vec`) + `bge-small-en` | Qdrant, ChromaDB, PGVector | In-process native vector search with zero background service memory overhead. |
| **Isolation** | `sandbox-exec` + Dedicated User | Docker Desktop, UTM VMs | Native performance execution with hard path restrictions and no hypervisor overhead. |
| **Process Daemon** | macOS `launchd` + `caffeinate` | PM2, Systemd | Native macOS autostart daemon system with built-in hardware sleep inhibition. |
| **Remote Access** | Tailscale + Telegram Bot API | SSH, Cloudflare Tunnels, Ngrok | Secure encrypted mesh network connectivity with zero public inbound ports. |

---

## Deliverable B: Architecture Diagram

```
+-----------------------------------------------------------------------------------+
|                              OPERATOR INTERFACE                                   |
|       [ Tailscale VPN ] <---> [ Telegram Bot / Web Mobile Dashboard ]             |
+---------------------------------------+-------------------------------------------+
                                        | (HTTPS / Webhook)
                                        v
+-----------------------------------------------------------------------------------+
|                    SUPERVISOR DAEMON (macOS launchd Service)                      |
|  Task Dispatcher & Priority Queue (Async Event Loop)                              |
|  State Persistence & Memory Layer (SQLite + sqlite-vec WAL Mode)                  |
+---------------------------------------+-------------------------------------------+
                                        | (Task Assignment & Semaphore Gate)
                                        v
|                        AGENT WORKER POOL (Logical Nodes)                          |
|  Coding Agent (Aider) · Research Agent (Web) · System Review Agent                |
                                        | (Inference Requests)
                                        v
|                 LOCAL INFERENCE SERVER (llama.cpp - Metal GPU)                    |
|  Qwen2.5-Coder-32B-Instruct GGUF (Q4_K_M) + Q4_0 KV Cache (~21.6 GB Unified VRAM) |
                                        | (File IO & Execution)
                                        v
|                   ISOLATED SYSTEM STORAGE & SANDBOX (USB4 SSD)                    |
|  macOS Sandbox Profile (`sandbox-exec`) -> Restricted Access to /Volumes/Ext      |
|  Git Worktrees/Repos · Literature & PDF Cache · Execution Logs                    |
```

---

## Deliverable C: Resource Plan

### Memory Allocation Budget (32 GB Unified RAM)

```
macOS System Overhead & Graphics Buffer           :  6.0 GB
llama-server (Qwen2.5-Coder-32B Q4_K_M Weights)    : 19.8 GB
llama-server 16k Context Window (Q4_0 KV Cache)    :  1.8 GB
SQLite Vector Index & Local Embeddings Buffer      :  0.4 GB
Python Async Runtime & Agent State Nodes           :  0.5 GB
Active Tool Execution (Headless Browser / Aider)   :  1.5 GB
Dynamic System Headroom / Buffer                   :  2.0 GB
TOTAL ALLOCATED UNIFIED MEMORY                     : 32.0 GB
```

### Storage Allocation (512 GB Internal + 1 TB External SSD)

* **Internal 512 GB SSD:** macOS ~100 GB · Python/CLI ~30 GB · SQLite DB ~20 GB · reserve ~362 GB.
* **External 1 TB SSD:** GGUF model repo ~200 GB · repos/worktrees ~300 GB · PDFs/HTML cache/index ~250 GB · logs/backups ~250 GB.

---

## Deliverable D: Agent Model

Each agent = a row in an SQLite `agents` table with a JSON blob (`agent_id`, `status`, `current_step`, `task_memory`, `context_summary`). A Python `asyncio` event loop loads the state JSON only when the agent is actively executing. On inference need, the agent enters a `PriorityQueue`; a global semaphore enforces `max_concurrent_llm_calls = 1`; the agent runs inference via `llama-server`, updates its JSON in SQLite, yields the GPU. 100 idle logical agent nodes consume 0 MB VRAM and < 10 MB system RAM.

---

## Deliverable E: Model Assignment

| Task Category | Assigned Model Engine | Host |
| --- | --- | --- |
| Architecture Planning | Qwen2.5-Coder-32B / Claude 3.5 Sonnet (Fallback API) | Local GGUF / Cloud API |
| Code Generation & Editing | Qwen2.5-Coder-32B-Instruct | Local GGUF (Q4_K_M) |
| Debugging & Failure Analysis | Qwen2.5-Coder-32B-Instruct | Local GGUF (Q4_K_M) |
| Research & Web Scraping | Qwen2.5-7B-Instruct | Local GGUF (Q4_K_M) |
| Summarization | Qwen2.5-7B-Instruct | Local GGUF (Q4_K_M) |
| Task Routing & Classification | Qwen2.5-7B-Instruct | Local GGUF (Q4_K_M) |
| Final Synthesis & Reports | Qwen2.5-Coder-32B-Instruct | Local GGUF (Q4_K_M) |

---

## Deliverable F: Continuous-Operation Design

* **State Checkpointing:** Every workflow transition written atomically to SQLite with `PRAGMA journal_mode=WAL;`.
* **Watchdog Script (`watchdog.py`):** Runs every 60 s via `cron` or a secondary `launchd` job; `SIGKILL`s unresponsive processes and re-launches the `launchd` service.
* **Loop Protection:** Every sub-task capped at 10 automated self-correction loops. On 10 consecutive failures: mark `STALLED_REQUIRES_ATTENTION`, save a git diff / failure snapshot, notify Telegram, move to the next queue item.

---

## Deliverable G: Remote-Operation Design

Telegram Bot API commands: `/status`, `/submit [Task Prompt]`, `/approve [Task ID]`, `/kill` (emergency termination — process kills across all child sub-agents). Notification triggers: high-priority task completes; task hits max retry limit or requests privilege escalation.

---

## Deliverable H: Security Design

| Category | Allowed Unattended | Requires Human Approval |
| --- | --- | --- |
| Filesystem | read/write within `/Volumes/ExternalSSD/workspaces/` | writes outside designated workspaces or system folders |
| Shell | `git`, `pytest`, `npm test`, `python3`, `tree-sitter` inside sandbox | `sudo`, `brew install`, `chmod`, system config |
| Network | outbound HTTP/HTTPS to research sources & public APIs | local network IP ranges (192.168.x.x, 10.x.x.x) |
| Git | local `git commit`, `git checkout -b`, `git merge` on dev worktrees | `git push` to remote `main`/`master` |
| Secrets | isolated task-specific temporary API tokens | main personal keychains, `.bash_profile`, system credentials |

---

## Deliverable I: Installation Procedure

```bash
# 1. Create restricted dedicated work directories on external SSD
sudo mkdir -p /Volumes/ExternalSSD/{models,workspaces,datasets,logs}
sudo chown -R $(whoami):staff /Volumes/ExternalSSD/
# 2. Install native system dependencies via Homebrew
brew install llama.cpp git python@3.12 sqlite3 tailscale
# 3. Fetch primary model weights (Qwen2.5-Coder-32B Q4_K_M)
cd /Volumes/ExternalSSD/models
curl -L -O "https://huggingface.co/Qwen/Qwen2.5-Coder-32B-Instruct-GGUF/resolve/main/qwen2.5-coder-32b-instruct-q4_k_m.gguf"
curl -L -O "https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF/resolve/main/qwen2.5-7b-instruct-q4_k_m.gguf"
# 4. Set up Python Orchestrator Virtual Environment
mkdir -p /Volumes/ExternalSSD/daemon && cd /Volumes/ExternalSSD/daemon
python3 -m venv venv && source venv/bin/activate
pip install langgraph litellm aider-chat sqlite-vec pypdf playwright
playwright install chromium
# 5. Configure macOS launchd Service (~/Library/LaunchAgents/com.autonomous.aiworkstation.plist)
#    ProgramArguments = [/usr/bin/caffeinate, -dimsu, .../venv/bin/python3, .../daemon/main.py]
#    RunAtLoad=true, KeepAlive=true, StandardOut/ErrPath to /Volumes/ExternalSSD/logs/
# 6. Launch
launchctl load ~/Library/LaunchAgents/com.autonomous.aiworkstation.plist
```

---

## Deliverable J: Exclusion List

* **Docker Desktop / Heavy Virtual Machines:** severe 4–8 GB static RAM reservation tax. Native `sandbox-exec` used instead.
* **Heavy Standalone Vector Databases (Qdrant, Milvus, ChromaDB):** run background server processes that consume memory continuously. Replaced by `sqlite-vec` in-process.
* **Ollama Daemon:** redundant server abstraction layer; `llama-server` gives direct control over Metal parameters and KV caching.
* **Complex Multi-Agent Frameworks (CrewAI, AutoGen):** context management bloat and difficult state serialization during unexpected reboots.

---

## Deliverable K: Scaling Path

* **Base (32 GB):** Qwen2.5-Coder-32B Q4_K_M, 16k context, 1 heavy model process.
* **64 GB:** Qwen2.5-Coder-32B at Q8_0 or IQ4_NL 70B models; context up to 64k; hold 32B + 7B concurrently.
* **96 / 128+ GB or added GPU:** DeepSeek-Coder-V2 / Llama-3.3-70B locally at Q4/Q8; 2–4 parallel heavy inference streams; continuous local background embedding & reranking.

---

## Sources

1. **llama.cpp GitHub Repository & Documentation** — Metal optimization, `llama-server` deployment, GGUF KV-cache quantization parameters. (Primary Source)
2. **Qwen2.5-Coder Technical Report & Benchmarks (2024-2025)** — HumanEval / LiveCodeBench metrics. (Primary Source)
3. **Apple Silicon Memory Architecture Specifications** — M-series unified memory throughput and macOS graphics allocation limits. (Secondary Source)
4. **SQLite `sqlite-vec` Extension Documentation** — native C-extension vector search. (Primary Source)
5. **Aider Architecture & Multi-File Editing Documentation** — headless Git worktree code generation, automated repository map creation. (Primary Source)

## Model's own cited sources

5-entry list, **names only — no URLs**: "llama.cpp GitHub Repository", "Qwen2.5-Coder Technical
Report & Benchmarks (2024-2025)", "Apple Silicon Memory Architecture Specifications", "sqlite-vec
Extension Documentation", "Aider Architecture Documentation". Browsing was off. Not resolvable
as-given; all point at real projects. Note the explicit "(2024-2025)" date on the Qwen report — a
recency tell for the underlying model.

## Reviewer notes

### Purpose: RQ6 prompt-sensitivity — Gemini v1 vs v2

Compare to `data/responses/gemini-3.1-pro.md` (v1). Tracker: `analysis/rq6-prompt-sensitivity.md`.

### CONFOUND: the free tier served different models across runs

v2 self-reports "Gemini 2.5 Pro" / cutoff "2026". The v3 run self-reports "Gemini 1.5 Pro" /
cutoff "January 2025" — an older model. So **neither v1→v2 nor v2→v3 is a clean phrasing
comparison for Gemini**; the underlying model is not held fixed. v1 and v2 both browsed OFF and
both give a 2024-era model layer, so v1↔v2 is the least-confounded Gemini pair.

### Load-bearing axes vs v1 — barely moved

| axis | v1 | v2 (RFC framing) |
|---|---|---|
| inference engine | llama.cpp server first (Ollama as backend); MLX alt | **llama.cpp (`llama-server`) / mlx-lm**; Ollama excluded — essentially the same |
| primary model | Qwen2.5-Coder-32B dense Q4_K_M (2024) | **Qwen2.5-Coder-32B-Instruct Q4_K_M** — identical |
| reasoning/mid model | DeepSeek-R1-Distill-Qwen-14B (2024) | Qwen2.5-7B-Instruct (utility) — shifted, still 2024-era |
| orchestration | LangGraph core + custom async | **LangGraph core + LiteLLM + custom async** — same |
| coding agent | Aider headless | **Aider headless** — identical |
| vector store | sqlite-vec (no daemon) | **sqlite-vec + WAL** — identical |
| sandbox | dedicated `ai-worker` user + Lima/Docker | **`sandbox-exec` + OrbStack/Docker + dedicated `ai-worker` user** — Lima → OrbStack, otherwise same |
| cloud fallback | "Claude 3.5 Sonnet" / "DeepSeek-V3" (STALE) | **"Claude 3.5 Sonnet"** (STALE — unchanged) |
| M6 facts | none ("generic M-series") | "~150-200 GB/s" range guess, no specifics — still essentially none |
| sources | 0 | 5 project names, 0 URLs |

### RQ6 signal — Gemini is the least framing-sensitive so far

v1 and v2 (both browsing-off, both ~"2.5 Pro" era) are **nearly the same response**: identical
primary model, identical inference engine, identical orchestration, identical coding agent,
identical vector store, identical stale cloud fallback. The RFC paraphrase moved essentially
nothing. This puts Gemini with Perplexity at the low-sensitivity end (contrast GPT-5, whose
#1 engine changed in every framing).

### Fabrication (RQ2) — none

All tools real (llama.cpp, mlx-lm, LangGraph, LiteLLM, Aider, sqlite-vec, `sandbox-exec`,
OrbStack, Playwright, pypdf, pdfplumber, `bge-small-en-v1.5`, `caffeinate`, launchd, Tailscale).
Models all real and 2024-era. Real defect is **recency** (stale cloud fallback, no M6 facts,
"(2024-2025)" dating), not factuality.
