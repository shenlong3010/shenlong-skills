#!/usr/bin/env python3
"""Smoke: memoization, write-invalidation, TTL bypass, stats — against the real demo upstream."""
import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import server as S
from fastmcp import Client

async def main():
    S.DB_PATH = Path("/tmp/mcp-cache-test.db"); S.DB_PATH.unlink(missing_ok=True)
    cfg = {"mcpServers": {"demo": {"command": "python3",
           "args": [str(Path(__file__).parent / "demo_upstream.py")]}}}
    proxy = S.build(cfg, ttl_rules={"^live_": "live"})
    async with Client(proxy) as c:
        tools = [t.name for t in await c.list_tools()]
        print("tools:", tools)
        get = "get_data" if "get_data" in tools else "demo_get_data"
        wr  = "write_data" if "write_data" in tools else "demo_write_data"

        r1 = (await c.call_tool(get, {"key": "a"})).content[0].text
        r2 = (await c.call_tool(get, {"key": "a"})).content[0].text
        print("r1:", r1); print("r2:", r2)
        assert "call #1" in r1 and "call #1" in r2, "memoization failed — upstream was hit twice"

        r3 = (await c.call_tool(get, {"key": "b"})).content[0].text
        assert "call #2" in r3, "different args must miss"

        await c.call_tool(wr, {"key": "a", "value": "x"})          # flush
        r4 = (await c.call_tool(get, {"key": "a"})).content[0].text
        print("post-write:", r4)
        assert "call #3" in r4, "write did not invalidate"

        stats = (await c.call_tool("cache_stats", {})).content[0].text
        print("stats:", stats.splitlines()[0])
        assert "hits=1" in stats and "misses=3" in stats

        await c.call_tool("record_llm_usage", {"cache_read":100,"cache_write":50,"uncached_input":20,"output":40})
        for _ in range(3):
            await c.call_tool("record_llm_usage", {"cache_read":100,"cache_write":50,"uncached_input":20,"output":40})
        await c.call_tool("record_llm_usage", {"cache_read":0,"cache_write":9000,"uncached_input":600,"output":40})
        health = (await c.call_tool("prompt_cache_health", {})).content[0].text
        print("health:", health.splitlines()[0])
        assert "INFLATION FLAGS" in health
    print("SMOKE: ALL PASS")

asyncio.run(main())
