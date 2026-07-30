#!/usr/bin/env bash
# SessionStart hook (matcher: startup): print the day's finished blog read.
#
# SessionStart BLOCKS the user's first prompt until this script exits, so this
# does file operations only -- no network, no agent, no skill invocation. stdout
# is injected into the session context.
#
# Prints at most once per day: the first session of the day shows the read and
# stamps `shown`; later sessions exit silently.
set -u

PROJECT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
STATE_DIR="$PROJECT/notes/daily-blog"
PENDING="$STATE_DIR/pending.md"
STATE="$STATE_DIR/.state.json"
TODAY="$(date +%Y-%m-%d)"

[ -d "$STATE_DIR" ] || exit 0

# Already shown today -> stay quiet. This is the once-a-day gate.
if [ -f "$STATE" ] && grep -q "\"shown\"[[:space:]]*:[[:space:]]*\"$TODAY\"" "$STATE" 2>/dev/null; then
  exit 0
fi

if [ ! -f "$PENDING" ]; then
  # Staleness fallback: a prepare was attempted but produced nothing, which
  # means the detached child died (process-group survival past session exit is
  # undocumented). Report it in one line rather than failing silently -- an
  # invisible failure is the worst outcome for a background feature.
  if [ -f "$STATE" ] \
     && grep -q "\"prepared\"" "$STATE" 2>/dev/null \
     && ! grep -q "\"prepared\"[[:space:]]*:[[:space:]]*\"\"" "$STATE" 2>/dev/null \
     && ! ls "$STATE_DIR"/[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].md >/dev/null 2>&1; then
    echo "daily-blog: last prepare produced no read (detached child may have been killed). Run: /daily-blog prepare"
  fi
  exit 0
fi

cat "$PENDING"

# Rotate into the dated archive, then stamp shown so later sessions stay quiet.
mv "$PENDING" "$STATE_DIR/$TODAY.md" 2>/dev/null || true

python - "$STATE" "$TODAY" <<'PY' 2>/dev/null || true
import json, sys
p, today = sys.argv[1], sys.argv[2]
try:
    d = json.load(open(p, encoding="utf-8"))
except Exception:
    d = {"seen": [], "prepared": ""}
d["shown"] = today
json.dump(d, open(p, "w", encoding="utf-8"), indent=2)
PY

exit 0
