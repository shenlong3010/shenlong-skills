---
name: code-review
description: Two-stage code review of a diff or PR — spec compliance first, then code quality — with severity-ranked findings citing file:line. Invoke before requesting human review — "review this diff", "code review", "check this PR". Pre-review that raises quality before humans look, not a merge gate.
derivation: adapted
source: https://github.com/obra/superpowers
flow: review
domain: code
---

# Code Review (subagent)

## Stage 1 — spec compliance
Review the diff **against what was asked** (plan, ticket, task block) before judging how it's written:
- Does the change do the stated thing — all of it, and only it? Flag silent scope additions and silently dropped requirements separately; both are spec failures.
- Acceptance criteria from the task: met, and demonstrated by what evidence?
Beautiful code that solves the wrong problem fails here and stage 2 doesn't run until it's resolved.

## Stage 2 — quality
- **Correctness:** edge/null/empty inputs, off-by-one, error paths that swallow, concurrency on shared state, idempotency of writes.
- **Hidden coupling:** shared config/schema/global state connecting "independent" pieces; changes that fan out further than the diff shows; unstated dependencies the diff silently assumes exist (auth, quota, migration).
- **Security touchpoints:** anything crossing a trust boundary in this diff — inputs, queries, file paths, URLs — route deep concerns to security-review.
- **Tests:** exist, run, and would actually fail if the behavior regressed (assert outcomes, not implementation echoes). A diff with behavior change and no test change is a finding.
- **Error handling:** failures surfaced with context vs caught-and-ignored; retries bounded.
- **Performance:** only where the diff touches a hot path — N+1 queries, per-row I/O in loops, unbounded collections.
- **Readability/maintenance:** naming that lies, dead code, comments that restate instead of explain-why.

## Output
Findings ranked **blocker / major / minor / nit**, each with `file:line`, the issue, and the concrete fix. Separate "must fix" from "author's preference call" honestly. Final line, literal: `VERDICT: approve | fix-blockers | needs-rework`. Caveat stated up front: same-model review has correlated blind spots — this raises PR quality before human review; it never replaces it.

## Boundaries
- This subagent is the two-stage, full-diff review; the built-in `/code-review` command is the quick interactive pass for what's staged right now — reach for it for a fast look, this agent for the ranked-findings contract before human review.
- Deep security concerns (injection, authz, secrets, SSRF) belong to `security-review`; flag them here and route, don't do the full pass inline.
