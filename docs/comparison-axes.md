# Comparison axes

The rows of [`data/decisions-matrix.csv`](../data/decisions-matrix.csv). Each row is one decision
every response is expected to make (implicitly or explicitly). Cell = a short phrase capturing that
response's choice; flag fabrications in-cell (`... (FABRICATED)`).

`validate_matrix.py` warns if a row here has no definition below, so keep this file in sync when
adding an axis.

## Inference & models

| axis | meaning |
|------|---------|
| `inference_engine` | Local serving stack (MLX, llama.cpp, Ollama, vLLM, custom, or a fabricated one) |
| `heavy_local_model` | Primary coding/reasoning model + whether MoE or dense |
| `resident_light_model` | Small model kept loaded for routing/classification/summaries |
| `mid_reasoner_model` | Optional middle-tier model for planning/verification |
| `num_models_resident` | How many models the design keeps in memory at once |
| `model_swapping_recommended` | Is load/unload swapping endorsed, and any anti-thrash guard |
| `model_router` | How a task is mapped to a model (rule table, classifier, complexity threshold) |
| `cloud_dependence` | None / optional-for-hard-tasks / cloud-heavy; any budget stated |

## Orchestration & agents

| axis | meaning |
|------|---------|
| `orchestration_stance` | One harness / multiple + glue / full custom / heavy framework |
| `orchestration_framework` | The named runtime(s) at the core |
| `build_vs_adopt` | How much is custom code vs adopted |
| `coding_agent` | Tool used for autonomous code work |
| `topology` | Coordinator/worker (supervisor) / swarm / pipeline / other |
| `dynamic_agents` | Mechanism for creating specialist agents at runtime |
| `concurrency_heavy` | Simultaneous large-model workers |
| `concurrency_light` | Simultaneous small-model workers |
| `concurrency_cloud` | Simultaneous cloud workers |

## Research pipeline

| axis | meaning |
|------|---------|
| `research_arch` | Shape of the autonomous-research flow |
| `anti_hallucination` | Mechanisms to stop fabricated citations / unsupported claims |

## Memory

| axis | meaning |
|------|---------|
| `memory_start` | What to use on day one |
| `memory_later` | What to add as it grows, and the trigger |
| `vector_db` | Semantic-search store (sqlite-vec / Chroma / Qdrant / none) |
| `knowledge_graph` | KG stance (defer / adopt now / which) |

## Ops, security, remote

| axis | meaning |
|------|---------|
| `sandbox_isolation` | Dedicated user / containers / microVM / VM / none |
| `remote_network` | Tailscale / WireGuard / tunnel / exposed |
| `remote_control_plane` | Dashboard + API + notification stack |
| `remote_coding` | How interactive coding is driven remotely |
| `always_on_supervision` | launchd/daemon + watchdog design |
| `sleep_prevention` | pmset/caffeinate approach |
| `crash_recovery` | How in-flight work survives a crash/reboot |
| `task_queue` | Queue backend (SQLite / Redis+Celery / other) |

## Storage

| axis | meaning |
|------|---------|
| `storage_internal` | What lives on the 512 GB internal SSD |
| `storage_external` | What lives on the 1 TB external SSD |

## Meta (evaluation, not architecture)

| axis | meaning |
|------|---------|
| `biggest_bottleneck` | What the response names as the limiting factor |
| `recency_of_recommendations` | Rater judgement of currency (RQ4) |
| `sources_cited_count` | Number of citations the response provided (RQ5) |
| `internal_contradictions` | Contradictions found within the response (RQ6) |
| `trust_rating` | Overall rater confidence: HIGH / MEDIUM-HIGH / MEDIUM / LOW |
| `notinstall_list` | The response's own "what NOT to install" set (for overlap analysis) |
