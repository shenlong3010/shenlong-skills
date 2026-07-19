---
name: terse-rewrite
description: Rewrite a draft into terse, technically dense engineering prose — no filler, no hedging, no throat-clearing. Use for "make this terse", "tighten this", "rewrite for engineers", or any draft that needs compression without losing content.
derivation: original
flow: deliver
domain: docs
---

# /terse-rewrite

## Invocation
`/terse-rewrite <text or file>`

## Behavior
1. Delete: pleasantries, meta-commentary ("it's worth noting"), hedges that carry no probability information, restatements, adjectives that don't discriminate.
2. Keep exact: numbers, identifiers, commands, error strings, causal claims, caveats that change decisions.
3. Prefer: active voice, front-loaded conclusions, one idea per sentence, concrete nouns over category words.
4. Target 40–60% of original length. If cutting further would drop a decision-relevant fact, stop and say which fact bounded the compression.
