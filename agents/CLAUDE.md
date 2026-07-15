# agents/ — directory guide

Loaded when working in this directory; root globals apply. Agents are subagents — reviewers and critics — as flat `.md` files.

## Structure
**Role** (what this critic is for, and its paired maker where one exists — `plan-reviewer` ↔ `plan-writer`) → **Method** (passes or checklist, in execution order) → **Output** (the contract below).

## Output contract
- Findings severity-ranked (`blocker/major/minor/nit` for code, `fatal/major/minor` for plans — match the file's existing scale).
- Every finding cites the exact location (`file:line`, plan line, or section) plus the issue and a one-line concrete fix.
- End with a verdict the caller can act on, as a **literal greppable marker line**: `VERDICT: <approve|fix-majors|rewrite>` — every review in a transcript is then auditable with one `rg 'VERDICT:'`.

## Laws
- **Critics expose; they don't rewrite.** The maker fixes, the checker checks — no silent rewrites inside a review.
- **The correlated-blind-spot caveat is mandatory** in every reviewer: same-model review is pre-review, not a gate; a pass is weak evidence, a fail is strong.
- **Scope honesty:** end by naming what the pass cannot see (the `security-review` closing pattern).
- New agents via `/create-agent`.
