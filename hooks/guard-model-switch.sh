#!/usr/bin/env bash
# PreModelSwitch guard: warn on mid-session model switch (exit 2 = block/ask,
# CONFIRMED real for this event per docs table: "Blocks the model switch and
# prompts the user to confirm" — verified 2026-09-13).
# ADVISORY. Measured 2026-09-13: mid-session switches cost ~1.77M tokens across
# a 33-session sample (cache prefix invalidated). Not blocked outright because
# some switches are the right call — this just forces a deliberate confirm
# instead of a reflexive /model.
#
# Suppresses the warning on the FIRST switch of a session (proxy: nothing
# cached yet worth protecting) so it doesn't fire on routine session-start
# model selection and train the reflex to bypass without reading.
payload=$(cat)
PY=python3; [ "$(python3 -c 'print(1)' 2>/dev/null)" = "1" ] || PY=python
from_model=$(printf '%s' "$payload" | "$PY" -c "import json,sys; print(json.load(sys.stdin).get('from_model',''))" 2>/dev/null | tr -d '\r')
to_model=$(printf '%s' "$payload" | "$PY" -c "import json,sys; print(json.load(sys.stdin).get('to_model',''))" 2>/dev/null | tr -d '\r')
session_id=$(printf '%s' "$payload" | "$PY" -c "import json,sys; print(json.load(sys.stdin).get('session_id',''))" 2>/dev/null | tr -d '\r')
[ -z "$to_model" ] && exit 0
[ "$from_model" = "$to_model" ] && exit 0

state_dir="$HOME/.claude/.model-switch-state"
mkdir -p "$state_dir" 2>/dev/null
# Self-cleaning: prune markers older than 7 days on every invocation, so no
# separate cron/hook is needed to keep this directory bounded.
find "$state_dir" -type f -mtime +7 -delete 2>/dev/null
marker="$state_dir/$session_id"
if [ -n "$session_id" ] && [ ! -f "$marker" ]; then
  touch "$marker" 2>/dev/null
  exit 0
fi

# BUG FIXED 2026-09-17: exit 2 has no "user confirmed, let it through" path —
# re-running /model after seeing the warning re-triggers this same hook and
# blocks again forever, with no way to ever actually switch. Real fix: a
# per-(session,to_model) confirm-marker. First attempt at a given target
# model blocks + drops a marker; a second attempt at the SAME target within
# 5 minutes is treated as the deliberate confirm and let through. A
# different target model (or after 5 min) blocks fresh, so this can't be
# used to silently bypass the warning for an unrelated switch later.
confirm_marker="$state_dir/confirm_${session_id}_${to_model}"
if [ -f "$confirm_marker" ]; then
  now=$(date +%s)
  marker_time=$(date -r "$confirm_marker" +%s 2>/dev/null || stat -c %Y "$confirm_marker" 2>/dev/null)
  if [ -n "$marker_time" ] && [ $((now - marker_time)) -le 300 ]; then
    rm -f "$confirm_marker" 2>/dev/null
    exit 0
  fi
  rm -f "$confirm_marker" 2>/dev/null
fi
touch "$confirm_marker" 2>/dev/null

echo "guard-model-switch: switching $from_model -> $to_model mid-session breaks the prompt cache prefix (measured ~1.77M tokens/33 sessions from this exact action). Confirm this switch is worth the cache-break cost, or set the model before starting instead. Run the same /model command again within 5 minutes to confirm and proceed." >&2
exit 2
