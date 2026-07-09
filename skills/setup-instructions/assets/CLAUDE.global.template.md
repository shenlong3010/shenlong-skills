# CLAUDE.md — global

Applies to the entire repository. Directory conventions live in per-directory guides (below). Behavioral master: `archive/RULES-MASTER.md`. Precedence: master wins on behavior; this file and the directory guides win on repo mechanics.

## Hard constraints (read first)
1. <repo-specific constraint — secrets, boundaries, never-touch paths>
2. <irreversible operations that stop for confirmation: deploys, migrations, external sends>
3. <public-repo scan rule, if public>

## What this repo is
<one paragraph: purpose, stack, the one architectural fact that prevents the most wrong assumptions>

## Directory guides
- `<dir>/CLAUDE.md` — <one line on what it carries>

## Commands
```bash
<build>        # verified: <date/session>
<test>         # the single "done" gate
<lint>
```

## Efficiency routing (auto-pickup)
<map naive actions to this repo's skills/tools: "about to grep → X", "raw log → Y" — fire on the action, not the topic>

## Coding behavior (distilled — full form in archive/RULES-MASTER.md)
<the 17 rules, 1–2 lines each, numbered, matching the master's index>
