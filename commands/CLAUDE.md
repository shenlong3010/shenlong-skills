# commands/ — directory guide

Loaded when working in this directory; root globals apply. Commands are human-invoked slash operations — flat `.md` files, invoked as `/name`.

## Structure
**Invocation** (exact syntax, args, defaults) → **Behavior** (numbered steps) → the artifact or output the user receives.

## Laws
- Behavior steps read **real state** — the staged diff, the actual file, the live branch — never session memory (`commit-writer` runs `git diff --cached`; it does not summarize what it remembers changing).
- Side-effectful steps state exactly what is written where; anything irreversible stops for explicit confirmation instead of executing.
- Creators (`create-*`) route through `tools/scaffold.py` — never duplicate scaffolding logic in a command body.
- Rules of thumb for placement: invoked by the human at a moment in time → command; consumed by the agent mid-task → skill.
- New commands via `/create-command`.
