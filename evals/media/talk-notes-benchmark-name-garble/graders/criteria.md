# Pass criteria — talk-notes-benchmark-name-garble

Real conference talk (AI Engineer channel, "From Agent Traces to Agent Simulations" — Rustem
Feyzkhanov, Snorkel AI, `Ib5t2RLtxvM`). The auto-caption track garbles two public AI-agent
benchmark names while naming three others correctly, in a single sentence listing them together
— which makes this a precise test of whether verification runs per-term rather than being
skipped once a couple of terms in a list look fine.

Ground truth, verifiable against the benchmarks' own documentation and public naming (not
journalism — these are named software artifacts with canonical identities):

- **"SweepBench"** → real name is **SWE-bench** (benchmark for resolving real GitHub issues).
  Phonetically plausible garble: SWE-bench is pronounced "swee-bench," so "SweepBench" is a
  natural mishearing with no visual tell in the transcript.
- **"Co-Bench"** → the benchmark the speaker describes ("computer use agent") is **OSWorld**.
  No benchmark named "Co-Bench" exists. Note this correction rests on matching the *description*
  to a real benchmark rather than on a clean sound-alike — the phonetic distance here is larger
  than the SWE-bench case, and a run that flags this term as **unresolved after two tries**
  instead of correcting it to OSWorld is ALSO acceptable (see criterion 3).
- **TerminalBench / Terminal-Bench** — correctly named in the transcript, real, must not be
  "corrected."
- **Harbor** — correctly named, real (the sandboxing/task format used by Terminal-Bench, same
  maintaining team), must not be "corrected."
- **Arize** — correctly named, real AI observability platform, must not be "corrected."

1. **"SweepBench" corrected to SWE-bench**: the reader-facing notes must name the benchmark
   SWE-bench (not "SweepBench"), and the Verification log must carry an entry showing the
   correction with a source consulted. Repeating "SweepBench" in the notes is a FAIL.
2. **Verification log covers every benchmark name in the list**: entries required for all five
   terms above (SweepBench/SWE-bench, Co-Bench, TerminalBench, Harbor, Arize) — not just the
   ones that turned out wrong. Per Method step 6 the pass runs on every proper noun
   unconditionally; a log that only lists the corrected terms is evidence the check ran
   selectively, and is a FAIL on this criterion.
3. **"Co-Bench" handled honestly** — PASS if EITHER: (a) corrected to OSWorld with a source, OR
   (b) flagged `unresolved after 2 tries` with both attempts visible in the log. FAIL if it is
   marked "confirmed" (no such benchmark exists, so confirming it means the lookup was skipped
   or its result ignored), or if it is silently repeated in the notes with no log entry at all.
4. **The three correct names are not falsely flagged**: TerminalBench, Harbor, and Arize are
   real and correctly used. The log may list them as checked/confirmed — that is expected — but
   marking any of them "corrected" or "unresolved" is a false positive and a FAIL on this
   criterion specifically.

A PASS requires all four. This case tests the exact failure mode the whole verification effort
targets — a garbled proper noun sitting inside a list of correct ones — on unseen, real-world
content in the same technical domain the skill is scoped to.
