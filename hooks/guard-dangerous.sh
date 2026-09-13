#!/usr/bin/env bash
# PreToolUse guard: block obviously destructive bash commands. Exit 2 = block.
#
# ADVISORY, NOT A SECURITY BOUNDARY. This is a fixed-substring denylist and is
# fail-open by construction: whitespace variants (rm  -rf  ~), flag reordering
# (rm --recursive --force /), indirection (X=rf; rm -$X /), and any obfuscation
# the shell resolves at runtime but this matcher does not see will pass. A JSON
# parse failure also fails open (empty cmd -> no match -> exit 0). Treat it as a
# speed-bump that catches accidents, never as the control that makes destructive
# commands safe — reversibility discipline (CLAUDE.md rule 11) is the real guard.
# Hardening tracked in .agents/BACKLOG.md (guard-dangerous standing-landmines story).
payload=$(cat)
# Windows Store ships a python3 stub that prints an error yet exits 0 — test output, not exit code.
PY=python3; [ "$(python3 -c 'print(1)' 2>/dev/null)" = "1" ] || PY=python
# Python on Windows emits CRLF; a trailing \r makes every comparison below miss.
cmd=$(printf '%s' "$payload" | "$PY" -c "import json,sys; print(json.load(sys.stdin).get('tool_input',{}).get('command',''))" 2>/dev/null | tr -d '\r')
[ -z "$cmd" ] && exit 0

block() { echo "blocked by guard-dangerous.sh: $1" >&2; exit 2; }

# Recursive deletes of an absolute path or home. Relative paths are deliberately
# left alone: `rm -rf ./build` is routine, and blocking it trains the guard into
# noise that gets disabled.
case "$cmd" in
  *"rm -rf /"*|*"rm -rf ~"*|*'rm -rf $HOME'*|*'rm -rf "$HOME"'*|*"rm -fr /"*|*"rm -fr ~"*)
    block "recursive delete of an absolute path" ;;
  *":(){ :|:& };:"*)
    block "fork bomb" ;;
esac

# Destructive SQL. Read-only tools that merely mention the keywords are
# searching for the text, not executing it.
case "$cmd" in
  grep\ *|rg\ *|ack\ *|ag\ *|*[\;\&\|]\ grep\ *|*[\;\&\|]\ rg\ *) ;;
  *"DROP TABLE"*|*"DROP DATABASE"*|*"DROP SCHEMA"*|*"TRUNCATE "*)
    block "destructive SQL" ;;
esac

# Raw device writes. Anchored to command position (start, or after ;/&/|) so
# prose mentioning "mkfs" or "dd if=" in a commit message, comment, or grep
# pattern doesn't trip it — only actually invoking the tool does. (The prior
# *"mkfs"*-style substring match fired on any mention of the word, including
# this hook's own commit messages describing the fix — found 2026-09-13.)
case "$cmd" in
  mkfs*|*[\;\&\|]\ mkfs*)
    block "raw device write" ;;
esac
case "$cmd" in
  dd\ *|*[\;\&\|]\ dd\ *)
    case "$cmd" in
      *"of=/dev/"*) block "raw device write" ;;
    esac ;;
esac
case "$cmd" in
  *"> /dev/sd"*|*"> /dev/nvme"*)
    block "raw device write" ;;
esac

# Git history/work destruction. Gated on the command actually invoking git, so
# prose and paths containing these words don't trip it.
case "$cmd" in
  git\ *|*[\;\&\|]\ git\ *|*"&&"\ git\ *)
    case "$cmd" in
      *"push --force"*|*"push -f"*|*"push "*"--delete"*|*"push "*" +"*)
        block "force push or remote branch delete" ;;
      *"reset --hard"*)
        block "git reset --hard (discards uncommitted work)" ;;
      *"clean -"*[fdx]*)
        block "git clean (deletes untracked files)" ;;
      *"checkout -- "*|*"restore --staged --worktree"*|*"restore ."*)
        block "git checkout/restore discarding local changes" ;;
      *"branch -D"*)
        block "force branch delete" ;;
      *"filter-branch"*|*"reflog expire"*|*"gc --prune=now"*)
        block "history rewrite / reflog destruction" ;;
    esac ;;
esac

exit 0
