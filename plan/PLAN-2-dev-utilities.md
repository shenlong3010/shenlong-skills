# PLAN-2 — Daily Dev Utilities

**Prerequisite:** PLAN-1 complete (creators, guard, validator, packaging proven). Constraints from PLAN-1 apply unchanged.
**Objective:** The utilities used most days. Scaffold everything via the PLAN-1 creators; one line of intent each.

---

## Phase A — Document creation

- [ ] Vendor from `anthropics/skills` (with `source:` lines): `docx`, `pptx`, `xlsx`, `pdf`.

## Phase B — Dev workflow

- [ ] `commands/commit-writer` — staged diff → conventional commit message.
- [ ] `commands/pr-writer` — branch diff → PR title/body + test notes.
- [ ] `skills/stacktrace-analyzer` — trace → root-cause hypotheses + next checks.
- [ ] `skills/repo-orient` — new codebase → entry points, build, hot-paths map.
- [ ] `commands/test-scaffold` — target → unit-test skeleton in the repo's framework.
- [ ] `skills/sql-review` — query → plan concerns, index suggestions.
- [ ] `commands/regex-forge` — natural language ↔ regex with test cases.
- [ ] `skills/log-triage` — log dump → clustered errors + timeline.

## Phase C — Diagrams + writing

- [ ] `commands/gen-diagram` — code or description → Mermaid (sequence / flowchart / ERD); round-trip partner of `read-diagram`.
- [ ] `commands/terse-rewrite` — draft → terse engineering prose.
- [ ] `skills/adr-lite` — generic Nygard-format ADR (org-wired ADR writer stays internal).
- [ ] `skills/runbook-writer` — procedure → runbook with verification steps.

---

## Definition of Done

- [ ] Everything creator-scaffolded, `validate.py`-green, scan-clean; vendored items carry `source:` lines and README credits.
