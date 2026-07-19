---
name: plan-writer
description: Write an execution-ready plan that another agent — Claude Code by default — can run top-to-bottom without prior context. Use this whenever the user wants a plan, build plan, spec, roadmap, or implementation plan, especially one to hand off to, export to, or execute in Claude Code or any coding agent. Trigger even when the user says "turn this into a plan," "write a plan for X," "something I can give to Claude Code," or describes a multi-step build they want captured as executable steps — not only when they say the words "plan" or "skill" explicitly. Produces a phased markdown plan with hard constraints up front, self-checkable acceptance per phase, explicit human gates for irreversible actions, and a Definition of Done.
metadata:
  owner: Luke
  enforcement: advisory
  derivation: original
flow: plan
domain: process
---

# Plan Writer

Produce a plan that a *fresh* coding agent (Claude Code by default) can execute top-to-bottom. The reader is a literal, capable executor with **no shared context** and **no judgment about your risk tolerance**. Every rule below follows from that one fact. A plan written for a human can lean on shared assumptions and on the human pausing when something feels off; an agent has neither. Write accordingly.

## Intake — extract from the conversation first, ask only the gaps

The conversation usually already answers most of this. Pull what's there; confirm briefly; ask only what's genuinely missing. Do not interrogate.

Minimum set needed to write an executable plan:

1. **Objective** — the end state, one sentence.
2. **Execution surface** — what runs the plan (default: a Claude Code session) and what it may assume: tools available, repo/working dir, conventions it must follow. If it must follow conventions the agent can't infer, state them inline or point to a file in the repo.
3. **Irreversible or judgment-bound actions** — anything that needs a human: push to a remote, deploy, delete data, spend money, accept terms, legal/IP sign-off, writes to prod. These become explicit STOP points, not steps the agent performs.
4. **Scope boundaries** — what is explicitly *out* of scope, so the agent doesn't wander.
5. **Success criteria** — how "done" is verified.

If the user signals they just want it drafted ("just write it"), infer sensibly, state any assumption inline in the plan, and proceed.

## What makes a plan Claude-Code-executable

- **Self-contained.** No "as we discussed," no unstated conventions, no reliance on prior turns. A new agent opening only this file must be able to act. If context is needed, embed it or point to a path in the repo.
- **Hard constraints first.** The agent reads top-to-bottom and acts. Anything dangerous or irreversible must appear as a constraint *before* the tasks that could trigger it — never buried mid-plan. Placement is load-bearing because the reader executes in order.
- **One verifiable unit per task.** No compound "do X and Y and Z" tasks. One task = one thing that can be checked. This is also the steering granularity if the plan is run in a loop.
- **Acceptance per phase, self-checkable.** Each phase ends with a check the agent can run itself: a command, a file-exists test, a passing scan, a green test. No "looks good" acceptance — an agent can't grade vibes.
- **Phased so each phase ships and gates the next.** Order phases so each produces something verifiable and later phases depend on earlier acceptance. Scaffolding, guardrails, and safety checks come *before* the content they protect — and prove themselves (e.g., plant the failure case, confirm the guard catches it) before real work begins.
- **Mark every human gate explicitly.** Irreversible/judgment-bound actions get a dedicated section. The pattern is: the agent *stages* (writes the commit, prepares the PR, drafts the change); the human *performs* the irreversible act (push, merge, deploy, sign off). The agent must not auto-proceed past a gate.
- **State what NOT to do.** An OUT OF SCOPE section prevents scope creep and stops the agent from "helpfully" doing the thing you deliberately excluded.
- **Definition of Done.** A final checklist the agent and the human verify against. If it can't be checked, it isn't done.

## Output

- **Write a file, not an inline answer.** The plan is handed to another agent and/or committed. Inline defeats the purpose.
- Use `assets/plan-template.md` as the skeleton. If the user has an existing plan dialect visible in context (their own `PLAN-*.md` files, a house format), **match it** — fidelity to their dialect is what lets the plan slot into their existing set and makes downstream import a copy, not a transform.
- Default path: `PLAN-<slug>.md` in the outputs directory. Slug from the objective.
- Before presenting, **self-check against `references/cc-executability-checklist.md`**. Fix anything that fails. Then present the file.

## After writing

Present the file with a short summary of phase order and where the human gates are. Then offer — do not force — to:

- dry-run the phase order (walk the dependency chain without executing),
- add scope or acceptance detail to any phase,
- or test the plan by executing Phase 0 yourself to confirm it's actually runnable.

## Example — the human-gate principle in action

A plan that ends in publishing a repo should not contain a `git push` task. It contains a HARD CONSTRAINT ("the agent never pushes to a public remote") and a HUMAN GATE ("repo is staged and committed locally; the human performs the push after IP/legal sign-off"). The agent does everything up to the irreversible line and stops there. Same shape for deploys, deletes, spends, and merges.
