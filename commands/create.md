---
name: create
description: Scaffold a new skill, command, agent, tool, or hook in this toolbox — standard frontmatter, correct directory placement, immediate validation. Use whenever adding any toolbox artifact — never hand-roll the file.
derivation: original
flow: meta
domain: agent
---

# /create

## Invocation
`/create <skill|command|agent|tool|hook> <name>`

## Behavior
1. Run `python3 tools/scaffold.py <kind> <name>` (scaffold owns placement and runs validate.py automatically).
2. Open the generated stub and fill every TODO — especially the description: write it pushy, listing concrete trigger phrases (events, not topics), because undertriggering is the common failure mode. For skills, add a "Do NOT use for" boundary when confusable with a sibling.
3. Confirm `tools/validate.py` reports clean.
4. If the content is adapted from an upstream, set `derivation: adapted` and add `source: <url>`.
5. Regenerate catalogs: `python3 tools/gen-index.py`.
