#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# validate_matrix.py
#
# Lints data/decisions-matrix.csv so a malformed edit fails `make validate`
# (and CI) instead of silently corrupting the comparison.
#
# Checks:
#   1. File parses as CSV and every row has the same column count as the header.
#   2. First column is "axis"; first data column is the consensus anchor
#      ("claude_sonnet5") and is fully populated (no blank cells).
#   3. All REQUIRED_AXES rows are present (keeps the schema stable across edits).
#   4. No duplicate axis names.
#   5. Warns (does not fail) on any axis row not documented in
#      docs/comparison-axes.md, and on placeholder columns that are entirely blank
#      (expected while data collection is in progress).
#
# Usage:  validate_matrix.py data/decisions-matrix.csv
# Exit:   0 = clean, 1 = at least one hard error.
# ---------------------------------------------------------------------------

from __future__ import annotations

import csv
import pathlib
import sys

REQUIRED_AXES = {
    "inference_engine",
    "heavy_local_model",
    "resident_light_model",
    "orchestration_stance",
    "orchestration_framework",
    "coding_agent",
    "research_arch",
    "anti_hallucination",
    "memory_start",
    "vector_db",
    "knowledge_graph",
    "sandbox_isolation",
    "remote_network",
    "remote_control_plane",
    "always_on_supervision",
    "crash_recovery",
    "task_queue",
    "model_router",
    "cloud_dependence",
    "concurrency_heavy",
    "storage_internal",
    "storage_external",
    "topology",
    "dynamic_agents",
    "biggest_bottleneck",
    "recency_of_recommendations",
    "sources_cited_count",
    "trust_rating",
}

ANCHOR_COLUMN = "claude_sonnet5"


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_matrix.py <decisions-matrix.csv>", file=sys.stderr)
        return 2

    path = pathlib.Path(argv[1])
    if not path.is_file():
        print(f"ERROR: not found: {path}", file=sys.stderr)
        return 1

    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))

    errors: list[str] = []
    warnings: list[str] = []

    if not rows:
        print("ERROR: file is empty")
        return 1

    header = rows[0]
    ncols = len(header)

    # --- check 2a: header shape
    if header[0] != "axis":
        errors.append(f'header column 0 must be "axis", got "{header[0]}"')
    if ncols < 2 or header[1] != ANCHOR_COLUMN:
        errors.append(f'header column 1 must be "{ANCHOR_COLUMN}" (the consensus anchor)')

    # --- check 1: rectangular
    for i, r in enumerate(rows[1:], start=2):
        if len(r) != ncols:
            errors.append(f"row {i} has {len(r)} cells, expected {ncols}")

    data_rows = [r for r in rows[1:] if r and r[0].strip()]
    axes_seen = [r[0].strip() for r in data_rows]

    # --- check 4: duplicates
    dupes = {a for a in axes_seen if axes_seen.count(a) > 1}
    if dupes:
        errors.append(f"duplicate axis rows: {', '.join(sorted(dupes))}")

    # --- check 3: required axes present
    missing = REQUIRED_AXES - set(axes_seen)
    if missing:
        errors.append(f"missing required axis rows: {', '.join(sorted(missing))}")

    # --- check 2b: anchor column fully populated
    if not errors or all("column 1" not in e for e in errors):
        anchor_idx = 1
        for r in data_rows:
            if anchor_idx < len(r) and not r[anchor_idx].strip():
                errors.append(f'anchor column "{ANCHOR_COLUMN}" is blank for axis "{r[0]}"')

    # --- check 5: doc coverage (warn only)
    axes_doc = path.parent.parent / "docs" / "comparison-axes.md"
    if axes_doc.is_file():
        doc_text = axes_doc.read_text(encoding="utf-8")
        for a in axes_seen:
            if a not in doc_text:
                warnings.append(f'axis "{a}" not documented in docs/comparison-axes.md')

    # --- check 5b: entirely-blank columns (warn only — expected pre-collection)
    for c in range(2, ncols):
        col_vals = [r[c].strip() for r in data_rows if c < len(r)]
        if not any(col_vals):
            warnings.append(f'column "{header[c]}" is entirely blank (response not yet collected)')

    for w in warnings:
        print(f"WARN:  {w}")
    for e in errors:
        print(f"ERROR: {e}")

    if errors:
        print(f"\nFAILED with {len(errors)} error(s).")
        return 1
    print(f"\nOK — {len(data_rows)} axes, {ncols - 1} model columns, "
          f"{len(warnings)} warning(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
