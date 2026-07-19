---
name: env-probe
description: Probe the actual environment before assuming it — tool presence/versions, Python/Node runtime, shell dialect, encoding, PATH surprises. Use when first touching a shell on any machine, before writing scripts that call external tools, on "command not found", "is X installed", or any encoding/locale garbage (UnicodeEncodeError, cp1252, mojibake) — assumptions about the environment are bugs on a timer.
derivation: original
flow: lookup
domain: system
---

# Env Probe

## Purpose
Every "works on the author's machine" failure starts with an unprobed assumption. Probing costs one command; the failure it prevents costs a debugging session. Probe on first contact, state findings aloud, then write code against what *is* — not what's typical.

## Probe ladder

1. **Existence + which**: `command -v <tool>` (POSIX; silent, exit-code honest — never parse `which`). PowerShell: `(Get-Command <tool>).Source`.
2. **Version**: `<tool> --version` — pin behavior to the found major (ripgrep 13 vs 14 flag differences are real; python 3.9 vs 3.12 changes stdlib).
3. **Runtime modules**: `python -c "import X"` beats reading requirements files — installed truth over declared intent (`dependency-lookup` owns the deep version).
4. **Shell dialect**: `echo $0` / `$PSVersionTable.PSEdition`. Git Bash on Windows is POSIX-ish over a Windows filesystem — both sets of quirks at once.
5. **Encoding/locale**: `python -c "import sys; print(sys.stdout.encoding, sys.getfilesystemencoding())"` and `locale`. Anything not UTF-8 → set it before running tools, not after they crash.

## Gotchas
- **Windows Python defaults stdout and `open()` to cp1252**, so any script printing or writing `→ ≈ —` crashes with `UnicodeEncodeError: 'charmap' codec can't encode`. Fix at the boundary: `PYTHONUTF8=1` env var (or `-X utf8`) for runs you don't own; `encoding="utf-8"` on every `open()`/`write_text` in code you do own. (This repo's linters are the case study — they crashed exactly this way until wrapped.)
- **`command -v` over `which`**: `which` is non-standard, sometimes an alias, and its output format varies; `command -v` is POSIX and exit-code reliable in scripts.
- **Git Bash path mangling**: arguments that look like POSIX paths (`/foo`) get silently rewritten to `C:/Program Files/Git/foo` when passed to native Windows executables — `MSYS_NO_PATHCONV=1` disables it per-command.
- **Probing PATH ≠ probing the runtime**: `command -v python` finding one interpreter says nothing about which `python` a Makefile, venv, or shebang resolves — probe *inside* the execution context that will run the code.
- **State assumptions aloud** once probed: "assuming Python 3.14, PowerShell 5.1, no plocate" — a wrong stated assumption gets corrected by the user; a silent one gets discovered in production.

## Boundaries
"Which package provides this import / why is this version loaded" → `dependency-lookup`. "Who holds this port/file, where did disk go" → `system-lookup`. Building search indexes once tools are confirmed → `repo-index`.
