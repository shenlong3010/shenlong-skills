# book-corpus — MCP server over a personal library

One SQLite DB indexes many books, so a library of hundreds of mostly-unread
files becomes queryable: *which of my books cover consensus*, *what does page
340 say*, *what's actually indexed*.

## Wire it

Reference this file by absolute path in `~/.claude.json` (global user scope) and
let `uvx` provision dependencies in an isolated env — no global install:

```json
{ "mcpServers": { "book-corpus": {
    "type": "stdio",
    "command": "uvx",
    "args": ["--with", "fastmcp>=3", "--with", "pypdf", "python",
             "C:/Users/you/path/to/mcp/book-corpus/server.py"] } } }
```

The CLI reads MCP config **only** from `~/.claude.json` — never `settings.json` —
and a **restart** is required before the tools appear.

DB defaults to `~/.local/share/book-corpus.db`; override with `BOOK_CORPUS_DB`.
It is created on demand and lives outside the repo — book files and the index
are never committed.

## Two-phase ingest, on purpose

A library is mostly unread, so extraction cost is paid only where it earns out:

| phase | cost | gives you |
|---|---|---|
| `ingest_dir` / `ingest_book` — **sweep** | cheap, samples ~5 pages | title, author, page count, TOC, text-layer verdict |
| `full_index` — **full text** | costly, reads every page | per-page FTS5 search inside that book |

Sweep the whole library once; `full_index` a book when you actually start
reading it. `search_corpus` only sees fully-indexed books and says so when
nothing is indexed yet, rather than returning a confident empty result.

## Tools

| tool | what it gives you |
|---|---|
| `list_books(filter, limit)` | what's in the corpus and its index state |
| `get_toc(book_id)` | chapter list with pdf + printed page numbers |
| `search_corpus(query, limit, book_id)` | ranked page hits with snippets |
| `get_pages(book_id, start, end, printed)` | full text of a page span (20-page cap) |
| `ingest_book(path)` / `ingest_dir(path)` | sweep one book / a directory |
| `full_index(book_id)` | the expensive per-page pass |

## Two things it gets right that are easy to get wrong

**PDF page ≠ printed page.** Front matter offsets them, so "go to page 340"
lands in the wrong place if you store only one. Both are stored, every tool
reports both, and `get_pages(..., printed=True)` accepts the number on the paper.

The offset is **measured, not guessed**. Inferring it from the TOC's first
chapter entry looked reasonable and was silently wrong on real books — many
outlines list only part names ("I Foundations") and never "Chapter 1", so the
offset defaulted to zero and every printed-page lookup drifted. `full_index`
instead votes on the page numbers printed on the pages themselves: for each
page, a number in the first or last line votes for `pdf_page - printed`. The
true offset wins by a landslide because it is the only value that agrees across
the whole book — CLRS measures 21 with 1230 of 1306 pages agreeing.

When the vote is weak the measurement is rejected **and the provisional TOC
guess is cleared**, so printed numbers fall back to pdf numbers and the tool
says so. Keeping the guess was the subtler bug: one book carried a TOC-inferred
offset of 17 while `full_index` reported that measurement had failed, leaving
every printed page number resting on an inference the tool had just disclaimed.
It happened to be correct, which is exactly what made it dangerous.

Front matter precedes printed p.1 and is usually in roman numerals, which a
single linear offset cannot express. Those pages report `front matter` rather
than a negative number.

**Search terms are quoted for you.** FTS5 treats `-` as NOT, so `red-black tree`
is a syntax error rather than a search. Bare terms are quoted into literals;
explicit `"phrases"` and uppercase `AND`/`OR`/`NOT` pass through untouched. The
tokenizer still strips `+` and `:`, so `C++` matches bare "c" — for
symbol-heavy searches, use a distinctive adjacent word.

**Text quality is decided at sweep time, not discovered later.** A scanned PDF
has no text layer, and indexing it yields *searchable nothing* — worse than no
index, because the silence looks like a real negative result. The verdict is
judged on the **best** sampled page, not the mean: front matter, part dividers,
and full-page figures are legitimately near-empty, so averaging misflags real
books. `full_index` refuses a `none` book outright and routes you to OCR;
partial extractions warn with a page count so incomplete coverage is visible.

## Why there is no companion skill

An early `read-book` skill wrapped these tools in prose — a reading procedure,
an output shape, a summarizing method. Using it against a real book showed the
prose contributed nothing: summarizing a passage is baseline model capability,
and the two behaviors that *did* matter (check the corpus before extracting;
search, then load only the hit's span) belong in the tool descriptions above,
where they fire automatically instead of costing description tokens every
session. The server is the whole artifact.

## Limits (v1, deliberate)

PDF only. Single user. Keyword search (FTS5), no embeddings — escalate to
vectors only when keyword search repeatedly misses content you know is there,
or when conceptual rather than term queries dominate. Chunking is per page, not
semantic. Re-sweep after moving files; paths are the identity key.

Requirements: `fastmcp>=3`, `pypdf>=5`.
Test: `uvx --with fastmcp --with pypdf --with reportlab python test_corpus.py`
(reportlab builds the fixture PDFs; the server itself does not need it).
