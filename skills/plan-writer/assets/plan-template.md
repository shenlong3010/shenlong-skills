# PLAN — <Title>

**Audience:** A Claude Code session executing this build. Human owner: <name>.
**Objective:** <one sentence — the end state>.
**Non-goal:** <what this explicitly does not do>.
**Execution surface:** <what runs this and what it may assume — tools, repo/working dir, conventions it must follow>.

---

## ⚠ HARD CONSTRAINTS (read before any task)

State every irreversible or dangerous boundary here, before the tasks. The agent reads top-to-bottom and acts.

1. <constraint> — <why it matters>.
2. <constraint> — <why it matters>.

---

## <Structure / Context>  *(optional — repo layout, key paths, conventions the agent needs)*

```
<tree or key paths>
```

---

## Phase 0 — Scaffold + Safety (prove the guards before any content)

- [ ] <scaffold task>
- [ ] <guard task — the safety mechanism that later phases rely on>
- [ ] **Acceptance:** <plant the failure case, confirm the guard catches it, revert>. Guards proven before real work.

---

## Phase N — <name>

- [ ] <task — one verifiable unit>
- [ ] <task — one verifiable unit>
- [ ] **Acceptance:** <command / file-exists / scan-passes / test-green — self-checkable, no vibes>.

---

## OUT OF SCOPE — do NOT do these here

- <thing deliberately excluded> — <where it belongs instead, if anywhere>.

---

## HUMAN GATES (agent stops; does not auto-proceed)

The agent stages; the human performs the irreversible act.

- <push / merge / deploy / delete / spend / sign-off> — agent prepares it, human performs it after <condition>.

---

## Definition of Done

- [ ] <verifiable end-state check>
- [ ] <verifiable end-state check>
