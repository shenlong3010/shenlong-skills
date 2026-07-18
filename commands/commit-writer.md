---
name: commit-writer
description: Turn the currently staged diff into a conventional-commit message. Use whenever committing — after staging changes, before git commit, or when asked to "write the commit", "commit this", or "commit message".
derivation: original
flow: deliver
domain: git
---

# /commit-writer

## Invocation
`/commit-writer` (reads staged changes itself)

## Behavior
1. Run `git diff --cached --stat` and `git diff --cached` to see what is actually staged. Never write a message from memory of the session — the diff is the source of truth.
2. Classify: feat / fix / refactor / docs / test / chore / perf / build. Scope = the dominant module or path segment.
3. Emit `type(scope): imperative summary ≤ 72 chars`, blank line, then a body only when the diff needs explanation (why, not what). Breaking change → `!` after type and a `BREAKING CHANGE:` footer.
4. Multiple unrelated concerns staged → say so and propose a split instead of writing one blended message.
