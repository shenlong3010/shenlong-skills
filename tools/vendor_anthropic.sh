#!/usr/bin/env bash
# Vendor a skill from anthropics/skills at a pinned commit.
# Usage: tools/vendor_anthropic.sh <path-in-repo> <dest-dir> [ref]
# Reminds you to verify the upstream LICENSE before committing.
set -euo pipefail
[ $# -lt 2 ] && { echo "usage: $0 <path-in-repo> <dest-dir> [ref]"; exit 2; }
SRC="$1"; DEST="$2"; REF="${3:-main}"
SHA=$(curl -fsS "https://api.github.com/repos/anthropics/skills/commits/$REF" | python3 -c "import json,sys;print(json.load(sys.stdin)['sha'])")
mkdir -p "$DEST"
curl -fsS "https://raw.githubusercontent.com/anthropics/skills/$SHA/$SRC" -o "$DEST/$(basename "$SRC")"
echo "vendored $SRC @ $SHA -> $DEST"
echo "NOW: (1) verify upstream LICENSE permits redistribution; (2) add to frontmatter:"
echo "  source: https://github.com/anthropics/skills/blob/$SHA/$SRC"
