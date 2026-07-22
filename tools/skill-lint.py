#!/usr/bin/env python3
"""Description trigger-quality lint. Undertriggering is the common skill failure:
descriptions must say WHEN to use, not just what. Warnings, exit 0 unless --strict."""
import re, sys
from pathlib import Path
# Emit UTF-8 regardless of the platform default codec (e.g. Windows cp1252),
# so this runs clean in plain PowerShell without PYTHONUTF8=1.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
FM = re.compile(r"\A---\s*\n(.*?)\n---", re.S)
TRIGGER_WORDS = ("use when", "use whenever", "use for", "use after", "use before", "use on", "trigger", "invoke", "consult", "use this")

def desc_of(p: Path):
    m = FM.match(p.read_text(encoding="utf-8", errors="replace"))
    if not m: return None
    d, cap = m.group(1), False; out = []
    for line in d.splitlines():
        if line.startswith("description:"):
            out.append(line.split(":", 1)[1].strip()); cap = True
        elif cap and line.startswith((" ", "\t")):
            out.append(line.strip())
        elif cap:
            break
    return " ".join(out)

def main() -> int:
    warn = 0
    targets = list((ROOT/"skills").glob("*/SKILL.md")) + list((ROOT/"commands").glob("*.md")) + list((ROOT/"agents").glob("*.md"))
    for p in sorted(t for t in targets if t.name != "CLAUDE.md"):
        d = desc_of(p)
        rel = p.relative_to(ROOT)
        if not d:
            print(f"{rel}: no description"); warn += 1; continue
        if len(d) < 60:
            print(f"{rel}: description too thin ({len(d)} chars) — add trigger conditions"); warn += 1
        if not any(t in d.lower() for t in TRIGGER_WORDS):
            print(f"{rel}: no trigger language ('use when…') — undertrigger risk"); warn += 1
        if len(d) > 1200:
            print(f"{rel}: description bloated ({len(d)} chars) — costs every session"); warn += 1
    total = sum(len(desc_of(x) or "") for x in targets if x.name != "CLAUDE.md")
    print(f"skill-lint: {warn} warning(s); standing description cost ≈ {total // 4} tokens")
    return 1 if (warn and "--strict" in sys.argv) else 0

if __name__ == "__main__":
    sys.exit(main())
