#!/usr/bin/env bash
# Stop hook: append per-turn session metrics to a local log.
#
# SCOPE CORRECTED 2026-09-17 after capturing a real Stop payload. This hook
# previously logged total_cost_usd / total_duration_ms / num_turns and wrote
# 2323 rows with all three empty. The cause was not a wrong field name -- the
# Stop event carries NO cost, duration, or turn-count data at all. Verified
# real top-level keys on Claude Code 2.x:
#
#   background_tasks, cwd, effort, hook_event_name, last_assistant_message,
#   permission_mode, prompt_id, scratchpad_dir, session_crons, session_id,
#   stop_hook_active, transcript_path
#
# So per-turn spend is not obtainable here by any field name, and the honest
# fix is to stop claiming it. Cost data must come from the CLI's own usage
# reporting or the transcript, not this event.
#
# What IS available and worth logging: session identity plus the effort level
# and permission mode in force for the turn, which are the knobs that actually
# move cost. Extracts only scalars, so payload content (commands, paths,
# message text) never touches disk and tab/newline injection cannot forge a
# column.
payload=$(cat)
# Windows Store ships a python3 stub that prints an error yet exits 0 — test output, not exit code.
PY=python3; [ "$(python3 -c 'print(1)' 2>/dev/null)" = "1" ] || PY=python
row=$(printf '%s' "$payload" | "$PY" -c '
import json, sys
WANT = ("session_id", "effort", "permission_mode", "stop_hook_active")
try:
    p = json.load(sys.stdin)
    print("\t".join(str(p.get(k, "-")).replace("\t", " ") for k in WANT))
except Exception:
    print("-\t-\t-\tPARSE_FAIL")')
# UTC ISO stamp: %s-style epoch works everywhere, unlike GNU-only `date -Iseconds`.
printf '%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$row" >> "${HOME}/.claude/usage.log"
exit 0
