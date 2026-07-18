---
name: repo-orient
description: Orient in an unfamiliar codebase fast — entry points, build/run/test commands, layout, hot paths. Use on first contact with a repo, or when asked "how does this codebase work", "where do I start", "map this repo".
derivation: original
flow: lookup
domain: code
---

# Repo Orient

## Method
1. **Identity:** README first 50 lines, manifest (pom/build.gradle/package.json/pyproject/go.mod) → language, framework, dependencies that define the architecture (web framework, queue client, ORM).
2. **Commands:** extract real build/run/test invocations from the manifest scripts, Makefile/justfile, or CI config — CI is the ground truth for "how it actually builds".
3. **Layout:** top 2 directory levels; name the role of each top dir in ≤ 6 words; flag generated/vendored dirs to ignore.
4. **Entry points:** main()/handler/index/server bootstrap; route or handler registration; scheduled jobs and consumers.
5. **Hot paths:** the 3–5 files most central to change — largest churn (git log --stat heuristics), most-imported modules, the core domain types.
6. Output a one-screen map: identity line, commands block, annotated tree, entry points, hot-path list with one-line reasons.

## Rules
Read files, don't guess from names — a `utils/` dir can hide the core. Time-box: this is orientation, not an audit; depth on demand afterwards.
