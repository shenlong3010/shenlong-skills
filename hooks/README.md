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

## `audit-mcp-startup.sh`

`SessionStart`, **must stay wired with `"async": true`**. Shells out to
`claude mcp list` to log the real connected/failed MCP server set to
`~/.claude/mcp-audit.log` — `SessionStart`'s own JSON payload carries no
server-list field, so this is the only way to get real data.

Measured directly on the home machine (not assumed): a real `claude mcp
list` run against ~14 configured servers takes **~16 seconds** (each server
gets a live health check). Wiring this synchronously would add 16s to every
session start — exactly the overhead this hook exists to help reduce.
`timeout 25` bounds the subprocess; a timeout or non-zero exit is logged
explicitly (`TIMEOUT25` / `RUNFAIL_rc...`), never silently swallowed, so a
broken PATH doesn't masquerade as "zero servers configured". Verified this
does not itself trigger a nested `SessionStart` (ran `claude mcp list`
manually while watching the log file — no new session-start event fired).

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

**If porting to a machine with far fewer MCP servers, re-time this** — the
16s figure and 25s timeout are specific to this machine's ~14-server count,
not a universal constant.

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
