---
name: pr-writer
description: Generate a PR title and body from the branch diff against the base branch. Use when opening a pull request, or when asked to "write the PR", "PR description", or "describe this branch".
derivation: original
---

# /pr-writer

## Invocation
`/pr-writer [base-branch]` (default base: main)

## Behavior
1. `git log base..HEAD --oneline` and `git diff base...HEAD --stat` for the real change set.
2. Title: conventional-commit style, ≤ 72 chars.
3. Body sections: **What** (2–4 sentences), **Why** (the problem or ticket), **How verified** (tests run, manual checks — actual commands, not "tested locally"), **Risk / rollback** (one line each). Omit a section rather than pad it.
4. Call out anything a reviewer would want flagged: schema changes, config touches, dependency bumps, behavior changes not covered by tests.
