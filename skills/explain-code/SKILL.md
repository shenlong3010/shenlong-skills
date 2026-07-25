---
name: explain-code
description: Comprehend a specific piece of code — a function, class, module, or file you're staring at — into what it does, the contract it upholds, who depends on it, and the landmines a change would hit, so you can modify it safely without reading every line. Use whenever the question is understanding, not locating — "what does this function do", "explain this module", "what's the contract here", "is it safe to change this", "why is this written this way", "walk me through this class". Do NOT use to LOCATE code or callers (that is symbol-lookup / code-search) or to follow one execution path across many files (that is trace-flow).
derivation: original
flow: lookup
domain: code
---

# Explain Code

Turn a piece of code into the understanding needed to change it safely — its job, its contract, its dependents, and its traps — without linearly reading and re-reading every line.

## Scope boundary

`symbol-lookup` and `code-search` *locate* — where is this defined, who calls it, find the text. This skill *comprehends* the code once located: what it does and what you must not break. The two chain — locate with those, understand with this. Following a single request or data path *across* files is `trace-flow`, not this (this comprehends one unit; that walks a chain). Reading a whole unfamiliar repo for orientation is `code-search`'s first-contact pass.

## Output: the code brief

- **Job** — what this unit does, in one sentence, in caller's terms (what you get, not how it's built).
- **Contract** — inputs (types, required invariants, what it assumes is already true), outputs, side effects (writes, I/O, mutation of args/globals), and error behavior (raises / returns error / swallows). The contract is what a change must preserve.
- **Dependents** — who calls this and what they rely on; the blast radius of a change. Pull this from `symbol-lookup` (call sites), don't guess.
- **Dependencies** — what it calls that matters (the external system, the shared state, the config it reads).
- **Landmines** — the non-obvious: hidden ordering requirements, a global it mutates, a lock it holds, an exception path that leaves state half-updated, a "temporary" hack a comment warns about, concurrency assumptions.
- **Why-this-shape** — if the code is weird, the likely reason (a workaround, a perf hack, a compatibility shim) — from comments, git-blame context, or honest "unclear, verify before touching".

Answer the user's actual question from this brief; emit the full brief for "explain this" / "is it safe to change".

## Reading procedure

1. **Read the signature and the contract first**, not the body. Name, params, return, docstring, type hints — the intended contract. The body either honors it or lies about it; note lies.
2. **Read the body for effects, not lines.** What does it *do to the world* — return a value, mutate an argument, write a file, call a service, throw? Effects are the contract's real shape; a function that "returns a list" but also writes to a DB has a side effect the signature hides.
3. **Establish the blast radius.** Run `symbol-lookup` for callers before claiming a change is safe. "Safe to change" is a claim about dependents, and dependents are found, not assumed.
4. **Hunt the landmines.** Shared mutable state, order-dependence, swallowed exceptions, `# HACK`/`# TODO`/`# don't touch` comments, magic numbers, concurrency. These are why "obvious" changes break things.
5. **Explain weirdness with evidence.** If code is convoluted, look for the reason (comment, blame, a bug number) before calling it bad — it may be load-bearing. If no reason surfaces, say the reason is unknown; don't invent a rationale.

## Gotchas

- **The signature can lie.** A function typed `-> User` that also emails the user and updates a cache has three effects the signature hides. Read the body for effects; never brief the contract from the declaration alone.
- **Docstrings rot.** A docstring describes the code's past. Where docstring and body disagree, the body is truth — flag the drift rather than repeating the stale doc.
- **"Safe to change" without checking callers is a guess.** Comprehension of the unit alone can't establish safety; safety is a property of the dependents. Always resolve callers (`symbol-lookup`) before asserting a change won't break anything.
- **Swallowed errors hide behavior.** A bare `except: pass` or an ignored return code means failure modes that never surface — a core part of the real contract. Call these out explicitly; they're the bugs a "simple" change reintroduces.
- **Framework magic isn't in the file.** Decorators, DI, ORM lifecycle hooks, and metaclasses run code that isn't visible in the unit. Note what the framework injects (transaction boundaries, auth checks, serialization) rather than describing only the literal lines.
- **Global/shared state is invisible until it bites.** A function reading a module global or singleton has an input the signature doesn't show. Surface it — it's why the function behaves differently in different call orders.

## Boundaries

- Locating the code, its definition, or its callers is `symbol-lookup` (symbols) / `code-search` (text) — chain those in, don't reimplement search here.
- Following one request/data path across multiple units is `trace-flow`; this skill comprehends a single unit.
- If comprehension reveals a bug, root-causing it is `systematic-debug`; if it reveals a security-relevant effect (unvalidated input, injection surface), route to `security-review`.
- "Why did this line change / who wrote it" is `git-search` (blame, pickaxe) — pull that in as evidence for why-this-shape.
