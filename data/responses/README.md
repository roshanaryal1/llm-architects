# `data/responses/`

One file per run. **Verbatim** model output plus reviewer commentary. 13 base captures from 11
systems (DeepSeek contributed 3 modes of one base model), plus `prompt-v2`/`v3` paraphrase runs
for five systems (`<slug>-v2.md` / `<slug>-v3.md`).

## Base captures (`prompt_version: v1`)

| File | System | Browsing | Sources | Trust |
|------|--------|----------|---------|-------|
| `claude-sonnet-5.md` | Anthropic Claude Sonnet 5 | yes | ~97 URLs | HIGH (anchor, not blind) |
| `mistral-large-3.md` | Mistral Le Chat — Large 3 | yes | ~36 | HIGH |
| `gpt-5.md` | OpenAI ChatGPT — GPT-5.6 Luna | yes | ~20 inline, 0 URLs | HIGH |
| `perplexity.md` | Perplexity — Sonar | yes | ~17 URLs | MEDIUM-HIGH |
| `kimi-instant.md` | Moonshot Kimi — Instant | yes | search markers, 0 URLs | MEDIUM-HIGH |
| `deepseek-expert.md` | DeepSeek-V4-Pro — deep-reasoning mode (canonical DeepSeek) | no | 0 | MEDIUM-HIGH |
| `gemini-3.1-pro.md` | Google Gemini 3.1 Pro | no | 0 | MEDIUM |
| `qwen-3.7-plus.md` | Alibaba Qwen 3.7 Plus | no | 0 | MEDIUM |
| `grok-4.md` | xAI Grok 4 | no | 0 (M6 spec correct) | MEDIUM |
| `z-ai.md` | Zhipu z.ai — GLM class | no | 0 usable | MEDIUM → MED-LOW |
| `meta-llama-4.md` | Meta AI — hosted Llama 4 | yes | 99 refs, ~60% junk | LOW |
| `deepseek-instant.md` | DeepSeek-V4-Pro — fast mode | no | 0 | LOW |
| `deepseek-instant-deepthink.md` | DeepSeek-V4-Pro — instant + DeepThink | no | 0 | LOW |
| `_TEMPLATE.md` | — | — | — | copy this to add one |

Paraphrase runs: `gemini-3.1-pro`, `gpt-5`, `perplexity`, `qwen-3.7-plus`, `z-ai` each have
`-v2.md` (RFC-framed paraphrase) and `-v3.md` (v1 minus the anti-anchoring steer).

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
