---
name: gen-diagram
description: Generate a Mermaid diagram (sequence, flowchart, ERD, state, class) from code, a description, or a conversation. Round-trip partner of the read-diagram skill. Use for "diagram this", "draw the flow", "sequence diagram for X", "ERD for these tables".
derivation: original
---

# /gen-diagram

## Invocation
`/gen-diagram <type?> <source: files, description, or "this">`

## Behavior
1. Pick the type from the question if not given: interactions over time → sequence; branching logic → flowchart; data model → erDiagram; lifecycle → stateDiagram.
2. From code: diagram what the code does, not what comments claim. Name participants after real classes/services/tables.
3. Keep it readable: ≤ ~15 nodes per diagram; beyond that, split into an overview plus detail diagrams rather than one hairball.
4. Emit a complete fenced ```mermaid block that renders as-is — validate by re-parsing it mentally against Mermaid syntax (direction header, matched subgraph/end, legal arrows for the type).
5. State one line of what was deliberately omitted, so the reader knows the abstraction level.
