#!/usr/bin/env bash
# PreToolUse guard: block obviously destructive bash commands. Exit 2 = block.
#
# ADVISORY, NOT A SECURITY BOUNDARY. This is a fixed-substring denylist and is
# fail-open by construction: whitespace variants (rm  -rf  ~), flag reordering
# (rm --recursive --force /), indirection (X=rf; rm -$X /), and any obfuscation
# the shell resolves at runtime but this matcher does not see will pass. A JSON
# parse failure also fails open (empty cmd -> no match -> exit 0). Treat it as a
# speed-bump that catches accidents, never as the control that makes destructive
# commands safe — reversibility discipline (CLAUDE.md rule 11) is the real guard.
# Hardening tracked in .agents/BACKLOG.md (guard-dangerous standing-landmines story).
payload=$(cat)
# Windows Store ships a python3 stub that prints an error yet exits 0 — test output, not exit code.
PY=python3; [ "$(python3 -c 'print(1)' 2>/dev/null)" = "1" ] || PY=python
cmd=$(printf '%s' "$payload" | "$PY" -c "import json,sys; print(json.load(sys.stdin).get('tool_input',{}).get('command',''))" 2>/dev/null)
case "$cmd" in
  *"rm -rf /"*|*"rm -rf ~"*|*"git push --force"*|*"git push -f "*|*"DROP TABLE"*|*"DROP DATABASE"*|*":(){ :|:& };:"*)
    echo "blocked by guard-dangerous.sh: destructive pattern" >&2; exit 2;;
esac
exit 0
