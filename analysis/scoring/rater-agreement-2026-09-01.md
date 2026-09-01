# Inter-rater agreement + adjudicated scores (issue #9)

Date: 2026-09-01. Reproduce: `python3 analysis/scripts/agreement.py`.

## Rater set

| id | what it is | role |
|---|---|---|
| `rater-1` | this repo's first pass; 9-dim scores derived from each capture's `## Reviewer notes`, **corrected basis** (post-`analysis/verification/tool-model-register.md`) | first rater |
| `gpt-5.6-sol` | OpenAI ChatGPT, paid tier, web search on; ran `RATER-PACKET.md` + `rater-bundle.md` | **canonical rater-2** (study owner's designation) |
| `grok-4` | xAI Grok 4 + web verification; same inputs | variance check |
| `deepseek-chat` | run inside a DeepSeek chat; output self-labels "GPT-5 (via web search)" | variance check |

Score files: `analysis/scoring/scores-<id>-2026-09-01.csv` (slug, D1..D9 in {0,1,2}).
Full per-response justifications: `analysis/scoring/<id>-*-2026-09-01.md`.

## Threats to validity — read first

1. **Dimensions 3 & 4 are not blind.** `RATER-PACKET.md` rule 4, as sent, listed the 12
   tools/models rater-1 had false-flagged and asserted they are real. All three rater-2 runs saw
   this; `deepseek-chat` quotes the list back verbatim. D3/D4 agreement below is therefore partly
   circular and should be reported as a lower bound on difficulty, not a clean reliability figure.
   D1, D2, D5, D6, D7, D8, D9 are unaffected. (Fixed in the packet after this run — future raters
   get "web-verify yourself; UNRESOLVED scores 1, never 0" instead of the answer key.)
2. **Rater severity varies by ~3.6 points of 18.** Mean total: `gpt-5.6-sol` 11.1, `rater-1` 12.7,
   `grok-4` 13.8, `deepseek-chat` 14.7. `deepseek-chat` assigned 2 on D1–D4 and D7–D8 almost
   uniformly — a low-information rater; it is kept for the variance table but excluded from
   adjudication.
3. **`grok-4` self-scored the `grok-4` response** (16/18) and **`deepseek-chat` scored the three
   DeepSeek responses** (15/15/15). Possible self-preference; noted, not corrected.
4. `rater-1` is not independent of the study design (it wrote the rubric and the reviewer notes).
   That is why a rater-2 exists; the adjudicated column is the reportable one.

## Agreement — canonical pair (`rater-1` vs `gpt-5.6-sol`)

117 paired ratings (13 responses x 9 dims).

| metric | value |
|---|---|
| exact agreement | **68.4 %** |
| within 1 point | **96.6 %** |
| Cohen's kappa, unweighted | **+0.494** (moderate) |
| Cohen's kappa, quadratic-weighted | **+0.637** (substantial) |
| Gwet's AC1, unweighted | **+0.543** |
| Gwet's AC1, quadratic-weighted | **+0.728** (robust to the 2-heavy prevalence that deflates alpha) |
| Krippendorff's alpha, ordinal (pair) | **+0.198** |
| Krippendorff's alpha, ordinal (all 4 raters) | **+0.118** |

The kappa_w / AC1_w ≈ 0.64–0.73 vs alpha ≈ 0.20 gap is a prevalence artefact: several
dimensions are almost all 2s, which inflates alpha's chance term. Gwet's AC1 is designed for
that skew and agrees with the weighted kappa. Report all of them; read agreement as moderate
and dimension-dependent.

### Rank-order stability of per-response totals

Per-response total (/18) rank correlation, every rater pair:

| pair | Spearman rho | Kendall tau_b |
|---|---:|---:|
| rater-1 vs gpt-5.6-sol | +0.712 | +0.578 |
| rater-1 vs grok-4 | +0.452 | +0.381 |
| rater-1 vs deepseek-chat | +0.083 | +0.056 |
| gpt-5.6-sol vs grok-4 | +0.371 | +0.326 |
| gpt-5.6-sol vs deepseek-chat | +0.406 | +0.243 |
| grok-4 vs deepseek-chat | +0.114 | +0.072 |
| **mean over all pairs** | **+0.356** | **+0.276** |

The canonical pair rank-correlates moderately (rho 0.71); the heavier-scoring raters do not.
**Do not claim a stable fine-grained ranking.** What is reportable is coarse performance bands
(top / bottom membership is stable). The paper's §10.1 is stated as bands for this reason.

The raters almost always agree on **direction** (which response is stronger on a dimension) and
disagree on **exact level**. Only 4 of 117 cells are 2-point gaps.

### Per dimension

| dim | exact | kappa | kappa (wtd) | reading |
|---|---:|---:|---:|---|
| D2 recency | 85 % | +0.68 | +0.68 | reliable |
| D3 tool-factuality | 85 % | +0.70 | +0.70 | reliable (but not blind — see threat 1) |
| D5 benchmark-factuality | 77 % | +0.66 | +0.84 | reliable |
| D4 model-factuality | 77 % | +0.46 | +0.70 | ordinal-reliable (not blind) |
| D6 citation-quality | 69 % | +0.30 | +0.52 | weak; "0 vs 1" boundary is fuzzy |
| D8 security-model | 77 % | +0.32 | +0.32 | weak; "has tiers" vs "has an explicit boundary list" |
| D7 actionability | 62 % | +0.36 | +0.19 | weak; "has commands" vs "has rollback/tests too" |
| **D1 hardware-constraint** | 38 % | **+0.15** | +0.43 | **poor** — "sums to exactly 32 GB" scored 1 by Sol, 2 by rater-1 |
| **D9 internal-consistency** | 46 % | **+0.14** | +0.07 | **poor** — Sol missed the two DeepSeek "recommend X / forbid X" contradictions |

**Action for the rubric (v2):** D1, D7, D8, D9 need sharper anchors.
- D1: "sums to exactly 32 GB with no reserved margin" is a **1**, not a 2. A 2 requires a named
  free-RAM floor.
- D9: a section that recommends a tool the "do not install" list forbids is an automatic **0** —
  make that explicit so a rater cannot miss it.
- D7: a 2 requires commands **and** a test step **and** a rollback path; "phased plan with
  commands" alone is a 1.
- D8: a 2 requires an explicit forbidden-action list, not just autonomous/approval tiers.

### Pairwise exact agreement (all raters)

|  | rater-1 | gpt-5.6-sol | grok-4 | deepseek-chat |
|---|---:|---:|---:|---:|
| rater-1 | — | 68 % | 56 % | 62 % |
| gpt-5.6-sol | 68 % | — | 47 % | 53 % |
| grok-4 | 56 % | 47 % | — | 75 % |
| deepseek-chat | 62 % | 53 % | 75 % | — |

`grok-4` and `deepseek-chat` agree most with each other (both lenient); `gpt-5.6-sol` is the
outlier (strict). This severity spread is itself a study result: **the same rubric run through
four LLM raters produces an 8.5→14.7 / 18 range on the same response** — LLM-as-rubric-rater is
not yet a stable instrument without anchored examples.

## Adjudication

All 37 canonical-pair gaps resolved. Rule: rubric text wins; for factual dims the verification
register wins; anchor (`claude-sonnet-5`) gaps resolved conservatively since it is excluded from
cross-response stats anyway.

| response | dim | r1 | sol | adj | rationale |
|---|---|:--:|:--:|:--:|---|
| claude-sonnet-5 | D1 | 2 | 1 | **1** | scored raw block cites the bottleneck but gives no quantified co-resident budget |
| claude-sonnet-5 | D6 | 2 | 0 | **1** | block names a real ~97-source corpus by count but the URLs are not in the scored text |
| claude-sonnet-5 | D7 | 2 | 0 | **1** | block is decisions-focused; the full install plan is elsewhere in the response |
| claude-sonnet-5 | D8 | 2 | 1 | **2** | full capability-tier matrix (Autonomous/Notify/Approve/Never) + kill switch is in the response; Sol under-read |
| mistral-large-3 | D4 | 2 | 1 | **1** | "GLM-5.2 (744B MoE)" size is stated as fact and is off; it is a cloud fallback, not primary |
| mistral-large-3 | D6 | 2 | 1 | **2** | ~36 credibility-rated dated entries; best non-anchor apparatus; ~6 search-URLs don't drop it to 1 |
| mistral-large-3 | D9 | 2 | 1 | **2** | the 744B question is a factuality nit (already in D4), not a prose self-contradiction |
| gpt-5 | D1 | 2 | 1 | **1** | own minimum-RAM rows exceed 32 GB with the recommended 1+1 workers — a real slip |
| gpt-5 | D5 | 1 | 0 | **1** | numbers attributed to "Qwen reports ..." — attributable, unsourced, hedged |
| gpt-5 | D6 | 1 | 0 | **1** | ~20 inline attributions to real docs ("OpenHands docs recommend ...") are checkable |
| gpt-5 | D7 | 2 | 1 | **1** | rich commands + resource-aware scheduling but no explicit per-phase rollback |
| gpt-5 | D9 | 2 | 1 | **2** | Sol's "conflict" is a tightness issue, not a self-contradiction; grok + deepseek-chat also say clean |
| perplexity | D2 | 1 | 2 | **2** | models are current (Qwen3-Coder-30B-A3B), engages the M6 constraint, refuses to fake numbers; deliberate conservatism != stale |
| kimi-instant | D1 | 2 | 1 | **2** | RAM table reserves an explicit 2–4 GB floor "critical for stability" |
| kimi-instant | D3 | 2 | 1 | **2** | "commands would largely run as written"; the config-key quibble is thin |
| kimi-instant | D9 | 2 | 1 | **2** | headroom-vs-range-top is a tightness artefact, not a contradiction |
| gemini-3.1-pro | D7 | 2 | 1 | **1** | install commands + launchd plist + sanity tests, no rollback path |
| qwen-3.7-plus | D8 | 2 | 1 | **2** | 3-tier permission model + kill switch + resource limits present |
| grok-4 | D1 | 2 | 1 | **2** | quantified ranges, names the bottleneck correctly, "1 concurrent large-model worker preferred" |
| grok-4 | D5 | 1 | 0 | **1** | "~72% SWE-bench" for OpenHands is roughly right, unattributed |
| grok-4 | D7 | 2 | 1 | **1** | has a Phase-1 rollback but "config detail too sparse for a fully executable build" |
| grok-4 | D9 | 2 | 1 | **2** | "worker pool 1–3" vs "1 preferred" is phrasing tension, not a contradiction; rater-1 + 2 others say clean |
| z-ai | D2 | 1 | 2 | **1** | zero M6-specific facts + a 2025-dated own-model pick (GLM-4.5-Air); rubric-2 requires engaging M6 specifics |
| z-ai | D8 | 2 | 1 | **2** | explicit autonomous/approval/never matrix + audit + Keychain + egress limits |
| meta-llama-4 | D1 | 1 | 0 | **1** | the *fit* reasoning is sound (1 large, cap ctx 32K); the "~300+ GB/s" error is penalised in D2/D5, not here |
| meta-llama-4 | D6 | 0 | 1 | **0** | ~60% of the 99 refs are junk GitHub commit/PR/`SKILL.md` URLs = "reference apparatus mostly junk" |
| meta-llama-4 | D9 | 1 | 2 | **1** | citation apparatus internally incoherent (same tool, multiple repo URLs; `[38]` wrong title) |
| deepseek-expert | D1 | 2 | 1 | **1** | budget sums to exactly 32 GB with no reserved margin |
| deepseek-expert | D3 | 2 | 1 | **1** | `cd llama.cpp && make -j8` is stale (project moved to CMake) — wrong CLI, tool exists |
| deepseek-expert | D4 | 2 | 1 | **2** | primary models (Qwen3-Coder-30B-A3B, Phi-4-14B) all resolve; "Qwen3-Coder-70B" is upgrade-path only |
| deepseek-expert | D5 | 1 | 0 | **1** | "~25 tok/s on M6" unsourced but conservative/plausible (contrast deepseek-instant's invented figures) |
| deepseek-expert | D7 | 2 | 1 | **1** | extensive commands + test checklist, no rollback across the phased build |
| deepseek-expert | D9 | 0 | 2 | **0** | recommends "seatbelt + Docker" in A, forbids "Docker for Mac" in J — textbook rubric-0 |
| deepseek-instant | D1 | 2 | 1 | **1** | "one large at a time" is right but "3–5 worker slots" is optimistic and high-end ranges exceed 32 GB |
| deepseek-instant | D9 | 0 | 2 | **0** | recommends Ollama in Phase 4, forbids it in section J — textbook rubric-0 |
| deepseek-instant-deepthink | D1 | 0 | 1 | **0** | "~32–34 GB, slight oversubscription acceptable" + 3 models resident = a set that cannot fit |
| deepseek-instant-deepthink | D4 | 1 | 2 | **1** | primary "Qwen3.5-35B-A3B" tag is `UNRESOLVED` in the verification register |

Net effect of adjudication vs `rater-1`: claude 18→15, gpt-5 16→14, perplexity 17→18, grok-4
15→14, deepseek-expert 12→9, deepseek-instant 10→9. Others within 1.

## Adjudicated final scores

**Updated 2026-09-01** after the clean D3/D4 re-run (`d3d4-clean-rerun-result.md`): four D3/D4
cells moved. The canonical rater's clean uncontaminated D3/D4 pass reproduced its contaminated #9
pass on 11/13 responses, so the leak's effect on the table is small; the changes below come from
new web findings, not from removing the leak.

| slug | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | **/18** |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| perplexity | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | **18** |
| mistral-large-3 | 2 | 2 | **1** | 1 | 1 | 2 | 2 | 2 | 2 | **15** |
| gpt-5 | 1 | 2 | 2 | 2 | 1 | 1 | 1 | 2 | 2 | **14** |
| grok-4 | 2 | 2 | 2 | 2 | 1 | 0 | 1 | 2 | 2 | **14** |
| gemini-3.1-pro | 1 | 1 | 1 | 2 | 2 | 0 | 1 | 2 | 2 | **12** |
| qwen-3.7-plus | 1 | 1 | 1 | 2 | 2 | 0 | 2 | 2 | 1 | **12** |
| kimi-instant | 2 | 1 | **1** | 2 | 0 | 0 | 1 | 2 | 2 | **11** |
| meta-llama-4 | 1 | 2 | 1 | 1 | 1 | 0 | 2 | 2 | 1 | **11** |
| deepseek-instant | 1 | 2 | 1 | 2 | 0 | 0 | 1 | 2 | 0 | **9** |
| deepseek-expert | 1 | 1 | 1 | **1** | 1 | 0 | 1 | 2 | 0 | **8** |
| deepseek-instant-deepthink | 0 | 2 | 1 | **0** | 0 | 0 | 1 | 1 | 1 | **6** |
| z-ai | 0 | 1 | 1 | 0 | 0 | 0 | 1 | 2 | 0 | **5** |
| *claude-sonnet-5 (anchor)* | 1 | 2 | 2 | 2 | 2 | 1 | 1 | 2 | 2 | *15* |

**D3/D4 re-run changes:** `mistral` D3 2→1 (`brew install goose` → wrong formula); `kimi` D3 2→1
(`opencode config set model` not a real command); `deepseek-expert` D4 2→1 (future primary
`Qwen3-Coder-70B` does not exist); `deepseek-instant-deepthink` D4 1→0 (calls DeepSeek-V4 dense;
it is MoE). Local flip: `deepseek-instant` (9) now scores above `deepseek-expert` (8) — the deep
mode's fabricated future-model tags cost it on D4 while the fast mode's picks all resolved.

A second attempted clean rater (Perplexity) is **discarded**: it scored D3 = 0 for seven
responses by treating its own search misses as proof of nonexistence, violating `UNRESOLVED → 1`
— a live reproduction of the paper's §5 failure mode. Details: `d3d4-perplexity-2026-09-01.md`.

## What this says for the paper

1. **The adjudicated ranking matches the qualitative buckets** and survives both the fabrication
   correction and the clean D3/D4 re-run: `perplexity` / `mistral` / `gpt-5` / `grok-4` on top
   (sourced-or-consensus-aligned + current + M6-aware); `deepseek` fast modes + `z-ai` at the
   bottom — but now for **verifiable** reasons (recommend-then-forbid contradictions, memory
   oversubscription, a load-bearing model-size error, one genuine future-model fabrication), not
   for inventing an ecosystem.
2. **D6 citation-quality is the single biggest differentiator** — it is the only dimension where
   the top 4 separate cleanly from the rest (2/2/2/0 vs mostly 0). It also confirms the "citation
   count != citation quality" finding: `meta-llama-4` has the largest apparatus and scores 0.
3. **Inter-rater reliability is moderate (κ_w 0.64) and dimension-dependent.** Report D2/D3/D5 as
   reliable, D1/D7/D8/D9 as needing the sharpened v2 anchors above. Do not report a single
   headline κ without the per-dimension breakdown.
4. **LLM raters have a severity personality.** Same rubric, same responses, 8.5–14.7 / 18 spread
   across four raters. Anchored exemplars are required before this rubric is a portable
   instrument — a methods-section limitation and a possible follow-up experiment.
