# CC-Executability Checklist

Verify each item before presenting a plan. The reader is a fresh, literal, capable executor with no shared context and no judgment about your risk tolerance.

- [ ] A fresh agent opening only this file could execute it — no "as we discussed," no unstated conventions, no reliance on prior turns.
- [ ] Every irreversible or judgment-bound action is a HARD CONSTRAINT or a HUMAN GATE, placed *before* the tasks that would trigger it.
- [ ] Each task is one verifiable unit — no compound "do X and Y and Z" tasks.
- [ ] Each phase ends with self-checkable Acceptance (command, file-exists, scan, test) — no "looks good" / "feels right" acceptance.
- [ ] Phases are ordered so each ships something and gates the next; scaffolding and guards precede the content they protect, and the guards prove themselves first.
- [ ] An OUT OF SCOPE section names what the agent must not do here.
- [ ] A HUMAN GATES section lists every push / merge / deploy / delete / spend / sign-off; the agent stages, the human performs.
- [ ] Definition of Done is a checklist the agent and human can verify against — nothing in it is uncheckable.
- [ ] The file contains no secrets, internal identifiers, or content the plan's reader should not have.
- [ ] If the user has an existing plan dialect, this matches it.
