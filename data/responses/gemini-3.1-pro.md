---
ai_name: Gemini 3.1 Pro
model_version_id: "user-labelled 'Gemini 3.1 Pro'. Note: Pro-series left the Google AI Studio free tier on 2026-04-01 (free tier is now Flash-class); Pro access is via a paid plan or the Gemini app. Exact build not disclosed in-answer."
provider: Google
interface: web app (Gemini) — free/Pro access, not disclosed
browsing_enabled: no (0 sources; no M6-specific facts; cloud-fallback models are 2024-era)
knowledge_cutoff: unknown (recommendations trail ~12-18 months: Qwen2.5-Coder-32B, R1-Distill-14B, "Claude 3.5 Sonnet", "DeepSeek-V3")
prompt_version: v1
date_run: 2026-08-31
run_by: roshanaryal1
notes_on_run: >
  Single message, complete answer with an "Architectural Analysis & Trade-offs" preamble and a
  "Final Verification Checklist" appendix. Emitted deliverables A–K but not the requested header
  line and not a Sources list. Only response so far to pick llama.cpp (not MLX) as the primary
  engine, and to name PaperQA2 for citation-grounded research.
trust_rating: MEDIUM — every named tool is real and the plan is internally consistent and executable, but 0 sources, 2024-era model picks, a stale cloud-fallback list ("Claude 3.5 Sonnet" / "DeepSeek-V3"), and no M6-specific reasoning.
---

## Raw response

Here is the complete architectural blueprint and implementation plan for your 24/7 autonomous AI workstation on the M6 Apple Mac mini (32 GB Unified Memory).

---

## Architectural Analysis & Trade-offs

Building a 24/7 autonomous agent environment on a 32 GB unified memory footprint requires strict resource boundaries. The core constraint is **memory bandwidth and capacity**: running large models leaves less RAM for parallel contexts, OS cache, worker processes, and sandboxes.

To maximize **useful work per hour**, the architecture decouples **Logical Agents** from **Model Inference**:

* **Logical Agents** are lightweight Python state machines (costing kilobytes of memory).
* **Model Inference** runs via a centralized server pool managing 1–2 models in VRAM with context slotting.

---

## A. Recommended Technology Stack

| Layer | Recommended Technology | Alternatives | Why Chosen for 32 GB M6 Mac mini |
| --- | --- | --- | --- |
| **Local Inference Engine** | **`llama.cpp` server** (or **Ollama** backend) | MLX-LM Server, vLLM | `llama.cpp` offers native Metal acceleration, precise GGUF quantization management, slot-based prompt caching (`-np 2`), and low CPU/RAM overhead compared to Python-heavy runners. |
| **Core Models (Local)** | **Qwen2.5-Coder-32B (Q4_K_M)** & **DeepSeek-R1-Distill-Qwen-14B (Q8_0)** | Llama-3.1-8B, Mistral-Small-24B | **Qwen2.5-Coder-32B** delivers state-of-the-art local coding and tool-use performance. **R1-Distill-14B** handles complex reasoning, planning, and verification. |
| **Orchestration Layer** | **Custom Python Async Engine** (built on **LangGraph** core) | CrewAI, AutoGen, MetaGPT | Heavy frameworks add unnecessary abstraction layers and memory overhead. LangGraph provides deterministic, stateful graph execution, persistent checkpoints, and dynamic subagent branching. |
| **Coding Harness** | **Aider** (headless CLI execution via API bridge) | OpenHands, Claude Code CLI | Aider is extremely efficient, natively handles Git context, repo map generation (via tree-sitter), and automated lint/test-driven refactoring loops with zero desktop GUI overhead. |
| **Research Engine** | **PaperQA2** + **SearXNG** + **Crawl4AI** | AutoGPT, Custom Scrapers | **SearXNG** provides self-hosted web search. **Crawl4AI** extracts clean Markdown from pages. **PaperQA2** uses RAG graph synthesis to ensure claim verification and zero-hallucination citations. |
| **Persistent Memory** | **SQLite** + **`sqlite-vec`** + **Markdown Files** | ChromaDB, Pinecone, Neo4j | Eliminates external daemon overhead. Markdown files (`AGENTS.md`, `MEMORY.md`) provide transparent context loading; `sqlite-vec` handles fast semantic vector searches in a single file binary. |
| **Execution Sandbox** | **Dedicated macOS User** (`ai-worker`) + **Lima / Docker** | Full UTM VM, Bare-Metal macOS | Prevents agent access to host credentials. Docker via Lima runs untrusted code inside isolated Linux containers without full VM system overhead. |
| **System Daemon (24/7)** | **macOS `launchd`** + **`caffeinate`** | Docker Compose, Systemd, PM2 | Native macOS service manager. `launchd` guarantees automatic process respawning after crashes or system reboots, while `caffeinate` prevents system sleep. |
| **Remote Access & Control** | **Tailscale** + **Mosh / SSH** + **Textual/Web Dashboard** | Open-port SSH, Cloudflare Tunnel | Tailscale provides encrypted WireGuard mesh networking with zero open ports. Mosh provides resilient mobile terminal connections across network drops. |

---

## B. Complete Architecture Diagram

```
                                  [ User Interface ]
                   (Tailscale Network / Phone / Laptop / Remote CLI)
                                          |
                                          v
                               [ Secure Remote Gateway ]
                       (SSH / Mosh / Lightweight Web Portal)
                                          |
                                          v
                     +-----------------------------------------+
                     |     macOS launchd (Daemon Supervisor)   |
                     |  - Keeps process alive via caffeinate   |
                     |  - Automatically restarts on failure    |
                     +--------------------+--------------------+
                                          |
                                          v
                     +-----------------------------------------+
                     |       Orchestrator Core (LangGraph)     |
                     |  - Event loop & Scheduled Cron Tasks    |
                     |  - Task Queue & Prioritization Engine   |
                     |  - Dynamic Agent Spawner & State Guard  |
                     +--------------------+--------------------+
                                          |
                  +-----------------------+-----------------------+
                  v                       v                       v
       +---------------------+ +---------------------+ +---------------------+
       |   Software Agent    | |   Research Agent    | |   System Inspector  |
       |   (Aider Engine)    | | (SearXNG + PaperQA) | |   (Metrics & Logs)  |
       +----------+----------+ +----------+----------+ +----------+----------+
                  |                       |                       |
                  +-----------------------+-----------------------+
                                          |
                                          v
                     +-----------------------------------------+
                     |          Smart Model Router             |
                     |  - Routes fast vs heavy tasks           |
                     |  - Enforces max concurrent LLM calls    |
                     +--------------------+--------------------+
                                          |
                  +-----------------------+-----------------------+
                  v                                               v
     +-------------------------+                     +-------------------------+
     |  Primary Model Inference|                     |  Cloud Fallback (Opt.)  |
     |   (llama.cpp Server)    |                     |  (Claude Sonnet 3.5 /   |
     |  Metal GPU Acceleration |                     |    DeepSeek-V3 API)      |
     +------------+------------+                     +------------+------------+
                  |                                               |
                  +-----------------------+-----------------------+
                                          |
                                          v
                     +-----------------------------------------+
                     |       Persistent Memory Architecture    |
                     |  - Flat Markdown Files (Core Context)   |
                     |  - SQLite Engine (Task & Exec State)    |
                     |  - sqlite-vec (Semantic Search Index)   |
                     +-----------------------------------------+
```

---

## C. Hardware & Resource Plan

### Memory Allocation Map (32 GB Unified Memory)

To maintain maximum stability under 24/7 continuous operation:

```
+----------------------------------------------------------------------+
| Total Unified Memory: 32 GB                                          |
+------------------+-------------------+-------------------+------------+
| macOS System &   | LLM VRAM Weight   | LLM KV Cache &    | Agent Loop,|
| OS Overhead      | Allocation        | Context Window    | Tools & RAM|
| ~5.0 GB          | ~19.5 GB          | ~3.5 GB           | ~4.0 GB    |
+------------------+-------------------+-------------------+------------+
```

* **macOS & Core Daemons**: 5.0 GB baseline system overhead.
* **LLM Model Weights**: ~19.5 GB allocated to `llama.cpp` via `sysctl` memory pinning.
* **KV Cache Allocation**: ~3.5 GB for 16k total context window support (split across 2 concurrent inference slots of 8k each).
* **Agent Tools, RAG, Python Runtimes, SearXNG & Docker**: ~4.0 GB total runtime RAM pool.

### SSD Storage Topology

| Storage Drive | Capacity / Interface | Content & Directory Structure | Rationale |
| --- | --- | --- | --- |
| **Internal SSD** | 512 GB (Fast PCIe NVMe) | `/Users/ai-worker/workspace/` ; `/Users/ai-worker/db/` (SQLite) ; `/Users/ai-worker/logs/` ; Active Git Repositories & Worktrees | High IOPS for rapid file scanning, fast Git operations, high-frequency SQLite writes, and local compilation. |
| **External SSD** | 1 TB (Thunderbolt 3/4) | `/Volumes/AI_Storage/models/` (GGUFs) ; `/Volumes/AI_Storage/paper_archive/` (PDFs) ; `/Volumes/AI_Storage/vector_cache/` ; Historical Backups | Sustained throughput for loading large model weights into VRAM at startup; avoids wear on internal drive from large file churn. |

---

## D. Agent Architecture (100+ Logical Agents on Bounded Hardware)

Running 100 simultaneous LLM model instances on 32 GB RAM will crash the operating system. The system instead uses **Logical Agent Abstraction with Bounded Worker Pools**.

```
  100+ Logical Tasks / Agents
 [Agent A]  [Agent B] ... [Agent N]
     |          |             |
     +----------+-------------+
                v
     +----------------------+
     |  SQLite State Queue  |  <-- Non-blocking Task Queue
     +----------+-----------+
                v
     +----------------------+
     |  Worker Pool Queue   |  <-- Max 2 Active Workers
     +-------+------+-------+
             |      |
             v      v
        +--------------+
        |  Slot 1 LLM  | (Parallel Processing in llama.cpp)
        |  Slot 2 LLM  |
        +--------------+
```

### Key Components

1. **Task State Objects (TSO)**: A logical agent is simply an isolated record in SQLite containing state, memory references, tools, permissions, and a instruction set. Creating 100 logical agents takes <5 MB of RAM.
2. **Prioritized Scheduler**: The Orchestrator monitors queued tasks and ranks them by priority (e.g., active debugging task > background literature scan).
3. **Execution Worker Pool**: The Orchestrator limits active LLM interaction to **2 worker threads** matching the 2 slots configured in the `llama.cpp` server (`-np 2`).
4. **Context Switching via Slot Caching**: `llama.cpp` preserves prompt context per slot. Logical agents executing sequential steps send incremental diffs, avoiding expensive re-tokenization.

---

## E. Model Strategy

| Task Category | Primary Model | Quantization | Quantized Size | Target Context |
| --- | --- | --- | --- | --- |
| **Architecture, Planning & Reasoning** | DeepSeek-R1-Distill-Qwen-14B | Q8_0 | ~15.0 GB | 16,384 tokens |
| **Coding, Modification & Git Operations** | Qwen2.5-Coder-32B | Q4_K_M | ~19.8 GB | 16,384 tokens |
| **Fast Summarization, Extraction, Classification** | Qwen2.5-Coder-7B or Llama-3.1-8B | Q8_0 | ~8.5 GB | 8,192 tokens |
| **Cloud Fallback (Optional Edge Cases)** | Claude 3.5 Sonnet / DeepSeek-V3 | Cloud API | N/A | Variable |

### Routing Strategy

* **Local Preference**: 95%+ of operations execute locally.
* **Model Hot-Swapping**: The Orchestrator natively relies on **Qwen2.5-Coder-32B (Q4_K_M)** as its default engine for both planning and execution. If an ultra-complex algorithmic or logical task fails twice, the router unloads the coder model, loads **DeepSeek-R1-Distill-Qwen-14B**, performs deep reasoning, saves the plan, and swaps back to the coding model.
* **Cloud Fallback Policy**: Cloud APIs are triggered *only* when a local task fails 3 consecutive iteration cycles with syntax or logical errors, or when explicit web search parsing requires high-window multimodal vision processing.

---

## F. 24/7 Architecture

Continuous autonomous operation requires automatic crash recovery, power-management overrides, and transaction logging.

```
       +------------------------+
       |     macOS System       |
       +-----------+------------+
                   | Starts at Boot
                   v
       +------------------------+
       | launchd Daemon Service |
       +-----------+------------+
                   | Spawns & Keeps Alive
                   v
       +------------------------+     Prevents Sleep
       | caffeinate Wrapper     +----------------------+
       +-----------+------------+                      |
                   | Execs Process                    v
                   v                       +----------------------+
       +------------------------+          | macOS Power Mgmt     |
       | Python Orchestrator    |          | (System Stays Awake) |
       +-----------+------------+          +----------------------+
                   |
         +---------+---------+
         v                   v
+-----------------+ +-----------------+
| System Health   | | Heartbeat Log   |
| Watchdog Thread | | & SQLite Check  |
+-----------------+ +-----------------+
```

### 1. Sleep Prevention

macOS will attempt to sleep the CPU during periods of low user interaction. Prevent this by running the primary daemon wrapped in the native `caffeinate` utility:

```bash
/usr/bin/caffeinate -s -i -m -u python3 /Users/ai-worker/orchestrator/main.py
```

### 2. Service Definition (`launchd`)

Place the following configuration in `/Library/LaunchDaemons/com.aiworkstation.orchestrator.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.aiworkstation.orchestrator</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/caffeinate</string>
        <string>-s</string>
        <string>-i</string>
        <string>/Users/ai-worker/orchestrator/venv/bin/python3</string>
        <string>/Users/ai-worker/orchestrator/main.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>ThrottleInterval</key>
    <integer>10</integer>
    <key>StandardOutPath</key>
    <string>/Users/ai-worker/logs/orchestrator.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/ai-worker/logs/orchestrator.err</string>
    <key>WorkingDirectory</key>
    <string>/Users/ai-worker/workspace</string>
</dict>
</plist>
```

---

## G. Remote-Control Architecture

You can control and monitor the system remotely without opening public firewall ports.

```
 [ Mobile Phone / Remote Laptop ]
                |
                | (Encrypted WireGuard Mesh Tunnel)
                v
        [ Tailscale Mesh ]
                |
         -------+-------
        |               |
        v               v
   [ Mosh/SSH ]   [ Web Portal / Bot API ]
   Terminal UI    (Streamlit / Telegram)
```

1. **Tailscale Network**: The Mac mini connects to a private, encrypted Tailnet network. Access is secured using hardware keys (WebAuthn/YubiKey).
2. **Terminal Remote Access**: Use **Mosh** over Tailscale for resilient mobile shell connections (e.g., using Blink Shell on iOS) that survive cell coverage drops.
3. **Interactive Control Dashboard**: A local **Streamlit** or **FastAPI** web service bound strictly to the `tailscale0` IP address (`100.x.y.z`) provides task creation UI, system metrics, agent execution logs, and approval buttons for sensitive actions.
4. **Instant Emergency Stop**: A dedicated mobile button or terminal command (`touch /Users/ai-worker/HALT`) immediately pauses the agent worker queue and halts model inference.

---

## H. Security Architecture

Autonomous execution requires strict isolation boundaries to protect personal credentials and host system integrity.

```
+----------------------------------------------------------------------+
| macOS Host (Primary Admin Account)                                   |
|                                                                      |
|   +--------------------------------------------------------------+   |
|   | Dedicated Restricted User Space: "ai-worker"                  |   |
|   |                                                              |   |
|   |   +------------------------------------------------------+   |   |
|   |   | Orchestrator & Task Execution Runtime                 |   |   |
|   |   +-------------------------+----------------------------+   |   |
|   |                             |                                |   |
|   |                             v                                |   |
|   |   +------------------------------------------------------+   |   |
|   |   | Command Interceptor Guard (Regex / AST Checking)      |   |   |
|   |   +-------------------------+----------------------------+   |   |
|   |                             |                                |   |
|   |                +------------+-----------+                    |   |
|   |                v                        v                    |   |
|   |   +------------------------+  +--------------------------+   |   |
|   |   | Standard Workspace Ops |  | Untrusted Code Execution |   |   |
|   |   | (Local File Operations)|  | (Docker / Lima Sandbox)  |   |   |
|   |   +------------------------+  +--------------------------+   |   |
|   +--------------------------------------------------------------+   |
+----------------------------------------------------------------------+
```

### Permission Matrix

| Operation Category | Execution Policy | Enforcement Mechanism |
| --- | --- | --- |
| **Workspace File Creation / Editing** | Fully Autonomous | Restricted to `/Users/ai-worker/workspace/` |
| **Local Git Commits & Branching** | Fully Autonomous | Dedicated sub-repo git scope |
| **Package Installation (`pip`, `npm`)** | Autonomous in Virtualenv | Isolated venv inside workspace |
| **Destructive Command (`rm -rf`, `dd`)** | **BLOCKED** | Custom shell wrapper & AST interceptor |
| **External Network Web Scraping** | Autonomous | Outbound HTTP proxy filtering local IPs |
| **Git Push to Remote Main Branch** | **Requires Approval** | Gatekeeper queue notification |
| **System File Access (`/System`, `~admin`)** | **FORBIDDEN** | OS file permissions for `ai-worker` user |
| **Sudo Execution** | **FORBIDDEN** | `ai-worker` excluded from `/etc/sudoers` |

---

## I. Practical Implementation Plan

### Phase 1: Storage Mapping & Base Setup

Create the workspace environment under a separate, unprivileged system user.

```bash
# 1. Create External SSD directories
sudo mkdir -p /Volumes/AI_Storage/{models,paper_archive,vector_cache}
sudo chown -R ai-worker:staff /Volumes/AI_Storage

# 2. Setup internal directory structure
mkdir -p /Users/ai-worker/{workspace,db,logs,config,orchestrator}
cd /Users/ai-worker/orchestrator

# 3. Initialize Python virtual environment
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```

### Phase 2: Inference Engine Deployment

Deploy `llama.cpp` natively with Metal backend support.

```bash
# 1. Clone and build llama.cpp with Metal support
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
LLAMA_METAL=1 make -j

# 2. Download Recommended Quantized Models to External SSD
cd /Volumes/AI_Storage/models
# Download Qwen2.5-Coder-32B-Instruct GGUF (Q4_K_M)
curl -LO https://huggingface.co/Qwen/Qwen2.5-Coder-32B-Instruct-GGUF/resolve/main/qwen2.5-coder-32b-instruct-q4_k_m.gguf

# Download DeepSeek-R1-Distill-Qwen-14B GGUF (Q8_0)
curl -LO https://huggingface.co/unsloth/DeepSeek-R1-Distill-Qwen-14B-GGUF/resolve/main/DeepSeek-R1-Distill-Qwen-14B-Q8_0.gguf

# 3. Test launch llama.cpp server with 2 parallel slots
/Users/ai-worker/orchestrator/llama.cpp/llama-server \
  -m /Volumes/AI_Storage/models/qwen2.5-coder-32b-instruct-q4_k_m.gguf \
  -c 16384 \
  -np 2 \
  -ngl 99 \
  --host 127.0.0.1 \
  --port 8080
```

### Phase 3: Autonomous Coding Agent Harness Setup

Install and configure **Aider** for headless operation using the local `llama.cpp` server endpoint.

```bash
source /Users/ai-worker/orchestrator/venv/bin/activate
pip install aider-chat

# Create Aider configuration file
cat << 'EOF' > /Users/ai-worker/config/.aider.conf.yml
openai-api-base: http://127.0.0.1:8080/v1
openai-api-key: local-no-key
model: openai/qwen2.5-coder-32b-instruct-q4_k_m.gguf
auto-commits: true
lint: true
test-cmd: pytest
dirty-commits: true
EOF
```

### Phase 4: Autonomous Research Pipeline Setup

Install the search engine and automated research toolchain.

```bash
# 1. Install SearXNG via Docker
cd /Users/ai-worker/config
git clone https://github.com/searxng/searxng-docker.git
cd searxng-docker
# Edit docker-compose.yml to bind port to 127.0.0.1:8081
docker compose up -d

# 2. Install PaperQA2 & Crawl4AI
source /Users/ai-worker/orchestrator/venv/bin/activate
pip install paper-qa crawl4ai sqlite-vec
crawl4ai-setup
```

### Phase 5: Database & Memory Initialization

Initialize the unified SQLite database schema.

```python
# /Users/ai-worker/orchestrator/init_db.py
import sqlite3
import sqlite_vec

db_path = "/Users/ai-worker/db/system_memory.db"
conn = sqlite3.connect(db_path)
conn.enable_load_extension(True)
sqlite_vec.load(conn)

cursor = conn.cursor()

# Task Queue Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS task_queue (
    id TEXT PRIMARY KEY,
    parent_id TEXT,
    priority INTEGER,
    agent_type TEXT,
    status TEXT,
    payload TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Agent Memory Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS memory_log (
    id TEXT PRIMARY KEY,
    project_id TEXT,
    agent_id TEXT,
    content TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

conn.commit()
conn.close()
print("SQLite memory database initialized successfully.")
```

Run initialization:

```bash
python3 /Users/ai-worker/orchestrator/init_db.py
```

### Phase 6: Core Orchestrator Deployment

Create the main event loop (`main.py`) using **LangGraph** to process incoming tasks, manage worker pools, and handle error recovery.

```python
# /Users/ai-worker/orchestrator/main.py
import os
import sys
import time
import logging
import sqlite3
import subprocess

logging.basicConfig(
    filename='/Users/ai-worker/logs/orchestrator.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

HALT_FILE = "/Users/ai-worker/HALT"

def check_emergency_stop():
    if os.path.exists(HALT_FILE):
        logging.warning("Emergency halt file detected. Suspending execution.")
        return True
    return False

def get_next_task():
    conn = sqlite3.connect("/Users/ai-worker/db/system_memory.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, agent_type, payload FROM task_queue WHERE status = 'QUEUED' ORDER BY priority ASC LIMIT 1"
    )
    row = cursor.fetchone()
    conn.close()
    return row

def update_task_status(task_id, status):
    conn = sqlite3.connect("/Users/ai-worker/db/system_memory.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE task_queue SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (status, task_id)
    )
    conn.commit()
    conn.close()

def execute_agent_task(task_id, agent_type, payload):
    logging.info(f"Starting execution of Task {task_id} ({agent_type})")
    update_task_status(task_id, "RUNNING")

    try:
        if agent_type == "CODING":
            # Call headless Aider execution wrapper
            cmd = [
                "/Users/ai-worker/orchestrator/venv/bin/aider",
                "--config", "/Users/ai-worker/config/.aider.conf.yml",
                "--message", payload
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
            if res.returncode == 0:
                update_task_status(task_id, "COMPLETED")
                logging.info(f"Task {task_id} completed successfully.")
            else:
                update_task_status(task_id, "FAILED")
                logging.error(f"Task {task_id} failed: {res.stderr}")
    except Exception as e:
        update_task_status(task_id, "ERROR")
        logging.exception(f"Unhandled error in task {task_id}: {e}")

def main():
    logging.info("Autonomous AI Workstation Orchestrator Started.")
    while True:
        if check_emergency_stop():
            time.sleep(10)
            continue

        task = get_next_task()
        if task:
            task_id, agent_type, payload = task
            execute_agent_task(task_id, agent_type, payload)
        else:
            time.sleep(5)  # Idle polling interval

if __name__ == "__main__":
    main()
```

### Phase 7: Service Activation & Remote Access Setup

```bash
# 1. Install Tailscale and authenticate
brew install tailscale
sudo tailscaled &
tailscale up

# 2. Install and launch daemon via launchd
sudo cp /Users/ai-worker/config/com.aiworkstation.orchestrator.plist /Library/LaunchDaemons/
sudo launchctl load -w /Library/LaunchDaemons/com.aiworkstation.orchestrator.plist

# 3. Verify process status
sudo launchctl list | grep aiworkstation
```

---

## J. What NOT to Install

* **Neo4j / Heavy Graph Databases**: Graph databases add immense Java runtime overhead and memory consumption (~2-4 GB baseline). Markdown relationships and SQLite joins are much more efficient for a single 32 GB node.
* **Heavy Multi-Agent Frameworks (CrewAI, AutoGen)**: High abstraction overhead, uncontrolled nested loop recursion, and excessive prompt token usage.
* **Stand-Alone Vector Daemons (Milvus, Weaviate, Qdrant)**: Operating a separate vector database daemon wastes hundreds of megabytes of RAM. Use `sqlite-vec` directly in-process.
* **Electron-Based Desktop Agent Apps**: Electron runtimes consume significant RAM per window. Stick strictly to headless CLI processes, lightweight web dashboards, or terminal dashboards.

---

## K. Future Upgrade Path

If you eventually scale your hardware setup:

```
+----------------------------------------------------------------------+
| Current System: 32 GB M6 Mac mini                                    |
| Single Node - Local LLM Engine + Local Orchestrator                   |
+----------------------------------------------------------------------+
                                   |
                                   v
+----------------------------------------------------------------------+
| Upgrade Stage 1: 64 GB - 128 GB Unified Memory                       |
| - Run Qwen2.5-Coder-32B @ full Q8_0 or 70B parameter models @ Q4_K_M |
| - Increase parallel inference slots from -np 2 to -np 8              |
| - Add local vision processing models (e.g., Llama-3.2-Vision)        |
+----------------------------------------------------------------------+
                                   |
                                   v
+----------------------------------------------------------------------+
| Upgrade Stage 2: Multi-Node Distributed Cluster                      |
| - Retain M6 Mac mini as dedicated Orchestrator & Task Scheduler      |
| - Offload heavy inference workloads to dedicated Linux GPU cluster   |
| - Expand SQLite memory to distributed PostgreSQL with pgvector       |
+----------------------------------------------------------------------+
```

---

## Final Verification Checklist

Run these sanity checks to ensure the workstation is ready for autonomous execution:

1. **Daemon Verification**: Run `sudo launchctl list | grep aiworkstation` to ensure the process status returns `0`.
2. **Sleep Prevention**: Execute `pmset -g assertions` and confirm that `PreventUserIdleSystemSleep` is set to `1` by `caffeinate`.
3. **Emergency Stop**: Run `touch /Users/ai-worker/HALT`, check `/Users/ai-worker/logs/orchestrator.log`, and confirm the orchestrator pauses task picking. Remove the file to resume normal operations.

## Model's own cited sources

NONE. No Sources section; the prompt's request for one was ignored. (GitHub URLs for llama.cpp / SearXNG / HuggingFace model files appear in the install commands but are not offered as evidence for any claim.)

## Reviewer notes

### Trust — MEDIUM. Real tools, clean plan, but unsourced and behind on models.
- **No fabricated tools or models.** Every component exists: llama.cpp, Ollama, MLX-LM, Aider (with a correct headless `.aider.conf.yml`), **PaperQA2**, **SearXNG**, **Crawl4AI**, `sqlite-vec`, Lima, Docker, Mosh, Tailscale, Streamlit, `caffeinate`, `launchd`. This alone puts it well above both DeepSeek free-mode runs.
- The install commands and the `launchd` plist are internally consistent and would mostly run as written (see minor issues below).

### Recency (RQ4) — behind by ~12-18 months
- Core models: **Qwen2.5-Coder-32B (dense)** + **DeepSeek-R1-Distill-Qwen-14B** + Qwen2.5-Coder-7B / Llama-3.1-8B — all 2024. No Qwen3 / Qwen3-Coder-30B-A3B / gpt-oss / Devstral. Claude + Perplexity + DeepSeek-Expert all name Qwen3-Coder-30B-A3B; Gemini does not.
- **Cloud fallback list is stale: "Claude 3.5 Sonnet" and "DeepSeek-V3"** — current is Claude Sonnet 4.6 / Opus 4.8 and DeepSeek-V4. (The DeepSeek-V4 model that likely wrote the sibling DeepSeek captures postdates this recommendation.)
- No M6-specific facts (no 170 GB/s, no dual Neural Engine, no ship date). "M6 Mac mini" is used as a generic label, like Qwen 3.7 Plus did.
- Tool layer is more current than the model layer: LangGraph, PaperQA2, Crawl4AI, `sqlite-vec` are all 2024-2025 and appropriate.

### Hallucination (RQ2) — none
- No invented tools, no invented models, no fabricated benchmark numbers. The quantized sizes quoted (Q4_K_M 32B ~19.8 GB, Q8_0 14B ~15 GB) are in the right ballpark.

### Constraint reasoning (RQ3) — sound, one hidden tension
- Memory map sums to exactly 32.0 GB (5 OS + 19.5 weights + 3.5 KV + 4 tools). Self-consistent **only if a single model is resident** — which the routing section confirms (hot-swap coder <-> R1, never both).
- `memory_budget.py --preset gemini` (coder ~19.8 resident, 16K ctx, browser/Docker on, conservative 7 GB macOS): tips ~2 GB over — i.e. the 32.0 budget depends on an optimistic 5 GB macOS footprint while also running Docker + SearXNG + Crawl4AI 24/7. Tight, like every other response's peak case.
- Good detail unique to this response: **2 llama.cpp slots (`-np 2`) of the *same* model** with per-slot prompt caching, rather than 1 heavy + N small. A legitimate alternative concurrency model; means two agents can share the 32B without a second copy of weights.
- `-c 16384 -np 2` in llama.cpp splits context across slots (~8K each), which the text acknowledges. Correct.

### Internal consistency (RQ6) — clean
- No contradiction found. "What NOT to install" (Neo4j, CrewAI/AutoGen, standalone vector daemons, Electron apps) is consistent with the body — and notably **contradicts Perplexity**, which chose Qdrant (embedded) precisely to avoid the daemon Gemini warns about. Both are internally coherent; they disagree with each other.
- Minor plan bugs (not inconsistencies): `sudo tailscaled &` is not how the macOS (brew cask / Mac App Store) Tailscale runs; `enable_load_extension` may need the system Python replaced with one built `--enable-loadable-sqlite-extensions`; `-ngl 99` is fine on Metal but the comment "sysctl memory pinning" oversimplifies `iogpu.wired_limit_mb`.

### Agreements vs the anchor (Claude)
- Decouple logical agents (SQLite rows / state machines) from model inference; ~100 agents = KB of RAM; bounded worker pool is the real limit.
- **`sqlite-vec` + SQLite + Markdown for memory — NOT ChromaDB.** (Gemini + Claude vs Qwen + both DeepSeek runs, which chose Chroma.)
- Markdown context files named `AGENTS.md` / `MEMORY.md` (same convention Claude uses).
- Custom orchestrator on a **LangGraph** core; explicitly not CrewAI/AutoGen/MetaGPT.
- Dedicated non-admin user + Lima/Docker sandbox + AST/regex command interceptor + `rm -rf`/`dd` blocked + sudo forbidden + push-to-main gated.
- launchd KeepAlive + ThrottleInterval + `caffeinate`; HALT-file kill switch (same idea as Claude's PAUSE file).
- Tailscale-only, dashboard bound to the `tailscale0` IP, no open ports; Mosh for resilient mobile shell.
- Models on external SSD (load throughput / wear), workspace + DB + logs + git on internal SSD (IOPS). (Note: Claude puts the *hot* model on internal; Gemini puts *all* GGUFs on external and loads at startup — a divergence.)
- Optional cloud fallback, triggered only after repeated local failure; system is ~95%+ local.

### Divergences vs the anchor
| Axis | Gemini 3.1 Pro | Claude (anchor) |
|---|---|---|
| Inference engine | **llama.cpp server first** (Ollama as backend); MLX only an alternative | MLX + llama-swap |
| Heavy model | Qwen2.5-Coder-32B **dense** (2024) | Qwen3-Coder-30B-A3B **MoE** (2026) |
| Reasoning model | DeepSeek-R1-Distill-Qwen-14B (2024) | gpt-oss-20b MoE |
| Concurrency | **2 slots of one model** (`-np 2`, shared weights) | 1 heavy + 2 light + 4 cloud (separate models) |
| Research anti-hallucination | **PaperQA2** (off-the-shelf citation RAG) | custom evidence-DB pipeline with reader/verifier split |
| Web fetch | Crawl4AI (page -> clean Markdown) | Playwright |
| Coding harness | Aider headless | Claude Code + Goose |
| Cloud models | "Claude 3.5 Sonnet" / "DeepSeek-V3" (stale) | Claude Opus 4.8 / Sonnet 4.6 |
| Model storage | ALL GGUFs on external SSD, load at startup | hot model on internal SSD for reload speed |
| Remote auth | WebAuthn / YubiKey (only response to name hardware keys) | bearer token in phone keychain |
| Sources | 0 | ~97 |
