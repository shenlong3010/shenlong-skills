---
name: tdd-loop
description: Enforce RED-GREEN-REFACTOR test-driven development — failing test first, minimal code to pass, refactor on green. Use whenever implementing features or fixes where correctness matters — "TDD this", "test-first", or any task where tests were requested. The discipline: no production code before a failing test exists.
derivation: adapted
source: https://github.com/obra/superpowers
---

# TDD Loop

## The cycle — one behavior at a time

**RED** — write one test for the next behavior. Run it. **Watch it fail, and read the failure**: it must fail for the intended reason (assertion), not a typo (import error). A test that passes immediately is testing nothing — investigate before proceeding.

**GREEN** — write the *minimum* production code that passes. Resist implementing the next three behaviors "while you're there"; they don't have tests yet, so they don't exist yet.

**REFACTOR** — with the suite green, clean up: names, duplication, structure. Run the suite after every refactor step. Red during refactor → undo the step, don't debug forward.

Commit on green, per cycle. Small commits = cheap bisects later.

## The hard rule

**Production code written before its failing test gets deleted, not retrofitted.** Writing the test after the code inverts the point — the test then documents whatever the code happens to do, including its bugs. If code slipped ahead: delete it, write the test, watch it fail, rewrite. (It rewrites faster the second time; that's not waste, that's the design clarifying.)

## Boundaries
- Spikes/throwaway exploration are exempt — but label the code `# SPIKE` and delete it before real implementation starts; spike code that survives becomes untested production code.
- Behavior at external boundaries (HTTP, DB) → test through the repo's existing fake/mock idiom (see test-scaffold); don't invent a new mocking style mid-TDD.
- One assertion-concept per test; a test that checks five behaviors fails uninformatively.
