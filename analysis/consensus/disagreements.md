# Genuine disagreements

These are the architectural axes where the corpus does **not** support a single safe majority choice. The disagreement is useful: it identifies where the final reference architecture requires an explicit engineering judgment rather than a vote.

## 1. Primary local model

**Positions**

- **Qwen3-Coder-30B-A3B 4-bit MoE:** recurring in Claude, Perplexity, DeepSeek Expert and Kimi.
- **Qwen3.6-35B-A3B:** GPT-5's primary; Mistral includes it as an alternative.
- **Qwen 27B dense / 35B-A3B:** Grok's current family recommendation.
- **Qwen2.5-Coder 32B / Qwen2.5 32B:** Qwen and Gemini-style conservative recommendations.
- **Fabricated or corrupted variants:** several low-trust responses give nonexistent Qwen3.5 tags or an incorrect 8B size for Qwen3-Coder-Next.

**Tradeoff:** larger/newer models may improve coding and reasoning but consume more of the 32 GB memory budget and increase swap latency. Dense 32B models are simpler but can be older; the 30B-A3B MoE family offers a strong active-parameter/footprint compromise.

**Implication:** select the model by benchmarked quality-per-GB rather than by model-name popularity. The consensus supports the *class* of model, not a permanent winner.

## 2. Inference server

**Positions:** mlx-lm directly; Ollama with MLX backend; llama.cpp server; MLX + llama-swap; vLLM-MLX.

**Tradeoff:** direct MLX gives control and Apple-Silicon alignment; Ollama gives operational simplicity; llama.cpp provides mature compatibility; llama-swap addresses lifecycle management; vLLM-MLX is attractive where its current feature set is actually validated.

**Implication:** inference serving should be behind an internal adapter so the supervisor is not coupled to one runtime. Benchmark the selected runtime on the actual M6 before treating throughput claims as facts.

## 3. Orchestration substrate

**Positions:** Claude Agent SDK; LangGraph; PydanticAI; plain asyncio/custom Python; hybrid combinations.

**Tradeoff:** frameworks provide durable state, graph semantics and integrations, while custom asyncio gives minimal overhead and complete control. A heavy framework can become the architecture rather than serve it.

**Implication:** the supervisor should own task state and scheduling. A framework can implement selected stateful workflows but should remain replaceable.

## 4. Coding execution layer

**Positions:** Aider; OpenHands; Claude Code; OpenCode; combinations.

**Tradeoff:** Aider is strong for deterministic, git-native interactive edits; OpenHands is attractive for autonomous multi-step execution with a sandbox; interactive CLI tools are better for human steering.

**Implication:** use different executors for different autonomy levels rather than forcing one coding agent to perform every job.

## 5. Vector store

**Positions:** sqlite-vec; ChromaDB; Qdrant embedded; LanceDB.

**Tradeoff:** embedded stores minimize infrastructure and operational failure modes; dedicated/feature-rich stores offer richer retrieval capabilities but add memory, processes and maintenance.

**Implication:** start embedded. The disagreement is over which embedded engine, not whether a vector database cluster is needed on day one.

## 6. Sandbox implementation

**Positions:** dedicated OS user only; Seatbelt/sandbox-exec; Docker/OrbStack; Lima VM; Apple containers.

**Tradeoff:** stronger isolation costs memory, startup time and operational complexity. Containers are practical for untrusted coding workloads, while an OS-user boundary is cheaper for trusted tasks.

**Implication:** make isolation **capability-based**: ordinary tasks use a dedicated non-admin user and workspace permissions; untrusted/autonomous code gets a stronger sandbox. Do not make Docker a universal prerequisite.

## 7. Task queue: SQLite vs Redis

**Positions:** SQLite WAL is dominant; Redis is proposed by a minority, sometimes with Celery.

**Tradeoff:** Redis can provide familiar distributed-queue semantics and future multi-worker scale, but it introduces another always-on service and another persistence/failure surface. SQLite is already required for durable state and is sufficient for one M6.

**Implication:** SQLite first. Add Redis only when measured workload characteristics require cross-process/distributed queue throughput that SQLite cannot provide.

## 8. Cloud escalation

**Positions:** local-only vs optional cloud burst.

**Tradeoff:** pure local maximizes privacy, cost control and independence; cloud burst provides access to frontier reasoning/coding when the local model is uncertain or the task exceeds local capability.

**Implication:** cloud must be an **explicit policy-gated escape hatch**, not a hidden dependency. Privacy class, confidence, task severity and token budget should all be checked before escalation.

## 9. Memory policy: aggressive residency vs headroom

Most systems converge on headroom, but one DeepThink response proposes roughly 32–34 GB of always-loaded models.

**Tradeoff:** aggressive residency reduces reload latency but risks unified-memory pressure, swap, instability and unpredictable latency. Conservative residency sacrifices some warm-cache convenience.

**Implication:** reserve a measurable RAM floor. Treat the 32 GB unified-memory ceiling as a hard engineering constraint, not a target to fill.

## 10. Monitoring stack

**Positions:** minimal custom health/metrics vs Prometheus + Grafana.

**Tradeoff:** Prometheus/Grafana are excellent for mature observability but add services and storage; a small agent system can often obtain the required signals directly from SQLite, launchd, macOS metrics and structured logs.

**Implication:** start with structured logs + SQLite metrics + health endpoints; export to Prometheus later if the workload warrants it.

## What the disagreements mean for the paper

The important result is not that one model or framework “won.” It is that **the models agree on constraints and topology but disagree on implementation choices at the boundary of those constraints**. That is stronger evidence than a superficial majority vote because it separates robust architectural principles from rapidly changing product preferences.

The reference architecture therefore records these choices as `[adjudicated]` rather than presenting them as consensus facts.