#!/usr/bin/env bash
# PreToolUse guard: block obviously destructive bash commands. Exit 2 = block.
payload=$(cat)
# Windows Store ships a python3 stub that prints an error yet exits 0 — test output, not exit code.
PY=python3; [ "$(python3 -c 'print(1)' 2>/dev/null)" = "1" ] || PY=python
cmd=$(printf '%s' "$payload" | "$PY" -c "import json,sys; print(json.load(sys.stdin).get('tool_input',{}).get('command',''))" 2>/dev/null | tr -d '\r')
[ -z "$cmd" ] && exit 0

block() { echo "blocked by guard-dangerous.sh: $1" >&2; exit 2; }

# Recursive deletes of an absolute path or home. Relative paths are left alone:
# `rm -rf ./build` is routine, and blocking it would train the guard into noise.
case "$cmd" in
  *"rm -rf /"*|*"rm -rf ~"*|*'rm -rf $HOME'*|*'rm -rf "$HOME"'*|*"rm -fr /"*|*"rm -fr ~"*)
    block "recursive delete of an absolute path -- use a path relative to the working dir (rm -rf ./build), or cd into the parent first" ;;
  *":(){ :|:& };:"*)
    block "fork bomb -- no escape; this is never a legitimate command here" ;;
esac

# Destructive SQL. Read-only tools that merely mention the keywords (grep, rg,
# ack) are searching for the text, not executing it.
case "$cmd" in
  grep\ *|rg\ *|ack\ *|ag\ *|*[\;\&\|]\ grep\ *|*[\;\&\|]\ rg\ *) ;;
  *"DROP TABLE"*|*"DROP DATABASE"*|*"DROP SCHEMA"*|*"TRUNCATE "*)
    block "destructive SQL -- point it at a scratch/test database explicitly, or wrap it in a transaction you can roll back" ;;
esac

# Raw device writes. Anchored to command position (start, or after ;/&/|) so
# prose mentioning "mkfs" or "dd if=" in a commit message, comment, or grep
# pattern doesn't trip it — only actually invoking the tool does.
case "$cmd" in
  mkfs*|*[\;\&\|]\ mkfs*)
    block "raw device write -- target a regular file instead (of=./image.img); writing to /dev/* destroys the device" ;;
esac
case "$cmd" in
  dd\ *|*[\;\&\|]\ dd\ *)
    case "$cmd" in
      *"of=/dev/"*) block "raw device write -- target a regular file instead (of=./image.img); writing to /dev/* destroys the device" ;;
    esac ;;
esac
case "$cmd" in
  *"> /dev/sd"*|*"> /dev/nvme"*)
    block "raw device write -- target a regular file instead (of=./image.img); writing to /dev/* destroys the device" ;;
esac

# Git history/work destruction. Matched only when the command actually starts a
# git invocation, so prose and paths containing these words don't trip it.
case "$cmd" in
  git\ *|*[\;\&\|]\ git\ *|*"&&"\ git\ *)
    case "$cmd" in
      *"push --force-with-lease"*|*"push --force-if-includes"*) ;;  # safe forms: refuse if the remote moved
      *"push --force"*|*"push -f"*|*"push "*"--delete"*|*"push "*" +"*)
        block "force push or remote branch delete -- use --force-with-lease (refuses if the remote moved), or push to a new branch name" ;;
      *"reset --hard"*)
        block "git reset --hard discards uncommitted work -- commit or stash first; use git restore <path> for a single file" ;;
      *"clean -"*[fdx]*)
        block "git clean deletes untracked files -- run it with -n first to list what would go, then remove those paths deliberately" ;;
      *"checkout -- "*|*"restore --staged --worktree"*|*"restore ."*)
        block "git checkout/restore discards local changes -- stash first, or name the single path instead of a wildcard" ;;
      *"branch -D"*)
        block "force branch delete -- use git branch -d (refuses if unmerged); if it is merged elsewhere, record the SHA from git log first" ;;
      *"filter-branch"*|*"reflog expire"*|*"gc --prune=now"*)
        block "history rewrite / reflog destruction -- create a backup branch first so the old history stays reachable" ;;
    esac ;;
esac

exit 0
