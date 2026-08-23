---
name: spend
description: Report Claude Code spend and session stats from the local usage log — totals by day, per-session averages, top sessions. Use for "/spend", "how much have I spent", "what did this month cost", "token spend report", or before/after changing model tiers in reasoning-budget-guidance. Read-only — never writes to the log.
derivation: original
flow: session
domain: agent
---

# /spend

## Invocation

```
/spend [days N] [log <path>]
```

- `days N` — window (default 30). `log <path>` — override; default `~/.claude/usage.log` (written by the `cost-logger` Stop hook).

## Behavior

1. Run the reporter:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/tools/spend-report.py" --days 30
   ```

   `${CLAUDE_PLUGIN_ROOT}` is set inside Claude Code when the plugin is active; if empty (repo-local dev), fall back to `tools/spend-report.py` from this repo. Pass through any args verbatim (`--days`, `--json`, `--log`).

2. Present the tool's summary as-is: total cost, session count, avg/session, by-day table, top sessions. Never round up silently — costs are shown at the tool's precision.

3. If the log is missing or empty, say so and point to `hooks/cost-logger.sh` — an absent log means the Stop hook isn't wired (see hooks/README.md platform notes), not zero spend.

## Output

The rendered report. No writes anywhere; the log file is never modified.
