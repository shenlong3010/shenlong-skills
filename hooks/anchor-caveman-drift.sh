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
# Threshold scales with active mode. Caps CALIBRATED 2026-09-17 against the
# caveman plugin's own eval snapshot (evals/snapshots/results.json, 10 prompts,
# claude-opus-4-6), not guessed:
#   __baseline__ 121.1 avg words | __terse__ 125.8 | caveman(full) 60.8
#   caveman-cn 24.5 | compress 91.9
# Notably "Answer concisely." (__terse__ 125.8) is no better than no prompt at
# all (__baseline__ 121.1) -- generic terseness instructions do nothing, which
# is exactly why an anchor has to name specifics.
# Caps sit ~1.5x the measured average for that mode: enough headroom that a
# legitimately long answer does not trip it, tight enough to catch a sustained
# run of drift. `full` = 90 (1.5 x 60.8). `ultra` has no eval arm, so 45 is
# extrapolated from it being strictly tighter than full -- the one guess left
# here, and flagged as such.
# Mode comes from the caveman plugin's flag file; missing/unknown falls back
# to `full`.
mode=""
[ -f "$HOME/.caveman-active" ] && mode=$(tr -d '\r\n' < "$HOME/.caveman-active" 2>/dev/null)
[ -z "$mode" ] && [ -f "$HOME/.claude/.caveman-active" ] && mode=$(tr -d '\r\n' < "$HOME/.claude/.caveman-active" 2>/dev/null)
case "$mode" in
  ultra)              cap=45  ;;  # extrapolated: no eval arm exists
  wenyan-ultra)       cap=25  ;;  # caveman-cn measured 24.5 avg
  wenyan-full)        cap=40  ;;  # between cn (24.5) and full (60.8)
  lite)               cap=140 ;;  # near __terse__ (125.8); lite keeps sentences
  *)                  cap=90  ;;  # 1.5 x caveman full measured 60.8
esac

verdict=$(tail -n 50 "$log" | WORD_CAP="$cap" PYTHONIOENCODING=utf-8 "$PY" -c "
import re, sys, os

WINDOW = 3      # recent turns considered
WORD_CAP = int(os.environ.get('WORD_CAP', '120'))

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
echo "$ts anchored mode=${mode:-full} cap=$cap peak_words=$verdict" >> "$HOME/.claude/caveman-anchor.log"

echo "[caveman-drift] Mode is ${mode:-full} (cap $cap prose words); recent turns hit $verdict. That is structural drift, not filler drift — filler count is already 0, so the word-choice rules are being followed and the SHAPE is not. Cut: section headers, tables used for 2-3 items, recap paragraphs restating what was just done, transition sentences between steps, and closing summaries of work the user just watched happen. State the finding, then stop. Code blocks and security warnings stay normal prose."
exit 0
