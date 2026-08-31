# Glossary

Terms that recur across the captured responses. Definitions are scoped to this project's context
(a 32 GB Apple-Silicon local-AI build).

| Term | Meaning here |
|------|--------------|
| **Unified memory** | Apple Silicon shares one memory pool between CPU and GPU. Model weights, KV cache, apps, and OS all draw from the same 32 GB. |
| **Memory bandwidth** | Rate the chip can move data between RAM and compute. Base M6 ≈ 170 GB/s. LLM token generation is bandwidth-bound: each token reads (a portion of) the weights. |
| **MoE (Mixture of Experts)** | Model with many parameters but only a fraction "active" per token (e.g. Qwen3-Coder-30B-A3B = 30B total, ~3B active). Runs at roughly the speed of a 3B dense model while carrying more knowledge. |
| **Dense model** | Every parameter is used for every token. A dense 32B is far slower per token than a 30B MoE on the same bandwidth. |
| **Quantization (Q4_K_M, MXFP4, 4-bit)** | Storing weights at reduced precision to shrink memory. 4-bit ≈ 0.5 bytes/param, so ~30B params ≈ 15–18 GB. |
| **KV cache** | Per-token key/value tensors kept for the whole context window. Grows with context length; a silent multi-GB memory cost. |
| **Context window** | How many tokens the model can attend to at once. Larger = more KV cache = less room for weights. |
| **MLX** | Apple's array/ML framework, Metal-accelerated, the fastest local-LLM path on Apple Silicon for short-to-mid context in 2026. |
| **llama.cpp / llama-server** | Mature C++ inference engine; GGUF weights; better multi-request serving; competitive past ~40K context. |
| **llama-swap** | Thin router in front of llama-server / mlx-lm that loads/unloads models on demand (Ollama-style hot-swap with explicit control). |
| **Ollama** | Convenience wrapper around local inference; v0.19+ uses MLX on Apple Silicon and hot-swaps models. |
| **Model swapping** | Unloading one model to load another because they can't co-reside. Costs seconds of load time; essential at 32 GB. |
| **Logical agent** | An agent *definition* (role, prompt, tools, permissions, model tier) plus a task and a context window — instantiated for minutes, not a running process. 100+ is cheap. |
| **Inference process / slot** | An actual model loaded and doing forward passes. The scarce resource: ~1 heavy + 1–2 light on this hardware. |
| **Worker pool** | Bounded set of queue consumers; pool size (not agent-definition count) is the real concurrency limit. |
| **Coordinator / supervisor topology** | One agent decomposes an objective into queued tasks; workers execute; workers don't negotiate peer-to-peer. The 2026 production default. |
| **Swarm topology** | Peer agents negotiate directly. Token-expensive and hard to observe on one box; generally not recommended here. |
| **Model router** | Logic that maps a task (type, context size, budget, offline?) to a model tier (local light / local heavy / cloud). |
| **git worktree** | Multiple working directories from one repo, each on its own branch — lets an agent iterate on a task in isolation without touching your main checkout. |
| **launchd** | macOS service manager. `LaunchDaemon` = system-wide/headless; `LaunchAgent` = per-user session. `KeepAlive` restarts on crash. |
| **Watchdog** | Separate small process that health-checks the main service and restarts it if unresponsive. |
| **caffeinate / pmset** | macOS tools to prevent idle/display/system sleep so overnight work continues. |
| **Tailscale** | WireGuard-based mesh VPN; devices reach each other over a private tailnet with no public ports. **Headscale** = self-hosted Tailscale control server. |
| **ntfy** | Lightweight pub/sub push-notification service, self-hostable; used for approval prompts and completion alerts. |
| **sqlite-vec** | SQLite extension adding vector similarity search — semantic memory without a separate vector-DB service. |
| **Chroma / Qdrant / Weaviate / Milvus** | Standalone/embedded vector databases. Debated as overkill below ~10M chunks. |
| **Graphiti / Cognee** | Graph-based agent-memory systems (entities + relationships) for multi-hop recall; run locally. |
| **Docling / Marker** | Local PDF→structured-text tools that preserve layout, tables, and character offsets (needed for span-level citations). |
| **SearXNG** | Self-hosted meta-search engine; private web search with no API key. |
| **OpenAlex / Crossref / Semantic Scholar** | Free scholarly-metadata APIs; DOI resolution kills identifier-hijack citation hallucinations. |
| **Apple `container`** | macOS 26 framework running each workload in its own lightweight VM — stronger isolation than shared-kernel containers. |
| **Colima** | Lightweight container/VM runtime for macOS; common Docker Desktop replacement. |
| **seatbelt / sandbox-exec** | macOS's built-in application sandbox mechanism. |
| **Claude Code / Claude Agent SDK** | Anthropic's coding agent (CLI) and the library exposing its agent loop, permissions, subagents, and per-subagent model routing. |
| **Claude Code Remote Control** | Native feature (2026) to drive a Claude Code session on a host machine from the Claude mobile app, no port forwarding. |
| **Goose** | Block's open-source, MCP-native agent that runs on any local model; Apache-2.0, Linux Foundation-governed. |
| **Aider** | Open-source git-first coding assistant; commits every change; model-agnostic. |
| **OpenHands** (formerly OpenDevin) | Open-source autonomous software-engineering agent runtime. |
| **MCP (Model Context Protocol)** | Open protocol for exposing tools/data to agents; Goose extensions and Claude Code tools both use it. |
| **Confabulated futurism** | (This project's term.) A response that sounds current by inventing plausible near-future tool/model names instead of citing real ones — arguably worse than an honest older snapshot. |
