#!/usr/bin/env python3
"""Structural vs product consensus split (RQ1, §4.2).

Closes the "obvious quantitative follow-up" left in §4.2: is agreement on the
*structural* decisions (topology, state model, security boundary, concurrency
stance, memory architecture) actually higher than agreement on the *product*
decisions (which named tool/model realises each layer)?

Method. Each architecture axis of `data/decisions-matrix.csv` is tagged
`structural` or `product` below. The per-axis agreement count is the modal /
plurality count over the 10 non-anchor canonical systems, taken verbatim from
`analysis/consensus/consensus-matrix.md` (structural axes: the normalized
architectural-choice count) and from draft §4.2 (product axes: the modal
product-name count, which is deliberately *not* normalized — that is the point
of the split). The six meta rows (bottleneck, recency, sources, contradictions,
trust, notinstall) are evaluation signals, not architecture, and are excluded.

This is a re-tabulation of already-published counts, not a fresh coding pass; it
adds no new researcher judgement beyond the structural/product tag on each axis,
which is listed in full so a reader can disagree axis by axis.

Run: python3 analysis/scripts/consensus_split.py
"""
from __future__ import annotations

import statistics

N = 10  # non-anchor canonical systems

# axis -> (group, modal_count_out_of_10, source)
AXES = {
    # ---- structural: topology / state / boundary / concurrency / memory arch ----
    "num_models_resident":        ("structural", 9,  "consensus-matrix"),
    "model_swapping_recommended": ("structural", 10, "consensus-matrix"),
    "model_router":               ("structural", 8,  "consensus-matrix"),
    "cloud_dependence":           ("structural", 8,  "consensus-matrix"),
    "orchestration_stance":       ("structural", 10, "consensus-matrix"),
    "build_vs_adopt":             ("structural", 6,  "consensus-matrix"),
    "topology":                   ("structural", 10, "consensus-matrix"),
    "dynamic_agents":             ("structural", 10, "consensus-matrix"),
    "concurrency_heavy":          ("structural", 9,  "consensus-matrix"),
    "concurrency_light":          ("structural", 6,  "consensus-matrix"),
    "concurrency_cloud":          ("structural", 5,  "consensus-matrix"),
    "research_arch":              ("structural", 10, "consensus-matrix"),
    "anti_hallucination":         ("structural", 10, "consensus-matrix"),
    "memory_start":               ("structural", 10, "consensus-matrix"),
    "memory_later":               ("structural", 9,  "consensus-matrix"),
    "knowledge_graph":            ("structural", 10, "consensus-matrix"),
    "sandbox_isolation":          ("structural", 10, "consensus-matrix"),
    "remote_network":             ("structural", 10, "consensus-matrix"),
    "remote_coding":              ("structural", 10, "consensus-matrix"),
    "always_on_supervision":      ("structural", 10, "consensus-matrix"),
    "sleep_prevention":           ("structural", 10, "consensus-matrix"),
    "crash_recovery":             ("structural", 10, "consensus-matrix"),
    "storage_internal":           ("structural", 7,  "consensus-matrix"),
    "storage_external":           ("structural", 10, "consensus-matrix"),
    # ---- product: which named tool/model realises the layer ----
    "inference_engine":           ("product", 4, "§4.2 (mlx-lm / Ollama-MLX / llama.cpp+MLX / vLLM-MLX)"),
    "heavy_local_model":          ("product", 4, "consensus-matrix (Qwen3-Coder-30B-A3B)"),
    "resident_light_model":       ("product", 4, "consensus-matrix"),
    "mid_reasoner_model":         ("product", 5, "consensus-matrix (reuse heavy / no separate tier)"),
    "orchestration_framework":    ("product", 5, "consensus-matrix (no framework wins)"),
    "coding_agent":               ("product", 7, "consensus-matrix (Aider)"),
    "vector_db":                  ("product", 4, "consensus-matrix (sqlite-vec; Chroma also 4)"),
    "task_queue":                 ("product", 8, "consensus-matrix (SQLite WAL)"),
    "remote_control_plane":       ("product", 10, "consensus-matrix (small FastAPI dashboard)"),
}


def summarise(group):
    counts = sorted(c for _, (g, c, _) in AXES.items() if g == group)
    return {
        "axes": len(counts),
        "counts": counts,
        "median": statistics.median(counts),
        "mean": round(statistics.mean(counts), 1),
        "min": min(counts),
        "max": max(counts),
        "unanimous_or_near": sum(1 for c in counts if c >= 9),
    }


def main():
    print("=" * 68)
    print("STRUCTURAL vs PRODUCT consensus  (modal agreement / 10 systems)")
    print("=" * 68)
    for group in ("structural", "product"):
        s = summarise(group)
        print(f"\n{group.upper()}  ({s['axes']} axes)")
        print(f"  counts (sorted): {s['counts']}")
        print(f"  median {s['median']} / {N}   mean {s['mean']}   "
              f"range {s['min']}-{s['max']}")
        print(f"  axes at >= 9/10: {s['unanimous_or_near']}/{s['axes']}")
    st, pr = summarise("structural"), summarise("product")
    print(f"\n=> structural median {st['median']}/10 vs product median "
          f"{pr['median']}/10  (gap {st['median'] - pr['median']} points)")
    print("\nper-axis tags:")
    for ax, (g, c, src) in sorted(AXES.items(), key=lambda kv: (kv[1][0], -kv[1][1])):
        print(f"  {g:<11} {c:>2}/10  {ax:<26} [{src}]")


if __name__ == "__main__":
    main()
