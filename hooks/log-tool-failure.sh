#!/usr/bin/env bash
# PostToolUseFailure: append failed tool name + error to a rolling log.
# Surfaces failures (like the python3-stub hookify bug) at the point they
# happen instead of only as generic "Stop hook error" noise at turn end.
#
# Field name for the error/reason is UNCONFIRMED (docs fetches didn't surface
# PostToolUseFailure's exact schema — 2026-09-13). Logs the raw payload
# alongside the parsed line specifically so a wrong field-name guess is
# visible and correctable, not silently empty forever.
payload=$(cat)
PY=python3; [ "$(python3 -c 'print(1)' 2>/dev/null)" = "1" ] || PY=python
ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
raw_file="$HOME/.claude/.last-tool-failure-raw.json"
printf '%s' "$payload" > "$raw_file" 2>/dev/null
# Restrict to owner — real protection on Linux/macOS. VERIFIED NO-OP on
# Windows/NTFS via Git Bash (tested 2026-09-13: stat showed mode stayed 0644
# after this call, chmod itself reported no error). Kept because it costs
# nothing and works on the other two platforms; on Windows treat this file
# as readable by anything running as the same OS user regardless.
chmod 600 "$raw_file" 2>/dev/null
line=$(printf '%s' "$payload" | "$PY" -c "
import json,sys
d=json.load(sys.stdin)
err = d.get('error') or d.get('error_message') or (d.get('tool_response') or {}).get('error') or ''
print(f\"{d.get('tool_name','?')} | {str(err)[:200]}\")
" 2>/dev/null | tr -d '\r')
[ -z "$line" ] && exit 0
echo "$ts $line" >> "$HOME/.claude/tool-failures.log"
exit 0
