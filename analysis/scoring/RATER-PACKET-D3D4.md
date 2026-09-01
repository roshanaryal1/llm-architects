# Rater packet — CLEAN re-run of dimensions 3 & 4 only (issue #9 follow-up)

Hand this whole file, plus `analysis/scoring/rater-bundle.md` (the 13 `## Raw response` blocks),
to a **fresh LLM session** with **web search ON**. A previous scoring pass had these two
dimensions contaminated — the packet it used named specific tools and asserted they were real, so
the raters were not blind. This re-run fixes that: **nothing here tells you which tools or models
are real.** Score from your own web searches only.

Its scores go in `analysis/scoring/d3d4-<rater-slug>-<YYYY-MM-DD>.md`.

---

## What you are scoring

13 AI-generated systems-architecture answers to one identical prompt: *design a 24/7 autonomous
AI development-and-research workstation for a 32 GB Apple M6 Mac mini* (the M6 is a real 2026
machine: announced 2026-08-25, 12-core CPU, dual 16-core Neural Engine, 170 GB/s memory
bandwidth, 32 GB max unified memory; the study's capture date is 2026-08-31).

You are scoring **only two dimensions** for each response:

| # | Dimension | 0 | 1 | 2 |
|---|-----------|---|---|---|
| 3 | **Tool factuality** | ≥ 1 tool/engine/framework that your web search shows **does not exist**, presented as a real recommendation | all named tools exist, but ≥ 1 has a wrong CLI/command/install path/repo URL | every named tool/repo resolves to a real project |
| 4 | **Model factuality** | ≥ 1 model that your web search shows **does not exist**, used as a primary pick — **OR** a real model given a wrong load-bearing attribute (e.g. an 80B model described as 8B, a dense model called MoE) that the design depends on | model families are right, but ≥ 1 point-version or size tag does not resolve | every model name / version / size resolves for 2026 |

## Scoring rules — read before you start

1. **Score each response independently.** Finish response A fully, then response B. Do not compare
   responses to each other and adjust.
2. **Only the `## Raw response` text counts.** Ignore any front-matter, commentary, or notes.
3. **Web-verify every named tool and model before you score it.** Your training cutoff is earlier
   than the study; a tool being unfamiliar to you is not evidence it is fake. For each name:
   - it resolves to a real GitHub repo / package / Hugging Face model card / official release
     note → **it exists.** Not a fabrication, however obscure. (Dim stays 2, or drops to 1 only
     for a wrong command/URL/version tag.)
   - your searches find nothing either way → **UNRESOLVED.** This scores the dimension **1, never
     0.** Say "unresolved" in your justification.
   - your searches positively establish it does not exist (e.g. the name only appears in
     AI-generated text, no repo, no registry entry) → that supports a **0**. Name the searches
     you ran.
   - a real model is given a wrong size/architecture that the design leans on → **0** on dim 4.
4. **Do NOT read `analysis/verification/`, `docs/rubric.md`, the capture `## Reviewer notes`, or
   any other file in this repository.** Score from the raw responses and your own live searches
   only. (Reading the verification register is exactly the contamination this re-run exists to
   avoid.)
5. Cite, per response, the specific text you scored on and at least one URL you verified against
   (or "no source found" for an UNRESOLVED).
6. A tool is software you install; a model is weights you load. Score them separately — a
   response can invent one and not the other.

## The 13 responses — score in this order

(paste each `## Raw response` block from `rater-bundle.md`)

1. `claude-sonnet-5`
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

## Output template

```markdown
---
rater: <your model name + version>
date: <YYYY-MM-DD>
method: dims 3 & 4 only; raw-response-only; web-search-verified; no repo files read
---

## <slug>

| Dim | Score | Named items checked | Verdict + URL(s) |
|-----|:-----:|---------------------|------------------|
| 3 Tool factuality | _ | <tools/engines named> | <exists / unresolved / not-found, with URLs> |
| 4 Model factuality | _ | <models + sizes named> | <resolves / size wrong / not-found, with URLs> |

(...repeat for all 13...)

## Summary

| slug | D3 | D4 |
|------|:--:|:--:|
| ... | | |

## Names you could not resolve either way

<bullet list of every UNRESOLVED tool/model, so the study can chase them separately>
```

## After the rater returns

1. Save as `analysis/scoring/d3d4-<rater-slug>-<YYYY-MM-DD>.md` (do not overwrite).
2. Diff its D3/D4 against the contaminated columns in
   `analysis/scoring/scores-gpt-5.6-sol-2026-09-01.csv` (and the other #9 rater CSVs).
3. If the clean scores match the contaminated ones within ~1 point per cell → the leak did not
   change the outcome; soften `paper/draft-v1.md` §11 accordingly. If they diverge → the
   contaminated D3/D4 must be replaced with the clean pass in the adjudicated table and the
   paper's §5/§10 numbers re-checked.
4. Fold any newly-UNRESOLVED names into `analysis/verification/tool-model-register.md` §G.
