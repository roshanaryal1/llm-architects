---
ai_name: Grok 4
model_version_id: "xAI Grok, free tier (grok.com / X). User labelled 'xai'. Exact build (Grok 4 / 4-fast / 4-heavy) not disclosed in-answer."
provider: xAI
interface: web app (grok.com or X, free tier)
browsing_enabled: unknown — states "Research (as of late August 2026) prioritizes evidence from primary sources, benchmarks, model cards, GitHub activity" but cites NOTHING (no URLs, no inline attributions). M6 facts are correct, so either browsed silently or has a current cutoff.
knowledge_cutoff: unknown; M6 specifics are correct (170 GB/s, correct core layout)
prompt_version: v1
date_run: 2026-08-31
run_by: roshanaryal1
notes_on_run: >
  Compact, well-organised answer: a research-findings preamble, the A-K deliverables, a phased
  roadmap. Emitted every lettered deliverable. Did not produce the requested header line or a
  Sources list.
trust_rating: MEDIUM — engaged the real M6 spec correctly (unlike meta-llama-4, which got bandwidth wrong) and the primary picks are all real and match the cross-model consensus, but 0 sources and it casually cites three fabricated model families (`rapid-mlx`, `Gemma 4 31B`, `GLM-4.7-Flash`) in its alternatives lists. Closes #6.
---

## Raw response

**Recommended architecture for a 24/7 autonomous AI workstation on your M6 Mac mini (32 GB unified memory, 512 GB internal + 1 TB external SSD).**

Research (as of late August 2026) prioritizes evidence from primary sources, benchmarks, model cards, GitHub activity, and hardware-specific tests over popularity. Key findings:

- **M6 hardware**: 2 nm process, 12-core CPU (2 super + 4 P + 6 E), 12-core GPU with Neural Accelerators, dual 16-core Neural Engine, up to 170 GB/s memory bandwidth, max 32 GB unified memory. Strong for on-device LLMs (Apple claims up to 4× AI performance vs M4).

- **Inference**: MLX (Apple's framework) is the performance leader on Apple Silicon for prompt processing and decode on mid-size models, with superior unified-memory efficiency. Ollama (0.19+) uses MLX backend on Mac and is the practical default. llama.cpp remains the most compatible/format-flexible. oMLX and rapid-mlx are strong specialized servers.

- **Models for 32 GB**: Optimize for useful work/hour, not max parameters. Comfortable fits at Q4/Q5 or NVFP4: Qwen3.6/3.8 27B dense (~16–20 GB), Qwen3.6 35B-A3B MoE (3B active, ~20–24 GB), Gemma 4 31B, GLM-4.7-Flash (30B-A3B), Devstral Small 2 (24B). Larger dense 70B+ requires offloading or swapping and is rarely worth it for agent loops.

- **Coding agents**: OpenHands (MIT, event-stream, sandbox, ~72% SWE-bench Verified with strong models) leads for true autonomous long-horizon work. Aider is best for git-native, transparent pair-programming with local models. Cline/OpenCode strong for IDE/terminal. Claude Code/Codex are stronger but proprietary/cloud-oriented.

- **Orchestration**: Logical agents (definitions + queue + worker pool) scale to 100+ without concurrent LLMs. LangGraph for durable stateful graphs; CrewAI for rapid role-based prototypes; custom supervisor preferred for hardware limits.

- **Memory**: Start simple (filesystem + SQLite + sqlite-vec). Hybrid vector + structured later. Avoid heavy graph DBs initially.

- **Computer control**: Terminal/filesystem primary; browser via Playwright or MCP; GUI via thin harnesses (macos-harness, Cua VMs, Seatbelt sandboxes) with strict isolation. Never unrestricted host access.

- **24/7 + remote**: launchd + Tailscale (or WireGuard) + never-sleep + KeepAlive. No public exposure.

### A. Recommended Technology Stack

| Layer | Recommended | Alternatives | Why (evidence-based) |
|-------|-------------|-------------|----------------------|
| Inference engine | Ollama (MLX backend) + mlx-lm for max speed | oMLX, rapid-mlx, llama.cpp/LM Studio | Ollama easiest + now MLX-fast on 32 GB+; mlx-lm for peak single-user throughput |
| Primary models | Qwen3.8/3.6 27B Q4/NVFP4 (coding/planning); Qwen 35B-A3B MoE or Gemma 4 31B (general); small 7–14B for classification/summarization | Devstral Small 2, GLM-4.7-Flash, DeepSeek distill | Best quality/speed fit for 32 GB; strong coding/agent scores |
| Coding harness | OpenHands (autonomous) + Aider (git-native interactive) | Cline, OpenCode, SWE-agent | OpenHands for long unattended loops + sandbox; Aider for transparent Git |
| Orchestration | Custom supervisor (Python + queue) + LangGraph for complex flows | CrewAI (prototypes), Microsoft Agent Framework | Logical agents + worker pool fits 32 GB; LangGraph for durable state |
| Research | GPT-Researcher (local) + Semantic Scholar/arXiv APIs + PDF tools | ResearchPilot, Elicit (cloud), Firecrawl Research Index | Open, citation-aware, local-first; hybrid web + local docs |
| Memory | Filesystem (Markdown/JSON) + SQLite + sqlite-vec | Cognee/Mem0 (later hybrid), Graphiti | Zero extra infra; hybrid later for multi-hop |
| Browser/GUI | Playwright (browser) + macos-harness / Cua (sandboxed GUI) | Safari MCP, Seatbelt profiles | Controlled, isolatable; avoid host GUI by default |
| Always-on | launchd LaunchAgents/Daemons + caffeinate | launchd + watchdog scripts | Native, reliable restart |
| Remote | Tailscale (mesh VPN) + SSH + simple dashboard (FastAPI/Streamlit) | WireGuard, Cloudflare Tunnel (restricted) | Zero public ports; encrypted; easy phone/laptop access |
| Storage | Internal: OS + active models/cache; External: models, repos, data, logs, backups | — | Throughput + reliability considerations |

Completely local/free core. Optional paid: frontier API calls for hard reasoning (temporary), academic APIs if rate-limited.

### B. Complete Architecture

```
User (phone/laptop via Tailscale)
        v
Remote Interface (Tailscale Serve / SSH / lightweight web UI + notifications)
        v
Always-on Supervisor (launchd service, Python)
  - Task queue (SQLite or Redis-lite)
  - Watchdog / crash recovery
  - Resource governor (RAM, concurrent workers, time/token limits)
  - Approval gates + audit log
        v
Agent Orchestrator (logical agents only)
  - Dynamic agent spawning (role, tools, context, model preference)
  - Hierarchical or swarm as needed
  - Model router (local primary; optional cloud fallback)
        v
Worker Pool (1-3 concurrent large-model processes max on 32 GB)
  - Specialized agents (Coder, Researcher, Reviewer, Documenter, Experimenter...)
  - Subagents spawned on demand, executed sequentially or limited-parallel
        v
Local Inference (Ollama/MLX)
        v
Tools (permissioned)
  |-- Terminal (sandboxed / dedicated user)
  |-- Filesystem (workspace isolation)
  |-- Git + worktrees
  |-- Browser (Playwright, isolated profile)
  |-- Python / experiment runner
  |-- Research (web + academic + PDF)
  +-- Documents
        v
Persistent Memory (filesystem + SQLite + sqlite-vec; project + global)
```

Logical agents (100+) are just definitions + queued tasks. Only a small worker pool runs inference. Model swapping or sequential execution is preferred over concurrent large models.

### C. Hardware / Resource Plan (32 GB unified)

Approximate allocation (macOS + overhead ~6–8 GB):

- OS + background + browser/tools: 6–10 GB
- Primary large model (27B Q4 / 35B-A3B NVFP4) + KV cache (32k–64k context): 18–22 GB
- One small model or embeddings: 2–4 GB
- Agent processes + DB + caches: 2–4 GB

**Practical limits**:
- Concurrent large-model workers: 1 (preferred); 2 only with aggressive quantization and short context.
- Small-model / classification workers: 2–4 concurrent.
- Context: 32k–128k practical; longer via summarization or RAG.
- Model swapping: worthwhile for overnight specialized jobs; keep one "always-loaded" daily driver.
- Bottlenecks: memory bandwidth and KV cache growth, not raw FLOPS. Prefill benefits from Neural Accelerators.

Storage:
- Internal 512 GB: macOS, Ollama cache, active workspaces, SQLite DBs, logs.
- External 1 TB (fast SSD preferred): full model library, Git repos, research papers/datasets, embeddings, backups, temporary agent workspaces. Avoid spinning HDDs for active inference.

### D. Agent Architecture (100+ logical without 100 LLMs)

- **Agent definitions**: YAML/JSON or code (role, system prompt, allowed tools, model preference, permissions, max steps/tokens).
- **Task queue**: Persistent (SQLite). Supervisor dequeues, assigns to available worker.
- **Worker pool**: Fixed size (1–3). Each worker loads/runs one model instance.
- **Dynamic subagents**: Orchestrator creates specialized definitions on the fly and enqueues them.
- **Execution modes**: Sequential by default; limited parallel for independent subtasks; hierarchical (coordinator → workers).
- **State**: Checkpoints in memory layer; recovery on restart.
- Throughput maximized by keeping the queue full and models warm, not by concurrent inference.

### E. Model Strategy

| Task | Primary Local Model | Notes |
|------|---------------------|-------|
| Planning / orchestration | Qwen3.8/3.6 27B or 35B-A3B | Strong reasoning + tool use |
| Coding / editing / Git | Qwen3.6 27B or Devstral Small 2 | Highest local coding scores |
| Debugging / tests | Same + smaller for quick checks | Iterate in loop |
| Research / synthesis | Qwen 27B/35B-A3B or Gemma 4 31B | Long context + citation discipline |
| Summarization / classification | 7–14B (Qwen/Gemma/Llama) | Fast, cheap |
| Final synthesis / reports | 27B+ | Quality over speed |
| Embeddings | nomic-embed or similar (local) | sqlite-vec |

Router chooses by task type + current load. Optional temporary cloud (Claude/GPT) for the hardest verification steps only.

### F. 24/7 Architecture

1. System Settings → Energy → Prevent automatic sleeping when display is off; `caffeinate -s` or equivalent.
2. Auto-login (or dedicated service user) if needed for GUI tools.
3. launchd LaunchAgent/Daemon for supervisor:
   - `RunAtLoad` + `KeepAlive`
   - StandardOut/Error paths for logs
   - Restart on crash
4. Supervisor monitors queue, workers, resource usage; restarts failed agents; persists state.
5. Watchdog script (separate launchd) kills runaways (CPU/RAM/time).
6. On reboot: launchd brings everything back; queue is durable.

### G. Remote-Control Architecture

- Install Tailscale on Mac mini + phone/laptop (mesh, encrypted, no public ports).
- SSH over Tailscale for commands/logs.
- Lightweight FastAPI or Streamlit dashboard (bound to Tailscale IP or Serve) for status, queue, approvals, emergency stop.
- Notifications via ntfy.sh, Pushover, or email (local SMTP or Tailscale-relayed).
- Approvals for high-risk actions push to phone.
- Emergency kill: remote command or dashboard button that stops workers and drains queue.

### H. Security Architecture

- **Dedicated macOS user** for agent processes (limited home, no keychain access to personal secrets).
- **Workspace isolation**: Agents operate only inside designated project directories or worktrees; never home or system paths by default.
- **Sandboxing**: Seatbelt profiles / Agent Safehouse / Cua VMs for terminal and GUI; Docker for OpenHands where possible.
- **Secrets**: Never in agent context. Use macOS Keychain with restricted access or external secret store; inject only via supervised tools.
- **Network**: Outbound only via controlled proxy or Tailscale; block sensitive domains if desired.
- **Git safeguards**: Prefer worktrees/branches; require human review for force-push, main, or destructive ops.
- **Approval thresholds**:
  - Fully autonomous: read files, run tests, edit in workspace, research, document, non-destructive Git.
  - Approval required: install packages, network writes outside research, delete large trees, credential use, system changes, financial/sensitive data access.
- **Limits**: Per-task token/time/RAM caps; global concurrent inference cap; audit log of every tool call.
- **Emergency stop**: launchd unload + process kill + queue freeze.
- Audit everything to append-only logs on external drive.

### I. Exact Installation Plan (Phase-oriented roadmap)

**Phase 1 – Minimal working system**
- Update macOS. Install Homebrew.
- `brew install ollama` (or official installer). Pull Qwen3.6/3.8 27B and a small model.
- Install Python 3.12+, git, uv/poetry.
- Simple Python supervisor + SQLite queue that can call Ollama and run a shell command.
- Test: enqueue "list files in /tmp and summarize".
- Directory: `~/ai-lab/{supervisor,queue,memory,workspaces,logs}`. External mount for models/data.
- Rollback: stop services, remove LaunchAgent.

**Phase 2 – Autonomous coding**
- Install OpenHands (Docker or native) pointed at local Ollama.
- Install Aider.
- Wire supervisor to spawn coding tasks with workspace isolation + Git worktrees.
- Test on a throwaway repo: "add feature X, run tests, open PR".
- Common failures: context overflow → add summarization; tool permission denials → tighten profiles.

**Phase 3 – Research agents**
- Install GPT-Researcher (or ResearchPilot) with local LLM + Semantic Scholar/arXiv.
- PDF tools (pymupdf, marker, etc.).
- Add research tool to orchestrator. Enforce citation extraction + verification steps.
- Test: "survey papers on X, produce report with evidence table".

**Phase 4 – Persistent memory**
- SQLite + sqlite-vec for embeddings + FTS. Markdown files for human-readable notes.
- Project-specific + global stores.
- Agents read/write via tools.

**Phase 5 – Multi-agent orchestration**
- Implement logical agent definitions + dynamic spawning.
- LangGraph for complex stateful flows.
- Resource governor.

**Phase 6 – 24/7**
- launchd plists for supervisor + watchdog.
- caffeinate / Energy settings.
- Auto-restart tests (kill process, verify recovery).

**Phase 7 – Remote**
- Tailscale.
- Dashboard + notifications.
- Test from phone.

**Phase 8 – Optimization**
- Model router refinements, speculative decoding if available, SSD caching, better KV management, hybrid memory (Cognee-style).

Test each phase with a known task; keep previous phase as fallback. Log everything.

### J. What NOT to Install

- Full Neo4j / heavy graph DBs early (unnecessary overhead).
- Multiple concurrent large inference servers (OOM risk).
- Unrestricted GUI computer-use on host (security).
- Proprietary locked harnesses as primary (Claude Code etc. as optional cloud accelerators only).
- Complex Kubernetes or multi-node orchestration (overkill for one Mac mini).
- Every trending agent framework simultaneously (redundancy).
- Models > ~35B dense without clear quality gain for your tasks.

### K. Future Upgrade Path

- 64/96/128 GB: keep two large models resident, longer contexts, more concurrent workers, higher-quality quant, larger MoEs.
- Dedicated GPU/server: move heavy inference off Mac mini; keep Mac as orchestrator + lightweight agents.
- Add vector DB or full hybrid memory when corpus grows large.
- Multi-machine: Tailscale mesh + shared queue.

This design maximizes useful autonomous work per hour on exactly your hardware while remaining recoverable, private, and controllable. Start with Phase 1 this week; each subsequent phase builds on a working system. All core components are free/open-source and local-first.

## Model's own cited sources

NONE. The preamble asserts "Research (as of late August 2026) prioritizes evidence from primary
sources, benchmarks, model cards, GitHub activity, and hardware-specific tests" but provides no
URLs and no inline attributions. The M6 hardware facts stated are correct (unlike `meta-llama-4`),
suggesting a current knowledge cutoff or silent retrieval.

## Reviewer notes

> ### CORRECTION 2026-09-01 — the "alt-list fabrications" below are SUPERSEDED
> Web verification (`analysis/verification/tool-model-register.md`): all three alt-list items are
> **real, post-anchor-cutoff releases**:
> - **`rapid-mlx`** — real: `github.com/raullenchai/Rapid-MLX` (ex vLLM-MLX, renamed Mar 2026).
> - **`Gemma 4 31B`** — real: Gemma 4 released 2026-04-02; **31B dense is a real variant** (the
>   "different vendors give different sizes ⇒ confabulation" argument was invalid — 26B, 31B and
>   12B are all real Gemma 4 variants).
> - **`GLM-4.7-Flash (30B-A3B)`** — real: Zhipu, released 2026-01-19, 30B-A3B MoE, MIT. grok's
>   "30B-A3B" label is spec-accurate.
> - `macos-harness`, `Agent Safehouse`, `Cua VMs` — `UNRESOLVED` (grok itself hedged these).
>
> **Net effect:** grok has **no surviving factual defect** — it also states the full M6 spec incl.
> **170 GB/s correctly**. Its only real weakness is 0 sources. The bucket-2 placement rested partly
> on "alt-list fabrications" that don't exist; on the rebuild it sits at the bucket-1/2 boundary,
> held out of bucket 1 only by the missing source apparatus. Text below retained as evidence for
> the RQ2 cutoff-bias finding.

### Trust — MEDIUM. M6-aware and consensus-aligned, but unsourced with minor alt-list fabrications.
- **Engaged the real M6 spec correctly:** "2 nm, 12-core CPU (2 super + 4 P + 6 E), 12-core GPU
  with Neural Accelerators, dual 16-core Neural Engine, up to 170 GB/s, max 32 GB". This is the
  same level of detail as Claude / Mistral / GPT-5 and it got the **bandwidth right (170 GB/s)** —
  the number `meta-llama-4` got wrong ("~300+ GB/s").
- The primary picks are all real and match the cross-model consensus almost exactly.
- But it cites **0 sources** and drops three fabricated model families into its *alternatives*
  lists — see Hallucination.

### Hallucination (RQ2) — minor, confined to alternatives lists; part of a cross-vendor pattern
- **`rapid-mlx`** — listed as a "strong specialized server" and an inference-engine alternative
  ("oMLX, rapid-mlx"). No install command, no fake benchmark table (unlike `meta-llama-4`), just a
  passing mention. **This is the 3rd response across 3 vendors to name `Rapid-MLX`**
  (`deepseek-instant`, `meta-llama-4`, `grok-4`) — a shared hallucination attractor, not a one-off.
- **`Gemma 4 31B`** — used as a general/research model option and a summarization tier. Gemma 4
  does not exist (Gemma 3 is current). **3rd response to invent "Gemma 4"**, and each gives a
  different size: `deepseek-instant` "26B", `meta-llama-4` "12B", `grok-4` "31B" — the classic
  signature of confabulation (the family is invented, so the parameter count is unstable).
- **`GLM-4.7-Flash (30B-A3B)`** — plausible family (GLM-4.x Flash/Air is real) but the "4.7"
  point release and "Flash 30B-A3B" spec are unverified.
- **`macos-harness`, `Agent Safehouse`, `Cua VMs`, `Firecrawl Research Index`, `ResearchPilot`** —
  plausible tool *categories* named without detail; unverified but not load-bearing.
- Real, correct picks: Ollama 0.19+ MLX backend, mlx-lm, oMLX, llama.cpp, LM Studio, Qwen 27B /
  35B-A3B, Devstral Small 2 24B, OpenHands (~72% SWE-bench Verified — plausible), Aider, Cline,
  OpenCode, LangGraph, CrewAI, Microsoft Agent Framework, GPT-Researcher, Semantic Scholar / arXiv,
  pymupdf, marker, sqlite-vec, Cognee, Mem0, Graphiti, Playwright, Seatbelt, launchd, `caffeinate`,
  Tailscale, ntfy.sh, Pushover.

### Constraint reasoning (RQ3) — sound, matches consensus
- macOS overhead 6–10 GB; primary large model + KV (32–64k) 18–22 GB; small model / embeddings
  2–4 GB; agents + DB 2–4 GB. **1 concurrent large-model worker preferred** (2 only with
  aggressive quant + short context); 2–4 small-model workers. Model swapping worthwhile for
  overnight jobs; keep one always-loaded daily driver.
- **Bottleneck named correctly:** "memory bandwidth and KV cache growth, not raw FLOPS".
- `memory_budget.py --preset grok` (27B dense ~18 GB or 35B-A3B ~22 GB, one large + one small,
  32–64k ctx, browser) → tight/over — consistent with its "18–22 GB" primary-model line.

### Recency (RQ4) — M6-current, model-layer partly confabulated
- Correct current facts: M6 spec, Ollama 0.19+ MLX backend, NVFP4 quant, Devstral Small 2,
  OpenHands ~72% SWE-bench, sqlite-vec, LangGraph, GPT-Researcher.
- But `Gemma 4` / `GLM-4.7-Flash` / `rapid-mlx` are not real, and the cloud fallback is left
  generic ("Claude/GPT") — no stale-name trap, but no verifiable current name either.
- Net: better M6 grounding than bucket 2 (`gemini`, `kimi`, `qwen-3.7-plus`), worse source
  discipline than bucket 1. Sits at the bucket-1/bucket-2 boundary; scored **bucket 2** for the
  0-sources + alt-list fabrications.

### Internal consistency (RQ6) — clean
- No self-contradiction. "What NOT to install" (Neo4j-early, multiple concurrent large inference
  servers, unrestricted host GUI, proprietary harnesses as primary, k8s/multi-node, every
  trending framework, dense >35B) is consistent with the body.

### Agreements vs the anchor (Claude)
- MLX perf leader; **Ollama 0.19+ MLX backend as the practical default** + mlx-lm for peak;
  llama.cpp for compat.
- 30B-class model (dense 27B or 35B-A3B MoE) + a 7–14B small tier; **1 concurrent large worker**;
  model swapping worthwhile; keep one daily driver warm.
- 100+ logical agents = YAML/JSON definitions + persistent SQLite queue + fixed 1–3 worker pool;
  dynamic subagent spawning; hierarchical coordinator/worker; sequential-by-default,
  limited-parallel for independent subtasks.
- Custom supervisor + LangGraph for complex flows; NOT CrewAI as the backbone.
- **filesystem + SQLite + `sqlite-vec` first**, hybrid (Cognee/Mem0/Graphiti) later — the
  sqlite-vec camp (now Claude, Gemini, Kimi, Mistral, GPT-5, Meta, Grok).
- Research = GPT-Researcher / local LLM + Semantic Scholar / arXiv + PDF tools; **enforce citation
  extraction + a verification step + an evidence table**.
- Computer control: API/terminal/filesystem first, Playwright for browser, GUI only via a
  sandboxed harness; never unrestricted host access.
- Dedicated macOS user + workspace isolation + Seatbelt/Docker sandbox + Keychain secrets never in
  agent context + git worktrees + explicit autonomous-vs-approval thresholds + per-task limits +
  global concurrent-inference cap + append-only audit log + emergency stop (launchd unload + kill
  + queue freeze).
- launchd `RunAtLoad` + `KeepAlive` + separate watchdog + `caffeinate` / Energy settings; durable
  queue survives reboot.
- Tailscale mesh, no public ports; SSH over Tailscale; FastAPI/Streamlit dashboard bound to the
  tailnet; ntfy/Pushover notifications; phone approvals for high-risk actions.
- Internal SSD = OS + Ollama cache + active workspaces + DBs + logs; external = full model library
  + repos + papers/datasets + embeddings + backups.
- Optional temporary cloud for the hardest verification steps only; $0-local core.

### Divergences vs the anchor
| Axis | Grok 4 | Claude (anchor) |
|---|---|---|
| Inference engine | **Ollama (MLX backend)** as the default + mlx-lm for peak | MLX + llama-swap |
| Primary model | Qwen **27B dense** (or 35B-A3B MoE) — leans dense | Qwen3-Coder-30B-A3B (MoE) |
| Orchestration | custom supervisor + LangGraph | Claude Agent SDK + thin custom |
| Coding harness | OpenHands + Aider | Claude Code + Goose |
| GUI control | names `macos-harness` / `Cua VMs` / `Agent Safehouse` (mostly unverified) | Playwright; computer-use last resort |
| Sources | 0 (asserts "evidence-based" without any) | ~97 URLs |
| Fabrication | 3 in alt-lists (`rapid-mlx`, `Gemma 4 31B`, `GLM-4.7-Flash`) | none |
