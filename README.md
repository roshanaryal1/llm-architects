<!--
  README.md — project landing page.
  Audience: (1) a future maintainer, (2) contributors submitting a new model response,
  (3) a reader who arrives from the eventual paper.
  Keep this file authoritative for repo layout + workflow. If you move a directory,
  update the "Repository layout" section and docs/methodology.md in the same commit.
-->

# llm-architects

**A controlled comparison of how frontier LLMs design the same hard systems-architecture task.**
Formerly `llm-architecture-eval` (renamed 2026-09-01; the old GitHub URL redirects).

Around a dozen frontier AI systems are each given one identical, evidence-demanding prompt: *design a 24/7
autonomous AI development-and-research workstation for a 32 GB Apple M6 Mac mini.* Every response
is captured verbatim, scored against a written rubric, and cross-checked for fabricated tools,
stale recommendations, hardware-constraint violations, and citation quality. The corpus feeds a
research write-up and doubles as the design
brief for the author's real build.

> **Status:** analysis complete; paper **submitted to Cureus Journal of Computer Science**
> (Springer Nature) and, after a deferral at the initial quality check, **revised and
> resubmitted on 2026-09-03** — now in the editor/peer-review queue. 13 responses / 11 systems
> captured (Claude Sonnet 5, Qwen 3.7 Plus, DeepSeek ×3 modes, Perplexity, Gemini 3.1 Pro, Kimi
> Instant, Mistral Large 3, GPT-5.6 Luna, Meta / Llama 4, Grok 4, z.ai / GLM); all falsifiable
> sub-claims web-verified ([`analysis/verification/`](analysis/verification/)); four independent
> rater score sets with agreement stats ([`analysis/scoring/`](analysis/scoring/)); consensus
> synthesis and reference architecture ([`analysis/consensus/`](analysis/consensus/)); write-up
> in [`paper/draft-v1.md`](paper/draft-v1.md). Archived at Zenodo — concept DOI
> [10.5281/zenodo.22245991](https://doi.org/10.5281/zenodo.22245991). See
> [`CHANGELOG.md`](CHANGELOG.md) for the running log.
>
> **This repository is the canonical project folder.** Everything lives here — prompt,
> responses, matrix, analysis, tooling. Earlier loose working files in the parent directory were
> superseded and archived out of the way; nothing outside this repo is authoritative.

---

## Why this exists

Closed benchmarks (SWE-bench, MMLU, …) measure LLMs on tasks with a known answer. Open-ended
**architecture** — "given these constraints and goals, design the system" — is where these models
are actually used by engineers, and it is barely measured. This repo treats one such task as a
study instrument and asks:

| # | Question | How it is measured |
|---|----------|--------------------|
| RQ1 | Where do models **agree**? | Consensus matrix over ~38 decision axes ([`data/decisions-matrix.csv`](data/decisions-matrix.csv)) |
| RQ2 | How often do they **fabricate** tools, versions, or benchmark numbers? | Per-response hallucination audit in the `## Reviewer notes` of each capture file |
| RQ3 | Do they respect the **hardware envelope** (32 GB, ~170 GB/s, one GPU)? | `analysis/scripts/memory_budget.py` + rubric dimension |
| RQ4 | Are recommendations **current** (2026) or stale defaults? | Rubric "Recency" score, cross-checked vs Claude's sourced baseline |
| RQ5 | When models cite sources, do the citations **resolve and support** the claim? | Rubric "Citation quality". Early finding: citation *count* is not a proxy — `meta-llama-4` has 99 refs, ~60% junk; `gpt-5` has ~20 solid inline attributions and 0 URLs |
| RQ6 | Are responses **internally consistent**? | `internal_contradictions` row in the matrix |

Full method: [`docs/methodology.md`](docs/methodology.md). Rubric: [`docs/rubric.md`](docs/rubric.md).

## Roadmap

Tracked work is in **[the project board](https://github.com/users/roshanaryal1/projects/6)** and
milestone **v0.1 — data collection complete**. Open issues, in rough order:

| # | Item | Status |
|---|------|--------|
| ~~#5 #6 #7~~ | ~~Capture GPT-5 / Grok 4 / Llama 4~~ | done — **12 responses / 10 systems** |
| **#10** | Build `analysis/consensus/` synthesis | **unblocked — critical path** |
| #9 | Second rubric rater + inter-rater agreement | required for paper |
| #12 #13 #14 | Follow-up probes (fabrication-retraction, recency-vs-effort, cite-on-demand) | optional, high value |
| #8 | `prompt-v2` / `v3` paraphrases (RQ6) | after captures |
| #9 | Second rubric rater + inter-rater agreement | required for paper |
| #11 | Draft the meta-study paper | blocked on #8 #9 #10 |

Contribution flow is one branch + PR per issue — see [`CONTRIBUTING.md`](CONTRIBUTING.md).

---

## Repository layout

```
llm-architects/
├── prompts/                     The study instrument (frozen)
│   ├── prompt-v1.md             Canonical prompt. DO NOT EDIT after freeze.
│   ├── prompt-v2.md             Paraphrase for prompt-sensitivity testing (RQ6). [planned]
│   └── prompt-v3.md             Second paraphrase. [planned]
│
├── data/
│   ├── responses/               One verbatim capture per AI system
│   │   ├── _TEMPLATE.md         Copy this to add a new response
│   │   ├── claude-sonnet-5.md
│   │   ├── qwen-3.7-plus.md
│   │   ├── deepseek-instant.md
│   │   └── deepseek-expert.md
│   ├── decisions-matrix.csv     Structured extraction: 1 row per decision axis, 1 column per AI
│   └── schema/
│       └── decisions-matrix.schema.md   What each row/column means; allowed values
│
├── analysis/
│   ├── findings/                Deep per-response research notes (long form)
│   │   └── claude-sonnet-5-findings.md
│   ├── consensus/              Cross-response synthesis (RQ1) — the paper's Section 7
│   │   └── README.md
│   └── scripts/                Reproducible checks
│       ├── memory_budget.py     Estimate weights + KV cache vs 32 GB for a given model set
│       └── validate_matrix.py   Lint decisions-matrix.csv (shape, required rows, no empty anchor col)
│
├── docs/
│   ├── methodology.md           Full protocol: prompt design, model set, extraction, scoring
│   ├── rubric.md                9-dimension scoring rubric (0/1/2 per dimension)
│   ├── comparison-axes.md       The ~38 axes used in decisions-matrix.csv, defined
│   └── glossary.md              Terms used across responses (MoE, KV cache, worktree, …)
│
├── reference/                   Non-study reference material
│   └── (architecture artifacts, external links)
│
├── .github/                     Issue/PR templates + CI (markdown + CSV validation)
├── CONTRIBUTING.md              How to submit a new model response
├── CODE_OF_CONDUCT.md
├── CITATION.cff                 Cite this dataset
├── CHANGELOG.md                 Running log of captures + analysis milestones
├── Makefile                     `make validate` / `make budget` / `make lint`
└── LICENSE / LICENSE-DATA       MIT (code) / CC-BY-4.0 (corpus + analysis)
```

---

## Quick start

```bash
# 1. Read the instrument
less prompts/prompt-v1.md

# 2. See what has been collected and how they compare
column -s, -t < data/decisions-matrix.csv | less -S

# 3. Run the hardware sanity check on any model set
python3 analysis/scripts/memory_budget.py --preset claude
python3 analysis/scripts/memory_budget.py --weights 19 --kv 3 --small 3

# 4. Validate the matrix before committing
make validate
```

No runtime dependencies beyond Python 3.10+ standard library. `make lint` additionally uses
`markdownlint-cli` if present (optional).

---

## How to add a new AI response

Short version (full version in [`CONTRIBUTING.md`](CONTRIBUTING.md)):

1. Paste the **frozen** prompt from `prompts/prompt-v1.md` (START/END markers included) into the AI.
2. `cp data/responses/_TEMPLATE.md data/responses/<model-slug>.md`.
3. Fill the YAML front-matter (model, version, provider, browsing on/off, date, `trust_rating`).
4. Paste the response **verbatim** under `## Raw response` — no edits, no reformatting.
5. Copy the model's own citations under `## Model's own cited sources` (or write `NONE`).
6. Write `## Reviewer notes`: recency, hallucinations, constraint reasoning, agreements, divergences.
7. Add a column to `data/decisions-matrix.csv` and fill every row you can.
8. Add a line to `CHANGELOG.md`. Open a PR using the template.

---

## Known limitations (read before citing)

- **n = 1 base prompt.** Paraphrases (`prompt-v2/v3`) are planned to test sensitivity; until then,
  generality is limited.
- **Reviewer subjectivity.** Scoring is one rater so far. The rubric is written to reduce this;
  a second independent rater + inter-rater agreement is a prerequisite for the paper.
- **Claude is not a blind peer.** It answered from inside the tool that built this repo, with live
  browsing and partial authorship of the response format. It is used as the *consensus anchor and
  the only sourced baseline*, not as an independent sample. See its capture file's note.
- **Snapshot in time.** Model versions move monthly. Every capture is timestamped; treat results
  as a 2026-08 snapshot.
- **"No ground truth" for the architecture itself.** Only falsifiable sub-claims (does a tool
  exist? does a model fit in 32 GB? does a version number resolve?) and cross-model consensus are
  scored — never "the design is correct."

---

## License

- **Code** (`analysis/scripts/`, `Makefile`, CI): [MIT](LICENSE).
- **Corpus + analysis + docs**: [CC-BY-4.0](LICENSE-DATA). Attribute this repository.
- Third-party model responses are reproduced for research/commentary; each remains the work of its
  respective vendor's system and is quoted verbatim with attribution in its capture file.

## Citation

See [`CITATION.cff`](CITATION.cff). Short form:

> Aryal, R. (2026). *Large Language Models as Systems Architects: A Controlled Study of Consensus, Fabrication, and Constraint Reasoning on One Hard Design Task* (dataset and analysis code). Zenodo. https://doi.org/10.5281/zenodo.22245991

Manuscript under review at *Cureus Journal of Computer Science* (Springer Nature).
