# Consensus matrix

**Status:** synthesis complete (issue #10). **Partly corrected 2026-09-01** — the
`heavy_local_model`, `recency_of_recommendations`, `sources_cited_count`, `internal_contradictions`
and `trust_rating` rows mention "fabricated" variants that web verification later cleared as real
post-cutoff releases (`analysis/verification/tool-model-register.md`); the RQ1 *counts* are
unaffected (they were never fabrication-dependent) but read "fabricated/incorrect variants" as
"one genuine size error in z-ai, plus unverified point-version tags elsewhere".

This is the formal RQ1 synthesis from `data/decisions-matrix.csv`. Counts use the **10 non-anchor canonical systems** only: Qwen 3.7 Plus, DeepSeek Expert, Perplexity, Gemini 3.1 Pro, Kimi Instant, Mistral Large 3, GPT-5, Grok-4, Meta/Llama 4, and z.ai. Claude Sonnet 5 is the anchor and is excluded; the two non-canonical DeepSeek captures are excluded from the per-system tally but remain part of the RQ2/RQ6 corpus.

A count is attached to a normalized choice where responses use different product names for substantially the same architectural decision. Where no defensible normalization produces a dominant choice, the modal/plurality position is reported and the spread is explicitly retained rather than manufacturing consensus.

## RQ1 results

| Axis | Modal / plurality choice | Count | Spread / interpretation |
|---|---|---:|---|
| `inference_engine` | MLX-family local inference as the primary path, with llama.cpp/Ollama compatibility | **10/10** | Product-level disagreement is real: mlx-lm, Ollama-MLX, llama.cpp+MLX and vLLM-MLX all appear. The common architectural choice is Apple-Silicon-native MLX rather than a CUDA-first stack. |
| `heavy_local_model` | Qwen3-Coder-30B-A3B 4-bit MoE | **4/10** | Qwen2.5-Coder/32B dense appears in 2; Qwen3.6-35B-A3B in 1; Grok gives a 27B/35B family; Llama and z.ai contain fabricated/incorrect variants. No model has majority support. |
| `resident_light_model` | Small ~4–8B Qwen-family helper | **4/10** | Choices range from Qwen3-4B/4B-class to 7B/8B, 9B, 14B, or no permanently separate light model. The architectural role is much more stable than the exact checkpoint. |
| `mid_reasoner_model` | Reuse the heavy model / no mandatory separate mid-tier model | **5/10** | Several systems propose a distinct 14B–32B reasoner; others explicitly reuse the main MoE. This is an optional tier, not a consensus requirement. |
| `num_models_resident` | One large model resident; small model(s) optional/on-demand | **9/10** | The outlier is the aggressive 2–3-instance design. The corpus strongly rejects co-resident large models on 32 GB. |
| `model_swapping_recommended` | Yes, with anti-thrash/load-policy controls | **10/10** | Agreement is unusually strong. Differences concern thresholds (idle time, RAM pressure, task boundaries) and warm-cache policy. |
| `model_router` | Lightweight rule-based routing by task type/complexity/load | **8/10** | LiteLLM and classifier-based routing are alternatives. The common principle is policy routing before learned routing. |
| `cloud_dependence` | Optional cloud burst for hard/ambiguous work; local core remains useful at $0 | **8/10** | Two systems advocate a purely local main strategy. Cloud is consistently framed as an escalation path rather than a prerequisite. |
| `orchestration_stance` | Custom supervisor + thin integration with specialist runtimes | **10/10** | Strong convergence against a single mega-framework. Frameworks are treated as components, not the architecture itself. |
| `orchestration_framework` | No single framework wins; lightweight custom Python is the common substrate | **5/10** | LangGraph, PydanticAI, Claude Agent SDK and plain asyncio/custom Python divide the field. The consensus is architectural, not vendor-framework-specific. |
| `build_vs_adopt` | Build the supervisor/scheduler; adopt mature executors and libraries | **6/10** | The rest lean toward adoption plus glue. Nobody recommends building every execution/research primitive from scratch. |
| `coding_agent` | Aider as the recurring git-native coding layer | **7/10** | OpenHands is the strongest autonomous alternative/co-primary. Claude Code and OpenCode appear in narrower roles. |
| `topology` | Hierarchical coordinator/worker; explicitly not a swarm | **10/10** | Decomposition, bounded workers, verification and aggregation recur across all canonical systems. |
| `dynamic_agents` | Logical agent definitions created/instantiated on demand | **10/10** | “100 agents” is treated as cheap state/configuration, not 100 resident LLM processes. |
| `concurrency_heavy` | One concurrent large-model worker | **9/10** | A single response proposes 2–3 instances. The rest converge on one heavy inference slot because 32 GB unified memory is the hard constraint. |
| `concurrency_light` | Small pool, roughly 2–3 workers | **6/10** | Exact counts vary from 1 to 5; lightweight I/O/tool workers can exceed the LLM worker count. |
| `concurrency_cloud` | Budget/approval/confidence-gated bursts rather than standing cloud workers | **5/10** | Several systems specify zero/unspecified cloud concurrency. No stable numeric concurrency target exists. |
| `research_arch` | Evidence-first pipeline: search → retrieve → extract → verify → contradiction check → synthesize | **10/10** | Tool names differ, but the staged evidence pipeline is universal. |
| `anti_hallucination` | Stored evidence ledger + claim/source verification + contradiction pass | **10/10** | The strongest common rule is that final prose is generated from verified evidence, not unchecked model memory. |
| `memory_start` | SQLite + filesystem as the day-one source of truth | **10/10** | Some add vectors immediately, but SQLite/filesystem durability is the common base. |
| `memory_later` | Defer vector/graph complexity until corpus or reasoning needs justify it | **9/10** | One response proposes a four-layer memory architecture from the start; otherwise staged growth dominates. |
| `vector_db` | sqlite-vec / embedded local vectors | **4/10** | ChromaDB 4/10; Qdrant embedded 1/10; LanceDB/Chroma 1/10. The deeper consensus is **no standalone vector-DB daemon initially** (8/10). |
| `knowledge_graph` | Defer until multi-hop/temporal reasoning demonstrates a real need | **10/10** | Neo4j-heavy day-one designs are consistently rejected. |
| `sandbox_isolation` | Dedicated non-admin macOS user with workspace isolation | **10/10** | Container/VM/Seatbelt implementation varies. The stable security boundary is least privilege + isolated workspaces. |
| `remote_network` | Tailscale-only private network | **10/10** | WireGuard/Headscale/tunnel alternatives appear, but no canonical response recommends public exposure. |
| `remote_control_plane` | Small FastAPI/web dashboard over the private tailnet | **10/10** | Streamlit/HTMX/SSH-only variants exist, but private dashboard/API control is the recurring pattern. |
| `remote_coding` | SSH and/or private web dashboard over Tailscale | **10/10** | Product/UI differs; the invariant is authenticated private remote operation without exposing model endpoints publicly. |
| `always_on_supervision` | launchd + KeepAlive + independent watchdog/heartbeat | **10/10** | The exact plist layout varies, but restart supervision is universal. |
| `sleep_prevention` | `caffeinate` and/or `pmset` on AC power | **10/10** | Some designs add queue-aware sleep rather than disabling sleep permanently. |
| `crash_recovery` | Durable queue + leases/checkpoints + requeue interrupted work | **10/10** | Idempotence and “resume, don't replay destructive actions” are recurring safety rules. |
| `task_queue` | SQLite WAL-backed queue | **8/10** | Redis is the main alternative (2/10). The majority explicitly rejects distributed queue infrastructure at this scale. |
| `storage_internal` | Fast internal SSD for OS/runtime, active workspace, databases/cache, and preferably hot model weights | **7/10** | Three designs keep model weights primarily external. The shared rule is to reserve internal I/O capacity for hot working state. |
| `storage_external` | Model library + research corpus + datasets + archives/backups | **10/10** | Exact allocations differ; all treat the 1 TB external SSD as bulk/cold storage rather than the latency-critical system disk. |
| `biggest_bottleneck` | 32 GB unified-memory capacity/bandwidth, especially KV cache and large-model residency | **10/10** | Wording varies between capacity, bandwidth and KV growth, but all converge on memory rather than CPU/GPU compute as the limiting resource. |
| `recency_of_recommendations` | Mixed; no majority currentness level | **3/10 tie** | MEDIUM and MEDIUM-HIGH each occur 3 times. Currentness is strongly correlated with retrieval/source quality, but not perfectly. |
| `sources_cited_count` | 0 usable/resolvable citations | **7/10** | Perplexity, Mistral and Llama provide many references, but citation quantity is not equivalent to evidence quality; Llama's large count is particularly noisy. |
| `internal_contradictions` | None detected | **8/10** | Llama and z.ai contain material internal inconsistencies. Minor plan bugs are not counted as contradictions unless they change an architectural claim. |
| `trust_rating` | MEDIUM / MEDIUM-HIGH (tie) | **3/10 each** | Mistral/GPT are HIGH; several retrieval-grounded systems are MEDIUM-HIGH; Llama is LOW; z.ai trends MEDIUM-LOW. This is deliberately not collapsed into a single “average trust” score. |
| `notinstall_list` | Avoid heavyweight infrastructure and premature distributed services | **no single modal set** | Recurrent exclusions include Kubernetes, standalone vector databases, Neo4j, multiple large models, public endpoints, and “all-frameworks-at-once” designs. Exact lists are intentionally not collapsed because overlap is the analysis target. |

## What actually constitutes consensus

The strongest RQ1 result is **architectural convergence despite implementation-level disagreement**. The corpus converges on a memory-constrained, local-first coordinator/worker machine: one large model at a time, bounded lightweight workers, durable SQLite state, MLX-family inference, staged model swapping, private Tailscale access, least-privilege isolation, launchd supervision, and evidence-first research.

The exact framework or model checkpoint is much less settled. Those are therefore treated as **adjudication points**, not as majority facts.

## Counting rule

The formal denominator is **10 systems**, not 13 responses. DeepSeek's three captures are not independent vendors: `deepseek-expert` is the canonical DeepSeek system response; `deepseek-instant` and `deepseek-instant-deepthink` remain separate for response-level analyses. Claude Sonnet 5 is the non-blind anchor and is excluded from RQ1 voting.