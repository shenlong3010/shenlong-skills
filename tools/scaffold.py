#!/usr/bin/env python3
"""Shared creator core. The five create-* slash commands call this.

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
    "hook": """# {title} hook

Add to hooks/hooks.json:

```json
{{
  "hooks": {{
    "Stop": [{{ "matcher": "*", "hooks": [{{ "type": "command", "command": "$CLAUDE_PROJECT_DIR/hooks/{name}.sh" }}] }}]
  }}
}}
```

Handler script `hooks/{name}.sh`:

```bash
#!/usr/bin/env bash
# TODO — hook behavior. Event payload arrives on stdin as JSON.
exit 0
```
""",
}

DESTS = {
    "skill": lambda n: ROOT / "skills" / n / "SKILL.md",
    "command": lambda n: ROOT / "commands" / f"{n}.md",
    "agent": lambda n: ROOT / "agents" / f"{n}.md",
    "tool": lambda n: ROOT / "tools" / f"{n}.py",
    "hook": lambda n: ROOT / "hooks" / f"{n}.md",
}


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
    content = body if kind == "tool" else FRONT.format(name=name, flow=flow, domain=domain) + body
    dest.write_text(content, encoding="utf-8")
    print(f"created {dest}")
    if kind in ("skill", "command", "agent"):
        return subprocess.call([sys.executable, str(ROOT / "tools" / "validate.py")])
    return 0


if __name__ == "__main__":
    sys.exit(main())
