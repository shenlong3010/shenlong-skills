#!/usr/bin/env bash
# Stop hook: append per-session cost metrics to a local usage log for spend visibility.
# Extracts only scalar fields — the raw payload (commands, paths) never touches disk,
# and tab/newline injection dies here because every field is a JSON scalar.
payload=$(cat)
# Windows Store ships a python3 stub that prints an error yet exits 0 — test output, not exit code.
PY=python3; [ "$(python3 -c 'print(1)' 2>/dev/null)" = "1" ] || PY=python
row=$(printf '%s' "$payload" | "$PY" -c '
import json, sys
try:
    p = json.load(sys.stdin)
    print("\t".join(str(p.get(k, "-")) for k in ("session_id", "total_cost_usd", "total_duration_ms", "num_turns")))
except Exception:
    print("-\t-\t-\t-")')
# UTC ISO stamp: %s-style epoch works everywhere, unlike GNU-only `date -Iseconds`.
printf '%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$row" >> "${HOME}/.claude/usage.log"
exit 0
