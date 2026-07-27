# Pass criteria — talk-notes-countable-claim-unseen

> **Why this case exists.** `talk-notes-homophone-garble` grades a defect whose exact wording an
> earlier draft of Method step 8 quoted as its worked example — so it can only prove that known
> defect does not regress, never that step 8 fires cold. This case is its generalization
> counterpart: **none of the terms, counts, or claims graded here appear anywhere in
> `skills/talk-notes/SKILL.md`**, verified by grep at authoring time. A PASS here is evidence
> that step 8's abstract trigger shapes (counts / exclusivity / support) actually fire on unseen
> material. A FAIL here while `homophone-garble` passes would be strong evidence that step 8
> works only as an answer key and not as a rule — the single most useful signal this suite can
> produce about that step.

Real video (Awesome channel, "Postgres is dropping a crazy new feature", `zPsr0n9DQ7o`) — the
same source as `talk-notes-standard-year-precision`, graded on different claims. That case tests
a wrong *date* on correctly-named standards; this one tests **countable and exclusivity claims**,
which are step 8's territory rather than step 5's.

Deliberately mixed: two claims here are **correct** and must be confirmed, one is a **real
caption garble** that must be corrected. A run that "corrects" its way through all three fails as
badly as one that confirms all three.

Ground truth (verifiable against ISO catalogue records and PostgreSQL's own documentation):

- **"the ISO committee, which defined two languages"** — **CORRECT, confirm it.** Exactly two:
  SQL/PGQ (ISO/IEC 9075-16:2023) and GQL (ISO/IEC 39075:2024), both from SC32 WG3. A count-shaped
  claim that happens to be right — the case for verifying counts rather than assuming a count in
  an auto-caption is suspect.
- **"Postgres 19 only supports fixed-depth pattern matching for now"** — **CORRECT, confirm it.**
  An exclusivity claim ("only supports"), accurate for this release: variable-length path
  quantifiers are absent from the documented `GRAPH_TABLE` syntax and deferred to a future
  version. Note the docs confirm this by *absence* of quantifiers rather than an affirmative
  "not supported" sentence — do not fail a run for citing release coverage alongside the docs.
- **"a customer node, an arrow through a boat edge, a product node"** — **GARBLE, correct it.**
  The speaker said **"a bought edge"**: the worked example throughout is customer→bought→product.
  "Boat" is a correctly-spelled common word substituted for another common word, in a technical
  gloss where it reads as a plausible (if odd) label. No proper noun, no comparison — step 6 and
  step 7 do not fire on it.

1. **The count claim is confirmed, not corrected.** "Two languages" is accurate. The Verification
   log must show it checked with an outcome of confirmed. Marking it corrected or unresolved is a
   false positive and a FAIL — this criterion guards against a step-8 implementation that treats
   every number in an auto-caption as suspect.
2. **The exclusivity claim is confirmed, not corrected.** "Only supports fixed-depth pattern
   matching" is accurate for Postgres 19. Same grading as criterion 1: confirmed in the log, not
   flagged.
3. **The "boat edge" garble does not reach the notes as a technical term.** The reader-facing
   notes must not present "boat edge" as an edge type, label, or table name. PASS if the notes
   render it correctly as a `bought` edge (customer→bought→product), or omit the specific edge
   label while describing the pattern. A notes body containing "boat edge" as if it were real
   schema vocabulary is a FAIL.
4. **Verification log covers all three claims above** — term/claim, source consulted, tries,
   outcome — regardless of whether each turned out right or wrong. Per the suite's standing law,
   a log that lists only the corrected item is evidence the pass ran selectively; confirmed items
   must appear too.

A PASS requires all four. Criteria 1 and 2 are the load-bearing ones for this case's stated
purpose: they test whether step 8 *discriminates*, since a step that flags every count and every
"only" would satisfy criterion 3 while making the skill useless on accurate technical content.
