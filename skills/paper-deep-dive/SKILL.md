---
name: paper-deep-dive
description: Deep, multi-pass read of a research paper — assumptions register, derivation walk-through, critical questions. Use for "deep dive this paper", "walk me through this paper", "really understand this paper", "check the math", "verify this derivation", "read this paper section by section". Do NOT use for a quick summary or is-it-worth-my-time verdict — that is paper-notes.
derivation: original
flow: lookup
domain: docs
---

# Paper Deep Dive

Linear front-to-back reading produces the illusion of understanding: hours spent, yet unable to name the load-bearing assumption or say why Table 2 supports the claim. This skill is the discipline that prevents deep effort on the wrong paper and shallow output from a deep read.

## Method — three passes

**Pass 0 — relevance gate.** If the paper hasn't been triaged, run `paper-notes` first; deep-dive only on an adopt/watch verdict. Never deep-dive a paper whose Claim and So-what are unknown.

**Pass 1 — structure skim (minutes, not hours).** Read title, abstract, section headings, every figure and table caption, and the conclusion. Output two things before going further:
- the one-sentence contribution, and
- the **genre call**: ML/empirical · systems · theory. The genre selects what pass 2 deep-reads; everything else gets skimmed.

**Pass 2 — method + results, genre-weighted.**
- Build a **notation table** (symbol → meaning → where introduced) *before* reading equations; most derivation confusion is notation confusion.
- Walk the key derivation step by step; flag every "it can be shown" / "it follows that" jump explicitly rather than nodding past it.
- Read every results table against the specific claim it is supposed to support; note deltas, missing baselines, absent ablations.
- Maintain an **assumptions register**: stated vs implied, and what breaks if each assumption fails.
- Genre emphasis: ML → experimental setup + ablations; systems → workload realism + eval hardware; theory → assumptions of the main theorem + proof sketch.

**Pass 3 — critical read.**
- Questions-to-ask-the-authors list — anything the paper asserts but doesn't defend.
- Related-work map: 3–5 entries, what this builds on vs competes with.
- Reproduction notes: data/compute/code needed; is code actually released.

## Output contract

Deliver: notation table · assumptions register · claims-vs-evidence notes · question list · related-work map · one paragraph "what I now believe and why". Distinguish the paper's claims from reader inference; label inference as such (same rule as `paper-notes`).

## Gotchas

- PDF text extraction mangles equations and multi-column tables — extract page ranges via `pdf`, and for garbled math read the rendered page image instead. Never "correct" an equation from mangled text; a plausible-looking reconstruction is worse than a flagged gap.
- The abstract's numbers and the results table's numbers frequently disagree — the table wins, and the disagreement itself goes in the notes.
- Deep-reading the whole paper is the trap that kills the session: deep-read only the sections the genre call marks load-bearing; skim the rest.

## Boundaries

- Quick structured summary / is-it-worth-my-time verdict → `paper-notes` (it also gates pass 0).
- PDF mechanics (page extraction, splitting, text ops) → `pdf`; scanned pages → `image-ocr`; figures as images → `read-image`.
- Fetching the paper or hunting related work online → `web-research`.
