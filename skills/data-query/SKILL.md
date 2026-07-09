---
name: data-query
description: Query JSON/YAML/structured data precisely with jq, gron, and yq instead of grepping it. Use for "find the key/value in this JSON", "extract field X", "search this config/API response", or any moment grep is about to be aimed at structured data — grep on JSON is a false-positive machine (keys vs values, escaping, minified single lines).
derivation: original
---

# Data Query

Structured data has paths, not lines. Query the structure.

## jq — the default

```bash
jq '.items[].name' resp.json                  # extract
jq '.items[] | select(.status=="failed")'     # filter
jq -r '.token'                                # -r: raw string for shell use (no quotes)
jq 'paths | select(.[-1]=="apiKey")'          # WHERE does this key live? (path discovery)
jq '[..|.url? // empty]'                      # every url anywhere in the tree
jq 'keys' big.json                            # probe structure FIRST — cheap map before expensive query
```

- `-e` sets exit code by result — makes jq scriptable in conditionals.
- Huge files: `jq -c` per-line compact; `--stream` for files that don't fit memory.
- Precision gotcha: very large integers can be mangled (float round-trip) — ids as strings, or `tostring` early.

## gron — make JSON greppable, then ungreppable

```bash
gron resp.json | rg 'apiKey'                  # JSON → flat assignments → rg finds path AND value
gron resp.json | rg 'retries = ' | sed 's/3/5/' | gron -u   # edit via grep, back to JSON
```

The bridge tool when you don't know the structure: every leaf becomes one greppable line carrying its full path.

## yq — YAML lane

```bash
yq '.services[].image' compose.yml
yq -i '.spec.replicas = 3' deploy.yml         # in-place edit
```

**Variant trap:** two incompatible tools share the name — mikefarah's Go yq (v4 syntax, `.a.b`) vs the Python jq-wrapper yq (pipes YAML through actual jq). `yq --version` before trusting any snippet; syntax differs materially.

## Boundaries

- CSV/tabular → `data-csv` (pandas/csv discipline); SQLite as query engine for big JSON arrays: `sqlite3 :memory: 'select …'` with `-json`, or duckdb-class tools.
- Config semantics (Norway problem, safe_load) → `config`; this skill is querying, that one is parsing safely.
