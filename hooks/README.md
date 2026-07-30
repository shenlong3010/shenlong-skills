# Hooks

Starter lifecycle hooks. Copy the script per project, wire it in `hooks.json` (or project `.claude/settings.json`), `chmod +x` the script. Hook events receive a JSON payload on stdin; a PreToolUse hook exiting 2 blocks the tool call.

`daily-blog-queue.sh` (SessionEnd) and `daily-blog-show.sh` (SessionStart:startup) are a pair serving the **daily-blog** skill: the first launches a detached read after you leave, the second prints the finished notes at the next day's first session. Three things about them generalize to any hook that spawns work:

- **`Stop` is not session end.** It fires after every agent response. `SessionEnd` is the exit event, but it has a ~1.5s shared budget — enough to launch, never to do.
- **Guard against recursion before anything else.** A hook that spawns `claude -p` gets a child whose own hook spawns another, forever. `CLAUDE_CODE_CHILD_SESSION=true` and `CLAUDE_CODE_ENTRYPOINT=mcp-stdio-cli` identify a headless child (verified); interactive sessions leave the first unset and report `cli`.
- **`setsid` does not exist in Git Bash on Windows**, so a POSIX detach there spawns nothing *silently*. Branch to `powershell Start-Process -WindowStyle Hidden`. Detached survival past session exit is undocumented in Claude Code, so record the attempt before spawning and report a missing result rather than failing invisibly.
