#!/usr/bin/env bash
# Copy this toolbox into a flat ~/.claude/{skills,commands,agents} layout, with an
# optional name prefix — for a machine that cannot install the plugin (marketplace
# blocked) and instead clones the repo and copies the setup over by hand.
#
# WHY a prefix: a plugin namespaces every skill as `shenlong-skills:<name>`, so a
# bare `code-review` never collides with a native/anthropic one. A flat copy into
# ~/.claude/skills/ has NO namespace, so `code-review` there shadows or is shadowed
# by same-named built-ins. `--prefix shenlong-` rewrites the copied dir AND the
# frontmatter `name:` (the field the Skill tool resolves) so the flat copies are
# uniquely addressable. Canonical repo names stay clean — the prefix lives only on
# the copy, so home (plugin/namespaced) is untouched and guard-hook escape strings
# that name a skill keep resolving.
#
# Vendored skills (`derivation: copied`, e.g. crawl4ai) keep their upstream identity
# by repo rule — they are copied WITHOUT the prefix unless --prefix-vendored is given.
#
# Idempotent: re-running re-syncs; existing prefixed copies are overwritten, not
# duplicated. Dry-run by default — pass --apply to actually write.
#
# Usage:
#   bash tools/sync-flat.sh [--prefix P] [--dest DIR] [--include-extra]
#                           [--prefix-vendored] [--apply]
# Defaults: --prefix (none), --dest ~/.claude, dry-run.
set -u
set -o pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

PREFIX=""
DEST="$HOME/.claude"
INCLUDE_EXTRA=0
PREFIX_VENDORED=0
APPLY=0
while [ $# -gt 0 ]; do
  case "$1" in
    --prefix) PREFIX="${2:?--prefix needs a value}"; shift 2 ;;
    --dest) DEST="${2:?--dest needs a value}"; shift 2 ;;
    --include-extra) INCLUDE_EXTRA=1; shift ;;
    --prefix-vendored) PREFIX_VENDORED=1; shift ;;
    --apply) APPLY=1; shift ;;
    -h|--help) sed -n '2,25p' "$0"; exit 0 ;;
    *) echo "sync-flat: unknown arg: $1" >&2; exit 2 ;;
  esac
done

say() { printf '%s\n' "$*"; }
# Rewrite the first `name:` line in a SKILL.md/command/agent .md so the flat copy
# is addressable by its prefixed name. Only the first occurrence (frontmatter).
rewrite_name() {
  # $1 = file, $2 = new name
  awk -v nn="$2" '
    !done && /^name:[[:space:]]/ { sub(/^name:[[:space:]].*/, "name: " nn); done=1 }
    { print }
  ' "$1"
}

is_vendored() { # $1 = SKILL.md path
  grep -q '^derivation: copied' "$1" 2>/dev/null
}

# Copy one skill dir (with SKILL.md + references/assets) applying the prefix.
sync_skill() {
  # $1 = source skill dir, $2 = dest skills dir
  local src="$1" destdir="$2" base name pfx target
  base="$(basename "$src")"
  local skmd="$src/SKILL.md"
  [ -f "$skmd" ] || { say "  skip (no SKILL.md): $base"; return; }
  pfx="$PREFIX"
  if is_vendored "$skmd" && [ "$PREFIX_VENDORED" -eq 0 ]; then
    pfx=""   # vendored keeps upstream identity
  fi
  name="${pfx}${base}"
  target="$destdir/$name"
  say "  $base -> $name"
  [ "$APPLY" -eq 0 ] && return
  rm -rf "$target"; mkdir -p "$target"
  # copy tree, then rewrite the name: field in the copied SKILL.md
  cp -r "$src/." "$target/"
  if [ -n "$pfx" ]; then
    rewrite_name "$target/SKILL.md" "$name" > "$target/SKILL.md.tmp" && mv "$target/SKILL.md.tmp" "$target/SKILL.md"
  fi
}

# Copy one flat .md artifact (command/agent) applying the prefix to filename + name:.
sync_md() {
  # $1 = source .md, $2 = dest dir
  local src="$1" destdir="$2" base name target
  # Skip directory guides — they are repo-internal, not shippable artifacts.
  # Check the real filename BEFORE stripping .md (basename "$f" .md yields "CLAUDE").
  [ "$(basename "$src")" = "CLAUDE.md" ] && return
  base="$(basename "$src" .md)"
  name="${PREFIX}${base}"
  target="$destdir/${name}.md"
  say "  ${base}.md -> ${name}.md"
  [ "$APPLY" -eq 0 ] && return
  mkdir -p "$destdir"
  if [ -n "$PREFIX" ]; then
    rewrite_name "$src" "$name" > "$target"
  else
    cp "$src" "$target"
  fi
}

mode="DRY-RUN (pass --apply to write)"; [ "$APPLY" -eq 1 ] && mode="APPLYING"
say "sync-flat: $mode  prefix='${PREFIX:-<none>}'  dest=$DEST"

say "skills:"
for d in "$ROOT"/skills/*/; do [ -d "$d" ] && sync_skill "$d" "$DEST/skills"; done
if [ "$INCLUDE_EXTRA" -eq 1 ] && [ -d "$ROOT/extra/skills" ]; then
  say "extra/skills:"
  for d in "$ROOT"/extra/skills/*/; do [ -d "$d" ] && sync_skill "$d" "$DEST/skills"; done
fi
say "commands:"
for f in "$ROOT"/commands/*.md; do [ -f "$f" ] && sync_md "$f" "$DEST/commands"; done
say "agents:"
for f in "$ROOT"/agents/*.md; do [ -f "$f" ] && sync_md "$f" "$DEST/agents"; done

say "sync-flat: done ($mode)"
[ "$APPLY" -eq 0 ] && say "Re-run with --apply to write these changes."
exit 0
