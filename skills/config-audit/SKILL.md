---
name: config-audit
description: Audit a Claude Code setup — skills, CLAUDE.md, hooks, commands, MCP servers, output-style injectors — for dead weight, token cost, duplication, and missed enhancements. Use whenever asked to "audit my setup / skills / agents / hooks / config", "clean up my Claude Code", "find duplicate skills", "why is my context so heavy", "what's conflicting", or before pruning any plugin/skill/hook. Loads a per-surface reference on demand. Do NOT use for source-code review (code-review), a single CLAUDE.md rewrite (claude-md-improver owns that), or spend reporting (/spend).
derivation: original
flow: meta
domain: agent
---

# config-audit

## Purpose
One method for auditing any part of a Claude Code setup against four goals:
**cleanup** (dead/stale artifacts), **token efficiency** (standing context cost),
**deduplication** (repo vs native vs plugin vs user-scope), **enhancement** (what's
missing or misfiring). The method is identical per surface; the surface-specific
checks live in `references/` and load only when that surface is in scope.

## When to use
- "audit my setup / skills / hooks / config", "clean up my Claude Code"
- "do I have duplicate skills", "what conflicts with what", "why is context heavy"
- before disabling/deleting any plugin, skill, hook, or MCP server

Route to the reference for the surface asked; audit all when the ask is "my setup".

## Method (every surface)

1. **Inventory — from every source, not just the repo.** A verdict from a partial
   inventory is wrong. Enumerate all load paths before judging (see the load-path
   list below). The session's own skill/tool listing is ground truth for *what
   actually loaded*; the working tree is what *should* load. They diverge.
2. **Cross-reference.** For each artifact, find every other place the same
   capability is provided — native built-in, first-party plugin, another plugin,
   user-scope, repo core, repo extra. Match by **what it does and its contract**,
   never by name alone.
3. **Classify** each finding into one action class, with a reversibility note:
   `delete` · `disable` · `merge` · `enhance` · `keep` (with reason).
4. **Propose, don't apply.** Present the classified list, verified-vs-inferred
   tagged (below), and get explicit approval before any destructive or
   config-changing step. Read-only by default.
5. **Apply on approval**, cheapest-blast-radius first, and verify each change with
   the surface's own gate (linters, `test-hooks.sh`, re-inventory).

## Load paths — enumerate ALL before any verdict

- repo **core** (`skills/`, `commands/`, `agents/`, `hooks/`) and repo **extra**
  (a second plugin in the same repo, often off on one machine)
- **user-scope**: `~/.claude/{skills,agents,commands}` (an `install.sh` symlink
  fallback or an older hand-copy loads here, next to the plugin)
- **plugins**: `enabledPlugins` in `settings.json`, plus
  `~/.claude/plugins/{installed_plugins.json,known_marketplaces.json}` and the
  version-keyed cache under `~/.claude/plugins/cache/`
- **synced** skills: `~/.claude/skills/synced/` (toggled on claude.ai, not in
  settings.json)
- **MCP servers**: read ONLY from `~/.claude.json` — never `settings.json`
- **hooks**: three wiring sources — `settings.json`, a plugin's `hooks/hooks.json`
  (auto-discovered from the plugin root), and the manifest's inline `hooks` block
- **injectors**: any hook writing `additionalContext` at `SessionStart` /
  `UserPromptSubmit`, plus output-style plugins

## Cross-cutting gotchas (all surfaces)

- **A name collision is NOT a duplicate.** Two artifacts can share a name and
  differ in contract, callers, or `source:`. Check all three before calling one
  redundant. A repo agent with a `VERDICT:` contract and internal callers is not
  the native command of the same name.
- **Stale cache masks the truth.** The plugin cache is keyed on the **version
  string**. Editing a plugin file without bumping the version never reaches a
  running or reinstalling session — "already at latest version" keeps serving the
  old cache. A finding that a change "didn't take effect" is usually this, not a
  real bug. Bump the version to invalidate.
- **Marketplace-blocked machines flip the dedup rule.** Where the marketplace is
  unavailable, the repo is the *only* source — never delete repo copies to favor a
  plugin. Dedupe by disabling the *other* side in that machine's config instead.
- **Config toggles break the prompt cache.** `enabledPlugins` and MCP changes sit
  upstream of conversation in the cache prefix — apply them at the **start of the
  next session**, not mid-session. Say so in every proposal.
- **Tag every finding verified or inferred.** An inference recorded as fact hardens
  and misleads later. "Runs twice" needs a measurement or a doc citation; "manifest
  wires only N" without checking the loader is an inference. Promote to verified
  only with evidence.

## Reference routing (load one, on demand)

- `references/skills.md` — skill/agent dedup vs native + plugins, trigger-quality
  and standing token cost (`skill-lint`), core-vs-extra placement
- `references/claude-md.md` — CLAUDE.md token cost, staleness, self-contradiction,
  the memory-vs-hook boundary
- `references/hooks.md` — double-fire (manifest + hooks.json), per-event exit
  contracts, stderr-must-name-an-escape, no `set -e`, `install.sh` wires nothing
- `references/commands.md` — command dedup vs native, read-real-state law,
  irreversible-stops rule
- `references/mcp.md` — dead/failed servers, `~/.claude.json`-only, cache cost of
  churn, restart-to-reload
- `references/injectors.md` — SessionStart/UserPromptSubmit conflicts, one injector
  containing another verbatim, output-style vs terse/caveman mode

## Output contract
Findings grouped by surface, each: **[verified|inferred]**, the artifact
(`path` or `plugin@marketplace`), the action class (`delete|disable|merge|enhance|keep`),
reversibility, and the one-line fix. Cache-breaking or destructive steps flagged
"next session" / "confirm first". End: what this pass could not see (runtime-only
behavior, another machine's config, claude.ai-side sync state).

## Boundaries
- Source-code review → `code-review`; SQL → `sql-review`.
- A single CLAUDE.md rewrite → `claude-md-management:claude-md-improver` where that
  plugin is available; on a marketplace-blocked machine it isn't, so do the rewrite
  here (or via `setup-instructions` if extra is enabled). This skill *flags* CLAUDE.md
  issues in a whole-setup pass either way.
- Spend/usage numbers → `/spend` (repo command, always available).
- Session token breakdown → `session-report:session-report` where available.
- Reducing permission prompts specifically → the native `fewer-permission-prompts`.

Note: several of the above are plugins/built-ins. On a machine where the
marketplace is blocked they may be absent — this skill (core, always-on) still
performs the audit itself and only *routes* to them when present.
