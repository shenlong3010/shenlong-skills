# templates/ralph/

Scaffolds for a ralph loop run. `ralph-plan` (skill) instantiates them into
`.agents/runs/run-<yyyymmdd>-<story-slug>/` in the **target** repo; `ralph-next`
(skill) reads and updates the instantiated copies. Placeholders use `{{name}}`.

Not validated by `tools/validate.py` (templates carry no frontmatter). Do not
add tracker-specific fields here — adapters map tracker payloads onto these
generic shapes.

| File | Instantiated as | Written by | Read by |
|---|---|---|---|
| `PRD.md.template` | `PRD.md` | ralph-plan | roles (context) |
| `SPEC.md.template` | `SPEC.md` | ralph-plan, ralph-diagnostician (`[R]` rewrites) | roles |
| `TASKS.md.template` | `TASKS.md` (marker table — state machine truth) | ralph-plan, ralph-next | ralph-next, /ralph status |
| `task.md.template` | `task-<n>-<slug>.md` (one per task) | ralph-plan, replan | the one file a role subagent receives |
| `PROGRESS.md.template` | `PROGRESS.md` (iteration log + plan-sha) | ralph-next | ralph-next, /ralph status |
| `LOOP-CONTEXT.md.template` | `LOOP-CONTEXT.md` (steering channel) | human (Guidance), ralph-next (Learned) | prepended to every subagent prompt |
| `ralph.yml.template` | `.agents/ralph.yml` (budgets, repo-wide) | ralph-plan (first run only) | ralph-next |
| `TICKETS.md.template` | `TICKETS.md` (ticket outbox — outward open loop) | ralph-next (proposals), /ralph tickets (flush/dismiss) | /ralph tickets, /ralph status |
