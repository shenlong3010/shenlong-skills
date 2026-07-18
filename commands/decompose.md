---
name: decompose
description: Break a goal, story, or feature into verifiable task units with machine-checkable acceptance and explicit file scope. Use when planning execution — "break this down", "decompose this story", "turn this into tasks" — before any loop or session burns time on an unverifiable blob.
derivation: original
flow: plan
domain: process
---

# /decompose

## Invocation
`/decompose <goal, story text, or ticket>`

## Behavior
1. Split until every task is **one verifiable unit**: it can be checked in isolation, without executing its siblings. The split rule is absolute — if a task can't be verified alone, it isn't one task.
2. Emit each task in this schema:

```markdown
## TASK-NNN: <imperative summary>
status: pending
gate: none | human          # human = irreversible or judgment-bound
acceptance:
  - "<command that exits 0>" | "<file exists>" | "<observable check — no vibes>"
scope:
  - <the only paths this task may touch>
```

3. Classify each acceptance criterion **checkable / uncheckable**. Uncheckable ones ("feels responsive") force `gate: human` — never assume them away, never fake a proxy command that doesn't actually test the criterion.
4. Order by dependency; state the order's reason in one line. Flag any pair of tasks whose scopes overlap — overlapping scope means sequential by definition.
5. Size: a task an agent can finish in one focused session. Bigger → split; trivially small → merge into its parent.
