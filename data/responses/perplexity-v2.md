---
ai_name: Perplexity (free tier)
model_version_id: "free tier — model not disclosed in-answer (auto model-selection)"
provider: Perplexity
interface: web app (free tier)
browsing_enabled: yes (retrieval-based; ~14 inline citations to real URLs)
knowledge_cutoff: n/a (retrieval-based)
prompt_version: v2
date_run: 2026-09-01
run_by: roshanaryal1
notes_on_run: >
  Second capture of Perplexity on the paraphrased instrument (prompt-v2 — RFC framing,
  reshuffled sections). Fresh chat, no history. Same free-tier Perplexity as the v1 capture.
  Pair with data/responses/perplexity.md (v1) for the RQ6 prompt-sensitivity delta; the
  axis-by-axis comparison lives in analysis/rq6-prompt-sensitivity.md.
trust_rating: MEDIUM-HIGH — retrieval-grounded, all tools real, states M6 spec facts with a primary source (apple.com/mac-mini/specs) while still refusing to invent throughput numbers.
---

## Raw response

Perplexity — version not disclosed; knowledge cutoff not disclosed; web/tools enabled.  
**Scope note:** I researched the ecosystem using available web sources as of the prompt’s stated 31 August 2026. The M6 Mac mini is a newly announced platform, so there are no independent, reproducible end-to-end agent benchmarks specifically for the 32 GB M6 configuration yet; throughput figures below are therefore treated as estimates unless explicitly sourced.

## Decisions at a glance

| Layer | Final pick | Why |
|---|---|---|
| Local inference | `mlx-lm` server / MLX-native model weights | MLX is designed for Apple silicon shared memory and is the most direct performance/control path; retain Ollama only as a compatibility adapter if a tool insists on its API.  [github](https://github.com/ml-explore/mlx-lm) |
| Primary local model | Qwen-family 14B–18B instruct/coder model in 4-bit MLX quantization, selected after local eval | This is the useful-work sweet spot: enough quality for agent tool use, but leaves RAM for context, browser, queue, and OS. |
| Fast utility model | Qwen 4B–8B instruct, 4-bit MLX | Cheap routing, classification, summarization, task decomposition, log triage, and extraction. |
| Optional cloud escalation | One explicitly configured frontier API provider, approval-gated | Use only for high-stakes final synthesis, hard debugging, or research verification when local work stalls. No cloud dependency. |
| Coding harness | OpenHands in isolated container runtime, called as a bounded job worker | It supports local/Docker runtimes and headless/local filesystem workflows, but it is not a multi-tenant secure platform; use it only behind the supervisor and never expose it publicly.  [docs.openhands](https://docs.openhands.dev/openhands/usage/v0/runtimes/V0_overview) |
| Supervisor/orchestrator | Custom, small Python service backed by SQLite | A narrow custom control plane is more appropriate than adopting a large “multi-agent framework”; it enforces queueing, budgets, approvals, auditability, and recovery. |
| Agent topology | Coordinator + persistent task graph + bounded worker pool | Represents 100+ logical agents as data and task state, while running only one primary inference worker plus one small-model worker. |
| Durable memory | Per-project filesystem evidence store + SQLite/WAL/FTS5 first | SQLite provides durable transactions, full-text search, and better concurrent behavior in WAL mode without operating a separate database server.  [sqlite](https://sqlite.org/docs.html) |
| Semantic retrieval | Local embeddings plus SQLite metadata; add Qdrant only after measured need | Avoid a premature vector-database service on a 32 GB personal workstation. |
| Isolation | Dedicated non-admin macOS user, project allowlist, disposable container/VM workspace where possible | Do not run an autonomous agent under the owner’s daily macOS account. |
| Browser/research | Playwright in a dedicated worker plus evidence-first citation pipeline | Browser output is captured as artifacts; claims cannot cite URLs until source text, metadata, and quoted support are stored. |
| Remote access | Tailscale, Tailscale SSH, private dashboard bound to loopback/Tailscale only | Identity-aware encrypted access avoids public port forwarding; use device approval and narrowly scoped ACLs/SSH rules.  [tailscale](https://tailscale.com/docs/features/access-control/device-management/device-approval) |
| 24/7 process manager | `launchd` LaunchAgents plus SQLite lease recovery and watchdogs | macOS-native restart handling; `KeepAlive` and `ThrottleInterval` support persistent jobs and crash-loop control.  [deepwiki](https://deepwiki.com/apple-oss-distributions/launchd/4.2-property-list-keys) |

# 1. On-device inference

The M6 Mac mini described is a 12-core CPU / 12-core GPU Apple-silicon system with up to 32 GB unified memory and up to 170 GB/s memory bandwidth. Apple lists 32 GB as a supported configuration; contemporary reporting places the M6 at 170 GB/s of bandwidth. [apple](https://www.apple.com/mac-mini/specs/)

The governing constraint is **unified memory**, not raw storage. Model weights, KV cache, macOS, browser tabs, containers, Python services, filesystem cache, and GPU allocations all contend for the same 32 GB pool. The goal is therefore not “largest model that can load,” but reliable sustained progress with low restart frequency.

### Inference runtime choice

Use MLX-native inference through `mlx-lm` as the primary backend.

- MLX is built for Apple silicon and uses shared memory, avoiding CPU/GPU copying inherent in many conventional GPU workflows. [huggingface](https://huggingface.co/docs/transformers/en/community_integrations/mlx)
- `mlx-lm` is maintained by the MLX project and supports loading/generating with compatible Hugging Face model weights; its package exposes command-line and Python interfaces. [github](https://github.com/ml-explore/mlx-lm)
- Independent comparative material suggests MLX often sustains higher Apple-silicon throughput than `llama.cpp`-based paths, though those measurements should be reproduced on the actual M6 before setting operational SLOs. [arxiv](https://arxiv.org/abs/2511.05502)
- Ollama is useful as an OpenAI-like or model-registry compatibility layer. It should not be the architectural center: it can obscure memory residency, context settings, model lifecycle, and scheduler control.

### Actual local model policy

Start with this two-tier configuration:

| Role | Recommended class | Quantization | Resident policy | Context target |
|---|---|---:|---|---:|
| Main agent worker | Strong 14B–18B instruction/coder model, preferably Qwen-family MLX release | 4-bit | Keep resident while task queue is nonempty | 16k–24k tokens |
| Utility worker | 4B–8B instruction model | 4-bit | Keep resident if stable; otherwise load on demand | 8k–16k tokens |
| Embeddings | Small local embedding model | Native/quantized as supported | On demand | N/A |
| Escalation | Frontier cloud reasoning/coding API | Provider-hosted | Never resident | Provider limit |

A 14B 4-bit model normally occupies roughly 8–11 GB after format/runtime overhead; a 4B–8B worker is commonly in the rough 3–6 GB range. Exact memory use varies materially by architecture, MLX conversion, KV cache representation, context length, and batch size. Measure it locally before enabling unattended concurrency.

### What not to do

Do **not** run:

- A 27B–32B model as the always-on primary worker on 32 GB.
- Two simultaneous large model instances.
- A “100 agent” swarm with one model server per role.
- Maximum advertised context sizes by default.
- Multiple large web browsers, local IDEs, Docker Desktop-heavy workloads, and two inference servers together without resource measurements.

A 27B model may technically fit at aggressive quantization, but “fits” leaves too little RAM for useful long-context work and makes swap pressure likely. One benchmark-oriented guide characterizes 22B as the practical comfort ceiling and 27B at 4-bit as tight on 32 GB systems; treat that as a directional datapoint, not a substitute for an M6 measurement. [blog.starmorph](https://blog.starmorph.com/blog/apple-silicon-llm-inference-optimization-guide)

### Expected performance and bottlenecks

No source retrieved provides a trustworthy M6-specific benchmark for the exact models recommended. Before autonomous rollout, record:

- Prompt-prefill tokens/s at 4k, 16k, and 24k context.
- Decode tokens/s at 128, 512, and 2,000 output tokens.
- Peak resident memory for each model/context configuration.
- Model load time from external SSD.
- Time-to-first-token after idle.
- Task completion rate on a local benchmark set: repository edit, failing-test repair, source extraction, and report citation audit.

The main bottleneck will be memory bandwidth during generation, then context prefill and tool latency—not CPU core count. The scheduler should optimize for long uninterrupted turns and tool batching rather than firing many tiny requests.

# 2. Agent runtimes and harnesses

No single current framework should own this entire system. Use complementary tools under a deliberately narrow orchestration layer.

### Category comparison

| Category | Best overall | Best for this Mac | Best open source | Best lightweight | Best mature/stable | Best cutting-edge | Actual pick |
|---|---|---|---|---|---|---|---|
| Coding agent runtime | OpenHands / frontier vendor coding tools | OpenHands bounded jobs + local CLI tools | OpenHands | Aider-style CLI workflow | Conventional CI + Git worktrees | Cloud coding agents | OpenHands as an isolated worker, not supervisor |
| Personal remote gateway | OpenClaw-style gateway | OpenClaw if messaging-driven control is wanted | OpenClaw | Tailscale SSH + dashboard | Tailscale + launchd | OpenClaw ecosystem | Tailscale first; OpenClaw optional |
| Multi-agent orchestration | Custom task graph | Custom SQLite queue | Custom + open libraries | Python asyncio + SQLite | Celery/Redis-style stacks | Large graph/swarm frameworks | Custom small supervisor |
| Browser automation | Playwright | Playwright headless Chromium | Playwright | `curl`/HTTP fetch for simple pages | Playwright | GUI computer-use agents | Playwright evidence worker |
| Isolation | Container/VM workspace | Lightweight container or separate account | Docker-compatible tooling | Separate account + `sandbox-exec`-style restrictions where viable | Dedicated VM | Browser/OS computer-use | Dedicated agent account + containers |

OpenHands is the best fit among general coding-agent harnesses when treated as a **job executor**, because it supports Docker-based and local runtimes. Its own documentation says Docker is the default recommended runtime, while the local runtime executes directly on the machine.  The project’s local-runtime source explicitly warns that it has no sandbox, so it must not be selected for broad unattended machine control. [docs.openhands](https://docs.openhands.dev/openhands/usage/v0/runtimes/V0_overview)

OpenHands also describes itself as intended for a single-user local workstation and states that it lacks built-in authentication, isolation, and scalability for multi-tenant deployments. That makes it unsuitable as the externally accessible control plane. [github](https://github.com/All-Hands-AI/OpenHands/blob/main/README.md)

### Final design

Use:

1. A custom `lab-supervisor` process for queue ownership, policies, routing, resource budgets, retries, approvals, and logging.
2. OpenHands only for isolated coding sessions with a mounted task worktree.
3. Playwright for browser tasks in a separate research-worker container.
4. A small internal tool protocol over localhost HTTP or a Unix domain socket.
5. Tailscale and a minimal private dashboard for human interaction.
6. Optional OpenClaw only if the operator wants chat-based task submission and notifications.

OpenClaw is viable as an optional messaging gateway because it supports macOS installation and a local launchd-managed gateway. However, it has experienced macOS launch-agent lifecycle issues and configuration pitfalls, so it should not be the sole reliability boundary. [github](https://github.com/openclaw/openclaw)

# 3. Many-agent design on small hardware

“100 agents” must mean **100 logical agent records**, not 100 simultaneous inference processes.

### Definitions

| Term | Meaning in this design |
|---|---|
| Logical agent | A row or configuration object specifying role, goal, tool policy, context selection rules, budget, and output contract |
| Agent run | A resumable execution record linked to a task and logical-agent profile |
| Model worker | A single active inference process serving one or a small number of serialized requests |
| Tool worker | A separate process for shell, browser, indexing, test execution, PDF extraction, or dataset analysis |
| Task | A durable unit of work with dependencies, acceptance tests, time/token cost limits, artifacts, and state |
| Coordinator | The policy-governed process that decomposes objectives, assigns work, verifies outputs, and schedules the next state transition |

### Recommended topology

Use a **coordinator–worker task graph**:

```text
Human task / scheduled objective
             |
             v
      Policy + supervisor
             |
     SQLite task graph / event log
             |
   +---------+----------+----------------+
   |                    |                |
   v                    v                v
Planner              Research          Coding
logical agent        logical agent     logical agent
   |                    |                |
   +---------> model-router <------------+
                    |
        +-----------+-----------+
        |                       |
        v                       v
  Main MLX worker         Small MLX worker
  14B–18B, serialized     4B–8B, low-cost tasks
        |
   Tool execution queue
        |
   +----+-----+------+-----+---------+
   | shell    Git   tests  browser  PDF/data |
   +----+-----+------+-----+---------+
```

### Concurrency policy

For this machine:

- One main-model inference request at a time.
- One small-model request at a time, only if its measured memory coexistence is stable.
- Two to four tool workers, because shell tests, indexing, PDF extraction, and web retrieval are often I/O-bound or CPU-bound but do not require a second large model.
- One browser context by default; at most two isolated contexts for approved research jobs.
- Up to 100–500 queued logical agent runs, because queue entries are metadata, not model processes.

### Dynamic sub-agents

The planner may create new logical agents by emitting a constrained schema:

```json
{
  "role": "dependency-auditor",
  "goal": "Identify incompatible API changes in the proposed migration",
  "allowed_tools": ["read_repo", "grep", "run_readonly_tests"],
  "workspace_scope": "project:alpha/worktree:task-184",
  "model_class": "small",
  "max_tool_calls": 20,
  "max_tokens": 6000,
  "approval_required_for": ["network", "write_repo", "shell_destructive"]
}
```

The supervisor validates this schema. Agents cannot create arbitrary new permissions, mount arbitrary directories, or bypass quotas.

### Why this beats a swarm

A swarm adds conversation overhead, duplicate reading of the same repository, and concurrent KV caches. On 32 GB, this degrades useful work per hour. A persistent task graph preserves the supposed benefits of many agents—specialization, independent evidence, review, and parallel tool execution—without duplicating model memory.

# 4. Autonomous coding systems

The coding environment should be **Git-first, test-first, and worktree-first**.

### Chosen coding flow

1. Create a ticket with acceptance criteria, allowed path scope, budget, and stop condition.
2. Create a separate Git worktree on a task branch.
3. Have the planner generate a bounded implementation plan.
4. Run repository inventory and targeted code search.
5. Let the coding worker edit only within the mounted worktree.
6. Run formatting, linting, unit tests, and targeted integration tests.
7. Ask a separate review logical agent to inspect the diff and test evidence.
8. Commit only after verification passes.
9. Keep merge, push, release, and deployment behind explicit approval.

### Git policy

- No work directly on `main` or the operator’s active branch.
- No force pushes, branch deletion, remote pushes, tag creation, or releases unattended.
- Each task has a named worktree: `worktrees/<project>/<task-id>`.
- Use `git diff --check`, status checks, test transcripts, and a generated `RESULT.md` as required completion artifacts.
- Auto-commit to the task branch may be allowed if the commit is local, scoped, and includes test evidence.
- Merge remains an operator approval unless the repository has an explicitly authorized low-risk policy.

### Sandbox policy

OpenHands’ Docker runtime is preferable to its direct local runtime, since the latter explicitly has no sandbox.  However, do not mount: [docs.openhands](https://docs.openhands.dev/openhands/usage/v0/runtimes/V0_overview)

- The agent user’s entire home directory.
- `/Users/<owner>`.
- macOS keychains.
- SSH configuration or keys.
- Docker socket.
- Cloud credentials.
- The root filesystem.
- The host’s `/Applications` or `/Library`.

Mount only the specific worktree, a package-cache mirror when safe, and a task scratch directory.

# 5. Autonomous research systems

Research autonomy fails primarily through weak provenance—not through lack of model reasoning. Build an evidence pipeline where the model cannot turn a search snippet into a citation.

### Research pipeline

```text
Question
  -> research plan
  -> web/literature search
  -> source retrieval
  -> archive source text + metadata + checksum
  -> extract quotations and claims
  -> assign claim-to-evidence links
  -> contradiction scan
  -> draft with machine-checkable citations
  -> citation audit
  -> report
```

### Source hierarchy

Use this ordering when determining what can support a claim:

1. Primary sources: official documentation, vendor specifications, standards, original papers, source repositories, regulator filings, public datasets.
2. High-quality secondary sources: peer-reviewed reviews, respected technical journalism, benchmark analyses with methodology.
3. Tertiary sources: summaries, blogs, forum posts, model-generated indexes—leads only, not decisive evidence.

### Citation integrity gates

A research report cannot be marked complete unless:

- Every external factual claim has one or more source IDs.
- Each source ID resolves to an archived artifact with URL, retrieval timestamp, title, publisher, and extracted text.
- At least one direct excerpt is attached for material claims.
- The report differentiates fact, inference, uncertainty, and recommendation.
- Citations to search-result snippets are rejected.
- The citation checker flags unsupported numerals, named model versions, dates, benchmark values, and superlatives.
- A second logical agent tries to find contradictory evidence before final synthesis.

### Literature and PDFs

Use:

- DOI/Crossref/arXiv/PubMed-style metadata lookups where suitable.
- `pdftotext`, OCR only when necessary, and page/image retention for scanned PDFs.
- Per-document manifest files containing original URL, checksum, license/terms notes, extraction status, and page anchors.
- Local full-text indexing into SQLite FTS5.
- A small local embedding index only for semantic recall, never as the authoritative source record.

# 6. Durable memory

Start simple and inspectable.

### Initial memory architecture

```text
/lab
  /projects
    /project-name
      /repo
      /memory
        decisions.md
        runbook.md
        findings/
        evidence/
        experiments/
        task-briefs/
  /state
    lab.sqlite
    artifacts/
    logs/
    checkpoints/
  /models
  /cache
```

SQLite is the control-plane database. It should contain:

- Tasks, task state, dependencies, leases, retry count, and next-run time.
- Agent definitions and policy profiles.
- Run transcripts and tool invocation summaries.
- Artifact metadata and hashes.
- Claim/evidence/citation links.
- Project decision records.
- Cost, token, runtime, failure, and resource telemetry.
- Full-text searchable notes and extracted documents.

SQLite FTS5 provides full-text-search functionality, while WAL mode can improve concurrency relative to rollback journaling. [sqlite](https://sqlite.org/docs.html)

### Memory types

| Memory | Store | Retention | Use |
|---|---|---|---|
| Working memory | Current prompt/context bundle | Per run | Immediate reasoning |
| Episodic memory | Task runs, failures, tool outputs, checkpoints | Per project | Resume and learn from prior attempts |
| Semantic memory | Curated decisions, architecture facts, validated findings | Per project with limited global summaries | Reuse trusted knowledge |
| Evidence memory | Archived source files, quotes, metadata, checksums | Long-lived | Report provenance |
| Code memory | Repo map, symbol index, test history, commit summaries | Rebuilt incrementally | Faster code navigation |
| Operational memory | Service incidents, resource telemetry, recovery actions | Long-lived | Reliability tuning |

### What to add later

Add a dedicated vector store only after you can show that SQLite FTS plus document metadata fails on real retrieval tasks. At 64 GB or with several large projects, add:

- Qdrant or similar vector service.
- A code-specific indexer.
- A graph layer only for genuinely graph-shaped questions: dependency impact, evidence conflicts, authorship/provenance, or entity relationships.

Do not add Neo4j, Redis, Kafka, Temporal, Kubernetes, or a graph database in phase one.

# 7. Machine control and isolation

The agent should have broad capability **inside an intentionally constrained workspace**, not unrestricted access to the owner’s personal machine.

### Account layout

Create a dedicated standard macOS account such as `ailab`.

- It must not be an administrator.
- It must not share the owner’s home directory.
- It must not have access to personal browser profiles, Messages, Photos, Notes, iCloud Drive, Desktop/Documents, macOS Keychain items, or personal SSH keys.
- Give it access only to explicitly shared project roots and the external data volume.
- Enable FileVault. Apple describes FileVault as built-in encryption for data at rest on Macs. [support.apple](https://support.apple.com/en-nz/guide/deployment/dep82064ec40/web)

macOS application sandboxing and access-control mechanisms are useful layers, but do not treat them as a complete agent sandbox. Apple’s platform security documentation describes sandboxing as restricting what data an app can access and notes data-protection controls. [help.apple](https://help.apple.com/pdf/security/en_US/apple-platform-security-guide.pdf)

### Permission tiers

| Tier | Examples | Unattended? |
|---|---|---|
| P0: Read-only | Read repository, inspect local logs, search indexed documents | Yes |
| P1: Isolated write | Edit a task worktree, create scratch files, generate reports | Yes |
| P2: Bounded execution | Run tests, linters, compilers, container commands within task sandbox | Yes, with resource limits |
| P3: External research | Fetch public URLs, query literature APIs, download documents to quarantine | Yes, allowlisted domains and rate limits |
| P4: Local Git commit | Commit on a task branch with passing checks | Yes, if explicitly enabled per project |
| P5: Network write | Publish issue/comment, send email/message, push to remote | No; approval required |
| P6: Destructive | Delete non-scratch files, modify system settings, install privileged packages, reset database | No; approval required |
| P7: Sensitive/financial | Access keychain, passwords, banking, purchases, production credentials, deploy production systems | Never by default; separate explicit process |

### Network controls

- Bind local APIs to `127.0.0.1` or Unix sockets.
- Do not expose Ollama/MLX, OpenHands, dashboards, or database ports to LAN/WAN.
- Use Tailscale for remote access instead of router port-forwarding.
- Create Tailscale policies permitting only the operator’s approved phone/laptop to reach the dashboard and SSH ports.
- Turn on device approval. Unapproved devices cannot send or receive tailnet traffic. [tailscale](https://tailscale.com/docs/features/access-control/device-management/device-approval)
- Use Tailscale SSH with explicit ACL/SSH rules. Tailscale requires both network and SSH policy authorization for SSH access. [tailscale](https://tailscale.com/docs/features/tailscale-ssh)
- Deny default outbound access for tool containers except DNS, package registries where specifically needed, and research domains during a task.

### Emergency stop

Provide three independent stops:

1. Dashboard “pause queue” switch: no new tasks are leased.
2. Local command: `labctl emergency-stop`, which stops workers, revokes active leases, and blocks new tool calls.
3. `launchctl bootout` or Tailscale SSH command from the operator’s phone/laptop to stop the LaunchAgent.

The emergency-stop path must not depend on the model, browser, queue, or dashboard being healthy.

# 8. Running 24/7

Use `launchd`, not a terminal session, as the macOS service manager.

`launchd` supports `KeepAlive` behavior and configurable `ThrottleInterval`; its default restart throttling exists specifically to avoid repeatedly respawning rapidly failing jobs. [deepwiki](https://deepwiki.com/apple-oss-distributions/launchd/4.2-property-list-keys)

### Services

| Service | Responsibility | Restart policy |
|---|---|---|
| `com.operator.ailab.supervisor` | Queue, policy, task leasing, recovery, routing | `KeepAlive`; 30–60 s throttle |
| `com.operator.ailab.model` | MLX inference endpoint | Restart on failure; unload after prolonged idle if memory pressure |
| `com.operator.ailab.toolworker` | Shell/test/PDF/data execution | Supervisor-managed bounded child processes |
| `com.operator.ailab.research` | Browser fetch, source archiving, citation extraction | Restartable task worker |
| `com.operator.ailab.indexer` | Index and compact artifacts | Scheduled/off-peak |
| `com.operator.ailab.backup` | Snapshot SQLite and manifests | Scheduled daily |
| `com.operator.ailab.monitor` | Health checks, disk/RAM/temp-like metrics, alerting | `KeepAlive` |

### Recovery model

Every task must be durable and idempotent enough to resume:

1. Worker claims task with a lease and heartbeat.
2. Every important tool result becomes an artifact with a hash.
3. Worker writes checkpoints after each plan/tool/verification transition.
4. Supervisor detects expired leases after crash, reboot, or model failure.
5. A recoverer either resumes from checkpoint, retries with exponential backoff, routes to a fallback model, or marks the task `needs_review`.
6. Crash loops trip a circuit breaker; the task is quarantined rather than endlessly retried.
7. A morning summary includes completed tasks, failures, blocked approvals, costs, and proposed next tasks.

### Stop conditions

Each task needs at least one:

- Acceptance tests pass.
- Evidence threshold reached.
- Maximum wall-clock duration.
- Maximum model tokens.
- Maximum tool calls.
- Maximum retries.
- No-progress threshold, such as three edit/test cycles without an objective improvement.
- Sensitive action needed.
- Human clarification required.

### macOS power behavior

For 24/7 operation:

- Prevent system sleep while connected to power using an approved `pmset` configuration or a supervised `caffeinate` process.
- Permit display sleep.
- Disable automatic restarts that bypass disk integrity checks only if the operator accepts that trade-off.
- Configure “restart automatically after power failure.”
- Test a power-loss recovery drill, not merely a process restart.

# 9. Remote reach

The remote interface should favor **status and approvals** over unrestricted remote desktop control.

### Recommended access surfaces

| Surface | Purpose | Exposure |
|---|---|---|
| Tailscale SSH | Emergency control, logs, repairs, Git inspection | Tailnet only |
| Private web dashboard | Submit tasks, view queue/status/logs, approve actions, pause system | Loopback plus Tailscale only |
| Mobile notifications | Completion, failure, approval request, disk/RAM warnings | Push/chat provider, metadata-minimized |
| Read-only status endpoint | Health checks and machine state | Tailnet only |
| Optional chat gateway | Task submission and summaries | Tailnet/private channel only |

Tailscale access-control rules can be narrowed by device/user and destination port, while Tailscale SSH uses the tailnet identity system rather than manually managed SSH keys.  Device approval adds a useful barrier for newly added phones and laptops. [tailscale](https://tailscale.com/docs/features/access-control/device-management/device-approval)

### Phone workflow

A good mobile interaction should require no terminal:

1. Open dashboard or approved private chat.
2. Submit: “Investigate issue 241; do not push or merge.”
3. Receive a plan summary and estimated budget.
4. Inspect artifacts, diffs, failing-test logs, and citation evidence.
5. Approve one of: continue, commit locally, push branch, open PR, stop.
6. Use “pause all” or “emergency stop” at any time.

Do not place secrets, full code, raw customer data, or detailed terminal transcripts in push notifications.

# 10. Storage split

Treat the internal SSD as the operating-system and latency-sensitive service volume; use the external SSD for large, replaceable, project-centric, and archival content.

### Proposed allocation

| Data | Location | Approximate budget | Reason |
|---|---|---:|---|
| macOS, applications, Homebrew, Python/Node runtimes | Internal SSD | 100–150 GB | Reliability and low latency |
| Service state, SQLite DB, WAL, active logs, launchd files | Internal SSD | 20–50 GB | Avoid external disconnect risk and protect transactional state |
| Active model cache: main + utility + embeddings | Internal SSD | 40–100 GB | Faster model startup; keep one current model set only |
| External model archive / alternate quantizations | External SSD | 100–250 GB | Large but noncritical; re-downloadable |
| Repositories and Git worktrees | External SSD or internal for active priority projects | 100–300 GB | Capacity; use internal for latency-sensitive active repos if room permits |
| Papers, datasets, web-source archive | External SSD | 150–400 GB | Large, durable research corpus |
| Scratch workspaces, build outputs, browser downloads | External SSD | 150–300 GB | Isolate churn and simplify cleanup |
| Logs/artifacts older than 30 days | External SSD | 50–150 GB | Keep internal volume clean |
| Backups | Separate encrypted backup disk/cloud destination, not same external SSD alone | Variable | External SSD failure must not destroy state |

### External SSD cautions

- Format it as APFS with encryption.
- Give it a stable volume label and fail-safe mount checks.
- Never place the only live SQLite database on removable storage.
- Store a daily compressed SQLite backup plus evidence manifests on a separate backup target.
- Treat models and derived indexes as rebuildable, but treat the task database, evidence archive, and project decision records as irreplaceable.

# A. Technology stack

| Layer | Chosen technology | Alternatives considered | Rationale |
|---|---|---|---|
| macOS account | Dedicated non-admin `ailab` user | Owner account, root, VM-only | Limits default access to personal data and administrative controls |
| Process management | `launchd` | Docker Desktop restart policies, `supervisord`, manual terminal sessions | Native macOS restart integration and boot/login lifecycle control |
| Primary inference | MLX + `mlx-lm` | Ollama, LM Studio, direct `llama.cpp`, MLC | Best low-level Apple-silicon fit and transparent control of model lifecycle  [github](https://github.com/ml-explore/mlx-lm) |
| Inference API | Small FastAPI/Unix-socket wrapper around MLX | Ollama API-only, OpenAI-compatible server framework | Enables routing, quotas, tracing, cancellation, and explicit residency |
| Main model | 14B–18B Qwen-family instruct/coder MLX 4-bit candidate | Llama-family, Mistral-family, Gemma-family, larger 27B+ models | Most balanced starting class; actual model selected by local acceptance evaluation |
| Utility model | 4B–8B MLX instruct model | Same primary model for all tasks | Faster/cheaper classification and summarization |
| Coding executor | OpenHands in container runtime | Aider, Continue, Cline-like tools, custom shell loop | Strong autonomous coding surface; retain containment and supervisor control  [docs.openhands](https://docs.openhands.dev/openhands/usage/v0/runtimes/V0_overview) |
| Orchestration | Custom Python supervisor + SQLite state machine | LangGraph, CrewAI, AutoGen, Temporal, Celery/Redis | Lower operational overhead and direct enforceability of safety policy |
| Task queue | SQLite task tables + leases | Redis/Celery, RabbitMQ, Kafka | Sufficient at one-machine scale; resilient and inspectable |
| Browser | Playwright worker | GUI automation, browser extensions | Scriptable, isolated, reproducible artifacts |
| Research store | Filesystem artifact archive + SQLite metadata/FTS5 | Notion, cloud RAG service, graph DB | Local, auditable, cheap, queryable  [sqlite](https://sqlite.org/docs.html) |
| Embeddings | Local embedding model + SQLite metadata | Hosted embeddings, immediate vector DB | Local-first; add vector database only after need is demonstrated |
| Remote | Tailscale + private dashboard + SSH | Public reverse proxy, port-forwarding, VNC | No public service required; identity-aware encrypted access  [tailscale](https://tailscale.com/docs/features/access-control) |
| Secrets | Separate secret manager/files with restrictive permissions; injected per approved task | Environment-wide `.env`, owner keychain access | Prevents broad credential inheritance |
| Backup | Time Machine plus encrypted state/artifact snapshots | One external SSD only | Separates machine recovery from data recovery |
| Observability | JSON logs, SQLite run events, disk/RAM checks, local dashboard | Full Prometheus/Grafana stack | Adequate for one workstation; simpler failure domain |

# B. Architecture diagram

```text
                         ┌─────────────────────────────┐
                         │ Operator: phone / laptop    │
                         │ Tailscale-authenticated     │
                         └──────────────┬──────────────┘
                                        │
                      Tailnet-only HTTPS / Tailscale SSH
                                        │
┌───────────────────────────────────────▼────────────────────────────────────────┐
│ Mac mini M6 — dedicated non-admin `ailab` account                              │
│                                                                                │
│  ┌──────────────────┐      ┌───────────────────────────────────────────────┐ │
│  │ Private dashboard │◄────►│ lab-supervisor                                │ │
│  │ status/approval   │      │ policy • scheduling • budgets • recovery      │ │
│  └──────────────────┘      └───────────────┬───────────────────────────────┘ │
│                                             │                                  │
│                               ┌─────────────▼─────────────┐                    │
│                               │ SQLite/WAL task graph     │                    │
│                               │ events • leases • memory  │                    │
│                               └────┬─────────────┬────────┘                    │
│                                    │             │                             │
│                           ┌────────▼───┐   ┌─────▼─────────┐                   │
│                           │ Model router│   │ Evidence store │                   │
│                           │ role/budget │   │ files + hashes │                   │
│                           └──────┬──────┘   └───────────────┘                   │
│                                  │                                               │
│                ┌─────────────────┴──────────────────┐                           │
│                │                                    │                           │
│       ┌────────▼────────┐                 ┌─────────▼─────────┐                │
│       │ Main MLX worker │                 │ Utility MLX worker │                │
│       │ 14B–18B 4-bit   │                 │ 4B–8B 4-bit        │                │
│       └────────┬────────┘                 └─────────┬─────────┘                │
│                └─────────────────┬───────────────────┘                          │
│                                  │                                               │
│          ┌───────────────────────▼────────────────────────────────────┐         │
│          │ Tool broker: validates policy, paths, quotas, audit record │         │
│          └───────┬──────────┬───────────┬─────────────┬───────────────┘         │
│                  │          │           │             │                         │
│     ┌────────────▼─┐ ┌──────▼─────┐ ┌───▼──────┐ ┌────▼──────────┐             │
│     │ OpenHands /  │ │ Git/work-  │ │ Playwright│ │ PDF/data/     │             │
│     │ coding box   │ │ trees/tests│ │ research  │ │ indexing box  │             │
│     └──────────────┘ └────────────┘ └──────────┘ └───────────────┘             │
│                                                                                │
│  Internal SSD: OS, live state, active models      External SSD: projects/data │
└────────────────────────────────────────────────────────────────────────────────┘
```

# C. Resource plan

### RAM budget

| Consumer | Target reservation | Notes |
|---|---:|---|
| macOS, WindowServer, network/security agents | 4–6 GB | Varies with display, browser, system services |
| Main 14B–18B model, 4-bit | 9–13 GB | Model/runtime dependent |
| Main model KV cache, 16k–24k context | 2–5 GB | Must be measured; cap aggressively |
| Utility 4B–8B model, 4-bit | 3–6 GB | Keep only if coexistence passes stress tests |
| Utility model KV cache | 1–2 GB | Shorter context |
| Browser/Playwright | 1–3 GB | One active context |
| Containers, Python supervisor, tools | 2–4 GB | Apply per-worker limits |
| SQLite, filesystem cache, indexing | 1–2 GB | Prefer spare RAM over forced cache target |
| Emergency headroom | 3–5 GB | Essential to avoid memory pressure and swap |

**Normal mode:** main model plus tools; utility model unloadable.  
**Peak target:** stay below about 26–28 GB sustained pressure.  
**Degraded mode:** unload utility model, reduce context to 8k–12k, pause browser/indexing, finish or checkpoint current task.

### Storage budget

| Volume | Use | Budget |
|---|---|---:|
| Internal 512 GB | macOS/apps 150 GB; live state/logs 50 GB; active models 100 GB; free headroom 150+ GB | Keep at least 25–30% free |
| External 1 TB | Models/archive 200 GB; repos/worktrees 200 GB; papers/datasets 300 GB; scratch 200 GB; retained logs 100 GB | Clean scratch automatically |
| Separate backup target | SQLite snapshots, evidence manifests, project metadata, selected repos | Required; not optional |

### Model lifecycle

- Keep the primary model loaded while work is queued.
- Keep the utility model loaded only after proving stable mixed operation.
- Do not hot-swap models for every task; model load time and cache churn destroy throughput.
- Swap primary model only for an explicitly high-value job or scheduled evaluation.
- Schedule embedding/indexing work during model-idle periods.

# D. Agent model

Run 100+ logical agents as durable data, not processes.

Each logical agent is a profile containing:

- Role and goal.
- Allowed tools and allowed project paths.
- Default model class.
- Input retrieval policy.
- Maximum tokens, wall-clock time, tool calls, and retries.
- Evidence/output schema.
- Escalation rules.
- Required reviewer type.
- Approval threshold.

The scheduler maps active tasks to a tiny worker pool. For example:

| Logical role | Runs simultaneously | Model class | Typical output |
|---|---:|---|---|
| Coordinator | 1 | Main | Next-task plan and routing decisions |
| Coding implementer | 1 | Main | Diff, tests, commit candidate |
| Debugger | 0–1 | Main | Failure analysis and minimal fix |
| Research planner | 0–1 | Main | Search/evidence plan |
| Source extractor | 1 | Utility + tools | Structured source record |
| Citation auditor | 1 | Utility | Claim-evidence completeness report |
| Test runner | 2 | No model during execution | Test artifacts |
| Code reviewer | 1 | Main or cloud escalation | Review findings |
| Summarizer/classifier | 1 | Utility | Compressed structured notes |

The queue can hold hundreds of pending roles, but active model inference remains capped.

# E. Model assignment

| Task | Default model | Escalate when | Verification |
|---|---|---|---|
| Planning and decomposition | Main 14B–18B local model | Multi-repo architecture or repeated failed plans | Task graph feasibility check |
| Coding | Main 14B–18B local coder/instruct model | Repeated test failures or security-critical code | Tests, lint, diff review |
| Debugging | Main local model | Three failed loops or opaque cross-system failure | Reproduction script and failing/passing evidence |
| Research query planning | Main local model | Novel high-stakes domain | Source plan review |
| Web/PDF extraction | Utility local model + deterministic parsers | Difficult tables/OCR or academic nuance | Artifact and quote validation |
| Summarization | Utility 4B–8B local model | Legal/scientific high-stakes synthesis | Source-linked audit |
| Classification/routing | Utility 4B–8B local model | Low confidence | Coordinator review |
| Code review | Main local model | Security, production impact, or disagreement | Separate reviewer plus tests |
| Final synthesis | Main local model | Publication-quality/high-stakes output | Citation linter + contradiction scan + optional cloud review |
| Hard reasoning escalation | Optional cloud frontier model | Explicit quality trigger and approval/policy allows | Preserve full prompt/output/audit record |

Cloud routing must include task scope, reason, maximum spend, data classification, and whether code/documents may leave the device. Sensitive local artifacts are never silently sent to a cloud API.

# F. Continuous-operation design

### Overnight cycle

1. Supervisor wakes on timer or queue event.
2. It checks disk space, network reachability, model server health, backup freshness, and unresolved approvals.
3. It selects the highest-value ready task with no blocked dependency.
4. It assigns a logical-agent profile and resource budget.
5. Worker executes a bounded plan–tool–observe–verify loop.
6. Results become immutable artifacts; task state is checkpointed.
7. The verifier accepts, retries, creates follow-up tasks, or blocks for human review.
8. The next task begins only if memory, thermal, disk, and retry policies remain healthy.
9. Morning digest is generated from durable task records.

### Automatic recovery

- `launchd` restarts supervisor/model services with throttling.
- Supervisor reclaims expired task leases.
- Interrupted model responses do not corrupt task state because state changes occur at checkpoint boundaries.
- Browser crashes result in a new isolated context and preserved partial evidence.
- Test timeout kills only the child process, not the supervisor.
- Failed task retries use exponential backoff and change one variable at a time: model, context length, tool timeout, or task decomposition.
- More than a threshold of failures pauses that project and alerts the operator.

# G. Remote-operation design

Use a private web dashboard with Tailscale authentication as the main remote interface.

### Required dashboard functions

- Queue view: state, owner agent, elapsed time, retries, token/time budget.
- Submit task with project, scope, priority, and approval policy.
- View artifacts: diffs, test logs, citations, PDF/source extracts, model decisions.
- Approve or reject privileged steps.
- Pause project, pause all work, retry task, or emergency-stop.
- Check disk/RAM/model health and latest backup.
- Receive concise overnight report.

### Transport and authentication

- Dashboard listens on loopback only, with Tailscale proxying or direct Tailnet binding.
- No public DNS requirement.
- Tailscale device approval enabled. [tailscale](https://tailscale.com/docs/features/access-control/device-management/device-approval)
- Strict ACLs limit dashboard/SSH access to operator-owned devices. [tailscale](https://tailscale.com/docs/features/access-control/acls)
- Tailscale SSH uses identity/policy rather than unmanaged keys. [tailscale](https://tailscale.com/docs/features/access-control)
- Require device lock, platform MFA, and short-lived dashboard session tokens.

# H. Security design

### Default boundaries

- Dedicated non-admin `ailab` user.
- FileVault enabled for internal and encrypted external storage. [support.apple](https://support.apple.com/en-nz/guide/deployment/dep82064ec40/web)
- Projects exposed through explicit shared directories only.
- No inherited owner credentials or browser session.
- Secrets stored separately and injected only into approved task environments.
- Network services private to loopback/Tailscale.
- Tool calls logged with actor, task, arguments, working directory, exit status, and artifact references.
- Containers mount only the current worktree and scratch path.
- Per-task CPU, memory, disk, wall-clock, network, tool-call, and token ceilings.
- Deny patterns for destructive shell operations, plus an allowlist for privileged package installation.

### Unattended permissions

Allowed unattended:

- Read/search allowed project data.
- Create/edit files inside designated task worktrees.
- Run tests, linters, compilers, and analysis scripts with resource bounds.
- Download and parse public research materials to quarantine storage.
- Commit locally to an isolated task branch where policy permits.
- Generate documentation, reports, and evidence bundles.

Requires approval:

- Any network write: push, PR, issue/comment, email, chat, upload.
- Merge, release, deployment, tag, branch deletion, force push.
- Any access to named secrets or production systems.
- Installing system-wide software or changing macOS/security/network settings.
- Deleting outside scratch directories.
- Purchases, subscriptions, or use of paid API beyond a declared budget.
- Sending any material that may contain private project data to a cloud model.

# I. Installation procedure

These commands are a starting procedure, not an instruction to blindly grant permissions. Run them under the dedicated `ailab` account after creating it through macOS Users & Groups.

### Phase 1: Minimal working system

```bash
xcode-select --install
```

Install Homebrew if it is not already present, using the current official Homebrew instructions rather than a copied shell pipe. Then:

```bash
brew install git python@3.12 node sqlite jq ripgrep fd tmux gh
brew install --cask tailscale
```

Create directories:

```bash
mkdir -p ~/ailab/{bin,config,logs,state,models,cache,projects,artifacts,worktrees}
mkdir -p /Volumes/AILAB_DATA/{models-archive,projects,papers,datasets,scratch,retained-logs}
chmod 700 ~/ailab ~/ailab/config ~/ailab/state
```

Create a Python environment:

```bash
python3.12 -m venv ~/ailab/venv
source ~/ailab/venv/bin/activate
python -m pip install --upgrade pip wheel
pip install mlx-lm fastapi uvicorn pydantic sqlalchemy aiosqlite httpx playwright
playwright install chromium
```

MLX LM is installable through `pip install mlx-lm`, and its documented CLI can run MLX-compatible models. [github](https://github.com/ml-explore/mlx-lm)

Initialize the state database:

```bash
sqlite3 ~/ailab/state/lab.sqlite <<'SQL'
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS task (
  id TEXT PRIMARY KEY,
  project TEXT NOT NULL,
  state TEXT NOT NULL,
  priority INTEGER NOT NULL DEFAULT 0,
  payload_json TEXT NOT NULL,
  lease_owner TEXT,
  lease_expires_at TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS event (
  id INTEGER PRIMARY KEY,
  task_id TEXT,
  kind TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
SQL
```

SQLite’s WAL mode is enabled with `PRAGMA journal_mode=WAL;`. [sqlite](https://sqlite.org/wal.html)

### Phase 2: Inference acceptance testing

Download no more than one candidate primary model and one utility model at first. Run controlled benchmarks for:

- 4k/16k/24k context.
- Typical coding prompts and repository maps.
- Tool-calling JSON reliability.
- Peak memory.
- Restart/load time.
- Long 2–4 hour unattended stability.

Do not activate two resident models until the combined stress test shows safe headroom.

### Phase 3: Coding sandbox

Install a Docker-compatible container runtime only if its security model and memory overhead are acceptable on the machine. Configure OpenHands with:

- One task worktree bind-mounted read/write.
- A scratch directory.
- No Docker socket.
- No home-directory mount.
- No host network by default.
- Explicit resource limits.

OpenHands’ docs identify Docker-based execution as the default runtime and characterize the local runtime as direct machine execution.  Do not use the local runtime for broad autonomous execution because it lacks a sandbox. [docs.openhands](https://docs.openhands.dev/openhands/usage/v0/runtimes/V0_overview)

### Phase 4: Research worker

Build a worker that:

- Receives a URL/task ID.
- Downloads to a quarantine directory.
- Stores headers, URL, retrieval time, content hash, title, and text extraction.
- Runs PDF extraction or browser capture.
- Inserts searchable text into SQLite FTS5.
- Emits quotes with source/page/section anchors.
- Never marks a source “citable” until extraction succeeds.

### Phase 5: Supervisor

Implement the supervisor as a small Python service with:

- SQLite leasing and heartbeat.
- JSON task definitions.
- Explicit state machine: `queued → leased → running → verifying → completed|failed|blocked`.
- Tool policy enforcement.
- Per-task budgets.
- Event logging.
- Graceful shutdown and restart recovery.
- A model-router interface.

Test by pulling power or killing the worker process mid-task, then confirming the task resumes or becomes safely blocked.

### Phase 6: `launchd`

Create `~/Library/LaunchAgents/com.operator.ailab.supervisor.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.operator.ailab.supervisor</string>

  <key>ProgramArguments</key>
  <array>
    <string>/Users/ailab/ailab/venv/bin/python</string>
    <string>/Users/ailab/ailab/bin/supervisor.py</string>
  </array>

  <key>WorkingDirectory</key>
  <string>/Users/ailab/ailab</string>

  <key>RunAtLoad</key>
  <true/>

  <key>KeepAlive</key>
  <true/>

  <key>ThrottleInterval</key>
  <integer>30</integer>

  <key>StandardOutPath</key>
  <string>/Users/ailab/ailab/logs/supervisor.out.log</string>

  <key>StandardErrorPath</key>
  <string>/Users/ailab/ailab/logs/supervisor.err.log</string>

  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
    <key>AILAB_HOME</key>
    <string>/Users/ailab/ailab</string>
  </dict>
</dict>
</plist>
```

Load it:

```bash
launchctl bootstrap "gui/$(id -u)" \
  ~/Library/LaunchAgents/com.operator.ailab.supervisor.plist

launchctl kickstart -k \
  "gui/$(id -u)/com.operator.ailab.supervisor"

launchctl print "gui/$(id -u)/com.operator.ailab.supervisor"
```

`KeepAlive` tells `launchd` to keep a job alive, while `ThrottleInterval` controls relaunch pacing. [deepwiki](https://deepwiki.com/apple-oss-distributions/launchd/4.2-property-list-keys)

### Phase 7: Remote access

Install and log into Tailscale under the dedicated operational policy. Then:

```bash
sudo tailscale up --ssh
```

Configure the tailnet so only the operator’s approved devices can reach:

- SSH port 22.
- Dashboard port, for example 8443.
- No inference/database ports.

Tailscale requires explicit network and SSH authorization policies for SSH use in controlled tailnets. [tailscale](https://tailscale.com/docs/features/tailscale-ssh)

### Phase 8: Backup and drills

Automate:

```bash
sqlite3 ~/ailab/state/lab.sqlite ".backup ~/ailab/state/backups/lab-$(date +%F).sqlite"
```

Then copy encrypted backups to a distinct destination. Test:

- Service crash.
- Reboot.
- External SSD disconnected.
- Full disk warning.
- Model out-of-memory event.
- Browser crash.
- Network outage.
- Invalid model output/tool request.
- Emergency stop from remote device.

# J. Exclusion list

| Technology or pattern | Exclude initially | Why |
|---|---|---|
| 100 concurrent LLM agents | Yes | Impossible to run effectively on 32 GB; adds memory contention and coordination overhead |
| 27B–70B model as always-on primary | Yes | Reduces operational headroom and worsens long-context reliability |
| Kubernetes | Yes | Operational complexity exceeds one-machine benefit |
| Kafka/RabbitMQ/Redis stack | Yes | SQLite queue is adequate for a single workstation |
| Neo4j or a knowledge graph from day one | Yes | No demonstrated need; adds a service and ontology burden |
| Full Prometheus/Grafana stack | Yes | JSON logs and dashboard metrics are enough initially |
| Open public dashboard/API | Yes | Unnecessary attack surface |
| Owner-account execution | Yes | Conflates agent access with personal identity and secrets |
| Mounting Docker socket into agent container | Yes | Equivalent to broad host control |
| OpenHands local runtime for unattended broad control | Yes | Its code warns that it has no sandbox.  [github](https://github.com/All-Hands-AI/OpenHands/blob/main/openhands/runtime/impl/local/local_runtime.py) |
| Autonomous Git push/merge/deploy | Yes | High-impact external actions need human confirmation |
| Always-on cloud API keys in agent environment | Yes | A compromised prompt/tool path can exfiltrate or spend |
| GUI computer-use as primary coding mechanism | Yes | Less reproducible and less auditable than shell/Git/API tools |
| Browser profile reuse | Yes | Risks access to logged-in personal accounts and cookies |
| “Memory” based solely on chat transcript/vector embeddings | Yes | Not durable enough; lacks provenance and task-state semantics |
| Blind self-modification of supervisor policies | Yes | The system must not alter its own safety envelope unattended |

# K. Scaling path

| Upgrade | What changes | New practical design |
|---|---|---|
| 64 GB unified memory | More context and a stronger primary model; still favor one main worker | Primary 22B–32B 4-bit candidate plus 4B–8B utility worker; 24k–48k contexts after testing |
| 96 GB unified memory | Support a larger primary model and more isolated tool/browser activity | One 32B–40B main model, one utility model, larger evidence/index workloads, possibly a separate vector service |
| 128+ GB unified memory | Quality and concurrency headroom improve substantially | 32B–70B quantized main model depending on measured throughput; two substantial model workers can become viable |
| External GPU | Not the normal Apple-silicon upgrade path | Prefer a separate Linux inference server rather than trying to force unsupported/awkward eGPU paths |
| Added Linux GPU server | Offload main inference while retaining Mac as trusted control plane | Mac runs supervisor, SQLite, dashboard, and local utility model; GPU server hosts vLLM/SGLang-like high-throughput inference behind private network controls |
| Small cluster | Separate execution, research, and inference nodes | Move queue/database to a backed-up service; retain per-project isolation and policy enforcement |
| Multiple operators | Requires a redesign | Add authentication, authorization, tenancy, secrets governance, audited approvals, and real multi-user isolation; OpenHands itself is not positioned as a multi-tenant secure/scalable control plane.  [github](https://github.com/All-Hands-AI/OpenHands/blob/main/README.md) |

The first scaling dollar should usually buy **memory**, then a separate GPU inference server, not a larger swarm framework. More memory enables longer reliable contexts, more room for verification tools, fewer model swaps, and safer coexistence between browser, containers, and inference.

## Sources

- [Apple Mac mini technical specifications](https://www.apple.com/mac-mini/specs/) — primary. [apple](https://www.apple.com/mac-mini/specs/)
- [MLX LM GitHub repository](https://github.com/ml-explore/mlx-lm) — primary. [github](https://github.com/ml-explore/mlx-lm)
- [Hugging Face MLX integration documentation](https://huggingface.co/docs/transformers/en/community_integrations/mlx) — primary documentation. [huggingface](https://huggingface.co/docs/transformers/en/community_integrations/mlx)
- [OpenHands runtime overview](https://docs.openhands.dev/openhands/usage/v0/runtimes/V0_overview) — primary documentation. [docs.openhands](https://docs.openhands.dev/openhands/usage/v0/runtimes/V0_overview)
- [OpenHands repository README](https://github.com/All-Hands-AI/OpenHands/blob/main/README.md) — primary project documentation. [github](https://github.com/All-Hands-AI/OpenHands/blob/main/README.md)
- [OpenHands local runtime source](https://github.com/All-Hands-AI/OpenHands/blob/main/openhands/runtime/impl/local/local_runtime.py) — primary source. [github](https://github.com/All-Hands-AI/OpenHands/blob/main/openhands/runtime/impl/local/local_runtime.py)
- [SQLite documentation](https://sqlite.org/docs.html) — primary. [sqlite](https://sqlite.org/docs.html)
- [SQLite WAL documentation](https://sqlite.org/wal.html) — primary. [sqlite](https://sqlite.org/wal.html)
- [Apple Platform Security Guide](https://help.apple.com/pdf/security/en_US/apple-platform-security-guide.pdf) — primary. [help.apple](https://help.apple.com/pdf/security/en_US/apple-platform-security-guide.pdf)
- [Apple FileVault deployment guide](https://support.apple.com/en-nz/guide/deployment/dep82064ec40/web) — primary. [support.apple](https://support.apple.com/en-nz/guide/deployment/dep82064ec40/web)
- [Tailscale device approval documentation](https://tailscale.com/docs/features/access-control/device-management/device-approval) — primary. [tailscale](https://tailscale.com/docs/features/access-control/device-management/device-approval)
- [Tailscale access control documentation](https://tailscale.com/docs/features/access-control) — primary. [tailscale](https://tailscale.com/docs/features/access-control)
- [Tailscale SSH documentation](https://tailscale.com/docs/features/tailscale-ssh) — primary. [tailscale](https://tailscale.com/docs/features/tailscale-ssh)
- [launchd plist manual](https://keith.github.io/xcode-man-pages/launchd.plist.5.html) — secondary mirror of system manual. [keith.github](https://keith.github.io/xcode-man-pages/launchd.plist.5.html)
- [OpenClaw macOS documentation](https://docs.openclaw.ai/platforms/macos) — primary project documentation. [docs.openclaw](https://docs.openclaw.ai/platforms/macos)

## Model's own cited sources

Inline `[name](url)` citations throughout + a Sources list. ~14 distinct URLs, mostly primary:
apple.com/mac-mini/specs, github.com/ml-explore/mlx-lm, huggingface.co MLX integration docs,
docs.openhands.dev runtime overview, github.com/All-Hands-AI/OpenHands (README + local_runtime.py),
sqlite.org (docs + WAL), help.apple.com Platform Security Guide, support.apple.com FileVault,
tailscale.com (device-approval + access-control + tailscale-ssh + acls),
deepwiki.com launchd plist keys, keith.github.io launchd.plist(5) mirror,
docs.openclaw.ai/platforms/macos, github.com/openclaw/openclaw.
Secondary: blog.starmorph.com (Apple-silicon LLM guide), arxiv.org/abs/2511.05502 (MLX vs
llama.cpp comparison — arXiv ID is future-dated relative to a 2026-08 capture; existence
unverified, same soft spot as the v1 capture's arXiv IDs).

## Reviewer notes

### Purpose: RQ6 prompt-sensitivity (v1 vs v2)

Second Perplexity capture, on `prompt-v2` (RFC framing, reshuffled sections). Compare to
`data/responses/perplexity.md` (v1). Full axis table: `analysis/rq6-prompt-sensitivity.md`.

### Architecture shape — UNCHANGED

Same machine as v1: MLX-family local inference, **one primary inference worker + one small
worker**, coordinator/worker task graph (explicitly "not a swarm"), SQLite/WAL as the control
plane, dedicated non-admin macOS user + container/VM isolation, Tailscale-only remote with a
private dashboard, launchd + KeepAlive + ThrottleInterval + watchdog, evidence-first research
pipeline with citation-integrity gates, internal SSD = OS + live state + hot models / external
SSD = archive + corpus + scratch, optional approval-gated cloud with no dependency.

### Implementation axes that MOVED (v1 → v2) — all toward *more conservative / less
product-specific*

| axis | v1 | v2 | direction |
|---|---|---|---|
| inference engine | "Ollama first, then MLX-native server" | **`mlx-lm` server primary**; Ollama demoted to "compatibility adapter only, not the architectural center" | MLX-first |
| primary local model | Qwen3-Coder-30B-A3B Q4 | **14B–18B Qwen-family, 4-bit**; explicitly "do NOT run a 27B–32B model as the always-on primary on 32 GB" | smaller, safer |
| orchestration | "LangGraph (durable state machine) + SQLite" | **custom small Python service + SQLite**; "more appropriate than adopting a large multi-agent framework" — LangGraph now only in the "large graph/swarm frameworks" column, not the pick | drops the named framework |
| semantic retrieval | Qdrant (embedded/local persistent) | **local embeddings + SQLite metadata first; add Qdrant only after measured need** | defers the vector store |
| M6 facts | "refused to fake M6 numbers" (no spec stated) | **states 170 GB/s + 12-core CPU/GPU + 32 GB, cited to `apple.com/mac-mini/specs`**, still refuses throughput SLOs | more M6 engagement, still hedged |

### Axes UNCHANGED

coding executor (OpenHands in a container, bounded job worker), task queue (SQLite + leases),
sandbox (dedicated user + container/VM), remote (Tailscale + SSH + private dashboard), 24/7
(launchd), cloud posture (optional, approval-gated, $0-usable), research pipeline (evidence-first
+ citation gates), storage split.

### Fabrication (RQ2) — none

Every named tool resolves: MLX, `mlx-lm`, OpenHands, Playwright, Tailscale, SQLite, launchd,
Qdrant, FileVault, OpenClaw (real per `analysis/verification/tool-model-register.md`). No invented
models — v2 avoids naming a specific model tag at all, giving a "14B–18B Qwen-family, select after
local eval" range. Same soft spot as v1: one future-dated arXiv ID (`2511.05502`) whose existence
is unverified; `blog.starmorph` + `deepwiki` are secondary.

### RQ6 signal

The RFC framing (v2) produced the **same architecture** with **four implementation choices shifted
uniformly toward minimalism** — no named orchestration framework, a smaller primary model, MLX
instead of Ollama as the centre, and a deferred vector store. This is consistent with the paper's
"converge on shape, diverge on products" result, and is a preliminary datapoint that the
"senior AI infrastructure architect" role framing in v1 nudges toward naming specific products
while a neutral "respond to this RFC" framing nudges toward the smallest defensible stack.
Zero fabrication in either framing for this system.
