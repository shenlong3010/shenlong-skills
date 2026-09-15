#!/usr/bin/env bash
# SubagentStop: log agent_type + a truncated tail of its final message, to
# see which subagent types get used and how they conclude, without shelling
# out (docs confirm agent_id/agent_type/last_assistant_message are already
# in the payload — no extra work needed to get real data, unlike Hook 2's
# MCP audit which had to shell out because SessionStart carries no server
# list). Exit 2 on this event blocks the subagent from stopping (confirmed
# 2026-09-15) — this is a pure logger, must never exit 2, even on error.
payload=$(cat)
PY=python3; [ "$(python3 -c 'print(1)' 2>/dev/null)" = "1" ] || PY=python
ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
line=$(printf '%s' "$payload" | PYTHONIOENCODING=utf-8 "$PY" -c "
import json,sys
d=json.load(sys.stdin)
agent_type = d.get('agent_type','?')
agent_id = d.get('agent_id','?')
msg = (d.get('last_assistant_message') or '').replace('\n',' ').strip()[:150]
print(f'{agent_type} | {agent_id} | {msg}')
" 2>/dev/null | tr -d '\r')
[ -z "$line" ] && exit 0
echo "$ts $line" >> "$HOME/.claude/subagent.log"
exit 0
