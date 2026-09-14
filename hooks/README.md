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

A retired pair — `daily-blog-queue.sh` (SessionEnd) and `daily-blog-show.sh` (SessionStart:startup) — once served the **daily-blog** skill: the first launched a detached read after you left, the second printed the finished notes at the next day's first session. They were removed on 2026-08-01 in favour of the `engineering-blog-daily` local reader (browse + search + on-demand notes, no background process); recover them from commit `a2362f7` if the pattern is ever needed again. Their failure mode is itself the lesson: the pair sat wired-but-never-firing for days, because a plugin-delivered hook resolved `CLAUDE_PROJECT_DIR` to the wrong tree and the script's missing-state guard exited 0 in silence. Four things generalize to any hook that spawns work:

- **`Stop` is not session end.** It fires after every agent response. `SessionEnd` is the exit event, but it has a ~1.5s shared budget — enough to launch, never to do.
- **Guard against recursion before anything else.** A hook that spawns `claude -p` gets a child whose own hook spawns another, forever. `CLAUDE_CODE_CHILD_SESSION=true` and `CLAUDE_CODE_ENTRYPOINT=mcp-stdio-cli` identify a headless child (verified); interactive sessions leave the first unset and report `cli`.
- **`setsid` does not exist in Git Bash on Windows**, so a POSIX detach there spawns nothing *silently*. Branch to `powershell Start-Process -WindowStyle Hidden`. Detached survival past session exit is undocumented in Claude Code, so record the attempt before spawning and report a missing result rather than failing invisibly.
- **A hook that exits 0 when its state is missing is indistinguishable from a hook that never ran.** Both of these opened with `[ -d "$STATE_DIR" ] || exit 0`, which is correct for "nothing to show" and catastrophic for "wired to the wrong tree" — the two cases produce identical silence. Either log the reason to a file the user will see, or fail loudly the first time. Pair this with the delivery gotcha: a hook shipped in a plugin's `hooks.json` runs with `CLAUDE_PLUGIN_ROOT` pointing at the *plugin cache snapshot*, and `CLAUDE_PROJECT_DIR` at whatever project is open — neither is your working checkout. A hook that reads repo state needs the path pinned, or it must resolve state relative to `$CLAUDE_PLUGIN_ROOT` and ship that state with the plugin.
