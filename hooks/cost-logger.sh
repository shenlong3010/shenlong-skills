#!/usr/bin/env bash
# Stop hook: append session metadata to a local usage log for personal spend visibility.
payload=$(cat)
printf '%s\t%s\n' "$(date -Iseconds)" "$payload" >> "${HOME}/.claude/usage.log"
exit 0
