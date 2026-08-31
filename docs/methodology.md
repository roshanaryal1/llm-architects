# Methodology

## 1. Research questions

| ID  | Question | Instrument |
|-----|----------|------------|
| RQ1 | On which architecture decisions do frontier LLMs **converge**, and how strong is the majority? | `data/decisions-matrix.csv` → consensus counts per axis |
| RQ2 | How often do responses **fabricate** tools, model names, version numbers, benchmark figures, or repo URLs? | Per-response hallucination audit (`## Reviewer notes`), tallied |
| RQ3 | Do responses respect the **hardware envelope** (32 GB unified, ~170 GB/s, single GPU)? | `analysis/scripts/memory_budget.py` + rubric dim. "hardware-constraint adherence" |
| RQ4 | Are recommendations **current** as of the capture date, or stale defaults? | Rubric dim. "recency"; cross-check vs the one sourced baseline (Claude) |
| RQ5 | When a response cites sources, do the citations **resolve** and **support** the claim? | Rubric dim. "citation quality"; taxonomy from arXiv 2604.03173 / 2605.08583 |
| RQ6 | Are responses **internally consistent**, and how sensitive are they to prompt paraphrase? | `internal_contradictions` matrix row; `prompt-v2/v3` re-runs (planned) |

There is **no ground truth** for "the correct architecture." Only falsifiable sub-claims and
cross-model agreement are scored. The synthesised reference architecture in
`analysis/consensus/` is an *output*, not a scoring key.

## 2. The instrument

- **`prompts/prompt-v1.md`**, frozen. Contains a responder-context header (fixes the date at
  2026-08-31, asks the model to declare browsing/version, requests a Sources list) followed by the
  verbatim task prompt and a response-format request (decisions table → sections 1–10 →
  deliverables A–K → sources).
- **Paraphrases** `prompt-v2.md`, `prompt-v3.md` (planned): same content, reordered sections and
  reworded framing, to measure prompt-sensitivity (RQ6). Until they exist, generality is limited
  to the v1 phrasing.

## 3. Model set

Target ≥ 10 systems spanning vendors, sizes, and access modes. For each capture, record:
`model_version_id`, `provider`, `interface`, `browsing_enabled`, `knowledge_cutoff`,
`prompt_version`, `date_run`. Browsing-on and browsing-off runs of the same family are treated as
**separate** data points (the browsing effect is itself a finding).

**Anchor caveat.** `claude-sonnet-5` was produced inside Claude Code — the same tool used to build
this repo — with live browsing and partial authorship of the response format. It is retained as
the **consensus anchor and the only sourced baseline**, and explicitly *excluded* from
"independent sample" counts in RQ1/RQ4/RQ5 aggregates.

## 4. Extraction

Two artefacts per response:

1. **Capture file** `data/responses/<slug>.md` — front-matter + verbatim `## Raw response` +
   `## Model's own cited sources` + `## Reviewer notes`. Never edited after merge except to append
   a dated correction note.
2. **Matrix column** in `data/decisions-matrix.csv` — one short phrase per decision axis
   (`docs/comparison-axes.md` defines the ~39 axes). Fabrications are flagged in-cell, e.g.
   `Rapid-MLX (FABRICATED)`.

## 5. Scoring

- Rubric: `docs/rubric.md`, nine dimensions, each 0 / 1 / 2.
- **≥ 2 independent raters** before any paper claim. Each rater's scores go in a separate file
  under `analysis/scoring/`; agreement reported as Cohen's κ (pairwise) or Krippendorff's α.
- Automatable sub-checks feed the rubric but are recorded verbatim:
  - **Tool/version exists?** resolve the package registry / GitHub repo / official docs, fixed to
    the capture date.
  - **Benchmark figure real?** locate in a primary source or mark `unverified`.
  - **Fits 32 GB?** `memory_budget.py` verdict pasted into the capture file.

## 6. Aggregation

- **Consensus matrix** (RQ1): per axis, the modal choice and the count of independent responses
  holding it; disagreements highlighted.
- **Hallucination table** (RQ2): per response, counts by taxonomy category (total fabrication,
  attribute corruption, identifier hijack, placeholder, semantic) + severity.
- **Constraint-violation table** (RQ3): per response, hard violations (model set cannot fit,
  assumes CUDA/eGPU as baseline, ignores KV cache, etc.).
- **Recency score** (RQ4) vs capture date; correlated with browsing flag and model release date.
- **Citation quality** (RQ5): only for responses that cited anything.

## 7. Synthesis

`analysis/consensus/` merges the majority positions plus adjudicated expert judgement into one
reference architecture, with every non-consensus call explicitly labelled. Built only after ≥ 6
responses are captured.

## 8. Threats to validity

- **n = 1 base prompt.** Paraphrases mitigate partially; a second hardware spec would help.
- **Rater subjectivity.** Mitigated by a written rubric + multi-rater κ.
- **No ground truth for the design.** Only sub-claims + consensus are scored.
- **Model churn.** Every capture is a dated snapshot.
- **Anchor contamination.** Claude is not blind; handled by exclusion from independent-sample
  aggregates.
- **Evaluator-is-an-LLM risk.** If an LLM assists scoring, it is disclosed in the rater file and
  spot-checked by hand.
