---
name: parallel-tools
description: Run independent tool calls in parallel, long commands in background, and fan work out to subagents with token economics in mind. Use when a turn is about to issue several independent reads/searches serially, when a command will run >30s (builds, test suites, installs), or when deciding "should this be a subagent" — serial-by-habit is the waste this skill kills.
derivation: original
flow: session
domain: agent
---

# Parallel Tools

## Purpose
Three levers turn wall-clock and context waste into throughput: batched parallel tool calls, background execution, and subagent fan-out. Each has a precise applicability test — parallelism applied to dependent steps produces garbage faster.

## Method

**1. Batch independent calls.** Before issuing a tool call, ask: does its input depend on any earlier call's *output*? No → batch every such call into one message (multiple Reads, Read + Grep + Glob, several git inspections). One round-trip instead of N.
- Dependence test is on **outputs, not topic**: "read the file the grep finds" is dependent; "read these three known files" is not.

**2. Background long commands.** Anything >~30s that produces a *result later* — builds, full test suites, installs, downloads — runs in background; work continues, completion notifies. Foreground-blocking on a 5-minute build is a turn wasted.
- Keep foreground: anything whose output the very next step consumes, and anything interactive.

**3. Subagent fan-out.** Spawn when the work is (a) self-contained — describable in one prompt without the conversation, (b) bulky — would flood this context with intermediate output, and (c) reducible — a short report is the only thing needed back. Broad codebase sweeps, isolated review passes, per-module audits.
- Keep inline: anything needing session context, anything cheap, anything whose intermediate steps matter to the user.

## Gotchas
- **Parallel writes to one file = last-writer-wins corruption.** Batch reads freely; edits to the *same* file stay serial. Different files parallel-edit fine.
- **Background + `cd`-dependent commands**: background shells don't inherit later directory changes — absolute paths in backgrounded commands, always.
- **Subagent economics flip on small tasks**: a spawn costs a cold start (system prompt + context re-derivation, easily 10-20k tokens). A task under ~5 tool calls is cheaper inline even when it "feels delegatable".
- **Fan-out correlation**: N same-model subagents reviewing N modules share blind spots — parallel review widens coverage, not independence (same caveat as the repo's reviewer agents).
- **Don't poll background work** — completion notifies. A sleep-check loop burns turns exactly where background execution was supposed to save them.

## Boundaries
Token-budget policy for *search output* belongs to `code-search`; model-tier choice to `reasoning-budget-guidance`; prompt/tool caching to `caching`. Loop-structured multi-task execution (state on disk, roles, retries) is the ralph loop (`ralph-next`), not ad-hoc fan-out.
