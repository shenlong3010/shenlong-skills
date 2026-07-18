---
name: systematic-debug
description: Structured root-cause debugging — reproduce, observe, hypothesize, isolate, fix the cause, add the regression test. Use for any nontrivial bug — "this is broken", "worked yesterday", "fails only in prod", intermittent failures — before flailing at symptoms. For a pasted stack trace specifically, stacktrace-analyzer feeds step 2.
derivation: adapted
source: https://github.com/obra/superpowers
flow: debug
---

# Systematic Debug

## Method

1. **Reproduce, minimally.** Shrink to the smallest input/steps that still fail. No reliable repro → the task IS building one (add logging, capture inputs); guessing without a repro is superstition.
2. **Observe before theorizing.** Read the actual error text, the actual logs, the actual values — not what they "probably" say. Half of debugging time is lost to a misread error message.
3. **Hypothesis ladder.** List candidate causes, ranked by *cheapness to test*, not by likelihood. Test the 10-second check before the 10-minute one even if it feels less likely.
4. **One variable per experiment.** Change one thing, observe, record. Two changes that "fixed it" = you don't know which, and one of them is now cargo cult.
5. **Write down falsified hypotheses.** A kill-list prevents re-testing the same theory an hour later — the most common debugging waste.
6. **Isolate by bisection** when the ladder stalls: git bisect for "worked yesterday" (then diff code AND config AND data AND environment — regressions hide in all four), binary-search the input, comment-out halves, differential-test against the working environment.
7. **Fix the cause, not the symptom.** A retry wrapped around a race is a snooze button. State in one line why the fix addresses the mechanism from step 6.
8. **Close the loop:** add the regression test that would have caught it, and the log line/metric that would have made this diagnosis 10× faster. The bug's lasting value is the observability it forces.

## Anti-patterns this replaces
Shotgun edits ("try this"), fixing the first plausible suspect, deleting the repro before the regression test exists, and declaring victory on "can't reproduce anymore" without knowing why.
