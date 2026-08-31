---
ai_name: Qwen 3.7 Plus
model_version_id: "free Qwen Chat — user labelled 'Qwen 3.7 Plus'; likely Qwen3.7 (Qwen3.8-Max became the flagship on 2026-08-03). Exact ID not shown in-answer."
provider: Alibaba
interface: web app (assumed)
browsing_enabled: unknown — no sources cited, answer reads as from-knowledge
knowledge_cutoff: unknown (stated none; model recommendations are 2024-era — see notes)
prompt_version: v1
date_run: 2026-08-31
run_by: roshanaryal1
notes_on_run: Single message, complete answer. No "Sources" section produced despite the prompt asking for one. Did not emit the requested header line (model/version/cutoff/browsing).
trust_rating: MEDIUM — no sources and 2024-era model picks, but an honest, internally-consistent snapshot with strong process agreement vs the anchor; nothing fabricated.
---

## Raw response

# Autonomous AI Workstation Architecture for 32GB Apple Silicon

## Executive Summary

After analyzing your requirements against the constraints of 32GB unified memory, I've designed a production architecture that prioritizes **useful work per hour** over parameter count. The system uses a **coordinator/worker pattern** with intelligent model routing, running 2-3 models concurrently while supporting 100+ logical agents through task queuing and dynamic instantiation.

**Key insight**: On 32GB unified memory, your bottleneck is memory bandwidth and model loading time, not raw compute. The architecture must minimize model swapping and maximize context reuse.

---

## 1. Hardware Reality Check

### M6 Chip with 32GB Unified Memory

**Memory budget breakdown:**
- macOS + system overhead: ~6-8 GB
- Available for AI workloads: ~24 GB
- KV cache overhead: ~20-30% of model size depending on context length

**Realistic model capacities:**
- Single 32B model (Q4_K_M): ~19-20 GB weights + 4-6 GB KV cache = 24-26 GB total
- Two 14B models (Q4_K_M): ~9 GB each + 3 GB KV each = 24 GB total
- One 32B + one 7B: ~20 GB + 4 GB + 5 GB KV = 29 GB (tight, requires swapping)
- Three 7B models: ~4 GB each + 2 GB KV each = 18 GB total (comfortable)

**Critical constraint**: You cannot run a 70B model at useful quality on 32GB. Even Q3 quantization of 70B requires ~35 GB.

**Recommendation**: Target 30-34B parameter models as your primary workhorses, with 7-14B models for fast routing and specialized tasks.

---

## 2. Local Inference Strategy

### Recommended Stack

**Primary inference engine: MLX**
- Apple's native framework, optimized for Apple Silicon
- Best memory efficiency and throughput on M-series chips
- Native support for quantization (4-bit, 8-bit)
- Active development, tight integration with macOS

**Fallback/alternative: llama.cpp with Metal backend**
- Mature, widely supported
- Excellent quantization options (Q4_K_M, Q5_K_M, Q6_K)
- Good for models not yet ported to MLX

**Serving layer: LocalAI or custom FastAPI wrapper**
- OpenAI-compatible API
- Model routing and load balancing
- Health checks and monitoring

### Model Selection (Optimized for 32GB)

**Primary coding model: Qwen2.5-Coder 32B Instruct (Q4_K_M)**
- Size: ~19 GB
- Best-in-class coding ability at this size
- Strong tool-use and agentic capabilities
- 32K context window (practical: 16-24K on 32GB)

**Primary reasoning/general model: Qwen2.5 32B Instruct (Q4_K_M)**
- Size: ~19 GB
- Strong reasoning, planning, research synthesis
- Can swap with coder model based on task type

**Fast router/classifier: Qwen2.5 7B Instruct (Q4_K_M)**
- Size: ~4.5 GB
- Task classification, routing, summarization
- Always resident in memory

**Specialized models (load on demand):**
- DeepSeek-Coder-V2-Lite (16B) for complex debugging
- Llama 3.2 3B for ultra-fast classification
- Phi-3.5-mini (3.8B) for quick reasoning tasks

### Model Loading Strategy

**Always resident (8-10 GB):**
- 7B router model
- Embedding model (nomic-embed-text or similar, ~1-2 GB)

**Hot-swappable (19-20 GB each):**
- 32B coder model
- 32B reasoning model

**On-demand (load/unload as needed):**
- Specialized models for research, document analysis

**Implementation:**
- Use MLX's model caching to keep weights in memory
- Implement a model manager that tracks usage and preloads likely next models
- Accept 2-5 second load time for model switches

---

## 3. Agent Architecture

### Recommended Approach: Custom Orchestrator + Existing Runtimes

**Do NOT use a single monolithic agent framework.** Instead:

**Core orchestrator: Custom Python layer**
- Task queue (SQLite-based for simplicity, or Redis if you need distributed later)
- Agent lifecycle management
- Model routing logic
- Resource monitoring and throttling

**Specialized runtimes (use existing tools where mature):**

**For coding tasks: Aider**
- Excellent local model support
- Strong Git integration
- Proven architecture for code editing
- Can run as a subprocess or library

**For autonomous research: Custom implementation**
- Web search: SearXNG (self-hosted) or DuckDuckGo API
- PDF processing: PyMuPDF + marker for extraction
- Literature: Semantic Scholar API, arXiv API
- Synthesis: Use your 32B reasoning model

**For general autonomous tasks: OpenHands (formerly OpenDevin)**
- Mature agent runtime
- Supports local models
- Good tool ecosystem
- Can be customized for your workflow

### Why Not Pure LangGraph/CrewAI/AutoGen?

These frameworks add abstraction layers that:
- Increase latency
- Make debugging harder
- Limit fine-grained control over model routing
- Often assume cloud API access

For your use case, you need **tight control over resource usage** and **minimal overhead**. A thin custom orchestrator calling specialized runtimes is more efficient.

---

## 4. Multi-Agent Design (100+ Logical Agents)

### Architecture Pattern: Coordinator/Worker with Task Queue

**Logical agents ≠ model instances**

```
┌─────────────────────────────────────────┐
│         Agent Definitions (100+)        │
│  - Stored as config/prompts in DB       │
│  - Lightweight Python objects           │
│  - No model loaded until activated      │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Task Queue (SQLite/Redis)       │
│  - Prioritized tasks                    │
│  - Dependencies tracked                 │
│  - Retry logic                          │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│      Worker Pool (2-3 concurrent)       │
│  - Each worker = 1 model instance       │
│  - Workers pick tasks from queue        │
│  - Dynamic model loading per task       │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Model Router                    │
│  - Analyzes task requirements           │
│  - Selects optimal model                │
│  - Manages model loading/unloading      │
└─────────────────────────────────────────┘
```

### How It Works

1. **Agent definitions** are stored as metadata (name, role, tools, permissions, system prompt)
2. **Tasks** are created and queued with requirements (e.g., "needs coding model", "needs web access")
3. **Workers** (2-3 max on 32GB) pull tasks from queue
4. **Model router** ensures correct model is loaded before task execution
5. **Agent context** is injected dynamically when task starts
6. **Results** are stored, follow-up tasks created if needed

### Concurrency Strategy

**Sequential execution for most tasks** (safer, easier to debug)

**Parallel execution only when:**
- Tasks are independent (no shared state)
- Different models needed (can load both if memory allows)
- User explicitly requests parallelism

**Example:**
- 1 worker running 32B coder on a complex refactoring
- 1 worker running 7B router doing quick classifications
- 1 worker running research agent with web access

Total memory: ~19 GB + 4.5 GB + 2 GB (browser/tools) = ~25.5 GB ✓

---

## 5. Coding Agent Implementation

### Core: Aider + Custom Wrapper

**Why Aider:**
- Best local model support (tested extensively with Qwen, Llama)
- Excellent Git integration (commits, branches, worktrees)
- Proven edit formats (whole file, diff, unified diff)
- Active development, strong community

**Custom wrapper adds:**
- Task queue integration
- Automatic test execution and iteration
- Long-running task management
- Context management for large repos
- Approval workflows for destructive operations

**Workflow:**
```
Task: "Add user authentication to the API"
  ↓
1. Analyze repo structure (Aider with 32B coder)
2. Plan implementation (32B reasoning model)
3. Create branch: git checkout -b feature/auth
4. Implement changes (Aider iterative editing)
5. Run tests (pytest, jest, etc.)
6. If tests fail:
   - Analyze errors (32B coder)
   - Fix code (Aider)
   - Re-run tests
   - Repeat up to 5 iterations
7. If tests pass:
   - Code review (32B reasoning model)
   - Generate documentation
   - Commit with descriptive message
   - Create PR (optional, requires approval)
```

**Context management for large repos:**
- Use repo-map (Aider feature) to understand structure
- Load only relevant files into context
- Use embeddings to find related code
- Summarize large files before including

---

## 6. Research Agent Implementation

### Custom Research Pipeline

**Components:**

**Web search:**
- SearXNG (self-hosted, privacy-respecting) OR
- DuckDuckGo API (free, no key needed) OR
- Brave Search API (paid, higher quality)

**Academic literature:**
- Semantic Scholar API (free, excellent coverage)
- arXiv API (free, preprints)
- CrossRef API (free, DOI metadata)
- PubMed API (for biomedical)

**PDF processing:**
- marker (best for complex layouts, tables)
- PyMuPDF (fast, good for simple PDFs)
- Unstructured.io (comprehensive but heavier)

**Research workflow:**
```
Task: "Research transformer architectures for time series"
  ↓
1. Query generation (7B router)
   - Generate 5-10 search queries
   - Mix of web and academic sources

2. Source discovery (parallel)
   - Web search → top 20 results
   - Semantic Scholar → top 20 papers
   - arXiv → top 10 papers

3. Source filtering (7B router)
   - Score relevance (1-10)
   - Select top 10-15 sources

4. Deep extraction (32B reasoning)
   - Download PDFs
   - Extract key sections
   - Identify claims, methods, results

5. Evidence collection
   - Extract specific claims with citations
   - Track supporting/contradicting evidence
   - Note methodology details

6. Synthesis (32B reasoning)
   - Identify patterns
   - Note contradictions
   - Generate structured report

7. Verification
   - Cross-check claims across sources
   - Verify citations exist
   - Flag unsupported claims
```

**Preventing hallucinated citations:**
- Always extract direct quotes with page numbers
- Verify DOIs exist via CrossRef API
- Never generate citations from memory
- Use structured output (JSON) for claims + evidence pairs
- Flag any claim without direct source support

---

## 7. Persistent Memory

### Recommended: Hybrid Approach

**Layer 1: Filesystem (immediate, simple)**
```
/workspace/
  memory/
    projects/
      {project-name}/
        decisions.md
        progress.md
        context.md
    research/
      {topic}/
        findings.md
        sources.json
    global/
      preferences.md
      lessons-learned.md
```

**Layer 2: SQLite (structured data)**
```sql
-- Tasks and results
CREATE TABLE tasks (
  id TEXT PRIMARY KEY,
  type TEXT,
  status TEXT,
  created_at DATETIME,
  completed_at DATETIME,
  result TEXT,
  metadata JSON
);

-- Agent interactions
CREATE TABLE interactions (
  id TEXT PRIMARY KEY,
  agent_id TEXT,
  task_id TEXT,
  input TEXT,
  output TEXT,
  model_used TEXT,
  tokens_used INTEGER,
  timestamp DATETIME
);

-- Decisions and rationale
CREATE TABLE decisions (
  id TEXT PRIMARY KEY,
  context TEXT,
  decision TEXT,
  rationale TEXT,
  alternatives TEXT,
  timestamp DATETIME
);
```

**Layer 3: Vector database (semantic search)**
- **ChromaDB** (simple, embedded, good for starting)
- Store: code snippets, research findings, decision rationales
- Embedding model: nomic-embed-text or all-MiniLM-L6-v2

**Layer 4: Knowledge graph (future, if needed)**
- Only add if you need complex relationship queries
- NetworkX or Neo4j (but Neo4j is heavy for 32GB)

**Implementation:**
```python
class MemoryManager:
    def __init__(self):
        self.fs_path = Path("/workspace/memory")
        self.db = sqlite3.connect("/workspace/memory.db")
        self.vector_db = chromadb.PersistentClient(path="/workspace/vectordb")
    
    def store_decision(self, context, decision, rationale):
        # Store in SQLite
        # Store in vector DB for semantic search
        # Append to project-specific markdown file
    
    def recall_similar(self, query, top_k=5):
        # Search vector DB
        # Return relevant past decisions/findings
```

**Start with:** Layer 1 + Layer 2 (filesystem + SQLite)
**Add after 1 month:** Layer 3 (vector DB)
**Add only if needed:** Layer 4 (knowledge graph)

---

## 8. Computer Control & Security

### Control Methods

**Terminal access:**
- Direct subprocess execution
- Sandboxed to specific directories
- Command allowlist/blocklist

**Filesystem access:**
- Direct Python file operations
- Restricted to /workspace and specific project directories
- No access to ~/.ssh, ~/.gnupg, etc. by default

**Browser access:**
- Playwright with headless Chrome
- Separate browser profile (no personal cookies/data)
- Network isolation (can block certain domains)

**Git operations:**
- Full Git access within /workspace
- Cannot push to remotes without approval
- Cannot modify global Git config

### Security Model

**Dedicated user account:**
```bash
sudo sysadminctl -addUser aiworker -fullName "AI Worker" -password randompassword
sudo dscl . -create /Users/aiworker NFSHomeDirectory /Users/aiworker
sudo mkdir -p /Users/aiworker/workspace
sudo chown aiworker:staff /Users/aiworker/workspace
```

**Permission tiers:**

**Tier 1: Fully autonomous (no approval)**
- Read files in /workspace
- Create/edit files in /workspace
- Run tests
- Git operations (local only)
- Web search
- Read-only database queries

**Tier 2: Log and notify (async approval)**
- Install Python packages
- Modify system files in /workspace
- Create Git branches
- Send emails/notifications
- Write to external APIs

**Tier 3: Require explicit approval (sync)**
- Push to Git remotes
- Delete files
- Modify files outside /workspace
- Access network resources (non-search)
- Install system packages
- Any operation marked "destructive"

**Implementation:**
```python
class SecurityManager:
    def check_permission(self, action, context):
        tier = self.classify_action(action)
        
        if tier == 1:
            return True
        
        elif tier == 2:
            self.log_action(action, context)
            self.notify_user(action, context)
            return True
        
        elif tier == 3:
            self.log_action(action, context)
            approval = self.request_approval(action, context)
            return approval
    
    def request_approval(self, action, context):
        # Send notification via Telegram/email
        # Wait for user approval (with timeout)
        # Return True/False
```

**Emergency kill switch:**
- Watchdog process monitors agent activity
- Can kill all agent processes: `pkill -f "python.*agent"`
- Revoke network access: `sudo pfctl -d`
- Revert Git changes: `git reset --hard`

**Resource limits:**
- Max tokens per task: 100K
- Max runtime per task: 2 hours
- Max file operations per hour: 1000
- Max network requests per hour: 100

---

## 9. Always-On Operation

### Service Management

**Primary: launchd (macOS native)**

Create `/Library/LaunchDaemons/com.aiworkstation.orchestrator.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.aiworkstation.orchestrator</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/opt/aiworkstation/orchestrator.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/var/log/aiworkstation/orchestrator.log</string>
    <key>StandardErrorPath</key>
    <string>/var/log/aiworkstation/orchestrator.error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin</string>
    </dict>
</dict>
</plist>
```

**Load the service:**
```bash
sudo cp com.aiworkstation.orchestrator.plist /Library/LaunchDaemons/
sudo launchctl load /Library/LaunchDaemons/com.aiworkstation.orchestrator.plist
```

**Prevent sleep:**
```bash
sudo pmset -a sleep 0
sudo pmset -a disksleep 0
sudo pmset -a displaysleep 0
caffeinate -s &  # Keep system awake
```

### Crash Recovery

**Orchestrator watchdog:**
```python
class Orchestrator:
    def __init__(self):
        self.task_queue = TaskQueue()
        self.worker_pool = WorkerPool(max_workers=3)
        self.checkpoint_interval = 300  # 5 minutes
    
    def run(self):
        while True:
            try:
                self.check_workers()
                self.process_queue()
                self.checkpoint_state()
                time.sleep(1)
            except Exception as e:
                self.log_error(e)
                self.recover()
    
    def checkpoint_state(self):
        # Save current state to disk
        # Allows recovery after crash
        with open('/workspace/state/checkpoint.json', 'w') as f:
            json.dump({
                'active_tasks': self.worker_pool.get_active_tasks(),
                'queue_state': self.task_queue.get_state(),
                'timestamp': time.time()
            }, f)
    
    def recover(self):
        # Load last checkpoint
        # Restart interrupted tasks
        # Clean up orphaned processes
        pass
```

**Task persistence:**
- All tasks stored in SQLite before execution
- Status updates written immediately
- On restart, incomplete tasks are re-queued

**Process monitoring:**
```bash
# Watchdog script (runs every minute via cron)
#!/bin/bash
if ! pgrep -f "orchestrator.py" > /dev/null; then
    echo "Orchestrator not running, restarting..." | mail -s "AI Workstation Alert" user@example.com
    sudo launchctl start com.aiworkstation.orchestrator
fi
```

---

## 10. Remote Access

### Recommended: Tailscale + Web Dashboard

**Tailscale (secure VPN-like access):**
```bash
# Install Tailscale
brew install tailscale

# Start Tailscale
sudo tailscale up

# Now your Mac is accessible from anywhere via Tailscale network
# SSH, web dashboard, etc. all secured by Tailscale
```

**Web dashboard (FastAPI + simple frontend):**
```python
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/api/status")
async def get_status():
    return {
        "active_tasks": orchestrator.worker_pool.get_active_tasks(),
        "queue_length": orchestrator.task_queue.length(),
        "models_loaded": model_router.get_loaded_models(),
        "memory_usage": get_memory_usage(),
        "uptime": get_uptime()
    }

@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    await websocket.accept()
    # Stream live logs to dashboard
    async for log in log_stream():
        await websocket.send_text(log)
```

**Telegram bot for notifications/commands:**
```python
from telegram import Update
from telegram.ext import Application, CommandHandler

async def status_command(update: Update, context):
    status = orchestrator.get_status()
    await update.message.reply_text(f"Status: {status}")

async def stop_command(update: Update, context):
    orchestrator.emergency_stop()
    await update.message.reply_text("Emergency stop activated")

# Add task
async def task_command(update: Update, context):
    task_description = ' '.join(context.args)
    orchestrator.task_queue.add_task(task_description)
    await update.message.reply_text(f"Task added: {task_description}")
```

**SSH access:**
```bash
# Enable SSH on Mac
sudo systemsetup -setremotelogin on

# Connect from anywhere via Tailscale
ssh user@your-mac.tailnet-name
```

**Security:**
- All access via Tailscale (no public internet exposure)
- SSH key authentication only (no passwords)
- Web dashboard requires Tailscale authentication
- Telegram bot requires user ID whitelist

---

## 11. Storage Architecture

### Internal SSD (512 GB) - High Performance

**Allocation:**
- macOS + system: ~30 GB
- Models (MLX format): ~80 GB
  - Qwen2.5-Coder 32B Q4_K_M: 19 GB
  - Qwen2.5 32B Q4_K_M: 19 GB
  - Qwen2.5 7B Q4_K_M: 4.5 GB
  - Embedding models: 2 GB
  - Reserve for additional models: 35 GB
- Databases: ~20 GB
  - SQLite (tasks, interactions, decisions): 5 GB
  - ChromaDB (vector embeddings): 10 GB
  - Reserve: 5 GB
- Active projects: ~100 GB
  - Current coding projects: 50 GB
  - Active research: 30 GB
  - Temporary workspaces: 20 GB
- Logs and checkpoints: ~20 GB
- Application data: ~30 GB
  - Python environments: 15 GB
  - Browser data: 5 GB
  - Tools and utilities: 10 GB
- Free space (SSD health): ~50 GB

**Total: ~330 GB used, 182 GB free**

### External SSD (1 TB) - High Capacity

**Allocation:**
- Git repositories (all projects): ~200 GB
- Research papers and datasets: ~300 GB
- Backups: ~200 GB
  - Daily database backups
  - Weekly project snapshots
  - Monthly full system backup
- Archives: ~200 GB
  - Completed projects
  - Old research
  - Historical logs
- Free space: ~100 GB

**Mount point:** `/Volumes/ExternalSSD`

**Symlinks for frequently accessed data:**
```bash
ln -s /Volumes/ExternalSSD/repos /workspace/repos
ln -s /Volumes/ExternalSSD/research /workspace/research
```

**Performance considerations:**
- External SSD via USB-C/Thunderbolt: ~1-2 GB/s (good enough for most tasks)
- Keep models and databases on internal SSD for speed
- Git operations on external SSD are fine (mostly sequential reads/writes)

---

## 12. Complete Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      User Interfaces                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   Web    │  │ Telegram │  │   SSH    │  │  Local   │   │
│  │Dashboard │  │   Bot    │  │ Terminal │  │ Terminal │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼──────────────┼──────────────┼──────────────┼────────┘
        └──────────────┴──────────────┴──────────────┘
                           │
                    ┌──────┴──────┐
                    │   Tailscale │
                    │   (Secure   │
                    │    Access)  │
                    └──────┬──────┘
                           │
┌──────────────────────────┼──────────────────────────────────┐
│              Always-On Supervisor (launchd)                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  - Crash recovery                                   │   │
│  │  - Health monitoring                                │   │
│  │  - Automatic restart                                │   │
│  │  - Resource limits enforcement                      │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────┼──────────────────────────────────┐
│              Agent Orchestrator (Python)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Task Queue   │  │   Security   │  │   Memory     │     │
│  │  (SQLite)    │  │   Manager    │  │   Manager    │     │
│  └──────┬───────┘  └──────────────┘  └──────────────┘     │
│         │                                                   │
│  ┌──────┴───────────────────────────────────────────────┐  │
│  │              Worker Pool (2-3 workers)                │  │
│  │  ┌────────┐  ┌────────┐  ┌────────┐                 │  │
│  │  │Worker 1│  │Worker 2│  │Worker 3│                 │  │
│  │  └───┬────┘  └───┬────┘  └───┬────┘                 │  │
│  └──────┼───────────┼───────────┼──────────────────────┘  │
│         └───────────┴───────────┘                          │
│                    │                                        │
│           ┌────────┴────────┐                              │
│           │  Model Router   │                              │
│           │  - Task analysis│                              │
│           │  - Model select │                              │
│           │  - Load/unload  │                              │
│           └────────┬────────┘                              │
└────────────────────┼───────────────────────────────────────┘
                     │
┌────────────────────┼───────────────────────────────────────┐
│           Local Inference (MLX + llama.cpp)                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Qwen2.5-    │  │  Qwen2.5-    │  │  Qwen2.5-    │    │
│  │  Coder 32B   │  │  32B         │  │  7B          │    │
│  │  (coding)    │  │  (reasoning) │  │  (router)    │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└────────────────────────────────────────────────────────────┘
                     │
┌────────────────────┼───────────────────────────────────────┐
│                    Tools Layer                              │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ │
│  │Terminal│ │   FS   │ │  Git   │ │Browser │ │Research│ │
│  │        │ │        │ │        │ │        │ │        │ │
│  │subproc │ │Python  │ │GitPython│ │Playwrgt│ │Custom  │ │
│  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘ │
│  ┌────────┐ ┌────────┐ ┌────────┐                         │
│  │ Python │ │  Docs  │ │ Aider  │                         │
│  │        │ │        │ │        │                         │
│  │execute │ │PyMuPDF │ │Code ed │                         │
│  └────────┘ └────────┘ └────────┘                         │
└────────────────────────────────────────────────────────────┘
                     │
┌────────────────────┼───────────────────────────────────────┐
│              Persistent Memory Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Filesystem  │  │    SQLite    │  │   ChromaDB   │    │
│  │  (markdown)  │  │  (structured)│  │  (vectors)   │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└────────────────────────────────────────────────────────────┘
                     │
┌────────────────────┼───────────────────────────────────────┐
│                 Storage Layer                                │
│  ┌─────────────────────────┐  ┌─────────────────────────┐ │
│  │   Internal SSD (512GB)  │  │   External SSD (1TB)    │ │
│  │   - Models              │  │   - Git repos           │ │
│  │   - Databases           │  │   - Research papers     │ │
│  │   - Active projects     │  │   - Backups             │ │
│  │   - Logs                │  │   - Archives            │ │
│  └─────────────────────────┘  └─────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

---

## 13. Implementation Roadmap

### Phase 1: Minimal Working System (Week 1)

**Goal:** Get basic inference working with a simple agent loop

**Install:**
```bash
# Create workspace
sudo mkdir -p /opt/aiworkstation
sudo chown $USER:staff /opt/aiworkstation
cd /opt/aiworkstation

# Create Python environment
python3 -m venv venv
source venv/bin/activate

# Install MLX
pip install mlx mlx-lm

# Download models
mkdir -p models
cd models
# Download Qwen2.5 7B (start small)
mlx.community download Qwen/Qwen2.5-7B-Instruct-4bit
cd ..

# Install basic dependencies
pip install fastapi uvicorn sqlite-utils
```

**Create basic orchestrator:**
```python
# orchestrator.py
from mlx_lm import load, generate
import sqlite3
import time

class SimpleOrchestrator:
    def __init__(self):
        self.model, self.tokenizer = load("models/Qwen2.5-7B-Instruct-4bit")
        self.db = sqlite3.connect("tasks.db")
        self.setup_db()
    
    def setup_db(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                description TEXT,
                status TEXT,
                result TEXT
            )
        """)
        self.db.commit()
    
    def process_task(self, task):
        prompt = f"Task: {task['description']}\n\nSolve this task step by step:"
        result = generate(self.model, self.tokenizer, prompt=prompt, max_tokens=1000)
        return result
    
    def run(self):
        while True:
            # Get pending task
            cursor = self.db.execute(
                "SELECT * FROM tasks WHERE status='pending' LIMIT 1"
            )
            task = cursor.fetchone()
            
            if task:
                task_id, description, _, _ = task
                self.db.execute(
                    "UPDATE tasks SET status='running' WHERE id=?", (task_id,)
                )
                self.db.commit()
                
                result = self.process_task({"description": description})
                
                self.db.execute(
                    "UPDATE tasks SET status='completed', result=? WHERE id=?",
                    (result, task_id)
                )
                self.db.commit()
            
            time.sleep(1)

if __name__ == "__main__":
    orch = SimpleOrchestrator()
    orch.run()
```

**Test:**
```bash
# Add a test task
sqlite3 tasks.db "INSERT INTO tasks (description, status) VALUES ('What is 2+2?', 'pending')"

# Run orchestrator
python orchestrator.py

# Check result
sqlite3 tasks.db "SELECT * FROM tasks"
```

**Failure modes:**
- Model loading fails → Check MLX installation, redownload model
- SQLite locked → Ensure only one process accessing DB
- Out of memory → Reduce max_tokens or use smaller model

**Rollback:**
```bash
rm -rf /opt/aiworkstation
```

---

### Phase 2: Autonomous Coding (Week 2-3)

**Goal:** Integrate Aider for code editing tasks

**Install Aider:**
```bash
pip install aider-chat
```

**Create coding agent:**
```python
# coding_agent.py
import subprocess
import os

class CodingAgent:
    def __init__(self, workspace):
        self.workspace = workspace
        os.makedirs(workspace, exist_ok=True)
    
    def execute_task(self, task_description, repo_path=None):
        if repo_path:
            os.chdir(repo_path)
        
        # Create Aider command
        cmd = [
            "aider",
            "--model", "local/mlx_http://localhost:8080",
            "--message", task_description,
            "--yes",
            "--no-auto-commits"
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=self.workspace
        )
        
        return result.stdout

# Integrate with orchestrator
# Add task type detection and routing
```

**Set up local model server:**
```bash
# Install MLX server
pip install mlx-lm[server]

# Start server
mlx_lm.server --model models/Qwen2.5-Coder-32B-Instruct-4bit --port 8080
```

**Test:**
```bash
# Create test repo
mkdir test_repo
cd test_repo
git init
echo 'def hello():\n    print("Hello")' > main.py
git add .
git commit -m "Initial commit"

# Run coding task
python -c "
from coding_agent import CodingAgent
agent = CodingAgent('/workspace/test_repo')
result = agent.execute_task('Add a function that calculates fibonacci numbers', '/workspace/test_repo')
print(result)
"
```

---

### Phase 3: Research Agents (Week 4)

**Goal:** Add web search and document processing

**Install:**
```bash
pip install duckduckgo-search pymupdf requests beautifulsoup4
```

**Create research agent:**
```python
# research_agent.py
from duckduckgo_search import DDGS
import requests
import fitz  # PyMuPDF

class ResearchAgent:
    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer
    
    def search_web(self, query, max_results=10):
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        return results
    
    def download_and_extract_pdf(self, url):
        response = requests.get(url)
        # Save to temp file
        # Extract text with PyMuPDF
        doc = fitz.open(stream=response.content, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    
    def research_topic(self, topic):
        # Generate search queries
        queries = self.generate_queries(topic)
        
        # Collect sources
        all_sources = []
        for query in queries:
            sources = self.search_web(query)
            all_sources.extend(sources)
        
        # Synthesize findings
        synthesis = self.synthesize(topic, all_sources)
        
        return synthesis
```

---

### Phase 4: Persistent Memory (Week 5)

**Goal:** Add vector database for semantic search

**Install:**
```bash
pip install chromadb sentence-transformers
```

**Implement memory manager:**
```python
# memory.py
import chromadb
from sentence_transformers import SentenceTransformer

class MemoryManager:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="/workspace/vectordb")
        self.collection = self.client.get_or_create_collection("agent_memory")
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
    
    def store(self, text, metadata=None):
        embedding = self.embedder.encode(text).tolist()
        self.collection.add(
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata or {}],
            ids=[str(hash(text))]
        )
    
    def recall(self, query, top_k=5):
        embedding = self.embedder.encode(query).tolist()
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k
        )
        return results
```

---

### Phase 5: Multi-Agent Orchestration (Week 6-7)

**Goal:** Implement worker pool and model routing

**Create model router:**
```python
# model_router.py
class ModelRouter:
    def __init__(self):
        self.models = {
            "coder": "Qwen2.5-Coder-32B",
            "reasoner": "Qwen2.5-32B",
            "router": "Qwen2.5-7B"
        }
        self.loaded_model = None
    
    def select_model(self, task):
        # Analyze task requirements
        if "code" in task or "implement" in task:
            return "coder"
        elif "analyze" in task or "research" in task:
            return "reasoner"
        else:
            return "router"
    
    def ensure_model_loaded(self, model_name):
        if self.loaded_model != model_name:
            # Unload current model
            # Load new model
            self.loaded_model = model_name
```

**Implement worker pool:**
```python
# worker_pool.py
import threading
from queue import Queue

class WorkerPool:
    def __init__(self, max_workers=3):
        self.max_workers = max_workers
        self.task_queue = Queue()
        self.workers = []
        
        for i in range(max_workers):
            worker = threading.Thread(target=self.worker_loop, args=(i,))
            worker.start()
            self.workers.append(worker)
    
    def worker_loop(self, worker_id):
        while True:
            task = self.task_queue.get()
            if task is None:
                break
            
            # Process task
            result = self.process_task(task)
            
            self.task_queue.task_done()
```

---

### Phase 6: 24/7 Operation (Week 8)

**Goal:** Set up launchd service and crash recovery

**Create launchd plist:**
```bash
sudo nano /Library/LaunchDaemons/com.aiworkstation.plist
```

**Add crash recovery:**
```python
# Add to orchestrator
def checkpoint_state(self):
    state = {
        'active_tasks': self.worker_pool.get_active(),
        'queue': self.task_queue.get_all(),
        'timestamp': time.time()
    }
    with open('/workspace/state/checkpoint.json', 'w') as f:
        json.dump(state, f)

def recover_from_checkpoint(self):
    if os.path.exists('/workspace/state/checkpoint.json'):
        with open('/workspace/state/checkpoint.json') as f:
            state = json.load(f)
        # Restore state
```

---

### Phase 7: Remote Access (Week 9)

**Goal:** Set up Tailscale and web dashboard

**Install Tailscale:**
```bash
brew install tailscale
sudo tailscale up
```

**Create web dashboard:**
```python
# dashboard.py
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return """
    <html>
        <body>
            <h1>AI Workstation Dashboard</h1>
            <div id="status"></div>
            <script>
                // Fetch status every 5 seconds
                setInterval(async () => {
                    const response = await fetch('/api/status');
                    const status = await response.json();
                    document.getElementById('status').innerText = JSON.stringify(status, null, 2);
                }, 5000);
            </script>
        </body>
    </html>
    """

@app.get("/api/status")
async def get_status():
    return orchestrator.get_status()
```

---

### Phase 8: Advanced Optimization (Week 10+)

**Goal:** Fine-tune performance and add advanced features

**Optimizations:**
- Implement model preloading based on task patterns
- Add intelligent context window management
- Implement task batching for similar tasks
- Add performance monitoring and alerting

---

## 14. Final Deliverables

### A. Recommended Technology Stack

| Layer | Recommended | Alternatives | Why |
|-------|-------------|--------------|-----|
| **Inference Engine** | MLX | llama.cpp, Ollama | Best Apple Silicon optimization, native Metal support |
| **Primary Model (Coding)** | Qwen2.5-Coder 32B Q4_K_M | DeepSeek-Coder-V2 | Best coding ability at 32B size, strong tool use |
| **Primary Model (Reasoning)** | Qwen2.5 32B Q4_K_M | Llama 3.3 70B (won't fit) | Strong reasoning, fits in 32GB |
| **Router Model** | Qwen2.5 7B Q4_K_M | Phi-3.5-mini, Llama 3.2 3B | Fast, accurate classification |
| **Agent Orchestrator** | Custom Python | LangGraph, CrewAI | Full control, minimal overhead |
| **Coding Agent** | Aider | OpenHands, SWE-agent | Best local model support, proven Git integration |
| **Task Queue** | SQLite | Redis, RabbitMQ | Simple, reliable, no extra infrastructure |
| **Vector DB** | ChromaDB | Qdrant, Pinecone | Embedded, simple, good for starting |
| **Web Search** | DuckDuckGo API | SearXNG, Brave Search | Free, no API key needed |
| **PDF Processing** | PyMuPDF + marker | Unstructured.io | Fast, good quality |
| **Browser Automation** | Playwright | Selenium | Modern, reliable, good async support |
| **Service Management** | launchd | systemd (Linux), supervisord | macOS native, reliable |
| **Remote Access** | Tailscale | ngrok, Cloudflare Tunnel | Secure, no public exposure |
| **Notifications** | Telegram Bot | Discord, Email | Easy setup, mobile-friendly |
| **Monitoring** | Custom + SQLite | Prometheus, Grafana | Lightweight, no overhead |

---

### B. Complete Architecture Diagram

(See Section 12 above)

---

### C. Hardware/Resource Plan

**Memory Allocation (32 GB total):**

| Component | Allocation | Notes |
|-----------|------------|-------|
| macOS + System | 6-8 GB | Always resident |
| 7B Router Model | 4.5 GB | Always resident |
| Embedding Model | 1.5 GB | Always resident |
| 32B Primary Model | 19-20 GB | Hot-swappable |
| KV Cache | 3-4 GB | Depends on context length |
| Agent Processes | 2-3 GB | Python overhead |
| Browser (Playwright) | 1-2 GB | When active |
| Databases | 1-2 GB | SQLite + ChromaDB |
| Filesystem Cache | 2-3 GB | macOS managed |
| **Total** | **~30-32 GB** | Tight but workable |

**Storage Allocation:**

**Internal SSD (512 GB):**
- Models: 80 GB
- Databases: 20 GB
- Active projects: 100 GB
- Logs/checkpoints: 20 GB
- Applications: 30 GB
- System: 30 GB
- Free: 232 GB

**External SSD (1 TB):**
- Git repos: 200 GB
- Research papers: 300 GB
- Backups: 200 GB
- Archives: 200 GB
- Free: 100 GB

---

### D. Agent Architecture (100+ Logical Agents)

**Key insight:** Logical agents are lightweight definitions, not running processes.

```
Agent Definition (stored in DB):
{
  "id": "research-agent-001",
  "name": "Academic Literature Reviewer",
  "role": "research",
  "system_prompt": "You are an expert at...",
  "tools": ["web_search", "pdf_reader", "citation_checker"],
  "model_preference": "reasoner",
  "permissions": ["read_files", "web_access"],
  "max_tokens": 50000,
  "max_runtime": 3600
}

When task assigned:
1. Load agent definition from DB
2. Inject system prompt into context
3. Load preferred model (if not already loaded)
4. Execute task
5. Store results
6. Unload model if not needed by next task
```

**Concurrency:**
- 100+ agent definitions can exist
- Only 2-3 agents run simultaneously (limited by memory)
- Task queue ensures orderly execution
- Model router optimizes model loading

---

### E. Model Strategy

| Task Type | Model | Why |
|-----------|-------|-----|
| **Planning** | Qwen2.5 32B | Strong reasoning, can handle complex decomposition |
| **Coding** | Qwen2.5-Coder 32B | Best-in-class code generation at this size |
| **Debugging** | Qwen2.5-Coder 32B | Understands code context, can trace errors |
| **Research** | Qwen2.5 32B | Good synthesis, can handle long contexts |
| **Summarization** | Qwen2.5 7B | Fast, good enough quality for summaries |
| **Classification** | Qwen2.5 7B | Ultra-fast routing decisions |
| **Final Synthesis** | Qwen2.5 32B | Best quality for final output |

**Fallback strategy:**
- If 32B model fails or times out, retry with 7B model
- For simple tasks, always use 7B to save resources
- Use 32B only when task complexity warrants it

---

### F. 24/7 Architecture

**Service management:**
```bash
# launchd keeps orchestrator running
sudo launchctl load /Library/LaunchDaemons/com.aiworkstation.plist

# Orchestrator has built-in watchdog
while True:
    try:
        process_tasks()
        checkpoint_state()
    except Exception as e:
        log_error(e)
        recover()
        time.sleep(5)
```

**Crash recovery:**
1. launchd restarts orchestrator if it crashes
2. Orchestrator loads last checkpoint
3. Incomplete tasks are re-queued
4. Orphaned processes are killed
5. System continues from last known good state

**Prevent sleep:**
```bash
sudo pmset -a sleep 0 disksleep 0 displaysleep 0
caffeinate -s &
```

**Monitoring:**
- Watchdog script checks orchestrator every minute
- Sends alert if orchestrator down for >5 minutes
- Automatic restart via launchd

---

### G. Remote Control Architecture

**Access methods:**

1. **Tailscale VPN** (primary)
   - Secure, no public exposure
   - Access from anywhere
   - Works on phone, laptop, tablet

2. **Web Dashboard** (monitoring)
   - FastAPI + simple HTML/JS
   - Shows status, active tasks, logs
   - Accessible via Tailscale

3. **Telegram Bot** (commands/notifications)
   - Send tasks
   - Get status updates
   - Approve/reject actions
   - Emergency stop

4. **SSH** (advanced control)
   - Full terminal access
   - Debug issues
   - Manual intervention

**Security:**
- All access via Tailscale (encrypted)
- SSH key authentication only
- Telegram bot requires user ID whitelist
- Web dashboard requires Tailscale auth

---

### H. Security Architecture

**Principle:** Autonomous but not trusted

**Permission tiers:**

**Tier 1 (Autonomous):**
- Read files in /workspace
- Create/edit files in /workspace
- Run tests
- Local Git operations
- Web search
- Database reads

**Tier 2 (Log + Notify):**
- Install packages
- Create Git branches
- Send notifications
- Write to external APIs

**Tier 3 (Require Approval):**
- Push to Git remotes
- Delete files
- Access outside /workspace
- Network requests (non-search)
- System modifications

**Implementation:**
```python
class SecurityManager:
    def check_permission(self, action):
        tier = self.classify(action)
        
        if tier == 1:
            return True
        elif tier == 2:
            self.log(action)
            self.notify(action)
            return True
        elif tier == 3:
            self.log(action)
            return self.wait_for_approval(action)
```

**Sandboxing:**
- Dedicated user account (aiworker)
- Restricted file access
- Network controls (can block domains)
- Resource limits (tokens, time, operations)

**Emergency controls:**
- Kill switch: `pkill -f orchestrator`
- Revoke network: `sudo pfctl -d`
- Revert changes: `git reset --hard`

---

### I. Exact Installation Plan

**Step 1: Prepare system**
```bash
# Update macOS
sudo softwareupdate -i -a

# Install Xcode command line tools
xcode-select --install

# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.11+
brew install python@3.11

# Create workspace
sudo mkdir -p /opt/aiworkstation
sudo chown $USER:staff /opt/aiworkstation
cd /opt/aiworkstation
```

**Step 2: Set up Python environment**
```bash
python3 -m venv venv
source venv/bin/activate

# Install core dependencies
pip install mlx mlx-lm fastapi uvicorn sqlite-utils
pip install aider-chat duckduckgo-search pymupdf playwright
pip install chromadb sentence-transformers python-telegram-bot
```

**Step 3: Download models**
```bash
mkdir -p models
cd models

# Download models (will take time)
mlx.community download Qwen/Qwen2.5-7B-Instruct-4bit
mlx.community download Qwen/Qwen2.5-32B-Instruct-4bit
mlx.community download Qwen/Qwen2.5-Coder-32B-Instruct-4bit

cd ..
```

**Step 4: Create directory structure**
```bash
mkdir -p workspace/{projects,research,memory,logs,state}
mkdir -p vectordb
```

**Step 5: Create orchestrator**
(Use code from Phase 1-8 above)

**Step 6: Set up launchd service**
```bash
sudo nano /Library/LaunchDaemons/com.aiworkstation.plist
# (paste plist content from Section 9)

sudo launchctl load /Library/LaunchDaemons/com.aiworkstation.plist
```

**Step 7: Prevent sleep**
```bash
sudo pmset -a sleep 0 disksleep 0 displaysleep 0
```

**Step 8: Set up Tailscale**
```bash
brew install tailscale
sudo tailscale up
# Follow authentication flow
```

**Step 9: Test system**
```bash
# Add test task
sqlite3 workspace/tasks.db "INSERT INTO tasks (description, status) VALUES ('Write a Python function to calculate factorial', 'pending')"

# Check logs
tail -f /var/log/aiworkstation/orchestrator.log
```

**Step 10: Set up remote access**
```bash
# Enable SSH
sudo systemsetup -setremotelogin on

# Test Tailscale connection from another device
```

---

### J. What NOT to Install

**Avoid these (redundant, unnecessary, or counterproductive):**

1. **Ollama** - Adds abstraction layer, MLX is better for Apple Silicon
2. **LangChain** - Heavy, adds latency, overkill for your needs
3. **CrewAI/AutoGen** - Too much abstraction, hard to debug
4. **Docker** - Significant overhead on Mac, not needed
5. **PostgreSQL** - Overkill, SQLite is sufficient
6. **Redis** - Not needed unless you scale to multiple machines
7. **Prometheus/Grafana** - Heavy monitoring, custom logging is enough
8. **Neo4j** - Knowledge graph is overkill for starting
9. **vLLM** - Designed for GPU clusters, not Apple Silicon
10. **Multiple agent frameworks** - Pick one (Aider) and customize

**Why avoid:**
- Each adds complexity, overhead, and potential failure points
- On 32GB, every GB of RAM and CPU cycle matters
- Simpler = more reliable = easier to debug

---

### K. Future Upgrade Path

**If you upgrade to 64 GB unified memory:**

**Immediate improvements:**
- Run 70B models (Q4_K_M ~40 GB)
- Keep multiple large models loaded simultaneously
- Increase context windows to 32K+
- Run 4-5 concurrent workers instead of 2-3

**Architecture changes:**
- Can add knowledge graph (Neo4j)
- Can run more sophisticated models (Llama 3.3 70B, DeepSeek-V3)
- Can increase parallelism significantly

**If you upgrade to 96-128 GB:**

**Major improvements:**
- Run 70B+ models at higher quantization (Q6_K, Q8)
- Keep 3-4 large models loaded simultaneously
- Run 6-8 concurrent workers
- Can add dedicated GPU via eGPU (if needed)

**Architecture changes:**
- Can use more complex multi-agent patterns
- Can add real-time collaboration features
- Can support more users/projects simultaneously

**If you add dedicated GPU server:**

**Hybrid approach:**
- Keep Mac for orchestration and light inference
- Offload heavy inference to GPU server
- Use network (Tailscale) to connect
- Can run 70B+ models at full precision
- Massive speedup for large models

**Implementation:**
```python
# Model router decides where to run inference
class ModelRouter:
    def select_backend(self, task):
        if task.requires_large_model():
            return "gpu_server"
        else:
            return "local_mac"
```

---

## Final Recommendations

**Start simple, iterate quickly:**
1. Get Phase 1-3 working first (basic inference + coding + research)
2. Use it for 2-3 weeks before adding complexity
3. Identify actual bottlenecks before optimizing
4. Add Phase 4-8 only when you need them

**Key success factors:**
- **Model selection matters more than framework choice** - Qwen2.5-Coder 32B is your workhorse
- **Keep it simple** - Custom orchestrator > complex framework
- **Monitor resource usage** - 32GB is tight, watch memory closely
- **Test thoroughly** - Autonomous systems need robust error handling
- **Start with Tier 1-2 permissions** - Don't give full autonomy until you trust it

**Expected timeline:**
- Week 1-2: Basic system working
- Week 3-4: Coding agent functional
- Week 5-6: Research agent working
- Week 7-8: Multi-agent orchestration
- Week 9-10: 24/7 operation + remote access
- Week 11+: Optimization and advanced features

This architecture gives you a production-quality autonomous AI workstation that maximizes the capabilities of your 32GB Mac mini while maintaining security and reliability.

## Model's own cited sources

NONE. The response contained zero citations / no "Sources" section, despite the prompt explicitly requesting
"a Sources list with URLs, marking each primary or secondary." Relevant for RQ5 (citation quality) — treat as
a from-knowledge answer.

## Reviewer notes

### Recency — WEAK (RQ4 flag)
- Recommends the **Qwen2.5 generation** (Qwen2.5-Coder 32B, Qwen2.5 32B, Qwen2.5 7B) — all 2024-era.
- Specialist list: DeepSeek-Coder-V2-Lite, **Llama 3.2 3B**, **Phi-3.5-mini** — all 2024.
- Alternatives named: **Llama 3.3 70B**, DeepSeek-V3, OpenDevin/OpenHands — late-2024 / early-2025.
- No mention of: Qwen3 / Qwen3-Coder-30B-A3B, gpt-oss, MLX MoE support, llama-swap, Ollama's MLX backend, Claude Code / Agent SDK / Remote Control, Goose, Docling, sqlite-vec, Apple `container`, ntfy, 2026 agent-harness landscape.
- Did NOT engage with the M6 specifically (170 GB/s bandwidth, dual Neural Engine, ship date) — treats it as generic "M-series 32GB."
- Conclusion: answered from a ~2024 knowledge snapshot; almost certainly no browsing.

### Constraint reasoning — MOSTLY OK (RQ3)
- Correctly rejects 70B on 32GB. Correct that dense 32B Q4 ≈ 19–20 GB.
- Exec summary correctly names memory bandwidth + model-load time as the bottleneck.
- BUT picks a **dense 32B** as the primary workhorse. On ~170 GB/s a dense 32B is far slower per token than a 30B **MoE with ~3B active** (Claude's Qwen3-Coder-30B-A3B pick). Qwen never considers MoE. This is the biggest technical divergence and arguably a sub-optimal call for "useful work per hour."
- KV-cache heuristic ("20–30% of model size") is hand-wavy but not crazy.
- Memory table sums to "30–32 GB … tight but workable" — leaves almost no headroom for FS cache / browser at peak (same tight spot Claude flagged).

### Hallucination check (RQ2)
- No fabricated tools spotted — Aider, OpenHands, ChromaDB, SearXNG, PyMuPDF, marker, Playwright, Tailscale, launchd, python-telegram-bot all real.
- `mlx.community download` CLI syntax is wrong/fabricated (real is `mlx_lm.convert` / `huggingface-cli download` / `mlx-community/...` HF repos). Minor.
- `--model local/mlx_http://localhost:8080` Aider syntax is not real. Minor.
- No fabricated benchmark numbers because it cited no numbers — avoids RQ2-benchmark failure by omission.

### Agreements with Claude (consensus signal)
- MLX primary, llama.cpp fallback.
- Custom thin orchestrator, NOT CrewAI/AutoGen/LangGraph.
- 100+ logical agents = DB-stored definitions + task queue + small worker pool; model router loads/unloads.
- SQLite task queue, no Redis.
- Memory: filesystem + SQLite first, vector DB later, knowledge graph only if needed.
- launchd + KeepAlive + watchdog + caffeinate + pmset + checkpoint/requeue for 24/7.
- Tailscale-only remote, no public exposure; FastAPI dashboard.
- Dedicated non-admin user; 3-tier permission model (autonomous / notify / approve); kill switch; resource limits.
- Storage: models + DBs on internal, git repos + papers + backups on external; symlinks for hot dirs.
- "What NOT to install" overlap: CrewAI/AutoGen, LangChain, Neo4j-early, Redis, Prometheus/Grafana, Docker.
- Phased 8-step roadmap, same phase ordering as the prompt.

### Divergences from Claude (interesting for the paper)
| Axis | Qwen 3.7 Plus | Claude Sonnet 5 |
|---|---|---|
| Model family | Qwen2.5 gen, **dense** 32B | Qwen3 gen, **MoE** 30B-A3B + gpt-oss-20b |
| Reasoning model | Qwen2.5 32B dense | gpt-oss-20b MoE |
| Cloud burst | none — pure local, cloud barely mentioned | optional Claude API for planning / synthesis / citation-verify (<$30/mo) |
| Coding agent | Aider (primary) + OpenHands | Claude Code + Goose(local) |
| Model swap layer | "MLX model manager" (custom) | llama-swap |
| Vector DB | **ChromaDB** from month 2 | **sqlite-vec** (explicitly avoid Chroma/standalone) |
| Exec sandbox | dedicated user + file perms + `pfctl` only — **no containers/VM** | dedicated user **+ Apple `container` / Colima per risky exec** |
| Notifications | Telegram bot | ntfy |
| Remote coding | SSH + web dashboard | + Claude Code Remote Control (native) |
| Concurrency model | flat "2–3 workers" | separated lanes: heavy=1 / light=2 / cloud=4 |
| Ollama | listed under "do NOT install" | "acceptable simpler substitute" |
| Research anti-hallucination | quotes + DOI check + JSON claims (lighter) | + independent verifier agent re-opens source, contradiction-link pass, evidence DB schema (heavier) |
| Sources | 0 | ~97 |
| M6-specific reasoning | none | bandwidth/ship-date/NE engaged |
| Timeline framing | "weeks" (Week 1 … Week 11+) | phases, no week estimates |

### For decisions-matrix.csv
Column `qwen37plus` filled.
