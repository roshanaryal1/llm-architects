# Research Findings — Autonomous AI Workstation (Claude / Sonnet 5)

> **Purpose of this file:** capture everything this AI response found, with sources, so it can be
> pasted alongside 9 other AI responses to build a comparison + a publishable paper.
> Keep one file per AI (`research-findings-claude.md`, `research-findings-gpt.md`, …).
>
> - **AI:** Claude (claude-sonnet-5), Claude Code
> - **Date of research:** 2026-08-31
> - **Method:** live web search (WebSearch) + targeted fetches; primary sources preferred, secondary roundups cross-checked
> - **Companion deliverable:** architecture artifact — https://claude.ai/code/artifact/6e8265be-66e1-4fce-bb42-973e08819df3
> - **Target hardware:** Apple Mac mini, M6 (base), 32 GB unified memory, 512 GB internal SSD + 1 TB external SSD, always-on

---

## 0. One-line decisions (Claude's recommendation)

| Layer | Recommendation |
|---|---|
| Inference engine | MLX (`mlx-lm`) + `llama-swap` for load/unload; Ollama 0.19+ acceptable simpler substitute |
| Heavy local model | `Qwen3-Coder-30B-A3B` 4-bit MLX |
| Light resident model | `Qwen3-4B-Instruct` 4-bit |
| Mid reasoner | `gpt-oss-20b` MXFP4 |
| Vision | `Qwen3-VL-4B` (30B-A3B for hard docs) |
| Orchestration | Thin custom supervisor + SQLite task queue on top of **Claude Agent SDK** + **Goose** — NOT from scratch, NOT a heavy framework |
| Interactive coding | Claude Code (headless `claude -p` + Remote Control) |
| Local coding worker | Goose (or opencode) + Qwen3-Coder-30B |
| Task queue | SQLite table + asyncio workers (no Redis/Celery) |
| Memory | Markdown files + SQLite now; `sqlite-vec` later; knowledge graph only on proven need |
| Embeddings | `bge-m3` / `nomic-embed-text-v2` via MLX, stored in `sqlite-vec` |
| Web search | SearXNG (self-host) |
| Academic | OpenAlex + arXiv + Crossref + Semantic Scholar APIs |
| PDF/documents | Docling (or Marker) — local, layout + offset preserving |
| Browser | Playwright headless Chromium (computer-use only as last resort) |
| Exec sandbox | Apple `container` (macOS 26) or Colima; non-root, read-only mounts, egress allowlist, timeouts |
| Process supervision | `launchd` KeepAlive + separate watchdog job |
| Sleep prevention | `pmset -a sleep 0 disablesleep 1` + `caffeinate -dimsu` |
| Remote network | Tailscale only (no public ports) |
| Control plane | FastAPI + HTMX dashboard, bound to tailnet IP, bearer token |
| Notifications | ntfy (self-host or random topic) |
| Backups | restic → external SSD + B2/S3 offsite (exclude models) |
| Model router | ~80-line rule table (not a trained router like RouteLLM) |
| Cloud spend | Optional; target < $30/mo Claude API for planning + final synthesis + citation verification; $0 still useful |

---

## 1. Hardware reality — Apple M6 base

**Findings:**
- 2026 Mac mini announced **2026-08-25**, ships **2026-09-22**. Configurable with new **M6** or the earlier **M5 Pro**.
- **M6 chip:** 12-core CPU, 12-core GPU (up from 10/10 on M5). First-ever **dual Neural Engine** (two 16-core engines). Apple's **first 2 nm** processor.
- **Memory bandwidth: ~170 GB/s** (up from 153 GB/s on M5) — modest; this is a base chip, not Pro/Max.
- Base M6 mini configurable **up to 32 GB RAM** and up to 2 TB SSD. Starts **$899**.
- Apple claims vs prior-gen M4 mini: up to 40% faster CPU, up to 4× faster AI tasks, up to 2× GPU, up to 2× storage.

**Interpretation (Claude):**
- Two hard constraints define the whole design:
  1. **Memory capacity is the wall.** After macOS + services (~6–8 GB), ~22–25 GB usable for model weights + KV cache + headless browser + Python workers. A single 30B-class MoE at 4-bit + meaningful context nearly fills that. Cannot hold two large models + a browser at once.
  2. **Memory bandwidth caps token speed.** ~170 GB/s is mid-tier. 30B MoE (~3B active) at 4-bit → real-world ~50–70 tok/s short context, degrading past 32K. Two parallel heavy inferences don't help (share the bus).
- **Implication:** one heavy inference slot, sequential. Parallelism = many logical agents feeding a bounded worker pool + small-model workers + cloud calls running concurrently with the heavy slot. Optimize for useful work/hour, not parameter count.

**Sources:**
- https://www.macrumors.com/2026/08/25/apple-announces-2026-mac-mini/
- https://www.macrumors.com/2026/08/27/m6-chip-to-come-these-two-macs-next/
- https://www.macworld.com/article/2964754/2026-mac-mini-m5-pro-design-specs-release-date.html
- https://9to5mac.com/2026/08/25/apple-announces-new-mac-mini-heres-everything-new/
- https://www.forbes.com/sites/davidphelan/2026/08/25/apple-surprise-launches-new-mac-mini-mac-studio-m6-and-m5-ultra-chips-unexpectedly/

---

## 2. Local inference

### Engine comparison (Apple Silicon, 2026)

**Findings:**
- **MLX vs llama.cpp (Metal):** MLX 30–300% faster on short-to-mid context on 2026 Apple Silicon; one source: "MLX beats llama.cpp by 30–40% on M5 hardware." Ollama switched its Apple-Silicon backend to MLX.
- MLX advantage **erodes past ~40K context**; llama.cpp competitive or ahead there.
- **`mlx-lm` / `mlx_lm.server`** is single-request / pipeline oriented — "not a production inference server." **`llama-server` with `-np`** handles concurrency better.
- **Model swapping:** Ollama hot-swaps (unload current, load next; requests to two models queue). vLLM locks one model, switching = restart. `llama-server` default = one model; **`llama-swap`** adds Ollama-like hot-swap with raw llama.cpp control.
- **vLLM-MLX** introduced continuous batching: +3.4× throughput at 5 concurrent requests. Still limited concurrent-serving maturity on Apple Silicon.
- **Ollama 0.19+** now uses MLX under the hood on Apple Silicon + native hot-swap.
- On **M4 Pro** running `Qwen3-Coder-30B-A3B`: Ollama benchmark 130 tok/s on MLX vs 43 on old llama.cpp backend (3× from a software swap).
- vLLM = CUDA-first, weak Apple Silicon story.

**Recommendation (Claude):** `llama-swap` in front of `mlx_lm.server` (heavy + light) and optionally one `llama-server`. Keep ONE small model resident; swap the big coder in on demand, TTL-unload when idle. If minimizing moving parts: Ollama 0.19+ alone.

### Models to run locally

| Role | Model | Quant / size | Evidence |
|---|---|---|---|
| Heavy coder/agent | `Qwen3-Coder-30B-A3B` | 4-bit MLX; ~16.6 GB @1K ctx, ~25.5 GB @64K (measured on M4 Pro 48GB) | local-llm-coding-eval: 80% code-gen, 77% tool-selection, 80% agent accuracy — "most balanced." 30B MLX port ~79.5% quality @ ~64 tok/s. 256K context capable. MoE ~3B active. |
| Resident light | `Qwen3-4B-Instruct` | 4-bit; ~2.5–3 GB | Small enough to coexist with heavy model; routing/classification/extraction/summarization |
| Mid reasoner | `gpt-oss-20b` (OpenAI, Apache-2.0, released 2025-08-05) | MXFP4 native ~14 GB | 20.9B total / 3.61B active, 131,072 ctx, reasoning-effort control, ~81.7% HumanEval (model card) |
| Vision | `Qwen3-VL-4B` / `Qwen3-VL-30B-A3B-Thinking` | 4-bit ~4 GB / ~17 GB | PDF figures, chart/screenshot grounding |
| Alt coder (16 GB budget) | `Devstral Small 2 24B` (Mistral) | Q4_K_M ~15 GB | Only local coder with a hard agentic number: Mistral reports 68.0% SWE-bench Verified; another source cites 46.8% at 14 GB. |

**Throughput data points (indicative, adjacent hardware):**
- Qwen3-Coder-30B-A3B 4-bit MLX on M4 Pro (48GB): 73.6 tok/s @1K ctx → 13.5 tok/s @64K ctx.
- Same model, MLX vs llama.cpp on M4 Pro: 130 vs 43 tok/s.
- "32 GB M-class Mac runs 30B MoE models at ~100 tok/s" (one optimistic source; treat as ceiling).

**Context guidance (Claude):** default 32K for coder, 64K ceiling local, 256K only for rare cloud-assisted jobs. KV cache = silent memory eater, budget 2–6 GB.

**Do NOT (Claude):** 70B dense / gpt-oss-120b / Llama-70B — don't fit with context headroom, single-digit tok/s stalls the queue. 30B-A3B MoE class = ceiling for this machine.

**By-category picks:**
| | Best overall | Best for this Mac | Best open-source | Best lightweight | Most mature | Cutting edge |
|---|---|---|---|---|---|---|
| Engine | vLLM (N/A on Mac) | MLX + llama-swap | llama.cpp | Ollama | llama.cpp | MLX / vLLM-MLX continuous batching |
| Model | Qwen3-Coder-Next / Kimi-class (too big) | Qwen3-Coder-30B-A3B | gpt-oss-20b | Qwen3-4B | Qwen3-Coder-30B | Qwen3-Coder-Next, GLM-4.x air |

**Sources:**
- https://yage.ai/share/mlx-apple-silicon-en-20260331.html
- https://pub.towardsai.net/apples-mlx-runs-local-llms-3x-faster-than-llama-cpp-until-your-context-hits-40k-715ec441afbb
- https://insiderllm.com/guides/llamacpp-vs-ollama-vs-vllm/
- https://www.promptquorum.com/local-llms/mlx-vs-ollama-vs-llama-cpp-mac
- https://www.besthub.dev/articles/which-framework-wins-for-running-large-models-vllm-vs-llama-cpp-vs-mlx-2026-deep-comparison-0610c28f73fc
- https://contracollective.com/blog/mlx-lm-server-vs-llama-server-apple-silicon-2026
- https://dev.to/sienna/qwen3-coder-next-the-complete-2026-guide-to-running-powerful-ai-coding-agents-locally-1k95
- https://unsloth.ai/docs/models/qwen3.6
- https://www.morphllm.com/best-ollama-models
- https://www.promptquorum.com/local-llms/best-local-llms-for-coding
- https://www.layer3labs.io/guides/best-local-llm-for-coding
- https://localaimaster.com/vram/best-coding-llm-16gb-vram
- https://apxml.com/posts/best-local-llms-apple-silicon-mac
- https://www.sitepoint.com/local-llms-apple-silicon-mac-2026/
- https://codersera.com/blog/apple-silicon-llms-complete-guide-2026/
- https://codersera.com/blog/run-qwen3-vl-30b-a3b-thinking-on-macos-installation-guide/

---

## 3. Agent runtimes / harnesses

**Findings:**
- **Claude Code**: terminal-first, ~1M token context, subagents with **per-subagent model control**, hooks, headless mode (`claude -p` + `--allowedTools`), `/loop`, background tasks (Ctrl+B; `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` to disable), native **Remote Control**, MCP, Agent SDK. SWE-bench Verified ~80.9% with Opus; "#1 in late-July 2026 on Opus 5 + per-subagent model control." **Anthropic-model only** (no local models directly).
- **Goose** (Block → moved to **Linux Foundation Agentic AI Foundation** in 2026): Apache-2.0, free, **runs fully offline with local models**, **MCP-native** (every "extension" = MCP server). ~27K GitHub stars. You control model/provider/data.
- **opencode**: MIT, breadth play — **75+ LLM providers**, local Ollama, same interface.
- **Aider**: Apache-2.0, **git-first** (every change committed, auditable/reversible), model-agnostic, turn-based (weak long autonomous iteration).
- **Cline** (VS Code, ~5M installs), **Roo Code** (multi-mode VS Code) also in the mix.
- **Claude Agent SDK**: exposes the same agent loop, built-in tools, permission system, subagents that power Claude Code, for embedding in products/pipelines. **Model routing: per-subagent model override via `ClaudeAgentOptions`.** Current Anthropic lineup (Aug 2026): **Opus 4.8, Sonnet 4.6, Haiku 4.5**. (Note: some sources also reference "Opus 5"; lineup is in flux.)
- **Multi-agent orchestration frameworks (2026):** Swarms (Python, production), CrewAI ("crew" of specialized agents), **Microsoft Agent Framework 1.0 GA April 2026** (merges Semantic Kernel + AutoGen), OpenAI Agents SDK (handoffs). Self-hosted/local: **Yao Agents** (Go, local execution platform), **RustFox** (Rust, self-hosted Telegram assistant w/ sandboxed tools + MCP + multi-agent).
- **Five orchestration patterns:** fan-out (parallel scatter-gather), pipeline (sequential), debate (multi-perspective critique), **supervisor (hierarchical delegation)**, swarm (dynamic peers). **Supervisor is the 2026 production default** — Claude Code subagents, LangGraph Supervisor, OpenAI Agents SDK handoffs all converge on it.
- **Claude Code parallel-work modes (Anthropic 2026 docs):** subagents, agent view, agent teams, dynamic workflows.
- **Scheduling:** Claude Code **Routines** run scheduled agents in Anthropic's cloud (no local process alive). `/loop` for session-scoped. `cron` + `claude -p` headless for persistent local scheduling. Desktop scheduled tasks survive restarts while the app is open.

**Recommendation (Claude):** multiple complementary systems + thin custom glue. NOT one harness, NOT from-scratch orchestrator.
- Claude Agent SDK = orchestrator process (agent loop, permissions, MCP, subagents, model routing for free)
- Goose = local-model execution harness invoked as worker
- Claude Code (headless + Remote Control) = interactive/hard-coding surface driven from phone
- Your code = ~500–1500 lines: supervisor loop, SQLite queue, model router, approval broker, control-plane API — the hardware-aware scheduler is the thing worth owning
- Why not CrewAI/AutoGen/LangGraph/Swarms as backbone: add abstraction, don't solve scheduling many agents against one memory-bound GPU. Keep LangGraph in reserve for branchy research flows.

**Sources:**
- https://thoughts.jock.pl/p/ai-coding-harness-agents-2026
- https://www.requesty.ai/blog/agentic-coding-tools-compared-2026-claude-code-cursor-codex-aider
- https://pinggy.io/blog/top_cli_based_ai_coding_agents/
- https://www.morphllm.com/comparisons/goose-vs-claude-code
- https://www.lowcode.agency/blog/claude-code-vs-goose
- https://baeseokjae.github.io/posts/goose-ai-agent-review-2026/
- https://mcp.directory/blog/goose-vs-cline-vs-aider-vs-claude-code-vs-opencode-2026
- https://hidekazu-konishi.com/entry/claude_agent_sdk_complete_guide.html
- https://hidekazu-konishi.com/entry/claude_code_subagents_and_orchestration_guide.html
- https://www.digitalapplied.com/blog/multi-agent-orchestration-5-patterns-that-work
- https://www.truefoundry.com/blog/multi-agent-orchestration-frameworks
- https://www.augmentcode.com/tools/open-source-agent-orchestrators
- https://github.com/ARUNAGIRINATHAN-K/awesome-ai-agents-2026
- https://www.mindstudio.ai/blog/claude-code-routines-24-7-agents
- https://www.tembo.io/blog/claude-code-subagents
- https://wmedia.es/en/tips/claude-code-background-agents-map
- https://claudefa.st/blog/guide/development/scheduled-tasks
- https://baeseokjae.github.io/posts/claude-code-async-workflows-guide-2026/

---

## 4. Multi-agent architecture on limited hardware

**Distinctions (Claude):**
- **Agent definition** = file on disk (role, prompt, tools, perm tier, model tier, objective). Costs bytes. Can have 1000.
- **Logical agent** = definition + task + context window, instantiated when its task runs. Lives minutes. 100+ fine because not concurrent.
- **Inference process** = a model loaded in memory doing forward passes. On this Mac: **1 heavy + 1–2 light, ever.** Scarce resource.
- **Worker** = queue consumer: picks task, instantiates logical agent, calls model router, runs tools, writes results. Bounded pool.

**Topology:** hierarchical coordinator/worker (supervisor pattern) — 2026 production default. NOT swarm (peer negotiation wastes tokens, hard to observe on one box).

**Concurrency setting (from resource plan):** `heavy=1, light=2, cloud=4`.

**Throughput model (Claude estimate):** coding task ~4 min on heavy slot → ~15 tasks/hr heavy lane. Light-slot tasks (summaries, classification, lint-fix, file inventory) 2–3 parallel at ~20–40/hr each. Cloud slots add rate-limit/budget-bound capacity. One objective fanned into 60 subtasks completes in the time the *heavy* subset takes; everything else overlaps.

**Dynamic agent creation:** coordinator tool `create_agent_definition(name, role, tools, tier)` writes new `agents/*.md`. Cap (~200 definitions), approval past cap, review in nightly digest.

**Sources:** (same as §3 orchestration sources)

---

## 5. Coding agents

| Capability | Claude Code | Goose | opencode | Aider |
|---|---|---|---|---|
| Repo understanding | Excellent (agentic search, subagents) | Good | Good | Good (repo-map) |
| Local model support | no | yes, first-class | yes (75+ providers) | yes |
| Terminal / test exec | yes | yes | yes | yes |
| Git + worktrees | yes + native worktree flow | yes (manual) | yes | auto-commit every change |
| Long autonomous iteration | Strong (loop, background) | Moderate | Moderate | Weak (turn-based) |
| Subagents / delegation | yes, per-subagent model | recipes/subrecipes | limited | no |
| Sandboxing hooks | hooks + permission modes | MCP allowlist | permissions | minimal |
| Remote control | native mobile app | no | no | no |
| License / cost | proprietary, $20–200/mo | Apache-2.0, free | MIT, free | Apache-2.0, free |

**Benchmarks:** Claude Code + Opus 4.6 → 80.9% SWE-bench Verified (leads). OpenAI Codex ~80% (keeps Terminal-Bench record). Trend: "assign models per task — expensive model to plan, cheaper ones to execute in parallel."

**Recommendation (Claude):** use both.
- Local / bulk / offline: Goose (or opencode) + Qwen3-Coder-30B — refactors, test writing, dep bumps, doc generation, first-pass bug triage.
- Hard / large-repo / your review: Claude Code + Sonnet 4.6 (Opus 4.8 for architecture) — cross-cutting features, subtle debugging, multi-service changes, review of local agent's output.
- Both inside `git worktree` per task under workspace root. Supervisor creates worktree; agent iterates + commits locally; review step gates merge; `git push` to shared remote = always approval.

**Sources:** (same as §3 coding-agent sources) + https://www.kunalganglani.com/blog/aider-vs-claude-code + https://frontman.sh/blog/best-open-source-ai-coding-tools-2026/ + https://nimbalyst.com/blog/best-ai-coding-agents-2026/

---

## 6. Research agents + anti-hallucination

**Findings (from 2026 arXiv papers):**
- Best autonomous research systems still only ~**65% citation quality** — weakest performance axis.
- **Fabricated-citation taxonomy:** total fabrication 66%, partial attribute corruption 27%, identifier hijacking 4%, placeholder hallucination 2%, semantic hallucination 1%.
- **Verification gap:** 87% claim to always verify AI citations, yet 42% copy-paste BibTeX without checking; 77% of reviewers don't thoroughly check references.
- **Grounding chain is attackable:** injecting crafted passages into a retrieval corpus flips RAG answers with ~**90% success**.
- **Mitigation that works:** tool-grounding — bind outputs to retriever-checked API docs. Core principle: **"the model is never allowed to answer from memory — it answers from documents it just retrieved."**
- Recent systems: CiteLLM, BibAgent (traceable miscitation detection).
- GPTZero found 50+ hallucinations in ICLR 2026 submissions.

**Architecture (Claude) — deterministic pipeline, evidence DB is source of truth:**
1. Model never answers from memory — every claim carries `source_id` resolving to a doc fetched this run + exact quoted span.
2. Evidence store (SQLite): `sources(url,title,authors,retrieved_at,sha256)`, `claims(text,source_id,quoted_span,char_offsets)`, `claim_links(claim_a,claim_b,relation ∈ supports/contradicts/refines)`.
3. Separate **reader** (extract claim+quote) and **verifier** (independent agent re-opens source, confirms quote at offset + support). Unverified claims cannot enter report.
4. **Contradiction pass:** pairwise over same-topic claims → populate `claim_links`; report surfaces contradictions explicitly.
5. **Citation resolver:** every DOI checked against Crossref/OpenAlex before entering bibliography — kills identifier-hijack + placeholder hallucination.

**Tools (Claude):**
- Web search: self-hosted **SearXNG** default; paid API (Brave/Exa/Tavily) fallback for freshness.
- Academic: arXiv API, **OpenAlex** (free, 250M+ works), Semantic Scholar Graph API, Crossref, Unpaywall.
- PDF → structured text: **Docling** (IBM) or **Marker** — local, layout/table/equation preserving, char offsets for span citation.
- Reading/extraction: local Qwen3-4B or gpt-oss-20b per chunk. Synthesis: cloud Claude; gpt-oss-20b offline fallback.
- Architecture: fixed pipeline (plan → gather → read/extract → verify → link → synthesize → resolve-citations), NOT a free-roaming swarm. Determinism = auditability.

**Sources:**
- https://arxiv.org/html/2608.05179v1 (Autonomous Research Agents: A Survey of AI Scientists and the Verification Gap)
- https://arxiv.org/html/2604.03173v1 (Detecting and Correcting Reference Hallucinations in Commercial LLMs and Deep Research Agents)
- https://arxiv.org/pdf/2605.08583 (Source or It Didn't Happen: Multi-Agent Framework for Citation Hallucination Detection)
- https://arxiv.org/pdf/2604.03159 (BibTeX Citation Hallucinations in Scientific Publishing Agents)
- https://arxiv.org/html/2509.18970v1 (LLM-based Agents Suffer from Hallucinations: Survey)
- https://gptzero.me/news/iclr-2026/
- https://pickaxe.co/post/ai-research-agent

---

## 7. Persistent memory

**Findings (2026):**
- Production agents need **three layers:** episodic (conversation/run history), semantic (entities + relationships), state (working task state).
- Vector-only retrieval hits a "**consolidation ceiling**."
- **Graph memory** (Zep's **Graphiti**) = current SOTA: **63.8% on LongMemEval** vs **49.0%** for flat vector store.
- Graph-vector **hybrid** most expressive (e.g. **Cognee** — open-source, converts docs to persistent knowledge graph, runs locally / self-hosted / cloud).
- Other frameworks named: Mem0, Letta, Chroma, Pinecone.

**Recommendation (Claude) — plan for graph, don't start there:**
| Layer | Start with (Phase 4) | Add when | Never (at this scale) |
|---|---|---|---|
| State/task | SQLite tables (queue, runs, leases) | — | Redis, Postgres |
| Episodic | Append-only JSONL run logs + per-project `MEMORY.md` | search slow → SQLite FTS5 | dedicated event store |
| Semantic notes | Markdown `memory/<slug>.md` w/ frontmatter, `[[wiki-links]]` | recall needs similarity → `sqlite-vec` embeddings over same files | Milvus, Weaviate, Qdrant, Pinecone |
| Relationships | frontmatter links + a `links` table | multi-hop cross-project queries recur → **Cognee** or **Graphiti** (both local) | standalone Neo4j from day one |

- Embeddings: local `nomic-embed-text-v2` or `bge-m3` via MLX; vectors in `sqlite-vec` in the same DB file. No separate service, no separate backup target.
- Project vs global: each project dir → `./.agentlab/memory/`; global `~/agentlab/memory/` for cross-project facts + project index. Coordinator loads global + active project only.
- Principle: one fact per file, human-readable, diffable, greppable. If you can't audit with `cat` + `grep`, too much infra.

**Sources:**
- https://vectorize.io/articles/best-ai-agent-memory-systems
- https://www.cognee.ai/blog/guides/building-an-ai-agent-best-persistent-memory-layer
- https://atlan.com/know/agentic-ai-memory-vs-vector-database/
- https://www.braintrust.dev/articles/best-ai-agent-memory-tools-2026
- https://mem0.ai/blog/graph-memory-solutions-ai-agents
- https://arxiv.org/pdf/2606.20570 (Infrastructure for the Agentic Web: Agentverse)

---

## 8. Computer control + security

**Findings (2026 sandboxing):**
- Isolation approaches: **microVMs** (Firecracker, Kata) = strongest, dedicated kernel per workload; **gVisor** = user-space kernel / syscall interception, no full VM; **hardened containers** = trusted code only (standard containers share host kernel — insufficient for AI-generated code).
- **macOS:** Apple **`container`** — MCP server / native lightweight VMs, each agent its own VM, superior to shared-kernel containers. (Apple `container` framework matured on macOS 26.)
- Firecracker/Kata are **Linux-only**.
- Baseline for any agent today: **non-root container, network egress filtering, read-only mounts, strict timeouts on every task.**
- Need for sandboxing "became obvious within days of Claude Computer Use public beta."

**Security model (Claude) — isolation layers, outermost first:**
1. **Dedicated non-admin macOS user `agent`.** All autonomous work runs here. Your login Keychain, browser profiles, `~/Documents`, iCloud, SSH keys not readable by this user. Highest-value control, free.
2. **Workspace jail.** Agent user writes only under `/Volumes/ext/agent/work/` + its own `~`. Filesystem perms + a hook rejecting tool calls with paths outside allowlist.
3. **Per-task exec sandbox.** Risky code in fresh Apple `container` VM (or Colima/Docker): non-root, read-only mounts except workspace, CPU/mem caps, wall-clock timeout, **egress default-deny** + allowlist (pypi, npm, github, crates.io, arxiv, openalex, own SearXNG).
4. **Secrets broker.** Credentials in *your* account's Keychain. Tiny broker on tailnet hands agent short-lived scoped tokens only for allowlisted ops, logs every issuance. Agent process never sees a long-lived secret in env.

**Autonomous vs approval vs forbidden:**
- **Autonomous:** read/write inside task workspace; run tests/linters/builds; local git branch/commit/worktree/stash (never `--force`, never on `main`); local model inference (token/day budget); web GET to allowlisted hosts (no form POST); install deps into sandbox; cloud API calls under cap; create agent definition under cap.
- **Approval:** `git push` / open PR / touch shared remote (always, diff to phone); write outside workspace or to `$HOME` dotfiles; network to non-allowlisted host (one-shot grant); any credential/token request (broker prompts, scope + TTL shown); spend real money (hard gate, no auto-approve cap); cloud spend above $X/day or per-call token ceiling; create agent definition past N.
- **Forbidden (no approval path):** read `~/.ssh`, Keychain, browser profiles, finance/tax dirs (not reachable by `agent` user by construction); `sudo`, disk utils, `launchctl` on other users, system settings (non-admin can't); recursive delete outside workspace / `rm -rf` on real paths (hook pattern-blocks); disable own audit log / watchdog / kill switch (owned by your account).

**Runaway protection:**
- **Kill switch:** `agentctl stop` writes `~/agentlab/PAUSE` (checked every loop) + SIGKILLs worker process group. One tap from phone. Owned by your account.
- **Budgets:** tokens/task, tokens/day, USD/day, max subagents/objective, max queue depth, max task wall-clock. Exceed any → fail task + page.
- **Loop detection:** supervisor tracks (task_id, tool, args-hash); same call 3× in a window → task blocked for review.
- **Audit log:** every tool call, model call, approval, secret issuance → `audit.jsonl` (your account, append-only) + mirrored to dashboard.

**Sources:**
- https://northflank.com/blog/how-to-sandbox-ai-agents
- https://amux.io/guides/ai-agent-sandboxing/
- https://www.firecrawl.dev/blog/ai-agent-sandbox
- https://cosmonic.com/blog/ai-sandbox-guide/
- https://mcpmarket.com/server/container

---

## 9. Always-on operation

**Approach (Claude):**
- **Process supervision:** `launchd` job per long-lived component (`com.agentlab.supervisor`, `.inference`, `.controlplane`) with `KeepAlive=true`, `ThrottleInterval=10`, `StandardOut/ErrorPath` → `/Volumes/ext/agent/logs/`. **LaunchDaemon** for headless; **LaunchAgent** in `agent` user session for GUI-needing parts (headless-Chromium OK as daemon; real computer-use needs Agent + login).
- **Watchdog:** second tiny `launchd` job, 60 s `StartInterval`, curls `http://127.0.0.1:PORT/healthz`; two consecutive failures → `launchctl kickstart -k` supervisor + push notification.
- **Sleep prevention:** `sudo pmset -a sleep 0 disablesleep 1 powernap 0`; run supervisor under `caffeinate -dimsu`.
- **Crash recovery:** tasks hold `lease_expires_at`. On startup, requeue anything `running`/`leased` with expired lease. Steps checkpointed to task row → requeued task resumes, not restarts.
- **Reboot recovery:** `launchd` restarts everything on boot; requeue sweep handles in-flight work. Nothing depends on human login except GUI computer-use (auto-login for `agent` user, or accept it pauses until login).
- **Log rotation:** `/etc/newsyslog.d/agentlab.conf`, 14 days hot on external, restic older to offsite.
- **Scheduled "wake and think":** `launchd` `StartCalendarInterval` (e.g. 02/06/12/20:00) enqueues `review-and-plan` task: read queue + memory + open objectives, generate follow-ups, stop if stopping-conditions met.
- **Cloud alternative for schedule slice:** Claude Code Routines run scheduled agents in Anthropic cloud, no local process alive — redundant trigger; local `launchd` path primary since compute is local.

**Sources:** https://www.mindstudio.ai/blog/claude-code-routines-24-7-agents + macOS `launchd`/`pmset`/`caffeinate` man pages (general knowledge)

---

## 10. Remote access

**Findings:**
- **Anthropic Claude Code Remote Control** shipped **2026-02-25**; reliability upgrades **2026-08-22**. Native streaming connection, **no port forwarding / VPN config**. Auto-reconnect if laptop sleeps / network drops. After Aug 2026: any machine running `claude remote-control` shows as a device card in the Claude mobile app's Code tab — tap, pick directory, start a new session on that machine from the phone.
- **Pre-official DIY stack:** Tailscale (secure tunnel) + Termius/Termux (mobile SSH) + tmux (session persistence) + ttyd (terminal as web page) + optional FastAPI voice wrapper (iOS dictation, quick-action buttons).
- Other options: Happy Coder (free middle ground), Orca.
- Community project: `buckle42/claude-code-remote` (phone access over VPN).

**Approach (Claude):**
- **Network:** Tailscale tailnet across mini + phone + laptop. WireGuard, no inbound ports, no public exposure. Tailscale SSH for shell. ACLs restrict phone to control-plane port + SSH.
- **Control plane:** small **FastAPI** service bound to tailnet interface only, bearer-token auth (token in phone keychain / Secure Enclave). Endpoints: `POST /tasks`, `GET /queue`, `GET /runs/{id}/logs` (SSE stream), `POST /approvals/{id}`, `POST /stop`, `GET /status`.
- **Dashboard:** same service serves mobile-first HTML (HTMX, no build): queue state, live logs, pending approvals w/ approve/deny, big red STOP, resource gauges.
- **Notifications:** **ntfy** (self-host on mini or ntfy.sh with unguessable topic) for approval-needed / task-done / budget-hit / crash. Approval pushes carry action buttons hitting the control plane over the tailnet.
- **Coding surface:** Claude Code Remote Control (native) for interactive coding; FastAPI dashboard for the autonomous fleet.
- **Internet-facing webhooks (only if needed):** single Tailscale Funnel path + HMAC signature verification, nothing else.

**Sources:**
- https://venturebeat.com/orchestration/anthropic-just-released-a-mobile-version-of-claude-code-called-remote
- https://www.explainx.ai/blog/claude-code-mobile-remote-control-phone-guide-2026
- https://www.zbuild.io/resources/news/claude-code-remote-control-mobile-terminal-handoff-guide-2026
- https://medium.com/@zilliz_learn/3-easiest-ways-to-use-claude-code-on-your-mobile-phone-bb65914f5297
- https://github.com/buckle42/claude-code-remote
- https://www.guvi.in/blog/claude-code-on-your-phone/

---

## 11. Storage architecture

**Rule (Claude):** latency-sensitive or fsync-heavy → internal SSD; bulky, churny, or disposable → external. External SSD over USB/TB has lower sustained throughput + can drop under load — never the live databases or the resident model there.

| Data | Drive | Path | Why |
|---|---|---|---|
| macOS, apps, Homebrew, dev tools | internal 512 | `/` | System |
| **Active / resident model weights** | internal 512 | `/opt/models` | Fast random read per token; reload speed; USB dropout stalls inference |
| **SQLite DBs** (queue, memory, evidence, audit) + vec index | internal 512 | `~/agentlab/db` | fsync durability + IOPS; corruption risk on flaky external |
| Supervisor / orchestrator / agent defs / global memory | internal 512 | `~/agentlab` | Small, critical, backed up |
| Model *library* (alt quants, cold models) | external 1TB | `/Volumes/ext/agent/models` | Big, re-downloadable, rarely read |
| Task workspaces + git worktrees | external 1TB | `/Volumes/ext/agent/work` | High churn, disposable, can be large |
| Research paper corpus + PDFs | external 1TB | `/Volumes/ext/agent/papers` | Grows unbounded; sequential reads |
| Datasets, experiment outputs | external 1TB | `/Volumes/ext/agent/datasets` | Bulky, regenerable |
| Logs (hot 14 d), container images, caches | external 1TB | `/Volumes/ext/agent/{logs,containers,cache}` | Write-heavy, low value; protects internal SSD write endurance |
| **Backups** (restic: memory, DBs, config, code) | external + offsite | `/Volumes/ext/agent/backups` | 3-2-1; models excluded (re-downloadable); offsite = B2/S3 encrypted |

- Format external as **APFS**. Symlink churny `agent`-user dirs (`~/work`, caches) to external so tools "just work."
- Check `system_profiler SPNVMeDataType` / vendor spec to confirm genuine NVMe SSD, not a DRAM-less / SMR-adjacent enclosure.

---

## 12. Resource plan (32 GB unified)

> Planning estimates from published MLX benchmarks on adjacent hardware (M4 Pro / M5), NOT measurements of the base M6. Treat as indicative.

**Steady state — light work (heavy model unloaded):**
- macOS + services ~7 GB
- Qwen3-4B resident ~3 GB
- Python (supervisor + orchestrator + workers) ~3.5 GB
- headless Chromium ~2.5 GB
- free / FS cache ~15 GB

**Peak — heavy coding task (Qwen3-Coder-30B-A3B @ ~32K ctx):**
- macOS ~7 GB
- Qwen3-Coder-30B 4-bit ~18 GB
- KV cache @ 32K ~3 GB
- Qwen3-4B (kept for routing) ~3 GB
- headroom ~1 GB (browser evicted)

**Over budget — does NOT fit:** Qwen3-Coder-30B (~18) + gpt-oss-20b (~14) + browser (~3) + macOS (~7) = ~42 GB > 32 GB. Router must serialise: heavy model OR mid reasoner, never both.

**Tuning targets:**
- Ideal model size: 20–32B **MoE** (~3B active). Quant: 4-bit (MLX Q4 / MXFP4). Context: 32K default, 64K ceiling local.
- Concurrent heavy-model workers: **1**. Light-model workers: **2–3**. Cloud workers: **3–5** (rate/budget bound).
- Model swapping: **yes, essential**. Multiple models resident: only Qwen3-4B + one of (heavy / mid). Never heavy + mid.
- Bottlenecks in order: (1) memory capacity, (2) memory bandwidth → tok/s, (3) single heavy slot → queue latency, (4) external SSD throughput during workspace-heavy tasks, (5) cloud rate limits if leaned on.
- Storage: internal ~180–250 GB used (OS + 2–3 hot models + DBs + tools); external 300–800 GB (library, workspaces, papers, logs, backups).

---

## 13. Model strategy — model per job

| Task | Primary (default) | Escalate to | Offline fallback |
|---|---|---|---|
| Planning / decomposition | gpt-oss-20b | Claude Opus 4.8 | gpt-oss-20b |
| Architecture / cross-repo design | Claude Sonnet 4.6 | Claude Opus 4.8 | Qwen3-Coder-30B |
| Coding (feature, bulk) | Qwen3-Coder-30B-A3B | Claude Sonnet 4.6 | Qwen3-Coder-30B |
| Debugging (subtle) | Qwen3-Coder-30B | Claude Sonnet 4.6 | gpt-oss-20b |
| Code review | Qwen3-Coder-30B | Claude Sonnet 4.6 | Qwen3-Coder-30B |
| Research: source reading / extraction | Qwen3-4B | gpt-oss-20b | Qwen3-4B |
| Citation / claim verification | gpt-oss-20b | Claude Sonnet 4.6 | gpt-oss-20b |
| Contradiction detection | gpt-oss-20b | Claude Sonnet 4.6 | gpt-oss-20b |
| Summarisation | Qwen3-4B | gpt-oss-20b | Qwen3-4B |
| Classification / routing / tagging | Qwen3-4B | — | Qwen3-4B |
| Final research synthesis / report | Claude Sonnet 4.6 | Claude Opus 4.8 | gpt-oss-20b |
| PDF figures / screenshots / UI grounding | Qwen3-VL-4B | Qwen3-VL-30B-A3B | Qwen3-VL-4B |

**Router rules (in order):** offline flag → fallback column. Else context > 120K → cloud. Else task class → primary. Escalate on: primary self-reports low confidence, verifier rejects output twice, or task marked `critical`. Every escalation logged; daily cloud spend cap gates it.

**Why local-primary:** privacy, zero marginal cost, no rate limits, works if internet drops. **Why cloud at all:** 30B-class local models still trail frontier Claude on hard multi-file reasoning + citation discipline — the two places a mistake costs hours.

---

## 14. What NOT to install (Claude)

| Tempting tech | Why skip it here |
|---|---|
| Kubernetes / k3s / Nomad | Cluster orchestration for one box. `launchd` + SQLite queue does it with zero operational surface. |
| vLLM | CUDA-first; weak Apple Silicon. MLX/llama.cpp win. Revisit only with an NVIDIA box. |
| Neo4j / standalone graph DB | Real infra to run + back up. Markdown links + `links` table first; Cognee/Graphiti (embedded, local) only on proven multi-hop need. |
| Milvus / Weaviate / Qdrant / Pinecone | Overkill below ~10M chunks. `sqlite-vec` in the DB you already have. |
| CrewAI / AutoGen / Swarms as backbone | Add abstraction, don't solve scheduling many agents against one GPU. Keep the scheduler yours. |
| LangChain as core plumbing | Churny API surface for a few hundred lines of explicit code. LangGraph fine *later* for branchy research only. |
| Airflow / Prefect / n8n | Workflow engines for what cron + a queue cover. Reconsider if flows get genuinely complex. |
| Three inference stacks (Ollama + llama.cpp + MLX raw) | Pick one front (`llama-swap` or Ollama). Three = triple bugs + duplicated weights. |
| 70B+ dense local models | Don't fit with context headroom; single-digit tok/s stalls the queue. 30B-A3B MoE is the ceiling. |
| Pixel-level computer-use as primary interface | Brittle, slow, hard to audit. Prefer CLI/API/MCP tools; computer-use as last-resort tool w/ vision verification. |
| ngrok / public reverse proxy / exposed SSH | Unnecessary attack surface. Tailscale only; Funnel only for one signed webhook path. |
| Docker Desktop | Licensing + overhead. Colima or Apple `container` on macOS 26. |
| Trained model router (RouteLLM etc.) | Tiers are 3 and hardware-fixed. An 80-line rule table is more predictable + debuggable. |

---

## 15. Upgrade path (Claude)

| Move to… | What changes |
|---|---|
| 64 GB unified | Hold Qwen3-Coder-30B + gpt-oss-20b resident at once; add resident vision model. Heavy slots → 2. Default context → 64K, ceiling 128K. Browser not evicted at peak. Cloud dependence drops to synthesis + hardest planning. |
| 96–128 GB (M-series Pro/Max) | Higher bandwidth → tok/s ~doubles. Run 70B-class or Qwen3-Coder-Next-scale; keep 3–4 specialist models hot; heavy slots → 3. Local synthesis approaches cloud — make cloud opt-in per objective. Consider Graphiti if cross-project reasoning routine. |
| Dedicated GPU / LAN inference server | Move all inference there (vLLM on NVIDIA, or MLX on a Mac Studio). Mac mini → pure orchestrator + tools + control plane. Worker pool scales to server concurrency; switch queue to Redis/RQ for multi-host consumers. Router gains "which inference host" dimension. |
| Second always-on machine | Split roles: cheap low-power box runs supervisor + control plane + queue + memory 24/7; beefy box runs inference + sandboxes, can sleep when idle, woken by supervisor. Survives compute box crash. |
| Corpus > ~5M chunks or > 50 projects | Migrate embeddings off sqlite-vec to Qdrant/LanceDB; add knowledge graph for cross-project entity resolution; partition memory DBs per project + global index. |

Architecture doesn't change — only the numbers in the resource plan and which side of the local/cloud line each task falls. Keeping scheduler, queue, memory format, control plane yours makes upgrades config edits, not rewrites.

---

## 16. Recommended final architecture (Claude)

```
Phone / Laptop
    │   (Tailscale tailnet — WireGuard, no public ports)
    ▼
REMOTE INTERFACE
  FastAPI control plane · HTMX dashboard · ntfy push
  Claude Code Remote Control (interactive coding slice)
    │
    ▼   launchd KeepAlive        + launchd watchdog (60s /healthz → kickstart)
ALWAYS-ON SUPERVISOR  ◄────────►  CROSS-CUTTING (owned by your account):
  loop: pause? → sweep leases         Persistent Memory: FS Markdown + SQLite (+vec)
  → schedule → observe                Approval Broker (secrets allowlist)
  → requeue / escalate                Audit log (append-only)
    │                                 Kill switch (PAUSE file)
    ▼
TASK QUEUE (SQLite)   states: queued│leased│running│blocked│done│failed
    │   bounded worker pool (asyncio): heavy×1  light×2  cloud×N (rate + $ capped)
    ▼
AGENT ORCHESTRATOR  (Claude Agent SDK · Goose workers)
  load agent DEFINITION (role·tools·perms·model tier)
  coordinator ⇒ subagents ⇒ merge ; dynamic-create defs
    │
    ▼
MODEL ROUTER   (task class + ctx size + $budget + offline? → tier)
    │
    ├── LOCAL: llama-swap → Qwen3-Coder-30B-A3B (heavy) · Qwen3-4B (light) · gpt-oss-20b · Qwen3-VL
    └── CLOUD (Claude API): hard planning · 200K-ctx repo reasoning · final synthesis · citation verify
    │
    ▼
SANDBOX LAYER
  user 'agent' (non-admin) · git-worktree workspace on ext SSD
  Apple container / Colima per risky exec · egress allowlist
    │
    ▼
TOOLS: Terminal · Filesystem · Git · Browser(headless Playwright) · Python ·
       Research(SearXNG + OpenAlex + arXiv + Crossref) · Documents(Docling/Marker)
```

Changes from the user's original sketch: split Model Router into local + cloud; inserted a Sandbox layer between agents and tools; made Memory / Approval-broker / Audit / Kill-switch cross-cutting rather than a bottom leaf.

---

## 17. Implementation roadmap (8 phases) — summary

Full commands + per-phase test / failure-modes / rollback are in the artifact
(https://claude.ai/code/artifact/6e8265be-66e1-4fce-bb42-973e08819df3). Condensed:

- **Phase 1 — Minimal system:** Homebrew toolchain (`python@3.13 uv git git-lfs sqlite ripgrep jq colima docker`, `--cask tailscale`); `uv tool install mlx-lm`; `llama-swap`; pull `Qwen3-Coder-30B-A3B-Instruct-4bit` + `Qwen3-4B-Instruct-2507-4bit` MLX weights; scaffold supervisor + SQLite queue (`tasks`, `audit` tables); worker = git worktree → model call → tool exec in Colima → write result. Test: submit a "write function + pytest" task, watch it converge.
- **Phase 2 — Autonomous coding:** `brew install goose`; `uv tool install claude-agent-sdk`; `npm i -g @anthropic-ai/claude-code`; `goose configure` → openai-compatible `http://127.0.0.1:8080`. Wrap Goose as `coding` worker with iteration budget; add `code-reviewer` agent gating merges; push/PR = approval gate.
- **Phase 3 — Research agents:** `docker run searxng/searxng`; `uv add docling arxiv pyalex crossref-commons trafilatura`; pull `bge-m3` embeddings. Fixed pipeline: plan → gather → read/extract → verify → link → synthesize → resolve-citations; evidence DB source of truth.
- **Phase 4 — Persistent memory:** `uv add sqlite-vec`; `memory/<slug>.md` + frontmatter + `[[links]]`; per-project `.agentlab/memory/`; `memory_chunks` in sqlite-vec; hybrid recall (FTS5 ∪ vec). Git-init the memory dir for rollback.
- **Phase 5 — Multi-agent orchestration:** formalise `agents/*.md` (`role, system_prompt, tools[], perm_tier, model_tier, max_iterations`); coordinator emits task DAG to queue; pool `heavy=1, light=2, cloud=4`; `create_agent_definition` tool capped at 200; stopping conditions per objective.
- **Phase 6 — 24/7:** `sysadminctl -addUser agent` (non-admin); `pmset -a sleep 0 disablesleep 1`; LaunchDaemon `com.agentlab.supervisor` (`caffeinate -dimsu`, KeepAlive, ThrottleInterval); watchdog LaunchDaemon (StartInterval 60, kickstart -k on 2 fails); nightly plan LaunchDaemon (StartCalendarInterval). Lease-sweep on startup. `newsyslog.d` rotation.
- **Phase 7 — Remote access:** `tailscale up --ssh --hostname mac-lab`; ACL phone → `mac-lab:8600` + `:22`; `brew install ntfy`; `uvicorn controlplane.app:app --host 100.x.y.z --port 8600` (tailnet IP only); dashboard page; broker → ntfy w/ action buttons; `claude remote-control` on the mini. No Funnel unless inbound webhooks (then one signed path).
- **Phase 8 — Advanced optimisation:** speculative decoding (0.5–1.7B draft model in MLX, 1.3–2×); prompt/KV caching of system prompt + repo-map prefix; context discipline (repo-map + retrieval, keep heavy ≤ 32K); schedule cloud-heavy synthesis off-peak; local Grafana/SQLite observability (tok/s, success rate, cost/day, approval latency); fixed eval harness re-run after any model/prompt change; revisit vLLM-MLX when mature.

---

## 18. Cost

- **Completely local / free:** MLX + llama-swap, all local models (Qwen3-Coder-30B, Qwen3-4B, gpt-oss-20b, Qwen3-VL, bge-m3), Goose, opencode, Aider, SearXNG, OpenAlex/arXiv/Crossref APIs, Docling, Playwright, Colima / Apple container, launchd, Tailscale (personal tier), ntfy (self-host), FastAPI, SQLite / sqlite-vec, restic (to external).
- **Optional paid:** Claude API (Opus 4.8 / Sonnet 4.6 / Haiku 4.5) for hard planning + final synthesis + citation verification; Claude Code subscription ($20–200/mo) if you want the polished interactive + Remote Control experience; paid search API (Exa/Tavily/Brave) fallback; offsite backup storage (B2/S3, a few $/mo).
- **Cloud genuinely worth it:** multi-repo architectural planning, 200K+ context reasoning, final research synthesis where citation discipline matters, hardest debugging.
- **Local better:** everything private, bulk/overnight work, anything where 80%-quality-at-$0 wins, offline resilience, no rate limits.
- **Target:** < $30/mo Claude API. System stays fully useful at $0.

---

## 19. Caveats / uncertainty flags

- All tok/s and memory figures are from **third-party benchmarks on M4 Pro / M5**, not the base M6. The M6's 170 GB/s bandwidth is only ~11% above M5 — expect similar-order numbers, not dramatically better for LLM inference.
- Anthropic model lineup is in flux across sources (Opus 4.6 / 4.8 / "Opus 5", Sonnet 4.6). Verify current model IDs at implementation time.
- "Qwen 3.6 / 35B-A3B", "Gemma 4 31B", "Qwen3-Coder-Next" appear in sources as newer options — check whether a newer Qwen3-Coder generation supersedes 30B-A3B by the time you build.
- Apple `container` framework maturity on macOS 26 for long-running agent workloads not independently verified here — validate before relying on it; Colima is the safe fallback.
- Secondary-source roundups (blog benchmarks) can be sloppy; primary model cards + arXiv papers weighted higher above.

---

## 20. Full source list

**Hardware:**
1. https://www.macrumors.com/2026/08/25/apple-announces-2026-mac-mini/
2. https://www.macrumors.com/2026/08/27/m6-chip-to-come-these-two-macs-next/
3. https://www.macworld.com/article/2964754/2026-mac-mini-m5-pro-design-specs-release-date.html
4. https://9to5mac.com/2026/08/25/apple-announces-new-mac-mini-heres-everything-new/
5. https://www.forbes.com/sites/davidphelan/2026/08/25/apple-surprise-launches-new-mac-mini-mac-studio-m6-and-m5-ultra-chips-unexpectedly/

**Local inference / models:**
6. https://yage.ai/share/mlx-apple-silicon-en-20260331.html
7. https://pub.towardsai.net/apples-mlx-runs-local-llms-3x-faster-than-llama-cpp-until-your-context-hits-40k-715ec441afbb
8. https://insiderllm.com/guides/llamacpp-vs-ollama-vs-vllm/
9. https://www.promptquorum.com/local-llms/mlx-vs-ollama-vs-llama-cpp-mac
10. https://www.besthub.dev/articles/which-framework-wins-for-running-large-models-vllm-vs-llama-cpp-vs-mlx-2026-deep-comparison-0610c28f73fc
11. https://contracollective.com/blog/mlx-lm-server-vs-llama-server-apple-silicon-2026
12. https://contracollective.com/blog/llama-cpp-metal-vs-mlx-backend-apple-silicon-2026
13. https://dev.to/sienna/qwen3-coder-next-the-complete-2026-guide-to-running-powerful-ai-coding-agents-locally-1k95
14. https://unsloth.ai/docs/models/qwen3.6
15. https://www.morphllm.com/best-ollama-models
16. https://computingforgeeks.com/ollama-models-cheat-sheet/
17. https://www.layer3labs.io/guides/best-local-llm-for-coding
18. https://www.promptquorum.com/local-llms/best-local-llms-for-coding
19. https://www.orcarouter.ai/blog/best-local-llm-for-coding
20. https://localaimaster.com/vram/best-coding-llm-16gb-vram
21. https://apxml.com/posts/best-local-llms-apple-silicon-mac
22. https://apxml.com/posts/best-local-llm-apple-silicon-mac
23. https://www.sitepoint.com/local-llms-apple-silicon-mac-2026/
24. https://codersera.com/blog/apple-silicon-llms-complete-guide-2026/
25. https://codersera.com/blog/run-qwen3-vl-30b-a3b-thinking-on-macos-installation-guide/
26. https://macgpu.com/en/blog/2026-0402-mac-metalrt-mlx-llamacpp-local-llm-engine-comparison.html
27. https://miyagadget.page/en/blog/2026/06/03/qwen36-mlx-local-benchmark-en/

**Agent harnesses / coding agents:**
28. https://thoughts.jock.pl/p/ai-coding-harness-agents-2026
29. https://www.requesty.ai/blog/agentic-coding-tools-compared-2026-claude-code-cursor-codex-aider
30. https://pinggy.io/blog/top_cli_based_ai_coding_agents/
31. https://mightybot.ai/blog/coding-ai-agents-for-accelerating-engineering-workflows/
32. https://www.kunalganglani.com/blog/aider-vs-claude-code
33. https://frontman.sh/blog/best-open-source-ai-coding-tools-2026/
34. https://www.opensourcealternatives.to/blog/best-open-source-ai-coding-assistants
35. https://nimbalyst.com/blog/best-ai-coding-agents-2026/
36. https://www.morphllm.com/comparisons/goose-vs-claude-code
37. https://www.lowcode.agency/blog/claude-code-vs-goose
38. https://theaiagentindex.com/compare/claude-code-vs-goose
39. https://www.lazytechtalk.com/ai/goose-vs-claude-code-the-free-local-ai-agent-challenging-premium-walled-gardens
40. https://mcp.directory/blog/goose-vs-cline-vs-aider-vs-claude-code-vs-opencode-2026
41. https://baeseokjae.github.io/posts/goose-ai-agent-review-2026/
42. https://sanj.dev/post/goose-vs-claude-code/
43. https://aitoolanalysis.com/goose-ai-review/

**Claude Agent SDK / subagents / scheduling:**
44. https://hidekazu-konishi.com/entry/claude_agent_sdk_complete_guide.html
45. https://hidekazu-konishi.com/entry/claude_code_subagents_and_orchestration_guide.html
46. https://helply.com/blog/create-ai-agent-using-claude-agent-sdk
47. https://alloq.digital/en/blog/claude-agent-sdk/
48. https://tech-insider.org/how-to-use-claude-agent-sdk-2026/
49. https://www.digitalapplied.com/blog/build-claude-code-custom-subagent-step-by-step-2026
50. https://www.channel.tel/blog/claude-code-subagents-orchestrator-pattern
51. https://www.totalum.app/blog/claude-agent-sdk-totalum-2026
52. https://www.mindstudio.ai/blog/claude-code-routines-24-7-agents
53. https://www.tembo.io/blog/claude-code-subagents
54. https://wmedia.es/en/tips/claude-code-background-agents-map
55. https://claudefa.st/blog/guide/development/scheduled-tasks
56. https://baeseokjae.github.io/posts/claude-code-async-workflows-guide-2026/
57. https://handsonai.info/platforms/claude/subagents/scheduling-subagents/
58. https://help.apiyi.com/en/claude-code-2026-new-features-loop-computer-use-remote-control-guide-en.html

**Multi-agent orchestration:**
59. https://github.com/ARUNAGIRINATHAN-K/awesome-ai-agents-2026
60. https://rasa.com/blog/agent-orchestration-tools
61. https://www.augmentcode.com/tools/open-source-agent-orchestrators
62. https://www.truefoundry.com/blog/multi-agent-orchestration-frameworks
63. https://www.augmentcode.com/tools/multi-agent-orchestration-platforms-build-vs-buy
64. https://www.digitalapplied.com/blog/multi-agent-orchestration-5-patterns-that-work

**Memory:**
65. https://www.cognee.ai/blog/guides/building-an-ai-agent-best-persistent-memory-layer
66. https://atlan.com/know/agentic-ai-memory-vs-vector-database/
67. https://vectorize.io/articles/best-ai-agent-memory-systems
68. https://www.braintrust.dev/articles/best-ai-agent-memory-tools-2026
69. https://mem0.ai/blog/graph-memory-solutions-ai-agents
70. https://arxiv.org/pdf/2606.20570

**Research agents / hallucination:**
71. https://arxiv.org/html/2608.05179v1
72. https://arxiv.org/html/2604.03173v1
73. https://arxiv.org/pdf/2605.08583
74. https://arxiv.org/html/2605.08583
75. https://arxiv.org/pdf/2604.03159
76. https://arxiv.org/html/2509.18970v1
77. https://gptzero.me/news/iclr-2026/
78. https://pickaxe.co/post/ai-research-agent

**Sandboxing / computer control:**
79. https://northflank.com/blog/how-to-sandbox-ai-agents
80. https://www.firecrawl.dev/blog/ai-agent-sandbox
81. https://cosmonic.com/blog/ai-sandbox-guide/
82. https://mcpmarket.com/server/container
83. https://amux.io/guides/ai-agent-sandboxing/

**Remote access:**
84. https://venturebeat.com/orchestration/anthropic-just-released-a-mobile-version-of-claude-code-called-remote
85. https://medium.com/@zilliz_learn/3-easiest-ways-to-use-claude-code-on-your-mobile-phone-bb65914f5297
86. https://github.com/buckle42/claude-code-remote
87. https://www.guvi.in/blog/claude-code-on-your-phone/
88. https://www.zbuild.io/resources/news/claude-code-remote-control-mobile-terminal-handoff-guide-2026
89. https://www.vibebrowser.app/blog/2026-05-27-claude-code-mobile-remote-control
90. https://www.explainx.ai/blog/claude-code-mobile-remote-control-phone-guide-2026

**Model routing:**
91. https://github.com/ulab-uiuc/LLMRouter
92. https://www.braintrust.dev/articles/best-llm-routers-2026
93. https://arxiv.org/pdf/2510.07429
94. https://entelligence.ai/blogs/9-best-llm-routers-and-model-routing-tools-in-2026
95. https://inworld.ai/resources/best-llm-router-ai-gateway
96. https://arxiv.org/pdf/2606.18774
97. https://www.clawrouters.com/blog/best-open-source-llm-router

---

## 21. Notes for the paper / multi-AI comparison

Suggested comparison axes when merging 10 AI responses:
1. **Inference engine choice** — MLX-only / llama.cpp-only / Ollama / hybrid + swap layer
2. **Heavy model pick** — Qwen3-Coder-30B-A3B vs Devstral vs gpt-oss vs GLM vs "biggest that fits"
3. **Number of resident models** and whether swapping is recommended
4. **Orchestration stance** — existing single harness / multiple + glue / full custom / heavy framework (CrewAI etc.)
5. **Cloud dependence** — $0-only / cloud-for-synthesis / cloud-heavy
6. **Memory** — files+SQLite / vector DB / knowledge graph / hybrid, and when
7. **Sandbox** — dedicated user / containers / microVM / full VM / none
8. **Remote** — Tailscale+custom / Claude Code Remote Control / SSH+tmux / exposed service
9. **Concurrency numbers** — heavy/light/cloud worker counts proposed
10. **"What not to install" agreement** — which anti-recommendations are shared across AIs
11. **Disagreements worth flagging** — where AIs contradict each other (these are the interesting parts of the paper)

Keep each AI's raw claims + its sources so the paper can attribute and cross-check.
