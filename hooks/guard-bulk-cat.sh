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

# BUG FIXED 2026-09-17: `head -50 big.log` reads 50 lines -- it IS the cheap
# bounded read this hook exists to steer toward, and it was being blocked
# exactly like a bare `cat`, with a message that said "instead of
# cat/head/tail" and pointed at a subagent. That steered work away from the
# correct answer toward spawning an agent to read 50 lines. Same failure class
# as the model-switch guard: the guard blocked the legitimate escape and the
# message never named a working one. guard-bulk-read.sh already exits 0 when
# offset/limit is set; this is the Bash-side equivalent of that rule.
case "$cmd" in
  head\ *|tail\ *)
    # An explicit count (-n 50, -50, -n50) bounds the read. No count means
    # the default 10 lines for head/tail, which is also bounded -- so any
    # head/tail invocation on a plain file is fine. Only cat/less/more read
    # the whole thing.
    exit 0 ;;
esac

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

echo "blocked by guard-bulk-cat.sh: $file_path is $lines lines (limit $MIN_LINES). Escapes, cheapest first: \`head -N\`/\`tail -N\` for a bounded slice (allowed, not blocked), \`grep\` for a targeted match, or delegate to a Haiku subagent via the Agent tool (see the bulk-reader skill) if you truly need the whole file. Override the threshold with BULK_READ_MIN_LINES if this file is a genuine exception." >&2
exit 2
