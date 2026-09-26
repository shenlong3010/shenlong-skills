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
# Restrict to owner — VERIFIED NO-OP on this machine's Windows/NTFS via Git
# Bash (tested 2026-09-13: stat showed mode stayed 0644, chmod reported no
# error). Kept anyway since it's free and this is a single-user login either
# way; treat the raw payload as readable by anything running as this OS user.
chmod 600 "$raw_file" 2>/dev/null
line=$(printf '%s' "$payload" | "$PY" -c "
import json, re, sys
d=json.load(sys.stdin)
err = d.get('error') or d.get('error_message') or (d.get('tool_response') or {}).get('error') or ''
# Collapse ALL whitespace before truncating. A traceback or a multi-line tool
# error carries embedded newlines, and [:200] bounds length but not lines --
# one failure then wrote N log lines and broke the one-row-per-failure
# contract (measured 2026-09-26: 69 of 106 rows were spill from a handful of
# real failures, so every count off this file was wrong).
err = re.sub(r'\s+', ' ', str(err)).strip()
print(f\"{d.get('tool_name','?')} | {err[:200]}\")
" 2>/dev/null | tr -d '\r')
[ -z "$line" ] && exit 0
echo "$ts $line" >> "$HOME/.claude/tool-failures.log"
exit 0
