---
name: read-diagram
description: Parse text-based diagram formats — Mermaid, PlantUML, Lucidchart text/CSV exports, and SVG structure — into a structural summary of nodes, edges, labels, and hierarchy that can be reasoned over and edited, then re-emitted as valid syntax. Use whenever a diagram file or diagram source block appears in a task — reading architecture diagrams, reviewing a flowchart, extracting entities from an ERD, comparing two sequence diagrams, or editing a diagram programmatically. Trigger on file extensions .mmd, .mermaid, .puml, .plantuml, .svg, on fenced mermaid/plantuml code blocks, and on Lucidchart CSV exports. Do NOT use for raster images (PNG/JPG) — those are read natively by vision.
derivation: original
---

# Read Diagram

Turn a text-format diagram into structure you can reason over, and edit it without breaking its syntax.

## Scope boundary

Raster images (PNG, JPG, screenshots of diagrams) are read natively by vision — do not route them here. This skill covers formats where the diagram *is text*: Mermaid, PlantUML, SVG, and Lucidchart's text/CSV exports.

## Output: the structural summary

Whatever the input format, produce the same summary shape before answering questions about the diagram:

- **Type** — flowchart, sequence, ERD, class, state, or freeform (SVG).
- **Nodes** — id, label, and shape/stereotype where the format encodes one.
- **Edges** — source → target, label, and direction/arrow style.
- **Hierarchy** — subgraphs, packages, groups, or SVG `<g>` nesting.
- **Anomalies** — orphan nodes, duplicate ids, edges referencing undefined nodes.

Answer the user's actual question from this summary; include the summary itself only when they ask for the structure.

## Per-format notes

**Mermaid** — direction header (`graph TD`, `sequenceDiagram`, `erDiagram`) determines type. Node ids and labels differ: `A[Label]` declares both; later bare `A` references the id. Edge syntax varies by type (`-->`, `->>`, `||--o{`). Subgraphs open with `subgraph` and close with `end`.

**PlantUML** — wrapped in `@startuml` / `@enduml`. Participants may be declared explicitly or implicitly by first use. Skinparams and notes are presentation, not structure — record them only if the task is about styling.

**SVG** — structure lives in `<g>` nesting, `id` attributes, and `<text>` children; geometry (`x`, `y`, `d`) is layout, not meaning. Infer edges from `<line>`/`<path>` elements whose endpoints coincide with shape boundaries; flag inferred edges as inferred.

**Lucidchart text/CSV export** — rows carry Id, Name, Shape Library, and connector rows reference Source/Destination ids. Treat connector rows as edges, everything else as nodes; page grouping is hierarchy.

## Round-trip editing rule

When asked to modify a diagram: parse → apply the change to the structural summary → re-emit the **complete** file in the original format, preserving untouched declarations byte-for-byte where possible (ordering, comments, styling directives). Never emit a fragment; a partial Mermaid block that fails to render costs more than it saves. After emitting, re-parse your own output — if it does not produce a structural summary consistent with the intended change, fix before presenting.

## Failure honesty

If a format variant does not parse cleanly (nonstandard Lucid export, hand-mangled SVG), say which lines failed and answer from the parts that did parse — do not guess structure from unparsed text.
