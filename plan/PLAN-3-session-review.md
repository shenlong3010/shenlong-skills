# PLAN-3 — Session Ops + Review

**Prerequisite:** PLAN-1 complete. Constraints from PLAN-1 apply unchanged.
**Objective:** Session continuity and adversarial review — the layer that makes multi-session work and self-checking cheap.

---

## Phase A — Session ops

- [ ] `commands/handoff-writer` — session state → `HANDOFF.md` brief for the next fresh session.
- [ ] `commands/context-audit` — what's loaded, rough token cost, trim suggestions.
- [ ] `tools/skill-lint` — description trigger-quality check, complements `validate.py` (source: anthropics skill-creator).

## Phase B — Reviewers

- [ ] `agents/grill-me` — Socratic adversarial plan/design reviewer; findings ranked by severity; pre-review, not a gate (source: JuliusBrussee).
- [ ] `agents/junior-to-senior` — surfaces what a senior catches that a junior misses: hidden coupling, ops burden, failure modes, unstated scope (source: JuliusBrussee).

## Phase C — Eval seed

- [ ] `commands/eval-writer` — run trace → `.eval.yml` golden case (input / expected / scorer).

---

## Definition of Done

- [ ] All creator-scaffolded, `validate.py`-green, scan-clean; `handoff-writer` produces a brief a fresh session can act on without the prior transcript.
