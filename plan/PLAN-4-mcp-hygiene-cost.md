# PLAN-4 — MCP Tooling + Hygiene + Cost

**Prerequisite:** PLAN-1 complete. Constraints from PLAN-1 apply unchanged.
**Objective:** The infrastructure-flavored utilities: MCP building and compression, repo hygiene scanners, token/cost levers.

---

## Phase A — MCP tooling

- [ ] `tools/mcp-builder` — FastMCP scaffold; env-var keys never plaintext config; trust-boundary + scope fields; tool-annotation hints (source: anthropics).
- [ ] `tools/caveman-shrink` — stdio proxy compressing MCP tool/prompt/resource *descriptions* in flight; byte-safe (source: JuliusBrussee, MIT).
- [ ] `tools/compress-tool-output` — compresses tool *outputs* (diffs, logs, search dumps) at the same proxy layer.

## Phase B — Repo hygiene

- [ ] `tools/secret-guard` — secret patterns + configurable denylist; diff-range scanning; fail-closed (source: pluginpool).
- [ ] `tools/flaky-detector` — re-run-N, pass@k with variance bounds; flags stochastic pass/fail (source: pluginpool).
- [ ] `tools/changelog-forge` — conventional commits → changelog; semver bump inference (source: pluginpool).
- [ ] `tools/knowledge-lint` — broken cross-references, staleness, ADR contradictions.

## Phase C — Cost

- [ ] `skills/reasoning-budget-guidance` — task-class → model-tier/effort mapping; reasoning-token lever output compression doesn't touch.
- [ ] `tools/prompt-cache-inflation-check` — flags cache-spend anomalies; input contract: `{cache_read, cache_write, uncached_input, output}` per call.

---

## Definition of Done

- [ ] All creator-scaffolded, `validate.py`-green, scan-clean; `caveman-shrink` demonstrably shrinks a sample server's `tools/list` payload; `prompt-cache-inflation-check` flags a planted inflation record.
