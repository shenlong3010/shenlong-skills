# Pass criteria — talk-notes-clean-run-no-false-positives (negative case)

Real video (Awesome channel, "Low-level programming is fun now", `4wRH1lkeds0`) — an Odin +
raylib coding walkthrough. This is the **inverse** of every other verification case in the
suite: the transcript's technical content is *correct throughout*. Nothing needs correcting.

The suite already tests whether verification fires when something IS wrong (jargon-catch,
adversarial-plausible-error, benchmark-name-garble) and whether it can catch a wrong fact on a
right name (standard-year-precision). None of those can detect the opposite failure: a
verification pass that "corrects" things that were already right. A skill tuned to always find
something will pass every positive case and still be useless. This case exists to catch that.

Ground truth, every claim confirmed against the projects' own documentation (Context7:
`/odin-lang/odin-lang.org`, `/raysan5/raylib`):

- **`::` declares a compile-time constant in Odin**, distinct from `:=` (runtime variable) —
  correct, matches Odin's official overview and FAQ verbatim ("`::` declares compile-time
  constants, while `:=` declares runtime variables").
- **"Parametric polymorphism" is Odin's own term for generics** — correct. The video explicitly
  corrects its own earlier claim that Odin lacks generics; Odin's docs use "parametric
  polymorphism, often called 'generics' or 'parapoly'."
- **Odin does not support closures "in the traditional sense"** — correct. Odin's FAQ:
  "Odin features non-capturing lambda procedures. Capturing closures require automatic memory
  management, which goes against Odin's core philosophy."
- **raylib is a C library with Odin bindings, created ~2013 to teach game dev to art students
  with no coding experience** — correct; raylib development began August 2013 for exactly that
  teaching context (Spain's first official video game development course).
- **Odin package/procedure model, `defer`, dynamic arrays, delta time, Euler integration** — all
  standard and correctly described.

1. **Zero corrections issued**: the Verification log must not mark ANY term "corrected." Every
   proper noun in this video (Odin, raylib, and the language features above) is correctly named
   and correctly described. A single "corrected from X" entry is a FAIL — that is a false
   positive, the exact failure this case is built to detect.
2. **Verification still visibly ran**: a log must be present listing the checked terms
   (at minimum Odin and raylib, plus the language-feature claims) with sources and "confirmed"
   outcomes. Producing no log because "nothing looked wrong" is a FAIL — Method step 6 runs
   unconditionally, and a clean video must still show its work. This criterion is what keeps
   criterion 1 from being trivially satisfiable by skipping verification entirely.
3. **The closures claim is not over-corrected**: "Odin doesn't support closures in the
   traditional sense" is precisely right, including the hedge. An output that flattens this to
   "Odin has no closures" (dropping the nuance) or flags it as wrong (Odin does have
   non-capturing lambdas) is a FAIL — this is the subtlest claim in the video and the most
   likely to be mishandled in either direction.
4. **The generics self-correction is preserved**: the speaker explicitly retracts an earlier
   video's claim that Odin lacks generics. The notes must not reintroduce the retracted claim
   as if it were the video's position.

A PASS requires all four. Treat a FAIL here as seriously as a FAIL on any positive case: a
verification mechanism with a nonzero false-positive rate injects errors into notes that were
previously correct, which is strictly worse than not checking at all.
