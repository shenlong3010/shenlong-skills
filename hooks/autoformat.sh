#!/usr/bin/env bash
# PostToolUse (Edit|Write): format the touched file if a formatter is configured. Best-effort, never blocks.
payload=$(cat)
f=$(printf '%s' "$payload" | python3 -c "import json,sys; print(json.load(sys.stdin).get('tool_input',{}).get('file_path',''))" 2>/dev/null)
[ -z "$f" ] && exit 0
case "$f" in
  *.py)  command -v ruff >/dev/null && ruff format -q "$f";;
  *.js|*.ts|*.jsx|*.tsx|*.json|*.md) command -v prettier >/dev/null && prettier -w --log-level silent "$f";;
  *.java) command -v google-java-format >/dev/null && google-java-format -i "$f";;
esac
exit 0
