---
ai_name: Perplexity (free tier)
model_version_id: "free tier — default 'Sonar' (Llama-based), auto model-selection; not disclosed in-answer"
provider: Perplexity
interface: web app (free tier)
browsing_enabled: yes (Perplexity always retrieves; ~12 inline citations to real URLs)
knowledge_cutoff: n/a (retrieval-based)
prompt_version: v1
date_run: 2026-08-31
run_by: roshanaryal1
notes_on_run: >
  Free-tier Perplexity. Default model is "Sonar" (Perplexity's own, built on Llama); the free tier
  auto-selects a model per query and does not expose which one answered. Cited sources inline
  (arxiv, docs.langchain, docs.openhands, tailscale, sqlite.org, docs.litellm, support.apple, etc.).
  Explicitly flagged the M6 as "future hardware relative to published benchmarks" and used
  conservative sizing instead of inventing throughput numbers.
trust_rating: MEDIUM-HIGH — retrieval-grounded, real tools only, honest about hardware uncertainty; the single most security-thorough response so far.
---

## Raw response

You should build this as a **small, durable local AI platform**, not as a single "autonomous agent" application. On a 32 GB Apple-Silicon Mac mini, the best practical design is a queue-driven orchestrator with a small number of local inference workers, sandboxed execution workspaces, strong approval gates, and a research pipeline that treats every claim as data with attached evidence.

The key constraint is that you can have **100+ logical agents and tasks**, but you should normally run only **one substantial local model worker at a time**—or one medium worker plus a few tiny classifier/extractor workers. The goal is useful verified work per hour, not an impressive-looking swarm of simultaneously stalled model instances.

A caveat: an "M6 Mac mini" is future hardware relative to many published model benchmarks. I therefore use current Apple-Silicon runtime findings and conservative sizing rather than pretending there are exact M6 throughput measurements. On Apple Silicon, MLX-family runtimes are generally the high-throughput path; research comparing MLX, MLC-LLM, llama.cpp, Ollama, and PyTorch MPS found MLX strongest for sustained generation, while llama.cpp remains a very useful compatibility and lightweight single-stream option. Recent work on MLX-based serving also reports substantial throughput advantages and continuous batching, though its benchmark hardware is not your exact Mac. [ui.adsabs.harvard](https://ui.adsabs.harvard.edu/abs/2025arXiv251105502R/abstract)

## Executive recommendation

Build this stack:

- **Inference service:** Ollama first, with MLX-native serving as the performance upgrade path after baseline stability. Keep `llama.cpp` installed only as a diagnostic/compatibility tool.
- **Primary local coding model:** Qwen3-Coder-30B-A3B-Instruct at a 4-bit quantization, *only if measured headroom is acceptable on your specific M6*. Otherwise use an 8B–14B coding/general model as the always-loaded worker and reserve the 30B MoE model for deliberate high-value jobs.
- **Primary runtime for coding:** OpenHands Software Agent SDK / OpenHands local deployment, but run actual coding execution in isolated workspaces—not directly in your home directory. OpenHands has sandboxed execution concepts, lifecycle controls, multi-model routing, REST/WebSocket support, and integration paths for visual, CLI, API, and browser-oriented interfaces. [arxiv](https://arxiv.org/abs/2511.03690)
- **Orchestration:** a **custom, intentionally small Python supervisor** built with LangGraph for durable state-machine workflows, SQLite for task state, and a worker queue. LangGraph is appropriate here because its agents/runtimes support durable execution, persistence, human-in-the-loop mechanisms, and controlled deterministic-plus-agentic flows. [docs.langchain](https://docs.langchain.com/oss/python/langchain/overview?ajs_aid=1e2b6e66-3572-445f-b59e-2af844e3fb2f)
- **Research:** custom evidence-first research pipeline using Playwright, OpenAlex, Crossref/Semantic Scholar-compatible metadata connectors, local PDF extraction/OCR, structured claim-evidence tables, and mandatory source verification. OpenAlex's data expansion includes DataCite and many institutional/subject repositories, making it a strong open discovery layer. [docs.openalex](https://docs.openalex.org/how-to-use-the-api/xpac)
- **Memory:** SQLite + FTS5 + Markdown/Git from day one. Add local embeddings and Qdrant only after you have enough material that lexical search no longer works. SQLite FTS5 is built-in full-text search and is sufficient for a personal knowledge/work log initially. [sqlite](https://sqlite.org//fts5.html)
- **Isolation:** a dedicated non-admin macOS account, per-task git worktrees, restricted sandbox containers, allowlisted directories, no host secrets mounted by default, and a command/approval policy.
- **Remote access:** Tailscale private tailnet, Tailscale SSH, and `tailscale serve` for the dashboard. Do **not** open your dashboard, Ollama, OpenHands, Docker socket, databases, or agent APIs to the public internet. Tailscale supports policy-controlled private access and SSH auditing; its access controls can be maintained through visual policy tooling or policy files. [tailscale](https://tailscale.com/blog/march-26-product-update)
- **Always-on:** `launchd` services plus SQLite-backed task leases, heartbeats, restart policies, watchdog checks, structured logs, and scheduled queue scans.

Do **not** start with a swarm framework, a graph database, Kubernetes, Redis, Postgres, a vector database server, a desktop GUI automation agent, or 100 model processes. Those add failure modes without increasing useful autonomy on 32 GB unified memory.

## Technology choices

"Best" varies by criterion. The choices below distinguish market leaders from what is actually rational on your hardware.

| Layer | Best overall | Best for 32 GB M6 Mac mini | Best open-source option | Best lightweight option | Best mature/stable option | Best cutting-edge option | What you should use |
|---|---|---|---|---|---|---|---|
| Apple inference runtime | MLX-based serving | Ollama with current Apple backend, then MLX-native server if benchmarked faster | MLX / `mlx-lm`; llama.cpp | llama.cpp server | Ollama | vLLM-MLX / MLX-native continuous batching | Ollama initially; benchmark MLX server later |
| Local coding model | Larger cloud frontier coding models | Qwen3-Coder-30B-A3B Q4 only for high-value jobs; smaller local model for routine loops | Qwen3-Coder family | Qwen 3.5/3 4B–8B class | Qwen models through Ollama | Devstral Small 2 if its exact local quant/performance proves suitable | Qwen3-Coder-30B-A3B plus one 4B–8B helper |
| Coding harness | Strong cloud-native coding agents | OpenHands SDK with local sandboxed worktrees | OpenHands SDK | Aider/CLI loop for narrowly scoped work | OpenHands | Custom OpenHands SDK agent topology | OpenHands for execution, custom supervisor for scheduling |
| Workflow orchestration | Durable workflow runtime | LangGraph + SQLite | LangGraph | Plain Python state machine | LangGraph | Event-sourced worker fabric | Custom Python supervisor, optionally using LangGraph |
| Model routing | Dedicated gateway/router | Direct local endpoint + simple policy router | LiteLLM | Python routing function | LiteLLM | Budget/fallback-aware LiteLLM gateway | Start simple; add LiteLLM only when cloud fallback exists |
| Research automation | Evidence-first custom pipeline | Playwright + APIs + local storage | Playwright, GROBID, PyMuPDF, OpenAlex | `requests` + structured APIs | Playwright | Browser-agent systems under strict tool policy | Custom evidence pipeline, not a generic "deep research agent" |
| Memory | Hybrid long-term store | SQLite + FTS5 + Markdown/Git | SQLite, Qdrant local | SQLite only | SQLite | SQLite + vector + graph projection | SQLite/FTS5 first, Qdrant later |
| Browser automation | Playwright | Playwright in sandboxed profile | Playwright | Playwright headless | Playwright | Browser MCP/agent interfaces | Playwright directly; optional MCP wrapper later |
| Sandbox | VM/microVM isolation | Containers plus dedicated macOS account | Docker/Podman constraints | Per-worktree subprocess policy | Docker Desktop | MicroVM tools where proven on macOS | Docker workspaces; do not mount your home directory |
| Remote access | Zero-trust private network | Tailscale | Headscale is an alternative, more operational work | Tailscale | Tailscale | Tailscale identity-aware app controls | Tailscale only |
| Scheduling/always-on | Durable queue plus OS service manager | `launchd` + SQLite + watchdog | Python + `launchd` | cron/launchd timer | `launchd` | Temporal-like distributed workflow engines | `launchd`, SQLite leases, no external scheduler |

### Why this split matters

OpenHands is useful as a **software-agent execution harness**, not as the complete control plane for a personal autonomous operating environment. Its SDK provides useful building blocks—concurrency, sandboxes, conversations, event access, security analysis hooks, and an agent-server model—but it should not be the thing that owns your global task queue, credentials, personal filesystem, security decisions, research corpus, or long-term memory. [docs.openhands](https://docs.openhands.dev/sdk/guides/convo-async)

LangGraph should likewise not be mistaken for an autonomous coding tool. It is a durable workflow/state-machine substrate. Use it to model explicit state transitions such as:

Queued -> Scoped -> Planned -> Executing -> Verifying -> Blocked/Complete

This gives you restartability, observability, approval points, and deterministic failure handling rather than an unbounded "keep trying" agent loop.

## Complete architecture

```text
                         Phone / Laptop / Browser
                                  |
                    Tailscale private encrypted tailnet
                                  |
                     Tailscale Serve reverse proxy
                                  |
                Local dashboard + approval console + API
                                  |
                    +-------------v--------------+
                    | Always-on Supervisor       |
                    | Python service via launchd |
                    | health checks / watchdog   |
                    +-------------+--------------+
                                  |
          +-----------------------v-------------------------+
          | Durable Control Plane                          |
          | SQLite: tasks, leases, events, approvals, budget|
          | Markdown/Git: durable project/research artifacts |
          +---------------+----------------+----------------+
                          |                |
                 +--------v-------+  +----v-----------------+
                 | Policy Engine  |  | Scheduler / Queue    |
                 | permissions    |  | priorities / retries |
                 | risk scoring   |  | resource reservations|
                 +--------+-------+  +---------+------------+
                          |                    |
          +---------------v--------------------v----------------+
          | Logical Agent Factory                              |
          | planner / coder / test / reviewer / research / docs|
          | Each is a role specification, not a permanent LLM  |
          +-----------------------+---------------------------+
                                  |
          +-----------------------v---------------------------+
          | Worker Pool and Model Router                     |
          | 1 primary coding/reasoning worker               |
          | 1 small utility worker when headroom permits    |
          | browser / PDF / test workers without LLM        |
          +-------+-----------------------+------------------+
                  |                       |
       +----------v---------+   +--------v---------------------+
       | Local inference    |   | Optional cloud escalation   |
       | Ollama / MLX       |   | only approval/budget governed|
       | localhost only     |   | LiteLLM proxy if enabled    |
       +----------+---------+   +-----------------------------+
                  |
      +-----------v-----------------------------------------------------+
      | Restricted Tool Plane                                          |
      | Git worktrees | sandbox terminal | Python | test runners       |
      | Playwright browser | PDF/document extraction | research connectors |
      | filesystem capability API | artifact/report generator          |
      +-----------+-----------------------------------------------------+
                  |
      +-----------v-----------------------------------------------------+
      | Storage and Memory                                            |
      | Internal SSD: OS, applications, active DB, active repos        |
      | External SSD: models, papers, datasets, task workspaces, archives|
      | SQLite + FTS5; later embeddings + Qdrant local                 |
      +---------------------------------------------------------------+
```

### Control-plane principle

Your autonomous system needs a separation between:

1. **Decision plane** — model chooses a plan, proposes actions, assesses evidence.
2. **Control plane** — task state, policy, scheduling, resource limits, retries, audit logs.
3. **Tool plane** — commands, browsers, filesystem, Git, documents, network.
4. **Data plane** — repositories, papers, databases, models, artifacts.

Never let the model itself become the sole control plane. A hallucinated or compromised model response must not be able to silently alter resource budgets, erase logs, expose secrets, change policy, or bypass approvals.

## Hardware and model plan

### Memory allocation

Treat your 32 GB unified memory as a shared system pool, not "32 GB VRAM." In practice, preserve substantial headroom to prevent memory pressure, swapping, browser failures, and model eviction.

| Consumer | Target reservation | Notes |
|---|---:|---|
| macOS, WindowServer, base services | 4–6 GB | Higher during normal interactive use |
| Supervisor, SQLite, dashboard, queue, logs | 1–2 GB | Mostly modest |
| Development tools, Git, Python, test processes | 2–4 GB | Can spike substantially during builds/tests |
| Browser research process | 1–3 GB | Multiple pages/PDF viewers can spike |
| Filesystem cache and safety headroom | 4–6 GB | Do not allocate this to models |
| Primary LLM weights | 8–18 GB | Depends on model/quantization |
| KV cache / active context | 2–6 GB | Main variable; constrain it deliberately |
| Small helper model, if loaded | 2–5 GB | Optional, only after measurement |
| Practical working allocation | about 26–28 GB | Leaves 4–6 GB of resilience margin |

### The important conclusion

A 30B-total-parameter MoE coder at Q4 may technically fit, but it is **not** a general concurrent serving model on your machine. Reports place Qwen3-Coder-30B-A3B around roughly 17–20 GB at 4-bit, with 30.5B total parameters and about 3.3B active parameters; its large nominal context does not mean you should provision 256K context locally. [orcarouter](https://www.orcarouter.ai/blog/best-local-llm-for-coding)

Use it as a single high-quality coding worker with:

- **Initial context cap:** 16K tokens.
- **Normal maximum:** 32K tokens.
- **Exceptional cap:** 48K–64K only when other memory-heavy programs are stopped and the agent has a clear reason.
- **One primary inference request at a time.**
- **No second large model concurrently resident.**
- **No browser-heavy, test-heavy, long-context job while the model is handling a massive prompt unless measured headroom supports it.**

The quoted 256K native context is a capability ceiling, not a productivity recommendation for a 32 GB machine. Context consumes KV cache and raises time-to-first-token. Make repository indexing, targeted retrieval, file summaries, and code navigation do the work that people often try to solve by loading an entire repository into the context.

### Recommended model roles

| Role | Default model | Configuration | Why |
|---|---|---|---|
| Planning and task decomposition | Qwen3-Coder-30B-A3B Q4 when code-heavy; otherwise 8B general/reasoning model | 16K–32K context, low temperature | Planning must read repository and constraints, but does not need a giant context by default |
| Coding and multi-file modification | Qwen3-Coder-30B-A3B-Instruct Q4 | One worker, 16K–32K context | Strong practical local coding choice; designed for agentic coding/tool workflows and long-context code tasks [localaimaster](https://localaimaster.com/blog/qwen-3-local-setup-guide) |
| Debugging | Same coding model | Tool-call/test loop with max iteration count | Debugging benefits from shared repository state and test results |
| Code review | Primary coder or small separate reviewer sequentially | Read-only worktree by default | Avoid a second large model; use a fresh context and evidence-oriented review rubric |
| Research query planning | 8B general model or primary model when needed | 8K–16K | Lower-cost task; web evidence does the heavy lifting |
| Paper/PDF extraction | No LLM first; PyMuPDF/GROBID/OCR then small model | Chunked structured extraction | Deterministic extraction before interpretation |
| Claim classification and triage | 4B–8B model | Short contexts, batched | Cheap, fast, and parallel-friendly |
| Summarization | 4B–8B helper | 4K–12K | Summaries should be traceable to chunks/citations |
| Final synthesis | Primary coder/general model; optional approved cloud escalation | Evidence pack, strict citation schema | Highest leverage; explicitly verify citations first |

### Models to install initially

Do not install ten models. Start with two, benchmark them, then decide.

1. **Primary:** `Qwen3-Coder-30B-A3B-Instruct`, 4-bit variant compatible with your serving stack.
   - Use for coding, complex debugging, implementation planning, synthesis.
   - Keep unloaded except when active if memory pressure is a concern.
   - Verify actual model tag and quantization availability in Ollama/MLX at install time; model registries change frequently.

2. **Utility model:** a current Qwen 3/Qwen 3.5 4B–8B instruct model.
   - Use for classification, routing, document chunk labels, simple summaries, task extraction, log triage, and first-pass research clustering.
   - This allows useful noncoding tasks without waking/loading the primary coder.

3. **Optional visual/document model:** only after the base system works.
   - A compact Qwen-VL-family model can help inspect screenshots, scanned figures, and visual PDFs.
   - Do not keep it resident with the primary coder.

Devstral Small 2 is worth periodically re-evaluating: reports describe it as a 24B local-capable agentic coding variant with a 256K context window, but your system should select it only after a direct benchmark on your own hardware shows better end-to-end repo-task results than Qwen3-Coder at your safe memory cap. Do not make model choice from parameter count or a single SWE-bench score. [therundown](https://www.therundown.ai/tools/devstral-2)

### Inference runtime decision

| Runtime | Verdict | Use |
|---|---|---|
| Ollama | **Recommended starting point** | Simple lifecycle, model management, local API compatibility, mature integrations |
| MLX / `mlx-lm` | Recommended performance experiment | Benchmark for your two selected models; may become hot-path server |
| vLLM-MLX | Promising but not first install | Consider when you genuinely have multiple queued local requests and want continuous batching |
| llama.cpp | Keep as fallback/diagnostic | Useful GGUF ecosystem, portability, single-stream service |
| LM Studio | Optional interactive workstation UI | Not the always-on backend |
| PyTorch MPS | Avoid as main server | Less suitable for the local-serving role compared with dedicated runtimes |

A recent Apple-Silicon runtime study found MLX strongest in sustained generation, MLC-LLM lower in moderate-prompt first-token latency, llama.cpp efficient for lightweight single-stream work, and Ollama easier operationally but with runtime overhead in the tested configurations. Treat that as a direction, then run your own two-hour repeatable benchmark because your chip, model format, context length, and workload mix dominate the decision. [ui.adsabs.harvard](https://ui.adsabs.harvard.edu/abs/2025arXiv251105502R/abstract)

### Concurrency rule

| Workload | Safe initial concurrency |
|---|---:|
| Primary 30B MoE coding model | 1 active request |
| Small 4B–8B model | 1 active request, possibly 2 short batch-like requests after testing |
| Browser-only research retrieval | 2–4 isolated jobs, rate-limited |
| PDF extraction | 1–2 jobs, CPU/RAM constrained |
| Git/test execution | 1 heavy build/test job per repository workspace |
| Logical agents/tasks in queue | 100–1,000+ |
| Active agent loops | 1 primary executive loop + 1–3 non-LLM I/O workers |

The research on MLX-style continuous batching demonstrates why aggregate throughput may grow with concurrency on larger systems, but you do not have the memory margin to turn that result into a recommendation for many 30B-model requests on 32 GB. [arxiv](https://arxiv.org/abs/2601.19139)

## Agent architecture

### 100 logical agents is not 100 LLMs

A logical agent is a short-lived job specification:

```json
{
  "id": "task-2026-08-31-042",
  "role": "test_failure_triager",
  "objective": "Classify failing tests and propose minimal reproduction",
  "workspace": "project-alpha/worktrees/task-042",
  "allowed_tools": ["read_repo", "run_tests", "read_logs"],
  "model_class": "utility",
  "max_steps": 12,
  "max_wall_time_minutes": 20,
  "approval_policy": "no-write",
  "depends_on": ["task-041"],
  "status": "queued"
}
```

It does **not** require an always-running system prompt, model process, browser, terminal, or memory context.

### Recommended topology

```text
Human objectives / scheduled jobs
            |
            v
      Executive coordinator
      - converts objectives into task DAG
      - assigns risk/cost class
      - creates stop conditions
            |
      +-----+---------------+
      v     v               v
 Planner  Research lead   Coding lead
      |     |               |
      v     v               v
 scoped  evidence       implementation
 tasks   collection     tasks
      |     |               |
      +-----+-------+-------+
                    v
              Queue + leases
                    |
       +------------+------------+
       v            v            v
  LLM worker    browser/PDF    test/Git
  one at a time  I/O workers    workers
                    |
                    v
         verifier / critic / artifact writer
                    |
                    v
           follow-up tasks or completion
```

### Worker-pool behavior

1. The coordinator creates a task DAG, not a flat prompt.
2. Cheap deterministic steps run first: repository index, `git status`, test discovery, file inventory, paper metadata collection, PDF text extraction, source deduplication.
3. The model receives a focused work packet rather than raw filesystem chaos.
4. Tool actions append events to durable storage.
5. Verification runs independently from the actor where feasible.
6. Failed verification becomes a structured follow-up task with failure artifacts.
7. Tasks expire, pause for approval, retry with bounded attempts, or escalate—not loop forever.

### Why not a swarm?

A fully peer-to-peer swarm is inefficient on a resource-constrained system: multiple models compete for the same unified memory and memory bandwidth; agents duplicate repository exploration and web search; their contexts diverge; their tool actions collide; debugging emergent failure paths becomes difficult; a weak local model is often made worse by a noisy swarm architecture.

Use a **coordinator/worker architecture with hierarchical delegation**, not a free-form swarm: Coordinator plans and maintains the task graph; Leads for coding, research, documentation, operations; Workers are narrowly scoped ephemeral tasks; Verifiers do read-only evaluation where possible; Policy engine is not model-controlled.

## Coding system

### Recommended coding loop

Use OpenHands as the execution harness only after you define workspace discipline:

```text
Repository inventory -> Create issue/task record -> Create dedicated Git branch and worktree ->
Read-only repository analysis -> Plan with acceptance tests -> Implementation loop in sandbox ->
Formatter / lint / unit test / integration test -> Independent review task ->
Generate changelog / docs / evidence bundle -> Human approval for merge or publication
```

OpenHands is well suited to tool-driven coding because its SDK/runtime direction emphasizes sandboxed execution, lifecycle management, model-agnostic routing, and user/API interfaces. Its automation model also illustrates the risk: an automation sandbox can have terminal, files, secrets, MCP integrations, network access, and Git-provider access. For your workstation, do **not** copy that broad default; split privileges by task class. [arxiv](https://arxiv.org/abs/2511.03690)

### Git rules

Fully autonomous: create branches such as `agent/task-042-short-name`; create and delete task worktrees; modify files inside an approved workspace root; run formatters, linters, tests, static analysis, and local development commands; commit with signed-off machine identity only within agent branches; produce diffs, test logs, and review summaries; open a local "ready for review" task.

Requires approval: merge into `main`, `master`, release, or protected branches; push to a remote repository for the first time; create pull requests on public repositories; modify CI/CD workflows, deploy scripts, package publishing configuration, infrastructure-as-code, or dependency lockfiles with major version changes; delete branches with unmerged work; rebase a shared branch; write outside the workspace/repository allowlist.

Never allowed without manual reconfiguration: force-push; `git clean -fdx` outside a disposable worktree; rewrite shared history; alter SSH/GPG signing configuration; read arbitrary credential stores; upload private repository content to a third-party model provider.

### Worktree layout

```text
/Volumes/AIData/agent-lab/
├── models/
├── projects/
│   ├── project-alpha/
│   │   ├── source/                 # canonical clone, mostly human-maintained
│   │   ├── worktrees/
│   │   │   ├── task-00042/
│   │   │   └── task-00043/
│   │   ├── .agent/
│   │   │   ├── project-policy.yaml
│   │   │   ├── repository-map.md
│   │   │   ├── decisions/
│   │   │   └── task-artifacts/
│   │   └── README-agent.md
├── research/
│   ├── corpus/
│   ├── extracted/
│   ├── evidence/
│   └── reports/
├── state/
│   ├── agent.db
│   ├── embeddings/
│   ├── events/
│   └── checkpoints/
├── workspaces/
│   └── disposable/
├── logs/
├── cache/
└── backups/
```

## Research architecture

### Do not use a generic research agent as the source of truth

Autonomous research is fundamentally an **evidence management workflow**, not a chat completion workflow. The system should never output a polished assertion unless it can link the assertion to source passages and identify whether the source was primary, secondary, preprint, peer-reviewed, publisher metadata, or an unverified web page.

### Evidence-first pipeline

```text
Research question -> Question decomposition and search plan ->
Discovery (web search; OpenAlex / Crossref / Semantic Scholar-style metadata; publisher pages; relevant repositories and standards) ->
Source capture (canonical URL; DOI / arXiv / PMID / OpenAlex ID; publication date; authors / venue; licensing / access status) ->
Document acquisition and extraction (HTML text; PDF text; OCR if scanned; structured section/chunk IDs) ->
Evidence ledger (claim ID; quoted passage; exact location/page/section; source ID; confidence; limitations; contradicting evidence) ->
Claim verification (at least two independent sources for consequential claims; primary source required for technical/product claims where possible; contradiction search) ->
Synthesis (every sentence classified as sourced, inference, or recommendation) ->
Report + bibliography + evidence appendix
```

OpenAlex is a good open discovery connector, and its recent data expansion explicitly adds DataCite plus many institutional and subject repositories. But metadata discovery is not evidence extraction: retrieve the primary paper/publisher page wherever permitted and record the exact supporting passages. [docs.openalex](https://docs.openalex.org/how-to-use-the-api/xpac)

### Anti-hallucination rules

1. **No citation is generated from model memory.** A citation can only be emitted from a source record in the evidence ledger.
2. **Every factual claim carries an evidence key.**
3. **The final writer sees only extracted evidence objects, not a vague list of URLs.**
4. **Citation verifier checks:** source exists; URL/DOI resolves or is archived; quoted text actually appears in extracted content; cited source supports the specific claim; publication date and venue match metadata; source is not cited twice under conflicting titles/authors.
5. **Contradiction agent is mandatory** for important reports: searches for counterevidence; labels unresolved disagreement; does not average incompatible findings.
6. **No "research complete" state** until every material assertion is either cited, explicitly marked as inference, or removed.
7. **PDF extraction errors are recorded**, especially tables, formulas, figures, and OCR confidence.

### Document tools

Start with deterministic tools: `PyMuPDF` / `pymupdf4llm` for PDF text and page references; `pdftotext` as a cross-check; OCR only for scanned PDFs, with page-level OCR confidence; GROBID later if you process many academic PDFs and need structured references/sections; Pandoc/Markdown export where useful; Python/Pandas/Polars/DuckDB for datasets; Playwright for browser research and reproducible browser workflows.

Playwright is a solid browser control choice because it supports robust locator-based automation and trace artifacts that include timeline/state information useful for diagnosing automation failures; use its traces as tool/audit artifacts, not as an invitation to let an agent log into every website. [thinksys](https://thinksys.com/qa-testing/playwright-features/)

## Persistent memory

### Start simple

| Memory type | Initial storage | Contents |
|---|---|---|
| Operational/task memory | SQLite | task state, queue leases, retries, approvals, budgets, event log |
| Project memory | Markdown + Git in each project | architecture, decisions, conventions, commands, issues, changelog |
| Research memory | SQLite + Markdown/JSON artifacts | sources, claims, evidence, papers, notes, reports |
| Code/repository memory | Repository maps and generated summaries | module maps, test commands, dependency notes |
| Episodic memory | SQLite events | what agent did, observations, outputs, failures |
| Semantic memory | FTS5 initially | searchable decisions, docs, evidence, notes |
| Global policies | Versioned YAML/Markdown | permissions, model routing, data boundaries, action policy |

SQLite FTS5 is enough initially because it provides full-text indexes and searchable text collections without operating a separate search server. [sqlite](https://sqlite.org//fts5.html)

### Add later

After you have a meaningful corpus—e.g., thousands of notes/chunks or repeated retrieval failures—add: local embedding generation; Qdrant embedded/local persistent mode; hybrid retrieval (FTS/BM25 + embeddings + metadata filters); separate project and global collections; reranking; optional lightweight knowledge-graph projections.

Qdrant's client can run locally within the Python process with in-memory or persistent-on-disk storage, so it is a sensible later step without immediately deploying another server. [jeongsk.mintlify](https://jeongsk.mintlify.app/oss/python/integrations/vectorstores/qdrant)

Do **not** begin with Neo4j, Mem0-style opaque memory automation, a graph database, or multiple vector stores. The hard problem at first is not semantic retrieval—it is disciplined source provenance, project boundaries, and explicit task records.

## Security architecture

Your system should be autonomous within a narrow, explicit authority envelope—not privileged by default.

### Accounts and boundaries

| Boundary | Recommendation |
|---|---|
| macOS account | Create `agentops` as a separate standard, non-admin user |
| Personal account | Keep email, browser profiles, iCloud Drive, password manager, Messages, financial files, photos, and personal home directory out of agent scope |
| Agent home | `/Users/agentops` with only required tools, no personal keychain access |
| Workspace root | External SSD `/Volumes/AIData/agent-lab` owned/mounted for `agentops` |
| Repositories | Read/write only through approved worktrees |
| Model server | Bind to `127.0.0.1`; no LAN/public listener |
| Dashboard | Bind localhost, publish privately through Tailscale Serve |
| Containers | No Docker socket inside an agent container; non-root user; read-only base image where possible |
| Network | Default outbound allowlist for research; block LAN/private network ranges from agent containers except explicitly needed services |
| Secrets | Inject per-task short-lived secrets only; never mount a whole `.env`, browser profile, SSH directory, or macOS Keychain |
| Logs | Append-only event log plus rotating application logs; redact secrets before storage |

### Permission tiers

| Tier | Examples | Autonomous? |
|---|---|---|
| 0: Read-only local | Read approved repo/docs, inspect Git status, search indexed corpus | Yes |
| 1: Safe workspace write | Edit files in task worktree, create branch, run formatter, run tests | Yes |
| 2: Reversible development | Commit to agent branch, create local report, download public papers to quarantine | Yes, logged |
| 3: External/reputational | Push branch, open PR, post an issue/comment, send email/message, submit web form | Approval required |
| 4: Sensitive data | Access personal files, password manager, private tokens, customer data, financial records | Denied by default; explicit one-time approval and narrow secret injection |
| 5: Destructive/system | Delete non-workspace data, install system software, modify `launchd`, firewall, users, disk settings, `sudo`, security configuration | Manual only |
| 6: Money/legal/irreversible | Purchases, cloud provisioning with billing, package publish, production deployment, contracts, financial transactions | Manual only |

### Command-risk policy

Block by default, not by simplistic string matching alone: `sudo`, `su`, privilege escalation; `rm -rf` outside disposable sandboxes; disk formatting, partitioning, APFS manipulation; `launchctl` system-level changes; shell profile changes, SSH config changes, Keychain access; network scanning, port scanning, packet capture; firewall/VPN/proxy modifications; commands that use untrusted shell interpolation; `curl | sh`, remote scripts, unsigned installers; package install/update unless the exact package/version is approved; global Git config edits; database destructive queries outside a task-owned disposable DB; Docker privileged mode, host networking, Docker socket mount.

### Runaway protection

Every task needs: max wall-clock time; max steps/tool calls; max model tokens; max retries; max subprocesses; CPU/memory limits where available; max disk growth; maximum network requests/domain budget; maximum cloud spend if cloud fallback exists; lease renewal heartbeat; "no progress" detector; circuit breaker after repeated identical errors; explicit stopping condition.

LiteLLM is not necessary on day one, but it becomes useful if you add cloud escalation because it supports routing/fallback and budget caps, including automatic fallbacks when a configured model budget is exceeded. [docs.litellm](https://docs.litellm.ai/docs/proxy/budget_fallbacks)

### Emergency stop

Provide three independent stop paths:

1. **Dashboard Kill All** — pauses queue, sends termination to workers, removes leases.
2. **Tailscale SSH command** — `agentctl halt --all --lockdown`.
3. **Physical/local command** — disable the `launchd` service and terminate runtime processes.

The emergency stop must not require the LLM, dashboard, or external internet to work.

## Always-on design

### Services

Run these as separate launchd-managed processes under `agentops`:

| Service | Responsibility | Restart behavior |
|---|---|---|
| `agent-supervisor` | queue scan, leases, policy, dispatch, watchdog coordination | `KeepAlive`, restart on failure |
| `agent-dashboard` | local UI/API, status, approvals, task submission | restart on crash |
| `agent-worker-llm` | serial high-value agent execution | restart only after task recovery check |
| `agent-worker-browser` | Playwright research jobs | limited concurrency, recycle browsers |
| `agent-worker-docs` | PDF extraction/indexing | restartable/idempotent |
| `agent-indexer` | repository and corpus indexing | scheduled/event-driven |
| `agent-backup` | SQLite backups, artifact snapshots | schedule nightly |
| `agent-watchdog` | health probes and stale-lease cleanup | independent of supervisor |

### Durable task recovery

Every task record should include: task_id, state, attempt, lease_owner, lease_expiry, checkpoint_artifact, workspace_path, model_policy, tool_policy, started_at, last_heartbeat, last_progress_at, failure_reason, next_retry_at, approval_id.

On restart: Supervisor opens SQLite; finds tasks with expired worker leases; validates workspace state, Git status, and latest artifacts; marks the previous worker attempt as interrupted; either resumes from a checkpoint, creates a verifier/recovery task, retries with backoff, or pauses for human review after bounded failures; never blindly replays a destructive action.

### macOS operational settings

- Configure the Mac mini not to sleep while on power.
- Leave display sleep enabled if desired; display sleep is different from system sleep.
- Use a small UPS if overnight reliability matters.
- Enable FileVault and automatic OS/security updates according to your maintenance window.
- Configure automatic restart after power failure in macOS settings.
- Keep the external SSD on a reliable powered enclosure and avoid bus-powered hubs for the main data drive.
- Log thermal and disk-health alerts.
- Test a hard reboot once before trusting overnight operation.

macOS background security/system updates can install automatically; keep an update policy and test window because an unattended restart can interrupt agent tasks. [support.apple](https://support.apple.com/en-am/101591)

### Watchdog rules

- If dashboard unhealthy: restart dashboard only.
- If LLM server unhealthy: pause LLM tasks, restart model service, preserve task state.
- If model memory pressure persists: unload primary model, halt new model tasks, notify you.
- If browser worker crashes: restart browser profile/container; retry only idempotent navigation/extraction steps.
- If external SSD disappears: pause all write tasks immediately; do not fall back to internal disk silently.
- If database integrity check fails: stop dispatch, restore latest consistent backup, alert you.
- If queue has no progress for a threshold: notify, attach top blocked tasks and logs.

## Remote-control architecture

Use a private tailnet rather than public port forwarding.

```text
Phone / laptop with Tailscale
          | encrypted authenticated tailnet
          v
     Mac mini Tailscale node
          |
   Tailscale Serve
          |
    localhost dashboard
          |
Status / queue / logs / approvals / stop / task submission
```

### Remote capabilities

Your mobile-friendly dashboard should expose: current model loaded and memory status; queue depth and task status; live worker state and last action; task submission templates; approval inbox; artifact previews; research report status; logs and trace links; pause/resume controls; emergency stop; daily cost and cloud-fallback usage; "what changed overnight?" report.

Use Tailscale Serve to proxy the dashboard privately; avoid Funnel/public exposure. A Tailscale configuration example explicitly distinguishes private Serve handling from `AllowFunnel: false`. Tailscale's policy tooling supports fine-grained control over which users/devices can reach the Mac, and current offerings also include audit-oriented SSH access behavior. [tailscale](https://tailscale.com/blog/march-26-product-update)

### Remote SSH

- Enable SSH only for your own Tailscale identity/device group.
- Use Tailscale SSH or conventional SSH constrained through the tailnet.
- Disable password authentication.
- Do not expose port 22 on the public router.
- Separate: your admin SSH; `agentops` service account; no interactive login for agent subprocess identities if possible.

Apple notes that enabling certain remote-management functions via `systemsetup` can require Full Disk Access for the parent process; avoid giving broad Full Disk Access merely to make agent automation easier. [support.apple](https://support.apple.com/en-mn/101653)

## Storage plan

### Internal SSD: 512 GB

Use the internal drive for latency-sensitive, boot-critical, and operational components: macOS and applications; Xcode command-line tools / Homebrew; Docker Desktop runtime and lightweight images; Python/uv environments; Ollama application/runtime; active SQLite database mirror or primary DB; active logs, small caches, launchd files; current critical source checkout cache; 100–150 GB free-space reserve.

Do not fill the internal disk with model libraries, large PDFs, datasets, or long-lived Playwright artifacts. macOS needs working free space for updates, memory pressure/swap behavior, logs, and cache.

### External SSD: 1 TB

Use the external SSD for bulk, replaceable, and portable agent data:

```text
External SSD: /Volumes/AIData
├── models/                  100–300 GB target cap
├── projects/                repositories and worktrees
├── research/corpus/         PDFs, HTML snapshots, source captures
├── research/extracted/      text, OCR outputs, chunks
├── datasets/                raw + processed data
├── state/                   SQLite backups, optional vector store
├── artifacts/               reports, diffs, traces, test results
├── cache/                   model/download/build caches
├── logs/archive/
└── backups/                 encrypted rotating copies
```

### Storage policy

| Data | Drive | Retention |
|---|---|---|
| Model weights | External | Keep only two active models plus one test model |
| Active task DB | Internal primary + external backup, or external primary if it is always mounted | Daily snapshots, WAL-aware backup |
| Repositories | External | Git remote plus local snapshots |
| Active worktrees | External | Delete after merged/archived and artifacts retained |
| Papers/raw web captures | External | Immutable source archive |
| Extracted text/chunks | External | Regenerable but retain with corpus |
| Browser traces/screenshots | External | Retain failures and sampled successes; prune routine traces |
| Logs | Internal recent + external archive | Rotate aggressively |
| Caches | External | Prune automatically |
| Credentials | Internal Keychain/secret service, never external plaintext | Per-task injection only |

### External SSD risks

The external drive becomes a single point of failure if it holds models, projects, database, and evidence. Mitigate it: use a high-quality NVMe enclosure with good thermals; ensure stable connection; avoid surprise dismounts; use encrypted APFS where appropriate; monitor free space and mount state; run daily SQLite backups and periodic `PRAGMA integrity_check`; maintain a second encrypted backup drive or offsite encrypted backup; make all task writes fail closed when the volume is unavailable.

## Cost strategy

### Fully local/free core

Ollama or MLX/llama.cpp; Qwen open-weight local models where licensing permits your use; OpenHands SDK/local deployment; LangGraph/community libraries; Python, SQLite, FTS5, Git; Playwright; PyMuPDF, Pandas/Polars, DuckDB; Tailscale free/personal tier if suitable for your device count and needs; Docker Desktop may have licensing considerations depending on use, assess current terms for your scenario.

### Optional paid components worth considering

| Use case | Why a paid/cloud option can be justified | Control |
|---|---|---|
| Difficult coding task | Frontier models may finish a complicated refactor/debug task faster than repeated local attempts | Explicit escalation approval, code-redaction policy, dollar cap |
| High-stakes research synthesis | Better reasoning and citation discipline may be worthwhile after evidence is collected locally | Send only curated evidence bundle, not raw private corpus |
| Large OCR/vision tasks | Cloud models can help with difficult scanned documents/figures | Per-document opt-in |
| Backup | Encrypted offsite backup protects against SSD loss | Client-side encryption |
| Remote notifications | Push/email service | No sensitive content in notification body |

Do not make cloud a mandatory dependency. The local system should plan, code, test, index, extract PDFs, search its own corpus, produce reports, and operate its queue with no cloud API.

If you add cloud models, put them behind LiteLLM or a similarly controlled gateway, with: per-project allowlist; input redaction; daily/monthly budget; model-specific caps; approval-required first use per task; complete request metadata audit; local fallback when budget is exhausted. [docs.litellm](https://docs.litellm.ai/docs/proxy/budget_fallbacks)

## Implementation roadmap

The commands below are intentionally conservative. Verify current package names, model identifiers, and version compatibility at installation time; the platform moves faster than this architecture should.

### Phase 1: Minimal local foundation

**Goal:** one local model, local task database, a manually triggered task runner, and no broad computer control.

```bash
xcode-select --install
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install git jq sqlite uv just tmux htop btop gh
brew install --cask ollama
brew install --cask tailscale
brew install --cask docker
```

Create the dedicated account manually in macOS System Settings: User `agentops`, Type Standard user, Admin privileges No.

```bash
sudo mkdir -p /Volumes/AIData/agent-lab
sudo chown -R agentops:staff /Volumes/AIData/agent-lab
```

As `agentops`:

```bash
mkdir -p /Volumes/AIData/agent-lab/{models,projects,research/{corpus,extracted,evidence,reports},state,workspaces,logs,cache,backups}
mkdir -p ~/agent-control/{app,config,policies,launchd,scripts}
cd ~/agent-control
uv init
uv add fastapi uvicorn pydantic sqlalchemy aiosqlite typer rich httpx pyyaml
```

```bash
ollama --version
ollama pull qwen3-coder:30b-a3b
ollama pull qwen3:8b
ollama list
```

Model tags may differ by release. If the 30B tag/quant is unavailable or causes memory pressure, start with the available 8B model and defer the primary model decision until benchmarking.

`~/agent-control/config/settings.yaml`:

```yaml
storage_root: /Volumes/AIData/agent-lab
database_url: sqlite:////Volumes/AIData/agent-lab/state/agent.db

models:
  utility:
    provider: ollama
    model: qwen3:8b
    max_context_tokens: 8192
    max_concurrent_requests: 1
  primary:
    provider: ollama
    model: qwen3-coder:30b-a3b
    max_context_tokens: 16384
    max_concurrent_requests: 1

limits:
  max_task_minutes: 90
  max_model_steps: 30
  max_retries: 2
  max_browser_workers: 2
  max_pdf_workers: 1
  disk_free_floor_gb: 100

security:
  workspace_root: /Volumes/AIData/agent-lab/projects
  network_mode: allowlisted
  cloud_models_enabled: false
  require_approval_for:
    - external_write
    - remote_git_push
    - sensitive_data
    - destructive_action
    - system_change
```

Test: run a simple local prompt; insert a dummy task into SQLite; run a test worker that writes only to `/Volumes/AIData/agent-lab/workspaces/disposable`; confirm it cannot read your personal user home directory; reboot the Mac and verify no important state is lost.

Common failures: external SSD not mounted (worker pauses, does not write elsewhere); Ollama model too large (reduce context first, then use the 8B utility model); Docker inaccessible under `agentops` (do not solve by making `agentops` admin without understanding the privilege boundary); Homebrew location/path mismatch (explicitly set environment paths in launchd configuration).

Rollback: stop Ollama; remove the test model; disable the test service; delete only the disposable workspace directory; preserve SQLite logs for postmortem.

### Phase 2: Autonomous coding

**Goal:** constrained coding within per-task worktrees.

```bash
brew install ripgrep fd tree gh
uv add gitpython pytest ruff
```

Install OpenHands only after Docker and your local model endpoint are tested. Prefer its current documented installation path rather than relying on a stale copy/paste command. Use local Docker sandboxes, never an agent process operating directly in your personal account. OpenHands documentation distinguishes local Docker workspaces from cloud workspaces and makes clear that remote/cloud environments require provider credentials; for your goals, start with local Docker workspace execution. [docs.openhands](https://docs.openhands.dev/sdk/guides/agent-server/cloud-workspace)

Per-project policy `.agent/project-policy.yaml`:

```yaml
allowed_paths: [src/, tests/, docs/, scripts/]
blocked_paths: [.env, secrets/, production/]
commands:
  allow: [git status, git diff, git checkout -b, git worktree add, pytest, ruff, npm test, npm run lint, make test]
  approval_required: [git push, gh pr create, npm publish, terraform apply, docker build, any networked deployment]
git:
  protected_branches: [main, master, release]
```

Test: give the agent a small issue with a known expected patch; require it to create a worktree, write a plan, implement, run tests, create a commit on an `agent/` branch, produce a diff and test report; ensure it cannot merge or push without an approval record; kill the worker mid-task and verify task recovery sees the worktree and asks whether to resume or restart.

Rollback: `git worktree remove /path/to/worktree`; `git branch -D agent/task-xxxx`. Do not delete the canonical repository.

### Phase 3: Research pipeline

```bash
uv add playwright pymupdf pydantic pandas polars duckdb trafilatura beautifulsoup4 lxml
uv run playwright install chromium
```

Tables: sources, source_versions, documents, document_chunks, claims, claim_evidence, contradictions, research_runs, reports.

Minimum `claim_evidence` fields: claim_id, source_id, document_id, chunk_id, quote_text, page_or_section, retrieved_at, support_type, confidence, verification_status.

Test: research a narrow technical question with 5–10 sources. Passes only if every factual paragraph has source references; at least one contradiction/limitation search was performed; PDFs retain page references; the report can be regenerated from the stored evidence ledger; a verifier catches intentionally inserted fake citations.

### Phase 4: Persistent memory

Markdown decisions under each project; SQLite event store; SQLite FTS5 over task summaries, decisions, research chunks, extracted docs, agent reports; repository maps generated periodically.

Only then add embeddings:

```bash
uv add qdrant-client sentence-transformers
```

Use Qdrant in persistent local mode at `/Volumes/AIData/agent-lab/state/qdrant/`. Keep FTS5 and vector search together; never replace lexical search entirely.

### Phase 5: Multi-agent orchestration

```bash
uv add langgraph langchain-core
```

Worker classes: planner, repository_mapper, implementation_agent, test_runner, debugger, code_reviewer, documentation_writer, research_discovery, source_verifier, pdf_extractor, claim_checker, synthesis_writer, task_recovery.

Scheduler reserves resources, e.g. primary_llm = 1 permit; utility_llm = 1 permit; browser = 2 permits; pdf_cpu = 1 permit; heavy_test = 1 permit. A task cannot begin unless it holds its required permits.

Test: queue 50 synthetic logical tasks (35 summarization/classification; 10 repository-map; 3 browser research; 2 coding). Verify only permitted workers run; primary LLM stays at one concurrent request; low-risk non-LLM tasks progress while LLM is busy; state persists after a supervisor restart; failed task retries do not exceed the configured budget.

### Phase 6: 24/7 operation

Create user-level launchd plists under `~/Library/LaunchAgents/`. Example:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>local.agent.supervisor</string>
  <key>ProgramArguments</key>
  <array>
    <string>/Users/agentops/.local/bin/uv</string>
    <string>run</string>
    <string>python</string>
    <string>/Users/agentops/agent-control/app/supervisor.py</string>
  </array>
  <key>WorkingDirectory</key>
  <string>/Users/agentops/agent-control</string>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>ThrottleInterval</key>
  <integer>15</integer>
  <key>StandardOutPath</key>
  <string>/Volumes/AIData/agent-lab/logs/supervisor.out.log</string>
  <key>StandardErrorPath</key>
  <string>/Volumes/AIData/agent-lab/logs/supervisor.err.log</string>
</dict>
</plist>
```

```bash
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/local.agent.supervisor.plist
launchctl print gui/$(id -u)/local.agent.supervisor
```

Test power-loss recovery and hard reboot before allowing unattended overnight work.

### Phase 7: Remote access

Install and authenticate Tailscale on Mac mini, phone, laptop. Then: name the Mac mini node clearly, e.g. `agent-lab`; create tailnet ACLs/grants that permit only your identities/devices; serve dashboard from localhost using Tailscale Serve; leave Funnel disabled; use HTTPS via Tailscale; require dashboard authentication even inside the tailnet; make the dashboard session expire; expose no model server endpoint remotely.

Tailscale's private-network and policy model is the reason to prefer it over router port forwarding; its current policy tools support controlled reachability among nodes/users. [tailscale](https://tailscale.com/blog/visual-editor-ga)

### Phase 8: Optimization

Only after 2–4 weeks of logs: benchmark Ollama versus direct MLX runtime using utility model, primary model, 8K/16K/32K prompt conditions, code generation, repository retrieval, model load/unload behavior. Record time-to-first-token; tokens/sec; memory pressure; swap; task wall time; test pass rate; task completion/retry rates. Decide whether to keep Ollama, move primary serving to MLX, introduce MLX continuous batching, reduce model/context, or add cloud escalation for only specific task categories.

The emerging vLLM-MLX ecosystem is interesting for batching on Apple hardware, with published results claiming continuous batching benefits, but it is an optimization phase—not a prerequisite for a stable autonomous workstation. [arxiv](https://arxiv.org/abs/2601.19139)

## What not to install

| Technology or pattern | Why not for this machine now |
|---|---|
| Kubernetes, k3s, Nomad | Operational complexity; no meaningful benefit for one Mac and a few workers |
| Redis + Celery + Postgres | SQLite queue/state is enough initially; adds daemons and recovery paths |
| Multiple vector databases | Redundant; start with SQLite FTS5 |
| Neo4j/graph DB | Premature; project decisions and evidence are better represented in Markdown/SQLite first |
| A 70B+ dense model as default | It may fit only barely or require excessive quantization/context compromise; poor work-per-hour |
| 100 simultaneous LLM agents | Will thrash unified memory and duplicate work |
| General GUI/computer-control agent with Accessibility permissions over your personal account | Excessive authority and high privacy/security risk |
| Public Ollama/OpenAI-compatible API endpoint | Unnecessary attack surface |
| Exposed Docker socket | Equivalent to broad host control in many configurations |
| Browser profile containing personal sessions/cookies | The agent inherits your identity and access |
| "Auto approve everything overnight" | Destroys the main security boundary |
| Unreviewed MCP servers | MCP is a protocol, not a safety guarantee; every server is executable authority |
| An opaque "memory" product as source of truth | Difficult to audit, back up, migrate, or correct |
| Cloud-only agent platform | Violates local-first resilience and privacy requirements |
| Docker privileged containers / host networking | Weakens the isolation you are trying to create |

## Future upgrade path

| Upgrade | What changes |
|---|---|
| 64 GB unified memory | Run primary 30B model with much healthier KV cache; consider one 14B utility model resident; 2 modest concurrent model requests may become viable after testing |
| 96 GB unified memory | Consider a 32B dense/reasoning model or higher quantization; run primary plus utility concurrently; larger document/vision tasks become more comfortable |
| 128 GB+ unified memory | Larger 70B-class quantized models become plausible; multi-model routing becomes genuinely useful; batching can matter more; upgrade vector/document services if corpus grows |
| Dedicated NVIDIA GPU server | Move high-throughput serving to vLLM/SGLang-class CUDA stack; keep Mac as secure control plane, dashboard, local/private data workstation, and low-latency fallback |
| Separate Linux host | Put inference and disposable sandboxes there; keep secrets, personal data, scheduler authority, and approval service on the Mac |
| Multiple machines | Introduce a real remote queue/broker only then; use signed worker registration, per-node capabilities, and separate data zones |
| Large research corpus | Add GROBID pipeline, object storage, Qdrant server or equivalent, hybrid retrieval/reranking, and archival source snapshots |
| Production/deployment automation | Add a dedicated staging environment; never let development agents deploy directly from the personal Mac |

## Final recommendation

Build the system in this order:

1. **Dedicated `agentops` user + external SSD structure + Ollama + two local models.**
2. **SQLite-backed task supervisor with strict limits and no broad filesystem access.**
3. **Git-worktree coding loop using sandboxed OpenHands execution.**
4. **Evidence-first research pipeline with Playwright, source ledger, PDF extraction, and citation verification.**
5. **SQLite/FTS5 memory, then vector retrieval only when needed.**
6. **Queue-based coordinator/worker system with one primary LLM permit.**
7. **`launchd` supervision, watchdogs, recovery, backups, and overnight scheduling.**
8. **Tailscale private remote dashboard with approvals and an emergency stop.**
9. **Only then benchmark MLX-native serving, advanced model routing, and carefully bounded cloud escalation.**

That architecture gives you genuine autonomous operation—planning, delegation, execution, verification, correction, documentation, and continuation—while keeping the critical facts of your environment under deterministic control rather than delegating safety and reliability to a language model.

## Model's own cited sources

Inline citations (as rendered by Perplexity; some are aggregator/mirror URLs, not always the primary):

- https://ui.adsabs.harvard.edu/abs/2025arXiv251105502R/abstract — Apple-Silicon LLM runtime comparison (MLX / MLC-LLM / llama.cpp / Ollama / PyTorch MPS)
- https://arxiv.org/abs/2511.03690 — OpenHands Software Agent SDK
- https://docs.langchain.com/oss/python/langchain/overview — LangGraph / LangChain durable execution
- https://docs.openalex.org/how-to-use-the-api/xpac — OpenAlex data expansion (DataCite + repositories)
- https://sqlite.org//fts5.html — SQLite FTS5
- https://tailscale.com/blog/march-26-product-update — Tailscale policy / SSH
- https://tailscale.com/blog/visual-editor-ga — Tailscale policy editor
- https://www.orcarouter.ai/blog/best-local-llm-for-coding — Qwen3-Coder-30B-A3B sizing (~17–20 GB Q4, 30.5B total / ~3.3B active)
- https://localaimaster.com/blog/qwen-3-local-setup-guide — Qwen3 local setup
- https://www.therundown.ai/tools/devstral-2 — Devstral Small 2 (24B, 256K ctx)
- https://arxiv.org/abs/2601.19139 — MLX continuous batching / vLLM-MLX
- https://docs.openhands.dev/sdk/guides/convo-async — OpenHands SDK async conversations
- https://docs.openhands.dev/sdk/guides/agent-server/cloud-workspace — OpenHands local vs cloud workspace
- https://docs.litellm.ai/docs/proxy/budget_fallbacks — LiteLLM budget fallbacks
- https://thinksys.com/qa-testing/playwright-features/ — Playwright locators / traces
- https://support.apple.com/en-am/101591 — macOS automatic updates
- https://support.apple.com/en-mn/101653 — macOS remote management / Full Disk Access

## Reviewer notes

### Trust — MEDIUM-HIGH. Most security-thorough and most epistemically-honest response so far.
- Only non-Claude response that **cited sources** (the prompt asked for them). Citations are real URLs; a few are aggregator mirrors (ui.adsabs for an arXiv paper) or SEO-blog pages (orcarouter, localaimaster, therundown) rather than primary — RQ5: resolve yes, primary partially.
- **Explicitly refused to fake M6 numbers**: "an 'M6 Mac mini' is future hardware relative to many published model benchmarks ... I use conservative sizing rather than pretending there are exact M6 throughput measurements." This is the correct move and no other response made it this cleanly.
- Two arXiv IDs look post-dated/implausible (`2511.03690`, `2601.19139` = Nov 2025 / Jan 2026 numbering). Treat the *existence* of those exact papers as unverified; the claims attributed to them (OpenHands SDK, MLX continuous batching) are real topics. Minor RQ5 flag, not fabrication of a tool.

### Recency (RQ4) — good, conservative
- Real current tools throughout: Ollama(+MLX path), MLX, llama.cpp, OpenHands SDK, LangGraph, Playwright, OpenAlex/Crossref/GROBID/PyMuPDF, Qdrant (embedded), Tailscale Serve, LiteLLM, `uv`, `just`.
- Did NOT chase the 2026 edge (no Claude Code / Agent SDK / Goose / llama-swap / sqlite-vec / Docling / Apple `container`). Picks a proven 2025-era stack and says "benchmark before trusting". Defensible given the free-tier/retrieval constraints.
- Uses Qwen3-Coder-30B-A3B (real) and correctly hedges the 256K context as "a capability ceiling, not a productivity recommendation".

### Hallucination (RQ2) — none material
- No fabricated tools or models. Every tool named exists. Model picks are real and conservatively hedged ("only if measured headroom is acceptable").
- The only soft spots are the two arXiv IDs and the aggregator citations — evidence-quality issues, not fabrication.

### Constraint reasoning (RQ3) — strongest of all responses
- Treats 32 GB as a shared pool, not VRAM; reserves 4–6 GB filesystem-cache headroom explicitly and says "do not allocate this to models".
- Hard rules: one primary inference request at a time; **no second large model concurrently resident**; initial context cap 16K, normal max 32K, exceptional 48–64K only with other programs stopped.
- `memory_budget.py --preset perplexity`: coder (~17) + optional 4–8B helper + browser + OS → fits at 16K, tight/over at 32K with the helper — matches its own "practical working allocation ~26–28 GB, 4–6 GB margin".

### Internal consistency (RQ6) — clean
- No contradiction found. "What not to install" (Redis/Celery/Postgres, Docker socket, Neo4j, k8s, 100 LLMs, GUI-control agent, public API, auto-approve overnight) is consistent with the body. Recommends Docker workspaces AND warns against the Docker socket / privileged mode — that is a coherent position, not a contradiction.

### Agreements vs the anchor (Claude)
- MLX path for performance, Ollama to start; llama.cpp as diagnostic only.
- Qwen3-Coder-30B-A3B as the one heavy worker; 4–8B utility model; ~1 heavy inference slot.
- Custom thin Python supervisor + SQLite queue + leases; NOT CrewAI/AutoGen as backbone.
- Coordinator/worker (supervisor) topology, explicitly NOT swarm.
- Evidence-first research pipeline; "model never cites from memory"; contradiction agent mandatory; PyMuPDF/GROBID deterministic-first.
- SQLite + FTS5 + Markdown/Git first; Qdrant later; NO Neo4j/graph DB to start.
- Dedicated non-admin user (`agentops`); per-task git worktrees; per-task short-lived secrets, never mount `.env`/Keychain/SSH; `pfctl`-style egress allowlist; 3 independent emergency-stop paths; runaway limits.
- Tailscale-only, bind model server to 127.0.0.1, dashboard via Tailscale Serve, Funnel off.
- launchd + watchdog + lease-expiry recovery; "fail closed if external SSD disappears".
- Models on internal for load speed / archive on external; ~100–150 GB internal free reserve.
- Optional cloud behind LiteLLM with budget caps; system fully useful with $0 cloud.

### Divergences vs the anchor
| Axis | Perplexity | Claude (anchor) |
|---|---|---|
| Orchestration substrate | LangGraph + SQLite (durable state machine) | Claude Agent SDK + thin custom; LangGraph only "in reserve" |
| Coding harness | OpenHands SDK (local Docker workspaces) | Claude Code + Goose |
| Sandbox | dedicated user + Docker workspaces (+ "MicroVM where proven") | dedicated user + Apple `container` / Colima |
| Vector store (later) | Qdrant (embedded/local) | sqlite-vec |
| Model router | direct endpoint + policy fn; LiteLLM only if cloud added | ~80-line rule table |
| 2026-edge tooling | deliberately avoided (proven stack + benchmark-first) | adopted (llama-swap, Docling, Remote Control, etc.) |
| Sources | ~17 (real, some aggregator) | ~97 (mostly primary) |
| Storage root | external SSD `/Volumes/AIData` as the workspace root (accepts SSD as SPOF, mitigates hard) | internal for DBs + hot models, external for churn |
