#!/usr/bin/env bash
# Stop: measure the final assistant message and log its size, so caveman-mode
# drift is a measured number rather than a vibe.
#
# WHY THIS SHAPE AND NOT A REWRITER: verified against docs 2026-09-17 --
# no hook can rewrite assistant output before display. Stop and MessageDisplay
# both see the text read-only, and MessageDisplay is explicitly display-only.
# So enforcement can only ever be prevention (reminder before generation) or
# measurement (after). The caveman plugin already injects a reminder on every
# prompt; a second identical reminder would be duplicate context on every turn
# -- pure token cost, no new signal. This hook does the part that is actually
# missing: recording whether the reminder is WORKING.
#
# Reads ~/.claude/output-length.log to answer: is output actually terse, and
# does it drift over a long session? Only once that data exists is a
# conditional re-reminder worth designing -- and it would need a mechanism
# that does not yet exist here, since Stop fires after the response is
# already written.
#
# Exit 2 on Stop BLOCKS the turn from ending (docs-confirmed for this event),
# which would trap the session. Pure logger: every path exits 0.
payload=$(cat)
PY=python3; [ "$(python3 -c 'print(1)' 2>/dev/null)" = "1" ] || PY=python
ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
line=$(printf '%s' "$payload" | PYTHONIOENCODING=utf-8 "$PY" -c "
import json, sys, re

try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)

msg = d.get('last_assistant_message') or ''
if not msg:
    sys.exit(0)

# Strip fenced code blocks before measuring: CLAUDE.md exempts code from
# caveman, so counting it as prose would flag every code-heavy turn as drift.
prose = re.sub(r'\`\`\`.*?\`\`\`', '', msg, flags=re.DOTALL)

words = len(prose.split())
chars = len(prose)
# Filler markers caveman mode is supposed to eliminate. Their presence in
# prose is the actual drift signal, independent of raw length -- a long
# answer can still be terse, and a short one can still be padded.
filler = len(re.findall(
    r'\b(just|really|basically|actually|simply|certainly|of course|'
    r'I would be happy|feel free|please note|it.s worth noting|'
    r'that said|in order to|make sure to)\b',
    prose, flags=re.IGNORECASE))
sid = d.get('session_id', '-')
print(f'{sid} words={words} chars={chars} filler={filler}')
" 2>/dev/null | tr -d '\r')

[ -z "$line" ] && exit 0
echo "$ts $line" >> "$HOME/.claude/output-length.log"
exit 0
