# PLAN — Advanced Skills Build (internal registry)

**Audience:** A coding agent operating on the internal registry repo.
**Objective:** Author org-specific skills — ADR, incident postmortem, debug, cost-attribution, burn-rate forecast, compliance review, and port automation — directly in the internal registry, in registry dialect, each eval-gated and provenance-tracked. These encode internal context by design.
**Non-goal:** Publishing any of these to a public remote or personal account (the pipeline is one-way: public→internal, never reverse). Re-authoring the generic externally-derived skills — those are vendored in from the public repo (see Phase 0).
**Execution surface:** Internal registry repo; issue tracker / VCS / wiki MCP servers available; IDE surface — **no hooks**, so any lifecycle enforcement is runner-side or human, never an advisory SKILL.md hook.

---

## ⚠ HARD CONSTRAINTS (read before any task)

1. **Registry-only, never published publicly.** These skills encode internal context (the ADR layer, incident postmortems, the debug gate). They must never reach a public remote, a personal account, or any repo whose build artifacts ship. One-way pipeline: public→internal.
2. **Outbound controls still bind, internally.** AI config gitignored; excluded from build artifacts; MCP keys via env vars, never plaintext `mcp.json`; pre-commit + CI assert AI config is absent from shippable paths. Same *enforced* controls as the public repo, applied here.
3. **Every knowledge-base write is `gate: human`.** ADR, postmortem, and any LEARN write are a memory-poisoning vector — a wrong "decision" propagates with ADR authority into every future session. Until the knowledge-compilation quality gate exists, writes land in `staging/`, promoted by a human. Non-negotiable.
4. **Maker/checker, never maker alone.** The ADR writer ships with an ADR evaluator; the postmortem with a review pass. Same-model self-review is weak evidence — pair these with the vendored `grill-me` / `junior-to-senior` critics. No writer ships without its checker.
5. **Dialect + discipline.** Registry dialect (`agents/ commands/ skills/ tools/ org-standards/`). Standard-compliant frontmatter, registry bookkeeping under `metadata`. Every skill: an eval case, a `PROVENANCE.md` row, `owner`, `enforcement`.

---

## Context — dialect + dependency on the public repo

Directory layout and frontmatter shape are identical to the public repo (`agents/ commands/ skills/ tools/`, plus `org-standards/` for policy-shaped artifacts; SKILL.md with `name` / `description` / `metadata`). Preserve the `commands` (directly-invocable) vs `skills` (agent-consumed) distinction.

These advanced skills **build on** the generic skills from the public repo (`PLAN-skill-list-build.md`). Phase 0 vendors a pinned, security-reviewed snapshot of that repo before any advanced skill is authored; advanced skills then compose with the vendored generics (the ADR evaluator uses `grill-me`; `eval-writer` gets wired to real traces; the cost tools reuse `prompt-cache-inflation-check`). Crucially, the vendored snapshot also includes the four creators (`create-agent` / `create-skill` / `create-command` / `create-tool`) and `tools/validate.py` — **every skill below is scaffolded with the matching creator, then filled in.** Hand-rolling is the exception, not the default.

---

## Phase 0 — Vendor the generic snapshot + verify gates (do first)

- [ ] Vendor a **pinned, security-reviewed snapshot** of the public skills repo (recorded tag/SHA) into the registry. NOT a live submodule from a personal account. (This is the public plan's HUMAN GATE — it must be complete before any internal work.)
- [ ] Verify the vendored generics pass the registry validator and the outbound-controls scan.
- [ ] Confirm the four creators and `tools/validate.py` are present in the vendored snapshot and runnable — they author every skill in Phases 1–3.
- [ ] Confirm `staging/` exists with a human-promotion flow (constraint #3 dependency).
- [ ] **Acceptance:** snapshot pinned at a recorded SHA; registry validator green on the vendored set; a planted AI-config file in a shippable path is blocked by CI.

---

## Phase 1 — Knowledge-writing skills (`gate: human`, maker/checker)

Scaffold each via the vendored creator (`create-skill` for skills, `create-agent` for the evaluator), then fill the body.

- [ ] `skills/adr-writer` — emits an ADR into `staging/decisions/` in your ADR format. **Must contain:** ADR structure (context / decision / consequences / alternatives); the `gate: human` checkpoint; output to staging, never directly to `decisions/`. `derivation: original`.
- [ ] `agents/adr-evaluator` — critiques a proposed ADR: contradiction with existing ADRs (via vendored `knowledge-lint`), missing alternatives, unstated consequences. **Must contain:** the maker/checker pairing with `adr-writer`; composition with `grill-me`. `derivation: adapted`.
- [ ] `skills/incident-postmortem` — triage → blameless postmortem → `staging/incidents/`. **Must contain:** triage structure; blameless framing; `gate: human`; staging output. Upstream shape: engineering:incident-response (adapted).
- [ ] **Acceptance:** ADR and postmortem outputs land in `staging/` (never directly in `decisions/` or `incidents/`); a `gate: human` task halts auto-progress; the evaluator runs against a planted contradictory ADR and flags it.

---

## Phase 2 — Debug + compliance

Scaffold via the vendored creators (`create-skill`, `create-command` for the reviewer), then fill the body.

- [ ] `skills/debug-procedure` — structured reproduce → isolate → diagnose → fix; **read-only during debug** per guardrails config (write_allowed: false during debug sessions). **Must contain:** the read-only constraint binding; the diagnosis structure. Upstream shape: engineering:debug + systematic-debugger (adapted); the generic reproduce/isolate portion may be sourced from the vendored shape, the production-gate wiring is added here.
- [ ] `org-standards/compliance-reviewer` — regulatory / policy reviewer; attaches compliance checks by archetype. Policy-shaped → `org-standards/`, not a generic skill. **Must contain:** the compliance-checklist mapping; positioned explicitly as pre-review, not a gate (org SDLC: human-approved merge, always). `derivation: adapted`.
- [ ] **Acceptance:** `debug-procedure` cannot write during a debug session (guardrail enforced, verified); `compliance-reviewer` emits findings against a planted compliance-relevant diff.

---

## Phase 3 — Cost instrumentation + automation (runner / MCP layer)

Scaffold each with the vendored `create-tool`, then fill the body.

- [ ] `tools/cost-attribution` — bucket-decomposition instrumentation at the runner + MCP layer: uncached input / cached input / cache-write / output / reasoning. The measurement layer that makes cost-reduction claims defensible. **Must contain:** the five-bucket schema; where it taps (runner + MCP layer, since platform AI credits may not expose buckets natively). Reuses `prompt-cache-inflation-check`. `derivation: original`.
- [ ] `tools/burn-rate-forecast` — per-story burn-rate + projected overrun, appended to `loop-report.md`. **Must contain:** the forecast metric ($/completed-task, projected overrun); integration with the existing loop-report format. `derivation: original`.
- [ ] `tools/port-project` — automation to scaffold a new app repo from `templates/` with full harness structure. **Must contain:** the porting steps; boundary enforcement (app specifics → app-repo `_variables.yml`; only org-level artifacts → registry). `derivation: original`.
- [ ] *(optional)* extend the vendored `eval-writer` with internal trace sourcing — wire to real `implement-story` run traces (3–5 golden cases). Composition, not a re-author.
- [ ] **Acceptance:** `cost-attribution` emits all five buckets on a sample run; burn-rate appears in `loop-report.md`; `port-project` scaffolds a test repo that passes the registry validator.

---

## OUT OF SCOPE

- The generic externally-derived skills — built in the public repo, vendored in Phase 0, never re-authored here.
- Publishing any internal skill to any public remote or personal account.
- Step-0-gated hook features — deferred until the invocation-engine decision; advisory hooks only until then, and labelled advisory.

---

## HUMAN GATES (agent stops; does not auto-proceed)

The agent stages; the human performs the irreversible/authoritative act.

- **Any write to `decisions/` or `incidents/`** — the agent writes to `staging/`; the human reviews and promotes.
- **Compliance-reviewer findings** — advisory only; the human owns the merge decision (org SDLC: agent-prepared PR, human-approved merge, always).

---

## Definition of Done

- [ ] Vendored generic snapshot pinned at a recorded SHA + validator-green; the four creators + `tools/validate.py` confirmed present and runnable; `staging/` promotion flow live.
- [ ] ADR / postmortem / debug / compliance / cost-attribution / burn-rate / port skills scaffolded via the vendored creators and authored in dialect, each passing `tools/validate.py`, with an eval case, a `PROVENANCE.md` row, `owner`, and `enforcement`.
- [ ] No knowledge-writing skill writes directly to `decisions/` or `incidents/` (staging-only, verified).
- [ ] No internal skill is committed to a public remote or a shippable artifact path (scan clean across full history).
- [ ] Maker/checker pairing verified — no writer present without its critic.
