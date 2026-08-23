#!/usr/bin/env python3
"""Spend Report — summarize the Claude Code usage log written by hooks/cost-logger.sh.

Reads TSV rows: <UTC timestamp>\t<session_id>\t<total_cost_usd>\t<total_duration_ms>\t<num_turns>
Tolerates legacy rows (raw JSON payloads from the pre-2026-08 logger) by skipping them
and reporting the skip count. Read-only; writes nothing.

Usage:
    python3 tools/spend-report.py [--days N] [--log PATH] [--json] [--top K]

Exit codes: 0 report produced · 1 log missing/unreadable · 2 usage error.
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone

DEFAULT_LOG = os.path.join(os.path.expanduser("~"), ".claude", "usage.log")


def parse_args(argv):
    p = argparse.ArgumentParser(description="Summarize ~/.claude/usage.log spend data.")
    p.add_argument("--days", type=int, default=30, metavar="N",
                   help="window in days (default 30)")
    p.add_argument("--log", default=DEFAULT_LOG, help="usage log path")
    p.add_argument("--json", action="store_true", dest="as_json",
                   help="emit machine-readable JSON instead of a table")
    p.add_argument("--top", type=int, default=5, metavar="K",
                   help="rows in the top-sessions table (default 5)")
    return p.parse_args(argv)


def _f(value, default=None):
    return default if value in ("-", "", None) else float(value)


def parse_rows(path):
    """Yield (timestamp, session_id, cost_usd, duration_ms, turns); skip unparseable rows."""
    skipped = 0
    with open(path, encoding="utf-8-sig", errors="replace") as fh:
        for lineno, line in enumerate(fh, 1):
            parts = line.rstrip("\n").split("\t")
            if len(parts) != 5 or parts[0].count("-") < 2:
                skipped += 1
                continue
            try:
                ts = datetime.strptime(parts[0][:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
                session_id = parts[1]
                cost = _f(parts[2])
                duration_ms = _f(parts[3], 0.0)
                turns = _f(parts[4], 0.0)
            except ValueError:
                skipped += 1
                continue
            if cost is None:
                skipped += 1
                continue
            yield ts, session_id, cost, duration_ms, turns
    if skipped:
        print(f"note: skipped {skipped} unparseable/legacy row(s)", file=sys.stderr)


def main(argv=None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if not os.path.isfile(args.log):
        print(f"error: usage log not found at {args.log} "
              f"(wire hooks/cost-logger.sh — see hooks/README.md)", file=sys.stderr)
        return 1
    if args.days <= 0:
        print("error: --days must be positive", file=sys.stderr)
        return 2

    cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)
    rows = [r for r in parse_rows(args.log) if r[0] >= cutoff]

    sessions = defaultdict(lambda: {"cost": 0.0, "ms": 0.0, "turns": 0.0})
    by_day = defaultdict(lambda: {"cost": 0.0, "sessions": set()})
    for ts, sid, cost, ms, turns in rows:
        s = sessions[sid]
        s["cost"] += cost
        s["ms"] += ms
        s["turns"] += turns
        day = ts.strftime("%Y-%m-%d")
        by_day[day]["cost"] += cost
        by_day[day]["sessions"].add(sid)

    total_cost = sum(s["cost"] for s in sessions.values())
    top = sorted(sessions.items(), key=lambda kv: kv[1]["cost"], reverse=True)[:args.top]

    if args.as_json:
        print(json.dumps({
            "days": args.days,
            "total_cost_usd": round(total_cost, 4),
            "sessions": len(sessions),
            "by_day": {d: {"cost": round(v["cost"], 4), "sessions": len(v["sessions"])}
                       for d, v in sorted(by_day.items())},
            "top_sessions": [{"session": k[:12], "cost": round(v["cost"], 4),
                              "turns": int(v["turns"]),
                              "hours": round(v["ms"] / 3_600_000, 2)}
                             for k, v in top],
        }, indent=2))
        return 0

    print(f"Spend report — last {args.days} day(s) ({len(rows)} logged responses)")
    print(f"  total:      ${total_cost:.4f}")
    print(f"  sessions:   {len(sessions)}"
          + (f"  (${total_cost / len(sessions):.4f}/session avg)" if sessions else ""))
    print("\n  by day:")
    for d, v in sorted(by_day.items()):
        print(f"    {d}  ${v['cost']:.4f}  ({len(v['sessions'])} session(s))")
    if top:
        print(f"\n  top {len(top)} session(s):")
        for k, v in top:
            print(f"    {k[:12]}…  ${v['cost']:.4f}  {int(v['turns'])} turn(s)"
                  f"  {v['ms'] / 3_600_000:.2f}h")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
