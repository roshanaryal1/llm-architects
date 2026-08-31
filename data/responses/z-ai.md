---
ai_name: z.ai (Zhipu GLM)
model_version_id: "z.ai chat (chat.z.ai), free. User labelled 'z.ai'. Underlying model is a GLM (GLM-4.6 / 4.7 class); exact build not disclosed in-answer. It recommends its own GLM-4.5-Air as the fast utility model."
provider: Zhipu AI
interface: web app (z.ai, free)
browsing_enabled: yes — uses `【turn0searchN】` result markers (~10 distinct), but no resolvable URLs (same category as kimi-instant's inline markers)
knowledge_cutoff: unknown; no M6-specific facts (generic "Apple Silicon / unified memory")
prompt_version: v1
date_run: 2026-08-31
run_by: roshanaryal1
notes_on_run: >
  Emoji-headed report with Mermaid diagrams, `<details>` code blocks, an 8-phase 14-week roadmap,
  and the A-K deliverables. Cites via `【turn0searchN】` markers throughout. Did not emit the
  requested header line or a resolvable Sources list.
trust_rating: MEDIUM (leaning MEDIUM-LOW) — architecture shape is fully consensus-aligned and no invented ecosystem, but 0 usable sources, no M6 facts, its load-bearing primary pick is a fabricated size ("Qwen3-Coder-Next 8B" — the real model is an 80B MoE), it has internal inconsistencies (5 GB vs 14 GB for the same model; Qwen3-Coder-Next vs Devstral as "the" coding model), it relies on swap ("Fits within 32GB RAM with swapping"), and it assumes a 3rd drive (2 TB HDD) not in the spec. Response 13 / system 11.
---

## Raw response

# 🏗️ Comprehensive Architecture for a 24/7 Autonomous AI Workstation on Apple Silicon

## 📊 Executive Summary & Key Recommendations

Based on extensive research of the current (2026) technology ecosystem, I've designed a complete architecture for your 32GB M6 Mac mini that enables **autonomous, always-on AI operation** with minimal cloud dependency. The system leverages Apple's **MLX framework** for optimized local inference, **vLLM-MLX** for high-throughput serving, and a **hierarchical agent architecture** that can manage 100+ logical agents without exhausting memory resources.

**Core Decision**: For your specific hardware (M6/32GB), the optimal approach is a **MLX-native inference stack** with **dynamic model routing** and a **worker-pool architecture** that maintains 2-3 concurrent model instances while handling dozens of queued agent tasks.

```mermaid
flowchart LR
    A[User Remote Control] --> B[Always-on Supervisor]
    B --> C[Agent Orchestrator]
    C --> D[Task Queue]
    D --> E[Worker Pool<br/>2-3 Concurrent Models]
    E --> F[Model Router]
    F --> G[Local Inference<br/>MLX/vLLM-MLX]
    G --> H[Tool Layer]
    H --> I[Persistent Memory]
```

## 🔬 1. Local Inference Engine Analysis

### Comparative Assessment of Inference Options

| Engine | Apple Silicon Optimization | Throughput (tok/s) | Tool Calling Support | Concurrency | Maturity | Recommendation |
|--------|----------------------------|-------------------|---------------------|-------------|----------|----------------|
| **vLLM-MLX** | Native MLX, continuous batching | 130-464 (Qwen3.5) 【turn0search8】【turn0search21】 | Excellent (MCP native) | High (3.4x speedup) | Production-ready | **★ Best Overall** |
| **MLX-LM Server** | Native, Apple-developed | 100-130 (via HTTP) 【turn0search21】 | Good (with configuration) | Medium | Stable | Good alternative |
| **llama.cpp** | Metal backend, good optimization | 50-90 (typical) | Built-in tools (`--tools all`) 【turn0search10】 | Low-Medium | Very mature | Fallback option |
| **Ollama** | Wrapper around llama.cpp/MLX | 30-70 (typical) | Basic | Low | Easy but limited | Not recommended |

**Key Findings**:
- **vLLM-MLX** delivers **2-3x higher throughput** than alternatives on Apple Silicon through continuous batching and paged KV cache 【turn0search8】【turn0search21】
- MLX's unified memory architecture eliminates CPU-GPU data transfers, critical for your 32GB system 【turn0search22】【turn0search38】
- **Tool calling** is essential for agentic workloads—vLLM-MLX has native MCP support, while llama.cpp requires `--tools all` flag and has known bugs in file editing tools 【turn0search10】

### Model Selection for 32GB Unified Memory

Memory Allocation Breakdown:
```
macOS + System Services:    ~4GB
vLLM-MLX Server Process:   ~2GB
Model Weights (Primary):   ~14GB (Qwen3-Coder-8B at 4-bit)
KV Cache (32k context):    ~6GB
Agent Processes & Tools:    ~4GB
Buffer/Caching:            ~2GB
Total:                     ~32GB
```

**Recommended Model Strategy**:

| Model Type | Recommended Model | Size (4-bit) | Context | Speed (tok/s) | Use Case |
|------------|-------------------|--------------|---------|---------------|----------|
| **Primary Coding** | Qwen3-Coder-Next 8B | ~5GB | 32K | 60-80 【turn0search23】 | Complex code generation, refactoring |
| **Fast Utility** | GLM-4.5-Air 4-bit | ~4GB | 8K | 40-54 【turn0search27】 | Quick completions, summaries |
| **Research** | Mistral Small 3.1 4-bit | ~6GB | 16K | 20-35 【turn0search17】 | Document analysis, web research |
| **Fallback** | Qwen3.5-0.8B | ~1GB | 8K | 100+ | Simple classifications, routing |

**Critical Insight**: Do not attempt to load all models simultaneously. Implement a **model swapping strategy** where the primary coding model remains loaded, with others loaded on-demand by the model router.

## 🤖 2. Agent Runtime & Orchestration Architecture

### Agent Hierarchy Design

Supervisor Agent → Coordinator Agent → {Coding Agent Pool (Frontend/Backend/Database/DevOps Specialist), Research Agent Pool (Web Search/Academic Literature/Data Analysis/Fact-Checking Specialist), Documentation Agent, Testing Agent}.

### Recommended Agent Runtime: **Custom Orchestration Layer**

**Rationale**: No existing single harness meets all your requirements. Instead, build a **lightweight orchestration layer** using:

1. **Python-based supervisor** (using `asyncio` for concurrency)
2. **Redis** for task queuing and state management
3. **FastAPI** for remote control interface
4. **MCP (Model Context Protocol)** for standardized tool access 【turn0search10】

```python
class AgentSupervisor:
    def __init__(self):
        self.task_queue = RedisQueue()
        self.model_router = ModelRouter()
        self.agent_registry = AgentRegistry()
        self.tool_manager = ToolManager()

    async def run_agent_loop(self, agent_config):
        while True:
            task = await self.task_queue.get_task(agent_config.specialization)
            model = await self.model_router.select_model(task.complexity)
            result = await self.execute_with_tools(model=model, task=task, tools=agent_config.allowed_tools)
            if await self.verify_result(result, task):
                await self.persistent_memory.store(task, result)
                await self.task_queue.mark_complete(task)
            else:
                await self.task_queue.retry_with_modification(task)
```

### Multi-Agent Concurrency Strategy

**The 100-Agent Problem**: You cannot run 100 LLM instances on 32GB. Instead:

1. **Logical Agent Pool**: 100+ agent definitions stored in SQLite with specializations, tools, and permissions
2. **Physical Worker Pool**: Only 2-3 model instances active simultaneously
3. **Task-Based Routing**: Agents are instantiated on-demand based on task requirements
4. **Context Preservation**: Each agent maintains persistent state in SQLite between activations

| Resource | Allocation | Purpose |
|----------|------------|---------|
| **Model Instances** | 2-3 concurrent | Primary coding + research + utility |
| **Agent Processes** | 5-10 lightweight | Python processes with minimal memory footprint |
| **Task Queue** | Unlimited | Redis-based persistent queue |
| **State Storage** | SQLite | Agent states, conversation history, task results |

## 💻 3. Coding Agent Architecture

### Recommended Stack: **Devstral Small 2 + Custom Tools**

**Why Devstral Small 2**:
- Specifically designed for agentic coding workflows 【turn0search31】
- Handles multi-file edits and codebase exploration efficiently
- Works with MLX despite some tokenization issues (workarounds available) 【turn0search34】
- Smaller memory footprint than larger coding models

**Coding Agent Toolset**:

| Tool | Implementation | Security Level |
|------|----------------|----------------|
| **Filesystem** | MCP server-filesystem with restricted paths 【turn0search10】 | Read: Allowed / Write: Approval for >5 files |
| **Terminal** | Sandboxed shell with command whitelist | Safe: Auto / Destructive: Approval |
| **Git** | Direct git commands via subprocess | All operations: Logged |
| **Testing** | pytest/unittest with coverage analysis | Test runs: Auto / Fix attempts: Approval |

**Autonomous Coding Loop**: Receive Task → Analyze Codebase → Plan → Create Branch → Write Code → Run Tests → (pass) Commit & Document → Create PR → Wait for Review; (fail) Debug & Fix → Run Tests.

## 📚 4. Research Agent Architecture

### Anti-Hallucination Research Framework

**Core Principle**: **Evidence-Based Synthesis** with mandatory verification steps.

1. **Source Discovery Layer**: Web search via SerpAPI or Brave Search API; academic databases (Semantic Scholar API, arXiv API); local PDF analysis with PyMuPDF.
2. **Evidence Tracking System**:
   ```python
   class Evidence:
       id: str
       source_url: str
       source_type: str  # 'web', 'academic', 'pdf'
       claim: str
       confidence: float
       verification_status: str  # 'verified', 'contradicted', 'unverified'
       related_evidence: List[str]
   ```
3. **Contradiction Detection**: Embedding-based similarity comparison; LLM-based claim comparison; cross-reference validation.

**Research Workflow**: Research Question → Search Multiple Sources → Extract Claims & Evidence → Verify Each Claim → Detect Contradictions → Synthesize Findings → Generate Report → Human Review if Low Confidence.

## 🧠 5. Persistent Memory Architecture

### Hybrid Memory System

| Memory Type | Technology | Use Case | Growth Pattern |
|-------------|------------|----------|----------------|
| **Episodic** | SQLite + JSON | Conversation history, task results | Linear growth, periodic cleanup |
| **Semantic** | Vector DB (ChromaDB) | Knowledge embeddings, document vectors | Controlled growth with deduplication |
| **Procedural** | Git + Filesystem | Code patterns, successful solutions | Versioned, immutable history |
| **Working** | Redis | Current task context, intermediate results | Ephemeral, cleared after task completion |

```python
class PersistentMemory:
    def __init__(self):
        self.episodic = SQLiteStore('episodic.db')
        self.semantic = ChromaDB('semantic_store')
        self.procedural = GitStore('procedures')
        self.working = RedisStore()

    def store_task_result(self, task, result):
        self.episodic.store({'task_id': task.id, 'description': task.description, 'result': result, 'timestamp': datetime.now(), 'agent_id': task.agent_id})
        knowledge = self.extract_knowledge(result)
        self.semantic.add(documents=[knowledge], metadatas=[{'source': task.id, 'type': 'task_result'}])
        if task.type == 'coding':
            self.procedural.commit(task.files_changed, task.commit_message)
```

## 🖥️ 6. Computer Control & Security Architecture

### Security Model Overview

**Principle**: **Least Privilege with Auditability**

| Operation Type | Autonomous Allowed | Requires Approval | Never Allowed |
|----------------|-------------------|-------------------|---------------|
| **File Read** | ✅ Within project dirs | ⚠️ System directories | ❌ Passwords, keys |
| **File Write** | ✅ Within project dirs | ⚠️ Outside projects | ❌ System files |
| **Command Execution** | ✅ Whitelisted commands | ⚠️ Package installs | ❌ rm -rf, format |
| **Network Access** | ✅ API endpoints | ⚠️ New domains | ❌ Local network scanning |
| **Git Operations** | ✅ Branch, commit | ⚠️ Push to remote | ❌ Force push to main |

**Implementation Layers**:
1. **Dedicated User Account**: Create `ai-agent` user with restricted permissions
2. **Sandboxed Execution**: Use `sandbox-exec` on macOS for process isolation
3. **Credential Isolation**: Store secrets in macOS Keychain, never in files
4. **Network Controls**: Firewall rules limiting outbound connections

Security config: a `/Library/LaunchDaemons/com.ai-agent.supervisor.plist` running `supervisor.py --user ai-agent --config config.yaml` with `RunAtLoad` + `KeepAlive` and log paths under `/var/log/ai-agent/`.

## 🔄 7. 24/7 Operation & Recovery Architecture

**Crash Recovery**: System Start → Launch Supervisor → Check Task Queue → (incomplete) Resume Tasks → Execute with Checkpointing → (not complete) Save State → Crash Recovery → Restart from Checkpoint; (complete) Archive Results → Wait for New Tasks.

**Implementation Components**:
1. **LaunchDaemon** for supervisor process (auto-restart on crash)
2. **Task Checkpointing** to SQLite every 5 minutes
3. **Heartbeat Monitoring** with watchdog process
4. **Log Rotation** to prevent disk fill
5. **Sleep Prevention** via `caffeinate` or PMSET settings

## 📱 8. Remote Control Architecture

### Secure Remote Access Stack

**Recommended Stack**: **Tailscale + Caddy + FastAPI**

| Component | Purpose | Port | Security |
|-----------|---------|------|----------|
| **Tailscale** | VPN mesh, no public exposure | - | WireGuard encryption |
| **Caddy** | Reverse proxy with auth | 443 | Automatic HTTPS |
| **FastAPI** | Control API | 8000 | API key + JWT |
| **Web Dashboard** | Monitoring interface | 8080 | Tailscale access only |

FastAPI endpoints: `POST /tasks/submit`, `GET /tasks/status/{task_id}`, `POST /emergency/stop`, `GET /system/health` — all behind `verify_api_key`.

## 💾 9. Storage Architecture

### Disk Allocation Strategy

| Drive | Content | Size | Backup Strategy |
|-------|---------|------|-----------------|
| **Internal SSD (512GB)** | macOS, applications, model weights, current projects | ~200GB used | Time Machine |
| **External SSD (1TB)** | Git repositories, research papers, datasets, archives | ~400GB used | Weekly backup to cloud |
| **External HDD (2TB)** | Time Machine backups, long-term archives | ~1TB used | Monthly rotation |

Directory structure: `/opt/ai-agent/{bin,config,models,workspace,research,data}`, `/var/ai-agent/{logs,cache,state}`, `/tmp/ai-agent/`.

## 📋 Implementation Roadmap

### Phase 1: Foundation (Week 1-2) — basic local inference and tool calling

```bash
pip install mlx-lm
pip install vllm-mlx
mlx_lm.download --model mlx-community/Qwen3-Coder-Next-8bit
vllm-mlx-server --model mlx-community/Qwen3-Coder-Next-8bit --port 8080 --enable-tool-calling
curl -X POST http://localhost:8080/v1/chat/completions -H "Content-Type: application/json" -d '{"messages": [{"role": "user", "content": "List files in /tmp"}], "tools": [{"type": "function", "function": {"name": "list_files", "parameters": {"path": {"type": "string"}}}}}]}'
```

**Test Plan**: Verify model loads, tool calling works, response times <2s for simple queries.

### Phase 2: Autonomous Coding (Week 3-4) — Git integration, file editing, test execution

```yaml
# config/coding-agent.yaml
specialization: coding
allowed_tools: [filesystem, terminal, git, testing]
model: qwen3-coder-next
context_window: 32768
max_iterations: 10
approval_threshold: 5  # files changed
```

### Phase 3: Research Agents (Week 5-6) — web search, PDF analysis, evidence tracking
SerpAPI integration, PyMuPDF, ChromaDB for evidence storage, contradiction detection logic.

### Phase 4: Persistent Memory (Week 7-8) — SQLite integration, vector storage, knowledge graph

```python
class PersistentMemory:
    def __init__(self):
        self.episodic = SQLiteStore('episodic.db')
        self.semantic = ChromaDB('semantic_store')
        self.working = RedisStore()
```

### Phase 5: Multi-Agent Orchestration (Week 9-10) — task queuing, agent spawning, model routing
Redis for task queue; agent registry in SQLite; model router with complexity assessment; worker pool with 2-3 concurrent agents.

### Phase 6: 24/7 Operation (Week 11-12) — LaunchDaemon, crash recovery, monitoring
Supervisor process with auto-restart; task checkpointing every 5 minutes; log rotation and monitoring; health check endpoints.

### Phase 7: Remote Access (Week 13-14) — secure API, web dashboard, mobile access
Tailscale for VPN; Caddy for reverse proxy; FastAPI for control endpoints; simple web dashboard.

### Phase 8: Optimization (Ongoing)
Performance tuning, model updates, security hardening. Metrics: inference throughput, task completion rate, memory usage patterns, error rates by agent type.

## 📊 Final Architecture Summary

### A. Recommended Technology Stack

| Layer | Technology | Alternatives | Why Selected |
|-------|------------|--------------|--------------|
| **Inference Engine** | vLLM-MLX | MLX-LM Server, llama.cpp | 2-3x faster, continuous batching, native MCP 【turn0search8】【turn0search21】 |
| **Primary Model** | Qwen3-Coder-Next 8B (4-bit) | GLM-4.5-Air, Mistral Small 3.1 | Best coding performance for size 【turn0search23】 |
| **Agent Orchestration** | Custom Python supervisor | CrewAI, LangGraph | Full control, minimal overhead, exact requirements |
| **Task Queue** | Redis | RabbitMQ, Celery | In-memory speed, persistence, simplicity |
| **Persistent Memory** | SQLite + ChromaDB | PostgreSQL, Weaviate | Local, efficient, good enough for 100+ agents |
| **Remote Access** | Tailscale + Caddy + FastAPI | Ngrok, Cloudflare Tunnel | Secure, no public exposure, flexible |
| **Monitoring** | Prometheus + Grafana | Datadog, New Relic | Open-source, self-hosted, comprehensive |

### B. Complete Architecture Diagram

User → Tailscale VPN → Caddy Reverse Proxy → FastAPI Control API → Always-on Supervisor → Agent Orchestrator → Redis Task Queue → Worker Pool (2-3 concurrent: Qwen3-Coder / GLM-4.5-Air / Mistral Small) → Model Router → vLLM-MLX Server → Tool Layer (Terminal / Filesystem / Git / Browser / Python / Research / Documents) → Persistent Memory (SQLite Episodic / ChromaDB Semantic / Filesystem Procedural / Redis Working) → Storage (Internal SSD: Models, System / External SSD: Projects, Research / Backup HDD: Archives).

### C. Hardware/Resource Plan

| Component | Memory Allocation | Storage Allocation | Notes |
|-----------|-------------------|-------------------|-------|
| **macOS + System** | 4GB | 50GB | Includes window manager, services |
| **vLLM-MLX Server** | 2GB | 1GB | Inference engine process |
| **Model Weights** | 14GB | 20GB | Primary model (Qwen3-Coder 4-bit) |
| **KV Cache** | 6GB | - | 32K context window |
| **Agent Processes** | 4GB | 1GB | 5-10 lightweight Python processes |
| **Redis** | 1GB | 1GB | Task queue and working memory |
| **SQLite + ChromaDB** | 1GB | 5GB | Persistent memory stores |
| **Buffer/Caching** | 2GB | 10GB | File system cache, temporary files |
| **Total** | **32GB** | **88GB** | Fits within 32GB RAM with swapping |

### D. Agent Architecture: 100+ Logical Agents

**Key Insight**: 100 logical agents ≠ 100 model instances. Implement: Agent Registry (SQLite, 100+ definitions); Dynamic Instantiation (on-demand by task); Shared Model Resources (2-3 instances serve all agents); Context Preservation (state saved between activations).

```python
class AgentRegistry:
    def __init__(self):
        self.agents = {
            'frontend_specialist': {'model': 'qwen3-coder', 'tools': ['filesystem', 'terminal'], 'permissions': {'write': 'approval_required'}, 'context_template': 'frontend_context.j2'},
            'research_analyst': {'model': 'mistral-small', 'tools': ['web_search', 'pdf_analysis'], 'permissions': {'network': 'restricted'}, 'context_template': 'research_context.j2'},
            # ... 98 more agent definitions
        }
```

### E. Model Strategy by Task Type

| Task Type | Recommended Model | Fallback Model | Why |
|-----------|-------------------|----------------|-----|
| **Complex Coding** | Qwen3-Coder-Next 8B | GLM-4.5-Air | Best code generation and understanding 【turn0search23】 |
| **Quick Completions** | GLM-4.5-Air 4-bit | Qwen3.5-0.8B | Fast inference, good enough quality 【turn0search27】 |
| **Research & Analysis** | Mistral Small 3.1 4-bit | GLM-4.5-Air | Document handling, longer context 【turn0search17】 |
| **Summarization** | GLM-4.5-Air | Mistral Small 3.1 | Fast, accurate summaries |
| **Classification** | Qwen3.5-0.8B | GLM-4.5-Air | Very fast, simple tasks |
| **Final Synthesis** | Qwen3-Coder-Next 8B | Mistral Small 3.1 | High-quality reasoning and writing |

### F. 24/7 Operation Architecture

**Crash Recovery Flow**: Supervisor runs as LaunchDaemon (auto-restart); task checkpointing every 5 minutes to SQLite; heartbeat monitoring every 30 seconds; log rotation daily; sleep prevention via `caffeinate -di`. On crash: LaunchDaemon restarts within 10s → supervisor reads last checkpoint → resumes incomplete tasks → notifies via Tailscale webhook.

### G. Remote Control Architecture

Mobile Device → Tailscale VPN → Mac mini:443 → Caddy Reverse Proxy → Authentication → FastAPI Control API → Supervisor → Task Queue → Agent Execution → Results & Logs → Mobile Dashboard. Dashboard: task submission/monitoring, real-time log streaming, emergency stop, system health, approval requests.

### H. Security Architecture

**Layered Security Model**: Network (Tailscale mesh, no public ports) → Application (API keys, JWT, rate limiting) → Execution (sandboxed processes, restricted user) → Filesystem (path restrictions, permission checks) → Credential (macOS Keychain, no hardcoded secrets) → Audit (comprehensive logging).

```python
async def check_approval_required(operation):
    if operation.type == 'file_write':
        if operation.path.startswith('/Users/'): return True
        if operation.file_count > 5: return True
    elif operation.type == 'command':
        if operation.command in ['rm', 'format', 'mkfs']: return True
        if 'install' in operation.command: return True
    return False
```

### I. Exact Installation Plan

```bash
sudo dscl . -create /Users/ai-agent
sudo dscl . -create /Users/ai-agent UserShell /bin/bash
sudo dscl . -create /Users/ai-agent NFSHomeDirectory /opt/ai-agent
brew install python@3.11 redis node
pip3 install mlx-lm vllm-mlx fastapi uvicorn redis chromadb
sudo mkdir -p /opt/ai-agent/{bin,config,models,workspace}
sudo mkdir -p /var/ai-agent/{logs,cache,state}
sudo chown -R ai-agent:staff /opt/ai-agent /var/ai-agent
# vllm-mlx.yaml: server port 8080 host 127.0.0.1; models qwen3-coder (mlx-community/Qwen3-Coder-Next-8bit, 4bit, 32768) + glm-4.5-air (mlx-community/GLM-4.5-Air-4bit, 4bit, 8192); tool_calling enabled, mcp_servers [filesystem, terminal]
# /Library/LaunchDaemons/com.ai-agent.supervisor.plist -> python3 /opt/ai-agent/bin/supervisor.py --config /opt/ai-agent/config/supervisor.yaml, RunAtLoad + KeepAlive, logs in /var/ai-agent/logs/
sudo launchctl load /Library/LaunchDaemons/com.ai-agent.supervisor.plist
```

### J. What NOT to Install

| Technology | Why Avoid |
|------------|-----------|
| **Ollama** | Wrapper with limited control, slower than vLLM-MLX |
| **LM Studio** | GUI-focused, limited programmatic control |
| **CrewAI** | Overkill for single-machine, heavy dependency |
| **LangChain** | Too abstract, unnecessary complexity for your use case |
| **Docker** | Unnecessary overhead on macOS, native processes sufficient |
| **Kubernetes** | Massive overkill for single machine |
| **Multiple Virtual Machines** | Waste of resources, use process isolation instead |

### K. Future Upgrade Path

**When Upgrading to 64GB+ Memory**: increase concurrent models (4-5 instances); larger models (Qwen3-Coder-32B at 4-bit ~20GB); more agents (15-20 concurrent workers); larger context (64K windows).

**When Adding Dedicated GPU/Server**: offload inference (Mac for orchestration, GPU server for inference); distributed queue; network-attached storage; high-availability (redundant supervisors and failover).

## 🎯 Conclusion & Final Recommendations

For your specific M6 Mac mini with 32GB unified memory: (1) MLX-native inference with vLLM-MLX; (2) custom orchestration layer rather than existing frameworks; (3) hierarchical agent architecture with 2-3 physical workers handling 100+ logical agents; (4) hybrid memory system (SQLite + ChromaDB + filesystem); (5) security-first with dedicated user account + sandboxed execution; (6) Tailscale-based remote access, no public internet exposure.

**Critical Success Factors**: start small (Phase 1 first); monitor memory usage continuously (32GB is tight); implement approval workflows early; regular backups of SQLite databases and config.

## Model's own cited sources

No resolvable URLs. z.ai cites via `【turn0searchN】` result markers (the platform's search-hit
references), ~10 distinct: `turn0search8`, `10`, `17`, `21`, `22`, `23`, `27`, `31`, `34`, `38`.
These indicate a web search was performed but cannot be resolved or checked. Scored as
**0 usable sources** for RQ5, with a note that retrieval occurred (same category as `kimi-instant`).

## Reviewer notes

> ### CORRECTION 2026-09-01 — partial. One flagged item is a REAL defect; the framing changes.
> Web verification (`analysis/verification/tool-model-register.md`):
> - **`Qwen3-Coder-Next 8B` (~5 GB) — this IS a genuine error, and it survives.** The real
>   Qwen3-Coder-Next is an **80B MoE / 3B active** (`huggingface.co/Qwen/Qwen3-Coder-Next`);
>   `gpt-5` and `meta-llama-4` both name it correctly. z-ai uses the wrong-sized version as its
>   load-bearing primary coding pick. Call it a **model-size error**, not "fabrication" — the model
>   is real, the attribute is wrong.
> - **`Claw Code`** (referenced) — real: clean-room Claude Code rewrite after the 2026-03-31
>   source-map leak. Not a fabrication.
> - `vLLM-MLX` — already noted as real; the throughput numbers around it stay `UNRESOLVED`.
> - `Qwen3.5-0.8B` tag — `UNRESOLVED`.
>
> **What survives, unchanged:** the size error above **plus** the internal inconsistencies (5 GB
> vs 14 GB for the same model; Qwen3-Coder-Next vs Devstral as "the" coding model; 3-instance
> co-resident diagram vs on-demand prose), "fits within 32 GB with swapping", no M6-specific
> facts, and the assumed third drive. z-ai remains the softest bucket-2 member — but for real
> reasons (size error + inconsistency + no sourcing), not for inventing an ecosystem, which it
> did not do.

### Trust — MEDIUM, leaning MEDIUM-LOW. Consensus-shaped, but unsourced with a load-bearing fabrication.

### Hallucination (RQ2) — one significant model-attribute fabrication + unattributed numbers
- **`Qwen3-Coder-Next 8B` (~5 GB)** — used as the **primary coding / final-synthesis model**
  throughout (§1, §E, §A, install commands `mlx-community/Qwen3-Coder-Next-8bit`). The real
  **Qwen3-Coder-Next is an ~80B MoE** (`gpt-5` and `meta-llama-4` both name it correctly at 80B and
  reject it for 32 GB). Calling it "8B / ~5 GB" is attribute corruption on a real model — the same
  pattern as `meta-llama-4`'s fake `Qwen3.5-35B-A3B` id. This is z.ai's headline pick, so it
  matters more than an alt-list slip.
- **`vLLM-MLX` is real** (named by `mistral-large-3` and `meta-llama-4` too — `waybarrios/vllm-mlx`
  / `vllm-project/vllm-metal`) — **not** a fabrication. But the numbers around it are invented:
  "130-464 tok/s (Qwen3.5)", "3.4x speedup", "2-3x higher throughput", and the CLI
  `vllm-mlx-server --enable-tool-calling` is likely not the real interface.
- **`GLM-4.5-Air`** — real Zhipu model (mid-2025), recommended here by Zhipu's own chat as the
  fast-utility model. Reasonable but a year dated vs GLM-4.6/4.7; expected self-preference.
- `Qwen3.5-0.8B`, `Mistral Small 3.1` — plausible; `Mistral Small 3.1` is real (2025), the
  `Qwen3.5-0.8B` tag is unverified.
- No invented *tools* or *ecosystems* (unlike `meta-llama-4` / `deepseek-instant`). The fabrication
  is confined to model sizes and benchmark numbers.

### Recency (RQ4) — no M6 facts; model layer partly dated/confabulated
- Title + exec summary say "M6 / 32 GB" but there is **no M6-specific detail** — no 170 GB/s, no
  dual Neural Engine, no core layout, no ship date. Generic "Apple Silicon / unified memory".
  Bucket-2 signal (like `gemini-3.1-pro`, `kimi-instant`, `qwen-3.7-plus`).
- Real current picks: vLLM-MLX, MLX-LM server, MCP, Devstral Small 2, ChromaDB, Redis, Tailscale,
  Caddy, sandbox-exec, LaunchDaemon, Prometheus/Grafana.

### Constraint reasoning (RQ3) — relies on swap; internal inconsistencies
- Resource table sums to "**32 GB … Fits within 32GB RAM with swapping**" — explicitly depends on
  swap, i.e. it does not actually fit. Softer than `deepseek-instant-deepthink`'s "oversubscription
  acceptable" but the same category of wishful budgeting.
- **Inconsistent memory figures for the same model:** §1 table says Qwen3-Coder-Next 8B is "~5 GB",
  the §C resource plan says "Model Weights … ~14 GB (Qwen3-Coder-8B at 4-bit)". An 8B at 4-bit is
  ~4-5 GB; 14 GB is wrong either way.
- **Inconsistent coding-model recommendation:** §1/§E name Qwen3-Coder-Next 8B as primary coding;
  §3 opens "**Recommended Stack: Devstral Small 2**" as *the* coding stack. Never reconciled.
- Worker-pool diagram shows **3 large model instances co-resident** (Qwen3-Coder + GLM-4.5-Air +
  Mistral Small) — against the corpus-wide "1 heavy at a time" rule. `memory_budget.py --preset zai`
  → well over 32 GB.
- Assumes a **third drive** ("External HDD (2TB)") the user's spec does not include (512 GB
  internal + 1 TB external only).

### Internal consistency (RQ6) — several small internal contradictions
- 5 GB vs 14 GB for the same model; Qwen3-Coder-Next vs Devstral as "the" coding model;
  "model swapping strategy … primary model remains loaded" (§1) vs a 3-instance concurrent
  worker-pool diagram (§B). "Docker" on the do-not-install list is consistent with the body
  (no containers used) — that part is clean, unlike `deepseek-expert`.

### Agreements with the anchor (Claude) — the shape is fully consensus
- MLX-family inference (vLLM-MLX / MLX-LM server; llama.cpp fallback; Ollama "not recommended").
- 100+ logical agents = SQLite definitions + task queue + 2-3 physical worker instances;
  on-demand instantiation; state preserved between activations; hierarchical coordinator/worker.
- Custom Python orchestrator (asyncio), NOT CrewAI/LangChain as the backbone; MCP for tools.
- Research = source discovery + evidence table (`claim / source / confidence / verification_status`)
  + contradiction detection + "human review if low confidence" + synthesise from verified evidence.
- Hybrid memory: SQLite episodic + vector semantic + Git procedural + Redis working;
  filesystem + SQLite is the base.
- Dedicated `ai-agent` macOS user + **`sandbox-exec`** isolation + Keychain secrets never in files
  + firewall egress limits + an explicit autonomous / approval / never matrix + audit logging.
- LaunchDaemon `RunAtLoad` + `KeepAlive` + checkpoint every 5 min + heartbeat + log rotation +
  `caffeinate`; resume-from-checkpoint on restart.
- Tailscale mesh, no public ports; FastAPI control API (`/tasks/submit`, `/tasks/status`,
  `/emergency/stop`, `/system/health`); mobile dashboard with an emergency-stop button and
  approval prompts.
- Models on internal SSD; git repos + research + datasets on external SSD.
- "What NOT to install": Ollama, LM Studio, CrewAI, LangChain, Docker, Kubernetes, multiple VMs.

### Divergences vs the anchor
| Axis | z.ai (Zhipu GLM) | Claude (anchor) |
|---|---|---|
| Inference engine | **vLLM-MLX as the primary #1 pick** (first response to do so) | MLX + llama-swap |
| Primary coding model | **"Qwen3-Coder-Next 8B"** (fabricated size) — or Devstral Small 2 (§3) | Qwen3-Coder-30B-A3B |
| Task queue | **Redis** | SQLite table + asyncio |
| Working memory | **Redis** (4th memory tier) | not a separate tier |
| Vector store | **ChromaDB** (with Qwen + DeepSeek fast modes) | sqlite-vec |
| Monitoring | **Prometheus + Grafana** (with DeepSeek-Expert) | custom / minimal |
| Remote proxy | **Caddy** reverse proxy + FastAPI (unique — nobody else adds Caddy) | FastAPI + HTMX + ntfy |
| Concurrency | "2-3 concurrent **model instances**" + a 3-instance diagram | 1 heavy + 2 light + N cloud |
| M6 engagement | none (generic "Apple Silicon") | 170 GB/s, dual NE, ship date |
| Sources | 0 usable (`【turn0searchN】` markers) | ~97 URLs |
