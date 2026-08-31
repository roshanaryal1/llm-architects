---
ai_name: ChatGPT (GPT-5.6 Luna, free tier)
model_version_id: "ChatGPT free tier. As of 2026-08-06 the free/Go default is GPT-5.6 Luna (smallest of the GPT-5.6 family: Luna / Terra / Sol). User labelled it 'chatgpt / GPT-5'. Exact build not disclosed in-answer."
provider: OpenAI
interface: web app (ChatGPT, free tier)
browsing_enabled: partial — no consolidated Sources list, but ~20 specific inline factual attributions ("Apple officially announced...", "Qwen reports 75.0 on SWE-bench Verified...", "OpenHands' own docs recommend...", "MLX-LM documentation warns...")
knowledge_cutoff: n/a effectively — recommendations are current 2026 (Qwen3.6-35B-A3B, Pydantic AI durable execution, Exa Agent beta, Letta MemFS, Mem0 2026 benchmark caveats); engaged M6 specifics
prompt_version: v1
date_run: 2026-08-31
run_by: roshanaryal1
notes_on_run: >
  Delivered as an 87-section "Architecture Review" with an executive conclusion, a full stack
  table, per-decision rationale, ASCII diagrams, and a numbered implementation order. Emitted the
  A-K deliverable content (stack table / diagram / resource plan / agent architecture / model
  strategy / 24-7 / remote / security / install / what-not-to-install / upgrade path) but not
  labelled A-K and not a consolidated Sources list. Cites facts inline with specific attributions
  rather than URLs.
trust_rating: HIGH — every named tool is real, current, and correctly described; engaged M6 specifics; strong epistemic discipline (flags benchmarks as capability indicators not throughput; sqlite-vec pre-v1; Exa Agent beta; OpenHands headless auto-approval as a risk); zero fabrications. Weakness: no resolvable Sources list (inline attributions only), closes #5.
---

## Raw response

# Architecture Review: 24/7 Local Autonomous AI Workstation

### Target: Apple M6 Mac mini, 32 GB unified memory, 512 GB internal SSD + 1 TB external SSD

### Evidence cutoff: 31 August 2026

## Executive conclusion

Your machine is unusually well suited to a **small always-on agent server**, but it is not well suited to the architecture most people imagine when they hear "100 AI agents."

The correct design is:

```text
                         PHONE / LAPTOP
                               |
                     Tailscale private network
                               |
                               v
                    +----------------------+
                    | Remote Control UI    |
                    | + approvals + logs   |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | ALWAYS-ON SUPERVISOR |
                    | launchd + watchdog   |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | ORCHESTRATOR         |
                    | Python + Pydantic AI |
                    | persistent SQLite    |
                    +----------+-----------+
                               |
                 +-------------+-------------+
                 v             v             v
            Task Queue    Approval Queue   Event Log
                 |
        +--------+---------+
        |                  |
        v                  v
 Coding worker       Research worker
 OpenHands           custom research pipeline
 sandbox             web + papers + PDFs
        |                  |
        +--------+---------+
                 v
             MODEL ROUTER
                 |
       +---------+---------+
       v                   v
 Qwen3.6-35B-A3B      Qwen3.5-4B
     Q4 MLX             Q4 MLX
       |                   |
       +---------+---------+
                 v
             MLX-LM
            Apple Silicon
                 |
     +-----------+------------+
     v           v            v
 Terminal     Filesystem     Browser
 Git          Python         Playwright
 Documents   Experiments    Research APIs
     |           |            |
     +-----------+------------+
                 |
                 v
        Persistent Memory
       SQLite + FTS5 + vec
                 |
                 v
          External SSD
```

### The stack I would actually build

| Layer                  | Recommended technology                            | Alternatives                 | Why                                                                       |
| ---------------------- | ------------------------------------------------- | ---------------------------- | ------------------------------------------------------------------------- |
| OS                     | macOS on M6                                       | Linux VM                     | Native Apple Silicon gives you the best local inference path              |
| Always-on supervisor   | `launchd`                                         | Docker restart policy        | Native macOS service management                                           |
| Orchestrator           | **Python + Pydantic AI + custom async scheduler** | LangGraph, Temporal          | Maximum control without unnecessary infrastructure                        |
| Persistent queue/state | **SQLite WAL**                                    | PostgreSQL                   | One-machine deployment does not justify Postgres initially                |
| Vector memory          | **sqlite-vec**                                    | pgvector, Chroma             | Keeps relational + vector state in one local DB                           |
| Local inference        | **MLX-LM**                                        | LM Studio, Ollama, llama.cpp | Native Apple Silicon path and OpenAI-compatible server                    |
| Main model             | **Qwen3.6-35B-A3B Q4 MLX**                        | Qwen3.5-27B Q4               | Best current local quality/fit trade-off                                  |
| Small model            | **Qwen3.5-4B Q4**                                 | Qwen3.5-9B Q4                | Cheap routing/classification/summaries                                    |
| Coding execution       | **OpenHands sandbox**                             | Qwen Code                    | Docker isolation is critical for autonomous execution                     |
| Interactive coding     | **Qwen Code**                                     | Claude Code, Aider           | Excellent native subagent/permission model; useful as a human-facing tool |
| Browser                | **Playwright**                                    | browser-use                  | Deterministic browser automation should be preferred over GUI clicking    |
| Paper extraction       | **GROBID + Marker**                               | PyMuPDF                      | Structured papers + robust PDF conversion                                 |
| Web research           | **Exa Search + Contents**                         | Tavily, Brave                | Excellent semantic search + clean content extraction                      |
| Academic discovery     | **OpenAlex + Semantic Scholar + Crossref**        | Google Scholar scraping      | Structured bibliographic sources                                          |
| Memory                 | **SQLite + FTS5 + sqlite-vec**                    | Letta/Mem0                   | Simple first; migrate later only if needed                                |
| Remote access          | **Tailscale**                                     | WireGuard manually           | Private network, SSH, Serve                                               |
| Remote UI              | FastAPI + lightweight web UI                      | Grafana                      | You need an operator console, not a monitoring platform                   |
| Sandbox                | **Docker**                                        | Lima/Colima/OrbStack         | OpenHands officially recommends Docker sandboxing                         |
| Monitoring             | structured JSON logs + OpenTelemetry              | Sentry                       | Small system, low overhead                                                |
| Alerts                 | local dashboard + optional ntfy/Pushover          | Telegram                     | Keep cloud notifications optional                                         |
| Secrets                | macOS Keychain initially                          | 1Password/Doppler            | Avoid introducing a secrets server on day one                             |

---

# 1. Hardware reality

Apple officially announced the M6 Mac mini on 25 August 2026. The M6 configuration has a 12-core CPU, 12-core GPU, Dual 16-core Neural Engine, up to 32 GB unified memory and up to 170 GB/s memory bandwidth. Apple explicitly positions the machine for on-device AI and agentic workflows.

That means your stated hardware is real and, importantly, **the 32 GB ceiling is the fundamental architectural constraint**.

Your system is not going to fail because the CPU is too slow first. It will fail because macOS + drivers, browser, Docker, database, Python processes, model runtime, model weights and KV/context state all have to coexist in the same unified memory pool.

## My practical memory budget

| Component                      | Target budget |
| ------------------------------ | ------------: |
| macOS + background services    |        5-7 GB |
| Desktop/browser/dev tools      |        2-4 GB |
| Orchestrator/database          |        1-2 GB |
| Docker + sandbox overhead      |        1-2 GB |
| Small model                    |       ~3-4 GB |
| Main model weights/runtime     |     ~20-22 GB |
| Context/KV + transient buffers |       ~2-5 GB |
| Safety margin                  |       ~1-3 GB |

This means the architecture should **not** keep multiple large models loaded.

### Hard recommendation

Run 1 x large-model worker + 1 x small-model worker and treat that as the normal maximum. Not 10 x large workers, and absolutely not 100 x LLM processes. The "100 agents" requirement is solved by **logical concurrency**, not inference concurrency.

---

# 2. Local model strategy

## Best primary model: Qwen3.6-35B-A3B

Qwen3.6-35B-A3B has: 35B total parameters, only 3B activated parameters, 256K native context, support for vision, strong repository-level and agentic coding, explicit agentic coding improvements.

Qwen reports 75.0 on SWE-bench Verified for the model, 51.5 on Terminal-Bench 2.0, 73.4 on another coding baseline shown in its benchmark table, and strong MCP/tool-use results. The benchmark setup matters: these figures use Qwen's own agent scaffolds and large contexts, so they should be treated as model capability indicators rather than predictions of your Mac's throughput.

More importantly for your actual hardware, there is a verified MLX community 4-bit build. Its disk footprint is **20.4 GB**. That is exactly why the MoE model is attractive: you get the reasoning behavior of a much larger model without the compute characteristics of a 35B dense model.

Run: `mlx-community/Qwen3.6-35B-A3B-4bit`

### Why Q4 instead of FP16?

FP16 for 35B would be roughly 35B x 2 bytes ~= 70 GB, which is impossible on your machine. The current MLX Q4 artifact is ~20.4 GB, making it actually usable.

---

# 3. Why I am NOT choosing Qwen3-Coder-Next

Qwen3-Coder-Next has: 80B total parameters, 3B activated, 256K native context, explicit long-horizon coding/agent training, 70.6 SWE-bench Verified in its published evaluation. Qwen specifically describes it as optimized for complex tool use, failure recovery and coding-agent deployment.

But 80B x 4 bits / 8 ~= 40 GB before runtime overhead. That already exceeds the entire physical unified memory of your Mac. So: **excellent model, wrong machine.**

---

# 4. Secondary model

Use: `mlx-community/Qwen3.5-4B-MLX-4bit` (~3 GB). Use it for classification, routing, small summaries, metadata extraction, simple planning, JSON normalization, memory compaction, duplicate detection, task tagging. Do not waste the 35B worker on "Is this task coding or research?", "Summarize these 3 paragraphs.", "Generate a filename.", "Extract the DOI."

---

# 5. Third model: optional

A 9B Q4 model is a reasonable alternative if you later discover the 4B model is too weak. There is a current MLX 4-bit Qwen3.5-9B build for Apple Silicon. But start with 35B main + 4B utility rather than 35B + 9B because the memory margin matters more than marginal summarization quality.

---

# 6. Inference engine

## Winner: MLX-LM

MLX is Apple's native ML framework; MLX-LM provides local LLM generation, quantization and a local HTTP server. The MLX-LM server exposes an OpenAI-like API at `localhost:8080/v1/chat/completions` but its own documentation warns the HTTP server has only basic security controls and is **not recommended as a production internet-facing server**. That is fine. Your architecture should be Internet -> (blocked) -> Tailscale -> Remote UI -> Supervisor -> localhost -> MLX-LM. Never Internet -> :8080 -> MLX-LM.

---

# 7. LM Studio vs MLX-LM vs Ollama vs llama.cpp

### MLX-LM
Best for your actual hardware. Pros: native Apple Silicon, MLX backend, good local model ecosystem, scripting, OpenAI-compatible endpoint, direct Python integration. Cons: server security is minimal; you need your own serving policy; ecosystem smaller than Ollama.

### LM Studio
Best operator-friendly alternative. OpenHands' own current local-LLM documentation recommends LM Studio and explicitly recommends Qwen3.6-35B-A3B as the first local model to try for local software development. Strong administration/testing GUI, but I would still make MLX-LM the underlying inference service in production.

### Ollama
Best compatibility and simplicity. I would not make it the central orchestration boundary because your architecture benefits from controlling model lifecycle yourself.

### llama.cpp
Its Metal backend is enabled for macOS and uses the GPU, and its ecosystem is mature for GGUF inference. Use it as your fallback engine when a model is easier to obtain in GGUF than MLX.

### Decision
Primary MLX-LM / GUI-testing LM Studio / Fallback llama.cpp / Optional Ollama.

---

# 8. Agent-runtime decision

You should not choose one mega-framework and put everything inside it. Use complementary layers.

## Coding execution: OpenHands

OpenHands currently supports local LLMs through LM Studio, Ollama, vLLM and SGLang, and its own docs now recommend Qwen3.6-35B-A3B for local software development. OpenHands recommends its Docker sandbox for local execution because it isolates the agent's command execution from the host and improves reproducibility. Architecture: Orchestrator -> OpenHands worker -> Docker sandbox (repo/worktree, compiler, tests, git, Python), not LLM -> unrestricted host shell.

---

# 9. Qwen Code is also important

Qwen Code now supports actual subagents with separate contexts, specialized prompts, controlled tools, autonomous execution, background execution, forked agents, and configurable permission modes such as plan, auto-edit and yolo. That makes it useful as the interactive expert coding interface. Install both OpenHands (autonomous worker) and Qwen Code (human-directed expert coding console), with different jobs.

---

# 10. Claude Code is the benchmark to beat architecturally

Claude Code's current subagent model supports foreground subagents, background subagents, concurrent sessions, custom subagents, isolated worktree sessions, agent view, permission controls, and can resume previously created agents with their conversation history. Its permission model distinguishes read-only access, shell execution and file modification. You should copy that architectural pattern, not necessarily make Claude Code your core.

---

# 11. Your 100-agent requirement

## Logical agents != model processes

A logical agent is simply: agent_id, role, system_prompt, tool_policy, workspace, memory_scope, task, state - stored in your database. e.g. agent 001 -> Python reviewer, agent 002 -> frontend reviewer, agent 003 -> literature scout, ... agent 100 -> documentation reviewer. These are not 100 neural networks. They are 100 jobs/personas waiting for worker capacity.

---

# 12. Recommended concurrency

Logical agents: 100+. Queued: unlimited-ish, bounded by disk. CPU/background tool tasks: 4-8. Large-model inference: 1 concurrent request. Small-model inference: 1 concurrent request. Maximum total LLM generation: 2. The model router can dynamically decide: Task A -> large worker, Task B -> small worker, Task C -> wait, Task D -> browser-only, Task E -> CPU-only.

---

# 13. Coordinator/worker architecture

Do not use a swarm as your default. A fully connected swarm causes duplicated reasoning, message explosion, inconsistent decisions, difficult cancellation, difficult auditing. Use a hierarchical coordinator/worker model: Supervisor -> Planner -> {coding, research, document, testing, verification} tasks.

---

# 14. Persistent state

I strongly recommend SQLite + WAL + FTS5 + sqlite-vec rather than PostgreSQL initially. `sqlite-vec` currently provides local vector search inside SQLite, supports float/int8/binary vectors, runs on macOS and is intentionally very small; it is still pre-v1, so treat it as an internal component whose API may change. Database `agent.db` with tables such as: agents, tasks, task_dependencies, task_attempts, workspaces, events, approvals, artifacts, memories, memory_links, documents, chunks, embeddings, research_sources, research_claims, claim_evidence, experiments, metrics, system_health.

---

# 15. Memory architecture

Use four memory tiers. Tier 1 working memory (current task context). Tier 2 episodic memory (what happened). Tier 3 semantic memory (durable facts). Tier 4 artifact memory (actual long-lived files: papers, reports, datasets, source snapshots, code, benchmarks).

---

# 16. Why I am not starting with Mem0 or Letta

Letta's current MemFS architecture uses a Git-backed Markdown memory filesystem, with core memory loaded into the system context and deeper memory discovered on demand; it also now supports background "dreaming" processes for memory consolidation. Mem0's 2026 benchmark report claims large improvements on LoCoMo, LongMemEval and BEAM, although its published numbers are for its managed platform and it explicitly warns open-source users should not expect identical results. Neither is necessary on day one. Your first version should own the memory semantics itself.

---

# 17. Research architecture

Not Search -> LLM -> answer. Instead: Question -> Research plan -> Search -> Source discovery -> Primary-source filtering -> Retrieve source -> Extract evidence -> Store evidence -> Claims -> Cross-check -> Contradiction detection -> Synthesis -> Citation validation -> Report.

---

# 18. Web research

## Exa

Exa's current API can search semantically, search by category, retrieve clean text, extract highlights, retrieve PDFs, crawl subpages, perform deeper multi-step research, and now has an Agent API for asynchronous research workflows, although that agent feature is still explicitly beta. Use Exa Search + Exa Contents. Do not make Exa Agent your entire research stack. Keep control of the research state locally.

---

# 19. Academic research stack

Use OpenAlex, Semantic Scholar, Crossref, arXiv, publisher pages, DOI metadata; then feed discovered documents into GROBID, Marker, PyMuPDF. GROBID/S2ORC-style pipelines convert scientific PDFs into structured bibliographic content; the Allen AI S2ORC tooling uses GROBID to turn scientific papers into structured JSON. Marker can convert PDFs to Markdown/JSON/HTML and supports CPU/MPS execution.

---

# 20. Hallucinated citation prevention

Every claim gets: claim_id, claim_text, source_id, source_url, DOI, publisher, retrieved_at, evidence_excerpt, evidence_location, source_type, confidence, verification_status.

The final writer is instructed: "You may only state a factual claim when: 1. a source exists, 2. evidence exists, 3. the evidence supports the claim, 4. the source identity is preserved. Otherwise label the claim UNVERIFIED." This is much stronger than telling a model "Please don't hallucinate citations."

---

# 21. Contradiction engine

Every important research claim should be classified: SUPPORTED, CONTRADICTED, PARTIALLY_SUPPORTED, INSUFFICIENT_EVIDENCE. If Paper A says a method improves accuracy by 12% and Paper B says 2%, the system must not automatically choose A. Instead: CONTRADICTION DETECTED -> compare dataset, year, model, metric, sample size, evaluation protocol, statistical method -> explain why results differ. That turns the agent into a research system rather than a search summarizer.

---

# 22. Coding architecture

For every coding task: Task -> repo discovery -> repository map -> plan -> create isolated worktree -> implement -> test -> inspect failure -> patch -> test again -> review diff -> commit -> report. Do not let the agent directly mutate your main branch.

---

# 23. Git policy

Allowed: git status, diff, log, checkout, branch, worktree, add, commit. Approval: git push, merge, force-push, rebase shared branch, delete protected branch. For maximum safety: one task = one worktree, under `repo/.worktrees/task-NNN/`.

---

# 24. Computer control

Three capability levels. Level 0 read (read files, search files, inspect git, inspect processes, read logs) - fully autonomous. Level 1 reversible changes (edit code, create files, install project dependencies, run tests, create commits) - autonomous inside an isolated workspace. Level 2 dangerous (rm -rf outside workspace, sudo, credential access, Keychain access, financial apps, password stores, production deployment, git push, cloud infrastructure changes, disk formatting, system configuration, firewall changes, kernel/system extension changes, sending external messages as you) - require approval.

---

# 25. The most important security principle

Do not give the agent read/write access to your entire home directory even though that would technically satisfy "any directory." Instead create `/Volumes/AIData/Projects/` and make that the autonomous workspace root, with per-project subdirs. The user explicitly registers another directory when necessary. The agent's filesystem broker should enforce `resolved_path.startswith(allowed_root)` after resolving symlinks. This prevents a `/workspace/project -> ~/Documents/private` symlink from bypassing the policy.

---

# 26. Docker isolation

OpenHands' Docker sandbox is explicitly recommended as its standard local sandbox and allows specific workspace mounts. Host keeps macOS, supervisor, inference, database, private files; Docker sandbox gets only the source tree, compiler, test runtime, browser, agent process - only the workspace it needs.

---

# 27. Browser control

Prefer Playwright for search, login, navigation, forms, downloads, screenshots, web extraction, rather than computer vision / GUI control for everything. Use GUI/computer-use only when there is no usable DOM/API. The principle: API > DOM > browser automation > GUI vision. Each lower level is harder to validate.

---

# 28. Always-on operation

macOS gives you the right primitive: `launchd`. Your services: launchd -> {ai.supervisor, ai.inference, ai.dashboard, ai.watchdog}. Do not depend on a Terminal window remaining open, or on VS Code being open.

---

# 29. Sleep

Because this is a desktop Mac mini: display can sleep, system must not sleep while the AI service is active. Apple's current support documentation provides the setting to prevent automatic sleeping while on power with the display off. For diagnostics, Apple documents `pmset` and `pmset -g assertions`. Use an AI-service-specific keep-awake policy (AI queue non-empty -> keep system awake; queue empty for long period -> allow normal sleep policy) rather than blindly disabling every power-management feature. For your intended overnight workload, the normal operating mode can simply keep the Mac awake.

---

# 30. Failure recovery

Every task must have a durable state: PENDING, RUNNING, WAITING, FAILED, RETRYING, BLOCKED, SUCCEEDED, CANCELLED. Every worker heartbeat: worker_started, worker_heartbeat, tool_started, tool_finished, worker_failed, worker_restarted. If the Mac crashes: database survives -> RUNNING tasks discovered on startup -> mark them INTERRUPTED -> requeue according to retry policy. Never assume process memory = task state.

---

# 31. Durable execution framework

Pydantic AI currently supports durable execution integrations with Temporal, DBOS, Prefect, Restate, and explicitly supports long-running, asynchronous and human-in-the-loop workflows with fault tolerance. I would not install Temporal on day one. Phase 1: SQLite + durable task records. Phase 2: Pydantic AI. Phase 3: Temporal - only when your workflows become complex enough (multiple machines, long-running distributed workflows, many independent workers, strong replay requirements, complex timers/signals).

---

# 32. Remote access

## Winner: Tailscale

Do not port-forward your dashboard from your home router. Use Phone -> Tailscale -> Mac mini. Tailscale Serve can expose a local web service privately to your tailnet over HTTPS, with access control still applied. For shell access, Tailscale SSH handles authentication/authorization through the tailnet, and its check mode can require reauthentication for higher-risk connections. Tailscale Tailnet Lock provides an additional cryptographic control over which nodes can join the network. From your phone: `https://your-mac.tailnet...` shows system status, active/completed/failed tasks, approvals, logs, CPU, RAM, model, queue, kill switch.

---

# 33. Remote approval system

The dashboard should contain: APPROVE, DENY, CANCEL, PAUSE, RETRY, KILL WORKER, STOP ALL. A request such as "Agent wants to run: sudo rm ..." becomes a PENDING APPROVAL card with Reason / Risk / Command and [DENY] [APPROVE ONCE]. You should never need to log into SSH just to approve a command.

---

# 34. Emergency stop

Two independent kill paths. Soft kill: dashboard STOP ALL sets `system_mode = PAUSED`; no new tasks scheduled. Hard kill: a local command `~/ai-lab/bin/kill-all` that terminates worker processes, OpenHands, browser sessions, inference clients. The watchdog must not immediately restart them. Use `KILL SWITCH ACTIVE` as a durable database state.

---

# 35-38. Storage architecture

512 GB internal = OS/runtime drive (macOS, Homebrew, Python environments, system applications, small configs, active system database, hot cache); keep at least ~120 GB free; do not fill with models. 1 TB external = AI laboratory drive at `/Volumes/AIData/` with models/, projects/{active,archived,worktrees}/, research/{papers,sources,extracted,reports}/, datasets/, experiments/, artifacts/, logs/, backups/, cache/.

Approx 1 TB allocation: Models 250-300 GB, Projects/worktrees 200 GB, Papers/research 120 GB, Datasets/experiments 150 GB, Logs/artifacts 50 GB, Backups/snapshots 80-100 GB, Free space 100+ GB. A continuously attached SSD is storage, not backup. Backup strategy: Mac internal + external AIData + separate backup destination; later local SSD + offline SSD + encrypted cloud. Most important backups: SQLite database, Git repositories, research evidence, agent configurations, memory, task state, reports. Models can be re-downloaded.

---

# 39. Exact project structure

`~/ai-lab/` with supervisor/, orchestrator/{agents,tools,policies,workflows,workers}/, config/{agents,models,permissions,schedules}/, scripts/{start,stop,health,kill-all}.sh, launchd/{com.roshan.ai.supervisor,watchdog,dashboard}.plist, tests/. Data at `/Volumes/AIData/`.

---

# 40. Phase 1 - minimal working system

```bash
brew install git jq ripgrep fd
brew install uv
mkdir -p ~/ai-lab && cd ~/ai-lab
uv venv --python 3.13
source .venv/bin/activate
uv pip install fastapi uvicorn pydantic pydantic-ai aiosqlite httpx psutil
uv tool install mlx-lm
mlx_lm.server --model mlx-community/Qwen3.6-35B-A3B-4bit
curl http://127.0.0.1:8080/v1/chat/completions -H 'Content-Type: application/json' -d '{"messages":[{"role":"user","content":"Explain what a Unix process is in one paragraph."}]}'
```

The current Qwen3.6 MLX model documentation itself uses `uv tool install mlx-lm` and the local MLX server on port 8080.

---

# 41. Install the small model

Download `mlx-community/Qwen3.5-4B-MLX-4bit`. Do not immediately make the router itself LLM-dependent. Use deterministic rules first: coding/architecture/debugging -> 35B; classification/metadata/simple summary -> 4B; browser-only -> no LLM; PDF extraction -> CPU pipeline. Then introduce learned routing later.

---

# 42. Phase 2 - autonomous coding

Install Docker Desktop for Apple Silicon (Docker officially supports it; supported macOS versions are the current release plus the two previous major releases). Install OpenHands using its current Docker setup; its documented local example uses an OpenHands container with an agent-server and mounts `~/.openhands`; OpenHands also supports a current headless mode for automation.

### Important security note

OpenHands headless mode currently runs with automatic approval and explicitly does not offer interactive approval prompts in that mode. Therefore headless OpenHands + Docker sandbox + restricted mount is acceptable. But headless OpenHands + full host filesystem is not acceptable.

---

# 43. Phase 3 - research agents

```bash
uv pip install requests beautifulsoup4 pymupdf lxml
```

Install Marker per its current distribution. Use PyMuPDF first, then Marker when PDF structure is important. Use GROBID for scholarly-paper structure and bibliography extraction. Research worker pipeline: Query -> Search -> OpenAlex/Semantic Scholar/Crossref -> candidate papers -> publisher/arXiv retrieval -> PDF -> GROBID/Marker -> evidence extraction -> claim table -> synthesis.

---

# 44. Phase 4 - memory

```bash
uv pip install sqlite-vec
```

The current project exposes a Python package install through PyPI and supports persistent local vector storage inside SQLite. Store memory.id, memory.kind, memory.scope, memory.text, memory.embedding, memory.created_at, memory.updated_at, memory.source, memory.confidence.

---

# 45. Phase 5 - multi-agent orchestration

Create `agent_definitions/`. Example:

```yaml
name: python-reviewer
model: qwen35-large
tools: [read_file, grep, git_diff, run_tests]
permissions: { write: false, network: false }
```

```yaml
name: research-scout
model: qwen35-large
tools: [web_search, fetch_url, pdf_extract]
permissions: { filesystem: research_workspace, network: research_only }
```

Agent spawning becomes `task = create_task(role="research-scout", objective="Find primary sources for claim X")`. No manual agent configuration is required each time.

---

# 46-47. Phase 6 - 24/7 + watchdog

launchd service `com.roshan.ai.supervisor` (ProgramArguments = venv python + supervisor/main.py, RunAtLoad, KeepAlive, StandardOut/ErrorPath to /Volumes/AIData/logs/). `launchctl bootstrap gui/$(id -u) ~/ai-lab/launchd/com.roshan.ai.supervisor.plist`; `launchctl print gui/$(id -u)/com.roshan.ai.supervisor`.

A watchdog runs separately from the supervisor. It checks: supervisor heartbeat, database responsiveness, model server, disk space, RAM pressure, task queue, Docker, external SSD, network. Policy: supervisor dead < 30 s -> restart; model unavailable -> retry; database locked -> backoff; RAM pressure > threshold -> stop new LLM jobs; external SSD disconnected -> pause all filesystem agents; disk free < 15% -> enter SAFE MODE.

---

# 48-49. Phase 7 - remote control

Install Tailscale, then `tailscale serve 3000` to expose only the dashboard. The current Tailscale documentation says Serve routes a local service to the tailnet and applies the same access controls used for other tailnet services. Do not use Funnel. Enable macOS Remote Login only if you need raw SSH access - Apple explicitly allows remote access through SSH/SFTP and recommends restricting which users may log in. Even better: Tailscale SSH, because Tailscale provides authentication and authorization controls on top.

---

# 50. Phase 8 - optimization

Only after the system is stable: model preload, prompt caching, batching, tool concurrency, context compaction, embedding cache, document deduplication, model swapping, CPU thread tuning, SSD layout, browser pooling. Do not optimize these before the core state/recovery model is correct.

---

# 51. Context-window policy

Qwen3.6 advertises 262K native context and can be extended further. But supported context is not the same as economically sensible context on 32 GB RAM. Practical defaults: simple task 8K, normal coding 16K, complex coding 32K, rare long task 64K. Do not routinely send 200K tokens. Instead: large repository -> repository map -> relevant files -> retrieved chunks -> summaries -> current context.

---

# 52. Model swapping

Yes, but only strategically. idle -> 4B loaded; coding task arrives -> load 35B; coding finishes -> keep 35B warm for a grace period; idle -> optionally unload 35B. Do not continuously swap 4B -> 35B -> 9B -> 35B -> 4B for every trivial task. Model loading has I/O and memory costs.

---

# 53-56. Scheduling / autonomous loop / stopping conditions / runaway protection

Weighted queue: P0 emergency, P1 interactive, P2 deadline-driven, P3 autonomous research, P4 background maintenance, P5 memory consolidation. Overnight hours allow P3/P4/P5; daytime interactive dominates.

Core loop: WAKE -> LOAD STATE -> CHECK QUEUE -> PLAN -> DECOMPOSE -> CREATE TASKS -> SCHEDULE -> EXECUTE -> OBSERVE -> VERIFY -> SUCCESS? (YES -> DOCUMENT -> UPDATE MEMORY -> CREATE FOLLOW-UPS -> CONTINUE; NO -> DIAGNOSE -> RETRY/PATCH -> VERIFY AGAIN).

Every task gets: max_attempts, max_runtime, max_model_tokens, max_cost, max_file_changes, max_command_count, allowed_tools, deadline. Global system limits: RAM/CPU/disk thresholds, LLM token budget, task count, retry count, browser page count, HTTP request rate. RAM > 85% -> stop scheduling new large-model tasks; > 90% -> cancel lowest-priority LLM task; > 95% -> emergency safe mode. Calibrate thresholds on your machine.

---

# 57-58. Observability / research evidence ledger

Every task: task ID, agent ID, worker ID, model, start/end time, tool calls, tokens, files touched, commands, test results, errors, retries, final status. You should be able to answer "Why did agent 47 change this file at 3:12 AM?" with an audit trail. Every published report has a claim -> {source, evidence} tree that lets you regenerate the report later without repeating the research.

---

# 59-60. Agent catalogue / what runs simultaneously

Coding: architect, repo-analyst, implementation-agent, debugger, test-agent, reviewer, security-reviewer, performance-reviewer, documentation-agent, release-agent. Research: research-planner, web-scout, paper-scout, source-verifier, pdf-analyst, citation-verifier, contradiction-detector, statistical-reviewer, synthesis-agent, editor. Operations: queue-manager, health-monitor, memory-manager, artifact-manager, backup-agent, cleanup-agent. The orchestrator dynamically instantiates them. Typical overnight: 100+ logical agents -> task queue -> {large worker (35B), small worker (4B), tool workers (CPU/browser/PDF)}.

---

# 61-63. Cost / cloud / data routing

Fully local/free: macOS, MLX, MLX-LM, Qwen models, OpenHands, Qwen Code, SQLite, sqlite-vec, Playwright, GROBID, Marker, FastAPI, Pydantic AI, Git, Docker, Tailscale client. Optional paid: Exa, premium web search, cloud frontier model fallback, push-notification service, encrypted cloud backup. Do not become ideological about "100% local" - use cloud selectively when local model confidence is low, task is exceptionally difficult, large multimodal reasoning is needed, you need a frontier coding model, or a second-opinion reviewer. Every task gets a privacy_class (PUBLIC / INTERNAL / PRIVATE / HIGHLY_SENSITIVE): PUBLIC -> local or cloud; INTERNAL -> local preferred; PRIVATE -> local only by default; HIGHLY_SENSITIVE -> local only.

---

# 64. What NOT to install

Kubernetes (unnecessary for one Mac). Ray (not a distributed compute cluster). Redis (SQLite is sufficient for the initial queue). Celery (adds infrastructure without solving your main problem). Kafka (massive overkill). Neo4j (no knowledge graph on day one). Milvus / Weaviate (too much operational complexity for this machine). Postgres (excellent but unnecessary initially). Temporal (excellent later, not day one). 10 different agent frameworks - pick one execution framework and one orchestration layer; do not build CrewAI + LangGraph + AutoGen + PydanticAI + OpenHands + Letta + Mem0 into one machine simultaneously. That becomes architecture cosplay.

---

# 65-67. Agent-framework decision

Pydantic AI (reasoning/tool abstraction and structured agent logic) + custom orchestrator (your actual operating system) + OpenHands (coding execution sandbox). Why not LangGraph as the core? It is strong for structured agent graphs and persistence, but your main problem is broader: queue, scheduling, workers, permissions, resource limits, restart, remote control, memory, audit, filesystem policy, model routing. A graph framework alone is not your operating system. Custom orchestration is justified at 100-logical-agent scale because you need application-specific rules anyway (if research_source_count < 3: create more scout tasks; if evidence_conflict: create verification task; if tests_fail_twice: escalate to debugger; if memory_pressure: pause large-model scheduling).

---

# 68. Final model assignments

| Task | Model |
| --- | --- |
| High-level planning | Qwen3.6-35B-A3B |
| Architecture design | Qwen3.6-35B-A3B |
| Coding | Qwen3.6-35B-A3B |
| Debugging | Qwen3.6-35B-A3B |
| Difficult code review | Qwen3.6-35B-A3B |
| Research synthesis | Qwen3.6-35B-A3B |
| Contradiction analysis | Qwen3.6-35B-A3B |
| Final report synthesis | Qwen3.6-35B-A3B |
| Classification | Qwen3.5-4B |
| Metadata extraction | Qwen3.5-4B |
| Simple summarization | Qwen3.5-4B |
| Routing | deterministic first; 4B fallback |
| Embeddings | dedicated small embedding model |
| PDF extraction | CPU/MPS tools first |
| Browser navigation | Playwright |
| Verification | rules + model |

---

# 69-72. Memory strategy / inference policy / router / resource-aware scheduling

Default runtime: Qwen3.6 35B Q4 (~20.4 GB artifact + runtime buffers + context) + Qwen3.5 4B Q4 (~3 GB + runtime). The current MLX Qwen3.6 artifact is explicitly listed at 20.4 GB; the 4B MLX artifact is about 3.0 GB. That plus macOS + Docker + browser + databases + KV/context gets close to the physical ceiling quickly. Hence: one big worker.

Use a semaphore: `large_model_slots = 1`, `small_model_slots = 1`; `await large_model.acquire()` / `finally: large_model.release()`. 100 tasks may exist, but only one consumes the expensive inference path at once.

Router uses rules first: classification -> small; requires_code_execution -> large; requires_deep_reasoning -> large; requires_web_retrieval_only -> no_llm_or_small; requires_final_synthesis -> large. Only later train the router from history. The scheduler inspects RAM/CPU/disk/model-loaded/queue-depth/deadline/priority: `if memory_pressure > HIGH: don't_start_large_task()`.

---

# 73-78. 24/7 state machine / dashboard / project registry / directory abstraction / secrets / tool capability model

Supervisor states: STARTING, HEALTHY, DEGRADED, PAUSED, SAFE_MODE, STOPPING, FAILED. A failed model server should not mean entire system dead - research tasks (web retrieval, PDF processing, database operations, Git analysis) continue while inference recovers.

Dashboard pages: /dashboard, /tasks, /agents, /workers, /projects, /research, /memory, /approvals, /logs, /metrics, /system.

Project registry (YAML): each project has name, root, permissions {read, write, network}. Users think "any directory"; the security layer thinks "approved capability": `capability://workspace/project-a`, `capability://research/current` maps to real paths. Agents never directly choose arbitrary absolute paths.

Never place API keys, SSH private keys, browser cookies, passwords, banking credentials inside `/Volumes/AIData/projects`. The agent receives secrets only as a tool capability: `deploy_to_github()` rather than `cat ~/.ssh/id_ed25519`.

Each tool declares: name, risk, network, requires_approval, filesystem {read, write}. Then an agent cannot "invent" permission.

---

# 79-83. Long-term architecture / upgrade path

Eventually: CONTROL PLANE -> {Task Queue, Memory Store} -> {Coding Workers, Research Workers} + {Semantic Memory, Episodic Memory} -> Model Router -> {Local 35B, Cloud fallback, Specialist models}. This survives a later move to 64/96/128 GB or a GPU server without rewriting the application.

At 64 GB: larger coding model + larger context + small model, or one large + one medium. Still not dozens of large model processes. At 96/128 GB: 80B-class Qwen3-Coder-Next family becomes viable; the important change is larger model + larger context + multiple inference workers = real parallel agent execution. Dedicated GPU/server: Mac mini = control plane (scheduler, dashboard, memory, storage, remote gateway), GPU server = inference plane (model serving, parallel agents, large-context reasoning). That is the cleanest long-term architecture, and when "100 agents" becomes computationally meaningful.

---

# 84-87. The production stack / final diagram / bottom-line

Stack: macOS / launchd / Tailscale / Tailscale Serve + SSH / FastAPI / Python + Pydantic AI / SQLite WAL / sqlite-vec / SQLite FTS5 / MLX-LM / Qwen3.6-35B-A3B-4bit / Qwen3.5-4B-4bit / OpenHands + Docker / Qwen Code / Playwright / Exa Search + Contents + OpenAlex + Semantic Scholar + Crossref + arXiv / PyMuPDF + Marker + GROBID / Git worktrees / structured logs + OpenTelemetry / external SSD + separate backup / macOS Keychain.

Bottom-line: Best model Qwen3.6-35B-A3B Q4 MLX (~20.4 GB artifact, targeted at agentic coding). Best small model Qwen3.5-4B Q4 MLX (~3 GB). Best inference engine MLX-LM. Best coding execution OpenHands inside Docker. Best interactive coding Qwen Code. Best orchestration Custom Python control plane + Pydantic AI. Best initial state store SQLite WAL. Best initial vector layer sqlite-vec. Best remote access Tailscale. Best browser automation Playwright. Best research architecture Exa + OpenAlex/Semantic Scholar/Crossref + GROBID/Marker + local evidence ledger. Best multi-agent architecture 100+ logical agents / 1 large inference worker / 1 small inference worker. Best security model capability-based workspaces + Docker sandbox + approval gates + Tailscale.

## The single most important architectural rule

Do not build 100 autonomous LLMs running forever. Build 100 logical agents -> persistent task graph -> 2 inference workers -> many tool workers -> durable state -> automatic retry -> verification. That is how you get agentic scale without hardware-scale requirements. Your M6 Mac mini is strong enough to become a very capable personal AI laboratory. It is not strong enough to brute-force the problem with massive parallel model inference.

## Recommended implementation order

1. MLX-LM + Qwen3.6
2. SQLite task queue
3. FastAPI supervisor
4. OpenHands + Docker sandbox
5. Git worktree manager
6. Playwright
7. research/evidence pipeline
8. memory
9. launchd + watchdog
10. Tailscale dashboard
11. dynamic logical agents
12. resource-aware model routing
13. advanced optimization

## Model's own cited sources

No consolidated Sources list. The response cites facts inline with **specific attributions** (not URLs), e.g.:

- "Apple officially announced the M6 Mac mini on 25 August 2026 ... 12-core CPU, 12-core GPU, Dual 16-core Neural Engine ... up to 170 GB/s"
- "Qwen reports 75.0 on SWE-bench Verified ... 51.5 on Terminal-Bench 2.0 ... use Qwen's own agent scaffolds"
- "there is a verified MLX community 4-bit build. Its disk footprint is 20.4 GB" (Qwen3.6-35B-A3B); "the 4B MLX artifact is about 3.0 GB"
- "OpenHands' own current local-LLM documentation recommends LM Studio and explicitly recommends Qwen3.6-35B-A3B"
- "OpenHands headless mode currently runs with automatic approval and explicitly does not offer interactive approval prompts in that mode"
- "MLX-LM ... documentation warns that the HTTP server has only basic security controls and is not recommended as a production internet-facing server"
- "Pydantic AI currently supports durable execution integrations with Temporal, DBOS, Prefect, Restate"
- "sqlite-vec ... is still pre-v1"
- "Exa ... now has an Agent API ... still explicitly beta"
- "Letta's current MemFS architecture uses a Git-backed Markdown memory filesystem ... background 'dreaming' processes"
- "Mem0's 2026 benchmark report claims ... LoCoMo, LongMemEval and BEAM ... numbers are for its managed platform"
- "the Allen AI S2ORC tooling uses GROBID"; "Marker ... supports CPU/MPS execution"
- "Tailscale Serve ... applies the same access controls"; "Tailscale SSH ... check mode"; "Tailnet Lock"
- "Apple ... documents pmset and pmset -g assertions"

These are specific and mostly verifiable, but no URL is provided. Scored as **inline-attributed, 0 resolvable sources** for RQ5.

## Reviewer notes

### Trust — HIGH. Top-tier; rivals mistral-large-3 and perplexity, close to the anchor.
- **Every named tool is real, current, and correctly described.** MLX-LM, LM Studio, Ollama, llama.cpp, **Pydantic AI** (with accurate detail on its Temporal/DBOS/Prefect/Restate durable-execution integrations), **OpenHands** (LM Studio/Ollama/vLLM/SGLang support; Docker sandbox; headless = auto-approval), **Qwen Code** (subagents; plan/auto-edit/yolo permission modes), **Exa** (Search/Contents/Agent, Agent flagged beta), OpenAlex/Semantic Scholar/Crossref/arXiv, **GROBID** (S2ORC), **Marker** (MPS), **sqlite-vec** (flagged pre-v1), **Letta MemFS**, **Mem0 2026 benchmark** (managed-platform caveat), Tailscale Serve/SSH/**Tailnet Lock**, `pmset -g assertions`.
- **Strong epistemic discipline** throughout: "treat [benchmark] figures as model capability indicators rather than predictions of your Mac's throughput"; "supported context is not the same as economically sensible context on 32 GB RAM"; "Do not become ideological about '100% local'"; explicitly flags sqlite-vec pre-v1, Exa Agent beta, and OpenHands headless auto-approval as a security risk.
- **Zero fabrications.**

### Recency (RQ4) — current, and engaged M6 specifics
- M6 detail engaged: announced 2026-08-25, 12C CPU / 12C GPU / dual 16-core NE, up to 32 GB / **170 GB/s**, "the 32 GB ceiling is the fundamental architectural constraint". Same tier as claude / mistral / perplexity.
- Current models: **Qwen3.6-35B-A3B** (35B/3B-active/256K/vision) as primary — the same model Mistral lists as its alt and OpenHands' docs recommend; correctly **rejects Qwen3-Coder-Next 80B** ("excellent model, wrong machine", ~40 GB @ 4-bit).
- Current tooling layer: Pydantic AI, Qwen Code, Exa, Letta MemFS, Mem0 2026, sqlite-vec — all 2025-2026.
- No stale cloud-fallback trap: does not name a specific dated cloud model, just "cloud frontier model fallback" / "second-opinion reviewer".

### Hallucination (RQ2) — none
- No invented tools, models, or benchmark figures. Every number is attributed and hedged (e.g. Qwen3.6-35B-A3B "75.0 SWE-bench Verified" attributed to "Qwen reports", with the scaffold caveat).

### Constraint reasoning (RQ3) — strong, matches the anchor
- Memory budget table with a safety margin line; explicit "should not keep multiple large models loaded".
- **1 large + 1 small worker**, enforced with a `large_model_slots = 1` semaphore. 100 logical agents != 100 model processes stated as "the single most important architectural rule".
- Context defaults 8K/16K/32K/64K; repo-map + retrieval instead of 200K dumps.
- `memory_budget.py --weights 20.4 3 --ctx 16000 --browser` → tight/over (its own table admits it "gets close to the physical ceiling surprisingly quickly").
- Resource-aware scheduling: RAM > 85/90/95% → stop-new / cancel-lowest / safe-mode.

### Internal consistency (RQ6) — clean
- No contradiction found. "What NOT to install" (k8s, Ray, Redis, Celery, Kafka, Neo4j, Milvus, Weaviate, Postgres, Temporal-day-one, "10 agent frameworks / architecture cosplay") is consistent with the body, which recommends exactly Pydantic AI + custom orchestrator + OpenHands.

### Distinctive positions vs the anchor
| Axis | GPT-5.6 Luna | Claude (anchor) |
|---|---|---|
| Orchestration substrate | **Pydantic AI** + custom async scheduler (dedicated §66 arguing against LangGraph-as-core) | Claude Agent SDK + thin custom |
| Primary model | **Qwen3.6-35B-A3B** MoE (not Qwen3-Coder-30B-A3B); rejects the 80B Coder-Next | Qwen3-Coder-30B-A3B |
| Interactive coding console | **Qwen Code** (Alibaba's Claude-Code-alike) — only response to name it | Claude Code |
| Coding executor | OpenHands (Docker) — same as perplexity/mistral | Claude Code + Goose |
| Web research | **Exa Search + Contents** (Agent explicitly avoided as beta) | self-hosted SearXNG |
| Memory | SQLite WAL + FTS5 + **sqlite-vec** (with Claude/Gemini/Kimi = 5/10) | sqlite-vec |
| Filesystem security | **`capability://` URI broker** + symlink-resolution enforcement — most explicit after perplexity | dedicated user + workspace jail |
| Data routing | **`privacy_class` per task** (PUBLIC/INTERNAL/PRIVATE/HIGHLY_SENSITIVE) — unique | secrets broker + forbidden paths |
| Sleep | **queue-aware keep-awake** (sleep when queue empty) — unique nuance | pmset sleep 0 + caffeinate |
| Durable execution | Pydantic AI → Temporal only at multi-machine scale | n/a |
| Sources | inline attributions, 0 URLs | ~97 URLs |

### Agreements vs the anchor
- MLX-LM primary (llama.cpp fallback, LM Studio for GUI); one large + one small worker; model swapping strategic not per-task.
- 100+ logical agents = DB rows; hierarchical coordinator/worker, explicitly NOT swarm; dynamic agent instantiation from `agent_definitions/`.
- SQLite WAL task queue + durable states + heartbeats + requeue-INTERRUPTED-on-restart; NOT Redis/Postgres/Celery day one.
- Research = plan → search → primary-source filter → retrieve → extract evidence → store → claims → cross-check → contradiction → synthesis → citation validation → report; claim/source/DOI/evidence_excerpt ledger; "only state a claim when a source + evidence exists and supports it, else UNVERIFIED".
- sqlite-vec; NOT Mem0/Letta day one (own the memory semantics first).
- Playwright; API > DOM > browser automation > GUI vision.
- launchd (supervisor/inference/dashboard/watchdog) + separate watchdog; two independent kill paths.
- Tailscale-only, Tailscale Serve (not Funnel), Tailscale SSH; dashboard-based approvals so you never SSH to approve.
- Dedicated workspace root on the external SSD; capability-scoped filesystem; secrets as tool capabilities not files.
- Internal SSD = OS/runtime (keep ~120 GB free); external = models + projects + research + datasets + logs + backups; "attached SSD is storage, not backup".
- Optional cloud escalation on low local confidence; system fully useful at $0 cloud.
