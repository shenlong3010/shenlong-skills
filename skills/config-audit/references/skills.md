# Auditing skills and agents

## Inventory (every source)
- repo core + repo extra (a second plugin in the same repo, often off on one machine)
- `~/.claude/{skills,agents}` — user-scope copies (symlink fallback or hand-copy)
- `enabledPlugins` + the plugin cache (version-keyed) + `installed_plugins.json`
- synced skills (`~/.claude/skills/synced/`)
- the session's **skill listing** = what actually loaded (ground truth), vs the
  working tree = what should load. They diverge when the cache is stale.

## Deduplication — by contract, not name
A shared name is not a duplicate. Before calling a skill/agent redundant, check:
1. **Contract** — does it produce the same output shape? A repo review agent with
   a severity-ranked `VERDICT:` marker is a different artifact from a native
   quick-pass command of the same name.
2. **Callers** — grep the repo for artifacts that route to it by name. An agent
   with internal callers stays even if a native twin exists.
3. **`source:`** — `original` vs `adapted`/`copied` from a specific upstream. A
   skill adapted from repo X is not a duplicate of plugin Y; and enabling the X
   plugin would *recreate* the duplication you're removing.

When a native built-in genuinely covers a repo skill's whole job with equal fit,
that's a real duplicate. But "native" means a **CLI built-in** — a marketplace
plugin or `anthropic-skills:` entry may not exist on a marketplace-blocked machine,
so it can't be the fallback there. Check fit, not just existence: a plugin agent
hardcoded to one language/framework gives wrong advice on other stacks; a
native command that reads the actual diff + CLAUDE.md wins on fit.

## Overlap sources to check by function (not name)
Native `/code-review`, `/simplify`, `/init`, `/security-review`, `/context`,
`/doctor`, `/skill-doctor`; plugins `claude-md-management` (owns CLAUDE.md
rewrites), `plugin-dev` (skill/agent/hook authoring, `skill-reviewer`,
`plugin-validator`), `skill-creator`, `pr-review-toolkit`, `feature-dev`,
`session-report`, `fewer-permission-prompts`. When a repo skill overlaps one,
either retire the repo skill or add a `Do NOT use for …` boundary naming it.

## The manifest-array-replaces-discovery trap (verified, cited)
In a plugin's `.claude-plugin/plugin.json`, an explicit `agents` array **replaces**
the `agents/` scan, and an explicit `commands` key **replaces** the `commands/`
scan (components.md:688,724) — a file present in the directory but missing from the
array is **silently not loaded.** (A `skills` array, by contrast, *adds to* the
scan — components.md:667.) So when an agent/command is in the repo tree but absent
from the session's listing, check the manifest array before blaming cache
staleness — an omission from the array is the usual cause. Fix: add the file to
the array, or drop the array to restore auto-discovery.

## Token efficiency
- Every skill **description** loads into every session; bodies load only on
  trigger. Standing cost = sum of descriptions. Run `skill-lint` for the number;
  report it before/after any add/remove. The native `/skill-doctor` reports each
  skill's **context cost and usage frequency** and flags never-invoked skills —
  use it for the cost/usage half; this skill owns the **trigger-quality** half
  (`/skill-doctor` does not check whether a description actually triggers).
- A skill that never triggers is pure standing cost — check its description has
  literal event-triggers (phrases a user types), not topic labels. Undertriggering
  is the common failure.
- Two skills with overlapping triggers cause misroutes and double cost — split
  their triggers or merge them.

## Placement (core vs extra)
- Core = always-on essentials (search, debug, data, deps). Extra = on-demand,
  often disabled on one machine.
- A skill in extra is unavailable wherever extra is disabled — don't put a skill
  there if it's needed exactly on the machine where extra is off.

## Enhancement
- Missing `Do NOT use for` boundary where a sibling is confusable.
- Description in topic-language not event-language (undertriggers).
- No eval / routing case — add one with `eval-writer`, each positive case paired
  with a negative twin (a near-miss prompt that must NOT trigger it).
- OS-dependent method with only one platform's lane (routing lie on the other OS).

## Verify
`validate.py` (frontmatter + placement), `skill-lint` (trigger quality + cost),
`knowledge-lint` (broken reference links). Re-check the session's skill listing
matches the tree after any add.

Windows note: running these linters via `python3`/`python` works, but a Python
process given a bash-style `/c/Users/...` path can `FileNotFoundError` (and values
piped from Python carry a trailing `\r` that breaks string compares). Use
`os.path.expanduser("~/...")` or read via the harness Read tool, and `tr -d '\r'`
on piped values.
