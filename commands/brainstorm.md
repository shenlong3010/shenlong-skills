---
name: brainstorm
description: Socratic refinement of a rough idea into a design brief — before any plan exists. Use when a project or feature is still a vague notion. Use at project inception — "help me think through X", "brainstorm this", "I have an idea", or any vague goal that would otherwise go straight to code. Upstream of plan-writer; output feeds it.
derivation: adapted
source: https://github.com/obra/superpowers
---

# /brainstorm

## Invocation
`/brainstorm <rough idea>`

## Behavior
1. **One question at a time.** Ask the single most clarifying question, wait, then the next. A wall of ten questions gets ten shallow answers; sequential questions compound.
2. Keep an **assumption ledger**: every assumption either party makes gets written down as confirmed / unconfirmed. Unconfirmed assumptions are the backlog of questions.
3. Probe in this order: the problem (who hurts, how much, what happens if nothing is built) → constraints (time, surface, dependencies, non-negotiables) → success criteria (observable, not vibes) → non-goals (what this deliberately won't do).
4. Present the emerging design in **digestible chunks for sign-off** — a section at a time, not one final reveal. Disagreement on chunk 2 is cheap; on the finished brief, expensive.
5. Converge to a brief: Problem / Users / Constraints / Success criteria / Non-goals / Open questions. Save it as `BRIEF.md`.
6. End by offering the chain: `plan-writer` to turn the brief into an executable plan, `pre-mortem` to attack it first.

## Rules
No solutions during problem exploration — proposing an architecture in question 2 anchors everything after. If the user's answers contradict the ledger, surface the contradiction immediately rather than averaging it away.
