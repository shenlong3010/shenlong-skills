---
name: runbook-writer
description: Turn a procedure into an operational runbook with verification after every step. Use for "write a runbook", "document this procedure", "on-call doc for X".
derivation: original
---

# Runbook Writer

## Structure
1. **Title + trigger:** the exact symptom/alert that means "use this runbook".
2. **Preconditions:** access needed, tools installed, safety state (traffic drained? backup taken?).
3. **Steps:** each step = one action with the literal command (copy-pasteable, placeholders in <angle-brackets>), followed by a **Verify:** line — the observable result that proves the step worked. A step without verification is a hope.
4. **Rollback:** per irreversible step, how to undo — written before it is needed.
5. **Escalation:** the condition that means stop-and-page, and to whom.

## Rules
Assume the reader is competent but has zero context and is at 3 a.m. — no unstated tribal knowledge, no "restart the service" without the command. Test-read: could the steps be executed exactly as written? If a step needs judgment, state the decision rule, not just the choice.
