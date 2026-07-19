# Backlog

Improvement stories for this toolbox, consumed by `/ralph plan` (local-backlog adapter: one story per `##` heading). Keep every story's AC machine-checkable.

## Story: overlap boundaries for review surfaces

Three code-review surfaces exist (agents/code-review.md, built-in /code-review, caveman-review) and two security-review surfaces (agents/security-review.md, built-in) with no routing note — ambiguity taxes every review request.

AC: `agents/code-review.md` and `agents/security-review.md` each gain a short Boundaries note naming their sibling surfaces and when to use which; `python3 tools/validate.py` and `python3 tools/skill-lint.py` and `python3 tools/knowledge-lint.py` all exit 0.

## Story: UTF-8 tool output without env var

`skill-lint.py`, `knowledge-lint.py`, and `gen-index.py` crash or mis-write on Windows without `PYTHONUTF8=1` (cp1252 stdout/file default). Tools should be self-sufficient.

AC: `python tools/skill-lint.py`, `python tools/knowledge-lint.py`, and `python tools/gen-index.py` each exit 0 in plain PowerShell with no `PYTHONUTF8` set; no functional output change under UTF-8 mode.

## Story: eval expansion — log-triage and diff-read routing cases

Only three routing evals exist; the two highest-traffic remaining lanes are uncovered.

AC: `evals/routing-log-triage/` and `evals/routing-diff-read/` each contain `prompt.md` + `graders/criteria.md` (fixtures optional, tiny); criteria are behavior-specific and tool-agnostic per the pattern fixed in `evals/routing-data-query/graders/criteria.md`.

## Story: reserve — claude-code-setup recommendations

Placeholder: replaced by concrete stories after the one-shot claude-code-setup analysis runs next session. Not implementable as written.

AC: (blocked — replace before planning; ralph-plan should skip this story as not implementable and list it with reason)
