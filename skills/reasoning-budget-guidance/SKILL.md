---
name: reasoning-budget-guidance
description: Pick the model tier and reasoning effort per task class instead of defaulting to maximum everywhere. Consult when choosing a model for a task, batching work, or when spend matters — "which model for this", "do I need the big model".
derivation: original
---

# Reasoning Budget Guidance

## Task-class → tier
- **Mechanical** (rename, format, boilerplate, simple extraction): smallest tier, minimal reasoning. Errors are cheap and obvious.
- **Standard implementation** (a function against clear specs, tests, straightforward debugging): mid tier, default reasoning.
- **Design / architecture / security review / gnarly debugging** (many interacting constraints, expensive-to-detect errors): top tier, extended reasoning.
- **Retry after a cheap-tier failure:** retry once on the same tier *with the failure output injected* before escalating a tier — most first failures are missing context, not missing capability.

## Principles
Cost of an error > cost of the tokens → buy reasoning. Output length is not reasoning need — long boilerplate is still mechanical. Surface caveat: effort/thinking controls are per-surface (frontmatter, API params, or a picker); where only a model picker exists, this mapping is guidance for the human's choice.
