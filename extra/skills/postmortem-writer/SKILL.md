---
name: postmortem-writer
description: Turn a resolved incident, outage, or debugging saga into a blameless postmortem — evidence-backed timeline, quantified impact, contributing factors, and verifiable action items. Use for "write up what happened", "postmortem this incident", "incident report", after any ERROR-halted or [H]-halted ralph run, or when a session ends in a lesson worth institutionalizing. Do NOT use for deciding an architecture choice (`adr-lite`) or turning the fix into an ops procedure (`runbook-writer`).
derivation: original
flow: deliver
domain: docs
---

# Postmortem Writer

An incident that isn't written up will happen again with better production value. The artifact's job is to convert pain into process — which it can only do if the timeline is evidence-backed and every action item has a machine-checkable "done".

## Method

1. **Gather from real state, not memory.** Reconstruct from artifacts first: git log around the window, PROGRESS.md/HANDOFF.md if a ralph run was involved, logs (`log-triage` output is good raw material), monitoring/alert timestamps, chat where the firefight happened. Memory fills gaps only when marked as recollection.
2. **Build the timeline bottom-up.** Each entry: UTC timestamp + event + *source* (commit sha, log line, ticket). Gaps get stated as gaps ("visibility gap 14:02–14:19") — never smoothed. Mark three moments explicitly: first cause present, first symptom observable, detection.
3. **Quantify impact.** Duration of user-visible impact (not duration of investigation), scope (who/what was affected), and the counterfactual that bounds it. "Users saw errors" is not impact; "checkout returned 500s for ~18 min for EU traffic" is.
4. **Root cause via mechanism, not narrative.** If `systematic-debug` ran during the incident, its step-6/7 conclusion *is* the root-cause section — don't re-derive it differently. State the causal chain: trigger → condition → failure mode → impact.
5. **Contributing factors, blamelessly.** Name systems, defaults, and decisions — never people ("the guard exited 0 on missing state" not "X forgot to check"). Bounded five-whys: stop at the first cause you can act on; whys beyond that become philosophy. Include at least one thing that went *well* — the detection path or mitigation that worked is as repeatable as the failure.
6. **Action items: few and falsifiable.** Each item names an owner, a deadline, and a verification ("guard-dangerous fails loudly on empty state" — testable; "improve monitoring hygiene" — not). Cap the list (3–5); an item nobody will do is noise wearing a checkbox. Split by role: detect sooner / fail safer / mitigate faster.
7. **Summary up top.** One paragraph a newcomer can act on: what broke, why, impact, the one fix that matters most.

## Gotchas

- **Hindsight bias inflates predictability.** Knowing the outcome, every precursor looks obvious. Counterfactual check per finding: *what was knowable at t₀?* Findings that required outcome knowledge are labeled as such or cut.
- **Action-item theater:** the doc ships, the items rot. Every item gets a tracking home before publication (issue, backlog row) — an untracked item is a finding, not a fix.
- **The second-victim pattern:** postmortems that name individuals teach everyone else to hide incidents. Blameless isn't softness; it's the reporting pipeline staying open.

## Boundaries

- Choosing between options going forward → `adr-lite` (a postmortem may spawn one).
- Operationalizing the fix into a checked procedure → `runbook-writer`.
- The pre-incident counterparts are `pre-mortem` (before committing to work) and `plan-reviewer` (before executing a plan).
