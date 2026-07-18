---
name: regex-forge
description: Convert a natural-language matching requirement into a regex with test cases, or explain an existing regex piece by piece. Use for "regex for X", "what does this regex do", or any pattern-matching request.
derivation: original
flow: util
---

# /regex-forge

## Invocation
`/regex-forge <requirement or pattern>`

## Behavior
1. Building: state the target flavor first (PCRE, Java, Python, JS — they differ on lookbehind, named groups, escaping). Emit the pattern, then a table of at least 3 should-match and 3 should-not-match cases, then a one-line-per-token breakdown.
2. Explaining: decompose token by token; flag catastrophic-backtracking risk (nested quantifiers over overlapping classes) and anchoring gaps.
3. If the requirement is really parsing (nested structures, quotes with escapes), say regex is the wrong tool and name the right one.
