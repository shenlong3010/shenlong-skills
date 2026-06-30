# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Personal public skill registry for Claude Code / GitHub Copilot. Skills here are generic and app-agnostic by construction — they are designed to be vendored (pinned-snapshot, not live submodule) into a company registry. The pipeline is strictly one-way: public → internal, never reverse.

## Commands

Once Phase 0 is built:

```bash
# Validate a skill file against the registry dialect
python tools/validate.py <path-to-SKILL.md>

# Validate all skill files
python tools/validate.py agents/ commands/ skills/ tools/

# Run pre-commit guards (secret scanner + denylist scan)
pre-commit run --all-files

# Run CI scans against diff range (not just working tree)
pre-commit run --from-ref HEAD~1 --to-ref HEAD
```

## Directory layout (target)

```
agents/        subagent definitions (reviewers, critics)
commands/      directly-invocable harness ops
skills/        agent-consumed work skills
tools/         scripts + MCP-server scaffolds
docs/
templates/
.github/workflows/
PROVENANCE.md
```

**Key distinction:** `commands` = human-invocable harness operations; `skills` = work the agent consumes mid-task. Both use SKILL.md format but live in separate dirs.

## SKILL.md frontmatter (required shape)

```yaml
---
name: <skill-name>
description: <what it does + when to trigger; pushy, to fight undertriggering>
metadata:
  owner: <name>
  enforcement: advisory | enforced
  derivation: original | adapted | copied
  upstream_repo: <url or "n/a">
  upstream_sha: <sha or "n/a">
  license: <MIT | Apache-2.0 | n/a>
---
```

Only `name`, `description`, `metadata`, and optionally `license`/`allowed-tools` are valid top-level keys. Registry bookkeeping lives under `metadata`. `tools/validate.py` enforces this.

Every skill also requires a row in `PROVENANCE.md` (columns: skill | upstream | sha | license | derivation).

## Coding behavior rules

These apply to all implementation work in this repo. Source: [Karpathy's CLAUDE.md](https://github.com/multica-ai/andrej-karpathy-skills/blob/main/CLAUDE.md).

**1. Think before coding**

Don't assume. Don't hide confusion. Surface tradeoffs.

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

**2. Simplicity first**

Minimum code that solves the problem. Nothing speculative.

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

**3. Surgical changes**

Touch only what you must. Clean up only your own mess.

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

**4. Goal-driven execution**

Define success criteria. Loop until verified.

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

Before any code is written, define what "done" looks like in terms a machine can verify. "Add validation" fails this test. "Users who submit a blank or malformed email field see a specific error message, and both cases have passing tests" passes it. For multi-step work, state a plan first — before autonomous generation goes in the wrong direction.

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

**5. Verification**

Close the gap between code that seems correct and code that actually runs.

Before fixing a bug:
- Write a test that reliably reproduces it.
- Fix the code.
- Run the test. Only when the test passes is the bug fixed — not when it "feels" fixed.

This constraint matters most in loop contexts: an autonomous loop has no human reviewer at each step. The test is the only check.

**6. Debugging**

Reproduce before diagnosing. Change one variable at a time.

Sequence:
- Read the full error message and stack trace.
- Reproduce the problem before attempting a fix.
- Change one variable at a time.

The failure mode this prevents: confident wrong diagnosis — reading an ambiguous error, picking an interpretation, and generating a fix for a problem that was never confirmed to exist.

**7. Dependencies**

Every added package is permanent, uncontrolled code updated on someone else's schedule.

Before reaching for a library:
- Ask whether the standard library handles it.
- If not, ask whether the problem is small enough to implement directly.

If a dependency is added, document the decision explicitly: why this library, why not the standard library, what the tradeoff is.

**8. Communication**

Distinguish actionable uncertainty from vague reassurance.

- "I'm not sure this library supports streaming" — useful. Acts on real information.
- "I think this should work" — not useful. Sounds confident, carries no information.

When uncertainty is the accurate answer, say so precisely. Confident-sounding guesses that turn out wrong waste more time than honest uncertainty upfront.

**9. Common failure modes**

Recognize these patterns in your own behavior and stop immediately — do not continue toward completion.

- **Kitchen Sink** — asked to fix a faucet, renovating the kitchen. Scope has expanded beyond the request without permission.
- **Wrong Abstraction** — the same logic appears in three places without recognition that it should be a function. Duplication is visible; the fix is not being made.
- **Optimistic Path** — code written only for the happy case. Bad inputs, dropped connections, and server failures are unhandled.
- **Runaway Refactor** — one file becomes ten because nothing stops the cascade. Each change feels justified; the total is out of scope.

The prescribed response to recognizing any of these in progress: stop, surface the pattern, and ask before continuing.

## Hard constraints

1. **Zero employer-internal content.** No internal server names, app names, domain-model terms, stack idioms tied to internal systems, tokens/keys, or `/memory`-derived content. Scan the full diff range, not just the working tree — git history is permanent.

2. **Provenance per skill.** Every skill carries the full `metadata` block and a `PROVENANCE.md` row before it is considered complete.

3. **Guards before content.** The pre-commit secret scanner and denylist scanner must exist and be proven (plant a failure, confirm it's caught) before any skill is authored.

4. **No remote push, no vendoring.** Agent stages and commits locally. `git push` to public remote and company-registry import are human gates — agent never performs them.

5. **Denylist wordlist is local-only.** `.gitignore`d. The CI config references it by path. Empty wordlist = vacuous pass; populate it before any acceptance run.

## Authoring flow

All skills except the four bootstrap creators are scaffolded via a creator command, not hand-rolled:
- `create-agent` → `agents/`
- `create-skill` → `skills/`
- `create-command` → `commands/`
- `create-tool` → `tools/`

The creators share one core helper that writes frontmatter, appends the `PROVENANCE.md` row, and runs `tools/validate.py`. Never duplicate that logic across creators.

## Human gates (agent stops, does not auto-proceed)

- **Public push** — agent commits locally; human runs `git push` after IP/legal sign-off.
- **Company-registry import** — human vendors a pinned, security-reviewed snapshot at a tag/SHA. Never a live submodule from a personal account into company infrastructure.

## Current state

Repo is in planning phase. Two build plans exist:
- `plan/PLAN-skill-list-build.md` — public generic skills (phases 0–3, what belongs here)
- `plan/PLAN-skills-advanced-build.md` — org-specific skills (ADR, postmortem, debug, cost, compliance); executed against the internal registry after the public plan's Phase 0 is complete

No skill files, creators, or tooling exist yet. Phase 0 of `PLAN-skill-list-build.md` must complete before any other phase.
