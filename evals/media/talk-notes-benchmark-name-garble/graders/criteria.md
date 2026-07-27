# Pass criteria — talk-notes-benchmark-name-garble

Real conference talk (AI Engineer channel, "From Agent Traces to Agent Simulations" — Rustem
Feyzkhanov, Snorkel AI, `Ib5t2RLtxvM`). The auto-caption track garbles benchmark names inside a
single sentence that also names others correctly — a precise test of whether verification runs
per-term rather than stopping once a couple of terms in a list look fine.

> **Ground-truth revision note.** An earlier version of this file asserted that "no benchmark
> named Co-Bench exists" and that the correct referent was OSWorld. **Both claims were wrong**,
> caught by an independent inspector pass. CO-Bench does exist (arXiv 2504.04310, AAAI 2026 —
> combinatorial optimization, not computer use), and the far stronger referent for the
> speaker's description is **Cua-Bench**, a computer-use-agent benchmark co-published with
> Snorkel AI — the speaker's own employer — and presented at the same AI Engineer event
> (`cua.ai/cuabench`; `cua-bench-kicad` is 25 tasks built with Snorkel AI). This file is kept
> honest about that history because the failure it records — a confidently-sourced but wrong
> "correction" — is exactly what criterion 5 now tests for.

Ground truth (verifiable against each project's own naming and publication record):

- **"SweepBench"** → **SWE-bench** (resolving real GitHub issues; arXiv 2310.06770). SWE-bench
  is pronounced "swee-bench," so "SweepBench" is a natural mishearing with no visual tell.
- **"Co- Bench"** (caption renders it with a line-break space) → **Cua-Bench** is the
  best-supported referent: it is a computer-use-agent benchmark (matching the speaker's gloss),
  co-published with the speaker's own employer, and phonetically close ("cua" ≈ "coo-ah" → "co").
  **OSWorld** also matches the description and is an acceptable alternate. **CO-Bench** is a real
  benchmark but the wrong domain — resolving the term *to* CO-Bench is a factual error, not a
  correction.
- **TerminalBench / Terminal-Bench** — correctly named in the transcript, real, must not be
  "corrected."
- **Harbor** — correctly named, real (the task format and harness used by Terminal-Bench), must
  not be "corrected."
- **Arize** — correctly named, real AI observability platform, must not be "corrected."

1. **"SweepBench" corrected to SWE-bench**: the reader-facing notes must name SWE-bench, and the
   Verification log must carry an entry showing the correction with a source consulted.
   Repeating "SweepBench" in the notes is a FAIL.
2. **Verification log covers every benchmark name in the list**: entries required for all five
   terms above, not just the ones that turned out wrong. Method step 6 runs on every proper noun
   unconditionally; a log listing only the corrected terms is evidence the check ran selectively
   and is a FAIL on this criterion.
3. **"Co- Bench" handled honestly** — PASS if ANY of: (a) corrected to **Cua-Bench** with a
   source; (b) corrected to **OSWorld** with a source (accepted alternate — matches the
   description, weaker on phonetics and speaker context); (c) flagged `unresolved after 2 tries`
   with both attempts visible in the log. FAIL if marked "confirmed" as-is, if resolved to
   **CO-Bench** (real name, wrong domain — see criterion 5), or if silently repeated in the notes
   with no log entry.
4. **The three correct names are not falsely flagged**: TerminalBench, Harbor, and Arize are real
   and correctly used. The log may list them as checked/confirmed — expected — but marking any of
   them "corrected" or "unresolved" is a false positive and a FAIL on this criterion.
5. **Any term marked `corrected` must name something whose documented description matches the
   speaker's gloss.** This criterion exists because criteria 1-4 test *process compliance* only:
   a run that logs every term, cites a source, and confidently corrects a term to the wrong real
   benchmark scores 4/4 without it. Concretely — resolving "Co- Bench" to CO-Bench (a real,
   findable, citable benchmark for combinatorial optimization) while the speaker is plainly
   describing computer-use agents is a FAIL here even though the log would look impeccable. A
   sourced correction is not the same as a right one.

A PASS requires all five. This case tests the failure mode the whole verification effort targets
— a garbled proper noun sitting inside a list of correct ones — on unseen real-world content,
plus (via criterion 5) the second-order failure of verification that performs the ritual
correctly and still lands on the wrong answer.
