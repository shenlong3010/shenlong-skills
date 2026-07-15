#!/usr/bin/env bash
# PostToolUse (Edit|Write): format the touched file if a formatter is configured. Best-effort, never blocks.
payload=$(cat)
# Windows Store ships a python3 stub that prints an error yet exits 0 — test output, not exit code.
PY=python3; [ "$(python3 -c 'print(1)' 2>/dev/null)" = "1" ] || PY=python
f=$(printf '%s' "$payload" | "$PY" -c "import json,sys; print(json.load(sys.stdin).get('tool_input',{}).get('file_path',''))" 2>/dev/null)
[ -z "$f" ] && exit 0
case "$f" in
  *.py)  command -v ruff >/dev/null && ruff format -q "$f";;
  *.js|*.ts|*.jsx|*.tsx|*.json|*.md) command -v prettier >/dev/null && prettier -w --log-level silent "$f";;
  *.java) command -v google-java-format >/dev/null && google-java-format -i "$f";;
esac
exit 0
