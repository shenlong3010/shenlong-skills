---
name: symbol-lookup
description: Find symbol definitions, references, and approximate call hierarchies — the ctags/ast-grep lane between grep and a full LSP. Use for "go to definition", "who calls this function", "where is this class defined", "call hierarchy of X", or whenever code-search finds text but the question is about the SYMBOL. Use INSTEAD of grepping a common name and drowning in false positives.
derivation: original
flow: lookup
---

# Symbol Lookup

Grep finds text; symbols have scope. Three rungs, cheapest first — and an honest ceiling: only a real LSP resolves types and cross-file semantics; everything below approximates.

## Rung 1 — ctags index (definitions)

```bash
ctags -R --fields=+n -f .tags .          # universal-ctags; ~seconds, rerun after big pulls
readtags -t .tags PaymentRouter          # definition site(s), with line numbers
readtags -t .tags -p Pay                 # prefix match when the exact name is fuzzy
```

Instant definition lookup across the repo, no server. Staleness rule as plocate: a miss means "index is old", regenerate before concluding absence.

## Rung 2 — ast-grep (references and call sites, structurally)

```bash
sg run -p 'processRefund($$$)' -l java        # call sites — not comments, not strings
sg run -p 'class $C extends PaymentRouter' -l java   # subclass references
sg run -p 'new PaymentRouter($$$)' -l java    # instantiations only
```

Structural match kills the false positives that make grepping `id` or `get` useless.

## Approximate call hierarchy (no LSP)

- **Callers of f:** `sg run -p 'f($$$)'` → for each hit file, `readtags`/ctags the enclosing function (or `git grep -W 'f('` to print the enclosing block). One level up per pass; recurse manually and cheaply.
- **Callees of f:** read f's body (rung 1 gives the location), then `sg` each invoked name once for definitions.
- Two levels is usually enough to answer "what breaks if I change this"; beyond that you're re-deriving what an LSP gives free — escalate.

## Rung 3 — real LSP (types, rename-safety, true hierarchy)

Type errors, cross-module inference, and guaranteed-complete hierarchies need a language server: IDE surface, or an LSP-bridge MCP server (mcp-language-server class) when the agent must have it. Overloads/dynamic dispatch make text-level caller lists over-approximate — say so in findings instead of presenting them as exact.

## Boundaries

- Free-text/content search → `code-search`; which artifact *provides* a symbol → `dependency-lookup`; history of a symbol → `git-search -L`.
- Dynamic languages' runtime dispatch (Python duck typing, JS) caps static confidence — mark caller lists "static approximation" in any report.
