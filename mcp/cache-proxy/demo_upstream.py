#!/usr/bin/env python3
"""Demo upstream for cache-proxy smoke tests. get_data increments a call counter
(memoization proof = counter NOT advancing); write_data triggers invalidation."""
from fastmcp import FastMCP

mcp = FastMCP("demo-upstream")
CALLS = {"n": 0}

@mcp.tool()
def get_data(key: str) -> str:
    """Read a value; upstream call counter embedded in the response (test probe)."""
    CALLS["n"] += 1
    return f"value-for-{key} (upstream call #{CALLS['n']})"

@mcp.tool()
def write_data(key: str, value: str) -> str:
    """Write a value; the proxy classifies this as a write and flushes its cache."""
    return f"wrote {key}={value}"

if __name__ == "__main__":
    mcp.run()
