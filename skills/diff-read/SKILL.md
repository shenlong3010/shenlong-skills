---
name: diff-read
description: Read large diffs token-efficiently — stat first, then targeted per-file hunks, word-diff for prose, function-context for code. Use before reviewing any branch/PR diff, when "git diff" is about to dump thousands of lines into context, or when a diff must be summarized — never page a full raw diff to understand a change.
derivation: original
flow: lookup
domain: git
---

# Diff Read

## Purpose
A raw `git diff` of a real branch is the single most common context-flooder in review work. The ladder reads the *shape* first, then drills only where shape says to — same files-first law as `code-search`, applied to diffs.

## Ladder

1. **Shape** — `git diff --stat <base>...HEAD` (three-dot: changes *since* divergence, not noise from base moving). Numstat for machine-readable: `git diff --numstat`. Decide right here which files matter; most diffs are 3 hot files + N mechanical ones.
2. **Mechanical bulk, verified cheaply** — lockfiles, generated code, renames: confirm with `--stat` counts and `git diff --find-renames --diff-filter=R --stat`; never read their hunks.
3. **Hot files, one at a time** — `git diff <base>...HEAD -- path/to/file`. Add `--function-context` (`-W`) for code: hunks expand to whole enclosing functions — the 3-line default hides what a change actually does to control flow.
4. **Prose/config** — `--word-diff` (docs, YAML): line-diff on prose marks whole paragraphs changed when one word moved.
5. **Intent check** — `git log --oneline <base>..HEAD` beside the diff: commit boundaries say what the author *thinks* the units are; a diff that ignores them misreads mixed concerns.

## Gotchas
- **Two-dot vs three-dot is the classic wrong-diff**: `main..feature` diffs *tips* (includes everything main gained since branching — someone else's merges appear as "the change"); `main...feature` diffs from the merge-base — the change the branch actually made. Review wants three-dot, nearly always.
- **`-U0` lies for review**: zero context makes hunks unplaceable and merges adjacent edits; shrink context only for machine consumption (`scan.sh`-style line mapping), never for reading.
- **Whitespace storms**: a reformat + real change in one diff → `git diff -w` first to find the real change, then confirm the reformat is *only* whitespace with the full diff's `--stat` (same counts, `-w` shows nothing = pure format).
- **Binary and minified files report as "changed" with no readable hunk** — `--stat` flags them (`Bin`, one giant line); do not open, name them in the summary instead.
- **`--color-moved=dimmed-zebra`** separates moved code from new code — a 200-line "addition" that's a relocation reviews in seconds instead of line-by-line.

## Boundaries
Judging the diff (bugs, quality) → `code-review` agent / `sql-review`; this skill only gets it into context affordably. History archaeology (who/when/why) → `git-search`. Staged-diff → commit message is `commit-writer`; branch-diff → PR body is `pr-writer`.
