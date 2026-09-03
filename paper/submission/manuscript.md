# LLMs as Systems Architects: A Controlled Study of Consensus, Fabrication, and Constraint Reasoning on One Hard Design Task

**Author.** Roshan Aryal
Bachelor of Information Technology (AI & Data Science), Otago Polytechnic, Auckland, New Zealand
Corresponding author: roshanaryaal@gmail.com

**Data and code availability.** All data, prompts, the rubric, the four rater score sets, the
web-verified tool/model register, the checking scripts, and the adjudicated scores are released
at <https://github.com/roshanaryal1/llm-architects> under the MIT licence (code) and
CC-BY-4.0 (data), and permanently archived at Zenodo (concept DOI
<https://doi.org/10.5281/zenodo.22245991>, which resolves to the latest version). Section and
file references of the form `analysis/...` or `data/...` in this manuscript point into that
repository, which is the paper's supplementary material.

---

## Abstract

Closed benchmarks — a hidden answer key, a scalar score, a leaderboard — dominate large
language model (LLM) evaluation, but many real tasks have no single correct answer. We treat
one such task, *designing a 24/7 autonomous AI development-and-research workstation for a 32 GB
Apple M6 Mac mini*, as an LLM evaluation problem: an open-ended design with no ground-truth
solution but many individually falsifiable sub-claims (does this model fit in 32 GB? does this
tool exist? does the response contradict itself?). We give one identical, evidence-demanding
prompt to eleven frontier LLM systems, capture thirteen verbatim responses, and characterise
where the systems agree, diverge, and fail. Four results stand out. (1) *Architectural convergence
despite implementation disagreement:* across 39 decision axes the systems converge almost
unanimously on the shape of the machine (one large model resident at a time, coordinator/worker
topology, durable SQLite state, Apple-Silicon-native inference, private-network remote access,
least-privilege isolation) while splitting on the products that realise each choice. (2)
*LLM-as-rater training-cutoff bias:* our study-internal rater — itself an LLM — flagged 14
tools and models as hallucinated; on web verification none of the 14 was confirmed nonexistent
and at least 12 are real releases dated after that rater's training cutoff. This is a rater
failure, not an absence of defects: independent verification did find genuine factual errors
elsewhere, none of them among the 14 flags. (3) *Citation quantity does not predict citation
quality:* the response with the largest reference apparatus (99 URLs) is the least reliable. (4)
*Reasoning mode produces large within-model variation:* the one system captured in multiple
modes moves a full grounding-and-fabrication tier between its fast and deep-reasoning modes with
weights and prompt fixed. We release the corpus, a nine-dimension rubric, four independently
scored rater sets (within-one-point agreement 96.6 %; quadratic-weighted Cohen's kappa 0.64,
Gwet's AC1 0.73), a stdlib memory-budget checker, a web-verified register, and the synthesised
reference-architecture recommendation the corpus supports.

**Keywords:** LLM evaluation; LLM-as-judge; training-cutoff bias; hallucination; inter-rater
agreement; prompt sensitivity; systems architecture; reproducible benchmark corpus

---

## 1. Introduction

Closed benchmarks dominate LLM evaluation: a task with a hidden answer key, a scalar score, a
leaderboard. Systems architecture is not that. Given a hardware envelope and a requirements
list, there is no single correct design — but there are many claims inside any proposed design
that are individually checkable: *does this model fit in 32 GB? does this tool exist? does this
version number resolve? does the response contradict itself?*

This paper treats "design a hard system under a fixed consumer-hardware constraint" as an LLM
task and measures it. The task is deliberately stress-inducing along several dimensions: the
hardware is new (the Apple M6 Mac mini was announced 2026-08-25, six days before the study),
the memory ceiling (32 GB unified) is tight enough that a single wrong model choice breaks the
design, and the prompt explicitly asks for sources and for a list of things *not* to build.

Our contributions:

- A **reusable protocol** for evaluating open-ended architecture responses: verbatim capture,
  structured extraction into a 39-axis decision matrix, a nine-dimension 0/1/2 rubric,
  multi-rater scoring with reported agreement, and automatable falsifiable-sub-claim checks.
- An empirical **consensus map** across eleven systems (Section 4).
- A characterisation of **fabrication** on this task that turns out to be mostly a
  characterisation of **the LLM rater** (Section 5).
- **Constraint-reasoning** and **recency** results, including a memory-fit checker showing that
  every co-resident model set a response describes as simultaneously loaded exceeds 32 GB
  (Sections 6, 7).
- A **citation-quality** analysis (Section 8) and a **reasoning-mode sensitivity** result
  (Section 9).
- The **synthesised reference architecture** (Section 10) and a frank **threats-to-validity**
  section (Section 11) that includes a methodological error we made and its fix.

The study is descriptive and exploratory: with thirteen captures it establishes patterns and
failure modes on one instrument, not population-level laws. We are explicit throughout about
which claims are corpus observations and which are candidates for generalisation.

## 2. Related work

**LLM evaluation on open-ended tasks.** Agentic benchmarks — SWE-bench and its variants [12],
WebArena [13], and others such as Terminal-Bench, OSWorld, Tau-Bench and AgentBench — all score
against an execution oracle: the task has a hidden pass/fail, and the scope has widened from
function-level generation to environment-grounded interaction, but the answer key is always
present (surveys: [1]; [2] evaluates frontier LLMs across a research lifecycle). Constrained
*design* has no such oracle. We take the "score only falsifiable sub-claims, and measure
consensus rather than correctness" stance from systematic-review methodology — PRISMA-S for
reporting a reproducible search [3], PRESS for peer-reviewing a search strategy [4], and the
National Academies' reproducibility/replicability framing [5] (all summarised in
`docs/deep-research-methodology.md`).

**LLM-as-judge and its biases.** Using an LLM to score another LLM's output is now standard and
its failure modes are catalogued: [6] and follow-ups document **position bias, verbosity bias,
self-enhancement**, and [7] reports high agreement with low validity; [8] surveys mitigation.
The standard fixes are randomised ordering, repeated runs, and **rubric-based scoring that
constrains the judge to factual criteria** — which is exactly the instrument we use. Our
Section 5 result adds a bias not on those lists: **training-cutoff recency bias** — when the
judged content is more current than the judge's own knowledge, the judge systematically emits
*false-positive fabrication flags*.

**Citation and reference hallucination.** The reference-hallucination literature gives us our
citation-quality categories and our fabrication vocabulary. [9] and [10] define the taxonomy we
reuse in the verification register — total fabrication, partial attribute corruption,
identifier hijacking, placeholder hallucination, semantic hallucination. On large URL corpora
(DRBench, ExpertQA) [9] measures 3–13 % of citation URLs outright hallucinated (no Wayback
record) and 5–18 % non-resolving, with deep-research agents worse than search-augmented LLMs.
That literature already names **temporal cutoffs (recently published content)** as a
knowledge-boundary cause of *models* fabricating citations; [11] studies four models across
five prompting regimes and finds no model exceeds a 0.475 citation-existence rate, with the
temporal-window regime the steepest drop. Our contribution is to move that same cutoff
mechanism from the *author* to the *judge*: it is not only that a model with an old cutoff
invents post-cutoff sources — it is that a *rater* with an old cutoff flags real post-cutoff
artefacts as invented.

**LLMs for code and infrastructure.** Line-level and repo-level code generation is heavily
studied (SWE-agent, AutoCodeRover, Agentless, OpenHands explore different issue-resolution
agent designs). Whole-system design under a fixed resource envelope is not — the nearest
analogue is human-expert capacity-planning / "rightsizing". We treat "produce a deployable
architecture from a hardware spec plus a requirements list" as an evaluable LLM task.

## 3. Task and protocol

We follow the reporting guidelines of Baltes et al. [14] for empirical SE studies involving
LLMs: Section 3.1 declares the LLM usage and role, Section 3.2 reports model / version /
interface / browsing state per capture, the prompts are released verbatim (Appendix A), session
provenance is recorded in each capture's front-matter, and an open-weight system is included in
the corpus. The AI-assistance declaration for the study itself is in Section 11 and the
Declarations.

### 3.1 The instrument

The frozen prompt (`prompts/prompt-v1.md`) has a responder-context header that fixes the date
at 2026-08-31, asks the model to declare browsing state and version, and requests a Sources
list; the task body asks for a 24/7 autonomous development-and-research workstation on a **32 GB
Apple M6 Mac mini** (12-core CPU, dual 16-core Neural Engine, 170 GB/s memory bandwidth, 512 GB
internal plus 1 TB external SSD), coordinating "100+ logical agents without running 100 LLMs",
remotely controllable, securely sandboxed; and asks for deliverables A–K including an exact
install plan and a "what NOT to install" list.

Two controlled variants are frozen (`prompt-v2.md`, `prompt-v3.md`): v2 is a full paraphrase
(RFC framing, reshuffled sections, no shared sentences); v3 is v1 with the anti-anchoring /
anti-popularity steer removed. Both were re-run on a five-system subset; the prompt-sensitivity
results are in Section 9.4. The matrices and rankings elsewhere in this paper are for the v1
captures.

### 3.2 Corpus

Thirteen captures from eleven systems (`data/systems.csv`), collected 2026-08-31:

| system | slug | base model (free tier) | notes |
|---|---|---|---|
| Anthropic | `claude-sonnet-5` | Claude Sonnet 5 (in an AI coding tool, browsing on) | **anchor — not blind**; excluded from cross-response stats |
| Mistral | `mistral-large-3` | Mistral Large 3 (675B/41B) | — |
| OpenAI | `gpt-5` | GPT-5.6 Luna | — |
| Perplexity | `perplexity` | Sonar (auto) | — |
| Moonshot | `kimi-instant` | Kimi K3-class, Instant mode | — |
| Google | `gemini-3.1-pro` | Gemini 3.x Pro | — |
| Alibaba | `qwen-3.7-plus` | Qwen ~3.7 | — |
| Meta | `meta-llama-4` | Llama 4 (variant undisclosed) | — |
| DeepSeek | `deepseek-expert` | DeepSeek-V4-Pro, deep-reasoning mode | **canonical** DeepSeek answer |
| DeepSeek | `deepseek-instant` | DeepSeek-V4-Pro, fast mode | mode-variant (Sections 5, 9 only) |
| DeepSeek | `deepseek-instant-deepthink` | DeepSeek-V4-Pro, Instant+DeepThink | mode-variant (Sections 5, 9 only) |
| xAI | `grok-4` | Grok 4 | — |
| Zhipu | `z-ai` | GLM-4.6/4.7-class (undisclosed) | — |

**Counting rule.** Consensus analysis (Section 4) counts **one canonical column per system → 10
non-anchor systems**. The fabrication and internal-consistency analyses use all **13 captures**,
because the three DeepSeek modes are a within-model sensitivity measurement no other vendor gave
us.

**Anchor caveat.** `claude-sonnet-5` ran inside the same tool used to build this repository,
with live browsing and partial authorship of the requested response format. It is retained as
the consensus anchor and the only sourced baseline, and is excluded from every
independent-sample aggregate.

The unit of analysis is the **system capture** — a product interface plus its routing, model,
system prompt, browsing state and mode — not an isolated model. We use "system" and "capture"
throughout and avoid "model X scored ...".

### 3.3 Extraction and scoring

Per capture we retain: a verbatim raw response (never edited post-merge except a dated
correction note), the model's own cited-sources list, and structured reviewer notes; plus one
short phrase per decision axis in `data/decisions-matrix.csv` (39 axes,
`docs/comparison-axes.md`).

Scoring uses a nine-dimension 0/1/2 rubric (`docs/rubric.md`): (D1) hardware-constraint
adherence, (D2) recency, (D3) tool factuality, (D4) model factuality, (D5) benchmark
factuality, (D6) citation quality, (D7) actionability, (D8) security model, (D9) internal
consistency. Four raters applied this procedure independently — one author-derived baseline and
three frontier LLMs on an identical packet (Section 9.3). Falsifiable sub-claims are checked and
recorded verbatim: tool and version existence against a registry / repository fixed to the
capture date (`analysis/verification/tool-model-register.md`); memory fit via a stdlib checker
(`analysis/scripts/memory_budget.py`).

The rubric mixes two layers, and we do not claim to establish an objective ground truth for
overall architectural quality. Some dimensions are objective (model existence, version
existence, memory feasibility under stated assumptions, self-contradiction); others are
rubric-based judgements of design quality (actionability, security adequacy). The study
evaluates the objective sub-claims and separately measures rubric-based quality.

## 4. Consensus

`analysis/consensus/consensus-matrix.md` gives the full 39-axis table (counts over the 10
non-anchor systems).

### 4.1 Near-unanimous — the *shape* of the machine

Unanimous or near-unanimous (9–10 / 10):

- **Apple-Silicon-native inference** as the primary path (MLX family), with llama.cpp / Ollama
  compatibility — 10/10. (Product-level split is real: mlx-lm, Ollama-MLX, llama.cpp+MLX,
  vLLM-MLX all appear.)
- **One large model resident at a time**; small models optional / on-demand — 9/10. The lone
  outlier proposes 2–3 co-resident instances and is separately shown to violate the memory
  budget (Section 6).
- **Model swapping** with an anti-thrash / load policy — 10/10.
- **Custom supervisor plus thin integration** with specialist runtimes, not one mega-framework
  — 10/10.
- **Hierarchical coordinator/worker**, explicitly not a swarm — 10/10.
- "**100 agents = cheap state/config**", not 100 resident LLMs — 10/10.
- **One concurrent heavy-inference slot** — 9/10.
- **Evidence-first research pipeline** (search → retrieve → extract → verify → contradiction →
  synthesise) with a **stored evidence ledger**, final prose generated only from verified
  evidence — 10/10.
- **SQLite plus filesystem as day-one memory**; defer vector / graph complexity — 10/10, 9/10.
- **Defer a knowledge graph** until a multi-hop / temporal need is demonstrated — 10/10.
- **Dedicated non-admin user plus workspace isolation** as the security boundary — 10/10.
- **Tailscale-only private network**, no public exposure — 10/10; small private dashboard / API
  — 10/10.
- **launchd plus KeepAlive plus an independent watchdog** — 10/10; `caffeinate` / `pmset` on AC
  — 10/10; **durable queue plus leases / checkpoints plus requeue (never replay destructive
  actions)** — 10/10.
- **32 GB unified memory is the bottleneck** (capacity / bandwidth / KV growth), not CPU/GPU
  compute — 10/10. *This is a corpus observation: all ten non-anchor responses identified
  memory as the primary architectural constraint. Our independent memory model (Section 6) is
  consistent with that interpretation.*
- **1 TB external SSD is cold / bulk storage**, not the latency-critical disk — 10/10.

Axis coding used predefined inclusion criteria (`docs/comparison-axes.md`); e.g. "Apple-Silicon
-native inference" counts MLX-family runtimes and llama.cpp with Metal, not CPU-only inference.
The 39 axes were defined by the authors, which introduces researcher degrees of freedom; the
coding guide and the per-response phrases are released so the coding can be audited.

### 4.2 Genuine splits — the *products*

No majority; recorded as adjudication points, not facts
(`analysis/consensus/disagreements.md`):

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

**Quantifying the split.** Tag each of the 33 architecture axes as *structural* (topology,
state model, security boundary, concurrency stance, memory architecture — 24 axes) or *product*
(which named tool or model realises a layer — 9 axes) and take the modal-agreement count per
axis over the 10 non-anchor systems (`analysis/scripts/consensus_split.py`, re-tabulating the
per-axis counts from the consensus matrix; the per-axis tags are listed in the script so the
classification can be audited):

| group | axes | median agreement | mean | axes at ≥ 9/10 |
|---|---:|---:|---:|---:|
| structural | 24 | **10 / 10** | 9.0 | 18 / 24 |
| product | 9 | **5 / 10** | 5.7 | 1 / 9 |

**The consensus result** is that the systems agree on constraints and topology and disagree on
implementation at the boundary of those constraints — a five-point gap in median modal
agreement between the structural and product axes. This separates robust architectural
principles from fast-moving product preference more cleanly than a superficial majority vote.

## 5. Apparent fabrication and the rater that generated it

### 5.1 What we found first

Our study-internal rater (an LLM with a roughly January 2026 training cutoff) audited every
capture and flagged **14 tools/models** across five responses as fabricated — most heavily in
the two DeepSeek fast modes and in Meta / Llama 4. We drafted a "cross-vendor shared
hallucination" finding around `Rapid-MLX` and `Gemma 4`, each named by three vendors.

### 5.2 What web verification showed

Verifying every flag against 2026 web sources
(`analysis/verification/tool-model-register.md`):

| flagged as fabricated | verdict | evidence (2026) |
|---|---|---|
| `Rapid-MLX` (3 vendors) | **real** | `github.com/raullenchai/Rapid-MLX`, ex vLLM-MLX, renamed 2026-03 |
| `Gemma 4` 26B / 31B / 12B (3 vendors) | **real** | released 2026-04-02; 26B-A4B MoE + 31B dense + 12B unified are all real variants |
| `DeepSeek Harness` / `DSH` | **real** | `github.com/deepseek-ai/deepseek-harness`, open-sourced 2026-08-13, MIT |
| `OpenClaw` | **real** | ex Warelay → Moltbot → OpenClaw; Wikipedia page |
| `Claw Code` | **real** | clean-room rewrite after the 2026-03-31 source-map leak; ~72k stars |
| `Clawtrol` | **real** | `github.com/wolverin0/clawtrol` |
| `Ornith-1.0-9B` | **real** | `huggingface.co/deepreinforce-ai/Ornith-1.0-9B`; Ollama `ornith:9b` |
| `WhipDesk` | **real** | `github.com/BinaryBananaLLC/WhipDesk` |
| `LightAgent` | **real** | `github.com/wanxingai/LightAgent`; arXiv 2509.09292 |
| `nono` (kernel sandbox) | **real** | sandbox tool: Landlock (Linux) / Seatbelt (macOS); 2026-05 references |
| `GLM-4.7-Flash` (30B-A3B) | **real** | Zhipu, 2026-01-19, 30B-A3B MoE |
| `Qwen3-Coder-Next` (referenced) | **real, 80B MoE** | `huggingface.co/Qwen/Qwen3-Coder-Next` |
| `Helmrig`, `Cloak`, `DiffResearch`, `cplt`, `memo`, `agent-policy-engine`, `pi-search-hub` | **unresolved at first pass** | no web evidence either way — **not** counted as fabrication |

A follow-up verification pass (Section 5.3) later resolved three of those seven — `Cloak`
(`getcloak.dev`), `memo` (`jagoff/memo`) and `pi-search-hub` (`ronnieops/pi-search-hub`) — to
real projects, leaving four genuinely unresolvable: `Helmrig`, `DiffResearch`, `cplt`,
`agent-policy-engine`.

**None of the 14 was confirmed nonexistent. At least 12 are real releases dated after the
rater's cutoff.** The false positives cluster precisely on the *most current* responses.

**This is a statement about the 14 flags, not about the corpus.** We keep three populations
separate:

- **(A) initial-rater fabrication flags** — the 14 names above. Verification: 0 confirmed
  nonexistent, ≥ 12 real post-cutoff, 4 unresolvable.
- **(B) the wider set of flagged-or-doubted names** — ~18 once later passes are included; still
  0 confirmed nonexistent, the same 4 unresolvable (`Helmrig`, `DiffResearch`, `cplt`,
  `agent-policy-engine`).
- **(C) factual defects found by independent verification, *not* raised as fabrication flags**
  — one genuinely nonexistent future model (`deepseek-expert`'s `Qwen3-Coder-70B`), several
  model-attribute errors (`z-ai`'s `Qwen3-Coder-Next` size; `GLM-4.5-Air` spec), and internal
  contradictions. These are real and stay in the analysis (Section 5.4).

So the corpus is **not** fabrication-free; the *initial rater's fabrication verdicts* were.
The register carries the per-entity table (entity exists / identity correct / attribute correct
/ claim supported / final category).

### 5.3 The reframed finding

> An LLM used as an evaluator of technical currency systematically misclassifies real
> post-cutoff artefacts as hallucinations. The study-internal rater's initial audit produced 14
> fabrication flags; on web verification none was confirmed nonexistent and ≥ 12 were real
> releases dated after the rater's training cutoff. Widening to every flagged-or-doubted name
> reaches ~18, still 0 confirmed nonexistent (4 unresolvable). Independent verification did find
> genuine factual errors elsewhere (population C) — the rater's failure is false *positives* on
> currency, not blanket leniency.

The catalogued LLM-as-judge biases — position, verbosity, self-enhancement [6–8] — are all
about *how the judge is influenced by the candidate's form*; this one is about *what the judge
cannot know*, and it does not wash out with randomised ordering or repeated runs. The mechanism
is more precisely **temporal epistemic misclassification**: the evaluator treats absence from
its internal knowledge, or an unsuccessful retrieval, as evidence that a post-cutoff entity
does not exist. Training cutoff is one cause; retrieval failure is another.

Our mitigation: dimensions D3 and D4 of the rubric now **require the rater to web-verify each
name before scoring**, and "not in my training data" scores 1 (unresolved), never 0.

The failure mode also reproduces *in a rater given exactly that instruction*. In a clean
re-scoring of D3–D4 (Section 9.3), one of two fresh raters (Perplexity) scored tool factuality
= 0 for seven responses by treating *its own search misses* as evidence of non-existence — its
"could not resolve" list contained `Rapid-MLX`, `OpenClaw`, `Clawtrol`, `nono`, `Ornith-1.0-9B`,
`DeepSeek Harness` and `Gemma 4 31B/12B`, every one of which the other fresh rater (GPT-5.6 Sol)
resolved to a real repository or model card on the same task. We discard that rater's scores.

### 5.4 Defects that survive verification

The analysis is not empty of real defects. These stay in:

| response | defect | type |
|---|---|---|
| `z-ai` | `Qwen3-Coder-Next` given as "8B / ~5 GB" — real model is 80B MoE; it is the load-bearing primary coding pick | model-attribute error |
| `z-ai` | same model quoted at 5 GB and 14 GB; 3-instance co-resident diagram vs on-demand prose | internal inconsistency |
| `meta-llama-4` | "M6 ≈ 300+ GB/s" (real: 170); 59 / 99 citation URLs non-supporting or unresolvable; same tool given multiple repo URLs; one reference mis-titles a real arXiv paper | spec error + citation quality |
| `z-ai` | `GLM-4.5-Air` treated as a ~4 GB fast-utility model — official spec is 106B total / 12B active | model-attribute error |
| `deepseek-expert` | recommends Docker in one section, forbids "Docker for Mac" in the "do not install" list; binds a dashboard to `0.0.0.0` while claiming "no public exposure" | internal contradiction |
| `deepseek-expert` | primary future model `Qwen3-Coder-70B` does not exist (the Qwen3-Coder line is 30B-A3B, 480B, and the separate 80B Coder-Next) | nonexistent model |
| `deepseek-instant` | recommends Ollama in Phase 4, forbids it in the "do not install" list | internal contradiction |
| `deepseek-instant-deepthink` | 256K-context claim vs a 1–2 GB KV budget; advocates ~32–34 GB always-loaded ("slight oversubscription acceptable") | hardware violation |
| `deepseek-instant-deepthink` | upgrade path describes DeepSeek-V4 as a dense model needing 96–128 GB — V4-Pro / V4-Flash are MoE | model-architecture error |

`grok-4` records **no** surviving factual defect — it states the full M6 spec including
170 GB/s correctly and its alternate-tool list resolves entirely — so it does not appear above;
its only weakness is zero cited sources (a Section 8 point). We note this explicitly because an
earlier draft mis-attributed a "~300 GB/s" bandwidth error to `grok-4`; the error belongs to
`meta-llama-4` only. The corrected picture: the low-scoring responses are low-scoring for
verifiable reasons — contradictions, a load-bearing size error, memory oversubscription, an
unreliable citation apparatus — not for inventing an ecosystem.

## 6. Constraint reasoning

`analysis/scripts/memory_budget.py` (stdlib) estimates weights plus KV cache for a response's
*co-resident* model set (what it says stays loaded) against 32 GB, with presets for each
capture. "Fails to fit" is defined against a fixed non-model reserve — macOS + WindowServer
≈ 5 GB, a headless browser ≈ 1.5 GB, the Python worker pool + runtime ≈ 2 GB, SQLite + vector
index ≈ 1 GB, and a 2 GB safety floor (≈ 11.5 GB total) — plus a KV cache sized at the
response's own stated context length at 8-bit KV. Weight sizes are the actual 4-bit GGUF / MLX
artefact sizes where published, else parameter-count × 0.5 bytes + 8 % runtime overhead. The
script prints every line item and takes the reserve as overridable flags; Section 11 notes the
sensitivity.

**Every co-resident set that a response describes as simultaneously loaded exceeds 32 GB** once
that reserve and KV cache are counted alongside the weights. The designs that fit are the ones
that *do not* keep the heavy models co-resident:

- Designs that keep **one** large MoE resident (Qwen3-Coder-30B-A3B ≈ 17–20 GB at 4-bit) plus a
  small dense model swapped in are *tight but feasible* — several responses say so explicitly
  and reserve a 2–6 GB floor (`perplexity`, `mistral`, `kimi`).
- Designs that keep **two** large models resident, or a dense 32B plus a helper, exceed the
  ceiling at working context lengths.
- `deepseek-instant-deepthink` is the clearest violation: ~32–34 GB of always-loaded weights
  before OS / browser / KV, with the text calling oversubscription "acceptable". `z-ai`'s
  three-instance worker-pool diagram (Qwen3-Coder + GLM-4.5-Air + Mistral Small co-resident)
  plus "fits within 32 GB with swapping" is the second.

**Scoring (adjudicated, D1):** 2 → `perplexity`, `mistral`, `kimi`, `grok-4`; 1 → `claude`,
`gpt-5`, `gemini`, `qwen`, `deepseek-expert`, `deepseek-instant`, `meta-llama-4`; 0 → `z-ai`,
`deepseek-instant-deepthink`. Inter-rater kappa on this dimension is the lowest of the nine
(0.15) — "sums to exactly 32 GB with no reserved margin" was scored 1 by one rater and 2 by
another. The v2 rubric fixes this: a 2 requires a **named free-RAM floor**.

## 7. Recency

The M6 facts, web-verified: announced **2026-08-25**, **170 GB/s** memory bandwidth at 24–32 GB
(153 GB/s at 16 GB), 32 GB maximum unified memory. Against that:

| tier | responses | character |
|---|---|---|
| current + M6-aware + sourced | `perplexity`, `mistral-large-3` (+ anchor `claude-sonnet-5`) | engage the real M6 spec, hedge every throughput number, cite |
| current picks, no usable sources | `gpt-5`, `grok-4`, `kimi-instant`, `gemini-3.1-pro`, `qwen-3.7-plus`, `meta-llama-4` | real 2026 tool/model picks; 0 usable sources (`gpt-5`: inline attributions, 0 URLs). `qwen` / `gemini` also carry a ~12–18-month model lag; `meta` also has the 170-vs-300 GB/s error |
| behind on models | `qwen-3.7-plus`, `gemini-3.1-pro` (partly `deepseek-expert`) | Qwen2.5-generation primaries, stale cloud-fallback lists (Claude 3.5 Sonnet / GPT-4o), no M6 engagement |

**Only `meta-llama-4` got a hard M6 fact wrong** ("~300+ GB/s"); `grok-4` — which our first
rater mistakenly grouped with it — states 170 GB/s correctly.

Recency correlates with (a) retrieval / browsing and (b) *not being penalised by a stale
rater* (Section 5). It does **not** cleanly predict agreement with the cross-model consensus:
several consensus-aligned responses are unsourced, and one behind-on-models response
(`gemini`) is internally clean and consensus-shaped.

## 8. Citation quality

Only the anchor and four non-anchor responses cite anything resolvable.

| response | apparatus | resolves? | supports? | primary? |
|---|---|---|---|---|
| `claude-sonnet-5` (anchor) | ~97 URLs | mostly | mostly | mostly primary |
| `perplexity` | ~17 URLs | mostly | mostly | mixed (some aggregator mirrors; 2 arXiv IDs unverified) |
| `mistral-large-3` | ~36 credibility-rated, dated entries | mostly | yes | mixed (~6 are `google.com/search` URLs) |
| `gpt-5` | ~20 inline attributions, **0 URLs** | n/a | attributions are to real docs | n/a |
| `meta-llama-4` | **99 numbered URLs** | ~40 % resolve-and-support | patchy | mostly secondary |
| all others | none | — | — | — |

**Citation quantity did not predict citation quality on this corpus** (exploratory — only five
of thirteen responses carry any citation apparatus, so we report the pattern, not a correlation
coefficient). The pattern is driven by the extremes: `meta-llama-4` has the largest apparatus
and the worst — 59 of its 99 URLs are non-supporting or unresolvable, the same tool is given
several different repo URLs, and one real arXiv URL sits under the wrong paper title — while
`gpt-5` cites zero URLs but every inline attribution points at a real, checkable source.
**Reference presence and evidential grounding are distinct properties.** We classify each URL
on three axes — resolves / does not; supports / partly / does not support the claim; primary /
secondary / tertiary / irrelevant — and count "non-supporting or unresolvable" as the union of
*does-not-resolve* and *does-not-support*.

**Consequence for evaluation design:** "has a Sources section" must not be used as a proxy for
"is grounded". Scoring it that way ranks `meta-llama-4` above `gpt-5` — backwards. D6 of our
rubric scores a mostly-unsupported apparatus as 0, and it is the **cleanest single separator**
in the adjudicated scores: the top four responses score 2/2/2/0 on it, every other response
scores 0.

## 9. Internal consistency and reasoning-mode sensitivity

### 9.1 Internal contradictions

Material self-contradictions in 3 of 13 captures:

- `deepseek-expert` and `deepseek-instant` each recommend a tool (Docker; Ollama) that their
  own "do not install" list forbids.
- `z-ai` gives one model two different memory sizes (5 GB vs 14 GB) and pairs "primary model
  stays loaded, others on demand" with a three-instance co-resident diagram.
- `meta-llama-4`'s prose is coherent but its citation apparatus is not (same tool, multiple
  repo URLs; wrong title on a real paper).

### 9.2 The DeepSeek mode effect

DeepSeek is the only system captured in more than one mode — three captures, one base model
(DeepSeek-V4-Pro), three chat modes:

| mode | grounding | internal defects | adj. /18 |
|---|---|---|---:|
| deep-reasoning (`deepseek-expert`) | real tools; but a nonexistent future model (`Qwen3-Coder-70B`) and an unresolved `DeepSeek-Coder-V3` | Docker recommend-then-forbid | 8 |
| fast (`deepseek-instant`) | real tools + real models, all post-cutoff | Ollama recommend-then-forbid | 9 |
| Instant+DeepThink (`deepseek-instant-deepthink`) | real tools; DeepSeek-V4 mislabelled dense | memory oversubscription, 256K-context-vs-KV | 6 |

Within this single DeepSeek case study, holding weights and prompt fixed, **the reasoning mode
produced materially different factual and constraint profiles**: the three captures span three
of the rubric's coarse tiers. The effect is *not monotone across every dimension* — after the
clean D3–D4 re-run (Section 9.3), `deepseek-instant` (9/18) actually scores *above*
`deepseek-expert` (8/18), because the deep mode's more elaborate upgrade path reached for
future models that do not exist while the fast mode's picks all resolved. On this evidence,
mode is at least as large a factor as the base-model label for a fixed DeepSeek family; whether
that generalises across model families is an open question and the obvious controlled
follow-up (n = 1 family, n = 3 modes here).

### 9.3 Inter-rater agreement

The nine-dimension rubric was applied **independently** to all 13 captures by four raters — one
study-internal and three frontier LLMs given the identical scoring packet. "Independent" here
means each scored the same packet without seeing another rater's scores; it does **not** mean
design-independent — the study-internal rater also wrote the rubric and the reviewer notes, so
we treat it as an author-derived baseline, not a neutral fourth opinion, and use GPT-5.6 Sol as
the canonical comparison rater.

| rater | role | mean total / 18 |
|---|---|---:|
| study-internal (from the reviewer notes) | author-derived baseline | 12.7 |
| GPT-5.6 Sol (paid tier, web search) | **canonical rater** | 11.1 |
| Grok 4 (+ web verification) | additional LLM rater | 13.8 |
| DeepSeek chat run | additional LLM rater | 14.7 |

Canonical pair (study-internal vs GPT-5.6 Sol), 117 paired ratings:

| metric | value |
|---|---|
| exact agreement | 68.4 % |
| within 1 point | 96.6 % |
| Cohen's kappa [15] (unweighted / quadratic-weighted) | +0.49 / **+0.64** |
| Krippendorff's alpha [16] (ordinal) | +0.20 (pair), +0.12 (all four) |
| Gwet's AC1 [17] (unweighted / quadratic-weighted) | +0.54 / **+0.73** |

The gap between kappa_w = 0.64 and alpha = 0.20 is a prevalence effect: several dimensions are
dominated by 2s, which inflates chance agreement in Krippendorff's ordinal alpha. Gwet's AC1,
designed for exactly this skew, sits with the weighted kappa. We report all three and read
agreement as **moderate and dimension-dependent**.

Per-dimension: **reliable** — D2 recency (kappa 0.68), D3 tool factuality (0.70), D5 benchmark
factuality (0.66); **weak** — D6 citation quality (0.30), D8 security model (0.32), D7
actionability (0.36), and the two worst, D1 hardware-constraint (0.15) and D9
internal-consistency (0.14). The weak dimensions share a fuzzy 0/1 or 1/2 boundary; the v2
rubric adds hard anchors for each.

**Rank-order stability is limited, not established.** Rank-correlating the per-response totals
between every rater pair gives a mean Spearman rho = 0.36 / Kendall tau_b = 0.28. The canonical
pair is the tightest (rho = 0.71, tau_b = 0.58); the two heavier-scoring raters diverge sharply
(study-internal vs DeepSeek rho = 0.08). So we do **not** claim a stable fine-grained ranking.
What survives across raters is coarse: the same responses land in the top and bottom bands
(Section 10). The numeric total is a secondary summary and is always reported with the
per-dimension kappa, never as a headline.

Raters also have a **severity personality**: the same rubric on the same responses produces an
11.1 → 14.7 / 18 spread of rater means, and the DeepSeek run assigned 2 on five dimensions
almost uniformly (a low-information rater). LLM-as-rubric-rater is not a portable instrument
without anchored exemplars.

**Which rater run feeds which result.** Two scoring passes exist; they are not interchangeable:

| run | packet | raters | status | why |
|---|---|---|---|---|
| four-rater full pass (9 dims) | contained a leaked list of real post-cutoff tools in rule 4 | study-internal, GPT-5.6 Sol, Grok 4, DeepSeek | **kept for agreement stats only**, not for D3/D4 levels | the leak contaminates the two factuality dimensions but not the other seven or the agreement structure |
| clean D3/D4 re-run | names nothing; forbids reading the verification register; mandatory web verify; unresolved → 1 | GPT-5.6 Sol (kept), Perplexity (**discarded** — scored 7 responses' tool factuality = 0 from its own search misses) | **canonical for D3/D4 levels** and folded into Section 10.1 | isolates the leak's effect on the factuality dimensions |

The canonical rater reproduced its contaminated D3/D4 on **11 of 13 responses**; the two
changes (`meta-llama-4` D4 1→2, `deepseek-instant-deepthink` D4 2→0) were driven by specific
web findings, not by removing the leak. Four further cells moved on new findings surfaced by
the clean pass — `mistral` D3 2→1, `kimi` D3 2→1, `deepseek-expert` D4 2→1
(`Qwen3-Coder-70B` does not exist), `deepseek-instant-deepthink` D4 1→0 — and are folded into
Section 10.1. **Net: the leak changed two D3/D4 cells directly and four more via newly found
evidence; the top and bottom performance bands are unchanged.**

### 9.4 Prompt sensitivity

Five systems (`perplexity`, `gpt-5`, `gemini-3.1-pro`, `qwen-3.7-plus`, `z-ai`) were re-run on
two controlled prompt variants: **v2**, a full paraphrase (RFC framing, reshuffled sections, no
shared sentences), and **v3**, v1 with the anti-anchoring / anti-popularity steer removed. Each
`(system, variant)` is a fresh session; 15 captures total.

**Primary result — framing moves products, not topology.** Across all 15 captures, **every
response keeps its architecture** — coordinator/worker topology, logical agents as data, one
heavy plus one small model, SQLite state, dedicated non-admin user, launchd, Tailscale — and
changes only which *products* realise each layer. This holds under both perturbation kinds.

**Effect size is strongly model-dependent.** `gpt-5`'s primary inference-engine pick is
*different in each of the three framings* (MLX-LM in v1, llama.cpp in v2, Ollama in v3);
`perplexity` and `gemini-3.1-pro` sit at the other extreme.

**The anti-anchoring steer does real work, but its sign is not uniform.** Removing it (v3) made
`gpt-5` and `qwen-3.7-plus` name *more* products; `z-ai` (GLM-5.2) went the *other* way,
becoming more conservative.

**Free chat tiers are not reproducible instruments across sessions.** Two of the five systems
served a *different underlying model* between paraphrase runs: `z-ai` self-reported cutoff
"~mid-2025" for v2 and "Late 2024" for v3 under the same "GLM-5.2" label; `gemini` self-reported
"Gemini 2.5 Pro" / "2026" for v2 and "Gemini 1.5 Pro" / "January 2025" for v3 — a materially
older model. Only `gpt-5` and `perplexity` held their model identity across all three framings;
the clean prompt-sensitivity comparison exists only for those two. This is a threat to validity
that generalises to any study using a consumer chat product as an instrument.

**No effect on fabrication rate or architecture.** Across all ten v2/v3 captures, zero
fabrications were confirmed on web verification (one hallucinated-context item — `gemini` v3
closed by asking about nonexistent user projects — is logged separately).

## 10. Synthesised reference architecture and performance bands

### 10.1 Adjudicated rubric totals and performance bands (non-anchor, / 18)

Adjudicated after the clean D3–D4 re-run. **What is reportable across raters is the band, not
the exact rank** (Section 9.3: mean Spearman rho = 0.36 on per-response totals). A one-point gap
inside a band carries no claim; the band boundaries fall at natural gaps in the adjudicated
totals and are stable to which non-canonical rater is substituted in.

| band | responses (adjudicated total /18) | character |
|---|---|---|
| **Strong** | `perplexity` (18), `mistral-large-3` (15) | quantified memory budget with a reserved floor; methodology / limits stated; dated sources that resolve |
| **Good** | `gpt-5` (14), `grok-4` (14) | all picks real and current; strong epistemic discipline; both lose points only on citations |
| **Mixed** | `gemini-3.1-pro` (12), `qwen-3.7-plus` (12), `kimi-instant` (11), `meta-llama-4` (11) | real tools and a workable plan, but a model-era lag, a wrong command, an M6-bandwidth error, or an unreliable citation apparatus |
| **Weak** | `deepseek-instant` (9), `deepseek-expert` (8), `deepseek-instant-deepthink` (6), `z-ai` (5) | recommend-then-forbid contradictions, a nonexistent future model, memory oversubscription, or a load-bearing model-size error |

Per-response notes behind the bands are in `analysis/scoring/scores-adjudicated-2026-09-01.csv`
and the adjudication report. Anchor `claude-sonnet-5`: 15 (excluded from the bands).

### 10.2 The architecture the corpus supports

This is an **analytic synthesis** — majority positions plus adjudicated calls — not a consensus
ground truth, and not empirically validated as optimal. Adjudicated calls are marked
`[adjudicated]`.

- **Inference:** one MLX-family runtime behind an internal adapter; **one large MoE resident**
  (Qwen3-Coder-30B-A3B-class, 4-bit, ≈ 17–20 GB) plus one small dense model swapped in on
  demand; never two large models co-resident. Benchmark the chosen runtime on the actual M6
  before trusting any throughput claim.
- **Agents:** 100+ agents as SQLite rows / definition files; **hierarchical coordinator/worker**;
  one concurrent heavy-inference slot plus 2–3 small / tool workers.
- **Orchestration:** a thin custom Python supervisor owns task state and scheduling; a framework
  (LangGraph / PydanticAI) may implement selected stateful workflows but stays replaceable
  `[adjudicated]`.
- **Coding execution:** capability-tiered — Aider for git-native interactive edits, OpenHands
  in a container for autonomous multi-step jobs `[adjudicated]`.
- **Research:** evidence-first pipeline; every claim traces to a stored snippet; a second-pass
  verification agent re-opens sources; contradiction pass; synthesise only from the verified
  ledger.
- **Memory:** filesystem Markdown plus SQLite (plus FTS) day one; `sqlite-vec` for embedded
  vectors `[adjudicated]`; no standalone vector daemon and no knowledge graph until a real need
  is demonstrated.
- **State / recovery:** SQLite WAL task queue plus leases / checkpoints; requeue interrupted
  work; never replay destructive actions.
- **Security:** dedicated non-admin macOS user plus workspace isolation; capability tiers
  (autonomous / notify-log / approve / never) plus a kill switch plus per-task runaway limits;
  secrets in Keychain, never in the agent tree. Stronger sandboxing (container / VM) is
  capability-scoped to untrusted code, not a universal prerequisite `[adjudicated]`.
- **Always-on:** launchd KeepAlive plus a separate watchdog plus `caffeinate` / `pmset` on AC.
- **Remote:** Tailscale-only, zero inbound ports; a small FastAPI dashboard / API on the
  tailnet; approvals through the dashboard, never SSH-to-approve.
- **Storage:** internal SSD for OS / runtime plus hot working state (and preferably hot
  weights); external SSD for the model library, research corpus, datasets and backups.
- **Cloud:** an explicit policy-gated escape hatch (privacy class plus confidence plus budget),
  not a hidden dependency; the system must remain useful at $0 cloud spend `[adjudicated]`.

The **32 GB unified-memory ceiling is a hard engineering constraint, not a target to fill** —
reserve a measured RAM floor.

## 11. Threats to validity

- **n = 1 base prompt — partly mitigated.** The v1 phrasing is the primary instrument. Two
  controlled paraphrases (Section 9.4) were re-run on a 5-system subset: the architecture was
  stable across all framings and no new fabrications appeared, so the consensus and
  fabrication findings are not v1-phrasing artefacts. The product-level results (the
  disagreement axes, the Section 10.1 bands) *are* somewhat phrasing-sensitive and should be
  read as "for the v1 instrument". A second hardware spec is not done.
- **Consumer chat tiers are not reproducible instruments** (Section 9.4). For `z-ai` and
  `gemini`, the free product served a different underlying model between paraphrase runs. Any
  per-system claim for those two is a snapshot, not a controlled measurement.
- **Anchor contamination.** `claude-sonnet-5` is not blind (built the repo, browsing on,
  partial format authorship). Handled by exclusion from every cross-response aggregate;
  reported separately.
- **The evaluator is an LLM.** Three of the four raters are frontier LLMs (the fourth is the
  author-derived baseline). Section 5 is a direct demonstration of the risk (training-cutoff
  false positives). Mitigations: mandatory web verification for factual dimensions; a
  human-authored rubric; four raters with reported agreement; every falsifiable sub-claim
  recorded verbatim.
- **We leaked part of the answer key — effect measured.** An intermediate version of the rater
  packet listed the 12 real-but-post-cutoff tools while instructing raters to treat them as
  real; all three four-rater-pass second-rater runs saw it. We ran a clean re-scoring of the
  affected dimensions (D3, D4) with an uncontaminated packet (Section 9.3). Outcome: the clean
  re-run changed **two** canonical D3/D4 cells directly attributable to removing the leaked
  list, and **four** additional D3/D4 cells on verification evidence newly found during the
  clean pass; the canonical rater reproduced its contaminated D3/D4 on 11 of 13 responses; the
  top and bottom performance bands are unchanged. D1, D2, D5–D9 were never contaminated. The
  packet is fixed for future raters.
- **AI assistance in producing this study — disclosed in full.** (i) The consensus anchor
  `claude-sonnet-5` is itself a frontier LLM, run inside an AI coding tool with live browsing
  and partial authorship of the requested output format; it is excluded from every
  cross-response aggregate. (ii) The repository — analysis scripts, data plumbing, and drafting
  of parts of this manuscript — was built with an AI pair-programming assistant; every script
  is stdlib, is in the release, and its outputs are reproducible from the released CSVs. (iii)
  Three of the four rubric raters are frontier LLMs (Section 9.3). All numeric results in the
  paper were regenerated from the released artefacts by running the released scripts; no result
  is quoted from an un-scripted model statement.
- **Rater severity variance** (Section 9.3): ~3.6 / 18 across four raters. Report per-dimension
  kappa, not a single headline score.
- **Self-scoring.** `grok-4` scored the `grok-4` response (16/18); the DeepSeek run scored the
  three DeepSeek responses (15/15/15). Noted, not corrected; both are variance-check raters.
- **The study-internal rater is not design-independent** — it wrote the rubric and the reviewer
  notes. That is why a canonical rater exists; the adjudicated bands are the reportable output.
- **Reproducibility of a moving ecosystem.** Every capture is a dated snapshot (2026-08-31);
  free-tier defaults and the underlying models will have moved by publication. We preserve the
  *information state* of the evaluation — verbatim responses, prompts, model identifiers,
  browsing state, capture dates, and the verification verdicts as of the capture window — rather
  than claiming the live ecosystem is reproducible.
- **DeepSeek modes are one system.** The mode-effect result (Section 9.2) is n = 1 system; it
  motivates a controlled multi-mode experiment, it does not establish a general law.

## 12. Conclusion

Asked to design the same constrained machine, eleven frontier LLM systems agree on what the
machine *is* — a memory-bound, local-first, coordinator/worker workstation with durable SQLite
state and private-network control — and disagree on which specific products build it. The
disagreements are informative: they mark exactly the decisions a human engineer still has to
adjudicate.

The sharper result is about evaluation. On a task where currency matters, an LLM asked to judge
another LLM's factual grounding will penalise the newest, best-grounded answers hardest,
because the judge's own knowledge is stale. Any evaluation pipeline that puts an LLM in the
grader's seat for technical-currency questions needs an external verification step in front of
it. We built one; this paper is partly the record of discovering we needed it.

## Broader impact

This work contributes a reusable protocol and a released corpus for auditing LLM-as-judge
pipelines on open-ended technical tasks, and it documents a specific, cheaply mitigated failure
mode (temporal epistemic misclassification by an LLM rater). Risks: the released corpus and
rubric could be used to game an evaluation; "an LLM said it's fake" verdicts, shown here to be
unreliable, may still be cited as authoritative; and the synthesised reference architecture is
a dated snapshot — following it uncritically past its 2026 currency window would reproduce the
recency failure it documents.

## Declarations

**Funding.** This work received no external funding.

**Competing interests.** The author declares no competing interests.

**Ethics.** The study involved no human subjects and no personal data. All evaluated content is
model-generated text collected from publicly available LLM products under their normal terms of
use.

**Use of AI tools.** See Section 11. In summary: the consensus anchor and three of four rubric
raters are LLMs (by design; this is the object of study); the analysis code and parts of the
manuscript were produced with an AI pair-programming assistant; all reported numbers are
regenerated by released stdlib scripts from released data.

**Data and code availability.** All data, prompts, the rubric, the four rater score sets, the
web-verified tool/model register, the checking scripts, and the adjudicated scores are at
<https://github.com/roshanaryal1/llm-architects> under MIT (code) and CC-BY-4.0 (data), and
permanently archived at Zenodo (concept DOI <https://doi.org/10.5281/zenodo.22245991>). A
datasheet for the response corpus is included as supplementary material.

**Author contributions.** R.A. designed the study, collected the corpus, built the analysis
code, performed the verification and adjudication, and wrote the manuscript.

## References

[1] B. Xu. *AI Agent Systems: Architectures, Applications, and Evaluation.* arXiv:2601.01743, 2026.

[2] J. Wang et al. *Act As a Real Researcher: A Suite of Benchmarks Evaluating Frontier LLMs and Agentic Harnesses in Research Lifecycle.* arXiv:2606.07462, 2026.

[3] M. L. Rethlefsen et al. *PRISMA-S: an extension to the PRISMA statement for reporting literature searches in systematic reviews.* Systematic Reviews, 10(39), 2021.

[4] J. McGowan et al. *PRESS Peer Review of Electronic Search Strategies: 2015 Guideline Statement.* Journal of Clinical Epidemiology, 75:40–46, 2016.

[5] National Academies of Sciences, Engineering, and Medicine. *Reproducibility and Replicability in Science.* The National Academies Press, 2019.

[6] J. Gu et al. *A Survey on LLM-as-a-Judge.* The Innovation 7:101253, 2026. doi:10.1016/j.xinn.2025.101253.

[7] J. D. Norman, M. U. Rivera, D. A. Hughes. *Reliability without Validity: A Systematic, Large-Scale Evaluation of LLM-as-a-Judge Models Across Agreement, Consistency, and Bias.* arXiv:2606.19544, 2026.

[8] S. K. Soumik. *Judging the Judges: A Systematic Evaluation of Bias Mitigation Strategies in LLM-as-a-Judge Pipelines.* arXiv:2604.23178, 2026.

[9] D. Rao, E. Wong, C. Callison-Burch. *Detecting and Correcting Reference Hallucinations in Commercial LLMs and Deep Research Agents.* arXiv:2604.03173, 2026.

[10] M. Li, Z. Lin, S. Ma. *Source or It Didn't Happen: A Multi-Agent Framework for Citation Hallucination Detection.* arXiv:2605.08583, 2026.

[11] C. Zhao, Y. Tang, Y. Qian. *Do Deployment Constraints Make LLMs Hallucinate Citations? An Empirical Study across Four Models and Five Prompting Regimes.* arXiv:2603.07287, 2026.

[12] C. E. Jimenez et al. *SWE-bench: Can Language Models Resolve Real-World GitHub Issues?* ICLR, 2024.

[13] S. Zhou et al. *WebArena: A Realistic Web Environment for Building Autonomous Agents.* ICLR, 2024.

[14] S. Baltes et al. *Guidelines for Empirical Studies in Software Engineering involving Large Language Models.* arXiv:2508.15503, 2025.

[15] J. Cohen. *A Coefficient of Agreement for Nominal Scales.* Educational and Psychological Measurement, 20(1):37–46, 1960.

[16] K. Krippendorff. *Reliability in content analysis: some common misconceptions and recommendations.* Human Communication Research, 30(3):411–433, 2004.

[17] K. L. Gwet. *Computing Inter-Rater Reliability and Its Variance in the Presence of High Agreement.* British Journal of Mathematical and Statistical Psychology, 61(1):29–48, 2008.

## Appendix A. The frozen prompt and the two paraphrases

The verbatim v1 prompt is `prompts/prompt-v1.md`; the two controlled paraphrases are
`prompts/prompt-v2.md` (RFC-framed full reword) and `prompts/prompt-v3.md` (v1 minus the
anti-anchoring steer). All three are frozen in the supplementary repository.

## Appendix B. The nine-dimension rubric

The full rubric with 0/1/2 anchors per dimension, and the v2 hardened anchors for D1/D7/D8/D9,
are in `docs/rubric.md`.

## Appendix C. Web-verified tool/model register

The per-entity verification table (entity exists / identity correct / attribute correct / claim
supported / final category) is `analysis/verification/tool-model-register.md`.

## Appendix D. Per-response decision matrix

The 39-axis × 13-capture matrix is `data/decisions-matrix.csv`; per-capture reviewer notes are
in `data/responses/*.md`.

## Appendix E. Datasheet for the response corpus

Provided as a separate supplementary document (`paper/submission/datasheet.md`).
