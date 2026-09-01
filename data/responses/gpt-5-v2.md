---
ai_name: OpenAI ChatGPT (GPT-5.6 Sol)
model_version_id: "GPT-5.6 Sol; knowledge cutoff not exposed in session"
provider: OpenAI
interface: ChatGPT web (paid tier)
browsing_enabled: yes
knowledge_cutoff: not disclosed
prompt_version: v2
date_run: 2026-09-01
run_by: roshanaryal1
notes_on_run: >
  Second GPT-5 capture, on prompt-v2 (RFC framing, reshuffled sections). Fresh chat, no history.
  Pair with data/responses/gpt-5.md (v1). Delivered the full A–K package. Well-sourced: ~10 real
  primary URLs (Apple newsroom, Qwen HF model card, ggml-org GGUF repo, llama.cpp server README,
  mini-swe-agent, paper-qa, Tailscale docs) + one secondary (llama.cpp issue #27473).
trust_rating: HIGH — every named tool/model resolves, GGUF sizes and benchmark numbers cited to primary sources, M6 spec correct, strong epistemic discipline ("no credible independent M6 benchmarks yet"), zero fabrication.
---

## Raw response

GPT-5.6 Sol | knowledge cutoff: not exposed to me | web browsing/tools: ON | evidence date: 31 August 2026

Your RFC asks for a concrete, production-oriented design for one continuously running base-M6 Mac mini with 32 GB unified memory, 512 GB internal storage and a 1 TB external SSD, including 100+ logical agents, autonomous coding, research, durable state, security, remote control and recovery. 

There is one important timing constraint. Apple announced the M6 Mac mini on 25 August 2026, but deliveries do not begin until 22 September 2026. Therefore, there are no credible independent M6 production benchmarks yet. Apple reports up to 170 GB/s memory bandwidth on M6 configurations and up to 4.8x faster LM Studio prompt processing than M4, but those are Apple-run July 2026 tests. I will not convert those claims into invented tokens-per-second figures. ([Apple][1])

## Decisions at a glance

| Layer                        | Final choice                                 | Why                                                                                                             |
| ---------------------------- | -------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| Host                         | Base M6 Mac mini, 32 GB                      | Fixed target. 32 GB is enough for a strong 4-bit local model, but not enough for multiple large resident models |
| Primary local model          | Qwen3.6-35B-A3B Q4_K_M                       | 35B total, only 3B activated per token, 20.4 GB GGUF, strong current coding and agent results                   |
| Local inference              | llama.cpp server                             | Best low-level control of memory, KV cache, context, loading and OpenAI-compatible APIs on this machine         |
| M6 fallback inference        | LM Studio headless                           | Apple has explicitly tested LM Studio on M6. Use only if launch-day measurements beat llama.cpp materially      |
| Local context                | 16,384 tokens initially                      | Preserves operating headroom on a 32 GB shared-memory machine                                                   |
| Model concurrency            | 1                                            | Do not run two large inference requests simultaneously                                                          |
| Agent orchestration          | Thin Python supervisor + LangGraph           | Durable checkpoints, interrupts, subgraphs, resumable tasks without maintaining 100 live model sessions         |
| Persistent operational state | SQLite WAL                                   | Appropriate for a single machine and eliminates unnecessary infrastructure                                      |
| Agent population             | 100+ logical agent records                   | Agent identities and state are cheap. Model inference is leased from one shared worker                          |
| Coding worker                | mini-SWE-agent v2                            | Very small execution loop, local-model compatible and easy to put inside isolated workspaces                    |
| Repository isolation         | Git branches + worktrees                     | Each task gets its own branch and filesystem workspace                                                          |
| Tool isolation               | Colima using Apple Virtualization Framework  | Stronger separation than unrestricted host shell while remaining practical on Apple Silicon                     |
| Research                     | LangGraph research flow + SearXNG + PaperQA2 | Separates web retrieval, literature retrieval, evidence checking and synthesis                                  |
| Web browser                  | Playwright only when HTTP retrieval fails    | Do not keep Chromium resident continuously                                                                      |
| Research integrity           | SQLite evidence ledger                       | Final writer receives verified claims and citations rather than unverified search output                        |
| Human-readable memory        | Markdown inside project                      | Decisions and findings remain readable without the system                                                       |
| Retrieval memory later       | LanceDB + BGE-M3                             | Embedded rather than another server. Add only when corpus size justifies it                                     |
| Remote access                | Tailscale + local FastAPI control panel      | Private tailnet access. No public dashboard                                                                     |
| 24/7 operation               | launchd + heartbeat + leases + watchdog      | Survives process crashes and reboots                                                                            |
| Secrets                      | Separate credential broker                   | The autonomous account never receives raw personal credentials                                                  |
| Cloud                        | Optional escalation only                     | Fully functional local baseline. Cloud is not required                                                          |

The core architectural decision is this:

100 agents should mean 100 durable identities, queues and task contexts, not 100 running LLMs.

On 32 GB, one high-quality inference worker feeding a large population of logical agents is far more useful than a swarm competing for the same unified memory.

---

# 1. On-device inference

## Final model: Qwen3.6-35B-A3B Q4_K_M

This is the strongest fit I found for the machine.

Qwen3.6-35B-A3B has 35 billion total parameters but activates about 3 billion. It has 40 layers, 256 experts and 8 routed experts plus one shared expert per token. Qwen gives it a native context length of 262,144 tokens. ([Hugging Face][2])

The official Qwen results report:

| Evaluation         | Qwen3.6-35B-A3B |
| ------------------ | --------------: |
| SWE-bench Verified |            73.4 |
| Terminal-Bench 2.0 |            51.5 |
| LiveCodeBench v6   |            80.4 |
| MCPMark            |            37.0 |
| QwenWebBench       |            1397 |

These are vendor-run model results, not Mac mini results. In particular, Qwen ran SWE-bench with an internal bash/file-edit setup and a 200K context window. Terminal-Bench used 32 CPUs, 48 GB RAM and a 256K context. Do not expect these scores from a 4-bit model at 16K context on the Mac. They demonstrate capability, not your expected workstation throughput. ([Hugging Face][2])

The key hardware fact is quantized size:

* Q4_K_M: 20.4 GB
* Q8_0: 36.9 GB
* BF16: 69.4 GB

Q8 is already larger than the Mac's total physical memory before KV cache, macOS or tools. Q4_K_M is therefore the correct starting quantization. ([Hugging Face][3])

## Why not simply use a smaller model?

A 7B to 12B model would give more concurrency, but that is the wrong optimization for this system.

You are trying to perform repository-level coding, planning, debugging and evidence synthesis without constant supervision. One stronger model operating serially should complete more useful jobs than several weaker models producing more failed trajectories.

The MoE structure also helps. Only part of Qwen3.6 is active for each token, even though all weights remain resident.

## Why not use 128K or 262K context?

Qwen recommends very large context for its full intended capabilities. ([Hugging Face][2])

Do not follow that recommendation on this 32 GB machine.

Start at:

* llama context: 16,384
* normal working input ceiling: approximately 12,000
* remaining space: generation, tool responses and state
* parallel slots: 1

Long-lived agent state belongs in SQLite and files, not endlessly growing prompts.

The orchestration layer should compact old interactions into structured state before the next inference call.

## Inference server

Use llama.cpp.

Current llama.cpp supports OpenAI-compatible APIs, parallel decoding, continuous batching, monitoring, schema-constrained output and controllable KV-cache types. It allows explicit context size and Q8 or Q4 KV caches. ([GitHub][4])

Start with:

```bash
llama serve \
  -hf ggml-org/Qwen3.6-35B-A3B-GGUF:Q4_K_M \
  --host 127.0.0.1 \
  --port 8080 \
  --ctx-size 16384 \
  --parallel 1 \
  --cache-type-k q8_0 \
  --cache-type-v q8_0 \
  --flash-attn auto
```

The official GGUF repository explicitly supports loading this Q4 model directly through llama.cpp. ([Hugging Face][3])

Do not enable llama.cpp's experimental built-in shell or file tools. The server documentation itself warns against enabling them in untrusted environments. Keep inference separate from execution. ([GitHub][4])

## M6-specific warning

There is an unresolved llama.cpp issue filed on 21 August 2026 concerning Apple's newer tensor functionality on M5/A19-class devices. The reporter observed that the Metal tensor API was disabled and that prompt prefilling was slower than expected. M6 is not yet shipping, so it is not possible to say whether the same issue affects M6. ([GitHub][5])

Therefore perform an acceptance test on the actual M6.

Run Qwen3.6 Q4_K_M through:

1. llama.cpp
2. LM Studio headless

Use identical prompts and settings.

Measure:

* cold model load
* 2K prompt time
* 8K prompt time
* 12K prompt time
* generation tokens/sec
* peak memory
* tool-call formatting accuracy
* ten real coding jobs
* ten real research jobs
* successful jobs per hour

Keep llama.cpp unless LM Studio improves successful end-to-end work per hour by at least about 20 percent without increasing failures or memory pressure.

That is the only part of this architecture I would leave subject to an M6 launch measurement.

---

# 2. Agent runtimes and orchestration

## Pick: LangGraph inside a small custom supervisor

Do not make LangGraph the whole product.

Use it for what it is good at:

* durable execution graphs
* checkpoints
* resumability
* human interrupts
* nested agent subgraphs
* state transitions

LangGraph explicitly provides checkpoint persistence and SQLite checkpointer support, and its subgraph model supports different persistence patterns for repeated agents. ([Docs by LangChain][6])

Build a thin supervisor around it for:

* queues
* scheduling
* priorities
* resource leases
* project registration
* security policy
* watchdogs
* approvals
* model routing
* agent creation

Do not add another orchestration product around LangGraph.

## Runtime structure

Each logical agent is a database record similar to:

```text
agent_id
role
parent_agent_id
project_id
project_root
worktree
allowed_tools
permission_tier
model_profile
context_digest
token_budget
time_budget
status
heartbeat
created_at
```

Each task contains:

```text
task_id
objective
parent_task
dependencies
priority
assigned_agent
state
lease_owner
lease_expiry
attempt_count
stop_reason
created_at
updated_at
```

The scheduler can therefore hold 100, 500 or several thousand logical agents without corresponding model processes.

## Execution topology

Use:

Coordinator → specialist workers → verifier

Not:

100-agent peer swarm.

The coordinator breaks objectives into tasks. Specialists perform jobs. A separate verifier checks significant outputs before tasks become complete.

That gives you agent specialization without uncontrolled message chatter.

---

# 3. Many-agent design on small hardware

The practical limit is not the number of agent definitions.

The limit is simultaneous memory-intensive execution.

Set:

```text
Logical agents registered: 100+
Concurrent local LLM calls: 1
Concurrent heavy tool jobs: 1
Concurrent light tool jobs: up to 2
Resident large models: 1
Resident secondary LLMs: 0
```

## Model lease

Every LLM-requiring job requests a model lease.

Conceptually:

```text
job ready
   ↓
request model lease
   ↓
lease available?
   ├─ no → remain queued
   └─ yes
       ↓
       assemble bounded context
       ↓
       inference
       ↓
       release lease
       ↓
       execute tools if required
```

This prevents five agents from independently driving the model into memory pressure.

## Agent factory

Do not preconfigure 100 prompt files.

The coordinator can create an agent definition dynamically:

```json
{
  "role": "dependency-debugger",
  "objective": "Identify cause of failing integration tests",
  "tools": ["read", "grep", "shell", "git_diff"],
  "permission": "workspace-write",
  "budget": {
    "model_calls": 20,
    "minutes": 40
  }
}
```

The agent disappears from active scheduling when done, while its history remains durable.

That is how you get 100+ agents on 32 GB.

---

# 4. Autonomous coding

## Actual pick: mini-SWE-agent v2

OpenHands is the stronger full application if you want a ready-made coding platform. For this machine, I would not make it the core.

mini-SWE-agent v2 is a better worker inside your own supervisor.

The project describes an agent implementation of roughly 100 lines, supports local environments and multiple isolation systems, and supports models through LiteLLM. Its shell-first execution model is also easy to place inside disposable containers. ([GitHub][7])

Its published >74 percent SWE-bench Verified figure should not be mistaken for expected Qwen-on-M6 performance. The value here is its architecture, not that headline score.

## Coding workflow

For every code task:

```text
Registered project
      ↓
git fetch/status
      ↓
create agent/<task-id> branch
      ↓
create separate Git worktree
      ↓
mini-SWE coding worker
      ↓
edit
      ↓
build/test/lint
      ↓
failure?
  ├─ yes → analyse → modify → retest
  └─ no
      ↓
independent verifier
      ↓
local commit
      ↓
task report
```

The verifier should receive:

* task specification
* diff
* test logs
* lint results
* relevant repository context

It should not receive the coder's full reasoning history.

That reduces correlated mistakes.

## Git policy

Allowed unattended:

* status
* log
* diff
* branch creation
* worktree creation
* editing task worktree
* test execution
* local commit

Approval required:

* push to remote
* merge to protected branch
* force push
* delete remote branch
* alter CI/CD secrets
* create release
* publish package

Forbidden:

* rewrite protected branch history
* delete arbitrary repositories
* operate against unregistered repository roots

A coding failure can therefore damage its disposable branch, not your main branch.

---

# 5. Autonomous research

## Pick: custom research graph

Use four stages:

```text
Question
   ↓
Search planner
   ↓
Web / literature retrieval
   ↓
Evidence extraction
   ↓
Claim verifier
   ↓
Contradiction pass
   ↓
Synthesis
```

### Web search

Run a local SearXNG instance.

This gives the agent a search API without tying the architecture to one commercial search provider.

### Academic work

Use PaperQA2.

PaperQA2 currently supports PDFs, text, Office documents and source code, with particular focus on scientific literature. It includes citation-oriented retrieval and a dedicated contradiction mode. It also documents locally hosted model and local sentence-transformer support. ([GitHub][8])

### Browser

Use plain HTTP retrieval first.

Start Playwright only when:

* JavaScript rendering is required
* pagination cannot be obtained directly
* content requires interaction
* a browser-based source must be visually verified

Then terminate it.

Chromium should not consume memory all night while nothing needs it.

## Citation integrity

Do not allow the final writer to invent a bibliography from memory.

Create an evidence table:

```text
claim_id
claim_text
source_url
source_title
publisher
retrieved_at
content_sha256
locator
evidence_excerpt
stance
verification_status
verified_by
```

`stance` is:

```text
supports
contradicts
unclear
```

Before final synthesis, a verifier reopens each source.

Only rows with:

```text
verification_status = verified
```

can be cited as factual support.

If the source does not support the claim, the final writer either drops the claim or marks it as inference.

This is the single most important research control in the build.

---

# 6. Durable memory

Do not start with a knowledge graph.

Use three layers.

## Layer 1: human-readable project memory

Inside each registered project:

```text
.agentlab/
    PROJECT.md
    decisions.md
    findings.md
    open_questions.md
    experiments/
    reports/
```

This remains useful even if the AI system is removed.

## Layer 2: SQLite

SQLite is the system of record for:

* projects
* agents
* jobs
* dependencies
* executions
* checkpoints
* approvals
* evidence
* decisions
* errors
* budgets
* audit events

Enable WAL mode.

Use foreign keys.

Checkpoint after every meaningful state transition.

SQLite FTS5 gives adequate initial full-text retrieval.

## Layer 3: vector retrieval when needed

Later add:

* LanceDB
* BGE-M3 embeddings

LanceDB is attractive here because it can operate embedded in-process rather than forcing you to maintain a separate database server.

BGE-M3 supports dense and sparse retrieval and multilingual material, which is useful for heterogeneous research corpora. ([LanceDB][9])

Do not keep the embedding model resident.

Load it for ingestion batches, write embeddings, then release it.

## When should a knowledge graph be added?

Only after you can name queries that SQLite relationships plus hybrid search cannot answer well.

For example:

```text
Which organisations have repeatedly funded researchers who made conflicting claims about X across these 30,000 papers?
```

Until that need exists, a graph database creates work rather than capability.

---

# 7. Machine control and isolation

This is where I would be stricter than most personal-agent builds.

## Separate macOS identity

Create a dedicated standard user:

```text
agentlab
```

Not an administrator.

Do not run the autonomous supervisor from your personal login.

Do not grant `agentlab`:

* Full Disk Access
* access to your personal home directory
* browser profiles containing your normal logins
* personal cloud drives
* your personal SSH keys
* financial files
* system administration rights

This changes the security problem fundamentally.

A shell running as your normal user cannot meaningfully be prevented from reading secrets that your normal user can read.

## Tool execution

Run dangerous build and test processes in Colima.

Use Apple's Virtualization Framework backend rather than unrestricted host execution.

Give the VM explicit mounts only.

For example:

```yaml
vmType: vz
cpu: 4
memory: 3
rootDisk: 30
mountType: virtiofs

mounts:
  - location: ~/Worktrees
    writable: true

  - location: /Volumes/AIData/agent-scratch
    writable: true
```

Do not leave the default home-directory mount in place.

Each disposable coding job can then impose its own limits:

```bash
docker run --rm \
  --memory=1536m \
  --cpus=2 \
  -v "$WORKTREE:/workspace:rw" \
  -w /workspace \
  agentlab-runner:latest \
  ./agent-entrypoint
```

If a project genuinely requires more than the available tool memory, temporarily unload the LLM and give the build process more RAM.

llama.cpp now exposes model load/unload functionality, which makes this kind of resource-phase switching practical. ([GitHub][4])

## Permission tiers

| Tier | Policy                     | Examples                                                                                                            |
| ---- | -------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| P0   | Automatic                  | Read registered files, search web, Git diff/status/log, query databases                                             |
| P1   | Automatic inside workspace | Edit worktree, execute tests, build container, create branch, local commit                                          |
| P2   | Human approval             | Push, merge protected branch, cloud upload, host package install, browser login, write outside project              |
| P3   | Blocked                    | sudo, personal home access, financial transactions, Keychain extraction, disk formatting, disable security controls |

## Credentials

Never inject raw secrets into an autonomous shell.

For optional services build a narrow credential broker.

Example:

```text
agent asks:
"push commit 47ab... to repository X"

broker checks:
project X permitted?
approval present?
target branch permitted?

if yes:
broker performs push

agent never sees the private key
```

Use the same principle for cloud LLM APIs.

The agent submits a permitted request to the broker. The broker attaches the secret.

---

# 8. Running continuously

Use macOS launchd.

Do not depend on an open Terminal window, `nohup`, `tmux` or manually restarted Python.

## Supervisor responsibilities

The supervisor should own:

* scheduler
* LangGraph execution
* SQLite
* policy engine
* watchdog
* local API
* model process lifecycle
* agent registry
* notifications

## Recovery design

Each running job has a lease expiry.

Example:

```text
status = running
lease_owner = worker-1
lease_expires = 2026-09-23T03:12:00
```

The worker updates the lease every 30 seconds.

After a crash:

1. launchd restarts the supervisor.
2. Supervisor opens SQLite.
3. It finds expired `running` leases.
4. Jobs are moved back to `ready`.
5. LangGraph reloads their last durable checkpoint.
6. Idempotency guards verify what already happened.
7. Work resumes.

Do not infer recovery from an agent chat transcript alone.

## Watchdog

Every minute check:

* supervisor heartbeat
* llama.cpp health
* external SSD mounted
* external SSD writable
* free internal storage
* free external storage
* memory pressure
* SQLite accessibility
* model API response
* number of repeated failures

Actions:

```text
single model crash
→ restart model

3 repeated model crashes
→ pause model jobs
→ notify operator

external SSD missing
→ stop jobs touching external data
→ keep scheduler alive

internal disk < 15% free
→ stop new jobs
→ rotate caches
→ notify operator

database error
→ enter safe mode
→ no writes except diagnostic log
```

## Default runaway limits

Per ordinary task:

```text
Maximum wall time:       4 hours
Maximum model calls:     80
Maximum repair cycles:   25
Repeated identical fail: 3
Maximum child-agent depth: 4
Default child agents:    12
```

The limits can be overridden per project.

This prevents an agent from spending three days rebuilding the same broken dependency.

---

# 9. Remote reach

## Pick: Tailscale

Do not put the dashboard on the public Internet.

For this particular always-on machine I prefer the open-source `tailscaled` variant because it can run during system boot before anyone logs in.

Tailscale documents Homebrew installation as:

```bash
brew install --formula tailscale
sudo brew services start tailscale
sudo tailscale up
sudo tailscale status
```

Its macOS documentation notes that this version can operate at boot before login, although it is less tested than its main macOS application. ([GitHub][10])

## Local control panel

Run the control API only on:

```text
127.0.0.1:8787
```

Expose it inside the tailnet:

```bash
tailscale serve --bg localhost:8787
```

With background mode, Tailscale documents that Serve configuration resumes after a reboot or Tailscale restart. ([Tailscale][11])

The phone interface should expose:

* system state
* queued tasks
* running task
* agent tree
* recent results
* logs
* approve
* reject
* pause project
* pause all
* emergency stop
* submit new objective

Do not expose an unrestricted shell as the primary phone UI.

## Emergency SSH

Enable macOS SSH with key authentication only.

Then forward a tailnet-only port:

```bash
tailscale serve --bg \
  --tcp=2222 \
  tcp://localhost:22
```

Tailscale explicitly supports raw TCP forwarding to local services such as SSH. ([Tailscale][11])

No router port-forwarding.

No Funnel.

No public reverse proxy.

## Emergency stop

The dashboard needs one button that:

1. stops issuing model leases
2. cancels pending tool execution
3. terminates running tool containers
4. stops llama.cpp
5. marks running jobs `paused_by_operator`
6. leaves SQLite and logs intact

A second local-only administrative command can be:

```bash
agentlab emergency-stop
```

This must not delete anything.

---

# 10. Storage and market comparison

## Storage layout

### Internal SSD

Keep operational state and active code internal.

```text
~/AI-Lab/
    app/
    config/
    state/
    logs/
    projects/

~/Worktrees/
```

Target limits:

| Internal use                |  Target |
| --------------------------- | ------: |
| macOS, apps, updates        | ~100 GB |
| AI-Lab operational state    |  <20 GB |
| Active worktrees            | <120 GB |
| Browser/tool cache and logs |  <30 GB |
| Minimum free headroom       |  100 GB |

Do not try to fill a 512 GB SSD to its advertised capacity.

### External SSD

Format as APFS Encrypted and call it:

```text
AIData
```

Layout:

```text
/Volumes/AIData/
    models/
    corpora/
    repos/
    artifacts/
    caches/
    backups/
    agent-scratch/
```

Planning allocation:

| External use               | Budget |
| -------------------------- | -----: |
| Models                     | 250 GB |
| Papers and datasets        | 250 GB |
| Repository mirrors/archive | 160 GB |
| Archived task artifacts    | 100 GB |
| Caches                     |  80 GB |
| Backups                    |  60 GB |
| Spare                      | ~30 GB |

Do not put the canonical SQLite task queue on the removable disk.

If the external SSD disappears, the supervisor should still know exactly what is happening.

## Category comparison

The "best" columns below are architectural judgments for this use case, not universal benchmark rankings.

| Category         | Best overall                             | Best on this Mac      | Best open           | Best lightweight       | Best mature/stable    | Newest/high-potential                    | Actual choice               |
| ---------------- | ---------------------------------------- | --------------------- | ------------------- | ---------------------- | --------------------- | --------------------------------------- | --------------------------- |
| Inference        | vLLM on NVIDIA                           | llama.cpp / LM Studio | llama.cpp           | llama.cpp              | llama.cpp             | Apple-native MLX / newer LM Studio stack | llama.cpp                   |
| Orchestration    | LangGraph                                | LangGraph             | LangGraph           | Python + SQLite        | LangGraph             | emerging multi-agent frameworks          | LangGraph + thin supervisor |
| Coding           | OpenHands                                | mini-SWE-agent        | OpenHands           | mini-SWE-agent         | Aider                 | mini-SWE v2                              | mini-SWE-agent              |
| Research         | Purpose-built research graph             | custom graph          | PaperQA2 + SearXNG  | SearXNG + simple fetch | PaperQA2              | specialized agentic literature systems   | custom graph                |
| State            | PostgreSQL for multi-host systems        | SQLite                | SQLite              | SQLite                 | SQLite                | embedded hybrid stores                   | SQLite                      |
| Vector retrieval | pgvector or dedicated vector DB at scale | LanceDB               | LanceDB             | LanceDB                | pgvector              | embedded hybrid search                   | add LanceDB later           |
| Isolation        | Separate remote execution hosts          | Colima VZ             | Colima              | process sandbox        | VM/container approach | newer Apple VM tooling                   | Colima VZ                   |
| Remote           | private overlay network                  | Tailscale             | WireGuard/Headscale | Tailscale              | Tailscale             | Tailscale Grants                         | Tailscale                   |

One particularly current exclusion is LangChain's `open_deep_research` repository, which was archived on 21 August 2026. I would not start a new production system on an archived research project. ([GitHub][12])

---

# A. Technology stack

| Layer               | Chosen technology                 | Alternatives considered            | Rationale                                       |
| ------------------- | --------------------------------- | ---------------------------------- | ---------------------------------------------- |
| OS                  | macOS 27 on release/stable build  | Linux VM full-time                 | Native Apple GPU access                         |
| LLM                 | Qwen3.6-35B-A3B Q4_K_M            | Qwen smaller models, gpt-oss-20b   | Best balance of model capability and 32 GB fit  |
| Inference           | llama.cpp                         | LM Studio, MLX, Ollama             | Direct resource control and simple API          |
| Supervisor          | Python 3.12                       | Go, Node                           | Strong AI ecosystem and orchestration libraries |
| Workflow            | LangGraph                         | AutoGen, CrewAI, bespoke-only      | Durable state and resumable graphs              |
| Queue               | SQLite                            | Redis, RabbitMQ                    | Single host does not justify another service    |
| Coding              | mini-SWE-agent                    | OpenHands, Aider                   | Small worker that fits your own scheduler       |
| Source isolation    | Git worktrees                     | cloned repository per job          | Cheap, native, traceable                        |
| Execution isolation | Colima VZ + containers            | Docker Desktop, unrestricted shell | Lower host exposure                             |
| Search              | SearXNG                           | paid search APIs                   | Local search gateway                            |
| Papers              | PaperQA2                          | generic RAG                        | Literature and citation focus                   |
| Browser             | Playwright                        | Selenium                           | Good programmable browser support               |
| Memory              | Markdown + SQLite                 | Postgres, graph DB                 | Simple and durable                              |
| Vector memory       | LanceDB later                     | Qdrant, Milvus                     | Embedded and appropriate for one machine        |
| Embeddings          | BGE-M3, loaded on demand          | cloud embeddings                   | Local and multilingual                          |
| Remote              | Tailscale                         | public HTTPS, raw WireGuard        | Private and simple                              |
| Control UI          | FastAPI + small responsive web UI | large dashboard product            | Low resource footprint                          |
| Service management  | launchd                           | cron, terminal sessions            | macOS-native restart management                 |

---

# B. Architecture diagram

```text
                    PHONE / LAPTOP
                          |
                     TAILSCALE
                          |
                 +------------------+
                 | Control API / UI |
                 | 127.0.0.1:8787   |
                 +---------+--------+
                           |
                   POLICY / APPROVAL
                           |
              +------------v-------------+
              |      AGENT SUPERVISOR    |
              | Python + LangGraph       |
              +------+----------+--------+
                     |          |
            +--------+          +----------------+
            |                                    |
      +-----v------+                       +-----v------+
      | SQLite    |                       | Scheduler  |
      | WAL       |                       | + leases   |
      +-----+------+                       +-----+------+
            |                                    |
     state / jobs /                      Agent factory
     checkpoints /                             |
     evidence / audit                 100+ logical agents
                                                 |
                           +---------------------+------------------+
                           |                     |                  |
                    +------v------+       +------v------+    +------v------+
                    | Coding      |       | Research    |    | Verifier    |
                    | worker      |       | worker      |    | agents      |
                    +------+------+       +------+------+    +------+------+
                           |                     |                  |
                    mini-SWE-agent          SearXNG               |
                           |                 HTTP fetch             |
                     Git worktree           Playwright             |
                           |                 PaperQA2               |
                    Colima container       Evidence ledger         |
                           |                     |                  |
                           +----------+----------+------------------+
                                      |
                                MODEL ROUTER
                                      |
                         +------------+------------+
                         |                         |
                 LOCAL, DEFAULT             CLOUD, OPTIONAL
                 llama.cpp                  credential broker
                         |                         |
                  Qwen3.6 Q4                 selected API
```

---

# C. Resource plan

This is a design budget. It is not a measured M6 memory trace because the hardware has not shipped.

| Component                         |             Target |
| --------------------------------- | -----------------: |
| Qwen Q4 weights                   |            20.4 GB |
| macOS + base daemons              |   target 5 to 6 GB |
| KV/runtime/model buffers          | target 1 to 1.5 GB |
| Supervisor + SQLite               |           <0.75 GB |
| One normal tool process           |      0.5 to 1.5 GB |
| Browser when active               |          1 to 2 GB |
| Safety reserve / filesystem cache |              2+ GB |

That is tight enough that resource phases matter.

Do not run at the same time:

```text
large model
+ several Chromium processes
+ large compiler
+ multiple containers
```

When a very large build needs RAM:

```text
checkpoint task
→ unload LLM
→ perform build/test
→ persist output
→ reload LLM
→ continue
```

The expected first bottleneck is memory capacity and memory traffic, followed by long-prompt prefilling.

It is not the number of agent records.

---

# D. 100+ agent model

Use 100+ logical agents in SQLite.

Use one LLM inference lease.

Use dynamic agent creation.

Use coordinator-worker-verifier topology.

Do not use persistent peer-to-peer conversations between dozens of agents.

A 150-agent system might have:

```text
1 coordinator
8 coding role templates
10 research role templates
8 verification role templates
5 operations role templates
118 dormant/generated specialist identities
```

At any instant, perhaps:

```text
1 agent waiting on Qwen
1 container executing tests
1 researcher downloading documents
147 sleeping
```

That is feasible.

---

# E. Model assignment

Do not load a different LLM for every job.

| Task                    | Default                                                   |
| ----------------------- | -------------------------------------------------------- |
| Planning                | Qwen3.6                                                   |
| Coding                  | Qwen3.6                                                   |
| Debugging               | Qwen3.6                                                   |
| Research planning       | Qwen3.6                                                   |
| Evidence interpretation | Qwen3.6                                                   |
| Summarisation           | Qwen3.6 with smaller output budget                        |
| Classification          | Rules first, Qwen only when semantic judgment is required |
| Verification            | Fresh Qwen context                                        |
| Final synthesis         | Qwen3.6                                                   |
| Embeddings              | BGE-M3 on demand                                          |
| Difficult escalation    | Optional cloud model                                      |

Why one model?

Switching models constantly on a 32 GB system spends time on model load and unload while reducing usable cache.

Role prompts should vary. Resident weights should not.

Optional cloud inference should only activate when:

* local model fails the same verified objective twice
* input cannot reasonably be compacted into local context
* a final high-consequence technical review benefits from another model
* a task has an explicit cloud-enabled policy

Cloud remains off by default.

---

# F. Continuous-operation design

The overnight loop should be:

```text
wake/restart
↓
check hardware + storage
↓
recover expired leases
↓
read ready queue
↓
choose highest-priority unblocked task
↓
create or resume specialist
↓
execute
↓
verify
↓
persist result
↓
generate follow-up tasks
↓
continue
```

Every transition is persisted before the next consequential step.

No critical state lives only in Python memory.

No task is considered complete because an LLM says "done."

Completion requires an explicit verifier condition.

Examples:

```text
coding:
tests pass + diff reviewed

research:
required claims verified + citations resolvable

experiment:
command exited + artifact exists + result parsed

documentation:
required sections present + references verified
```

---

# G. Remote-operation design

Phone:

```text
Tailscale
→ HTTPS Serve
→ local FastAPI dashboard
```

Emergency administrator access:

```text
Tailscale
→ TCP 2222
→ localhost SSH 22
```

Control panel actions:

```text
submit objective
inspect queue
read report
approve P2 action
reject P2 action
change priority
pause project
stop task
stop all
```

Keep inference port 8080 bound to localhost.

Keep dashboard 8787 bound to localhost.

Only Tailscale exposes them.

---

# H. Security design

The operating rule is:

Capability is granted to individual jobs, not permanently to the AI.

The default autonomous account can work heavily inside:

```text
~/Worktrees
/Volumes/AIData/corpora
/Volumes/AIData/artifacts
/Volumes/AIData/agent-scratch
```

It cannot automatically work inside:

```text
your personal home
Mail
Messages
Photos
personal cloud storage
financial folders
password stores
Keychain
system configuration
```

Require approval for:

* raw credential use
* pushing code
* merging protected branches
* publishing anything
* installing host software
* enabling new network destinations
* browser authentication
* sending local files to a cloud model
* deleting outside disposable workspaces

Block financial transactions completely.

Maintain an append-only audit event for every tool call containing:

```text
timestamp
task
agent
tool
arguments hash
target
policy decision
exit code
duration
result hash
```

---

# I. Installation procedure

## Phase 1: operating system and directories

Create the `agentlab` standard macOS account manually.

Format the external SSD APFS Encrypted as `AIData`.

Install Homebrew if required, then:

```bash
brew update

brew install \
  uv \
  git \
  git-lfs \
  jq \
  ripgrep \
  fd \
  sqlite \
  llama.cpp \
  colima \
  docker
```

Create directories:

```bash
mkdir -p ~/AI-Lab/app
mkdir -p ~/AI-Lab/config
mkdir -p ~/AI-Lab/state
mkdir -p ~/AI-Lab/logs
mkdir -p ~/AI-Lab/projects
mkdir -p ~/Worktrees

mkdir -p /Volumes/AIData/models
mkdir -p /Volumes/AIData/corpora
mkdir -p /Volumes/AIData/repos
mkdir -p /Volumes/AIData/artifacts
mkdir -p /Volumes/AIData/caches
mkdir -p /Volumes/AIData/backups
mkdir -p /Volumes/AIData/agent-scratch

chmod 700 ~/AI-Lab
chmod 700 ~/Worktrees
```

Test:

```bash
test -w ~/AI-Lab
test -w ~/Worktrees
test -w /Volumes/AIData
```

Rollback: none required. These are data directories.

## Phase 2: Python supervisor

```bash
cd ~/AI-Lab/app

uv init --python 3.12 agentlab
cd agentlab

uv add \
  langgraph \
  langgraph-checkpoint-sqlite \
  fastapi \
  uvicorn \
  pydantic \
  aiosqlite \
  httpx \
  litellm \
  mini-swe-agent
```

Commit the resulting:

```text
pyproject.toml
uv.lock
```

Do not install every possible AI library.

## Phase 3: local model

Start with:

```bash
llama serve \
  -hf ggml-org/Qwen3.6-35B-A3B-GGUF:Q4_K_M \
  --host 127.0.0.1 \
  --port 8080 \
  --ctx-size 16384 \
  --parallel 1 \
  --cache-type-k q8_0 \
  --cache-type-v q8_0 \
  --flash-attn auto
```

Test:

```bash
curl -fsS http://127.0.0.1:8080/health
```

Then make one OpenAI-compatible completion call.

If it fails under memory pressure:

1. reduce context to 12,288
2. test again
3. do not reduce model quantization first

## Phase 4: Colima

Run:

```bash
colima start --edit
```

Configure only required mounts.

Then:

```bash
colima start
colima status
docker run --rm alpine:latest echo "container ok"
```

Test that the container cannot see your personal files.

That negative test matters as much as the positive one.

## Phase 5: research

Add:

```bash
uv add \
  paper-qa \
  playwright

uv run playwright install chromium
```

Run SearXNG locally in a container:

```bash
docker run -d \
  --name searxng \
  --restart unless-stopped \
  -p 127.0.0.1:8888:8080 \
  -v ~/AI-Lab/config/searxng:/etc/searxng:rw \
  docker.io/searxng/searxng:latest
```

Enable JSON search results in its configuration.

Test:

```bash
curl \
  'http://127.0.0.1:8888/search?q=apple+m6&format=json'
```

## Phase 6: vector memory

Only after the basic system is working:

```bash
uv add \
  lancedb \
  sentence-transformers
```

Put the index on:

```text
/Volumes/AIData/corpora/index
```

Do not run continuous re-embedding.

Schedule ingestion batches.

## Phase 7: launchd

Create:

```text
/Library/LaunchDaemons/nz.agentlab.supervisor.plist
```

Conceptually:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC
 "-//Apple//DTD PLIST 1.0//EN"
 "http://www.apple.com/DTDs/PropertyList-1.0.dtd">

<plist version="1.0">
<dict>

  <key>Label</key>
  <string>nz.agentlab.supervisor</string>

  <key>UserName</key>
  <string>agentlab</string>

  <key>ProgramArguments</key>
  <array>
    <string>/Users/agentlab/AI-Lab/app/agentlab/.venv/bin/python</string>
    <string>-m</string>
    <string>agentlab.supervisor</string>
  </array>

  <key>WorkingDirectory</key>
  <string>/Users/agentlab/AI-Lab/app/agentlab</string>

  <key>RunAtLoad</key>
  <true/>

  <key>KeepAlive</key>
  <true/>

  <key>StandardOutPath</key>
  <string>/Users/agentlab/AI-Lab/logs/supervisor.out.log</string>

  <key>StandardErrorPath</key>
  <string>/Users/agentlab/AI-Lab/logs/supervisor.err.log</string>

</dict>
</plist>
```

Validate:

```bash
sudo plutil -lint \
  /Library/LaunchDaemons/nz.agentlab.supervisor.plist
```

Load:

```bash
sudo launchctl bootstrap system \
  /Library/LaunchDaemons/nz.agentlab.supervisor.plist
```

Restart:

```bash
sudo launchctl kickstart -k \
  system/nz.agentlab.supervisor
```

Rollback:

```bash
sudo launchctl bootout \
  system/nz.agentlab.supervisor
```

Then remove the plist.

## Phase 8: remote access

```bash
brew install --formula tailscale

sudo brew services start tailscale
sudo tailscale up
sudo tailscale status
```

Dashboard:

```bash
tailscale serve --bg localhost:8787
```

SSH forwarder:

```bash
tailscale serve --bg \
  --tcp=2222 \
  tcp://localhost:22
```

Test both from a phone on mobile data, not from the home Wi-Fi.

Then test a reboot.

The acceptance condition is:

```text
power cycle
→ Mac starts
→ network returns
→ Tailscale returns
→ supervisor returns
→ model returns
→ unfinished task resumes
→ phone dashboard is reachable
```

If that does not work, the system is not yet 24/7-ready.

---

# J. Exclusion list

I would explicitly exclude these from version 1:

| Technology/approach                    | Reason                                                                              |
| -------------------------------------- | --------------------------------------------------------------------------------- |
| Kubernetes                             | Wrong scale for one Mac                                                             |
| Redis                                  | SQLite can handle this queue                                                        |
| RabbitMQ                               | More operational work without benefit                                               |
| Celery                                 | Unnecessary distributed-task layer                                                  |
| PostgreSQL                             | Add only when moving to multiple hosts                                              |
| Milvus                                 | Excessive for personal embedded retrieval                                           |
| Qdrant server initially                | Another service before there is evidence it is needed                               |
| Knowledge graph                        | Premature complexity                                                                |
| Docker Desktop                         | Colima is sufficient                                                                |
| 100 running LLM agents                 | Destroys throughput and memory                                                      |
| Qwen Q8                                | 36.9 GB weights alone cannot fit                                                    |
| 262K local context                     | Bad use of 32 GB shared memory                                                      |
| Multiple resident large LLMs           | Insufficient memory                                                                 |
| Model swapping for each role           | Wastes time                                                                         |
| OpenHands as entire platform           | Strong product, but duplicates supervisor functions and adds weight                 |
| Crew-style swarm as core architecture  | Too much agent chatter and uncontrolled concurrency                                 |
| Ollama as another layer                | Convenient, but unnecessary when llama.cpp already provides the desired server      |
| mlx_lm server as production core today | Attractive Apple stack, but not my first choice for this unattended production role |
| Archived open_deep_research            | Project was archived in August 2026                                                 |
| Public web dashboard                   | Unnecessary attack surface                                                          |
| Tailscale Funnel                       | Makes private control plane public                                                  |
| Full Disk Access                       | Violates the isolation objective                                                    |
| macOS Accessibility control by default | Gives excessive GUI authority                                                       |
| Personal account as agent account      | Defeats secret isolation                                                            |
| Mandatory commercial LLM API           | Violates local-first requirement                                                    |

---

# K. Scaling path

## At 64 GB

Change:

* consider Qwen Q8, whose current GGUF is 36.9 GB
* raise useful context to 32K or 64K after testing
* keep one small embedding/classification model resident if useful
* permit larger tool containers
* potentially run two inference slots if throughput measurements justify it

Do not immediately run two giant models merely because they fit.

## At 96 GB

You can move into:

* 70B-class Q4 models
* higher quantization of 35B models
* larger context
* resident embedding/reranking model
* two genuine local LLM workers
* larger research indices

The scheduler architecture does not change.

## At 128+ GB

Consider:

* multiple resident specialist models
* large coding model + separate reasoning model
* higher local concurrency
* larger document contexts
* persistent reranker
* more simultaneous browser/container jobs

SQLite can still remain if this is one computer.

## Add an NVIDIA GPU server

This is where the architecture pays off.

Do not move orchestration.

Keep the M6 Mac as:

```text
control plane
scheduler
SQLite
dashboard
policy
memory
remote access
```

Move inference to:

```text
NVIDIA server
→ vLLM or SGLang
→ OpenAI-compatible endpoint
```

The model router simply changes its destination.

Then raise inference workers from:

```text
1
```

to perhaps:

```text
2, 4, 8...
```

according to measured server capacity.

## Add multiple compute machines

Only then replace SQLite coordination with PostgreSQL if concurrent distributed writers justify it.

Workers should claim leased jobs from the central queue.

You still do not create 100 permanent LLM processes.

---

# Implementation sequence I recommend

Build it in this order:

1. Dedicated macOS account.
2. Encrypted external SSD and directory layout.
3. llama.cpp + Qwen3.6 Q4.
4. M6 acceptance benchmark against LM Studio.
5. Python supervisor + SQLite.
6. One reliable autonomous task loop.
7. Git worktrees.
8. mini-SWE coding worker.
9. Colima isolation.
10. Research retrieval + evidence ledger.
11. PaperQA2.
12. Durable project memory.
13. Dynamic agent generation.
14. 100-agent queue stress test.
15. launchd recovery.
16. Tailscale remote control.
17. Approval broker.
18. Vector retrieval only after accumulated data warrants it.

Do not start by building the 100-agent layer.

First prove this chain:

```text
one objective
→ one plan
→ one isolated execution
→ one verification
→ one durable result
→ crash
→ successful resume
```

Then scale the number of logical agents.

That sequence will save substantial debugging time.

## Final build specification

If I were installing this exact machine, the production baseline would therefore be:

```text
Apple Mac mini M6
32 GB unified memory
512 GB internal
1 TB encrypted external APFS SSD

macOS 27 stable release
Dedicated non-admin account: agentlab

Qwen3.6-35B-A3B
GGUF Q4_K_M
20.4 GB

llama.cpp
16K context
Q8 KV
1 inference slot

Python 3.12
LangGraph
SQLite WAL
FastAPI

100+ logical agents
1 shared model lease
coordinator / worker / verifier design

mini-SWE-agent v2
Git worktrees
Colima VZ containers

SearXNG
HTTP retrieval
Playwright on demand
PaperQA2
SQLite evidence ledger

Markdown project memory
SQLite FTS
LanceDB + BGE-M3 later

launchd
watchdog
leases
checkpoint recovery

Tailscale
private control dashboard
key-only emergency SSH

credential broker
permission tiers
audit log
hard resource limits
```

This directly satisfies the RFC requirement for a system that plans, delegates, executes, observes, verifies, corrects, documents and continues with little operator involvement, while keeping actual inference concurrency within what 32 GB can sustain. 

The main uncertainty is not the architecture. It is the actual M6 performance of llama.cpp versus Apple's already-tested LM Studio path once retail machines arrive on 22 September 2026. Everything else can be designed now.

## Sources

Primary sources:

1. [Apple, M6 Mac mini announcement and benchmark disclosures](https://www.apple.com/nz/newsroom/2026/08/apple-unveils-a-more-powerful-mac-mini-featuring-the-all-new-m6-and-m5-pro/)
2. [Qwen, official Qwen3.6-35B-A3B model card](https://huggingface.co/Qwen/Qwen3.6-35B-A3B/blob/main/README.md)
3. [ggml-org, Qwen3.6 Q4_K_M GGUF, 20.4 GB](https://huggingface.co/ggml-org/Qwen3.6-35B-A3B-GGUF/blob/main/Qwen3.6-35B-A3B-Q4_K_M.gguf)
4. [ggml-org, Qwen3.6 GGUF quantization files](https://huggingface.co/ggml-org/Qwen3.6-35B-A3B-GGUF/tree/main)
5. [llama.cpp server documentation](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)
6. [mini-SWE-agent v2 repository](https://github.com/SWE-agent/mini-swe-agent)
7. [PaperQA2 repository and documentation](https://github.com/future-house/paper-qa)
8. [Tailscale macOS daemon documentation](https://github.com/tailscale/tailscale/wiki/Tailscaled-on-macOS)
9. [Tailscale Serve documentation](https://tailscale.com/docs/reference/tailscale-cli/serve)

Secondary operational evidence:

10. [llama.cpp M5/A19 Metal tensor issue, 21 August 2026](https://github.com/ggml-org/llama.cpp/issues/27473)

Because the M6 is pre-release as of the RFC evidence date, I would re-check local-inference support and independent benchmarks once retail hardware is available.

## Model's own cited sources

Numbered bracket citations `([Name][n])` + a Sources list with ~10 URLs, almost all primary:
apple.com/nz/newsroom M6 announcement; huggingface.co/Qwen/Qwen3.6-35B-A3B model-card README;
huggingface.co/ggml-org/Qwen3.6-35B-A3B-GGUF (the Q4_K_M .gguf file + the quant-files tree);
github.com/ggml-org/llama.cpp tools/server/README.md; github.com/ggml-org/llama.cpp issue #27473
(M5/A19 Metal tensor — flagged secondary by the model); github.com/SWE-agent/mini-swe-agent;
github.com/future-house/paper-qa; docs.langchain.com checkpointers page; docs.lancedb.com
quickstart; github.com/tailscale/tailscale wiki Tailscaled-on-macOS; tailscale.com serve docs;
github.com/langchain-ai/open_deep_research (cited to note it was archived 2026-08-21).

## Reviewer notes

### Purpose: RQ6 prompt-sensitivity — GPT-5 v1 vs v2

Compare to `data/responses/gpt-5.md` (v1). Tracker: `analysis/rq6-prompt-sensitivity.md`.

### Architecture shape — UNCHANGED

Same as v1: one resident MoE + hot-swap; 100+ logical agents as DB rows; coordinator → worker →
verifier, explicitly not a swarm; one shared model lease; SQLite WAL task queue + leases +
checkpoint recovery; dedicated non-admin macOS user; capability granted per-job not to the AI;
credential broker; evidence-first research with a verified-claims ledger; launchd + watchdog;
Tailscale-only, no public dashboard; internal SSD = state, external = models/corpus; cloud
optional and off by default.

### Load-bearing axes that MOVED (v1 → v2)

| axis | v1 | v2 | note |
|---|---|---|---|
| inference engine | **MLX-LM primary** (+ LM Studio + llama.cpp + Ollama) | **llama.cpp server primary** (+ LM Studio headless fallback); `mlx_lm server` explicitly on the exclusion list ("attractive Apple stack, but not my first choice for this unattended production role"); Ollama also excluded | full reversal on the #1 engine |
| orchestration substrate | **Pydantic AI** + custom async scheduler (dedicated argument against LangGraph-as-core) | **LangGraph** + thin custom supervisor; Pydantic AI not mentioned | opposite framework |
| coding executor | **OpenHands** (autonomous, Docker sandbox) + Qwen Code interactive console | **mini-SWE-agent v2** as the worker; OpenHands explicitly demoted ("strong product, but duplicates supervisor functions and adds weight"); Qwen Code not mentioned | different coding worker |
| primary model | Qwen3.6-35B-A3B Q4 MLX (~20.4 GB), rejects 80B Qwen3-Coder-Next | Qwen3.6-35B-A3B **Q4_K_M** (20.4 GB, same family), with SWE-bench 73.4 / Terminal-Bench 51.5 cited to the HF card | same model, now sourced |
| sandbox | dedicated workspace root + `capability://` URI broker + Docker for OpenHands | **Colima with Apple Virtualization Framework** (`vmType: vz`) + per-job container memory/cpu limits; Docker Desktop excluded | different isolation tech |
| memory (later) | sqlite-vec | **LanceDB + BGE-M3** (embedded, on-demand embedding model) | different vector store |

### Axes UNCHANGED

topology, agent-as-DB-row, one model lease, SQLite WAL queue, dedicated non-admin user,
credential broker, evidence ledger + verified-claims gate, launchd + watchdog + lease recovery,
Tailscale-only + no public dashboard, storage split, cloud-off-by-default, "do not run 262K
context", "one model, vary the prompt not the weights".

### Fabrication (RQ2) — none

Every tool resolves: llama.cpp, LM Studio, LangGraph, mini-SWE-agent (`SWE-agent/mini-swe-agent`),
Colima, PaperQA2 (`future-house/paper-qa`), SearXNG, Playwright, LanceDB, BGE-M3, Tailscale,
launchd. Every model resolves: Qwen3.6-35B-A3B (with correct GGUF sizes cited to `ggml-org`),
BGE-M3. Benchmark numbers (SWE-bench 73.4, Terminal-Bench 51.5, GGUF 20.4/36.9/69.4 GB) are
attributed to the HF model card and the ggml-org GGUF repo — falsifiable and sourced.
`open_deep_research` correctly noted as archived. M6 spec correct (170 GB/s, 25 Aug announce,
22 Sep ship). The llama.cpp M5/A19 Metal-tensor issue #27473 is a real, current caveat.

### Citations (RQ5) — big jump vs v1

v1 gpt-5 = "~20 specific inline attributions, **0 URLs**" (adjudicated D6 = 1). v2 = **~10
resolving primary URLs** in a numbered Sources list (Apple newsroom, HF Qwen card, ggml-org GGUF
repo, llama.cpp README, mini-swe-agent, paper-qa, Tailscale docs). This is a bucket-1 citation
apparatus. The RFC framing did not cause it (the header/Sources request is identical across
versions) — but the same model produced a far better apparatus on this run.

### RQ6 signal

GPT-5 is **highly framing-sensitive on product choice.** Same model, same task, same
responder-context header: v1 and v2 disagree on the primary inference engine (MLX-LM vs
llama.cpp), the orchestration framework (Pydantic AI vs LangGraph), the coding worker (OpenHands
vs mini-SWE-agent) and the sandbox (Apple container/`capability://` vs Colima-VZ). The
*architecture* (one resident MoE, coordinator/worker, SQLite state, per-job capability, evidence
ledger, Tailscale) is stable. Strong within-model support for the paper's "converge on shape,
diverge on products" — and a sharper datapoint than Perplexity's (whose product choices barely
moved). Zero fabrication in either framing; v2's citation quality is markedly better than v1's.
