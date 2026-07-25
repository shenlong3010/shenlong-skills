---
name: read-pdf-doc
description: Comprehend a document-class PDF — report, contract, spec, RFC, whitepaper, policy — into its structure, key claims, tables, and any obligations or requirements it imposes, so you can answer questions about what it says and requires. Use whenever a PDF's meaning must be understood — "what does this document say", "summarize this report", "what are the obligations in this contract", "find the requirement about X", "what does section 4 cover". Do NOT use for mechanical PDF operations like merge/split/form-fill (that is the pdf skill), for a scanned image-only PDF (route text extraction to image-ocr first), or for a research paper needing a method/math deep-read (that is paper-deep-dive).
derivation: original
flow: lookup
domain: docs
---

# Read PDF Doc

Turn a document PDF into structured meaning you can answer from — sections, claims, tables, and the requirements it imposes — without paging the whole file into context.

## Scope boundary

This *comprehends* a document; it does not manipulate the file. Merging, splitting, watermarking, form-filling, or raw text extraction as a mechanical op is the `pdf` skill. A scanned/image-only PDF has no text layer — route extraction to `image-ocr` (or `image-prep` first if pages are huge/skewed), then comprehend the extracted text here. A research paper where the point is the method and the math routes to `paper-deep-dive` (multi-pass, derivation walk-through) or `paper-notes` (is-it-worth-my-time); this skill is for reports, contracts, specs, and policy docs.

## Output: the document brief

- **Type & purpose** — report / contract / spec / RFC / policy, and what it exists to do. This drives what matters: a contract's payload is its obligations; a spec's is its requirements; a report's is its findings.
- **Structure map** — the section/heading tree with page anchors, so later questions can jump to a section without re-reading. Built once, reused for every follow-up.
- **Key content** — findings (report), obligations & parties (contract), MUST/SHALL requirements (spec/RFC), decisions & scope (policy). Extract to the level the task needs.
- **Tables & figures** — what each conveys in one line; pull specific cells only when asked (tables are where PDFs mangle most — see gotchas).
- **Defined terms & references** — a glossary/defined-terms section governs meaning elsewhere; cross-references ("as set out in Schedule 2") point to where the real content lives.
- **Gaps & flags** — ambiguous obligations, undefined terms used, "TBD"/placeholder sections, contradictions between sections.

Answer the user's actual question from this brief; emit the full brief for "summarize this" / "walk me through this".

## Reading procedure

1. **Confirm there's a text layer.** Extract text (the `pdf` skill's extraction, or a quick check); if a page yields no text or gibberish, it's scanned — stop and route to `image-ocr`. Comprehending an empty extraction produces confident fiction.
2. **Build the structure map first**, from headings / bookmarks / the table of contents. This is the index every later answer jumps from — never linear-read a 60-page PDF front to back.
3. **Read to the question.** For "what are the obligations", go to the operative clauses; for "requirement about X", jump via the structure map. Load sections, not the document.
4. **Handle tables deliberately.** Extracted table text loses column alignment; re-associate cells to headers before quoting a value, or note that the table couldn't be reliably reconstructed rather than guessing an alignment.
5. **Resolve defined terms and cross-references** before stating what a clause means — a term with a capital-letter Definition means the defined thing, not the ordinary word.

## Gotchas

- **Multi-column layout scrambles reading order.** Extractors often read across columns instead of down them, interleaving two columns into nonsense. If sentences don't cohere, suspect column order and re-extract per-region rather than trusting the flow.
- **Tables lose structure on extraction.** A PDF table is positioned text, not a grid; extraction drops the alignment that made it a table. Never quote a cell value without re-establishing which header column it sits under — a misaligned number is worse than "couldn't read it".
- **Headers/footers/watermarks pollute the text.** Running headers, page numbers, and "DRAFT" watermarks interleave into extracted body text. Strip repeating per-page lines before comprehending.
- **"MUST" vs "should" is load-bearing in specs.** RFC-style docs define MUST/SHALL/SHOULD/MAY precisely (RFC 2119). Preserve the exact keyword — downgrading a MUST to "should" changes the requirement.
- **The defined-terms section governs everything.** A contract's "Confidential Information" means exactly what its definitions say, which may exclude things you'd assume. Read definitions before interpreting clauses that use them.
- **Scanned pages hide inside "digital" PDFs.** A born-digital PDF can contain scanned inserts (a signed signature page, an appendix). Per-page text-layer checks catch these; a whole-file assumption misses them.

## Boundaries

- File operations — merge, split, extract-a-page, fill a form, add a watermark — are the `pdf` skill; this skill reads meaning, it does not edit the file.
- No text layer → `image-ocr` for extraction (`image-prep` first for oversized/skewed pages), then return here to comprehend.
- Research paper, method/math focus → `paper-deep-dive`; quick relevance verdict → `paper-notes`.
- A contract's *legal* risk analysis is beyond a reader's remit — extract the obligations faithfully and flag ambiguities; do not opine on enforceability.
