---
name: setup-instructions
description: Scaffold the layered AI-instruction architecture in any repository — global CLAUDE.md, per-directory CLAUDE.md guides, a behavioral rules master, AGENTS.md, and .github/copilot-instructions.md. Use when starting a new repo, when asked to "set up CLAUDE.md", "add AI instructions", "create agent instructions for this project", or when migrating an existing monolithic CLAUDE.md to the layered form. Do NOT use inside the toolbox repo itself — it is the reference implementation this skill copies.
derivation: original
flow: meta
domain: agent
---

# Setup Instructions

Installs the one-master-many-adapters instruction architecture: behavior rules live once in a master file; each surface gets a thin adapter; each directory gets only its local conventions. No rule exists at two levels.

## Step 1 — Inventory (read before write)

- Existing instruction files? `CLAUDE.md`, `AGENTS.md`, `.github/copilot-instructions.md`, `.cursorrules`, etc. **Migration rule:** never overwrite an existing monolith — preserve it verbatim at `archive/CLAUDE-v1.md` and reference it from the new root file.
- **Refuse the reference repo:** if this repo IS the toolbox that ships this skill (check: a `skills/setup-instructions/` dir exists, or the root README names it the reference implementation), STOP — it is the source this skill copies from, not a target. Say so and exit; do not scaffold over the master.
- Real commands: extract build/test/lint invocations from the manifest, Makefile/justfile, or CI config — CI is ground truth. For a full pass, run `code-search`'s first-contact orientation first.
- Candidate directories for local guides: only dirs with genuinely local conventions (`src/`, `tests/`, `infra/`, `migrations/`). An empty guide is noise — skip dirs that would only restate globals.

## Step 2 — Elicit the repo-specifics (brief, batched)

Ask once, together: (a) public or private — public repos get a secrets/terms scan constraint; (b) the single verify command that gates "done"; (c) irreversible operations specific to this repo (deploys, migrations, external sends) — these become named stops; (d) paths the agent must never touch.

## Step 3 — Generate, in this order

1. `archive/RULES-MASTER.md` ← copy `assets/rules-master.md` verbatim (17 rules, attribution intact). Behavior lives here, once.
2. Root `CLAUDE.md` ← `assets/CLAUDE.global.template.md`: hard constraints first (from step 2), identity paragraph, **verified** commands block, directory-guides index, the 17 rules distilled to 1–2 lines each with a pointer to the master.
3. Per-directory `CLAUDE.md` ← `assets/CLAUDE.dir.template.md`, one per qualifying directory: local conventions only.
4. `AGENTS.md` ← `assets/AGENTS.template.md` and `.github/copilot-instructions.md` ← `assets/copilot-instructions.template.md`: global-only distillations — those surfaces don't load directory files, so their authoring notes stay inline. Copilot's file is injected into every request; keep it the tightest of the set.

Write the precedence line into the root file: master wins on behavior; root and directory files win on repo mechanics.

## Step 4 — Verify before presenting

- Every command listed was actually run in this session, or is explicitly marked unverified (evidence over claims).
- No rule appears at two levels — spot-check by grepping a distinctive phrase from each global rule against the directory guides.
- Size discipline: root ≤ ~100 lines, directory guides ≤ ~40, Copilot file ≤ ~25. Compliance is **constant-sum** — every added rule dilutes attention on the others; over budget means a rule must leave, not that the cap grows.
- Every NEVER is paired with its do-instead in the same breath ("never commit X — fetch it via Y"); an unpaired prohibition invites workarounds.
- All referenced paths exist.

## Boundaries

- Never invent build/test commands — a wrong command in an instruction file misleads every future session.
- Directory-guide loading is a Claude Code feature; AGENTS.md and Copilot get flat global files only — do not promise hierarchy on those surfaces.
- Migrating rules content from an existing file is editing, not authoring — preserve attribution the original carried.
