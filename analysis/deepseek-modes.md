# DeepSeek: one model, three modes

DeepSeek is the only system in the corpus with more than one capture. All three are the **same base
model — DeepSeek-V4-Pro** (the free `chat.deepseek.com` default since 2026-04-24) — run in three
different chat modes:

| capture | mode | `canonical` | trust | fabrications |
|---|---|---|---|---|
| `deepseek-expert` | DeepThink / deep-reasoning | **yes** | MEDIUM-HIGH | none (real tools; only stale point-versions) |
| `deepseek-instant` | fast / non-thinking | no | LOW | `Rapid-MLX`, `DeepSeek Harness (DSH)` / `Local DSH`, `Gemma 4 26B`, `Qwen3.5/3.6/3.8` tags |
| `deepseek-instant-deepthink` | Instant + DeepThink toggle | no | LOW | `Ornith-1.0-9B`, `Qwen3.5-35B-A3B` tag, `WhipDesk`, `Cloak`, `Helmrig`, `RemoteVibe`, `Lody`, `DiffResearch`, `LightAgent`, `Engram-Mem`, invented tok/s + SWE-bench numbers; also advises memory oversubscription |

## Why we keep all three but count only one

- **"One answer per AI" for RQ1 (consensus):** `data/systems.csv` marks `deepseek-expert` as the
  canonical DeepSeek answer. Per-system agreement tallies use it and ignore the other two, exactly
  as every other vendor contributes one best-effort free-tier answer.
- **The other two are kept as mode-variant data points** for:
  - **RQ2 (hallucination):** the mode effect below is a result, not noise.
  - **RQ6 (consistency / sensitivity):** same weights, same prompt, three outputs — a within-model
    sensitivity measurement other vendors can't give us.
- **We never merge the files.** `CONTRIBUTING.md` requires verbatim captures; merging would also
  erase the finding.

## The mode effect (provisional)

Holding the model and the prompt fixed, the reasoning mode changes the output category:

- **deep-reasoning mode (`deepseek-expert`)** → bucket 2 in the corpus's recency/rigour split:
  real tools throughout (Claude Code, Redis+Celery, Grafana+Prometheus, Docker+seatbelt), only
  point-versions lag; one internal contradiction (recommends Docker, then forbids "Docker for Mac").
- **non-reasoning / fast modes (`deepseek-instant`, `deepseek-instant-deepthink`)** → bucket 3
  ("confident futurism"): both invent plausible-sounding tools and models, with `deepseek-instant-deepthink`
  producing the highest fabrication count of any single capture.

Cross-vendor echo: **`Rapid-MLX` + the `raullenchai` Homebrew tap + `Gemma 4`** appear in *both*
`deepseek-instant` and `meta-llama-4` — a shared hallucination attractor, not a one-off.

**Implication for the paper:** "which DeepSeek model" is the wrong question; "which mode" is the
right one. Toggling extended reasoning on this model moves it a full bucket on grounding and
fabrication. Worth a dedicated subsection and, ideally, a controlled re-run (issue #6/#8 territory:
same prompt, same model, N modes, scored).
