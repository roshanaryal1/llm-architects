# Rater packet — independent second-rater scoring (issue #9)

Hand this whole file, plus the 13 `## Raw response` blocks, to a **fresh LLM session** (a different
model from the one that built this repo — GPT-5, Gemini, a fresh Claude session, etc.). Its scores
go in `analysis/scoring/<rater>-<YYYY-MM-DD>.md`. Do **not** show it the `## Reviewer notes` in the
capture files — those are rater-1's opinions and would contaminate independence.

The purpose is inter-rater agreement (Cohen's κ / Krippendorff's α) on the 9-dimension rubric.

---

## Instructions for the rater

You are scoring 13 AI-generated systems-architecture answers to one identical prompt: *design a
24/7 autonomous AI development-and-research workstation for a 32 GB Apple M6 Mac mini* (the frozen
prompt is in `prompts/prompt-v1.md`; the M6 is a real 2026 machine: 12-core CPU, dual 16-core
Neural Engine, **170 GB/s** memory bandwidth, 32 GB max unified memory).

For **each** of the 13 responses, score all **9 dimensions 0 / 1 / 2** using the rubric below.

Rules:

1. **Score each response independently.** Do not compare responses to each other and adjust. Score
   response A fully, then response B fully.
2. **Only the `## Raw response` text counts.** Ignore any commentary, front-matter, or reviewer
   notes you are shown.
3. **Cite the specific text** you are scoring on — one short quote per dimension in your
   justification.
4. **Verify falsifiable sub-claims** where you can: does a named tool/model exist? does a version
   number resolve? does the model set physically fit 32 GB? (weights + KV cache; a ~30B 4-bit MoE
   ≈ 17–20 GB, a dense 32B 4-bit ≈ 19–20 GB, an 80B 4-bit ≈ 40 GB.) If you cannot verify, say so —
   do not guess.
5. Output one table per response (9 rows) plus a one-line justification per row. Then a summary
   table of all 13 × 9 scores. See the output template below.

## The 9-dimension rubric (from `docs/rubric.md`)

| # | Dimension | 0 | 1 | 2 |
|---|-----------|---|---|---|
| 1 | **Hardware-constraint adherence** | ignores the 32 GB / 170 GB/s / one-GPU envelope, or a hard violation (recommends a model set that cannot fit; assumes CUDA/eGPU as the baseline) | acknowledges 32 GB but with a slip (co-resident set >32 GB once browser/DB counted; hand-waves KV cache; "fits with swapping") | quantified budget, model set fits with headroom **or** the tightness is explicitly called out |
| 2 | **Recency** | pre-2024 defaults dominate (Llama-2/3.0-era, Chroma-only, LangChain-as-core) | mixed: some current, some stale point-versions | current tools **and** current model families/versions for 2026; engages M6 specifics |
| 3 | **Tool factuality** | ≥ 1 fabricated tool/engine/framework presented as a real recommendation | minor errors only (wrong CLI syntax, wrong install path) but all named tools exist | every named tool/repo resolves |
| 4 | **Model factuality** | ≥ 1 fabricated model or version number used as a primary pick | model families right, ≥ 1 point-version / size does not resolve | all model names/versions/sizes resolve for 2026 |
| 5 | **Benchmark factuality** | cites specific numbers that are fabricated or unattributable | vague/plausible numbers, no source | numbers cited to a primary source, or explicitly none given |
| 6 | **Citation quality** | prompt asked for sources; none given, or none resolve, or the reference apparatus is mostly junk URLs | some sources given, some resolve/support | sources resolve **and** support the claim; primary preferred |
| 7 | **Actionability** | vague prose, no commands/config | partial: some install commands, gaps in wiring | executable phased plan with commands, config, test, rollback |
| 8 | **Security model** | absent or token | mentions dedicated user / permissions but no explicit boundary list | explicit autonomous-vs-approval-vs-forbidden boundaries + kill switch + runaway limits |
| 9 | **Internal consistency** | self-contradictory (recommends X in one section, forbids X in another; incoherent numbers) | one minor inconsistency | coherent throughout |

Notes:

- **Dim 3 vs 4:** a *tool* is software you install; a *model* is weights you load. Score
  separately — a response can invent one and not the other.
- **Dim 6:** if the response cited nothing and the prompt asked for sources, score 0. Note that a
  0 here with 2s on 3/4/5 is a real pattern (avoided fabrication by citing nothing) — not a
  scoring error.
- **Dim 1:** run the arithmetic. A design that keeps two large models co-resident, or says "fits
  with swapping", is a 1 at best.

## The 13 responses to score

Score them in this order (paste each `## Raw response` block):

1. `claude-sonnet-5`  (note: this one had live browsing + is the repo's anchor — score it normally, but the analysis will report it separately)
2. `mistral-large-3`
3. `gpt-5`
4. `perplexity`
5. `kimi-instant`
6. `deepseek-expert`
7. `gemini-3.1-pro`
8. `qwen-3.7-plus`
9. `grok-4`
10. `z-ai`
11. `meta-llama-4`
12. `deepseek-instant`
13. `deepseek-instant-deepthink`

(11–13: `deepseek-instant` and `-deepthink` are the same base model as `deepseek-expert` in
different chat modes — score all three; the mode comparison is a separate finding.)

## Output template

```markdown
---
rater: <your model name + version>
date: <YYYY-MM-DD>
method: single-pass, raw-response-only, no access to rater-1 notes
---

## <slug>

| Dim | Score | Justification (one line, with a short quote) |
|-----|:-----:|----------------------------------------------|
| 1 Hardware-constraint | _ | ... |
| 2 Recency | _ | ... |
| 3 Tool factuality | _ | ... |
| 4 Model factuality | _ | ... |
| 5 Benchmark factuality | _ | ... |
| 6 Citation quality | _ | ... |
| 7 Actionability | _ | ... |
| 8 Security model | _ | ... |
| 9 Internal consistency | _ | ... |
| **Total** | **_/18** | |

(...repeat for all 13...)

## Summary

| slug | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | Total |
|------|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:-----:|
| ... | | | | | | | | | | |
```

## After the rater returns

1. Save it as `analysis/scoring/<rater-slug>-<YYYY-MM-DD>.md` (do not overwrite any existing rater
   file).
2. Rater-1's provisional scores currently live inside each capture's `## Reviewer notes`; extract
   them into `analysis/scoring/rater-1-<date>.md` in the same table format for comparison.
3. Compute pairwise Cohen's κ per dimension and overall Krippendorff's α (a small
   `analysis/scripts/agreement.py`, stdlib, is fine).
4. Adjudicate disagreements ≥ 1 point; record the adjudicated scores.
5. Report agreement + the adjudicated table in the paper's methods section.
