#!/usr/bin/env bash
# SessionStart: log actually-connected MCP servers (via `claude mcp list`) to
# a rolling audit file, not just cwd+timestamp — a bare SessionStart payload
# carries no server-list field (confirmed against docs 2026-09-13), so the
# only way to get real data is to shell out.
# Not injected into context (would add to the overhead being measured) —
# check ~/.claude/mcp-audit.log periodically to see which servers actually
# connect vs sit idle, informing which to disable by default per project.
#
# `timeout 25` bounds the subprocess (an unbounded shell-out inside
# SessionStart could hang forever). Measured 2026-09-13: a real
# `claude mcp list` run against ~14 configured servers takes ~16s (each
# server gets a live health check) — an earlier 5s timeout was WRONG and
# would have false-TIMEOUT'd every single run; 25s gives headroom.
# MUST be wired with "async": true in settings.json (see hooks/README or
# settings.json comment) — a synchronous 16s call here would add 16s to
# every session start, which is the exact overhead this whole session is
# trying to cut. On timeout or non-zero exit the failure is LOGGED, not
# swallowed (fail-loudly) — a silent 2>/dev/null here would hide a real
# PATH/auth problem as an empty server list indistinguishable from "no
# servers".
payload=$(cat)
PY=python3; [ "$(python3 -c 'print(1)' 2>/dev/null)" = "1" ] || PY=python
ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
cwd=$(printf '%s' "$payload" | "$PY" -c "import json,sys; print(json.load(sys.stdin).get('cwd',''))" 2>/dev/null | tr -d '\r')
raw=$(timeout 25 claude mcp list 2>&1)
rc=$?
if [ "$rc" -eq 124 ]; then
  servers="TIMEOUT25"
elif [ "$rc" -ne 0 ]; then
  servers="RUNFAIL_rc$rc"
else
  # Compact name:status pairs — raw CLI output is ~1-2KB/line (full URLs,
  # command paths, prose per server); only connect/fail/pending/disabled
  # status is ever queried later, so collapse to one char per server.
  # Status legend: + connected, - failed, ~ pending approval, o disabled.
  # PYTHONIOENCODING forces UTF-8 stdin — on Windows, python.exe defaults
  # stdin to the console codepage (cp1252 on this dev machine), which
  # mis-decodes claude mcp list's UTF-8 status symbols (✔/✘/⏸/⊘) into 3
  # garbage chars each, so no symbol ever matches. Confirmed via direct
  # repr()/ord() test 2026-09-15. No-op on Linux/macOS (already UTF-8
  # default) — safe to set unconditionally.
  servers=$(printf '%s' "$raw" | PYTHONIOENCODING=utf-8 "$PY" -c "
import sys, re
out = []
for line in sys.stdin:
    m = re.match(r'^([A-Za-z0-9_.:-]+):\s', line)
    if not m:
        continue
    name = m.group(1)
    if '✔' in line:
        st = '+'
    elif '✘' in line:
        st = '-'
    elif '⏸' in line:
        st = '~'
    elif '⊘' in line:
        st = 'o'
    else:
        st = '?'
    out.append(f'{name}:{st}')
print(','.join(out))
" 2>/dev/null | tr -d '\r')
  [ -z "$servers" ] && servers="PARSEFAIL"
fi
echo "$ts $cwd $servers" >> "$HOME/.claude/mcp-audit.log"
exit 0
