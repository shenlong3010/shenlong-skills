---
name: skill-bootstrap
description: Seed the first eval case for a skill that has never run — human-supplied test prompts, a real run, criteria drafted from that real output, human approval before anything counts as ground truth. Use whenever a skill has no eval yet — "just scaffolded <skill>, need test cases", "this skill has no evals", "bootstrap the first eval for <skill>", "seed test prompts", "no run history to extract from". Do NOT use for a skill that has already run (a trace exists → `/eval-writer`) or one that already has a case (iteration → `ralph-plan`).
derivation: original
flow: plan
domain: agent
---

# Skill Bootstrap

## Purpose
The seeding step upstream of `/eval-writer`. Every other eval mechanism in this toolbox presupposes something that does not exist yet for a fresh skill: `/eval-writer` extracts from a prior run trace, `ralph-plan`'s `skill-eval` work-type references an already-authored case. A skill scaffolded by `/create skill` has neither. This skill produces the *first* case — the one nothing else can — and stops there.

## When to use
Right after `/create skill <name>` and enough stub-filling that the skill does something observable. One invocation authors one case for one skill; more cases come from real usage via `/eval-writer`, not from repeated bootstrapping.

## Method

1. **Confirm target and look up its domain.** Read `skills/<name>/SKILL.md` frontmatter for `domain:` — same lookup rule `/eval-writer` uses; never ask the user for a value that is on disk. A command target with no `domain:` falls back to `agent`.

2. **Ask the human for 2–3 realistic test prompts.** Real phrasings they would actually type, not paraphrases of the skill's own description — a prompt echoing the skill's trigger language tests nothing but string matching. **This step has no automated alternative:** no trace exists, so there is nothing to extract from, and inventing prompts here means grading the skill against the same model's guess about its own use.

3. **Run each prompt for real, fresh context per run.** Spawn a `general-purpose` subagent per prompt with an instruction of this shape: *"Read the skill at `<abs path to SKILL.md>` and follow its Method exactly to answer the request below. Follow only what that skill body says. Output the skill's result and nothing else."* — then the prompt verbatim. Fresh context is the point: a run that can see this conversation is grading a rehearsal, not the skill. Sequential, not parallel. Capture output verbatim; a summary of the output is not the output.

   If the target skill reads a fixture (an image, a data file), pass the absolute path — a subagent shares the filesystem but not the conversation, so a relative path or an inline reference to "the diagram above" resolves to nothing.

4. **Draft criteria from the real output.** For each prompt emit `evals/<domain>/<case-id>/` with `prompt.md` (the seeded prompt, verbatim), `graders/criteria.md` (numbered, objectively checkable), and `fixtures/` if the prompt needs them — the identical native layout `/eval-writer` emits, one shape from two producers. `case-id` = `<target-name>-<short-slug>`. Grader law is `/eval-writer`'s, unrestated: **the weakest check that still catches the regression**, objectively checkable over prose-quality judgment.

   Two failure modes specific to drafting from a single run:
   - **Criteria that encode the run's incidental phrasing.** Grade the property, not the sentence that happened to carry it.
   - **Criteria whose answer the skill body already contains.** If `SKILL.md` names the term, count, or example the case grades, the case tests recall of an answer key and proves nothing about the capability. Grep the skill body for the case's load-bearing terms before writing them into criteria; on a hit, either pick different material or label the case a **named-regression guard** in the criteria header, explicitly not evidence of generalization.

5. **Prove each criterion rejects something before showing it to anyone.** Presenting a criterion beside the output it was drafted from proves nothing — they agree by construction, so the human can only catch a criterion that *misdescribes* the run, which is the one error drafting-from-output cannot make. Instead write **degraded twins**: plausible, professional-looking outputs that each break exactly one graded property while satisfying every other criterion. Grade the criteria against them.

   **How many twins.** One per *load-bearing* criterion — the ones whose failure is the reason the case exists. A twin that breaks two criteria at once proves neither independently; split it. Structural criteria (a section is present, a required field appears) can be argued rather than twinned, but say so explicitly in the criteria file: name which criteria have a twin and which rest on argument, so a reader knows which claims were tested and which were asserted. Four criteria with two twins and an honest note beats six criteria with one twin and silence.
   - A criterion that passes its twin does not discriminate — it describes the good run. Rewrite or cut it.
   - Ask of each criterion: *can this fail while every other criterion passes?* One that can only fail alongside another is coupled, and the pair is one test scored twice. Split them.
   - Keep the twin in the case directory (`graders/degraded-<slug>.md`), not in scratch. A verification claim whose evidence was deleted is unfalsifiable by the next reader.
   - **Grade the twin; never write the result from memory.** Record which criteria it passes and which it fails, by reading it. Twice in this skill's own development a from-memory note claimed a twin passed a criterion it failed — once against a criterion with two clauses, where only the first had been checked.

6. **Human-approval gate — mandatory, not advisory.** Present each criterion, its real output, and its degraded twin's graded result. The human approves, edits, or rejects per criterion. **Never auto-accept machine-drafted criteria as ground truth.** A drafted criterion is a hypothesis about what "good" means; only a human confirms it is. Stop here and wait — proceeding on unreviewed criteria is the whole failure this gate exists for. Scope errors surface here too: the human is the one who can say a graded property belongs to a different skill entirely.

7. **Hand off, don't iterate.** With at least one approved case on disk, report the case path(s) and route: `ralph-plan` with work-type `skill-eval` and the case as AC, or direct manual iteration. Grading belongs to `ralph-task-inspector`, fixing to `ralph-coder` — both unchanged, both already provenance-blind about where a case came from.

## Gotchas
- **A brand-new skill's first output is often bad — that is a usable result, not a blocked one.** Draft criteria from what *should* have happened, marked `aspirational — first run failed this` in the criteria file. The first `ralph-plan` task is then honestly bugfix-shaped. The alternative (criteria describing whatever the broken run produced) manufactures a PASS baseline that certifies the bug.
- **Every positive case wants a negative twin.** A case proving the skill fires on X says nothing about whether it fires on everything. Where the skill's value is discrimination — catching a defect without flagging correct material — draft a companion case whose correct answer is "confirm, don't change." Without it, a skill that flags everything scores identically to one that works.
- **Same-model drafting and grading is Success Theater.** The model that drafted criteria will grade its own output favorably against them. Step 5's degraded twin and step 6's human gate exist for this; neither is satisfied by the drafting model re-reading its own criteria and agreeing.
- **A verification note written from memory is worth less than no note.** Every "the twin passes 2, fails 3" claim must come from grading the twin at the time of writing. In this skill's own development three such notes were wrong, each in the same way: a criterion with two clauses, graded on the first. All three were caught by independent review, none by re-reading. If a criterion contains "and", grade both halves separately or split the criterion.
- **Domain lookup, not domain invention.** Writing a case under a `domain:` the target skill does not declare scatters `evals/` into directories nothing routes to.
- **Prefer a fixture to a live URL, and say which a case depends on.** A case whose prompt names a live page grades the internet as much as the skill: the page changes, goes 404, or starts rate-limiting, and the case rots without anyone touching the repo. Snapshot the fetched content into `fixtures/` where the skill's behavior can be exercised against it. When the case genuinely must hit the network — the skill's whole job is retrieval, and a snapshot would test nothing — state in the criteria file that an unreachable URL is an **ERROR, not a FAIL**: a broken oracle, not a failing skill, and the distinction decides whether a human debugs the case or the skill.
- **A skill that writes files makes its own eval cases non-idempotent.** If the target persists output — notes, reports, caches — every eval run mutates the repo, and reruns may hit already-exists paths. Name the write path in the criteria file, confirm it is gitignored, and treat leftover artifacts as run output to clean rather than results to keep.

## Boundaries
A trace already exists → `/eval-writer` (extraction beats seeding whenever there is something to extract). A case already exists → `ralph-plan` for iteration. Authors **one case per seeded prompt** — so 2–3 cases in a typical invocation, matching the 2–3 prompts step 2 asks for. What it does not do is keep producing cases for a skill that now has some: once a first set exists, later regression cases come from real usage through `/eval-writer`, not from re-running bootstrap. Never grades, never fixes the target skill — `ralph-task-inspector` and `ralph-coder` own those, and this skill ends at "a first eval case exists and a human approved it."
