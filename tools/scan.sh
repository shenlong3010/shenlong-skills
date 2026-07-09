#!/usr/bin/env bash
# Scans staged changes for secret patterns and local-wordlist terms.
# Prints file:line only — never the matched content.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIFF="$(git -C "$ROOT" diff --cached --unified=0 2>/dev/null || true)"
[ -z "$DIFF" ] && { echo "scan: nothing staged"; exit 0; }
FAIL=0

hits() { # $1 = pattern (extended regex, case-insensitive)
  echo "$DIFF" | awk -v pat="$1" '
    /^\+\+\+ b\// { file=substr($0,7) }
    /^@@/ { split($3,a,","); gsub(/^\+/,"",a[1]); line=a[1]-1 }
    /^\+/ && !/^\+\+\+/ { line++; if (tolower($0) ~ tolower(pat)) print file ":" line }
    /^[^+@-]/ { line++ }'
}

SECRET_PATTERNS='AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----|xox[bap]-[0-9A-Za-z-]+|ghp_[0-9A-Za-z]{36}|(api[_-]?key|secret|token|passwd|password)[[:space:]]*[:=][[:space:]]*["'"'"'][^"'"'"']{8,}'
S=$(hits "$SECRET_PATTERNS")
[ -n "$S" ] && { echo "SECRET pattern hit(s):"; echo "$S"; FAIL=1; }

WL="$ROOT/.wordlist"
if [ -s "$WL" ]; then
  while IFS= read -r term; do
    [ -z "$term" ] && continue
    W=$(hits "$term")
    [ -n "$W" ] && { echo "WORDLIST hit(s):"; echo "$W"; FAIL=1; }
  done < "$WL"
else
  echo "scan: WARNING — .wordlist missing or empty; wordlist half of the scan is vacuous"
fi

[ "$FAIL" -eq 1 ] && { echo "scan: BLOCKED"; exit 1; }
echo "scan: clean"
