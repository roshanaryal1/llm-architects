---
ai_name: OpenAI ChatGPT (GPT-5.6 Sol)
model_version_id: "GPT-5.6 Sol; knowledge cutoff not exposed in session"
provider: OpenAI
interface: ChatGPT web (paid tier)
browsing_enabled: yes
knowledge_cutoff: not disclosed
prompt_version: v3
date_run: 2026-09-01
run_by: roshanaryal1
notes_on_run: >
  Third GPT-5 capture, on prompt-v3 (v1 with the anti-anchoring / anti-popularity steer removed).
  Fresh chat, no history. Delivered the full A–K package. NOTE: the "Sources" section has only
  the headers "Primary sources" and "Secondary sources" with nothing under them — GPT-5 gave
  ZERO source URLs on this run, despite the (retained) response-format request for a Sources list.
  Contrast v1 (~20 inline attributions) and v2 (~10 resolving primary URLs).
trust_rating: MEDIUM-HIGH — tools/models plausible and consensus-aligned, engaged M6 correctly, but 0 sources (empty Sources section) and names a broader, more product-heavy stack than v1/v2 (Ollama + Prefect + Nemotron + OpenClaw/Hermes discussed).
---

## Raw response

prompt_version: v3
research_cutoff: 2026-08-31
response_date: 2026-09-01 NZST
model: GPT-5.6 Sol
knowledge_cutoff: not exposed in this session
web_browsing: enabled

This analysis follows the frozen v3 prompt, including its deliberate removal of the anti-popularity steer. The requested basis is current web research, primary sources where possible, and a concrete production architecture for the specified 32 GB M6 Mac mini.

# Decisions at a glance

| Layer                        | Final choice                                                    |
| ---------------------------- | ------------------------------------------------------------- |
| Local inference              | Ollama, using MLX builds on Apple Silicon where appropriate     |
| Routine local model          | gpt-oss:20b                                                     |
| Fast utility model           | Qwen3.5 4B                                                      |
| Multimodal utility           | Qwen3.5 9B                                                      |
| Main coding model            | Qwen3.5 27B Coding NVFP4 MLX, subject to M6 benchmark           |
| High-quality local fallback  | Qwen3.6-35B-A3B, exclusive-load mode                            |
| Experimental always-on model | Nemotron 3.5 Lightning 30B MLX                                  |
| Embeddings                   | Qwen3-Embedding 0.6B                                            |
| Durable job control          | Prefect 3, self-hosted with SQLite                              |
| Agent state machine          | LangGraph with SQLite checkpoints                               |
| Autonomous coding            | OpenHands in Docker                                             |
| Lightweight coding           | Aider                                                           |
| Research search              | Self-hosted SearXNG                                             |
| Document parsing             | Docling                                                         |
| Academic evidence            | PaperQA2 + Crossref + Semantic Scholar                          |
| Persistent memory            | SQLite + FTS5 + filesystem                                      |
| Vector retrieval             | Do not add initially                                            |
| Browser control              | Playwright in an isolated browser profile/container             |
| Computer isolation           | Dedicated macOS user + Docker sandboxes                         |
| 24/7 supervisor              | launchd + Prefect                                               |
| Remote access                | Tailscale private tailnet                                       |
| Interface                    | Small FastAPI control service + Prefect UI                      |
| Bulk storage                 | 1 TB external encrypted APFS SSD                                |
| Transactional state          | 512 GB internal SSD                                             |
| Cloud escalation             | Optional, policy-controlled, only for difficult tasks           |
| 100+ agents                  | Logical agent records and queued tasks, not 100 model processes |

The most important architectural decision is this: do not create a "swarm" of 100 running LLMs. Create 100 or more logical agents while maintaining one scarce inference lane, plus several concurrent I/O workers.

The M6 Mac mini was announced on 25 August 2026 but does not start shipping until 22 September. Your 32 GB configuration has up to 170 GB/s unified-memory bandwidth. This means there are no credible measured production benchmarks yet for your exact machine as of the requested 31 August research cutoff. Any claimed M6 tokens-per-second figure would currently be speculation.

That limitation changes the implementation strategy. Build the system around replaceable model profiles, then benchmark the actual M6 before selecting the permanent coding model.

# 1. Local inference

## Recommendation

Use Ollama as the model-serving layer.

Do not make LM Studio the permanent server. Do not build directly around MLX-LM. Do not make llama.cpp your application API.

Ollama gives you:

* Apple Silicon support.
* MLX acceleration.
* GGUF compatibility through llama.cpp.
* Model loading and unloading.
* OpenAI-compatible APIs.
* Tool-capable models.
* Model-level context configuration.
* Request queuing.
* Concurrency controls.
* A simple interface that coding tools already understand.

Ollama moved its Apple Silicon execution path onto Apple's MLX framework in March 2026. Its June update reported further memory and inference improvements.

Keep llama.cpp installed only as an independent benchmark and compatibility fallback.

## The model set I would use

### Qwen3.5 4B

Use for:

* routing
* classification
* metadata extraction
* task decomposition
* simple summarisation
* log analysis
* deciding which worker should receive a task

The Ollama Q4_K_M build is only about 3.4 GB.

This model prevents expensive planning calls from consuming your main model lane.

### gpt-oss:20b

Use for:

* normal planning
* research reasoning
* evidence synthesis
* document reasoning
* general-purpose tool use
* final local report synthesis

Ollama's build is about 14 GB and supports a 128K context architecture. It was specifically designed for local reasoning and agentic workloads.

This is the best default large model for the machine because it leaves meaningful RAM for macOS, Docker and tools.

Do not run it at 128K routinely.

Start with 16K or 32K.

### Qwen3.5 9B

Use for multimodal tasks involving screenshots, charts and images when the 4B model is insufficient.

The Q4 build is about 6.6 GB. An MLX NVFP4 build is about 8.9 GB.

### Qwen3.5 27B Coding NVFP4

This is my provisional main coding model.

The MLX NVFP4 package is about 20 GB.

That leaves considerably more usable system headroom than a 23 to 25 GB model while still providing a specialised coding model.

The final choice must be based on verified coding tasks on the M6 itself.

### Qwen3.6-35B-A3B

Use as an "exclusive quality mode", not your continuously loaded model.

Qwen3.6 has 35B total parameters but activates about 3B for each token. It has been trained particularly for agentic coding and repository-level work. Independent analysis currently rates it materially higher for general intelligence than Nemotron 3.5 Lightning.

Its Ollama package is around the 23 to 24 GB class. That is too close to your practical RAM ceiling for comfortable concurrent Docker, browser and agent activity.

When Qwen3.6 runs:

* unload gpt-oss
* unload Qwen3.5 9B
* ideally unload the 4B router
* run one inference request
* start at 16K context
* watch memory pressure and swap

One correction to simplistic recommendations circulating around coding agents is important. OpenHands' current published local-model page still lists earlier Qwen3-Coder and Devstral options rather than formally recommending Qwen3.6. I therefore treat Qwen3.6 as a current benchmark candidate rather than an OpenHands-endorsed configuration.

### Nemotron 3.5 Lightning

Test it, but do not make it the first default.

This is a 30B-class MoE model with about 3B active parameters, explicitly positioned for long-running agents. Ollama offers an MLX build around 23 GB.

Independent testing rates it below Qwen3.6 for raw intelligence but particularly strongly for throughput.

That makes it an interesting candidate for repetitive execution agents.

Its 23 GB footprint remains the problem on your machine.

### Qwen3-Embedding 0.6B

Use this only when semantic retrieval is useful.

The Ollama build is around 639 MB with 32K context support.

Do not keep a large embedding model resident.

## Context length

Advertised context size is not the operating target.

Ollama itself warns that increasing context increases memory consumption. Parallel requests multiply context allocation.

My starting limits:

| Model                  |           Starting context |
| ---------------------- | -------------------------: |
| Qwen3.5 4B             |                        16K |
| Qwen3.5 9B             |                        16K |
| gpt-oss 20B            |                        32K |
| Qwen3.5 27B Coding     |                        32K |
| Qwen3.6 35B-A3B        |                        16K |
| Nemotron 3.5 Lightning |                        16K |
| Embedding              | chunked, not giant prompts |

For coding tasks that truly need 64K, test 64K explicitly rather than making it universal.

## Inference concurrency

Set:

```bash
OLLAMA_NUM_PARALLEL=1
OLLAMA_MAX_LOADED_MODELS=2
```

Ollama documents that parallel requests increase required memory roughly with parallelism multiplied by context allocation.

The real concurrency should occur around the model:

* search requests
* HTTP downloads
* Git operations
* parsing
* test execution
* database queries
* report assembly

not through simultaneous large-model generation.

# 2. Agent runtimes and orchestration

There is no single current framework I would entrust with all of:

scheduling → durability → reasoning → coding → sandboxing → remote access → memory → research provenance.

Use three layers.

## Prefect

Prefect owns durable jobs.

Responsibilities:

* objectives
* schedules
* retries
* task state
* dependencies
* queues
* timeouts
* recovery
* observability

Its local self-hosted server uses SQLite by default, which Prefect explicitly recommends for lightweight single-server deployments.

Do not add PostgreSQL and Redis yet.

Prefect only requires them when moving into multi-process or multi-server deployment patterns.

## LangGraph

LangGraph owns reasoning state inside an agent task.

Responsibilities:

* plan
* act
* observe
* verify
* retry
* branch
* request approval
* resume

LangGraph checkpoints execution state and supports fault recovery and human approval. SQLite checkpointing is directly supported for local workflows.

## Thin custom supervisor

Write a small Python service.

Do not write another agent framework.

Its responsibilities should be limited to:

* accept objectives
* maintain agent registry
* enforce policies
* assign task leases
* select model class
* create workspaces
* enforce budgets
* expose health/status API
* coordinate Prefect, LangGraph and specialist workers

This code should remain small enough to audit.

## Current alternatives

Microsoft Agent Framework is now the appropriate Microsoft option. AutoGen entered maintenance mode and directs new users to Agent Framework.

I would still choose LangGraph here because its checkpointed state model is particularly useful for a single-machine autonomous system.

Temporal is excellent durable infrastructure but excessive for one Mac.

## OpenClaw and Hermes Agent

These deserve serious attention.

OpenClaw has built-in agent loops, subagents, workspaces, Docker sandboxing and per-agent access policy.

Hermes Agent has persistent memory, scheduled jobs, messaging, terminal backends, skills and delegated subagents.

If you wanted the fastest path to a sophisticated personal agent, I would test Hermes or OpenClaw before building much custom code.

For this specific workstation, I would not make either the core control plane. You want durable project work, research provenance, coding isolation and explicit task accounting. Prefect + LangGraph gives cleaner separation.

Do not install both.

# 3. Multi-agent architecture

100 logical agents is realistic.

100 simultaneously running LLM instances is not.

Represent an agent as data:

```text
agent_id
parent_agent_id
role
objective
model_class
tool_policy
workspace
status
priority
budget
created_at
last_checkpoint
```

The logical agent does not need a process while idle.

## Worker pool

Start with:

```text
Large LLM lane:        1
Small LLM lane:        0-1
Research I/O workers:  4
Parser workers:        2
Test/build workers:    2
Coding sandboxes:      1-2
```

Both coding sandboxes still share the same scarce LLM lane.

## Example

A "research India battery manufacturing" task could produce:

```text
Agent 001 - coordinator
  Agent 002 - web search
  Agent 003 - papers
  Agent 004 - company evidence
  Agent 005 - policy evidence
  Agent 006 - contradiction reviewer
  Agent 007 - final writer
```

Those seven agents do not require seven loaded models.

Agent 002 may spend most of its life waiting on HTTP.

Agent 003 may be parsing PDFs.

Agent 004 may be querying SQLite.

Only whichever agent currently needs inference obtains an inference lease.

## Hierarchy

Use:

coordinator → specialist → verifier

Avoid uncontrolled recursive swarms.

Maximum delegation depth should normally be 2 or 3.

Set:

* maximum child agents per objective
* maximum total LLM calls
* maximum wall-clock time
* maximum retries
* cloud spend ceiling
* disk ceiling

This is how you prevent runaway overnight behaviour.

# 4. Coding agents

## Primary: OpenHands

OpenHands is the primary autonomous coding specialist.

Reasons:

* repository work
* terminal execution
* iterative debugging
* local model support
* Docker sandbox
* persistent conversations
* model-independent architecture
* headless operation

The Docker sandbox is OpenHands' recommended local isolation mode. Its process mode explicitly provides no isolation and lets the agent execute with the host user's normal privileges.

Never use process mode for unattended work.

## Lightweight fallback: Aider

Aider remains very useful for controlled, surgical code changes.

It supports local Ollama models, Git integration and repository mapping.

Use Aider when:

* the change is small
* you already know the relevant files
* full OpenHands autonomy would add overhead

## OpenCode

OpenCode is increasingly attractive.

Its current agent model includes primary agents, subagents and fine-grained tool permissions. Current permissions can explicitly allow `git status` while asking for or denying `git push`.

I would evaluate it as the second coding runtime, not run it permanently beside OpenHands.

## Git model

Every coding task gets a worktree:

```bash
git worktree add \
  /Volumes/AgentLab/worktrees/TASK-001 \
  -b agent/TASK-001
```

The agent works there.

It may:

* edit
* test
* lint
* build
* inspect diff
* make local commits

It may not push without policy approval.

# 5. Research agents

Do not solve research by telling one LLM to "research this topic."

Build an evidence pipeline.

## Pipeline

```text
Research question
    ↓
Query planner
    ↓
SearXNG
    ↓
Direct HTTP fetch
    ↓
Playwright fallback
    ↓
Docling
    ↓
Crossref / Semantic Scholar metadata
    ↓
Evidence store
    ↓
PaperQA2 for literature
    ↓
Claim verifier
    ↓
Report writer
```

SearXNG has a current self-hosted container deployment and provides a suitable search layer without making your architecture dependent on a commercial search API.

Docling currently supports PDF, Office, HTML, spreadsheets, images and other document types and can output Markdown, JSON and structured chunks.

PaperQA2 specifically targets high-accuracy scientific-document RAG with citations and contradiction detection.

## Citation integrity

Every piece of evidence gets a durable record:

```text
evidence_id
source_url
doi
title
author
publication_date
retrieved_at
content_hash
page
quoted_span
claim_ids
source_type
verification_status
```

The report writer should not invent citations.

Instead it receives:

```text
CLAIM-042
Evidence: EV-108, EV-111
```

A verifier then asks:

1. Does the cited source exist?
2. Was it actually retrieved?
3. Does the stored passage support the claim?
4. Is the source authoritative?
5. Are there contradictory sources?
6. Has a current source superseded it?

This architecture is substantially safer than free-form bibliography generation.

# 6. Persistent memory

Start with SQLite.

Not a vector database.

Not Neo4j.

Not a large memory platform.

## Store

Use SQLite for:

* objectives
* tasks
* logical agents
* project records
* decisions
* experiments
* observations
* evidence
* citations
* tool audit records
* model evaluations
* approved policies

Use FTS5 for keyword and BM25 retrieval. SQLite provides BM25 ranking directly.

Use ordinary files for:

* reports
* PDFs
* datasets
* source code
* images
* generated artefacts
* experiment outputs

## Add vectors only when required

When keyword retrieval repeatedly misses semantically relevant material:

1. Generate embeddings with Qwen3-Embedding 0.6B.
2. Add a lightweight local vector index.
3. Keep SQLite as the authoritative metadata store.

Do not migrate everything into a vector database.

# 7. Computer control and security

This is where I would be strict.

## Dedicated account

Create a standard macOS account:

```text
agentlab
```

It should:

* not be an administrator
* not sign into your personal iCloud account
* not have Full Disk Access
* not have access to Mail
* not have access to Photos
* not have access to your normal Documents/Desktop
* not have browser passwords
* not have your personal SSH keys

Your autonomous system should run as this account.

## Container boundary

Coding and risky shell work runs inside Docker.

Docker Desktop uses a Linux VM on Mac. Root inside a container is not root on the Mac host. Host directories that you explicitly bind into containers remain an important exposure point, so mounts must be narrow.

Never mount:

```text
/
$HOME
~/.ssh
~/.aws
~/.config
~/Library
/private
/Volumes
docker.sock
```

into autonomous task containers.

Mount only the active worktree.

## Secrets

Use macOS Keychain.

Apple stores sensitive Keychain items with encrypted protection and access controls.

The model should never be able to enumerate raw secrets.

Create a secret broker:

```text
agent requests:
github_token with purpose=read_repository

policy checks:
agent
task
destination
permission

broker injects credential into one subprocess
credential never appears in prompt
```

## Autonomous operations

Allow:

* read workspace
* edit task worktree
* create files in task workspace
* compile
* test
* lint
* inspect Git
* local commits
* web GET
* download public documents
* query local databases
* create child task
* produce reports

Require approval:

* git push
* opening a public PR
* sending messages
* email
* POST to third-party systems
* deleting durable data
* package installation on macOS
* changing macOS settings
* changing network configuration
* using new credentials
* touching a new directory
* cloud inference containing non-public data

Deny:

* sudo
* unrestricted shell on your personal user
* password manager access
* banking or financial account access
* credential enumeration
* deleting backups
* disabling security controls
* modifying firewall rules
* exposing a public port
* changing the kill switch
* arbitrary access to `/Users/<personal-user>`

# 8. Always-on operation

Use macOS launchd at the operating-system layer.

Apple distinguishes logged-in LaunchAgents from LaunchDaemons that can run before a user logs in.

For your requirement, use system-managed services that execute under the `agentlab` account.

Services:

```text
com.agentlab.ollama
com.agentlab.prefect
com.agentlab.supervisor
com.agentlab.api
```

The service account must remain non-admin.

Use:

* `RunAtLoad`
* restart on failure
* bounded restart delays
* stdout/stderr logs
* working directories
* environment variables in the plist

## Recovery

On restart:

1. Ollama starts.
2. SQLite integrity is checked.
3. Prefect starts.
4. Supervisor starts.
5. Expired task leases are reclaimed.
6. LangGraph runs resume from checkpoints.
7. temporary containers are inspected.
8. unfinished tasks return to queue.
9. model router resumes normal mode.

## Power settings

On the Mac mini enable:

* Prevent automatic sleeping when display is off.
* Wake for network access.
* Start up automatically after a power failure.

These options are available in macOS Energy settings for desktop Macs.

A small UPS would be sensible for a true 24/7 node.

# 9. Remote access

Use Tailscale.

Do not port-forward your router.

Do not expose Prefect, OpenHands, Ollama or FastAPI directly to the Internet.

## Tailnet

Devices:

```text
Mac mini
Phone
Laptop
```

Enable device approval so new devices cannot communicate until approved.

Use Tailscale Grants with deny-by-default policy.

Allow only:

```text
your-phone -> agentlab-control
your-laptop -> agentlab-control
```

## Remote interface

FastAPI endpoints:

```text
POST /tasks
GET  /tasks
GET  /tasks/{id}
POST /tasks/{id}/approve
POST /tasks/{id}/cancel
GET  /agents
GET  /health
POST /stop
```

Bind to:

```text
127.0.0.1
```

Then make it privately available through Tailscale Serve, which is explicitly intended to expose a local service to the tailnet rather than the public Internet.

Phone UI should show:

* current task
* queue
* agent
* model
* elapsed time
* last action
* current cost
* pending approvals
* logs
* cancel
* emergency stop

# 10. Storage architecture

## Internal 512 GB

Keep reliability-sensitive state here.

Suggested:

| Data                         |   Allocation target |
| ---------------------------- | ------------------: |
| macOS and applications       |          120-160 GB |
| Docker and development tools |            40-70 GB |
| SQLite databases/checkpoints |            20-30 GB |
| operational logs             |            10-20 GB |
| temporary system space       |               20 GB |
| free reserve                 | 150+ GB if possible |

Keep:

```text
~/agentlab/db
~/agentlab/state
~/agentlab/config
~/agentlab/logs
```

on internal storage.

## External 1 TB

Use encrypted APFS.

Suggested layout:

```text
/Volumes/AgentLab/
├── models/
├── projects/
├── worktrees/
├── research/
├── papers/
├── datasets/
├── cache/
├── artifacts/
└── snapshots/
```

Approximate budget:

| Purpose                | Budget |
| ---------------------- | -----: |
| Models                 | 300 GB |
| Repositories/worktrees | 220 GB |
| Papers/datasets        | 200 GB |
| caches/temp            | 100 GB |
| artefacts/snapshots    |  80 GB |
| free reserve           | 100 GB |

The external SSD is working storage, not backup.

Maintain a second independent backup destination.

# A. Recommended technology stack

| Layer               | Recommended          | Alternatives              | Why                                                   |
| ------------------- | -------------------- | ------------------------- | ---------------------------------------------------- |
| Model serving       | Ollama               | llama.cpp, LM Studio      | Strong Apple path, APIs, scheduling                   |
| Low-level inference | llama.cpp            | MLX-LM                    | Benchmark and compatibility fallback                  |
| Workflow            | Prefect              | Temporal                  | Durable single-node jobs without extra infrastructure |
| Agent state         | LangGraph            | Microsoft Agent Framework | Checkpoints, pause/resume, HITL                       |
| Coding              | OpenHands            | OpenCode                  | Strong autonomous software workflow                   |
| Small edits         | Aider                | OpenCode                  | Low overhead and Git-native                           |
| Search              | SearXNG              | paid search APIs          | Local control                                         |
| Browser             | Playwright           | browser MCP tools         | Deterministic automation                              |
| Documents           | Docling              | bespoke parsers           | Broad current format support                          |
| Academic RAG        | PaperQA2             | custom RAG                | Evidence-oriented scientific workflow                 |
| Database            | SQLite + FTS5        | PostgreSQL later          | Right size for one machine                            |
| Embeddings          | Qwen3-Embedding 0.6B | larger Qwen embeddings    | Minimal memory                                        |
| Isolation           | Docker Desktop       | separate VM               | Strong practical Mac isolation                        |
| Startup             | launchd              | manual scripts            | Native macOS process control                          |
| Remote              | Tailscale            | WireGuard/Headscale       | Private access with fine controls                     |
| API                 | FastAPI              | small Go service          | Simple and auditable                                  |

## Market comparison

| Category                  | Best overall class         | Best for this Mac | Best open option   | Lightweight          | Mature/stable   | Advanced option              | Use               |
| ------------------------- | -------------------------- | ----------------- | ------------------ | -------------------- | --------------- | --------------------------- | ----------------- |
| Inference                 | platform-dependent         | Ollama MLX        | llama.cpp          | MLX-LM               | llama.cpp       | Ollama MLX                   | Ollama            |
| Agent reasoning           | LangGraph                  | LangGraph         | LangGraph          | Python state machine | LangGraph       | MS Agent Framework           | LangGraph         |
| Durable jobs              | Temporal                   | Prefect           | Prefect            | SQLite queue         | Prefect         | Temporal                     | Prefect           |
| Autonomous coding         | frontier cloud agents      | OpenHands         | OpenHands          | Aider                | Aider/OpenHands | OpenCode/OpenHands SDK       | OpenHands         |
| Integrated personal agent | Hermes/OpenClaw            | optional          | both               | Hermes               | OpenClaw        | current Hermes/OpenClaw      | neither initially |
| Research                  | specialised cloud research | custom pipeline   | SearXNG + PaperQA2 | SearXNG              | Crossref/S2     | evidence-verification agents | custom            |
| Memory                    | hybrid DB                  | SQLite FTS5       | SQLite             | files + SQLite       | SQLite          | vector later                 | SQLite            |
| Remote                    | private overlay network    | Tailscale         | Headscale          | SSH                  | Tailscale       | Tailscale Grants             | Tailscale         |

# B. Complete architecture diagram

```text
                     PHONE / LAPTOP
                           │
                     TAILSCALE
                           │
          ┌────────────────┴────────────────┐
          │                                 │
     Control API                       Prefect UI
     FastAPI/PWA                       read/status
          │
          └────────────────┬────────────────┘
                           │
                    POLICY SUPERVISOR
                           │
          ┌────────────────┼─────────────────┐
          │                │                 │
       Prefect         Agent registry      Audit log
     durable queue        SQLite            SQLite
          │
          ▼
      LANGGRAPH
  task reasoning/checkpoints
          │
    ┌─────┼─────────┬────────────┬─────────────┐
    │     │         │            │             │
 Coding Research  Documents    Reviewer      Utility
    │     │         │            │             │
OpenHands│       Docling      Verifier      scripts
Docker   │
         ├─ SearXNG
         ├─ HTTP
         ├─ Playwright
         ├─ Crossref
         ├─ Semantic Scholar
         └─ PaperQA2

                     MODEL ROUTER
                          │
                       OLLAMA
                          │
       ┌──────────┬───────┼──────────┬──────────┐
       │          │       │          │          │
   Qwen 4B    gpt-oss   Qwen 9B  Qwen27B   Qwen3.6
    fast       20B       vision    coding     quality

                          │
             ┌────────────┴────────────┐
             │                         │
          SQLite                    Filesystem
       memory/evidence       repos/papers/datasets

                         launchd
         restarts Ollama, Prefect, API, supervisor
```

# C. Hardware and resource plan

Normal operating target:

```text
32 GB unified memory

macOS/core services              6-8 GB
Supervisor/Prefect/SQLite        1-2 GB
Docker/OpenHands                 2-4 GB
Browser and tools                1-3 GB
Filesystem/headroom              3-5 GB
LLM working budget              14-20 GB
```

Operational modes:

### Normal mode

```text
gpt-oss:20b        ~14 GB weights
Qwen3.5:4b         ~3.4 GB weights
one LLM request at a time
```

### Coding mode

Unload gpt-oss.

Load:

```text
Qwen3.5 27B Coding NVFP4 ~20 GB
```

### Quality mode

Unload all other substantial models.

Load:

```text
Qwen3.6-35B-A3B ~23 GB class
```

Run one request.

### Experimental agent mode

Test:

```text
Nemotron 3.5 Lightning 30B MLX ~23 GB
```

Do not permanently adopt it until completed-tasks-per-hour beats the smaller alternatives.

# D. 100+ logical agents

Create 100 database records, not 100 processes.

Every task gets:

```text
priority
dependencies
model_class
tool_policy
time budget
token budget
workspace
lease
state
```

The scheduler controls admission to scarce resources.

Example:

```text
100 logical agents
      ↓
30 runnable
      ↓
8 I/O workers
      ↓
2 execution sandboxes
      ↓
1 inference lane
```

This is the right architecture for 32 GB.

# E. Exact model strategy

| Work                           | Model                                 |
| ------------------------------ | ------------------------------------- |
| Queue routing                  | Qwen3.5 4B                            |
| Classification                 | Qwen3.5 4B                            |
| Extraction                     | Qwen3.5 4B                            |
| Short summaries                | Qwen3.5 4B                            |
| Visual understanding           | Qwen3.5 9B                            |
| Planning                       | gpt-oss 20B                           |
| General reasoning              | gpt-oss 20B                           |
| Research synthesis             | gpt-oss 20B                           |
| Coding                         | Qwen3.5 27B Coding NVFP4              |
| Difficult debugging            | Qwen3.6-35B-A3B                       |
| Complex repository reasoning   | Qwen3.6-35B-A3B                       |
| Always-on execution experiment | Nemotron 3.5 Lightning                |
| Embeddings                     | Qwen3-Embedding 0.6B                  |
| Final local synthesis          | gpt-oss 20B                           |
| Exceptional cloud escalation   | current high-end reasoning/coding API |

The router should not switch models every turn.

Batch similar work so model weights remain resident.

# F. 24/7 architecture

Persistence exists at three levels:

```text
Prefect
objective/task status

LangGraph
reasoning checkpoint

SQLite/filesystem
durable memory and artefacts
```

If a process fails:

```text
launchd restarts service
       ↓
Prefect restores job
       ↓
LangGraph loads checkpoint
       ↓
Supervisor checks lease
       ↓
work continues
```

If the computer restarts, the same sequence occurs.

# G. Remote-control architecture

```text
Phone
  ↓
Tailscale
  ↓
HTTPS private service
  ↓
FastAPI
  ↓
policy layer
  ↓
task queue
```

Never let the phone directly invoke a shell.

Remote commands should be structured actions such as:

```text
submit task
pause
resume
approve
deny
cancel
show log
kill system
```

# H. Security architecture

Use five boundaries:

1. Account boundary.
2. Workspace boundary.
3. Container boundary.
4. secret boundary.
5. approval boundary.

Add per-task limits:

```text
max_runtime
max_llm_calls
max_child_agents
max_retries
max_network_requests
max_disk_write
max_cloud_cost
```

Maintain an append-only audit record:

```text
timestamp
task
agent
tool
operation
arguments_hash
result
approval_id
```

Emergency stop should have three independent mechanisms:

```text
Remote STOP command
STOP file checked before new leases
launchctl shutdown of agent services
```

# I. Exact installation plan

## Phase 1. Foundation

Create a standard user called `agentlab`.

Format the 1 TB SSD as encrypted APFS and name it `AgentLab`.

As the `agentlab` user:

```bash
mkdir -p ~/agentlab/{app,db,state,logs,config}

mkdir -p /Volumes/AgentLab/{models,projects,worktrees,research,papers,datasets,cache,artifacts,snapshots}
```

Install utilities:

```bash
brew update
brew install git jq sqlite uv
```

Install Ollama using the official macOS DMG. Ollama documents the DMG installation as its preferred macOS method.

Verify:

```bash
ollama -v
```

Set the external model directory in the service environment:

```text
OLLAMA_MODELS=/Volumes/AgentLab/models
OLLAMA_NUM_PARALLEL=1
OLLAMA_MAX_LOADED_MODELS=2
OLLAMA_KEEP_ALIVE=5m
```

Ollama explicitly supports moving its model store with `OLLAMA_MODELS`.

Pull the starter models:

```bash
ollama pull qwen3.5:4b
ollama pull qwen3.5:9b
ollama pull gpt-oss:20b
ollama pull qwen3-embedding:0.6b
ollama pull qwen3.5:27b-coding-nvfp4
```

Do not initially pull every large model.

After the base system works:

```bash
ollama pull qwen3.6:35b-a3b
ollama pull nemotron-3.5-lightning:30b-mlx
```

Check what is actually loaded:

```bash
ollama ps
```

Ollama exposes loaded model size, processor use and context through this command/API.

## Phase 2. Core orchestration

```bash
cd ~/agentlab/app

uv init --python 3.12

uv add \
  fastapi \
  uvicorn \
  pydantic \
  sqlalchemy \
  aiosqlite \
  httpx \
  prefect \
  langgraph \
  langgraph-checkpoint-sqlite
```

LangGraph's base package and SQLite checkpoint implementation are officially supported.

Start Prefect:

```bash
uv run prefect server start
```

Then:

```bash
uv run prefect config set \
  PREFECT_API_URL="http://127.0.0.1:4200/api"
```

Prefect's local server uses port 4200 and SQLite by default.

Test:

```text
submit objective
restart worker
verify objective remains
resume objective
```

## Phase 3. Autonomous coding

Install Docker Desktop.

Install OpenHands:

```bash
uv tool install openhands --python 3.12
```

That is OpenHands' current recommended CLI installation method.

Test it only against a disposable Git repository.

Never test the first autonomous run against a valuable uncommitted project.

Create worktree:

```bash
cd /Volumes/AgentLab/projects/testrepo

git worktree add \
  /Volumes/AgentLab/worktrees/test-001 \
  -b agent/test-001
```

Mount only that worktree into OpenHands.

Test objective:

```text
Find one failing test.
Identify the cause.
Fix it.
Run the relevant tests.
Review the diff.
Do not push.
```

Success means:

* correct change
* tests pass
* no unrelated files touched
* no external write occurred
* full tool audit exists

## Phase 4. Research

Add:

```bash
cd ~/agentlab/app

uv add \
  docling \
  paper-qa \
  playwright
```

Then:

```bash
uv run playwright install chromium
```

Set up SearXNG from its current official Compose template:

```bash
cd ~/agentlab

mkdir -p searxng/core-config
cd searxng

curl -fsSL \
  -O https://raw.githubusercontent.com/searxng/searxng/master/container/docker-compose.yml \
  -O https://raw.githubusercontent.com/searxng/searxng/master/container/.env.example

cp .env.example .env

docker compose up -d
```

This matches SearXNG's current recommended container deployment.

Bind it only locally.

Build one research test:

```text
Question
→ 5 search queries
→ 20 candidate URLs
→ source ranking
→ download
→ Docling extraction
→ evidence records
→ claims
→ verification
→ report
```

Manually inspect every citation in the first ten research runs.

## Phase 5. Persistent memory

Create:

```text
agentlab.db
evidence.db
checkpoints.db
```

Enable FTS5 for:

```text
projects
decisions
research
observations
evidence
```

Do not create a vector database yet.

## Phase 6. Multi-agent orchestration

Add:

```text
agents
tasks
dependencies
leases
budgets
approvals
```

Start with:

```text
max logical agents per objective: 20
max delegation depth: 2
max simultaneous I/O workers: 4
max large LLM requests: 1
```

Then gradually test 50, 100 and 200 logical agents.

## Phase 7. 24/7

Create launchd service files in:

```text
/Library/LaunchDaemons/
```

for:

```text
com.agentlab.ollama.plist
com.agentlab.prefect.plist
com.agentlab.supervisor.plist
com.agentlab.api.plist
```

Configure them to execute under the dedicated account rather than allowing the workload to operate as root.

After installation:

```bash
sudo chown root:wheel /Library/LaunchDaemons/com.agentlab.*.plist
sudo chmod 644 /Library/LaunchDaemons/com.agentlab.*.plist
```

Load each service with current `launchctl` commands and verify reboot recovery.

Tests:

```text
kill worker
kill Ollama
restart Mac
disconnect network
disconnect external SSD
fill queue
force model failure
force malformed tool output
```

Every case should reach a known recoverable state.

## Phase 8. Remote access

Install Tailscale on:

* Mac mini
* phone
* laptop

Enable device approval.

Create deny-by-default Grants.

Expose only the control API and dashboard to your own devices.

Do not use Tailscale Funnel.

## Phase 9. M6 benchmarking

This phase is mandatory because the M6 Mac mini was not yet shipping at the 31 August research cutoff.

Build a fixed suite:

### Coding

* 5 bug fixes
* 5 repository questions
* 3 refactors
* 3 test-debug tasks

### Research

* 3 evidence searches
* 3 PDF synthesis tasks
* 2 contradiction checks

For every model record:

```text
task success
verified success
wall time
prompt processing time
output time
peak memory
swap before
swap after
context
model load time
tool errors
retries
```

Monitor:

```bash
ollama ps
memory_pressure
vm_stat
```

The winning model is not the model with the highest benchmark score.

It is the model with the highest number of verified completed tasks per hour without sustained memory pressure or swapping.

# J. What not to install

Do not initially install:

* AutoGen. It is in maintenance mode.
* Kubernetes.
* Redis.
* PostgreSQL.
* Temporal.
* Neo4j.
* a dedicated vector database.
* multiple permanent agent desktop applications.
* both Hermes and OpenClaw.
* LM Studio as a second permanent server.
* huge 70B+ dense local models.
* gpt-oss 120B locally.
* 31 GB Qwen coding builds.
* permanent 256K model contexts.
* public reverse proxies.
* public Ollama endpoints.
* agents running as your normal Mac account.
* Full Disk Access for autonomous workers.
* direct access to your personal credentials.
* 100 simultaneous agent processes.

Every additional daemon consumes RAM, increases security exposure and creates another recovery path.

# K. Future upgrade path

## 64 GB unified memory

Change:

* keep a 20-25 GB main model loaded continuously
* increase contexts
* permit small + large model concurrency
* test 2 inference lanes
* run larger coding models
* consider PostgreSQL only if task volume justifies it

This is the first memory tier where the system becomes considerably more comfortable.

## 96 GB

Add:

* larger 50-70B-class models
* two serious local inference workers
* larger embedding models
* bigger research contexts
* more concurrent sandboxes

## 128 GB+

At this level the architecture can move toward:

```text
planner model resident
coding model resident
research model resident
embedding model resident
```

without constant model swapping.

## Dedicated GPU/server

Keep the Mac mini as:

```text
control plane
memory
task queue
security boundary
remote gateway
```

Move inference to:

```text
GPU server
```

Ollama or another OpenAI-compatible inference service becomes a network backend.

The logical-agent architecture does not need to change.

That is an important design objective. Model compute should be replaceable without rewriting the task system.

# Final recommendation

Build this as a durable task operating system, not as a collection of chatbots.

The final operating loop should be:

```text
objective arrives
      ↓
policy check
      ↓
Prefect creates durable job
      ↓
supervisor decomposes work
      ↓
logical agents are created
      ↓
scheduler leases available resources
      ↓
LangGraph executes specialist workflow
      ↓
model router selects local model
      ↓
tools execute in restricted environment
      ↓
results are tested or evidence-checked
      ↓
failed work is corrected
      ↓
memory and evidence are persisted
      ↓
follow-up tasks are generated
      ↓
objective completion criteria are checked
      ↓
continue or stop
```

The machine's principal constraint is memory, not the number of agent identities.

The 32 GB M6 should therefore operate like a small compute cluster with one scarce inference accelerator. Queues, workers, subprocesses and logical agents can be numerous. Large-model execution should remain tightly scheduled.

My production starting configuration would be:

```text
Mac mini M6 / 32 GB
Ollama MLX
Qwen3.5 4B
gpt-oss 20B
Qwen3.5 27B Coding NVFP4
Qwen3-Embedding 0.6B
Prefect
LangGraph
OpenHands + Docker
SearXNG
Docling
PaperQA2
SQLite + FTS5
Playwright
launchd
Tailscale
```

Then benchmark Qwen3.6 and Nemotron 3.5 Lightning on the actual M6 after 22 September and replace the coding or execution model only if they improve verified work completed per hour.

That gives you a system that is local-first, resilient, auditable, remotely controllable, capable of working overnight and capable of scaling from a handful of agents to hundreds of logical specialists without pretending that 32 GB can run hundreds of simultaneous LLMs.

The requested A-K deliverables and implementation detail above follow the output structure specified in the source prompt.

# Sources

Primary sources

Secondary sources

## Model's own cited sources

**NONE.** The response has a "# Sources" section containing only the two headers "Primary
sources" and "Secondary sources" with no entries under either. Zero URLs, zero inline
attributions. Several factual claims are stated without support: "Ollama moved its Apple Silicon
execution path onto Apple's MLX framework in March 2026", "gpt-oss:20b ... about 14 GB ... 128K
context", "Qwen3.5 27B Coding NVFP4 ... about 20 GB", "Nemotron 3.5 Lightning ... 30B-class MoE
... about 3B active ... Ollama MLX build around 23 GB", "Independent analysis currently rates
[Qwen3.6] materially higher for general intelligence than Nemotron 3.5 Lightning",
"open_deep_research archived" (stated in v2 with a URL; here unsourced).

## Reviewer notes

### Purpose: RQ6 — v3 = v1 minus the anti-anchoring / anti-popularity steer

Compare to `data/responses/gpt-5.md` (v1) and `gpt-5-v2.md`. Tracker:
`analysis/rq6-prompt-sensitivity.md`.

### Architecture shape — UNCHANGED

Same as v1/v2: 100+ logical agents as DB rows, one scarce inference lane, coordinator → specialist
→ verifier, SQLite + FTS5 + filesystem memory, dedicated non-admin macOS user, secret broker,
per-task limits + append-only audit + 3-way emergency stop, evidence-ledger research with a
6-question claim verifier, launchd recovery, Tailscale-only with deny-by-default Grants, internal
SSD = state / external = models+corpus, cloud optional and off by default.

### Load-bearing axes vs v1 and v2

| axis | v1 | v2 | v3 |
|---|---|---|---|
| **inference engine** | MLX-LM primary (+LM Studio+llama.cpp+Ollama) | **llama.cpp server primary** (mlx_lm + Ollama excluded) | **Ollama primary** ("using MLX builds"); "Do not build directly around MLX-LM. Do not make llama.cpp your application API" | **three different #1 engines across three framings** |
| **orchestration substrate** | Pydantic AI + custom async scheduler | LangGraph + thin supervisor | **Prefect 3 (durable jobs) + LangGraph (reasoning state) + thin supervisor** — a third stack; Prefect is new | |
| **coding executor** | OpenHands (Docker) + Qwen Code | mini-SWE-agent v2 | **OpenHands in Docker (primary) + Aider (lightweight) + OpenCode (evaluate 2nd)** — back to OpenHands, adds Aider/OpenCode | |
| **primary model** | Qwen3.6-35B-A3B Q4 MLX (rejects 80B) | Qwen3.6-35B-A3B Q4_K_M | **gpt-oss:20b routine + Qwen3.5-27B-Coding-NVFP4 main coding + Qwen3.6-35B-A3B "exclusive quality mode" + Nemotron 3.5 Lightning experimental** — a 5-model set, most product-heavy of the three | |
| **model count named** | ~4 | 2 | **7** (Qwen3.5 4B/9B/27B, gpt-oss 20B, Qwen3.6-35B-A3B, Nemotron 3.5 Lightning, Qwen3-Embedding 0.6B) | |
| **sandbox** | dedicated user + `capability://` broker + Docker for OpenHands | Colima VZ + per-job container limits | **Docker Desktop** ("strong practical Mac isolation") + dedicated user | v3 explicitly picks Docker Desktop, which v2 put on the exclusion list |
| **new tools introduced in v3** | — | — | **Prefect 3, Nemotron 3.5 Lightning, Docker Desktop (as the pick), Microsoft Agent Framework, OpenClaw + Hermes Agent (discussed at length), Crossref + Semantic Scholar (explicit)** | |
| **citations (RQ5)** | ~20 inline attributions, 0 URLs (adj. D6 = 1) | ~10 resolving primary URLs, numbered list (D6 = 2) | **0 — empty "Sources" section, no inline attributions either** (D6 = 0) | |

### Fabrication (RQ2) — needs the clean D3/D4 protocol

Names to web-verify before scoring dim 3/4: `gpt-oss:20b` (real, OpenAI open model),
`Qwen3.5 4B / 9B / 27B Coding NVFP4`, `Qwen3.6-35B-A3B` (real), `Nemotron 3.5 Lightning 30B MLX`
(NVIDIA Nemotron line real; "3.5 Lightning" tag to verify), `Qwen3-Embedding 0.6B` (real),
`Prefect 3` (real), `Docling` (real, IBM), `PaperQA2` (real), `Microsoft Agent Framework` (real —
AutoGen successor), `OpenClaw` + `Hermes Agent` (both real per `tool-model-register.md`),
`OpenCode` (real). No obvious invention; the risk items are the `Nemotron 3.5 Lightning` and
`Qwen3.5 27B Coding NVFP4` exact tags. Several specific numeric claims (14 GB, 20 GB, 23 GB, 3.4 GB,
639 MB, "March 2026 Ollama→MLX") are **unsourced** — dim 5 (benchmark factuality) will likely
score 1 or 0.

### RQ6 signal — the strongest datapoint so far

Removing the anti-anchoring / anti-popularity steer (v3) produced, from the same model on the
same task:

1. **A third distinct primary inference engine** (Ollama), after MLX-LM (v1) and llama.cpp (v2) —
   GPT-5's #1 engine pick is not stable under *any* of the three framings.
2. **A markedly more product-heavy answer**: 7 models named vs 2 in v2; Prefect added as a whole
   new orchestration layer; Nemotron, Docker Desktop, Microsoft Agent Framework, OpenClaw and
   Hermes all introduced; the "do not adopt a young all-in-one daemon" caution that v1/v2 carried
   is softened to "test Hermes or OpenClaw before building much custom code".
3. **Citations collapsed to zero** — v3 has an empty Sources section, versus v2's ~10 primary
   URLs and v1's ~20 inline attributions. The response-format request for a Sources list is
   identical across all three versions.

This is direct support for the P3 (`prompt-v3`) ablation hypothesis: the anti-anchoring /
anti-popularity steer is doing real work — with it removed, GPT-5 names more tools, hedges less
about adopting them, and (on this run) stopped sourcing its claims. The *architecture* (one
inference lane, logical agents, coordinator/worker, SQLite state, evidence ledger, Tailscale,
dedicated user) is unchanged across all three — again, "converge on shape, diverge on products",
with the product list widening specifically when the anti-popularity instruction is gone.
