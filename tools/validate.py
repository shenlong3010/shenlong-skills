#!/usr/bin/env python3
"""Thin toolbox validator.

Checks every artifact in skills/, commands/, agents/:
  - YAML frontmatter present with non-empty `name` and `description`
  - skills are folders containing SKILL.md; commands/agents are flat .md files
  - if the frontmatter declares a non-original derivation, a `source:` line must exist
  - `flow:` present and one of the fixed vocabulary (drives the generated catalogs)

Exit 0 = clean, 1 = violations (printed as path: reason).
"""
import re
import sys
from pathlib import Path
# Emit UTF-8 regardless of the platform default codec (e.g. Windows cp1252),
# so this runs clean in plain PowerShell without PYTHONUTF8=1. Error strings
# here interpolate artifact paths and frontmatter values, which can be non-ASCII.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
FM = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
FLOWS = ("plan", "execute", "review", "debug", "lookup", "deliver", "session", "util", "meta", "career")
DOMAINS = ("code", "git", "data", "web", "docs", "media", "system", "agent", "process", "career")


def frontmatter(text: str):
    m = FM.match(text)
    if not m:
        return None
    fields = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith((" ", "\t", "#")):
            k, _, v = line.partition(":")
            fields[k.strip()] = v.strip()
    return fields


def check_file(path: Path, errors: list):
    fm = frontmatter(path.read_text(encoding="utf-8", errors="replace"))
    if fm is None:
        errors.append(f"{path}: missing frontmatter")
        return
    for key in ("name", "description"):
        if not fm.get(key):
            errors.append(f"{path}: frontmatter missing `{key}`")
    derivation = fm.get("derivation", "original")
    if derivation != "original" and not fm.get("source"):
        errors.append(f"{path}: derivation `{derivation}` but no `source:` line")
    flow = fm.get("flow")
    if not flow:
        errors.append(f"{path}: frontmatter missing `flow` (one of {', '.join(FLOWS)})")
    elif flow not in FLOWS:
        errors.append(f"{path}: unknown flow `{flow}` (allowed: {', '.join(FLOWS)})")
    domain = fm.get("domain")
    if not domain:
        errors.append(f"{path}: frontmatter missing `domain` (one of {', '.join(DOMAINS)})")
    elif domain not in DOMAINS:
        errors.append(f"{path}: unknown domain `{domain}` (allowed: {', '.join(DOMAINS)})")


def main() -> int:
    errors: list = []

    skills = ROOT / "skills"
    if skills.is_dir():
        for entry in sorted(skills.iterdir()):
            if entry.name.startswith(".") or entry.name == "CLAUDE.md":
                continue
            if not entry.is_dir():
                errors.append(f"{entry}: skills/ entries must be folders containing SKILL.md")
                continue
            sk = entry / "SKILL.md"
            if not sk.is_file():
                errors.append(f"{entry}: missing SKILL.md")
            else:
                check_file(sk, errors)

    for dirname in ("commands", "agents"):
        d = ROOT / dirname
        if d.is_dir():
            for f in sorted(d.glob("*.md")):
                if f.name == "CLAUDE.md":
                    continue
                check_file(f, errors)

    if errors:
        print("\n".join(errors))
        return 1
    print("validate: clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
