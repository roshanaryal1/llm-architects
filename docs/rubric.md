# Scoring rubric

Nine dimensions, each scored **0 / 1 / 2**. Max 18. Score every response independently; do not
compare-and-adjust. Record scores per rater in `analysis/scoring/<rater>-<YYYY-MM-DD>.md` as a
small table, plus a one-line justification per dimension citing specific text.

| # | Dimension | 0 | 1 | 2 |
|---|-----------|---|---|---|
| 1 | **Hardware-constraint adherence** (RQ3) | Ignores the envelope, or a hard violation (recommends a model set that cannot fit; assumes CUDA/eGPU as the baseline) | Acknowledges 32 GB but with a slip (co-resident set is >32 GB once browser/DB counted; hand-waves KV cache) | Quantified budget, model set fits with headroom or the tightness is explicitly called out; `memory_budget.py` agrees |
| 2 | **Recency** (RQ4) | Pre-2024 defaults dominate (e.g. Llama-2/3.0-era, Chroma-only, LangChain-core as backbone) | Mixed: some current, some stale point-versions | Current tools **and** current model families/versions for the capture date |
| 3 | **Tool factuality** (RQ2) | ≥ 1 fabricated tool/engine/framework presented as a real recommendation | Minor errors only (wrong CLI syntax, wrong install path) but all named tools exist | Every named tool/repo resolves |
| 4 | **Model factuality** (RQ2) | ≥ 1 fabricated model or version number used as a primary pick | Model families right, ≥ 1 point-version doesn't resolve | All model names/versions resolve for the capture date |
| 5 | **Benchmark factuality** (RQ2) | Cites specific numbers that are fabricated or unattributable | Vague/plausible numbers, no source | Numbers cited to a primary source, or explicitly none given |
| 6 | **Citation quality** (RQ5) | Prompt asked for sources; none given, or none resolve | Some sources given, some resolve/support | Sources resolve **and** support the claim; primary preferred |
| 7 | **Actionability** | Vague prose, no commands/config | Partial: some install commands, gaps in wiring | Executable phased plan with commands, config, test, rollback |
| 8 | **Security model** | Absent or token | Mentions dedicated user / permissions but no explicit boundary list | Explicit autonomous-vs-approval-vs-forbidden boundaries + kill switch + runaway limits |
| 9 | **Internal consistency** (RQ6) | Self-contradictory (recommends X in one section, forbids X in another) | One minor inconsistency | Coherent throughout |

## Notes for raters

- **Dimension 3 vs 4:** a tool is software you install (`Rapid-MLX`, `DSH`); a model is weights you
  load (`Gemma 4 26B`). Score separately — a response can invent one and not the other.
- **Dimension 6:** if the response cited nothing, score 0 **only if the prompt asked for sources**
  (v1 does). Note that a 0 here plus 2s on 3/4/5 is possible (avoided fabrication by citing
  nothing) — that pattern is itself a finding, not a scoring error.
- **Dimension 1:** run `python3 analysis/scripts/memory_budget.py` against the response's
  co-resident model set (what it says stays loaded, not what it can swap). Paste the verdict.
- **Anchor:** score `claude-sonnet-5` like any other for completeness, but exclude it from
  cross-response means (it is not blind — see `docs/methodology.md` §3).

## Current scores

Populated once a second rater is onboarded. Rater-1 provisional scores live in the
`## Reviewer notes` of each capture file until then.
