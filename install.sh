#!/usr/bin/env bash
# Symlink fallback for non-plugin consumption.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
link() { mkdir -p "$2"; for p in "$1"/*; do [ -e "$p" ] || continue; b=$(basename "$p"); [ "$b" = ".gitkeep" ] && continue; t="$2/$b"; [ -e "$t" ] && { echo "skip (exists): $t"; continue; }; ln -s "$p" "$t"; echo "linked $t"; done; }
link "$ROOT/skills"   "$HOME/.claude/skills"
link "$ROOT/commands" "$HOME/.claude/commands"
link "$ROOT/agents"   "$HOME/.claude/agents"
echo "done"
