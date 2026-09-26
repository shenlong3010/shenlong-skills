#!/usr/bin/env bash
# PreToolUse (Read): block whole-file reads of very large files. Exit 2 = block.
# Silent exit 0 on every other path so the normal permission flow is untouched.
payload=$(cat)
PY=python3; [ "$(python3 -c 'print(1)' 2>/dev/null)" = "1" ] || PY=python

# Newline-delimited (paths may contain spaces). Python on Windows writes CRLF,
# so terminate each field explicitly and strip the stray \r.
{ read -r f; read -r offset; read -r limit; } <<<"$(printf '%s' "$payload" | "$PY" -c "
import json,sys
t=json.load(sys.stdin).get('tool_input',{})
for k in ('file_path','offset','limit'):
    sys.stdout.write((str(t.get(k,'') or '-'))+'\n')
" 2>/dev/null | tr -d '\r')"

[ "$f" = "-" ] || [ -z "$f" ] && exit 0
# A targeted read is already the behavior this hook wants to encourage.
[ "$offset" != "-" ] || [ "$limit" != "-" ] && exit 0
[ -f "$f" ] || exit 0

# Measured 2026-09-13: delegating a 6751-line file to a Haiku subagent cost
# 140.4k tokens total vs 45.3k reading it directly (3.1x more raw tokens) — but
# at Opus billing that trade is ~19x CHEAPER, since Haiku runs ~60x below Opus
# rate and only the subagent's short answer lands in the caller's context.
# 400 lines keeps the direct-read path for genuinely small files, where
# subagent spawn overhead (4 API calls minimum) isn't worth it regardless of
# rate. Override with BULK_READ_MIN_LINES if running on Sonnet/Haiku, where
# the economics are closer to breakeven.
MIN_LINES="${BULK_READ_MIN_LINES:-400}"
case "$MIN_LINES" in ''|*[!0-9]*) MIN_LINES=400 ;; esac

lines=$(wc -l < "$f" 2>/dev/null | tr -d ' ') || exit 0
[ -z "$lines" ] && exit 0
[ "$lines" -le "$MIN_LINES" ] && exit 0

echo "blocked by guard-bulk-read.sh: $f is $lines lines (limit $MIN_LINES). Escapes, cheapest first: Read with offset/limit for the section you need (allowed, not blocked), Grep for a targeted match, or delegate to a Haiku subagent via the Agent tool (see the shenlong-bulk-reader skill) if you truly need the whole file — cheaper on Opus even though it costs more raw tokens. Override the threshold with BULK_READ_MIN_LINES if this file is a genuine exception." >&2
exit 2
