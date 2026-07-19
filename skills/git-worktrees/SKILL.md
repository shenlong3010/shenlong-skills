---
name: git-worktrees
description: Isolate each work stream in its own git worktree — parallel sessions without branch-switching stomps, clean test baseline before changes. Use when starting a feature alongside other work, running parallel agent sessions, or reviewing a branch without disturbing current state — "work on this separately", "parallel branch".
derivation: adapted
source: https://github.com/obra/superpowers
flow: execute
domain: git
---

# Git Worktrees

## Setup

```bash
git worktree add -b feature-x ../repo-feature-x     # new branch, sibling dir
cd ../repo-feature-x
<test command>                                       # BASELINE FIRST
```

**Verify a green baseline before writing anything.** A failing suite discovered mid-feature is undebuggable — is it your change or was it already broken? Baseline red → fix or flag that first; never build on unknown ground.

## Why worktrees over branch-switching
- Each worktree = its own directory + checked-out branch, same underlying repo. Two agent sessions in two worktrees can't stomp each other's working files; `git checkout` in a shared dir mid-session corrupts the other session's context.
- Review a PR branch in a second worktree while your feature stays untouched.

## Cleanup

```bash
git worktree remove ../repo-feature-x     # after merge
git worktree prune                        # stale admin entries
git branch -d feature-x
```

Leftover worktrees hold branch refs — "why won't this branch delete" is usually a forgotten worktree.

## Gotchas
- **Same branch can't be checked out in two worktrees** — git refuses; that's the stomp-protection working.
- Hooks, config, and stash are **shared** (one repo underneath) — a pre-commit hook change affects all worktrees instantly.
- Per-worktree artifacts don't follow: `node_modules`, venvs, build dirs, `.env` files — re-install/copy per worktree, and remember `.env` is gitignored so it never arrives on its own.
- Disk is the price; worktrees share the object store but not working files.
