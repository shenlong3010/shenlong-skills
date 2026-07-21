#!/usr/bin/env bash
# Scans staged changes for secret patterns and local-wordlist terms.
# Prints file:line only — never the matched content.
set -u
set -o pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if ! DIFF="$(git -C "$ROOT" diff --cached --unified=0 2>/dev/null)"; then
  echo "scan: git diff failed — failing closed" >&2; exit 2
fi
[ -z "$DIFF" ] && { echo "scan: nothing staged"; exit 0; }
FAIL=0

# $1 = pattern, $2 = mode ("regex" for the secret patterns, "literal" for
# wordlist terms). Wordlist terms are matched as fixed strings via index() so a
# term containing regex metacharacters (foo(bar, a.b.corp) can never fatally
# error awk and be silently skipped — that was a fail-open on the secret guard.
# printf, not echo, so diff content that looks like an echo flag/escape passes through.
hits() {
  printf '%s\n' "$DIFF" | awk -v pat="$1" -v mode="$2" '
    /^\+\+\+ b\// { file=substr($0,7) }
    /^@@/ { split($3,a,","); gsub(/^\+/,"",a[1]); line=a[1]-1 }
    /^\+/ && !/^\+\+\+/ {
      line++
      hit = (mode == "literal") ? (index(tolower($0), tolower(pat)) > 0) \
                                : (tolower($0) ~ tolower(pat))
      if (hit) print file ":" line
    }
    /^[^+@-]/ { line++ }'
}

SECRET_PATTERNS='AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----|xox[bap]-[0-9A-Za-z-]+|ghp_[0-9A-Za-z]{36}|(api[_-]?key|secret|token|passwd|password)[[:space:]]*[:=][[:space:]]*["'"'"'][^"'"'"']{8,}'
S=$(hits "$SECRET_PATTERNS" regex)
[ -n "$S" ] && { echo "SECRET pattern hit(s):"; echo "$S"; FAIL=1; }

WL="$ROOT/.wordlist"
# Count real (non-blank) terms — a whitespace-only wordlist passes `-s` but
# enforces nothing, so it would report a healthy-but-vacuous scan.
TERMS=0
[ -f "$WL" ] && TERMS=$(grep -cvE '^[[:space:]]*$' "$WL" 2>/dev/null || echo 0)
if [ "$TERMS" -gt 0 ]; then
  while IFS= read -r term; do
    [ -z "$term" ] && continue
    W=$(hits "$term" literal)
    [ -n "$W" ] && { echo "WORDLIST hit(s):"; echo "$W"; FAIL=1; }
  done < "$WL"
else
  echo "scan: WARNING — .wordlist missing or has no non-blank terms; wordlist half of the scan is vacuous"
fi

[ "$FAIL" -eq 1 ] && { echo "scan: BLOCKED"; exit 1; }
echo "scan: clean"
