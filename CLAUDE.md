# CLAUDE.md — global

Applies to the entire repository. Directory-specific conventions live in per-directory guides (below), auto-loaded when working in each directory. This file is the behavioral master; the surface adapters (`AGENTS.md`) distill it.

## Hard constraints (read first)

1. **Zero employer-internal content.** No internal server names, app names, domain-model terms, stack idioms tied to internal systems, tokens/keys. Public repo; pipeline is one-way: public → internal, never reverse.
2. **Never commit `vendor/anthropic/`.** Proprietary Anthropic doc skills, local fetch only (`tools/fetch-doc-skills.sh`); gitignored — never force-add, mirror, or copy their text into committable skills.
3. **Guards stay proven.** `tools/scan.sh` (secrets + local `.wordlist`) must pass on staged changes; an empty wordlist makes the scan vacuous — treat its warning as a failure.
4. **No remote push.** Stage and commit locally; `git push` is a human act.
5. **Attribution.** Adapted/copied content carries `derivation:` + `source:` in frontmatter and a README credits entry. Pull shapes, write original prose.

## What this repo is

Personal Claude Code toolbox — skills, slash commands, subagents, hooks, MCP scaffolds, styles, templates — packaged as a plugin (`.claude-plugin/plugin.json`), `install.sh` as symlink fallback. Company import = downstream cherry-pick at a tag, not the purpose.

## Directory guides

- `skills/CLAUDE.md` — skill anatomy, description trigger-language law, gotcha quality bar, boundary/routing conventions
- `agents/CLAUDE.md` — reviewer structure, severity-ranked output contract, correlated-blind-spot caveat, expose-don't-rewrite
- `commands/CLAUDE.md` — invocation/behavior shape, read-real-state law, irreversible-stops rule
- `tools/CLAUDE.md` — stdlib-only, exit-code contract, scanner redaction, idempotence
- `hooks/README.md` — hook wiring and handler conventions

`AGENTS.md` (other agents) is the tool-agnostic mirror — that surface doesn't load directory files, so its authoring notes stay inline there.

## Commands

```bash
python3 tools/validate.py        # frontmatter + placement, whole repo
python3 tools/skill-lint.py      # description trigger-quality
python3 tools/knowledge-lint.py  # broken links, staleness
python3 tools/eval-lint.py       # evals/ case structure + fixture references
bash tools/scan.sh               # secret + wordlist scan of STAGED changes
python3 tools/scaffold.py <skill|command|agent|tool|hook> <name>
claude plugin eval shenlong-skills --tag routing --runs 1 --max-cost-usd 2  # scored eval suite (evals/**; early-access gated)
```

All four linters green before any commit.

## Authoring (global law)

Everything except the bootstrap creator is scaffolded via `/create <skill|command|agent|tool|hook>` — never hand-rolled. Frontmatter is flat everywhere:

```yaml
name: <name>
description: <what + when to trigger>
derivation: original | adapted | copied   # if not original: source: <url> required
flow: plan | execute | review | debug | lookup | deliver | session | util | meta | career
```

`flow:` = the workflow stage the artifact serves; validate.py enforces the vocabulary, gen-index.py groups every catalog by it.

No `metadata:` block, no PROVENANCE.md — credits live in README. Nontrivial work follows the toolbox's own chain: `/brainstorm` → `plan-writer` → `plan-reviewer` + `pre-mortem` → `/decompose` → `git-worktrees` + `tdd-loop` → `code-review` / `security-review` → `systematic-debug`.

## Efficiency routing (auto-pickup)

Before reaching for the naive tool, the matching skill applies — these fire on the *action*, not the topic:

- about to `grep`/search code → `code-search` (rg ladder, `-l` first, head-cap)
- about to grep/cat JSON or YAML → `data-query` (jq paths, gron bridge)
- hunting a *filename* → `file-find` (fd/plocate) — not a content grep
- about to page `git log -p` / blame → `git-search` (pickaxe, `-L`, true-origin blame)
- about to fetch a URL / read a page → `web-research` (llms.txt probe, extract-then-rg)
- port/process/file-handle question → `system-lookup` (ss, lsof +L1, /proc)
- "which jar/package provides X" → `dependency-lookup` (runtime truth first)
- raw log dump in front of you → `log-triage` (cluster before reading)
- multi-page crawl / JS-heavy scrape / extraction pipeline → `crawl4ai` (schema-based, LLM-free)
- "who calls this / where is it defined" → `symbol-lookup` — not a bare grep of the name

One law across all: search output ≤ ~15% of the context window; files-first, sections-second, full reads last.

## Coding behavior

General coding behavior lives in `~/.claude/CLAUDE.md` (13-point list: think
before coding, simplicity, surgical changes, read-before-write, verification,
debugging, dependencies, reversibility, idempotence, comments-explain-why,
context economy, evidence over claims, failure-mode self-recognition). This
repo adds four points the general list doesn't cover:

1. **Goal-driven** — machine-verifiable "done" before code; multi-step work gets a plan with a verify per step. *Deep: `decompose`.*
2. **Environment assumptions** — probe tools and versions (`command -v`, import check); state platform assumptions aloud.
3. **Secure by default** — parameterized queries; env-var secrets only; validate at trust boundaries; never log credentials/PII.
4. **Checkpoint discipline** — commit at every green verifiable unit; small commits, real messages.

Skill cross-references from the trimmed points, kept for discoverability:
verification → `tdd-loop`; debugging → `systematic-debug`; context economy →
`code-search` for search-output budgets.
