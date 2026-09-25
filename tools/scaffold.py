#!/usr/bin/env python3
"""Shared creator core. The /create slash command calls this.

Usage: python3 tools/scaffold.py <skill|command|agent|tool|hook> <name> [flow] [domain]

`flow` and `domain` are from the vocabularies in validate.py (defaults:
util/code — fix before committing). Writes a stub in the right directory with
standard frontmatter, then runs tools/validate.py so a bad stub fails
immediately.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

FRONT = """---
name: {name}
description: TODO — what it does and when to trigger; write it pushy, undertriggering is the common failure.
derivation: original
flow: {flow}
domain: {domain}
---

"""

BODIES = {
    "skill": """# {title}

## Purpose
TODO — one paragraph.

## When to use
TODO — trigger conditions.

## Steps
1. TODO
""",
    "command": """# /{name}

## Invocation
`/{name} <args>`

## Behavior
TODO — what this command does when invoked.
""",
    "agent": """# {title} (subagent)

## Role
TODO — what this reviewer/worker does.

## Input
TODO.

## Output
TODO — structure of findings/results.
""",
    "tool": """#!/usr/bin/env python3
\"\"\"{title} — TODO one-line purpose.\"\"\"

def main() -> int:
    # TODO
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
""",
    # Real handler script, not a note. CLAUDE.md hook law baked in: block with
    # exit 2 + stderr naming a WORKING escape; loggers always exit 0; never emit
    # {{"decision":"allow"}}. Wire ONLY in hooks/hooks.json — adding the same
    # (event,matcher,command) to .claude-plugin/plugin.json too makes it fire
    # TWICE (both sources load; no within-plugin dedup). See hooks/README.md.
    "hook": """#!/usr/bin/env bash
# {title} hook. Event payload arrives on stdin as JSON.
#
# WIRING: add to hooks/hooks.json ONLY (never also to plugin.json — the same
# entry in both files runs twice). Snippet (${{CLAUDE_PLUGIN_ROOT}}, not
# $CLAUDE_PROJECT_DIR — the latter breaks outside this repo):
#   "Stop": [{{ "matcher": "*", "hooks": [
#     {{ "type": "command", "command": "bash \\"${{CLAUDE_PLUGIN_ROOT}}/hooks/{name}.sh\\"", "timeout": 5 }} ]}}]
# Then add a case to hooks/test-hooks.sh and read hooks/README.md first.
#
# NO `set -e`: it makes a failed command (e.g. grep exits 2 on no-match) abort
# with that non-zero code, which on a logger event BLOCKS the turn. No existing
# hook uses it. Guard each risky command explicitly instead.

# TODO pick ONE contract:
#  - Guard (PreToolUse/PreModelSwitch): to block, `echo "reason + working escape" >&2; exit 2`.
#    stderr MUST name an escape that actually reaches the user's goal. Never
#    emit {{"decision":"allow"}} (real auto-approval, skips the permission prompt).
#    Pass-through: exit 0 silently.
#  - Logger (Stop/PreCompact/SubagentStop/PostToolUse*/ConfigChange/SessionStart):
#    exit 2 on these either blocks the event or is a no-op — ALWAYS exit 0, even
#    on parse failure. Never let a logger stop a turn.
exit 0
""",
}

DESTS = {
    "skill": lambda n: ROOT / "skills" / n / "SKILL.md",
    "command": lambda n: ROOT / "commands" / f"{n}.md",
    "agent": lambda n: ROOT / "agents" / f"{n}.md",
    "tool": lambda n: ROOT / "tools" / f"{n}.py",
    "hook": lambda n: ROOT / "hooks" / f"{n}.sh",
}

# Kinds that get no YAML frontmatter (scripts, not markdown artifacts).
SCRIPT_KINDS = {"tool", "hook"}


def main() -> int:
    if len(sys.argv) not in (3, 4, 5) or sys.argv[1] not in DESTS:
        print(__doc__)
        return 2
    kind, name = sys.argv[1], sys.argv[2].strip().lower().replace(" ", "-")
    flow = sys.argv[3].strip().lower() if len(sys.argv) >= 4 else "util"
    domain = sys.argv[4].strip().lower() if len(sys.argv) == 5 else "code"
    dest = DESTS[kind](name)
    if dest.exists():
        print(f"refusing to overwrite {dest}")
        return 1
    dest.parent.mkdir(parents=True, exist_ok=True)
    title = name.replace("-", " ").title()
    body = BODIES[kind].format(name=name, title=title)
    content = body if kind in SCRIPT_KINDS else FRONT.format(name=name, flow=flow, domain=domain) + body
    dest.write_text(content, encoding="utf-8")
    print(f"created {dest}")
    if kind in ("skill", "command", "agent"):
        return subprocess.call([sys.executable, str(ROOT / "tools" / "validate.py")])
    return 0


if __name__ == "__main__":
    sys.exit(main())
