# `decisions-matrix.csv` schema

## Shape

- **CSV**, UTF-8, LF, header row required, final newline required.
- **Column 0** is `axis`. Every subsequent column is one AI response, slug = the capture file
  basename (`claude-sonnet-5.md` → column `claude_sonnet5`; hyphens and dots become underscores).
- **Column 1 MUST be `claude_sonnet5`** — the consensus anchor — and MUST be fully populated.
- Rectangular: every row has exactly as many cells as the header.
- One row per axis; no duplicate axis names.
- `validate_matrix.py` enforces all of the above (`make validate`).

## Cell conventions

- A **short phrase**, not a sentence or paragraph. Aim < 90 chars.
- Commas inside a cell → wrap the cell in double quotes (standard CSV).
- **Flag fabrications in-cell**: `Rapid-MLX (FABRICATED)`, `"Gemma 4 26B" (model not real)`.
- Unknown / not addressed by that response: `n/a` or `not discussed`.
- Blank cell = response not yet captured for that column (placeholder). CI warns, does not fail.

## Required axes

Enforced by `validate_matrix.py::REQUIRED_AXES`. Adding an axis: update that set **and**
`docs/comparison-axes.md` in the same commit. Current required set:

```
inference_engine, heavy_local_model, resident_light_model, orchestration_stance,
orchestration_framework, coding_agent, research_arch, anti_hallucination, memory_start,
vector_db, knowledge_graph, sandbox_isolation, remote_network, remote_control_plane,
always_on_supervision, crash_recovery, task_queue, model_router, cloud_dependence,
concurrency_heavy, storage_internal, storage_external, topology, dynamic_agents,
biggest_bottleneck, recency_of_recommendations, sources_cited_count, trust_rating
```

Optional-but-present axes (not enforced, keep if useful): `mid_reasoner_model`,
`num_models_resident`, `model_swapping_recommended`, `build_vs_adopt`, `memory_later`,
`sleep_prevention`, `concurrency_light`, `concurrency_cloud`, `remote_coding`,
`internal_contradictions`, `notinstall_list`.

## Column order

`axis`, then `claude_sonnet5`, then captured responses in capture order, then blank placeholder
columns for planned-but-uncaptured models. When a placeholder is captured, fill it in place
(don't reorder) so historical diffs stay readable.
