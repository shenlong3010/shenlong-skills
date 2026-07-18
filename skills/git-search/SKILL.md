---
name: git-search
description: Search git history efficiently — pickaxe, regex diffs, line-range history, rename-following, true-origin blame. Use for "when did this change", "who wrote/removed this", "where did this function come from", "find the commit that introduced X", or any history/blame archaeology — use INSTEAD of paging `git log -p` or raw `git blame`. Bisect itself lives in systematic-debug; this skill finds the needle without stepping.
derivation: original
flow: lookup
---

# Git Search

History is a corpus; grep it with the purpose-built flags instead of paging `git log -p`.

## The core four

```bash
git log -S'connectionPool' --oneline          # pickaxe: commits where the STRING's occurrence count changed
git log -G'retry\s*\(' --oneline              # regex against diff lines (catches moves -S misses)
git log -L :publish:src/SnsPublisher.java     # full history of ONE function
git log -L 40,60:config/pool.yml              # history of a line range
```

- **-S vs -G matters:** `-S` fires only when the total occurrence count changes — code *moved within a file* is invisible to it. Suspect a move → `-G`. `-S` takes `--pickaxe-regex` if the needle itself is a pattern.
- `--follow` for a single file's history across renames; `--all --source` to search every branch and see which one hit.

## Blame that finds the true origin

```bash
git blame -w -C -C -C src/Handler.java        # -w ignore whitespace; -C^3 track code copied across files
```

Default blame convicts the last reformatter, not the author. `-w` skips whitespace commits; stacking `-C` traces lines to the file they were copied from. Repos with a `.git-blame-ignore-revs` file: `--ignore-revs-file` skips known bulk-format commits.

## Metadata lanes

```bash
git log --grep='NTWG-1234' --oneline          # message search (ticket archaeology)
git log --author=name --since='3 months ago' --oneline -- src/payments/
git log --oneline -- path/                    # everything that touched a path
```

## Token discipline

`--oneline` first, always; cap with `-n 20`; `--stat` before `-p`; full patches only for the one commit that matters (`git show <sha> -- path`). A raw `log -p` on an active repo is a context bomb.

## Boundaries

- Finding the *breaking* commit by stepping → `git bisect`, run under `systematic-debug`.
- Searching working-tree content → `code-search`; tracked-content-only text search: `git grep --cached`.
