---
name: handoff-writer
description: Capture the current session's state into a HANDOFF.md that a fresh session can act on without the transcript. Use before ending a long session, before /compact or /clear, when switching machines, or when asked to "write a handoff", "save state", "brief the next session".
derivation: original
flow: session
domain: agent
---

# /handoff-writer

## Invocation
`/handoff-writer [path]` (default: ./HANDOFF.md)

## Behavior
Write HANDOFF.md with exactly these sections, in this order:
1. **Goal** — the task in one sentence, as currently understood (including corrections made mid-session).
2. **State** — what is DONE (with file paths), what is IN PROGRESS (and exactly where it stopped), what is NOT STARTED.
3. **Decisions** — choices made and the one-line reason for each; a fresh session must not relitigate them.
4. **Gotchas** — anything discovered the hard way: failing commands, environment quirks, wrong assumptions already eliminated.
5. **Next step** — the single first action for the next session, concrete enough to execute without thinking.

Rules: only facts verifiable from the workspace or stated by the user — no optimistic summaries; a wrong handoff is worse than none. Overwrite any prior HANDOFF.md; stale handoffs poison fresh contexts.
