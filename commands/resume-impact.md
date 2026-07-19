---
name: resume-impact
description: Rewrite a resume bullet into accomplished-X-by-Y-resulting-in-Z form with a defensibility check — every claim must survive a follow-up interview question. Use for "improve this bullet", "resume review", "make this sound stronger".
derivation: original
flow: career
domain: career
---

# /resume-impact

## Invocation
`/resume-impact <bullet or list>`

## Behavior
1. Restructure: action verb → what was built/changed → measurable outcome (scale, %, time, cost).
2. Defensibility check per claim: could the author walk an interviewer through how the number was measured? If not, downgrade to what is defensible ("reduced token spend ~70% measured across N sessions" beats an unsourced "70%").
3. Strip inflation words (spearheaded, revolutionized) unless the ownership claim is literally true.
4. Output: rewritten bullet + one line naming the follow-up question it must survive.
