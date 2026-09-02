# `prompts/`

The study instrument.

| File | Status | Purpose |
|------|--------|---------|
| `prompt-v1.md` | **FROZEN 2026-08-31** | Canonical prompt. Every response in `data/responses/` (`prompt_version: v1`) was run against this. Do not edit. |
| `prompt-v2.md` | **FROZEN 2026-09-01** | Controlled paraphrase — RFC framing, reshuffled sections, no shared sentences with v1. Same substance. For prompt-sensitivity (RQ6). |
| `prompt-v3.md` | **FROZEN 2026-09-01** | v1 minus the anti-anchoring / anti-popularity steer (exact diff in the file header). Ablation: does the steer change the recommendation spread and fabrication rate? |

## Which subset to re-run (P1 pre-submission)

Run v2 **and** v3 on ≥ 5 systems, chosen to span the corpus: keep 2 top-tier (`perplexity`,
`gpt-5` or `mistral`), 2 mid (`gemini`, `qwen` or `kimi`), 1 low (`z-ai` or a DeepSeek fast
mode). Capture with `prompt_version: v2` / `v3` front-matter; extract into new matrix columns
`<slug>_v2` / `<slug>_v3`; report per-system decision-axis deltas and fabrication-count deltas
vs the v1 capture. See `paper/draft-v1.md`.

## Using it

Paste **only** the text between `=== PROMPT START ===` and `=== PROMPT END ===` — the responder
header (fixed date, browsing/version declaration, Sources request) is part of the instrument.

## Changing it

You don't. A change to the task means a new versioned file and a re-run of the whole set. Record
which version each response used in that response's `prompt_version` front-matter field.
