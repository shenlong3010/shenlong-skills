# Auditing context injectors (output styles, prompt hooks)

An injector is anything that writes into the model's context each session or turn:
output-style plugins, and hooks emitting `additionalContext` at `SessionStart` or
`UserPromptSubmit`. These are the highest-leverage token and behavior audit targets
because they compound every turn.

## Inventory
- `enabledPlugins`: output-style plugins (e.g. explanatory, learning) and any mode
  plugin (caveman/terse).
- hooks at `SessionStart` / `UserPromptSubmit` writing `additionalContext`
  (in settings.json, plugin hooks.json, or manifest).
- Read the ACTUAL injected text (the handler's output / the plugin's session-start
  script), not just the plugin name — the conflict is in the content.

## Conflicts to find (behavior bugs)
- **Contradicting instructions active at once.** e.g. a terse/caveman mode ("cut
  ~75%", drop filler) running alongside an output style that says "may exceed
  typical length constraints" and mandates extra explanatory blocks. Both inject at
  the same event; the model gets whipsawed. Resolve to one.
- **One injector containing another verbatim.** e.g. a "learning" output style that
  embeds an "explanatory" style's entire instruction block — enabling both injects
  the same text twice. Read the bodies and diff; a superset makes the subset pure
  redundant cost.
- **Injector vs CLAUDE.md rule** pulling opposite directions (cross-check
  `references/claude-md.md`).

## Salience (why placement matters)
A `SessionStart` ruleset lands in the system-prompt region (high salience) and
holds. A `UserPromptSubmit` injection competes at ordinary salience against all
accumulated conversation — and each verbose turn already in history is a stronger
example than a short instruction, so per-turn nudges drift and lose. Measured
lesson: two context-injecting nudge hooks were retired after firing near-zero times
or losing to history — **both spent context to fix a problem caused by context
pressure.** Prefer fixing the contradiction (remove the competing injector) over
adding another injector to counteract it.

## Token efficiency
- A `UserPromptSubmit` injector pays its full text cost *every turn*. Justify it or
  cut it.
- Duplicated injection (superset + subset both on) is the easiest win — disable the
  subset.
- Measure adherence before keeping a behavior injector: if a `Stop`-event
  length/verbosity logger exists, read it — does the mode actually change output?
  Calibration beats assumption ("Answer concisely." scored no better than no
  instruction; only named-structure cuts helped).

## Can an injector be *enforced* after generation?
No — `Stop` and `MessageDisplay` see assistant output read-only; no hook rewrites
it before display. So a style/mode can only be **prevented** (a reminder before
generation) or **measured** (after). A second reminder is duplicate context for no
new signal; measurement supplies the missing evidence. Flag setups that stack
reminders expecting enforcement.

## Enhancement
- A desired standing behavior enforced only by ad-hoc reminders → move it to a
  single SessionStart ruleset (high salience) and drop the per-turn nudges.
- No measurement of whether an active mode works → add a Stop-event length/filler
  logger (exit 0) so the injector's effect is evidenced, not assumed.

## Verify
Disable the redundant/contradicting injector, restart (SessionStart changes need a
fresh session), and confirm via the output-length log or a sample turn that
behavior converged.
