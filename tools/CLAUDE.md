# tools/ — directory guide

Loaded when working in this directory; root globals apply. Tools are runnable scripts (Python, bash) that enforce or automate repo conventions.

## Laws
- **Stdlib only** unless a dependency is explicitly justified and documented (root rule 8) — every current tool is stdlib; keep it that way.
- Every script carries a module docstring with usage; arguments via argparse or a documented argv contract.
- **Exit codes mean things:** 0 clean · 1 findings/failure · 2 usage error. Linters distinguish warnings from errors and take `--strict` to escalate (`skill-lint` pattern).
- **Scanners redact:** report `file:line` and counts only — never the matched secret or term (`scan.sh` pattern). This is what lets scan output live in public CI logs.
- **Idempotent by construction:** check-before-create, refuse-overwrite (`scaffold.py` pattern); a re-run after a crash must be safe.
- New tools via `/create tool <name>`.
