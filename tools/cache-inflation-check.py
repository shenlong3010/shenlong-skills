#!/usr/bin/env python3
"""Flag prompt-cache spend anomalies from telemetry records.
Input: JSONL on stdin, one record per call:
  {"cache_read": int, "cache_write": int, "uncached_input": int, "output": int}
Flags: (a) cache writes >> reads (paying to fill a cache never hit),
       (b) cache_read + uncached_input growing per call (prefix instability),
       (c) write/read ratio anomalies vs the session median."""
import json, statistics, sys

def main() -> int:
    recs = [json.loads(l) for l in sys.stdin if l.strip()]
    if not recs:
        print("no records"); return 2
    reads = sum(r.get("cache_read", 0) for r in recs)
    writes = sum(r.get("cache_write", 0) for r in recs)
    flags = []
    if writes and reads / max(writes, 1) < 1.0:
        flags.append(f"writes ({writes}) exceed reads ({reads}) — paying cache-fill without reuse; check prefix stability")
    totals = [r.get("cache_read", 0) + r.get("uncached_input", 0) for r in recs]
    if len(totals) >= 4 and totals[-1] > 1.5 * statistics.median(totals[: len(totals)//2]):
        flags.append("input tokens per call trending up — cache prefix likely invalidating (dynamic content before static)")
    per_call_w = [r.get("cache_write", 0) for r in recs]
    med = statistics.median(per_call_w)
    for i, w in enumerate(per_call_w):
        if med and w > 10 * med:
            flags.append(f"call {i}: cache_write {w} is >10x median {med:.0f} — inflation event")
    if flags:
        print("INFLATION FLAGS:"); [print(" -", f) for f in flags]; return 1
    print(f"clean: reads={reads} writes={writes} calls={len(recs)}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
