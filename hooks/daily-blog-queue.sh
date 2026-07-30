#!/usr/bin/env bash
# SessionEnd hook: queue tomorrow's engineering-blog read.
#
# SessionEnd has a ~1.5s shared budget, and a full read takes 60-90s, so this
# script only LAUNCHES a detached child and exits. The child writes
# notes/daily-blog/pending.md; the SessionStart hook prints it next day.
#
# Guard order matters: the recursion guard must come first. Without it the
# spawned `claude -p` child fires its own SessionEnd, spawning another child,
# unattended, forever.
set -u

PROJECT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
STATE_DIR="$PROJECT/notes/daily-blog"
PENDING="$STATE_DIR/pending.md"
STATE="$STATE_DIR/.state.json"
LOG="$STATE_DIR/.queue.log"
TODAY="$(date +%Y-%m-%d)"

# 1. Recursion guard. Verified: a headless `claude -p` child reports
#    CLAUDE_CODE_CHILD_SESSION=true; an interactive session leaves it unset.
[ "${CLAUDE_CODE_CHILD_SESSION:-}" = "true" ] && exit 0

# 2. Interactive sessions only. Verified: headless reports mcp-stdio-cli.
[ "${CLAUDE_CODE_ENTRYPOINT:-cli}" != "cli" ] && exit 0

# 3. A finished read is already waiting -> nothing to do.
[ -f "$PENDING" ] && exit 0

# 4. Once per day, not once per session. SessionEnd fires on every session exit.
if [ -f "$STATE" ] && grep -q "\"prepared\"[[:space:]]*:[[:space:]]*\"$TODAY\"" "$STATE" 2>/dev/null; then
  exit 0
fi

mkdir -p "$STATE_DIR" || exit 0

# Record the attempt BEFORE spawning: if the detached child dies (undocumented
# whether Claude Code kills the process group), the SessionStart hook sees a
# prepared date with no pending.md and reports the failure instead of silently
# doing nothing.
if [ -f "$STATE" ]; then
  python - "$STATE" "$TODAY" <<'PY' 2>/dev/null || true
import json, sys
p, today = sys.argv[1], sys.argv[2]
try:
    d = json.load(open(p, encoding="utf-8"))
except Exception:
    d = {}
d["prepared"] = today
json.dump(d, open(p, "w", encoding="utf-8"), indent=2)
PY
else
  printf '{\n  "seen": [],\n  "shown": "",\n  "prepared": "%s"\n}\n' "$TODAY" > "$STATE"
fi

PROMPT='Run the daily-blog skill in prepare mode: pick one worth-reading post from skills/daily-blog/assets/feeds.json and read it at full fidelity, writing notes/daily-blog/pending.md. Follow the skill body exactly.'

echo "[$(date +%H:%M:%S)] queueing prepare for $TODAY" >> "$LOG"

# Detached spawn. setsid does NOT exist in Git Bash on Windows -- a POSIX
# detach there silently spawns nothing, so branch on what actually exists.
if command -v setsid >/dev/null 2>&1; then
  setsid nohup claude -p "$PROMPT" >> "$LOG" 2>&1 < /dev/null &
elif command -v powershell >/dev/null 2>&1; then
  WINPROJ="$(cygpath -w "$PROJECT" 2>/dev/null || echo "$PROJECT")"
  powershell -NoProfile -NonInteractive -Command \
    "Start-Process -WindowStyle Hidden -FilePath 'claude' \
     -ArgumentList '-p','$PROMPT' -WorkingDirectory '$WINPROJ'" \
    >> "$LOG" 2>&1
else
  nohup claude -p "$PROMPT" >> "$LOG" 2>&1 < /dev/null &
fi

exit 0
