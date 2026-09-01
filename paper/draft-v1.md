<!--
  paper/draft-v1.md — working draft of the meta-study paper (Option 1 in docs/paper-options.md).
  Status: DRAFT. Numbers are pulled from the repo artefacts named inline; if an artefact changes,
  update the corresponding sentence here in the same PR. Not yet submitted anywhere.
-->

# LLMs as Systems Architects: A Controlled Study of Consensus, Fabrication, and Constraint Reasoning on One Hard Design Task

**Draft v1 — 2026-09-01.** Data, prompts, rubric, per-rater scores and checking scripts:
`github.com/roshanaryal1/llm-architecture-eval`.

---

## Abstract

We give thirteen captures from eleven frontier LLM systems one identical, evidence-demanding
prompt — *design a 24/7 autonomous AI development-and-research workstation for a 32 GB Apple M6
Mac mini* — and characterise empirically where the models agree, diverge, and fail on an
open-ended task that has **no single ground-truth answer** but many **falsifiable sub-claims**.

Four findings stand out. (1) **Architectural convergence despite implementation disagreement:**
across 39 decision axes the systems converge almost unanimously on the *shape* of the machine
(one large model resident at a time, coordinator/worker topology, durable SQLite state,
Apple-Silicon-native inference, private-network remote access, least-privilege isolation) while
splitting on the *products* that realise each choice. (2) **LLM-as-rater training-cutoff bias:**
our first rater — itself an LLM — flagged 14 tools and models as hallucinated; on web
verification **zero were confirmed fabricated** and at least twelve are real releases dated
*after that rater's training cutoff*. The false positives cluster on the responses that were most
up to date. (3) **Citation quantity is anti-correlated with citation quality:** the response with
the largest reference apparatus (99 numbered URLs) is the least reliable (~60 % junk links),
while the responses that score highest on citation quality cite fewer, resolving, primary
sources. (4) **Reasoning mode dominates model identity:** the only system we captured in multiple
modes moves a full grounding-and-fabrication tier between its fast and its deep-reasoning mode,
holding weights and prompt fixed.

We release the full corpus, a nine-dimension rubric, four independent rater score sets with
inter-rater agreement (Cohen's κ_w = 0.64; Krippendorff's α = 0.20), a stdlib memory-budget
checker, a web-verified tool/model register, and the synthesised reference architecture the
corpus supports.

---

## 1. Introduction

Closed benchmarks dominate LLM evaluation: a task with a hidden answer key, a scalar score, a
leaderboard. Systems architecture is not that. Given a hardware envelope and a requirements list,
there is no single correct design — but there are many claims inside any proposed design that are
individually checkable: *does this model fit in 32 GB? does this tool exist? does this version
number resolve? does the response contradict itself?*

This paper treats "design a hard system under a fixed consumer-hardware constraint" as an LLM
task and measures it. The task is deliberately adversarial to weak models in specific ways: the
hardware is new (the Apple M6 Mac mini was announced 2026-08-25, six days before the study), the
memory ceiling (32 GB unified) is tight enough that a single wrong model choice breaks the
design, and the prompt explicitly asks for sources and for a list of things *not* to build.

Our contributions:

- A **reusable protocol** for evaluating open-ended architecture responses: verbatim capture,
  structured extraction into a 39-axis decision matrix, a nine-dimension 0/1/2 rubric, multi-rater
  scoring with reported agreement, and automatable falsifiable-sub-claim checks.
- An empirical **consensus map** across eleven systems (§4).
- A characterisation of **fabrication** on this task that turns out to be mostly a
  characterisation of **the LLM rater** (§5).
- **Constraint-reasoning** and **recency** results, including a memory-fit checker that every
  real response's co-resident model set fails (§6, §7).
- A **citation-quality** analysis (§8) and a **reasoning-mode sensitivity** result (§9).
- The **synthesised reference architecture** (§10) and a frank **threats-to-validity** section
  (§11) that includes a methodological error we made and its fix.

---

## 2. Related work

**LLM evaluation on open-ended tasks.** Most agentic benchmarks (SWE-bench, Terminal-Bench,
WebArena) score against an execution oracle. Design/architecture tasks lack one; prior work here
is largely qualitative case studies. We borrow the "score only falsifiable sub-claims + measure
consensus" stance from systematic-review methodology (PRISMA-S, Cochrane; see
`docs/deep-research-methodology.md`).

**Hallucination and citation fabrication.** Studies of fabricated citations in LLM output
(reference-hallucination taxonomies) motivate our RQ5 categories: does the cited artefact exist,
does it resolve, does it support the claim, is it primary or secondary. Our RQ2 result adds a
failure mode specific to *using an LLM as the checker*: the checker's own cutoff manufactures
false positives.

**LLMs for code and infrastructure.** Line-level and repo-level code generation is well studied;
whole-system design under resource constraints is not. The closest analogue is capacity-planning
and "rightsizing" work, which is human-expert-driven.

---

## 3. Task and protocol

### 3.1 The instrument

`prompts/prompt-v1.md`, frozen. A responder-context header fixes the date at 2026-08-31, asks the
model to declare browsing state and version, and requests a Sources list; the task body asks for
a 24/7 autonomous dev-and-research workstation on a **32 GB Apple M6 Mac mini** (12-core CPU,
dual 16-core Neural Engine, 170 GB/s memory bandwidth, 512 GB internal + 1 TB external SSD),
coordinating "100+ logical agents without running 100 LLMs", remotely controllable, securely
sandboxed; and asks for deliverables A–K including an exact install plan and a "what NOT to
install" list.

Paraphrases `prompt-v2/v3` are planned but not yet run; generality is currently limited to the
v1 phrasing (§11).

### 3.2 Corpus

Thirteen captures from eleven systems (`data/systems.csv`), collected 2026-08-31:

| system | slug | base model (free tier) | notes |
|---|---|---|---|
| Anthropic | `claude-sonnet-5` | Claude Sonnet 5 (in Claude Code, browsing) | **anchor — not blind**; excluded from cross-response stats |
| Mistral | `mistral-large-3` | Mistral Large 3 (675B/41B) | — |
| OpenAI | `gpt-5` | GPT-5.6 Luna | — |
| Perplexity | `perplexity` | Sonar (auto) | — |
| Moonshot | `kimi-instant` | Kimi K3-class, Instant mode | — |
| Google | `gemini-3.1-pro` | Gemini 3.x Pro | — |
| Alibaba | `qwen-3.7-plus` | Qwen ~3.7 | — |
| Meta | `meta-llama-4` | Llama 4 (variant undisclosed) | — |
| DeepSeek | `deepseek-expert` | DeepSeek-V4-Pro, deep-reasoning mode | **canonical** DeepSeek answer |
| DeepSeek | `deepseek-instant` | DeepSeek-V4-Pro, fast mode | mode-variant (RQ2/RQ6 only) |
| DeepSeek | `deepseek-instant-deepthink` | DeepSeek-V4-Pro, Instant+DeepThink | mode-variant (RQ2/RQ6 only) |
| xAI | `grok-4` | Grok 4 | — |
| Zhipu | `z-ai` | GLM-4.6/4.7-class (undisclosed) | — |

**Counting rule.** RQ1 (consensus) counts **one canonical column per system → 10 non-anchor
systems**. RQ2/RQ6 use all **13 captures**, because the three DeepSeek modes are a within-model
sensitivity measurement no other vendor gave us.

**Anchor caveat.** `claude-sonnet-5` ran inside the same tool used to build this repository, with
live browsing and partial authorship of the requested response format. It is retained as the
consensus anchor and the only sourced baseline, and excluded from every independent-sample
aggregate.

### 3.3 Extraction and scoring

Per capture: a verbatim `## Raw response` (never edited post-merge except a dated correction
note), the model's own `## Model's own cited sources`, and `## Reviewer notes`; plus one short
phrase per decision axis in `data/decisions-matrix.csv` (39 axes, `docs/comparison-axes.md`).

Scoring: `docs/rubric.md`, nine dimensions each 0/1/2 — hardware-constraint adherence, recency,
tool factuality, model factuality, benchmark factuality, citation quality, actionability,
security model, internal consistency. Four independent raters (§9.3). Falsifiable sub-claims are
checked and recorded verbatim: tool/version existence against a registry/repo fixed to the
capture date (`analysis/verification/tool-model-register.md`); memory fit via
`analysis/scripts/memory_budget.py`.

---

## 4. RQ1 — Consensus

`analysis/consensus/consensus-matrix.md` gives the full 39-axis table (counts over the 10
non-anchor systems). The pattern:

### 4.1 Near-unanimous — the *shape* of the machine

Unanimous or near-unanimous (9–10 / 10):

- **Apple-Silicon-native inference** as the primary path (MLX family), with llama.cpp/Ollama
  compatibility — 10/10. *(Product-level split is real: mlx-lm, Ollama-MLX, llama.cpp+MLX,
  vLLM-MLX all appear.)*
- **One large model resident at a time**; small models optional/on-demand — 9/10. The lone
  outlier proposes 2–3 co-resident instances and is separately shown to violate the memory
  budget (§6).
- **Model swapping** with anti-thrash/load policy — 10/10.
- **Custom supervisor + thin integration** with specialist runtimes, *not* one mega-framework —
  10/10.
- **Hierarchical coordinator/worker**, explicitly not a swarm — 10/10.
- "**100 agents = cheap state/config**", not 100 resident LLMs — 10/10.
- **One concurrent heavy-inference slot** — 9/10.
- **Evidence-first research pipeline** (search → retrieve → extract → verify → contradiction →
  synthesise) with a **stored evidence ledger** and final prose generated only from verified
  evidence — 10/10.
- **SQLite + filesystem as day-one memory**; defer vector/graph complexity — 10/10 / 9/10.
- **Defer a knowledge graph** until multi-hop/temporal need is demonstrated — 10/10.
- **Dedicated non-admin user + workspace isolation** as the security boundary — 10/10.
- **Tailscale-only private network**, no public exposure — 10/10; small private
  dashboard/API — 10/10.
- **launchd + KeepAlive + independent watchdog** — 10/10; `caffeinate`/`pmset` on AC — 10/10;
  **durable queue + leases/checkpoints + requeue (never replay destructive actions)** — 10/10.
- **32 GB unified memory is the bottleneck** (capacity/bandwidth/KV growth), not CPU/GPU
  compute — 10/10.
- **1 TB external SSD is cold/bulk storage**, not the latency-critical disk — 10/10.

### 4.2 Genuine splits — the *products*

No majority; recorded as adjudication points, not facts (`analysis/consensus/disagreements.md`):

| axis | positions |
|---|---|
| heavy local model | Qwen3-Coder-30B-A3B (4/10) · Qwen2.5-Coder-32B dense (2) · Qwen3.6-35B-A3B (1) · Qwen 27B/35B family (Grok) · fabricated/incorrect variants (Llama, z.ai) |
| inference server product | mlx-lm · Ollama-MLX · llama.cpp+MLX · vLLM-MLX |
| orchestration substrate | LangGraph · PydanticAI · Claude Agent SDK · plain asyncio (5/10 "no framework wins") |
| coding executor | Aider (7/10 git-native layer) · OpenHands (autonomous co-primary) · Claude Code · OpenCode |
| vector store | sqlite-vec (4/10) · ChromaDB (4) · Qdrant-embedded (1) · LanceDB (1) — but "no standalone vector daemon initially" is 8/10 |
| sandbox implementation | dedicated-user-only · Seatbelt · Docker/OrbStack · Lima VM · Apple `container` |
| task queue | SQLite WAL (8/10) · Redis(+Celery) (2) |
| cloud dependence | optional burst, local core useful at $0 (8/10) · pure-local main strategy (2) |
| monitoring | minimal/custom (most) · Prometheus+Grafana (2) |

**The RQ1 result** is that the models agree on constraints and topology and disagree on
implementation at the boundary of those constraints. That separates robust architectural
principles from fast-moving product preference more cleanly than a superficial majority vote
would.

---

## 5. RQ2 — Fabrication, and the rater that manufactured it

### 5.1 What we found first

Our first rater (an LLM with a ~January 2026 training cutoff) audited every capture and flagged
**14 tools/models** across five responses as fabricated — most heavily in the two DeepSeek fast
modes and in Meta/Llama 4. We drafted a "cross-vendor shared hallucination" finding around
`Rapid-MLX` and `Gemma 4`, each named by three vendors.

### 5.2 What web verification showed

Verifying every flag against 2026 web sources (`analysis/verification/tool-model-register.md`):

| flagged as fabricated | verdict | evidence (2026) |
|---|---|---|
| `Rapid-MLX` (3 vendors) | **real** | `github.com/raullenchai/Rapid-MLX`, ex vLLM-MLX, renamed 2026-03 |
| `Gemma 4` 26B / 31B / 12B (3 vendors) | **real** | released 2026-04-02; 26B-A4B MoE + 31B dense + 12B unified are all real variants |
| `DeepSeek Harness` / `DSH` | **real** | `github.com/deepseek-ai/deepseek-harness`, open-sourced 2026-08-13, MIT |
| `OpenClaw` | **real** | Steinberger; ex Warelay → Moltbot → OpenClaw; Wikipedia page |
| `Claw Code` | **real** | clean-room Claude Code rewrite after the 2026-03-31 source-map leak; ~72k stars |
| `Clawtrol` | **real** | `github.com/wolverin0/clawtrol` |
| `Ornith-1.0-9B` | **real** | `huggingface.co/deepreinforce-ai/Ornith-1.0-9B`; Ollama `ornith:9b` |
| `WhipDesk` | **real** | `github.com/BinaryBananaLLC/WhipDesk` |
| `LightAgent` | **real** | `github.com/wanxingai/LightAgent`; arXiv 2509.09292 |
| `nono` | **real** | Landlock/Seatbelt sandbox tool |
| `GLM-4.7-Flash` (30B-A3B) | **real** | Zhipu, 2026-01-19, 30B-A3B MoE |
| `Qwen3-Coder-Next` (referenced) | **real, 80B MoE** | `huggingface.co/Qwen/Qwen3-Coder-Next` |
| `Helmrig`, `Cloak`, `DiffResearch`, `cplt`, `memo`, `agent-policy-engine`, `pi-search-hub` | **unresolved** | no web evidence either way — **not** counted as fabrication |

**Zero of 14 confirmed fabricated. At least twelve are real releases dated after the rater's
cutoff.** The false positives cluster precisely on the *most current* responses: the rater
penalised recency it could not verify.

### 5.3 The reframed finding

> **An LLM used as an evaluator of technical currency systematically misclassifies real
> post-cutoff artefacts as hallucinations.** On this corpus the false-positive rate on
> "fabrication" flags was 100 % (14/14), concentrated on the responses that engaged the newest
> ecosystem.

This is a hazard for any pipeline that uses an LLM to judge the factuality of another LLM's
technical claims. The mitigation we adopted: dims 3 and 4 of the rubric now **require the rater
to web-verify each name before scoring**, and "not in my training data" scores 1 (unresolved),
never 0.

The failure mode also reproduces *in a rater given exactly that instruction*. In a clean
re-scoring of dims 3–4 (§9.3), one of two fresh raters (Perplexity) scored "tool factuality" = 0
for seven responses by treating *its own search misses* as evidence of non-existence — its
"could not resolve" list contained `Rapid-MLX`, `OpenClaw`, `Clawtrol`, `nono`, `Ornith-1.0-9B`,
`DeepSeek Harness` and `Gemma 4 31B/12B`, every one of which the other fresh rater (GPT-5.6 Sol)
resolved to a real repository or model card on the same task. We discard that rater's scores; it
is a live demonstration that "not found by my search" collapses to "does not exist" unless the
rubric and the rater actively resist it.

### 5.4 Defects that survive verification

RQ2 is not empty. These are real and stay in the analysis:

| response | defect | type |
|---|---|---|
| `z-ai` | `Qwen3-Coder-Next` given as "8B / ~5 GB" — real model is 80B MoE; it is the load-bearing primary coding pick | model-attribute error |
| `z-ai` | same model quoted at 5 GB and 14 GB; 3-instance co-resident diagram vs on-demand prose | internal inconsistency |
| `grok-4` | none — states the full M6 spec incl. 170 GB/s correctly; alt-list picks all real | (no surviving factual defect; only 0 sources) |
| `meta-llama-4` | "M6 ≈ 300+ GB/s" (real: 170); ~60 % of 99 citation URLs are junk; same tool given multiple repo URLs; `[38]` mis-titles a real arXiv paper | spec error + citation quality |
| `z-ai` | `GLM-4.5-Air` treated as a ~4 GB fast-utility model — official spec is 106B total / 12B active | model-attribute error |
| `deepseek-expert` | recommends Docker in one section, forbids "Docker for Mac" in the "do not install" list; binds a dashboard to `0.0.0.0` while claiming "no public exposure" | internal contradiction |
| `deepseek-expert` | future primary model `Qwen3-Coder-70B` does not exist (the Qwen3-Coder line is 30B-A3B, 480B, and the separate 80B Coder-Next) | model fabrication (future pick) |
| `deepseek-instant` | recommends Ollama in Phase 4, forbids it in the "do not install" list | internal contradiction |
| `deepseek-instant-deepthink` | 256K-context claim vs a 1–2 GB KV budget; advocates ~32–34 GB always-loaded ("slight oversubscription acceptable") | hardware violation |
| `deepseek-instant-deepthink` | upgrade path describes DeepSeek-V4 as a dense model needing 96–128 GB — V4-Pro / V4-Flash are MoE (1.6T/49B-active; 284B/13B-active) | model-architecture error |

*(The `Qwen3-Coder-70B`, DeepSeek-V4-architecture and GLM-4.5-Air rows were surfaced by the clean
dims-3/4 re-run, §9.3.)*

The corrected picture: the low-scoring responses are low-scoring for **verifiable** reasons —
contradictions, a load-bearing size error, memory oversubscription, junk citations — not for
inventing an ecosystem.

---

## 6. RQ3 — Constraint reasoning

`analysis/scripts/memory_budget.py` (stdlib) estimates weights + KV cache for a response's
*co-resident* model set (what it says stays loaded) against 32 GB, with presets for each capture.

**Every real response's stated co-resident set fails to fit**, once macOS, a headless browser, a
Python worker pool, SQLite/indexes and a realistic KV cache are counted alongside the weights:

- Designs that keep **one** large MoE resident (Qwen3-Coder-30B-A3B ≈ 17–20 GB @ 4-bit) plus a
  small dense model swapped in are *tight but feasible* — several responses say so explicitly and
  reserve a 2–6 GB floor (perplexity, mistral, kimi).
- Designs that keep **two** large models resident, or a dense 32B plus a helper, exceed the
  ceiling at working context lengths.
- `deepseek-instant-deepthink` is the clearest violation: ~32–34 GB of always-loaded weights
  before OS/browser/KV, with the text calling oversubscription "acceptable". `z-ai`'s
  three-instance worker-pool diagram (Qwen3-Coder + GLM-4.5-Air + Mistral Small co-resident) plus
  "fits within 32 GB with swapping" is the second.

**Scoring (adjudicated, dim 1):** 2 → perplexity, mistral, kimi, grok-4; 1 → claude, gpt-5,
gemini, qwen, deepseek-expert, deepseek-instant, meta-llama-4; 0 → z-ai, deepseek-instant-deepthink.
Inter-rater κ on this dimension is the lowest of the nine (0.15) — "sums to exactly 32 GB with no
reserved margin" was scored 1 by one rater and 2 by another. The v2 rubric fixes this: a 2
requires a **named free-RAM floor**.

---

## 7. RQ4 — Recency

The M6 facts, web-verified: announced **2026-08-25**, **170 GB/s** memory bandwidth at
24–32 GB (153 GB/s at 16 GB), 32 GB maximum unified memory. Against that:

| tier | responses | character |
|---|---|---|
| current + M6-aware + sourced | `perplexity`, `mistral-large-3` (+ anchor `claude-sonnet-5`) | engage the real M6 spec, hedge every throughput number, cite |
| current picks, no usable sources | `gpt-5`, `grok-4`, `kimi-instant`, `gemini-3.1-pro`, `qwen-3.7-plus`, `meta-llama-4` | real 2026 tool/model picks; 0 usable sources (gpt-5: inline attributions, 0 URLs). `qwen`/`gemini` also carry a ~12–18-month model lag; `meta` also has the 170-vs-300 GB/s error |
| behind on models | `qwen-3.7-plus`, `gemini-3.1-pro` (partly `deepseek-expert`) | Qwen2.5-generation primaries, stale cloud-fallback lists (Claude 3.5 Sonnet / GPT-4o), no M6 engagement |

**Only `meta-llama-4` got a hard M6 fact wrong** ("~300+ GB/s"); `grok-4` — which our first rater
mistakenly grouped with it — states 170 GB/s correctly.

Recency correlates with (a) retrieval/browsing and (b) *not being penalised by a stale rater* —
§5. It does **not** cleanly predict agreement with the cross-model consensus: several
consensus-aligned responses are unsourced, and one behind-on-models response (`gemini`) is
internally clean and consensus-shaped.

---

## 8. RQ5 — Citation quality

Only the anchor and four non-anchor responses cite anything resolvable.

| response | apparatus | resolves? | supports? | primary? |
|---|---|---|---|---|
| `claude-sonnet-5` (anchor) | ~97 URLs | mostly | mostly | mostly primary |
| `perplexity` | ~17 URLs | mostly | mostly | mixed (some aggregator mirrors; 2 arXiv IDs unverified) |
| `mistral-large-3` | ~36 credibility-rated, dated entries | mostly | yes | mixed (~6 are `google.com/search` URLs) |
| `gpt-5` | ~20 inline attributions, **0 URLs** | n/a | attributions are to real docs | n/a |
| `meta-llama-4` | **99 numbered URLs** | ~40 % | patchy | mostly secondary; commits/PRs/`SKILL.md` |
| all others | none | — | — | — |

**Citation count is anti-correlated with citation quality on this corpus.** `meta-llama-4` has
the largest apparatus and the worst — ~60 % junk links, the same tool given several different
repo URLs, and one real arXiv URL under the wrong paper title. `gpt-5` cites zero URLs but every
inline attribution ("Apple officially announced…", "OpenHands docs recommend…") points at a real,
checkable source.

**Consequence for evaluation design:** "has a Sources section" must not be used as a proxy for
"is grounded". Scoring it that way ranks `meta-llama-4` above `gpt-5` — backwards. Dim 6 of our
rubric scores a mostly-junk apparatus as 0, and it is the **cleanest single separator** in the
adjudicated scores: the top four responses score 2/2/2/0 on it, every other response scores 0.

---

## 9. RQ6 — Internal consistency, and reasoning-mode sensitivity

### 9.1 Internal contradictions

Material self-contradictions in 3 of 13 captures:

- `deepseek-expert` and `deepseek-instant` each recommend a tool (Docker; Ollama) that their own
  "do not install" list forbids.
- `z-ai` gives one model two different memory sizes (5 GB vs 14 GB) and pairs "primary model
  stays loaded, others on demand" with a three-instance co-resident diagram.
- `meta-llama-4`'s prose is coherent but its citation apparatus is not (same tool, multiple repo
  URLs; wrong title on a real paper).

### 9.2 The DeepSeek mode effect

DeepSeek is the only system captured in more than one mode — three captures, one base model
(DeepSeek-V4-Pro), three chat modes (`analysis/deepseek-modes.md`):

| mode | grounding | internal defects | adj. /18 |
|---|---|---|---:|
| deep-reasoning (`deepseek-expert`) | real tools; but a non-existent future model (`Qwen3-Coder-70B`) and an unresolved `DeepSeek-Coder-V3` | Docker recommend-then-forbid | 8 |
| fast (`deepseek-instant`) | real tools + real models, all post-cutoff | Ollama recommend-then-forbid | 9 |
| Instant+DeepThink (`deepseek-instant-deepthink`) | real tools; DeepSeek-V4 mislabelled dense | memory oversubscription, 256K-ctx-vs-KV | 6 |

Holding weights and prompt fixed, **the reasoning mode changes the output category**: the two
fast modes and the deep mode span three of the rubric's coarse tiers. The effect is *not
monotone across every dimension* — after the clean dims-3/4 re-run (§9.3), `deepseek-instant`
(9/18) actually scores *above* `deepseek-expert` (8/18), because the deep mode's more elaborate
upgrade path reached for future models that do not exist while the fast mode's picks all
resolved. "Which DeepSeek model" is the wrong question; "which mode" is the right one, and the
answer is dimension-dependent. A controlled N-mode re-run is the obvious follow-up.

### 9.3 Inter-rater agreement

Four raters scored all 13 captures on the nine dimensions
(`analysis/scoring/rater-agreement-2026-09-01.md`):

| rater | mean total / 18 |
|---|---:|
| rater-1 (this study, from reviewer notes, corrected basis) | 12.7 |
| GPT-5.6 Sol (ChatGPT, paid, web search) — **canonical rater-2** | 11.1 |
| Grok 4 (+ web verification) | 13.8 |
| DeepSeek chat run | 14.7 |

Canonical pair (rater-1 vs GPT-5.6 Sol), 117 paired ratings:

| metric | value |
|---|---|
| exact agreement | 68.4 % |
| within 1 point | 96.6 % |
| Cohen's κ (unweighted / quadratic-weighted) | +0.49 / **+0.64** |
| Krippendorff's α (ordinal) | +0.20 (pair), +0.12 (all four) |

Per-dimension: **reliable** — recency (κ 0.68), tool factuality (0.70), benchmark factuality
(0.66); **weak** — citation quality (0.30), security model (0.32), actionability (0.36), and the
two worst, hardware-constraint (0.15) and internal-consistency (0.14). The weak dimensions share
a fuzzy 0/1 or 1/2 boundary ("has commands" vs "has rollback too"; "acknowledges 32 GB" vs
"reserves a floor"); the v2 rubric adds hard anchors for each.

Two agreement results matter beyond the numbers:

1. **Raters have a severity personality.** The same rubric on the same responses produces an
   8.5 → 14.7 / 18 spread across four LLM raters; the DeepSeek run assigned 2 on five dimensions
   almost uniformly (a low-information rater). LLM-as-rubric-rater is not a portable instrument
   without anchored exemplars.
2. **The rank order is stable even though the levels are not** (within-1 agreement 97 %). The
   adjudicated ranking (§10) is robust; the absolute totals are not, and should be reported with
   the per-dimension κ, never as a single headline number.

**Clean dims-3/4 re-run.** Because the packet used in the four-rater pass had leaked a list of
real post-cutoff tools (§11), we re-scored dimensions 3 and 4 with an uncontaminated packet
(names nothing; forbids reading the verification register; mandatory web verification;
`unresolved → 1`). The canonical rater (GPT-5.6 Sol) reproduced its contaminated D3/D4 on **11 of
13 responses**; the two changes (`meta-llama-4` D4 1→2, `deepseek-instant-deepthink` D4 2→0) were
driven by specific web findings, not by removing the leak. Four further cells moved on new
findings surfaced by the clean pass — `mistral` D3 2→1 (`brew install goose` installs the wrong
formula), `kimi` D3 2→1 (`opencode config set model` is not a real command), `deepseek-expert`
D4 2→1 (`Qwen3-Coder-70B` does not exist), `deepseek-instant-deepthink` D4 1→0 (DeepSeek-V4
mislabelled dense) — and are folded into §10.1. **Net: the leak's measured effect on the
reported scores is small; the ranking bands are unchanged.**

---

## 10. Synthesised reference architecture and adjudicated ranking

### 10.1 Adjudicated rubric totals (non-anchor, / 18)

Adjudicated after the clean dims-3/4 re-run (§9.3):

| rank | response | total | one-line |
|---:|---|---:|---|
| 1 | `perplexity` | 18 | quantified budget with a reserved floor; refuses to fake M6 numbers; most security-thorough; the only response to score 2 on every dimension |
| 2 | `mistral-large-3` | 15 | explicit methodology/limitations/open-questions; rated, dated sources; loses a point on a wrong `brew install goose` path |
| 3 | `gpt-5` | 14 | all picks real and current; strong epistemic discipline; loses points for 0 URLs and a memory table that touches the ceiling |
| 3 | `grok-4` | 14 | M6 spec correct incl. 170 GB/s; consensus-aligned real picks, all web-verified; only defect is 0 sources |
| 5 | `gemini-3.1-pro` | 12 | real tools, clean plan, explicit permission matrix; ~12–18-month model lag, 0 sources |
| 5 | `qwen-3.7-plus` | 12 | honest 2024-snapshot answer; dense-32B primary, 0 sources |
| 7 | `kimi-instant` | 11 | real tools, reserved RAM floor; number inflation, a wrong `opencode` command, 0 usable sources |
| 7 | `meta-llama-4` | 11 | aggressively current real ecosystem; M6 bandwidth wrong; largest and worst citation apparatus |
| 9 | `deepseek-instant` | 9 | real (post-cutoff) picks, all resolve; Ollama recommend-then-forbid; 0 sources |
| 10 | `deepseek-expert` | 8 | best-*grounded* DeepSeek mode on tools, but names a non-existent future model (`Qwen3-Coder-70B`); Docker recommend-then-forbid; 0 sources |
| 11 | `deepseek-instant-deepthink` | 6 | real picks; DeepSeek-V4 mislabelled dense; advocates memory oversubscription; 0 sources |
| 12 | `z-ai` | 5 | consensus-shaped but a load-bearing model-size error (Qwen3-Coder-Next 8-vs-80B; GLM-4.5-Air 4 GB-vs-106B), a 5-vs-14 GB self-contradiction, relies on swap, no M6 facts |

Anchor `claude-sonnet-5`: 15 (excluded from the ranking). Movement vs the pre-re-run table:
`mistral` 16→15, `kimi` 12→11, `deepseek-expert` 9→8, `deepseek-instant-deepthink` 7→6; band
structure unchanged.

### 10.2 The architecture the corpus supports

From `analysis/consensus/reference-architecture.md` (majority positions + adjudicated calls):

- **Inference:** one MLX-family runtime behind an internal adapter; **one large MoE resident**
  (Qwen3-Coder-30B-A3B-class, 4-bit, ≈ 17–20 GB) + one small dense model swapped in on demand;
  never two large models co-resident. Benchmark the chosen runtime on the actual M6 before
  trusting any throughput claim.
- **Agents:** 100+ agents as SQLite rows / definition files; **hierarchical coordinator/worker**;
  one concurrent heavy-inference slot + 2–3 small/tool workers.
- **Orchestration:** a thin custom Python supervisor owns task state and scheduling; a framework
  (LangGraph / PydanticAI) may implement selected stateful workflows but stays replaceable
  `[adjudicated]`.
- **Coding execution:** capability-tiered — Aider for git-native interactive edits, OpenHands in
  a container for autonomous multi-step jobs `[adjudicated]`.
- **Research:** evidence-first pipeline; every claim traces to a stored snippet; a second-pass
  verification agent re-opens sources; contradiction pass; synthesise only from the verified
  ledger.
- **Memory:** filesystem Markdown + SQLite (+ FTS) day one; `sqlite-vec` for embedded vectors
  `[adjudicated]`; no standalone vector daemon and no knowledge graph until a real need is
  demonstrated.
- **State/recovery:** SQLite WAL task queue + leases/checkpoints; requeue interrupted work; never
  replay destructive actions.
- **Security:** dedicated non-admin macOS user + workspace isolation; capability tiers
  (autonomous / notify-log / approve / never) + kill switch + per-task runaway limits; secrets in
  Keychain, never in the agent tree. Stronger sandboxing (container/VM) is capability-scoped to
  untrusted code, not a universal prerequisite `[adjudicated]`.
- **Always-on:** launchd KeepAlive + a separate watchdog + `caffeinate`/`pmset` on AC.
- **Remote:** Tailscale-only, zero inbound ports; a small FastAPI dashboard/API on the tailnet;
  approvals through the dashboard, never SSH-to-approve.
- **Storage:** internal SSD for OS/runtime + hot working state (+ preferably hot weights);
  external SSD for the model library, research corpus, datasets and backups.
- **Cloud:** an explicit policy-gated escape hatch (privacy class + confidence + budget), not a
  hidden dependency; the system must remain useful at $0 cloud spend `[adjudicated]`.

The **32 GB unified-memory ceiling is a hard engineering constraint, not a target to fill** —
reserve a measured RAM floor.

---

## 11. Threats to validity

- **n = 1 base prompt.** Generality is limited to the v1 phrasing. Paraphrase re-runs
  (`prompt-v2/v3`) and a second hardware spec are the mitigation and are not yet done.
- **Anchor contamination.** `claude-sonnet-5` is not blind (built the repo, browsing on, partial
  format authorship). Handled by exclusion from every cross-response aggregate; reported
  separately.
- **The evaluator is an LLM.** Both the first rater and two of the three second raters are LLMs.
  §5 is a direct demonstration of the risk (training-cutoff false positives). Mitigations:
  mandatory web verification for factual dimensions; a human-authored rubric; four raters with
  reported agreement; every falsifiable sub-claim recorded verbatim.
- **We leaked part of the answer key — effect measured and small.** An intermediate version of
  the rater packet listed the 12 real-but-post-cutoff tools while instructing raters to treat
  them as real; all three four-rater-pass second-rater runs saw it. We ran a clean re-scoring of
  the affected dimensions (3 and 4) with an uncontaminated packet (§9.3). The canonical rater
  reproduced its contaminated D3/D4 on **11 of 13 responses**; its two changes were driven by
  fresh web findings, not by the missing list. Four further cells moved on newly-surfaced
  findings and are folded into §10.1. Dimensions 1, 2, 5–9 were never contaminated. The leak
  remains a real defect in method — one rater was contaminatable in principle — but its effect on
  the reported scores is now bounded by evidence rather than assumed. The packet is fixed for
  future raters ("web-verify yourself; do not read the verification register before scoring").
- **Rater severity variance** (§9.3): ~3.6 / 18 across four raters. Report per-dimension κ, not a
  single headline score.
- **Self-scoring.** `grok-4` scored the `grok-4` response (16/18); the DeepSeek run scored the
  three DeepSeek responses (15/15/15). Noted, not corrected; both are variance-check raters, not
  canonical.
- **rater-1 is not design-independent** — it wrote the rubric and the reviewer notes. That is why
  a canonical rater-2 exists; the adjudicated column is the reportable one.
- **Model churn.** Every capture is a dated snapshot (2026-08-31). Free-tier defaults and the
  underlying models will have moved by publication.
- **DeepSeek modes are one system.** The mode-effect result (§9.2) is n = 1 system; it motivates
  a controlled multi-mode experiment, it does not establish a general law.

---

## 12. Release

`github.com/roshanaryal1/llm-architecture-eval` — MIT (code) / CC-BY-4.0 (data):

- `prompts/prompt-v1.md` — the frozen instrument
- `data/responses/*.md` — 13 verbatim captures + front-matter + per-capture reviewer notes
- `data/decisions-matrix.csv` — 39 axes × 13 columns
- `data/systems.csv` — slug → system → canonical mapping
- `docs/rubric.md`, `docs/methodology.md`, `docs/comparison-axes.md` — the protocol
- `analysis/verification/tool-model-register.md` — web-verified tool/model verdicts
- `analysis/scoring/` — four rater score sets + `agreement.py` + the adjudication report; the
  clean dims-3/4 re-run (`RATER-PACKET-D3D4.md`, `d3d4-*`, `d3d4-clean-rerun-result.md`);
  `scores-adjudicated-2026-09-01.csv` (the reportable table)
- `analysis/scripts/memory_budget.py`, `validate_matrix.py` — the checkers
- `analysis/consensus/` — the consensus matrix, disagreement ledger, and reference architecture

---

## 13. Conclusion

Asked to design the same constrained machine, eleven frontier LLM systems agree on what the
machine *is* — a memory-bound, local-first, coordinator/worker workstation with durable SQLite
state and private-network control — and disagree on which specific products build it. The
disagreements are informative: they mark exactly the decisions a human engineer still has to
adjudicate.

The sharper result is about evaluation. On a task where currency matters, an LLM asked to judge
another LLM's factual grounding will penalise the newest, best-grounded answers hardest, because
the judge's own knowledge is stale. Any evaluation pipeline that puts an LLM in the grader's seat
for technical-currency questions needs an external verification step in front of it. We built one;
this paper is partly the record of discovering we needed it.
