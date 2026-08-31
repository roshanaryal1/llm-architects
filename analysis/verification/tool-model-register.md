# Tool / model / spec verification register

**Purpose.** Every falsifiable claim (a named tool, model, version, size, benchmark number, or
hardware spec) that the study needs to classify as *real*, *wrong*, or *unresolved* — verified
against **web sources dated 2026**, not against any rater model's training knowledge.

**Why this file exists.** The anchor rater (Claude Sonnet, ~Jan 2026 knowledge cutoff) flagged 14
tools/models across the corpus as "FABRICATED" in `data/decisions-matrix.csv` reviewer notes and in
`analysis/consensus/README.md`. On web verification (2026-09-01), **zero of those 14 were confirmed
fabricated**; at least 12 are real products or model releases dated **after the anchor's cutoff**
(Feb–Aug 2026). The false-positive flags were an artefact of rater cutoff, not of the responses.

This register is now the single source of truth for RQ2 (fabrication) and RQ4 (recency). The
`decisions-matrix.csv` reviewer notes and the consensus README must be corrected to match it.

---

## Verdict codes

| Code | Meaning |
|------|---------|
| `REAL` | Named thing exists; spec as stated is accurate (or close enough not to be an error). |
| `REAL / SPEC-OFF` | Thing exists but a stated size/version/number is wrong. |
| `WRONG` | Specific falsifiable claim is contradicted by a primary/reliable source. |
| `UNRESOLVED` | No web evidence found either way. Not proof of fabrication — treat as unknown. |
| `FABRICATED` | Positively established as not existing (would need a strong negative search). None yet. |

---

## A. Tools / frameworks / engines

| Claim (as stated in a response) | Responses that used it | Verdict | Evidence (2026) |
|---|---|---|---|
| **Rapid-MLX** inference engine | deepseek-instant, meta-llama-4, grok-4 | `REAL` | `github.com/raullenchai/Rapid-MLX`. Began as vLLM-MLX (Wayner Barrios), renamed March 2026. Drop-in OpenAI API; works with Claude Code / Cursor / Aider. |
| **vLLM-MLX** as #1 engine | z-ai, kimi (alt) | `REAL` | Predecessor project to Rapid-MLX; MLX port of vLLM. z-ai's throughput numbers ("130–464 tok/s", "3.4x") remain `UNRESOLVED` — no source. |
| **DeepSeek Harness (dsh / DSH)** | deepseek-instant | `REAL` | `github.com/deepseek-ai/deepseek-harness`. Open-sourced 2026-08-13, MIT. "Everything is a plugin"; `Model + Harness = Agent`; localhost-only; developer preview. |
| **OpenClaw** / OpenClaw Gateway | meta-llama-4 | `REAL` (tool) | OpenClaw: Peter Steinberger. Warelay (Nov 2025) → Moltbot (2026-01-27, Anthropic TM complaint) → OpenClaw. Has a Wikipedia page. "Gateway" sub-component `UNRESOLVED`. |
| **Claw Code** | z-ai | `REAL` | Clean-room Python/Rust rewrite of Claude Code after the 2026-03-31 source-map leak (~512k LOC TS exposed). ~72k GitHub stars in first days. |
| **Clawtrol** dashboard | meta-llama-4 | `REAL` | `github.com/wolverin0/clawtrol`. Kanban "mission control" for AI coding agents. |
| **WhipDesk** mobile control UI | deepseek-instant-deepthink | `REAL` | `github.com/BinaryBananaLLC/WhipDesk`. "Control AI coding agents from your phone." Includes a "prompt scheduled to fire at 3am when your session resets" feature — exactly as the response described. |
| **LightAgent** | deepseek-instant-deepthink | `REAL` | `github.com/wanxingai/LightAgent`; arXiv 2509.09292. v0.10.0 (2026-08-15): durable Sessions, Capability Registry, Inbox/Goals/Budgets, SQLite FTS5. ~1000 LOC, no LangChain dep. |
| **nono** kernel sandbox | meta-llama-4 | `REAL` | Sandbox tool using Landlock (Linux) / Seatbelt (macOS); file + network isolation. Referenced in 2026-05 blog posts. |
| **oMLX** (SSD-tiered KV cache) | mistral-large-3, kimi | `UNRESOLVED` | No direct source located yet. Re-search before treating as real or fake. |
| **memo** (memory pattern/tool) | meta-llama-4 | `UNRESOLVED` | Nearby real tools exist (MemOS `github.com/MemTensor/MemOS`, Memori). Exact "memo" not confirmed. |
| **cplt** kernel sandbox | meta-llama-4 | `UNRESOLVED` | Not located. |
| **agent-policy-engine** | meta-llama-4 | `UNRESOLVED` | Generic name; not located as a specific project. |
| **Clawtrol / OpenClaw "channels"**, `openclaw onboard --install-daemon` | meta-llama-4 | `UNRESOLVED` | Parent projects real; exact CLI/subfeatures not verified. |
| **DiffResearch** research pipeline | deepseek-instant-deepthink | `UNRESOLVED` | Not located. |
| **WhipDesk siblings: Cloak, Helmrig** | deepseek-instant-deepthink | `UNRESOLVED` | Not located; possible misspellings. |
| **pi-search-hub** (12–19 search backends) | z-ai | `UNRESOLVED` | Not located. |
| **"Agent Safehouse", "Cua VMs"** | grok-4 | `UNRESOLVED` | grok itself hedged these as unverified. |
| llama-swap, sqlite-vec, LiteLLM, OpenHands, Aider, OpenCode, LangGraph, PydanticAI, Goose, GPT-Researcher, Firecrawl, Exa, PaperQA2, Graphiti, Mem0, Letta, Caddy, OrbStack, Lima, `sandbox-exec` | many | `REAL` | Established pre-cutoff; not disputed. Spot-check versions only. |

## B. Models

| Claim | Responses | Verdict | Evidence (2026) |
|---|---|---|---|
| **Gemma 4** — sizes E2B / E4B / 12B / **26B-A4B MoE** / **31B dense** | deepseek-instant ("26B"), meta-llama-4, grok-4 ("31B") | `REAL` | Released 2026-04-02 (12B Unified 2026-06). `huggingface.co/google/gemma-4-31B`, `google/gemma-4-26B-A4B-it`. **Both 26B and 31B are real variants** — the "unstable size ⇒ confabulated" reasoning was invalid. |
| **Qwen3-Coder-Next** — 80B MoE, 3B active, 512 experts, 256K ctx | gpt-5 (rejects as too big — **correct**), z-ai (calls it 8B — **wrong**) | `REAL` | `huggingface.co/Qwen/Qwen3-Coder-Next`. 80B-A3B. |
| **GLM-4.7-Flash** — 30B-A3B MoE, MIT, 59.2% SWE-bench Verified | grok-4 (alt list) | `REAL` | Zhipu, released 2026-01-19. MLA architecture. grok's "30B-A3B" label is spec-accurate. |
| **Ornith-1.0-9B** (+ 31B / 35B-MoE / 397B-MoE) | deepseek-instant-deepthink (primary + "Claude Code backend") | `REAL` | `huggingface.co/deepreinforce-ai/Ornith-1.0-9B`; Ollama `ornith:9b`. Self-improving agentic-coding family, post-trained on Gemma 4 + Qwen 3.5, MIT. ~19 GB bf16. |
| **Qwen3-Coder-30B-A3B** 4-bit MoE (consensus heavy model) | claude, perplexity, deepseek-expert, kimi, mistral, gpt-5 (alt) | `REAL` — **re-verify exact tag** | Qwen3-Coder family real. Confirm the precise "30B-A3B" tag and 4-bit artifact size against Qwen's model card. |
| **Qwen3.6-35B-A3B** | gpt-5 (primary), mistral (alt) | `REAL` — **re-verify** | Confirm against Qwen releases. |
| **Qwen3.5-35B-A3B** tag + OpenRouter id `qwen/qwen3.5-35b-a3b-20260224` | deepseek-instant-deepthink, meta-llama-4 | `UNRESOLVED` — **re-verify** | May be a real point-release or a wrong tag for 3.6/Coder-30B. Check OpenRouter + Qwen. |
| **GLM-4.5-Air** (~4 GB 4-bit) | z-ai (light model) | `REAL` — 2025-dated | Real Zhipu model; note it's an older pick than GLM-4.7-Flash. |
| **GLM-5.2** (cloud burst) | mistral, gpt-5 | `REAL` — **re-verify** | Check Zhipu's current flagship. |
| **gpt-oss-20b** | claude (mid reasoner) | `REAL` | OpenAI open-weight model. |
| **Frontier free-tier identities** — GPT-5.6 Luna, DeepSeek-V4-Pro, Kimi K3, Mistral Large 3, Gemini 3.1 Pro | n/a (the raters themselves) | `REAL` | Web-checked 2026-08-31; see project memory. Re-confirm Gemini 3.1 Pro naming. |

## C. Hardware — Apple M6 Mac mini

| Claim | Responses | Verdict | Evidence |
|---|---|---|---|
| Announced **2026-08-25** | mistral ("2026-08-25"), gpt-5 ("2026-08-25") | `REAL` | Apple newsroom + MacRumors, 2026-08-25. |
| **170 GB/s** memory bandwidth (at 24/32 GB; 153 GB/s at 16 GB) | claude, mistral, gpt-5, perplexity, grok (in prose) | `REAL` | M6: up to 170 GB/s, up from M5 153 / M4 120. Config-dependent. |
| "M6 expected **~300+ GB/s**" | meta-llama-4 (only) | `WRONG` | Real M6 = 170 GB/s. `grok-4`, by contrast, states the full spec incl. 170 GB/s correctly. |
| M6 = 12-core CPU, dual 16-core Neural Engine | mistral, gpt-5 | `RE-VERIFY` | Check against Apple M6 spec page / Wikipedia. |
| 32 GB max unified memory | all | `REAL` | Base Mac mini M6 tops out at 32 GB. |
| "no M6-specific facts" (generic Apple Silicon only) | z-ai, qwen, gemini, kimi, deepseek (all modes), meta | n/a | Not an error — a recency gap. Feeds RQ4, not RQ2. |

## D. Benchmark numbers (all `UNRESOLVED` unless sourced)

| Number | Response | Status |
|---|---|---|
| OpenHands ~72% SWE-bench | meta-llama-4 | `RE-VERIFY` against OpenHands docs. |
| vLLM-MLX "130–464 tok/s", "3.4x faster" | z-ai | `UNRESOLVED` — no source. |
| MLX "~35–48 tok/s" on M6 | grok-4 | `UNRESOLVED` — plausible extrapolation, not measured. |
| sqlite-vec "4 ms latency" | kimi | `UNRESOLVED` — no source. |
| GLM-4.7-Flash 59.2% SWE-bench Verified | (not cited by a response; from our own verification) | `REAL` per Zhipu. |

---

## E. Genuine defects that survive verification

These are **not** recency artefacts. They stay in the analysis.

| Response | Defect | Type |
|---|---|---|
| `z-ai` | Qwen3-Coder-Next given as "8B ~5 GB" — real is 80B MoE. Load-bearing (it's the primary coding model). | model size error |
| `z-ai` | Same model quoted at 5 GB (§1) and 14 GB (§C). | internal inconsistency |
| `z-ai` | 3-instance concurrent co-resident diagram vs "primary stays loaded, others on-demand" prose; "fits within 32 GB with swapping". | internal inconsistency + hardware slip |
| `grok-4` | none beyond 0 sources — it gets the full M6 spec (incl. 170 GB/s) right; alt-list picks all real. | (no surviving factual defect) |
| `deepseek-expert` | Recommends Docker in sections A/H, forbids "Docker for Mac" in J; dashboard binds `0.0.0.0` vs "no public exposure". | internal contradiction |
| `deepseek-instant` | Recommends Ollama in Phase 4, forbids it in section J. | internal contradiction |
| `deepseek-instant-deepthink` | 256K context claim vs 1–2 GB KV budget; advocates memory oversubscription (~32–34 GB always-loaded). | hardware violation |
| `meta-llama-4` | 99 numbered refs; ~60% are junk GitHub commit/PR/issue/`SKILL.md` URLs; same tool given multiple different repo URLs; ref [38] mis-titles a real arXiv paper. | citation quality (verifiable independent of recency) |
| `gemini`, `kimi` | Stale cloud fallback list (Claude 3.5 Sonnet / GPT-4o). | recency (RQ4) |

---

## F. Actions this register forces

1. **`data/decisions-matrix.csv`** — remove/relabel every `(FABRICATED)` / `(NOT REAL)` / `(not real)`
   note for the items marked `REAL` above. Replace with `(real; post-anchor-cutoff release, DATE)`.
2. **`analysis/consensus/README.md`** — delete the "cross-vendor shared hallucination" finding as
   stated (Rapid-MLX / Gemma 4). Replace with the anchor-cutoff false-positive finding.
3. **`data/responses/*.md` `## Reviewer notes`** — same correction, per file: deepseek-instant,
   deepseek-instant-deepthink, meta-llama-4, grok-4, z-ai.
4. **`docs/rubric.md` + `analysis/scoring/RATER-PACKET.md`** — dim 3 & 4 scoring MUST instruct the
   rater to web-verify each named tool/model against 2026 sources before scoring, and to treat
   "not in my training data" as `UNRESOLVED`, never as fabrication.
5. **Recency (RQ4) / the 3-way bucket split** — recompute against this register, not anchor
   judgment. Provisional effect: the "confident futurism" bucket-3 responses (deepseek-instant,
   deepseek-instant-deepthink, meta-llama-4) were *ahead of* the anchor on ecosystem currency, not
   behind it. Their real weaknesses are citation quality and internal consistency, not fabrication.
6. **Paper** — RQ2 becomes: *"LLM-as-rater training-cutoff bias produces systematic
   false-positive hallucination flags in systems-architecture evaluation."* Ground-truth table =
   section A + B of this file.

## G. Still to verify (next web pass)

oMLX · memo · cplt · DiffResearch · Cloak · Helmrig · pi-search-hub · agent-policy-engine ·
"Agent Safehouse" · "Cua VMs" · exact Qwen3-Coder-30B-A3B / Qwen3.6-35B-A3B / Qwen3.5-35B-A3B tags ·
GLM-5.2 · Gemini 3.1 Pro naming · M6 core layout · OpenHands SWE-bench % · Devstral Small 2 ·
Mistral Small 3.1 · Phi-4-14B.
