# Pass criteria — read-eng-blog-figure-contradicts-prose

Seeded by `skill-bootstrap` from a real first run. Criteria checked against degraded twins
before approval.

**Live-URL case — an unreachable page is an ERROR, not a FAIL.** The prompt names
`https://www.cockroachlabs.com/blog/vehicle-search-sql-vector-embeddings/`. A 404, paywall, or
rate-limit is a broken oracle: record ERROR, fix the case, do not score the skill. No fixture is
snapshotted — the graded property is retrieval of material the static HTML does not contain, and
a snapshot of the rendered page would supply exactly what the case tests.

**Write side effect.** The skill persists to `notes/eng-blogs/vehicle-search-sql-vector-embeddings.md`.
`notes/` is gitignored. A leftover file from a previous run is run output to delete, not a result
to keep — and the grader must read the run's output, not the file on disk.

This case is the **figure-vs-prose branch** of Step 2. Its companion case
`read-eng-blog-hidden-code-blocks` grades recovering artifacts the prose merely *fails* to
include. Here the figures actively **contradict** the prose, which is a strictly harder property:
an output can retrieve every figure and still, by trusting the body text, report the wrong
number. Neither case covers the other.

Answer-key check: `SKILL.md` names Playwright, `scrollIntoView()`, `currentSrc`, the
blank-screenshot gotcha, and the "figure you can't retrieve → say so" rule — all out of bounds as
graded material. **`SKILL.md:36` also says to incorporate the diagram "not its alt-text"**, so the
general instruction *don't settle for describing a figure* is skill-body material and is not what
criterion 2 grades; criterion 2 is scoped to the quantitative axis read, which the skill body
nowhere supplies. No price, no variance percentage, no distance value, and no vector ID appears in
the skill body — verified by grep at authoring time. That is the scope of the claim: specific
graded values, not every concept the criteria touch.

1. **The screenshot's Camaro price is reported, and the conflict with the prose is stated.** The
   article body gives the 1969 Camaro at **$335,000**; the result screenshot shows **$33,445**. A
   PASS reports the figure's value *and* says the two disagree. Reporting only $335,000 FAILs:
   that is the summarizing-fetcher outcome the skill exists to prevent, and the reader is left
   with a wrong number. Reporting only $33,445 with no mention of the discrepancy also FAILs —
   silently picking the right source is not the same as flagging that the post is internally
   inconsistent, and the reader cannot tell the figure was even consulted.

   This is the load-bearing criterion, and it is **conjunctive by design**: report the figure's
   value *and* state the conflict. Grade both halves separately. Both halves have plausible
   independent failures — the first is the summarizer that never opened the screenshot, the second
   is the careful figure-reader who silently takes the better number without cross-checking. The
   twin below exercises the first. The second is asserted, not twinned.

2. **The PCA visualization's variance percentages are read off the axes.** The 3D plot's axes are
   labelled **PC2 (7.38%)** and **PC3 (6.35%)** — single-digit figures showing 512-dim CLIP space
   does *not* compress cleanly into three dimensions, while the prose claims the PCA "retains the
   most significant variance." A PASS gives the percentages, or states the axis labels
   quantitatively undercut the prose claim. General remarks that "PCA loses information" FAIL:
   that is inferable without opening the figure, and the whole point is that the number is on the
   axis.

   Independence: this fails while 1 passes whenever a run reads the results screenshot but not
   the plot — different figures, different failure.

3. **The rating column is identified as batch-relative, not absolute.** The `CASE` expression
   rescales distance min-max over the returned rows using `MAX(distance) OVER ()` and
   `MIN(distance) OVER ()`, so the same car's "Closeness Rating" changes when `LIMIT` changes. An
   output that reproduces the SQL but presents the rating as a fixed similarity score FAILs.
   Reproducing the query verbatim is necessary but not sufficient here — this criterion grades
   whether the window functions were *read*.

   Independence: purely a code-comprehension property, orthogonal to both figure criteria.

4. **The absence of any vector-index DDL is named as a gap.** The post ships a `CREATE TABLE`
   with `image_embedding VECTOR(512)` and never shows a `CREATE VECTOR INDEX`, so at ~4,597 rows
   it is not even stated whether the demo is using an index or doing an exact scan — while the
   post's own linked companion piece is about billions of vectors. A "what the post omits"
   section that lists only "no performance numbers" FAILs; the missing DDL is the specific,
   checkable omission.

5. **The `VECTOR(512)` column type and the `<->` operator are reproduced exactly.** Step 3
   requires literal reproduction of schemas and named operators. "A 512-dimensional vector
   column" and "a distance operator" are the flattening this skill exists to stop.

All five required. **Criterion 1 is load-bearing**; 2 guards the second figure independently.

## Twins

`graders/degraded-trusts-the-prose.md` — **passes 2, 3, 4, and 5; fails 1.** A thorough read that
opens the PCA plot and reads its axes, comprehends the window functions, names the missing DDL,
and reproduces the schema — then reports the Camaro at $335,000 from the body text without ever
reconciling it against the results screenshot. Single-property failure, deliberately: a FAIL here
cannot be explained away as a sloppy read, because everything else in the output is correct.

`graders/degraded-alt-text-figures.md` — **passes 1, 3, 4, and 5; fails 2.** Reads the results
screenshot carefully enough to catch the price conflict, then handles the PCA plot by describing
what it depicts rather than reading its axis labels, concluding generically that "some variance is
inevitably lost." Exists to give criterion 2 an independent failure, which the first twin cannot.

Criteria 3, 4, and 5 **rest on argument, not a twin** — each is a plain presence/comprehension
check whose failure mode is the same generic flattening the twins already exercise, and both
twins pass all three, which is the evidence that they do not fire spuriously. Named here so a
reader knows which claims were tested by grading and which were asserted.
