# Pass criteria — talk-notes-name-substitution-kipchoge

Real video (PrimeTime, "Worst Advice Ever," `L_JgETH8zKM`), not synthetic. Near the end, the
speaker references "the greatest marathon runner in the world... the one that broke the
two-hour barrier" and names him "Elliot." The real person is **Eliud Kipchoge** — the athlete
who broke the two-hour marathon barrier at the INEOS 1:59 Challenge in Vienna, October 2019.
"Elliot" is a common English first name substituted for an unfamiliar one ("Eliud") — fluent,
grammatically ordinary, zero garbling tell (unlike "3.js" or "cooper netties" — this is the
plausible-substitution failure mode, same class as the `talk-notes-adversarial-plausible-error`
case, but found in the wild on a real video rather than constructed).

Ground truth, independently verified this session via web-research (not the fixture — this
case has no fixture; the transcript comes from the real MCP tool call): Kipchoge broke the
2-hour barrier in Vienna in 2019, and multiple sources (ABC News, Olympics.com, CBS News)
confirm he smiled at the finish line — the video's surrounding claim ("he smiled through it,"
used to support the "remember to smile" argument) is also accurate, not just the name.

1. **Name corrected**: the reader-facing notes must refer to the runner as "Eliud Kipchoge"
   (or "Kipchoge"), not "Elliot." A note that repeats "Elliot" as the runner's name is a FAIL
   regardless of anything else in the output.
2. **Verification log present**: per Method step 6, output includes a Verification log entry
   for this name — term ("Elliot"), source consulted (web-research query), outcome ("corrected
   from Elliot" or equivalent). No log entry for this term is a FAIL even if the name in the
   visible notes happens to be correct (correct-by-luck is not a pass, same law as the
   adversarial case).
3. **Marathon/smiling claim not falsely flagged**: the claim that this runner "smiled through"
   the record-breaking run is accurate and must not be marked "unresolved" or "corrected" in
   the log — only the name itself was wrong, not the surrounding claim. Marking the whole
   claim as suspect when only the name was wrong is a FAIL on this criterion (over-correction /
   false positive).
4. **Travis Kalanick not falsely flagged**: the video also names Travis Kalanick (real person,
   correctly attributed as source of a quote) — the log may list him as checked, but must not
   mark him "corrected" or "unresolved." A well-known real name getting flagged as wrong is a
   FAIL on this criterion specifically.

A PASS requires all four. This case is the strongest evidence in the eval suite that Method
step 6 catches a real, non-constructed, zero-tell name substitution — a FAIL here would be the
single most important finding of the whole verification-hardening effort, since every other
passing case so far involved either an already-suspicious spelling or a synthetic fixture.
