# cache-proxy — caching MCP server

Interposes between your MCP client and upstream servers, memoizing read-tool
responses. Management plane (`cache_stats`, `cache_flush`) and prompt-cache
telemetry (`record_llm_usage`, `prompt_cache_health`) ride along.

## Wire it

1. Copy `upstreams.sample.json` to `upstreams.json` (gitignored) and list only
   the servers safe to cache — idempotent, write-free, no live state. Move those
   entries **out** of your client config so they aren't also loaded directly.
2. Point the client at this proxy instead. To activate from **any** project
   (global user scope), reference this file by absolute path in `~/.claude.json`
   and provision `fastmcp` in an isolated env via `uvx` — no global install:

```json
{ "mcpServers": { "cache-proxy": {
    "type": "stdio",
    "command": "uvx",
    "args": ["--with", "fastmcp==3.4.4", "python",
             "C:/Users/you/path/to/mcp/cache-proxy/server.py"] } } }
```

`server.py` reads `upstreams.json` from beside itself, so the absolute path makes
it work regardless of your current directory. Upstream tools appear under their
own names; identical read calls within the TTL are served from cache without
touching the upstream.

**Route only safe servers.** Coarse invalidation flushes the *whole* cache on any
write-classified tool, so a server that writes often (memory, semantic-edit)
nulls its own hit rate — and a live-state server (browser automation) would
return stale snapshots. Keep those **direct** in your client config; route only
idempotent reads (hosted-doc lookups, transcript fetches, code search) here.

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
