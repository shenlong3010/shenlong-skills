---
name: repo-index
description: Pre-build local search indexes — ctags, plocate/updatedb, git commit-graph, a gron cache — so later lookups are instant instead of full scans. Use when starting a long session in a big repo, when symbol-lookup or file-find report "no index", when the same slow search runs twice, or for "make search faster here".
derivation: original
flow: lookup
domain: agent
---

# Repo Index

## Purpose
The lookup skills (`symbol-lookup`, `file-find`, `git-search`) degrade to slow full scans when no index exists. Ten seconds of index-building at session start converts every later lookup from O(repo) to O(1). This skill owns *building and refreshing* those indexes; the lookup skills own *querying* them.

## When to build
- Long session ahead in a repo > ~5k files, or any monorepo.
- The second time the same class of search runs slow — first slow search is information, second is waste.
- A lookup skill reports its backing index missing (`ctags: no tags file`, `plocate: database too old`).

## Indexes

| Index | Build | Serves | Refresh trigger |
|---|---|---|---|
| ctags | `ctags -R --fields=+n -f .tags .` (add `--exclude=node_modules --exclude=.git` always) | symbol definitions | after big pulls/refactors — mtime of `.tags` older than newest source file |
| plocate | `updatedb -l 0 -o .plocate.db -U .` (user-local db, no root) | filename lookups | daily or after mass file adds |
| commit-graph | `git commit-graph write --reachable --changed-paths` | `git log -- <path>`, pickaxe, blame speed | after large fetches; safe to re-run, git skips if fresh |
| gron cache | `gron big.json > big.json.gron` per large JSON | repeated `data-query` greps on the same payload | source file changed |

## Gotchas
- **Index files are scratch, never commit them.** `.tags`, `.plocate.db`, `*.gron` go into local excludes: `.git/info/exclude` — not the shared `.gitignore` (personal tooling, not project policy).
- **Stale beats missing as a failure mode**: a missing index falls back to a slow scan (correct, slow); a stale one silently returns wrong line numbers to `symbol-lookup`. Check `.tags` mtime against the newest touched source before trusting a jump; rebuild costs seconds.
- **`updatedb` without `-l 0 -U .` tries system-wide root indexing** and fails or prompts; the flags scope it to the repo, unprivileged.
- **commit-graph `--changed-paths` is the flag that matters** — it's what accelerates path-scoped history (`git log -- file`, pickaxe); a bare commit-graph only speeds walks.
- Windows: ctags = `winget install UniversalCtags.Ctags` (Exuberant ctags is dead, flags differ); plocate is unavailable — skip it, `fd` from `file-find` is the fallback there.

## Boundaries
Builds indexes only — querying belongs to `symbol-lookup` (tags), `file-find` (plocate/fd), `git-search` (history), `data-query` (gron). Environment tool probing (is ctags even installed?) is `env-probe`'s job — call it first on a new machine.
