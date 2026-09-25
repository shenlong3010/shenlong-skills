#!/usr/bin/env bash
# Full hook regression suite. Every hook, real payloads + edge cases.
# Asserts exit code AND (where applicable) that a log line landed.
#
# Usage:
#   bash test-hooks.sh                 # tests hooks in this directory
#   HOOKS_DIR=~/.claude/hooks bash …   # tests an installed copy instead
#
# NOTE: the logger tests append real rows to ~/.claude/*.log. Snapshot line
# counts before running and truncate back afterward if you care about keeping
# those logs clean -- the suite does not do it for you, because guessing which
# rows were yours risks deleting real ones.
H="${HOOKS_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
PASS=0; FAIL=0
SANDBOX="$(mktemp -d)"
trap 'rm -rf "$SANDBOX"' EXIT

ok()   { PASS=$((PASS+1)); printf '  PASS  %s\n' "$1"; }
bad()  { FAIL=$((FAIL+1)); printf '  FAIL  %s  (%s)\n' "$1" "$2"; }

# run <name> <script> <payload> <expected_rc>
run() {
  local name=$1 script=$2 payload=$3 want=$4
  local got
  printf '%s' "$payload" | bash "$H/$script" >/dev/null 2>&1
  got=$?
  [ "$got" = "$want" ] && ok "$name" || bad "$name" "rc=$got want=$want"
}

# run_out <name> <script> <payload> <expected_rc> <grep_pattern_in_stdout_or_stderr>
run_out() {
  local name=$1 script=$2 payload=$3 want=$4 pat=$5
  local out got
  out=$(printf '%s' "$payload" | bash "$H/$script" 2>&1)
  got=$?
  if [ "$got" != "$want" ]; then bad "$name" "rc=$got want=$want"; return; fi
  if printf '%s' "$out" | grep -q "$pat"; then ok "$name"; else bad "$name" "missing /$pat/"; fi
}

echo "=== syntax: all hooks ==="
for f in "$H"/*.sh; do
  [ "$(basename "$f")" = "test-hooks.sh" ] && continue
  bash -n "$f" 2>/dev/null && ok "syntax $(basename "$f")" || bad "syntax $(basename "$f")" "parse error"
done

echo
echo "=== guard-dangerous.sh (PreToolUse Bash) ==="
run_out "blocks rm -rf /"        guard-dangerous.sh '{"tool_input":{"command":"rm -rf /"}}'                    2 "recursive delete"
run_out "blocks fork bomb"       guard-dangerous.sh '{"tool_input":{"command":":(){ :|:& };:"}}'               2 "fork bomb"
run_out "blocks git push -f"     guard-dangerous.sh '{"tool_input":{"command":"git push -f origin main"}}'      2 "force push"
run_out "blocks reset --hard"    guard-dangerous.sh '{"tool_input":{"command":"git reset --hard HEAD~1"}}'      2 "reset --hard"
run_out "blocks DROP TABLE"      guard-dangerous.sh '{"tool_input":{"command":"psql -c \"DROP TABLE users\""}}' 2 "destructive SQL"
run     "allows grep DROP TABLE" guard-dangerous.sh '{"tool_input":{"command":"grep -r \"DROP TABLE\" src/"}}'  0
run     "allows normal ls"       guard-dangerous.sh '{"tool_input":{"command":"ls -la"}}'                       0
run     "allows git status"      guard-dangerous.sh '{"tool_input":{"command":"git status"}}'                   0
run     "allows rm single file"  guard-dangerous.sh '{"tool_input":{"command":"rm foo.txt"}}'                   0
run     "malformed json"         guard-dangerous.sh 'not json'                                                 0
run     "empty payload"          guard-dangerous.sh '{}'                                                       0

echo
echo "=== guard-bulk-read.sh (PreToolUse Read) ==="
BIG="$SANDBOX/big.txt";   seq 1 500 > "$BIG"
SMALL="$SANDBOX/small.txt"; seq 1 10 > "$SMALL"
SPACED="$SANDBOX/with space.txt"; seq 1 500 > "$SPACED"
run_out "blocks 500-line read"   guard-bulk-read.sh "{\"tool_input\":{\"file_path\":\"$BIG\"}}"                  2 "Escapes, cheapest first"
run     "allows offset/limit"    guard-bulk-read.sh "{\"tool_input\":{\"file_path\":\"$BIG\",\"offset\":1,\"limit\":50}}" 0
run     "allows small file"      guard-bulk-read.sh "{\"tool_input\":{\"file_path\":\"$SMALL\"}}"                0
run     "allows missing file"    guard-bulk-read.sh '{"tool_input":{"file_path":"/nope/gone.txt"}}'              0
run_out "blocks path w/ space"   guard-bulk-read.sh "{\"tool_input\":{\"file_path\":\"$SPACED\"}}"               2 "Escapes"
run     "malformed json"         guard-bulk-read.sh 'not json'                                                  0
run     "no file_path"           guard-bulk-read.sh '{"tool_input":{}}'                                         0

echo
echo "=== guard-bulk-cat.sh (PreToolUse Bash) ==="
run_out "blocks cat big"         guard-bulk-cat.sh "{\"tool_input\":{\"command\":\"cat $BIG\"}}"                 2 "head -N"
run     "ALLOWS head -50"        guard-bulk-cat.sh "{\"tool_input\":{\"command\":\"head -50 $BIG\"}}"            0
run     "ALLOWS tail -20"        guard-bulk-cat.sh "{\"tool_input\":{\"command\":\"tail -20 $BIG\"}}"            0
run     "ALLOWS head no flag"    guard-bulk-cat.sh "{\"tool_input\":{\"command\":\"head $BIG\"}}"                0
run_out "blocks less"            guard-bulk-cat.sh "{\"tool_input\":{\"command\":\"less $BIG\"}}"                2 "Escapes"
run     "allows cat | grep"      guard-bulk-cat.sh "{\"tool_input\":{\"command\":\"cat $BIG | grep 42\"}}"       0
run     "allows cat > out"       guard-bulk-cat.sh "{\"tool_input\":{\"command\":\"cat $BIG > /tmp/o\"}}"        0
run     "allows cat small"       guard-bulk-cat.sh "{\"tool_input\":{\"command\":\"cat $SMALL\"}}"               0
run     "allows non-read cmd"    guard-bulk-cat.sh '{"tool_input":{"command":"echo hello"}}'                     0
run     "malformed json"         guard-bulk-cat.sh 'not json'                                                    0

echo
echo "=== guard-model-switch.sh (PreModelSwitch) ==="
SD="$HOME/.claude/.model-switch-state"; mkdir -p "$SD"
rm -f "$SD/TESTSESS" "$SD/confirm_TESTSESS"*
run "1st switch suppressed"      guard-model-switch.sh '{"from_model":"a","to_model":"b","session_id":"TESTSESS"}' 0
run_out "2nd switch blocks"      guard-model-switch.sh '{"from_model":"a","to_model":"b","session_id":"TESTSESS"}' 2 "again within 5 minutes"
run "3rd same target confirms"   guard-model-switch.sh '{"from_model":"a","to_model":"b","session_id":"TESTSESS"}' 0
run_out "4th re-blocks"          guard-model-switch.sh '{"from_model":"a","to_model":"b","session_id":"TESTSESS"}' 2 "cache"
run_out "diff target blocks"     guard-model-switch.sh '{"from_model":"a","to_model":"c","session_id":"TESTSESS"}' 2 "cache"
run "same from/to no-op"         guard-model-switch.sh '{"from_model":"a","to_model":"a","session_id":"TESTSESS"}' 0
run "missing to_model"           guard-model-switch.sh '{"from_model":"a","session_id":"TESTSESS"}'               0
run "malformed json"             guard-model-switch.sh 'not json'                                                 0
rm -f "$SD/TESTSESS" "$SD/confirm_TESTSESS"*

echo
echo "=== loggers: exit 0 on everything + write a line ==="
# log-tool-failure
L="$HOME/.claude/tool-failures.log"; before=$(wc -l < "$L" 2>/dev/null || echo 0)
run "log-tool-failure valid"     log-tool-failure.sh '{"tool_name":"Bash","error":"boom"}'                        0
after=$(wc -l < "$L" 2>/dev/null || echo 0)
[ "$after" -gt "$before" ] && ok "log-tool-failure wrote line" || bad "log-tool-failure wrote line" "no new line"
run "log-tool-failure malformed" log-tool-failure.sh 'not json'                                                   0
run "log-tool-failure empty"     log-tool-failure.sh '{}'                                                         0

# log-subagent-stop
L="$HOME/.claude/subagent.log"; before=$(wc -l < "$L" 2>/dev/null || echo 0)
run "log-subagent valid"         log-subagent-stop.sh '{"agent_type":"Explore","agent_id":"a1","last_assistant_message":"done"}' 0
after=$(wc -l < "$L" 2>/dev/null || echo 0)
[ "$after" -gt "$before" ] && ok "log-subagent wrote line" || bad "log-subagent wrote line" "no new line"
run "log-subagent malformed"     log-subagent-stop.sh 'not json'                                                  0
run "log-subagent empty"         log-subagent-stop.sh '{}'                                                        0

# snapshot-precompact
L="$HOME/.claude/compact.log"; before=$(wc -l < "$L" 2>/dev/null || echo 0)
run "precompact valid"           snapshot-precompact.sh '{"trigger":"manual","cwd":"/x","session_id":"s"}'        0
after=$(wc -l < "$L" 2>/dev/null || echo 0)
[ "$after" -gt "$before" ] && ok "precompact wrote line" || bad "precompact wrote line" "no new line"
run "precompact malformed"       snapshot-precompact.sh 'not json'                                                0
run "precompact empty"           snapshot-precompact.sh '{}'                                                      0

# log-config-change
L="$HOME/.claude/config-change.log"; before=$(wc -l < "$L" 2>/dev/null || echo 0)
run "config-change valid"        log-config-change.sh '{"source":"user_settings"}'                                0
after=$(wc -l < "$L" 2>/dev/null || echo 0)
[ "$after" -gt "$before" ] && ok "config-change wrote line" || bad "config-change wrote line" "no new line"
run "config-change malformed"    log-config-change.sh 'not json'                                                  0

# measure-output-length
L="$HOME/.claude/output-length.log"; before=$(wc -l < "$L" 2>/dev/null || echo 0)
run "measure valid"              measure-output-length.sh '{"session_id":"s","last_assistant_message":"Bug in auth. Fixed."}' 0
after=$(wc -l < "$L" 2>/dev/null || echo 0)
[ "$after" -gt "$before" ] && ok "measure wrote line" || bad "measure wrote line" "no new line"
run "measure malformed"          measure-output-length.sh 'not json'                                              0
run "measure empty msg"          measure-output-length.sh '{"last_assistant_message":""}'                         0
run "measure no field"           measure-output-length.sh '{}'                                                    0

# cost-logger: retired 2026-09-25 (Stop carries no usable cost data; 227 of
# 231 post-rewrite rows were empty). Deliberately no test — the hook is gone.

# autoformat (no formatter for .xyz => must still exit 0)
run "autoformat unknown ext"     autoformat.sh "{\"tool_input\":{\"file_path\":\"$SANDBOX/x.xyz\"}}"              0
run "autoformat malformed"       autoformat.sh 'not json'                                                         0
run "autoformat no path"         autoformat.sh '{"tool_input":{}}'                                                0

# notify (Stop): best-effort notifier, must never block a turn from ending.
# Skipped when testing an installed copy that doesn't ship it.
if [ -f "$H/notify.sh" ]; then
  run "notify valid"             notify.sh '{"session_id":"s","last_assistant_message":"done"}'                    0
  run "notify malformed"         notify.sh 'not json'                                                              0
  run "notify empty"             notify.sh '{}'                                                                    0
fi

echo
echo "=== audit-mcp-startup.sh (slow: real claude mcp list) ==="
L="$HOME/.claude/mcp-audit.log"; before=$(wc -l < "$L" 2>/dev/null || echo 0)
run "mcp-audit valid"            audit-mcp-startup.sh '{"cwd":"/c/test","session_id":"s"}'                        0
after=$(wc -l < "$L" 2>/dev/null || echo 0)
[ "$after" -gt "$before" ] && ok "mcp-audit wrote line" || bad "mcp-audit wrote line" "no new line"
tail -1 "$L" | grep -qE '(:\+|:-|:~|:o|TIMEOUT|RUNFAIL)' && ok "mcp-audit real status chars" || bad "mcp-audit real status chars" "no parsed status"

echo
echo "================================"
printf 'PASS %d   FAIL %d\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
