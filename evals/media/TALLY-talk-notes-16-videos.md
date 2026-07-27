# talk-notes verification tally — 16 real videos

Artifact for Plan A item 4/5 and verification item 5: the raw numbers, on disk, inspectable.
Written 2026-07-27. Every video run through `talk-notes`' Method with the mandatory Method
step 6 proper-noun pass, step 7 polarity pass, and step 8 countable/structural pass.

## Scope rule (learned the hard way, mid-sample)

An earlier expansion used 10 videos across gaming/legal/culture domains for "domain diversity."
Those were **discarded** — their claims rest on journalism, which conflicts, goes stale, and
carries spin, so no `criteria.md` grounded in them can settle a disagreement. Three eval cases
built on them were committed and then removed (`423d349` → `47100c2`).

**The rule that replaced it:** every video must sit in the computer/software domain where a
claim resolves against a *canonical* source — Context7 library docs, a project's own
documentation, an ISO standard's publication record, a benchmark's own naming. Diversity comes
from varying the **technical subfield**, not from leaving the domain.

Subfields covered: JS frameworks/browser APIs · Java · systems programming (Odin) · databases
(Postgres/graph) · JS runtime internals (Bun/Zig/Rust) · distributed systems (Uber) ·
JS toolchain (Rust rewrites, Astro/Vite) · AI agent evaluation · language design.

## Per-video results

Videos 1-6 are the original session's sample, retained. 7-16 are the docs-verifiable expansion.

| # | Video | Subfield | Checked | Confirmed | Corrected | Unresolved | Flagged |
|---|---|---|---|---|---|---|---|
| 1 | Browsers replacing JS frameworks (`l1cWUrG_vNs`) | web/browser APIs | 5 | 0 | 5 | 0 | 0 |
| 2-6 | original session batch | web/JS/Java | ~10-15 | ~10-15 | 0 | 0 | 0 |
| 7 | Low-level programming is fun now (`4wRH1lkeds0`) | systems (Odin) | 4 | 4 | 0 | 0 | 0 |
| 8 | Postgres new feature (`zPsr0n9DQ7o`) | databases | 5 | 4 | 1 | 0 | 0 |
| 9 | Agent Traces to Simulations (`Ib5t2RLtxvM`) | AI eval | 5 | 3 | 2 | 0 | 0 |
| 10 | Bun rewrite lessons (`U73TPeCCAMI`) | runtime internals | 9 | 6 | 1 | 0 | 2 |
| 11 | Uber's architecture (`g7FmEc5GLWs`) | distributed systems | 7 | 6 | 1 | 0 | 0 |
| 12 | Rust taking over the web (`TdDt7AiN6aw`) | JS toolchain | 8 | 6 | 2 | 0 | 0 |
| 13 | Odin first impressions (`z_GpYtSbgts`) | language design | 6 | 3 | 2 | 0 | 1 |
| 14 | Future of Evals (`q2JrUKBMf0w`) | AI eval | 5 | 2 | 1 | 1 | 1 |
| 15 | Web dev is healing (`A2JTsIeNqow`) | JS toolchain | 6 | 3 | 2 | 1 | 0 |
| 16 | Vending-Bench (`cO8qC6HBuBg`) | AI eval | 9 | 2 | 6 | 0 | 1 |

## Corrections found (the substance)

| Caption said | Real | Class |
|---|---|---|
| SweepBench | SWE-bench | phonetic garble, proper noun |
| Co- Bench | Cua-Bench (or OSWorld) | garble; **my first correction to "OSWorld" was itself likely wrong** — see below |
| GQL formalized 2023 | GQL published 2024 (SQL/PGQ *is* 2023) | wrong fact on correctly-named entity |
| Andrew Kelly | Andrew Kelley | spelling |
| Nicholas Minorsky | Nicolas Minorsky | spelling |
| Firefly | Pyrefly | proper noun |
| Vit / VT ecosystem | Vite | proper noun |
| Jenga effects | JangaFX | proper noun |
| "Odin has no generics" | Odin has parametric polymorphism | **speaker error, not caption garble** |
| V8 + Rollup (Astro's bundler) | Vite 8 + Rolldown | two errors in one clause |
| Tori | Tauri | proper noun |
| Lucas H | Lukas Petersson | proper noun |
| Entropic | Anthropic | proper noun |
| Kimmy | Kimi | proper noun |
| Grock 4.3 | Grok | proper noun |
| GP 5.5 / GBT / JP | GPT | three variants, one garble |
| bending bench / evvelts / develops | Vending-Bench / evals | phonetic |
| "the four keyword for loops" | `for` | homophone → false claim |
| "a boat edge" | "a bought edge" | homophone, identifier in syntax |
| "we use is to close the window" | `defer rl.CloseWindow()` | dropped verb |

## Unresolved after 2 tries (honest non-answers)

- **"Saturation"** (Astro's markdown processor, video 15) — no processor by that name found.
- **"GDB"** (video 14) — likely Greg Brockman's handle, spoken as initials; not confidently resolvable.

## Flagged, not corrected (claims that are neither clean-true nor clean-false)

- Bun's "6,778 commits" — sources report 6,502 / 6,755. Same order, differing exact figure.
- Bun's "4% unsafe blocks" — independent reporting cites 13,044 unsafe blocks vs 73 in
  comparable hand-written Rust. Bun's own metric, not independently corroborated.
- Odin's "batteries-included core library" — caption garbled ("a better using included"),
  decoded rather than rendered literally.
- Arize's "100M evals/month, 3,800 evaluators" — vendor stats, single-source.
- Andon Labs' "Opus 4.7 SOTA, 4.8 worse" — first-party claim citing a system card, unchecked.

## Totals

**~79-84 terms/claims checked across 16 videos.** 24 corrections, 2 unresolved after 2 tries,
5 flagged as contested/single-source, remainder confirmed. **Zero known false positives** — no
term that was already correct got "corrected."

## What this does and does not establish

**Does:** the mechanism generalizes across technical subfields it was never tuned against. It
catches phonetic garbles, spelling errors, wrong facts on correctly-named entities, homophones
that manufacture false claims, and — in one case — a **speaker's own factual error** rather than
a transcription defect. It also produced honest non-answers rather than confident guesses twice.

**Does not:** establish a coverage rate. The denominator is unknown — these are terms the
mechanism *chose* to check, not all terms present. A term it walked past silently leaves no
trace. Measuring misses requires ground-truth transcripts to diff against, which exist for
exactly one video in this sample (`talk-notes-jargon-catch`'s manual-caption fixture).

**A correction here was itself wrong, and that matters more than the pass rate.** "Co- Bench"
was first corrected to OSWorld with a plausible-sounding rationale. An independent
`ralph-task-inspector` pass found CO-Bench is a real benchmark (AAAI 2026, combinatorial
optimization) and that Cua-Bench — co-published with the speaker's own employer — was the
stronger referent. A sourced correction is not the same as a right one. Eval criteria that check
only whether the verification ritual ran will score such a correction 4/4; the
`benchmark-name-garble` case now carries a fifth criterion specifically for this.

## Same-model caveat

Every run above was produced and tallied by the same model. Four cases were independently
graded by `ralph-task-inspector` in fresh context (commit `2779486`); those found three real
defects this self-tally did not. **Treat these numbers as pre-review, not as a gate.** Per
`agents/CLAUDE.md`: a PASS is weak evidence, a FAIL is strong.
