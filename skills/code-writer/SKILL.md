---
name: code-writer
description: "Delegate boilerplate code generation to a Haiku subagent when the output is mostly predictable from a reference file — repetitive tests, config, docstrings, type stubs, fixtures, migrations. Point it at the reference and state the contract; worth it on Opus (~19x rate gap), never when already running Haiku. Do NOT use for code needing real design judgment, or where a wrong guess is expensive to detect — the cost is reviewing plausible-looking output, not generating it."
derivation: original
flow: util
domain: agent
---

Spawn a Haiku subagent to draft the boilerplate, then review and land it yourself:

```
Agent({
  subagent_type: "general-purpose",
  model: "haiku",
  description: "Draft <what>",
  prompt: "Reference file: <reference-path>. Generate <spec — what to produce, in what style/format>. Write the result to <target-path> using the Write tool."
})
```

Notes (see bulk-reader's SKILL.md for the measured cost breakdown — same
economics apply: more raw tokens overall, but cheap-model tokens instead of
caller-model tokens, and only a short confirmation lands in your context):

- Each call is independent. To build on what was just generated, pass that
  output file as the new reference for the next call.
- Always review the generated file yourself and make surgical edits for the
  ~5–20% that needs real judgment (edge cases, project-specific conventions,
  correctness) — Haiku output is a draft, not a final answer.
- Don't delegate anything involving architectural decisions, security-sensitive
  logic, or nuanced business rules — only genuinely boilerplate/predictable
  generation, where the input-token cost (reference file + spec) is what
  dominates rather than reasoning depth.
- On Sonnet or Haiku already, weigh whether the generation is large enough to
  outweigh a subagent's ~4-call spawn overhead — for a short function, writing
  it directly is often both faster and cheaper.
