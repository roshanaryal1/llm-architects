---
ai_name: z.ai (Zhipu GLM)
model_version_id: "GLM-5.2 (Z.ai); self-reports knowledge cutoff Late 2024"
provider: Zhipu AI (z.ai)
interface: z.ai chat (free)
browsing_enabled: NO — self-declared "Answering from internal knowledge, projecting to the Aug 2026 ecosystem"; URLs given as "canonical project locations"
knowledge_cutoff: "self-reported Late 2024"
prompt_version: v3
date_run: 2026-09-01
run_by: roshanaryal1
notes_on_run: >
  Third z.ai capture, on prompt-v3 (v1 with the anti-anchoring / anti-popularity steer removed).
  Fresh chat. Full A–K + a 7-entry Sources list of real canonical URLs. Browsing OFF. NOTE:
  this run self-reports cutoff "Late 2024" while the v2 run reported "~mid-2025" — same model
  name (GLM-5.2), different stated cutoff; treat cross-run comparison as noisy. Clean phrasing
  comparison for z.ai is v2 vs v3 (both GLM-5.2, both no-browse).
trust_rating: MEDIUM — all tools/models real, coherent, honest no-browsing disclaimer; more conservative than v2 (Qwen 14B not 30B-A3B, ChromaDB not LanceDB, Docker not sandbox-exec, Redis not SQLite queue). Only 7 sources.
---

## Raw response

Model: GLM-5.2 (Z.ai)
Knowledge cutoff: Late 2024
Web browsing/tools: OFF (Answering from internal knowledge, projecting to the Aug 2026 ecosystem based on current trajectories and stated advancements. URLs provided are based on canonical project locations.)

### Decisions at a Glance

| Layer | Recommended Technology | Alternatives | Why |
| :--- | :--- | :--- | :--- |
| **Local Inference** | `mlx-lm` server + `llama.cpp` | Ollama, vLLM (Apple Silicon fork) | MLX is natively optimized for Apple Silicon unified memory, providing the highest token throughput on M-series chips. |
| **Primary Local Models** | Qwen-2.5/3.0 14B (4-bit), Llama-3.x 8B | Mistral, Phi-4, DeepSeek-Coder-V2 | Qwen 14B fits comfortably in 32GB with large context windows; Llama 8B offers blazing fast utility generation. |
| **Orchestration** | Custom Python asyncio + LangGraph | AutoGen, CrewAI | LangGraph provides stateful, cyclic multi-agent graphs with built-in persistence, essential for 24/7 unattended operation. |
| **Task Queue** | Redis + RQ (Redis Queue) | Celery, RabbitMQ | Extremely lightweight, low memory overhead, perfectly sufficient for managing agent state and job routing on a single machine. |
| **Coding Agent** | Aider (CLI wrapped by orchestrator) | OpenDevin, SWE-agent | Aider has the most mature Git integration, repository-wide understanding, and local model support via LiteLLM. |
| **Persistent Memory** | SQLite + ChromaDB | Postgres, Qdrant | SQLite is zero-config and highly reliable for state/audit logs; ChromaDB is lightweight and local-first for vector embeddings. |
| **Computer Control** | Docker containers + dedicated macOS user | Lima, UTM VMs, bare metal | Docker provides hard filesystem/network sandboxing while maintaining near-native M6 performance via Rosetta 2/virtualization framework. |
| **Remote Access** | Tailscale + FastAPI Web Dashboard | ngrok, Cloudflare Tunnels | Tailscale creates a zero-config WireGuard mesh network, making the Mac mini accessible from a phone without exposing public ports. |
| **24/7 Operations** | `launchd` + Watchdog scripts | systemd (Linux), supervisord | `launchd` is native to macOS, handles restarts on crash, and starts processes at boot without requiring a user login. |
| **Storage Strategy** | Internal: OS, active repos, DBs <br> External: Models, datasets, backups | - | Keeps the high-IOPS internal SSD free for active agent work, while bulk storage handles the multi-gigabyte model weights. |

---

### 1. Local Inference

For a 32 GB unified-memory Apple Silicon machine (M6), the memory bandwidth and unified memory architecture are the primary advantages. 
- **Inference Engine:** Apple's **MLX** framework is the definitive choice. It natively understands unified memory, avoiding the memory copies required by traditional CPU/GPU split frameworks. `mlx-lm` provides an OpenAI-compatible server that can be queried by agent frameworks.
- **Model Selection:** You should avoid running models larger than 14B parameters at high quantization to ensure you have enough RAM for the OS, KV cache, and agent processes. 
  - **Main Workhorse:** Qwen-2.5 (or 3.0) 14B Instruct at 4-bit or 8-bit quantization. It occupies ~8-14 GB of RAM, leaving ~18 GB for the system and context windows. It has exceptional coding, reasoning, and multi-lingual capabilities.
  - **Utility/Small Model:** Llama 3.x 8B Instruct. When loaded, it takes ~4-5 GB. It is incredibly fast for simple classification, routing, and summarization tasks where a 14B model is overkill.
- **Concurrency:** Running two 14B models simultaneously will exceed 32GB when accounting for KV cache and macOS overhead. The system should run **one large model (14B) and one small model (8B) concurrently**, or dynamically swap models using MLX's lazy loading if a specialized coding model (like DeepSeek-Coder) is required. 
- **Context Window:** Allocate ~8K-16K tokens for active coding agents, 4K for utility agents. Do not use 128K context locally on a 32GB machine; the KV cache will consume all available RAM and cause system swapping, reducing throughput to near zero.

### 2. Agent Runtimes / Harnesses

Current agent harnesses like OpenDevin or SWE-agent are excellent for interactive coding but lack the robust, stateful, 24/7 autonomous loop required for unattended operation. 
- **Recommendation:** Build a custom orchestration layer using **LangGraph**. LangGraph allows you to define agents as nodes in a state machine, with conditional edges that allow for loops (e.g., "if tests fail, go back to coding node"). It includes built-in checkpointing, meaning if the Mac mini reboots, the agent graph resumes exactly where it left off.
- **Harness Capabilities:** The orchestrator will expose tool-calling interfaces to the LLM. These tools are Python functions executing Bash commands, reading/writing files, or querying the vector database. By keeping the harness custom, you maintain strict control over permissions and logging, avoiding the bloat of full IDE-in-a-browser harnesses.

### 3. Multi-Agent Architecture

Running 100 simultaneous LLM instances is physically impossible on 32GB of RAM. Instead, you must separate **logical agents** from **physical inference**.
- **Logical Agents:** Agent definitions stored in an SQLite database. Each has a system prompt, role, objective, and state (e.g., "queued," "executing," "blocked," "complete"). You can have 10,000 logical agents.
- **Worker Pool:** The orchestrator maintains a pool of physical execution contexts. On 32GB RAM, you configure a pool of 3-5 workers. 
- **Execution Model:** The task queue (Redis) dispatches tasks to the worker pool. A worker formats the prompt for the specific logical agent, sends it to the local MLX inference server, processes the tool calls, and updates the state in the DB. 
- **Hierarchical Architecture:** Use a Coordinator-Worker pattern. A single "Supervisor" agent (running on the 14B model) breaks down large tasks and enqueues sub-tasks. "Worker" agents (running on the 8B model) pick up the sub-tasks. The Supervisor reviews the results. This maximizes useful throughput.

### 4. Coding Agents

For serious software development, the agent needs deep repository understanding, file editing, and Git control.
- **Recommendation:** Use **Aider** as the core coding engine, wrapped by your orchestrator. Aider is a CLI tool that natively supports local models via LiteLLM, understands repository structure using a repository map (reducing token usage), and directly manages Git commits, branches, and diffs.
- **Isolation:** Each coding task should be executed in a separate `git worktree`. This allows multiple coding agents to work on different features of the same repository simultaneously without overwriting each other's files.
- **Workflow:** Orchestrator spawns worker -> Worker runs Aider in a specific worktree -> Aider edits code -> Worker runs tests -> If pass, Aider commits -> Worker reports back to Supervisor.

### 5. Research Agents

Autonomous research is highly susceptible to hallucinated citations. The architecture must physically prevent the LLM from inventing sources.
- **Search & Retrieval:** Run a local **SearXNG** instance for web metasearch. Use **Playwright** to scrape full-text content from top URLs.
- **PDF Analysis:** Use **PyMuPDF** to extract text from downloaded PDFs.
- **Anti-Hallucination Architecture:** The LLM is strictly forbidden from generating citations. Instead, the LLM generates a search query. The Python backend executes the search, scrapes the content, chunks it, and passes it into the LLM's context window as a retrieved context. The LLM synthesizes the text and provides quotes, but the actual citation IDs are injected by the backend based on which chunks were accessed. 
- **Verification:** A secondary utility model (8B) acts as a "Fact-Checker," cross-referencing the LLM's claims against the source text.

### 6. Persistent Memory

- **State & Audit:** **SQLite**. Fast, zero-config, handles concurrent reads perfectly. Every agent state, task, tool call, and output is logged here.
- **Semantic Memory:** **ChromaDB**. Used to store embeddings of past research, code snippets, and decisions. When an agent starts a new task, it queries ChromaDB for "things I've learned about this repository/topic" to inject into the context window.
- **Filesystem Memory:** A structured directory `/workspace/memory/{projects, research, decisions}` in Markdown. Agents can read/write to this to maintain long-term, human-readable context.

### 7. Computer Control

Broad computer access must be paired with strict boundaries.
- **Sandboxing:** All agent tool execution (Bash, Python) occurs inside a **Docker container** running a lightweight Linux image. The container maps to specific directories on the Mac mini (e.g., a `/workspace` folder) but has no access to the host's home directory, `~/.ssh`, or system files.
- **Git Safeguards:** Agents operate on local branches. Pushing to remote repositories requires a webhook approval from your phone.
- **Network Control:** The Docker container can access the internet for research (ports 80/443) but cannot bind to local network ports, preventing lateral movement.
- **Secrets Management:** Environment variables containing API keys are injected at runtime via a `.env` file owned by the root user, readable by the orchestrator but invisible to the Docker containers.

### 8. Always-on Operation

- **Process Management:** Use macOS native **`launchd`**. Define a `.plist` that starts the Redis server, the MLX inference server, and the Python orchestrator upon boot. Set `KeepAlive` to `true` so if any process crashes, `launchd` automatically restarts it.
- **Sleep Prevention:** Use `caffeinate -d` or a `launchd` argument to prevent the Mac mini from sleeping. Ensure "Restart automatically if the computer freezes" is checked in macOS Energy Saver settings.
- **Task Persistence:** LangGraph checkpoints the entire agent state to SQLite after every node execution. If the power fails, the system boots, `launchd` starts the orchestrator, and the graph resumes from the last known state.

### 9. Remote Access

- **Network:** **Tailscale**. Install on the Mac mini and your phone/laptop. This creates an end-to-end encrypted WireGuard tunnel. You can access the Mac mini's local IP from anywhere in the world without opening router ports.
- **Dashboard:** A lightweight **FastAPI** web server running on the Mac mini, accessible via the Tailscale IP. It provides a dashboard showing active agents, task queues, and logs.
- **Interactions:** The dashboard includes a "Task Submission" form and "Emergency Stop" button. The Emergency Stop triggers a SIGTERM to the orchestrator, gracefully shutting down agents after their current tool execution completes.
- **Notifications:** A simple Telegram bot or Pushover integration sends push notifications to your phone when an agent requires human approval (e.g., "Push to main? Y/N") or when a long-running task completes.

### 10. Storage Architecture

- **Internal 512 GB SSD:** Keep this for high-IOPS operations. 
  - macOS System & Docker Desktop (~50 GB)
  - Active Git repositories and worktrees (~50 GB)
  - SQLite & ChromaDB databases (~20 GB)
  - Temporary agent workspaces (~50 GB)
  - *Rationale:* Fast read/write speeds are crucial for vector databases and Git operations. 
- **External 1 TB SSD:** Use for bulk storage.
  - `/models` directory: Local model weights in MLX/GGUF format (~200 GB for a library of 5-10 models).
  - `/datasets`: Large datasets for analysis (~200 GB).
  - `/research_papers`: Scraped PDFs and literature (~100 GB).
  - `/backups`: Nightly zipped archives of the SQLite DB and local Markdown memory (~50 GB).
  - *Note:* Format the external SSD as APFS or ExFAT. Ensure it is mounted automatically at boot via `/etc/fstab` or Disk Utility.

---

### Deliverables

#### A. Recommended Technology Stack
| Layer | Recommended technology | Alternatives | Why |
| :--- | :--- | :--- | :--- |
| **Interface** | FastAPI + Tailscale + Telegram Bot | Streamlit, Gradio | FastAPI is lightweight, handles WebSockets for live logs, and pairs perfectly with a mobile Telegram bot for push alerts. |
| **Supervisor** | LangGraph StateGraph | AutoGen, CrewAI | LangGraph allows explicit definition of cyclic agent loops with built-in SQLite checkpointing for crash recovery. |
| **Task Queue** | Redis + RQ | Celery, RabbitMQ | Minimal memory footprint (~5MB), highly reliable, perfectly adequate for local single-machine queuing. |
| **Specialized Agents** | Aider (Coding), Custom LangChain tools (Research) | OpenDevin, SWE-agent | Aider wraps Git and LLMs perfectly. Custom tools ensure strict control over research hallucinations. |
| **Model Router** | Custom LiteLLM proxy | OpenRouter | Routes requests to local MLX server based on agent role, seamlessly handling fallback to cloud APIs if allowed. |
| **Local Inference** | `mlx-lm` server | Ollama, llama.cpp | Directly leverages Apple Silicon unified memory without overhead, providing fastest token generation on M6. |
| **Persistent Memory** | SQLite (State) + ChromaDB (Vectors) | Postgres, Qdrant | Zero-config, low resource usage, natively local, perfectly scales for a single-user workstation. |
| **Sandboxing** | Docker Desktop for Mac | Lima, UTM | Provides hard filesystem and network isolation, easy to spin up/tear down per agent task. |
| **Remote Access** | Tailscale | Cloudflare Tunnel, ngrok | Zero-trust WireGuard mesh network. No public ports exposed, accessible from mobile devices seamlessly. |

#### B. Complete Architecture Diagram
```text
[ Mobile Phone / Laptop ]
       |
       v
[ Tailscale Mesh Network (Encrypted) ]
       |
       v
+-------------------------------------------------------------+
|  Mac mini M6 (32GB RAM) - macOS Server                      |
|  Remote Interface (FastAPI + WebSockets) <-> Watchdog/launchd|
|         |                                                    |
|         v                                                    |
|  Orchestrator (LangGraph Python) -> Redis Task Queue         |
|         |                               (Logical Agents)     |
|         v                               |                    |
|  Model Router (LiteLLM)          Worker Pool (Python RQ)      |
|         |                               |                    |
|         v                               v                    |
|  Local Inference (MLX Server)    Docker Sandbox              |
|   - Qwen 14B (4-bit)             (Bash, Git, Playwright)     |
|   - Llama 8B                     /workspace mount            |
|         |                               |                    |
|         v                               v                    |
|  Persistent Memory              Storage Layer               |
|   - SQLite (State)               - Internal SSD             |
|   - ChromaDB (Vectors)           - External SSD             |
+-------------------------------------------------------------+
```

#### C. Hardware/Resource Plan (32 GB RAM Allocation)
- **macOS & System Processes:** ~6.0 GB
- **Docker Desktop & VM overhead:** ~2.0 GB
- **Redis & ChromaDB:** ~1.0 GB
- **MLX Inference Server:**
  - Qwen 14B (4-bit weights): ~8.0 GB
  - Llama 8B (4-bit weights): ~4.5 GB
  - KV Cache (Active contexts): ~4.5 GB
- **Python Orchestrator/Workers:** ~2.0 GB
- **Buffer/Filesystem Cache:** ~4.0 GB
- **Total:** 32.0 GB (Optimized for zero-swap operation)

#### D. Agent Architecture (100+ Logical Agents)
To manage 100+ agents without running 100 LLMs:
1. **Agent Registry (SQLite):** A table defining each agent's `id`, `role`, `system_prompt`, `objective`, and `status` (queued, active, paused, done).
2. **Task Queue (Redis):** When the Supervisor creates a sub-task, it enqueues a message with the `agent_id` and `task_payload`.
3. **Worker Pool (RQ):** Configure 3 persistent Python worker processes. They listen to the Redis queue.
4. **Execution Cycle:**
   - Worker pops task -> queries SQLite for agent definition -> formats prompt -> calls MLX server -> executes tools -> saves results to SQLite -> updates agent status to `done` -> fetches next task.
5. **Concurrency Limit:** The MLX server processes requests sequentially (or interleaved if using continuous batching). 3 workers ensure that while one worker is executing a Bash command (I/O bound), another worker can be waiting for LLM generation (Compute bound).

#### E. Model Strategy
- **Planning & Synthesis:** Qwen 2.5/3.0 14B Instruct. (Requires deep reasoning and context integration).
- **Coding:** Qwen 14B or DeepSeek-Coder 7B/33B (if 33B can be highly quantized). Qwen has excellent multi-language coding benchmarks.
- **Debugging:** Qwen 14B (can read stack traces and apply fixes).
- **Research Summarization:** Llama 3.x 8B Instruct. (Fast, cheap, good enough for text synthesis).
- **Classification & Routing:** Llama 3.x 8B. (Rapidly categorizes tasks to route them to the correct specialized agent queue).
- **Final Synthesis:** Qwen 14B. (Ensures high-quality output for user-facing reports).

#### F. 24/7 Architecture
- **Boot Sequence:** Mac mini powers on after outage -> `launchd` executes `startup.sh`.
- **Startup Script:** Mounts external SSD -> Starts Redis -> Starts MLX server -> Starts FastAPI dashboard -> Starts Orchestrator.
- **Crash Recovery:** If the Orchestrator Python process crashes, `launchd` immediately restarts it. LangGraph loads the last checkpoint from SQLite and resumes the agent loop.
- **Watchdog:** A cron job runs every 5 minutes, checking if the MLX server responds to a ping. If not, it kills and restarts the MLX process.

#### G. Remote-Control Architecture
- **Tailscale:** Runs on Mac mini and phone. Provides IP `100.x.y.z`.
- **FastAPI Dashboard:** Binds to `0.0.0.0:8000`. Accessible via `http://100.x.y.z:8000` from phone browser. Requires Basic Auth or Tailscale-side authentication.
- **Telegram Bot:** Integrated into Orchestrator. Sends push messages:
  - "Task 'Refactor Auth Module' complete. View diff?"
  - "Approval required: Agent wants to run `npm publish`."
- **Emergency Stop:** FastAPI endpoint `/emergency_stop` sets a global flag in Redis. Workers check this flag before every LLM call or tool execution, gracefully halting and dumping state.

#### H. Security Architecture
- **Filesystem Isolation:** Docker containers mount read-write only to `/workspace/projects/{project_name}`. No access to `~/.ssh`, `~/Documents`, or host system files.
- **Network Isolation:** Docker containers are on a restricted bridge network. Outbound traffic allowed on 80/443. Inbound traffic blocked.
- **Git Safeguards:** Agents work on `agent/{task_id}` branches. Committing is allowed. Pushing to `origin` requires webhook approval via FastAPI.
- **Destructive Commands:** A tool blacklist intercepts commands like `rm -rf /`, `sudo`, `dd`, `mkfs`. If detected, task fails immediately, and user is alerted.
- **Credential Isolation:** API keys (if using cloud models) stored in macOS Keychain or root-owned `.env` file. Orchestrator injects them into environment variables at runtime; they are never written to disk in agent workspaces.

#### I. Exact Installation Plan
**Phase 1: Minimal System**
1. Install Homebrew, Python 3.12, Node.js.
2. `brew install redis` and configure to start on boot.
3. `pip install mlx-lm litellm langgraph redis rq fastapi uvicorn`
4. Download Qwen-14B-Instruct-MLX-4bit from HuggingFace.
5. Start `mlx_lm.server --model Qwen-14B-Instruct-MLX-4bit`.

**Phase 2: Autonomous Coding**
1. `pip install aider-chat`.
2. Configure Aider to use local MLX endpoint via LiteLLM.
3. Create `workspace/` directory and clone target repos.
4. Write LangGraph orchestrator script that accepts a coding task, creates a `git worktree`, and runs `aider --message "task"` in subprocess.

**Phase 3: Research Agents**
1. `docker run -d -p 8080:8080 searxng/searxng`.
2. `pip install playwright pymupdf beautifulsoup4`.
3. Write Python tool: `search_web(query) -> returns text`.
4. Write Python tool: `scrape_url(url) -> returns markdown`.

**Phase 4: Persistent Memory**
1. `pip install chromadb`.
2. Initialize ChromaDB client in Orchestrator.
3. Create embedding function using local Llama 8B or sentence-transformers.
4. After every agent task completion, chunk the output and store in ChromaDB.

**Phase 5: Multi-Agent Orchestration**
1. Define Redis Queue `agent_tasks`.
2. Create 3 Python RQ workers: `rq worker agent_tasks`.
3. Update Orchestrator to enqueue tasks instead of executing synchronously.

**Phase 6 & 7: 24/7 & Remote**
1. `brew install tailscale` and authenticate.
2. Create `com.ai.orchestrator.plist` in `~/Library/LaunchAgents/` pointing to `python orchestrator.py`.
3. `launchctl load com.ai.orchestrator.plist`.

#### J. What NOT to Install
- **Ollama:** Unnecessary overhead. MLX provides direct, optimized access to Apple Silicon hardware without an intermediary daemon.
- **VS Code Server / Code Server:** Adds unnecessary bloat. The system is an autonomous CLI agent environment, not a remote IDE.
- **PostgreSQL:** Overkill for a single-user local system. SQLite handles concurrent reads perfectly and requires zero administration.
- **Kubernetes / Docker Swarm:** Absolutely unnecessary for a single Mac mini. `launchd` and Docker Desktop are sufficient.
- **Heavy Desktop Environments (GNOME/KDE via X11):** The Mac mini should run "headless" or with a basic desktop. GUIs waste RAM and CPU cycles needed for LLM inference.

#### K. Future Upgrade Path
- **64 GB Unified Memory:** Run Qwen 32B or DeepSeek-Coder-V2 33B at 4-bit locally with 32k context. Increase RQ worker pool to 6-8 simultaneous agents. Introduce continuous batching in MLX.
- **128 GB Unified Memory (Mac Studio):** Run a 70B parameter model (Llama 3 70B) at 4-bit. This unlocks PhD-level reasoning and complex autonomous software architecture planning. Run 10+ concurrent RQ workers.
- **Dedicated GPU Server:** If offloading inference to a dedicated Linux server with 4x RTX 5090s, the Mac mini becomes purely the orchestrator and interface, communicating with the GPU server via a 10Gbps Tailscale connection. The Mac mini runs zero models, dedicating all 32GB to agent processes, large databases, and massive parallel research scraping.

### Sources
- **MLX Framework:** Apple Machine Learning Research (https://github.com/ml-explore/mlx)
- **LangGraph:** LangChain Documentation (https://langchain-ai.github.io/langgraph/)
- **Aider CLI:** Paul Gauthier (https://aider.chat/docs/)
- **Redis Queue (RQ):** (https://python-rq.org/)
- **ChromaDB:** (https://www.trychroma.com/)
- **Tailscale:** (https://tailscale.com/kb/1017/install)
- **launchd Documentation:** Apple Developer (https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html)

## Model's own cited sources

7-entry Sources list, all real canonical project homes (github.com/ml-explore/mlx,
langchain-ai.github.io/langgraph, aider.chat/docs, python-rq.org, trychroma.com,
tailscale.com/kb, developer.apple.com launchd). Browsing was off; these are pointers, not
retrieved evidence. No arXiv, no model cards, no benchmark sources.

## Reviewer notes

### Purpose: RQ6 — v3 = v1 minus the anti-anchoring / anti-popularity steer

Compare to `z-ai-v2.md` (clean pair — both GLM-5.2, both no-browse) and `data/responses/z-ai.md`
(v1 — different model + broken browse, confounded). Tracker: `analysis/rq6-prompt-sensitivity.md`.

### Cross-run noise flag

v2 self-reported cutoff "~mid-2025"; this v3 run self-reports "Late 2024" — same model name,
different stated cutoff. Free-tier GLM-5.2 may vary run-to-run. Treat v2↔v3 deltas as
directional, not precise.

### Clean comparison — v2 vs v3 (both GLM-5.2, both no-browse)

| axis | v2 (RFC framing) | v3 (no anti-anchoring steer) |
|---|---|---|
| inference engine | MLX-LM #1, llama.cpp 2nd, Ollama UI-only | `mlx-lm` + `llama.cpp` (same); Ollama on the exclusion list |
| primary model | **Qwen3-30B-A3B 4-bit** (MoE, ~16 GB) | **Qwen 2.5/3.0 14B** 4-bit (~8-14 GB) — more conservative |
| coding model | Qwen2.5-Coder-14B Q6 (on demand) | Qwen 14B (same model does coding) |
| orchestration | LangGraph + custom supervisor (~800 lines) | Custom asyncio + LangGraph (same pair) |
| task queue | **SQLite WAL** | **Redis + RQ** — reverses v2's pick; Redis is on v2's exclusion list |
| vector store | **LanceDB** | **ChromaDB** — reverses v2's pick |
| sandbox | **`sandbox-exec` profiles** + dedicated user + `pf` egress allowlist | **Docker Desktop** + dedicated user — reverses v2 ("Docker Desktop heavier" was v2's backup) |
| remote | Tailscale + Caddy + Open WebUI + Telegram | Tailscale + FastAPI dashboard + Telegram (no Caddy, no Open WebUI) |
| research | GPT-Researcher + PaperQA2 | SearXNG + Playwright + PyMuPDF, custom (no named product) |
| embeddings | bge-m3 (named) | "local Llama 8B or sentence-transformers" (unnamed) |
| memory detail | 8 SQLite tables + Markdown ADRs + hash-chained audit | SQLite + ChromaDB + `/workspace/memory/` Markdown |
| # sources | ~45 real URLs | 7 real URLs |
| RAM math | "21 GB resident, bottleneck is RAM", coder swapped | "Total: 32.0 GB, optimized for zero-swap" (sums to exactly 32) |
| security detail | `pf` allowlist, per-domain research allowlist, SHA-256 audit chain | tool blacklist, Docker bridge network, root-owned `.env` |

### RQ6 signal — z.ai runs OPPOSITE to GPT-5 and Qwen on the v3 ablation

For GPT-5 and Qwen, removing the anti-anchoring / anti-popularity steer (v2 → v3) made the answer
**more** product-heavy. For z.ai it made the answer **less** so and **more conservative**: v3
drops to a 14B primary (from 30B-A3B MoE), Redis+ChromaDB+Docker (all three on v2's own exclusion
list), no named research/embedding products, 7 sources vs 45, and a RAM budget that sums to
exactly 32 GB with "zero-swap" (v2 explicitly said the resident set is 21 GB and the coder must
be swapped). Two possibilities: (a) the effect is genuinely model-dependent — GLM-5.2 leans
*conservative* when the "don't just pick popular tools" instruction is removed, or (b) this is
run-to-run variance amplified by the "Late 2024" vs "mid-2025" cutoff difference. Either way it is
a useful counter-example to a simple "steer removal → more products" rule. Architecture *shape*
(coordinator/worker, logical agents as DB rows, one heavy + small, launchd, Tailscale, dedicated
user) is unchanged across v1/v2/v3.

### Fabrication (RQ2) — none

Every tool real: MLX, mlx-lm, llama.cpp, LangGraph, Redis/RQ, Aider, SQLite, ChromaDB, Docker,
Tailscale, FastAPI, SearXNG, Playwright, PyMuPDF, `launchd`, LiteLLM. Models conservative and
real (Qwen 2.5/3.0 14B, Llama 3.x 8B, DeepSeek-Coder). No invented sizes (contrast v1's
"Qwen3-Coder-Next 8B"). No internal contradiction beyond the "zero-swap" claim on a budget that
sums to exactly 32 GB (a dim-1 slip, not a contradiction).
