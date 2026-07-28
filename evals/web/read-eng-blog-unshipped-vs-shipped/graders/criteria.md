# Pass criteria — read-eng-blog-unshipped-vs-shipped

Seeded by `skill-bootstrap` from a real first run. Criteria checked against degraded twins
before approval.

**Live-URL case — an unreachable page is an ERROR, not a FAIL.** The prompt names
`https://www.cockroachlabs.com/blog/cspann-real-time-indexing-billions-vectors/`. A 404,
paywall, or rate-limit is a broken oracle: record ERROR and fix the case rather than scoring the
skill. No fixture is snapshotted — one graded property is recovery of a code block absent from
the static HTML, which a saved render would hand over for free.

**Write side effect.** Persists to `notes/eng-blogs/cspann-real-time-indexing-billions-vectors.md`.
`notes/` is gitignored. Leftover files are run output to delete; grade the run's output, not the
file on disk.

This case grades **Step 4's "what the post omits" line under maximum pressure**. The post is
fluent, well-structured, and describes two mechanisms at length that **are not implemented in
the 25.2 preview** — and its own accuracy-over-time claim partly rests on them. A summarizer
reproduces the structure faithfully and presents design intent as shipped behaviour. That is the
degradation. Its companion cases grade retrieval (`-hidden-code-blocks`) and figure-vs-prose
conflict (`-figure-contradicts-prose`); none covers this one.

Answer-key check: `SKILL.md` requires a "What the post omits" section and gives an example line
("architecture writeup only — no scale/throughput numbers, no code"), so the *presence* of such a
section is answer-key material and is **not graded here**. What is graded is the specific
content below, none of which appears in the skill body — no partition, quantization, index, or
version term. Verified by grep at authoring time.

1. **Merges and partition reassignments are identified as not yet implemented in 25.2.** The post
   describes both mechanisms in the architecture narrative and only later, in a status section,
   notes they are unimplemented. An output that presents merges as part of how the index works,
   without flagging them as unshipped, FAILs. This is the load-bearing criterion: the reader's
   decision — can I use this today — turns on it.

2. **The accuracy claim is tied to the unshipped mechanism, in one statement.** Beyond noting
   merges are missing, the output must state the *dependency*: that the post's "insert millions of
   vectors and still get high accuracy after many cycles" claim rests partly on maintenance
   operations that have not shipped, so a reader cannot separate measured behaviour from design
   intent.

   **Operational test, because this is otherwise a judgment call.** PASS requires a single
   sentence containing both the accuracy claim and its dependence on unshipped machinery — a
   causal connective ("rests on", "depends on", "because ... not yet implemented", or equivalent).
   Co-presence of the two facts in separate sections is an explicit **FAIL**, however correct each
   section is on its own. Two graders must reach the same verdict, and the only way to guarantee
   that is to require the connective rather than to ask whether the connection was "drawn."

   Independence: this fails while 1 passes whenever an output copies the status section faithfully
   and never links it back to the claim made sections earlier. That is the more common failure of
   the two, and the one that leaves a wrong impression.

3. **Euclidean is named as the only supported metric today.** Cosine and inner product are listed
   as *planned*. An output that says the index supports pgvector-compatible distance operators
   without stating that only Euclidean works in 25.2 FAILs — this is a concrete adoption blocker
   for anyone embedding with CLIP or OpenAI models, where cosine is conventional.

4. **The multi-region `crdb_region` index DDL is recovered.** The third SQL block sits behind a
   JS "Show code" toggle and is not in the static HTML:

   ```sql
   CREATE TABLE photos (
     id UUID PRIMARY KEY,
     user_id UUID,
     embedding VECTOR(1536),
     VECTOR INDEX (crdb_region, user_id, embedding)
   ) LOCALITY REGIONAL BY ROW;
   ```

   A PASS reproduces it, or at minimum states that `crdb_region` joins the index columns under
   `LOCALITY REGIONAL BY ROW`. Reproducing only the two visible SQL blocks FAILs.

   Independence: pure retrieval, orthogonal to 1, 2, 3, and 5.

5. **RaBitQ's compression is reported with the mechanism, not just the percentage.** The ~94%
   figure (~3 KB → ~200 bytes) is meaningless alone. A PASS states that each dimension becomes a
   single bit, and that quantization is **relative to the partition's centroid** — which is why
   splits and merges only re-quantize the affected partition instead of forcing global
   retraining. An output giving "94% compression via RaBitQ quantization" with no mechanism has
   reproduced a marketing number.

All five required. **Criteria 1 and 2 are load-bearing.**

## Twins

`graders/degraded-shipped-as-designed.md` — **passes 3, 4, and 5; fails 1 and 2.** The fluent,
faithful summary: every mechanism described accurately, the hidden DDL recovered, Euclidean-only
correctly noted, RaBitQ explained mechanically — and merges and partition reassignments presented
as part of how the index maintains itself, with the accuracy claim repeated unqualified. It fails
1 and 2 together because both have one cause: the status section was never reconciled against the
architecture narrative. The reverse split — 1 passing while 2 fails — is exactly the second twin
below, so criterion 2 has an independent failure and the pair is not one test scored twice.

`graders/degraded-status-list-only.md` — **passes 1, 3, 4, and 5; fails 2.** Copies the status
section correctly, listing merges and reassignments as unimplemented, while the architecture
section still presents the accuracy-over-many-cycles claim as an established property. Nothing is
false; the two facts simply never meet. This twin is what gives criterion 2 an independent
failure, and it is the more realistic of the two defects.

Criteria 3, 4, and 5 **rest on argument, not a twin** — each is a presence check with an obvious
failure mode (omit the version caveat, miss the hidden block, quote the number bare), and both
twins pass all three, which is the evidence they do not fire spuriously. Stated so a reader knows
which claims were tested by grading and which were asserted.
