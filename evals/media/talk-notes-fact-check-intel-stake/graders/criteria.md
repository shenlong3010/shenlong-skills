# Pass criteria — talk-notes-fact-check-intel-stake

Real video (PrimeTime, "Government Ownership Bad," `qaPBqtDmYeQ`), not synthetic. Very short
clip: the speaker states the US government owns "9%... 10%" of Intel (self-corrects live,
settles on 10%). Independently confirmed via web-research this session: real figure is 9.9%
(per Bloomberg, PBS News, CoinDesk — CHIPS Act grants converted to equity in August, 433.3M
shares), stake worth ~$35-36B as of April 2026. The video's on-the-fly estimate is accurate
within normal rounding.

This is the "should be a clean pass, nothing subtle" contrast case in this batch — included
specifically to confirm the fact-check step doesn't over-flag an approximately-correct number
as wrong, and doesn't under-flag by skipping verification just because a claim sounds roughly
plausible.

1. **Percentage is confirmed, not corrected or flagged**: 9-10% is within rounding of the real
   9.9% figure. The output must treat this as accurate — flagging it as wrong, imprecise, or
   "unverified" is a FAIL. This tests against over-correction: a check that "fixes" an already-
   close-enough number is as much a failure mode as missing a wrong one.
2. **Verification did occur, not skipped**: per Method step 5's law that single-source/numeric
   claims get routed through fact-check, this claim (a specific ownership percentage) should
   show evidence of being checked (a Verification log entry, source cited, or an explicit
   statement that the figure was verified) — not silently repeated with no indication a check
   happened, even though the claim happens to be correct. Passing "by luck" with no visible
   check is graded the same as elsewhere in this suite: not a full pass.
3. **No unrelated commentary treated as factual claims**: the clip also includes the speaker's
   own uncertainty ("Is that the government or Trump? I thought it was the government.") — this
   is the speaker thinking out loud, not a claim to fact-check. The output must not present this
   aside as if it were an assertion needing verification; doing so would be noise, not signal.

A PASS requires all three. Given the video's brevity and the claim's simplicity, this case
should be the easiest PASS in this batch — a FAIL here (especially on criterion 1, over-
correcting an accurate figure) would be a stronger signal of a false-positive problem than
anything found in the broader 16-video sample this session.
