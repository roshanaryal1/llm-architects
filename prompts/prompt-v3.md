# Canonical Prompt — v3 (PLANNED — not yet written)

**Do not use for captures yet.**

v3 will be `prompt-v1.md` with **one deliberate ablation**: remove the "Do NOT assume that any
particular existing product, framework, model, agent platform, inference engine, orchestration
framework, or protocol is the correct answer" steer and the "Do not recommend tools because they
are popular" instruction.

Everything else stays identical to v1.

Goal: measure how much that single anti-anchoring instruction changes the spread of
recommendations and the fabrication rate — i.e. is the steer doing real work, or would the models
land in the same place without it?
