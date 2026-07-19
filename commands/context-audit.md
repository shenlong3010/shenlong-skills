---
name: context-audit
description: Report what is currently occupying context — files, tool outputs, conversation — with rough token weight and trim suggestions. Use when the session feels heavy, before adding large files, or when asked "what's in context", "context usage", "why is this slow".
derivation: original
flow: session
domain: agent
---

# /context-audit

## Invocation
`/context-audit`

## Behavior
1. Inventory the major context occupants from this session: loaded files (path + approx size), large tool outputs (which tool, roughly how big), long conversation stretches.
2. Estimate weight per item in rough tokens (chars/4 is fine — precision is not the point, ranking is).
3. Rank by cost and flag: items no longer needed for the current goal, duplicated reads of the same file, verbose outputs that a summary already covers.
4. Recommend: what to drop, what to re-read fresh after a /clear, whether a HANDOFF.md (via /handoff-writer) plus restart beats continuing.
