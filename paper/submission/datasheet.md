# Datasheet — the LLM systems-architecture response corpus

Format: Gebru et al. "Datasheets for Datasets". Companion to *LLMs as Systems Architects*.
Repository: <https://github.com/roshanaryal1/llm-architects> (MIT code / CC-BY-4.0 data).

## Motivation

- **Why was the dataset created?** To study how frontier LLM systems respond to one hard,
  open-ended systems-architecture task under a fixed consumer-hardware constraint, and to build
  a reusable protocol for evaluating such open-ended design output without a ground-truth
  answer key.
- **Who created it / funded it?** Roshan Aryal (Otago Polytechnic). No external funding.

## Composition

- **What do instances represent?** One instance = one *system capture*: the verbatim response
  of one LLM product to one frozen prompt in one session, plus its self-reported metadata
  (model name, version, browsing state, date), its own cited-sources list, and structured
  reviewer notes.
- **How many instances?** 13 v1 captures from 11 systems (one system, DeepSeek, contributes 3
  reasoning-mode captures). Plus 10 controlled-paraphrase captures (v2/v3) from a 5-system
  subset, used only for the prompt-sensitivity analysis.
- **Is it a sample or the population?** A purposive sample of widely used frontier LLM
  products available to a single user 2026-08-31. Not random; chosen for vendor and
  architecture coverage.
- **What data does each instance contain?** Markdown with YAML front-matter (`ai_name`,
  `provider`, `browsing_enabled`, `prompt_version`, `date_run`, `run_by`, `notes_on_run`,
  `trust_rating`), a verbatim `## Raw response`, `## Model's own cited sources`, and
  `## Reviewer notes`.
- **Labels / targets?** A 39-axis decision matrix (`data/decisions-matrix.csv`) and four
  independent 9-dimension rubric score sets (`analysis/scoring/`), plus an adjudicated score
  set and a web-verified tool/model register.
- **Missing information?** Some systems did not disclose an exact model variant (recorded as
  "undisclosed"). Two free-tier systems served different underlying models between sessions
  (documented in the paper, Section 9.4).
- **Confidential or offensive content?** None. All content is model-generated technical text.

## Collection process

- **How collected?** Manually: the frozen prompt was pasted into each product's web interface
  on 2026-08-31; the full response was copied verbatim into a capture file. No API, no
  automated scraping.
- **Who collected it?** The author.
- **Over what timeframe?** v1 captures on 2026-08-31; v2/v3 paraphrase captures on 2026-09-01.
- **Ethical review?** Not required — no human subjects, no personal data.

## Preprocessing / cleaning / labelling

- **Any preprocessing?** None to the raw responses (verbatim; only dated correction notes are
  appended, never edits). Decision-axis phrases and rubric scores are added as separate files.
- **Is raw data saved?** Yes — the raw response is the canonical artefact.
- **Labelling procedure?** 9-dimension 0/1/2 rubric applied independently by four raters (one
  author-derived, three frontier LLMs on an identical packet); disagreements adjudicated;
  factual sub-claims web-verified against sources fixed to the capture window. Full procedure
  and inter-rater agreement in the paper, Section 9.3, and `analysis/scoring/`.

## Uses

- **Intended uses?** Studying LLM consensus and failure modes on open-ended technical design;
  methodology research on LLM-as-judge and verification protocols; a worked example of the
  training-cutoff / retrieval-failure rater bias.
- **Uses to avoid?** Do not treat the adjudicated bands as a general model leaderboard (the
  ranking is coarse and instrument-specific). Do not treat the reference architecture as
  validated-optimal or as current past 2026. Do not reuse the rubric as a black-box scorer
  without the anchored exemplars.

## Distribution

- **How distributed?** Public GitHub repository (made public at paper publication).
- **Licence?** MIT for code and scripts; CC-BY-4.0 for data, prompts, rubric, and analysis
  text.
- **IP / ToS constraints?** Responses are model-generated text collected under each product's
  normal consumer terms of use; released for research under CC-BY-4.0 with provenance recorded.

## Maintenance

- **Who maintains it?** The author.
- **Update policy?** The corpus is frozen as a dated snapshot. Corrections are appended as
  dated notes, never silent edits. Any follow-up capture wave will be a separate, dated
  directory.
- **Contact?** roshanaryaal@gmail.com.
