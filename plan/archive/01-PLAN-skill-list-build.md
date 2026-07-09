# 01-PLAN — Skill List Build (personal public repo)

**Audience:** A Claude Code session executing this build. Human owner: Luke.
**Objective:** Author the externally-derived generic skill list as content-complete SKILL.md entries in the personal public repo, in the registry dialect, each provenance-tracked, so import into the company registry is a *copy, not a transform*.
**Non-goal:** Authoring any employer-derived skill (those are internal-first — see § OUT OF SCOPE); pushing to any remote; vendoring into the company registry.
**Execution surface:** A Claude Code session operating on the local personal skills repo. The dialect this plan depends on is embedded in § Context — do not assume prior knowledge of it. Downstream consumption is GitHub Copilot IDE: the portable value is SKILL.md *text*, not plugin/hook machinery.

---

## ⚠ HARD CONSTRAINTS (read before any task)

1. **Zero employer-internal content.** No internal server names, app names, domain-model terms, stack idioms tied to internal systems, tokens/keys, or any `/memory`-derived content. Generic by construction or it does not belong here. This is the outbound-exposure incident class.
2. **Provenance + license per skill.** Every skill's frontmatter carries `metadata: {owner, enforcement, derivation, upstream_repo, upstream_sha, license}`, and gets a row in `PROVENANCE.md`. No skill is complete without it. Pull the *shape* from upstream; write original prose — do not copy upstream text wholesale.
3. **Guards before content.** The scanners in Phase 0 must exist and prove themselves (plant a failure, confirm the guard catches it) BEFORE any skill is authored. Scan the diff range, not just the working tree — git history is permanent.
4. **No remote push, no vendoring.** This plan ends with the repo staged and committed locally. Publishing and company-registry import are HUMAN GATES (see below). The agent never runs `git push` to a public remote.
5. **Dialect fidelity.** Mirror the structure and frontmatter in § Context exactly. Standard-compliant frontmatter only (`name`, `description`, `metadata`, optional `license`/`allowed-tools`) — registry bookkeeping lives under `metadata`, never as top-level keys, or the standard validator rejects it.

---

## Context — the registry dialect (embedded for self-containment)

Directory layout:

```
agents/        subagent definitions (reviewers, critics)
commands/      directly-invocable harness ops (the human invokes these)
skills/        agent-consumed work skills
tools/         scripts + MCP-server scaffolds
docs/  templates/  .github/workflows/
README.md  LICENSE  CONTRIBUTING.md  PROVENANCE.md
.gitignore  .pre-commit-config.yaml
```

Distinction to preserve: **`commands`** = directly-invocable harness operations; **`skills`** = work the agent consumes mid-task. Both use SKILL.md format.

SKILL.md frontmatter shape (standard-compliant):

```yaml
---
name: <skill-name>
description: <what it does + when to trigger; pushy, to fight undertriggering>
metadata:
  owner: <name>
  enforcement: advisory | enforced
  derivation: original | adapted | copied
  upstream_repo: <url or "n/a">
  upstream_sha: <sha or "n/a">
  license: <MIT | Apache-2.0 | n/a>
---
```

---

## Phase 0 — Bootstrap (scaffold + guards + validator + creators)

Everything Phases 1–3 depend on. Ordering inside this phase is dependency-bound: scaffold → validator → guards (proven) → creators (which call the validator and emit from the template). **The four creators are hand-authored here** — `create-command` cannot create `create-command` (bootstrap paradox; the compiler-bootstrap pattern). From the end of this phase, every skill in this plan *and* the internal plan is creator-generated.

### 0A — Scaffold + guards + validator

- [ ] Create the directory layout in § Context. Add `README.md` (what the repo is — generic app-agnostic skills; the import contract: pinned-snapshot vendoring, not a live submodule), `LICENSE` (Apache-2.0 — safest superset given Anthropic's mcp-builder upstream), `CONTRIBUTING.md`, `PROVENANCE.md` (table header: skill \| upstream \| sha \| license \| derivation), `.gitignore` (exclude local env, any `mcp.json`, secrets, scratch sets, **the denylist wordlist**).
- [ ] `templates/SKILL.template.md` — the frontmatter shape in § Context plus an empty body skeleton.
- [ ] `tools/validate.py` — the dialect validator every later acceptance depends on. Checks: frontmatter standard-compliant (only `name` / `description` / `metadata` / optional `license` / `allowed-tools` at top level; bookkeeping under `metadata`), required `metadata` keys present (`owner`, `enforcement`, `derivation`, `upstream_repo`, `upstream_sha`, `license`), file in a valid dialect dir, `PROVENANCE.md` row exists.
- [ ] `.pre-commit-config.yaml` — secret scanner + a denylist scan against an employer-term wordlist. **Wordlist authored locally, NOT committed** (`.gitignore` it); config references it by path. **Wordlist must be populated before the acceptance** — empty = vacuous pass (false green).
- [ ] `.github/workflows/scan.yml` — the same two scans in CI on PR and push; fail on any hit; run against the full diff range. The wordlist reaches CI as a repository secret decoded at runtime (it is gitignored, so a path reference alone cannot work in CI), and the scan output reports file, line, and count only — never the matched term — so no internal term ever appears in a public CI log.
- [ ] **Acceptance (0A):** wordlist non-empty; a throwaway commit with a fake secret AND a term **in the wordlist** is blocked by pre-commit locally and by CI on a test branch, and the CI log does not contain the planted term itself → revert; `tools/validate.py` runs clean on `templates/SKILL.template.md`.

### 0B — The creators (hand-authored bootstrap)

Build a **shared core helper** (a module the creators import) that writes standard-compliant frontmatter, appends the `PROVENANCE.md` row, and runs `tools/validate.py`. Each creator adds only its type-specific body template. Separate entry points for discoverability; one core so de-consolidation isn't 4× duplicated logic.

- [ ] `commands/create-agent` — scaffolds an agent against the generic registry schema (identity / context / tools / evals / taxonomy / concurrency / failure / lifecycle / budget); prompts per section; emits a schema-valid stub via the shared core. `derivation: original`.
- [ ] `commands/create-skill` — scaffolds an agent-consumed work skill into `skills/` (body skeleton: purpose, trigger, steps). `derivation: original`.
- [ ] `commands/create-command` — scaffolds a directly-invocable harness op into `commands/` (body skeleton: invocation, args, behavior). `derivation: original`.
- [ ] `commands/create-tool` — scaffolds a script or MCP-server stub into `tools/` (runnable skeleton: script entrypoint or FastMCP stub). `derivation: original`.
- [ ] *(spec'd, build-gated on Step-0)* `create-hook` — the 5th creator, **not built here**: there is no hook artifact in the dialect because the Copilot surface has no hook mechanism, so building it now means generating advisory-only sections that risk being mistaken for enforcement. It activates the day the Step-0 invocation-engine decision lands, when real runner-enforced hooks exist for it to scaffold.
- [ ] **Acceptance (0B):** each of the four creators, run once, emits a stub that passes `tools/validate.py` and lands in the correct dialect dir; the creators themselves pass `tools/validate.py` and the guards; the four demonstrably share one core helper (no duplicated frontmatter / validation logic). Bootstrap proven — the rest of both plans is now "run the creator, fill the body."

---

## Phase 1 — Reviewers + generic tools

**Author each via the matching Phase 0 creator** — `create-agent` for agents, `create-tool` for tools — then fill the body with the content elements listed and add the `PROVENANCE.md` row. Don't hand-roll files the creators can scaffold. Batch in groups of 2–3, validating each batch before the next (bus-factor discipline).

- [ ] `agents/grill-me` — Socratic adversarial reviewer for plan/design review. **Must contain:** trigger (review a plan or design); the interrogation pattern (probe intent, edge cases, trade-offs, failure modes — a senior reviewer's *questions*, not a checklist); output (findings ranked by severity); the boundary that it is pre-review, not a gate (correlated-blind-spot caveat — same-model review is weak evidence). Upstream: JuliusBrussee / GetBindu socratic-reviewer.
- [ ] `agents/junior-to-senior` — adversarial plan elevation. **Must contain:** takes a plan; surfaces what a senior catches that a junior misses (hidden coupling, ops/support burden, failure modes, unstated scope); output as concrete gaps with fixes. Upstream: JuliusBrussee.
- [ ] `tools/mcp-builder` — FastMCP server scaffold. **Must contain:** generic server skeleton; conventions (env-var keys, never plaintext config; `trust_boundary` + `scopes` fields per registry schema); tool-annotation hints (readOnly / destructive / idempotent / openWorld). Upstream: Anthropic mcp-builder example.
- [ ] `tools/compress-tool-output` — compresses tool **outputs** at the MCP-proxy layer. **Must contain:** where it sits (between tool output and the model's context); what it targets (diffs, logs, search-result dumps — the uncurated payloads selective loading can't pre-trim); the generic compression approach. Upstream: RTK / compress-lib shape.
- [ ] `tools/caveman-shrink` — compresses tool **descriptions** at the MCP-proxy layer (a different bucket than `compress-tool-output`). **Must contain:** a stdio proxy that wraps an MCP server and compresses the `tools/list` / `prompts/list` / `resources/list` description fields in flight; byte-safe (code, URLs, paths, identifiers preserved exactly); the rationale (per-session input overhead from many servers' tool schemas). One MCP-proxy layer hosts three concerns — description compression (here), output compression (`compress-tool-output`), response caching (downstream). Upstream: JuliusBrussee caveman-shrink (MIT).
- [ ] `tools/secret-guard` — reusable pre-commit/CI scanner (the generic form of the Phase 0 guard). **Must contain:** secret patterns + a configurable external denylist; diff-range scanning (not just tree); fail-closed behavior. Upstream: pluginpool.
- [ ] `tools/flaky-detector` — eval-flakiness detector. **Must contain:** re-run-N; pass@k with variance bounds; flag stochastic pass/fail so a flaky eval doesn't get treated as a real regression. Upstream: pluginpool.
- [ ] `tools/changelog-forge` — semver / CHANGELOG discipline. **Must contain:** conventional-commit → changelog mapping; semver bump inference; breaking-change detection. Upstream: pluginpool.
- [ ] **Acceptance:** each file passes `tools/validate.py`; one `PROVENANCE.md` row per skill; the "Must contain" elements are present (spot-check each); scan green across the diff.

---

## Phase 2 — Remaining meta tools (via the creators)

The four creators now live in Phase 0. These two are the rest of the authoring layer — scaffold each with `create-command` / `create-tool`, then fill the body.

- [ ] `commands/eval-writer` — trace → generic `.eval.yml`. **Must contain:** takes a run trace; extracts a golden case (input / expected / scorer); emits `.eval.yml`. Generic only — no employer-specific golden-case wiring. `derivation: original`.
- [ ] `tools/knowledge-lint` — knowledge-base linter. **Must contain:** broken cross-reference detection; staleness heuristic; contradiction detection between ADRs. `derivation: original`.
- [ ] **Acceptance:** both scaffolded via a creator; both pass `tools/validate.py`; "Must contain" elements present; scan green.

---

## Phase 3 — Generic token/cost patterns (app-agnostic only)

Scaffold each with `create-skill` / `create-tool`, then fill the body.

- [ ] `skills/reasoning-budget-guidance` — per-task model-tier guidance (the reasoning-token lever that output compression does not cover). **Must contain:** task-class → effort/tier mapping; the surface caveat documented explicitly (effort-level frontmatter is a Claude Code mechanism; on the Copilot surface this is model guidance, human-selected). `derivation: original`.
- [ ] `tools/prompt-cache-inflation-check` — cache-inflation detector. **Must contain:** a defined **input contract** — a telemetry record of `{cache_read, cache_write, uncached_input, output}` token counts per call — so the tool is functional against *any* source emitting that shape (an internal runner feeds it that shape; the public tool stays generic). Compare cache-write vs cache-read vs uncached; flag the inflation anomaly (the failure mode where caching silently multiplies spend rather than cutting it). `derivation: original`.
- [ ] **Acceptance:** `reasoning-budget-guidance` documents the surface caveat; `prompt-cache-inflation-check` runs against a sample telemetry record matching its input contract and flags a planted inflation case; no employer-specific runner specifics present; scan green.

---

## OUT OF SCOPE — build internal-first, NEVER in this repo

These encode employer IP or internal structure. They are authored directly in the internal registry via `02-PLAN-skills-advanced-build.md`; do not route them through a personal account. Do not author any of the following here, even as a stub:

- ADR writer/evaluator (encodes the internal decision layer)
- Incident postmortem (encodes the internal incident layer)
- Debug procedure (encodes the internal production-debug gate)
- Cost-attribution / bucket-decomposition instrumentation (internal runner + MCP wiring)
- Burn-rate forecast (internal loop-report wiring)
- Compliance reviewer (org policy scope)
- Port automation (internal templates)

---

## HUMAN GATES (agent stops; does not auto-proceed)

The agent stages; the human performs the irreversible act.

- **Public push** — agent stages and commits locally; the human runs `git push` to the public remote *after* IP/legal sign-off. Internal recognition of the work is not the same channel as authorization to publish.
- **Company-registry import** — the human vendors a pinned, security-reviewed snapshot at a tag/SHA into the company registry; the snapshot is the release artifact produced by `01B-PLAN-skills-repo-operations.md`. Never a live submodule from a personal account into internal company infrastructure. Consumers pin to tags, never float on `main`.

---

## Definition of Done

- [ ] The four creators (`create-agent` / `create-skill` / `create-command` / `create-tool`) are hand-authored in Phase 0, share one core helper, and each emits a stub that passes `tools/validate.py`.
- [ ] Every other skill in this plan was scaffolded via a creator, not hand-rolled; `create-hook` is spec'd in the family with its build gated on the Step-0 decision (known gap, not silent).
- [ ] Structure mirrors the registry dialect; import is copy, not transform.
- [ ] Guards enforced and proven (a planted secret AND a planted internal term are blocked by pre-commit and by CI).
- [ ] Every skill: dialect-valid frontmatter + a `PROVENANCE.md` row + the "Must contain" content elements present.
- [ ] Zero employer-internal terms (scan clean across full history, not just `HEAD`).
- [ ] `README.md` documents the import contract and the boundary rule (app specifics live in app-repo `_variables.yml` overrides downstream).
- [ ] Each skill carries `owner` and `enforcement` under `metadata`.
- [ ] No public push performed; no company-registry vendoring performed — both staged for the human gates.
