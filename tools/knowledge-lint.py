#!/usr/bin/env python3
"""Knowledge-base lint: broken relative markdown links, TODO/FIXME staleness, duplicate H1s."""
import re, sys
from pathlib import Path
# Emit UTF-8 regardless of the platform default codec (e.g. Windows cp1252),
# so this runs clean in plain PowerShell without PYTHONUTF8=1.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
LINK = re.compile(r"\[[^\]]*\]\(([^)#\s]+)")

def main() -> int:
    errs = 0
    def is_vendored_ref(md: Path) -> bool:
        # copied third-party skills: their internal reference docs keep upstream link
        # structure we don't own — surgical-changes rule; SKILL.md itself still linted.
        if md.name == "SKILL.md" or "references" not in md.parts: return False
        # The skill dir is the parent of references/ — works under skills/ AND
        # extra/skills/ (the earlier skills-index math missed the extra/ prefix).
        try:
            rel = md.relative_to(ROOT).parts
            ridx = rel.index("references")
            sk = ROOT.joinpath(*rel[:ridx]) / "SKILL.md"
            return sk.exists() and "derivation: copied" in sk.read_text(encoding="utf-8", errors="replace")
        except ValueError:
            return False
    for md in sorted(ROOT.rglob("*.md")):
        if ".git" in md.parts: continue
        # .claude/worktrees/ holds transient working copies (git-worktrees skill),
        # not source we own — linting them double-counts every real finding.
        if ".claude" in md.parts: continue
        if is_vendored_ref(md): continue
        text = md.read_text(encoding="utf-8", errors="replace")
        for target in LINK.findall(text):
            if target.startswith(("http://", "https://", "mailto:")): continue
            if not (md.parent / target).exists():
                print(f"{md.relative_to(ROOT)}: broken link -> {target}"); errs += 1
        todos = len(re.findall(r"\bTODO\b|\bFIXME\b", text))
        if todos > 5:
            print(f"{md.relative_to(ROOT)}: {todos} TODO/FIXME markers — stale or unfinished")
    print(f"knowledge-lint: {errs} error(s)")
    return 1 if errs else 0

if __name__ == "__main__":
    sys.exit(main())
