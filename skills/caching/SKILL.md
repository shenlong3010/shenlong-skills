---
name: caching
description: Caching strategy across the AI stack — prompt/prefix caching, MCP and tool-response caching, session file-read reuse, HTTP conditional requests. Use when reducing token spend or latency, "cache this", "why is my prompt cache missing", designing MCP servers or loops that repeat calls, or any repeated-cost complaint. Every cache decision here has a key, an invalidation rule, and a measurement.
derivation: original
flow: session
---

# Caching

One law: a cache is a bet that staleness costs less than recomputation. Every cache gets three answers — **key** (what identifies an entry), **invalidation** (what makes it wrong), **measurement** (hit rate; an unmeasured cache is superstition).

## Layer 1 — prompt/prefix caching

Prefix caches invalidate at the **first divergent token** — everything after the divergence is a miss, every call.

- Order context static → dynamic: system prompt, tool/skill definitions, stable instructions first; timestamps, per-request data, conversation tail last.
- Killers to hunt: a timestamp or UUID near the top, tool lists in nondeterministic order, "helpful" per-call preamble edits. One early volatile token invalidates the entire suffix.
- Deterministic assembly is a caching feature: sorted skill catalogs and stable file ordering exist so the prefix bytes repeat.
- Measure with `tools/cache-inflation-check.py` on per-call token telemetry: writes ≫ reads = paying to fill a cache never hit; input tokens trending up per call = prefix instability.

## Layer 2 — MCP / tool-response caching

Reference implementation: `mcp/cache-proxy/` — a FastMCP proxy applying every rule below (run its `test_cache.py` to see memoization, write-flush, and TTL bypass asserted live).

- **In-run memo first (cheapest win):** identical tool + normalized args within one run → reuse the first result; never pay twice in the same session for the same read.
- **Volatility classes set TTL:** immutable (content at a git SHA, published docs) → cache long; slow-changing (ticket fields, org config) → minutes; live (metrics, statuses, prices) → don't cache.
- **Key:** `server + tool + hash(normalized args)` — normalize arg order and defaults or identical calls miss.
- **Write-through invalidation:** any write to X busts cached reads of X in the same run; a loop that edits a file must not reuse its pre-edit read.
- **Scope:** never share user-scoped or auth-derived responses across identities; cache per-principal or not at all.

## Layer 3 — session file/read reuse

- Unchanged files are not re-read (track by path + mtime/hash); *changed* files must be — the read-before-write rule and this cache are the same mechanism with opposite triggers.
- Summarize-once: a verbose output gets one summary, then references to it — the summary is the cache entry; don't re-ingest the raw.

## Layer 4 — HTTP

Conditional requests are a free cache: capture `ETag`/`Last-Modified`, send `If-None-Match`/`If-Modified-Since`, treat 304 as a hit. Respect `Cache-Control` on GETs in any polling loop (pairs with `http-requests` sessions).

## Anti-patterns

Caching non-idempotent calls; TTL by vibes instead of volatility class; invalidation by restart; measuring nothing and calling it optimized; caching across trust boundaries.

## Boundaries

Application-tier distributed caching (Redis/memcached design, cache-aside vs write-behind) is systems architecture — out of scope here beyond the same three questions applying. Search/fetch *output budgeting* → `code-search` / `web-research`.
