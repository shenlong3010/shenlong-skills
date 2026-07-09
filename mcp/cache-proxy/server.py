#!/usr/bin/env python3
"""cache-proxy — caching MCP proxy (fastmcp v3 native proxy + middleware).

Client -> THIS SERVER -> upstream MCP servers (from upstreams.json MCPConfig).
CacheMiddleware memoizes read-tool responses (in-memory authoritative, sqlite
text mirror for stats/persistence); write-classified tools pass through and
flush the cache. Management plane: cache_stats / cache_flush. Prompt-cache
telemetry: record_llm_usage / prompt_cache_health.

v1 scope (deliberate): single-user, TTL volatility classes via name patterns,
coarse invalidation (any write flushes everything). NOT: cross-user sharing,
arg-level dependency graphs, distributed anything.

Prompt-caching honesty: an MCP server never sees the prompt and cannot cache
it. The telemetry tools diagnose prefix instability; the fix is context
ordering — see skills/caching layer 1.

Run:  python3 server.py          (expects upstreams.json beside this file)
Wire: point your client's .mcp.json at this command instead of the upstreams.
"""
import hashlib, json, re, sqlite3, statistics, time
from pathlib import Path
from fastmcp import FastMCP
from fastmcp.server.middleware import Middleware
try:                                    # fastmcp >=3.4 preferred API
    from fastmcp.server import create_proxy
except ImportError:                     # older 3.x fallback
    create_proxy = None

HERE = Path(__file__).parent
DB_PATH = Path.home() / ".cache" / "mcp-cache.db"
TTL_CLASS = {"immutable": 86400.0, "slow": 300.0, "live": 0.0}
WRITE_DEFAULT = [r"^write", r"^create", r"^update", r"^delete", r"^set_", r"^post", r"^put"]

STATS = {"hits": 0, "misses": 0, "bypass": 0, "flushes": 0}
MEM: dict[str, tuple[float, float, object]] = {}   # key -> (created, ttl, result_obj)
USAGE: list[dict] = []

def db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS cache(
        k TEXT PRIMARY KEY, tool TEXT, text TEXT,
        created REAL, ttl REAL, hits INTEGER DEFAULT 0)""")
    return conn

def text_of(result) -> str:
    content = getattr(result, "content", None) or []
    return "\n".join(getattr(c, "text", "") for c in content if getattr(c, "text", None))

class CacheMiddleware(Middleware):
    def __init__(self, ttl_rules: dict[str, str] | None = None,
                 write_patterns: list[str] | None = None):
        self.ttl_rules = ttl_rules or {}
        self.write_patterns = write_patterns or WRITE_DEFAULT

    def classify(self, tool: str) -> tuple[bool, float]:
        for pat in self.write_patterns:
            if re.search(pat, tool, re.I):
                return True, 0.0
        for pat, cls in self.ttl_rules.items():
            if re.search(pat, tool, re.I):
                return False, TTL_CLASS.get(cls, float(cls) if str(cls).replace('.','',1).isdigit() else 300.0)
        return False, TTL_CLASS["slow"]

    async def on_call_tool(self, context, call_next):
        msg = context.message
        tool = getattr(msg, "name", "")
        args = getattr(msg, "arguments", None) or {}
        if tool in LOCAL_TOOLS:                      # never cache the management plane
            return await call_next(context)
        is_write, ttl = self.classify(tool)
        if is_write:
            out = await call_next(context)
            n = len(MEM); MEM.clear()
            with db() as conn:
                conn.execute("DELETE FROM cache")
            STATS["flushes"] += 1
            return out
        if ttl <= 0:
            STATS["bypass"] += 1
            return await call_next(context)
        canon = json.dumps(args, sort_keys=True, separators=(",", ":"))
        k = hashlib.sha256(f"{tool}|{canon}".encode()).hexdigest()
        now = time.time()
        hit = MEM.get(k)
        if hit and now - hit[0] < hit[1]:
            STATS["hits"] += 1
            with db() as conn:
                conn.execute("UPDATE cache SET hits=hits+1 WHERE k=?", (k,))
            return hit[2]
        out = await call_next(context)
        MEM[k] = (now, ttl, out)
        with db() as conn:
            conn.execute("INSERT OR REPLACE INTO cache VALUES(?,?,?,?,?,0)",
                         (k, tool, text_of(out), now, ttl))
        STATS["misses"] += 1
        return out

def build(config: dict | None = None, ttl_rules: dict | None = None) -> FastMCP:
    cfg = config
    if cfg is None:
        p = HERE / "upstreams.json"
        cfg = json.loads(p.read_text()) if p.exists() else None
    if cfg:
        proxy = create_proxy(cfg) if create_proxy else FastMCP.as_proxy(cfg)
    else:
        proxy = FastMCP("cache-proxy")
    proxy.add_middleware(CacheMiddleware(ttl_rules=ttl_rules))

    @proxy.tool()
    def cache_stats() -> str:
        """Hit/miss/bypass/flush counters + per-tool cached-entry stats."""
        with db() as conn:
            rows = conn.execute("SELECT tool, COUNT(*), SUM(hits) FROM cache GROUP BY 1").fetchall()
        total = STATS["hits"] + STATS["misses"]
        rate = f"{STATS['hits']/total:.0%}" if total else "n/a"
        lines = [f"hits={STATS['hits']} misses={STATS['misses']} bypass={STATS['bypass']} "
                 f"flushes={STATS['flushes']} hit_rate={rate} mem_entries={len(MEM)}"]
        lines += [f"{t}: entries={c} hits={h or 0}" for t, c, h in rows]
        return "\n".join(lines)

    @proxy.tool()
    def cache_flush() -> str:
        """Flush all cached entries (memory + sqlite mirror)."""
        n = len(MEM); MEM.clear()
        with db() as conn:
            m = conn.execute("DELETE FROM cache").rowcount
        STATS["flushes"] += 1
        return f"flushed {n} memory / {m} persisted entries"

    @proxy.tool()
    def record_llm_usage(cache_read: int, cache_write: int, uncached_input: int, output: int) -> str:
        """Record one LLM call's token buckets for prompt-cache health analysis."""
        USAGE.append(dict(cache_read=cache_read, cache_write=cache_write,
                          uncached_input=uncached_input, output=output))
        return f"recorded call #{len(USAGE)}"

    @proxy.tool()
    def prompt_cache_health() -> str:
        """Prefix-instability diagnosis over recorded usage. MCP cannot cache prompts —
        this diagnoses; the fix is context ordering (skills/caching layer 1)."""
        if not USAGE:
            return "no usage recorded — call record_llm_usage per LLM call first"
        reads = sum(r["cache_read"] for r in USAGE)
        writes = sum(r["cache_write"] for r in USAGE)
        flags = []
        if writes and reads / max(writes, 1) < 1.0:
            flags.append(f"writes ({writes}) exceed reads ({reads}) — filling a cache never hit")
        totals = [r["cache_read"] + r["uncached_input"] for r in USAGE]
        if len(totals) >= 4 and totals[-1] > 1.5 * statistics.median(totals[: len(totals)//2]):
            flags.append("input per call trending up — prefix likely invalidating")
        per_w = [r["cache_write"] for r in USAGE]
        med = statistics.median(per_w)
        flags += [f"call {i}: cache_write {w} >10x median {med:.0f}"
                  for i, w in enumerate(per_w) if med and w > 10 * med]
        return ("INFLATION FLAGS:\n- " + "\n- ".join(flags)) if flags else \
               f"clean: reads={reads} writes={writes} calls={len(USAGE)}"

    return proxy

LOCAL_TOOLS = {"cache_stats", "cache_flush", "record_llm_usage", "prompt_cache_health"}

if __name__ == "__main__":
    build().run()
