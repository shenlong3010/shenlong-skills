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
servers=$(timeout 25 claude mcp list 2>&1 | tr '\n' ';' | tr -d '\r')
rc=$?
if [ "$rc" -eq 124 ]; then
  servers="TIMEOUT after 5s"
elif [ "$rc" -ne 0 ]; then
  servers="FAILED rc=$rc: $servers"
fi
echo "$ts cwd=$cwd servers=$servers" >> "$HOME/.claude/mcp-audit.log"
exit 0
