---
name: adr-lite
description: Write a generic Nygard-format Architecture Decision Record. Use for "write an ADR", "document this decision", "should we record this choice". Generic format only — org-specific ADR pipelines live elsewhere.
derivation: original
---

# ADR Lite

## Format
```
# ADR-NNN: <decision title, stated as the decision>
Date: YYYY-MM-DD    Status: Proposed | Accepted | Superseded by ADR-MMM

## Context
The forces at play: the problem, constraints (technical, org, cost), and why now. Facts, not advocacy.

## Decision
"We will …" — one paragraph, active voice, the chosen option only.

## Alternatives considered
Each rejected option with the one-line reason it lost. An ADR without real alternatives is a memo.

## Consequences
What becomes easier, what becomes harder, what debt or follow-up this creates — including the negative ones; consequences sections with only upsides are advertising.
```

## Rules
One decision per ADR. Write it when the decision is made, not retrofitted months later (say so if retrofitting). Number sequentially; never delete a superseded ADR — mark it and link forward.
