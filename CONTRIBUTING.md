# Contributing

This repo is a **research dataset**, not software. The most valuable contribution is a
carefully-captured new AI response. Analysis PRs are also welcome.

## Ground rules

1. **The prompt is frozen.** Never edit `prompts/prompt-v1.md`. If you think it needs to change,
   open an issue; a change means a `prompt-v2.md` and a re-run, not an in-place edit.
2. **Responses are verbatim.** Do not fix typos, reformat tables, shorten, or "clean up" a model's
   output. Reviewer commentary goes only in the clearly-marked `## Reviewer notes` section.
3. **Everything is attributable and timestamped.** Fill the whole front-matter block.
4. **No secrets, no large files.** Text only. CI rejects anything else.

## Adding a new model response

```bash
git checkout -b response/<model-slug>
cp data/responses/_TEMPLATE.md data/responses/<model-slug>.md
```

Slug convention: lowercase, hyphenated, `<vendor-or-family>-<version>[-<mode>]`, e.g.
`gpt-5`, `gemini-3-pro`, `llama-4-maverick`, `deepseek-expert`.

Then:

1. **Run the instrument.** Paste the text between `=== PROMPT START ===` and `=== PROMPT END ===`
   from `prompts/prompt-v1.md` into the target AI. Nothing else. If the model asks a clarifying
   question, answer only with "please proceed with reasonable assumptions and state them" and
   record that in `notes_on_run`.
2. **Front-matter.** `ai_name`, `model_version_id`, `provider`, `interface`, `browsing_enabled`,
   `knowledge_cutoff`, `prompt_version`, `date_run`, `run_by`, `notes_on_run`, `trust_rating`.
   `trust_rating` ∈ {HIGH, MEDIUM-HIGH, MEDIUM, LOW} with a one-line reason.
3. **`## Raw response`** — paste verbatim. If the answer was delivered over multiple messages,
   concatenate with a `--- [continuation N] ---` marker and note it in `notes_on_run`.
4. **`## Model's own cited sources`** — copy them, or write `NONE` if the model cited nothing.
5. **`## Reviewer notes`** — at minimum cover:
   - **Recency (RQ4):** are the tools/models current for the capture date? Name stale picks.
   - **Hallucination (RQ2):** list every tool, model, version number, benchmark figure, or repo
     URL that does not resolve. Rate severity.
   - **Constraint reasoning (RQ3):** does it fit 32 GB? Run
     `python3 analysis/scripts/memory_budget.py` against its model set and paste the verdict.
   - **Internal consistency (RQ6):** contradictions within the response.
   - **Agreements / divergences** vs the existing responses (a small table is ideal).
6. **Matrix.** Add a column to `data/decisions-matrix.csv` (append after the last filled column,
   before the blank placeholders, or fill a placeholder if the slug matches). Fill every row you
   can; use a short phrase, not a paragraph. Flag fabrications in-cell, e.g.
   `Rapid-MLX (FABRICATED)`.
7. **Changelog.** Add a dated line to `CHANGELOG.md`.
8. **Validate.** `make check` must pass.
9. Open a PR with the "New model response" template.

## Analysis contributions

- Consensus synthesis, contradiction catalogues, rubric scoring by a second rater, and small
  reproducible check scripts (stdlib only, MIT-licensed) are all welcome.
- Put scoring by a new rater in `analysis/scoring/<rater>-<date>.md` and do **not** overwrite an
  existing rater's file — inter-rater agreement depends on independent scores.

## Style

- Markdown, LF line endings, UTF-8 (`.editorconfig` enforces it).
- `make lint` runs `markdownlint` if you have it; the config is deliberately lenient because
  verbatim model output cannot be reflowed.
