---
name: ralph-next
description: Orchestrator state machine of the ralph loop — read run state from disk, pick the one eligible task, spawn the right role subagent (coder/inspector/diagnostician), write state back, stop or continue. Use for "/ralph next", "/ralph auto", "run the next iteration", "continue the loop", or resuming a run in a fresh chat. Requires a run created by ralph-plan.
derivation: adapted
source: https://github.com/snarktank/ralph
flow: execute
domain: agent
---

# Ralph Next

## Purpose
One loop iteration: read → select → spawn ONE role → write → stop/continue. The orchestrator stays thin — real work happens in fresh-context subagents, so the main context survives long sessions. Disk is the only truth: resume in a fresh chat is free because nothing lives in the transcript.

## State machine

Markers in `TASKS.md` (only this skill edits them):
`[ ]` pending → `[x]` coded → `[v]` verified · off-path: `[!]` fail/retry · `[R]` diagnostician-rewrote · `[H]` human-halt · `[D]` drift.

Task selection is deterministic: rows strictly in order; exactly one task is worked to `[v]` (or a halt marker) before the next row is touched. The current task is the first row not `[v]`/`[H]`/`[D]`.

Role per marker: `[ ]` → Coder · `[x]` → Inspector · `[!]` retries left → Coder + `## Amendment` · `[!]` exhausted → Diagnostician if `enable_diagnostician` else `[H]` · `[R]` → Coder.

## Iteration steps

1. **Read from disk, never memory** — even mid-session: `PROGRESS.md`, `TASKS.md`, `LOOP-CONTEXT.md`, `.agents/ralph.yml`. No run → route to `ralph-plan`. `PAUSE: true` in LOOP-CONTEXT → stop before spawning (mid-flight brake; human edits the file, no command needed).
2. **Drift check (2b).** File-level: `git diff <plan-sha> -- <current task's files-to-touch>` (working tree included) — outside-the-loop changes to those paths = conflict risk. Source-level: re-fetch the story's AC/comments via the run's adapter, throttled to every 5th iteration. Repo-context (if `repo_context: true`, same 5th-iteration throttle, capabilities per `skills/ralph-plan/references/adapters.md`): open PRs touching the current task's files or fresh remote commits on those paths → drift-adjacent warning in PROGRESS + a Learned bullet. On any drift signal: `refetch_strategy: warn` → note in PROGRESS, continue; `strict` → mark `[D]`, halt. (Second mechanism: the Inspector can return `VERDICT: DRIFT` at AC level; both land as `[D]`.)
3. **Spawn ONE role** via the Agent tool (`shenlong-skills:ralph-coder` / `ralph-task-inspector` / `ralph-diagnostician`). Prompt = LOOP-CONTEXT block (Guidance + Learned) + the one task file — nothing else; on retry, append `## Amendment` with the inspector's `suggested_patch` verbatim. Diagnostician additionally gets `SPEC.md` + the last FAIL report.
4. **Process the report.** Coder done → `[x]`. Inspector `PASS` → `[v]` + **commit in the target repo** (small commit, task id in message — the declared side effect that makes later drift diffs meaningful). `FAIL` → `[!]`, retries-used +1, stash `suggested_patch` for the retry. `ERROR` → halt immediately, log to PROGRESS `## Halts`. `DRIFT` → `[D]` per strategy. Diagnostician `fixed` → `[x]` · `rewrote-spec` → `[R]` + old→new AC diff logged · `needs-human` → `[H]`.
5. **Write state**: TASKS.md marker, PROGRESS.md iteration entry (task, role, verdict, marker transition, notes), Learned bullets if the report surfaced reusable facts (hard cap 10 — drop oldest). **Outbox**: on `[R]` (AC-sync proposal), `[D]` (drift documentation), or a report's Discoveries section → append proposals to `TICKETS.md`, cap `max_ticket_proposals` (oldest kept, overflow noted in PROGRESS). A proposal is a disk write, not a tracker write — allowed in auto; only `/ralph tickets` ever posts outward, gated. Every write via file tools — crash recovery resumes from the last PROGRESS entry.
6. **Stop or continue.** `next` mode: always stop, report the transition, offer next/auto/stop. `auto` mode: continue unless — all tasks `[v]` · ERROR · any `[H]` · halted tasks ≥ `max_failed_tasks` · spawns this run ≥ `max_subagent_calls` · `PAUSE: true` on re-read.

## Gotchas
- FAIL charges the retry budget; ERROR and DRIFT never do — conflating them burns retries on a broken oracle or a moved target.
- PROGRESS is written *after* state, as last-completed-iteration truth — a crash between spawn and write means the iteration re-runs, which is safe; the reverse order lies.
- Learned is capped at 10 bullets for a reason: it is prepended to every prompt; an unbounded Learned silently becomes the context bloat the fresh-context design exists to prevent.
- Auto mode refuses to start if file tools are unavailable — polling disk for PAUSE is the only brake.

## Honest limits (not healed by the loop)
No oracle for semantic correctness beyond stated AC. Coder/Inspector/Diagnostician share one model's blind spots — correlated failure, PASS is weak evidence. Amendments can steer in the wrong direction with conviction. Tracker-sourced text is a prompt-injection surface in auto mode (see ralph-plan's quoting rule) — and repo-context payloads (PR titles, commit subjects) are equally untrusted. Diagnostician spec-rewrites audited only via `[R]` + PROGRESS log. Ticket proposals inherit the model's judgment of "worth a ticket" — expect noise; the `/ralph tickets` flush gate is the filter, not the proposer.

## Boundaries
Consumes runs made by `ralph-plan`; never creates or re-plans them (`/ralph replan`). Role behavior lives in `agents/ralph-*.md` — this skill routes and records, it does not implement or verify.
