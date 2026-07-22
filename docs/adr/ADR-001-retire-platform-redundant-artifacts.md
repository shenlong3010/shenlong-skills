# ADR-001: Retire toolbox artifacts the platform does natively

Date: 2026-07-19    Status: Accepted

## Context

The toolbox grew to 49 skills, 10 agents, and 18 commands while Claude Code itself gained overlapping capability: a built-in Explore agent, `/context` accounting, native commit/PR message generation, plan mode, `/code-review`, and system-prompt-enforced parallel tool use. Each overlapping artifact costs standing description tokens (~5.8k total front-load at peak) and — worse — puts a hand-maintained description in routing competition with a platform-maintained equivalent, degrading trigger accuracy for both. The 2026-07 verification campaign proved live tests can distinguish artifacts that add value from those the bare model matches.

## Decision

We will retire any toolbox artifact whose job the platform or model already does as well or better, on evidence rather than sentiment: 18 artifacts deleted in `dc40f61` (explorer, context-audit, parallel-tools, regex-forge, gen-diagram, terse-rewrite, test-scaffold, commit-writer, pr-writer, five `create-*` commands consolidated to one `/create`, grill-me and junior-to-senior folded into surviving critics, repo-orient folded into code-search, chart). The README documents the "deliberately absent" list so the gap reads as policy, not oversight. Campaign verdict `PASS-r` (works, but native baseline equals it) marks future retirement candidates.

## Alternatives considered

- **Keep everything, document boundaries** — rejected: boundary notes don't fix routing competition, and 17 extra surfaces stay in every session's registry.
- **Disable rather than delete** — rejected: disabled artifacts rot invisibly; git history already preserves them for resurrection.
- **Namespace-prefix the duplicates** — rejected: renames muddy provenance and the routing collision remains.

## Consequences

Easier: routing (17 fewer surfaces), maintenance, onboarding to the catalog; standing cost fell 5818→5068 tokens. Harder: workflows that referenced retired names need the native equivalent (README maps them); a platform regression in a native capability would require resurrecting from history. Follow-up debt: the "deliberately absent" list must be re-checked when the platform changes — an absent artifact is a bet on the platform, and bets need re-auditing.
