# `data/responses/`

One file per AI system. **Verbatim** model output plus reviewer commentary.

## Files

| File | System | Browsing | Sources | Trust |
|------|--------|----------|---------|-------|
| `claude-sonnet-5.md` | Anthropic Claude Sonnet 5 | yes | ~97 | HIGH (anchor, not blind) |
| `qwen-3.7-plus.md` | Alibaba Qwen 3.7 Plus | no | 0 | MEDIUM |
| `deepseek-instant.md` | DeepSeek (fast mode) | no | 0 | LOW (fabricated stack) |
| `deepseek-expert.md` | DeepSeek (deep mode) | no | 0 | MEDIUM-HIGH |
| `_TEMPLATE.md` | — | — | — | copy this to add one |

Run `make responses` to regenerate this list from the front-matter.

## File contract

```
---
<YAML front-matter: ai_name, model_version_id, provider, interface, browsing_enabled,
 knowledge_cutoff, prompt_version, date_run, run_by, notes_on_run, trust_rating>
---

## Raw response
<verbatim — never edited>

## Model's own cited sources
<the model's citations, or NONE>

## Reviewer notes
<recency / hallucination / constraint-reasoning / internal-consistency /
 agreements + divergences vs other responses>
```

## Rules

- Never edit `## Raw response` after merge. Corrections go in a dated note appended to
  `## Reviewer notes`.
- `trust_rating` ∈ {HIGH, MEDIUM-HIGH, MEDIUM, LOW} + one-line reason.
- Keep reviewer notes evidence-based: quote the response text you're flagging.
- See `../../CONTRIBUTING.md` for the full submission workflow.
