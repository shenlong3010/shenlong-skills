#!/usr/bin/env bash
# PreToolUse (Bash): block cat/head/tail/less/more dumping a large file into
# context, mirroring guard-bulk-read.sh for the Bash path. Exit 2 = block.
# Silent exit 0 on every other path so the normal permission flow is untouched.
payload=$(cat)
PY=python3; [ "$(python3 -c 'print(1)' 2>/dev/null)" = "1" ] || PY=python
cmd=$(printf '%s' "$payload" | "$PY" -c "import json,sys; print(json.load(sys.stdin).get('tool_input',{}).get('command',''))" 2>/dev/null | tr -d '\r')
[ -z "$cmd" ] && exit 0

# Piped or redirected commands are targeted (cat file | grep, cat file > out),
# not a read-into-context operation.
case "$cmd" in *[\|\>]*) exit 0 ;; esac

file_path=""
if echo "$cmd" | grep -qE '^(cat|head|tail|less|more) '; then
  args=$(echo "$cmd" | sed -E 's/^(cat|head|tail|less|more) +//')
  # Word-split would break a quoted path containing spaces ("a dir/big
  # file.txt"). xargs -n1 with its own quote-aware parser splits into real
  # arguments without re-interpreting $(...) or backticks the way eval would.
  while IFS= read -r arg; do
    case "$arg" in
      -*) continue ;;
      *)  file_path="$arg"; break ;;
    esac
  done < <(printf '%s' "$args" | xargs -n1 printf '%s\n' 2>/dev/null)
fi
[ -z "$file_path" ] && exit 0
[ -f "$file_path" ] || exit 0

# Same threshold and rationale as guard-bulk-read.sh — see that file.
MIN_LINES="${BULK_READ_MIN_LINES:-400}"
case "$MIN_LINES" in ''|*[!0-9]*) MIN_LINES=400 ;; esac

lines=$(wc -l < "$file_path" 2>/dev/null | tr -d ' ') || exit 0
[ -z "$lines" ] && exit 0
[ "$lines" -le "$MIN_LINES" ] && exit 0

echo "blocked by guard-bulk-cat.sh: $file_path is $lines lines (limit $MIN_LINES). Delegate to a Haiku subagent via the Agent tool (see the bulk-reader skill) instead of cat/head/tail." >&2
exit 2
