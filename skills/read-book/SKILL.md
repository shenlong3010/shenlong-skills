---
name: read-book
description: Read and query a book you will return to across sessions, using a persistent local corpus index instead of re-reading the file every time — sweep a library, summarize a chapter, then jump straight to the passage that answers a later question. Use whenever a book is the source and the reading outlives one session — "index this book", "add these books to my library", "what do my books say about X", "which of my books cover Y", "summarize chapter 7", "go deeper on page 340", "I'll be referencing this". Do NOT use for a one-shot read of a document you will not revisit (that is read-pdf-doc), for a research paper's method and math (that is paper-deep-dive), or for mechanical PDF operations like merge and split (that is the pdf skill).
derivation: original
flow: lookup
domain: docs
---

# Read Book

Turn a book — or a library of hundreds — into something you can ask questions of months later, without re-paging the file each time.

## Scope boundary

Route on the **action, not the page count**: *will you come back to this across sessions?* A report you read once and close is `read-pdf-doc`, however long it is. A book you will return to — textbook, technical reference, manual — belongs here, because the persistent index is the entire point. A research paper's derivations are `paper-deep-dive`; a quick is-it-worth-reading verdict is `paper-notes`.

The corpus lives in the `book-corpus` MCP server (`mcp/book-corpus/`). Its tool mechanics and wiring are documented in that README; this skill covers **when and how to use them**, and what to distrust in the results.

## Two-phase ingest

A library is mostly unread, so extraction cost is paid only where it earns out:

- **Sweep** (`ingest_dir`, `ingest_book`) — cheap. Title, author, page count, TOC, text-layer verdict. Run across the whole library; makes "which of my books have a chapter on consensus" answerable from TOCs alone.
- **Full index** (`full_index`) — costly, per page. Run on a book when you actually start reading it. `search_corpus` only sees fully-indexed books.

Sweeping hundreds of books is fine. Full-indexing hundreds up front is paying for pages you may never open.

## Procedure

1. **Check the corpus before extracting anything.** `list_books(filter=…)` — already indexed means query, not re-ingest. Re-reading a book the index already holds is the most common waste here.
2. **Sweep, then read the verdict.** After `ingest_dir`, look at the text-quality tally before trusting anything downstream. A `none` book is a scan; a `sparse` book is thin or partial.
3. **Orient with `get_toc` before reading.** The chapter list plus page offsets is the map every later jump uses. Never linear-read a book to find out what is in it.
4. **Full-index only what you are reading**, then summarize **per section**, not per book — each section gets its claim, its argument, and its page anchor. A whole-book summary loses exactly the detail you indexed for.
5. **Answer follow-ups by query-then-load.** `search_corpus` → page numbers → `get_pages` on that span alone. Never re-page a book to answer a question about one passage.
6. **Escalate genuine concepts.** When a section teaches something you want to actually understand rather than locate, hand its text to `concept-explain` instead of paraphrasing inline.

## Gotchas

- **PDF page ≠ printed page.** Front matter offsets them, so "go to page 340" lands wrong if you track only one. The server stores both and infers the offset from the TOC's first chapter entry — but that inference **fails on books whose TOC omits chapter 1 or numbers front matter in roman numerals**. When a retrieved page's content disagrees with its label, distrust the offset and navigate by pdf page.
- **An index over a failed extraction is worse than no index.** It returns silence that looks like a real negative result — "your books don't cover this" when they do. Check `text_quality` before concluding anything from an empty search. A `none` book needs `image-ocr` first.
- **Text quality is judged on the best sampled page, not the average.** Front matter, part dividers, and full-page figures are legitimately near-empty; averaging would misflag real books as scanned. Consequence: a book with one good page and hundreds of scanned ones can read `ok`. The per-page count in `full_index`'s output is the honest check — far fewer indexed pages than total pages means partial coverage.
- **A definition 200 pages back governs the passage in front of you.** Books build vocabulary cumulatively. When a term's local use seems off, `search_corpus` the term itself to find where it was introduced rather than inferring meaning from context.
- **Code listings and math extract badly** and pollute FTS with noise tokens. A search that returns listing fragments instead of prose is the extractor's failure, not the book's.
- **Paths are the identity key.** Move or rename a file and it re-enters the corpus as a new book on the next sweep. Re-sweep after reorganizing a library.
- **Keyword search misses paraphrase.** FTS5 matches terms, not meaning; a book that discusses an idea in different words will not surface. This is the deliberate v1 limit — escalate to embeddings only when keyword search repeatedly misses content you know is present, or when conceptual rather than term queries dominate.
- **Windows lane:** this box runs `python`, not `python3`; set `PYTHONUTF8=1` when a book's text trips a console encoding error.

## Boundaries

- Mechanical PDF operations — merge, split, extract a page, fill a form → `pdf`.
- SQLite mechanics → `sqlite`. The corpus schema is the server's business; do not hand-query it when a tool exists.
- Concept comprehension → `concept-explain`. Locating code, not prose → `code-search`.
- One-shot document read → `read-pdf-doc`. Paper → `paper-deep-dive` / `paper-notes`.
- No text layer → `image-ocr` (via `image-prep` for oversized or skewed scans), then re-sweep.
- The server is not wired by this skill. If its tools are absent, wiring is a `~/.claude.json` change plus a restart — see `mcp/book-corpus/README.md`.
