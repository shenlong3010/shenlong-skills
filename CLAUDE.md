# CLAUDE.md — global

Applies to the entire repository. Directory-specific conventions live in per-directory guides (below), auto-loaded when working in each directory. Behavioral master with full rule text: `archive/CLAUDE-v2-full.md` (v1 original preserved beside it). Precedence: master wins on behavior; this file and the directory guides win on repo mechanics.

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

`AGENTS.md` (other agents) and `.github/copilot-instructions.md` (Copilot) are global-only distillations — those surfaces don't load directory files, so their authoring notes stay inline there.

## Commands

```bash
python3 tools/validate.py        # frontmatter + placement, whole repo
python3 tools/skill-lint.py      # description trigger-quality
python3 tools/knowledge-lint.py  # broken links, staleness
bash tools/scan.sh               # secret + wordlist scan of STAGED changes
python3 tools/scaffold.py <skill|command|agent|tool|hook> <name>
```

All three linters green before any commit.

## Authoring (global law)

Everything except the five bootstrap creators is scaffolded via `create-skill` · `create-command` · `create-agent` · `create-tool` · `create-hook` — never hand-rolled. Frontmatter is flat everywhere:

```yaml
name: <name>
description: <what + when to trigger>
derivation: original | adapted | copied   # if not original: source: <url> required
```

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

One law across all: search output ≤ ~15% of the context window; files-first, sections-second, full reads last.

## Coding behavior (distilled — full form in archive/CLAUDE-v2-full.md)

1. **Think before coding** — surface assumptions; multiple interpretations → present them; unclear → stop and ask.
2. **Simplicity first** — minimum code; no speculative features or abstractions; if 200 lines could be 50, rewrite.
3. **Surgical changes** — only what the request requires; match existing style; clean only the orphans your change created.
4. **Read before write** — never edit a file from memory; re-read after any external change; earlier reads are stale.
5. **Goal-driven** — machine-verifiable "done" before code; multi-step work gets a plan with a verify per step. *Deep: `decompose`.*
6. **Verification** — reproducing test → fix → test passes = fixed; run the stated check before claiming done. *Deep: `tdd-loop`.*
7. **Debugging** — read the actual error; reproduce first; one variable per experiment; record falsified hypotheses. *Deep: `systematic-debug`.*
8. **Dependencies** — stdlib first; document why + tradeoff when adding; pin versions.
9. **Environment assumptions** — probe tools and versions (`command -v`, import check); state platform assumptions aloud.
10. **Secure by default** — parameterized queries; env-var secrets only; validate at trust boundaries; never log credentials/PII.
11. **Reversibility** — classify before acting; irreversible (delete, push, publish, migrate, spend) → stop and confirm; prefer the reversible path.
12. **Idempotence** — check-before-create; every step safe to re-run and resumable.
13. **Checkpoint discipline** — commit at every green verifiable unit; small commits, real messages.
14. **Context economy** — load sections, not repos; summarize verbose output once; when history dominates, hand off and restart. *Deep: `code-search` for search-output budgets.*
15. **Honest uncertainty** — precise doubt ("unsure X supports streaming") beats confident vagueness ("should work").
16. **Evidence over claims** — report what changed, the check run, and its output; never "successfully" without the check in this session.
17. **Failure-mode self-recognition** — Kitchen Sink · Wrong Abstraction · Optimistic Path · Runaway Refactor · Groundhog Loop (identical retry, no new info) · Success Theater → stop, surface the pattern, ask.
