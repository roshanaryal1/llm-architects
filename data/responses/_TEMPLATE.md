---
ai_name:             # e.g. GPT-5, Gemini 3 Pro, Grok 4, Llama 4 Maverick, Mistral Large 3
model_version_id:    # exact version / ID if shown, else "not shown"
provider:            # OpenAI / Google / xAI / Anthropic / Meta / Mistral / DeepSeek / Alibaba / ...
interface:           # web app / API / mobile app / CLI / local
browsing_enabled:    # yes / no / unknown
knowledge_cutoff:    # as stated by the model, else "unknown"
prompt_version:      # v1  (only v1 is frozen; v2/v3 are planned)
date_run:            # YYYY-MM-DD
run_by:              # your GitHub handle
notes_on_run:        # refusals, length limits, multi-message answers, clarifying questions, etc.
trust_rating:        # HIGH | MEDIUM-HIGH | MEDIUM | LOW  — plus a one-line reason
---

## Raw response

<!--
  Paste the AI's answer VERBATIM. Do not fix typos, reflow tables, shorten, or reformat.
  Multi-message answer? Concatenate with "--- [continuation N] ---" and note it in notes_on_run.
-->


## Model's own cited sources

<!--
  Copy the model's citations here as a clean list (needed for the citation-quality analysis, RQ5).
  If the model cited nothing, write exactly:  NONE
-->


## Reviewer notes

<!-- Evidence-based. Quote the response text you are flagging. Cover at least: -->

### Recency (RQ4)
<!-- Are the tools/models current for date_run? Name every stale pick. -->

### Hallucination (RQ2)
<!-- List every tool, model, version number, benchmark figure, or repo URL that does not resolve.
     Categorise (total fabrication / attribute corruption / identifier hijack / placeholder /
     semantic) and rate severity. -->

### Constraint reasoning (RQ3)
<!-- Does the co-resident model set fit 32 GB? Run:
       python3 analysis/scripts/memory_budget.py --weights <gb> <gb> --ctx <n> [--browser]
     Paste the verdict. Note any assume-CUDA / assume-eGPU / ignore-KV-cache errors. -->

### Internal consistency (RQ6)
<!-- Contradictions within the response (recommends X here, forbids X there; security stance vs
     an install command; etc.). -->

### Agreements vs existing responses
<!-- Bullet the points where this response lines up with the others (consensus signal). -->

### Divergences vs existing responses
<!-- A small table is ideal: | axis | this response | Claude (anchor) | -->

### Provisional rubric score (rater 1)
<!-- 0/1/2 per docs/rubric.md dimension, until a second rater is onboarded. -->
