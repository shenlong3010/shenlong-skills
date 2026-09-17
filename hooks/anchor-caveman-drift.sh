#!/usr/bin/env bash
# UserPromptSubmit: re-anchor caveman mode ONLY when measured output shows
# real drift, and anchor the dimension the existing reminder misses.
#
# WHY THIS EXISTS. The caveman plugin's own per-turn hook is, by its docs,
# "just an attention anchor" -- 26 words naming filler/articles/pleasantries.
# The full ruleset ships once at SessionStart and is then buried under the
# whole conversation. Measured here 2026-09-17: a 248-word verbose turn
# scored filler=0. Drift is NOT lexical -- the existing anchor's targets were
# already satisfied. Drift is STRUCTURAL: tables, headers, recap paragraphs,
# transition sentences, restating what was just done. None of that is filler,
# so nothing currently pushes back on it.
#
# Self-reinforcement makes it worse: each prose-heavy turn becomes the
# in-context example the next turn imitates, and recent context outweighs a
# short instruction.
#
# Fires only on evidence, from measure-output-length.sh's log. An
# unconditional second reminder would be duplicate context every turn -- the
# exact token cost this is supposed to reduce.
#
# Every path exits 0: exit 2 on UserPromptSubmit ERASES the user's prompt.
log="$HOME/.claude/output-length.log"
[ -f "$log" ] || exit 0

PY=python3; [ "$(python3 -c 'print(1)' 2>/dev/null)" = "1" ] || PY=python

# Pipe the log in on stdin rather than passing its path: $HOME here is a Git
# Bash POSIX path (/c/Users/...) that Windows Python cannot open. Passing the
# path made open() raise FileNotFoundError, which 2>/dev/null then swallowed --
# the hook looked like it was working and silently never fired. Caught by
# testing the drift case rather than trusting exit 0. stdin sidesteps all
# path translation.
verdict=$(tail -n 50 "$log" | PYTHONIOENCODING=utf-8 "$PY" -c "
import re, sys

WINDOW = 3      # recent turns considered
WORD_CAP = 120  # prose words above this is structural drift, not an answer

lines = [l for l in sys.stdin if 'words=' in l]

recent = lines[-WINDOW:]
if len(recent) < WINDOW:
    sys.exit(0)   # not enough evidence yet -- stay silent

counts = []
for l in recent:
    m = re.search(r'words=(\d+)', l)
    if m:
        counts.append(int(m.group(1)))

if len(counts) < WINDOW:
    sys.exit(0)

over = [c for c in counts if c > WORD_CAP]
# Require a majority of the window over cap. One long turn is often a
# legitimately long answer; a sustained run is drift.
if len(over) * 2 <= WINDOW:
    sys.exit(0)

print(max(counts))
" 2>/dev/null | tr -d '\r')

[ -z "$verdict" ] && exit 0

ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
echo "$ts anchored peak_words=$verdict" >> "$HOME/.claude/caveman-anchor.log"

echo "[caveman-drift] Last 3 responses averaged over 120 prose words — that is structural drift, not filler drift (filler count is already 0). The prose rules are being followed; the SHAPE is not. Cut: section headers, tables used for 2-3 items, recap paragraphs restating what was just done, transition sentences between steps, and closing summaries of work the user just watched happen. State the finding, then stop. Code blocks and security warnings stay normal prose."
exit 0
