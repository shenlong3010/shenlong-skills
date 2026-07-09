---
name: eval-writer
description: Extract a golden eval case from a run trace or a completed task and emit a .eval.yml next to the relevant skill. Use after a skill run worked (or failed instructively) — "capture this as an eval", "make a golden case", "add a regression case".
derivation: original
---

# /eval-writer

## Invocation
`/eval-writer <skill-name> [trace or "this session"]`

## Behavior
1. Identify from the trace: the input that triggered the skill, the output that made the run a success (or the failure worth pinning).
2. Reduce the input to the minimal reproduction — strip session-specific noise while keeping what actually exercised the behavior.
3. Emit `skills/<skill-name>/<case-id>.eval.yml`:

```yaml
cases:
  - id: <short-slug>
    input: <the minimal prompt or fixture path>
    expected: <artifact property or assertion>
    scorer: exact | regex | file-exists | command-exit
```

4. Pick the weakest scorer that still catches the regression — exact match on volatile prose creates flaky evals; prefer file-exists / command-exit / targeted regex.
