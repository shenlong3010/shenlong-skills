---
name: create-command
description: Scaffold a new command in this toolbox with standard frontmatter, correct directory placement, and immediate validation. Use whenever adding a command — never hand-roll the file.
derivation: original
---

# /create-command

## Invocation
`/create-command <name>`

## Behavior
1. Run `python3 tools/scaffold.py command <name>`.
2. Open the generated stub and fill every TODO — especially the description: write it pushy, listing concrete trigger phrases, because undertriggering is the common failure mode.
3. Confirm `tools/validate.py` reports clean (scaffold runs it automatically).
4. If the content is adapted from an upstream, set `derivation: adapted` and add a `source: <url>` line.
