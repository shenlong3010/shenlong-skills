#!/usr/bin/env bash
# PreToolUse guard: block obviously destructive bash commands. Exit 2 = block.
payload=$(cat)
# Windows Store ships a python3 stub that prints an error yet exits 0 — test output, not exit code.
PY=python3; [ "$(python3 -c 'print(1)' 2>/dev/null)" = "1" ] || PY=python
cmd=$(printf '%s' "$payload" | "$PY" -c "import json,sys; print(json.load(sys.stdin).get('tool_input',{}).get('command',''))" 2>/dev/null)
case "$cmd" in
  *"rm -rf /"*|*"rm -rf ~"*|*"git push --force"*|*"git push -f "*|*"DROP TABLE"*|*"DROP DATABASE"*|*":(){ :|:& };:"*)
    echo "blocked by guard-dangerous.sh: destructive pattern" >&2; exit 2;;
esac
exit 0
