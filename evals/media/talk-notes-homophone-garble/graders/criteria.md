# Pass criteria — talk-notes-homophone-garble

> **Scope of this case: named-regression guard, NOT evidence of generalization.** An independent
> inspector pass found that an earlier draft of Method step 8 quoted this video's exact garbles
> as its worked examples — so a run could pass by pattern-matching an answer key it had just
> been handed, whether or not the underlying capability existed. Step 8 has since been rewritten
> to state only abstract trigger shapes (counts / exclusivity / support claims) with no worked
> example naming this video. **This case still cannot prove step 8 fires cold**, because the
> defect it grades is the one that motivated the step. Its job is narrow and legitimate: prove
> this specific known defect does not regress. Evidence that step 8 generalizes requires a
> different case, on a different video, with a countable/structural garble not referenced
> anywhere in `skills/talk-notes/SKILL.md` — that case does not exist yet. Do not cite a PASS
> here as proof the mechanism works in general.

Real video (Awesome channel, "Low-level programming is fun now", `4wRH1lkeds0`) — the same
source as `talk-notes-clean-run-no-false-positives`, graded on a different property. That case
tests that a correct video produces zero corrections; this one tests four caption garbles in the
same transcript that a spelling-oriented scan cannot see, because every garbled word is itself a
correctly-spelled English word.

Found by an independent inspector pass, not constructed — these are real auto-caption defects:

- **"Odin only has the four keyword for loops"** → the speaker said **`for`**. This is the
  load-bearing one. Read literally, the caption asserts *"Odin has four loop keywords"* — a
  fluent, plausible, completely false claim about the language, with no odd spelling to notice.
  Ground truth (Odin FAQ, "Why does Odin not have a `while` statement?"; docs/demo.md: "Odin has
  a single loop statement, the `for` loop"): Odin has exactly **one loop statement**, `for`,
  which also serves as the while-loop form via `for cond`. ("Loop statement" is the precise term
  — `do`, `break`, and `continue` appear in loop contexts without being loop statements.) A homophone
  garble that inverts a factual claim is the same failure class as the polarity inversions
  Method step 7 targets, reached through a different mechanism.
- **"we use is to close the window"** → `defer rl.CloseWindow()`. The caption drops the verb
  entirely; context (a deferred cleanup immediately after window creation, discussed as a
  `defer` statement) supplies it.
- **"we can now remove that particles"** → **"dead"** particles. Minor, obscures the point.
- **"the left syntax"** → `.LEFT` — Odin's implicit-enum shorthand; the caption drops the leading
  dot.

1. **The "four keyword" garble does not reach the notes as a factual claim.** The reader-facing
   notes must NOT state or imply that Odin has four loop keywords, four keywords for loops, or
   any count other than one. PASS if the notes either state Odin's single `for` loop keyword
   correctly, or omit the loop-keyword claim entirely. A notes body carrying "four keywords" in
   any form is a FAIL — this is the criterion the case exists for.
2. **The claim is verified, not merely omitted by luck.** The Verification log must show the
   loop-keyword claim was checked against a source (Odin docs via Context7, or a documented
   equivalent), with an outcome. Silently dropping the sentence because it read oddly is not the
   same as checking it; per the suite's standing law, correct-by-omission with no visible check
   does not satisfy this criterion. (Criterion 1 can pass by omission; criterion 2 cannot.)
3. **No fabricated code semantics from the dropped-verb garble.** "we use is to close the window"
   must not be rendered into notes as a real API call or language feature named "is". PASS if the
   notes describe the deferred cleanup correctly (a `defer`red window-close), or omit the detail.
   Inventing an `is` keyword/procedure to make the caption grammatical is a FAIL.
4. **Odin's real language features are not corrected.** `::` (compile-time constant), `:=`
   (runtime variable), parametric polymorphism as Odin's term for generics, non-capturing lambdas
   without traditional closures, `defer`, and dynamic arrays are all correctly described in the
   transcript. Marking any of them "corrected" is a false positive and a FAIL.

A PASS requires all four. The distinguishing value of this case: every other jargon case in the
suite garbles a *proper noun* (a library, framework, or product name). This one garbles a
**common word into another common word**, producing a false technical claim about a language's
design with no name to look up and no misspelling to notice — the hardest shape for Method step
6 to catch, since step 6 is framed around proper nouns and this error has none.
