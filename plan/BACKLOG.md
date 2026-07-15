# Expansion Backlog

Ranked per class; [S/M] = effort. Pull items via the lifecycle chain (/brainstorm → plan-writer) — no direct-to-code for [M] items. Prune candidates beat new additions when the dead-skill detector says so.

## Top 3 by leverage
- [ ] registry-mcp — toolbox as MCP server: search_skills(query) → body on demand; retires ~4.6K standing metadata tokens [M]
- [ ] tools/eval-runner.py — execute .eval.yml golden cases → pass/fail table; closes the eval-writer loop [M]
- [ ] compress middleware in mcp/cache-proxy — port compress-tool-output/caveman-shrink as second Middleware class [S-M]

## MCP
- [ ] telemetry middleware — per-call tokens/latency into prompt_cache_health [S]
- [ ] budget middleware — per-session call ceiling + kill switch [S]
- [ ] memory-mcp — cross-session key-value notes (handoff-writer's queryable sibling) [M]
- [ ] secrets-broker — env indirection; keys never in configs [S-M]

## Hooks
- [ ] scan-on-write — PostToolUse Edit|Write runs tools/scan.sh [S]
- [ ] gen-index-on-skill-write — regen catalog on skills/** writes [tiny]
- [ ] guard-dangerous for Edit|Write — extend beyond Bash to guardrail paths [S]
- [ ] context-budget warn — cumulative tool-output counter, fires ~15% [M]
- [ ] lint-gate on Stop — three linters, notify on red [S]
- [ ] early-stop hook — halt when the stated goal is met instead of gold-plating (shape from fivetaku/fablize; original impl) [S]
- [ ] completion-gate hook — goals file checked before session close; unmet goals block "done" (fablize goals.py shape; original impl) [M]

## Tools
- [ ] dead-skill detector — usage.log × skills → never-triggered prune list [M]
- [ ] release.py — semver tag + changelog-forge + zip artifact [S-M]
- [ ] token-count.py — per-file estimates; INDEX numbers regenerate [S]

## Agents
- [ ] test-quality auditor — coverage-theater detection (assertions that can't fail) [M]
- [ ] concurrency-reviewer — races/locks/idempotency pass, Java-weighted [M]
- [ ] threat-modeler — STRIDE-lite on designs; security-review's upstream sibling [M]
- [ ] api-design-reviewer — breaking-change sniff, pagination/versioning contracts [S-M]

## Skills
- [ ] data-migration safety — expand-contract, backfill gates, dual-write windows [M]
- [ ] concurrency patterns — knowledge base behind the reviewer [M]
- [ ] container layer-cache discipline — caching skill's layer 5 [S-M]
- [ ] benchmark-methodology — warmup, variance, fair timing; pairs flaky-detector [S]
- [ ] observability-instrumentation — what to log/metric per service [M]
- [ ] prompt/description writing — feeds skill pickup rates [S]
