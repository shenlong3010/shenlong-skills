---
name: eval-writer
description: Extract a golden eval case from a run trace or a completed task and emit it under evals/ in the native `claude plugin eval` layout (prompt.md + graders/). Use after a skill run worked (or failed instructively) — "capture this as an eval", "make a golden case", "add a regression case" — and for routing checks ("did the right skill fire").
derivation: original
flow: meta
domain: agent
---

# /eval-writer

## Invocation
`/eval-writer <skill-or-command-name> [trace or "this session"]`

## Behavior
1. Identify from the trace: the input that triggered the behavior, and the output property that made the run a success (or the failure worth pinning).
2. Reduce the input to the minimal reproduction — strip session-specific noise while keeping what actually exercised the behavior. Fixtures stay tiny and live beside the case.
3. Emit the native `claude plugin eval` layout (the shape `claude plugin eval init --bare` generates):

```
evals/<case-id>/
  prompt.md            # the minimal input, verbatim — what the agent is given
  graders/criteria.md  # what a passing run must show, as checkable criteria
  fixtures/…           # optional tiny files the prompt references
```

4. `case-id` = `<target-name>-<short-slug>` (e.g. `symbol-lookup-find-def`). Routing cases get the `routing-` prefix and test that the *right skill lane fired*, not just that the answer was correct.
5. Grader criteria law unchanged: **pick the weakest check that still catches the regression.** Prefer objectively checkable criteria (a command was used, a file exists, output contains a literal marker like `VERDICT:`) over prose-quality judgments — the LLM judge grades against criteria.md, and vague criteria make flaky evals.

## Running

```bash
claude plugin eval shenlong-skills --tag routing --runs 1 --max-cost-usd 2
```

- Runs cost API spend (agent runs + judge) — smoke with `--runs 1` and a `--max-cost-usd` cap before any full pass; default is 3 runs/case.
- `--ablation with-without` adds a no-plugin baseline arm — the score *delta* is the toolbox's measured value.
- **Status note:** `claude plugin eval` is early-access as of 2026-07 (`claude` 2.1.215 reports "currently in early access" on run). Cases authored in this layout are inert until the gate opens — author them anyway; they are the regression backlog.

## Boundaries
Authoring cases only. Deciding *what* deserves an eval: any instructive failure, any routing miss (naive tool used where a skill should have fired), any gotcha proven in a session. Skill content fixes belong in the skill; an eval pins the fix.
