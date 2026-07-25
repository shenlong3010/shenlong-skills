---
name: trace-flow
description: Follow one execution or data path across files — a request from entry point to response, a value from source to sink, an event from emit to handler — into the actual ordered chain of what calls what, so you can debug or understand behavior that no single file shows. Use whenever the question spans files along a path — "trace this request", "how does data get from X to Y", "what happens when this endpoint is hit", "follow this value through the system", "where does this event go", "what's the call chain here". Do NOT use to comprehend one unit in place (that is explain-code) or to locate a definition/callers (that is symbol-lookup).
derivation: original
flow: lookup
domain: code
---

# Trace Flow

Reconstruct one path through a system — the ordered chain of calls and transformations from a start point to an end point — so behavior that lives *between* files becomes visible.

## Scope boundary

`explain-code` comprehends one unit in place; `symbol-lookup` finds a definition or its callers. This skill is for the *path*: the chain that crosses many units and that no single file reveals — a request's journey, a value's lineage, an event's fan-out. Use it when the answer is a sequence, not a location or a single unit's contract.

## Output: the flow trace

- **Endpoints** — the start (entry point, event emit, input source) and the end (response, sink, side effect) the trace connects. State them before tracing so the path has a target.
- **The ordered chain** — each hop as `unit → unit`, with what happens at each: the transformation, the branch taken, the data passed. Numbered, so the sequence is explicit.
- **Branch points** — where the path forks (conditionals, polymorphic dispatch, middleware chains) and which branch this trace follows; name the untaken branches as "not traced here".
- **Boundary crossings** — where the flow leaves the code you can see: a network call, a queue publish, an async handoff, a DB write later read elsewhere. These are where a trace goes dark; mark them, don't fabricate the far side.
- **Data at each hop** — how the payload is shaped/validated/mutated along the way, if the task is about data lineage rather than control flow.
- **Confidence** — which hops are verified from the code and which are inferred (dynamic dispatch, DI, framework routing you couldn't fully resolve statically).

Answer the user's actual question from this trace; emit the full chain for "walk me through this flow".

## Tracing procedure

1. **Pin both ends first.** A trace with no target wanders. Identify the entry (route handler, `main`, event listener) and what "done" looks like (HTTP response, row written, message published).
2. **Walk hop by hop, resolving each call with symbol-lookup.** At each unit, find where control goes next — don't grep the whole repo, follow the actual call. `explain-code` on a hop when a unit's behavior is itself unclear.
3. **Handle dispatch honestly.** Interfaces, virtual methods, DI, and event buses break the static chain — the call target is chosen at runtime. Enumerate the candidate implementations and say which the trace assumes, or mark the hop "runtime-dispatched, N candidates".
4. **Mark boundary crossings, don't cross them blind.** When flow hits a network/queue/async edge, note it and pick up the trace on the other side as a *separate* segment if the far side is in scope — never pretend a synchronous line runs through an async boundary.
5. **Note branches without chasing all of them.** Follow the branch the task cares about; list the others as untraced. A trace that expands every fork becomes a tree nobody can read — depth on the relevant path beats breadth.

## Gotchas

- **Dynamic dispatch breaks static tracing.** `handler.process()` where `handler` is an interface — the real target is runtime-chosen. Static tracing can only enumerate candidates; claiming one specific implementation without evidence is a fabricated chain. List candidates, mark the assumption.
- **Middleware and decorators run off the visible path.** Auth checks, logging, transactions, retries wrap the handler invisibly. The literal call chain skips them; the *real* runtime flow includes them. Note the framework layer even though it's not a line in the file.
- **Async/queue handoffs are trace breaks, not trace hops.** A `publish(event)` and its consumer are two separate flows joined by infrastructure, often in different processes. Treat the boundary as an edge; trace each side independently and state the join.
- **The trace is one path, not the behavior.** Following the happy path answers "what happens when it works". Error paths, retries, and alternate branches are different flows — say which one this trace is, so it's not mistaken for the whole picture.
- **Config and feature flags reroute flow.** A branch taken depends on config the code reads at runtime; the "real" path differs per environment. Name the flag/config that steers the fork rather than asserting one fixed route.
- **Framework routing hides the first hop.** The jump from URL to handler happens in framework config/annotations, not a call you can grep. Find the route table (decorators, routes file, annotations) to anchor the entry, or the trace starts one hop too late.

## Boundaries

- Comprehending any single hop in depth is `explain-code`; resolving each next-call target is `symbol-lookup` — this skill orchestrates those along a path, it doesn't replace them.
- If the trace is being run to find *why* something breaks, the reproduce-observe-isolate discipline is `systematic-debug`; this supplies the map, that runs the investigation.
- Data lineage that ends in a query is `sql-review` territory once it reaches the SQL; trace up to the query, hand the query off.
- A trace that crosses a network call into another service, with no shared code, goes dark at the boundary — say so; cross-service tracing needs runtime telemetry, not static reading.
