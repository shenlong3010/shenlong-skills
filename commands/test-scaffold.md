---
name: test-scaffold
description: Generate a unit-test skeleton for a target file or function, matching the repo's existing test framework and conventions. Use when asked to "add tests", "write a test for X", or "scaffold tests".
derivation: original
flow: execute
domain: code
---

# /test-scaffold

## Invocation
`/test-scaffold <path-or-symbol>`

## Behavior
1. Detect the framework from the repo itself (existing test dir, build file, imports) — never assume one.
2. Mirror existing conventions: file naming, directory layout, assertion style, fixture pattern. One existing test file is the style guide; read one before writing.
3. Emit: one happy-path case, one edge case, one failure case per public behavior — named for the behavior, not the method (`rejects_expired_token`, not `test1`).
4. Stub external dependencies the way the repo already does (mock library, fakes, test containers). Leave TODO markers only inside assertions that need domain values the code cannot infer.
