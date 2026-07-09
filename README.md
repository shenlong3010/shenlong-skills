# shenlong-skills

Personal Claude Code toolbox: skills, slash commands, subagents, hooks, MCP scaffolds, output styles, and instruction templates, packaged as a plugin so one install makes everything available in any project.

## Install

**Plugin (preferred):** add this repo as a local plugin — the `.claude-plugin/plugin.json` manifest wires commands, agents, skills, and hooks.

**Symlink fallback:** `./install.sh` links leaf folders into `~/.claude/skills`, `~/.claude/commands`, and `~/.claude/agents`.

**Copilot / other surfaces:** no auto-load; reference the SKILL.md text manually. Hooks and plugin machinery do not transfer.

## Layout

```
.claude-plugin/   plugin manifest
skills/           agent-consumed skills (folder per skill, SKILL.md inside)
commands/         slash commands (flat .md)
agents/           subagents (flat .md)
hooks/            lifecycle hook templates + hooks.json
mcp/              MCP configs and scaffolds (env-var keys only — never commit credentials)
styles/           output styles
templates/        CLAUDE.md / AGENTS.md starters, settings presets
tools/            validate.py, scaffold.py, scan.sh, vendor_anthropic.sh
plan/             the build plans (PLAN-1 … PLAN-5)
```

Instruction hierarchy: root `CLAUDE.md` is global; `skills/`, `agents/`, `commands/`, `tools/` each carry a directory `CLAUDE.md` with local conventions; `archive/CLAUDE-v2-full.md` is the behavioral master; `AGENTS.md` and `.github/copilot-instructions.md` are global-only surface adapters.

## Authoring

Use the creators — do not hand-roll files:

```
/create-skill <name>     /create-command <name>     /create-agent <name>
/create-tool <name>      /create-hook <name>
```

All five call `tools/scaffold.py`, which writes standard frontmatter and runs `tools/validate.py` immediately.

## Guard

This repo is public. `tools/scan.sh` (wired via `.pre-commit-config.yaml`) scans staged changes for secret patterns and for terms in a local `.wordlist` file. The wordlist is **gitignored and must be authored locally before the first real commit** — an absent or empty wordlist makes that half of the scan pass vacuously. Scan output prints file and line only, never the matched term. Migrated hand-written skills must pass the scan before their first commit.

## Vendoring

Third-party skills are pulled with `tools/vendor_anthropic.sh` (pins a SHA, reminds you to verify the upstream license before committing). Vendored files keep their upstream license; carry a `source:` line in frontmatter and a credits entry below.

**Exception — Anthropic document skills (docx / pdf / pptx / xlsx):** these are `license: Proprietary` (all rights reserved; see each skill's LICENSE.txt) and must never be committed or republished. `tools/fetch-doc-skills.sh` pulls them into `vendor/anthropic/` (gitignored) for local use. The canonical `skills/{docx,xlsx,pptx,pdf}` are committable originals (python-docx / openpyxl / python-pptx / pypdf + reportlab); the vendored proprietary set stays optional for advanced OOXML features (tracked changes, comments, template surgery).

## Credits

- `plan-writer`, `read-diagram`, creators, and tooling: original.
- Vendored skills: see each file's `source:` frontmatter line.
- `image-ocr`: adapted from benchflow-ai/skillsbench (Apache-2.0).
- Anthropic doc skills: local-fetch only, proprietary — not part of this repo's published content.

## License

MIT for original content in this repo. Vendored items retain their upstream licenses (noted per file).
