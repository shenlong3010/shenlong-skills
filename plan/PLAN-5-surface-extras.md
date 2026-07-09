# PLAN-5 — Surface Extras + Personal

**Prerequisite:** PLAN-1 complete. Constraints from PLAN-1 apply unchanged.
**Objective:** The rest of the Claude Code surface (hooks, styles, templates) plus personal skills. Last tier — nothing here blocks anything.

---

## Phase A — Hooks, styles, templates

- [ ] `hooks/` starters — templates to copy per project: Stop-hook notifier (long task done), PreToolUse dangerous-command guard (`rm -rf`, `git push --force`, `DROP TABLE`, path denylist), Stop-hook cost-logger (append session token usage to a local log), post-edit auto-format sample.
- [ ] `styles/` — one or two output styles actually used (e.g., terse-engineer).
- [ ] `templates/` — CLAUDE.md starter, AGENTS.md starter, settings.json preset, `.mcp.json` sample (env-var keyed).

## Phase B — Career + learning

- [ ] `commands/resume-impact` — bullet → XYZ metric format with a defensibility check.
- [ ] `skills/interview-drill` — system-design and behavioral drills.
- [ ] `skills/paper-notes` — paper/blog → structured summary + relevance-to-my-stack note.

---

## Boundary

- Beyond PLAN-5: author on demand via the PLAN-1 creators — the plan set stops here; the creators are the growth mechanism.
- Employer-internal skills (org ADR, postmortem, debug gate, cost instrumentation, port automation): separate internal-first track; revive when company import starts. The old `plan/PLAN-skills-advanced-build.md` in the repo covers that track — keep or archive it; it is not part of this set.

## Definition of Done

- [ ] Whatever is built passes `validate.py` + scans; a sample hook fires in a test project; templates copy in clean.
