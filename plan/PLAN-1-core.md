# PLAN-1 — Core Toolbox (must-have)

**Audience:** A Claude Code session executing this build.
**Objective:** The minimum viable personal toolbox: guard, validator, the five creators, the core skills used daily, and packaging so one install makes it available in any project. Everything in PLAN-2 and PLAN-3 builds on this.
**Non-goal:** Employer-derived skills (internal-first, separate track); pushing to a remote (owner's call, after the scan proves itself).
**Execution surface:** Claude Code on the local repo. Company import later takes only what the Copilot surface can consume (SKILL.md text; no hooks, no plugin machinery) — filtered at import, not here.

---

## ⚠ CONSTRAINTS (apply to all three plans)

1. **Public repo → zero employer-internal content.** Pre-commit scan (secret scanner + local wordlist, gitignored) runs on everything — including migrated hand-written skills before their first commit, since they predate the guard.
2. **Attribution, minimal.** Adapted/copied items carry a `source: <upstream url>` line in frontmatter and a README credits entry. Pull shapes, write original prose.
3. **Hooks are personal-surface only.** Fully supported in Claude Code; excluded automatically at any company import.

---

## Layout (native Claude Code plugin shape)

```
.claude-plugin/plugin.json    manifest — repo installable as one plugin
skills/<name>/SKILL.md        agent-consumed skills
commands/*.md                 slash commands
agents/*.md                   subagents
hooks/hooks.json              lifecycle hooks
mcp/ + .mcp.json              MCP configs (env-var keys only) + scaffolds
styles/                       output styles
templates/                    CLAUDE.md / AGENTS.md starters, plan-template, settings presets
tools/                        scripts (validate.py, helpers)
plan/                         these plan files
install.sh                    symlink fallback for non-plugin consumption
README.md  LICENSE  .gitignore  .pre-commit-config.yaml
```

---

## Phase A — Scaffold + guard

- [ ] Layout above; README (what it is, install via plugin or `install.sh`); **LICENSE (Apache-2.0 — currently missing from the repo; required before vendoring Anthropic skills)**; `.gitignore` (env files, wordlist, scratch).
- [ ] Pre-commit: secret scanner + wordlist scan. Wordlist local, gitignored, non-empty.
- [ ] `tools/validate.py` — thin: frontmatter has `name` + `description`, file sits in the right directory, `source:` present when derivation isn't original.
- [ ] **Acceptance:** planted secret and planted wordlist term both blocked; validator runs clean on an empty skill stub.

## Phase B — Creators (hand-authored bootstrap)

Shared helper (frontmatter + validate); each creator adds its type template. Hand-authored — `create-command` cannot create itself.

- [ ] `commands/create-skill` · `create-command` · `create-agent` · `create-tool`
- [ ] `commands/create-hook` — scaffolds a `hooks.json` entry + handler script (PreToolUse / PostToolUse / Stop).
- [ ] **Acceptance:** each creator emits a stub that passes `validate.py` and lands in the right directory.

## Phase C — Core daily skills

- [ ] `commands/plan-writer` — drop in as already built (with `plan-template.md` + executability checklist).
- [ ] Migrate existing personal skills (image-content reader, diagram readers) through `create-skill`; **scan each before its first commit**.
- [ ] `skills/read-diagram` — Mermaid / PlantUML / Lucid-export / SVG → structure summary + round-trip edit; raster images are native vision, out of scope.
- [ ] Vendor from `anthropics/skills` (with `source:` lines): `file-reading`, `pdf-reading`.
- [ ] **Acceptance:** all pass `validate.py` + scans; `read-diagram` round-trips a sample Mermaid file.

## Phase D — Packaging

- [ ] `.claude-plugin/plugin.json` wiring commands / agents / skills / hooks / mcp.
- [ ] `install.sh` — symlink fallback (`~/.claude/skills`, `~/.claude/commands`, …).
- [ ] **Acceptance:** fresh project, plugin installed from local path → a skill triggers and a slash command runs; same via `install.sh` in a second fresh project.

---

## Definition of Done

- [ ] One command installs the toolbox into a fresh project; `install.sh` works as fallback.
- [ ] All five creators functional; guard proven; every artifact passes `validate.py`.
- [ ] plan-writer, the migrated readers, `read-diagram`, and the two reading skills usable day-1.
