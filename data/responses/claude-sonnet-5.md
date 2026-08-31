---
ai_name: Claude Sonnet 5
model_version_id: claude-sonnet-5
provider: Anthropic
interface: Claude Code (CLI)
browsing_enabled: yes (WebSearch + WebFetch; ~97 sources cited)
knowledge_cutoff: January 2026 (stated)
prompt_version: v1 (answered a near-identical earlier draft of the prompt; see note)
date_run: 2026-08-31
run_by: roshanaryal1
notes_on_run: >
  Claude Code session. Ran ~15 live web searches before answering, then delivered the full
  architecture as a published HTML artifact plus a detailed findings document. This corpus keeps
  the raw findings in analysis/findings/claude-sonnet-5-findings.md; the artifact URL is below.
  Because Claude answered from within the tool that later built this repo, treat it as the
  "reference / most-instrumented" response rather than a blind peer — useful as a consensus anchor,
  weaker as an independent data point for the meta-study.
trust_rating: HIGH (only response with live sources), but NOT blind — see note.
---

## Raw response

Full deliverable was published as an HTML artifact:
**https://claude.ai/code/artifact/6e8265be-66e1-4fce-bb42-973e08819df3**

The complete research findings, section by section, with all ~97 sources, are archived in this repo at:
**`analysis/findings/claude-sonnet-5-findings.md`** (54 KB, 21 sections).

### Decisions at a glance (Claude's final picks)

| Layer | Pick |
|---|---|
| Inference engine | MLX (`mlx-lm`) + `llama-swap` for load/unload; Ollama 0.19+ acceptable substitute |
| Heavy local model | `Qwen3-Coder-30B-A3B` 4-bit MLX (MoE, ~3B active) |
| Resident light model | `Qwen3-4B-Instruct` |
| Mid reasoner | `gpt-oss-20b` MXFP4 |
| Vision | `Qwen3-VL-4B` (30B-A3B for hard docs) |
| Orchestration | Thin custom supervisor + SQLite task queue on top of Claude Agent SDK + Goose — not from scratch, not a heavy framework |
| Interactive coding | Claude Code (headless `claude -p` + Remote Control) |
| Local coding worker | Goose (or opencode) + Qwen3-Coder-30B |
| Task queue | SQLite table + asyncio workers (no Redis/Celery) |
| Memory | Markdown files + SQLite now; `sqlite-vec` later; knowledge graph only on proven need |
| Vector store | `sqlite-vec` (no standalone vector DB; explicitly avoid Chroma/Qdrant/etc.) |
| Web search | SearXNG (self-host) |
| Academic | OpenAlex + arXiv + Crossref + Semantic Scholar APIs |
| PDF / documents | Docling (or Marker) |
| Browser | Playwright headless Chromium; computer-use only as last resort |
| Exec sandbox | Dedicated non-admin macOS user + Apple `container` / Colima per risky exec; egress allowlist |
| Process supervision | `launchd` KeepAlive + separate watchdog job |
| Sleep prevention | `pmset -a sleep 0 disablesleep 1` + `caffeinate -dimsu` |
| Remote network | Tailscale only (no public ports) |
| Control plane | FastAPI + HTMX dashboard, tailnet-bound, bearer token |
| Notifications | ntfy |
| Backups | restic → external SSD + B2/S3 (exclude models) |
| Model router | ~80-line rule table (not RouteLLM/trained router) |
| Cloud dependence | Optional; target < $30/mo Claude API for planning + final synthesis + citation verification; $0 still useful |
| Concurrency | heavy=1, light=2, cloud=4 |
| Topology | Hierarchical coordinator/worker (not swarm) |
| Biggest bottleneck | Memory capacity, then bandwidth (~170 GB/s), then the single heavy inference slot |

## Model's own cited sources

~97 URLs — full list in `analysis/findings/claude-sonnet-5-findings.md` §20. Highlights:
- Apple M6 launch coverage (MacRumors, 9to5Mac, Macworld, Forbes) — 12C/12C, dual NE, 2 nm, ~170 GB/s, ships 2026-09-22.
- MLX vs llama.cpp benchmarks (yage.ai, Towards AI, PromptQuorum, Contra Collective).
- Qwen3-Coder-30B-A3B MLX memory + tok/s (Unsloth docs, oMLX, dev.to).
- gpt-oss-20b model card (Morph, OpenAI).
- Agent harness comparisons (thoughts.jock.pl, Requesty).
- Claude Agent SDK / subagents / Remote Control (Anthropic-adjacent, VentureBeat, hidekazu-konishi).
- Memory systems (Vectorize, Cognee, Mem0) — Graphiti 63.8% vs flat vector 49.0% on LongMemEval.
- Sandboxing (Northflank, amux) — microVM vs gVisor vs container.
- Citation-hallucination papers (arXiv 2604.03173, 2605.08583, 2608.05179).

## Reviewer notes

### Status: reference anchor, not a blind peer
Claude ran inside Claude Code and then set up this evaluation repo. Its answer benefits from
(a) live browsing, (b) knowing the exact hardware date, (c) an explicit request-format it partly
authored. For the meta-study, discount it as an independent sample; use it as the consensus anchor
and the only "sourced" baseline against which the others' recency/hallucination are measured.

### Only response with real, checkable citations (RQ5)
Every other response so far (Qwen 3.7 Plus, DeepSeek Instant, DeepSeek Expert) cited nothing.

### Distinctive positions vs the other three
- MoE-first (Qwen3-Coder-30B-A3B + gpt-oss-20b) vs Qwen's dense 32B, DeepSeek-Instant's fabricated models, DeepSeek-Expert's Phi-4-14B dense.
- `sqlite-vec` instead of ChromaDB (all three others picked Chroma).
- `llama-swap` named as the swap layer (others hand-wave a "custom model manager").
- Apple `container` / Colima per-exec sandbox (Qwen: none; DeepSeek-Expert: Docker + self-contradiction).
- Explicit cloud budget + Claude Code Remote Control for the mobile coding slice.
- Engaged M6-specific numbers (170 GB/s → ~50-70 tok/s) rather than generic "M-series".
