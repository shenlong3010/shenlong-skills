# 01B-PLAN — Skills Repo Operations (CI/CD + eval execution)

**Audience:** A Claude Code session executing this build.
**Objective:** Give the public skills repo the machinery that keeps the other two plans' acceptance criteria true over time: a tiered eval runner that executes `.eval.yml` cases, a release pipeline producing pinned consumable artifacts, a generated catalog, upstream-drift visibility, and a one-command dev loop.
**Non-goal:** Authoring skills (`01-PLAN-skill-list-build.md`); internal wiring (`02-PLAN-skills-advanced-build.md`); the Copilot invocation executor (Step-0-gated).
**Execution surface:** Same repo as `01-PLAN-skill-list-build.md`; requires its Phase 0 complete (`tools/validate.py`, the four creators, proven guards). Runs parallel to its Phases 1–3 and gates the first release. Python 3 + GitHub Actions; agent-executed evals use Claude Code headless (`claude -p`) on the personal machine — the internal Copilot executor does not exist yet (Step-0).

---

## ⚠ HARD CONSTRAINTS (read before any task)

1. **Local/CI parity.** Every CI job has a one-command local equivalent (`just <job>`). No CI-only logic; CI calls the same scripts the local commands call.
2. **Deterministic tier gates before model tier.** Tier 0 (validator, catalog drift, provenance completeness, scans) is free, deterministic, and blocking. Tier 1 (golden-case agent evals) consumes requests and runs under an explicit per-run request budget; hitting the budget halts with a partial report — never silent overspend.
3. **Stochastic ≠ failing.** Tier-1 verdicts are PASS / FAIL / FLAKY via pass@k with variance bounds (reuse `flaky-detector`). A FLAKY case never blocks a release by itself; it opens a triage item. A gate that false-blocks gets bypassed — a bypassed gate is worse than none.
4. **Executor is pluggable.** `eval_runner` core is executor-agnostic. Ships with `mock` (deterministic, free) and `claude-code` (headless). A `copilot` executor is named in the interface and Step-0-gated — do not build it here.
5. **Releases are tags + artifacts; consumers pin.** No floating `main`. The release path is blocked unless tier 0 is green and tier 1 is within thresholds. The tag/push itself is a HUMAN GATE.
6. **Public CI logs never print denylist terms.** The scan reports file/line/count only — never the matched string. The wordlist reaches CI as an Actions secret, decoded at runtime, never echoed. (Fixes the latent gap in the skills plan: the wordlist is gitignored, so a path reference alone cannot work in CI.)

---

## Context — layout added by this plan

```
justfile                      dev loop: new-skill | validate | catalog | eval | package | release-dry
tools/gen_catalog.py          frontmatter → CATALOG.md
tools/upstream_drift.py       provenance SHAs vs upstream heads → drift report
tools/eval_runner.py          tiered runner; executors: mock | claude-code
eval/config.yml               request budget, k, variance bounds, thresholds
.github/workflows/ci.yml      tier 0 on PR/push
.github/workflows/eval.yml    tier 1 on demand + pre-release
.github/workflows/release.yml tag-triggered artifact build
dist/                         packaged skill bundles (gitignored; release artifacts)
```

`.eval.yml` schema consumed (as defined by `eval-writer`):

```yaml
cases:
  - id: <case-id>
    input: <prompt or fixture path>
    expected: <artifact / assertion>
    scorer: exact | regex | file-exists | command-exit
```

---

## Phase 0 — Dev loop (justfile)

- [ ] `justfile` with recipes: `new-skill <type> <name>` (dispatches to the matching creator), `validate` (all skills through `tools/validate.py`), `catalog`, `eval [--executor mock|claude-code] [--skill <name>]`, `package <skill>`, `release-dry`.
- [ ] Each recipe calls the same script CI calls — parity by construction, not convention.
- [ ] **Acceptance:** `just validate` output is identical to the CI validator job on the same tree; `just new-skill skill demo` produces a validator-passing stub.

---

## Phase 1 — Catalog + provenance + scan hardening

- [ ] `tools/gen_catalog.py` — walks the dialect dirs, emits `CATALOG.md` from frontmatter: name | dir | one-line description | owner | enforcement | derivation | upstream. This is the discoverability surface the explicit `create-*` decision was made for.
- [ ] CI drift check: regenerate catalog, `git diff --exit-code` — drift fails tier 0.
- [ ] Provenance completeness check: every skill has a `PROVENANCE.md` row and a resolvable-format `upstream_sha` (fold into `validate.py` or standalone; either way it is tier 0).
- [ ] `tools/upstream_drift.py` — for each `upstream_repo` + `upstream_sha`, query the upstream head (GitHub API) and report commits-behind per skill. **Non-blocking**; a scheduled weekly workflow emits `drift-report.md`.
- [ ] Scan hardening per constraint 6: wordlist injected via Actions secret; matcher output redacts the term (file/line/count only).
- [ ] **Acceptance:** a planted stale `CATALOG.md` fails CI; the drift report flags a known-moved upstream; a planted denylist term on a test branch fails CI **without** the term appearing anywhere in the log.

---

## Phase 2 — Eval runner (tiered)

- [ ] `tools/eval_runner.py`: discovers `**/*.eval.yml`; executor interface `run(case) -> artifacts`; scorers: `exact`, `regex`, `file-exists`, `command-exit`. LLM-as-judge is deliberately **out** of v1 (request cost + correlated-judge failure modes).
- [ ] `mock` executor: returns fixture outputs — the free deterministic path for runner/scorer development and CI smoke tests.
- [ ] `claude-code` executor: headless invocation per case, workspace-isolated (temp dir per case), artifacts collected for scoring.
- [ ] pass@k + variance via `flaky-detector`; verdicts PASS / FAIL / FLAKY per constraint 3.
- [ ] `eval/config.yml`: per-run request budget, k, variance bounds, per-tier thresholds. Runner halts at budget with a partial `eval-report.md` (per-skill verdicts, requests used, budget remaining).
- [ ] **Acceptance:** full suite deterministically green on `mock`; a planted failing golden case → FAIL; a planted stochastic case → FLAKY (not FAIL); a budget cap of N halts at N with a partial report.

---

## Phase 3 — Release pipeline

- [ ] Release path: tier 0 green → tier 1 within thresholds → version bump → `changelog-forge` generates the CHANGELOG section → package all skills to `dist/` + repo tarball → draft release PR with artifacts attached.
- [ ] Human tags and pushes (gate below); a tag-triggered workflow attaches artifacts to the GitHub release.
- [ ] Import-contract update in `README.md`: internal vendoring consumes the **release artifact at a tag**, recording the SHA — "download and verify" replaces "clone and pin."
- [ ] **Acceptance:** `just release-dry` produces the CHANGELOG diff + `dist/` artifacts locally; a planted tier-0 failure blocks the release path; the drafted release PR contains artifacts + changelog.

---

## OUT OF SCOPE

- The `copilot` executor and any internal eval execution — Step-0-gated; the runner's executor interface is exactly where it plugs in later.
- LLM-as-judge scoring — revisit only after deterministic scorers prove insufficient.
- Usage telemetry / analytics — internal concern (03-PLAN 2.2 territory).
- Skill authoring — the other two plans.

---

## HUMAN GATES (agent stops; does not auto-proceed)

- **Tag + push of any release** — the agent drafts the release PR with artifacts; the human merges, tags, pushes (consistent with the IP/publish gate).
- **Eval threshold changes** (`eval/config.yml`: budgets, k, variance bounds, pass thresholds) — release-gating parameters are control-plane; the agent proposes a diff, the human applies.

---

## Definition of Done

- [ ] `just` covers the full dev loop; every CI job has an identical local command.
- [ ] Tier 0 (validate, catalog drift, provenance, redacted scans) blocks on every PR.
- [ ] The eval runner produces PASS / FAIL / FLAKY verdicts under an enforced request budget, on both executors, with an `eval-report.md` per run.
- [ ] One dry-run release produced end-to-end: changelog, artifacts, blocked-on-planted-failure verified.
- [ ] Upstream drift visible on a schedule, non-blocking.
- [ ] No denylist term ever appears in a public CI log (verified via the planted-term test).
