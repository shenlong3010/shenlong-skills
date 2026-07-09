#!/usr/bin/env bash
# Stop hook: desktop/terminal notification when a long task finishes.
msg="Claude session finished: $(basename "${CLAUDE_PROJECT_DIR:-$PWD}")"
command -v osascript >/dev/null && osascript -e "display notification \"$msg\"" && exit 0
command -v notify-send >/dev/null && notify-send "$msg" && exit 0
printf '\a%s\n' "$msg"
