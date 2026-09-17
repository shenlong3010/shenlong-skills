#!/usr/bin/env bash
# Stop hook: append per-session cost metrics to a local usage log for spend visibility.
# Extracts only scalar fields — the raw payload (commands, paths) never touches disk,
# and tab/newline injection dies here because every field is a JSON scalar.
payload=$(cat)
# Windows Store ships a python3 stub that prints an error yet exits 0 — test output, not exit code.
PY=python3; [ "$(python3 -c 'print(1)' 2>/dev/null)" = "1" ] || PY=python
# KNOWN BROKEN as of 2026-09-17, kept deliberately visible rather than
# silently wrong: on the source machine this wrote 2323 rows with every metric
# field "-". The names below (total_cost_usd/total_duration_ms/num_turns) were
# guessed and do not exist on the Stop payload there, so the spend-visibility
# purpose has never actually worked. Rather than guess a second set of names,
# this now records WHICH keys the payload really carries whenever the expected
# ones are all missing -- so the first real firing reveals the true schema
# instead of adding another indistinguishable "-" row.
row=$(printf '%s' "$payload" | "$PY" -c '
import json, sys
WANT = ("session_id", "total_cost_usd", "total_duration_ms", "num_turns")
try:
    p = json.load(sys.stdin)
    vals = [str(p.get(k, "-")) for k in WANT]
    # Every metric empty => the field names are wrong for this build. Emit the
    # actual top-level keys so the schema is recoverable from the log itself.
    if all(v == "-" for v in vals[1:]):
        vals.append("SCHEMA_MISS keys=" + ",".join(sorted(p.keys())))
    print("\t".join(vals))
except Exception:
    print("-\t-\t-\t-\tPARSE_FAIL")')
# UTC ISO stamp: %s-style epoch works everywhere, unlike GNU-only `date -Iseconds`.
printf '%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$row" >> "${HOME}/.claude/usage.log"
exit 0
