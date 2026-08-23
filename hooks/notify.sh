#!/usr/bin/env bash
# Stop hook: desktop notification when a long task finishes.
# Platform lane: macOS osascript → Linux notify-send → everything else (incl. Windows
# under Git Bash) falls through to the terminal bell. No native Windows toast lane —
# WinRT toasts from a hidden hook process are flaky; add one only if verified live.
msg="Claude session finished: $(basename "${CLAUDE_PROJECT_DIR:-$PWD}")"
command -v osascript >/dev/null && osascript -e "display notification \"$msg\"" && exit 0
command -v notify-send >/dev/null && notify-send "$msg" && exit 0
printf '\a%s\n' "$msg"
