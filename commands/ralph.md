---
name: ralph
description: User surface of the ralph loop — /ralph plan|next|auto|status|replan|tickets. Plan stories into runs, iterate one task at a time through coder/inspector/diagnostician subagents, watch state, regenerate tasks after upstream change, or flush discovered-work ticket proposals. Use for "/ralph", "run the loop", "loop status", "replan the run", "flush the tickets".
derivation: adapted
source: https://github.com/snarktank/ralph
---

# /ralph

## Invocation
`/ralph <plan|next|auto|status|replan|tickets> [run-id | story-filter]`

Bare `/ralph` → same as `status`, plus the suggested next subcommand.

## Behavior

All state read from disk under `.agents/runs/` at invocation time — never from session memory; every subcommand works identically in a fresh chat.

- **`plan [story-filter]`** — invoke the `ralph-plan` skill: adapter ladder (Jira MCP → GitHub issues → local BACKLOG.md/PRD.md), decompose, scaffold `run-<id>/` + INDEX. Writes: run directory, `.agents/ralph.yml` (first time), `.gitignore` line for `.agents/` (first time).
- **`next [run-id]`** — invoke the `ralph-next` skill for exactly **one** iteration on the given run (default: first incomplete run in INDEX order). Report the marker transition and verdict, then ask: next / auto / stop.
- **`auto [run-id]`** — iterate `ralph-next` until a stop condition (all `[v]`, ERROR, `[H]`, budget caps from `.agents/ralph.yml`, or `PAUSE: true` in LOOP-CONTEXT.md). Iteration ceiling: open AC count × (1 + max_retries_per_task) + inspections, hard-capped by `max_subagent_calls`. Report a per-iteration summary line as it goes.
- **`status`** — read-only, zero writes: per run in `.agents/runs/`, print the TASKS.md marker table, last PROGRESS entry, any `## Halts`, and the TICKETS.md proposal count (`proposed`/`flushed`/`dismissed`); flag runs paused via PAUSE or waiting on `[H]`.
- **`replan [run-id]`** — inward open-loop refresh: re-fetch the story via the run's adapter, `git diff <plan-sha> -- <files-to-touch of open tasks>`, list affected open tasks. **Stop and confirm the list with the user before writing** (regeneration overwrites task files). On confirm: regenerate affected `task-*.md` + TASKS.md rows, preserve every `[v]` task untouched, bump `plan-sha`, log the replan event to PROGRESS.md.
- **`tickets [run-id]`** — outward open-loop flush of the TICKETS.md outbox: list every `proposed` row with its full body → **stop and confirm per row with the user** (create / dismiss / leave). On confirm: create via the run adapter's `write` capability (see `skills/ralph-plan/references/adapters.md`), mark the row `flushed` with the ticket ref — or `dismissed`. No `write` capability available → say so and leave rows `proposed`; local-backlog adapter appends a `## Proposed:` story to `BACKLOG.md`.

## Rules
1. One role subagent per iteration — never two spawns from one `next`.
2. Markers only move via `ralph-next` processing a role report — no hand-editing markers on the user's behalf.
3. `status` writes nothing, ever.
4. `replan` never touches `[v]` tasks; completed work is settled.
5. If `.agents/runs/` is absent, every subcommand except `plan` says so and routes to `plan` — no auto-planning as a side effect.
6. `tickets` is the only subcommand that writes outside the repo; it never runs unconfirmed, and nothing else — auto mode included — ever calls an adapter's `write` capability.

## Boundaries
Loop mechanics live in `skills/ralph-next`; planning in `skills/ralph-plan`; role behavior in `agents/ralph-*.md`. This command is routing + confirmation gates only. Interval re-invocation ("run /ralph next every 10 minutes") is the built-in `/loop` command's job, composing with this one.
