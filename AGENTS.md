# AGENTS.md

Instructions for any coding agent working in this repository. Tool-agnostic mirror of `CLAUDE.md`; behavioral master with full rule text: `archive/CLAUDE-v2-full.md`.

## Constraints

- Public repo: zero employer-internal content (names, terms, tokens). Pipeline is one-way: public → internal, never reverse.
- Never commit `vendor/anthropic/` (proprietary, gitignored, local-fetch only via `tools/fetch-doc-skills.sh`).
- Never push to a remote; stage and commit locally only.
- Adapted/copied content carries `derivation:` + `source:` frontmatter and a README credits entry.

## Verify

```bash
python3 tools/validate.py && python3 tools/skill-lint.py && python3 tools/knowledge-lint.py
bash tools/scan.sh          # staged-changes secret + wordlist scan; must pass
```

All green before any commit — this is the single "done" gate for repo changes.

## Authoring

Scaffold, don't hand-roll: `python3 tools/scaffold.py <skill|command|agent|tool|hook> <name>`. Frontmatter is flat (`name`, `description` with explicit trigger language, `derivation`, `source`, optional `license`) — no nested metadata block.

Note for non-Claude agents: `skills/`, `commands/`, and `agents/` are Claude-Code-native artifacts. Treat them as reference documents — read the relevant SKILL.md and follow it manually; nothing auto-loads on other surfaces.

## Efficiency routing

Lookup tasks route to the matching skill doc before naive tooling: code text → `skills/code-search`, JSON/YAML → `skills/data-query`, filenames → `skills/file-find`, git history → `skills/git-search`, web pages → `skills/web-research`, runtime who/what → `skills/system-lookup`, dependency provenance → `skills/dependency-lookup`, log dumps → `skills/log-triage`. Search output stays ≤ ~15% of context.

## Rules (distilled — full form in archive/CLAUDE-v2-full.md)

1. Think before coding — surface assumptions; ambiguity → present options or ask.
2. Simplicity first — minimum code; nothing speculative.
3. Surgical changes — only what the request requires; match existing style.
4. Read before write — never edit a file from memory of its contents.
5. Goal-driven — machine-verifiable "done" before code; per-step verify in plans.
6. Verification — reproducing test → fix → passing test = fixed; run the check before claiming done.
7. Debugging — read the actual error; reproduce first; one variable per experiment.
8. Dependencies — stdlib first; document why + tradeoff; pin versions.
9. Environment — probe tools/versions; state platform assumptions.
10. Secure by default — parameterized queries; env-var secrets; validate at trust boundaries; no PII/credentials in logs.
11. Reversibility — irreversible actions (delete, push, publish, migrate, spend) stop for explicit confirmation.
12. Idempotence — check-before-create; steps re-runnable and resumable.
13. Checkpoints — commit every green verifiable unit.
14. Context economy — load selectively; summarize once; restart with a handoff when history dominates.
15. Honest uncertainty — precise doubt beats confident vagueness.
16. Evidence over claims — report the diff, the check, its output; no success theater.
17. Failure modes — scope creep, duplication ignored, happy-path-only, runaway refactor, identical retries, unverified "done" → stop and surface.
