# Auditing slash commands

## Inventory
- repo `commands/`, repo extra
- `~/.claude/commands/` (user-scope)
- plugin commands (each enabled plugin's `commands/`)
- native built-ins (`/init`, `/context`, `/doctor`, `/compact`, `/model`, …) — not
  files, but they occupy the same namespace a user types into.

## Deduplication
- A repo command duplicating a native built-in of the same name: keep the repo one
  only if it does something the built-in doesn't (different args, repo-specific
  behavior). Otherwise it's confusing namespace noise — retire it.
- Two plugins both defining `/x`: last-loaded wins silently; flag the collision.
- Match by behavior, not name — same as skills.

## Command-specific correctness checks
- **Read-real-state law.** A command's steps must read the *actual* live state —
  the staged diff, the file on disk, the current branch — never the model's memory
  of what it did. A status command that "summarizes what I remember doing" instead
  of deriving from disk is a bug. Flag any step that narrates instead of inspects.
- **Irreversible-stops rule.** Any side-effectful step (delete, push, publish,
  spend, overwrite) must state exactly what it writes where, and anything
  irreversible must stop for explicit confirmation rather than executing. Flag
  commands that do destructive work without a confirm gate.
- **Scaffolding not duplicated.** A creator command should route through the shared
  scaffold tool, not reimplement placement logic in the command body.

## Token efficiency
Commands are invoked, not always-loaded — their body cost is paid on use, not per
session. So the efficiency lever here is fewer *misfires* (clear invocation syntax,
no overlapping names), not description trimming.

## Enhancement
- A multi-step manual ritual done repeatedly with no command → propose one.
- A command missing argument handling or defaults that forces re-prompting.
- A command that should read state but takes it as an argument.

## Verify
`validate.py` for frontmatter/placement; run the command against a real repo state
and confirm its steps inspect disk, not memory.
