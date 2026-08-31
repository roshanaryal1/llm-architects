# `prompts/`

The study instrument.

| File | Status | Purpose |
|------|--------|---------|
| `prompt-v1.md` | **FROZEN 2026-08-31** | Canonical prompt. Every response in `data/responses/` was run against this. Do not edit. |
| `prompt-v2.md` | planned | Paraphrase 1 — reordered sections, reworded framing. For prompt-sensitivity (RQ6). |
| `prompt-v3.md` | planned | Paraphrase 2 — drops the "don't assume X is the answer" framing, to test how much that steer matters. |

## Using it

Paste **only** the text between `=== PROMPT START ===` and `=== PROMPT END ===` — the responder
header (fixed date, browsing/version declaration, Sources request) is part of the instrument.

## Changing it

You don't. A change to the task means a new versioned file and a re-run of the whole set. Record
which version each response used in that response's `prompt_version` front-matter field.
