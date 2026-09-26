# Auditing hooks

## Inventory
Three wiring sources, all load together:
1. `settings.json` `hooks` (user/project/local tiers)
2. a plugin's `hooks/hooks.json` — **auto-discovered from the plugin root**
3. a plugin manifest's inline `hooks` block (`.claude-plugin/plugin.json`)

Enumerate the actual handler scripts too (`hooks/*.sh`) and diff them against
what's wired — an unwired script is dead; a wired-but-missing script errors.

## The double-fire trap — pair-specific, so check the logs
`hooks/hooks.json` and the manifest `hooks` key **both load** — the manifest is
additive, not a replacement (verified: an official plugin whose manifest has no
`hooks` key still runs its hooks.json). Whether a hook wired twice *fires* twice
depends on WHICH two sources, so don't assume — confirm empirically:

- **manifest `hooks` block ↔ plugin `hooks/hooks.json`:** DOUBLE-FIRES. Observed —
  a handler in both logged **two lines per single `Stop`**. Dedup is documented
  only *across settings files*, not within a plugin. (The two command strings even
  differed textually — `bash "${ROOT}/x.sh"` vs bare `${ROOT}/x.sh` — so
  string-equality dedup wouldn't collapse them regardless.) **Fix:** one source;
  empty the manifest block, then **bump the plugin version** or the cache serves
  the old double-wired copy.
- **`settings.json` ↔ plugin `hooks/hooks.json`:** observed **single-fire** — a
  handler wired in both settings.json and an enabled plugin's hooks.json logged
  ONE line per event (checked `output-length.log`, `mcp-audit.log`: no duplicate
  timestamps). So the harness appears to dedup settings↔plugin, or one wiring is
  dormant. Still redundant/confusing (and a maintenance trap), so **merge to one
  source** — but it's not a live double-fire; classify it `merge`, not a bug.

**Rule: verify fire-count from a handler's own log before calling dual wiring a
double-fire.** Only the manifest↔hooks.json pair is a confirmed doubler.
- **Verify empirically** on the version actually loaded (not the edited tree):
  instrument a handler to append one line per call, trigger the event, count. A
  zero-count usually means you instrumented a version the running cache hasn't
  loaded — run the script manually to prove the probe works, then instrument the
  loaded version.

## Per-event exit-code contracts
Exit 2 means different things per event. Auditing a hook = checking it honors its
event's contract:

- **Guards** (`PreToolUse`, `PreModelSwitch`): exit 2 = block-and-ask.
  Pass-through must `exit 0` silently. Never emit `{"decision":"allow"}` — that's
  real auto-approval and skips the permission prompt. A `PreToolUse` JSON decision
  must nest under `hookSpecificOutput.permissionDecision`; a bare top-level
  `{"decision":"block"}` is silently ignored.
- **Loggers** (`Stop`, `PreCompact`, `SubagentStop`, `PostToolUse*`,
  `ConfigChange`, `SessionStart`): exit 2 either **blocks the event** (e.g.
  PreCompact blocks compaction; Stop blocks the turn ending) or is a documented
  no-op. Either way a logger must **always `exit 0`**, even on parse failure.

## Recurring hook bugs to flag
- **No named escape.** A hook that exits 2 must print, to stderr, an escape that
  actually reaches the user's goal — and it must be reachable. Classic failures: a
  block with no confirm path (blocks forever); a message steering to a more
  expensive path than needed. Test the path the user takes *after* reading the
  message, not just the block.
- **`set -e` in a logger.** `set -euo pipefail` makes any non-zero command abort
  the script with that code — and on a logger event a non-zero exit **blocks the
  turn.** The classic trip is `grep`: exit 1 on no-match, 2 on error — a routine
  "not found" check aborts the whole hook. Loggers must not use `set -e`; guard
  risky commands explicitly (`grep ... || true`).
- **Wrong root var.** `$CLAUDE_PROJECT_DIR` resolves to whatever project the user
  is in — a plugin hook must use `${CLAUDE_PLUGIN_ROOT}` or it breaks outside its
  own repo.
- **Guessed payload field.** A hook reading a field the event doesn't carry writes
  empty rows that look like legitimate zeros. Capture a real payload before
  trusting a field name (some events carry no cost/duration/turn data at all).
- **Symlink install wires nothing.** An `install.sh` that only symlinks
  skills/commands/agents into `~/.claude/` does NOT wire hooks — hooks.json
  auto-discovery is a *plugin* load, not a symlink load. On such a machine, guards
  don't run unless added to that machine's `settings.json`. Flag this gap.

## Token efficiency
- A context-injecting hook (`UserPromptSubmit`/`SessionStart` writing
  `additionalContext`) costs tokens every turn it fires. Measure before keeping:
  if it fires rarely or its instruction is already in the system prompt, it's
  paying rent for nothing. A SessionStart ruleset (high salience) beats a
  per-turn conversation injection that competes at ordinary salience and loses to
  accumulated history.
- Loggers cost ~nothing in context (they write to disk); their cost is latency —
  keep slow ones (`claude mcp list` shell-outs) async and bounded with `timeout`.

## Enhancement
- A repeatedly-done manual safety check (confirm-before-delete, format-on-save)
  with no hook → propose one, wired in ONE source, with a named escape.
- A guard that only blocks without teaching the escape → add the escape to stderr.
- A measurement gap: no logger for a behavior the user cares about (output length,
  tool failures, MCP health) → propose a Stop/PostToolUseFailure/SessionStart
  logger (always exit 0).

## Verify
Run `test-hooks.sh` (or the repo's hook regression suite) after any wiring change;
`bash -n` every generated handler; run each with empty AND malformed stdin and
confirm `exit 0` for loggers.
