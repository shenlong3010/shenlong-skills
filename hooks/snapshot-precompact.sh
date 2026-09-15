#!/usr/bin/env bash
# PreCompact: log a marker before context gets summarized, so a post-compact
# session has a breadcrumb of when/why compaction happened (manual vs auto)
# without relying on memory of the pre-compact state, which the summary may
# thin out. Confirmed via docs 2026-09-15: exit 2 on this event BLOCKS
# compaction — this script is a pure logger and must never risk that, so
# every path (including error paths) falls through to exit 0 explicitly.
payload=$(cat)
PY=python3; [ "$(python3 -c 'print(1)' 2>/dev/null)" = "1" ] || PY=python
ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
trigger=$(printf '%s' "$payload" | "$PY" -c "import json,sys; print(json.load(sys.stdin).get('trigger',''))" 2>/dev/null | tr -d '\r')
cwd=$(printf '%s' "$payload" | "$PY" -c "import json,sys; print(json.load(sys.stdin).get('cwd',''))" 2>/dev/null | tr -d '\r')
session_id=$(printf '%s' "$payload" | "$PY" -c "import json,sys; print(json.load(sys.stdin).get('session_id',''))" 2>/dev/null | tr -d '\r')
echo "$ts trigger=$trigger session=$session_id cwd=$cwd" >> "$HOME/.claude/compact.log"
exit 0
