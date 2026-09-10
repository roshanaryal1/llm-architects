<!--
  Point-by-point response to Cureus peer review.
  Paste the body into the portal's "What revisions did you make?" box once the article
  unlocks (>= 2 completed reviews). Keep in sync with manuscript-cureus.md.
-->

# Response to peer review — "Large Language Models as Systems Architects" (article 21832)

We thank the reviewer for a careful and constructive read. Reviewer Beta recommended
**Accept with Minor Revisions**. All requested points are addressed below; every change is a
clarification or an added discussion paragraph — no results changed and no re-analysis was
required.

## Reviewer Beta

### 1. Scope and generalizability of the architecture consensus (Section 4.1)

Added a paragraph to *Architectural consensus* stating that, with a single hardware instrument,
we cannot fully separate constraint-forced consensus from host-independent consensus, and that a
sweep across hardware envelopes is the natural follow-up. The paragraph splits the structural
agreements into two groups: (a) constraint-shaped — one resident heavy model, one concurrent
heavy-inference slot, model swapping, "100 agents" as cheap state — which would relax on a
larger machine; and (b) standard distributed-systems practice independent of memory size —
coordinator/worker over swarm, durable queue with leases/checkpoints, evidence-first pipeline,
dedicated non-admin user with workspace isolation, Tailscale-only networking, launchd +
watchdog supervision — which we expect to transfer to server/cluster deployments.

### 2. Rater filtering and reliability reporting (Section 3.3)

Added a paragraph to *Rater procedure and inter-rater agreement* clarifying that the discarded
Perplexity run participated **only** in the clean D3/D4 re-run (as one of its two fresh raters)
and was never part of the four-rater pass, so it enters no agreement statistic. All reported
inter-rater figures — pairwise quadratic-weighted Cohen's kappa 0.64, Gwet's AC1 0.73,
Krippendorff's ordinal alpha 0.20 (canonical pair) / 0.12 (all four) — are computed over the
author-derived baseline, GPT-5.6 Sol, Grok 4, and the DeepSeek chat run, and are unchanged by
the exclusion. The canonical D3/D4 levels come from the surviving clean-packet rater
(GPT-5.6 Sol); recomputing the canonical-pair agreement on the clean D3/D4 scores keeps tool
factuality in the reliable band (per-dimension kappa 0.66–0.70) with the top and bottom
performance bands unchanged. The released `analysis/scripts/agreement.py` regenerates every
figure from the scored packets, so the effect of including or excluding any rater can be
verified directly.

### 3. Sensitivity of the memory-budget floor (Sections 3.5 & 4.4)

Added a paragraph to *Memory-budget estimation* and a cross-reference in *Constraint reasoning*.
The ~11.5 GB non-model reserve is a desktop-macOS figure; a headless Linux host or a stripped
macOS profile with no window server removes roughly 3–4 GB, putting the reserve near 6–8 GB and
raising the fit ceiling by about the same amount. We now report the "fails to fit" verdicts
against both the 11.5 GB reserve and a 7 GB lower bound. The two explicit violations in the
corpus (the ~32–34 GB always-loaded design; the three-instance co-resident worker pool) exceed
32 GB on weights alone, before any reserve or KV cache, so they hold under either assumption.
Only the borderline "tight but feasible" one-large-MoE-plus-small-dense designs move, gaining a
comfortable margin under the leaner reserve.

### 4. Repository integrity (minor)

Confirmed. The public repository already contains all standard-library checking scripts
(`analysis/scripts/agreement.py`, `consensus_split.py`, `memory_budget.py`,
`validate_matrix.py`), the exact 39-axis matrix (`data/decisions-matrix.csv` plus its schema),
and the raw scoring packets and per-rater score CSVs (`analysis/scoring/`). No change needed;
these are part of the archived release.

### 5. Reference check (minor)

The reference list itself was made fully peer-reviewed during the editorial revision (no
preprints; all DOIs verified to resolve). For the verification register that is published as an
appendix, we will re-check that every post-cutoff tool pointer still resolves and is uniformly
formatted at the proof stage.
