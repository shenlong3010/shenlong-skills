# cache-proxy — caching MCP server

Interposes between your MCP client and upstream servers, memoizing read-tool
responses. Management plane (`cache_stats`, `cache_flush`) and prompt-cache
telemetry (`record_llm_usage`, `prompt_cache_health`) ride along.

## Wire it

1. Move your existing server entries out of the client's `.mcp.json` into
   `upstreams.json` here (same MCPConfig shape — see `upstreams.sample.json`).
2. Point the client at this proxy instead:

```json
{ "mcpServers": { "cache-proxy": {
    "command": "python3",
    "args": ["/path/to/mcp/cache-proxy/server.py"] } } }
```

Upstream tools appear under their own names; identical read calls within the
TTL are served from cache without touching the upstream.

## Behavior

- **Key:** `tool + sha256(canonical-json(args))` — arg order normalized.
- **TTL classes** by tool-name pattern (`ttl_rules`): `immutable` 24h · `slow`
  300s (default) · `live` 0 = bypass.
- **Writes** (name matches `^write|^create|^update|^delete|^set_|^post|^put`,
  configurable) pass through and **flush the whole cache** — v1 invalidation is
  deliberately coarse; correct beats clever until measurement says otherwise.
- Storage: in-memory authoritative + sqlite text mirror (`~/.cache/mcp-cache.db`)
  for stats; management tools are never cached.

## Prompt-caching honesty

An MCP server never sees the prompt and **cannot cache it**. The telemetry
tools diagnose prefix instability from token buckets you record per LLM call;
the actual fix is context ordering — `skills/caching`, layer 1.

## Limits (v1, on purpose)

Single-user; whole-cache flush on any write; no arg-level dependency tracking;
persisted entries inform stats but cold starts re-fetch. Requirements:
`fastmcp>=3` (`pip install fastmcp`). Test: `python3 test_cache.py`.
