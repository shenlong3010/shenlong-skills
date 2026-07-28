# Pass criteria — read-eng-blog-hidden-code-blocks

Seeded by `skill-bootstrap` from a real first run. Criteria checked against degraded twins
before approval.

**Live-URL case — an unreachable page is an ERROR, not a FAIL.** The prompt names
`https://www.cockroachlabs.com/blog/value-separation-pebble-optimization/`. If the page 404s,
paywalls, or rate-limits, the oracle is broken, not the skill: record ERROR and fix the case.
No fixture is snapshotted because the graded property *is* retrieval — a saved copy of the
already-rendered DOM would hand the run the exact thing the case tests whether it can obtain.
This is the case's known rot risk, stated rather than hidden.

**Write side effect.** The skill persists to `notes/eng-blogs/value-separation-pebble.md` (or a
similar slug). `notes/` is gitignored. Treat leftover files as run output to delete, not results
to keep; a rerun that finds the file already present has not been given a hint, but the grader
must read the *run's* output, not the file on disk from a previous run.

This case grades **Step 1 + Step 3 under an adversarial page**: the post's three code artifacts
are collapsed behind "Show code" toggles and are absent from the server-rendered HTML entirely —
`curl | bs4` returns zero `<pre>` tags. The prose introduces each with a colon and then nothing
visible, so an output that silently omits them reads as complete. This is the exact degradation
the skill exists to stop, on a page where it is invisible.

Answer-key check: `SKILL.md` names Playwright, `scrollIntoView()`, `currentSrc`, and the
blank-screenshot gotcha — all **out of bounds** as graded material. `SKILL.md:26-28` also
instructs "reproduce specifics verbatim ... never paraphrase into prose", so the *instruction* to
reproduce literally is skill-body material too. Criterion 1 does not grade that instruction; it
grades whether the artifact was **retrieved at all** from a page where `curl | bs4` returns zero
`<pre>` tags. What the skill body does **not** contain: a "Show code" toggle, a collapsed code
block, the absence of `<pre>` in static HTML, or any struct, field, or byte value graded below.
Two greps at authoring time, both zero hits: `contentful|show code|<pre>|collapsed` for the
retrieval mechanism, and
`BlobFileID|ValueLen|BlockID|ValueID|30-byte|magic|kv0|25.4|4 KiB|AS OF SYSTEM TIME|Virtual blocks`
for the graded values. That is the scope of the claim — the second pattern is quoted because a
claim about absent terms is only as good as the pattern behind it.

1. **The `Handle` struct is reproduced as code, with all four fields.** `BlobFileID`,
   `ValueLen`, `BlockID`, `ValueID` — in a code block, not paraphrased into prose. This artifact
   does not exist in the static HTML. An output that describes "a compact handle referencing the
   blob file" without the field list FAILs: Step 3 says reproduce literally, and the field names
   are the searchable handles.

2. **At least one of the two binary-format diagrams is read for structure the prose never
   states.** The BLOB FILE FORMAT and SSTABLE FILE FORMAT figures carry the byte-level layout.
   A PASS names concrete structure recovered from a figure — e.g. the 30-byte footer and its
   components (CRC 4B, index offset 8B, index length 8B, checksum type 1B, format 1B, magic 8B),
   or the index block's parallel `Virtual blocks` / `Offsets` columns, or the liveness index
   block's position in the SSTable layout. Restating the figure's caption or alt-text is a FAIL.

   Independence: on this platform the two artifacts have **different retrieval mechanisms** —
   figures are fetchable full-resolution straight from `src` attributes with no render needed,
   while the code blocks live JSON-escaped in an embedded Contentful payload. So an output can
   read every figure and still miss every code block, which is the natural partial success here.
   `graders/degraded-figures-only.md` is exactly that output.

3. **The ~50% throughput result is tied to its actual measurement conditions.** The number is
   meaningless without them: workload `kv0/values=4096`, 4 KiB values, and CockroachDB **v25.4**.
   An output stating "up to 50% faster" with no workload and no version FAILs. At minimum the
   value size and the version must appear.

   Independence: this is a prose-fidelity property. It can fail while 1, 2, 4, and 5 pass — a
   run can recover every hidden artifact and still report the headline number bare.

4. **The rejected alternative in decision 4 is named, not just the choice.** The post's sharpest
   decision is *not* rewriting the referencing SSTables when blob files are rewritten, and the
   reason is that rewriting them would give back the write-bandwidth savings that justify the
   whole feature. Step 4 of the skill requires "the decision, the alternative rejected, and why."
   An output listing decisions without their rejected alternatives FAILs — that is the degraded
   read the skill's own step 4 calls out by name.

5. **The unrealized-benefit admission is carried, not smoothed away.** The post concedes that the
   SQL optimizer's `AS OF SYSTEM TIME` statistics queries deliberately scan MVCC history, and
   their retrieval of separated values can dominate read bandwidth — offsetting much of the
   theoretical benefit of eagerly separating MVCC garbage. A summary that presents value
   separation as an unqualified win has flattened the post's most honest paragraph.

   Independence: this is content the prose *does* state plainly, so it fails independently of
   1 and 2 (retrieval) and of 4 (which grades tradeoff shape on a different decision).

All five required. **Criteria 1 and 2 are load-bearing** — they are why this URL was chosen.

## Twins

`graders/degraded-plausible-prose-read.md` — **passes 3, 4, and 5; fails 1 and 2.** The
summarizing fetcher's output: correct prose, correct tradeoffs, the benchmark correctly
conditioned, the AOST admission carried — and not one byte of material absent from the static
HTML. It fails both retrieval criteria because it never retrieved anything beyond the raw HTML.
This twin alone does not prove 1 and 2 independent, which is what the next twin is for.

`graders/degraded-figures-only.md` — **passes 2, 3, 4, and 5; fails 1.** Reads both binary-format
diagrams for byte-level structure, then paraphrases the value handle into prose because the Go
struct is JSON-escaped in the Contentful payload rather than in the DOM. This is not a contrived
split: figure `src` attributes and the Contentful payload are two different retrieval mechanisms
on this platform, and getting one without the other is the likeliest partial success. It gives
criterion 1 its independent failure.

`graders/degraded-bare-benchmark.md` — **passes 1, 2, 4, and 5; fails 3.** A full-fidelity read
that recovers the struct and the footer layout, then reports "up to ~50% throughput improvement"
with no workload and no version. Gives criterion 3 its independent failure.

Criterion 2's independence comes from the controlled pair `degraded-plausible-prose-read.md` vs.
`degraded-figures-only.md`. **Both fail criterion 1** — criterion 1 is the variable held fixed —
and they split on criterion 2, FAIL and PASS respectively. So criterion 2's verdict moves while
criterion 1's does not, which is what independence means here. The reverse direction is covered by
`degraded-figures-only.md` on its own: criterion 1 fails while 2 passes.

Criteria 4 and 5 **rest on argument, not a twin**: both grade whether plainly-stated prose
survived into the notes, and an output that drops them is the generic summarization failure the
first twin already demonstrates. All three twins pass 4 and 5, which is the evidence they do not
fire spuriously. Named here so a reader knows which claims were tested by grading and which were
asserted.
