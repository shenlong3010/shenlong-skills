#!/usr/bin/env python3
"""Generate a CHANGELOG section from conventional commits since a ref.
Usage: changelog-forge.py [since-ref]   (default: last tag, else full history)"""
import re, subprocess, sys
from collections import defaultdict
from datetime import date

CC = re.compile(r"^(feat|fix|perf|refactor|docs|test|build|chore)(\([^)]*\))?(!)?:\s*(.+)$")
ORDER = ["feat", "fix", "perf", "refactor", "docs", "test", "build", "chore"]
TITLES = {"feat": "Features", "fix": "Fixes", "perf": "Performance", "refactor": "Refactoring",
          "docs": "Docs", "test": "Tests", "build": "Build", "chore": "Chores"}

def main() -> int:
    since = sys.argv[1] if len(sys.argv) > 1 else None
    if not since:
        r = subprocess.run(["git", "describe", "--tags", "--abbrev=0"], capture_output=True, text=True)
        since = r.stdout.strip() or None
    rng = f"{since}..HEAD" if since else "HEAD"
    log = subprocess.run(["git", "log", "--pretty=%s", rng], capture_output=True, text=True).stdout
    groups, breaking = defaultdict(list), []
    for line in log.splitlines():
        m = CC.match(line.strip())
        if not m: continue
        typ, scope, bang, subj = m.group(1), (m.group(2) or "").strip("()"), m.group(3), m.group(4)
        entry = f"- {('**'+scope+'**: ') if scope else ''}{subj}"
        groups[typ].append(entry)
        if bang: breaking.append(entry)
    bump = "major" if breaking else "minor" if groups.get("feat") else "patch"
    print(f"## Unreleased — {date.today().isoformat()}  (suggested bump: {bump})\n")
    if breaking:
        print("### BREAKING\n" + "\n".join(breaking) + "\n")
    for t in ORDER:
        if groups.get(t):
            print(f"### {TITLES[t]}\n" + "\n".join(groups[t]) + "\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())
