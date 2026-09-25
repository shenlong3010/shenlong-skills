# Hooks

Starter lifecycle hooks. Copy the script per project, wire it in `hooks.json` (or project `.claude/settings.json`), `chmod +x` the script. Hook events receive a JSON payload on stdin; a PreToolUse hook exiting 2 blocks the tool call.

**Platform lane (read before wiring on Windows).** These handlers are POSIX bash. On macOS/Linux they run as-is. On native Windows, Claude Code executes the hook `command` through whatever shell resolves it — a bare `.sh` path does not run under cmd/PowerShell, so without Git Bash on PATH these are **wired-but-dead** (the exact failure mode the retired pair below died of). Verify before trusting: `bash -c 'echo ok'`. If that fails, either install Git Bash or port the handler to `.ps1`; do not leave silent wiring. `notify.sh` additionally has no native Windows toast lane — its bell fallback is the documented behavior there; `cost-logger.sh` and `guard-dangerous.sh` need a real `python3`/`python` on PATH (the Store python3-stub workaround is in-script).

## `guard-bulk-read.sh` / `guard-bulk-cat.sh`

`PreToolUse` on `Read` (guard-bulk-read.sh) and `Bash` (guard-bulk-cat.sh,
covering `cat`/`head`/`tail`/`less`/`more`). Block whole-file reads over
~400 lines and point at this plugin's `bulk-reader` skill: delegate to a
Haiku subagent via the `Agent` tool instead of reading the file directly in
the caller's own context. Same pattern, `code-writer` skill, for boilerplate
generation.

Measured on the home machine 2026-09-13: delegating costs *more* raw tokens
than a direct read (subagent overhead), but wins decisively in dollar terms
when the caller model is Opus (~19x cheaper net) since only the subagent's
short answer lands in the caller's expensive context. On a cheap caller model
this hook is a net loss — if porting to a setup that defaults to Haiku/Sonnet
throughout, reconsider the threshold or disable these two.

Wiring (`hooks.json`, already applied in this repo):

```json
"PreToolUse": [
  { "matcher": "Bash", "hooks": [
    { "type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/hooks/guard-dangerous.sh" },
    { "type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/hooks/guard-bulk-cat.sh" }
  ] },
  { "matcher": "Read", "hooks": [ { "type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/hooks/guard-bulk-read.sh" } ] }
]
```

`guard-bulk-cat.sh` word-splits its command args to find the target file —
uses `xargs -n1`, not `eval`, to avoid command-injection risk from a crafted
path containing `$(...)`. Both scripts pipe any Python-sourced value through
`tr -d '\r'` (Windows Python emits CRLF; an unstripped `\r` breaks every
downstream string comparison silently).

**Bug fixed 2026-09-17 — the guard blocked its own recommended escape.**
`head -50 big.log` reads 50 lines; it *is* the cheap bounded read this hook
exists to steer toward. It was being blocked identically to a bare `cat`,
and the block message read "instead of cat/head/tail" — actively steering
work away from the correct answer and toward spawning a subagent to read 50
lines. `head`/`tail` now exit 0 unconditionally (every invocation is bounded,
defaulting to 10 lines with no flag); `cat`/`less`/`more` still block.

Both guards' block messages now enumerate every real escape, cheapest first
— `offset`/`limit` or `head -N`/`tail -N`, then `grep`, then the subagent,
plus the `BULK_READ_MIN_LINES` env override — instead of naming only the
most expensive option. **General rule this produced:** a hook that exits 2
must name a working escape in its stderr, and that escape must actually be
reachable. Test the path a user takes *after* reading the message, not just
that the block fires. Two hooks in this directory failed that test on first
real use (this one, and `guard-model-switch.sh`); both looked correct in
isolation.

## `guard-model-switch.sh`

`PreModelSwitch`. Warns (exit 2 = confirmed block-and-ask for this event,
verified against docs, not assumed) on a mid-session `/model` switch — each
one invalidates the prompt cache prefix built so far. Measured on the home
machine 2026-09-13: ~1.77M tokens/33 sessions attributable to mid-session
switches specifically.

Suppressed on a session's *first* switch (a marker file keyed on
`session_id` under `~/.claude/.model-switch-state/`) so routine session-start
model selection doesn't get warned and train a reflexive "just click through
it" habit that would defeat the warning on the switches that actually matter.
The script self-prunes markers older than 7 days on every invocation — no
separate cleanup hook needed.

**Bug fixed 2026-09-17:** exit 2 has no built-in "user confirmed, proceed"
signal — re-running `/model <target>` after seeing the warning just
re-triggers this same hook and blocks again, with no way to ever actually
switch. Found live: a real `/model opus` attempt stayed blocked on every
retry. Fixed with a per-`(session_id, to_model)` confirm-marker: the block
that shows the warning also drops a marker; running the *same* `/model
<target>` again within 5 minutes reads that marker and lets the switch
through once. A different target model, or waiting past 5 minutes, blocks
fresh — so this can't be used to silently bypass the warning for an
unrelated later switch. Tested against 4 real scenarios (first-switch
suppress, block, confirm-through, re-block-after-consumed) plus malformed
JSON and missing-`session_id` payloads before shipping.

## `audit-mcp-startup.sh`

`SessionStart`, **must stay wired with `"async": true`**. Shells out to
`claude mcp list` to log the real connected/failed MCP server set to
`~/.claude/mcp-audit.log` — `SessionStart`'s own JSON payload carries no
server-list field, so this is the only way to get real data.

Measured directly on the home machine (not assumed): a real `claude mcp
list` run against ~14 configured servers takes **~16 seconds** (each server
gets a live health check). Wiring this synchronously would add 16s to every
session start — exactly the overhead this hook exists to help reduce.
`timeout 90` bounds the subprocess; a timeout or non-zero exit is logged
explicitly (`TIMEOUT90` / `RUNFAIL_rc...`), never silently swallowed, so a
broken PATH doesn't masquerade as "zero servers configured". Verified this
does not itself trigger a nested `SessionStart` (ran `claude mcp list`
manually while watching the log file — no new session-start event fired).

**Raised 25s -> 90s on 2026-09-25 after the bound went stale.** The 25s came
from a 14-server measurement (~16s). As plugins were added the count reached
36 and a real run took **33.5s**, so the hook silently began failing: **17 of
its 21 logged runs were `TIMEOUT25`** — ~81% dead, and the log read like an
MCP outage rather than a too-tight bound. The generalizable trap: a timeout
derived from a measurement of a *growing* quantity expires on its own, and
because the failure is logged as a legitimate status value it never looks
like a bug. 90s is ~2.7x the current measured time, so it absorbs roughly a
doubling of the server count.

**Log format (revised 2026-09-15 — token efficiency pass):** raw `claude mcp
list` output is ~1-2KB/line (full URLs, command paths, prose per server).
Only connect/fail/pending/disabled status is ever queried later, so the hook
parses it down to compact `name:status` pairs (`+` connected, `-` failed, `~`
pending approval, `o` disabled, `?` unrecognized), comma-joined:
`2026-09-15T05:53Z /c/Users/x/proj cavemem:+,serena:+,github:-`. Measured:
**88% size reduction** (1779 -> 197 bytes/line on the home machine's
14-server set). Requires `PYTHONIOENCODING=utf-8` on the parsing subprocess —
on Windows, `python.exe` defaults stdin to the console codepage (cp1252 on
the dev machine), which mis-decodes the CLI's UTF-8 status symbols into
garbage, so no symbol ever matched before this fix. No-op on Linux/macOS
(already UTF-8 by default), so safe to set unconditionally.

**Re-time this whenever the server count changes materially, in either
direction** — the timings above are tied to a specific server count, not a
universal constant. An earlier note here only warned about porting to a
machine with *fewer* servers; the failure that actually happened was the same
machine growing to *more*. If the log shows `TIMEOUT90` rows, re-measure
(`time claude mcp list`) before assuming the servers are down.

## `log-tool-failure.sh`

`PostToolUseFailure` (no matcher — every tool failure). Logs failed-tool
name + error to `~/.claude/tool-failures.log`, and separately writes the
full raw JSON payload to `~/.claude/.last-tool-failure-raw.json` on every
invocation (overwritten, not appended).

The error/reason field name for this event is **not confirmed** against
official docs as of 2026-09-13 (two fetch attempts didn't surface the exact
schema) — the script tries `error`, `error_message`, and
`tool_response.error` in that order. The raw-payload dump exists specifically
so a wrong guess is correctable in one look (`cat` the raw file after a real
failure) instead of silently logging an empty string indefinitely.

**Known gap, not fixed:** the raw-payload file is meant to be
access-restricted (`chmod 600`) since it can carry command args or file
content from a failed call. On Windows/NTFS via Git Bash, `chmod` silently
no-ops on this file class — verified with `stat` before/after, mode stayed
`0644` with no error reported. On a Linux/macOS port, `chmod 600` in the
script will actually take effect there; on Windows, treat the file as
readable by anything running as the same OS user.

## `snapshot-precompact.sh`

`PreCompact` (no matcher — fires on both manual and auto compaction).
Logs `trigger` (`manual`/`auto`) + `session_id` + `cwd` to
`~/.claude/compact.log` before context gets summarized — a breadcrumb for
when/why compaction happened, since the summary itself can thin out detail
the transcript had. Confirmed against docs 2026-09-15: exit 2 on this event
**blocks compaction outright**. This hook is pure logging and must never
exit non-zero on any path, including parse failure — a bug here would
silently prevent the user from ever compacting.

## `log-subagent-stop.sh`

`SubagentStop` (no matcher — every subagent). Logs `agent_type` + `agent_id`
+ a 150-char tail of `last_assistant_message` to `~/.claude/subagent.log`.
All three fields are already present in the documented payload — no
shell-out needed, unlike `audit-mcp-startup.sh` which has to call the CLI
because `SessionStart` carries no server list. Exit 2 on this event blocks
the subagent from stopping (confirmed 2026-09-15) — logger only, always
exits 0.

## `cost-logger.sh` — RETIRED 2026-09-25

**Deleted and unwired.** Kept here as the record of why, because the same
mistake was made twice on the same hook.

The 2026-09-17 rewrite below narrowed the hook to fields the `Stop` payload
was believed to carry. Audited 2026-09-25 against the log it had been
writing since: **227 of its 231 post-rewrite rows were `-` in every column**
— `effort` and `permission_mode` populate only rarely, and `stop_hook_active`
is absent entirely. So the corrected version failed the same way the original
did, for the same reason, and a second batch of empty rows again looked like
data for eight days.

Retired rather than narrowed a third time: after two rewrites the event has
produced nothing worth a row. Per-turn spend comes from the CLI's usage
reporting or the transcript. `~/.claude/usage.log` had also reached 4.8MB, of
which 4.81MB was pre-2026-09-17 raw payloads containing full
`last_assistant_message` text and file paths — a privacy leak, not just bloat;
truncated to the 232 real TSV rows at retirement.

**Historical record — scope corrected 2026-09-17 after capturing a real
payload.** This had written **2323 rows with every metric field `-`**. The
cause was not a wrong field name: the `Stop` event carries **no cost,
duration, or turn-count data at all**. Verified real top-level keys on
Claude Code 2.x:

```
background_tasks, cwd, effort, hook_event_name, last_assistant_message,
permission_mode, prompt_id, scratchpad_dir, session_crons, session_id,
stop_hook_active, transcript_path
```

So per-turn spend is unobtainable here under any field name, and the honest
fix was to stop claiming it rather than guess again. Cost data must come from
the CLI's own usage reporting or the transcript. The hook now logs what the
event does carry and what actually moves cost: session identity, `effort`,
`permission_mode`, `stop_hook_active`.

Two lessons worth keeping. First, a guessed field name that yields an empty
value is indistinguishable from a legitimate zero — 2323 rows looked like
real data. Second, the fix that found this was a five-line throwaway hook
that dumped one raw payload; when a schema is unknown, capture it rather than
iterating guesses.

## `measure-output-length.sh`

`Stop` (no matcher). Logs word count, char count, and filler-word count of
each turn's final assistant message to `~/.claude/output-length.log`, with
fenced code blocks stripped before measuring.

**Why measurement and not enforcement.** Verified against docs 2026-09-17:
**no hook can rewrite assistant output before display.** `Stop` and
`MessageDisplay` both receive the text read-only, and `MessageDisplay` is
explicitly a display-only event. So a terse-output policy can only ever be
enforced two ways — a reminder injected *before* generation
(`UserPromptSubmit`), or measurement *after*. If a terseness plugin is
already injecting a per-prompt reminder, adding a second identical reminder
is duplicate context on every single turn: pure token cost, zero new signal.
This hook supplies the half that is actually missing — evidence of whether
the reminder is working, and whether output drifts verbose over a long
session.

Filler count is the real drift signal, not raw length: a long answer can
still be terse, and a short one can still be padded. Code is excluded
because terse-prose policies normally exempt code blocks, so counting them
would flag every code-heavy turn as drift.

Exit 2 on `Stop` blocks the turn from ending, which would trap the session —
pure logger, every path exits 0.

## Retired: `anchor-caveman-drift.sh`, `nudge-underspecified.sh`

Both were built 2026-09-17 as `UserPromptSubmit` hooks that inject context,
and both were removed the same day after being measured. Kept here as a note
because the reasoning generalizes to any hook of that shape.

`nudge-underspecified.sh` appended a note when a prompt was a short bare
imperative stating neither success criteria nor constraints. Across a full
session of real work it fired **zero times**. The proximate cause was a
guessed verb list missing `audit`, `review`, `check`, `explain` — trivially
fixable — but widening it would have made it fire on exactly the prompts that
need no help. Replaying the session's real prompts against it confirmed none
of them would have benefited.

`anchor-caveman-drift.sh` re-anchored a terse-output mode when measurement
showed sustained drift. Never fired live; unwired, then deleted.

The shared flaw: **both spent context to fix a problem caused by context
pressure.** A mode ruleset works because it sits in the system prompt at
`SessionStart`, a high-salience position. Text injected into conversation
competes at ordinary salience against everything already there, and each
verbose turn already in history is a stronger example than a short
instruction. Re-issuing the mode command is cheaper and lands where it works.

What survived instead is `measure-output-length.sh` — it writes to disk,
injects nothing, and answers whether drift is real before anything is spent
fixing it. Measure first; only pay for a fix the data justifies.

Calibration data worth keeping, from the caveman plugin's own eval snapshot
(10 prompts, claude-opus-4-6): `__baseline__` 121.1 avg words, `__terse__`
125.8, `caveman` 60.8, `caveman-cn` 24.5, `compress` 91.9. **"Answer
concisely." scored no better than no instruction at all** — generic brevity
requests do nothing, which is why a useful instruction names specific
structures to cut.

## `log-config-change.sh`

`ConfigChange` (no matcher). Logs which settings tier changed
(`user_settings`/`project_settings`/`local_settings`/`policy_settings`/
`skills`) to `~/.claude/config-change.log`.

**Originally scoped as auto-backup-on-edit, cut back once the real payload
was checked (2026-09-15):** the `ConfigChange` input has **no filename and
no diff** — only `source` naming which tier changed. There is no way for
this hook to know *which file* to back up, so it logs drift timing instead
(an audit trail: "user_settings changed at TS") rather than claiming a
backup capability it can't deliver. Exit 2 is a documented no-op for this
event — the configuration change proceeds regardless of what the hook does.

A retired pair — `daily-blog-queue.sh` (SessionEnd) and `daily-blog-show.sh` (SessionStart:startup) — once served the **daily-blog** skill: the first launched a detached read after you left, the second printed the finished notes at the next day's first session. They were removed on 2026-08-01 in favour of the `engineering-blog-daily` local reader (browse + search + on-demand notes, no background process); recover them from commit `a2362f7` if the pattern is ever needed again. Their failure mode is itself the lesson: the pair sat wired-but-never-firing for days, because a plugin-delivered hook resolved `CLAUDE_PROJECT_DIR` to the wrong tree and the script's missing-state guard exited 0 in silence. Four things generalize to any hook that spawns work:

- **`Stop` is not session end.** It fires after every agent response. `SessionEnd` is the exit event, but it has a ~1.5s shared budget — enough to launch, never to do.
- **Guard against recursion before anything else.** A hook that spawns `claude -p` gets a child whose own hook spawns another, forever. `CLAUDE_CODE_CHILD_SESSION=true` and `CLAUDE_CODE_ENTRYPOINT=mcp-stdio-cli` identify a headless child (verified); interactive sessions leave the first unset and report `cli`.
- **`setsid` does not exist in Git Bash on Windows**, so a POSIX detach there spawns nothing *silently*. Branch to `powershell Start-Process -WindowStyle Hidden`. Detached survival past session exit is undocumented in Claude Code, so record the attempt before spawning and report a missing result rather than failing invisibly.
- **A hook that exits 0 when its state is missing is indistinguishable from a hook that never ran.** Both of these opened with `[ -d "$STATE_DIR" ] || exit 0`, which is correct for "nothing to show" and catastrophic for "wired to the wrong tree" — the two cases produce identical silence. Either log the reason to a file the user will see, or fail loudly the first time. Pair this with the delivery gotcha: a hook shipped in a plugin's `hooks.json` runs with `CLAUDE_PLUGIN_ROOT` pointing at the *plugin cache snapshot*, and `CLAUDE_PROJECT_DIR` at whatever project is open — neither is your working checkout. A hook that reads repo state needs the path pinned, or it must resolve state relative to `$CLAUDE_PLUGIN_ROOT` and ship that state with the plugin.
