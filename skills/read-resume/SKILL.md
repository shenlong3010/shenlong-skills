---
name: read-resume
description: Diagnose a whole resume as a document — scan pattern, impact vs duty bullets, quantification that means something, claims that survive an interview follow-up, ATS-hostile formatting — and, when a job posting is supplied, gap-map the resume against it. Use for "review my resume", "is my resume any good", "does this have impact", "what's wrong with my resume", "score my resume", and equally for "tailor my resume to this job", "do I match this posting", "what is this JD really asking for", "should I apply to this". Do NOT use to rewrite an individual bullet — this skill produces the queue of bullets that need work, and /resume-impact rewrites them.
derivation: original
flow: career
domain: career
---

# Read Resume

Grade a resume as a document, and — when a posting is in hand — against that posting. This skill **reads and grades; it never rewrites**. Its output is a ranked queue for `/resume-impact`.

## Two modes, one grading engine

- **Mode A — resume alone.** Diagnostic: how the document reads, what is weak, what would collapse in an interview.
- **Mode B — resume + job description.** Everything in Mode A, plus the posting decoded and diffed against the resume.

The claim-grading criteria below are stated once and used by both modes. Mode B adds JD extraction and the gap map on top; it does not re-grade by different rules.

## Grading criteria (both modes)

- **Impact vs duty.** A duty bullet says what you were assigned; an impact bullet says what changed because you were there. "Responsible for the payments service" is a duty. "Cut payment failure rate from 4% to 0.6%" is impact. Report the ratio per role, not just overall — a strong recent role and three duty-only older roles is a different problem from uniform weakness.
- **Quantification that means something.** Grade the denominator, not the percent sign. "Improved performance 40%" is decoration; "cut p99 from 800ms to 480ms at 12k rps" is a number. Count only bullets whose figure has a baseline, a unit, or a scale.
- **Defensibility.** Every claim must survive one interview follow-up: *how did you measure that, and what was your part?* Flag scope inflation (verbs claiming ownership of team work), unsourced numbers, and impossible solo scale.
- **Scan-path signal.** Readers scan the left edge and the opening of each bullet. Does the first third carry the outcome, or is it buried behind "Worked with the team to help…"? Signal-last bullets read as weak even when the work was strong.

## Mode A output — the resume brief

- **Target read** — the role and level this document aims at, inferred from its own content, and whether it actually supports that aim. If the target is unclear, that ambiguity is itself the top finding.
- **Per-section scan-path check** — where signal is buried, with the specific bullets.
- **Impact density** — outcome-vs-duty ratio per role.
- **Quantification rate** — share of bullets with a *meaningful* number, and the decorative ones called out.
- **Defensibility flags** — claims that would not survive the follow-up, each with the question that would expose it.
- **Structure & hygiene** — section order, length against experience level, ATS-hostile formatting (multi-column layouts, tables, text inside graphics, contact details in the header/footer).
- **Verdict + ranked fix queue** — the bullets whose repair buys the most, in order, each tagged with which criterion it fails. This queue is the handoff to `/resume-impact`.

## Mode B additions — the match brief

- **Role decode** — the actual level and function beneath the title, and the problem the team is hiring to solve. Titles are not comparable across companies; read the responsibilities.
- **Requirement split** — `must` / `nice` / `noise`. Most postings are mostly boilerplate; the real bar is usually three to six items.
- **Signal reading** — seniority tells, build-versus-maintain, on-call reality, and stack specificity. A narrowly named stack wants someone who can start immediately; a broad list means they will train.
- **Red flags** — IC title with management duties, unbounded scope, everything-marked-required, a posting that reads as two jobs.
- **Gap map** — per must-have: `covered` (citing the bullet), `weak` (present but unevidenced), or `missing`.
- **Action queue** — bullets to send to `/resume-impact`, gaps closable by reframing genuine experience, and gaps that are genuinely absent.

## Gotchas

- **A resume that extracts as interleaved nonsense is telling you what the ATS sees.** Two-column layouts hit the same reading-order failure `read-pdf-doc` documents for multi-column PDFs. Report it as a finding — do not quietly work around it by reconstructing the intended order and grading the reconstruction.
- **Contact details in a PDF header or footer are frequently dropped by parsers** — the same running-header pollution problem, with worse consequences: an unreachable candidate.
- **Quantification without a baseline is not quantification.** A percentage with no denominator, a "10x" with no starting point, and "improved reliability" all score the same: zero. Do not credit the number for existing.
- **Identical bullets read strong at one level and weak at another.** "Owned the migration" is impressive at IC2 and thin at IC6. Grade against the target level — and when the target is unstated, **ask rather than assume**, because every downstream judgment depends on it.
- **Tenure math is a free lie detector.** Sum the claimed scope against the months actually available in each role. Three flagship launches in an eight-month stint is a question, not an achievement.
- **Keyword stuffing in a skills section inflates ATS match and collapses in interview.** Flag every technology listed but never evidenced in any bullet — that is the list the interviewer picks from.
- **Seniority is claimed by verb, not by fact.** "Architected", "spearheaded", "drove" are cheap. Check whether any bullet shows the decision, the tradeoff, or the people — ownership language without ownership evidence is the most common defensibility failure.
- *(Mode B)* **Requirements are aspirational; the repeated one is real.** A requirement appearing in the title, the summary, and the responsibilities is the actual bar. One appearing once in a bulleted wish-list is not.
- *(Mode B)* **Years-of-experience lines are filters, not laws — but an ATS may enforce them literally.** Those are two separate facts and both belong in the brief: worth applying, and may be auto-screened.
- *(Mode B)* **Vocabulary mismatch loses real coverage.** The same work described as "distributed systems" on one side and "microservices at scale" on the other is covered, yet reads as missing to a keyword screen. Map synonyms before grading any gap `missing`.
- *(Mode B)* **Never invent experience to fill a gap.** A `missing` gap closes one of two ways: reframing genuine experience that was described in other words, or not claiming it. Manufacturing a credential is where tailoring becomes fabrication — and it fails at the interview, which is a worse place to fail than the screen.

## Boundaries

- Rewriting a bullet → `/resume-impact`. This skill produces its input queue and stops; that command owns the accomplished-X-by-Y-resulting-in-Z form and the defensibility rewrite.
- Practicing the answers behind the claims → `interview-drill`.
- A scanned or image-only resume PDF → `image-ocr` (via `image-prep` if oversized), then grade the extracted text here.
- A job description at a URL → fetch with `web-research` first, then reason over the text here. This skill reasons over text; it does not call job-board APIs.
- Career narrative, negotiation, and whether to apply are the user's calls — this skill reports what the documents say and where they are weak.
