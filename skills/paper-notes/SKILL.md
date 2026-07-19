---
name: paper-notes
description: Summarize a paper or technical blog post into structured notes plus a relevance-to-my-stack verdict. Use for "summarize this paper", "notes on this article", "is this arXiv link worth my time". Do NOT use for a full deep read of method and math — that is paper-deep-dive.
derivation: original
flow: lookup
domain: docs
---

# Paper Notes

## Output structure
1. **Claim:** the one-sentence contribution, in plain words.
2. **Mechanism:** how it works — 3–6 sentences, the actual technique, not the abstract's marketing.
3. **Evidence:** what was measured, against which baselines, effect size; note weak spots (tiny n, cherry-picked baselines, no ablation).
4. **Limits:** where the authors say (or the setup implies) it does not apply.
5. **So-what for my stack:** does this change anything I build — a concrete "adopt / watch / ignore" with one sentence of reasoning tied to my actual systems.

## Rules
Read the results tables, not just the abstract — the delta between claim and table is the review. Distinguish the paper's claims from your inference; label inference as such. If the PDF/link is unreadable, say what's missing rather than summarizing from the title.

## Boundaries
- Verdict says adopt/watch and the method or math must actually be understood → `paper-deep-dive`.
- Fetching the paper itself → `web-research`; unreadable PDF mechanics → `pdf`.
