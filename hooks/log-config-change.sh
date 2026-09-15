#!/usr/bin/env bash
# ConfigChange: log which settings tier changed (user/project/local/policy/
# skills) and when. Docs confirm (2026-09-15) the payload has NO filename or
# diff field, only `source` — originally planned as auto-backup-on-edit, but
# that needs a target file this event doesn't provide, so scoped down to an
# audit trail: "X tier changed at TS" is still useful for spotting drift
# across sessions, just not a backup mechanism. Exit 2 is a documented no-op
# for this event (change proceeds regardless) — logger exits 0 always.
payload=$(cat)
PY=python3; [ "$(python3 -c 'print(1)' 2>/dev/null)" = "1" ] || PY=python
ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
source=$(printf '%s' "$payload" | "$PY" -c "import json,sys; print(json.load(sys.stdin).get('source',''))" 2>/dev/null | tr -d '\r')
[ -z "$source" ] && source="UNKNOWN"
echo "$ts source=$source" >> "$HOME/.claude/config-change.log"
exit 0
