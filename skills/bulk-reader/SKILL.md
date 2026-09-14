---
name: bulk-reader
description: "Delegate bulk file reading to a Haiku subagent. Use when Read or cat/head/tail is blocked by guard-bulk-read.sh for exceeding the line threshold (~400 lines), when answering a question across 3+ files, or when summarizing a large diff — especially on Opus."
derivation: original
flow: util
domain: agent
---

Spawn a Haiku subagent instead of reading the file(s) yourself:

```
Agent({
  subagent_type: "general-purpose",
  model: "haiku",
  description: "Bulk read <file(s)>",
  prompt: "Read <path(s)>. Answer only this question, concisely: <question>. Do not paste large code blocks back unless specifically asked — summarize."
})
```

## Measured economics (2026-09-13)

Real test: 6751-line file (181KB, ~45k tokens), one focused question.

| | Direct read | Delegate to Haiku |
|---|---|---|
| Total tokens spent | ~45k | 140k (3.1x more, mostly Haiku-rate) |
| Tokens entering caller's context | ~45k | ~150 |
| API calls | 1 | 4 |

Delegation costs **more raw tokens**, not fewer — a subagent spawn is 4 API
calls minimum (init, read, reasoning, answer), each with its own system-prompt
overhead. The saving isn't token count, it's **rate**.

- **Running Opus:** Haiku is ~60x cheaper per token. 140k Haiku-tokens costs
  roughly the same as ~2.3k Opus-tokens — delegation wins by ~19x.
- **Running Sonnet:** Haiku is ~5x cheaper. 140k Haiku-tokens costs about the
  same as ~28k Sonnet-tokens — close to breakeven against the 45k direct read,
  delegation still wins but by less.
- **Running Haiku already:** delegating to yourself gains nothing. Just read
  the file.

So: delegate when the caller model is expensive, skip it for small files where
the 4-call spawn overhead dominates regardless of rate — hence the ~400-line
floor on the hook rather than delegating everything.

## Notes

- Each call is independent — no memory across calls. To ask a follow-up, spawn
  again with the same paths; re-sending costs nothing extra in the caller's
  context since the file content never lands there.
- Be specific in the question — a vague prompt makes Haiku return the whole
  file back, which defeats the point and burns the full 3x tax for nothing.
- Verify exact line numbers or values yourself (Read with offset/limit) before
  using them in edits — a summary is for understanding, not surgical precision.
- If the answer is insufficient, refine the question and re-delegate rather
  than falling back to reading the file directly — that's a second 3x tax on
  top of the first.
