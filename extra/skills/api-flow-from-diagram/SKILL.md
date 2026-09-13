---
name: api-flow-from-diagram
description: Turn a sequence or architecture diagram into an API contract sketch — endpoints, methods, request/response shapes, and call order. Use for "turn this diagram into an API spec", "what endpoints does this flow need", "extract the API from this sequence diagram", or any pasted Mermaid/PlantUML sequence diagram or screenshot of one that needs to become a contract. Do NOT use for reading an existing spec (`read-api-spec`) or for describing what a diagram shows without producing a contract (`read-diagram`).
derivation: original
flow: lookup
domain: code
---

# API Flow From Diagram

## Purpose
Diagrams describe interactions; specs describe contracts. This skill crosses that gap — a sequence diagram becomes the endpoint list, method, path, and request/response shapes it implies, in call order, with what the diagram leaves unspecified named as such.

## Method

1. **Classify the input.** Diagram source text (Mermaid `sequenceDiagram`, PlantUML `@startuml`) → parse it directly per `read-diagram`. Raster image (screenshot, photo, whiteboard) → extract via `read-image` first, then continue here. Both routes converge on the same extraction below.

2. **Extract participants and arrows.** Each participant is a service or actor. Each arrow is one call: source, target, label. Preserve order — the diagram's vertical axis is the call sequence.

3. **Map each arrow to an endpoint.** From the arrow label infer method and path. `GET /orders/{id}` style. Note the request body if the label implies one, and the response if a return arrow exists.

4. **Emit the contract sketch**, one block per endpoint, in call order:
   - method + path
   - caller → callee
   - request fields
   - response fields
   - what triggers it (the preceding step)

5. **List what the diagram does not say.** Auth, status codes, error responses, idempotency, pagination, content types, versioning — diagrams almost never carry these. Name each as a gap rather than inventing a plausible value. A gap list is this skill's deliverable; filling the gaps is not (see Boundaries).

## Gotchas
- **A diagram arrow is not always an HTTP call.** Message queues, database reads, and internal function calls all draw the same arrow. Check the label and participant type before assigning a method and path. Mermaid encodes participant type in the node shape: `[(...)]` is a datastore (database, cache), `{{...}}` a hexagon often used for brokers, `[...]` a plain service or process. A self-arrow (`N->>N`) is an internal call, never an endpoint.
- **A topology diagram has no call order.** `graph`/`flowchart` (`graph TD`, `graph LR`) draws which components talk, not when — edge order is declaration order. Only `sequenceDiagram` carries time on its vertical axis. Asked to extract an API from a topology, report the interfaces and their direction, say the ordering is undetermined, and do not narrate a request flow. Unlabeled edges yield no method or path at all; say so rather than inferring operations from service names.
- **Return arrows are responses, not new endpoints.** A dashed arrow back is the response to the call above it.
- **A plausible field and a drawn field look identical once written down.** The failure is silent and one-directional: a reader cannot tell that `created_at` was never in the diagram, so they build it as specified and never learn otherwise. Every field in an endpoint block must trace to an arrow label. Fields the API obviously *needs* but the diagram omits belong in the gap list, never in the contract.
- **The diagram is the only authority here, including where it is wrong.** A flow missing auth on an internal hop, or a money-moving call with no idempotency key, gets that recorded as a gap — not corrected in place. Fixing the design is a separate pass over the extracted spec; keeping it out is what makes this output trustworthy as a transcription.

## Boundaries
Reading an existing API contract → `read-api-spec`. Describing a diagram's content without producing a contract → `read-diagram`. Extracting text or structure from a raster image → `read-image` (this skill calls it, then continues).

**Extraction only — never design review.** This skill reports what the diagram specifies and what it omits. Judging whether the resulting API is *good* — idempotency on money-moving calls, auth on internal hops, versioning, rate limits, error contracts — is a separate pass over the extracted spec, and applies equally to specs that never came from a diagram. Recommending a fix inside the contract sketch destroys the property that makes this output usable: that every line in it was actually drawn.
